# Py Mixpanel Baseline

## Status: Completed

## Context

`py-mixpanel` is a legacy Python 2 Mixpanel event tracker. Recent maintenance
added mocked request coverage, moved tracking/import endpoints to HTTPS,
escaped encoded request values, and covered `track_async` callback behavior
without live network calls.

## Objectives

- Preserve the `EventTracker.track` and `track_async` API shape.
- Keep tokens, API keys, distinct IDs, and event payloads caller-controlled.
- Verify tracking and import request construction with mocked HTTP calls.
- Keep deterministic tests on Python 2 to match the source.
- Record the completed baseline under `docs/plans`.

## Work Completed

- Added mocked Python 2 tests for track, import, and async callback behavior.
- Added `make check` and `make verify` wrappers.
- Extended `make verify` to require this canonical completed plan.

## Verification

- `make check`
- `make verify`
- `python2 -m unittest test_mixpanel`
- `git diff --check`

## Follow-Up Candidates

- Add mocked error-handling coverage.
- Return or expose request errors instead of discarding response details.
- Document Python version and Mixpanel API assumptions.
