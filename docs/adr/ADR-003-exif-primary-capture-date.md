# ADR-003: EXIF As Primary Capture Date Source

## Status
Accepted

## Context
ArchiveOS should organize media by when it was captured, not when it was copied.

## Decision
Use EXIF capture metadata as the primary source of capture date. Allow mtime fallback only when explicitly configured.

## Consequences
- Organization reflects real-world capture chronology.
- Archive layout remains stable even if import happens much later.
- Bad or missing EXIF requires fallback or quarantine handling.
