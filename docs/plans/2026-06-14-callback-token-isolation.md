# Callback Token Isolation

Status: Completed

## Problem

`track` adds the configured project token and a generated timestamp to its
copied outbound properties before invoking a success callback. The same path is
used by `track_async`, so application callbacks can observe an internal project
credential that the caller did not supply.

## Plan

1. Snapshot normalized caller properties before enriching the outbound payload.
2. Keep the configured project token authoritative in every request and retain
   generated timestamps in outbound payloads.
3. Return only the pre-enrichment snapshot to successful synchronous and
   asynchronous callbacks.
4. Add mutation-sensitive Python 2 regressions and fail-closed static contracts
   for snapshot ordering, callback use, documentation, and plan evidence.
5. Run the canonical host and digest-pinned Python 2.7.18 verification without
   live Mixpanel traffic or credentials.

## Compatibility Boundary

- Preserve `track` and `track_async` signatures, request URLs, payload encoding,
  callback timing, and error behavior.
- Preserve caller-supplied property values, including an explicitly supplied
  timestamp, in callback properties.
- Do not expose the configured project token or a generated timestamp through a
  success callback.
- Preserve Python 2.7 compatibility and add no dependencies.

## Work Completed

- Captured callback properties after validation and caller-dictionary copying,
  but before project-token and timestamp enrichment.
- Kept the configured project token and generated timestamp in the outbound
  Mixpanel payload while passing the isolated snapshot to success callbacks.
- Added synchronous and asynchronous regressions that independently prove the
  payload remains enriched and the callback remains credential-free.
- Added fail-closed source-ordering, regression, documentation, completed-plan,
  and verification-evidence contracts.

## Verification Results

- Canonical `make check` passed from the repository root and through the
  absolute Makefile path from an unrelated directory.
- The digest-pinned Python 2.7.18 container gate passed without network access
  or repository writes.
- Focused hostile mutations covering snapshot removal, ordering, callback use,
  synchronous and asynchronous regression identity, documentation, and plan
  status were rejected.
- Generated-artifact scanning, changed-line secret review, protected-path
  review, and `git diff --check` passed.
