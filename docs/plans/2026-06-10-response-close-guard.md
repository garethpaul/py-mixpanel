# Mixpanel Response Close Guard

Status: Completed

## Context

`EventTracker.track` read the response returned by `urllib2.urlopen` but never
closed it. Repeated synchronous or asynchronous event submission could retain
network connections or file descriptors, and a response whose `read()` raised
would leak the resource on the failure path as well.

## Objectives

- Close every successfully opened Mixpanel HTTP response.
- Preserve request and response-read errors for callers.
- Keep callbacks skipped when reading a response fails.
- Cover successful and failed reads with deterministic Python 2 mocks.

## Work Completed

- Wrapped response reads in a `try`/`finally` block that always calls `close()`.
- Extended the fake response with close-state and read-error behavior.
- Added assertions for cleanup after successful tracking and failed reads.
- Added a baseline source guard and updated maintenance documentation.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python2 -m unittest test_mixpanel`
- `scripts/check-baseline.sh`
- `make check`
- Removed `resp.close()` in a mutation check and confirmed both response-close
  regressions rejected the change before the baseline guard ran.
- `git diff --check`
