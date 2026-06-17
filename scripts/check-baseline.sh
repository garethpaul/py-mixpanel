#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
README="$ROOT_DIR/README.md"
MAKEFILE="$ROOT_DIR/Makefile"
GITIGNORE="$ROOT_DIR/.gitignore"
DOCS_PLANS="$ROOT_DIR/docs/plans"
WORKFLOW="$ROOT_DIR/.github/workflows/check.yml"
CI_PLAN="$ROOT_DIR/docs/plans/2026-06-10-ci-baseline.md"
RESPONSE_BODY_PLAN="$ROOT_DIR/docs/plans/2026-06-12-response-body-size-boundary.md"

require_file() {
  path=$1
  if [ ! -f "$ROOT_DIR/$path" ]; then
    printf '%s\n' "Required file is missing: $path" >&2
    exit 1
  fi
}

for path in \
  ".gitignore" \
  "CHANGES.md" \
  "Makefile" \
  "README.md" \
  "SECURITY.md" \
  "VISION.md" \
  "mixpanel.py" \
  "test_mixpanel.py" \
  "docs/plans/2026-06-08-py-mixpanel-baseline.md" \
  "docs/plans/2026-06-09-scripted-baseline-check.md" \
  "docs/plans/2026-06-10-ci-baseline.md" \
  "docs/plans/2026-06-10-hosted-legacy-validation.md" \
  "docs/plans/2026-06-12-response-body-size-boundary.md" \
  "docs/plans/2026-06-13-project-token-authority.md" \
  "docs/plans/2026-06-13-async-json-preflight.md" \
  "docs/plans/2026-06-14-location-independent-make.md" \
  "docs/plans/2026-06-14-callback-token-isolation.md" \
  "docs/plans/2026-06-15-async-nested-property-snapshot.md" \
  "docs/plans/2026-06-16-finite-json-properties.md" \
  ".github/workflows/check.yml" \
  "scripts/check-baseline.sh"; do
  require_file "$path"
done

if [ "$(grep -Fc 'allow_nan=False' "$ROOT_DIR/mixpanel.py")" -ne 2 ]; then
  printf '%s\n' "Sync serialization and async preflight must both reject non-finite JSON numbers." >&2
  exit 1
fi

sync_finite_json_test=$(sed -n '/^    def test_track_rejects_non_finite_properties_before_request/,/^    def /p' "$ROOT_DIR/test_mixpanel.py")
for sync_finite_json_contract in \
  'float("nan"), float("inf"), float("-inf")' \
  '            with self.assertRaises(ValueError):' \
  '        self.assertEqual([], self.urls)' \
  'self.assertEqual([], callbacks)'; do
  if ! printf '%s\n' "$sync_finite_json_test" | grep -Fq "$sync_finite_json_contract"; then
    printf '%s\n' "Synchronous finite JSON regression must preserve $sync_finite_json_contract." >&2
    exit 1
  fi
done

async_finite_json_test=$(sed -n '/^    def test_track_async_rejects_non_finite_properties_before_thread/,/^    def /p' "$ROOT_DIR/test_mixpanel.py")
for async_finite_json_contract in \
  'float("nan"), float("inf"), float("-inf")' \
  '                with self.assertRaises(ValueError):' \
  '"non-finite properties must not create a worker"' \
  '"non-finite properties must not open a request"' \
  '        self.assertEqual([], callbacks)'; do
  if ! printf '%s\n' "$async_finite_json_test" | grep -Fq "$async_finite_json_contract"; then
    printf '%s\n' "Async finite JSON regression must preserve $async_finite_json_contract." >&2
    exit 1
  fi
done

FINITE_JSON_PLAN="$ROOT_DIR/docs/plans/2026-06-16-finite-json-properties.md"
for finite_json_evidence in \
  'Status: Completed' \
  '28 Python 2.7 tests passed' \
  'absolute Makefile' \
  'digest-pinned Python 2.7' \
  'hostile mutations were rejected' \
  'git diff --check'; do
  if ! grep -Fq "$finite_json_evidence" "$FINITE_JSON_PLAN"; then
    printf '%s\n' "Finite JSON plan must preserve completed evidence: $finite_json_evidence" >&2
    exit 1
  fi
