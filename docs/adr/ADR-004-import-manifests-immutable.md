# ADR-004: Import Manifests Are Immutable

## Status
Accepted

## Context
Long-term archival trust depends on knowing when and how files entered the system.

## Decision
Each import writes its own immutable report directory containing manifest and verification artifacts.

## Consequences
- Imports remain auditable over time.
- Historical ingestion state can be reconstructed.
- Reports should never be overwritten in place.
