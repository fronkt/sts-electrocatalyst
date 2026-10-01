"""Pin selected prior attempts and new-route coverage, not the entire access queue."""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
D = HERE / "evidence_recovery_2026-10-01"


def main():
    reports = []
    for name in ("rsc_nature_routes.json", "wiley_routes.json", "acs_routes.json"):
        data = json.loads((D / name).read_text(encoding="utf-8"))
        reports.extend(data if isinstance(data, list) else data["records"])
    ids = {r["screen_id"] for r in reports} | {"S01741"}
    if len(ids) != 21 or len(reports) != 20:
        raise ValueError("Unexpected dated retrieval coverage")
    prior = D / "prior_attempts.jsonl"
    if not prior.exists():
        lines = []
        for name in ("si_public_log.jsonl", "retrieval_log.jsonl"):
            for line in (HERE / name).read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                if row.get("screen_id") in ids and (name == "si_public_log.jsonl" or row["screen_id"] == "S01741"):
                    lines.append(json.dumps({"source_log": name, "attempt": row}))
        prior.write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary = {"date": "2026-10-01", "retrieval_targets": sorted(ids), "priority_si_targets": 20,
               "main_identity_recovery": ["S01741"], "recovered_si": ["S26375"],
               "si_not_recovered": sorted(ids - {"S01741", "S26375"}),
               "scope": "Focused public recovery batch, not a claim that all 164 checklist gaps were attempted or closed.",
               "librarian_reply": "Requested from entrant; not supplied. No email access or change to institutional-access pause.",
               "new_cambridge_route": "s26375_recovery.json supersedes the earlier no-recovery outcome in rsc_nature_routes.json.",
               "blocks": "Publisher access blocks/interstitials retained. No captcha bypass, proxy/login, keyed publisher API or Batch API used.",
               "publisher_gate_note": "Some initial publisher opens were queued together, producing multiple 403 reports before the publisher-level stop. No bypass was attempted; continuation prompts must check one publisher request before queuing more."}
    (D / "routes_summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print("21 targets pinned; 2 records recovered; 19 SI gaps retained")


if __name__ == "__main__":
    main()
