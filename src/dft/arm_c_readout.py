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
* failures: CEILING (iteration or wall ceiling; checked first, because a stopped run still prints
  gfortran flag notes), IEEE (an IEEE_INVALID/OVERFLOW/DIVIDE_BY_ZERO marker in the SCF or the
  projection output) or OTHER;
* probe: the first variant in registered priority order whose SCF is accepted (converged, no IEEE
  marker) becomes the recipe for ceiling-stopped re-runs; its energy and moments are reported
  against the production control on the same slab;
* re-run round (at most 6 SCFs): rerun_selection() below; a re-run replaces a failed state only if
  it is accepted, and the state then carries its recipe; a chain mixing recipes is flagged.
  Amended (Frank, 2026-10-07, "Go with the full rerun."): the round re-runs every failed state,
  built by arm_c_rerun_build.py; the selection order and substitution rules are unchanged.
Informative only: per-site DFT - MLIP differences of eta and of each dG; the re-run round's recipe
controls (an accepted production slab re-run with the probe recipe: energy and moment differences,
and the site's eta with the control slab).

Extension (exploratory; Frank, 2026-10-08, "Let's rerun DFT for those and get values for them."):
--ext-plan/--ext-mirror apply arm_c_ext_build.py's seeded SCFs after the re-run round, to states that
are still failed, with the same acceptance and substitution rules. The state then carries the recipe
"seeded" (or "unseeded_fallback" if QE did not report reading the seed). Such a readout is written with
the schema s8-arm-c-ext-readout-v1 and reports its K1/K2/Ni34 readings as exploratory_predictions;
arm C's registered readings stay those of the re-run readout. Each attempt records its plan's
seed_density: "copied" (round 1, arm_c_ext_build.py) or "moved" (round 2, arm_c_ext_r2_build.py, after
Frank's "repair": the seed density moved onto the target's atoms).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hea_panel_readout as hpr  # noqa: E402

STATES = ("slab", "OH", "O", "OOH")
BATCH_1 = ("Cu8Cr23Mn35Co34", "Ni31Cr29Cu5Mn35", "Fe25Co25Ni25Cr25", "Cu26Ni9Cr31Co33", "Cu22Fe30Co32Mn15")
NI34 = "Ni34Fe6Cu29Co31"
CU8, NI31, FE25, CU22 = "Cu8Cr23Mn35Co34", "Ni31Cr29Cu5Mn35", "Fe25Co25Ni25Cr25", "Cu22Fe30Co32Mn15"
RERUN_SLOTS = 6
RERUN_ROOT = "hea/arm_c_2026-10-07_rerun"
SEVERE = re.compile(r"IEEE_(?:INVALID|DIVIDE_BY_ZERO|OVERFLOW)")


def accepted(run_dir: Path, job: str) -> dict:
    """One SCF: COMPLETE runner receipt, CONVERGED parser status and one shared energy."""
    out = run_dir / (job + ".out")
    parsed = hpr.parse_out(out)
    receipt_path = run_dir / (job + ".qc.json")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else None
    projection = run_dir / (job + ".projwfc.out")
    projection_text = projection.read_text(encoding="utf-8", errors="replace") if projection.exists() else ""
    row = {"job": job, "parser_status": parsed["status"], "receipt_status": receipt and receipt.get("status"),
           "reason": receipt and receipt.get("reason"), "severe_failures": parsed.get("severe_failures", []),
           "projection_ieee": sorted(set(SEVERE.findall(projection_text))),
           "iterations": parsed.get("iterations"),
           "total_magnetization": parsed.get("totmag"), "absolute_magnetization": parsed.get("absmag"),
           "E_eV": None, "accepted": False, "recipe": "production"}
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
    """CEILING (probe-recipe re-run), IEEE (identical re-run) or OTHER; None if accepted."""
    if row["accepted"]:
        return None
    reason = row.get("reason") or ""
    if row["parser_status"] == "KILLED" or "ceiling" in reason.lower():
        return "CEILING"
    # The runner may stop on the marker mid-run ("numerical failure marker"), so read the outputs too.
    if (SEVERE.search(reason) or any(SEVERE.search(str(f).upper()) for f in row.get("severe_failures") or [])
            or row.get("projection_ieee")):
        return "IEEE"
    return "OTHER"


def site_result(site: dict, mirror: Path, gas: dict, substitutions: dict | None = None,
                rerun_mirror: Path | None = None, extension: dict | None = None,
                ext_mirror: Path | None = None) -> dict:
    run_dir = mirror / "runs" / site["dir"]
    states = {s: accepted(run_dir, site["states"][s]["job"]) for s in STATES}
    out = {k: site[k] for k in ("formula", "seed", "site_index", "site_metal", "roles", "eta_mlip_V", "dir")}
    out["original_failures"] = {s: failure_class(r) for s, r in states.items() if not r["accepted"]}
    attempts = []
    for state, sub in (substitutions or {}).items():
        if states[state]["accepted"] or rerun_mirror is None:
            continue
        rerun = accepted(rerun_mirror / "runs" / sub["dir"], sub["job"])
        rerun["recipe"] = sub["recipe"]
        rerun["replaces"] = states[state]["job"]
        attempts.append(dict(rerun, state=state, failure=failure_class(rerun)))
        if rerun["accepted"]:
            states[state] = rerun
    if substitutions:
        out["rerun_attempts"] = attempts
    extended = []
    for state, sub in (extension or {}).items():
        if states[state]["accepted"] or ext_mirror is None:
            continue
        run_dir = ext_mirror / "runs" / sub["dir"]
        attempt = accepted(run_dir, sub["job"])
        output = run_dir / (sub["job"] + ".out")
        text = output.read_text(errors="replace") if output.exists() else ""
        read = "The initial density is read from file" in text
        own_save = "/tmp_" + sub["job"] + "/" + sub["job"] + ".save/"
        written = any(own_save in line for line in text.splitlines() if "Writing all to output data dir" in line)
        attempt.update(recipe="seeded" if read else "unseeded_fallback", replaces=states[state]["job"],
                       seed=sub["seed"]["job"], seed_state=sub["seed"]["state"], seed_read=read,
                       seed_density=sub.get("seed_density", "copied"),
                       save_written=written, beyond_registered_cap=(attempt.get("iterations") or 0) > 126)
        extended.append(dict(attempt, state=state, failure=failure_class(attempt)))
        if attempt["accepted"]:
            states[state] = attempt
    if extension:
        out["extension_attempts"] = extended
    out["states"] = states
    out["failures"] = {s: failure_class(r) for s, r in states.items() if not r["accepted"]}
    recipes = sorted({r["recipe"] for r in states.values()})
    out["recipes"] = recipes
    out["mixed_recipe"] = len(recipes) > 1
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


def eval_fraction(text: str) -> float:
    numerator, _, denominator = text.partition("/")
    return int(numerator) / int(denominator or 1)


def alloy_values(sites: list) -> dict:
    values = {}
    for formula in BATCH_1 + (NI34,):
        own = [s for s in sites if s["formula"] == formula]
        supports = []
        for slot in ("support_lo", "support_hi"):
            match = [s for s in own if slot in s["roles"]]
            if len(match) != 1:
                raise ValueError(f"{formula}: expected one {slot} site")
            supports.append((match[0], eval_fraction(match[0]["roles"][slot]["weight"])))
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
            "mixed_recipe": any(s.get("mixed_recipe") for s, _ in done),
            "supports": [{"site": f"s{s['seed']}/{s['site_index']}", "weight": w,
                          "eta_dft_V": s.get("eta_dft_V"), "complete": s["complete"],
                          "recipes": s.get("recipes")} for s, w in supports],
            "p10_mlip_V": supports[0][0]["roles"]["support_lo"]["p10_V"],
            "best_site": ({"site": f"s{best[0]['seed']}/{best[0]['site_index']}", "eta_dft_V": best[0].get("eta_dft_V"),
                           "eta_mlip_V": best[0]["eta_mlip_V"], "complete": best[0]["complete"]} if best else None)}
    return values


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
    control_site = next(s for s in plan["sites"] if (s["formula"], s["seed"], s["site_index"]) ==
                        (source["formula"], source["seed"], source["site_index"]))
    control = accepted(mirror / "runs" / control_site["dir"], control_site["states"]["slab"]["job"])
    rows = {v: accepted(probe_dir, "slab__atomic_" + v) for v in plan["probe"]["priority"]}
    for row in rows.values():
        if row["accepted"] and control["accepted"]:
            row["energy_minus_control_meV"] = 1000 * (row["E_eV"] - control["E_eV"])
    chosen = next((v for v in plan["probe"]["priority"] if rows[v]["accepted"]), None)
    return {"control": control, "variants": rows, "rerun_recipe_for_ceiling_stops": chosen}


