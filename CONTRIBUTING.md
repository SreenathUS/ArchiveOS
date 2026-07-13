# Contributing

## Development workflow
1. Keep features frozen during stabilization milestones.
2. Add tests first for regressions or new behavior.
3. Run full test suite locally before proposing changes.
4. Update `CHANGELOG.md` and architecture docs for significant changes.

## Local checks
```bash
cd /home/sunntiha/githubCopilotWspace/archiveos
python3 -m py_compile archiveos/*.py archiveos/*/*.py
python3 -m unittest discover -s tests -v
```
