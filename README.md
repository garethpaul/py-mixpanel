# py-mixpanel

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/py-mixpanel` is a public sample, documentation, or utility project. Track events with mixpanel

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Python (1).

## Repository Contents

- `README.md` - project overview and local usage notes
- `CHANGES.md` - notable maintenance changes
- `Makefile` - local verification entry points
- `plans` - completed maintenance plans
- `test_mixpanel.py` - mocked HTTP regression tests
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: no top-level source directories detected
- Dependency and build manifests: Makefile
- Entry points or build surfaces: mixpanel.py, Makefile
- Test-looking files: test_mixpanel.py

## Getting Started

### Prerequisites

- Git
- Python 2.7 and `make`

### Setup

```bash
git clone https://github.com/garethpaul/py-mixpanel.git
cd py-mixpanel
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Import `EventTracker` from `mixpanel.py`.
- Call `track(event, properties)` only after the caller has explicit consent and a caller-provided `distinct_id`.
- Use `track_async` only when background submission is expected by the caller.

## Testing and Verification

- Run `make verify` before committing changes.
- The verification gate compile-checks the legacy Python 2 files and runs mocked HTTP tests for tracking, import URLs, and async callback behavior.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- Detected references to Mixpanel. Keep API keys, OAuth credentials, tokens, and account-specific values in local configuration only.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include mixpanel.py.
- Review changes touching external API calls or credential-adjacent configuration; examples from the scan include mixpanel.py.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include mixpanel.py.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include mixpanel.py.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
