from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Dict, List

from archiveos.catalog.db import CatalogDB
from archiveos.duplicates.stage import staged_duplicate_check
from archiveos.importer.registry import get_importer
from archiveos.metadata.exiftool_provider import ExifToolProvider
from archiveos.organizer.paths import build_verified_path, unique_path
from archiveos.reports.writer import write_csv, write_json, write_lines
from archiveos.storage.layout import ensure_layout
from archiveos.types import FileRecord
from archiveos.verifier.hashutil import sha256_file

SOFTWARE_VERSION = "ArchiveOS-v0.1"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _parse_capture_date(meta: Dict[str, object], rec: FileRecord, allow_mtime_fallback: bool) -> tuple[str, str]:
    def norm(v: object) -> str | None:
        if not v:
            return None
        s = str(v)
        if len(s) >= 10 and s[4] in {":", "-"} and s[7] in {":", "-"}:
            return f"{s[0:4]}-{s[5:7]}-{s[8:10]}"
        return None

    d = norm(meta.get("DateTimeOriginal")) or norm(meta.get("CreateDate"))
    if d:
        return d, "exif"
    if allow_mtime_fallback:
        return datetime.fromtimestamp(rec.mtime_ns / 1_000_000_000).strftime("%Y-%m-%d"), "mtime_fallback"
    raise RuntimeError("missing_exif_capture_date")