done

if ! grep -Fq 'import copy' "$ROOT_DIR/mixpanel.py" || \
   ! grep -Fq '    properties = copy.deepcopy(properties)' "$ROOT_DIR/mixpanel.py"; then
  printf '%s\n' "mixpanel.py must recursively snapshot async properties." >&2
  exit 1
fi

async_snapshot_line=$(grep -n '    properties = copy.deepcopy(properties)' "$ROOT_DIR/mixpanel.py" | cut -d: -f1)
async_json_line=$(grep -n '    validate_json_properties(event, properties)' "$ROOT_DIR/mixpanel.py" | cut -d: -f1)
thread_import_line=$(grep -n '    from threading import Thread' "$ROOT_DIR/mixpanel.py" | cut -d: -f1)
if [ -z "$async_snapshot_line" ] || [ -z "$async_json_line" ] || \
   [ -z "$thread_import_line" ] || \
   [ "$async_snapshot_line" -ge "$async_json_line" ] || \
   [ "$async_json_line" -ge "$thread_import_line" ]; then
  printf '%s\n' "Async nested properties must be snapshotted before JSON preflight and worker construction." >&2
  exit 1
fi

snapshot_test=$(sed -n '/^    def test_track_async_snapshots_nested_properties_before_worker/,/^    def /p' "$ROOT_DIR/test_mixpanel.py")
for snapshot_contract in \
  'class DeferredThread(object):' \
  'def run(self):' \
  'properties["profile"]["plan"] = "enterprise"' \
  'properties["profile"]["tags"].append("caller-mutation")' \
  '"plan": "free"' \
  '"tags": ["initial"]' \
  '"tags": ["initial", "caller-mutation"]'; do
  if ! grep -Fq "$snapshot_contract" "$ROOT_DIR/test_mixpanel.py"; then
    printf '%s\n' "Async nested snapshot tests must preserve $snapshot_contract." >&2
    exit 1
  fi
done
for executable_contract in \
  '            worker = tracker.track_async(' \
  '            worker.run()' \
  '        self.assertEqual(1, len(DeferredThread.created))' \
  '        }, payload["properties"]["profile"])' \
  '        ], callbacks)'; do
  if ! printf '%s\n' "$snapshot_test" | grep -Fqx "$executable_contract"; then
    printf '%s\n' "Async nested snapshot regression must preserve executable line: $executable_contract" >&2
    exit 1
  fi
done

ASYNC_SNAPSHOT_PLAN="$ROOT_DIR/docs/plans/2026-06-15-async-nested-property-snapshot.md"
for evidence in \
  'Status: Completed' \
  '26 Python 2.7 tests passed' \
  'absolute Makefile' \
  'digest-pinned Python 2.7.18' \
  'hostile mutations were rejected' \
  'git diff --check'; do
  if ! grep -Fq "$evidence" "$ASYNC_SNAPSHOT_PLAN"; then
    printf '%s\n' "Async nested snapshot plan must preserve completed evidence: $evidence" >&2
    exit 1
  fi
done
for copy_failure_contract in \
  'class UncopyableValue(object):' \
  'def __deepcopy__(self, memo):' \
  'test_track_async_rejects_copy_failures_before_thread' \
  '"copy failures must not create a worker"' \
  '"copy failures must not open a request"'; do
  if ! grep -Fq "$copy_failure_contract" "$ROOT_DIR/test_mixpanel.py"; then
    printf '%s\n' "Async snapshot tests must preserve copy-failure contract $copy_failure_contract." >&2
    exit 1
  fi
done
if grep -Eiq 'Status:[[:space:]]+Planned|pending|in[[:space:]]+progress' "$ASYNC_SNAPSHOT_PLAN"; then
  printf '%s\n' "Async nested snapshot plan must not retain provisional status." >&2
  exit 1
