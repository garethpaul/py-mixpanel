# Async Callback Test

## Status

Completed

## Context

`py-mixpanel` has mocked coverage for synchronous track and import requests,
but `track_async` still needs deterministic coverage. The method imports
`threading.Thread` at call time, so tests can patch the thread constructor with
a synchronous fake and avoid flakiness or live network calls.

## Objectives

- Verify `track_async` starts a thread-like worker and returns it.
- Verify async tracking sends the same HTTPS payload shape as `track`.
- Verify callbacks receive the event and enriched properties.
- Keep the test under Python 2 and the existing `make verify` gate.

## Verification

- `python2 -m unittest test_mixpanel`
- `make verify`
- `git diff --check`
