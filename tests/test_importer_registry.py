from __future__ import annotations

import unittest

from archiveos.importer.filesystem import FilesystemImporter
from archiveos.importer.registry import get_importer
from archiveos.importer.sony_a6700 import SonyA6700Importer


class ImporterRegistryTests(unittest.TestCase):
    def test_registry_returns_filesystem(self) -> None:
        self.assertIsInstance(get_importer("filesystem"), FilesystemImporter)

    def test_registry_returns_sony(self) -> None:
        self.assertIsInstance(get_importer("sony_a6700"), SonyA6700Importer)


if __name__ == "__main__":
    unittest.main()
