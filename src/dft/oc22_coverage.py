"""
OC22 coverage audit for the STS electrocatalyst project.

Question: does OC22 contain OER intermediates (*O, *OH, *OOH) on pristine rutile
MO2(110) for M in {Cr, Mn, Fe, Co, Ni, Cu, Ru, Ir} -- i.e. can it serve as an
external validation set for docs/35-37's DFT tier?

Answer produced by this script: no. Run it to reproduce the numbers.

Input (9.8 MB, CC-BY 4.0):
  https://dl.fbaipublicfiles.com/opencatalystproject/data/oc22/oc22_metadata.pkl

Result (docs/38 s3, reproduced 2026-08-06): 4,318 rutile systems, but only 83 at (110),
exactly 1 of which carries *OOH; 19 rutile(110) systems touch our metals, 0 with *OOH;
neither canonical rutile bulk (mp-825 RuO2, mp-2723 IrO2) is sampled at (110) at all.
This corrects the too-strong reading of docs/29 s2.

The audit's one lead is CLOSED NEGATIVE (2026-08-06, docs/38 s3b). mp-1095353 (Ir4O8)
has 15 systems at (110) including 3 *OOH, 3 *O and 1 *OH -- a complete OER triad -- but
it is not rutile. Via MP OPTIMADE (no API key) + spglib:

    mp-1095353  Pa-3 (205)      cubic  a,b,c = 4.904, 4.902, 4.905 A   Ir4O8, pyrite-type
    mp-2723     P4_2/mnm (136)  tetrag a,b,c = 3.177, 4.505, 4.505 A   Ir2O4, RUTILE

Identical at symprec 0.01 and 0.1, so not a tolerance artifact. A Pa-3 (110) cut has none
of the bridging-O-row / 5-fold-cus-metal motif rutile(110) has, so those adsorption
energies are not comparable and scoring against them would be a FALSE validation.

Conclusion: OC22 contains no usable external validation for rutile MO2(110) OER on any of
our metals. Reproduce the structure check with:

    curl -s https://optimade.materialsproject.org/v1/structures/mp-1095353

Usage:
  curl -L -o oc22_metadata.pkl \
    https://dl.fbaipublicfiles.com/opencatalystproject/data/oc22/oc22_metadata.pkl
  python src/dft/oc22_coverage.py oc22_metadata.pkl
"""

import collections
import pickle
import re
import sys

TARGET_METALS = {"Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Ru", "Ir"}
# OC22 adsorbate strings; HO2 is *OOH, HO is *OH.
OER_ADSORBATES = {"O", "OH", "HO2"}
# Canonical rutile bulks in Materials Project (lattice-verified via MP OPTIMADE).
CANONICAL_RUTILE = {"mp-825": "RuO2", "mp-2723": "IrO2"}


def parse_formula(symbols):
    """'Cr4O8' -> [('Cr', 4), ('O', 8)]"""
    return [
        (el, int(n) if n else 1)
        for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", symbols)
        if el
    ]


def main(path):
    meta = pickle.load(open(path, "rb"))
    print(f"OC22 systems in metadata: {len(meta)}")
    print(f"unique bulk_ids:          {len({m['bulk_id'] for m in meta.values()})}\n")

    # -- 1. The rutile subset. OC22 names its deliberately-built rutile
    #       prototypes with a '-rutile' bulk_id suffix.
    rutile = {s: m for s, m in meta.items() if "rutile" in str(m["bulk_id"]).lower()}
    print(f"[1] systems with 'rutile' in bulk_id: {len(rutile)}"
          "   (paper Table 1 reports 4,318)")
    print(f"    unique rutile bulks:             "
          f"{len({m['bulk_id'] for m in rutile.values()})}")
    print(f"    distinct Miller indices spanned: "
          f"{len({m['miller_index'] for m in rutile.values()})}\n")

    # -- 2. How many of those are the (110) facet this project models?
    r110 = [m for m in rutile.values() if m["miller_index"] == (1, 1, 0)]
    ads110 = collections.Counter(m.get("ads_symbols", "CLEAN") for m in r110)
    print(f"[2] rutile systems at (110), ANY metal: {len(r110)}")
    print(f"    adsorbate breakdown: {dict(ads110)}")
    print(f"    *OOH (HO2) on any rutile(110):    {ads110['HO2']}\n")

    # -- 3. Restrict to this project's metals.
    hits = collections.defaultdict(list)
    for sid, m in rutile.items():
        if m["miller_index"] != (1, 1, 0):
            continue
        els = set(re.findall(r"[A-Z][a-z]?", str(m["bulk_id"]).split("-")[0]))
        if els & TARGET_METALS:
            hits[m["bulk_id"]].append((m.get("ads_symbols", "CLEAN"), m.get("nads")))
    n_hits = sum(len(v) for v in hits.values())
    n_oer = sum(1 for v in hits.values() for a, _ in v if a in OER_ADSORBATES)
    n_ooh = sum(1 for v in hits.values() for a, _ in v if a == "HO2")
    print(f"[3] rutile(110) systems containing a target metal: {n_hits}")
    print(f"    of which carry an OER intermediate:            {n_oer}")
    print(f"    of which carry *OOH:                           {n_ooh}")
    for b, v in sorted(hits.items()):
        print(f"      {b:20s} {sorted(v)}")
    print()

    # -- 4. Pure MO2(110) for the target metals -- the actual surface modelled.
    pure = collections.defaultdict(list)
    for sid, m in meta.items():
        es = parse_formula(m["bulk_symbols"])
        if len(es) != 2 or es[1][0] != "O":
            continue
        metal, n_m = es[0]
        if metal not in TARGET_METALS or es[1][1] != 2 * n_m:
            continue
        if m["miller_index"] == (1, 1, 0):
            pure[metal].append((m["bulk_id"], m.get("ads_symbols", "CLEAN")))
    print("[4] PURE MO2(110) systems per target metal:")
    for metal in sorted(TARGET_METALS):
        print(f"      {metal}: {len(pure[metal])}  {sorted(pure[metal])}")
    print()

    # -- 5. Are the canonical rutile bulks sampled at (110) at all?
    print("[5] canonical rutile bulks -- facets actually sampled:")
    for bulk_id, name in CANONICAL_RUTILE.items():
        facets = collections.Counter(
            m["miller_index"] for m in meta.values() if m["bulk_id"] == bulk_id
        )
        at110 = facets.get((1, 1, 0), 0)
        print(f"      {bulk_id} ({name}): {dict(facets)}")
        print(f"        -> systems at (110): {at110}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "oc22_metadata.pkl")
