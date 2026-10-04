"""Remote-side read-only file inventory for the hash-pinned mirror (stdlib only, Python 3.6+).

Not executed by the readout tool and never run from this checkout against Anvil.  The session
that holds the SSH route pipes it to the remote Python 3.9 on stdin, the same way
watch_trial_readonly.py runs its observation script:

    ssh ... /apps/spack/.../python3 - ROOT [--max-hash-mb N] [--include PREFIX ...] < remote_inventory_snippet.py

ROOT is the trial parent, e.g. /anvil/projects/x-che260157/sts_pa_catalyst_2026-10-03; each --include
is a path prefix relative to ROOT (trial_results, trial_<job>.log).  Files larger than the hash limit
(wavefunctions, charge densities) are listed with size and no sha256, so the readout can size-check
them without a login-node hashing load.  It lists and reads only; it opens no output for writing.
"""
import hashlib
import json
import os
import sys


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(root, includes, limit):
    rows = []
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs.sort()
        for name in sorted(files):
            path = os.path.join(current, name)
            relative = os.path.relpath(path, root).replace(os.sep, "/")
            if includes and not any(relative == p or relative.startswith(p.rstrip("/") + "/") for p in includes):
                continue
            info = os.lstat(path)
            link = os.path.islink(path)
            row = {"path": relative, "size": info.st_size, "mtime": int(info.st_mtime), "islink": link, "sha256": None}
            if not link and info.st_size <= limit:
                row["sha256"] = sha256_file(path)
            rows.append(row)
    return rows


def main(argv):
    root, includes, limit = None, [], 50 * 1048576
    items = list(argv)
    while items:
        item = items.pop(0)
        if item == "--include":
            includes.append(items.pop(0))
        elif item == "--max-hash-mb":
            limit = int(float(items.pop(0)) * 1048576)
        elif root is None:
            root = item
        else:
            raise SystemExit("unexpected argument: " + item)
    if root is None or not os.path.isdir(root):
        raise SystemExit("ROOT directory required")
    print(json.dumps({"root": root, "includes": includes, "hash_size_limit_bytes": limit,
                      "files": inventory(root, includes, limit)}, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
