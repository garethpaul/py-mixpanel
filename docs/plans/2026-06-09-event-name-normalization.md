# Event Name Normalization

Status: Completed

## Context

`track` rejected blank event names, but nonblank names with surrounding
whitespace were sent exactly as provided. Tokens, API keys, and `distinct_id`
values are already trimmed, so event names should use the same predictable
normalization before payload construction and callback execution.

## Objectives

- Trim event names after validation and before Mixpanel payload encoding.
- Ensure callbacks receive the same normalized event name as the sent payload.
- Keep deterministic Python 2 coverage for the normalization behavior.
- Add a static `make build` alias for the legacy mocked verification gate.
- Document the completed guard in README, SECURITY, VISION, and CHANGES.

## Work Completed

- Normalized event names with `event.strip()` after the nonblank event check.
- Added mocked coverage asserting payload and callback event names are trimmed.
- Added `make build` as a static test alias and routed `verify` through lint,
  test, build, and docs.
- Updated repository documentation and maintenance notes.

## Verification

- Red `make test` with the event-name trimming regression.
- `make lint`
- `make test`
- `make build`
- `make docs`
- `make check`
- `git diff --check`
