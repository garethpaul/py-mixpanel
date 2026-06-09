# Changes

## 2026-06-09

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
