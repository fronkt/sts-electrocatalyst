"""Offline P-A-v2 decision and checkpoint evidence contract.

This module never launches QE, copies or deletes scratch, or claims production
acceptance. It validates supplied evidence, reads whole checkpoint trees, and
returns a proposed state transition. A future adapter must independently
validate the raw QE, checkpoint, UPF, and settings evidence it supplies here.

An ACCEPT receipt audits an already-observed continuation because proving
optimizer consumption requires its first-call output. It is not pre-launch
permission. `settings_identity` is the adapter's normalized calculation
identity; `settings_source` separately pins the retained source file.
`fixed_flags` uses 1=fixed and 0=free. The adapter must explicitly convert
QE `if_pos` values (1=movable, 0=fixed) before supplying geometry.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
from typing import Optional

RY_MEV = 13605.693
DELTA_MEV = 10.0
STATUS = "OFFLINE_CONTRACT_ONLY"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SCF_STATES = {"CONVERGED", "STALLED", "FAILED"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _path_root(value, label: str) -> Path:
    if value is None:
        raise ValueError(label + " path required")
    try:
        path = Path(value)
    except (TypeError, ValueError) as error:
        raise ValueError(label + " path is malformed") from error
    if path.is_symlink():
        raise ValueError(label + " root is a symlink")
    resolved = path.resolve(strict=False)
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(label + " root is not a directory")
    return resolved


def validate_scratch_separation(restart_outdir, fresh_outdir,
                                restart_wfcdir=None, fresh_wfcdir=None) -> dict:
    """Require restart and fresh outdir/wfcdir roots to be non-overlapping.

    Paths may not exist yet. Resolution detects lexical aliases and existing
    symlink aliases; direct symlink roots are refused. No directory is created.
    """
    roots = []
    for role, outdir, wfcdir in (
            ("restart", restart_outdir, restart_wfcdir),
            ("fresh", fresh_outdir, fresh_wfcdir)):
        roots.append((role + ".outdir", _path_root(outdir, role + ".outdir")))
        if wfcdir is not None:
            roots.append((role + ".wfcdir", _path_root(wfcdir, role + ".wfcdir")))
    for index, (left_name, left) in enumerate(roots):
        for right_name, right in roots[index + 1:]:
            if left == right or left in right.parents or right in left.parents:
                raise ValueError("scratch roots overlap or alias: %s and %s" % (left_name, right_name))
    return {"validated": True, "roots": {name: str(path) for name, path in roots}}


def tree_inventory(root) -> dict:
    """Read a complete recursive file inventory; reject symlinks and special files."""
    raw = Path(root)
    if raw.is_symlink():
        raise ValueError("checkpoint root is a symlink")
    resolved = raw.resolve(strict=True)
    if not resolved.is_dir():
        raise ValueError("checkpoint root is not a directory")
    files = []

    def visit(directory: Path):
        for path in sorted(directory.iterdir(), key=lambda item: item.name):
            if path.is_symlink():
                raise ValueError("checkpoint contains symlink: " + path.relative_to(resolved).as_posix())
            if path.is_dir():
                visit(path)
            elif path.is_file():
                files.append({"path": path.relative_to(resolved).as_posix(),
                              "size_bytes": path.stat().st_size,
                              "sha256": _sha256(path)})
            else:
                raise ValueError("checkpoint contains non-regular entry: " +
                                 path.relative_to(resolved).as_posix())

    visit(resolved)
    files.sort(key=lambda entry: entry["path"])
    return {"root": str(resolved), "files": files}


def checkpoint_inventory(outdir, wfcdir=None) -> dict:
    """Inventory the whole QE outdir and optional distinct wavefunction tree."""
    if wfcdir is not None:
        output_root = _path_root(outdir, "outdir")
        wave_root = _path_root(wfcdir, "wfcdir")
        if (output_root == wave_root or output_root in wave_root.parents
                or wave_root in output_root.parents):
            raise ValueError("outdir and wfcdir overlap or alias")
    out = tree_inventory(outdir)
    wfc = tree_inventory(wfcdir) if wfcdir is not None else None
    if not out["files"] or (wfc is not None and not wfc["files"]):
        raise ValueError("checkpoint outdir and supplied wfcdir must contain retained files")
    body = {"outdir": out, "wfcdir": wfc}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"schema": "pa-checkpoint-tree-v1", **body,
            "sha256": hashlib.sha256(encoded).hexdigest()}


def checkpoint_unchanged(before: dict, after: dict) -> bool:
    """Compare complete inventory identities; a byte/hash-only restart is not accepted."""
    for item in (before, after):
        if (not isinstance(item, dict)
                or set(item) != {"schema", "outdir", "wfcdir", "sha256"}
                or item.get("schema") != "pa-checkpoint-tree-v1"
                or not isinstance(item.get("sha256"), str)
                or not SHA256.fullmatch(item["sha256"])):
            raise ValueError("valid complete checkpoint inventory required")
        for key in ("outdir", "wfcdir"):
            tree = item.get(key)
            if key == "wfcdir" and tree is None:
                continue
            if (not isinstance(tree, dict) or set(tree) != {"root", "files"}
                    or not isinstance(tree.get("root"), str)
                    or not Path(tree["root"]).is_absolute() or not isinstance(tree.get("files"), list)
                    or not tree["files"]):
                raise ValueError("malformed checkpoint tree inventory")
            names = []
            for entry in tree["files"]:
                if (not isinstance(entry, dict) or set(entry) != {"path", "size_bytes", "sha256"}
                        or not isinstance(entry["path"], str)
                        or type(entry["size_bytes"]) is not int or entry["size_bytes"] < 0
                        or not isinstance(entry["sha256"], str) or not SHA256.fullmatch(entry["sha256"])):
                    raise ValueError("malformed checkpoint file inventory entry")
                relative = PurePosixPath(entry["path"])
                if (relative.is_absolute() or not relative.parts
                        or "\\" in entry["path"] or ":" in entry["path"]
                        or relative.as_posix() != entry["path"]
                        or any(part in ("", ".", "..") for part in relative.parts)):
                    raise ValueError("unsafe checkpoint relative path")
                names.append(entry["path"])
            if names != sorted(set(names)):
                raise ValueError("checkpoint inventory paths must be unique and sorted")
        body = {"outdir": item["outdir"], "wfcdir": item["wfcdir"]}
        encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if hashlib.sha256(encoded).hexdigest() != item["sha256"]:
            raise ValueError("checkpoint inventory digest does not match its complete manifest")
    return (before["sha256"] == after["sha256"]
            and before.get("outdir") == after.get("outdir")
            and before.get("wfcdir") == after.get("wfcdir"))


def _source(value, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(label + " source evidence required")
    path, digest = value.get("path"), value.get("sha256")
    first, last = value.get("line_start"), value.get("line_end")
    if (not isinstance(path, str) or not path.strip()
            or not isinstance(digest, str) or not SHA256.fullmatch(digest)
            or type(first) is not int or first < 1
            or type(last) is not int or last < first):
        raise ValueError("malformed " + label + " source evidence")
    return value


def _file_source(value, label: str) -> dict:
    if (not isinstance(value, dict) or not isinstance(value.get("path"), str)
            or not value["path"].strip() or not isinstance(value.get("sha256"), str)
            or not SHA256.fullmatch(value["sha256"])):
        raise ValueError("malformed " + label + " pinned-file evidence")
    return value


def _finite(value, label: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(label + " must be a finite number (bool is invalid)")
    try:
        normalized = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(label + " must be a finite number") from error
    if not math.isfinite(normalized):
        raise ValueError(label + " must be a finite number")
    return normalized


def _geometry(value, label: str) -> dict:
    if not isinstance(value, dict) or value.get("unit") != "bohr":
        raise ValueError(label + " geometry with explicit bohr units required")
    species, positions = value.get("species"), value.get("positions")
    if (not isinstance(species, list) or not species
            or any(not isinstance(atom, str) or not atom.strip() for atom in species)
            or not isinstance(positions, list) or len(positions) != len(species)):
        raise ValueError(label + " atom identities and positions must correspond")
    normalized = []
    for atom, row in zip(species, positions):
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError(label + " positions must be Cartesian triples")
        normalized.append([_finite(component, label + " position") for component in row])
    cell = value.get("cell")
    if not isinstance(cell, list) or len(cell) != 3:
        raise ValueError(label + " explicit three-vector cell required")
    normalized_cell = []
    for row in cell:
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError(label + " cell must contain three Cartesian vectors")
        normalized_cell.append([_finite(component, label + " cell") for component in row])
    fixed = value.get("fixed_flags")
    if not isinstance(fixed, list) or len(fixed) != len(species):
        raise ValueError(label + " fixed-atom flags must match atom count")
    normalized_fixed = []
    for flags in fixed:
        if (not isinstance(flags, list) or len(flags) != 3
                or any(type(flag) is not int or flag not in (0, 1) for flag in flags)):
            raise ValueError(label + " fixed-atom flags must be integer Cartesian 0/1 triples")
        normalized_fixed.append(list(flags))
    return {"unit": "bohr", "species": list(species), "positions": normalized,
            "cell": normalized_cell, "fixed_flags": normalized_fixed}


def _settings_id(value, label: str) -> str:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise ValueError(label + " settings_identity must be a lowercase SHA-256")
    return value


def _scf(value, label: str, *, warm: bool) -> dict:
    if (not isinstance(value, dict) or not isinstance(value.get("status"), str)
            or value["status"] not in SCF_STATES):
        raise ValueError(label + " SCF status must be CONVERGED, STALLED, or FAILED")
    if value.get("energy_unit") != "Ry" or value.get("geometry_unit") != "bohr":
        raise ValueError(label + " must declare Ry energy and bohr geometry units")
    if value.get("geometry_role") != "evaluated":
        raise ValueError(label + " energy must be paired with an explicitly evaluated geometry")
    geometry = _geometry(value.get("geometry"), label)
    energy = value.get("energy_Ry")
    state = value["status"]
    if state == "CONVERGED":
        energy = _finite(energy, label + " energy_Ry")
    elif energy is not None:
        raise ValueError(label + " nonconverged SCF must not carry an energy")
    if warm:
        proposal = _geometry(value.get("proposal_geometry"), "proposal")
        if (proposal["species"] != geometry["species"]
                or proposal["cell"] != geometry["cell"]
                or proposal["fixed_flags"] != geometry["fixed_flags"]):
            raise ValueError("proposal atom identity/order, cell, or fixed flags differ")
        for evaluated, proposed, flags in zip(geometry["positions"], proposal["positions"],
                                             geometry["fixed_flags"]):
            if any(flag and left != right for left, right, flag in zip(evaluated, proposed, flags)):
                raise ValueError("proposal moved a coordinate marked fixed")
    else:
        proposal = None
    return {"status": state, "energy_Ry": energy, "geometry": geometry,
            "proposal_geometry": proposal,
            "settings_identity": _settings_id(value.get("settings_identity"), label),
            "source": _source(value.get("source"), label)}


def _optimizer_resume(saved, observed, settings_identity: str) -> dict:
    if not isinstance(saved, dict) or not isinstance(observed, dict):
        raise ValueError("actual saved and observed optimizer receipts required for continuation")
    saved_bfgs = saved.get("bfgs_count")
    saved_scf = saved.get("scf_count")
    first_bfgs = observed.get("first_optimizer_bfgs_count")
    first_scf = observed.get("first_scf_count")
    for value, label in ((saved_bfgs, "saved BFGS count"), (saved_scf, "saved SCF count"),
                         (first_bfgs, "first optimizer BFGS count"), (first_scf, "first SCF count")):
        if type(value) is not int or value < 0:
            raise ValueError(label + " must be a nonnegative integer")
    if saved_bfgs == 0 or first_bfgs == 0:
        raise ValueError("post-move continuation requires nonzero saved and first-call BFGS counts")
    if saved_scf == 0 or first_scf == 0:
        raise ValueError("post-move continuation requires nonzero saved and first-call SCF counts")
    _source(saved.get("source"), "saved optimizer")
    _source(observed.get("source"), "resume optimizer")
    for field in ("checkpoint_source_validated", "upf_source_validated", "settings_source_validated"):
        if observed.get(field) is not True:
            raise ValueError("continuation lacks adapter validation: " + field)
    validated_files = {}
    for field in ("checkpoint_source", "upf_source", "settings_source"):
        validated_files[field] = _file_source(observed.get(field), field)
    if observed.get("settings_identity") != settings_identity:
        raise ValueError("observed continuation settings identity differs from the checked calculation")
    if observed.get("startup_history_reset") is not False:
        raise ValueError("continuation startup history reset is not allowed")
    if observed.get("restart_fallback") is not False:
        raise ValueError("restart fallback is not allowed")
    if first_bfgs != saved_bfgs or first_scf != saved_scf + 1:
        raise ValueError("first optimizer call does not consume saved state at the next SCF")
    return {"saved_bfgs_count": saved_bfgs, "first_optimizer_bfgs_count": first_bfgs,
            "saved_scf_count": saved_scf, "first_scf_count": first_scf,
            "settings_identity": settings_identity,
            "checkpoint_source_validated": True, "upf_source_validated": True,
            "settings_source_validated": True, "startup_history_reset": False,
            "restart_fallback": False, "validated_files": validated_files}


def _terminal_evidence(value, warm: dict) -> Optional[dict]:
    """Validate BFGS/force convergence at the final evaluated geometry."""
    if value is None:
        return None
    if not isinstance(value, dict) or value.get("geometry_role") != "evaluated":
        raise ValueError("terminal evidence must identify the evaluated geometry")
    geometry = _geometry(value.get("geometry"), "terminal")
    energy = _finite(value.get("energy_Ry"), "terminal evaluated energy_Ry")
    total_force = _finite(value.get("maximum_force_Ry_bohr"), "terminal maximum force")
    threshold = _finite(value.get("force_threshold_Ry_bohr"), "terminal force threshold")
    if total_force < 0 or threshold <= 0:
        raise ValueError("terminal force and threshold must be nonnegative/positive")
    if value.get("bfgs_converged") is not True:
        return {"accepted": False, "reason": "BFGS convergence is not evidenced"}
    _source(value.get("source"), "terminal relaxation")
    if geometry != warm["geometry"] or energy != warm["energy_Ry"]:
        raise ValueError("terminal energy/force evidence is not paired with the warm evaluated geometry")
    if total_force >= threshold:
        return {"accepted": False, "reason": "terminal force does not fall strictly below its registered threshold"}
    return {"accepted": True, "geometry": geometry, "energy_Ry": energy,
            "maximum_force_Ry_bohr": total_force,
            "force_threshold_Ry_bohr": threshold}


def decide_segment(*, warm, fresh, checkpoint_before, checkpoint_after,
                   scratch_paths, segment_index, reseeds_so_far, max_segments,
                   max_reseeds, terminal=False, saved_optimizer=None,
                   resume_receipt=None, terminal_evidence=None) -> dict:
    """Return a validated proposed transition for one segment and its fresh check.

    ACCEPT is a post-hoc audit: it requires evidence that the continuation's
    first optimizer invocation consumed saved history. A future adapter must
    decide ACCEPT versus RESEED from the fresh check before any continuation;
    this function does not authorize or schedule a launch. RESEED only records
    an intentional reset requirement. No scratch mutation occurs here.
    """
    if type(segment_index) is not int or segment_index < 1:
        raise ValueError("segment_index must be a positive integer")
    if type(reseeds_so_far) is not int or reseeds_so_far < 0:
        raise ValueError("reseeds_so_far must be a nonnegative integer")
    if type(max_segments) is not int or max_segments < 1:
        raise ValueError("max_segments must be a positive integer")
    if type(max_reseeds) is not int or max_reseeds < 0:
        raise ValueError("max_reseeds must be a nonnegative integer")
    if segment_index > max_segments or reseeds_so_far > max_reseeds:
        raise ValueError("current counters already exceed the approved cap")
    if type(terminal) is not bool:
        raise ValueError("terminal must be a bool")
    delta_meV = DELTA_MEV

    warm_record = _scf(warm, "warm", warm=True)
    fresh_record = _scf(fresh, "fresh", warm=False)
    if warm_record["settings_identity"] != fresh_record["settings_identity"]:
        raise ValueError("warm and fresh settings identities differ")
    if warm_record["geometry"] != fresh_record["geometry"]:
        raise ValueError("fresh energy must be evaluated at the warm evaluated geometry")
    if not isinstance(checkpoint_before, dict) or not isinstance(checkpoint_after, dict):
        raise ValueError("complete checkpoint inventories before and after fresh check required")
    stable = checkpoint_unchanged(checkpoint_before, checkpoint_after)
    if not isinstance(scratch_paths, dict):
        raise ValueError("restart/fresh scratch path receipt required")
    separation = validate_scratch_separation(
        scratch_paths.get("restart_outdir"), scratch_paths.get("fresh_outdir"),
        scratch_paths.get("restart_wfcdir"), scratch_paths.get("fresh_wfcdir"))
    restart_root = Path(separation["roots"]["restart.outdir"])
    checkpoint_out_root = Path(checkpoint_before["outdir"]["root"])
    checkpoint_wfc = checkpoint_before["wfcdir"]
    restart_wfc_path = separation["roots"].get("restart.wfcdir")
    if restart_root != checkpoint_out_root:
        raise ValueError("checkpoint inventory is not bound to the restart outdir")
    if ((checkpoint_wfc is None) != (restart_wfc_path is None)
            or (checkpoint_wfc is not None and Path(checkpoint_wfc["root"]) != Path(restart_wfc_path))):
        raise ValueError("checkpoint inventory is not bound to the restart wfcdir")
    terminal_record = _terminal_evidence(terminal_evidence, warm_record) if terminal else None

    proposed = "HOLD"
    reason = None
    drop_meV = None
    if not stable:
        reason = "restart checkpoint changed during fresh check"
    elif fresh_record["status"] != "CONVERGED":
        reason = "fresh check has no converged reference"
    elif warm_record["status"] == "FAILED":
        reason = "warm segment failed"
    else:
        if warm_record["status"] == "STALLED":
            proposed = "RESEED"
            reason = "warm segment stalled; fresh density requires intentional history reset"
        else:
            warm_energy = warm_record["energy_Ry"]
            fresh_energy = fresh_record["energy_Ry"]
            drop_meV = (warm_energy - fresh_energy) * RY_MEV
            if not math.isfinite(drop_meV):
                raise ValueError("warm/fresh energy difference is nonfinite")
            # Compare in Ry against the registered per-cell threshold, avoiding
            # a rounded display value deciding the strict boundary.
            if fresh_energy < warm_energy - delta_meV / RY_MEV:
                proposed = "RESEED"
                reason = "fresh state is lower by more than delta_meV"
            elif terminal and terminal_record is not None and terminal_record.get("accepted"):
                proposed = "COMPLETE"
                reason = "terminal segment, fresh reference, and evaluated force evidence accepted"
            elif terminal:
                reason = (terminal_record or {}).get(
                    "reason", "terminal segment lacks evaluated energy/force completion evidence")
            else:
                proposed = "ACCEPT"
                reason = "fresh reference is within the registered per-cell delta"

    action = proposed
    next_segment = segment_index
    next_reseeds = reseeds_so_far
    resume = None
    if proposed in {"ACCEPT", "RESEED"}:
        if segment_index >= max_segments:
            action = "HOLD"
            reason = "segment cap prevents the required next segment"
        elif proposed == "RESEED" and reseeds_so_far >= max_reseeds:
            action = "HOLD"
            reason = "reseed cap prevents the required intentional reset"
        else:
            next_segment = segment_index + 1
            if proposed == "RESEED":
                next_reseeds = reseeds_so_far + 1
            else:
                resume = _optimizer_resume(saved_optimizer, resume_receipt,
                                           warm_record["settings_identity"])

    destination_geometry = None
    history_disposition = "UNDECIDED"
    if action == "ACCEPT":
        destination_geometry = warm_record["proposal_geometry"]
        history_disposition = "INHERIT_VERIFIED"
    elif action == "RESEED":
        destination_geometry = warm_record["geometry"]
        history_disposition = "RESET_REQUIRED_BY_ADAPTER"
    elif action == "COMPLETE":
        destination_geometry = warm_record["geometry"]
        history_disposition = "NOT_APPLICABLE_TERMINAL"
    elif proposed == "COMPLETE":
        destination_geometry = warm_record["geometry"]
        history_disposition = "NOT_APPLICABLE_TERMINAL"
    elif proposed == "RESEED":
        history_disposition = "RESET_BLOCKED_BY_CAP"
    elif proposed == "ACCEPT":
        history_disposition = "INHERIT_BLOCKED_BY_CAP"

    return {
        "status": STATUS, "production_accepted": False,
        "real_catalyst_test_pending": True, "action": action,
        "decision_timing": "POST_HOC_RECEIPT_AUDIT_NOT_LAUNCH_AUTHORITY",
        "proposed_action": proposed, "reason": reason,
        "segment_index": segment_index, "next_segment_index": next_segment,
        "reseeds_so_far": reseeds_so_far, "next_reseeds_so_far": next_reseeds,
        "max_segments": max_segments, "max_reseeds": max_reseeds,
        "terminal": terminal, "delta_meV_per_cell": delta_meV,
        "warm_minus_fresh_meV": drop_meV,
        "evaluated_geometry": warm_record["geometry"],
        "proposed_geometry": warm_record["proposal_geometry"],
        "terminal_evidence": terminal_record,
        "next_geometry": destination_geometry,
        "history_disposition": history_disposition,
        "resume_receipt": resume,
        "checkpoint_unchanged_during_fresh_check": stable,
        "checkpoint_bound_to_restart_scratch": True,
        "checkpoint_sha256_before": checkpoint_before.get("sha256"),
        "checkpoint_sha256_after": checkpoint_after.get("sha256"),
        "scratch_separation": separation,
        "limitations": "Validated supplied evidence only; no raw-QE acceptance, runner, launch permission, or production authority.",
    }
