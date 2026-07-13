from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple

from archiveos.types import FileRecord

RAW_EXTS = {".arw", ".dng", ".raw"}
JPG_EXTS = {".jpg", ".jpeg"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mts", ".m2ts", ".mkv"}
SIDECAR_EXTS = {".xml", ".xmp", ".lrv", ".thm", ".srt"}
PRIMARY_EXTS = RAW_EXTS | JPG_EXTS | VIDEO_EXTS
TRACKED_EXTS = PRIMARY_EXTS | SIDECAR_EXTS


def _kind(ext: str) -> str:
    if ext in RAW_EXTS:
        return "RAW"
    if ext in JPG_EXTS:
        return "JPG"
    if ext in VIDEO_EXTS:
        return "Video"
    return "Sidecar"


def scan_source(source_root: Path) -> Tuple[List[FileRecord], Dict[Tuple[str, str], List[FileRecord]]]:
    primaries: List[FileRecord] = []
    sidecars: Dict[Tuple[str, str], List[FileRecord]] = {}

    for root, _, names in os.walk(source_root):
        root_path = Path(root)
        for name in names:
            p = root_path / name
            ext = p.suffix.lower()
            if ext not in TRACKED_EXTS:
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            rel = p.relative_to(source_root).as_posix()
            dir_rel = p.parent.relative_to(source_root).as_posix() if p.parent != source_root else ""
            rec = FileRecord(
                source_path=p,
                source_rel=rel,
                size=int(st.st_size),
                mtime_ns=int(st.st_mtime_ns),
                ext=ext,
                stem=p.stem,
                dir_rel=dir_rel,
                media_kind=_kind(ext),
                is_primary=ext in PRIMARY_EXTS,
            )
            key = (dir_rel, p.stem)
            if rec.is_primary:
                primaries.append(rec)
            else:
                sidecars.setdefault(key, []).append(rec)

    return primaries, sidecars
