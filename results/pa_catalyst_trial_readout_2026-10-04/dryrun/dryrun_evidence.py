"""Numerical evidence behind the pass of each internal read_qe_arm check on the real control output.

Re-derives the quantities the adapter compares (log vs XML energies, masked forces, logged proposal geometries,
fixed-coordinate drift, first-evaluation geometry) with the scratch patched adapter's own helpers, so each
adapter line range in the report has the measured margin next to it.  Read-only; writes only the new JSON.
Usage: python -B dryrun_evidence.py OUT.json
"""
import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SCRATCH = HERE / "scratch"
MIRROR = HERE.parent / "mirror" / "trial_results"
ARM = MIRROR / "control"
PREFIX = "slab_c5low__pa_boundary"
XML = ARM / "outdir" / (PREFIX + ".save") / "data-file-schema.xml"
sys.path.insert(0, str(SCRATCH))
spec = importlib.util.spec_from_file_location("pa_qe_adapter_patched", str(SCRATCH / "pa_qe_adapter.py"))
ad = importlib.util.module_from_spec(spec)
sys.modules["pa_qe_adapter_patched"] = ad
spec.loader.exec_module(ad)


def main(out):
    text = (ARM / "stdout.log").read_text(encoding="utf-8", errors="replace")
    deck = ad.parse_deck(ARM / "input.in")
    root = ET.parse(str(XML)).getroot()
    steps = [n for n in root if ad._tag(n) == "step"]
    ranges = ad._xml_source_ranges(XML.read_text(encoding="utf-8"), {"path": str(XML), "sha256": "x"}, "step")
    evals = [ad._xml_evaluation(n, deck, r) for n, r in zip(steps, ranges)]
    output = next(c for c in root if ad._tag(c) == "output")
    proposal = ad._xml_geometry(output, deck)
    nat = deck["nat"]
    energies = [ad._number(v) for v in re.findall(r"(?m)^\s*!\s+total energy\s*=\s*(" + ad.NUM + r")\s+Ry\s*$", text)]
    ev = {"evaluated_steps_in_xml": len(evals), "log_total_energies_Ry": energies,
          "xml_total_energies_Ry": [e["energy_Ry"] for e in evals],
          "max_abs_log_minus_xml_energy_Ry": max(abs(a - b["energy_Ry"]) for a, b in zip(energies, evals)),
          "adapter_energy_bound_Ry": 5.1e-8}
    markers = list(re.finditer(r"Forces acting on atoms \(cartesian axes, Ry/au\):", text))
    diffs, row_counts = [], []
    for i, (m, e) in enumerate(zip(markers, evals)):
        end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
        rows = list(re.finditer(r"(?m)^\s*atom\s+(\d+)\s+type\s+(\d+)\s+force\s*=\s*(" + ad.NUM + r")\s+(" + ad.NUM + r")\s+(" + ad.NUM + r")\s*$", text[m.end():end]))
        row_counts.append(len(rows))
        masked = [[ad._number(v.group(j + 3)) * flag for j, flag in enumerate(flags)] for v, flags in zip(rows, deck["qe_if_pos"])]
        diffs.append(ad._matrix_delta(masked, e["forces_Ry_bohr"]))
    ev.update(force_blocks=len(markers), rows_per_block=row_counts, max_abs_masked_log_minus_xml_force_Ry_bohr=diffs,
              adapter_force_bound=5.1e-8)
    pos = list(re.finditer(r"(?mi)^\s*ATOMIC_POSITIONS\s*\((bohr|angstrom)\)\s*\n", text))
    logged = []
    for m in pos:
        rows = [row.split() for row in text[m.end():].splitlines()[:nat]]
        factor = 1 if m.group(1).lower() == "bohr" else 1 / ad.BOHR_ANGSTROM
        logged.append([[ad._number(v) * factor for v in row[1:4]] for row in rows])
    ev["logged_ATOMIC_POSITIONS_blocks"] = len(logged)
    ev["max_abs_logged_vs_next_xml_step_bohr"] = [ad._matrix_delta(logged[i - 1], evals[i]["geometry"]["positions"]) for i in range(1, len(evals))]
    ev["max_abs_last_logged_vs_xml_output_proposal_bohr"] = ad._matrix_delta(logged[-1], proposal["positions"])
    ev["max_abs_first_evaluation_vs_input_deck_geometry_bohr"] = ad._matrix_delta(evals[0]["geometry"]["positions"], deck["geometry"]["positions"])
    drift = 0.0
    for e in evals + [{"geometry": proposal}]:
        for actual, original, flags in zip(e["geometry"]["positions"], deck["geometry"]["positions"], deck["geometry"]["fixed_flags"]):
            drift = max([drift] + [abs(a - b) for a, b, f in zip(actual, original, flags) if f])
    ev["max_fixed_coordinate_drift_bohr"] = drift
    ev["fixed_flag_atoms_all_axes"] = sum(1 for flags in deck["geometry"]["fixed_flags"] if all(flags))
    ev["moved_proposal_vs_third_evaluation_max_bohr"] = ad._matrix_delta(proposal["positions"], evals[-1]["geometry"]["positions"])
    ev["scf_cycles_log"] = [int(v) for v in re.findall(r"number of scf cycles\s*=\s*(\d+)", text)]
    ev["bfgs_counts_log"] = [int(v) for v in re.findall(r"number of bfgs steps\s*=\s*(\d+)", text)]
    ev["convergence_threshold_lines"] = re.findall(r"convergence threshold\s*=\s*(\S+)", text)
    ev["exit_status_xml"] = ad._integer(ad._number(next(c for c in root if ad._tag(c) == "exit_status").text), "x")
    ev["stderr_bytes"] = (ARM / "stderr.log").stat().st_size
    ev["stderr_distinct_lines"] = sorted(set(l for l in (ARM / "stderr.log").read_text(encoding="utf-8").splitlines() if l.strip()))
    ev["FAILURE_regex_hits_in_stdout_plus_stderr"] = [m.group(0) for m in ad.FAILURE.finditer(text + (ARM / "stderr.log").read_text(encoding="utf-8"))]
    ev["maximum_time_or_bfgs_converged_markers"] = {"Maximum CPU time": "Maximum CPU time" in text, "Maximum wall time": "Maximum wall time" in text,
                                                    "bfgs converged in": "bfgs converged in" in text.lower(),
                                                    "maximum number of steps": "maximum number of steps" in text.lower()}
    ev["stopped_by_user_request"] = ad.STOP in text
    ev["job_done"] = "JOB DONE." in text
    ev["pwscf_banners"] = re.findall(r"Program PWSCF v\.([0-9.]+) starts", text)
    ev["mpi_header_lines"] = [l.strip() for l in text.splitlines() if re.search(r"Number of MPI processes|Threads/MPI process|K-points division|R & G space division|ELPA distributed-memory", l)]
    with open(out, "x", encoding="utf-8") as stream:
        stream.write(json.dumps(ev, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: v for k, v in ev.items() if k not in ("log_total_energies_Ry", "xml_total_energies_Ry")}, indent=1, default=str)[:3500])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
