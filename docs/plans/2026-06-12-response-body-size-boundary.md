# Mixpanel Response Body Size Boundary

## Status: Completed

## Context

`EventTracker.track` reads the complete Mixpanel response before validating the
legacy plain-text acknowledgement. A valid response only needs to contain `1`,
but an upstream or intermediary can otherwise force the legacy client to hold
an arbitrarily large body in memory.

## Priority

The response is untrusted network input. Bounding it before acknowledgement
validation limits memory exposure without changing request construction,
authentication, callback behavior, or the accepted success value.

## Requirements

- R1. Read at most 1 KiB plus one overflow-detection byte from a response.
- R2. Reject larger bodies with a stable `MixpanelError` that does not include
  response content.
- R3. Preserve response closure and suppress callbacks on oversized bodies.
- R4. Continue accepting a stripped acknowledgement of exactly `1`.
- R5. Keep mocked tests deterministic, bytecode-free, and Python 2.7
  compatible.
- R6. Protect the cap, bounded read, regression coverage, documentation, and
  completed plan evidence in `scripts/check-baseline.sh`.

## Scope Boundaries

- Do not change Mixpanel endpoints, authentication, payload encoding, timeout,
  or asynchronous execution.
- Do not add dependencies or migrate the Python runtime.
- Do not expose rejected response bodies in errors.

## Verification Plan

- `PYTHONDONTWRITEBYTECODE=1 python2 -m unittest test_mixpanel`
- `make lint`
- `make test`
- `make build`
- `make check`
- focused hostile mutations of the response-boundary contracts
- `git diff --check`

## Work Completed

- Added `MAX_RESPONSE_BODY_BYTES = 1024` and a shared bounded response reader
  that requests one additional byte to detect overflow.
- Added a stable, body-safe overflow error before acknowledgement validation.
- Preserved response closure and callback suppression for oversized bodies.
- Extended the fake response with requested-read-size tracking and added an
  oversized-body regression test.
- Updated the checker and maintenance documentation to protect bounded response
  reads.

## Verification Completed

- `PYTHONDONTWRITEBYTECODE=1 python2 -m unittest test_mixpanel` passed 18 tests.
- `make lint`, `make test`, and `make build` passed.
- `make check` passed with the full 18-test suite and repository checker.
- `sh -n scripts/check-baseline.sh` passed.
- `git diff --check` passed.
- All 11 focused hostile mutations were rejected from a passing baseline,
  covering the cap, cap value, bounded read, overflow byte, sanitized error,
  regression name, requested-read proof, body-safety proof, README contract,
  completed status, and verification evidence.
