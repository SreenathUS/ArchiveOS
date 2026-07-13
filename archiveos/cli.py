from __future__ import annotations

import argparse
from pathlib import Path

from archiveos.config import load_config
from archiveos.pipeline import run_import_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="ArchiveOS v0.1 modular pipeline")
    parser.add_argument("--config", help="Path to JSON config file")
    parser.add_argument("--source-root", help="Source media root")
    parser.add_argument("--archive-root", help="Archive root containing Incoming/Quarantine/Verified/Reports")
    parser.add_argument("--log-level", help="Logging level: DEBUG, INFO, WARNING, ERROR")
    parser.add_argument("--dry-run", action="store_true", help="Plan only, no copy")
    parser.add_argument(
        "--allow-mtime-fallback",
        action="store_true",
        help="Allow mtime date if EXIF date is missing",
    )
    args = parser.parse_args()

    cfg = load_config(
        Path(args.config).resolve() if args.config else None,
        {
            "source_root": args.source_root,
            "archive_root": args.archive_root,
            "log_level": args.log_level,
            "dry_run": True if args.dry_run else None,
            "allow_mtime_fallback": True if args.allow_mtime_fallback else None,
        },
    )

    run_dir = run_import_pipeline(
        source_root=cfg.source_root,
        archive_root=cfg.archive_root,
        dry_run=cfg.dry_run,
        allow_mtime_fallback=cfg.allow_mtime_fallback,
        importer_name=cfg.importer,
        log_level=cfg.log_level,
    )
    print(f"RUN_DIR={run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
