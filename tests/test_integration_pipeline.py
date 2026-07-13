from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from archiveos.pipeline import run_import_pipeline


class FakeExifProvider:
    def name(self) -> str:
        return "fake-exif"

    def extract(self, files):
        return {
            str(p): {
                "DateTimeOriginal": "2026:07:09 10:00:00",
                "CreateDate": "2026:07:09 10:00:00",
                "Model": "Sony A6700",
                "ImageWidth": 100,
                "ImageHeight": 100,
            }
            for p in files
        }


class PipelineIntegrationTests(unittest.TestCase):
    def test_normal_import_dry_run_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            dst = Path(td) / "archive"
            src.mkdir()
            dst.mkdir()
            (src / "DSC00001.JPG").write_bytes(b"abc")

            with patch("archiveos.pipeline.ExifToolProvider", FakeExifProvider):
                run_dir = run_import_pipeline(src, dst, dry_run=True, allow_mtime_fallback=False, importer_name="filesystem")

            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["counters"]["primary_scanned"], 1)
            self.assertEqual(manifest["counters"]["errors"], 0)
            self.assertIn("metrics", manifest)
            self.assertEqual(manifest["metrics"]["files_scanned"], 1)
            self.assertIn("import_log", manifest["reports"])
            self.assertTrue((run_dir / "import.log").exists())

    def test_corrupt_zero_byte_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            dst = Path(td) / "archive"
            src.mkdir()
            dst.mkdir()
            (src / "BAD00001.JPG").write_bytes(b"")

            with patch("archiveos.pipeline.ExifToolProvider", FakeExifProvider):
                run_dir = run_import_pipeline(src, dst, dry_run=True, allow_mtime_fallback=True, importer_name="filesystem")

            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["counters"]["zero_byte_quarantined"], 1)
            self.assertEqual(manifest["counters"]["errors"], 1)
            self.assertEqual(manifest["metrics"]["verification_failures"], 1)

    def test_resume_like_rerun_is_stable_for_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            dst = Path(td) / "archive"
            src.mkdir()
            dst.mkdir()
            (src / "DSC00001.JPG").write_bytes(b"abc")

            with patch("archiveos.pipeline.ExifToolProvider", FakeExifProvider):
                run_dir1 = run_import_pipeline(src, dst, dry_run=True, allow_mtime_fallback=False, importer_name="filesystem")
                run_dir2 = run_import_pipeline(src, dst, dry_run=True, allow_mtime_fallback=False, importer_name="filesystem")

            m1 = json.loads((run_dir1 / "manifest.json").read_text(encoding="utf-8"))
            m2 = json.loads((run_dir2 / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(m1["counters"]["planned"], 1)
            self.assertEqual(m2["counters"]["planned"], 1)


if __name__ == "__main__":
    unittest.main()
