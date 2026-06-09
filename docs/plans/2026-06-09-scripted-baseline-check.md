# Scripted Baseline Check

## Status: Completed

## Context

The repository had a Makefile gate for Python 2 syntax, mocked tests, and
completed plan metadata, but it did not have a scriptable repository baseline
guard or ignore rules for local environment files and common editor metadata.

## Objectives

- Keep `make check` as the root verification command.
- Add a script-level baseline guard for required repository files.
- Check completed docs-plan metadata without needing to inspect the Makefile
  loop.
- Keep local secrets and editor metadata out of the legacy Python sample.

## Work Completed

- Added `scripts/check-baseline.sh`.
- Wired the script into `make check` after the existing verification gate.
- Added `.env`, `.env.*`, `.idea/`, `.vscode/`, and `*.iml` ignore rules.
- Updated README, VISION, and CHANGES.

## Verification

- `scripts/check-baseline.sh`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Add modern Python packaging metadata only in a dedicated compatibility pass.
- Add a Python 3 migration plan if the wrapper is revived beyond the archived
  Python 2 baseline.
