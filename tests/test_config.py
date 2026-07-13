from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from archiveos.config import load_config


class ConfigTests(unittest.TestCase):
    def test_load_config_file_and_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "cfg.json"
            cfg.write_text(
                json.dumps(
                    {
                        "source_root": td,
                        "archive_root": td,
                        "dry_run": True,
                        "allow_mtime_fallback": False,
                        "workers": 2,
                    }
                ),
                encoding="utf-8",
            )
            result = load_config(cfg, {"allow_mtime_fallback": True})
            self.assertTrue(result.dry_run)
            self.assertTrue(result.allow_mtime_fallback)
            self.assertEqual(result.workers, 2)


if __name__ == "__main__":
    unittest.main()
