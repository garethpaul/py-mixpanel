# Async Input Preflight Validation

Status: Completed

## Context

`track_async` validates callbacks before creating a worker, but event names,
properties, and `distinct_id` values are validated only after the new thread
starts. A caller can therefore receive a started thread for an invalid request
while the actual `ValueError` is raised only in the background worker.

## Priority

Invalid caller input is deterministic and should fail synchronously. Starting
a worker for a request that can never be sent makes failures easy to miss and
creates unnecessary thread activity without improving compatibility.

## Objectives

- Share event, properties, and distinct-ID preflight validation between
  synchronous and asynchronous tracking.
- Reject invalid async inputs before constructing or starting a thread.
- Preserve valid event normalization, property copying, callbacks, and request
  behavior.
- Add Python 2 regressions that prove invalid async inputs create no thread and
  open no network request.
- Protect the implementation, tests, docs, and completed plan in the baseline
  checker.

## Work Completed

- Extracted shared event-name and property preflight helpers from `track`.
- Applied the same preflight before `track_async` imports or constructs a
  worker thread.
- Added invalid event, property-container, and distinct-ID regressions proving
  no thread or network request is created.
- Updated the baseline checker and maintenance documentation.

## Verification

- `python2 -m unittest test_mixpanel`
- `sh scripts/check-baseline.sh`
- `make check`
- The focused Python 2 suite passed all 19 mocked tests.
- Two focused hostile mutations removed async preflight and its regression
  contract; the baseline checker rejected both.
- `git diff --check`
