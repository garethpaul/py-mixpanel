#!/usr/bin/env bash
set -euo pipefail

grep -q 'TRACK_BASE_URL = "https://api.mixpanel.com/track/?data=%s"' mixpanel.py
grep -q 'ARCHIVE_BASE_URL = "https://api.mixpanel.com/import/?data=%s&api_key=%s"' mixpanel.py

if grep -n 'http://api\.mixpanel\.com' mixpanel.py; then
  echo "Mixpanel API endpoints must not use cleartext HTTP" >&2
  exit 1
fi
