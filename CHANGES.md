# Changes

## 2026-06-26 - P2 - Bound asynchronous shutdown ownership

- Made `track_async` workers daemon threads before launch so best-effort
  analytics cannot hold interpreter shutdown for the network timeout.
- Preserved the returned thread handle so callers can explicitly `join()` when
  an event attempt must finish before exit.
- Added focused regression and hostile mutation coverage plus operator guidance.

## 2026-06-26 06:48 - P2 - Reconcile hosted verification evidence

### Summary

Replaced stale pre-merge placeholders in the latest completed maintenance
record with the exact hosted and post-merge verification evidence.

### Work completed

- Recorded successful hosted Python 2.7, Python 3.11, Python 3.14, Actions
  CodeQL, and Python CodeQL checks on the reviewed implementation head.
- Recorded successful post-merge Check and CodeQL runs on merge commit
  `9f08738403600ab22050b88d814484cafa132e6f`.
- Removed the already-completed local/hosted validation next action.
- Added a baseline contract preventing merged runtime/privacy records from
  retaining pending evidence or completed next actions.

### Threads

- None; this reconciles authoritative hosted state only.

### Files changed

- `CHANGES.md` and the runtime/privacy plan — exact verification evidence.
- `scripts/check-baseline.sh` — stale-evidence regression contract.
- `docs/plans/2026-06-25-hosted-evidence-reconciliation.md` — completed record.

### Validation

- Red baseline failed on the stale pending evidence before documentation edits.
- Current Python and pinned Python 2.7 `make check` evidence is recorded in the
  completed reconciliation plan.

## 2026-06-26 06:28 - P1 - Define runtime, consent, and identity assumptions

### Summary

Closed both remaining documentation priorities with one contract-enforced guide
for legacy API compatibility and privacy-safe analytics operation.

### Work completed

- Documented Python 2.7 and hosted Python 3.11/3.14 compatibility.
- Documented fixed US endpoints, legacy form tracking, response acknowledgement
  limits, and missing retry/batching/region/deduplication features.
- Marked query-based import authentication as legacy and noted Service Accounts
  for new integrations.
- Added consent, opt-out, minimization, retention, deletion, and pseudonymous
  distinct-ID guidance.

### Threads

- Started: runtime/privacy operator guide.
- Continued: continuous open-source maintenance loop.
- Stopped: none.

### Files changed

- `USAGE_AND_PRIVACY.md` — runtime, API, consent, and identity boundaries.
- `README.md`, `SECURITY.md`, `VISION.md` — links and roadmap state.
- `scripts/check-baseline.sh` — durable guide contract.
- `docs/plans/2026-06-25-runtime-consent-assumptions.md` — completed plan.
- `CHANGES.md` — this cycle record.

### Validation

- Red baseline — failed for the missing guide before documentation was added.
- Current Python and pinned Python 2.7 `make check` — each passed 42 unit tests,
  56 Make authority cases, 10 transport mutations, and the baseline contract.
- Fourteen isolated guide mutations — all rejected across runtime, endpoint,
  consent, identity, acknowledgement, feature, import, link, roadmap, and plan boundaries.
- Reviewed head `b7f1d0cf09b56875d4edc421c1146bae2d2112b6`
  passed hosted Python 2.7, Python 3.11, Python 3.14, Actions CodeQL, Python
  CodeQL, and the aggregate CodeQL check.
- Merge commit `9f08738403600ab22050b88d814484cafa132e6f`
  subsequently passed post-merge Check run `28221119276` and CodeQL run
  `28221118794`.

### Bugs / findings

- P1: Existing docs did not warn that response `1` is not token validation or
  that blind retries can duplicate events without `$insert_id` support.
- P1: Existing docs required `distinct_id` but did not define consent ownership,
  pseudonymity, environment scoping, or identifier lifecycle responsibilities.

### Blockers

- No live Mixpanel credentials or calls are required; API behavior is documented
  from source and official references, not integration-tested here.

### Next action

- None for this completed documentation cycle; future work requires a
  reproduced source defect, official API change, or reviewed caller need.

## 2026-06-25

- Verified token-only track events use HTTPS POST form bodies so event names,
  project tokens, distinct IDs, properties, and large payloads stay out of URLs.
- Preserved the legacy authenticated import request path and Python 2.7 support,
  with 42 unit tests and 10 hostile transport and isolation mutations.

## 2026-06-21

- Moved token-only `/track/` calls from credential-bearing GET query strings to
  HTTPS POST form bodies while preserving payload encoding, callbacks, timeout,
  response parsing, Python 2.7 compatibility, and the legacy `/import/` path.
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
