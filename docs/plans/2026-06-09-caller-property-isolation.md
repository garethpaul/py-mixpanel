# Caller Property Isolation

## Status: Completed

## Context

`EventTracker.track` enriched the caller-provided `properties` dictionary in
place by adding the project token and timestamp. That made outbound payload
construction visible to application-owned data structures and could also mutate
properties before validation rejected an event missing `distinct_id`.

## Objectives

- Preserve the existing `track(event, properties, callback)` API shape.
- Keep Mixpanel payload enrichment intact for outgoing requests.
- Avoid mutating caller-owned event property dictionaries.
- Cover both successful sends and validation failures with deterministic Python
  2 tests.

## Work Completed

- Copied caller-provided properties before validation and payload enrichment.
- Required `distinct_id` before adding token and timestamp defaults to the
  copied payload.
- Added mocked coverage proving caller dictionaries stay unchanged while the
  outbound payload still receives Mixpanel defaults.
- Updated README, VISION, SECURITY, and CHANGES notes for property isolation.

## Verification

- `python2 -c "import py_compile; py_compile.compile('mixpanel.py', cfile='/tmp/py-mixpanel-mixpanel.pyc', doraise=True)"`
- `python2 -c "import py_compile; py_compile.compile('test_mixpanel.py', cfile='/tmp/py-mixpanel-test_mixpanel.pyc', doraise=True)"`
- `python2 -m unittest test_mixpanel`
- `make check`
- `make verify`
- `git diff --check`
