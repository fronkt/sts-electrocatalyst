#!/usr/bin/env python3
"""The campaign-wide GATE-1 census, measured from disk.

Why this exists
---------------
Two counts of the same population disagree in the record, and `tasks/todo.md` marks the
contradiction **owed, to be reconciled before any readout is quoted**:

  * `docs/45:255-256` (2026-08-24): "Full-S3 GATE-1 census now: **38 AGREE / 0 REFUSED /
    2 UNVERIFIED**".
  * `tasks/todo.md` (2026-08-26): "GATE-1 measured across all 35 pairs on disk ... 29 rows
    at dmagtot <= 0.01 agree to <= 0.044 meV; **6 rows at dmagtot >= 0.18 disagree by
    >= 7.394 meV**."

Neither was produced by a script, so neither can be re-run.  This one is.

The registered rules it scores (verbatim thresholds, not invented here)
----------------------------------------------------------------------
  * `docs/43:311-314` (P16): every relaxation gets a GATE-1 fresh-density fixed-geometry
    SCF at its own final coordinates; **if that SCF lands >= 5 meV LOWER, the state is
    re-relaxed from it** and the loop repeats.  -> verdict **BASIN_DRIFT**.
  * `docs/43:1589-1592` (A8.3): a `__g1` child that lands **above its parent by more than
    1 meV** is **REFUSED** and re-run from the parent's converged density; if the second
    attempt also lands above, the pair is **MULTISTABLE** and neither number is banked.
  * Otherwise **AGREE**.

`dmagtot` is reported for every pair because docs/43 P16 makes the magnetic branch the
thing a fixed-geometry replicate can silently change.

This script MEASURES; it decides nothing.  It banks no energy, moves no verdict, and
re-runs no deck.  Zero DFT.

Usage
-----
    python src/dft/gate1_census.py [--json OUT.json] [--md OUT.md]
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RUNS = os.path.join(ROOT, "runs")

RY_TO_MEV = 13605.693122994

BASIN_DRIFT_MEV = -5.0     # docs/43:311-314, child at or below this is BASIN_DRIFT
REFUSE_MEV = 1.0           # docs/43:1589-1592, child above this is REFUSED
BRANCH_MUB = 0.1           # docs/43 P16 confound tolerance


def final_energy_ry(path):
    e = None
    for line in open(path, encoding="utf-8", errors="replace"):
        if line.startswith("!") and "total energy" in line:
            m = re.search(r"=\s*([-\d.]+)\s*Ry", line)
            if m:
                e = float(m.group(1))
    return e


def final_totmag(path):
    m = None
    for line in open(path, encoding="utf-8", errors="replace"):
        if "total magnetization" in line:
            hit = re.search(r"=\s*([-\d.]+)", line)
            if hit:
                m = float(hit.group(1))
    return m


def converged(path):
    """A usable GATE-1 side: the SCF closed and the job did not die mid-write."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    if "convergence NOT achieved" in txt:
        return False
    return "!    total energy" in txt or "!!   total energy" in txt


_MANIFEST_CACHE = {}


def _manifest_parent(child_path):
    """Route 1: a sibling manifest.json that names `parent_out` for this deck.

    Only runs/s0/f_gate1_uladder/manifest.json carries this today; the resolver asks
    every directory so a future family gets picked up without a code change.
    """
    d = os.path.dirname(child_path)
    mp = os.path.join(d, "manifest.json")
    if mp not in _MANIFEST_CACHE:
        try:
            _MANIFEST_CACHE[mp] = json.load(open(mp, encoding="utf-8"))
        except Exception:
            _MANIFEST_CACHE[mp] = None
    man = _MANIFEST_CACHE[mp]
    if not isinstance(man, dict):
        return None
    decks = man.get("decks")
    if not isinstance(decks, dict):
        return None
    key = os.path.basename(child_path)[:-4] + ".in"
    entry = decks.get(key)
    if not isinstance(entry, dict):
        return None
    rel = entry.get("parent_out")
    if not rel:
        return None
    cand = os.path.join(ROOT, rel.replace("/", os.sep))
    return cand if os.path.exists(cand) else None


