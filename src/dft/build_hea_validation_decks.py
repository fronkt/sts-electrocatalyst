"""Prepare both-projector SCF decks from a frozen HEA validation readiness snapshot.

Reuse requires exact existing input bytes except its single prefix line. Pending slots
remain explicit. This command runs no calculator and every manifest is NOT LICENSED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hea_cost_model as cm
import hea_deck as hd
import hea_validation_plan as hp

SCHEMA = "hea-validation-decks-v1"
PROJECTORS = ("atomic", "ortho")
REUSE_DIRS = ("hea/branch_panel", "hea/pilot_retained")


def canonical_deck(text):
    """Remove precisely one prefix value, preserving every other byte and line."""
    if "\r" in text:
        raise ValueError("reuse deck has CR bytes")
    lines = text.split("\n")
    indices = [i for i, line in enumerate(lines) if line.startswith("  prefix = '") and line.endswith("'")]
    if len(indices) != 1:
        raise ValueError("deck must have one exact prefix line")
    lines[indices[0]] = "  prefix = '<identity>'"
    return "\n".join(lines)


def validate_snapshot(plan, snapshot):
    hp.validate_plan(plan)
    if snapshot.get("schema") != hp.SNAPSHOT_SCHEMA or snapshot.get("plan_id") != plan["plan_id"]:
        raise ValueError("snapshot plan identity mismatch")
    if snapshot.get("snapshot_id") != hp.identity({k: v for k, v in snapshot.items() if k != "snapshot_id"}):
        raise ValueError("snapshot content identity mismatch")
    wanted = {s["slot_id"]: s for s in plan["slots"]}
    if len(snapshot["slots"]) != len(wanted) or {s["slot_id"] for s in snapshot["slots"]} != set(wanted):
        raise ValueError("snapshot slot denominator differs")
    ready, unique = 0, set()
    for slot in snapshot["slots"]:
        target = wanted[slot["slot_id"]]
        if any(slot[k] != target[k] for k in ("formula", "split", "arm", "selector")):
            raise ValueError("snapshot slot selection differs")
        if set(slot["states"]) != set(hp.STATES):
            raise ValueError("snapshot state denominator differs")
        for state in slot["states"].values():
            if state["status"] == "ready":
                geometry = state["geometry"]
                if hp._geometry(geometry) is None or state["geometry_sha256"] != hp.identity(geometry):
                    raise ValueError("snapshot geometry identity mismatch")
                ready += 1
                unique.add(state["geometry_sha256"])
            elif state["status"] != "pending_geometry":
                raise ValueError("unknown geometry readiness status")
    expected = dict(chain_slots=len(wanted), ready_chains=sum(s["status"] == "ready" for s in snapshot["slots"]),
                    state_slots=4*len(wanted), ready_state_slots=ready,
                    pending_state_slots=4*len(wanted)-ready, unique_ready_geometries=len(unique))
    if snapshot["counts"] != expected:
        raise ValueError("snapshot counts differ from retained slots")


def reuse_index(runs):
    out = {}
    for relative in REUSE_DIRS:
        for path in sorted((runs / relative).rglob("*.in")):
            text = path.read_bytes().decode("utf-8")
            canonical = canonical_deck(text)
            out.setdefault(canonical, []).append((path, text))
    return out


def render_bundle(plan, snapshot, out_root, *, repo=hd.REPO):
    """Pure preparation: all hashes, geometry masks, aliases and new-deck costs first."""
    validate_snapshot(plan, snapshot)
    runs = (Path(repo) / "runs").resolve()
    out_root = Path(out_root).resolve()
    try:
        relative = out_root.relative_to(runs).as_posix()
    except ValueError:
        raise ValueError("output root must be beneath repository runs")
    if out_root == runs or any(out_root == runs / p or (runs / p) in out_root.parents for p in REUSE_DIRS):
        raise ValueError("output root would overlap original reuse inputs")
    existing = reuse_index(runs)
    template = hd.load_template()
    aliases, unique, deck_texts = [], {}, {}
    for slot in snapshot["slots"]:
        for state_name in hp.STATES:
            state = slot["states"][state_name]
            for projector in PROJECTORS:
                alias = dict(slot_id=slot["slot_id"], formula=slot["formula"], split=slot["split"],
                             state=state_name, projector=projector, slot_status=slot["status"],
                             converged_by_force=state.get("converged_by_force"))
                if state["status"] != "ready":
                    aliases.append(dict(alias, status="pending", reason=slot["status"]))
                    continue
                geometry, digest = state["geometry"], state["geometry_sha256"]
                key = digest + "__" + projector
                if key in unique:
                    aliases.append(dict(alias, status="alias", target=unique[key]["path"],
                                        target_origin=unique[key]["origin"], geometry_sha256=digest))
                    continue
                job = "g_" + digest + "__" + projector
                text = hd.render_deck(job, geometry["symbols"], geometry["positions_A"], geometry["cell_A"],
                                      geometry["fixed_atom_indices"], projector, template)
                info = hd.deck_info(text)
                canonical = canonical_deck(text)
                matches = existing.get(canonical, [])
                if matches:
                    target, existing_text = matches[0]
                    # The canonical match checks coordinates, masks, all numerical settings,
                    # species, U/projector, magnetization and force output, not geometry alone.
                    path = target.relative_to(runs).as_posix()
                    record = dict(path=path, origin="existing", projector=projector,
                                  geometry_sha256=digest, md5=hd.md5_bytes(existing_text.encode()),
                                  sha256_bytes=hashlib.sha256(existing_text.encode()).hexdigest(),
                                  equivalent_existing_paths=[p.relative_to(runs).as_posix() for p, _ in matches])
                    status = "reused"
                else:
                    path = relative + "/" + job + ".in"
                    if path in deck_texts and deck_texts[path] != text:
                        raise ValueError("deck path collision")
                    deck_texts[path] = text
                    estimate = cm.per_scf(info["counts"], info["cell"], info["nkpts"], info["nk"])
                    record = dict(path=path, origin="new", projector=projector,
                                  geometry_sha256=digest, md5=hd.md5_bytes(text.encode()),
                                  sha256_bytes=hashlib.sha256(text.encode()).hexdigest(), nk=info["nk"],
                                  nat=info["nat"], species_counts=info["counts"], mesh=list(info["mesh"]),
                                  cost=dict(estimate[projector], ram_total_GB=estimate["ram_total_GB_envelope"],
                                            ram_ceiling_GB=estimate["ram_total_GB_ceiling"],
                                            billing=estimate["billing"], billing_ceiling=estimate["billing_ceiling"]))
                    status = "new"
                unique[key] = record
                aliases.append(dict(alias, status=status, target=path, geometry_sha256=digest))
    new = [r for r in unique.values() if r["origin"] == "new"]
    totals = {key: sum(r["cost"][key] for r in new) for key in ("plan_coreh", "floor_coreh", "ceiling_coreh")}
    totals.update(max_ram_GB=max((r["cost"]["ram_total_GB"] for r in new), default=0),
                  max_ram_ceiling_GB=max((r["cost"]["ram_ceiling_GB"] for r in new), default=0),
                  all_plan_fit_node=all(r["cost"]["billing"]["fits_node"] for r in new))
    inventory = dict(schema=SCHEMA, plan_id=plan["plan_id"], snapshot_id=snapshot["snapshot_id"],
                     claims=dict(plan["claims"], submitted=False), aliases=aliases, unique_inputs=list(unique.values()),
                     counts=dict(chain_slots=len(snapshot["slots"]), state_slots=snapshot["counts"]["state_slots"],
                                 projector_slots=len(aliases), pending_projector_slots=sum(a["status"] == "pending" for a in aliases),
                                 ready_projector_slots=sum(a["status"] != "pending" for a in aliases),
                                 unique_new_inputs=len(new), unique_reused_inputs=len(unique)-len(new)),
                     cost_new_inputs_only=totals,
                     protocol="Fixed geometry, banked FM/MP-U baseline, forces on, both projectors; spin/numerical controls remain separate.")
    hp.seal(inventory, "inventory_id")
    lines = ["# HEA DFT-label validation pilot: ready coordinates only; fixed geometry, both projectors.",
             "# NOT LICENSED FOR SUBMISSION. No calculation or deposit is implied by this manifest.",
             "# SUBMIT WITH EXCLUDE=" + hd.EXCLUDE, f"# NP={hd.NP} NCONC=1",
             "# plan_id=" + plan["plan_id"], "# snapshot_id=" + snapshot["snapshot_id"],
             "# inventory_id=" + inventory["inventory_id"],
             "# Counts " + json.dumps(inventory["counts"], sort_keys=True),
             "# New-input planning estimate " + json.dumps(totals, sort_keys=True),
             "# Estimates inherit hea_cost_model; no new-chemistry convergence guarantee.",
             "# Existing inputs below are reused by reference; they are not runnable rows in this manifest."]
    for alias in aliases:
        lines.append("# " + json.dumps(alias, sort_keys=True))
    for record in new:
        lines.append(f"# md5 {record['md5']} {record['path']}")
        path = Path(record["path"])
        lines.append(f"{path.parent.as_posix()} {path.stem} .in {record['nk']}")
    manifest = "\n".join(lines) + "\n"
    hd.check_manifest_text(manifest, expect_not_licensed=True)
    files = dict(deck_texts)
    files[relative + "/m_validation.txt"] = manifest
    files[relative + "/inventory.json"] = json.dumps(inventory, indent=2, allow_nan=False) + "\n"
    return inventory, files


def build(plan, snapshot, out_root, *, repo=hd.REPO, check=False):
    inventory, files = render_bundle(plan, snapshot, out_root, repo=repo)
    runs = (Path(repo) / "runs").resolve()
    # Preflight the whole bundle before any write; check mode requires every artifact.
    for relative, text in files.items():
        path = runs / relative
        if check and not path.is_file():
            raise FileNotFoundError("missing prepared artifact: " + str(path))
        if path.exists() and path.read_bytes() != text.encode("utf-8"):
            raise ValueError("prepared artifact differs: " + str(path))
    if not check:
        for relative, text in files.items():
            hd.write_lf(runs / relative, text)
    return inventory


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, default=hd.REPO / "runs/hea/validation_2026-09-07")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    inventory = build(hp.read_json(args.plan), hp.read_json(args.snapshot), args.out_root, check=args.check)
    print(json.dumps(dict(inventory_id=inventory["inventory_id"], counts=inventory["counts"],
                          cost_new_inputs_only=inventory["cost_new_inputs_only"]), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
