"""Replay the readout's raw layers over the retained real tiny H2 run (job 21024848).

Read-only.  Shows what the per-call table, SU arithmetic, mirror pin check and adapter
re-derivation report on genuine QE 7.5 output.  It is a plumbing replay of an old, already
read-out job and carries no catalyst result and no verdict.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import readout_trial as R  # noqa: E402

FT = REPO / "results/s2_2026-09-25/full_text/sequential_2026-10-03"
RAW = FT / "pa_tiny_raw"
TINY = RAW / "tiny_results"
OFFLINE_PROBE_TOLERANCE_CITE = ("docs/research/pa-offline-restart-probe-2026-10-03.md", 137,
                                "Proposed tiny-test tolerances, not production threshold changes")
SERIAL = {key: 1 for key in ("nprocs", "nthreads", "ntasks", "nbgrp", "npool", "ndiag")}


def main(out_dir):
    trial, adapter = R.load_modules(REPO)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=False)
    report = {"scope": "TINY_H2_PLUMBING_REPLAY_ONLY", "job_id": "21024848", "qe_executed": False,
              "production_accepted": False, "catalyst_result": False}
    mirror = json.loads((FT / "pa_tiny_mirror_receipt.json").read_text(encoding="utf-8"))
    comparison = R.compare_inventories(R.inventory_dir(RAW), R.normalize_remote_inventory(mirror))
    report["mirror_vs_retained_remote_pins"] = {k: comparison[k] for k in ("remote_rows", "matched", "size_only_matched",
                                                                         "mismatched", "not_mirrored")}
    accounting = json.loads(json.loads((FT / "pa_tiny_final_accounting.json").read_text(encoding="utf-8"))["stdout"])
    sched = R.parse_sacct(accounting["accounting"]["stdout"], "21024848")
    jobsu = R.parse_jobsu(accounting["usage"]["stdout"])
    su = R.charged_su(sched)
    report["scheduler"] = {"state": sched["state_raw"], "exit": "%s:%s" % (sched["exit_code"], sched["exit_signal"]),
                           "elapsed_s": sched["elapsed_s"], "billing": sched["alloc_tres"].get("billing"),
                           "charged_cpu_su_exact": su, "cputimeraw_su": sched["cputime_raw_s"] / 3600.0,
                           "jobsu_reported": jobsu["cpu_su_job"], "jobsu_minus_exact": jobsu["cpu_su_job"] - su,
                           "note": "scheduler FAILED 2:0 and scientific pass coexist in this historical job (OQ7)"}
    arms = {}
    for arm, scratch in (("continuous", "scratch"), ("candidate-stop", "scratch"), ("negative-fresh", "scratch"), ("resumed", "scratch")):
        text = (TINY / arm / "stdout.log").read_text(encoding="utf-8")
        out = R.summarize_stdout(text, trial)
        xml = R.summarize_xml(TINY / arm / scratch / "h2_probe.save/data-file-schema.xml")
        receipt = json.loads((TINY / arm / "receipt.json").read_text(encoding="utf-8"))
        arms[arm] = {"stdout": out, "xml": xml, "process_elapsed_s": receipt.get("elapsed_seconds"),
                     "returncode": receipt.get("returncode"), "timed_out": receipt.get("timed_out")}
    report["arms"] = arms
    directory = TINY / "candidate-stop"
    expected = adapter.parse_deck(directory / "input.in")
    pseudo = directory / "H.pbe-rrkjus_psl.1.0.0.UPF"
    expected["upf_pins"] = {pseudo.name: "27f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962"}
    logged = "/anvil/projects/x-che260157/sts_pa_probe_2026-10-03/tiny_results/candidate-stop/" + pseudo.name
    paths = {"input": directory / "input.in", "stdout": directory / "stdout.log", "stderr": directory / "stderr.log",
             "xml": directory / "scratch/h2_probe.save/data-file-schema.xml", "process_receipt": directory / "receipt.json"}
    rederived = R.rederive_arm(paths, adapter=adapter, expected_settings=expected, expected_parallel=SERIAL,
                               expected_exit="clean_stop", expected_evaluations=1, upf_path_map={logged: str(pseudo)})
    report["candidate_stop_adapter_rederivation"] = {
        "ok": rederived["ok"], "error": rederived["error"],
        "scf_counts": rederived["parsed"]["scf_counts"] if rederived["ok"] else None,
        "optimizer_counts": rederived["parsed"]["optimizer_counts"] if rederived["ok"] else None,
        "xml_exit_status": rederived["parsed"]["xml_exit_status"] if rederived["ok"] else None,
        "energy_Ry": rederived["parsed"]["evaluations"][0]["energy_Ry"] if rederived["ok"] else None}
    split = arms["candidate-stop"]["xml"]["steps"] + arms["resumed"]["xml"]["steps"]
    control = arms["continuous"]["xml"]["steps"]
    deltas = [abs(a["etot_Ry"] - b["etot_Ry"]) for a, b in zip(control, split)]
    retained = json.loads((FT / "pa_tiny_raw_readout.json").read_text(encoding="utf-8"))
    report["energy_trajectory_comparison"] = {
        "ordered_evaluations": [len(control), len(split)], "max_abs_energy_difference_Ry": max(deltas),
        "retained_pa_tiny_raw_readout_max_energy_Ry": retained["max_differences"]["energy_Ry"],
        "registered_tiny_energy_tolerance_Ry": retained["tolerances"]["energy_Ry"],
        "tolerance_cite": "%s:%d \"%s\"" % OFFLINE_PROBE_TOLERANCE_CITE,
        "energy_only_within_tolerance": max(deltas) <= retained["tolerances"]["energy_Ry"],
        "note": "positions and forces are compared by the frozen adapter (pa_tiny_raw_readout.py record), not re-derived here"}
    (out_dir / "tiny_replay_readout.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    rows = []
    for name, arm in arms.items():
        s, x = arm["stdout"], arm["xml"]
        rows.append([name, x["exit_status"], "%d/%d" % (sum(1 for t in x["steps"] if t["converged"]), len(x["steps"])),
                     s["scf_cycles"], s["bfgs_counts"][:1], s["startup_history_deleted"], s["stopped_by_user"],
                     s["wall_seconds"], arm["process_elapsed_s"], ", ".join("%.8f" % t["etot_Ry"] for t in x["steps"][:3]) + " ..."])
    md = ["# Tiny H2 replay of the readout layers (job 21024848)", "",
          "Plumbing replay only: no catalyst result, no verdict, no new QE run.", "",
          R._table(["arm", "XML exit", "SCF converged", "SCF cycles", "first BFGS count", "startup .bfgs deleted",
                    "user stop", "PWSCF WALL s", "process s", "energies Ry (first 3)"], rows), "",
          "Scheduler: %s" % json.dumps(report["scheduler"], sort_keys=True), "",
          "Mirror vs retained remote pins: %s" % json.dumps(report["mirror_vs_retained_remote_pins"]), "",
          "Adapter re-derivation of candidate-stop: %s" % json.dumps(report["candidate_stop_adapter_rederivation"], sort_keys=True), "",
          "Energy trajectory: %s" % json.dumps(report["energy_trajectory_comparison"], sort_keys=True), ""]
    (out_dir / "tiny_replay_readout.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE / "tiny_replay_output")
