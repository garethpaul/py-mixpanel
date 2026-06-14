# Make Legacy Verification Location Independent

Status: Completed

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

## Work Completed

- Added an override-protected absolute repository root to the Makefile.
- Rooted docs, both Python 2 compilation checks, tests, and baseline checking.
- Extended the scripted baseline with exact Make and completed-plan contracts.

## Verification Results

- Every Make alias passed from both the repository root and an unrelated
  directory with `REPO_ROOT=/tmp` supplied on the command line.
- Full root and external `make check` runs passed in the network-disabled,
  digest-pinned Python 2.7.18 container against a read-only disposable Git
  checkout; all 22 mocked tests passed in each run.
- Six hostile mutations rejected removal of override protection and every
  rooted executable recipe.
- Workflow YAML parsing, exact-base protected-file comparison, secret and
  generated-artifact scans, and `git diff --check` passed.
