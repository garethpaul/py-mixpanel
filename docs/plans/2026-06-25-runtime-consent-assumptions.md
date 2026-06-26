# Runtime, API, Consent, And Identity Guide

## Status: Completed

## Context

The roadmap required explicit Python/Mixpanel API assumptions and deeper consent
and distinct-ID guidance. Existing docs covered validation and transport safety
but not region support, acknowledgement limits, import authentication age,
retry/deduplication gaps, opt-out ownership, or pseudonymous identifier policy.

## Work Completed

- Documented Python 2.7 plus hosted Python 3.11/3.14 compatibility.
- Documented fixed US endpoints, legacy form POST tracking, response `1`
  limitations, and missing retry/batching/region/`$insert_id` features.
- Marked the query-based import path as legacy and documented Mixpanel's Service
  Account recommendation for new import/export integrations.
- Added explicit consent, minimization, opt-out, retention, deletion, and
  pseudonymous `distinct_id` ownership guidance.
- Removed both completed roadmap items and added baseline contracts.

## Scope Boundary

- No transport, endpoint, authentication, payload, callback, async, or public API
  behavior changes.
- No live Mixpanel calls, tokens, API keys, identifiers, or event payloads.

## Verification

- The baseline contract failed first for the missing guide.
- Current Python and pinned Python 2.7 `make check` each passed 42 unit tests,
  56 Make authority cases, 10 transport mutations, and the baseline contract.
- Fourteen hostile guide mutations rejected runtime, endpoint, consent,
  identity, acknowledgement, feature, import, link, roadmap, and plan drift.
- Exact-head hosted Python matrices and CodeQL remain required before merge.
