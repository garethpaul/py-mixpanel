# Runtime, API, Consent, And Identity Assumptions

This repository preserves a small legacy wrapper. Review these boundaries before
sending any real event.

## Python And Transport Contract

The source remains compatible with Python 2.7. Hosted verification covers
Python 3.11 and Python 3.14. It uses only the standard library and fixed US Mixpanel endpoints:
`https://api.mixpanel.com/track/` and the legacy import URL in
`mixpanel.py`. It does not select EU or India residency endpoints.

Tracking sends a legacy `application/x-www-form-urlencoded` POST body containing
a base64-encoded `data` field. A response body of 1 is only an ingestion acknowledgement;
Mixpanel's Track documentation notes that this does not prove a
valid project token. This wrapper does not implement retries, batching, regional
endpoints, or `$insert_id` deduplication. In contract terms, it does not implement retries, batching, regional endpoints, or $insert_id.
Callers must not add blind retries that
can duplicate events.

The archive/import method preserves a legacy import path that places encoded
event data and the configured API key in the HTTPS URL query. Treat it as
compatibility behavior, not a recommended new integration. Mixpanel documents
project-secret authentication as deprecating and recommends Service Accounts
for new import/export integrations. This wrapper does not implement Service
Accounts or current import authentication.

Official references:

- <https://developer.mixpanel.com/reference/track-event>
- <https://developer.mixpanel.com/reference/project-secret>

## Consent And Collection

Call `track` or `track_async` only after the application has an explicit consent
or other documented lawful collection basis appropriate to its users and
jurisdiction. This library does not display consent UI, remember opt-out state,
or automatically stop collection. The caller owns those controls and must avoid
calling the wrapper when analytics are disabled or consent is withdrawn.

Collect only event names and properties needed for a stated product purpose.
Do not send secrets, message contents, precise location, health data, financial
data, or other sensitive fields merely because JSON encoding accepts them.
Document retention and deletion behavior in the Mixpanel project and the source
system; this wrapper does not implement access, deletion, or export workflows.

## Distinct ID Boundary

Provide a stable pseudonymous distinct_id scoped to the intended project and
environment. Do not use email addresses, names, phone numbers, raw advertising
IDs, or other directly identifying values as `distinct_id`. Keep development,
staging, and production identifier namespaces separate.

The same person should receive the same approved identifier only within the
identity policy that the application controls. Record how identifiers are
created, rotated, merged, and deleted. Do not reuse another system's identifier
unless its disclosure and cross-system linkage were explicitly reviewed.

## Operator Checklist

- Verify the project token and endpoint region outside source control.
- Confirm consent/opt-out state before every explicit tracking call.
- Review event names and properties for minimization and sensitive content.
- Use a pseudonymous distinct ID with documented lifecycle ownership.
- Decide whether duplicate prevention is needed before adding any retry.
- Use mocked tests first; never run repository verification against live Mixpanel.
