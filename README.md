# py-mixpanel

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/py-mixpanel` is a public sample, documentation, or utility project. Track events with mixpanel

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Python (1).

## Repository Contents

- `README.md` - project overview and local usage notes
- `.github/workflows/check.yml` - pinned Python 2.7 hosted `make check` gate
- `CHANGES.md` - notable maintenance changes
- `Makefile` - local verification entry points
- `docs/plans` - canonical completed maintenance plans
- `plans` - completed maintenance plans
- `scripts/check-baseline.sh` - repository maintenance baseline guard
- `test_mixpanel.py` - mocked HTTP regression tests
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: no top-level source directories detected
- Dependency and build manifests: Makefile
- Entry points or build surfaces: mixpanel.py, Makefile
- Test-looking files: test_mixpanel.py

## Getting Started

### Prerequisites

- Git
- Python 2.7 or a supported Python 3 runtime and `make`

### Setup

```bash
git clone https://github.com/garethpaul/py-mixpanel.git
cd py-mixpanel
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

Read [`USAGE_AND_PRIVACY.md`](USAGE_AND_PRIVACY.md) before using real tokens,
events, or distinct IDs. It documents the Python/runtime boundary, fixed legacy
API assumptions, acknowledgement limits, consent ownership, and pseudonymous
identifier guidance.

- Import `EventTracker` from `mixpanel.py`.
- Construct `EventTracker` with a nonblank Mixpanel project token; surrounding
  whitespace is trimmed and blank tokens raise `ValueError`.
- Provide `api_key` only for import calls; when present it must be a nonblank
  string and surrounding whitespace is trimmed.
- Call `track(event, properties)` only after the caller has explicit consent and a caller-provided `distinct_id`.
- Event names must be nonblank strings; blank or non-string event names raise
  `ValueError` before any HTTP request.
- Surrounding whitespace is trimmed from event names before payload encoding
  and callback execution.
- Event properties must be dictionaries.
- Calls without a nonblank string `distinct_id` raise `ValueError` before any
  HTTP request.
- Caller-provided properties are copied before the tracker adds `token` or
  `time`, so validation and payload enrichment do not mutate application data.
- The configured project token is authoritative for outbound payloads; a
  caller property cannot redirect an event to another Mixpanel project.
- Token-only tracking sends an HTTPS `POST` to `/track/` with the encoded event
  in an `application/x-www-form-urlencoded` request body. The request URL does
  not contain `data`, the project token, distinct ID, event name, or properties.
- The optional `api_key` path still uses the repository's legacy `/import/`
  query-string request and is intentionally unchanged by the `/track/`
  transport correction. Modern service-account import support remains separate
  design work.
- Mixpanel HTTP requests use a ten-second timeout by default.
- Opened Mixpanel HTTP responses are closed after reads succeed or fail so
  repeated tracking does not leak network resources.
- Tracking succeeds only when Mixpanel returns a stripped plain-text `1`
  acknowledgement. Rejected, empty, or unexpected bodies raise `MixpanelError`
  before the success callback runs.
- Use `track_async` only when background submission is expected by the caller.
- `track_async` returns a daemon worker so best-effort analytics cannot hold
  interpreter shutdown; call `join()` on the returned thread when delivery must
  complete before process exit.
- Callbacks must be callable when provided; invalid callbacks raise
  `ValueError` before HTTP requests or async worker threads are started.
- Invalid async event names, property containers, and distinct IDs raise
  `ValueError` before a worker thread is constructed or a request is opened.
- JSON-incompatible async properties raise `TypeError` before a worker thread
  is constructed or a request is opened.
- Nested async properties are detached before worker construction, so later
  caller mutations cannot change the submitted payload or callback snapshot.
- Nested built-in and subclassed dictionaries, lists, and tuples are copied to
  a plain JSON tree without dispatching overridable container methods. Cycles
  and unsupported objects fail before network or worker activity.
- Async workers snapshot the configured project token and optional API key
  before launch, so later tracker mutation cannot redirect queued events.
- Transport, HTTP-status, read, and cleanup failures raise a stable error
  without returning credential-bearing URLs or upstream details.
- Synchronous serialization and async preflight reject `NaN`, positive
  infinity, and negative infinity before a request or worker is created.

## Testing and Verification

- Run `make check` before committing changes.
- Run `make build` for the static legacy verification gate; it uses the same
  mocked Python 2 tests as `make test`.
- Run `scripts/check-baseline.sh` for the SDK-free repository baseline guard.
- `make check` compile-checks the selected Python runtime, runs mocked HTTP
  tests, rejects hostile source mutations, and verifies completed plans. Use
  `make PYTHON=python3 check` for Python 3 locally.
