# Token-only track POST transport

Status: Completed

## Scope

Move only token-authenticated `/track/` requests from a GET query string to an
HTTPS POST with an `application/x-www-form-urlencoded` body. Preserve the
`EventTracker` API, base64 JSON payload, timeout, response parsing, callbacks,
async behavior, and Python 2.7 support. Keep the API-key-backed `/import/` path
unchanged and out of scope.

## Verification

- Mocked request-object tests cover POST method, exact endpoint-only URL, form
  body decoding, content headers, Unicode, byte bodies, empty-event rejection,
  large events, callbacks, errors, timeouts, and the frozen import path.
- Hostile source mutations reject GET regression and incorrect form headers.
- `make check` runs without live Mixpanel traffic or credentials.
