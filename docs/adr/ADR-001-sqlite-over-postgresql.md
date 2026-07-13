# ADR-001: SQLite Over PostgreSQL

## Status
Accepted

## Context
ArchiveOS is currently a single-user local archival system operating on one workstation and local storage volumes.

## Decision
Use SQLite as the primary catalog database for v0.1-alpha.

## Consequences
- Simple deployment with no database server dependency.
- Good fit for local, single-user archival workflows.
- Easier backups and portability.
- Future migration to a server database remains possible if requirements change.
