"""How much of the archive was relaxed inside a symmetry constraint? (docs/43, block 1D)

The claim the lead contribution rests on is that adsorbate relaxations in this field are
routinely confined to the slab mirror plane, invisibly. `orient_starts.py` proved it for
four specific runs by showing max|F_y| = 0.0000000000 Ry/au over every ionic step. That is
the airtight demonstration, but it is expensive to state -- it means parsing every force
block of every run.

pw.x prints a cheaper witness in its header: the size of the symmetry group it found and
will symmetrise forces onto.

    Sym. Ops., with inversion, found          4 symmetry operations
    Sym. Ops., no inversion, found            2 symmetry operations

For a rutile(110) slab with an adsorbate built at y == 0, the surviving operations are the
mirror in y and whatever combines with it. So the number in that line is a direct readout
of how many degrees of freedom pw.x removed before the optimiser ever saw the structure:

    >1 operation  -> forces were symmetrised; some coordinate could not move
     1 operation  -> identity only; the relaxation was free (this is what nosym gives)

This script reports the distribution across the whole archive, and cross-checks it against
the force evidence: for every run it also reports max|F_y| on the adsorbate atoms, so the
header claim and the force claim can be seen to agree. Where they disagree, the force
evidence wins and the disagreement is the finding.

Deliberately NOT inferred: this counts what pw.x reduced, not what the physics wanted. A
run with 4 operations whose true minimum happens to be symmetric lost nothing. The point of
the table is the *population* -- how much of a published-style archive carries the
constraint at all -- not a verdict on any single row.

    PYTHONPATH=src python src/dft/symops_audit.py runs
    PYTHONPATH=src python src/dft/symops_audit.py runs --csv docs/figs/symops_audit.csv
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys

#: The real pw.x 7.5 line puts the COUNT FIRST, e.g.
#:      2 Sym. Ops. (no inversion) found ( 1 have fractional translation)
#: and prints "No symmetry found" (i.e. identity only) when nosym/noinv are set. Getting
#: this wrong is not a harmless parse bug: an inverted regex reports 0% of the archive as
#: constrained, which is the exact opposite of the finding, and it agrees with nothing.
SYMOPS = re.compile(r"^\s*(\d+)\s+Sym\. Ops\.", re.M)
SYMOPS_NONE = re.compile(r"^\s*No symmetry found", re.M)
NOSYM = re.compile(r"^\s*nosym\s*=\s*\.true\.", re.I | re.M)
NAT = re.compile(r"number of atoms/cell\s*=\s*(\d+)")
FORCE_BLOCK = re.compile(r"^\s*atom\s+(\d+)\s+type\s+\d+\s+force =\s+"
                         r"(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)", re.M)
#: pw.x does not echo the &CONTROL namelist, so `calculation` has to be inferred from what
#: the run actually did. "BFGS Geometry Optimization" is printed once per relax; a plain scf
#: never prints it. (Reading it back from the .in would be wrong here -- the question is
#: what the OUTPUT is evidence of, and a deck can be edited after the fact.)
RELAX = re.compile(r"BFGS Geometry Optimization|Geometry Optimization")
TOTAL_E = re.compile(r"^!\s+total energy", re.M)


def n_symops(text: str):
    """Number of symmetry operations pw.x kept, or None if the line is absent.

    "No symmetry found" means the identity alone, which is 1 operation, not zero -- pw.x
    just does not bother to print a count for the trivial group.
    """
    m = SYMOPS.search(text)
    if m:
        return int(m.group(1))
    if SYMOPS_NONE.search(text):
        return 1
    return None


def adsorbate_max_fy(text: str, n_slab: int):
    """max |F_y| over adsorbate atoms across every printed force block.

    n_slab is the count of slab atoms; anything beyond it is adsorbate. A slab-only run
    (clean surface) has no adsorbate and returns None rather than 0.0, because "there was
    nothing to constrain" and "nothing moved" are different statements.
    """
    worst = None
    for m in FORCE_BLOCK.finditer(text):
        idx = int(m.group(1))
        if idx <= n_slab:
            continue
        fy = abs(float(m.group(3)))
        worst = fy if worst is None else max(worst, fy)
    return worst


#: below this, an out-of-plane force is indistinguishable from zero against the campaign's
#: own 1e-3 Ry/au convergence threshold -- the optimiser was never pushed off the plane
FY_NOISE = 1.0e-4


def classify(nops, fy):
    """Three-way, because "no symmetry constraint" is not the same as "it left the plane".

    LOCKED      pw.x kept a mirror and symmetrised F_y to exactly zero. The relaxation was
                a constrained optimisation and could not leave the plane.
    ON_PLANE    no symmetry was enforced, but the out-of-plane force never rose above noise,
                so the optimiser had no reason to leave and did not. Numerically free,
                physically identical to LOCKED.
    EXPLORED    a real out-of-plane force existed and the optimiser acted on it.

    The distinction matters because only EXPLORED runs constitute evidence that the
    published minimum is the true one. Reporting LOCKED alone would understate the problem.
    """
    if fy is None:
        return ""
    if nops is not None and nops > 1 and fy == 0.0:
        return "LOCKED"
    if fy < FY_NOISE:
        return "ON_PLANE"
    return "EXPLORED"


def slab_atom_count(text: str, path: str):
    """Infer how many of the atoms are slab.

    The campaign's states are named by their adsorbate, so the count is derivable from the
    filename plus the total: slab + {O:1, OH:2, OOH:3}. That is more robust than trying to
    read the constraint mask, which is not echoed in the output.
    """
    m = NAT.search(text)
    if not m:
        return None, None
    nat = int(m.group(1))
    base = os.path.basename(path)
    for tag, n_ads in (("s0_OOH", 3), ("s0_OH", 2), ("s0_O", 1)):
        if base.startswith(tag):
            return nat - n_ads, n_ads
    return nat, 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="runs")
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    rows = []
    for dirpath, _dirs, files in os.walk(args.root):
        for f in sorted(files):
            if not f.endswith(".out"):
                continue
            p = os.path.join(dirpath, f)
            try:
                text = open(p, errors="ignore").read()
            except OSError:
                continue
            if "Program PWSCF" not in text:
                continue
            nops = n_symops(text)
            n_slab, n_ads = slab_atom_count(text, p)
            fy = adsorbate_max_fy(text, n_slab) if (n_slab and n_ads) else None
            # nosym lives in the DECK, not the output. Reading it matters because
            # "pw.x found no symmetry" has two very different causes: we asked for none,
            # or the structure did not have any. Only the second is an accident.
            deck = p[:-4] + ".in"
            asked = bool(NOSYM.search(open(deck, errors="ignore").read())) \
                if os.path.exists(deck) else None
            n_scf = len(TOTAL_E.findall(text))
            rows.append(dict(
                path=os.path.relpath(p, args.root).replace(os.sep, "/"),
                calculation="relax" if RELAX.search(text) else "scf",
                n_scf_blocks=n_scf,
                n_symops=nops,
                nosym_in_deck=asked,
                n_adsorbate=n_ads,
                max_fy_adsorbate=fy,
                confinement=classify(nops, fy),
            ))

    if not rows:
        print(f"no pw.x outputs under {args.root}", file=sys.stderr)
        return 1

    # ---- distribution -------------------------------------------------------------
    dist = {}
    for r in rows:
        dist[r["n_symops"]] = dist.get(r["n_symops"], 0) + 1
    print(f"{len(rows)} pw.x outputs under {args.root}/\n")
    print("symmetry operations pw.x kept:")
    for k in sorted(dist, key=lambda x: (x is None, x)):
        label = "not printed" if k is None else f"{k} operation{'s' if k != 1 else ''}"
        free = "  <- free relaxation" if k == 1 else ""
        print(f"  {label:<16} {dist[k]:4d}  ({100*dist[k]/len(rows):5.1f}%){free}")

    constrained = [r for r in rows if r["n_symops"] not in (None, 1)]
    print(f"\nconstrained: {len(constrained)}/{len(rows)} "
          f"({100*len(constrained)/len(rows):.1f}%)")

    # ---- the force cross-check ----------------------------------------------------
    with_ads = [r for r in rows if r["max_fy_adsorbate"] is not None]
    exact_zero = [r for r in with_ads if r["max_fy_adsorbate"] == 0.0]
    print(f"\nadsorbate runs with a printed force block: {len(with_ads)}")
    print(f"  max|F_y| on the adsorbate EXACTLY 0.0000000000 : {len(exact_zero)}"
          f"  ({100*len(exact_zero)/len(with_ads):.1f}%)" if with_ads else "")

    # A run that kept symmetry ops but shows a nonzero F_y, or vice versa, is the
    # interesting case -- the header and the forces disagree and the forces decide.
    # Runs with no printed count are excluded: absence of the line is not a disagreement.
    disagree = [r for r in with_ads
                if r["n_symops"] is not None
                and (r["n_symops"] == 1) != (r["max_fy_adsorbate"] != 0.0)]
    if disagree:
        print(f"\n  header/force DISAGREEMENT on {len(disagree)} run(s):")
        for r in disagree[:20]:
            print(f"    {r['path']:<52} ops={r['n_symops']} max|F_y|={r['max_fy_adsorbate']}")
    else:
        print("  header and force evidence agree on every adsorbate run")

    # ---- the table the claim actually rests on ------------------------------------
    prod = [r for r in rows
            if r["calculation"] == "relax" and r["n_adsorbate"]
            and not r["path"].startswith("probe")]
    if prod:
        cls = {}
        for r in prod:
            cls[r["confinement"]] = cls.get(r["confinement"], 0) + 1
        n = len(prod)
        print(f"\nPRODUCTION adsorbate relaxations (n = {n}) -- the population the claim is about:")
        for k in ("LOCKED", "ON_PLANE", "EXPLORED"):
            v = cls.get(k, 0)
            print(f"  {k:<9} {v:3d}  ({100*v/n:5.1f}%)")
        conf = cls.get("LOCKED", 0) + cls.get("ON_PLANE", 0)
        print(f"  {'-'*9}")
        print(f"  confined to the mirror plane, by either route: {conf}/{n} "
              f"({100*conf/n:.1f}%)")
        print("\n  per metal:")
        by_metal = {}
        for r in prod:
            metal = r["path"].split("/")[0].split("_")[0]
            by_metal.setdefault(metal, []).append(r)
        for metal in sorted(by_metal):
            tags = " ".join(f"{os.path.basename(r['path'])[3:-4]}:{r['confinement']}"
                            for r in sorted(by_metal[metal], key=lambda r: r["path"]))
            print(f"    {metal:<3} {tags}")

    if args.csv:
        os.makedirs(os.path.dirname(args.csv) or ".", exist_ok=True)
        with open(args.csv, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"\nwrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