def parent_of(child_path):
    """Resolve a __g1 child to the relaxation it is a replicate of.

    Three routes, tried in order, and the route used is recorded per row so a reader
    can see how each pairing was made rather than trusting a naming convention:

      1. a sibling `manifest.json` whose `decks[<child>.in].parent_out` names the file
         (runs/s0/f_gate1_uladder);
      2. the same-directory conventional name -- `<stem>__g1[.fromparent].out` ->
         `<stem>.out`, and the basin family's older `_g1` spelling;
      3. the cross-directory basin convention -- `runs/s3/<M>/<state>__basin_g1.out`
         is a child of `runs/probe/<M>_basin/<state>.out`, which is where the basin
         re-relaxations live.

    A child no route resolves is returned as an orphan and counted; it is never
    silently dropped.
    """
    d = os.path.dirname(child_path)
    fn = os.path.basename(child_path)
    stem = fn[:-4] if fn.endswith(".out") else fn

    viam = _manifest_parent(child_path)
    if viam:
        return viam, "manifest"

    for suf in ("__g1.fromparent", "__g1", "_g1.fromparent", "_g1"):
        if stem.endswith(suf):
            base = stem[: -len(suf)]
            cand = os.path.join(d, base + ".out")
            if os.path.exists(cand):
                return cand, suf
            # route 3: the basin re-relaxation lives under runs/probe/<M>_basin/,
            # so a `<state>__basin_g1` child in runs/s3/<M>/ hops there -- and a child
            # already sitting IN runs/probe/<M>_basin/ finds its parent beside it.
            if base.endswith("__basin"):
                state = base[: -len("__basin")]
                here = os.path.join(d, state + ".out")
                if os.path.basename(d).endswith("_basin") and os.path.exists(here):
                    return here, "basin-samedir"
                metal = os.path.basename(d)
                cand2 = os.path.join(RUNS, "probe", metal + "_basin", state + ".out")
                if os.path.exists(cand2):
                    return cand2, "basin-crossdir"
            break
    return None, None


def find_children():
    out = []
    for dirpath, _dirnames, filenames in os.walk(RUNS):
        for fn in sorted(filenames):
            if not fn.endswith(".out"):
                continue
            stem = fn[:-4]
            if "g1" not in stem:
                continue
            if not (stem.endswith("__g1") or stem.endswith("_g1")
                    or stem.endswith("__g1.fromparent")
                    or stem.endswith("_g1.fromparent")):
                continue
            out.append(os.path.join(dirpath, fn))
    return sorted(out)


def family_of(path):
    rel = os.path.relpath(path, RUNS).replace("\\", "/")
    return rel.rsplit("/", 1)[0]


