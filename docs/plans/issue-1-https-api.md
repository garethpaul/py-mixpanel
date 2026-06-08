# Issue 1: Use HTTPS Mixpanel Endpoints

## Context

GitHub issue: `garethpaul/py-mixpanel#1`

The Mixpanel wrapper builds runtime tracking and import requests with plain HTTP URLs. That can expose analytics payloads and credentials in transit.

## Plan

1. Switch the Mixpanel tracking and import endpoint constants from HTTP to HTTPS.
2. Preserve the existing Python 2-era API and calling behavior.
3. Add a source-level baseline check that rejects plain-HTTP Mixpanel runtime endpoints.

## Verification

- Run `bash scripts/check-baseline.sh`.
- Run `git diff --check`.
