# Distinct ID Validation

Status: Completed

## Context

`track` already required a `distinct_id` key, but it accepted blank or non-string
identifiers and assumed caller-provided properties had a dictionary-like
`copy()` method. That could produce accidental runtime errors or malformed
analytics payloads before a caller noticed.

## Objectives

- Reject non-dict `properties` values with an explicit `ValueError`.
- Reject missing, blank, or non-string `distinct_id` values before request
  construction.
- Preserve ordinary dictionary properties and keep caller-property isolation.
- Add Python 2 mocked coverage for the new validation paths.

## Work Completed

- Added properties type validation and nonblank string `distinct_id` validation.
- Extended mocked tests for non-dict properties and invalid distinct IDs.
- Updated README, SECURITY, VISION, and CHANGES notes for the validation guard.

## Verification

- `python2 -m unittest test_mixpanel`
- `make check`
- `make verify`
- `git diff --check`
