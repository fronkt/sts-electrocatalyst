#!/usr/bin/env python3
"""Anvil <-> local mirror audit for runs/: what exists on the run tree and not here.

WHY THIS EXISTS
---------------
The same defect has now been recorded three times: an artefact that exists on
Anvil is described in this repository as missing or unrun.

  d26ea49            "the exhaustive search missed /anvil/projects, where the
                      run tree lives"
  docs/43:4134-4153  the Ni repair deck, called "unrun ... ~50 SU" in docs/78;
                      it had run 2026-08-25 as array 20135148 task 2
  2026-09-05         the replay leg of that same chain
                      (runs/s3/Ni/s0_OH__2x1v_off.replay.out), the final Ni
                      s0_OOH__2x1v_mir attempt, and 14 further S3 outputs in
                      Co/Fe/Mn -- all ledger-cited, none mirrored

docs/43:4148 records the check that should have followed the second instance:
"no line may assert that a deck is unrun without a listing of the Anvil run
tree in the same act." This script is that listing, made cheap enough to run
before any such sentence is written.

WHAT IT DOES
------------
1. On Anvil: `find runs -type f | xargs md5sum` under the run tree.
2. Locally:  the same over runs/.
3. Classifies every path as SAME / ANVIL-ONLY / LOCAL-ONLY / DIFFER and prints a
   per-directory table plus the lists that matter most: anvil-only pw.x outputs
   (the d26ea49 class) and any output that DIFFERS between the two ends (which
   would mean two records of one run).

It moves no file and changes nothing at either end. Pulling is a separate,
deliberate act, because several anvil-only classes are out of git BY DESIGN:
pseudopotentials, .save/ directories, *.pdos*, *.run.in (.gitignore:39) and the
full .projwfc.out files (912 MB across 383 files on 2026-09-05; the banked
readout is the .lowdin.txt beside each, whose header says "full projwfc output
retained on Anvil beside the deck").

LISTING FORMATS
---------------
GNU coreutils md5sum prints `<hash>  <path>` (two spaces). The md5sum in Git for
Windows prints `<hash> *./<path>` (one space, binary-mode star, ./ prefix).
Splitting on two spaces silently drops every local line -- the 2026-09-05 diff
reported "Ni local: 0" for exactly that reason -- so parsing splits on the first
run of whitespace and strips the star and ./ prefix.
"""
from __future__ import annotations

import argparse
import collections
import os
import subprocess
import sys

DEFAULT_HOST = "x-fcai3@anvil.rcac.purdue.edu"
DEFAULT_REMOTE_ROOT = "/anvil/projects/x-che260157/sts"

# Classes that are out of git by design; reported as counts, never listed.
BY_DESIGN = (".UPF", ".hdf5", ".xml", ".run.in", ".pdos", ".save/", ".wfc", ".mix",
             ".projwfc.out", "charge-density", "data-file-schema")


def parse_listing(text, strip_prefix="runs/"):
    """`<hash> <path>` per line, in either md5sum dialect -> {path: hash}."""
    out = {}
    for line in text.splitlines():
        line = line.rstrip("\r\n")
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        digest, name = parts
        name = name.lstrip("*")
        if name.startswith("./"):
            name = name[2:]
        if strip_prefix and name.startswith(strip_prefix):
            name = name[len(strip_prefix):]
        out[name.replace("\\", "/")] = digest.lower()
    return out


def classify(remote, local):
    same, ronly, lonly, differ = [], [], [], []
    for k, h in remote.items():
        if k not in local:
            ronly.append(k)
        elif local[k] != h:
            differ.append(k)
        else:
            same.append(k)
    for k in local:
        if k not in remote:
            lonly.append(k)
    return sorted(same), sorted(ronly), sorted(lonly), sorted(differ)


def is_by_design(path):
    return any(tag in path for tag in BY_DESIGN)


def is_pw_output(path):
    base = path.rsplit("/", 1)[-1]
    return base.endswith(".out") and ".projwfc" not in base


