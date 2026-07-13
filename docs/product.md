# ArchiveOS Product Definition

## What is ArchiveOS?

ArchiveOS is a personal digital archive system for importing, verifying, organizing, and cataloging media and related files from cameras, phones, exported cloud archives, and other sources.

Its primary purpose is to provide a trustworthy long-term archive for original media while preserving provenance, verification evidence, and searchable metadata.

## Problems it solves

- Safely importing media from removable devices and filesystem sources.
- Verifying copied media with cryptographic hashes.
- Preserving source provenance through immutable import manifests.
- Organizing verified media into a stable archive layout.
- Cataloging media metadata in a queryable SQLite database.
- Quarantining corrupt, zero-byte, and suspicious files without polluting the main archive.

## Non-goals for v0.1-alpha

- Cloud sync or multi-user collaboration.
- AI tagging, face recognition, OCR, or semantic search.
- Full photo editing workflow.
- Public or internet-facing deployment.
- Destructive modification of original media contents.

## Expected workflow

1. A source device or folder is scanned by an importer.
2. Files are copied into the archive pipeline with verification.
3. Metadata is extracted from verified files.
4. File and import records are stored in the catalog.
5. Duplicate decisions are recorded.
6. Valid media is placed into the verified archive layout.
7. Corrupt or suspicious files are redirected to quarantine.
8. Immutable reports are written for the import.

## What does "verified" mean?

A file is verified when the destination copy has been checked against the source using the configured hash algorithm and the digests match.

For v0.1-alpha, the expected algorithm is SHA-256.

## What is an Import?

An Import is one immutable ingestion event from a specific source root into the archive.

An Import has:

- a unique import name
- a start time
- a source root
- an archive root
- a manifest
- verification and duplicate reports
- a status

## What is a Media object?

A Media object is the catalog representation of one file tracked by ArchiveOS.

It stores:

- source and destination paths
- file size and hash
- capture date and metadata source
- media kind (RAW, JPG, Video, Sidecar)
- camera and lens metadata when available
- verification state
- duplicate grouping metadata

## What is an Event?

An Event is a logical grouping of media representing a real-world shoot, outing, trip, or occasion.

Events are a planned catalog concept. They are not yet a stable v0.1-alpha entity.

## What is an Album?

An Album is a user-curated grouping of media that may span multiple Events or Imports.

Albums are a planned catalog concept. They are not yet a stable v0.1-alpha entity.

## Release positioning

The current system should be treated as v0.1.0-alpha until multiple real imports complete without requiring structural changes.
