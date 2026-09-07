#!/usr/bin/env python3
"""Readout for the HEA fixed-geometry SCF arms (branch panel + fidelity pilot).

Written while runs/hea/ holds decks and no output. Bands are INHERITED and parsed from their
source files at run time, never copied into source:

  * branch panel: |dE_DFT - dE_MACE| <= the MACE-MPA-0 single-point 15-point dG MAE of
    docs/33-r3-mlip-evaluation.md (the '0.250 eV' cell of the MACE-MPA-0 row), reported
    WITHIN/OUTSIDE. The sign of dE_DFT is scored against the sign of dE_MACE only where
    |dE_MACE| exceeds that band (a sign test inside the band is degenerate: half of the
    WITHIN interval would print SIGN DISAGREES); elsewhere the sign is printed UNSCORED.
    Projector agreement reported per pair (sign and |dE_atomic - dE_ortho|).
  * pilot: eta_DFT at fixed geometry (DFT energies of slab/OH/O/OOH with the banked gas
    references runs/Cr_slab/H2O.out and runs/Cr_slab/H2.out, referencing of
    src/hea_oer/referencing.py, steps of src/hea_oer/descriptors.py) beside eta_MACE from the
    census record; primary band = the MACE-MPA-0 single-point eta MAE of the SAME docs/33 row
    (0.164 V, like-for-like with a fixed-geometry arm); the relaxed-pipeline validation MAE
    `mae_eta` of r4_validate.json (docs/36:16) is printed beside it as a second column;
    per-step dG against the 0.250 eV band; rank order of eta_DFT vs eta_MACE across the
    chains scored. A chain whose OOH record is desorbed has no *OOH state: its third-state
    energy is printed WITHOUT the 0.40 eV *OOH correction, its AEM eta is UNDEFINED and not
    scored, and the bridge-pathway lower bound max(dG1, dG2, dE3) - 1.23 V is printed with
    the fourth step (OH_b -> O_b + H+ + e-, O2 release) UNMEASURED.

Per output the parser reads: the last '!' total energy, JOB DONE, 'convergence NOT
achieved', 'Maximum CPU time exceeded', the SCF iteration count, the PWSCF WALL, the total
and absolute magnetisation, and a <job>.KILLED sidecar (written by the kill rule). A leg is
terminal as CONVERGED, NOT CONVERGED or KILLED, and PENDING otherwise. The readout refuses to
write while any leg is PENDING (exit 3) and writes docs/figs/hea_panel_readout.json once every
leg is terminal, NOT CONVERGED / KILLED rows included (no number on those). For the desorbed
states the Loewdin moment on the adsorbate atoms (<job>.lowdin.txt, or the .projwfc.out) is
read beside the free-species moment (HO2 doublet 1, O2 triplet 2 Bohr mag); a mismatch of
0.5 Bohr mag or more, or a missing table, prints SPIN-STATE UNRESOLVED. No banked value
moves in any branch.

Usage:  python src/dft/hea_panel_readout.py [--json docs/figs/hea_panel_readout.json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

import hea_geometry as hg  # noqa: E402

DOCS33 = ROOT / "docs" / "33-r3-mlip-evaluation.md"
R4_VALIDATE = (ROOT / "results" / "ranking_adequacy_2026-09-06" / "inputs" / "r4_validate.json",
               ROOT / "results" / "r4_validate.json")
BANK = ROOT / "results" / "cr_site_chains_2026-09-06"
PANEL_JSON = BANK / "dft_branch_panel.json"
PANEL_DIR = ROOT / "runs" / "hea" / "branch_panel"
PILOT_DIR = ROOT / "runs" / "hea" / "pilot_retained"
GAS_DIR = ROOT / "runs" / "Cr_slab"
JSON_OUT = ROOT / "docs" / "figs" / "hea_panel_readout.json"
PROJECTORS = ("atomic", "ortho")
STATES = ("slab", "OH", "O", "OOH")
RY_EV = 13.605693122   # src/dft/qe_slab.py:31
EQUILIBRIUM_V = 1.23   # src/hea_oer/descriptors.py OER_EQUILIBRIUM_V
SPIN_TOL_MUB = 0.5     # a moment that rounds to a different integer than the free species
TERMINAL = ("CONVERGED", "NOT CONVERGED", "KILLED")


class Fatal(RuntimeError):
    pass


# --------------------------------------------------------------------------- bands
def registered(docs33: Path = DOCS33, r4_paths=R4_VALIDATE) -> dict:
    text = Path(docs33).read_text(encoding="utf-8")
    m = re.search(r"^\| MACE-MPA-0 \(2024\) \|[^|]*\|[^|]*\|\s*\*\*([\d.]+) eV\*\*\s*\|\s*\*\*([\d.]+) V\*\*\s*\|", text, re.M)
    if not m:
        raise Fatal("could not parse the MACE-MPA-0 15-point dG MAE and eta MAE from docs/33")
    band_dG = float(m.group(1))
    band_eta = float(m.group(2))
    mae = None
    for p in r4_paths:
        if Path(p).exists():
            doc = json.loads(Path(p).read_text(encoding="utf-8"))
            mae = doc.get("mae_eta")
            src = str(p)
            break
    if mae is None:
        raise Fatal("could not read mae_eta from r4_validate.json (tracked copy or original)")
    return dict(band_dG_eV=band_dG, band_dG_source=f"{docs33.name}: MACE-MPA-0 row, 15-point dG MAE",
                band_eta_V=band_eta, band_eta_source=f"{docs33.name}: MACE-MPA-0 row, eta MAE (single-point on DFT geometries)",
                band_eta_secondary_V=float(mae),
                band_eta_secondary_source=os.path.relpath(src, ROOT).replace("\\", "/") + " mae_eta (MACE-relaxed pipeline, n = 7)")


# --------------------------------------------------------------------------- pw.x output
def _wall_seconds(s: str) -> float:
    m = re.match(r"\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*([\d.]+)s", s)
    if not m:
        raise Fatal(f"cannot parse WALL {s!r}")
    return (int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + float(m.group(3)))


def _sidecar(out_path: Path, ext: str) -> Path:
    """<dir>/<job><ext> for <dir>/<job>.out (job names carry dots, so no with_suffix)."""
    out_path = Path(out_path)
    stem = out_path.name[:-4] if out_path.name.endswith(".out") else out_path.name
    return out_path.parent / (stem + ext)


def parse_out(path: Path) -> dict:
    path = Path(path)
    killed = _sidecar(path, ".KILLED").exists()
    if not path.exists():
        return {"exists": False, "killed": killed, "status": "KILLED" if killed else "PENDING"}
    blob = path.read_bytes().decode("utf-8", "replace")
    bang = re.findall(r"^!\s+total energy\s+=\s+([-\d.]+) Ry", blob, re.M)
    it = re.findall(r"convergence has been achieved in\s+(\d+) iterations", blob)
    nit = re.findall(r"convergence NOT achieved after\s+(\d+) iterations", blob)
    wall = re.search(r"PWSCF\s*:\s*.+?CPU\s+(.+?)\s*WALL", blob)
    cores = re.search(r"running on\s+(\d+) processor cores", blob)
    mag = re.findall(r"total magnetization\s*=\s*([-\d.]+)", blob)
    amag = re.findall(r"absolute magnetization\s*=\s*([-\d.]+)", blob)
    o = {
        "exists": True,
        "killed": killed,
        "job_done": blob.count("JOB DONE"),
        "not_achieved": blob.count("convergence NOT achieved"),
        "max_seconds_hit": blob.count("Maximum CPU time exceeded"),
        "E_Ry": float(bang[-1]) if bang else None,
        "E_eV": float(bang[-1]) * RY_EV if bang else None,
        "iterations": int(it[-1]) if it else (int(nit[-1]) if nit else None),
        "wall_s": _wall_seconds(wall.group(1)) if wall else None,
        "cores": int(cores.group(1)) if cores else None,
        "totmag": float(mag[-1]) if mag else None,
        "absmag": float(amag[-1]) if amag else None,
    }
    o["status"] = leg_status(o)
    return o


def leg_status(o: dict) -> str:
    """CONVERGED: a '!' energy and JOB DONE and no non-convergence notice. NOT CONVERGED:
    pw.x printed `convergence NOT achieved` or `Maximum CPU time exceeded` (no '!' line is
    printed in either case). KILLED: the kill-rule sidecar exists. Else PENDING."""
    if not o.get("exists"):
        return "KILLED" if o.get("killed") else "PENDING"
    if o.get("not_achieved", 0) >= 1 or o.get("max_seconds_hit", 0) >= 1:
        return "NOT CONVERGED"
    if o.get("E_Ry") is not None and o.get("job_done", 0) >= 1:
        return "CONVERGED"
    if o.get("killed"):
        return "KILLED"
    return "PENDING"


def lowdin_polarization(path: Path) -> dict | None:
    """{atom_index (0-based): polarization} from a <job>.lowdin.txt / .projwfc.out; None if absent."""
    path = Path(path)
    if not path.exists():
        return None
    blob = path.read_bytes().decode("utf-8", "replace")
    out = {}
    cur = None
    for ln in blob.split("\n"):
        m = re.match(r"\s*Atom #\s*(\d+):", ln)
        if m:
            cur = int(m.group(1)) - 1
            continue
        m = re.match(r"\s*polarization\s*=\s*([-\d.]+)", ln)
        if m and cur is not None:
            out[cur] = float(m.group(1))
    return out or None


def spin_check(out_path: Path, integrity: dict) -> dict:
    """Adsorbate-region Loewdin moment beside the free-species moment for desorbed states;
    out_path is the leg's <job>.out (the tables are <job>.lowdin.txt / <job>.projwfc.out beside it)."""
    exp = integrity.get("expected_free_species_moment_muB")
    if exp is None:
        return {"applies": False}
    ads = sorted(int(i) for i in integrity["atoms"])
    pol = None
    src = None
    for cand in (_sidecar(out_path, ".lowdin.txt"), _sidecar(out_path, ".projwfc.out")):
        pol = lowdin_polarization(cand)
        if pol:
            src = cand.name
            break
    if not pol or any(i not in pol for i in ads):
        return {"applies": True, "expected_muB": exp, "moment_muB": None, "source": None,
                "verdict": "SPIN-STATE UNRESOLVED (no Loewdin table)"}
    m = sum(pol[i] for i in ads)
    ok = abs(abs(m) - exp) < SPIN_TOL_MUB
    return {"applies": True, "expected_muB": exp, "moment_muB": m, "source": src,
            "free_species": integrity["free_species"],
            "verdict": "free-species moment reproduced" if ok else "SPIN-STATE UNRESOLVED"}


