# Docs Gate Fail Closed

Status: Completed

## Problem

The `docs` target enforced 1 of its 93 assertions.

The recipe chained three per-plan checks with `;` inside a `for` loop:

    @cd "$$REPO_ROOT" && for plan in docs/plans/*.md; do \
        test -f "$$plan"; \
        grep -q "Status: Completed" "$$plan"; \
        grep -q "make check" "$$plan"; \
    done

Make runs recipes via `sh -c` with no `set -e`, and a shell `for` loop exits with
the status of the last command of the last iteration. With 31 plans and 3 checks,
only `grep -q "make check"` on the alphabetically final plan could fail the target.

Measured on the unfixed recipe (each probe applied and confirmed on disk):

    break 'Status: Completed'  first / mid / last plan   ->  exit 0, 0, 0   NOT CAUGHT
    break 'make check'         first / mid               ->  exit 0, 0      NOT CAUGHT
    break 'make check'         last                      ->  exit 2         CAUGHT

`Status: Completed` was unenforced for **every** plan, including the last, because
it is not the loop's final command. `test -f` is likewise vacuous: the value comes
from the glob, so it cannot fail in practice.

## Decision

Fail closed per assertion, with a diagnostic naming the offending file. This copies
the recipe already reviewed in `py-fitbit` and `purpleair-go` rather than inventing
a new shape — an account-wide sweep of all 146 Makefiles found this identical
recipe in exactly three repos, and those two are the other two.

`||`-guarding each check preserves the per-plan loop while making every assertion
load-bearing. No plan content changed; no library source changed.

## Verification

    make docs, clean tree                                  exit 0
    break 'Status: Completed'  first / mid / last          exit 2, 2, 2   CAUGHT
    break 'make check'         first / mid / last          exit 2, 2, 2   CAUGHT
    each diagnostic names its own plan file
    make check                                             see CI (python2 absent locally)

1 of 93 assertions enforced becomes 93 of 93.

## Known limitation, deliberately not addressed

Deleting a plan file outright is still not caught: the glob simply shrinks and the
loop iterates over what remains. Detecting that needs a manifest of expected plans,
which is a design decision about how plans are tracked rather than a bug fix, so it
is left to the maintainer.

## Severity

This was a real defect in the `docs` target, not merely a verification gap: the
target reported success while checking almost nothing. Its blast radius is bounded
to documentation-completeness checking — no library behaviour was affected, and
`make check` independently exercises the code.
