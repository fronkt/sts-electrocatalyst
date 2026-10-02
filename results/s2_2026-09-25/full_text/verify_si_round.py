"""Structural checks for the completed SI round; no eligibility judgements.

Run before collection with --snapshot, then after rebuild without it.
Local source files stay local; the report records hashes, not article text.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from ft_screen import check

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "reconcile" / "si_round_verification.json"
SNAPSHOT = HERE / "si_read" / "verification_baseline.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def state():
    return list(csv.DictReader((HERE / "reconcile" / "current_state.csv").open(encoding="utf-8")))


def sensitivity(rows):
    return [{k: r[k] for k in ("screen_id", "v3_decision", "v3_final", "v4_decision", "v4_final")} for r in rows]


def recovery_validation(st, recoveries, dates, versions):
    """Check shared recovery evidence and its exact current-state projection."""
    from verify_evidence_recovery import rebuilt_errors, validate_recovery_evidence

    errors, hashes, reads = validate_recovery_evidence(recoveries)
    by_id = {}
    for row in st:
        by_id.setdefault(row["screen_id"], []).append(row)
    for sid, ruling in recoveries.items():
        rows = by_id.get(sid, [])
        if len(rows) != 1:
            errors.append([sid, "reviewed recovery must occur exactly once in current state"])
        else:
            errors.extend([sid, error] for error in rebuilt_errors(rows[0], ruling, dates, versions))
    return errors, hashes, reads


def main(snapshot=False, require_audits=False):
    st = state()
    if snapshot:
        if SNAPSHOT.exists():
            raise RuntimeError("Baseline already exists; preserve it")
        SNAPSHOT.write_text(json.dumps(sensitivity(st), indent=1) + "\n", encoding="utf-8")
        print("Sensitivity baseline:", len(st), "records")
        return
    errors, seen, counts, inputs = [], {}, {}, {}
    from recovery_state import recovery_decisions
    recoveries = recovery_decisions()
    dates = {r["screen_id"]: r for r in csv.DictReader((HERE / "reconcile" / "date_check.csv").open(encoding="utf-8"))}
    versions = {r["screen_id"]: r for r in csv.DictReader((HERE / "reconcile" / "version_groups.csv").open(encoding="utf-8"))}
    recovery_errors, recovery_hashes, recovery_reads = recovery_validation(st, recoveries, dates, versions)
    errors.extend(recovery_errors)
    for name in ("pass_1", "pass_2", "third"):
        d = HERE / "si_read" / name
        plan = json.loads((d / "plan.json").read_text(encoding="utf-8"))
        ids, batch_outputs = [], []
        for batch, meta in plan["batches"].items():
            ip = d / "batches" / (batch + ".in.jsonl")
            op = d / "batches" / (batch + ".out.jsonl")
            problems = check(ip, op)
            if problems:
                errors.append([name, batch, problems])
            if digest(ip) != meta["sha256"]:
                errors.append([name, batch, "input hash mismatch"])
            rows = jsonl(ip)
            if [r["screen_id"] for r in rows] != meta["records"]:
                errors.append([name, batch, "plan order mismatch"])
            ids.extend(meta["records"])
            batch_outputs.extend(jsonl(op))
            for r in rows:
                inputs[r["screen_id"]] = r
        if len(ids) != len(set(ids)):
            errors.append([name, "duplicate records"])
        seen[name] = set(ids)
        aggregate = HERE / "si_read" / ("third_read.jsonl" if name == "third" else name + ".jsonl")
        aggregate_rows = jsonl(aggregate)
        if len({r["screen_id"] for r in aggregate_rows}) != len(aggregate_rows):
            errors.append([name, "duplicate aggregate rows"])
        if {r["screen_id"]: r for r in aggregate_rows} != {r["screen_id"]: r for r in batch_outputs}:
            errors.append([name, "aggregate differs from archived batch outputs"])
        counts[name] = {"batches": len(plan["batches"]), "records": len(ids)}
        if plan["instructions_sha256"] != digest(HERE / "eligibility_instructions.md"):
            errors.append([name, "instructions hash mismatch"])
    queue = list(csv.DictReader((HERE / "si_read" / "queue.csv").open(encoding="utf-8")))
    required = {r["screen_id"] for r in queue if r["lane"] == "THIRD_READ"}
    if seen["third"] != required:
        errors.append(["third coverage", sorted(required - seen["third"]), sorted(seen["third"] - required)])
    if seen["pass_1"] != seen["pass_2"] or seen["pass_1"] != {r["screen_id"] for r in queue}:
        errors.append(["pass coverage"])
    if json.loads(SNAPSHOT.read_text(encoding="utf-8")) != sensitivity(st):
        errors.append(["v3/v4 sensitivity changed"])
    checklist = list(csv.DictReader((HERE / "si_checklist.csv").open(encoding="utf-8")))
    from retrieve_si_public import has_document
    if len({r["screen_id"] for r in checklist}) != len(checklist):
        errors.append(["duplicate checklist rows"])
    if any(has_document(r["screen_id"]) for r in checklist):
        errors.append(["checklist includes a record with an SI document"])
    forced = {"S29721", "S10090", "S22807", "S26024"}
    expected_checklist = {r["screen_id"] for r in st
                          if (r["v5_final"] in ("NEEDS_SI", "UNRESOLVED") or r["screen_id"] in forced)
                          and not has_document(r["screen_id"])}
    if {r["screen_id"] for r in checklist} != expected_checklist:
        errors.append(["checklist coverage does not match current state"])
    from current_state import SI_VERIFY
    for r in st:
        if r["screen_id"] in SI_VERIFY and not r["v5_final"].startswith("collapsed") and r["v5_final"] != "UNRESOLVED":
            errors.append([r["screen_id"], "verification hold not applied"])
        if r["screen_id"] in SI_VERIFY and SI_VERIFY[r["screen_id"]].startswith("E6"):
            if any(r["v5_" + k] for k in ("eta_form", "eta_derivation", "eta_note")):
                errors.append([r["screen_id"], "E6 hold retained eta fields"])
    historical = json.loads((HERE / "si_read" / "outputs_before_adjudication.json").read_text(encoding="utf-8"))["sha256"]
    for path, expected_hash in historical.items():
        if digest(HERE / path) != expected_hash:
            errors.append([path, "historical output changed"])
    questions = {r["screen_id"] for r in jsonl(HERE / "si_read" / "third_read.jsonl") if r.get("entrant_question")}
    triage = (HERE / "reconcile" / "si_questions_triage.md").read_text(encoding="utf-8")
    triage_rows = re.findall(r"^\| ([RS]\d+) /[^|]*\| ([ABCD]),", triage, re.M)
    if len(triage_rows) != len(questions) or {sid for sid, _ in triage_rows} != questions:
        errors.append(["entrant-question triage coverage"])
    classes = {c: sum(kind == c for _, kind in triage_rows) for c in "ABCD"}
    target_file = HERE / "reconcile" / "si_verification_targets_2026-09-29.json"
    targets = json.loads(target_file.read_text(encoding="utf-8"))
    target_ids = set().union(*(set(targets[k]) for k in ("group1", "group2", "group3")))
    intake = list(csv.DictReader((HERE / "reconcile" / "si_verification_intake_2026-09-29.csv").open(encoding="utf-8")))
    expected_targets = {r["screen_id"] for r in intake if r["v5_final"] != r["v5_final_before_si"]} | {"S02105"}
    if target_ids != expected_targets:
        errors.append(["verification target list differs from reconstructed intake"])
    intake_by_id = {r["screen_id"]: r["v5_final"] for r in intake}
    final_by_id = {r["screen_id"]: r["v5_final"] for r in st}
    audit_rows = []
    audit_files = sorted((HERE / "reconcile").glob("si_verification_2026-09-29_*.jsonl"))
    for path in audit_files:
        file_rows = jsonl(path)
        if "economy" in path.name:
            for r in file_rows:
                if not r.get("review_mode"):
                    errors.append([r["screen_id"], "continuation audit review mode missing"])
        audit_rows.extend(file_rows)
    for r in audit_rows:
        if r["current_decision"] not in {intake_by_id[r["screen_id"]], final_by_id[r["screen_id"]]}:
            errors.append([r["screen_id"], "audit confuses raw/pre-SI disposition with merged final", r["current_decision"]])
    from current_state import si_adjudications
    adjudications = si_adjudications()
    unadjudicated = sorted({r["screen_id"] for r in audit_rows
                            if r["status"] == "CHALLENGE" and r["screen_id"] not in adjudications})
    if require_audits and unadjudicated:
        errors.append(["unadjudicated verification objections", unadjudicated])
    audited = {r["screen_id"] for r in audit_rows}
    missing_audits = sorted(target_ids - audited)
    if require_audits and missing_audits:
        errors.append(["source-verification coverage", missing_audits])
    evidence = {}
    for sid, inp in sorted(inputs.items()):
        paths = [inp["text"]] + ([inp["si_text"]] if inp.get("si_text") else [])
        evidence[sid] = {p: digest(HERE / p) for p in paths}
    report = dict(records=len(st), batches=counts, required_third_reads=len(required),
                  changed_records=[r["screen_id"] for r in st if r["v5_final"] != r["v5_final_before_si"]],
                  sensitivity_preserved=not any(e[0] == "v3/v4 sensitivity changed" for e in errors),
                  checklist_records=len(checklist), historical_outputs_preserved=len(historical),
                  entrant_questions=len(questions), triage_classes=classes,
                  verification_targets=len(target_ids), verified_target_records=len(target_ids & audited),
                  missing_verification=missing_audits,
                  adjudicated_records=len(adjudications), unadjudicated_objections=unadjudicated,
                  reviewed_recoveries=len(recoveries), recovery_independent_reads=recovery_reads,
                  recovery_source_hashes=recovery_hashes,
                  audit_rows=len(audit_rows), audit_review_modes=dict(Counter(r.get("review_mode", "not recorded in saved pre-cost-control audit") for r in audit_rows)),
                  verification_files={p.name: digest(p) for p in audit_files},
                  source_hashes=evidence, errors=errors)
    AUDIT.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("source_hashes", "recovery_source_hashes", "changed_records")}, indent=1))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true")
    ap.add_argument("--require-audits", action="store_true")
    args = ap.parse_args()
    main(args.snapshot, args.require_audits)
