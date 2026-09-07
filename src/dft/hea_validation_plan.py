"""Freeze a prospective DFT-label split and materialize retained HEA geometries.

The historical R4 pool and two Cr-chain investigations are already known. Held-out means
withheld from future DFT-label fitting; it never means unseen by the historical MACE screen.
This module performs no relaxation, DFT job, model fitting, or candidate replacement.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import json
from itertools import combinations
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from scripts.screen_diagnostic import identity, sha256_file, validate_manifest  # noqa: E402
from scripts.site_census_plan import BOX_SOURCE, BOX_TWELVE, MANIFEST_DIR, RESULT_DIR  # noqa: E402

SCHEMA = "hea-dft-validation-plan-v1"
SNAPSHOT_SCHEMA = "hea-dft-validation-geometries-v1"
SOURCE_SHA256_LF = "7e234cdfbc6c5b73114b906afa4c05bb8fefbca7c2317194ec738a83307f1124"
SALT = "hea-dft-label-split-2026-09-07-v1"
KNOWN = {"Ni31Cr29Cu5Mn35": (0, 0, "leader"), "Fe25Co25Ni25Cr25": (2, 0, "equiatomic")}
STATES = ("slab", "OH", "O", "OOH")
GEOMETRY_KEYS = ("symbols", "positions_A", "cell_A", "pbc", "fixed_atom_indices", "other_constraint_types")
MODULE = "src/dft/hea_validation_plan.py"


def read_json(path):
    def invalid(value):
        raise ValueError("non-finite JSON constant: " + value)
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("duplicate JSON key: " + key)
            out[key] = value
        return out
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=invalid,
                      object_pairs_hook=unique)


def write_new(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, allow_nan=False)
        handle.write("\n")


def seal(payload, key):
    payload[key] = identity({k: v for k, v in payload.items() if k != key})
    return payload


def _hash(label, candidate):
    # Exact fractions and chemical identity only: no eta, geometry, or result-derived field.
    pairs = sorted(zip(candidate["elements"], candidate["fractions"]))
    return identity({"salt": SALT, "purpose": label, "composition": pairs})


def selection(candidates):
    """Cover both splits' element sets before a deterministic composition-only tie-break.

    Enumerate every eligible four-group holdout. Maximize the smaller element coverage,
    then total coverage across both splits; a composition hash breaks ties. Therefore
    every element occurs in both splits whenever that is feasible. No result is read.
    """
    eligible = [c for c in candidates if c["formula"] not in KNOWN]
    if len(eligible) < 4:
        raise ValueError("need at least four eligible composition groups")

    def objective(group):
        labels = {c["formula"] for c in group}
        held_elements = {el for c in group for el in c["elements"]}
        discovery_elements = {el for c in candidates if c["formula"] not in labels for el in c["elements"]}
        coverage = (min(len(held_elements), len(discovery_elements)),
                    len(held_elements) + len(discovery_elements))
        tie = identity(dict(salt=SALT, purpose="split_combination",
                            composition_hashes=sorted(_hash("split", c) for c in group)))
        return (-coverage[0], -coverage[1], tie)

    chosen = min(combinations(eligible, 4), key=objective)
    heldout = {c["formula"] for c in chosen}
    return [dict(formula=c["formula"], split="heldout_dft_labels" if c["formula"] in heldout else "discovery",
                 seed=int(_hash("seed", c), 16) % 3,
                 site_index=int(_hash("site", c), 16) % 4)
            for c in sorted(candidates, key=lambda c: c["formula"])]


def _coverage(candidates, assignments):
    by_formula = {c["formula"]: c for c in candidates}
    return {split: dict(compositions=sum(a["split"] == split for a in assignments),
                        element_composition_counts=dict(sorted(Counter(
                            el for a in assignments if a["split"] == split
                            for el in by_formula[a["formula"]]["elements"]).items())))
            for split in ("discovery", "heldout_dft_labels")}


def _binding(path, result_filename):
    manifest = read_json(path)
    validate_manifest(manifest)
    return dict(manifest=manifest, manifest_sha256_lf=sha256_file(path, normalize_lf=True),
                result_filename=result_filename, source_kind="census")


def prepare(source=BOX_SOURCE, manifest_dir=MANIFEST_DIR, *, root=ROOT):
    """Freeze identities from the tracked R4 source and manifests, without census results."""
    source, manifest_dir, root = Path(source), Path(manifest_dir), Path(root)
    if sha256_file(source, normalize_lf=True) != SOURCE_SHA256_LF:
        raise ValueError("source is not the pinned tracked R4 box")
    box = read_json(source)
    if box.get("status") != "complete" or len(box["rows"]) != 12:
        raise ValueError("expected complete 12-composition box")
    by_formula = {r["formula"]: r for r in box["rows"]}
    if set(by_formula) != set(BOX_TWELVE):
        raise ValueError("box composition pool differs")
    candidates, bindings = [], {}
    for formula in sorted(by_formula):
        row = by_formula[formula]
        comp = {"elements": row["elements"], "fractions": row["fractions"]}
        candidate = dict(formula=formula, candidate_id=identity(comp), **comp)
        candidates.append(candidate)
        stem = "mpa0__" + formula
        binding = _binding(manifest_dir / (stem + ".json"), stem + "_result.json")
        manifest = binding["manifest"]
        if manifest["source"]["sha256_lf"] != SOURCE_SHA256_LF or manifest["candidates"] != [candidate]:
            raise ValueError("manifest/source composition mismatch: " + formula)
        p = manifest["protocol"]
        if p["seeds"] != [0, 1, 2] or p["n_sites"] != 4 or p["steps"] != 300 or p["fmax_eV_A"] != .05:
            raise ValueError("not the frozen CENSUS-1 protocol")
        bindings[formula] = binding
    assignments = selection(candidates)
    slots = [dict(slot_id="blind__" + a["formula"], arm="energy_blind", binding=a["formula"],
                  selector=dict(kind="fixed", seed=a["seed"], site_index=a["site_index"]),
                  split=a["split"], formula=a["formula"])
             for a in assignments]
    for formula, (seed, index, label) in sorted(KNOWN.items()):
        relative = "results/cr_site_chains_2026-09-06/" + label + "_result.json"
        path = root / relative
        retained = read_json(path)
        validate_manifest(retained["manifest"])
        binding_id = "known__" + label
        bindings[binding_id] = dict(source_kind="retained", result_path=relative,
                                   result_sha256_lf=sha256_file(path, normalize_lf=True),
                                   manifest=retained["manifest"])
        slots.append(dict(slot_id=binding_id, arm="targeted_known_chain", binding=binding_id,
                          formula=formula, split="targeted_audit", selector=dict(kind="fixed", seed=seed, site_index=index)))
    leader = by_formula["Ni31Cr29Cu5Mn35"]
    slots.append(dict(slot_id="historical_leader_winner", arm="targeted_historical_winner",
                      formula=leader["formula"], binding=leader["formula"], split="targeted_audit",
                      selector=dict(kind="unique_banked_fingerprint", seed=leader["bonds"]["seed"],
                                    site_metal=leader["bonds"]["site_metal"], eta_V=leader["eta"],
                                    bonds_A={s: leader["bonds"][s] for s in STATES[1:]},
                                    eta_tolerance_V=1e-6, bond_tolerance_A=1e-3)))
    plan = dict(schema=SCHEMA, source_sha256_lf=SOURCE_SHA256_LF, selection_salt=SALT,
                implementation_sha256_lf={MODULE: sha256_file(root / MODULE, normalize_lf=True)},
                scope="Held out from future DFT-label fitting only; all groups were historically MACE-screened.",
                rules=dict(heldout_composition_count=4, known_groups_excluded_from_holdout=sorted(KNOWN),
                           grouping="exact composition; every seed/site/intermediate of a group stays in its split",
                           selection="Enumerate eligible four-group holdouts; maximize minimum then total element coverage across both splits, composition SHA256 tie-break; seed/site hashes modulo 3/4",
                           replacement="none; retain all pending, failed, ambiguous, and unconverged slots",
                           downstream_holdout="Freeze fitting/threshold rules using discovery DFT labels before inspecting heldout DFT labels.",
                           stratification="Composition-only element coverage in both splits whenever feasible; no outcome-based stratification. Report coverage counts; a 4-group test cannot establish generalization across chemistry.",
                           pilot_scope="One chain per composition is a pilot; it cannot validate the full candidate ranking.",
                           extension="If unresolved, extend to all seeds 0,1,2 and sites 0,1,2,3 within the same composition split; keep all pilot cases. Redesign informed by heldout labels needs a new evaluation set.",
                           state_selection="Retain each selected site's census minimum-energy start, including non-intact and unconverged states; never substitute another site."),
                candidates=candidates, assignments=assignments, coverage=_coverage(candidates, assignments),
                bindings=bindings, slots=slots,
                counts=dict(energy_blind_chains=12, discovery_chains=8, heldout_chains=4,
                            targeted_audit_chains=3, chain_slots=15, state_slots=60,
                            states_per_chain=list(STATES), unique_dft_jobs=None),
                readouts=["paired MACE/DFT energies on identical geometries", "force errors and DFT residual forces",
                          "chemical-state retention and changes on separate DFT relaxation", "ranking reversals and all missing denominators"],
                claims=dict(calibrated_intervals=False, historical_screen_held_out=False,
                            ranking_validated=False, new_composition_generalization=False))
    return seal(plan, "plan_id")


def validate_plan(plan):
    if plan.get("schema") != SCHEMA or plan.get("selection_salt") != SALT:
        raise ValueError("unsupported validation plan")
    if plan.get("plan_id") != identity({k: v for k, v in plan.items() if k != "plan_id"}):
        raise ValueError("plan identity mismatch")
    if plan["source_sha256_lf"] != SOURCE_SHA256_LF:
        raise ValueError("wrong plan source")
    candidates = plan["candidates"]
    if len(candidates) != 12 or {c["formula"] for c in candidates} != set(BOX_TWELVE):
        raise ValueError("wrong plan composition pool")
    expected = selection(candidates)
    if plan["assignments"] != expected or plan["coverage"] != _coverage(candidates, expected):
        raise ValueError("selection or split differs from deterministic rule")
    if len(plan["slots"]) != 15 or len({s["slot_id"] for s in plan["slots"]}) != 15:
        raise ValueError("wrong slot denominator")
    for a in expected:
        slot = next(s for s in plan["slots"] if s["slot_id"] == "blind__" + a["formula"])
        if slot["split"] != a["split"] or slot["selector"] != dict(kind="fixed", seed=a["seed"], site_index=a["site_index"]):
            raise ValueError("energy-blind slot differs from rule")
    expected_counts = dict(energy_blind_chains=12, discovery_chains=8, heldout_chains=4,
                           targeted_audit_chains=3, chain_slots=15, state_slots=60,
                           states_per_chain=list(STATES), unique_dft_jobs=None)
    if plan["counts"] != expected_counts or set(plan["implementation_sha256_lf"]) != {MODULE}:
        raise ValueError("plan denominator or implementation identity differs")
    by_formula = {c["formula"]: c for c in candidates}
    for key, binding in plan["bindings"].items():
        validate_manifest(binding["manifest"])
        if binding["source_kind"] == "census":
            if key not in by_formula or binding["manifest"]["candidates"] != [by_formula[key]]:
                raise ValueError("plan binding composition differs")
            if binding["result_filename"] != "mpa0__" + key + "_result.json":
                raise ValueError("unexpected census filename")
        elif binding["source_kind"] != "retained":
            raise ValueError("unknown binding source kind")
    for slot in plan["slots"]:
        if slot["arm"] == "energy_blind":
            if slot["binding"] != slot["formula"] or slot["slot_id"] != "blind__" + slot["formula"]:
                raise ValueError("energy-blind binding differs")
        else:
            if slot["split"] != "targeted_audit" or slot["formula"] not in KNOWN:
                raise ValueError("targeted evidence cannot enter heldout groups")
            if slot["arm"] == "targeted_known_chain":
                seed, index, label = KNOWN[slot["formula"]]
                if slot["selector"] != dict(kind="fixed", seed=seed, site_index=index) or slot["binding"] != "known__" + label:
                    raise ValueError("known audit identity differs")
            elif slot["arm"] != "targeted_historical_winner" or slot["formula"] != "Ni31Cr29Cu5Mn35":
                raise ValueError("unknown audit arm")
        if slot["selector"]["kind"] not in ("fixed", "unique_banked_fingerprint"):
            raise ValueError("unknown selector")
    return plan


def _result(path, binding):
    """Accept complete records only; reject wrong manifests, candidate sets and hashes."""
    if not path.exists():
        return None, "pending_result", None
    raw_hash = sha256_file(path, normalize_lf=True)
    if binding["source_kind"] == "retained" and raw_hash != binding["result_sha256_lf"]:
        raise ValueError("retained result file changed: " + str(path))
    payload = read_json(path)
    manifest = binding["manifest"]
    if payload.get("schema") != "screen-diagnostic-v1" or payload.get("manifest") != manifest or payload.get("manifest_id") != manifest["manifest_id"]:
        raise ValueError("result manifest mismatch: " + str(path))
    records = payload.get("results", [])
    if payload.get("results_sha256") != identity(records):
        raise ValueError("result content hash mismatch: " + str(path))
    expected = [(c["candidate_id"], c["formula"]) for c in manifest["candidates"]]
    actual = [(r.get("candidate_id"), r.get("formula")) for r in records]
    if actual != expected[:len(actual)]:
        raise ValueError("result candidate identity mismatch")
    status = payload.get("status")
    if status not in ("pending", "running", "partial", "complete", "complete_with_errors"):
        raise ValueError("unknown result status")
    if status not in ("complete", "complete_with_errors"):
        return None, "pending_completion", raw_hash
    if actual != expected:
        raise ValueError("complete result has missing candidates")
    return payload, "complete", raw_hash


def _site(row, selector):
    sites = row.get("per_site_records", [])
    pairs = [(s["seed"], s["site_index"]) for s in sites]
    if len(pairs) != len(set(pairs)):
        raise ValueError("duplicate site identity")
    if selector["kind"] == "fixed":
        matches = [s for s in sites if (s["seed"], s["site_index"]) == (selector["seed"], selector["site_index"])]
    else:
        matches = [s for s in sites if s["seed"] == selector["seed"]
                   and s.get("bonds", {}).get("site_metal") == selector["site_metal"]
                   and isinstance(s.get("eta"), (int, float))
                   and abs(s["eta"] - selector["eta_V"]) <= selector["eta_tolerance_V"]
                   and all(isinstance(s["bonds"].get(sp), (int, float))
                           and abs(s["bonds"][sp] - selector["bonds_A"][sp]) <= selector["bond_tolerance_A"]
                           for sp in STATES[1:])]
    return (matches[0], "matched") if len(matches) == 1 else (None, "pending_ambiguous_identity" if matches else "pending_unmatched_identity")


def _geometry(state):
    """Check shape, finite coordinates, constraints and cell before declaring readiness."""
    if not isinstance(state, dict) or any(k not in state for k in GEOMETRY_KEYS):
        return None
    geom = {k: copy.deepcopy(state[k]) for k in GEOMETRY_KEYS}
    symbols, positions, cell = geom["symbols"], geom["positions_A"], geom["cell_A"]
    if not isinstance(symbols, list) or not symbols or not all(isinstance(s, str) and s.isalpha() for s in symbols):
        raise ValueError("invalid geometry symbols")
    if len(positions) != len(symbols) or len(cell) != 3:
        raise ValueError("invalid geometry shape")
    for vec in positions + cell:
        if not isinstance(vec, list) or len(vec) != 3 or not all(type(x) in (int, float) and math.isfinite(x) for x in vec):
            raise ValueError("invalid geometry coordinate")
    a, b, c = cell
    det = a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
    if abs(det) < 1e-10 or geom["pbc"] != [True, True, True] or any(type(x) is not bool for x in geom["pbc"]):
        raise ValueError("invalid periodic cell")
    fixed = geom["fixed_atom_indices"]
    if not isinstance(fixed, list) or any(type(i) is not int or i < 0 or i >= len(symbols) for i in fixed) or len(fixed) != len(set(fixed)):
        raise ValueError("invalid fixed-atom constraints")
    if geom["other_constraint_types"]:
        return None
    return geom


def materialize(plan, result_dir=RESULT_DIR, *, root=ROOT):
    """Separate immutable readiness snapshot; never update a plan or fill from another site."""
    validate_plan(plan)
    root, result_dir = Path(root), Path(result_dir)
    for relative, expected in plan["implementation_sha256_lf"].items():
        if relative != MODULE or sha256_file(root / relative, normalize_lf=True) != expected:
            raise ValueError("validation implementation changed; retain the old plan")
    loaded, inputs = {}, {}
    for key, binding in plan["bindings"].items():
        path = root / binding["result_path"] if binding["source_kind"] == "retained" else result_dir / binding["result_filename"]
        payload, status, digest = _result(path, binding)
        loaded[key] = (payload, status)
        inputs[key] = dict(path=str(path), status=status, sha256_lf=digest,
                           manifest_id=binding["manifest"]["manifest_id"])
    rows = []
    for slot in plan["slots"]:
        entry = dict(slot_id=slot["slot_id"], formula=slot["formula"], split=slot["split"], arm=slot["arm"],
                     selector=slot["selector"], states={s: dict(status="pending_geometry") for s in STATES})
        payload, status = loaded[slot["binding"]]
        entry["status"] = status
        if payload is not None:
            record = next(r for r in payload["results"] if r["formula"] == slot["formula"])
            if record.get("status") == "error":
                entry["status"] = "candidate_error"
                entry["error"] = record.get("error")
            elif record.get("status") != "evaluated":
                raise ValueError("unknown terminal candidate status")
            else:
                row = record.get("row")
                if not isinstance(row, dict) or row.get("formula") != slot["formula"]:
                    raise ValueError("candidate row identity mismatch")
                candidate = next(c for c in plan["candidates"] if c["formula"] == slot["formula"])
                if any(row.get(k) != candidate[k] for k in ("elements", "fractions")):
                    raise ValueError("candidate row composition mismatch")
                site, entry["status"] = _site(row, slot["selector"])
                if site is not None:
                    entry["resolved_site"] = {k: site[k] for k in ("seed", "site_index")}
                    entry["initial_binding_metal_index"] = site.get("initial_binding_metal_index")
                    entry["initial_binding_metal"] = site.get("initial_binding_metal")
                    entry["retained_site_status"] = {k: copy.deepcopy(site[k])
                                                     for k in ("status", "error", "failure", "failure_status") if k in site}
                    slabs = [r for r in row.get("decoration_records", []) if r["seed"] == site["seed"]]
                    if len(slabs) > 1:
                        raise ValueError("duplicate decoration identity")
                    states = dict(site.get("relaxed_states", {}), slab=slabs[0].get("relaxed_slab") if slabs else None)
                    for sp in STATES:
                        state = states.get(sp)
                        geom = _geometry(state)
                        if geom is not None:
                            entry["states"][sp] = dict(status="ready", geometry=geom,
                                                      geometry_sha256=identity(geom),
                                                      converged_by_force=state.get("converged_by_force"),
                                                      max_constrained_force_eV_A=state.get("max_constrained_force_eV_A"),
                                                      energy_eV=state.get("energy_eV"))
                    entry["status"] = "ready" if all(s["status"] == "ready" for s in entry["states"].values()) else "pending_geometry"
        rows.append(entry)
    ready = sum(s["status"] == "ready" for r in rows for s in r["states"].values())
    unique = {s["geometry_sha256"] for r in rows for s in r["states"].values() if s["status"] == "ready"}
    return seal(dict(schema=SNAPSHOT_SCHEMA, plan_id=plan["plan_id"], inputs=inputs, slots=rows,
                     counts=dict(chain_slots=len(rows), ready_chains=sum(r["status"] == "ready" for r in rows),
                                 state_slots=4*len(rows), ready_state_slots=ready, pending_state_slots=4*len(rows)-ready,
                                 unique_ready_geometries=len(unique)), claims=plan["claims"]), "snapshot_id")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--source", type=Path, default=BOX_SOURCE)
    p.add_argument("--manifest-dir", type=Path, default=MANIFEST_DIR)
    p.add_argument("--out", type=Path, required=True)
    m = commands.add_parser("materialize")
    m.add_argument("--plan", type=Path, required=True)
    m.add_argument("--result-dir", type=Path, default=RESULT_DIR)
    m.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        payload = prepare(args.source, args.manifest_dir)
        validate_plan(payload)
    else:
        payload = materialize(read_json(args.plan), args.result_dir)
    write_new(args.out, payload)
    print(json.dumps(dict(identity=payload.get("plan_id"), counts=payload["counts"]), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
