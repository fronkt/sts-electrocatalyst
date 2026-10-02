"""Validate the dated recovery without rewriting historical screening evidence."""
import csv
import argparse
import hashlib
import json
import pathlib
import re
import unicodedata
from collections import Counter

from ft_screen import check
from reconcile import verified
from recovery_state import recovery_decisions, validate_fields, evidence_path, DEFAULT_RECOVERY_SOURCE
from current_state import label, final, member, V5_FIELDS

HERE = pathlib.Path(__file__).resolve().parent
D = HERE / "evidence_recovery_2026-10-01"
CRIT = ["E" + str(n) for n in range(1, 7)]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def all_fragments_present(excerpt, text):
    # PDF ligatures such as ﬁ are compatibility characters, not changed wording.
    def canonical(value):
        return re.sub(r"[^a-z0-9]+", "", unicodedata.normalize("NFKD", value).lower())
    source = canonical(text)
    fragments = [canonical(s) for s in re.split(r"…|\.\.\.", excerpt)]
    fragments = [fragment for fragment in fragments if fragment]
    return bool(fragments) and all(fragment in source for fragment in fragments)


def row_errors(row, text, si_complete):
    """Validate recorded decisions and every assessed excerpt, not only positives."""
    errors = []
    if not row.get("screen_id") or not row.get("doi") or row.get("text_ok") is not True:
        errors.append("missing identity/usable text")
    for c in CRIT:
        v = (row.get(c) or {}).get("v")
        if v not in ("YES", "NO", "UNCLEAR", "NOT_ASSESSED"):
            errors.append(c + ": invalid verdict")
        elif v != "NOT_ASSESSED":
            if not row[c].get("where") or not row[c].get("excerpt"):
                errors.append(c + ": missing evidence location/excerpt")
            elif not all_fragments_present(row[c]["excerpt"], text):
                errors.append(c + ": excerpt not present in source")
            excerpt = row[c].get("excerpt") or ""
            fragments = re.split(r"…|\.\.\.", excerpt)
            cap = 25 if len(fragments) > 1 else 40
            if any(len(part.split()) > cap for part in fragments):
                errors.append(c + ": excerpt exceeds schema word limit")
        elif row.get("disposition") != "EXCLUDE" or not any((row.get(p) or {}).get("v") == "NO" for p in CRIT[:CRIT.index(c)]):
            errors.append(c + ": unassessed before any clear exclusion")
    allowed = {"form": ("journal", "preprint", "other"),
               "eta_form": (None, "numeric", "graphical", "relative"),
               "eta_derivation": (None, "direct", "equivalent", "scaling"),
               "secondary": (None, "reanalysis"),
               "provenance": (None, "own", "external", "mixed", "unclear")}
    for field, values in allowed.items():
        if field not in row or row[field] not in values:
            errors.append(field + ": missing/invalid field")
    for field in ("eta_note", "note"):
        if field not in row or (row[field] is not None and not isinstance(row[field], str)):
            errors.append(field + ": missing/invalid field")
        elif row[field] is not None and len(row[field].split()) > (25 if field == "eta_note" else 40):
            errors.append(field + ": exceeds schema word limit")
    from current_state import derive
    expected = derive(row)
    if expected == "NEEDS_SI" and si_complete:
        expected = "UNRESOLVED"
    actual = label(row)
    if actual != expected:
        errors.append("criterion/disposition inconsistency")
    if row.get("disposition") != "EXCLUDE" and row.get("exclude_criterion") is not None:
        errors.append("non-exclusion carries exclusion criterion")
    if (row.get("E6") or {}).get("v") != "YES" and any(row.get(k) is not None for k in ("eta_form", "eta_derivation", "eta_note")):
        errors.append("non-YES E6 carries eta fields")
    if (row.get("E6") or {}).get("v") == "YES" and any(row.get(k) is None for k in ("eta_form", "eta_derivation")):
        errors.append("YES E6 lacks eta descriptors")
    if row.get("secondary") != "reanalysis" and row.get("provenance") is not None:
        errors.append("provenance without reanalysis")
    if row.get("secondary") == "reanalysis" and row.get("provenance") is None:
        errors.append("reanalysis lacks provenance")
    return errors