def recipe_control(row: dict, mirror: Path, rerun_mirror: Path | None, sites: list, gas: dict) -> dict:
    """Informative: one accepted production SCF repeated under the probe recipe."""
    production = accepted(mirror / "runs" / row["site_dir"], row["control_of"])
    control = accepted(rerun_mirror / "runs" / row["dir"], row["job"]) if rerun_mirror else None
    out = {"site_dir": row["site_dir"], "state": row["state"], "recipe": row["recipe"],
           "production": production, "control": control}
    if control and control["accepted"] and production["accepted"]:
        out["energy_control_minus_production_meV"] = 1000 * (control["E_eV"] - production["E_eV"])
        for key in ("total_magnetization", "absolute_magnetization"):
            if control.get(key) is not None and production.get(key) is not None:
                out[key + "_control_minus_production"] = control[key] - production[key]
        site = next(s for s in sites if s["dir"] == row["site_dir"])
        if site["complete"]:
            energies = {s: site["states"][s]["E_eV"] for s in STATES}
            energies[row["state"]] = control["E_eV"]
            out["eta_dft_V_with_control"] = hpr.che_from_energies(energies, gas)["eta"]
    return out


def tier(site: dict) -> int:
    supports = any(r.startswith("support") for r in site["roles"])
    if supports and site["formula"] in (CU8, NI31, FE25):
        return 1
    if supports and site["formula"] in BATCH_1:
        return 2
    if supports:
        return 3
    return 4