fi

if ! grep -Fq '    callback_properties = properties.copy()' "$ROOT_DIR/mixpanel.py" || \
   ! grep -Fq '      callback(event, callback_properties)' "$ROOT_DIR/mixpanel.py"; then
  printf '%s\n' "mixpanel.py must isolate callback properties from outbound credentials." >&2
  exit 1
fi

callback_snapshot_line=$(grep -n '    callback_properties = properties.copy()' "$ROOT_DIR/mixpanel.py" | cut -d: -f1)
token_injection_line=$(grep -n "    properties\['token'\] = self.token" "$ROOT_DIR/mixpanel.py" | cut -d: -f1)
if [ -z "$callback_snapshot_line" ] || [ -z "$token_injection_line" ] || \
   [ "$callback_snapshot_line" -ge "$token_injection_line" ]; then
  printf '%s\n' "Callback properties must be snapshotted before project-token enrichment." >&2
  exit 1
fi

for callback_contract in \
  "test_track_callback_excludes_configured_token_and_generated_time" \
  "test_track_async_callback_excludes_configured_token_and_generated_time" \
  'self.assertNotIn("token", callbacks[0][1])' \
  'self.assertNotIn("time", callbacks[0][1])'; do
  if ! grep -Fq "$callback_contract" "$ROOT_DIR/test_mixpanel.py"; then
    printf '%s\n' "Callback credential-isolation tests must preserve $callback_contract." >&2
    exit 1
  fi
done

if ! grep -Fq 'def validate_json_properties(event, properties):' "$ROOT_DIR/mixpanel.py" || \
   ! grep -Fq 'json.dumps({"event": event, "properties": properties}, allow_nan=False)' "$ROOT_DIR/mixpanel.py"; then
  printf '%s\n' "mixpanel.py must preserve JSON serialization preflight for async properties." >&2
  exit 1
fi

async_json_line=$(grep -n '    validate_json_properties(event, properties)' "$ROOT_DIR/mixpanel.py" | cut -d: -f1)
thread_import_line=$(grep -n '    from threading import Thread' "$ROOT_DIR/mixpanel.py" | cut -d: -f1)
if [ -z "$async_json_line" ] || [ -z "$thread_import_line" ] || [ "$async_json_line" -ge "$thread_import_line" ]; then
  printf '%s\n' "Async JSON serialization preflight must run before worker construction." >&2
  exit 1
fi

for json_contract in \
  "test_track_async_rejects_unserializable_properties_before_thread" \
  'with self.assertRaises(TypeError):' \
  '"nested": object()' \
  '"unserializable properties must not create a worker"' \
  '"unserializable properties must not open a request"'; do
  if ! grep -Fq "$json_contract" "$ROOT_DIR/test_mixpanel.py"; then
    printf '%s\n' "Async JSON preflight tests must preserve $json_contract." >&2
    exit 1
  fi
done

exact_line_count() {
  awk -v expected="$2" '$0 == expected { count += 1 } END { print count + 0 }' "$1"
}

if [ "$(exact_line_count "$WORKFLOW" 'permissions:')" -ne 1 ] || \
   [ "$(exact_line_count "$WORKFLOW" '  contents: read')" -ne 1 ]; then
  printf '%s\n' "Hosted validation must use read-only repository contents permission." >&2
  exit 1
fi

if grep -Eq '^[[:space:]]+permissions:' "$WORKFLOW" || \
   grep -Eq '(^|[[:space:]])write-all([[:space:]]|$)' "$WORKFLOW" || \
   grep -Eq '^[[:space:]]+[^#][^:]*:[[:space:]]*write([[:space:]]*(#.*)?)?$' "$WORKFLOW"; then
  printf '%s\n' "Hosted validation must not add nested or write-capable permissions." >&2
  exit 1
fi

