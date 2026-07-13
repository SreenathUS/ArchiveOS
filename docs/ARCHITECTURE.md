# ArchiveOS Architecture (Authoritative)

Status: Active
Version scope: v0.1.0-alpha

This document is the authoritative architecture reference for ArchiveOS.

If this document conflicts with historical discussions, issue threads, or chat transcripts, this document and accepted ADRs are authoritative.

## 1. System Vision

ArchiveOS is an offline-first, verification-first personal digital preservation platform.

ArchiveOS guarantees that imported objects can be:

- verified
- cataloged
- searched
- recovered
- audited

without requiring cloud-vendor dependencies.

## 2. Core Principles

- Preserve originals: source bytes are never modified.
- Verify before trust: SHA-256 verification is required for integrity decisions.
- Catalog as system memory: SQLite catalog is the system source of truth.
- Determinism over convenience: reports and outcomes must be reproducible.
- Auditability by default: every import emits immutable provenance artifacts.
- Progressive extensibility: new importers and metadata providers plug in without pipeline rewrites.

## 3. C4 Model

### 3.1 Context (System Level)

Actors:

- Operator (single-user, local admin)
- Local storage devices (SD cards, phone exports, disks)
- Optional cloud export sources (e.g., Google Takeout) as offline datasets

External systems (current/future):

- Filesystem volumes (ext4/ntfs/exfat)
- Metadata toolchain (`exiftool`, future providers)
- Optional future UI/API clients

System boundary:

- ArchiveOS Core manages import, verification, cataloging, and reporting.

### 3.2 Containers (Application Level)

1. CLI Container
- Entry point for import execution and operational commands.
- Converts config + CLI overrides into pipeline execution.

2. Import Pipeline Container
- Orchestrates scan -> metadata extraction -> duplicate check -> verify -> catalog -> reporting.
- Applies engineering rules and failure handling.

3. Catalog Container (SQLite)
- Stores imports, media records, hash cache, migration state.
- Supports deterministic query and reproducible reporting.

4. Report Artifacts Container (Filesystem)
- Immutable per-import artifacts (`manifest.json`, verification/report CSVs, hashes, logs).

5. Quarantine/Verified Storage Container (Filesystem)
- Quarantine: problematic or suspicious files.
- Verified: integrity-accepted media organized by capture date policy.

### 3.3 Components (Code Level)

Current package responsibilities:

- `archiveos.cli`
: CLI parsing and run invocation.

- `archiveos.config`
: Config loading/merging (file + overrides).

- `archiveos.pipeline`
: Core orchestration and metrics/report generation.

- `archiveos.importer.*`
: Importer boundary (`Importer` base, registry, concrete importers).

- `archiveos.metadata.*`
: Metadata provider boundary + concrete provider(s).

- `archiveos.verifier.*`
: Hash and verification helpers.

- `archiveos.duplicates.*`
: Deterministic duplicate decision logic.

- `archiveos.catalog.*`
: SQLite access layer + schema migrations.

- `archiveos.reports.*`
: Structured report writing.

- `archiveos.storage.*`
: Physical archive folder layout handling.

## 4. Import Pipeline (Reference Flow)

1. Validate source and runtime config.
2. Discover files via selected importer.
3. Classify media/sidecars and quarantine invalid inputs (e.g., zero-byte).
4. Extract metadata from provider (EXIF-first policy).
5. Compute hashes as needed.
6. Apply staged duplicate checks.
7. Copy + verify to verified storage (or dry-run plan).
8. Write catalog records and import status.
9. Emit immutable reports and metrics.

## 5. Data Flow

Source Files -> Importer Scan -> Pipeline Planning -> Metadata Provider ->
Verifier/Hasher -> Duplicate Engine -> Verified/Quarantine Storage ->
Catalog DB -> Reports/Manifest

Key data artifacts:

- Operational records: import status, media state
- Integrity records: SHA-256 digests, verification outcomes
- Provenance records: source root, import identity, tooling/version info
- Deterministic outputs: report CSV/TXT/JSON + metrics

## 6. SQLite Catalog Role

SQLite is the operational and audit backbone for v0.1.0-alpha.

Catalog responsibilities:

- Track imports and lifecycle state.
- Track media metadata and verification state.
- Cache hashes for idempotent reprocessing.
- Provide deterministic query base for future UI/API.
- Maintain schema version through explicit migration files.

## 7. Import Lifecycle

Lifecycle states:

- `running`
- `completed`
- `completed_with_errors`

Lifecycle guarantees:

- Every import has a unique import identifier.
- Every import emits a manifest and report set.
- Import status transitions are persisted.

## 8. Plugin Architecture

### Importer Plugin Boundary

`Importer` contract:

- `verify_source(source_root)`
- `scan(source_root)`
- `name()`

Current implementations:

- Filesystem importer
- Sony A6700 importer (specialized filesystem flavor)

Future implementations:

- Google Takeout importer
- Android exporter importer
- DJI/GoPro importers

### Metadata Provider Boundary

`MetadataProvider` contract:

- `name()`
- `extract(files)`

Current implementation:

- ExifTool provider

Future implementations:

- ExifRead/Pillow/pyexiv2-based providers

## 9. Future Integration Points

### ArchiveUI (future)

ArchiveUI should consume catalog and report artifacts as read models.

Expected responsibilities:

- import timeline browsing
- media/filter search
- report inspection
- duplicate review

### ArchiveAI (future)

ArchiveAI should consume verified media and catalog metadata only.

Expected responsibilities:

- embeddings, OCR, face clustering
- semantic retrieval over catalog-linked derived data

AI components must not alter original media or bypass verification invariants.

## 10. Governance Note

Architecture changes that affect invariants, schema, or lifecycle semantics require:

1. ADR update or new ADR
2. Migration plan (if schema impacted)
3. Integration test updates
