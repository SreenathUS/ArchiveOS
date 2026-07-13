# ArchiveOS v0.1 (Modular Foundation)

This folder contains the first modular ArchiveOS pipeline scaffold.

## Goals

- Move away from a single giant script.
- Centralize state in a SQLite catalog.
- Keep import workflow auditable and resumable.
- Support sidecars and staged duplicate detection.
- Keep quarantine as a first-class area.

## Layout

- `archiveos/importer/` source scanning
- `archiveos/metadata/` metadata providers (`exiftool` now, pluggable later)
- `archiveos/verifier/` hashing and verification helpers
- `archiveos/duplicates/` staged duplicate decisions
- `archiveos/organizer/` destination path policy
- `archiveos/catalog/` SQLite catalog layer
- `archiveos/reports/` report writers
- `archiveos/storage/` Incoming/Quarantine/Verified/Reports layout
- `archiveos/pipeline.py` orchestration
- `archiveos/cli.py` command entrypoint

## Install/Run

```bash
cd /home/sunntiha/githubCopilotWspace/archiveos
python3 -m pip install -e .

archiveos \
  --source-root /media/sunntiha/IronWolf8TB2/ALL/a6700/07072026 \
  --archive-root /media/sunntiha/IronWolf8TB2/ALL/Camera/Sony_A6700 \
  --dry-run
```

## Reports per import

Each run creates `Reports/Import_YYYY-MM-DD_HHMMSS/` with:

- `manifest.json`
- `verification.txt`
- `planned_moves.csv`
- `duplicate_report.csv`
- `missing_files.csv`
- `hashes.sha256`

Catalog DB is stored at `Reports/archiveos_catalog.sqlite`.
