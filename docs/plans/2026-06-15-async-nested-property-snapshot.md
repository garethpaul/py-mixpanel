# Snapshot Nested Async Properties

Status: Completed

## Context

`track_async` validates and shallow-copies the caller's property dictionary
before constructing a worker. Nested lists and dictionaries remain shared with
the caller, so a mutation after `track_async` returns but before the worker
serializes the event can change the outbound analytics payload and callback
values after preflight has already succeeded.

## Requirements

- R1. Detach all nested caller property values before worker construction.
- R2. Preserve Python 2.7-compatible JSON values, callback behavior, project
  token authority, generated timestamps, and caller dictionary immutability.
- R3. Reject copy or serialization failures synchronously before creating a
  worker or opening a network request.
- R4. Prove mutations made after `track_async` returns cannot change the
  worker's payload or callback snapshot.
- R5. Add mutation-sensitive baseline contracts and truthful completed
  verification evidence.
- R6. Preserve dependencies, workflows, public signatures, and request URLs.

## Technical Decision

Create a recursive snapshot with the Python standard library's `copy.deepcopy`
after normalizing the outer dictionary and before JSON preflight. Deep copying
preserves the existing Python value shapes used by callbacks while detaching
nested mutable containers. JSON validation then runs against the detached
snapshot before worker construction.

## Implementation Units

### U1. Detach async properties

- **Files:** `mixpanel.py`
- Import the standard `copy` module and deep-copy normalized async properties
  before serialization validation and thread creation.
- Keep synchronous `track` behavior unchanged.

### U2. Add deferred-worker regression coverage

- **Files:** `test_mixpanel.py`
- Use a deterministic worker double whose `start` method records startup but
  defers target execution.
- Mutate nested caller data after `track_async` returns, run the worker, and
  require the original nested values in both the encoded payload and callback.
- Require the caller's mutation to remain visible only in its own object.

### U3. Protect the contract and evidence

- **Files:** `scripts/check-baseline.sh`,
  `docs/plans/2026-06-15-async-nested-property-snapshot.md`, and canonical
  maintenance documentation.
- Require deep-copy ordering before JSON validation and worker construction,
  executable deferred-worker assertions, caller isolation, and completed
  verification evidence.
- Reject isolated mutations that remove the snapshot, move it after preflight,
  bypass the deferred worker, weaken payload or callback assertions, or restore
  provisional plan language.

## Verification Results

- 26 Python 2.7 tests passed, including the deferred-worker nested mutation,
  synchronous copy-failure regression, and all existing request, callback,
  credential, and response boundaries.
- Root and absolute Makefile `make check` passed from the repository and an
  unrelated caller directory.
- The complete gate passed in the network-disabled, read-only,
  digest-pinned Python 2.7.18 hosted image.
- Twelve isolated hostile mutations were rejected across snapshot presence and
  depth, ordering, worker deferral, caller mutation, payload and callback
  assertions, documentation, and completed plan evidence.
- Final generated-artifact, added-credential, conflict-marker, dependency,
  workflow, protected-path, and `git diff --check` audits passed.

## Risks

- `copy.deepcopy` may raise for unusual custom objects. This is intentionally a
  synchronous preflight failure before a thread or request exists, matching the
  existing fail-fast async validation posture.
- The snapshot prevents caller-side nested mutation races; it does not make
  callback code itself thread-safe.
