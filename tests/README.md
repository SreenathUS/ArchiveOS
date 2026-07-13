# Test Strategy

## Unit tests
- config loading
- duplicate decision logic
- migration behavior
- importer registry

## Integration tests
- normal import dry-run
- corrupt zero-byte input reporting
- rerun/resume-like dry-run stability

These tests intentionally use tiny synthetic datasets so pipeline regressions can be caught without running against the real archive.
