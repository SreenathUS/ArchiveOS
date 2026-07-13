# ADR-005: Original Media Is Never Modified

## Status
Accepted

## Context
ArchiveOS is intended to protect original source media, not transform or rewrite it.

## Decision
ArchiveOS must never alter original media contents. It may copy, verify, catalog, quarantine, and later generate derived previews, but original bytes remain unchanged.

## Consequences
- Originals remain trustworthy source-of-truth assets.
- Derived artifacts must be stored separately from originals.
- Cleanup and deletion policies must be deliberate and explicit.
