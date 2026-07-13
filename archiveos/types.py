from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class FileRecord:
    source_path: Path
    source_rel: str
    size: int
    mtime_ns: int
    ext: str
    stem: str
    dir_rel: str
    media_kind: str
    is_primary: bool


@dataclass(frozen=True)
class ImportContext:
    import_name: str
    source_root: Path
    archive_root: Path
    incoming_root: Path
    quarantine_root: Path
    verified_root: Path
    reports_dir: Path
    dry_run: bool


@dataclass(frozen=True)
class PlannedAction:
    source_rel: str
    dest_rel: str
    media_kind: str
    capture_date: Optional[str]
    capture_source: Optional[str]
    reason: str
