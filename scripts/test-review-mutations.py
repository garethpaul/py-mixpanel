from __future__ import print_function

import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MUTATIONS = [
    (
        "token tracking falls back to a query-string GET",
        '      url = build_track_request(params)\n',
        '      url = TRACK_BASE_URL + "?data=" + encode_payload(params)\n',
    ),
    (
        "track request loses form content type",
        '  request.add_header("Content-Type", "application/x-www-form-urlencoded")\n',
        '  request.add_header("Content-Type", "text/plain")\n',
    ),
    (
        "track request reports an incorrect content length",
        '  request.add_header("Content-Length", str(len(body)))\n',
        '  request.add_header("Content-Length", str(len(body) + 1))\n',
    ),
    (
        "request exception details escape",
        '  except Exception:\n    resp = None\n  if resp is None:\n    raise MixpanelError("Mixpanel request failed")\n',
        '  except Exception:\n    raise\n  if resp is None:\n    raise MixpanelError("Mixpanel request failed")\n',
    ),
    (
        "non-success HTTP status accepted",
        '    if status is not None and (status < 200 or status >= 300):\n',
        '    if False:\n',
    ),
    (
        "close failure masks the primary request failure",
        '  except Exception:\n    if failure is None:\n      failure = MixpanelError("Mixpanel request failed")\n',
        '  except Exception:\n    raise\n',
    ),
    (
        "nested mappings remain caller-owned",
        '        snapshot[key] = snapshot_json_value(item, active)\n',
        '        snapshot[key] = item\n',
    ),
    (
        "nested lists remain caller-owned",
        '  if isinstance(value, list):\n    active.add(identity)\n',
        '  if isinstance(value, list):\n    return value\n    active.add(identity)\n',
    ),
    (
        "dict subclass overrides control canonicalization",
        '      for key, item in dict.items(value):\n',
        '      for key, item in value.items():\n',
    ),
    (
        "async worker reads mutable tracker credentials",
        '    t = threading.Thread(target=self._track_prepared, kwargs={\n',
        '    t = threading.Thread(target=self.track, kwargs={\n',
    ),
    (
        "async worker can hold interpreter shutdown",
        '    t.daemon = True\n    t.start()\n',
        '    t.start()\n',
    ),
]


def copy_repository(destination):
    for name in ("mixpanel.py", "test_mixpanel.py"):
        shutil.copy2(os.path.join(ROOT, name), os.path.join(destination, name))


def run_mutation(label, old, new):
    destination = tempfile.mkdtemp(prefix="py-mixpanel-mutation-")
    try:
        copy_repository(destination)
        source_path = os.path.join(destination, "mixpanel.py")
        with open(source_path, "r") as source_file:
            source = source_file.read()
        if source.count(old) != 1:
            raise RuntimeError("Mutation anchor is not unique: %s" % label)
        with open(source_path, "w") as source_file:
            source_file.write(source.replace(old, new, 1))
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        with open(os.devnull, "w") as devnull:
            result = subprocess.call(
                [sys.executable, "-m", "unittest", "test_mixpanel"],
                cwd=destination,
                env=environment,
                stdout=devnull,
                stderr=devnull,
            )
        if result == 0:
            raise RuntimeError("Tests survived hostile mutation: %s" % label)
        print("rejected: %s" % label)
    finally:
        shutil.rmtree(destination)


def main():
    for mutation in MUTATIONS:
        run_mutation(*mutation)
    print("Rejected %d hostile mutations." % len(MUTATIONS))


if __name__ == "__main__":
    main()