- The baseline script checks required files, completed docs-plan metadata,
  verification documentation, and local secret/editor metadata hygiene.
- The baseline script also rejects local `.pyc` files and `__pycache__`
  directories after the mocked Python 2 tests run.
- Request validation coverage includes nonblank project tokens, API keys when
  provided, event names, properties dictionaries, and nonblank caller-provided
  distinct IDs.
- GitHub Actions runs the complete gate on pushes, pull requests, and manual
  dispatches in the official Python 2.7.18 image pinned by digest and on clean
  Python 3.11 and 3.14 runners. The workflow uses read-only repository
  permissions and credential-free checkout.

All automated HTTP behavior is fake. There is no live Mixpanel request in the
verification suite, so provider authentication, schema, availability, and
production delivery remain unverified.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- Detected references to Mixpanel. Keep API keys, OAuth credentials, tokens, and account-specific values in local configuration only.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include mixpanel.py.
- Review changes touching external API calls or credential-adjacent configuration; examples from the scan include mixpanel.py.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include mixpanel.py.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include mixpanel.py.
- Event validation rejects blank event names before analytics payloads are
  encoded or sent.
- Event validation trims surrounding whitespace before analytics payloads are
  encoded or callbacks run.
- Constructor validation rejects blank API keys before import request URLs are
  built.
- Tracking validation rejects non-dict properties and blank distinct IDs before
  analytics payloads are encoded or sent.
- Callback validation rejects non-callable callbacks before analytics payloads
  are sent or async worker threads are started.
- Successful synchronous and asynchronous callbacks receive
  credential-free callback properties captured before the configured project
  token and any generated timestamp are added to the outbound payload.
- Dict-subclass property isolation canonicalizes the top-level mapping without
  virtual `copy()` dispatch, so caller data and callbacks remain token/time-free.
- The configured project token is captured before async worker launch, and
  successful calls receive an independent credential-free callback snapshot.
- Stable errors, HTTP status checks, and bounded response cleanup prevent
  provider or credential details from escaping through exceptions.

## Maintenance Notes

- Make gates reject caller-controlled `MAKEFILE_LIST` and `REPO_ROOT` values
  before running legacy or modern Mixpanel validation.

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-py-mixpanel-baseline.md` for the canonical
  mocked Mixpanel tracking baseline.
- See `docs/plans/2026-06-08-request-validation-and-timeout.md` for the
  distinct ID and request-timeout guard baseline.
- See `docs/plans/2026-06-08-request-error-coverage.md` for the mocked request
  failure behavior baseline.
- See `docs/plans/2026-06-09-caller-property-isolation.md` for caller-property
  mutation coverage.
- See `docs/plans/2026-06-09-token-validation.md` for constructor token
  validation coverage.
- See `docs/plans/2026-06-09-api-key-validation.md` for constructor API-key
  validation coverage.
- See `docs/plans/2026-06-09-event-name-validation.md` for event-name
  validation coverage.
- See `docs/plans/2026-06-09-event-name-normalization.md` for event-name
  normalization coverage and the static `make build` alias.
- See `docs/plans/2026-06-09-distinct-id-validation.md` for properties and
  distinct ID validation coverage.
- See `docs/plans/2026-06-09-scripted-baseline-check.md` for the scripted
  repository baseline guard and local secret/editor metadata ignores.
- See `docs/plans/2026-06-09-bytecode-free-verification.md` for the
  bytecode-free legacy verification guard.
- See `docs/plans/2026-06-10-ci-baseline.md` for the integrated hosted CI
  contract and workflow mutation coverage.
- See `docs/plans/2026-06-10-callback-validation.md` for the callback
  validation guard.
- See `docs/plans/2026-06-10-hosted-legacy-validation.md` for digest-pinned,
  full Python 2.7 hosted verification and fail-closed metadata checks.
- See `docs/plans/2026-06-10-response-close-guard.md` for deterministic HTTP
  response cleanup on successful and failed reads.
- See `docs/plans/2026-06-12-response-acknowledgement-validation.md` for strict
  Mixpanel acceptance checks before callbacks.
- See `docs/plans/2026-06-12-response-body-size-boundary.md` for bounded
  response reads before acknowledgement validation.
- See `docs/plans/2026-06-13-project-token-authority.md` for the configured
  project token boundary on synchronous and asynchronous payloads.
- See `docs/plans/2026-06-13-async-json-preflight.md` for synchronous rejection
  of JSON-incompatible async properties before worker creation.
- See `docs/plans/2026-06-14-callback-token-isolation.md` for the callback
  credential-isolation boundary.
- See `docs/plans/2026-06-19-async-transport-boundary-review.md` for deep JSON
  snapshots, async credential ownership, transport cleanup, Python 2/3
  verification, and hostile mutations.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
