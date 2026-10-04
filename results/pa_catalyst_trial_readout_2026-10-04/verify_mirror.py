"""Verify the local mirror against the remote read-only inventory (sha256 + size, both ends).

Usage: python verify_mirror.py REMOTE_INVENTORY.json MIRROR_DIR OUT.json [REMOTE_INVENTORY_2.json]

Reads only; writes OUT.json (new file, refuses to overwrite).  The optional second inventory is a later
re-run of the same remote read-only snippet; it is compared with the first to show the remote side did
not change while the mirror was taken (size, mtime, sha256 where hashed).
"""
import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main(argv):
    remote_path, mirror, out = Path(argv[0]), Path(argv[1]), Path(argv[2])
    remote = json.loads(remote_path.read_text(encoding="utf-8"))
    rows = remote["files"]
    by_path = {r["path"]: r for r in rows}
    local = {p.relative_to(mirror).as_posix(): p for p in sorted(mirror.rglob("*")) if p.is_file()}
    result = {"remote_inventory": remote_path.name, "remote_files": len(rows),
              "remote_bytes": sum(r["size"] for r in rows),
              "remote_hashed_files": sum(1 for r in rows if r["sha256"]),
              "remote_hash_limit_bytes": remote["hash_size_limit_bytes"],
              "local_files": len(local), "local_bytes": 0, "verified": [], "mismatch": [],
              "local_not_in_remote_inventory": sorted(set(local) - set(by_path)),
              "copied_without_remote_hash": []}
    for rel, path in local.items():
        size = path.stat().st_size
        result["local_bytes"] += size
        row = by_path.get(rel)
        if row is None:
            continue
        digest = sha256_file(path)
        if row["sha256"] is None:
            result["copied_without_remote_hash"].append(rel)
        elif digest == row["sha256"] and size == row["size"]:
            result["verified"].append({"path": rel, "size": size, "sha256": digest})
        else:
            result["mismatch"].append({"path": rel, "local_size": size, "remote_size": row["size"],
                                       "local_sha256": digest, "remote_sha256": row["sha256"]})
    not_copied = [r for r in rows if r["path"] not in local]
    result["not_copied_files"] = len(not_copied)
    result["not_copied_bytes"] = sum(r["size"] for r in not_copied)
    result["not_copied_with_remote_hash"] = sum(1 for r in not_copied if r["sha256"])
    result["not_copied_size_only"] = sum(1 for r in not_copied if not r["sha256"])
    result["all_copied_files_hash_verified"] = (not result["mismatch"] and not result["copied_without_remote_hash"]
                                               and not result["local_not_in_remote_inventory"]
                                               and len(result["verified"]) == len(local))
    if len(argv) > 3:
        second = json.loads(Path(argv[3]).read_text(encoding="utf-8"))
        a = {r["path"]: (r["size"], r["mtime"], r["sha256"]) for r in rows}
        b = {r["path"]: (r["size"], r["mtime"], r["sha256"]) for r in second["files"]}
        result["remote_unchanged_between_inventories"] = (a == b)
        result["remote_changed_paths"] = sorted(p for p in set(a) | set(b) if a.get(p) != b.get(p))[:20]
        result["second_inventory"] = Path(argv[3]).name
    with open(out, "x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("verified",)}, indent=1))
    return 0 if result["all_copied_files_hash_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
