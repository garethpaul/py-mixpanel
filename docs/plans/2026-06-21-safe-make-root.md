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
- Canonicalize the checked-in Makefile directory with pinned POSIX tools and export it only to recipes.
- Add executed coverage for all seven pre-existing public Make targets plus the root regression gate.
- Include the root policy in `make verify` and `make check`.

## Verification Completed

- 56 executed target and authority cases kept quality commands inside the checkout.
- Hostile checkout backticks were blocked and dollar-substitution paths failed closed.
- `MAKEFILES`, `SHELL`, `.SHELLFLAGS`, and invalid `PYTHON` authority were covered.
- Command-line and environment `MAKEFILE_LIST` overrides failed closed.
- `make check` remains the complete repository gate and no runtime source changed.
