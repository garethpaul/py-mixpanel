# Mocked Mixpanel Tests

## Status

Completed

## Context

`py-mixpanel` is a Python 2 Mixpanel wrapper with no local tests. The tracking
and import endpoints used HTTP URLs, and exercising behavior required a live
network request.

## Objectives

- Add deterministic tests that monkeypatch `urllib2.urlopen`.
- Verify track and import requests use HTTPS.
- Verify encoded payloads include event names, tokens, distinct IDs, and times.
- Keep the tests on Python 2 to match the legacy source.
- Provide `make verify` as the local quality gate.

## Verification

- `make verify`
- `python2 -m unittest test_mixpanel`
- `git diff --check`

## Follow-Up Candidates

- Return or expose request errors instead of discarding response details.
- Add tests for `track_async` callback behavior.
- Document Mixpanel API version assumptions and user-consent expectations.