if [ "$(grep -Fc 'uses: actions/checkout@' "$WORKFLOW")" -ne 1 ] || \
   ! grep -Fq 'uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3' "$WORKFLOW"; then
  printf '%s\n' "Hosted validation must pin the reviewed actions/checkout v6.0.3 commit." >&2
  exit 1
fi

if [ "$(exact_line_count "$WORKFLOW" '          persist-credentials: false')" -ne 1 ]; then
  printf '%s\n' "Hosted validation must disable checkout credential persistence." >&2
  exit 1
fi

if [ "$(grep -Fc 'image: python:2.7.18@' "$WORKFLOW")" -ne 1 ] || \
   ! grep -Fq 'image: python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20' "$WORKFLOW"; then
  printf '%s\n' "Hosted validation must pin the reviewed Python 2.7.18 image digest." >&2
  exit 1
fi

if grep -Fq 'setup-python@' "$WORKFLOW"; then
  printf '%s\n' "Hosted validation must use the pinned Python 2 container, not setup-python." >&2
  exit 1
fi

if grep -Fq 'continue-on-error' "$WORKFLOW" || grep -Fq 'command -v python2' "$WORKFLOW"; then
  printf '%s\n' "Hosted validation must not allow legacy verification failures." >&2
  exit 1
fi

if [ "$(exact_line_count "$WORKFLOW" '        run: make check')" -ne 1 ]; then
  printf '%s\n' "Hosted validation must run the canonical make check gate." >&2
  exit 1
fi

for workflow_contract in \
  '  workflow_dispatch:' \
  '  cancel-in-progress: true' \
  '    runs-on: ubuntu-24.04' \
  '    timeout-minutes: 10'; do
  if [ "$(exact_line_count "$WORKFLOW" "$workflow_contract")" -ne 1 ]; then
    printf '%s\n' "Hosted validation is missing required workflow contract: $workflow_contract" >&2
    exit 1
  fi
done

if grep -Fq 'command -v python2' "$MAKEFILE" || grep -Fq 'Skipping legacy Python 2' "$MAKEFILE"; then
  printf '%s\n' "Makefile must require Python 2 checks instead of skipping them." >&2
  exit 1
fi

if ! grep -Fq "scripts/check-baseline.sh" "$MAKEFILE"; then
  printf '%s\n' "Makefile must run scripts/check-baseline.sh from make check." >&2
  exit 1
fi

