from __future__ import annotations

from archiveos.importer.base import Importer
from archiveos.importer.filesystem import FilesystemImporter
from archiveos.importer.sony_a6700 import SonyA6700Importer


def get_importer(name: str) -> Importer:
    key = name.strip().lower()
    if key == "filesystem":
        return FilesystemImporter()
    if key == "sony_a6700":
        return SonyA6700Importer()
    raise ValueError(f"Unknown importer: {name}")
