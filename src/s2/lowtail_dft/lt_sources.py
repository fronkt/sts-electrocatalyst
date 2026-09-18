"""File-read sources: census site records and the acceptance registry of banked HEA outputs.

Acceptance is never re-decided here. Each banked pw.x output under runs/hea receives the
status its own readout recorded (winner, pilot, follow-up, numerical, IEEE replacement,
sensitivity, convergence-probe and setup diagnostics), with the readout path and hash.
An output no readout names is reported UNIDENTIFIED and never used.
"""
from __future__ import annotations

import re
from pathlib import Path

from lt_common import ROOT, evidence, read_json, rel, sha256_file

READOUTS = dict(
    winner=ROOT / "results/hea_continuation_2026-09-11/winner_readout.json",
    winner_spec=ROOT / "results/hea_winner_2026-09-10/launch_spec.json",
    pilot=ROOT / "results/hea_pilot_2026-09-07/completion_readout.json",
    followup=ROOT / "results/hea_followup_2026-09-07/completion_readout.json",
    followup_spec=ROOT / "results/hea_followup_2026-09-07/launch_spec.json",
    numerical=ROOT / "results/hea_numerical_2026-09-08/status_2026-09-09_2228/readout.json",
    replacement=ROOT / "results/hea_sensitivity_2026-09-09/status_2026-09-10_verified/atomic_replacement_readout.json",
    sensitivity=ROOT / "results/hea_sensitivity_2026-09-09/status_2026-09-10_verified/readout.json",
    final=ROOT / "results/hea_readout_2026-09-17/readout.json",
)
HEA_RUNS = ROOT / "runs" / "hea"
LEADER_JOB = re.compile(r"^(hc|hn|hs|hd|hp|hi)__leader_(builder|pull2\.10)__(atomic|ortho)__(.+)$")
WINNER_JOB = re.compile(r"^g_([0-9a-f]{64})__(atomic|ortho)$")


# --------------------------------------------------------------------------- census
def census_site(path, seed: int, site: int) -> dict:
    """The unique per-site record and its decoration slab from a screen-diagnostic-v1 result."""
    doc = read_json(path)
    if doc.get("status") != "complete":
        raise ValueError(f"{path}: census result is not complete")
    rows = [r for r in doc["results"] if r.get("status") == "evaluated"]
    if len(rows) != 1:
        raise ValueError(f"{path}: expected one evaluated candidate")
    row = rows[0]["row"]
    sites = [p for p in row["per_site_records"] if p["seed"] == seed and p["site_index"] == site]
    decorations = [d for d in row["decoration_records"] if d["seed"] == seed]
    if len(sites) != 1 or len(decorations) != 1:
        raise ValueError(f"{path}: seed {seed} site {site} is not unique")
    return dict(path=path, formula=row["formula"], model=doc["manifest"]["model"],
                environment=doc.get("environment"), site=sites[0], slab=decorations[0]["relaxed_slab"],
                gas=row["gas_reference_records"])


# --------------------------------------------------------------------------- registry
def _output_for(job: str) -> Path | None:
    hits = sorted(p for p in HEA_RUNS.rglob(f"{job}.out") if p.is_file())
    return hits[0] if len(hits) == 1 else None


def _entry(job, status, reasons, readout_key, recorded_output_sha=None, extra=None, output=None):
    out = Path(output) if output is not None else _output_for(job)
    stem = out.name[:-4] if out is not None else job
    run_in = out.with_name(stem + ".run.in") if out is not None else None
    frozen_in = out.with_name(stem + ".in") if out is not None else None
    entry = dict(job=job, status=status, reasons=list(reasons or []),
                 readout=rel(READOUTS[readout_key]) if readout_key in READOUTS else readout_key,
                 output=rel(out) if out is not None else None,
                 input=(rel(run_in) if run_in is not None and run_in.exists()
                        else rel(frozen_in) if frozen_in is not None and frozen_in.exists() else None),
                 recorded_output_sha256=recorded_output_sha)
    if out is not None:
        actual = sha256_file(out)
        entry["output_sha256"] = actual
        if recorded_output_sha is not None and recorded_output_sha != actual:
            entry["status"] = "REJECTED"
            entry["reasons"].append("output bytes differ from the readout's recorded sha256")
    if extra:
        entry.update(extra)
    return entry


def _qc_output_sha(job: str):
    out = _output_for(job)
    if out is None:
        return None
    qc = out.with_name(job + ".qc.json")
    if not qc.exists():
        return None
    doc = read_json(qc)
    return (doc.get("output") or {}).get("sha256_bytes")


