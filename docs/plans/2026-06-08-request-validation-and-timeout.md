# Request Validation and Timeout

## Status: Completed

## Context

`py-mixpanel` already had mocked Python 2 coverage for track, import, and async
callback request construction. Two reliability gaps remained: `distinct_id`
validation used `assert`, which can be removed by optimized Python execution,
and outbound Mixpanel requests used `urllib2.urlopen` without an explicit
timeout.

## Objectives

- Preserve the existing `EventTracker.track` and `track_async` API shape.
- Reject events without a caller-provided `distinct_id` before any HTTP
  request is made.
- Add a default request timeout for tracking and import calls.
- Cover validation and timeout behavior in mocked Python 2 tests.
- Make docs plan verification cover every completed plan under `docs/plans`.

## Work Completed

- Added `REQUEST_TIMEOUT_SECONDS` and an `open_mixpanel_url` helper.
- Replaced assert-based `distinct_id` validation with an explicit
  `ValueError`.
- Updated track and import calls to use the timeout helper.
- Extended mocked tests to cover missing `distinct_id` and timeout arguments.
- Updated README, VISION, CHANGES, and the docs verification target.

## Verification

- `python2 -c "import py_compile; py_compile.compile('mixpanel.py', cfile='/tmp/py-mixpanel-mixpanel.pyc', doraise=True)"`
- `python2 -c "import py_compile; py_compile.compile('test_mixpanel.py', cfile='/tmp/py-mixpanel-test_mixpanel.pyc', doraise=True)"`
- `python2 -m unittest test_mixpanel`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Return or expose request errors instead of discarding response details.
- Document Mixpanel API assumptions and user-consent expectations in more
  detail.
