"""Cost envelope of the corrected one-boundary re-test (arithmetic only; nothing is run or measured here).

Inputs: the measured control call of job 21034683 and the pre-run estimates of
docs/research/pa-catalyst-trial-readout-2026-10-04.md section 8; the September 72-atom fresh-SCF logs for the stall
rate; and a count of how often the registered controller hashes the 15 GB checkpoint.
Writes cost_envelope.json (refuses to overwrite).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "cost_envelope.json"
if TARGET.exists():
    raise SystemExit("cost_envelope.json exists; refusing to overwrite")

BILLING = 128
SU_PER_SECOND = BILLING / 3600.0
CAP_SU, CAP_SECONDS = 2048, 57600
BALANCE_AFTER_FIRST_JOB = 36775.4  # mybalance after job 21034683 (readout scheduler/mybalance.txt)


def su(seconds):
    return round(seconds * SU_PER_SECOND, 1)


measured = {"control_process_seconds": 2883.94, "control_process_su": su(2883.94),
            "job_elapsed_seconds": 2893, "job_charged_su": round(2893 * BILLING / 3600, 4),
            "per_second_su": round(SU_PER_SECOND, 5)}

calls = {  # seconds; basis in the readout section 8
    "control": {"seconds": 2884, "basis": "measured, job 21034683"},
    "candidate": {"seconds": 580, "basis": "measured 478.8 s to SCF 1 plus forces, start-up and teardown"},
    "fresh_converged": {"seconds": {"low": 3385, "mean": 3670, "high": 4680},
                        "basis": "September converged fresh SCFs at 8.08e-8 Ry (15 of 21 logs; CPU 3,329-4,657 s); the registered 1e-6 Ry target is looser"},
    "fresh_stalled_and_killed": {"seconds": 6420, "basis": "supervisor kill at SCF iteration 127; 6 of 21 September fresh SCFs stalled (CPU 6,024-6,457 s)"},
    "resumed": {"seconds": 2440, "basis": "measured control evaluations 2 and 3 plus restart start-up"},
    "negative": {"seconds": 2884, "basis": "taken equal to the control"},
    "reseed": {"seconds": 600, "basis": "one evaluation, planning figure"},
}

# Hash passes over the 15 GB retained checkpoint, counted from the registered code (pa_catalyst_retest.py, pa_qe_adapter_v2.py):
# copy_checkpoint = inventory before (1) + copy_tree [inventory source, copy, inventory copy, inventory source] (3) + inventory after (1) = 5 passes + 1 copy
# run(): immutable copy (5) ; before_full (1) ; adapter before (1) ; after_full (1) ; adapter after (1) ; pre_resume_decision (1) ;
#        resumed arm copy (5) ; audit_consumption -> pre_resume_decision (1) ; negative arm copy (5) ; final inventory (1)
passes = {"candidate_immutable_copy": 5, "before_full": 1, "adapter_before": 1, "after_full": 1, "adapter_after": 1,
          "pre_resume_decision": 1, "resumed_copy": 5, "audit_consumption_decision": 1, "negative_copy": 5, "final": 1}
checkpoint_gb = 15.07
hash_passes = sum(passes.values())
copies = 3
hash_gb = hash_passes * checkpoint_gb
overhead = {"hash_passes": hash_passes, "hashed_gb": round(hash_gb, 1), "checkpoint_copies": copies,
            "copied_gb_each_read_and_write": checkpoint_gb,
            "assumed_throughput_gb_per_s": {"slow": 0.5, "fast": 1.5},
            "idle_seconds": {"fast": round(hash_gb / 1.5 + copies * checkpoint_gb / 1.0), "slow": round(hash_gb / 0.5 + copies * checkpoint_gb / 0.5)},
            "readout_allowance_seconds": 1800, "readout_allowance_su": su(1800),
            "status": "arithmetic from counted passes and an assumed range; not measured"}
overhead["idle_su"] = {k: su(v) for k, v in overhead["idle_seconds"].items()}

fresh = calls["fresh_converged"]["seconds"]
paths = {}
for label, fresh_seconds in (("resume_fresh_low", fresh["low"]), ("resume_fresh_mean", fresh["mean"]), ("resume_fresh_high", fresh["high"])):
    total = calls["control"]["seconds"] + calls["candidate"]["seconds"] + fresh_seconds + calls["resumed"]["seconds"] + calls["negative"]["seconds"]
    paths[label] = {"calls_seconds": total, "calls_su": su(total), "with_readout_allowance_su": su(total + 1800),
                    "with_counted_overhead_su": {k: su(total + v) for k, v in overhead["idle_seconds"].items()}}
hold = calls["control"]["seconds"] + calls["candidate"]["seconds"] + calls["fresh_stalled_and_killed"]["seconds"]
reseed = calls["control"]["seconds"] + calls["candidate"]["seconds"] + fresh["mean"] + calls["reseed"]["seconds"]
paths["hold_fresh_stalls"] = {"calls_seconds": hold, "calls_su": su(hold), "with_readout_allowance_su": su(hold + 600)}
paths["reseed"] = {"calls_seconds": reseed, "calls_su": su(reseed), "with_readout_allowance_su": su(reseed + 600)}
low = paths["reseed"]["calls_su"]
high = paths["resume_fresh_high"]["with_readout_allowance_su"]

cumulative = []
elapsed = 0
for name in ("control", "candidate", "fresh_converged_mean", "resumed", "negative"):
    seconds = {"control": 2884, "candidate": 580, "fresh_converged_mean": 3670, "resumed": 2440, "negative": 2884}[name]
    elapsed += seconds
    cumulative.append({"after_call": name, "cumulative_seconds": elapsed, "cumulative_su": su(elapsed)})

report = {
    "basis": "arithmetic; see the readout doc for provenance of each input",
    "measured_first_job": measured, "calls": calls, "checkpoint_hashing_and_copying": overhead, "paths": paths,
    "cumulative_charge_by_call_on_the_resume_path_su": cumulative,
    "range_su": {"floor_reseed_path": low, "ceiling_resume_high_with_allowance": high,
                 "approved_cap_su": CAP_SU, "fraction_of_cap_at_ceiling": round(high / CAP_SU, 3)},
    "wall_clock": {"resume_mean_seconds": paths["resume_fresh_mean"]["calls_seconds"], "cap_seconds": CAP_SECONDS,
                   "fraction_of_wall_cap": round(paths["resume_fresh_mean"]["calls_seconds"] / CAP_SECONDS, 3)},
    "balance_projection_su": {"balance_after_first_job": BALANCE_AFTER_FIRST_JOB,
                              "after_floor": round(BALANCE_AFTER_FIRST_JOB - low, 1), "after_ceiling": round(BALANCE_AFTER_FIRST_JOB - high, 1),
                              "worst_case_at_cap": round(BALANCE_AFTER_FIRST_JOB - CAP_SU, 1),
                              "note": "live mybalance still to be read immediately before submission"},
    "stall_rate_september_fresh_scf": {"stalled": 6, "of": 21, "note": "different geometries from the registered evaluated state; a base rate, not a prediction"},
    "new_preflight_replay_cost": "reads 3.4 MB of fixtures and parses 0.9 MB of real output on the login or compute node: seconds, no QE",
}
TARGET.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
print(json.dumps({"range_su": report["range_su"], "paths": {k: v["calls_su"] for k, v in paths.items()}, "overhead": overhead["idle_su"],
                  "hash_passes": hash_passes}, indent=1))
