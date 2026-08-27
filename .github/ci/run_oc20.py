#!/usr/bin/env python3
"""The A9.2.1 OC20 negative control, with its transport mechanism left UNELECTED.

Registered threshold, docs/43-prereg-week1-factorial.md :1856, verbatim:

    "In force-only mode, exactly 0.00 % of the 500 relaxations contain any
     adsorbate atom (tags == 2) with a lateral force component that is exactly
     zero in every ionic step (the LOCKED criterion), with constrained atoms
     excluded per A9.1, and the per-step exact-zero count over all unconstrained
     atoms and axes is reported alongside. Any nonzero rate voids every
     downstream symmetry number until the detector is repaired. A nonzero rate
     may not be explained away as print quantisation by argument; if it occurs,
     the offending frames are exhibited and the number stays void until the
     detector is repaired."

WHY THIS SCRIPT REFUSES TO CHOOSE A TRANSPORT
---------------------------------------------
:1868 leaves the mechanism open, and says so explicitly:

    "THRESHOLD (open at adoption 2026-08-23 -- entrant's call between two
     mechanisms, written once in a dated line before the OC20 control first runs
     in CI): (a) the 500-file sample is published as a sha256-pinned release
     asset of the public repo ... and the workflow downloads and hash-checks it;
     or (b) a self-hosted runner on the STS machine holds the sample. Under
     either, a commit on which the OC20 job did not execute is not green."

Both mechanisms are implemented below. NEITHER is the default. Until the entrant
writes his dated line and sets $S1_OC20_MECHANISM, this script reports
NOT MEASURED and exits nonzero -- which, per the sentence above, is correctly
not green.

The 500 are already drawn and their manifest is already committed
(docs/research/oc20-val_id/first500.txt and first500.SHA256SUMS, A9.7 act 3,
2026-08-23). The draw is fixed: "no re-draw, no substitution, no second sample"
(:1854). This script verifies the sample against that committed manifest before
a single trajectory is scored; a hash mismatch is a hard failure, never a warning.

AUTHORSHIP: written by AI as "the CI workflow" under the A9.1 :1840 permitted
list. It moves bytes and checks hashes. It does not read a trajectory: the OC20
trajectory reader is named core at :1840 and is the entrant's.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DRAW_DIR = os.path.join(ROOT, "docs", "research", "oc20-val_id")
SUMS = os.path.join(DRAW_DIR, "first500.SHA256SUMS")

MEASURED = "MEASURED"
NOT_MEASURED = "NOT MEASURED"

OPEN_DECISION = """\
$S1_OC20_MECHANISM is not set, so the OC20 control did not execute.

  This is an OPEN REGISTERED DECISION and CI will not make it. docs/43:1868:
  "THRESHOLD (open at adoption 2026-08-23 -- entrant's call between two
   mechanisms, written once in a dated line before the OC20 control first runs
   in CI): (a) the 500-file sample is published as a sha256-pinned release asset
   of the public repo ... and the workflow downloads and hash-checks it; or
   (b) a self-hosted runner on the STS machine holds the sample. Under either, a
   commit on which the OC20 job did not execute is not green."

  To elect (a):  write the dated line, publish the 500-file sample as a release
                 asset, then set repository variable S1_OC20_MECHANISM=release-asset
                 and S1_OC20_ASSET_URL=<url of the archive>.
  To elect (b):  write the dated line, register the STS machine as a self-hosted
                 runner, then set S1_OC20_MECHANISM=self-hosted and
                 S1_OC20_SAMPLE_DIR=<directory holding the 500 files>.

  Either way the sample is verified against docs/research/oc20-val_id/first500.SHA256SUMS,
  which is already committed (A9.7 act 3, 2026-08-23). The draw is fixed:
  "no re-draw, no substitution, no second sample" (:1854).
