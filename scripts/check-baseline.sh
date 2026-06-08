#!/usr/bin/env bash
set -euo pipefail

python3 -B - <<'PY'
from pathlib import Path

source = Path("mixpanel.py").read_text()
compile(source, "mixpanel.py", "exec")

if "http://api.mixpanel.com" in source:
    raise SystemExit("Mixpanel runtime endpoints must use HTTPS")

for expected in [
    'TRACK_BASE_URL = "https://api.mixpanel.com/track/?data=%s"',
    'ARCHIVE_BASE_URL = "https://api.mixpanel.com/import/?data=%s&api_key=%s"',
]:
    if expected not in source:
        raise SystemExit("Missing expected HTTPS constant: %s" % expected)
PY
