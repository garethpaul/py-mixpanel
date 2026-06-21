# Changes

## 2026-06-21

- Hardened all seven pre-existing Make gates against `MAKEFILE_LIST` and
  `REPO_ROOT` redirection without changing Mixpanel transport behavior.

## 2026-06-19

- Canonicalized nested JSON properties through built-in container operations,
  rejecting cycles, hostile subclasses, unsupported objects, and non-finite
  values before requests or async worker creation.
- Snapshotted the configured project token and optional API key before async
  launch while preserving an independent credential-free callback snapshot.
- Added stable transport errors, HTTP status validation, primary-failure-safe
  cleanup, bounded response handling, Python 2/3 gates, and seven hostile
  mutations. There is no live Mixpanel request in automated verification.

## 2026-06-17

- Added dict-subclass property isolation so overridable `copy()` methods cannot
  alias project tokens or generated timestamps into caller or callback data.

## 2026-06-16

- Rejected `NaN`, positive infinity, and negative infinity during synchronous
  serialization and asynchronous JSON preflight before requests or workers.

## 2026-06-14

- Returned credential-free callback properties for synchronous and
  asynchronous success callbacks while retaining the configured project token
  and generated timestamp in outbound Mixpanel payloads.
- Detached nested async properties before worker construction so later caller
  mutations cannot alter the payload or callback snapshot.

## 2026-06-13

- Made the configured project token authoritative for synchronous and
  asynchronous payloads while preserving caller dictionaries and timestamps.
- Rejected JSON-incompatible async properties before constructing a worker
  thread or opening a Mixpanel request.

## 2026-06-12

- Added synchronous async-input preflight so invalid events, properties, and
  distinct IDs fail before worker creation.
- Added bounded response reads with a 1 KiB limit plus one overflow probe.
- Rejected oversized upstream bodies before acknowledgement validation or
  callbacks without exposing response content in errors.
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
