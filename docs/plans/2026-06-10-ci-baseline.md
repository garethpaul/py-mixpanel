# Py Mixpanel CI Baseline

## Status: Completed

## Context

`py-mixpanel` has a local `make check` baseline for a Python 2 analytics
wrapper. Hosted validation must run that complete legacy gate rather than
silently skipping syntax or mocked HTTP tests on a modern runner.

## Objectives

- Run the existing repository baseline in a pinned Python 2.7 environment.
- Keep syntax checks and all mocked HTTP tests mandatory.
- Limit workflow permissions and prevent checkout credential persistence.
- Make the CI workflow structure part of the scripted baseline contract.

## Work Completed

- Added `.github/workflows/check.yml` to run `make check` on pushes, pull
  requests, and manual dispatches in the digest-pinned official Python 2.7.18
  image.
- Pinned checkout by commit, disabled credential persistence, set read-only
  contents permission, bounded runtime, and cancelled superseded runs.
- Kept Python 2 syntax and mocked HTTP tests mandatory locally and in CI.
- Extended `scripts/check-baseline.sh` to require the workflow and completed CI
  plans and reject duplicate checkout steps, permission escalation, floating
  actions or images, skipped tests, and allowed failures.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `scripts/check-baseline.sh`
- hostile workflow mutation checks
- `git diff --check`

## Follow-Up Candidates

- Replace Python 2 only as an explicit compatibility migration with equivalent
  request, callback, acknowledgement, and cleanup coverage.