def _sign(x: float) -> int:
    return (x > 0) - (x < 0)


# --------------------------------------------------------------------------- panel
def deck_integrity(deck_path: Path) -> dict:
    from hea_deck import parse_deck
    p = parse_deck(Path(deck_path).read_bytes().decode("utf-8"))
    return hg.analyse(p["symbols"], p["positions"], p["cell"])


def score_panel(panel: dict, out_dir: Path, band_dG: float, deck_dir: Path | None = None) -> dict:
    res = {"band_dG_eV": band_dG, "pairs": [], "optional": None, "pending": [], "legs": {}, "integrity": {}}
    deck_dir = Path(deck_dir or out_dir)
    outs = {}

    def leg(label, proj):
        job = f"{label}__{proj}"
        if job not in outs:
            o = parse_out(Path(out_dir) / f"{job}.out")
            deck = deck_dir / f"{job}.in"
            if deck.exists():
                integ = deck_integrity(deck)
                res["integrity"][label] = dict(anomaly_class=integ["anomaly_class"], screen_category=integ["screen_category"],
                                               free_species=integ["free_species"], summary=hg.summary(integ))
                o["spin"] = spin_check(Path(out_dir) / f"{job}.out", integ)
            outs[job] = o
            res["legs"][job] = o
            if o["status"] == "PENDING":
                res["pending"].append(job)
        return outs[job]

    def pair_row(la, lb, dE_mace):
        row = dict(state_A=la, state_B=lb, dE_MACE_eV=dE_mace, sign_scored=abs(dE_mace) > band_dG, projectors={})
        for proj in PROJECTORS:
            oa, ob = leg(la, proj), leg(lb, proj)
            st = {la: oa["status"], lb: ob["status"]}
            if "PENDING" in st.values():
                row["projectors"][proj] = {"verdict": "PENDING", "legs": st}
                continue
            if any(s != "CONVERGED" for s in st.values()):
                row["projectors"][proj] = {"verdict": "NOT CONVERGED (no number)", "legs": st,
                                           "not_achieved": [x for x, s in st.items() if s != "CONVERGED"]}
                continue
            dE = ob["E_eV"] - oa["E_eV"]
            diff = dE - dE_mace
            within = abs(diff) <= band_dG
            agrees = _sign(dE) == _sign(dE_mace)
            verdict = ("WITHIN" if within else "OUTSIDE")
            if row["sign_scored"]:
                verdict = ("SIGN AGREES" if agrees else "SIGN DISAGREES") + " / " + verdict
            else:
                verdict += " (sign UNSCORED: |dE_MACE| <= band)"
            row["projectors"][proj] = dict(
                dE_DFT_eV=dE, dE_DFT_minus_dE_MACE_eV=diff, sign_agrees=agrees, sign_scored=row["sign_scored"],
                band="WITHIN" if within else "OUTSIDE", verdict=verdict, legs=st,
                totmag={la: oa.get("totmag"), lb: ob.get("totmag")},
                spin={la: oa.get("spin"), lb: ob.get("spin")})
        pa, po = row["projectors"]["atomic"], row["projectors"]["ortho"]
        if "dE_DFT_eV" in pa and "dE_DFT_eV" in po:
            row["projector_agreement"] = dict(
                sign_agrees=_sign(pa["dE_DFT_eV"]) == _sign(po["dE_DFT_eV"]),
                dE_atomic_minus_ortho_eV=pa["dE_DFT_eV"] - po["dE_DFT_eV"],
                both_within=pa["band"] == "WITHIN" and po["band"] == "WITHIN")
        else:
            row["projector_agreement"] = {"verdict": "PENDING or NOT CONVERGED"}
        return row

    for pair in panel["pairs"]:
        a, b = pair["states"]
        row = pair_row(f"{pair['arm']}_{a['start']}", f"{pair['arm']}_{b['start']}", pair["MACE_E_B_minus_E_A_eV"])
        row["arm"] = pair["arm"]
        res["pairs"].append(row)
    for opt in panel.get("optional", []):
        row = pair_row(f"{opt['arm']}_pull2.10", f"{opt['arm']}_{opt['start']}", opt["MACE_E_O68_minus_E_O56_eV"])
        row["arm"] = opt["arm"]
        row["role"] = "optional proton-acceptor control: dE = E(pull1.70) - E(pull2.10)"
        res["optional"] = row
    res["pending"] = sorted(set(res["pending"]))
    return res


