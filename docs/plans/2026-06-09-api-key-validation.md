# EventTracker API Key Validation

## Status: Completed

## Context

`EventTracker` uses `api_key` only for Mixpanel import calls. Blank or
non-string API keys could still be accepted by the constructor and later become
import request URL parameters without a usable credential.

## Goals

- Preserve token-only tracking without requiring an API key.
- Reject non-string and blank API keys when callers provide one.
- Trim surrounding whitespace for valid API keys.
- Cover constructor API-key validation with mocked Python 2 tests.
- Document the behavior in README, VISION, and CHANGES.

## Work Completed

- Added `test_tracker_requires_nonblank_api_key_when_provided`.
- Updated `EventTracker.__init__` to validate and trim provided API keys.
- Documented the constructor API-key boundary in the project docs.

## Verification

- `python2 -m unittest test_mixpanel`
- `make check`
- `make verify`
- `git diff --check`
