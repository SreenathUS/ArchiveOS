# ADR-002: SHA-256 For Verification

## Status
Accepted

## Context
ArchiveOS needs a stable and trustworthy verification algorithm for long-term media ingestion.

## Decision
Use SHA-256 as the verification hash for import validation and duplicate comparison in v0.1-alpha.

## Consequences
- Strong integrity verification.
- Slower than weaker checksums, but appropriate for archive trust.
- Hash values can be reused later for deduplication and AI indexing pipelines.
