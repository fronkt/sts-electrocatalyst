"""Offline readout for the fixed-geometry diagnostic; never runs QE or touches Anvil.

Parses each arm's retained stdout.log, input.in and data-file-schema.xml into
evaluations (XML energies/forces converted from Hartree to Ry), then applies the
readings registered in docs/research/pa-fixed-geometry-diagnostic-2026-10-05.md.

Unit conventions verified on job 21075231 (readout 2026-10-05): XML step and output
energies/forces are Hartree atomic units (x2 -> Ry, Ry/bohr); relaxation-step
scf_error is Ry, output convergence_info scf_error is Hartree (x2 -> Ry).

A rung run with scf_must_converge = .false. that hits electron_maxstep prints
"convergence has been achieved" and writes convergence_achieved=true
(electrons.f90:881, 1228). Such a rung is classified CAPPED when its iteration
count equals electron_maxstep and its final printed accuracy exceeds conv_thr.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NAT = 72
RY_EV = 13.605693122994
BOHR_ANG = 0.529177210903
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?"
GATE = {"energy_Ry": 1e-6, "position_bohr": 1e-5, "force_Ry_bohr": 1e-5}
IDENTICAL_FORCE = 1e-8          # same numerical path (stdout/XML rounding is 5.1e-9)
STATE_TRACE = 1e-3              # max |delta Tr[ns]| per atom and spin for "same state"
STATE_MAGNETIZATION = 0.01      # Bohr mag/cell


def number(text: str) -> float:
    value = float(text.replace("D", "E").replace("d", "e"))
    if not math.isfinite(value):
        raise ValueError("nonfinite value")
    return value


def tag(element) -> str:
    return element.tag.split("}")[-1]


def child(element, name):
    return next(x for x in element if tag(x) == name)


def find(element, *names):
    for name in names:
        element = child(element, name)
    return element


def values(element) -> list:
    return [number(x) for x in (element.text or "").split()]


def deck_settings(text: str) -> dict:
    def get(key, default=None):
        hits = re.findall(r"(?mi)^\s*" + re.escape(key) + r"\s*=\s*([^\s,!]+)", text)
        if len(hits) > 1:
            raise ValueError("duplicate deck key " + key)
        return hits[0].strip("'\"") if hits else default
    return {"calculation": get("calculation"), "restart_mode": get("restart_mode"),
            "conv_thr": number(get("conv_thr")), "electron_maxstep": int(get("electron_maxstep", "100")),
            "scf_must_converge": (get("scf_must_converge", ".true.").lower() != ".false."),
            "diago_thr_init": number(get("diago_thr_init", "0.0")),
            "startingpot": get("startingpot"), "startingwfc": get("startingwfc")}


def scf_blocks(stdout: str) -> list:
    """One record per completed SCF (an SCF with a printed '!' total energy)."""
    starts = list(re.finditer(r"(?m)^\s*Self-consistent Calculation\s*$", stdout))
    frames = []
    for i, start in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(stdout)
        block = stdout[start.end():end]
        energy = re.search(r"(?m)^!\s*total energy\s*=\s*(" + NUM + r")\s*Ry", block)
        if not energy:
            continue
        iterations = [int(m.group(1)) for m in re.finditer(r"(?m)^\s*iteration #\s*(\d+)", block)]
        achieved = re.search(r"convergence has been achieved in\s*(\d+)\s*iterations", block)
        if not achieved or iterations != list(range(1, int(achieved.group(1)) + 1)):
            raise ValueError("SCF iteration record is not contiguous")
        accuracy = [number(m.group(1)) for m in re.finditer(r"estimated scf accuracy\s*<\s*(" + NUM + r")\s*Ry", block)]
        ethr = [number(m.group(1)) for m in re.finditer(r"ethr\s*=\s*(" + NUM + r")", block)]
        traces = {}
        for m in re.finditer(r"Tr\[ns\(\s*(\d+)\)\]\s*\(up, down, total\)\s*=\s*(" + NUM + r")\s+(" + NUM + r")\s+(" + NUM + r")", block):
            traces[int(m.group(1))] = [number(m.group(j)) for j in (2, 3, 4)]
        total = re.findall(r"(?m)^\s*total magnetization\s*=\s*(" + NUM + r")", block)
        absolute = re.findall(r"(?m)^\s*absolute magnetization\s*=\s*(" + NUM + r")", block)
        correction = re.search(r"Total force\s*=\s*(" + NUM + r")\s*Total SCF correction\s*=\s*(" + NUM + r")", block)
        fermi = re.search(r"the Fermi energy is\s*(" + NUM + r")\s*ev", block)
        frames.append({
            "log_energy_Ry": number(energy.group(1)), "iterations": len(iterations),
            "accuracy_sequence_Ry": accuracy, "final_accuracy_Ry": accuracy[-1] if accuracy else None,
            "first_ethr_Ry": ethr[0] if ethr else None,
            "final_hubbard_traces": traces,
            "total_magnetization": number(total[-1]) if total else None,
            "absolute_magnetization": number(absolute[-1]) if absolute else None,
            "total_force_Ry_bohr": number(correction.group(1)) if correction else None,
            "total_scf_correction_Ry_bohr": number(correction.group(2)) if correction else None,
            "fermi_energy_eV": number(fermi.group(1)) if fermi else None})
    return frames


def xml_frames(xml_path: Path, kind: str) -> list:
    root = ET.fromstring(xml_path.read_bytes())
    nodes = [x for x in root if tag(x) == "step"] if kind == "relax" else [child(root, "output")]
    frames = []
    for node in nodes:
        atoms = list(find(node, "atomic_structure", "atomic_positions"))
        if [int(a.attrib["index"]) for a in atoms] != list(range(1, NAT + 1)):
            raise ValueError("XML atom indices are not 1..72")
        forces = values(find(node, "forces"))
        if len(forces) != 3 * NAT:
            raise ValueError("XML force record is not 72x3")
        scf = find(node, "scf_conv") if kind == "relax" else find(node, "convergence_info", "scf_conv")
        error = values(find(scf, "scf_error"))[0] * (1 if kind == "relax" else 2)
        magnetization = {}
        if kind == "scf":
            node_mag = next((x for x in node if tag(x) == "magnetization"), None)
            for key in ("total", "absolute"):
                field = next((x for x in node_mag if tag(x) == key), None) if node_mag is not None else None
                if field is not None:
                    magnetization[key] = number(field.text)
        frames.append({
            "xml_magnetization": magnetization,
            "species": [a.attrib["name"] for a in atoms],
            "positions_bohr": [values(a) for a in atoms],
            "energy_Ry": values(find(node, "total_energy", "etot"))[0] * 2,
            "forces_Ry_bohr": [[2 * v for v in forces[i:i + 3]] for i in range(0, 3 * NAT, 3)],
            "xml_scf_error_Ry": error, "xml_n_scf_steps": int(find(scf, "n_scf_steps").text)})
    return frames


def rung_status(kind: str, settings: dict, iterations: int, xml_error_Ry: float) -> str:
    """The printed accuracy has one or two significant digits; classify with the XML value."""
    if kind == "scf" and iterations == settings["electron_maxstep"] and xml_error_Ry >= settings["conv_thr"]:
        return "CAPPED_UNCONVERGED"
    return "CONVERGED"


def parse_arm(directory: Path, xml_path: Path) -> dict:
    deck = (directory / "input.in").read_text(encoding="utf-8")
    settings = deck_settings(deck)
    stdout = (directory / "stdout.log").read_text(encoding="utf-8", errors="replace")
    kind = "relax" if settings["calculation"] == "relax" else "scf"
    logs, frames = scf_blocks(stdout), xml_frames(xml_path, kind)
    if len(logs) != len(frames):
        raise ValueError(f"{directory.name}: {len(logs)} logged SCFs but {len(frames)} XML frames")
    evaluations = []
    for log, frame in zip(logs, frames):
        if abs(log["log_energy_Ry"] - frame["energy_Ry"]) > 5.1e-9:
            raise ValueError("stdout/XML energy mismatch")
        if frame["xml_n_scf_steps"] != log["iterations"]:
            raise ValueError("stdout/XML SCF iteration mismatch")
        if abs(frame["xml_scf_error_Ry"] - log["final_accuracy_Ry"]) > 5.1e-9 + 1e-6 * log["final_accuracy_Ry"]:
            raise ValueError("stdout/XML SCF error mismatch")
        merged = dict(frame, **log, status=rung_status(kind, settings, log["iterations"], frame["xml_scf_error_Ry"]))
        for key in ("total", "absolute"):
            if key in frame["xml_magnetization"]:
                merged[key + "_magnetization"] = frame["xml_magnetization"][key]
        evaluations.append(merged)
    cycles = [int(m) for m in re.findall(r"number of scf cycles\s*=\s*(\d+)", stdout)]
    # A warm start must actually have read the file state (wfcinit.f90 falls back silently
    # to atomic+random when the wavefunctions are missing).
    start = {"wfc_from_file": "Starting wfcs from file" in stdout,
             "wfc_fallback": ("Cannot read wfcs" in stdout or "recomputing them from scratch" in stdout),
             "density_from_file": "The initial density is read from file" in stdout}
    expected_file = settings["startingwfc"] == "file"
    start["valid"] = (not start["wfc_fallback"] and start["wfc_from_file"] == expected_file
                      and start["density_from_file"] == (settings["startingpot"] == "file"))
    return {"directory": str(directory), "settings": settings, "kind": kind, "start": start,
            "global_scf_cycles": cycles, "evaluations": evaluations}


def max_component(left: list, right: list, species: list) -> dict:
    rows = [(abs(b - a), i, j, a, b) for i, (ra, rb) in enumerate(zip(left, right))
            for j, (a, b) in enumerate(zip(ra, rb))]
    value, i, j, a, b = max(rows)
    return {"absolute": value, "atom": i + 1, "species": species[i], "axis": "xyz"[j],
            "left": a, "right": b}


def compare(left: dict, right: dict) -> dict:
    if left["species"] != right["species"]:
        raise ValueError("species order differs")
    force = max_component(left["forces_Ry_bohr"], right["forces_Ry_bohr"], left["species"])
    position = max_component(left["positions_bohr"], right["positions_bohr"], left["species"])
    traces = [abs(left["final_hubbard_traces"][k][s] - right["final_hubbard_traces"][k][s])
              for k in left["final_hubbard_traces"] for s in (0, 1)
              if k in right["final_hubbard_traces"]]
    metrics = {"energy_Ry": abs(right["energy_Ry"] - left["energy_Ry"]),
               "position_bohr": position["absolute"], "force_Ry_bohr": force["absolute"]}
    return {"metrics": metrics, "gate_failures": [k for k, v in metrics.items() if v > GATE[k]],
            "max_force_component": force, "max_position_component": position,
            "energy_delta_meV": (right["energy_Ry"] - left["energy_Ry"]) * RY_EV * 1000,
            "force_delta_eV_per_angstrom": force["absolute"] * RY_EV / BOHR_ANG,
            "max_hubbard_trace_delta": max(traces) if traces else None,
            "total_magnetization_delta": (None if left["total_magnetization"] is None or right["total_magnetization"] is None
                                          else abs(right["total_magnetization"] - left["total_magnetization"])),
            "absolute_magnetization_delta": (None if left["absolute_magnetization"] is None or right["absolute_magnetization"] is None
                                             else abs(right["absolute_magnetization"] - left["absolute_magnetization"]))}


def summary(evaluation: dict) -> dict:
    keys = ("status", "iterations", "xml_scf_error_Ry", "final_accuracy_Ry", "first_ethr_Ry", "energy_Ry",
            "total_force_Ry_bohr", "total_scf_correction_Ry_bohr", "total_magnetization",
            "absolute_magnetization", "fermi_energy_eV")
    return {k: evaluation[k] for k in keys}


def readings(arms: dict, trial: dict) -> dict:
    """Apply the registered readings; missing arms leave their reading UNAVAILABLE."""
    out = {}
    control, resumed = trial["control"]["evaluations"], trial["resumed"]["evaluations"]
    if "A_replay" in arms:
        c = compare(resumed[0], arms["A_replay"]["evaluations"][0])
        f = c["metrics"]["force_Ry_bohr"]
        out["R1_restart_path_reproducibility"] = dict(c, reading=(
            "REPRODUCIBLE" if f <= IDENTICAL_FORCE and c["metrics"]["energy_Ry"] <= IDENTICAL_FORCE
            else "REPRODUCIBLE_AT_GATE_ONLY" if not c["gate_failures"] else "NOT_REPRODUCIBLE"))
    if "B_ethr" in arms:
        b = arms["B_ethr"]["evaluations"]
        per_eval = [compare(control[k], b[k - 1]) for k in (1, 2) if k - 1 < len(b)]
        identical = bool(per_eval) and per_eval[0]["metrics"]["force_Ry_bohr"] <= IDENTICAL_FORCE
        passes = len(per_eval) == 2 and not any(c["gate_failures"] for c in per_eval)
        complete = len(per_eval) == 2
        out["R2_startup_threshold"] = {
            "control_eval2_vs_B": per_eval[0] if per_eval else None,
            "control_eval3_vs_B": per_eval[1] if len(per_eval) > 1 else None,
            "B_vs_A_eval2": compare(arms["A_replay"]["evaluations"][0], b[0]) if "A_replay" in arms else None,
            "reading": ("INCOMPLETE" if not complete
                        else "ETHR_RESTORES_IDENTICAL_PATH" if identical and passes
                        else "ETHR_RESTORES_REGISTERED_CONTINUITY" if passes else "ETHR_INSUFFICIENT")}
    ladder = [arms[n]["evaluations"][0] for n in ("C1_warm_1e-6", "C2_warm_1e-8", "C3_warm_1e-10") if n in arms]
    if len(ladder) == 3:
        reference = ladder[2]
        precision = compare(ladder[1], reference)["metrics"]["force_Ry_bohr"]
        errors = {"control_eval2": compare(control[1], reference),
                  "resumed_eval2": compare(resumed[0], reference),
                  "C1_1e-6": compare(ladder[0], reference),
                  "C2_1e-8": compare(ladder[1], reference)}
        if "B_ethr" in arms:
            errors["B_eval2"] = compare(arms["B_ethr"]["evaluations"][0], reference)
        precise = max(e["metrics"]["force_Ry_bohr"] for k, e in errors.items() if k in ("control_eval2", "resumed_eval2"))
        out["R3_force_precision"] = {
            "reference": "C3_warm_1e-10", "reference_summary": summary(reference),
            "reference_capped": reference["status"] == "CAPPED_UNCONVERGED",
            "rung_status": [rung["status"] for rung in ladder],
            "reference_precision_bound_Ry_bohr": precision,
            "errors_vs_reference": errors,
            "reading": ("UNRESOLVED_REFERENCE" if precision > GATE["force_Ry_bohr"] / 2
                        else "CONV_THR_1e-6_BELOW_GATE_PRECISION" if precise > GATE["force_Ry_bohr"]
                        else "CONV_THR_1e-6_WITHIN_GATE_PRECISION")}
        out["R4_scf_path_equivalence"] = dict(compare(resumed[0], ladder[0]), reading=(
            "SCF_PATH_EQUALS_RESTART_PATH" if compare(resumed[0], ladder[0])["metrics"]["force_Ry_bohr"] <= IDENTICAL_FORCE
            else "SCF_PATH_DIFFERS_FROM_RESTART_PATH"))
    fresh = [arms[n]["evaluations"][0] for n in ("D1_fresh_1e-8", "D2_fresh_1e-10") if n in arms]
    if len(fresh) == 2 and len(ladder) == 3:
        c = compare(ladder[2], fresh[1])
        resolved = c["max_hubbard_trace_delta"] is not None and c["total_magnetization_delta"] is not None
        same = (resolved and c["metrics"]["force_Ry_bohr"] <= GATE["force_Ry_bohr"]
                and c["max_hubbard_trace_delta"] <= STATE_TRACE
                and c["total_magnetization_delta"] <= STATE_MAGNETIZATION)
        out["R5_basin"] = dict(c, fresh_summary=summary(fresh[1]),
                               capped=[ladder[2]["status"] == "CAPPED_UNCONVERGED", fresh[1]["status"] == "CAPPED_UNCONVERGED"],
                               reading=("SAME_ELECTRONIC_STATE" if same else "DISTINCT_OR_UNRESOLVED_STATE"))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial", type=Path, required=True, help="mirrored trial_results directory")
    parser.add_argument("--runs", type=Path, help="mirrored diagnostic runs directory")
    parser.add_argument("--groups", type=Path, help="mirrored group receipts directory (call status)")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    xml = "outdir/slab_c5low__pa_boundary.save/data-file-schema.xml"
    trial = {"control": parse_arm(args.trial / "control", args.trial / "control" / xml),
             "resumed": parse_arm(args.trial / "resumed", args.trial / "resumed/checkpoint_copy" / xml)}
    status = {}
    if args.groups:
        for receipt in sorted(args.groups.glob("*/group_receipt.json")):
            for call in json.loads(receipt.read_text(encoding="utf-8"))["calls"]:
                status[call["name"]] = call.get("status")
    parsed, excluded = {}, {}
    if args.runs:
        for directory in sorted(p for p in args.runs.iterdir() if (p / "stdout.log").exists()):
            if args.groups and status.get(directory.name) != "COMPLETED":
                excluded[directory.name] = "controller status " + str(status.get(directory.name))
                continue
            try:
                parsed[directory.name] = parse_arm(directory, directory / xml)
            except (OSError, ValueError, StopIteration, KeyError, ET.ParseError) as exc:
                excluded[directory.name] = "parse error: " + repr(exc)
    arms = {k: v for k, v in parsed.items() if v["start"]["valid"]}
    excluded.update({k: "invalid start: " + json.dumps(v["start"]) for k, v in parsed.items() if not v["start"]["valid"]})
    result = {"schema": "pa-fixed-geometry-readout-v1", "gate": GATE,
              "trial_check": compare(trial["control"]["evaluations"][1], trial["resumed"]["evaluations"][0]),
              "controller_status": status, "excluded_arms": excluded,
              "start_checks": {k: v["start"] for k, v in parsed.items()},
              "arms": {k: [summary(e) for e in v["evaluations"]] for k, v in arms.items()},
              "readings": readings(arms, trial)}
    args.out.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"trial_check": result["trial_check"]["max_force_component"],
                      "readings": {k: v.get("reading") for k, v in result["readings"].items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
