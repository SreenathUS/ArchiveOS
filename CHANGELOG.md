# Changelog

## v0.1.0
- Introduced modular ArchiveOS package structure.
- Added import pipeline with scan, metadata, verify, organize, catalog, reports.
- Added quarantine handling for zero-byte/problem files.
- Added SQLite catalog and hash cache.
- Added explicit schema migration framework with versioned SQL files.
- Added config file support (`--config`) with CLI overrides.
- Added initial automated test suite (config, duplicate stage, DB migrations).
