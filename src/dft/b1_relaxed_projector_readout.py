#!/usr/bin/env python3
"""B1 readout: the relaxed Cr projector pair in the adopted 2x1 cell at U = 7.15 eV.

WRITTEN BEFORE ANY B1 OUTPUT EXISTS (registration: docs/research/b1-relaxed-projector-2026-10-16.md, committed
before the first deck was built). Nothing here may be changed after outputs land except to fix a bug, and any such
fix is recorded with its reason.

WHAT IS SCORED.
  eta per leg from the eight TERMINAL fresh-start SCFs (stage 2, `<stem>__u715_<leg>_scf`), through the same gas
  references, hea_oer.referencing, ZPE/TS constants and oer_overpotential as pproj_cell_readout.py.
  d_eta_relaxed = eta(ortho) - eta(atomic).  Bands inherited from A13.3: SURVIVES > 0.10 V, COLLAPSES < 0.03 V,
  INTERMEDIATE between, never rounded.  If the legs differ in limiting step, d_eta is split into electronic and
  ZPE/TS-constant parts (A13.6) and the split travels with the number.
WHAT IS REPORTED, NOT SCORED.
  - GATE-1 (docs/43:310-313): terminal SCF >= 5 meV below its relaxation's final energy -> RE-RELAX flag.
  - BRANCH MISMATCH: |total magnetization(atomic) - (ortho)| >= 0.5 muB for a state.
  - Adsorbate chemistry at each endpoint (hea_oer.site_integrity.DEFAULT_THRESHOLDS): desorbed (nearest Cr-O >= 3.00
    A), H not within 1.15 A of an adsorbate O, or *OOH O-O > 1.60 A is a CHEMICAL RESULT and that leg gives no eta.
  - Off-plane outcome for *O and *OH: the adsorbate's |dy| from the y = 1.56305954 A mirror at the endpoint
    (returned to the plane if every adsorbate atom has |dy| < 0.05 A), and the energy of the relaxed terminal SCF
    relative to the banked mirror single point at the same U and projector.
  - The fixed-geometry pair (docs/figs/pproj_cell_readout.json) beside the relaxed pair.
A missing, rejected or numerically failed leg makes the arm UNRESOLVED: all four states under both projectors are
scored, or none.

Usage:
  PYTHONPATH=src python src/dft/b1_relaxed_projector_readout.py [--json docs/figs/b1_relaxed_projector_readout.json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RUNS = os.path.join(ROOT, "runs", "b1_relaxed_projector_2026-10-16")

STEMS = {"slab": "ref__2x1v", "s0_O": "s0_O__2x1v_mir", "s0_OH": "s0_OH__2x1v_mir",
         "s0_OOH": "s0_OOH__2x1v_escape"}
LEGS = ("atomic", "ortho")
BANKED = {"atomic": ("runs/a0/cell", "{stem}__u715.out"), "ortho": ("runs/a0/pproj_cell", "{stem}__u715_ortho.out")}
SLAB_NAT = 36
MIRROR_Y = 1.56305954
ON_PLANE_A = 0.05
GATE1_MEV = 5.0
BRANCH_MUB = 0.5
SURVIVES_V, COLLAPSES_V = 0.10, 0.03
FIXED = dict(eta_atomic=0.9239810476816457, eta_ortho=1.0964974268814514, d_eta=0.17251637919980567, pls=1)
# research_batch_seeded.FAIL, the markers that make the runner reject a run (benign IEEE_DENORMAL/UNDERFLOW excluded)
SEVERE = re.compile(r"convergence NOT achieved|Maximum (?:CPU|wall) time exceeded|Error in routine|MPI_ABORT|"
                    r"Segmentation fault|Floating point exception|IEEE_INVALID_FLAG|IEEE_OVERFLOW_FLAG|"
                    r"IEEE_DIVIDE_BY_ZERO", re.I)


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def relax_name(stem, leg):
    return f"{stem}__u715_{leg}_relax"


def scf_name(stem, leg):
    return f"{stem}__u715_{leg}_scf"


def totmag(path):
    val = None
    with open(path, errors="replace") as fh:
        for line in fh:
            m = re.search(r"total magnetization\s*=\s*([-\d.]+)", line)
            if m:
                val = float(m.group(1))
    return val


def receipt_complete(base):
    path = base + ".qc.json"
    if not os.path.exists(path):
        return False, "no runner receipt"
    rec = json.load(open(path, encoding="utf-8"))
    return rec.get("status") == "COMPLETE", rec.get("reason") or rec.get("status")


def deck_cell_positions(path):
    text = open(path, encoding="utf-8").read()
    cell = re.search(r"(?ms)^CELL_PARAMETERS angstrom\s*\n(.*?)\n(?=\S)", text).group(1).split("\n")
    a, b = float(cell[0].split()[0]), float(cell[1].split()[1])
    rows = re.search(r"(?ms)^ATOMIC_POSITIONS angstrom\s*\n(.*?)^K_POINTS", text).group(1).splitlines()
    atoms = [(r.split()[0], tuple(float(x) for x in r.split()[1:4])) for r in rows if r.split()]
    return a, b, atoms


def dist(p, q, a, b):
    dx, dy, dz = p[0] - q[0], p[1] - q[1], p[2] - q[2]
    dx -= a * round(dx / a)
    dy -= b * round(dy / b)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def chemistry(state, deck, thresholds):
    """Endpoint class from the terminal SCF deck, whose positions are the relaxation's final coordinates."""
    a, b, atoms = deck_cell_positions(deck)
    if state == "slab":
        return dict(intact=True)
    slab, ads = atoms[:SLAB_NAT], atoms[SLAB_NAT:]
    metals = [p for s, p in slab if s == "Cr"]
    slab_o = [p for s, p in slab if s == "O"]
    ads_o = [p for s, p in ads if s == "O"]
    h = [p for s, p in ads if s == "H"]
    m_o = min(dist(o, m, a, b) for o in ads_o for m in metals)
    out = dict(m_o_A=m_o, desorbed=m_o >= thresholds.desorbed_min_A)
    if h:
        to_ads = min(dist(h[0], o, a, b) for o in ads_o)
        to_slab = min(dist(h[0], o, a, b) for o in slab_o)
        # registered: H counts as bonded within 1.15 A of an adsorbate O; the slab distance is a diagnostic only
        out.update(h_to_adsorbate_O_A=to_ads, h_to_slab_O_A=to_slab,
                   h_on_adsorbate=to_ads <= thresholds.h_bond_max_A)
    if state == "s0_OOH":
        out["o_o_A"] = dist(ads_o[0], ads_o[1], a, b)
        out["o_o_cleaved"] = out["o_o_A"] > thresholds.ooh_like_max_A
    out["intact"] = (not out["desorbed"] and out.get("h_on_adsorbate", True) and not out.get("o_o_cleaved", False))
    if state in ("s0_O", "s0_OH"):
        dys = [abs(p[1] - MIRROR_Y) for _, p in ads]
        out["adsorbate_abs_dy_A"] = dys
        out["returned_to_plane"] = max(dys) < ON_PLANE_A
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from hea_oer.referencing import delta_G, ZPE_TS_CORRECTION, reference_energy
    from hea_oer.descriptors import oer_overpotential
    from hea_oer.site_integrity import DEFAULT_THRESHOLDS
    qc = _load("qe_qc")
    zpe = _load("zpe_decomposition")

    fixed = json.load(open(os.path.join(ROOT, "docs", "figs", "pproj_cell_readout.json"), encoding="utf-8"))
    assert abs(fixed["legs"]["atomic"]["eta"] - FIXED["eta_atomic"]) < 1e-9
    assert abs(fixed["legs"]["ortho"]["eta"] - FIXED["eta_ortho"]) < 1e-9

    gas = {}
    for g in ("H2O", "H2"):
        e = qc.trusted_energy_ev(os.path.join(ROOT, "runs", "Cr_slab", f"{g}.out"), strict=True)
        if e is None:
            sys.exit(f"REFUSING: gas reference {g} missing or failed QC")
        gas[g] = e

    E, mag, chem, status, unresolved = {}, {}, {}, {}, []
    for st, stem in STEMS.items():
        for leg in LEGS:
            rbase = os.path.join(RUNS, relax_name(stem, leg))
            sbase = os.path.join(RUNS, scf_name(stem, leg))
            rec = {}
            ok_r, why_r = receipt_complete(rbase)
            ok_s, why_s = receipt_complete(sbase) if ok_r else (False, "relaxation not complete")
            rec.update(relax=why_r if not ok_r else "COMPLETE", scf=why_s if not ok_s else "COMPLETE")
            if not (ok_r and ok_s):
                unresolved.append(f"{st}/{leg}: relax {rec['relax']}; scf {rec['scf']}")
                status[(st, leg)] = rec
                continue
            e = qc.trusted_energy_ev(sbase + ".out", sbase + ".in", strict=True)
            if e is None:
                unresolved.append(f"{st}/{leg}: terminal SCF failed QC")
                status[(st, leg)] = rec
                continue
            relax_text = open(rbase + ".out", encoding="utf-8", errors="replace").read()
            last = re.findall(r"^!\s+total energy\s*=\s*([-\d.]+)\s+Ry", relax_text, re.M)[-1]
            rec["relax_final_eV"] = float(last) * qc.RY_EV
            rec["scf_eV"] = e
            rec["gate1_meV"] = (e - rec["relax_final_eV"]) * 1000.0
            rec["gate1_rerelax"] = rec["gate1_meV"] <= -GATE1_MEV
            banked_dir, pattern = BANKED[leg]
            banked_path = os.path.join(ROOT, banked_dir, pattern.format(stem=stem))
            banked = qc.trusted_energy_ev(banked_path, strict=True)
            # the banked single point must also pass the runner's numerical-failure markers (B1's own policy)
            flags = sorted(set(SEVERE.findall(open(banked_path, encoding="utf-8", errors="replace").read())))
            rec["banked_reference_flags"] = flags
            rec["relaxation_energy_meV"] = (e - banked) * 1000.0 if banked is not None and not flags else None
            rec["chemistry"] = chemistry(st, sbase + ".in", DEFAULT_THRESHOLDS)
            E[(st, leg)], mag[(st, leg)] = e, totmag(sbase + ".out")
            chem[(st, leg)] = rec["chemistry"]
            status[(st, leg)] = rec

    for (st, leg), rec in status.items():
        rec["total_magnetization"] = mag.get((st, leg))
    mismatch = [st for st in STEMS if (st, "atomic") in mag and (st, "ortho") in mag
                and None not in (mag[(st, "atomic")], mag[(st, "ortho")])
                and abs(mag[(st, "atomic")] - mag[(st, "ortho")]) >= BRANCH_MUB]

    def payload(extra):
        out = dict(arm="B1", registration="docs/research/b1-relaxed-projector-2026-10-16.md", U=7.15, cell="2x1v",
                   fixed_geometry=FIXED, branch_mismatch=mismatch,
                   states={f"{st}/{leg}": status.get((st, leg)) for st in STEMS for leg in LEGS})
        out.update(extra)
        return out

    def fmt(v, spec):
        return format(v, spec) if v is not None else "n/a"

    print("=" * 88)
    print("B1 -- relaxed Cr projector pair, U = 7.15 eV, adopted 2x1v cell (registered 2026-10-16)")
    print("=" * 88)
    # every available diagnostic is reported, whether or not the arm can be scored
    print(f"\n{'state':8s} {'leg':7s} {'E_scf (eV)':>15s} {'gate1 meV':>10s} {'relax meV':>10s} {'mag':>7s}  chemistry")
    for st in STEMS:
        for leg in LEGS:
            r = status[(st, leg)]
            if "scf_eV" not in r:
                print(f"{st:8s} {leg:7s} {'--':>15s}  relax {r.get('relax')}; scf {r.get('scf')}")
                continue
            c = r["chemistry"]
            extra = "" if st == "slab" else (
                f"M-O {c['m_o_A']:.3f}"
                + (f", H-O(ads) {c['h_to_adsorbate_O_A']:.3f}" if "h_to_adsorbate_O_A" in c else "")
                + (f", |dy| max {max(c['adsorbate_abs_dy_A']):.3f}"
                   f" ({'on plane' if c['returned_to_plane'] else 'off plane'})" if "adsorbate_abs_dy_A" in c else "")
                + (f", O-O {c['o_o_A']:.3f}" if "o_o_A" in c else "")
                + ("" if c.get("intact", True) else "  NOT INTACT"))
            flag = f"  [banked reference flagged: {r['banked_reference_flags']}]" if r["banked_reference_flags"] else ""
            print(f"{st:8s} {leg:7s} {r['scf_eV']:15.4f} {r['gate1_meV']:10.2f} "
                  f"{fmt(r['relaxation_energy_meV'], '10.1f'):>10s} {mag[(st, leg)]!s:>7}  {extra}{flag}")
    if mismatch:
        print(f"\n  BRANCH MISMATCH (reported, not averaged): {mismatch}")
    print(f"\n  fixed geometry (A13): atomic {FIXED['eta_atomic']:.7f} V, ortho {FIXED['eta_ortho']:.7f} V, "
          f"d-eta {FIXED['d_eta']:+.7f} V, both pls {FIXED['pls']}")

    blocked = list(unresolved)
    chemical = [f"{st}/{leg}" for (st, leg), c in chem.items() if not c.get("intact", True)]
    rerelax = [f"{st}/{leg}" for (st, leg), r in status.items() if r.get("gate1_rerelax")]
    for k in chemical:
        blocked.append(f"{k}: CHEMICAL RESULT (adsorbate not intact) -- no eta for this leg")
    for k in rerelax:
        blocked.append(f"{k}: GATE-1 terminal SCF >= {GATE1_MEV:g} meV below the relaxation -- re-relax")
    if blocked:
        print("\nARM UNRESOLVED -- eta is not scored (all four states under both projectors, or none):")
        for x in blocked:
            print("  " + x)
        if args.json:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump(payload(dict(verdict="UNRESOLVED", reasons=blocked)), fh, indent=2)
        sys.exit(2)

    legs = {}
    for leg in LEGS:
        dG = {sp: delta_G(E[("slab", leg)], E[(f"s0_{sp}", leg)], sp, gas["H2O"], gas["H2"])
              for sp in ("OH", "O", "OOH")}
        r = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
        dEl = {sp: E[(f"s0_{sp}", leg)] - E[("slab", leg)] - reference_energy(sp, gas["H2O"], gas["H2"])
               for sp in ("OH", "O", "OOH")}
        rz = oer_overpotential(dEl["OH"], dEl["O"], dEl["OOH"])
        legs[leg] = dict(dG=dG, eta=r.overpotential, pls=r.potential_limiting_step,
                         steps=[r.dG1, r.dG2, r.dG3, r.dG4], steps_electronic=[rz.dG1, rz.dG2, rz.dG3, rz.dG4])
    d_eta = legs["ortho"]["eta"] - legs["atomic"]["eta"]
    band = "SURVIVES" if abs(d_eta) > SURVIVES_V else ("COLLAPSES" if abs(d_eta) < COLLAPSES_V else "INTERMEDIATE")
    pls_differs = legs["atomic"]["pls"] != legs["ortho"]["pls"]
    decomp = None
    if pls_differs:
        c = zpe.step_constants(dict(ZPE_TS_CORRECTION))
        pa, po = legs["atomic"]["pls"], legs["ortho"]["pls"]
        const = c[po - 1] - c[pa - 1]
        elec = legs["ortho"]["steps_electronic"][po - 1] - legs["atomic"]["steps_electronic"][pa - 1]
        decomp = dict(electronic_eV=elec, constants_eV=const, closure=(elec + const) - d_eta)

    print(f"\n{'leg':8s} {'pls':>4s} {'eta (V)':>10s} | steps (eV)")
    for leg in LEGS:
        L = legs[leg]
        print(f"{leg:8s} {L['pls']:4d} {L['eta']:10.7f} | " + " ".join(f"{s:9.5f}" for s in L["steps"]))
    print(f"\n  relaxed d-eta = {d_eta:+.7f} V  -> {band}   (fixed geometry: {FIXED['d_eta']:+.7f} V, both pls 1)")
    print(f"  pls {legs['atomic']['pls']} -> {legs['ortho']['pls']} ({'DIFFERS' if pls_differs else 'SAME'})")
    if decomp:
        print(f"  split: electronic {decomp['electronic_eV']:+.4f} eV + constants {decomp['constants_eV']:+.4f} eV")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload(dict(verdict=band, d_eta_relaxed_V=d_eta, pls_differs=pls_differs,
                                   zpe_decomposition=decomp,
                                   legs={k: dict(eta=v["eta"], pls=v["pls"], steps=v["steps"]) for k, v in
                                         legs.items()})), fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
