# Event Name Validation

## Status: Completed

## Context

`EventTracker.track` already rejects missing `distinct_id` values before
building a Mixpanel request, and the constructor rejects blank project tokens.
Blank or non-string event names still reached payload construction even though
they are not useful analytics events.

## Goals

- Reject blank or non-string event names before building Mixpanel request URLs.
- Preserve caller-provided property dictionaries when validation fails.
- Cover the validation behavior with mocked Python 2 tests.
- Document the guard with the existing request-validation notes.

## Work Completed

- Added explicit `ValueError` validation for event names in `track`.
- Added mocked test coverage proving blank event names do not trigger requests
  or mutate caller properties.
- Updated README, VISION, SECURITY, and CHANGES notes for the validation guard.

## Verification

- `python2 -c "import py_compile; py_compile.compile('mixpanel.py', cfile='/tmp/py-mixpanel-mixpanel.pyc', doraise=True)"`
- `python2 -c "import py_compile; py_compile.compile('test_mixpanel.py', cfile='/tmp/py-mixpanel-test_mixpanel.pyc', doraise=True)"`
- `python2 -m unittest test_mixpanel`
- `make check`
- `git diff --check`
