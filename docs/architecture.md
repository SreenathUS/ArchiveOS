# ArchiveOS Architecture Notes

## Pipeline

SD/Source -> Incoming -> Verification -> Metadata -> Catalog -> Duplicates -> Verified -> Organization

## Core principles

- Never overwrite blindly.
- Verify by SHA-256.
- Keep imports auditable via immutable report folders.
- Quarantine bad/corrupt/suspicious files.
- Keep metadata extraction provider pluggable.

## Next milestones

1. Add web UI (FastAPI + HTMX).
2. Add thumbnail/preview generation module.
3. Add importer adapters (Sony, Google Takeout, mobile).
4. Add richer schema tables (events, albums, tags, faces, embeddings).
