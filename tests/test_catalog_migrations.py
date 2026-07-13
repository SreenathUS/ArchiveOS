from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from archiveos.catalog.db import CatalogDB


class CatalogMigrationTests(unittest.TestCase):
    def test_migrations_create_expected_tables(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "cat.sqlite"
            db = CatalogDB(db_path)
            db.close()

            con = sqlite3.connect(db_path)
            cur = con.cursor()
            tables = {r[0] for r in cur.execute("select name from sqlite_master where type='table'")}
            self.assertIn("schema_migrations", tables)
            self.assertIn("imports", tables)
            self.assertIn("media", tables)
            self.assertIn("hash_cache", tables)

            cols = {r[1] for r in cur.execute("pragma table_info(imports)")}
            self.assertIn("archive_root", cols)
            self.assertIn("dry_run", cols)
            self.assertIn("software_version", cols)
            con.close()


if __name__ == "__main__":
    unittest.main()
