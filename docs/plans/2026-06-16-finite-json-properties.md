# Require Finite JSON Properties

Status: Planned

## Context

Python 2.7's standard JSON encoder emits bare `NaN`, `Infinity`, and
`-Infinity` tokens by default. Those values are not valid JSON, but the current
sync serializer and async preflight accept them, allowing invalid analytics
payloads to reach worker construction or network access.

## Requirements

- Reject non-finite floating-point property values with the standard JSON
  encoder before opening a request.
- Reject asynchronous non-finite values synchronously before importing,
  constructing, or starting a worker.
- Apply the same strict JSON policy to validation and final payload encoding.
- Preserve nested property snapshots, project-token authority, generated
  timestamps, callbacks, valid numeric values, and caller-owned data.
- Add mutation-sensitive regressions for `NaN`, positive infinity, and negative
  infinity across synchronous and asynchronous entry points.

## Approach

- Pass `allow_nan=False` to the standard-library `json.dumps` calls used for
  async preflight and final event serialization.
- Extend the mocked Python 2 suite to require `ValueError` before requests,
  workers, or callbacks exist.
- Protect both strict serializer call sites, regression assertions,
  documentation, changelog, and completed evidence in the fail-closed baseline.

## Scope Boundaries

- Do not change event normalization, distinct-ID validation, property snapshot
  shape, token or API-key handling, request URLs, response handling, public
  signatures, dependencies, or workflows.
- Do not add live Mixpanel requests or credentials.
- Do not recursively reject finite numeric subclasses beyond the standard JSON
  encoder's existing behavior.

## Verification

- Run the focused Python 2.7 suite and complete `make check` from the repository
  root and through the absolute Makefile path from an unrelated directory.
- Run the network-disabled, read-only, digest-pinned Python 2.7 container gate.
- Reject hostile mutations that remove strict encoding from preflight or final
  serialization, weaken no-worker/no-request/no-callback evidence, omit a
  non-finite variant, or revert completed plan evidence.
- Audit the exact diff, bytecode and temporary artifacts, credential patterns,
  conflicts, dependencies, workflows, modes, binaries, and large files.

## Risks

- Callers that previously relied on Python's non-standard `NaN` or infinity
  output will now receive a synchronous `ValueError`, which is the intended
  fail-fast behavior for invalid JSON.