def final_entries() -> list:
    """The final 22 physical outputs; four pilot OOH aliases reuse panel evidence.

    Path-scoped job IDs are required because the two pilot chains use identical
    basenames. Acceptance comes from the final readout; accepted output/input bytes
    must also match the QC receipt made when that calculation completed.
    """
    final = read_json(READOUTS["final"])
    entries = {}
    for section in ("panel", "pilot"):
        for label, leg in final[section]["legs"].items():
            alias = re.fullmatch(r"(.+) \(reused (branch_panel/.+)\)", label)
            key = (alias.group(2) if alias else
                   ("branch_panel/" if section == "panel" else "pilot_retained/") + label)
            if alias:
                if key not in entries or entries[key]["readout_status"] != leg["status"]:
                    raise ValueError(f"{label}: reused leg missing or status differs from physical output")
                entries[key]["readout_aliases"].append(label)
                continue
            output = HEA_RUNS / (key + ".out")
            qc_path = output.with_name(output.name[:-4] + ".qc.json")
            qc = read_json(qc_path)
            accepted = leg["status"] == "CONVERGED"
            reasons = list(leg.get("severe_failures") or [])
            if not accepted:
                reasons.insert(0, f"final HEA readout status {leg['status']}: {qc.get('reason', 'no usable SCF')}")
            entry = _entry(key, "ACCEPTED" if accepted else leg["status"], reasons, "final",
                           qc.get("output_sha256"), output=output,
                           extra=dict(series="final", variant="baseline", projector=key.rsplit("__", 1)[1],
                                      family=key.rsplit("/", 1)[0], state=output.name[:-4].rsplit("__", 1)[0],
                                      readout_status=leg["status"], readout_aliases=[], qc=evidence(qc_path)))
            if accepted:
                if not qc.get("output_sha256"):
                    entry["status"] = "REJECTED"
                    entry["reasons"].append("accepted output has no recorded QC output hash")
                if entry["input"] is None or sha256_file(ROOT / entry["input"]) != qc.get("runtime_sha256"):
                    entry["status"] = "REJECTED"
                    entry["reasons"].append("runtime input bytes differ from the completion QC receipt")
            entries[key] = entry
    return list(entries.values())


def registry() -> dict:
    entries = {}

    def put(entry):
        if entry["job"] in entries:
            raise ValueError(f"job {entry['job']} classified twice")
        entries[entry["job"]] = entry

    winner = read_json(READOUTS["winner"])
    for e in winner["endpoints"]:
        put(_entry(e["job"], "ACCEPTED" if e["status"] == "ACCEPTED" else "REJECTED", e.get("reasons"), "winner",
                   e["files"]["output"]["sha256_bytes"],
                   dict(family="winner_Ni31Cr29Cu5Mn35_s1_site0", state=e["state"], projector=e["projector"],
                        variant="baseline")))
    pilot = read_json(READOUTS["pilot"])
    for j in pilot["jobs"]:
        put(_entry(j["job"], "ACCEPTED" if j["status"] == "VALID_SCF" else "REJECTED", j.get("reasons"), "pilot",
                   j["output"]["sha256_bytes"]))
    followup = read_json(READOUTS["followup"])
    for e in followup["endpoints"]:
        if e.get("source") != "followup":
            continue
        put(_entry(e["job"], "ACCEPTED", [], "followup", _qc_output_sha(e["job"])))
    spec_jobs = [j["job"] for j in read_json(READOUTS["followup_spec"])["jobs"]]
    for task in followup["failed_tasks"]:
        put(_entry(spec_jobs[task - 1], "REJECTED", ["SCF nonconvergence at max_seconds (completion_readout failed_tasks)"],
                   "followup"))
    numerical = read_json(READOUTS["numerical"])
    for e in numerical["endpoints"]:
        put(_entry(e["job"], e["status"], e.get("reasons"), "numerical",
                   (e.get("files") or {}).get("output", {}).get("sha256_bytes")))
    replacement = read_json(READOUTS["replacement"])
    b = replacement["builder"]
    put(_entry(b["job"], b["status"], b.get("reasons"), "replacement", b["files"]["output"]["sha256_bytes"],
               dict(pair_partner=replacement["pull"]["job"])))
    sensitivity = read_json(READOUTS["sensitivity"])
    for e in sensitivity["endpoints"]:
        put(_entry(e["job"], e["status"], e.get("reasons"), "sensitivity",
                   (e.get("files") or {}).get("output", {}).get("sha256_bytes")))
    for probe in sorted((HEA_RUNS / "convergence_probe_2026-09-10").glob("*.probe.json")):
        doc = read_json(probe)
        put(_entry(doc["job"], doc["scientific_status"], [doc["diagnostic_status"]] + list(doc.get("qc_reasons") or []),
                   rel(probe)))
    for diag in sorted((HEA_RUNS / "ieee_smearing_2026-09-10").glob("*.diagnostic.json")):
        doc = read_json(diag)
        put(_entry(doc["job"], doc["new_endpoint_status"], [doc["diagnostic_status"]] + list(doc.get("scf_reasons") or []),
                   rel(diag)))
    for diag in sorted((HEA_RUNS / "ieee_init_2026-09-11").glob("*.diagnostic.json")):
        doc = read_json(diag)
        put(_entry(doc["job"], "NO_SCF", [doc["diagnostic_status"], doc["scope"]], rel(diag)))
    for entry in final_entries():
        put(entry)

    # Every banked pw.x output must be classified exactly once.
    unidentified = []
    classified_paths = [e["output"] for e in entries.values() if e["output"] is not None]
    if len(classified_paths) != len(set(classified_paths)):
        raise ValueError("a physical output was classified twice")
    for out in sorted(HEA_RUNS.rglob("*.out")):
        if out.name.endswith(".projwfc.out"):
            continue
        job = out.name[:-4]
        if rel(out) not in classified_paths:
            unidentified.append(dict(job=job, status="UNIDENTIFIED", output=rel(out),
                                     reasons=["no readout names this output"]))
    for job, entry in entries.items():
        m = LEADER_JOB.match(job)
        if m:
            entry.setdefault("family", "leader_Ni31Cr29Cu5Mn35_s0_site0_OOH")
            entry.setdefault("state", f"OOH_{m.group(2)}")
            entry.setdefault("projector", m.group(3))
            entry.setdefault("variant", m.group(4))
            entry.setdefault("series", m.group(1))
    readout_evidence = {k: evidence(v) for k, v in READOUTS.items()}
    return dict(entries=[entries[k] for k in sorted(entries)], unidentified=unidentified,
                readouts=readout_evidence)