# --------------------------------------------------------------------------- pilot
def gas_references(gas_dir: Path = GAS_DIR) -> dict:
    out = {}
    for g in ("H2O", "H2"):
        o = parse_out(Path(gas_dir) / f"{g}.out")
        if o["status"] != "CONVERGED":
            raise Fatal(f"banked gas reference {g}.out in {gas_dir} missing or unusable")
        out[g] = dict(E_Ry=o["E_Ry"], E_eV=o["E_eV"], path=os.path.relpath(Path(gas_dir) / f"{g}.out", ROOT).replace("\\", "/"))
    return out


def che_from_energies(E: dict, gas: dict) -> dict:
    from hea_oer.referencing import delta_G
    from hea_oer.descriptors import oer_overpotential
    dG = {sp: delta_G(E["slab"], E[sp], sp, gas["H2O"], gas["H2"]) for sp in ("OH", "O", "OOH")}
    r = oer_overpotential(dG["OH"], dG["O"], dG["OOH"])
    return dict(dG=dG, eta=r.overpotential, pls=r.potential_limiting_step,
                steps=[r.dG1, r.dG2, r.dG3, r.dG4])


def bridge_lower_bound(E: dict, gas: dict) -> dict:
    """Third state is not *OOH: dG1, dG2 as usual; dE3 = E(third) - E(slab) - (2 E_H2O - 3/2 E_H2)
    with NO *OOH correction; the bridge pathway's fourth step (OH_b -> O_b + H+ + e-, O2 release)
    is UNMEASURED, so max(step1, step2, step3) - 1.23 V is a LOWER BOUND on the overpotential."""
    from hea_oer.referencing import delta_G, reference_energy
    dG1 = delta_G(E["slab"], E["OH"], "OH", gas["H2O"], gas["H2"])
    dG2 = delta_G(E["slab"], E["O"], "O", gas["H2O"], gas["H2"])
    dE3 = E["OOH"] - E["slab"] - reference_energy("OOH", gas["H2O"], gas["H2"])
    steps = [dG1, dG2 - dG1, dE3 - dG2]
    return dict(dG_OH=dG1, dG_O=dG2, dE3_no_correction=dE3, steps_1_to_3=steps,
                eta_lower_bound_V=max(steps) - EQUILIBRIUM_V, step_4="UNMEASURED (OH_b -> O_b + H+ + e-, O2 release)")


