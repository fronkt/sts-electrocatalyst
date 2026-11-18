#!/usr/bin/env python3
"""Readout for amendment 23's two follow-up checks of V1 (docs/research/film-dft-pilot-2026-11-14.md).

A  NiOOH configuration single points at U = 0 (A23CK__RUN): each counts, if converged, as the pattern
   it landed in (amendment 11); Ni0_OH and Ni0_O get the lowest of their relaxed energy and those
   points; the lowest-readout eta at Ni0 and V1 are recomputed, with every other energy as in the base
   readout. V1 stays a pass only if it still holds in the lowest readout (the as-relaxed readout cannot
   change); otherwise it is configuration-sensitive under rule 4.
B  PBE+U single points at the U = 0 geometries (A23U__RUN): per state, QC = converged SCF and every Ni
   low-spin (|m| < 1.6 muB, amendment 8); the sign pattern and Fe moment are reported. CHE with the
   registered corrections and the same gas references. A site with a failed slab is reported through
   its slab-independent steps (2, 3) as a lower bound on eta (amendment 4). The result is the ordering
   at PBE+U with geometry and starting configuration from U = 0; it does not change V1.

  python src/dft/film_followup_readout.py [--runs DIR] [--base readout_u0.json] [--out followup_a23.json]
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
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "src"))

from hea_oer.descriptors import oer_overpotential, oer_steps  # noqa: E402
from hea_oer.referencing import delta_G  # noqa: E402

_spec = importlib.util.spec_from_file_location("film_pilot_readout", os.path.join(HERE, "film_pilot_readout.py"))
fpr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fpr)

EQ = 1.23
NI_HIGH_SPIN = 1.6  # muB; amendment 8: low-spin Ni 1.24-1.42, high-spin ~1.9 at PBE+U
SITE_ATOM = 6       # pw.x 1-based: the site metal (Ni0 in NiOOH, Fe in Ni(Fe)OOH)
A_STATES = {"NiOOH__Ni0_OH": ("u0__NiOOH__Ni0_OH", ("C1", "C3", "C4")),
            "NiOOH__Ni0_O": ("u0__NiOOH__Ni0_O_r2", ("C1", "C2", "C3", "C4", "C5"))}
B_STATES = ("NiOOH__slab", "NiOOH__Ni0_OH", "NiOOH__Ni0_O", "NiOOH__Ni0_OOH",
            "NiFeOOH__slab", "NiFeOOH__Fe0_OH", "NiFeOOH__Fe0_O", "NiFeOOH__Fe0_OOH")
SITES = {"NiOOH__Ni0": ("NiOOH", "Ni0"), "NiFeOOH__Fe0": ("NiFeOOH", "Fe0")}


def symbols(inp):
    t = open(inp).read()
    nat = int(re.search(r"nat = (\d+)", t).group(1))
    rows = t.split("ATOMIC_POSITIONS angstrom\n", 1)[1].split("\n")[:nat]
    return [re.sub(r"\d+$", "", r.split()[0]) for r in rows]


def describe(sym, mom):
    """Pattern on the 0.25 muB cutoff, relative to atom 1: the site's sign and the antiparallel metals."""
    p = dict(fpr.pattern(sym, mom))
    neg = sorted(i for i, s in p.items() if s == "-" and i != SITE_ATOM)
    return dict(site=p.get(SITE_ATOM, "0"), antiparallel=neg)


def point(runs, name):
    """Energy (eV; None unless converged and trusted), moments and pattern of a single point."""
    out, inp = (os.path.join(runs, name, name + s) for s in (".out", ".in"))
    if not os.path.exists(out):
        return dict(run=name, status="missing", energy_ev=None)
    e = fpr.qe_qc.trusted_energy_ev(out, inp)
    tot, mom = fpr.magnetics(out)
    sym = symbols(inp)
    it = re.findall(r"convergence has been achieved in\s+(\d+) iterations", open(out, errors="replace").read())
    rec = dict(run=name, status="converged" if e is not None else "not converged", energy_ev=e,
               iterations=int(it[-1]) if it else None, mag_total=tot)
    if mom and len(mom) == len(sym):
        rec.update(moments=mom, pattern=describe(sym, mom))
        ni = [abs(m) for s, m in zip(sym, mom) if s == "Ni"]
        rec["ni_max_abs"] = round(max(ni), 3)
        if "Fe" in sym:
            rec["fe_moment"] = mom[sym.index("Fe")]
    return rec


