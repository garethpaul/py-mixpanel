---
title: Project Token Authority
type: fix
status: completed
date: 2026-06-13
---

# Project Token Authority

Status: Completed

## Context

`EventTracker` validates and stores a project token, but `track` only adds that
token when caller properties omit `token`. A caller property can therefore
silently redirect an event to a different Mixpanel project than the tracker
instance represents.

## Priority

The tracker constructor should define the destination project. Keeping that
credential authoritative prevents accidental cross-project submission while
preserving caller-owned property dictionaries and explicit event timestamps.

## Objectives

- Always write the validated `EventTracker` token into the outbound payload.
- Prevent caller properties from overriding the configured project token.
- Preserve caller dictionaries without mutation.
- Preserve explicit caller-provided `time` values for historical events.
- Cover synchronous, asynchronous, callback, and import payload behavior.
- Protect implementation, tests, documentation, and completed plan in the
  fail-closed baseline checker.

## Implementation Units

### 1. Authoritative token assignment

Files:

- `mixpanel.py`
- `test_mixpanel.py`

Requirements:

- Replace conditional token defaulting with unconditional assignment from
  `self.token` after caller properties have been copied and validated.
- Prove a conflicting caller token is not sent and the input dict is unchanged.
- Prove callbacks observe the authoritative token and preserved timestamp.
- Exercise the behavior through the async entry point as well as `track`.

### 2. Contracts and documentation

Files:

- `scripts/check-baseline.sh`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-13-project-token-authority.md`

Requirements:

- Document that constructor configuration controls the project token.
- Require unconditional assignment and regression coverage.
- Record completed status and actual verification only after implementation
  and tests pass.

## Test Scenarios

- `track` receives a conflicting `token` and explicit `time`: the payload and
  callback use the tracker token, preserve the time, and leave input unchanged.
- `track_async` receives a conflicting token: preflight succeeds, the worker
  payload uses the tracker token, and the input remains unchanged.
- Import requests continue using the configured API key and tracker token.
- Existing validation, response cleanup, acknowledgement, body-size, timeout,
  callback, and async preflight tests remain green.

## Scope Boundaries

- Do not reject the caller property solely because it contains `token`.
- Do not change caller-provided `time` semantics.
- Do not alter API-key query handling, request URLs, timeouts, or callbacks.
- Do not add dependencies or raise the Python 2.7 compatibility floor.
- Do not contact Mixpanel or require credentials.

## Verification

- `python2 test_mixpanel.py`
- `sh scripts/check-baseline.sh`
- `make lint`
- `make test`
- `make build`
- `make docs`
- `make verify`
- `make check`
- digest-pinned Python 2.7.18 container `make check`
- workflow YAML parse
- `git diff --check`

## Work Completed

- Made the validated `EventTracker` project token authoritative for every
  outbound event payload.
- Added synchronous and asynchronous regressions proving conflicting caller
  tokens are not sent while input dictionaries and explicit timestamps remain
  unchanged.
- Extended the fail-closed checker and public documentation with the project
  token authority contract.

## Verification Results

Completed locally on 2026-06-13:

- `python2 test_mixpanel.py` (21 tests passed)
- `sh scripts/check-baseline.sh`
- `make lint`
- `make test`
- `make build`
- `make docs`
- `make verify`
- `make check`
- digest-pinned Python 2.7.18 container `make check` with canonical and worktree
  Git paths mounted for metadata inspection
- workflow YAML parse
- six hostile project-token contract mutations rejected
- `git diff --check`
