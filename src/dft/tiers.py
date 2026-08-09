"""Pinned, immutable tiers of record — so a figure cannot silently change under a result.

Why this module exists
----------------------
`eta_bounded.reference_tier()` recomputes the tier from whatever is on disk. That was
right while there was only ever one answer. On 2026-08-09 there stopped being one: the
three basin restarts (docs/41 §6f) moved Cr, Co and Ni, and the tier's *ordering* changed
from Cr<Co<Ir<Ru<Mn<Ni<Fe to Cr<Ir<Co<Ru<Mn<Ni<Fe.

Every figure, every Spearman ρ, every MAE and every claim in the report is computed
against *a* tier. If the function that supplies it reads the run directory, then adding a
run directory rewrites the past — a figure regenerated in October would quietly disagree
with the number quoted beside it in August, with nothing in either artifact recording that
anything moved. That is the failure this module exists to make impossible.

The contract
------------
1. A tier version is a JSON file under ``data/tiers/`` and is **write-once**. ``freeze()``
   refuses to overwrite one that exists.
2. Anything that scores, plots or reports must name its version. ``load()`` has no default
   and ``reference_tier()`` now takes a required ``version`` argument.
3. ``"live"`` is a legal version meaning "recompute from disk". It is spelled out at every
   call site precisely so that using it is a visible choice rather than a default.
4. ``verify()`` re-derives a pinned tier from the run directory and reports every metal that
   moved. ``tier_v1`` must keep reproducing exactly, because the basin restarts were written
   to *new* directories (``runs/probe/*_basin``) rather than over the originals. If it ever
   stops reproducing, something overwrote history and that is a hard error, not a diff.

    PYTHONPATH=src python src/dft/tiers.py list
    PYTHONPATH=src python src/dft/tiers.py show tier_v2
    PYTHONPATH=src python src/dft/tiers.py verify tier_v1
"""
from __future__ import annotations

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", ".."))
PINNED_DIR = os.path.join(_REPO, "data", "tiers")

#: the sentinel that means "recompute from the run directory, I know that is what I want"
LIVE = "live"

#: energies in eV. Value = (state key, drift applied to that state's dG), signed so that a
#: negative number means the corrected state is LOWER than the production relaxation found.
#: Measured in docs/41 §6f from the basin re-relaxations; each reproduced its audit SCF at
#: ionic step 1 to better than 0.02 meV, which is what licenses treating them as corrections
#: to the production numbers rather than as separate calculations.
BASIN_DRIFT_V2 = {
    ("Cr", "dG_OOH"): -0.17858,
    ("Co", "dG_OH"): -0.40651,
    ("Ni", "dG_OH"): -0.17585,
}

G_TOTAL = 4.92
U_EQ = 1.23


def _versions_on_disk() -> list:
    if not os.path.isdir(PINNED_DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(PINNED_DIR) if f.endswith(".json"))


def path_for(version: str) -> str:
    return os.path.join(PINNED_DIR, f"{version}.json")


def load(version: str) -> dict:
    """A pinned tier. No default, on purpose — the caller must say which one."""
    if version == LIVE:
        raise SystemExit("tiers.load(): 'live' is not a pinned version; call live() explicitly")
    p = path_for(version)
    if not os.path.exists(p):
        raise SystemExit(f"tiers.load(): no pinned tier {version!r}; have {_versions_on_disk()}")
    with open(p, encoding="utf-8") as fh:
        doc = json.load(fh)
    return doc["tier"]


def meta(version: str) -> dict:
    with open(path_for(version), encoding="utf-8") as fh:
        doc = json.load(fh)
    return {k: v for k, v in doc.items() if k != "tier"}


def live(root: str = "runs") -> dict:
    """Recompute from the run directory. Equivalent to the pre-2026-08-09 behaviour."""
    from dft.eta_bounded import reference_tier
    return reference_tier(root, version=LIVE)


def freeze(version: str, tier: dict, provenance: str, derived_from: str | None = None) -> str:
    """Write a tier once. Refuses to overwrite, because that is the whole point."""
    os.makedirs(PINNED_DIR, exist_ok=True)
    p = path_for(version)
    if os.path.exists(p):
        raise SystemExit(f"refusing to overwrite pinned tier {version!r} at {p}")
    if not provenance.strip():
        raise SystemExit("refusing to freeze a tier with no provenance string")
    doc = dict(version=version, provenance=provenance, derived_from=derived_from,
               ordering=[m for m, _ in sorted(tier.items(), key=lambda kv: kv[1]["eta"])],
               tier=tier)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return p


