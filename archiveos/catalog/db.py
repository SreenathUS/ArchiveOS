from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock
from typing import Optional

from datetime import datetime


class CatalogDB:
    def __init__(self, db_path: Path) -> None:
        self._lock = Lock()
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._migrations_dir = Path(__file__).parent / "migrations"
        with self.conn:
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA synchronous=NORMAL")
            self._apply_migrations()

    def _table_columns(self, table: str) -> set[str]:
        rows = self.conn.execute(f"PRAGMA table_info({table})").fetchall()
        return {str(r[1]) for r in rows}

    def _ensure_schema_migrations_table(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
              version INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              applied_at TEXT NOT NULL
            )
            """
        )

    def _applied_versions(self) -> set[int]:
        rows = self.conn.execute("SELECT version FROM schema_migrations").fetchall()
        return {int(r[0]) for r in rows}

    def _apply_migrations(self) -> None:
        self._ensure_schema_migrations_table()
        applied = self._applied_versions()
        files = sorted(self._migrations_dir.glob("*.sql"))
        for f in files:
            prefix = f.stem.split("_", 1)[0]
            if not prefix.isdigit():
                continue
            version = int(prefix)
            if version in applied:
                continue
            sql = f.read_text(encoding="utf-8")
            try:
                self.conn.executescript(sql)
            except sqlite3.OperationalError as exc:
                msg = str(exc).lower()
                # Existing field deployments may already include these columns.
                if "duplicate column name" not in msg:
                    raise
            self.conn.execute(
                "INSERT INTO schema_migrations(version, name, applied_at) VALUES(?,?,?)",
                (version, f.name, datetime.now().isoformat(timespec="seconds")),
            )

        # Legacy compatibility bridge for existing DBs created before migration files.
        if self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='imports'").fetchone():
            cols = self._table_columns("imports")
            if "archive_root" not in cols:
                self.conn.execute("ALTER TABLE imports ADD COLUMN archive_root TEXT")
            if "manifest_path" not in cols:
                self.conn.execute("ALTER TABLE imports ADD COLUMN manifest_path TEXT")
            if "status" not in cols:
                self.conn.execute("ALTER TABLE imports ADD COLUMN status TEXT")
            if "dry_run" not in cols:
                self.conn.execute("ALTER TABLE imports ADD COLUMN dry_run INTEGER DEFAULT 0")
            if "software_version" not in cols:
                self.conn.execute("ALTER TABLE imports ADD COLUMN software_version TEXT")

        if self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='media'").fetchone():
            cols = self._table_columns("media")
            for col, decl in [
                ("capture_source", "TEXT"),
                ("camera_model", "TEXT"),
                ("lens", "TEXT"),
                ("camera_serial", "TEXT"),
                ("gps_lat", "REAL"),
                ("gps_lon", "REAL"),
                ("width", "INTEGER"),
                ("height", "INTEGER"),
                ("duration", "REAL"),
                ("media_group", "TEXT"),
                ("media_kind", "TEXT"),
                ("duplicate_group", "TEXT"),
                ("verified", "INTEGER DEFAULT 0"),
                ("note", "TEXT"),
                ("updated_at", "TEXT"),
            ]:
                if col not in cols:
                    self.conn.execute(f"ALTER TABLE media ADD COLUMN {col} {decl}")

    def close(self) -> None:
        self.conn.close()

    def insert_import(
        self,
        import_name: str,
        started_at: str,
        source_root: str,
        archive_root: str,
        source_uuid: str,
        manifest_path: str,
        status: str,
        dry_run: bool = False,
        software_version: str = "ArchiveOS-v0.1",
    ) -> int:
        cols = self._table_columns("imports")
        insert_cols = ["import_name", "started_at", "source_root"]
        values: list[object] = [import_name, started_at, source_root]

        if "dest_root" in cols:
            insert_cols.append("dest_root")
            values.append(archive_root)
        if "archive_root" in cols:
            insert_cols.append("archive_root")
            values.append(archive_root)
        if "source_uuid" in cols:
            insert_cols.append("source_uuid")
            values.append(source_uuid)
        if "manifest_path" in cols:
            insert_cols.append("manifest_path")
            values.append(manifest_path)
        if "status" in cols:
            insert_cols.append("status")
            values.append(status)
        if "software_version" in cols:
            insert_cols.append("software_version")
            values.append(software_version)
        if "dry_run" in cols:
            insert_cols.append("dry_run")
            values.append(1 if dry_run else 0)

        placeholders = ",".join(["?"] * len(insert_cols))
        sql = f"INSERT INTO imports({','.join(insert_cols)}) VALUES({placeholders})"

        with self._lock:
            with self.conn:
                self.conn.execute(sql, tuple(values))
                row = self.conn.execute("SELECT import_id FROM imports WHERE import_name=?", (import_name,)).fetchone()
                return int(row[0])

    def update_import_status(self, import_id: int, status: str) -> None:
        with self._lock:
            with self.conn:
                self.conn.execute("UPDATE imports SET status=? WHERE import_id=?", (status, import_id))

    def get_hash_cache(self, path: str, size: int, mtime_ns: int) -> Optional[str]:
        with self._lock:
            row = self.conn.execute(
                "SELECT size, mtime_ns, sha256 FROM hash_cache WHERE path=?",
                (path,),
            ).fetchone()
        if row is None:
            return None
        if int(row[0]) == int(size) and int(row[1]) == int(mtime_ns):
            return str(row[2])
        return None

    def set_hash_cache(self, path: str, size: int, mtime_ns: int, sha256: str, updated_at: str) -> None:
        with self._lock:
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO hash_cache(path, size, mtime_ns, sha256, updated_at)
                    VALUES(?,?,?,?,?)
                    ON CONFLICT(path) DO UPDATE SET
                        size=excluded.size,
                        mtime_ns=excluded.mtime_ns,
                        sha256=excluded.sha256,
                        updated_at=excluded.updated_at
                    """,
                    (path, size, mtime_ns, sha256, updated_at),
                )

    def upsert_media(
        self,
        import_id: int,
        source_rel: str,
        dest_rel: str,
        filename: str,
        ext: str,
        size: int,
        sha256: Optional[str],
        capture_date: Optional[str],
        capture_source: Optional[str],
        camera_model: Optional[str],
        lens: Optional[str],
        camera_serial: Optional[str],
        gps_lat: Optional[float],
        gps_lon: Optional[float],
        width: Optional[int],
        height: Optional[int],
        duration: Optional[float],
        media_group: str,
        media_kind: str,
        duplicate_group: Optional[str],
        verified: bool,
        status: str,
        note: Optional[str],
        updated_at: str,
    ) -> None:
        with self._lock:
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO media(
                        import_id, source_rel, dest_rel, filename, ext, size, sha256,
                        capture_date, capture_source, camera_model, lens, camera_serial,
                        gps_lat, gps_lon, width, height, duration,
                        media_group, media_kind, duplicate_group, verified, status, note, updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(source_rel) DO UPDATE SET
                        import_id=excluded.import_id,
                        dest_rel=excluded.dest_rel,
                        sha256=excluded.sha256,
                        capture_date=excluded.capture_date,
                        capture_source=excluded.capture_source,
                        camera_model=excluded.camera_model,
                        lens=excluded.lens,
                        camera_serial=excluded.camera_serial,
                        gps_lat=excluded.gps_lat,
                        gps_lon=excluded.gps_lon,
                        width=excluded.width,
                        height=excluded.height,
                        duration=excluded.duration,
                        media_group=excluded.media_group,
                        media_kind=excluded.media_kind,
                        duplicate_group=excluded.duplicate_group,
                        verified=excluded.verified,
                        status=excluded.status,
                        note=excluded.note,
                        updated_at=excluded.updated_at
                    """,
                    (
                        import_id,
                        source_rel,
                        dest_rel,
                        filename,
                        ext,
                        size,
                        sha256,
                        capture_date,
                        capture_source,
                        camera_model,
                        lens,
                        camera_serial,
                        gps_lat,
                        gps_lon,
                        width,
                        height,
                        duration,
                        media_group,
                        media_kind,
                        duplicate_group,
                        1 if verified else 0,
                        status,
                        note,
                        updated_at,
                    ),
                )