def group(path):
    parts = path.split("/")
    if len(parts) > 2 and parts[0] in ("s3", "a0", "s0", "probe", "probe_d02", "chains"):
        return "/".join(parts[:2])
    return parts[0]


def remote_listing(host, root):
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=25", host,
           "cd %s && find runs -type f -print0 | xargs -0 md5sum" % root]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("remote listing failed (rc=%d): %s"
                         % (proc.returncode, proc.stderr.strip()[-400:]))
    return proc.stdout


def local_listing(runs_dir):
    import hashlib
    lines = []
    for dirpath, _d, files in os.walk(runs_dir):
        for f in files:
            p = os.path.join(dirpath, f)
            h = hashlib.md5()
            with open(p, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
            rel = os.path.relpath(p, runs_dir).replace("\\", "/")
            lines.append("%s  %s" % (h.hexdigest(), rel))
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--remote-root", default=DEFAULT_REMOTE_ROOT)
    ap.add_argument("--runs", default="runs", help="local runs/ directory")
    ap.add_argument("--remote-list", help="reuse a saved remote md5 listing")
    ap.add_argument("--local-list", help="reuse a saved local md5 listing")
    ap.add_argument("--save-dir", help="write the four class lists here")
    ap.add_argument("--max-list", type=int, default=80)
    args = ap.parse_args(argv)

    rtext = (open(args.remote_list, encoding="utf-8", errors="replace").read()
             if args.remote_list else remote_listing(args.host, args.remote_root))
    ltext = (open(args.local_list, encoding="utf-8", errors="replace").read()
             if args.local_list else local_listing(args.runs))
    remote = parse_listing(rtext, "runs/")
    local = parse_listing(ltext, "runs/")
    same, ronly, lonly, differ = classify(remote, local)

    print("remote files: %d   local files: %d" % (len(remote), len(local)))
    print("SAME %d   ANVIL-ONLY %d   LOCAL-ONLY %d   DIFFER %d"
          % (len(same), len(ronly), len(lonly), len(differ)))

    S, R, L, D = (collections.Counter() for _ in range(4))
    for k in same:
        S[group(k)] += 1
    for k in ronly:
        R[group(k)] += 1
    for k in lonly:
        L[group(k)] += 1
    for k in differ:
        D[group(k)] += 1
    print("\n%-28s %8s %10s %10s %7s" % ("dir", "same", "anvil-only", "local-only", "differ"))
    for g in sorted(set(S) | set(R) | set(L) | set(D)):
        if R[g] or L[g] or D[g]:
            print("%-28s %8d %10d %10d %7d" % (g, S[g], R[g], L[g], D[g]))

    pw_ronly = [k for k in ronly if is_pw_output(k) and not is_by_design(k)]
    by_design = sum(1 for k in ronly if is_by_design(k))
    print("\nanvil-only, out of git by design (UPF/.save/pdos/run.in/projwfc.out ...): %d"
          % by_design)
    print("ANVIL-ONLY pw.x OUTPUTS -- the d26ea49 class -- %d:" % len(pw_ronly))
    for k in pw_ronly[:args.max_list]:
        print("   ", k)
    d_out = [k for k in differ if k.rsplit("/", 1)[-1].endswith(".out")]
    print("DIFFERING OUTPUTS (two records of one run) -- %d:" % len(d_out))
    for k in d_out[:args.max_list]:
        print("   ", k)
    other_d = collections.Counter(os.path.splitext(k)[1] or k for k in differ if k not in d_out)
    print("other differing files by extension:", dict(other_d.most_common(8)))

    if args.save_dir:
        os.makedirs(args.save_dir, exist_ok=True)
        for name, lst in (("same", same), ("anvil_only", ronly),
                          ("local_only", lonly), ("differ", differ)):
            with open(os.path.join(args.save_dir, "mirror_%s.txt" % name), "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(lst) + ("\n" if lst else ""))
        print("lists written to", args.save_dir)
    return 1 if (pw_ronly or d_out) else 0


if __name__ == "__main__":
    sys.exit(main())
