#!/usr/bin/env bash
set -euo pipefail

python3 -B - <<'PY'
from pathlib import Path

source = Path("mixpanel.py").read_text()
compile(source, "mixpanel.py", "exec")

checks = [
    "DEFAULT_TIMEOUT = 10",
    "def __init__(self, token, api_key=None, timeout=DEFAULT_TIMEOUT):",
    "self.timeout = timeout",
    "timeout=self.timeout",
]

for expected in checks:
    if expected not in source:
        raise SystemExit("Missing expected timeout handling: %s" % expected)

if source.count("urllib2.urlopen(") != source.count("timeout=self.timeout"):
    raise SystemExit("Every urlopen call must pass timeout=self.timeout")
PY
