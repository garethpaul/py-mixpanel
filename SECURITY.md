# Security Policy

## Supported Versions

The supported security scope for `py-mixpanel` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Track events with mixpanel

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/py-mixpanel` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a public sample, documentation, or utility project. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Review found secret-like configuration names that require careful review before use; changes in those areas should receive security-focused review before merge.
- No primary dependency manifest was detected in the repository root. If dependencies are added later, include a manifest and prefer reproducible installation instructions.
- GitHub Actions runs the static `make check` baseline; review workflow, Makefile, and checker changes alongside analytics request behavior changes.

## Service and API Notes

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

Event names, project tokens, event property containers, and caller-provided
distinct IDs should be validated before any Mixpanel request is built so
malformed analytics payloads do not leave the process.
Event names should be normalized before payload construction so caller typos do
not create visually duplicated analytics events.
Treat only a stripped plain-text `1` response as an accepted event; failed or
unexpected acknowledgements must raise a sanitized error without invoking the
success callback or exposing the upstream body.

Event property dictionaries can contain user identifiers and behavior data. The tracker copies caller-provided properties before adding Mixpanel defaults so application-owned data is not mutated during validation or submission.

The configured project token remains authoritative after that copy; a caller
property cannot redirect submission to a different Mixpanel project.
Successful callbacks receive credential-free callback properties captured
before the configured project token and generated timestamp are added to the
outbound request. Caller-supplied values remain available to the caller.

Callbacks should be callable before submission starts. Invalid callbacks are
rejected before analytics payloads are sent or async worker threads are
started.
Invalid asynchronous event names, property containers, and distinct IDs are
also rejected before a worker is created or any network request is opened.
JSON-incompatible async properties are rejected before a worker is created or
any network request is opened.
Nested async properties are detached before worker construction so caller-side
mutations cannot race with payload serialization or callback delivery.

Opened Mixpanel HTTP responses should be closed after successful and failed
reads so repeated analytics submission cannot exhaust local network resources.
The client also keeps bounded response reads in place before acknowledgement
validation so an untrusted endpoint cannot force an arbitrarily large body into
memory or reflect that content through an overflow error.

Hosted verification runs the full mocked request and callback gate in a
digest-pinned Python 2.7.18 container with read-only repository permissions.
Tracked-secret inspection fails closed if Git cannot inspect the checkout.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
