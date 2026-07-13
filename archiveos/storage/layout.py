from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArchiveLayout:
    archive_root: Path
    incoming: Path
    quarantine: Path
    verified: Path
    reports: Path


def ensure_layout(archive_root: Path) -> ArchiveLayout:
    incoming = archive_root / "Incoming"
    quarantine = archive_root / "Quarantine"
    verified = archive_root / "Verified"
    reports = archive_root / "Reports"
    for p in (incoming, quarantine, verified, reports):
        p.mkdir(parents=True, exist_ok=True)
    return ArchiveLayout(
        archive_root=archive_root,
        incoming=incoming,
        quarantine=quarantine,
        verified=verified,
        reports=reports,
    )