def score_pilot(chains: list, pilot_dir: Path, band_eta: float, band_dG: float, gas: dict,
                band_eta_secondary: float | None = None, panel_dir: Path = PANEL_DIR) -> dict:
    """chains: dicts from build_hea_pilot.find_chain (formula, seed, site, energies, dG, eta, pls,
    desorbed, integrity, reuse)."""
    res = {"band_eta_V": band_eta, "band_eta_secondary_V": band_eta_secondary, "band_dG_eV": band_dG,
           "gas_DFT": gas, "chains": [], "pending": [], "legs": {}}
    for c in chains:
        tag = f"{c['formula']}__s{c['seed']}_site{c['site']}"
        integ = c.get("integrity") or {}
        ooh_class = integ.get("OOH", {}).get("screen_category", "NORMAL")
        desorbed_ooh = ("OOH" in (c.get("desorbed") or [])) or ooh_class.startswith("DESORPTION")
        mace = dict(E=c["energies"], dG=c["dG"], eta=c["eta"], pls=c["pls"], desorbed=c.get("desorbed"),
                    eta_label=("AEM bookkeeping on a non-*OOH state (census value, kept visible)" if desorbed_ooh else "AEM eta"))
        row = dict(chain=tag, formula=c["formula"], seed=c["seed"], site=c["site"], MACE=mace, projectors={},
                   ooh_state=integ.get("OOH", {}).get("anomaly_class"), desorbed_ooh=desorbed_ooh,
                   integrity={st: hg.summary(integ[st]) for st in integ})
        for proj in PROJECTORS:
            E, pending, notconv, legs = {}, [], [], {}
            for st in STATES:
                job = f"{st}__{proj}"
                reuse = (c.get("reuse") or {}).get(st)
                if reuse:
                    # 'branch_panel/<label>' names a panel deck; its output lives in the panel dir
                    path = Path(panel_dir) / f"{reuse.split('/')[-1]}__{proj}.out"
                    key = f"{tag}/{job} (reused {reuse}__{proj})"
                else:
                    path = Path(pilot_dir) / tag / f"{job}.out"
                    key = f"{tag}/{job}"
                o = parse_out(path)
                if st in integ:
                    o["spin"] = spin_check(path, integ[st])
                res["legs"][key] = o
                legs[job] = o["status"]
                if o["status"] == "PENDING":
                    pending.append(job)
                elif o["status"] != "CONVERGED":
                    notconv.append(job)
                else:
                    E[st] = o["E_eV"]
            if pending:
                res["pending"] += [f"{tag}/{j}" for j in pending]
                row["projectors"][proj] = {"verdict": "PENDING", "missing": pending, "legs": legs}
                continue
            if notconv:
                row["projectors"][proj] = {"verdict": "NOT CONVERGED (no number)", "not_achieved": notconv, "legs": legs}
                continue
            g = {k: v["E_eV"] for k, v in gas.items()}
            if desorbed_ooh:
                bl = bridge_lower_bound(E, g)
                steps = {sp: dict(dG_DFT_eV=bl[f"dG_{sp}"], dG_MACE_eV=mace["dG"][sp],
                                  diff_eV=bl[f"dG_{sp}"] - mace["dG"][sp],
                                  band="WITHIN" if abs(bl[f"dG_{sp}"] - mace["dG"][sp]) <= band_dG else "OUTSIDE")
                         for sp in ("OH", "O")}
                steps["OOH"] = dict(verdict=f"NOT AN *OOH STATE ({row['ooh_state']}); dE3 without the 0.40 eV correction",
                                    dE3_no_correction_eV=bl["dE3_no_correction"], dG_MACE_eV=mace["dG"]["OOH"])
                row["projectors"][proj] = dict(
                    E_DFT_eV=E, legs=legs, bridge=bl, steps=steps, eta_scored=False,
                    verdict=(f"NOT AN *OOH STATE ({row['ooh_state']}): AEM eta UNDEFINED, not scored; "
                             f"bridge-pathway lower bound {bl['eta_lower_bound_V']:.4f} V, step 4 UNMEASURED"))
                continue
            che = che_from_energies(E, g)
            d_eta = che["eta"] - mace["eta"]
            steps = {sp: dict(dG_DFT_eV=che["dG"][sp], dG_MACE_eV=mace["dG"][sp],
                              diff_eV=che["dG"][sp] - mace["dG"][sp],
                              band="WITHIN" if abs(che["dG"][sp] - mace["dG"][sp]) <= band_dG else "OUTSIDE")
                     for sp in ("OH", "O", "OOH")}
            within = abs(d_eta) <= band_eta
            row["projectors"][proj] = dict(
                E_DFT_eV=E, legs=legs, dG_DFT_eV=che["dG"], eta_DFT_V=che["eta"], pls_DFT=che["pls"],
                steps_DFT_eV=che["steps"], eta_DFT_minus_eta_MACE_V=d_eta, eta_scored=True,
                band="WITHIN" if within else "OUTSIDE",
                band_secondary=(None if band_eta_secondary is None else ("WITHIN" if abs(d_eta) <= band_eta_secondary else "OUTSIDE")),
                pls_agrees=che["pls"] == mace["pls"], steps=steps,
                verdict=("WITHIN" if within else "OUTSIDE") + f" (pls DFT {che['pls']} vs MACE {mace['pls']})")
        res["chains"].append(row)
    # rank order across scored chains, per projector
    res["rank_order"] = {}
    for proj in PROJECTORS:
        done = [r for r in res["chains"] if "eta_DFT_V" in r["projectors"][proj]]
        unscored = [r["chain"] for r in res["chains"] if r["projectors"][proj].get("eta_scored") is False]
        pend = [r["chain"] for r in res["chains"] if r["projectors"][proj].get("verdict") in ("PENDING", "NOT CONVERGED (no number)")]
        if pend:
            res["rank_order"][proj] = {"verdict": "PENDING or NOT CONVERGED", "chains": pend}
        elif len(done) >= 2:
            by_dft = [r["chain"] for r in sorted(done, key=lambda r: r["projectors"][proj]["eta_DFT_V"])]
            by_mace = [r["chain"] for r in sorted(done, key=lambda r: r["MACE"]["eta"])]
            conc = disc = 0
            for i in range(len(done)):
                for j in range(i + 1, len(done)):
                    a = done[i]["projectors"][proj]["eta_DFT_V"] - done[j]["projectors"][proj]["eta_DFT_V"]
                    b = done[i]["MACE"]["eta"] - done[j]["MACE"]["eta"]
                    if a * b > 0:
                        conc += 1
                    elif a * b < 0:
                        disc += 1
            res["rank_order"][proj] = dict(order_DFT=by_dft, order_MACE=by_mace, identical=by_dft == by_mace,
                                           kendall_tau=(conc - disc) / max(1, conc + disc), n=len(done), unscored=unscored)
        else:
            res["rank_order"][proj] = {"verdict": f"NOT SCORED ({len(done)} scored chain(s); unscored: {unscored})"}
    res["pending"] = sorted(set(res["pending"]))
    return res


