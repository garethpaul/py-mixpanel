# AGENTS.md

## Repository purpose

`garethpaul/py-mixpanel` is a public sample, documentation, or utility project. Track events with mixpanel

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `plans` - repository source or sample assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Python (1).
- Prefer dependency-free tests or stdlib checks when legacy packages are unavailable.

## Testing guidance

- Test-related files detected: `plans/2026-06-08-async-callback-test.md`, `plans/2026-06-08-mocked-mixpanel-tests.md`, `test_mixpanel.py`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- Detected references to Mixpanel. Keep API keys, OAuth credentials, tokens, and account-specific values in local configuration only.
- Event validation rejects blank event names before analytics payloads are encoded or sent.
- Event validation trims surrounding whitespace before analytics payloads are encoded or callbacks run.
- Constructor validation rejects blank API keys before import request URLs are built.
- Tracking validation rejects non-dict properties and blank distinct IDs before analytics payloads are encoded or sent.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