def rebuilt_errors(row, ruling, dates, versions):
    chosen = ruling["row"]
    sid = chosen["screen_id"]
    f, step = final(sid, label(chosen), chosen, dates, ruling["si_complete"])
    vg = versions.get(sid, {})
    pd = dates.get(vg.get("primary"), {})
    pdate = pd.get("first_publication", "") if pd.get("flag") in ("", "OUTSIDE_WINDOW") else ""
    if not pd:
        pdate = vg.get("primary_date", "")
    source = ruling.get("source", DEFAULT_RECOVERY_SOURCE)
    membership, step = member(vg, f, step, source, [chosen["form"]], pdate)
    expected = {"doi": chosen["doi"], "v5_decision": label(chosen), "v5_final": membership,
                "v5_source": source, "v5_step": step,
                "si_read": "recovery reviewed", "v5_question": str(bool(chosen.get("entrant_question")))}
    expected.update({"v5_" + k: str(chosen[k]) if chosen[k] is not None else "" for k in V5_FIELDS})
    return [k + ": rebuilt state differs from reviewed ruling" for k, value in expected.items() if row.get(k) != value]


def validate_recovery_evidence(recoveries):
    """Validate the pinned sources and both independent reads for every recovery layer."""
    errors, hashes, reads = [], {}, 0
    for sid, ruling in recoveries.items():
        chosen = ruling["row"]
        meta_path = evidence_path(ruling.get("source_metadata", "evidence_recovery_2026-10-01/" + sid.lower() + "_recovery.json"))
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        hashes[meta_path.relative_to(HERE).as_posix()] = sha(meta_path)
        sources = meta.get("files", [meta])
        for source in sources:
            source_path = evidence_path(source["file"])
            if sha(source_path) != source["sha256"]:
                errors.append([sid, "recovered file hash mismatch"])
            hashes[source_path.relative_to(HERE).as_posix()] = sha(source_path)
        text_path = evidence_path(meta["text"])
        if sha(text_path) != meta["text_sha256"]:
            errors.append([sid, "recovered text hash mismatch"])
        hashes[text_path.relative_to(HERE).as_posix()] = sha(text_path)
        if "si_text" in meta:
            si_path = evidence_path(meta["si_text"])
            if sha(si_path) != meta.get("si_text_sha256"):
                errors.append([sid, "recovered SI text hash mismatch"])
            hashes[si_path.relative_to(HERE).as_posix()] = sha(si_path)
        if sid == "S01741":
            for key, pathkey in (("prior_wrong_file_sha256", "prior_wrong_file"),):
                if sha(evidence_path(meta[pathkey])) != meta[key]:
                    errors.append([sid, "prior wrong file not preserved"])
            if sha(HERE / "text" / "S01741.txt") != meta["prior_wrong_text_sha256"]:
                errors.append([sid, "prior wrong text not preserved"])
        signatures, read_rows = [], []
        input_rows = []
        for outpath in ruling["independent_reads"]:
            output = evidence_path(outpath)
            inp = evidence_path(pathlib.Path(str(output).replace(".out.", ".in.")))
            errors.extend([sid, e] for e in check(inp, output))
            input_row = json.loads(inp.read_text(encoding="utf-8"))
            row = json.loads(output.read_text(encoding="utf-8"))
            if "si_text" in meta and any(evidence_path(input_row[field]) != evidence_path(meta[field])
                                         for field in ("text", "si_text")):
                errors.append([sid, "read paths differ from pinned source metadata"])
            if (input_row.get("screen_id") != sid or row.get("screen_id") != sid
                    or input_row.get("doi") != meta["doi"] or row.get("doi") != meta["doi"]
                    or input_row["si_complete"] != ruling["si_complete"]):
                errors.append([sid, "input identity/completeness mismatch"])
            text = evidence_path(input_row["text"]).read_text(encoding="utf-8") + "\n" + evidence_path(input_row["si_text"]).read_text(encoding="utf-8")
            errors.extend([sid, outpath, e] for e in row_errors(row, text, ruling["si_complete"]))
            if not verified(row, text):
                errors.append([sid, "deciding excerpt not present in source"])
            for c in CRIT:
                if row[c]["v"] not in ("YES", "NO", "UNCLEAR", "NOT_ASSESSED"):
                    errors.append([sid, c, "invalid criterion"])
            if row["E6"]["v"] != "YES" and any(row.get(k) is not None for k in ("eta_form", "eta_derivation", "eta_note")):
                errors.append([sid, "non-YES E6 carries eta fields"])
            signatures.append(tuple(row[c]["v"] for c in CRIT) + (row["disposition"], row.get("exclude_criterion")))
            read_rows.append(row)
            input_rows.append(input_row)
            hashes[outpath] = sha(output)
            hashes[inp.relative_to(HERE).as_posix()] = sha(inp)
            hashes[input_row["text"]] = sha(evidence_path(input_row["text"]))
            hashes[input_row["si_text"]] = sha(evidence_path(input_row["si_text"]))
            reads += 1
        expected = tuple(chosen[c]["v"] for c in CRIT) + (chosen["disposition"], chosen.get("exclude_criterion"))
        if len(set(signatures)) != 1 or not signatures or signatures[0] != expected:
            errors.append([sid, "independent reads disagree or ruling mismatch; third read required"])
        errors.extend([sid, error] for error in validate_fields(ruling, read_rows))
        if input_rows:
            chosen_text = evidence_path(input_rows[-1]["text"]).read_text(encoding="utf-8") + "\n" + evidence_path(input_rows[-1]["si_text"]).read_text(encoding="utf-8")
            errors.extend([sid, e] for e in row_errors(chosen, chosen_text, ruling["si_complete"]))
            if not verified(chosen, chosen_text):
                errors.append([sid, "reviewed deciding excerpts not present"])
    return errors, hashes, reads


