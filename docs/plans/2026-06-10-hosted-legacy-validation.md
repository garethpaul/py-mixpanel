# Hosted Legacy Validation

Status: Completed

## Context

The Python 2.7 Mixpanel sample had compile checks, 14 mocked request and callback
tests, bytecode guards, and repository metadata checks, but no hosted workflow
ran the canonical gate. The baseline also suppressed Git command failures,
which could skip tracked-secret and editor-metadata inspection.

## Work Completed

- Added GitHub Actions validation in the official Python 2.7.18 image, pinned
  to the reviewed Linux amd64 digest.
- Kept the complete `make check` path with source/test compilation, all 14
  mocked tests, bytecode checks, plan validation, and metadata hygiene.
- Limited the workflow token to read-only contents access and pinned checkout
  to a reviewed commit.
- Made tracked local metadata inspection fail closed when Git cannot inspect the
  checkout.
- Extended the baseline to reject floating images, setup-python substitutions,
  skipped legacy tests, allowed failures, or weakened workflow contracts.

## Verification

- `make check`
- `docker run --rm --platform linux/amd64 -v "$PWD:/repo" -w /repo python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20 make check`
- `git diff --check`
