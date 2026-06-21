#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/py-mixpanel-root-control-XXXXXX")
trap 'rm -rf "$TEMP_ROOT"' EXIT HUP INT TERM
unset MAKEFILES MAKEFILE_LIST

grep -Fq 'sed_path=/usr/bin/sed' "$ROOT_DIR/Makefile"
grep -Fq 'sed_path=/bin/sed' "$ROOT_DIR/Makefile"
if grep -Eq '\|[[:space:]]+sed[[:space:]]' "$ROOT_DIR/Makefile"; then
  printf '%s\n' 'Makefile root resolution must not use caller-controlled PATH for sed' >&2
  exit 1
fi

CONTROL_DIR="$TEMP_ROOT/control"
CHECKOUT="$TEMP_ROOT/Py Mixpanel's [gate] \`touch MIXPANEL_BACKTICK_MARKER\`"
COMMAND_LOG="$TEMP_ROOT/commands.log"
FAKE_SHELL_LOG="$TEMP_ROOT/fake-shell.log"
mkdir "$CONTROL_DIR" "$CHECKOUT" "$CHECKOUT/scripts" "$CHECKOUT/docs" "$CHECKOUT/docs/plans"
CHECKOUT=$(CDPATH= cd -- "$CHECKOUT" && pwd -P)
MAKEFILE="$CHECKOUT/Makefile"
cp "$ROOT_DIR/Makefile" "$MAKEFILE"
printf '%s\n%s\n' 'Status: Completed' 'make check' >"$CHECKOUT/docs/plans/root.md"

write_logger() {
  cat >"$1" <<'EOF'
#!/bin/sh
printf '%s|%s\n' "$PWD" "$*" >> "$QUALITY_COMMAND_LOG"
EOF
  chmod +x "$1"
}

FAKE_BIN="$TEMP_ROOT/bin"
mkdir "$FAKE_BIN"
write_logger "$FAKE_BIN/python"
write_logger "$FAKE_BIN/python2"
for script in check-baseline.sh test-review-mutations.py test-makefile-root.sh; do
  write_logger "$CHECKOUT/scripts/$script"
done
FAKE_SHELL="$TEMP_ROOT/fake-shell"
cat >"$FAKE_SHELL" <<EOF
#!/bin/sh
: >'$FAKE_SHELL_LOG'
exec /bin/sh "\$@"
EOF
chmod +x "$FAKE_SHELL"

assert_commands() {
  scenario=$1 target=$2
  [ "$target" = docs ] && return
  [ -s "$COMMAND_LOG" ] || { printf '%s\n' "$scenario $target executed no quality command" >&2; exit 1; }
  while IFS= read -r command; do
    case "$command" in "$CHECKOUT|"*) ;; *) printf '%s\n' "$scenario $target escaped checkout: $command" >&2; exit 1;; esac
  done <"$COMMAND_LOG"
}

run_case() {
  scenario=$1 target=$2 mode=$3
  rm -f "$COMMAND_LOG"
  case "$mode" in
    default) args= ;;
    command-root) args="REPO_ROOT=/tmp/py-mixpanel-attacker-root" ;;
    command-shell) args="SHELL=$FAKE_SHELL" ;;
    command-flags) args='.SHELLFLAGS=-eu -c' ;;
  esac
  if [ "$mode" = environment-root ]; then
    (cd "$CONTROL_DIR" && REPO_ROOT=/tmp/py-mixpanel-attacker-root PATH="$FAKE_BIN:$PATH" QUALITY_COMMAND_LOG="$COMMAND_LOG" make --no-print-directory --file "$MAKEFILE" "$target")
  elif [ "$mode" = environment-shell ]; then
    (cd "$CONTROL_DIR" && SHELL="$FAKE_SHELL" PATH="$FAKE_BIN:$PATH" QUALITY_COMMAND_LOG="$COMMAND_LOG" make --no-print-directory --file "$MAKEFILE" "$target")
  elif [ "$mode" = environment-flags ]; then
    (cd "$CONTROL_DIR" && env '.SHELLFLAGS=-eu -c' PATH="$FAKE_BIN:$PATH" QUALITY_COMMAND_LOG="$COMMAND_LOG" make --no-print-directory --file "$MAKEFILE" "$target")
  else
    (cd "$CONTROL_DIR" && PATH="$FAKE_BIN:$PATH" QUALITY_COMMAND_LOG="$COMMAND_LOG" make --no-print-directory --file "$MAKEFILE" ${args:+"$args"} "$target")
  fi
  assert_commands "$scenario" "$target"
}

for target in build check docs lint mutations root-test test verify; do
  run_case default "$target" default
  run_case command-root "$target" command-root
  run_case environment-root "$target" environment-root
  run_case command-shell "$target" command-shell
  run_case environment-shell "$target" environment-shell
  run_case command-flags "$target" command-flags
  run_case environment-flags "$target" environment-flags
done

[ ! -e "$CONTROL_DIR/MIXPANEL_BACKTICK_MARKER" ] || { printf '%s\n' 'checkout-path backticks executed' >&2; exit 1; }
[ ! -e "$FAKE_SHELL_LOG" ] || { printf '%s\n' 'caller-controlled SHELL was executed' >&2; exit 1; }

DOLLAR_CHECKOUT="$TEMP_ROOT/Py Mixpanel \$(touch MIXPANEL_DOLLAR_MARKER)"
mkdir "$DOLLAR_CHECKOUT"
cp "$ROOT_DIR/Makefile" "$DOLLAR_CHECKOUT/Makefile"
if (cd "$CONTROL_DIR" && make --no-print-directory --file "$DOLLAR_CHECKOUT/Makefile" docs) >"$TEMP_ROOT/dollar.out" 2>&1; then exit 1; fi
[ ! -e "$CONTROL_DIR/MIXPANEL_DOLLAR_MARKER" ] || { printf '%s\n' 'checkout-path dollar substitution executed' >&2; exit 1; }

if (cd "$CONTROL_DIR" && make --no-print-directory --file "$MAKEFILE" MAKEFILE_LIST=/tmp/untrusted check) >"$TEMP_ROOT/list.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/list.out"
if (cd "$CONTROL_DIR" && MAKEFILE_LIST=/tmp/untrusted make --environment-overrides --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/environment-list.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILE_LIST must not be overridden' "$TEMP_ROOT/environment-list.out"
printf '%s\n' 'REPO_ROOT := /tmp/preloaded-attacker-root' >"$TEMP_ROOT/preloaded.mk"
if (cd "$CONTROL_DIR" && MAKEFILES="$TEMP_ROOT/preloaded.mk" make --no-print-directory --file "$MAKEFILE" check) >"$TEMP_ROOT/preloaded.out" 2>&1; then exit 1; fi
grep -Fq 'MAKEFILES must be empty' "$TEMP_ROOT/preloaded.out"
if (cd "$CONTROL_DIR" && make --no-print-directory --file "$MAKEFILE" PYTHON=/tmp/attacker-python check) >"$TEMP_ROOT/python.out" 2>&1; then exit 1; fi
grep -Fq 'PYTHON must be python or python2' "$TEMP_ROOT/python.out"

printf '%s\n' 'Makefile root tests passed: 56 executed target/authority cases, hostile backticks blocked, dollar paths failed closed, 2 MAKEFILE_LIST rejection cases, 1 MAKEFILES preload rejection, and 1 PYTHON rejection'
