# Safe Makefile Root Resolution

Status: Completed

## Context

Caller-controlled `MAKEFILE_LIST` redirected Python compilation, tests,
mutation checks, documentation checks, and baseline validation outside the
reviewed checkout.

## Scope Boundaries

- Do not change Mixpanel request, callback, credential, snapshot, or response behavior.
- Preserve Python 2.7 and current Python 3 validation without live requests.
- Preserve the pinned legacy container and modern hosted matrix.

## Work Completed

- Reject command-line and environment replacement of `MAKEFILE_LIST`.
- Canonicalize the checked-in Makefile directory with pinned-container-compatible tools.
- Add coverage for all seven pre-existing public Make targets plus the root regression gate.
- Include the root policy in `make verify` and `make check`.

## Verification Completed

- Python 2.7.18 and Python 3.12.8 each passed 39 tests and seven hostile mutations.
- All 24 target and `REPO_ROOT` override cases passed from a shell-sensitive path.
- Command-line and environment `MAKEFILE_LIST` overrides failed closed.
- Mixpanel source, credentials, callbacks, and transport behavior were unchanged.
