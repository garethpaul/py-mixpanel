#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

require_file() {
  if [ ! -f "$ROOT_DIR/$1" ]; then
    printf '%s\n' "Required file is missing: $1" >&2
    exit 1
  fi
}

require_text() {
  path=$1
  text=$2
  if ! grep -Fq "$text" "$ROOT_DIR/$path"; then
    printf '%s\n' "$path must preserve: $text" >&2
    exit 1
  fi
}

for path in \
  .github/workflows/check.yml \
  .gitignore \
  CHANGES.md \
  Makefile \
  README.md \
  SECURITY.md \
  VISION.md \
  mixpanel.py \
  test_mixpanel.py \
  scripts/check-baseline.sh \
  scripts/test-makefile-root.sh \
  scripts/test-review-mutations.py \
  docs/plans/2026-06-21-safe-make-root.md \
  docs/plans/2026-06-19-async-transport-boundary-review.md; do
  require_file "$path"
done

for contract in \
  'TRACK_BASE_URL = "https://api.mixpanel.com/track/?data=%s"' \
  'ARCHIVE_BASE_URL = "https://api.mixpanel.com/import/?data=%s&api_key=%s"' \
  'REQUEST_TIMEOUT_SECONDS = 10' \
  'MAX_RESPONSE_BODY_BYTES = 1024' \
  'def snapshot_json_value(value, active=None):' \
  'for key, item in dict.items(value):' \
  'list.__getitem__(value, index)' \
  'raise ValueError("Circular reference detected")' \
  'json.dumps(params, allow_nan=False)' \
  'raise MixpanelError("Mixpanel request failed")' \
  'status < 200 or status >= 300' \
  'response_body = resp.read(MAX_RESPONSE_BODY_BYTES + 1)' \
  'resp.close()' \
  'token = self.token' \
  'api_key = self.api_key' \
  'target=self._track_prepared'; do
  require_text mixpanel.py "$contract"
done

for test_name in \
  test_track_redacts_request_errors_without_callback \
  test_track_preserves_primary_failure_when_response_close_also_fails \
  test_track_rejects_non_success_http_status_before_callback \
  test_track_uses_builtin_dict_items_for_hostile_subclasses \
  test_track_callback_mutation_cannot_change_caller_or_payload \
  test_track_async_canonicalizes_self_aliasing_nested_containers \
  test_track_async_snapshots_tracker_credentials_before_worker \
  test_track_rejects_circular_properties_before_request \
  test_track_async_rejects_circular_properties_before_thread; do
  require_text test_mixpanel.py "def $test_name"
done

for make_contract in \
  'override SHELL := /bin/sh' \
  'override .SHELLFLAGS := -c' \
  '$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)' \
  'PYTHON ?= python2' \
  '$(error PYTHON must be python or python2)' \
  'ifneq ($(origin MAKEFILE_LIST),file)' \
  '$(error MAKEFILE_LIST must not be overridden)' \
  'override REPO_ROOT := $(shell path=' \
  '/usr/bin/sed' \
  'export REPO_ROOT' \
  '/usr/bin/dirname' \
  '/bin/pwd -P' \
  '$(PYTHON) -m unittest test_mixpanel' \
  '$(PYTHON) scripts/test-review-mutations.py' \
  'scripts/test-makefile-root.sh' \
  'verify: lint test build docs root-test' \
  'check: verify mutations'; do
  require_text Makefile "$make_contract"
done

for root_contract in \
  'Py Mixpanel' \
  '56 executed target/authority cases' \
  'hostile backticks blocked' \
  'dollar paths failed closed' \
  '1 MAKEFILES preload rejection' \
  '1 PYTHON rejection' \
  '2 MAKEFILE_LIST rejection cases' \
  'MAKEFILE_LIST must not be overridden'; do
  require_text scripts/test-makefile-root.sh "$root_contract"
done

for root_evidence in \
  'Status: Completed' \
  'seven pre-existing public Make targets plus the root regression gate' \
  '56 executed target and authority cases' \
  'Hostile checkout backticks were blocked and dollar-substitution paths failed closed' \
  '`MAKEFILES`, `SHELL`, `.SHELLFLAGS`, and invalid `PYTHON` authority were covered' \
  'Command-line and environment `MAKEFILE_LIST` overrides failed closed' \
  'make check'; do
  require_text docs/plans/2026-06-21-safe-make-root.md "$root_evidence"
done

WORKFLOW=.github/workflows/check.yml
for workflow_contract in \
  'permissions:' \
  'contents: read' \
  'runs-on: ubuntu-24.04' \
  'timeout-minutes: 10' \
  'persist-credentials: false' \
  'image: python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20' \
  'name: Python 2.7 legacy verification' \
  'python-version: ["3.11", "3.14"]' \
  'make PYTHON=python check'; do
  require_text "$WORKFLOW" "$workflow_contract"
done

if grep -Fq 'continue-on-error' "$ROOT_DIR/$WORKFLOW"; then
  printf '%s\n' "Hosted verification must not tolerate failures." >&2
  exit 1
fi

for documented in README.md SECURITY.md VISION.md CHANGES.md; do
  require_text "$documented" 'no live Mixpanel'
  require_text "$documented" 'configured project token'
  require_text "$documented" 'credential-free callback'
  require_text "$documented" 'bounded response'
done

for plan in "$ROOT_DIR"/docs/plans/*.md; do
  [ -f "$plan" ] || continue
  grep -Fq 'Status: Completed' "$plan" || {
    printf '%s\n' "$plan must record completed status." >&2
    exit 1
  }
  grep -Fq 'make check' "$plan" || {
    printf '%s\n' "$plan must record make check verification." >&2
    exit 1
  }
done

for ignored in '*.py[cod]' '__pycache__/' dist build .env '.env.*' .idea/ .vscode/ '*.iml'; do
  require_text .gitignore "$ignored"
done

bytecode_artifacts=$(find "$ROOT_DIR" -path "$ROOT_DIR/.git" -prune -o \
  \( -name '*.pyc' -o -name '*.pyo' -o -name '__pycache__' \) -print)
if [ -n "$bytecode_artifacts" ]; then
  printf '%s\n%s\n' "Generated Python artifacts are not allowed:" "$bytecode_artifacts" >&2
  exit 1
fi

if ! tracked_local=$(git -C "$ROOT_DIR" ls-files '.env' '.env.*' '.idea' '.vscode' '*.iml'); then
  printf '%s\n' "Unable to inspect tracked local metadata." >&2
  exit 1
fi
if [ -n "$tracked_local" ]; then
  printf '%s\n%s\n' "Local secrets or editor metadata must not be tracked:" "$tracked_local" >&2
  exit 1
fi

sh -n "$ROOT_DIR/scripts/check-baseline.sh"
printf '%s\n' "Repository baseline contracts passed."
