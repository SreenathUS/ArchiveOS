from __future__ import annotations

from archiveos.importer.filesystem import FilesystemImporter


class SonyA6700Importer(FilesystemImporter):
    def name(self) -> str:
        return "sony_a6700"
