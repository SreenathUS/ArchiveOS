from __future__ import annotations

from pathlib import Path


def build_verified_path(verified_root: Path, capture_date: str, media_kind: str, filename: str) -> Path:
    year = capture_date[:4]
    month = capture_date[5:7]
    day_folder = capture_date
    return verified_root / year / month / day_folder / "Originals" / media_kind / filename


def unique_path(dest: Path) -> Path:
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    i = 1
    while True:
        c = dest.with_name(f"{stem}__dup{i}{suffix}")
        if not c.exists():
            return c
        i += 1
