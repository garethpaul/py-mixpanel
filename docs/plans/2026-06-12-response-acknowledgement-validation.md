# Mixpanel Response Acknowledgement Validation

## Status: Completed

## Context

`EventTracker.track` reads and closes the Mixpanel response but ignores its
contents. The legacy tracking endpoint uses a plain-text acknowledgement where
`1` indicates accepted input and `0` indicates invalid input. Ignoring that
acknowledgement can report success and invoke callbacks after Mixpanel rejects
an event.

The current Mixpanel Track Events reference continues to document `1` for valid
data and `0` when no submitted object is valid:
https://developer.mixpanel.com/reference/track-event

## Priority

Silent telemetry loss is worse than a visible delivery failure. The wrapper
must not run success callbacks or return normally when the upstream service
explicitly rejects an event.

## Prioritized Engineering Backlog

1. Validate the legacy response acknowledgement now.
2. Migrate the Python 2 GET-based integration to the current authenticated
   POST APIs in a separately versioned Python 3 compatibility effort.
3. Add explicit async error reporting instead of relying on uncaught worker
   thread exceptions during that migration.

## Requirements

- R1. A response whose stripped body is exactly `1` must remain successful.
- R2. `0`, empty, whitespace-only, and unexpected response bodies must raise a
  stable `MixpanelError` without including the upstream body.
- R3. Rejected acknowledgements must not invoke callbacks.
- R4. Responses must close on accepted, rejected, and read-error paths.
- R5. Existing request timeout, validation, payload, and caller-property
  isolation behavior must remain unchanged.
- R6. Tests must remain mocked, deterministic, bytecode-free, and Python 2.7
  compatible.
- R7. README, security guidance, vision, changes, and the baseline script must
  document and protect the acknowledgement contract.

## Scope Boundaries

- Do not expose upstream response bodies in exceptions.
- Do not change endpoint URLs, authentication, or payload encoding.
- Do not add dependencies or migrate runtimes in this focused change.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python2 -m unittest test_mixpanel`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`

## Work Completed

- Added `MixpanelError` and a strict plain-text acknowledgement validator.
- Kept response closure in `finally` before acknowledgement validation.
- Added mocked tests for stripped success, rejection forms, callback
  suppression, and cleanup.
- Updated the repository baseline and maintenance documentation.