def site_eta(E, film, tag):
    """dG, steps and eta at one site from state energies E (eV); a missing slab gives a lower bound."""
    ads = {sp: E.get(f"{film}__{tag}_{sp}") for sp in ("OH", "O", "OOH")}
    if None in ads.values() or None in (E.get("gas__H2O"), E.get("gas__H2")):
        return dict(evaluable=False, missing=[k for k, v in ads.items() if v is None])
    slab = E.get(f"{film}__slab")
    if slab is None:  # amendment 4: steps 2 and 3 do not involve the slab
        dG = {sp: delta_G(0.0, e, sp, E["gas__H2O"], E["gas__H2"]) for sp, e in ads.items()}
        s2, s3 = dG["O"] - dG["OH"], dG["OOH"] - dG["O"]
        return dict(evaluable="bound", steps_2_3=[round(s2, 3), round(s3, 3)],
                    eta_lower_bound=round(max(s2, s3) - EQ, 3), eta_interval=[max(s2, s3) - EQ, None])
    dG = {sp: delta_G(slab, e, sp, E["gas__H2O"], E["gas__H2"]) for sp, e in ads.items()}
    r = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
    return dict(evaluable=True, dG={k: round(v, 3) for k, v in dG.items()},
                steps=[round(s, 3) for s in oer_steps(dG["OH"], dG["O"], dG["OOH"])],
                eta=round(r.overpotential, 3), pls=r.potential_limiting_step,
                eta_interval=[r.overpotential, r.overpotential])


