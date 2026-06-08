## Py Mixpanel Vision

Py Mixpanel is a small unofficial Python wrapper for sending Mixpanel tracking
and import events, including an asynchronous thread helper.

The repository is useful as a minimal event-tracking example: it builds encoded
payloads, requires a distinct identifier, and supports both token-only tracking
and API-key-backed import calls.

The goal is to keep the wrapper understandable while making analytics,
identity, and Python 2-era assumptions explicit.

Current baseline: `make check` verifies Python 2 syntax, mocked HTTPS tracking
and import requests, async callback behavior, and canonical `docs/plans`
coverage without contacting Mixpanel.

The current focus is:

Priority:

- Preserve the `EventTracker.track` and `track_async` API shape
- Keep token and API-key handling caller-controlled
- Avoid collecting analytics without explicit caller action
- Maintain `make check` with mocked HTTP coverage
- Treat `urllib2` and Python 2 idioms as legacy constraints
- Keep completed maintenance plans under `docs/plans`

Next priorities:

- Add more mock HTTP tests for error handling
- Return or expose request errors instead of swallowing response details
- Document Python version and Mixpanel API assumptions
- Add guidance for user consent and distinct ID handling

Contribution rules:

- One PR = one focused tracking, import, async, test, or documentation change.
- Do not commit real tokens, API keys, or event payloads.
- Keep network calls out of deterministic unit tests.
- Document any public API changes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Analytics libraries can leak user identifiers and behavior. This wrapper should
make tracking explicit, keep credentials out of source control, and avoid
background event submission that callers did not request.

## What We Will Not Merge (For Now)

- Hidden tracking or automatic event collection
- Checked-in tokens or API keys
- Live-network-only tests
- Payload logging that exposes user identifiers

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
