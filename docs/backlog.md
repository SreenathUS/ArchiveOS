# ArchiveOS Usage Backlog

Purpose: capture evidence from real-world imports and operations.

Scope: this backlog prioritizes observed friction, correctness risks, and operational pain points over speculative feature requests.

## Entry Template

- Import source:
- Date:
- Issue:
- Impact:
- Reproduction steps:
- Proposed improvement:
- Priority: `P0` | `P1` | `P2` | `P3`
- Status: `open` | `triaged` | `in_progress` | `blocked` | `done`

## Triage Guidance

- `P0`: integrity/provenance risk or data-loss risk.
- `P1`: major operational blocker.
- `P2`: workflow friction with moderate impact.
- `P3`: minor improvement or polish.

## Backlog Items

### BL-0001
- Import source: Sony A6700 SD import
- Date: 2026-07-09
- Issue: Zero-byte placeholder files from failed historical session contaminate source tree scans.
- Impact: High error volume, noisy reports, slower triage.
- Reproduction steps: Run dry-run import over source containing `Session_0001.../Photos` with zero-byte files.
- Proposed improvement: Add source-path exclusion policy and explicit legacy session filtering in importer config.
- Priority: P1
- Status: open
