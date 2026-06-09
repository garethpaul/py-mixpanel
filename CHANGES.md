# Changes

## 2026-06-09

- Added bytecode-free verification coverage for the legacy Python 2 tests.
- Added event-name normalization so surrounding whitespace is trimmed before
  payload encoding and callback execution.
- Added `scripts/check-baseline.sh` and local secret/editor ignore coverage for
  required files, completed plan metadata, and verification docs.
- Added a static `make build` gate for the legacy mocked verification flow.
- Added `EventTracker` API-key validation so blank import credentials are
  rejected before request URL construction.
- Added `EventTracker` token validation so blank project tokens are rejected
  before request construction.
- Added event-name validation so blank events are rejected before request
  construction.
- Added properties and distinct ID validation so non-dict properties and blank
  identifiers are rejected before request construction.
- Copied caller-provided event properties before validation and Mixpanel default
  enrichment so `track` no longer mutates application-owned dictionaries.

## 2026-06-08

- Added mocked request-error coverage so failed sends propagate and skip
  callbacks.
- Replaced `distinct_id` assert validation with an explicit `ValueError` and
  added default request timeout coverage.
- Added mocked Python 2 tests for `EventTracker.track` and API-key-backed import calls.
- Switched Mixpanel track/import endpoints from HTTP to HTTPS.
- URL-escaped the encoded payload and API key before building Mixpanel request URLs.
- Added `make verify` and `make check` for legacy syntax checks and mocked regression tests.
- Added deterministic `track_async` callback coverage using a fake thread and mocked HTTP request.
- Added canonical `docs/plans` coverage and made `make verify` require the
  completed baseline plan.