def ordering(fe, ni):
    """'kept' if eta_Fe < eta_Ni for every value the intervals allow, 'reversed' if never, else None."""
    if fe.get("evaluable") is False or ni.get("evaluable") is False:
        return None
    (fl, fh), (nl, nh) = ((lo, math.inf if hi is None else hi) for lo, hi in (fe["eta_interval"], ni["eta_interval"]))
    return "kept" if fh < nl else "reversed" if fl >= nh else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="D:/sts-electrocatalyst/film_pilot/out/runs")
    ap.add_argument("--base", default=os.path.join(REPO, "results", "film_pilot_2026-11-14", "readout_u0.json"))
    ap.add_argument("--out", default=os.path.join(REPO, "results", "film_pilot_2026-11-14", "followup_a23.json"))
    a = ap.parse_args()
    base = json.load(open(a.base))
    st = base["states"]
    gas = {g: st[g]["energy_ev"] for g in ("gas__H2O", "gas__H2")}

    # the base readout's etas must come back from its own energies (guards the CHE path used here)
    for tag, key in (("lowest", "energy_lowest_ev"), ("as_relaxed", "energy_ev")):
        for site, (film, mt) in SITES.items():
            E = dict(gas, **{n: st[n][key] for n in st if n.startswith(film + "__")})
            got, want = site_eta(E, film, mt)["eta"], base["sites"][tag][site]["eta"]
            assert abs(got - want) < 5e-4, (tag, site, got, want)

    # ---- A
    a_rec = {}
    for state, (run, cfgs) in A_STATES.items():
        rel = st[state]
        assert rel["name"] == run, (state, rel["name"], run)
        rel_pat = describe(symbols(os.path.join(a.runs, run, run + ".in")), rel["moments"])
        pts = []
        for c in cfgs:
            p = point(a.runs, f"A23{c}__{run}")
            p.update(target=c, counts=p["energy_ev"] is not None)
            if p["energy_ev"] is not None:
                p["dE_vs_relaxed_meV"] = round((p["energy_ev"] - rel["energy_ev"]) * 1000, 2)
                p["same_pattern_as_relaxed"] = p.get("pattern") == rel_pat
            pts.append(p)
        cand = [(rel["energy_ev"], "relaxed")] + [(p["energy_ev"], p["run"]) for p in pts if p["counts"]]
        e_low, frm = min(cand)
        a_rec[state] = dict(run=run, relaxed_pattern=rel_pat, energy_relaxed_ev=rel["energy_ev"],
                            energy_lowest_ev=e_low, lowest_from=frm,
                            shift_meV=round((e_low - rel["energy_ev"]) * 1000, 2), points=pts)
    E = dict(gas, **{n: st[n]["energy_lowest_ev"] for n in st if n.startswith("NiOOH__")})
    E.update({s: r["energy_lowest_ev"] for s, r in a_rec.items()})
    ni_low = site_eta(E, "NiOOH", "Ni0")
    fe_low = base["sites"]["lowest"]["NiFeOOH__Fe0"]["eta"]
    v1_low = bool(fe_low < ni_low["eta"])
    v1_rel = base["verdicts"]["as_relaxed"]["V1"]
    v1 = ("pass" if v1_low and v1_rel else "fail" if not (v1_low or v1_rel)
          else "configuration-sensitive (not a pass)")
    A = dict(states=a_rec, eta_Ni0_lowest=ni_low, eta_Fe0_lowest=fe_low,
             eta_Ni0_lowest_base=base["sites"]["lowest"]["NiOOH__Ni0"]["eta"],
             V1_lowest=v1_low, V1_as_relaxed=v1_rel, V1=v1)

    # ---- B
    b_rec, EU, E0 = {}, dict(gas), dict(gas)
    for state in B_STATES:
        run = st[state]["name"]
        p = point(a.runs, f"A23U__{run}")
        u0_pat = describe(symbols(os.path.join(a.runs, run, run + ".in")), st[state]["moments"])
        p["u0_pattern"] = u0_pat
        p["pattern_changed"] = None if "pattern" not in p else p["pattern"] != u0_pat
        p["low_spin"] = None if "ni_max_abs" not in p else p["ni_max_abs"] < NI_HIGH_SPIN
        p["evaluable"] = bool(p["energy_ev"] is not None and p["low_spin"])
        if p["evaluable"]:
            EU[state] = p["energy_ev"]
        E0[state] = st[state]["energy_ev"]  # the U = 0 as-relaxed energy the point started from
        b_rec[state] = p
    sites_u = {s: site_eta(EU, f, m) for s, (f, m) in SITES.items()}
    sites_0 = {s: site_eta(E0, f, m) for s, (f, m) in SITES.items()}
    for s, r in sites_u.items():
        if r.get("evaluable") is True:
            r["shift_vs_u0"] = dict(dG={k: round(v - sites_0[s]["dG"][k], 3) for k, v in r["dG"].items()},
                                    eta=round(r["eta"] - sites_0[s]["eta"], 3))
    B = dict(states=b_rec, sites=sites_u, sites_u0_as_relaxed=sites_0,
             ordering=ordering(sites_u["NiFeOOH__Fe0"], sites_u["NiOOH__Ni0"]))

    res = dict(amendment=23, base=a.base, runs=a.runs, A=A, B=B)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", newline="\n") as f:
        json.dump(res, f, indent=2)

    print("A: NiOOH configuration single points (U = 0)")
    for s, r in a_rec.items():
        print(f"  {s}: relaxed pattern {r['relaxed_pattern']}; lowest from {r['lowest_from']} ({r['shift_meV']} meV)")
        for p in r["points"]:
            print(f"    {p['target']}: {p['status']}, it {p.get('iterations')}, dE {p.get('dE_vs_relaxed_meV')} meV,"
                  f" landed {p.get('pattern')}, same as relaxed {p.get('same_pattern_as_relaxed')}")
    print(f"  eta Ni0 lowest {ni_low.get('eta')} (base {A['eta_Ni0_lowest_base']}), PLS {ni_low.get('pls')}, "
          f"steps {ni_low.get('steps')}; eta Fe0 lowest {fe_low}")
    print(f"  V1 lowest {v1_low}, as relaxed {v1_rel} -> V1: {v1}")
    print("B: PBE+U single points at the U = 0 geometries")
    for s, p in b_rec.items():
        print(f"  {s:18s} {p['status']:14s} it {p.get('iterations')} E {p['energy_ev']} Ni max |m| {p.get('ni_max_abs')}"
              f" Fe {p.get('fe_moment')} pattern {p.get('pattern')} (U=0 {p['u0_pattern']}) evaluable {p['evaluable']}")
    for s, r in sites_u.items():
        print(f"  {s}: {r.get('dG')} steps {r.get('steps') or r.get('steps_2_3')} eta {r.get('eta', r.get('eta_lower_bound'))}"
              f" PLS {r.get('pls')} shift {r.get('shift_vs_u0')} [{r['evaluable']}]")
    print(f"  ordering at PBE+U (fixed U = 0 geometry): {B['ordering']}")


if __name__ == "__main__":
    main()
