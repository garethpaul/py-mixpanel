#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
README="$ROOT_DIR/README.md"
MAKEFILE="$ROOT_DIR/Makefile"
GITIGNORE="$ROOT_DIR/.gitignore"
DOCS_PLANS="$ROOT_DIR/docs/plans"
CI_WORKFLOW="$ROOT_DIR/.github/workflows/check.yml"
CI_PLAN="$ROOT_DIR/docs/plans/2026-06-10-ci-baseline.md"

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
  ".github/workflows/check.yml" \
  "mixpanel.py" \
  "test_mixpanel.py" \
  "docs/plans/2026-06-08-py-mixpanel-baseline.md" \
  "docs/plans/2026-06-09-scripted-baseline-check.md" \
  "docs/plans/2026-06-10-ci-baseline.md" \
  "scripts/check-baseline.sh"; do
  require_file "$path"
done

if ! grep -Fq "scripts/check-baseline.sh" "$MAKEFILE"; then
  printf '%s\n' "Makefile must run scripts/check-baseline.sh from make check." >&2
  exit 1
fi

if ! grep -Fq "Skipping legacy Python 2 syntax checks" "$MAKEFILE" ||
  ! grep -Fq "Skipping legacy Python 2 Mixpanel tests" "$MAKEFILE"; then
  printf '%s\n' "Makefile must guard Python 2-dependent checks for hosted CI." >&2
  exit 1
fi

if ! grep -Fq "actions/checkout@v4" "$CI_WORKFLOW" ||
  ! grep -Fq "actions/setup-python@v5" "$CI_WORKFLOW" ||
  ! grep -Fq 'python-version: "3.12"' "$CI_WORKFLOW" ||
  ! grep -Fq "make check" "$CI_WORKFLOW"; then
  printf '%s\n' "GitHub Actions check workflow must set up Python and run make check." >&2
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

if ! grep -Fq "GitHub Actions" "$README"; then
  printf '%s\n' "README must document the GitHub Actions check." >&2
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

tracked_local=$(git -C "$ROOT_DIR" ls-files '.env' '.env.*' '.idea' '.vscode' '*.iml' || true)
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
