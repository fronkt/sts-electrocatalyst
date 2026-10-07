"""Registered readout for S8 arm C (docs/research/s8-arm-c-dft-design-2026-10-07.md); runs no QE.

Each SCF counts only if the unchanged September runner wrote a COMPLETE receipt and the
unchanged September parser (hea_panel_readout.parse_out) reads the output as CONVERGED, with the
same energy. Energies are scored with the unchanged CHE code (hea_panel_readout.che_from_energies,
banked PBE H2O/H2 of runs/Cr_slab). Registered rules:

* site eta: the four states (slab, OH, O, OOH) of one site, all accepted;
* alloy value C = w_lo * eta_lo + w_hi * eta_hi over the two arm-B p10 support sites with arm B's
  weights; one site incomplete -> the other site's eta, flagged SINGLE_SITE; both -> no value;
* predicted order: ascending C over alloys with a value; K1 and K2 as below;
* best sites: DFT eta at each alloy's best census site (the S8 re-rank gate), reported beside C;
* Ni34 batch-2 nomination: Ni34Fe6Cu29Co31 is nominated if arm C ranks it first or second of
  the six alloys (requires all six values);
* probe: the first variant in registered priority order whose SCF is accepted becomes the
  recipe for ceiling-stopped re-runs.
Informative only: per-site DFT - MLIP differences of eta and of each dG.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hea_panel_readout as hpr  # noqa: E402

STATES = ("slab", "OH", "O", "OOH")
BATCH_1 = ("Cu8Cr23Mn35Co34", "Ni31Cr29Cu5Mn35", "Fe25Co25Ni25Cr25", "Cu26Ni9Cr31Co33", "Cu22Fe30Co32Mn15")
NI34 = "Ni34Fe6Cu29Co31"
CU8, NI31, FE25, CU22 = "Cu8Cr23Mn35Co34", "Ni31Cr29Cu5Mn35", "Fe25Co25Ni25Cr25", "Cu22Fe30Co32Mn15"


def accepted(run_dir: Path, job: str) -> dict:
    """One SCF: COMPLETE runner receipt, CONVERGED parser status and one shared energy."""
    out = run_dir / (job + ".out")
    parsed = hpr.parse_out(out)
    receipt_path = run_dir / (job + ".qc.json")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else None
    row = {"job": job, "parser_status": parsed["status"], "receipt_status": receipt and receipt.get("status"),
           "reason": receipt and receipt.get("reason"), "severe_failures": parsed.get("severe_failures", []),
           "iterations": parsed.get("iterations"),
           "total_magnetization": parsed.get("totmag"), "absolute_magnetization": parsed.get("absmag"),
           "E_eV": None, "accepted": False}
    if receipt is None:
        row["problem"] = "no runner receipt"
        return row
    if receipt.get("status") == "COMPLETE" and parsed["status"] == "CONVERGED":
        energy = (receipt.get("scf") or {}).get("energy_Ry")
        if energy is None or abs(energy - parsed["E_Ry"]) > 1e-9:
            row["problem"] = "receipt and parser energies differ"
            return row
        row.update(E_eV=parsed["E_eV"], accepted=True)
    elif receipt.get("status") == "COMPLETE" or parsed["status"] == "CONVERGED":
        row["problem"] = "runner receipt and parser disagree"
    return row


def failure_class(row: dict) -> str | None:
    """IEEE (identical re-run), CEILING (probe-recipe re-run) or OTHER; None if accepted."""
    if row["accepted"]:
        return None
    reason = (row.get("reason") or "") + " " + row["parser_status"]
    # The runner may stop on the marker mid-run ("numerical failure marker"), so read the output too.
    if "IEEE_" in reason or any("IEEE_" in str(f).upper() for f in row.get("severe_failures") or []):
        return "IEEE"
    if "ceiling" in reason.lower() or row["parser_status"] == "KILLED":
        return "CEILING"
    return "OTHER"


def site_result(site: dict, mirror: Path, gas: dict) -> dict:
    run_dir = mirror / "runs" / site["dir"]
    states = {s: accepted(run_dir, site["states"][s]["job"]) for s in STATES}
    out = {k: site[k] for k in ("formula", "seed", "site_index", "site_metal", "roles", "eta_mlip_V", "dir")}
    out["states"] = states
    out["failures"] = {s: failure_class(r) for s, r in states.items() if not r["accepted"]}
    if out["failures"]:
        out["complete"] = False
        return out
    energies = {s: states[s]["E_eV"] for s in STATES}
    che = hpr.che_from_energies(energies, gas)
    out.update(complete=True, eta_dft_V=che["eta"], dG_dft_eV=che["dG"], steps_eV=che["steps"],
               potential_limiting_step=che["pls"])
    out["informative_dft_minus_mlip"] = {
        "eta_V": che["eta"] - site["eta_mlip_V"],
        "dG_eV": {s: che["dG"][s] - site["dG_mlip_eV"][s] for s in ("OH", "O", "OOH")}}
    return out


def alloy_values(sites: list) -> dict:
    values = {}
    for formula in BATCH_1 + (NI34,):
        own = [s for s in sites if s["formula"] == formula]
        supports = []
        for slot in ("support_lo", "support_hi"):
            match = [s for s in own if slot in s["roles"]]
            if len(match) != 1:
                raise ValueError(f"{formula}: expected one {slot} site")
            supports.append((match[0], float(eval_fraction(match[0]["roles"][slot]["weight"]))))
        done = [(s, w) for s, w in supports if s["complete"]]
        if len(done) == 2:
            value, status = sum(w * s["eta_dft_V"] for s, w in done), "TWO_SITE"
        elif len(done) == 1:
            value, status = done[0][0]["eta_dft_V"], "SINGLE_SITE"
        else:
            value, status = None, "NO_VALUE"
        best = [s for s in own if "best" in s["roles"]]
        values[formula] = {
            "C_V": value, "status": status,
            "supports": [{"site": f"s{s['seed']}/{s['site_index']}", "weight": w,
                          "eta_dft_V": s.get("eta_dft_V"), "complete": s["complete"]} for s, w in supports],
            "p10_mlip_V": supports[0][0]["roles"]["support_lo"]["p10_V"],
            "best_site": ({"site": f"s{best[0]['seed']}/{best[0]['site_index']}", "eta_dft_V": best[0].get("eta_dft_V"),
                           "eta_mlip_V": best[0]["eta_mlip_V"], "complete": best[0]["complete"]} if best else None)}
    return values


def eval_fraction(text: str) -> float:
    numerator, _, denominator = text.partition("/")
    return int(numerator) / int(denominator or 1)


def predictions(values: dict) -> dict:
    have = {f: v["C_V"] for f, v in values.items() if v["C_V"] is not None}
    order = sorted(have, key=have.get)
    out = {"order_all_with_values": order,
           "order_batch_1": [f for f in order if f in BATCH_1],
           "missing": sorted(set(values) - set(have))}
    if all(f in have for f in (CU8, NI31, FE25)):
        more = have[CU8] < have[NI31] and have[CU8] < have[FE25]
        less = have[CU8] > have[NI31] and have[CU8] > have[FE25]
        out["K1"] = ("CU8_MORE_ACTIVE_THAN_NI31_AND_FE25" if more else
                     "CU8_LESS_ACTIVE_THAN_NI31_AND_FE25" if less else "MIXED")
    else:
        out["K1"] = "NOT_EVALUABLE_UNDER_ARM_C"
    if all(f in have for f in BATCH_1):
        out["K2"] = "CU22_LAST" if out["order_batch_1"][-1] == CU22 else "CU22_NOT_LAST"
    else:
        out["K2"] = "NOT_EVALUABLE_UNDER_ARM_C"
    if len(have) == 6:
        out["ni34_batch_2"] = "NOMINATED" if order.index(NI34) <= 1 else "NOT_NOMINATED"
    else:
        out["ni34_batch_2"] = "NOT_EVALUABLE_UNDER_ARM_C"
    return out


def probe(plan: dict, mirror: Path) -> dict:
    source = plan["probe"]["source"]
    probe_dir = mirror / "runs" / "hea" / "arm_c_2026-10-07" / f"probe__{source['formula']}__s{source['seed']}_site{source['site_index']}"
    rows = {v: accepted(probe_dir, "slab__atomic_" + v) for v in plan["probe"]["priority"]}
    chosen = next((v for v in plan["probe"]["priority"] if rows[v]["accepted"]), None)
    return {"variants": rows, "rerun_recipe_for_ceiling_stops": chosen}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True, help="results/arm_c_2026-10-07/site_plan.json")
    parser.add_argument("--mirror", type=Path, required=True, help="raw_mirror with runs/ as on Anvil")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    gas_records = hpr.gas_references()
    gas = {g: gas_records[g]["E_eV"] for g in ("H2O", "H2")}
    sites = [site_result(site, args.mirror, gas) for site in plan["sites"]]
    values = alloy_values(sites)
    result = {"schema": "s8-arm-c-readout-v1", "design": plan["design"], "gas_references": gas_records,
              "sites": sites, "alloys": values, "predictions": predictions(values),
              "probe": probe(plan, args.mirror),
              "counts": {"scf_total": 4 * len(sites), "scf_accepted": sum(r["accepted"] for s in sites for r in s["states"].values()),
                         "sites_complete": sum(s["complete"] for s in sites)}}
    args.out.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"counts": result["counts"], "predictions": result["predictions"],
                      "probe_recipe": result["probe"]["rerun_recipe_for_ceiling_stops"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
