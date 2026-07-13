from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from archiveos.duplicates.stage import staged_duplicate_check


class DuplicateStageTests(unittest.TestCase):
    def test_duplicate_true_on_filename_size_sha(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.jpg"
            p.write_bytes(b"abc")
            dec = staged_duplicate_check("x.jpg", 3, "h1", p, "h1")
            self.assertTrue(dec.is_duplicate)

    def test_duplicate_false_on_sha_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.jpg"
            p.write_bytes(b"abc")
            dec = staged_duplicate_check("x.jpg", 3, "h1", p, "h2")
            self.assertFalse(dec.is_duplicate)


if __name__ == "__main__":
    unittest.main()