def checklist_errors(checklist, previous, recoveries):
    expected = {r["screen_id"]: r for r in previous}
    for sid, ruling in recoveries.items():
        if ruling["si_complete"] or ruling["row"]["disposition"] == "EXCLUDE":
            expected.pop(sid, None)
    errors = []
    if {r["screen_id"] for r in checklist} != set(expected) or len(checklist) != len(expected):
        errors.append(["checklist coverage mismatch"])
    for row in checklist:
        if row != expected.get(row["screen_id"]):
            errors.append([row["screen_id"], "retained checklist row changed"])
    return errors


def policy_rebuilt_errors(row, ruling, dates, versions):
    """Check the exact approved overlay against the preserved deciding SI row."""
    from current_state import adjudicated_row, derive, si_in_file, SI_VERIFY
    sid = ruling["screen_id"]
    original = [json.loads(line) for line in (HERE / "si_read" / "third_read.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip() and json.loads(line).get("screen_id") == sid]
    if len(original) != 1:
        return ["policy deciding-row identity mismatch"]
    chosen = adjudicated_row(original[0], ruling)
    with (HERE / "si_texts.csv").open(encoding="utf-8") as stream:
        whole = {r["screen_id"]: r["si_complete"] == "True" for r in csv.DictReader(stream)}.get(sid, False)
    decision = derive(chosen)
    if decision == "NEEDS_SI" and (whole or si_in_file(sid)):
        decision = "UNRESOLVED"
    result, step = final(sid, decision, chosen, dates, whole)
    vg = versions.get(sid, {})
    pd = dates.get(vg.get("primary"), {})
    pdate = pd.get("first_publication", "") if pd.get("flag") in ("", "OUTSIDE_WINDOW") else ""
    if not pd:
        pdate = vg.get("primary_date", "")
    source = "SI read: third read; SI adjudication " + ruling["date"]
    membership, step = member(vg, result, step, source, [chosen["form"]], pdate)
    if sid in SI_VERIFY:
        membership = "UNRESOLVED"
        step += (";" if step else "") + "SI verification: " + SI_VERIFY[sid]
    expected = {"doi": chosen["doi"], "v5_decision": decision, "v5_final": membership,
                "v5_source": source, "v5_step": step, "si_read": "third read", "v5_question": "False"}
    expected.update({"v5_" + k: str(chosen[k]) if chosen.get(k) is not None else "" for k in V5_FIELDS})
    errors = [k + ": rebuilt policy state differs from approved ruling" for k, value in expected.items() if row.get(k) != value]
    text = (HERE / "text" / (sid + ".txt")).read_text(encoding="utf-8") + "\n" + (HERE / "text_si" / (sid + ".txt")).read_text(encoding="utf-8")
    for name, criterion in ruling.get("criteria", {}).items():
        if not all_fragments_present(criterion["excerpt"], text):
            errors.append(name + ": approved-policy excerpt not present")
        fragments = re.split(r"…|\.\.\.", criterion["excerpt"])
        if any(len(part.split()) > (25 if len(fragments) > 1 else 40) for part in fragments):
            errors.append(name + ": approved-policy excerpt exceeds word limit")
    return errors


def main(baseline_dir=D, output_dir=D):
    errors = []
    preserved = 0
    baseline = json.loads((baseline_dir / "baseline.json").read_text(encoding="utf-8"))
    for path, expected in baseline["files"].items():
        if path in ("reconcile/current_state.csv", "reconcile/current_state.json", "si_checklist.csv", "si_checklist.html"):
            continue  # compared structurally below; these are the intended rebuild outputs
        if sha(evidence_path(path)) != expected:
            errors.append([path, "completed-round evidence changed"])
        else:
            preserved += 1
    recoveries = recovery_decisions()
    from current_state import policy_adjudications
    policies = policy_adjudications()
    dates = {r["screen_id"]: r for r in csv.DictReader(evidence_path("reconcile/date_check.csv").open(encoding="utf-8"))}
    versions = {r["screen_id"]: r for r in csv.DictReader(evidence_path("reconcile/version_groups.csv").open(encoding="utf-8"))}
    current = list(csv.DictReader((HERE / "reconcile" / "current_state.csv").open(encoding="utf-8")))
    old = {r["screen_id"]: r for r in baseline["records"]}
    if {r["screen_id"] for r in current} != set(old):
        errors.append(["record population changed"])
    changed = []
    for row in current:
        previous = old[row["screen_id"]]
        if any(row[k] != previous[k] for k in previous if k.startswith(("v3_", "v4_"))):
            errors.append([row["screen_id"], "historical v3/v4 sensitivity changed"])
        if any(row[k] != previous[k] for k in ("lane", "version_primary", "v5_final_before_si")):
            errors.append([row["screen_id"], "unaffected reconciliation membership/history changed"])
        if row != previous:
            changed.append(row["screen_id"])
            if row["screen_id"] not in recoveries and row["screen_id"] not in policies:
                errors.append([row["screen_id"], "unreviewed row change"])
        if row["screen_id"] in recoveries:
            errors.extend([row["screen_id"], error] for error in rebuilt_errors(row, recoveries[row["screen_id"]], dates, versions))
        if row["screen_id"] in policies:
            errors.extend([row["screen_id"], error] for error in policy_rebuilt_errors(row, policies[row["screen_id"]], dates, versions))
    evidence_errors, hashes, reads = validate_recovery_evidence(recoveries)
    errors.extend(evidence_errors)
    checklist = list(csv.DictReader((HERE / "si_checklist.csv").open(encoding="utf-8")))
    errors.extend(checklist_errors(checklist, baseline["checklist"], recoveries))
    for name in ("rsc_nature_routes.json", "wiley_routes.json", "acs_routes.json"):
        path = D / name
        if not path.exists():
            errors.append([name, "missing retrieval outcome report"])
        else:
            hashes[path.relative_to(HERE).as_posix()] = sha(path)
    report = {"records": len(current), "reviewed_recoveries": sorted(recoveries), "independent_reads": reads,
              "approved_policy_cases": sorted(policies),
              "changed_rows": sorted(changed), "historical_evidence_files_preserved": preserved,
              "v3_v4_preserved": not any("sensitivity" in str(e) for e in errors),
              "checklist_records": len(checklist), "v5_counts": dict(Counter("collapsed" if r["v5_final"].startswith("collapsed") else r["v5_final"] for r in current)),
              "hashes": hashes, "errors": errors}
    (output_dir / "verification.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "hashes"}, indent=1))
    if errors:
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-dir", type=pathlib.Path, default=D)
    parser.add_argument("--output-dir", type=pathlib.Path, default=D)
    args = parser.parse_args()
    main(args.baseline_dir, args.output_dir)
