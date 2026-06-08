# Issue 3: Bound Mixpanel URL Opens

## Context

GitHub issue: `garethpaul/py-mixpanel#3`

The Mixpanel wrapper sends runtime requests with `urllib2.urlopen` but does not provide a timeout. A stalled network connection can block tracking calls and async worker threads indefinitely.

## Plan

1. Add a default timeout value for outbound Mixpanel requests.
2. Allow callers to override the timeout through the existing `EventTracker` constructor.
3. Pass the configured timeout to every `urllib2.urlopen` call.
4. Add a source-level baseline check for timeout coverage.

## Verification

- Run `bash scripts/check-baseline.sh`.
- Run `git diff --check`.
