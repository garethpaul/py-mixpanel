# Callback Validation

## Status: Completed

## Context

`py-mixpanel` accepts optional callbacks for synchronous and asynchronous
tracking. Before this guard, a non-callable callback could allow a synchronous
request to send before raising, and `track_async` could push the failure into
the worker path after a thread had already started.

## Objectives

- Reject non-callable callbacks before HTTP requests are opened.
- Reject non-callable callbacks before async worker threads are started.
- Preserve valid callback behavior for `track` and `track_async`.
- Keep coverage deterministic under the existing Python 2 mocked test suite.

## Work Completed

- Added a shared callback validator.
- Called it from both `track` and `track_async`.
- Added mocked tests for synchronous request prevention and async thread
  prevention.
- Extended the repository baseline script and maintenance documentation.

## Verification

- `python2 -m unittest test_mixpanel`
- `make check`
- `make verify`
- `git diff --check`