for make_contract in \
  'override REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))' \
  '@cd "$(REPO_ROOT)" && for plan in docs/plans/*.md; do \' \
  'cd "$(REPO_ROOT)" && python2 -c "import py_compile; py_compile.compile('\''mixpanel.py'\''' \
  'cd "$(REPO_ROOT)" && python2 -c "import py_compile; py_compile.compile('\''test_mixpanel.py'\''' \
  'cd "$(REPO_ROOT)" && PYTHONDONTWRITEBYTECODE=1 python2 -m unittest test_mixpanel' \
  'cd "$(REPO_ROOT)" && scripts/check-baseline.sh'; do
  if ! grep -Fq "$make_contract" "$MAKEFILE"; then
    printf '%s\n' "Makefile must preserve rooted recipe: $make_contract" >&2
    exit 1
  fi
done

for target in "docs:" "lint:" "test:" "build:" "verify:" "check:"; do
  if ! grep -Fq "$target" "$MAKEFILE"; then
    printf '%s\n' "Makefile must expose the $target gate." >&2
    exit 1
  fi
done

for documented in "Python 2.7" "make check" "make build" "scripts/check-baseline.sh"; do
  if ! grep -Fq "$documented" "$README"; then
    printf '%s\n' "README must document $documented." >&2
    exit 1
  fi
done

if ! grep -Fq "GitHub Actions" "$README"; then
  printf '%s\n' "README must document the GitHub Actions check." >&2
  exit 1
fi

if ! grep -Fq "callable(callback)" "$ROOT_DIR/mixpanel.py"; then
  printf '%s\n' "mixpanel.py must validate callbacks before request or thread creation." >&2
  exit 1
fi

prepare_properties_source=$(sed -n '/^def prepare_properties(/,/^$/p' "$ROOT_DIR/mixpanel.py")
if ! printf '%s\n' "$prepare_properties_source" | grep -Fq 'properties = dict(properties)' ||
   printf '%s\n' "$prepare_properties_source" | grep -Fq 'properties.copy()'; then
  printf '%s\n' "prepare_properties must canonicalize accepted mappings without virtual copy dispatch." >&2
  exit 1
fi

subclass_fixture=$(sed -n '/^class SelfCopyingDict(dict):/,/^$/p' "$ROOT_DIR/test_mixpanel.py")
for subclass_contract in "class SelfCopyingDict(dict):" "return self"; do
  if ! printf '%s\n' "$subclass_fixture" | grep -Fq "$subclass_contract"; then
    printf '%s\n' "Dict-subclass fixture must preserve $subclass_contract." >&2
    exit 1
  fi
done

sync_subclass_test=$(sed -n '/^    def test_track_isolates_self_copying_dict_subclass(/,/^    def /p' "$ROOT_DIR/test_mixpanel.py")
for sync_subclass_contract in \
  '"distinct_id": "user-subclass"' \
  '}, properties)' \
  'self.assertEqual("project-token", payload["properties"]["token"])' \
  'self.assertNotIn("token", callbacks[0][1])' \
  'self.assertNotIn("time", callbacks[0][1])'; do
  if ! printf '%s\n' "$sync_subclass_test" | grep -Fq "$sync_subclass_contract"; then
    printf '%s\n' "Synchronous dict-subclass regression must preserve $sync_subclass_contract." >&2
    exit 1
  fi
done

async_subclass_test=$(sed -n '/^    def test_track_async_isolates_self_copying_dict_subclass(/,/^    def /p' "$ROOT_DIR/test_mixpanel.py")
for async_subclass_contract in \
  '"distinct_id": "async-subclass"' \
  '}, properties)' \
  'self.assertEqual(1, len(FakeThread.created))' \
  'self.assertEqual("project-token", payload["properties"]["token"])' \
  'self.assertNotIn("token", callbacks[0][1])' \
  'self.assertNotIn("time", callbacks[0][1])'; do
  if ! printf '%s\n' "$async_subclass_test" | grep -Fq "$async_subclass_contract"; then
    printf '%s\n' "Asynchronous dict-subclass regression must preserve $async_subclass_contract." >&2
    exit 1
  fi
done

for document in "$README" "$ROOT_DIR/SECURITY.md" "$ROOT_DIR/VISION.md" "$ROOT_DIR/CHANGES.md"; do
  if ! grep -Fiq "dict-subclass property isolation" "$document"; then
    printf '%s\n' "$document must document dict-subclass property isolation." >&2
    exit 1
  fi
done

DICT_SUBCLASS_PLAN="$DOCS_PLANS/2026-06-17-dict-subclass-property-isolation.md"
if ! grep -Fq "Status: Completed" "$DICT_SUBCLASS_PLAN" ||
   ! grep -Fq "make check" "$DICT_SUBCLASS_PLAN"; then
  printf '%s\n' "Dict-subclass property isolation plan must record completed verification." >&2
  exit 1
fi

if [ "$(grep -Fc 'event = validate_event(event)' "$ROOT_DIR/mixpanel.py")" -ne 2 ] || \
   [ "$(grep -Fc 'properties = prepare_properties(properties)' "$ROOT_DIR/mixpanel.py")" -ne 2 ]; then
  printf '%s\n' "track and track_async must share event and property preflight validation." >&2
  exit 1
fi

if [ "$(grep -Fc "properties['token'] = self.token" "$ROOT_DIR/mixpanel.py")" -ne 1 ] || \
   grep -Fq 'if not properties.has_key("token")' "$ROOT_DIR/mixpanel.py"; then
  printf '%s\n' "Outbound event payloads must use the configured project token." >&2
  exit 1
fi

for token_contract in \
  "test_track_uses_configured_token_over_caller_property" \
  "test_track_async_uses_configured_token_over_caller_property" \
  '"token": "caller-token"' \
  'self.assertEqual("project-token", payload["properties"]["token"])'; do
  if ! grep -Fq "$token_contract" "$ROOT_DIR/test_mixpanel.py"; then
    printf '%s\n' "Project token authority tests must preserve $token_contract." >&2
    exit 1
  fi
done

for async_contract in \
  "test_track_async_rejects_invalid_inputs_before_thread" \
  "self.assertEqual([], FakeThread.created)" \
  "self.assertEqual([], self.urls)"; do
  if ! grep -Fq "$async_contract" "$ROOT_DIR/test_mixpanel.py"; then
    printf '%s\n' "Async input preflight tests must preserve $async_contract." >&2
    exit 1
  fi
done

if ! grep -Fq "class MixpanelError" "$ROOT_DIR/mixpanel.py" || \
   ! grep -Fq "validate_mixpanel_response(response_body)" "$ROOT_DIR/mixpanel.py" || \
   ! grep -Fq 'response_body.strip() != "1"' "$ROOT_DIR/mixpanel.py"; then
  printf '%s\n' "mixpanel.py must reject failed or unexpected response acknowledgements." >&2
  exit 1
fi

if ! grep -Fq "MAX_RESPONSE_BODY_BYTES = 1024" "$ROOT_DIR/mixpanel.py" || \
   ! grep -Fq "resp.read(MAX_RESPONSE_BODY_BYTES + 1)" "$ROOT_DIR/mixpanel.py" || \
   ! grep -Fq 'Mixpanel response exceeds 1024 bytes' "$ROOT_DIR/mixpanel.py"; then
  printf '%s\n' "mixpanel.py must bound untrusted response bodies before acknowledgement validation." >&2
  exit 1
fi

for test_contract in \
  "test_track_accepts_stripped_success_acknowledgement" \
  "test_track_rejects_failed_or_unexpected_acknowledgements" \
  "test_track_rejects_oversized_response_before_callback"; do
  if ! grep -Fq "$test_contract" "$ROOT_DIR/test_mixpanel.py"; then
    printf '%s\n' "test_mixpanel.py must include $test_contract." >&2
    exit 1
  fi
done

if ! grep -Fq "MAX_RESPONSE_BODY_BYTES + 1" "$ROOT_DIR/test_mixpanel.py" || \
   ! grep -Fq "private-upstream-response" "$ROOT_DIR/test_mixpanel.py"; then
  printf '%s\n' "test_mixpanel.py must prove the bounded read and body-safe overflow error." >&2
  exit 1
fi

if ! grep -Fq "finally:" "$ROOT_DIR/mixpanel.py" || ! grep -Fq "resp.close()" "$ROOT_DIR/mixpanel.py"; then
  printf '%s\n' "mixpanel.py must close opened HTTP responses on every read path." >&2
  exit 1
fi

for ignored in "*.py[cod]" "__pycache__/" "dist" "build" ".env" ".env.*" ".idea/" ".vscode/" "*.iml"; do
  if ! grep -Fq "$ignored" "$GITIGNORE"; then
    printf '%s\n' ".gitignore must include $ignored" >&2
    exit 1
  fi
done

bytecode_artifacts=$(find "$ROOT_DIR" -path "$ROOT_DIR/.git" -prune -o \( -name '*.pyc' -o -name '__pycache__' \) -print)
if [ -n "$bytecode_artifacts" ]; then
  printf '%s\n%s\n' "Python bytecode artifacts must not be kept in the repository tree:" "$bytecode_artifacts" >&2
  exit 1
fi

if ! tracked_local=$(git -C "$ROOT_DIR" ls-files '.env' '.env.*' '.idea' '.vscode' '*.iml'); then
  printf '%s\n' "Unable to inspect tracked local secret or editor metadata." >&2
  exit 1
fi
if [ -n "$tracked_local" ]; then
  printf '%s\n%s\n' "Local secrets or editor metadata must not be tracked:" "$tracked_local" >&2
  exit 1
fi

found_plan=0
for plan in "$DOCS_PLANS"/*.md; do
  [ -e "$plan" ] || continue
  found_plan=1
  if ! grep -Fq "Status: Completed" "$plan"; then
    printf '%s\n' "$plan must record completed status." >&2
    exit 1
  fi
  if ! grep -Fq "make check" "$plan"; then
    printf '%s\n' "$plan must document make check verification." >&2
    exit 1
  fi
done

if [ "$found_plan" -eq 0 ]; then
  printf '%s\n' "docs/plans must contain completed markdown plans." >&2
  exit 1
fi

if ! grep -Fq "Status: Completed" "$CI_PLAN" || ! grep -Fq "make check" "$CI_PLAN"; then
  printf '%s\n' "CI baseline plan must record completed status and make check verification." >&2
  exit 1
fi

if ! grep -Fq "Status: Completed" "$RESPONSE_BODY_PLAN" || \
   ! grep -Fq "make check" "$RESPONSE_BODY_PLAN" || \
   ! grep -Fq "focused hostile mutations" "$RESPONSE_BODY_PLAN"; then
  printf '%s\n' "Response body size plan must record completed status and actual verification." >&2
  exit 1
fi

ASYNC_JSON_PLAN="$ROOT_DIR/docs/plans/2026-06-13-async-json-preflight.md"
for evidence in \
  'Canonical `make check` passed' \
  'digest-pinned Python 2.7.18 container' \
  'Eight hostile mutations' \
  'Workflow YAML parsing' \
  'secret scanning' \
  'generated-artifact scanning' \
  '`git diff --check` passed'; do
  if ! grep -Fq "$evidence" "$ASYNC_JSON_PLAN"; then
    printf '%s\n' "Async JSON preflight plan must preserve verification evidence: $evidence" >&2
    exit 1
  fi
done

LOCATION_INDEPENDENT_MAKE_PLAN="$ROOT_DIR/docs/plans/2026-06-14-location-independent-make.md"
for evidence in \
  'unrelated directory' \
  'digest-pinned Python 2.7.18 container' \
  'hostile mutations rejected' \
  '`git diff --check`'; do
  if ! grep -Fq "$evidence" "$LOCATION_INDEPENDENT_MAKE_PLAN"; then
    printf '%s\n' "Location-independent Make plan must preserve verification evidence: $evidence" >&2
    exit 1
  fi
done

CALLBACK_TOKEN_PLAN="$ROOT_DIR/docs/plans/2026-06-14-callback-token-isolation.md"
for evidence in \
  'Status: Completed' \
  'Canonical `make check` passed' \
  'hostile mutations' \
  'configured project token' \
  'generated timestamp' \
  '`git diff --check`'; do
  if ! grep -Fq "$evidence" "$CALLBACK_TOKEN_PLAN"; then
    printf '%s\n' "Callback token-isolation plan must preserve verification evidence: $evidence" >&2
    exit 1
  fi
done

for documented in "$README" "$ROOT_DIR/SECURITY.md" "$ROOT_DIR/CHANGES.md"; do
  if ! grep -Fq "credential-free callback properties" "$documented"; then
    printf '%s\n' "$documented must document credential-free callback properties." >&2
    exit 1
  fi
done

for documented in "$README" "$ROOT_DIR/SECURITY.md" "$ROOT_DIR/VISION.md" "$ROOT_DIR/CHANGES.md"; do
  if ! grep -Fq "bounded response reads" "$documented"; then
    printf '%s\n' "$documented must document bounded response reads." >&2
    exit 1
  fi
  if ! grep -Fq "configured project token" "$documented"; then
    printf '%s\n' "$documented must document configured project token authority." >&2
    exit 1
  fi
  if ! grep -Fq "JSON-incompatible async properties" "$documented"; then
    printf '%s\n' "$documented must document async JSON serialization preflight." >&2
    exit 1
  fi
done
