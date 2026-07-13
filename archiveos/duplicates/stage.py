from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DuplicateDecision:
    is_duplicate: bool
    reason: str


def staged_duplicate_check(src_name: str, src_size: int, src_sha: str, dest_path: Path, dest_sha: str | None) -> DuplicateDecision:
    if not dest_path.exists():
        return DuplicateDecision(False, "dest_missing")

    if dest_path.name != src_name:
        return DuplicateDecision(False, "filename_mismatch")

    try:
        st = dest_path.stat()
    except OSError:
        return DuplicateDecision(False, "dest_stat_error")

    if int(st.st_size) != int(src_size):
        return DuplicateDecision(False, "size_mismatch")

    if dest_sha is None:
        return DuplicateDecision(False, "dest_sha_unavailable")

    if src_sha == dest_sha:
        return DuplicateDecision(True, "filename_size_sha_match")

    return DuplicateDecision(False, "sha_mismatch")