def apply_drift(tier: dict, drift: dict) -> dict:
    """Re-derive eta/pls after shifting individual dG values.

    Kept here rather than in the caller so that `tier_v2` is reproducible from `tier_v1`
    plus a table of measured numbers, instead of being a hand-typed list of etas.
    """
    out = {}
    for m, v in tier.items():
        dOH = v["dG_OH"] + drift.get((m, "dG_OH"), 0.0)
        dO = v["dG_O"] + drift.get((m, "dG_O"), 0.0)
        dOOH = v["dG_OOH"]
        rec = dict(v)
        rec["dG_OH"], rec["dG_O"] = dOH, dO
        if dOOH is not None:
            dOOH += drift.get((m, "dG_OOH"), 0.0)
            rungs = [dOH, dO - dOH, dOOH - dO, G_TOTAL - dOOH]
            rec["dG_OOH"] = dOOH
            rec["eta"] = max(rungs) - U_EQ
            rec["pls"] = rungs.index(max(rungs)) + 1
        else:
            # bounded route: eta rides on max(dG1, dG2) and the admissible dG_OOH window
            # has to be recomputed, because it is defined against that same maximum.
            m12 = max(dOH, dO - dOH)
            rec["dG1"], rec["dG2"] = dOH, dO - dOH
            rec["dG3_plus_dG4"] = G_TOTAL - dO
            rec["max_12"] = m12
            rec["eta"] = m12 - U_EQ
            rec["pls"] = 1 if dOH >= dO - dOH else 2
            rec["lo"] = G_TOTAL - m12
            rec["hi"] = m12 + dO
            rec["margin_lo"] = None
            rec["margin_hi"] = None
            ub = v.get("upper_bound_dG_OOH")
            rec["hi_closed"] = bool(ub is not None and ub < rec["hi"])
        out[m] = rec
    return out


def scaling_floor(tier: dict) -> dict:
    """c_M, the exact floor eta >= c_M/2 - 1.23, and the excess above it.

    Only defined where a real dG_OOH exists; a bounded metal has no measured c_M and gets
    None rather than a number derived from its bound, which would be a floor on a floor.
    """
    out = {}
    for m, v in tier.items():
        if v.get("dG_OOH") is None:
            out[m] = dict(c_M=None, floor=None, excess=None)
            continue
        c = v["dG_OOH"] - v["dG_OH"]
        fl = c / 2.0 - U_EQ
        out[m] = dict(c_M=c, floor=fl, excess=v["eta"] - fl)
    return out


def verify(version: str, root: str = "runs", tol: float = 1e-6) -> dict:
    """Re-derive a pinned tier from disk and report every metal that moved."""
    pinned = load(version)
    now = live(root)
    if version == "tier_v2":
        now = apply_drift(now, BASIN_DRIFT_V2)
    moved = {}
    for m in sorted(set(pinned) | set(now)):
        a = pinned.get(m, {}).get("eta")
        b = now.get(m, {}).get("eta")
        if a is None or b is None or abs(a - b) > tol:
            moved[m] = dict(pinned=a, recomputed=b)
    return moved


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "list":
        for v in _versions_on_disk():
            md = meta(v)
            print(f"{v:10s} {' < '.join(md['ordering'])}")
            print(f"{'':10s} {md['provenance']}")
        return 0
    if cmd == "show":
        t = load(sys.argv[2])
        fl = scaling_floor(t)
        print(f"{'M':3s} {'eta':>7s} {'pls':>4s} {'c_M':>7s} {'floor':>7s} {'excess':>7s} source")
        for m, v in sorted(t.items(), key=lambda kv: kv[1]["eta"]):
            f = fl[m]
            fmt = lambda x: f"{x:7.3f}" if x is not None else "      -"  # noqa: E731
            print(f"{m:3s} {v['eta']:7.3f} {v['pls']:>4d} {fmt(f['c_M'])} {fmt(f['floor'])} "
                  f"{fmt(f['excess'])} {v.get('source', '')}")
        return 0
    if cmd == "verify":
        moved = verify(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "runs")
        if not moved:
            print(f"{sys.argv[2]}: reproduces exactly from disk")
            return 0
        print(f"{sys.argv[2]}: DOES NOT REPRODUCE -- history was overwritten")
        for m, d in moved.items():
            print(f"  {m}: pinned {d['pinned']} recomputed {d['recomputed']}")
        return 1
    print(f"unknown command {cmd!r}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