"""


def load_toml(path):
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover
        try:
            import tomli as tomllib  # type: ignore
        except ModuleNotFoundError:
            raise SystemExit("FATAL: need Python 3.11+ or `tomli` to read %s" % path)
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def read_sums(path):
    want = {}
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                raise SystemExit("FATAL: bad line in %s: %r" % (path, line))
            want[parts[1].strip().lstrip("*")] = parts[0].lower()
    return want


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sample(sample_dir, want):
    """Every one of the 500, present and hash-matching. No tolerance, no sampling."""
    missing, bad = [], []
    for name, digest in want.items():
        p = os.path.join(sample_dir, name)
        if not os.path.exists(p):
            missing.append(name)
            continue
        if sha256_file(p) != digest:
            bad.append(name)
    return missing, bad


def finish(out_json, status, detail, **extra):
    rec = {"status": status, "detail": detail}
    rec.update(extra)
    if out_json:
        with open(out_json, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=1)
    print(detail)
    return 0 if (status == MEASURED and extra.get("green")) else 1


def main():
    ap = argparse.ArgumentParser(description="A9.2.1 OC20 negative control")
    ap.add_argument("--invocation", default=os.path.join(HERE, "silentgate-invocation.toml"))
    ap.add_argument("--out-json", default=None)
    args = ap.parse_args()

    mech = os.environ.get("S1_OC20_MECHANISM", "").strip()
    if not mech:
        return finish(args.out_json, NOT_MEASURED, OPEN_DECISION)
    if mech not in ("release-asset", "self-hosted"):
        return finish(
            args.out_json, NOT_MEASURED,
            "S1_OC20_MECHANISM=%r is not one of the two registered mechanisms "
            "('release-asset', 'self-hosted'; docs/43:1868)." % mech,
        )

    if not os.path.exists(SUMS):
        return finish(args.out_json, NOT_MEASURED,
                      "the committed draw manifest %s is missing" % SUMS)
    want = read_sums(SUMS)
    if len(want) != 500:
        return finish(
            args.out_json, NOT_MEASURED,
            "the draw manifest lists %d files, not the registered N = 500 (:1854)"
            % len(want),
        )

    if mech == "self-hosted":
        sample_dir = os.environ.get("S1_OC20_SAMPLE_DIR", "").strip()
        if not sample_dir:
            return finish(args.out_json, NOT_MEASURED,
                          "S1_OC20_MECHANISM=self-hosted but S1_OC20_SAMPLE_DIR is unset")
    else:
        url = os.environ.get("S1_OC20_ASSET_URL", "").strip()
        if not url:
            return finish(args.out_json, NOT_MEASURED,
                          "S1_OC20_MECHANISM=release-asset but S1_OC20_ASSET_URL is unset")
        sample_dir = os.environ.get("S1_OC20_SAMPLE_DIR", "").strip() or os.path.join(
            ROOT, ".oc20-sample")
        os.makedirs(sample_dir, exist_ok=True)
        archive = os.path.join(sample_dir, "sample-archive")
        rc = subprocess.run(["curl", "-fsSL", "-o", archive, url]).returncode
        if rc != 0:
            return finish(args.out_json, NOT_MEASURED,
                          "download of the release asset failed (curl rc=%d): %s" % (rc, url))
        rc = subprocess.run(["tar", "-xf", archive, "-C", sample_dir]).returncode
        if rc != 0:
            return finish(args.out_json, NOT_MEASURED,
                          "extraction of the release asset failed (tar rc=%d)" % rc)
        # The archive may put the files in a sub-directory; find the one holding them.
        probe = next(iter(want))
        if not os.path.exists(os.path.join(sample_dir, probe)):
            for dirpath, _dirnames, filenames in os.walk(sample_dir):
                if probe in filenames:
                    sample_dir = dirpath
                    break

    missing, bad = verify_sample(sample_dir, want)
    if missing or bad:
        return finish(
            args.out_json, NOT_MEASURED,
            "the sample does not match the committed draw: %d missing, %d hash-mismatched "
            "(e.g. missing %s; mismatched %s). The draw is fixed -- 'no re-draw, no "
            "substitution, no second sample' (:1854) -- so this is a transport failure "
            "to fix, never a reason to re-draw."
            % (len(missing), len(bad), (missing[:3] or ["-"]), (bad[:3] or ["-"])),
        )

    cfg = load_toml(args.invocation)
    oc20_cmd = (cfg.get("cli", {}).get("oc20_cmd") or "").strip()
    if not oc20_cmd:
        return finish(
            args.out_json, NOT_MEASURED,
            "sample verified (500/500 sha256 match) but silentgate-invocation.toml "
            "declares no oc20_cmd. The OC20 trajectory reader and the CLI are core "
            "(docs/43:1840), so CI does not invent their interface.",
        )

    # Split the template FIRST, substitute into the argv after -- shlex in POSIX
    # mode eats the backslashes of a Windows path and hands the tool a path it
    # cannot open. Same fix as run_controls.run_command().
    argv = [tok.replace("{sample_dir}", sample_dir) for tok in shlex.split(oc20_cmd)]
    proc = subprocess.run(argv, capture_output=True, text=True, cwd=ROOT)
    if proc.returncode != 0:
        return finish(args.out_json, NOT_MEASURED,
                      "oc20_cmd failed (rc=%d): %s" % (proc.returncode,
                                                       (proc.stderr or "").strip()[:400]))
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return finish(args.out_json, NOT_MEASURED, "oc20_cmd stdout is not JSON: %s" % exc)

    schema = cfg.get("schema", {})
    runs_ptr = schema.get("runs_array") or ""
    lock_ptr = schema.get("locked_force_only") or ""
    path_ptr = schema.get("path") or ""
    zeros_ptr = schema.get("per_step_exact_zero_count") or ""
    if not runs_ptr or not lock_ptr or not path_ptr:
        return finish(args.out_json, NOT_MEASURED,
                      "[schema] runs_array / locked_force_only / path are unmapped "
                      "in silentgate-invocation.toml")

    def deref(obj, ptr):
        cur = obj
        for key in ptr.lstrip("/").split("/"):
            cur = cur.get(key) if isinstance(cur, dict) else None
        return cur

    cur = deref(payload, runs_ptr)
    if not isinstance(cur, list):
        return finish(args.out_json, NOT_MEASURED,
                      "runs_array pointer %r resolved to nothing in the OC20 output"
                      % runs_ptr)

    # Tie the census back to the sample that was hash-verified. Without this the
    # script verifies 500 files and then accepts ANY 500 records as "the OC20
    # val_id first-500" -- the verification and the measurement would never meet.
    scored = set()
    for item in cur:
        v = deref(item, path_ptr)
        if isinstance(v, str):
            scored.add(os.path.basename(v.replace("\\", "/")))
    unexpected = sorted(scored - set(want))
    unscored = sorted(set(want) - scored)
    if unexpected or unscored:
        return finish(
            args.out_json, NOT_MEASURED,
            "the census did not score the sample that was verified: %d of the 500 "
            "drawn files unscored (e.g. %s), %d records outside the draw (e.g. %s). "
            "The draw is fixed -- 'no re-draw, no substitution, no second sample' "
            "(:1854)."
            % (len(unscored), unscored[:3] or "-", len(unexpected), unexpected[:3] or "-"),
        )

    n = len(cur)
    locked, blank = [], 0
    for item in cur:
        v = deref(item, lock_ptr)
        if not isinstance(v, bool):
            # A null is NOT MEASURED, never "not locked". Counting nulls as
            # not-locked would report "exactly 0.00 %" from a census that
            # answered nothing -- the fail-open A9.2 exists to prevent.
            blank += 1
        elif v:
            locked.append(item)
    if blank:
        return finish(
            args.out_json, NOT_MEASURED,
            "%d of %d trajectories returned no boolean LOCKED verdict. A null is "
            "NOT MEASURED, not not-locked, so the 0.00 %% rate is not computed."
            % (blank, n),
        )
    if n != 500:
        return finish(
            args.out_json, NOT_MEASURED,
            "the census returned %d trajectories, not the registered N = 500 "
            "(:1854). The draw is fixed: no re-draw, no substitution, no second "
            "sample." % n,
        )
    rate = round(100.0 * len(locked) / n, 2)

    # The registered threshold has TWO halves (:1856): the 0.00 % rate, "and the
    # per-step exact-zero count over all unconstrained atoms and axes is reported
    # alongside". A control that produces the rate and not the companion count has
    # met half of it, so the companion is required rather than optional.
    zeros_total = None
    if zeros_ptr:
        vals = [deref(item, zeros_ptr) for item in cur]
        bad = [i for i, v in enumerate(vals) if not isinstance(v, int)]
        if bad:
            return finish(
                args.out_json, NOT_MEASURED,
                "%d of %d trajectories reported no per-step exact-zero count. :1856 "
                "requires it 'reported alongside' the rate." % (len(bad), n),
            )
        zeros_total = sum(vals)
    else:
        return finish(
            args.out_json, NOT_MEASURED,
            "[schema] per_step_exact_zero_count is unmapped. :1856 registers the "
            "rate AND 'the per-step exact-zero count over all unconstrained atoms "
            "and axes ... reported alongside'; the control is not complete without "
            "both.",
        )

    green = len(locked) == 0
    detail = ("OC20 val_id first-500: %s%% of %d relaxations LOCKED in force-only mode "
              "(registered: exactly 0.00 %% of 500); per-step exact-zero count over all "
              "unconstrained atoms and axes = %d." % (rate, n, zeros_total))
    if not green and locked:
        detail += (" A nonzero rate 'may not be explained away as print quantisation by "
                   "argument; if it occurs, the offending frames are exhibited and the "
                   "number stays void until the detector is repaired' (:1856). Offenders: "
                   + ", ".join(str(deref(x, path_ptr))[:80] for x in locked[:5]))
    return finish(args.out_json, MEASURED, detail,
                  n_relaxations=n, n_locked=len(locked),
                  locked_rate_percent=rate,
                  per_step_exact_zero_count=zeros_total, green=green)


if __name__ == "__main__":
    sys.exit(main())
