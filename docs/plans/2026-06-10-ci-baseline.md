# Py Mixpanel CI Baseline

## Status: Completed

## Context

`py-mixpanel` has a local `make check` baseline for a Python 2 analytics
wrapper. The repository needs a lightweight GitHub Actions gate that can run
static repository checks on hosted runners while keeping Python 2 mocked HTTP
tests active when that interpreter is available.

## Objectives

- Run the existing repository baseline in GitHub Actions.
- Keep Python 2 syntax and mocked HTTP tests active when Python 2 is present.
- Make missing Python 2 a clear CI skip instead of a hosted-runner failure.
- Make the CI workflow presence part of the scripted baseline contract.

## Work Completed

- Added `.github/workflows/check.yml` to run `make check` on pushes, pull
  requests, and manual dispatches.
- Set up Python 3.12 in CI for the scripted repository baseline guard.
- Guarded Python 2 syntax and mocked HTTP tests so they run when `python2` is
  installed and report clear skips otherwise.
- Extended `scripts/check-baseline.sh` to require the CI workflow and this
  completed plan.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `scripts/check-baseline.sh`
- `git diff --check`

## Follow-Up Candidates

- Add a pinned Python 2 job only if the repository is intentionally revived
  with a documented legacy interpreter source.
