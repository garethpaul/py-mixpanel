#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
README="$ROOT_DIR/README.md"
MAKEFILE="$ROOT_DIR/Makefile"
GITIGNORE="$ROOT_DIR/.gitignore"
DOCS_PLANS="$ROOT_DIR/docs/plans"
WORKFLOW="$ROOT_DIR/.github/workflows/check.yml"

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
  "docs/plans/2026-06-10-hosted-legacy-validation.md" \
  ".github/workflows/check.yml" \
  "scripts/check-baseline.sh"; do
  require_file "$path"
done

if ! grep -Fxq 'permissions:' "$WORKFLOW" || ! grep -Fxq '  contents: read' "$WORKFLOW"; then
  printf '%s\n' "Hosted validation must use read-only repository contents permission." >&2
  exit 1
fi

if ! grep -Fq 'actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10' "$WORKFLOW"; then
  printf '%s\n' "Hosted validation must pin the reviewed actions/checkout v6.0.3 commit." >&2
  exit 1
fi

if ! grep -Fq 'python:2.7.18@sha256:c934af72b8bd03b9804d5bde2569c320926e70392d708d113a2e71bcf98c8a20' "$WORKFLOW"; then
  printf '%s\n' "Hosted validation must pin the reviewed Python 2.7.18 image digest." >&2
  exit 1
fi

if grep -Fq 'setup-python@' "$WORKFLOW"; then
  printf '%s\n' "Hosted validation must use the pinned Python 2 container, not setup-python." >&2
  exit 1
fi

if grep -Fq 'continue-on-error' "$WORKFLOW"; then
  printf '%s\n' "Hosted validation must not allow legacy verification failures." >&2
  exit 1
fi

if ! grep -Eq '^[[:space:]]+run: make check$' "$WORKFLOW"; then
  printf '%s\n' "Hosted validation must run the canonical make check gate." >&2
  exit 1
fi

if grep -Fq 'command -v python2' "$MAKEFILE" || grep -Fq 'Skipping legacy Python 2' "$MAKEFILE"; then
  printf '%s\n' "Makefile must require Python 2 checks instead of skipping them." >&2
  exit 1
fi

if ! grep -Fq "scripts/check-baseline.sh" "$MAKEFILE"; then
  printf '%s\n' "Makefile must run scripts/check-baseline.sh from make check." >&2
  exit 1
fi

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

if ! grep -Fq "callable(callback)" "$ROOT_DIR/mixpanel.py"; then
  printf '%s\n' "mixpanel.py must validate callbacks before request or thread creation." >&2
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
