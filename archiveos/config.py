from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ArchiveConfig:
    source_root: Path
    archive_root: Path
    workers: int = 4
    importer: str = "filesystem"
    metadata_provider: str = "exiftool"
    hash_algorithm: str = "sha256"
    log_level: str = "INFO"
    quarantine_enabled: bool = True
    allow_mtime_fallback: bool = False
    dry_run: bool = True


def _bool(v: Any, default: bool) -> bool:
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"1", "true", "yes", "on"}:
            return True
        if s in {"0", "false", "no", "off"}:
            return False
    return default


def load_config(config_path: Optional[Path], cli_overrides: Dict[str, Any]) -> ArchiveConfig:
    data: Dict[str, Any] = {}
    if config_path is not None:
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        data = json.loads(config_path.read_text(encoding="utf-8"))

    def pick(name: str, default: Any) -> Any:
        if cli_overrides.get(name) is not None:
            return cli_overrides[name]
        return data.get(name, default)

    source_root = Path(str(pick("source_root", ""))).resolve()
    archive_root = Path(str(pick("archive_root", ""))).resolve()
    if not str(source_root):
        raise ValueError("source_root is required")
    if not str(archive_root):
        raise ValueError("archive_root is required")

    return ArchiveConfig(
        source_root=source_root,
        archive_root=archive_root,
        workers=int(pick("workers", 4)),
        importer=str(pick("importer", "filesystem")),
        metadata_provider=str(pick("metadata_provider", "exiftool")),
        hash_algorithm=str(pick("hash_algorithm", "sha256")),
        log_level=str(pick("log_level", "INFO")).upper(),
        quarantine_enabled=_bool(pick("quarantine_enabled", True), True),
        allow_mtime_fallback=_bool(pick("allow_mtime_fallback", False), False),
        dry_run=_bool(pick("dry_run", True), True),
    )
