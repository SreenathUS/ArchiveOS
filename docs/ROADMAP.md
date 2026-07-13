# ArchiveOS Roadmap

Status: Planning baseline

## v0.1.0-alpha (Current)

### Objectives

- Stabilize import pipeline behavior.
- Enforce verification-first and provenance-first flow.
- Prove schema migration reliability and deterministic reporting.

### Success Criteria

- Real imports execute with immutable artifacts.
- Core integration tests pass consistently.
- Migration/versioning strategy is operational.

### Non-goals

- Rich UI experience.
- AI features (embeddings, OCR, face clustering).
- Multi-node sync/replication.

### Exit Criteria

- 3-4 real-world imports completed without structural redesign.
- No unresolved critical data integrity defects.

## v0.1.0

### Objectives

- Deliver stable core preservation platform behavior.
- Harden operational workflows and error handling.

### Success Criteria

- Repeatable import outcomes across multiple source types.
- Stable schema and migration process with rollback guidance.
- Deterministic reports for all supported import flows.

### Non-goals

- Full web gallery experience.
- AI-assisted discovery.

### Exit Criteria

- Verified reliability over repeated imports from camera + at least one non-camera source.
- Documented runbooks for import, verify, and recovery paths.

## v0.2.0

### Objectives

- Introduce ArchiveUI read-only operational viewer.
- Improve discoverability of imports, media, and reports.

### Success Criteria

- Browse imports and media via UI.
- Inspect verification and duplicate reports via UI.
- Query by filename/date/type from catalog.

### Non-goals

- AI semantic search.
- Full editing/curation suite.

### Exit Criteria

- UI is usable for day-to-day archive validation and investigation.
- UI relies only on stable catalog/report contracts.

## v0.3.0

### Objectives

- Add archive management layer.
- Improve duplicate handling, event grouping, and operational tooling.

### Success Criteria

- Duplicate workflows are explicit and test-backed.
- Event/album primitives available in catalog and UI.
- Operational checks (health/integrity runs) are scriptable.

### Non-goals

- Broad AI automation.
- Cloud-dependent product direction.

### Exit Criteria

- Management workflows are stable and auditable.
- No regression of verification/preservation invariants.

## v1.0

### Objectives

- Deliver dependable personal digital preservation platform.
- Provide long-term operational confidence for offline-first archival use.

### Success Criteria

- Proven end-to-end import, verify, catalog, audit, and recover workflows.
- Strong documentation and contributor standards.
- Clear upgrade/migration guidance.

### Non-goals

- Competing with cloud-native social media platforms.
- Trading integrity guarantees for convenience shortcuts.

### Exit Criteria

- Real-world multi-source usage over extended period with stable invariants.
- No unresolved high-severity integrity/provenance defects.