# --------------------------------------------------------------------------- main
def pilot_chains() -> list:
    from build_hea_pilot import RETAINED, find_chain
    out = []
    for s in RETAINED:
        if Path(s["census"]).exists():
            c = find_chain(Path(s["census"]), s["formula"], s["seed"], s["site"])
            c["reuse"] = dict(s["reuse"])
            out.append(c)
    return out


def _spin_line(o: dict) -> str:
    sp = o.get("spin") or {}
    if not sp.get("applies"):
        return ""
    m = sp.get("moment_muB")
    return f"; {sp['verdict']}" + (f" (adsorbate Loewdin {m:+.3f} vs {sp['expected_muB']:.0f} Bohr mag, {sp['source']})" if m is not None else "")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(JSON_OUT))
    ap.add_argument("--no-json", action="store_true")
    args = ap.parse_args(argv)
    bands = registered()
    panel = json.loads(PANEL_JSON.read_text(encoding="utf-8"))
    pr = score_panel(panel, PANEL_DIR, bands["band_dG_eV"])
    print(f"HEA branch panel -- band |dE_DFT - dE_MACE| <= {bands['band_dG_eV']} eV ({bands['band_dG_source']}); sign scored only where |dE_MACE| > band")
    for label, integ in pr["integrity"].items():
        print(f"  integrity {label:22s} {integ['summary']}")
    rows = list(pr["pairs"]) + ([pr["optional"]] if pr["optional"] else [])
    for row in rows:
        print(f"  {row.get('role', 'pair ' + row['arm']):40s} B={row['state_B']} A={row['state_A']}  dE_MACE {row['dE_MACE_eV']:+.9f} eV  sign {'SCORED' if row['sign_scored'] else 'UNSCORED'}")
        for proj, r in row["projectors"].items():
            if "dE_DFT_eV" in r:
                print(f"    {proj:7s} dE_DFT {r['dE_DFT_eV']:+.6f} eV  diff {r['dE_DFT_minus_dE_MACE_eV']:+.6f}  -> {r['verdict']}")
                for lab in (row["state_A"], row["state_B"]):
                    o = pr["legs"][f"{lab}__{proj}"]
                    print(f"      {lab:22s} totmag {o.get('totmag')}{_spin_line(o)}")
            else:
                print(f"    {proj:7s} {r['verdict']} {r.get('legs', '')}")
        pa = row["projector_agreement"]
        if "sign_agrees" in pa:
            print(f"    projectors: sign {'AGREE' if pa['sign_agrees'] else 'DISAGREE'}, atomic - ortho {pa['dE_atomic_minus_ortho_eV']:+.6f} eV")

    chains = pilot_chains()
    gas = gas_references()
    pi = score_pilot(chains, PILOT_DIR, bands["band_eta_V"], bands["band_dG_eV"], gas, bands["band_eta_secondary_V"],
                     panel_dir=PANEL_DIR)
    print(f"HEA fidelity pilot -- primary band |eta_DFT - eta_MACE| <= {bands['band_eta_V']!r} V ({bands['band_eta_source']}); "
          f"secondary {bands['band_eta_secondary_V']!r} V ({bands['band_eta_secondary_source']}); gas {gas['H2O']['path']}, {gas['H2']['path']}")
    for row in pi["chains"]:
        print(f"  {row['chain']}  eta_MACE {row['MACE']['eta']:.6f} V pls {row['MACE']['pls']}  [{row['MACE']['eta_label']}]  OOH state: {row['ooh_state']}")
        for proj, r in row["projectors"].items():
            if "eta_DFT_V" in r:
                print(f"    {proj:7s} eta_DFT {r['eta_DFT_V']:.6f} V  d {r['eta_DFT_minus_eta_MACE_V']:+.6f}  -> {r['verdict']} [secondary {r['band_secondary']}]; "
                      + " ".join(f"dG_{sp} {s['diff_eV']:+.3f}/{s['band']}" for sp, s in r["steps"].items()))
            elif "bridge" in r:
                print(f"    {proj:7s} {r['verdict']}; dG_OH {r['steps']['OH']['diff_eV']:+.3f}/{r['steps']['OH']['band']} dG_O {r['steps']['O']['diff_eV']:+.3f}/{r['steps']['O']['band']} dE3 {r['bridge']['dE3_no_correction']:+.4f} eV (no correction)")
            else:
                print(f"    {proj:7s} {r['verdict']} {r.get('legs', '')}")
    for proj, r in pi["rank_order"].items():
        print(f"  rank order ({proj}): " + (f"DFT {r['order_DFT']} vs MACE {r['order_MACE']} -> {'IDENTICAL' if r['identical'] else 'DIFFERS'} (tau {r['kendall_tau']:+.3f}, n {r['n']}, unscored {r['unscored']})" if "identical" in r else r["verdict"]))

    pending = pr["pending"] + pi["pending"]
    if pending:
        print(f"PENDING ({len(pending)} outputs missing or unfinished): " + ", ".join(pending))
        return 3
    if not args.no_json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(dict(bands=bands, panel=pr, pilot=pi), fh, indent=2)
        print(f"json -> {os.path.relpath(out, ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fatal as e:
        print("REFUSE:", e, file=sys.stderr)
        sys.exit(4)