def _build_logger(run_dir: Path, import_name: str, log_level: str) -> logging.Logger:
    logger = logging.getLogger(f"archiveos.pipeline.{import_name}")
    logger.handlers.clear()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    file_handler = logging.FileHandler(run_dir / "import.log", encoding="utf-8")
    file_handler.setLevel(logger.level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logger.level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def run_import_pipeline(
    source_root: Path,
    archive_root: Path,
    dry_run: bool,
    allow_mtime_fallback: bool,
    importer_name: str = "filesystem",
    log_level: str = "INFO",
) -> Path:
    run_started = perf_counter()
    layout = ensure_layout(archive_root)
    import_name = f"Import_{datetime.now().strftime('%Y-%m-%d_%H%M%S_%f')}"
    run_dir = layout.reports / import_name
    run_dir.mkdir(parents=True, exist_ok=True)
    logger = _build_logger(run_dir, import_name, log_level)
    logger.info(
        "event=import_started import=%s importer=%s dry_run=%s source_root=%s archive_root=%s",
        import_name,
        importer_name,
        dry_run,
        source_root,
        archive_root,
    )

    manifest_path = run_dir / "manifest.json"
    source_uuid = "UNKNOWN"

    db_path = layout.reports / "archiveos_catalog.sqlite"
    db = CatalogDB(db_path)
    import_id = db.insert_import(
        import_name=import_name,
        started_at=_now(),
        source_root=str(source_root),
        archive_root=str(archive_root),
        source_uuid=source_uuid,
        manifest_path=str(manifest_path),
        status="running",
        dry_run=dry_run,
        software_version=SOFTWARE_VERSION,
    )

    importer = get_importer(importer_name)
    primaries, sidecars = importer.scan(source_root)
    logger.info(
        "event=scan_completed import=%s primaries=%d sidecars=%d",
        import_name,
        len(primaries),
        sum(len(v) for v in sidecars.values()),
    )

    zero_byte_primaries = [r for r in primaries if r.size == 0]
    valid_primaries = [r for r in primaries if r.size > 0]

    provider = ExifToolProvider()
    exif_started = perf_counter()
    exif = provider.extract([r.source_path for r in valid_primaries])
    exif_seconds = perf_counter() - exif_started
    logger.info(
        "event=metadata_extracted import=%s provider=%s files=%d duration_seconds=%.3f",
        import_name,
        provider.name(),
        len(valid_primaries),
        exif_seconds,
    )

    planned_rows: List[List[str]] = []
    dup_rows: List[List[str]] = []
    miss_rows: List[List[str]] = []
    hash_lines: List[str] = []

    counters = {
        "primary_scanned": len(primaries),
        "zero_byte_quarantined": len(zero_byte_primaries),
        "sidecars_detected": sum(len(v) for v in sidecars.values()),
        "planned": 0,
        "copied": 0,
        "verified": 0,
        "duplicates": 0,
        "errors": 0,
    }
    metrics = {
        "duration_seconds": 0.0,
        "files_scanned": len(primaries) + sum(len(v) for v in sidecars.values()),
        "files_imported": 0,
        "duplicates": 0,
        "hashes_computed": 0,
        "bytes_processed": 0,
        "bytes_copied": 0,
        "hash_seconds": 0.0,
        "copy_seconds": 0.0,
        "average_hash_rate_mbps": 0.0,
        "average_copy_rate_mbps": 0.0,
        "verification_failures": 0,
        "exif_extraction_seconds": round(exif_seconds, 6),
    }

    def cached_hash(rec: FileRecord) -> str:
        cached = db.get_hash_cache(str(rec.source_path), rec.size, rec.mtime_ns)
        if cached:
            logger.debug("event=hash_cache_hit path=%s", rec.source_path)
            return cached
        hash_started = perf_counter()
        h = sha256_file(rec.source_path)
        metrics["hashes_computed"] += 1
        metrics["hash_seconds"] += perf_counter() - hash_started
        metrics["bytes_processed"] += rec.size
        db.set_hash_cache(str(rec.source_path), rec.size, rec.mtime_ns, h, _now())
        logger.debug("event=hash_computed path=%s size=%d", rec.source_path, rec.size)
        return h

    def process_record(rec: FileRecord, is_sidecar: bool = False) -> None:
        nonlocal counters
        meta = exif.get(str(rec.source_path), {})
        capture_date, capture_source = _parse_capture_date(meta, rec, allow_mtime_fallback)
        dest = build_verified_path(layout.verified, capture_date, rec.media_kind, rec.source_path.name)
        dest_rel = dest.relative_to(archive_root).as_posix()
        counters["planned"] += 1
        planned_rows.append([rec.source_rel, str(rec.size), capture_date, capture_source, rec.media_kind, dest_rel])
        logger.debug(
            "event=file_planned source_rel=%s dest_rel=%s capture_date=%s kind=%s dry_run=%s",
            rec.source_rel,
            dest_rel,
            capture_date,
            rec.media_kind,
            dry_run,
        )

        media_group = f"{rec.dir_rel}/{rec.stem}"

        if dry_run:
            db.upsert_media(
                import_id=import_id,
                source_rel=rec.source_rel,
                dest_rel=dest_rel,
                filename=rec.source_path.name,
                ext=rec.ext,
                size=rec.size,
                sha256=None,
                capture_date=capture_date,
                capture_source=capture_source,
                camera_model=str(meta.get("Model")) if meta.get("Model") else None,
                lens=str(meta.get("LensModel")) if meta.get("LensModel") else None,
                camera_serial=str(meta.get("SerialNumber")) if meta.get("SerialNumber") else None,
                gps_lat=None,
                gps_lon=None,
                width=int(meta.get("ImageWidth")) if meta.get("ImageWidth") else None,
                height=int(meta.get("ImageHeight")) if meta.get("ImageHeight") else None,
                duration=None,
                media_group=media_group,
                media_kind=rec.media_kind,
                duplicate_group=None,
                verified=False,
                status="dry_run_planned",
                note="sidecar" if is_sidecar else None,
                updated_at=_now(),
            )
            return

        src_sha = cached_hash(rec)
        if dest.exists():
            st = dest.stat()
            dst_sha = db.get_hash_cache(str(dest), int(st.st_size), int(st.st_mtime_ns))
            if dst_sha is None:
                hash_started = perf_counter()
                dst_sha = sha256_file(dest)
                metrics["hashes_computed"] += 1
                metrics["hash_seconds"] += perf_counter() - hash_started
                metrics["bytes_processed"] += int(st.st_size)
                db.set_hash_cache(str(dest), int(st.st_size), int(st.st_mtime_ns), dst_sha, _now())
            dec = staged_duplicate_check(rec.source_path.name, rec.size, src_sha, dest, dst_sha)
            if dec.is_duplicate:
                counters["duplicates"] += 1
                metrics["duplicates"] += 1
                dup_rows.append([rec.source_rel, dest_rel, src_sha, dec.reason])
                logger.info(
                    "event=duplicate_detected source_rel=%s dest_rel=%s reason=%s",
                    rec.source_rel,
                    dest_rel,
                    dec.reason,
                )
                db.upsert_media(
                    import_id=import_id,
                    source_rel=rec.source_rel,
                    dest_rel=dest_rel,
                    filename=rec.source_path.name,
                    ext=rec.ext,
                    size=rec.size,
                    sha256=src_sha,
                    capture_date=capture_date,
                    capture_source=capture_source,
                    camera_model=str(meta.get("Model")) if meta.get("Model") else None,
                    lens=str(meta.get("LensModel")) if meta.get("LensModel") else None,
                    camera_serial=str(meta.get("SerialNumber")) if meta.get("SerialNumber") else None,
                    gps_lat=None,
                    gps_lon=None,
                    width=int(meta.get("ImageWidth")) if meta.get("ImageWidth") else None,
                    height=int(meta.get("ImageHeight")) if meta.get("ImageHeight") else None,
                    duration=None,
                    media_group=media_group,
                    media_kind=rec.media_kind,
                    duplicate_group=src_sha,
                    verified=True,
                    status="duplicate_verified",
                    note=dec.reason,
                    updated_at=_now(),
                )
                return
            dest = unique_path(dest)
            dest_rel = dest.relative_to(archive_root).as_posix()

        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        if tmp.exists():
            tmp.unlink()

        copy_started = perf_counter()
        shutil.copy2(rec.source_path, tmp)
        metrics["copy_seconds"] += perf_counter() - copy_started
        metrics["bytes_copied"] += rec.size
        dst_sha = sha256_file(tmp)
        metrics["hashes_computed"] += 1
        metrics["bytes_processed"] += rec.size
        if src_sha != dst_sha:
            miss_rows.append([rec.source_rel, dest_rel, "hash_mismatch_after_copy"])
            counters["errors"] += 1
            metrics["verification_failures"] += 1
            logger.error(
                "event=verification_failed source_rel=%s dest_rel=%s reason=hash_mismatch_after_copy",
                rec.source_rel,
                dest_rel,
            )
            try:
                tmp.unlink()
            except OSError:
                pass
            return

        tmp.replace(dest)
        counters["copied"] += 1
        counters["verified"] += 1
        metrics["files_imported"] += 1
        hash_lines.append(f"{src_sha}  {dest_rel}")
        logger.debug("event=file_verified source_rel=%s dest_rel=%s", rec.source_rel, dest_rel)

        st = dest.stat()
        db.set_hash_cache(str(dest), int(st.st_size), int(st.st_mtime_ns), dst_sha, _now())
        db.upsert_media(
            import_id=import_id,
            source_rel=rec.source_rel,
            dest_rel=dest_rel,
            filename=rec.source_path.name,
            ext=rec.ext,
            size=rec.size,
            sha256=src_sha,
            capture_date=capture_date,
            capture_source=capture_source,
            camera_model=str(meta.get("Model")) if meta.get("Model") else None,
            lens=str(meta.get("LensModel")) if meta.get("LensModel") else None,
            camera_serial=str(meta.get("SerialNumber")) if meta.get("SerialNumber") else None,
            gps_lat=None,
            gps_lon=None,
            width=int(meta.get("ImageWidth")) if meta.get("ImageWidth") else None,
            height=int(meta.get("ImageHeight")) if meta.get("ImageHeight") else None,
            duration=None,
            media_group=media_group,
            media_kind=rec.media_kind,
            duplicate_group=None,
            verified=True,
            status="verified",
            note="sidecar" if is_sidecar else None,
            updated_at=_now(),
        )

    for z in zero_byte_primaries:
        counters["errors"] += 1
        metrics["verification_failures"] += 1
        miss_rows.append([z.source_rel, "", "zero_byte_source_file"])
        logger.warning("event=quarantine_zero_byte source_rel=%s", z.source_rel)
        q_dest = layout.quarantine / z.source_rel
        if not dry_run:
            q_dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(z.source_path, q_dest)
            except OSError:
                pass

    for rec in valid_primaries:
        try:
            process_record(rec, is_sidecar=False)
            for s in sidecars.get((rec.dir_rel, rec.stem), []):
                process_record(s, is_sidecar=True)
        except Exception as e:
            counters["errors"] += 1
            metrics["verification_failures"] += 1
            miss_rows.append([rec.source_rel, "", str(e)])
            logger.error("event=file_failed source_rel=%s error=%s", rec.source_rel, e)
            # Quarantine problematic sources for auditability.
            q_dest = layout.quarantine / rec.source_rel
            if not dry_run:
                q_dest.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(rec.source_path, q_dest)
                except OSError:
                    pass

    metrics["duration_seconds"] = round(perf_counter() - run_started, 6)
    if metrics["hash_seconds"] > 0:
        metrics["average_hash_rate_mbps"] = round((metrics["bytes_processed"] / 1024 / 1024) / metrics["hash_seconds"], 3)
    if metrics["copy_seconds"] > 0:
        metrics["average_copy_rate_mbps"] = round((metrics["bytes_copied"] / 1024 / 1024) / metrics["copy_seconds"], 3)
    metrics["hash_seconds"] = round(metrics["hash_seconds"], 6)
    metrics["copy_seconds"] = round(metrics["copy_seconds"], 6)

    write_csv(run_dir / "planned_moves.csv", ["source_rel", "size", "capture_date", "capture_source", "kind", "dest_rel"], planned_rows)
    write_csv(run_dir / "duplicate_report.csv", ["source_rel", "dest_rel", "sha256", "reason"], dup_rows)
    write_csv(run_dir / "missing_files.csv", ["source_rel", "dest_rel", "reason"], miss_rows)
    write_lines(run_dir / "hashes.sha256", hash_lines)

    manifest = {
        "software_version": SOFTWARE_VERSION,
        "import_name": import_name,
        "generated_at": _now(),
        "source_root": str(source_root),
        "archive_root": str(archive_root),
        "source_uuid": source_uuid,
        "importer": importer.name(),
        "dry_run": dry_run,
        "metadata_provider": provider.name(),
        "log_level": log_level.upper(),
        "counters": counters,
        "metrics": metrics,
        "reports": {
            "planned_moves": str(run_dir / "planned_moves.csv"),
            "duplicates": str(run_dir / "duplicate_report.csv"),
            "missing": str(run_dir / "missing_files.csv"),
            "hashes": str(run_dir / "hashes.sha256"),
            "import_log": str(run_dir / "import.log"),
            "catalog_db": str(db_path),
        },
    }
    write_json(manifest_path, manifest)
    write_lines(
        run_dir / "verification.txt",
        [
            "ArchiveOS Verification Report",
            f"Generated: {manifest['generated_at']}",
            f"Import: {import_name}",
            f"Dry run: {dry_run}",
            f"Primary scanned: {counters['primary_scanned']}",
            f"Sidecars detected: {counters['sidecars_detected']}",
            f"Planned: {counters['planned']}",
            f"Copied: {counters['copied']}",
            f"Verified: {counters['verified']}",
            f"Duplicates: {counters['duplicates']}",
            f"Errors: {counters['errors']}",
            f"Duration seconds: {metrics['duration_seconds']}",
            f"Bytes processed: {metrics['bytes_processed']}",
            f"Average hash rate MB/s: {metrics['average_hash_rate_mbps']}",
            f"Average copy rate MB/s: {metrics['average_copy_rate_mbps']}",
        ],
    )

    db.update_import_status(import_id, "completed" if counters["errors"] == 0 else "completed_with_errors")
    logger.info(
        "event=import_completed import=%s status=%s duration_seconds=%.3f files_imported=%d duplicates=%d errors=%d",
        import_name,
        "completed" if counters["errors"] == 0 else "completed_with_errors",
        metrics["duration_seconds"],
        metrics["files_imported"],
        metrics["duplicates"],
        counters["errors"],
    )
    db.close()
    return run_dir
