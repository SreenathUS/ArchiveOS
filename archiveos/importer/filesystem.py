from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from archiveos.importer.base import Importer
from archiveos.importer.scan import scan_source
from archiveos.types import FileRecord


class FilesystemImporter(Importer):
    def name(self) -> str:
        return "filesystem"

    def verify_source(self, source_root: Path) -> None:
        if not source_root.is_dir():
            raise FileNotFoundError(f"Source root not found: {source_root}")

    def scan(self, source_root: Path) -> Tuple[List[FileRecord], Dict[Tuple[str, str], List[FileRecord]]]:
        self.verify_source(source_root)
        return scan_source(source_root)
