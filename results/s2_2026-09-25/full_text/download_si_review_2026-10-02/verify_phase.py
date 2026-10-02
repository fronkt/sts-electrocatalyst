"""Offline exact-scope check for the four downloaded SI packages."""
import csv
import hashlib
import json
import pathlib
from collections import Counter

PHASE = pathlib.Path(__file__).resolve().parent
FT = PHASE.parent
REPO = FT.parents[2]
IDS = {"S11310", "S20440", "S21356", "S23207"}
REBUILDS = {"reconcile/current_state.csv", "reconcile/current_state.json",
            "si_checklist.csv", "si_checklist.html"}
IMPLEMENTATION = {"current_state.py", "recovery_state.py",
                  "verify_evidence_recovery.py", "verify_si_round.py"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def source_link_errors(entry, ruling, meta):
    sid, errors = entry["screen_id"], []
    if ruling["row"].get("doi") != entry["doi"]:
        errors.append([sid, "reviewed DOI differs from verified source gate"])
    if meta.get("screen_id") != sid or meta.get("doi") != entry["doi"]:
        errors.append([sid, "source metadata identity differs from verified gate"])
    if ruling.get("si_complete") is not True or meta.get("si_complete") is not True or meta.get("identity_verified") is not True:
        errors.append([sid, "reviewed completeness/identity differs from verified gate"])
    metadata_pins = {(pin["file"], pin["sha256"]) for pin in meta.get("files", [])}
    if not {(pin["file"], pin["sha256"]) for pin in entry["source_pins"]} <= metadata_pins:
        errors.append([sid, "source metadata binary pins differ from verified gate"])
    for metadata_field, gate_field, hashfield in (("text", "main_text", "main_sha256"),
                                                 ("si_text", "si_text", "si_sha256")):
        if meta.get(metadata_field) != entry[gate_field] or meta.get(metadata_field + "_sha256") != entry[hashfield]:
            errors.append([sid, metadata_field, "source metadata differs from verified gate"])
    return errors


def input_link_errors(entry, input_row):
    sid, errors = entry["screen_id"], []
    if input_row.get("doi") != entry["doi"] or input_row.get("screen_id") != sid:
        errors.append([sid, "reading identity differs from verified gate"])
    if input_row.get("text") != entry["main_text"] or input_row.get("si_text") != entry["si_text"]:
        errors.append([sid, "reading paths differ from verified gate"])
    return errors


def main():
    baseline = json.loads((PHASE / "baseline.json").read_text(encoding="utf-8"))
    gate = json.loads((PHASE / "source_read_gate.json").read_text(encoding="utf-8"))
    originals = json.loads((PHASE / "initial_read_validation.json").read_text(encoding="utf-8"))
    history = json.loads((PHASE / "assessment_history.json").read_text(encoding="utf-8"))
    rulings = json.loads((PHASE / "reviewed_decisions.json").read_text(encoding="utf-8"))["records"]
    errors, preserved, implementation = [], {}, {}
    for name, expected in baseline["files"].items():
        actual = sha(FT / name)
        if name in REBUILDS:
            continue
        if name in IMPLEMENTATION:
            implementation[name] = {"before": expected, "after": actual}
        elif actual != expected:
            errors.append([name, "historical evidence changed"])
        else:
            preserved[name] = actual
    unrelated = {}
    for name, expected in baseline["unrelated_untracked_files"].items():
        actual = sha(REPO / name)
        unrelated[name] = actual
        if actual != expected:
            errors.append([name, "unrelated DFT file changed"])
    for original in originals["original_reads"]:
        if sha(PHASE / original["output"]) != original["sha256"]:
            errors.append([original["output"], "original assessment changed"])
    if history["original_source_assessments"] != 12 or len(history["original_outputs"]) != 12:
        errors.append(["new source-assessment coverage mismatch"])
    for original in history["original_outputs"]:
        if sha(PHASE / original["output"]) != original["sha256"]:
            errors.append([original["output"], "focused/initial original assessment changed"])
    source_hashes = {}
    if {r["screen_id"] for r in gate["records"]} != IDS or len(gate["records"]) != 4:
        errors.append(["source gate coverage mismatch"])
    if {r["row"]["screen_id"] for r in rulings} != IDS or len(rulings) != 4:
        errors.append(["reviewed ruling coverage mismatch"])
    by_id = {r["row"]["screen_id"]: r for r in rulings}
    for entry in gate["records"]:
        sid = entry["screen_id"]
        ruling = by_id.get(sid)
        if ruling is None:
            errors.append([sid, "source gate has no reviewed ruling"])
            continue
        meta = json.loads((FT / ruling["source_metadata"]).read_text(encoding="utf-8"))
        errors.extend(source_link_errors(entry, ruling, meta))
        if entry["identity_verified"] is not True or entry["si_complete_for_read"] is not True:
            errors.append([sid, "source identity/completeness not verified"])
        for pin in entry["source_pins"]:
            for path in (FT / pin["file"], pathlib.Path(pin["download_path"])):
                actual = sha(path)
                source_hashes[str(path)] = actual
                if actual != pin["sha256"]:
                    errors.append([sid, str(path), "source or Downloads changed"])
        for field, hashfield in (("main_text", "main_sha256"), ("si_text", "si_sha256")):
            if sha(FT / entry[field]) != entry[hashfield]:
                errors.append([sid, field, "reading text changed"])
        suffix = pathlib.Path(entry["source_pins"][1]["file"]).suffix
        cache = FT / "files_si" / (sid + "_SI1" + suffix)
        if sha(cache) != entry["source_pins"][1]["sha256"]:
            errors.append([sid, "canonical SI cache differs"])
        for out in ruling["independent_reads"]:
            inp = FT / out.replace(".out.", ".in.")
            input_row = json.loads(inp.read_text(encoding="utf-8"))
            errors.extend(input_link_errors(entry, input_row))
            row = json.loads((FT / out).read_text(encoding="utf-8"))
            for criterion in ("E" + str(n) for n in range(1, 7)):
                if len(row[criterion]["excerpt"].split(" … ")) > 2:
                    errors.append([sid, out, criterion, "more than two quote fragments"])
            if "_checked.out." in out:
                original_path = FT / out.replace("_checked.out.", ".out.")
                original = json.loads(original_path.read_text(encoding="utf-8"))
                for field in ("screen_id", "doi", "text_ok", "disposition", "exclude_criterion",
                              "form", "eta_form", "eta_derivation", "eta_note", "secondary", "provenance"):
                    if row[field] != original[field]:
                        errors.append([sid, out, field, "transcription copy changes assessment"])
                for criterion in ("E" + str(n) for n in range(1, 7)):
                    if row[criterion]["v"] != original[criterion]["v"]:
                        errors.append([sid, out, criterion, "transcription copy changes verdict"])
    old = {r["screen_id"]: r for r in baseline["records"]}
    current = csv_rows(FT / "reconcile" / "current_state.csv")
    now = {r["screen_id"]: r for r in current}
    if len(current) != 2496 or set(now) != set(old):
        errors.append(["record population changed"])
    changed = {sid for sid in old if now.get(sid) != old[sid]}
    if changed != IDS:
        errors.append(["canonical changes are not exactly the four reviewed records", sorted(changed)])
    for sid in old:
        for field in old[sid]:
            if field.startswith(("v3_", "v4_")) or field in ("lane", "version_primary", "v5_final_before_si"):
                if now[sid][field] != old[sid][field]:
                    errors.append([sid, field, "historical population/membership changed"])
    expected = [r for r in baseline["checklist"] if r["screen_id"] not in IDS]
    checklist = csv_rows(FT / "si_checklist.csv")
    if checklist != expected:
        errors.append(["retained checklist rows/order changed"])
    forced = {"S29721", "S10090", "S22807", "S26024"}
    if not forced <= {r["screen_id"] for r in checklist}:
        errors.append(["forced eligible-question checklist items missing"])
    if baseline["budget"] != {"lifetime_api_cap_usd": 50, "conservative_tracked_usd": 1.1105254,
                              "new_paid_external_api_calls": 0}:
        errors.append(["budget scope differs"])
    report = {"starting_head": baseline["git_head"], "records": len(current),
              "changed_rows": sorted(changed), "historical_files_preserved": len(preserved),
              "implementation_changes": implementation, "unrelated_dft_files_preserved": len(unrelated),
              "original_assessments_preserved": len(originals["original_reads"]),
              "source_assessments_preserved": len(history["original_outputs"]),
              "source_hashes": source_hashes, "checklist_records": len(checklist),
              "checklist_tiers": dict(Counter(r["tier"] for r in checklist)),
              "v5_counts": dict(Counter("collapsed" if r["v5_final"].startswith("collapsed") else r["v5_final"] for r in current)),
              "reviewed_outcomes": {sid: now[sid]["v5_final"] for sid in sorted(IDS)},
              "budget": baseline["budget"], "errors": errors}
    target = PHASE / "scientific_final" / "phase_verification.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "source_hashes"}, indent=1))
    if errors:
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    main()
