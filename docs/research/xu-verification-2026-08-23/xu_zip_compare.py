#!/usr/bin/env python3
"""A9.7 act 1 (docs/43 A9.3.1): compare the Zenodo zip listing with the hashed
GitHub-mirror listing (xu_tree.json, commit c4cb892...).
Comparison unit: the 6,989 blob paths and sizes; for each of the 815 pwscf.out
the git blob SHA-1 recomputed from the zip file's bytes (sha1('blob <len>\0'+bytes)).
A listing operation: no content is parsed or interpreted (A9.6).
Output: JSON report to stdout."""
import json, sys, zipfile, hashlib, posixpath

zip_path, tree_path = sys.argv[1], sys.argv[2]

tree = json.load(open(tree_path))
entries = tree["tree"] if isinstance(tree, dict) and "tree" in tree else tree
blobs = {e["path"]: e for e in entries if e.get("type") == "blob"}

zf = zipfile.ZipFile(zip_path)
zinfos = [i for i in zf.infolist() if not i.is_dir()]

# Determine common top-level prefix in the zip (if any)
tops = set(n.filename.split("/")[0] for n in zinfos)
prefix = tops.pop() + "/" if len(tops) == 1 else ""
def norm(name):
    return name[len(prefix):] if prefix and name.startswith(prefix) else name

zmap = {norm(i.filename): i for i in zinfos}

zpaths, tpaths = set(zmap), set(blobs)
common = zpaths & tpaths
only_zip = sorted(zpaths - tpaths)
only_tree = sorted(tpaths - zpaths)

size_mismatch = [{"path": p, "zip_size": zmap[p].file_size, "tree_size": blobs[p]["size"]}
                 for p in sorted(common) if zmap[p].file_size != blobs[p]["size"]]

# git blob SHA-1 recompute for every pwscf.out present in both listings
pwscf_out_tree = sorted(p for p in tpaths if posixpath.basename(p) == "pwscf.out")
sha_checked = sha_match = 0
sha_mismatch, sha_missing_in_zip = [], []
for p in pwscf_out_tree:
    if p not in zmap:
        sha_missing_in_zip.append(p)
        continue
    data = zf.read(zmap[p])
    h = hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()
    sha_checked += 1
    if h == blobs[p]["sha"]:
        sha_match += 1
    else:
        sha_mismatch.append({"path": p, "zip_git_blob_sha1": h, "tree_sha": blobs[p]["sha"]})

report = {
    "zip": zip_path.split("/")[-1],
    "zip_prefix_stripped": prefix,
    "zip_file_entries": len(zinfos),
    "tree_blob_entries": len(blobs),
    "paths_common": len(common),
    "paths_only_in_zip": len(only_zip),
    "paths_only_in_tree": len(only_tree),
    "only_in_zip_list": only_zip[:50],
    "only_in_tree_list": only_tree[:50],
    "size_mismatches": len(size_mismatch),
    "size_mismatch_list": size_mismatch[:50],
    "pwscf_out_in_tree": len(pwscf_out_tree),
    "pwscf_out_sha_checked": sha_checked,
    "pwscf_out_sha_match": sha_match,
    "pwscf_out_sha_mismatch": len(sha_mismatch),
    "sha_mismatch_list": sha_mismatch[:50],
    "pwscf_out_missing_in_zip": sha_missing_in_zip[:50],
}
print(json.dumps(report, indent=1))
