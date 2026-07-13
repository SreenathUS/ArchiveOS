# ArchiveOS Engineering Rules

Status: Mandatory
Applies to: all contributors and automation

## 1. Preservation and Integrity Rules

1. Original media is immutable.
- Importers and pipeline stages must never alter source bytes.

2. No deletion before successful verification.
- Source deletion, if ever enabled, requires successful verification of destination integrity.

3. SHA-256 is the verification authority.
- Integrity and duplicate trust decisions must be based on SHA-256 outcomes.

4. No silent overwrite.
- Existing destination files must never be overwritten without explicit collision handling and audit trail.

## 2. Schema and Data Rules

5. Every schema change requires a migration.
- No direct ad-hoc schema mutation in feature code.
- Migration files must be versioned and ordered.

6. Catalog changes require compatibility consideration.
- Backward compatibility path must be defined for active user databases.

7. Reports must be deterministic.
- Given the same input and configuration, report semantics must remain reproducible.

## 3. Testing Rules

8. Every new feature requires at least one integration test.
- Unit tests alone are insufficient for pipeline behavior changes.

9. Every bug fix requires a regression test where practical.
- The test should fail before the fix and pass after the fix.

10. No merge without passing tests.
- Local/CI test suite must pass before integrating changes.

## 4. Operational Rules

11. Logs must have explicit levels.
- Use `DEBUG`, `INFO`, `WARNING`, `ERROR` appropriately.

12. Logs and reports must be reproducible.
- Avoid non-deterministic free-form output when structured fields are possible.

13. Every import must produce immutable artifacts.
- At minimum: manifest, verification summary, missing/duplicate reporting, and run log.

14. Quarantine is authoritative for problematic files.
- Corrupt, zero-byte, and suspicious files must not be mixed into verified storage.

## 5. Design and Change Control Rules

15. ADRs govern architectural decisions.
- Accepted ADRs override informal design discussions.

16. Architecture changes require explicit rationale.
- Significant changes must update architecture docs and relevant ADRs.

17. Avoid feature creep during stabilization windows.
- During milestone stabilization, prioritize reliability, correctness, and observability over new capability.
