# Async And Transport Boundary Review

Status: Completed

## Scope

Review PRs #6 through #14 as one linear stack while preserving the public
`track` and `track_async` API and testing token authority, callback isolation,
JSON validation, worker ownership, HTTP status/timeout/cleanup, and Python 2/3
compatibility.

## Root Causes

- `copy.deepcopy` trusted overridable hooks instead of defining a canonical
  JSON ownership boundary.
- Deferred workers used mutable tracker credentials.
- Raw network exceptions could contain complete credential-bearing URLs.
- Cleanup errors could replace primary failures, and explicit non-2xx response
  objects could reach acknowledgement validation.
- The baseline asserted implementation text rather than executable behavior.

## Fix

- Canonicalize dictionaries, lists, and tuples through built-in operations;
  reject cycles, unsupported values, and non-finite JSON before side effects.
- Capture the configured project token and API key in worker arguments and use
  separate request and credential-free callback trees.
- Centralize stable errors, 2xx validation, bounded reads, acknowledgement
  validation, and cleanup precedence.
- Preserve Python 2.7 while supporting modern Python 3 imports and encoding.
- Require seven hostile mutations in `make check`.

## Verification

- `make PYTHON=python3.11 check`
- Python 3.11, 3.12, 3.13, and 3.14 unit suites
- Seven hostile mutations
- Caller-independent Make execution
- `sh -n scripts/check-baseline.sh`
- `git diff --check`
- Hosted digest-pinned Python 2.7 and Python 3.11/3.14 gates

All HTTP verification is fake and credential-free. There is no live Mixpanel
request, so current provider authentication and actual delivery remain
unverified.