def verdict(de_mev):
    if de_mev is None:
        return "UNVERIFIED"
    if de_mev <= BASIN_DRIFT_MEV:
        return "BASIN_DRIFT"
    if de_mev > REFUSE_MEV:
        return "REFUSED"
    return "AGREE"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="gate1_census.py")
    ap.add_argument("--json", default=os.path.join(ROOT, "docs", "figs",
                                                   "gate1_census.json"))
    ap.add_argument("--md", default=os.path.join(
        ROOT, "docs", "research", "2026-09-03-gate1-census.md"))
    # The measurement date was hardcoded into the title as well as the path, so any
    # re-run silently produced a document TITLED 2026-09-03 carrying a later
    # measurement.  The default reproduces the original title byte-for-byte; a re-run
    # that measures new files passes the date it actually measured on.  The banked
    # FILENAME keeps its original date because it is the banked path.
    ap.add_argument("--asof", default="2026-09-03",
                    help="measurement date stamped into the document title")
    args = ap.parse_args(argv)

    rows = []
    orphans = []
    for child in find_children():
        parent, suf = parent_of(child)
        rel_c = os.path.relpath(child, RUNS).replace("\\", "/")
        if parent is None:
            orphans.append(dict(child=rel_c,
                                why="no parent .out at the conventional name"))
            continue
        ok_c, ok_p = converged(child), converged(parent)
        ec, ep = final_energy_ry(child), final_energy_ry(parent)
        de = None
        if ok_c and ok_p and ec is not None and ep is not None:
            de = (ec - ep) * RY_TO_MEV
        mc, mp = final_totmag(child), final_totmag(parent)
        dm = (mc - mp) if (mc is not None and mp is not None) else None
        rows.append(dict(
            family=family_of(child), child=rel_c,
            parent=os.path.relpath(parent, RUNS).replace("\\", "/"),
            resolved_by=suf, child_converged=ok_c, parent_converged=ok_p,
            dE_meV=de, dmagtot=dm,
            branch_changed=(None if dm is None else abs(dm) > BRANCH_MUB),
            verdict=verdict(de)))

    # --- A8.3's second attempt: which refusals discharge -----------------------
    # A8.3 refuses a cold `__g1` child that lands above its parent and orders it
    # re-run FROM THE PARENT'S CONVERGED DENSITY.  A refusal with an AGREEing
    # `.fromparent` sibling is therefore DISCHARGED, not standing -- and that
    # distinction is exactly what the two disputed records were counting
    # differently.  Only the second attempt can discharge; nothing else does.
    by_state = {}
    for r in rows:
        base = os.path.basename(r["child"])[:-4]
        for suf in ("__g1.fromparent", "_g1.fromparent", "__g1", "_g1"):
            if base.endswith(suf):
                key = (r["parent"], base[: -len(suf)])
                by_state.setdefault(key, []).append((suf, r))
                break
    for key, entries in by_state.items():
        fromparent = [r for suf, r in entries if "fromparent" in suf]
        for suf, r in entries:
            r["attempt"] = "second (fromparent)" if "fromparent" in suf else "first (cold)"
            r["discharged_by_second_attempt"] = bool(
                r["verdict"] == "REFUSED"
                and any(f["verdict"] == "AGREE" for f in fromparent))
    for r in rows:
        r.setdefault("attempt", "first (cold)")
        r.setdefault("discharged_by_second_attempt", False)

    counts = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    def _standing(rs):
        """The post-discharge reading: a refusal whose fromparent re-run agrees is
        not a standing refusal."""
        c = {}
        for r in rs:
            v = r["verdict"]
            if v == "REFUSED" and r["discharged_by_second_attempt"]:
                v = "AGREE (refusal discharged)"
            c[v] = c.get(v, 0) + 1
        return c

    # the two records under reconciliation
    s3 = [r for r in rows if r["family"].startswith("s3/")]
    s3_counts = {}
    for r in s3:
        s3_counts[r["verdict"]] = s3_counts.get(r["verdict"], 0) + 1

    scored = [r for r in rows if r["dE_meV"] is not None and r["dmagtot"] is not None]
    same_branch = [r for r in scored if abs(r["dmagtot"]) <= 0.01]
    diff_branch = [r for r in scored if abs(r["dmagtot"]) >= 0.18]
    mid_branch = [r for r in scored
                  if 0.01 < abs(r["dmagtot"]) < 0.18]

    def band(rs):
        if not rs:
            return None
        a = [abs(r["dE_meV"]) for r in rs]
        return dict(n=len(rs), min_abs_dE_meV=min(a), max_abs_dE_meV=max(a))

    out = dict(
        purpose="Reconciles docs/45:255-256 (38 AGREE / 0 REFUSED / 2 UNVERIFIED) with "
                "tasks/todo.md's 29-vs-6 branch split. Measured from disk; decides "
                "nothing, banks nothing, re-runs nothing.",
        thresholds=dict(basin_drift_meV=BASIN_DRIFT_MEV, refuse_meV=REFUSE_MEV,
                        branch_muB=BRANCH_MUB,
                        source="docs/43:311-314 (P16) and docs/43:1589-1592 (A8.3)"),
        n_children=len(rows) + len(orphans), n_paired=len(rows),
        orphans=orphans,
        counts_all=counts, counts_s3_only=s3_counts,
        counts_all_post_discharge=_standing(rows),
        counts_s3_post_discharge=_standing(s3),
        branch_split=dict(same_branch_le_0p01=band(same_branch),
                          different_branch_ge_0p18=band(diff_branch),
                          between=band(mid_branch)),
        rows=rows,
    )
    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")

    L = []
    A = L.append
    A("# The GATE-1 census, measured from disk (%s)" % args.asof)
    A("")
    A("*Generated by `src/dft/gate1_census.py`. Zero DFT. This document measures; it "
      "decides nothing, banks no energy and moves no verdict.*")
    A("")
    A("Registered thresholds, quoted not invented: a child **>= 5 meV below** its parent "
      "is **BASIN_DRIFT** (`docs/43:311-314`); a child **more than 1 meV above** is "
      "**REFUSED** (`docs/43:1589-1592`); otherwise **AGREE**.")
    A("")
    A("## Counts")
    A("")
    A("| population | " + " | ".join(sorted(counts)) + " |")
    A("|---" * (len(counts) + 1) + "|")
    A("| all paired children (n = %d) | " % len(rows)
      + " | ".join(str(counts[k]) for k in sorted(counts)) + " |")
    A("| `runs/s3/` only (n = %d) | " % len(s3)
      + " | ".join(str(s3_counts.get(k, 0)) for k in sorted(counts)) + " |")
    A("")
    A("**Post-discharge reading** — A8.3 orders a refused child re-run from the "
      "parent's converged density, so a refusal with an AGREEing `.fromparent` "
      "sibling is discharged, not standing:")
    A("")
    A("- all paired children: %s"
      % ", ".join("%s %d" % (k, v)
                  for k, v in sorted(out["counts_all_post_discharge"].items())))
    A("- `runs/s3/` only: %s"
      % ", ".join("%s %d" % (k, v)
                  for k, v in sorted(out["counts_s3_post_discharge"].items())))
    A("")
    if orphans:
        A("Children with no parent `.out` at the conventional name (%d): %s"
          % (len(orphans), ", ".join("`%s`" % o["child"] for o in orphans)))
        A("")
    A("## The branch split")
    A("")
    for label, key in (("|dmagtot| <= 0.01", "same_branch_le_0p01"),
                       ("0.01 < |dmagtot| < 0.18", "between"),
                       ("|dmagtot| >= 0.18", "different_branch_ge_0p18")):
        b = out["branch_split"][key]
        if b:
            A("- **%s**: n = %d, |dE| from %.4f to %.4f meV"
              % (label, b["n"], b["min_abs_dE_meV"], b["max_abs_dE_meV"]))
        else:
            A("- **%s**: none" % label)
    A("")
    A("## Every non-AGREE row")
    A("")
    A("| family | child | attempt | dE (meV) | dmagtot | verdict | discharged |")
    A("|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda r: (r["verdict"],
                                         r["dE_meV"] if r["dE_meV"] is not None else 0)):
        if r["verdict"] == "AGREE":
            continue
        A("| `%s` | `%s` | %s | %s | %s | **%s** | %s |"
          % (r["family"], os.path.basename(r["child"]), r["attempt"],
             "n/a" if r["dE_meV"] is None else "%+.3f" % r["dE_meV"],
             "n/a" if r["dmagtot"] is None else "%+.3f" % r["dmagtot"],
             r["verdict"],
             "**yes**" if r["discharged_by_second_attempt"] else "-"))
    A("")
    with open(args.md, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L))

    print(json.dumps({k: out[k] for k in ("n_children", "n_paired", "counts_all",
                                          "counts_s3_only", "branch_split")},
                     indent=1, sort_keys=True))
    print("\nwrote %s\nwrote %s" % (args.json, args.md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
