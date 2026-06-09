# EventTracker Token Validation

## Status: Completed

## Context

`EventTracker` accepted `None`, empty strings, and whitespace-only tokens. Those
values could reach payload construction and produce Mixpanel requests without a
usable project token.

## Goals

- Reject non-string and blank project tokens in the constructor.
- Trim surrounding whitespace for valid tokens.
- Cover constructor validation with mocked Python 2 tests.
- Document the behavior in README, VISION, and CHANGES.

## Work Completed

- Added `test_tracker_requires_nonblank_token`.
- Updated `EventTracker.__init__` to validate and trim tokens.
- Added this completed plan under `docs/plans/`.

## Verification

- `python2 -m unittest test_mixpanel`
- `make check`
- `make verify`
- `git diff --check`
