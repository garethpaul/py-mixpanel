# Make Legacy Verification Location Independent

Status: Planned

## Context

The Make recipes resolve plan globs, Python modules, tests, and the baseline
script in the caller's directory. An absolute-path Make invocation from another
directory therefore cannot reproduce the repository gate.

## Objectives

- Resolve the repository root from the loaded Makefile.
- Run every executable recipe from that root, independent of the caller.
- Protect the root and rooted recipes with mutation-sensitive shell contracts.
- Preserve Python 2.7 behavior, mocked tests, and completed-plan validation.

## Scope Boundaries

- Do not change Mixpanel behavior, APIs, tokens, dependencies, workflow, or the
  supported legacy runtime.
- Do not add live requests, generated files, or new tooling.

## Verification

- every Make alias, including `make check`, from the repository root and an
  unrelated directory
- digest-pinned Python 2.7.18 container validation
- hostile mutations covering root derivation and every rooted recipe
- workflow parsing, exact-base protected-file comparison, secret and
  generated-artifact scans, and `git diff --check`

## Work Planned

- Add an override-protected absolute repository root to the Makefile.
- Root docs, both Python 2 compilation checks, tests, and baseline checking.
- Extend the scripted baseline with exact Make and completed-plan contracts.
