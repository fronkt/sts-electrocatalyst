"""Audit the evidence behind an R4 ranking without changing its frozen scores.

The error budgets are hypothetical independent score perturbations, never fitted
from MAE or site spread. The output cannot authorize a melt or certify OER activity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from hea_oer.ranking_sensitivity import analyze_ranking
from scripts.melt_list import select

INPUT_NAMES = ("r4_screen_box.json", "r4_gated.json", "r4_validate.json", "r4_melt_list.json")
DEFAULT_BUDGETS = (0.0, 0.025, 0.05, 0.10, 0.15, 0.20)


def finite(value, where):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{where}: expected a finite number")
    return float(value)


def _positive_integer(value, where):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{where}: expected a positive integer")
    return value


def _eta(row, where):
    oh, o, ooh = (finite(row[k], where + "." + k) for k in ("dG_OH", "dG_O", "dG_OOH"))
    steps = [oh, o - oh, ooh - o, 4.92 - ooh]
    eta = finite(row["eta"], where + ".eta")
    if abs(eta - (max(steps) - 1.23)) > 1e-9:
        raise ValueError(f"{where}: eta does not reproduce from its three dG values")
    pls = row["pls"]
    if isinstance(pls, bool) or not isinstance(pls, int) or pls not in (1, 2, 3, 4) or abs(steps[pls - 1] - max(steps)) > 1e-9:
        raise ValueError(f"{where}: potential-limiting step does not reproduce")
    return eta


def _rows(payload, where):
    rows = payload["rows"]
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{where}: nonempty rows required")
    result = {}
    for r in rows:
        label = r["formula"]
        if not isinstance(label, str) or not label or label in result:
            raise ValueError(f"{where}: missing or duplicate formula label")
        _eta(r, label)
        elements, fractions = r["elements"], r["fractions"]
        if (not elements or len(elements) != len(fractions) or len(set(elements)) != len(elements)
                or not all(isinstance(e, str) and e for e in elements)):
            raise ValueError(f"{label}: invalid composition")
        fractions = [finite(f, label + ".fraction") for f in fractions]
        if any(f <= 0 or f > 1 for f in fractions) or abs(sum(fractions) - 1) > 1e-8:
            raise ValueError(f"{label}: fractions must be positive and sum to one")
        for key in ("n_sites", "n_decorations"):
            _positive_integer(r[key], label + "." + key)
        lo, mean, hi, sd = (finite(r[k], label + "." + k) for k in ("eta_min", "eta_mean", "eta_max", "eta_std"))
        if lo > mean or mean > hi or sd < 0 or abs(lo - r["eta"]) > 1e-9:
            raise ValueError(f"{label}: invalid site summary")
        if not isinstance(r["desorbed"], list):
            raise ValueError(f"{label}: explicit desorption flags required")
        result[label] = r
    return result


def _site_audit(row):
    records = row.get("per_site_records")
    if records is None:
        return {"available": False, "leave_one_decoration_out": None,
                "reason": "Legacy summaries do not recover individual site chains or decoration minima."}
    if not isinstance(records, list) or len(records) != row["n_sites"]:
        raise ValueError(f"{row['formula']}: site-record count mismatch")
    seen, by_seed, etas = set(), {}, []
    for site in records:
        key = (site["seed"], site["site_index"])
        if key in seen:
            raise ValueError(f"{row['formula']}: duplicate site identity")
        seen.add(key)
        eta = _eta(site, f"{row['formula']} site {key}")
        by_seed.setdefault(str(site["seed"]), []).append(eta)
        etas.append(eta)
    if len(by_seed) != row["n_decorations"]:
        raise ValueError(f"{row['formula']}: decoration count mismatch")
    mean = sum(etas) / len(etas)
    sd = math.sqrt(sum((v - mean) ** 2 for v in etas) / len(etas))
    for key, value in (("eta_min", min(etas)), ("eta_max", max(etas)), ("eta_mean", mean), ("eta_std", sd)):
        if abs(value - row[key]) > 1e-9:
            raise ValueError(f"{row['formula']}: {key} does not reproduce from sites")
    leave_out = {seed: min(v for other, values in by_seed.items() if other != seed for v in values)
                 for seed in by_seed} if len(by_seed) > 1 else None
    return {"available": True, "seed_minima_V": {s: min(v) for s, v in by_seed.items()},
            "leave_one_decoration_out": leave_out,
            "interpretation": "Sampling sensitivity of the legacy minimum; not an electrode model or confidence interval."}


def build_audit(screen, gated, validation, melt_list, tier, budgets=DEFAULT_BUDGETS):
    all_rows = _rows(screen, "screen")
    kept = _rows(gated, "gated")
    if screen["n_screened"] != len(all_rows):
        raise ValueError("screen count mismatch")
    for label, row in kept.items():
        if label not in all_rows or row["desorbed"]:
            raise ValueError(f"{label}: gated row is absent from screen or has desorption flags")
        for key in ("elements", "fractions", "dG_OH", "dG_O", "dG_OOH", "eta", "pls", "eta_min", "eta_mean", "eta_max", "eta_std", "n_sites", "n_decorations", "bonds"):
            if row[key] != all_rows[label][key]:
                raise ValueError(f"{label}: screen/gated mismatch in {key}")
        for key in ("per_site_records", "decoration_records"):
            if row.get(key) != all_rows[label].get(key):
                raise ValueError(f"{label}: screen/gated mismatch in {key}")
    if set(kept) != {label for label, r in all_rows.items() if not r["desorbed"]}:
        raise ValueError("gated roster does not reproduce the legacy desorption gate")
    if screen.get("model") != validation.get("model"):
        raise ValueError("screen/validation model mismatch")

    cards = []
    for label, r in all_rows.items():
        exact_comp = sorted(zip(r["elements"], r["fractions"]))
        identity = hashlib.sha256(json.dumps(exact_comp, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        metal = r["bonds"]["site_metal"]
        ref = tier["tier"].get(metal)
        cards.append({"formula": label, "composition_sha256": identity,
                      "elements": r["elements"], "fractions": r["fractions"],
                      "retained_by_legacy_gate": label in kept, "selected_chain_desorbed": r["desorbed"],
                      "model_eta_V": r["eta"], "winning_site_metal": metal,
                      "site_mean_V": r["eta_mean"], "site_std_V": r["eta_std"],
                      "n_sites": r["n_sites"], "n_decorations": r["n_decorations"],
                      "per_site_evidence": _site_audit(r),
                      "winning_metal_reference": None if ref is None else
                      {"source": ref.get("source"), "OOH_present": ref.get("dG_OOH") is not None,
                       "OOH_upper_bound_closed": ref.get("hi_closed")},
                      "equilibrium_soluble_fraction": kept.get(label, {}).get("soluble_at_operating"),
                      "phase_heuristic": r.get("phase"), "formability_heuristic_passed": r.get("single_phase")})

    ref_rows = []
    for metal, prediction in validation["pred"].items():
        pred = _eta(prediction, "validation " + metal)
        old = finite(validation["dft"][metal], "historical DFT " + metal)
        current = tier["tier"].get(metal)
        ref_rows.append({"metal": metal, "model_eta_V": pred, "historical_target_eta_V": old,
                         "historical_residual_V": pred - old,
                         "tier_eta_V": current.get("eta") if current else None,
                         "tier_residual_V": pred - current["eta"] if current else None,
                         "tier_source": current.get("source") if current else None})
    if not ref_rows or validation["n"] != len(ref_rows):
        raise ValueError("validation count mismatch")
    old_mae = sum(abs(r["historical_residual_V"]) for r in ref_rows) / len(ref_rows)
    if abs(old_mae - finite(validation["mae_eta"], "historical MAE")) > 1e-9:
        raise ValueError("historical validation MAE does not reproduce")
    current_residuals = [r["tier_residual_V"] for r in ref_rows if r["tier_residual_V"] is not None]
    scores = {label: r["eta"] for label, r in kept.items()}
    old_picks = [r["formula"] for r in melt_list["picks"]]
    if len(set(old_picks)) != len(old_picks) or not set(old_picks).issubset(kept):
        raise ValueError("legacy picks do not identify distinct gated candidates")
    for p in melt_list["picks"]:
        if abs(p["eta_pred"] - kept[p["formula"]]["eta"]) > 1e-9:
            raise ValueError("legacy pick score mismatch")
    current_picks = [r["formula"] for _, r in select(list(kept.values()))]
    return {
        "status": "DESCRIPTOR AUDIT ONLY; prospective melt ranking not established",
        "scope": "R4 MACE rutile proxy; preserved legacy minimum over sampled sites",
        "claims": {"iridium_beating_melt_established": False, "S8_election": "not changed",
                   "hypothetical_budgets_are_calibrated": False},
        "counts": {"screened": len(all_rows), "legacy_retained": len(kept),
                   "legacy_excluded": len(all_rows) - len(kept)},
        "candidate_cards": cards,
        "reference_audit": {"rows": ref_rows, "historical_gate_met": validation["gate_met"],
                            "historical_MAE_V": old_mae,
                            "tier_nominal_MAE_V": sum(abs(v) for v in current_residuals) / len(current_residuals) if current_residuals else None,
                            "interpretation": f"{len(ref_rows)} pure endmembers, historical target drift; not a held-out mixed-oxide or electrode error model. Bounded tier values retain their conditional semantics."},
        "ranking_sensitivity": analyze_ranking(scores, budgets),
        "aggregation_diagnostic": {"minimum_order": sorted(scores, key=lambda k: (scores[k], k)),
                                   "mean_order": sorted(kept, key=lambda k: (kept[k]["eta_mean"], k)),
                                   "interpretation": "Changing the summary changes the estimand. Neither mean nor minimum is validated as electrode activity."},
        "selection_version_audit": {"banked_picks": old_picks, "current_selector_picks": current_picks,
                                    "same_members": set(old_picks) == set(current_picks),
                                    "interpretation": "Current-selector comparison only; neither set is newly elected or validated."},
        "evidence_needed": [
            "Complete site/decoration records, geometry identities, and relaxation/adsorption QC.",
            "Complete chains or defensible bounds for the decisions being made; no forced OOH or silent imputation.",
            "Validation on held-out mixed compositions in the modeled phase; grouped splits by composition and structure.",
            "A pre-melt mapping from precursor and processing to the working catalyst or an empirical performance baseline.",
            "Prospective matched-electrode measurements, independent batches, and oxygen/stability verification.",
            "An explicit S8 decision and prediction freeze before any new melt selection is treated as prospective."],
    }


def _lf_hash(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input-dir", type=Path, default=ROOT / "results")
    p.add_argument("--tier", type=Path, default=ROOT / "data/tiers/tier_v2.json")
    p.add_argument("--budgets", type=float, nargs="+", default=DEFAULT_BUDGETS)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    inputs = {name: args.input_dir / name for name in INPUT_NAMES}
    protected = [*inputs.values(), args.tier, Path(__file__), ROOT / "src/hea_oer/ranking_sensitivity.py", ROOT / "src/scripts/melt_list.py"]
    if args.out.resolve() in {path.resolve() for path in protected}:
        p.error("--out must not overwrite an input, reference tier, or implementation")
    data = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in inputs.items()}
    tier = json.loads(args.tier.read_text(encoding="utf-8"))
    audit = build_audit(data[INPUT_NAMES[0]], data[INPUT_NAMES[1]], data[INPUT_NAMES[2]], data[INPUT_NAMES[3]], tier, args.budgets)
    audit["sources"] = {name: {"sha256_lf": _lf_hash(path)} for name, path in inputs.items()}
    audit["sources"]["reference_tier"] = {"version": tier["version"], "sha256_lf": _lf_hash(args.tier)}
    audit["implementation_sha256_lf"] = {name: _lf_hash(ROOT / name) for name in
        ("src/scripts/ranking_adequacy.py", "src/hea_oer/ranking_sensitivity.py", "src/scripts/melt_list.py")}
    audit["hash_convention"] = "SHA256 of bytes with CRLF normalized to LF; no other normalization"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(audit, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(audit["status"])
    print(json.dumps(audit["counts"]))
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
