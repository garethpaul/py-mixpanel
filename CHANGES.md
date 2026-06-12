# Changes

## 2026-06-12

- Added strict validation for Mixpanel's plain-text success acknowledgement.
- Rejected failed, empty, whitespace-only, and unexpected response bodies with
  a stable `MixpanelError` before invoking success callbacks.
- Added mocked coverage proving responses close on every acknowledgement path.

## 2026-06-10

- Added read-only hosted verification in a digest-pinned Python 2.7.18
  container without skipping legacy tests, with credential-free checkout and
  manual dispatch support.
- Made tracked local metadata inspection fail closed when Git cannot inspect
  the checkout.
- Extended the scripted baseline to require the hosted workflow and completed
  CI plans while rejecting weakened workflow contracts.
- Added callback validation so non-callable callbacks fail before HTTP
  requests or async worker threads start.
- Closed Mixpanel HTTP responses after successful and failed reads to prevent
  repeated tracking from leaking network resources.

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
