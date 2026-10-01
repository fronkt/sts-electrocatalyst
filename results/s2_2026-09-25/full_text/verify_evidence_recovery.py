"""Validate the dated recovery without rewriting historical screening evidence."""
import csv
import hashlib
import json
import pathlib
from collections import Counter

from ft_screen import check
from reconcile import verified
from recovery_state import recovery_decisions, validate_fields

HERE = pathlib.Path(__file__).resolve().parent
D = HERE / "evidence_recovery_2026-10-01"
CRIT = ["E" + str(n) for n in range(1, 7)]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    errors = []
    baseline = json.loads((D / "baseline.json").read_text(encoding="utf-8"))
    for path, expected in baseline["files"].items():
        if sha(HERE / path) != expected:
            errors.append([path, "completed-round evidence changed"])
    recoveries = recovery_decisions()
    current = list(csv.DictReader((HERE / "reconcile" / "current_state.csv").open(encoding="utf-8")))
    old = {r["screen_id"]: r for r in baseline["records"]}
    if {r["screen_id"] for r in current} != set(old):
        errors.append(["record population changed"])
    changed = []
    for row in current:
        previous = old[row["screen_id"]]
        if any(row[k] != previous[k] for k in previous if k.startswith(("v3_", "v4_"))):
            errors.append([row["screen_id"], "historical v3/v4 sensitivity changed"])
        if row != previous:
            changed.append(row["screen_id"])
            if row["screen_id"] not in recoveries:
                errors.append([row["screen_id"], "unreviewed row change"])
    hashes, reads = {}, 0
    for sid, ruling in recoveries.items():
        chosen = ruling["row"]
        meta = json.loads((D / (sid.lower() + "_recovery.json")).read_text(encoding="utf-8"))
        sources = meta.get("files", [meta])
        for source in sources:
            if sha(HERE / source["file"]) != source["sha256"]:
                errors.append([sid, "recovered file hash mismatch"])
        if sha(HERE / meta["text"]) != meta["text_sha256"]:
            errors.append([sid, "recovered text hash mismatch"])
        if sid == "S01741":
            for key, pathkey in (("prior_wrong_file_sha256", "prior_wrong_file"),):
                if sha(HERE / meta[pathkey]) != meta[key]:
                    errors.append([sid, "prior wrong file not preserved"])
            if sha(HERE / "text" / "S01741.txt") != meta["prior_wrong_text_sha256"]:
                errors.append([sid, "prior wrong text not preserved"])
        signatures, read_rows = [], []
        for outpath in ruling["independent_reads"]:
            output = HERE / outpath
            inp = pathlib.Path(str(output).replace(".out.", ".in."))
            errors.extend([sid, e] for e in check(inp, output))
            input_row = json.loads(inp.read_text(encoding="utf-8"))
            row = json.loads(output.read_text(encoding="utf-8"))
            if input_row["si_complete"] != ruling["si_complete"] or row["doi"] != meta["doi"]:
                errors.append([sid, "input identity/completeness mismatch"])
            text = (HERE / input_row["text"]).read_text(encoding="utf-8") + "\n" + (HERE / input_row["si_text"]).read_text(encoding="utf-8")
            if not verified(row, text):
                errors.append([sid, "deciding excerpt not present in source"])
            for c in CRIT:
                if row[c]["v"] not in ("YES", "NO", "UNCLEAR", "NOT_ASSESSED"):
                    errors.append([sid, c, "invalid criterion"])
            if row["E6"]["v"] != "YES" and any(row.get(k) is not None for k in ("eta_form", "eta_derivation", "eta_note")):
                errors.append([sid, "non-YES E6 carries eta fields"])
            signatures.append(tuple(row[c]["v"] for c in CRIT) + (row["disposition"], row.get("exclude_criterion")))
            read_rows.append(row)
            hashes[outpath] = sha(output)
            hashes[inp.relative_to(HERE).as_posix()] = sha(inp)
            hashes[input_row["text"]] = sha(HERE / input_row["text"])
            hashes[input_row["si_text"]] = sha(HERE / input_row["si_text"])
            reads += 1
        expected = tuple(chosen[c]["v"] for c in CRIT) + (chosen["disposition"], chosen.get("exclude_criterion"))
        if len(set(signatures)) != 1 or signatures[0] != expected:
            errors.append([sid, "independent reads disagree or ruling mismatch; third read required"])
        errors.extend([sid, error] for error in validate_fields(ruling, read_rows))
        chosen_text = (HERE / input_row["text"]).read_text(encoding="utf-8") + "\n" + (HERE / input_row["si_text"]).read_text(encoding="utf-8")
        if not verified(chosen, chosen_text):
            errors.append([sid, "reviewed deciding excerpts not present"])
    checklist = list(csv.DictReader((HERE / "si_checklist.csv").open(encoding="utf-8")))
    expected_ids = {r["screen_id"] for r in baseline["checklist"]}
    expected_ids -= {sid for sid, r in recoveries.items() if r["si_complete"]}
    if {r["screen_id"] for r in checklist} != expected_ids or len(checklist) != len(expected_ids):
        errors.append(["checklist coverage mismatch"])
    for name in ("rsc_nature_routes.json", "wiley_routes.json", "acs_routes.json"):
        path = D / name
        if not path.exists():
            errors.append([name, "missing retrieval outcome report"])
        else:
            hashes[path.relative_to(HERE).as_posix()] = sha(path)
    report = {"records": len(current), "reviewed_recoveries": sorted(recoveries), "independent_reads": reads,
              "changed_rows": sorted(changed), "historical_evidence_files_preserved": len(baseline["files"]),
              "v3_v4_preserved": not any("sensitivity" in str(e) for e in errors),
              "checklist_records": len(checklist), "v5_counts": dict(Counter("collapsed" if r["v5_final"].startswith("collapsed") else r["v5_final"] for r in current)),
              "hashes": hashes, "errors": errors}
    (D / "verification.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "hashes"}, indent=1))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
