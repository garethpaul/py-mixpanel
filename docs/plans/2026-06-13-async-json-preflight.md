# Async JSON Serialization Preflight

Status: Completed

## Problem

`track_async` rejects invalid event names, callbacks, property containers, and
distinct IDs before creating a worker. JSON-incompatible nested property values
still reach `json.dumps` only inside the started thread, so callers can receive
a thread while the deterministic `TypeError` is raised in the background and
no request is sent.

## Plan

1. Validate the normalized event and copied caller properties with the same
   standard-library JSON encoder before importing or constructing a thread.
2. Preserve the existing synchronous encoding path, project-token authority,
   timestamp assignment inside `track`, callback behavior, and request format.
3. Add a mocked Python 2 regression proving unsupported nested values raise
   synchronously and create neither a worker nor a request.
4. Protect the implementation, regression, documentation, completed status,
   and exact verification evidence in the fail-closed baseline checker.
5. Run host and digest-pinned Python 2.7.18 verification without live network
   calls or credentials.

## Compatibility Boundary

- Keep `track` and `track_async` signatures and valid return behavior unchanged.
- Do not move timestamp calculation out of the worker or pre-enrich caller
  properties with the configured token.
- Preserve Python 2.7 compatibility and add no dependencies.
- Do not log, persist, or send invalid analytics property values.

## Verification

- `python2 test_mixpanel.py`
- `sh scripts/check-baseline.sh`
- `make lint`, `make test`, `make build`, `make docs`, `make verify`, and
  `make check`
- digest-pinned Python 2.7.18 container `make check`
- hostile mutations covering preflight removal, ordering, no-thread/no-request
  assertions, documentation, completed status, and evidence
- workflow parse, exact-base protected-file, secret, generated-artifact, and
  `git diff --check` gates

## Work Completed

- Added a validation-only standard-library JSON serialization pass after async
  event/property normalization and before worker-thread import or construction.
- Preserved project-token and timestamp enrichment inside `track`, so valid
  asynchronous payload and callback timing remain unchanged.
- Added a Python 2 regression proving a nested unsupported value raises
  `TypeError` synchronously with no worker and no request.
- Added fail-closed implementation, ordering, test, documentation, completed
  status, and verification-evidence contracts.

## Verification Results

- `python2 test_mixpanel.py` passed all 22 mocked tests.
- Canonical `make check` passed on the host and in the network-disabled,
  digest-pinned Python 2.7.18 container with a read-only source mount.
- Eight hostile mutations covering preflight removal and ordering, JSON
  validation, regression identity, no-worker evidence, documentation, and
  completed plan status were rejected, including exact-evidence drift.
- Workflow YAML parsing, exact-base protected-file comparison, added-line
  secret scanning, generated-artifact scanning, and `git diff --check` passed.