def rerun_selection(sites: list, probe_recipe: str | None, slots: int = RERUN_SLOTS) -> list:
    """Registered re-run order; every repairable failed state of a chosen site, all or nothing.

    A site is repairable only if each failed state is IEEE (identical re-run) or CEILING with a probe
    recipe. Order: tier (1 Cu8/Ni31/Fe25 supports, 2 Cu26/Cu22 supports, 3 Ni34 supports, 4 best-only
    sites), then fewer failed states, then site-plan order. A site whose failures exceed the remaining
    slots is skipped and the next one is considered.
    """
    candidates = []
    for order, site in enumerate(sites):
        failures = site["original_failures"]
        if not failures or site["complete"]:
            continue
        if any(c == "OTHER" or (c == "CEILING" and probe_recipe is None) for c in failures.values()):
            continue
        candidates.append((tier(site), len(failures), order, site))
    chosen, remaining = [], slots
    for _, count, _, site in sorted(candidates, key=lambda c: c[:3]):
        if count > remaining:
            continue
        remaining -= count
        name = site["dir"].rsplit("/", 1)[-1]
        for state in STATES:
            kind = site["original_failures"].get(state)
            if kind is None:
                continue
            recipe = "production" if kind == "IEEE" else probe_recipe
            job = state + "__atomic" + ("" if recipe == "production" else "_" + recipe)
            chosen.append({"site_dir": site["dir"], "state": state, "failure": kind, "recipe": recipe,
                           "dir": f"{RERUN_ROOT}/{name}", "job": job})
    return chosen


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True, help="results/arm_c_2026-10-07/site_plan.json")
    parser.add_argument("--mirror", type=Path, required=True, help="raw_mirror with runs/ as on Anvil")
    parser.add_argument("--rerun-plan", type=Path, help="rerun_plan.json written by a re-run build")
    parser.add_argument("--rerun-mirror", type=Path, help="raw_mirror of the re-run round")
    parser.add_argument("--ext-plan", type=Path, help="ext_plan.json written by arm_c_ext_build.py (exploratory)")
    parser.add_argument("--ext-mirror", type=Path, help="raw_mirror of the extension")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.rerun_plan and (args.rerun_mirror is None or not (args.rerun_mirror / "runs").is_dir()):
        parser.error("--rerun-plan needs --rerun-mirror pointing at a collected raw_mirror with runs/")
    if args.ext_plan and (not args.rerun_plan or args.ext_mirror is None or not (args.ext_mirror / "runs").is_dir()):
        parser.error("--ext-plan needs --rerun-plan and --ext-mirror pointing at a collected raw_mirror with runs/")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    gas_records = hpr.gas_references()
    gas = {g: gas_records[g]["E_eV"] for g in ("H2O", "H2")}
    substitutions, control_rows = {}, []
    if args.rerun_plan:
        rerun_plan = json.loads(args.rerun_plan.read_text(encoding="utf-8"))
        for row in rerun_plan["selection"]:
            substitutions.setdefault(row["site_dir"], {})[row["state"]] = row
        control_rows = rerun_plan.get("controls", [])
    extension = {}
    if args.ext_plan:
        for row in json.loads(args.ext_plan.read_text(encoding="utf-8"))["selection"]:
            extension.setdefault(row["site_dir"], {})[row["state"]] = row
    sites = [site_result(site, args.mirror, gas, substitutions.get(site["dir"]), args.rerun_mirror,
                         extension.get(site["dir"]), args.ext_mirror)
             for site in plan["sites"]]
    values = alloy_values(sites)
    probe_result = probe(plan, args.mirror)
    result = {"schema": "s8-arm-c-readout-v1", "design": plan["design"], "gas_references": gas_records,
              "sites": sites, "alloys": values, "predictions": predictions(values), "probe": probe_result,
              "rerun_selection": (None if args.rerun_plan else
                                  rerun_selection(sites, probe_result["rerun_recipe_for_ceiling_stops"])),
              "counts": {"scf_total": 4 * len(sites),
                         "scf_accepted": sum(r["accepted"] for s in sites for r in s["states"].values()),
                         "sites_complete": sum(s["complete"] for s in sites)}}
    if args.rerun_plan:
        attempts = [a for s in sites for a in s.get("rerun_attempts", [])]
        result["counts"].update(rerun_attempted=len(attempts), rerun_accepted=sum(a["accepted"] for a in attempts))
        result["recipe_controls"] = [recipe_control(row, args.mirror, args.rerun_mirror, sites, gas)
                                     for row in control_rows]
    if args.ext_plan:
        attempts = [a for s in sites for a in s.get("extension_attempts", [])]
        result["schema"] = "s8-arm-c-ext-readout-v1"
        result["exploratory_predictions"] = result.pop("predictions")
        result["extension_status"] = "exploratory; arm C's registered readings are those of the re-run readout"
        result["counts"].update(ext_attempted=len(attempts), ext_accepted=sum(a["accepted"] for a in attempts),
                                ext_seed_read=sum(a["seed_read"] for a in attempts))
        for formula, value in values.items():
            supports = [s for s in sites if s["formula"] == formula and {"support_lo", "support_hi"} & set(s["roles"])]
            value["uses_extension"] = any(r["recipe"] in ("seeded", "unseeded_fallback")
                                          for s in supports if s["complete"] for r in s["states"].values())
    args.out.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"counts": result["counts"],
                      "predictions": result.get("predictions", result.get("exploratory_predictions")),
                      "probe_recipe": probe_result["rerun_recipe_for_ceiling_stops"],
                      "rerun_selection": result["rerun_selection"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
