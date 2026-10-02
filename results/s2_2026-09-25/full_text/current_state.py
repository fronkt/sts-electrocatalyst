"""Current decision per record under instruction v5, with v4 and v3 kept as sensitivity sets.

  python current_state.py

Mechanical join, no judgement:
  v3 decision  AGREED_EXCLUDE / AGREED_ELIGIBLE lane -> the agreed pass disposition;
               THIRD_READ -> the third read; NEEDS_SI -> NEEDS_SI; RERETRIEVE -> none (no readable text).
  v4 decision  the v4 re-read where one exists (v4_read.py); otherwise the v3 decision, which v4 cannot
               change for that record by the v4_read.py selection rule.
  v5 decision  the v5 re-read where one exists (v5_read.py); otherwise the v4 decision, which v5 cannot
               change for that record by the v5_read.py selection rule.  The SI read (si_read.py: main text
               plus downloaded SI, two passes and a third read) replaces it once it settles the record:
               the SI third read, else two passes that agree with verified excerpts, else two passes that
               both find the SI incomplete (NEEDS_SI).  A record whose SI read is still open keeps its
               earlier v5 decision; column si_read shows the SI read's state, and v5_final_before_si the v5 final
               decision the record would have without the SI read.
Passes are dated by _screener.at.  Passes run after instruction v4 took effect (2026-09-27 07:50Z) are v4
reads; when both passes ran after v5 took effect (V5_FROM) they are v5 reads.  A THIRD_READ record's
third read has the version of its passes.  For v4 and v5 reads the v3 decision comes from the independent
v3 sensitivity read (v3_read.py) once it exists, else "v3 not read"; for v5 reads the v4 decision comes
from the independent v4 sensitivity read (v4s_read.py), else "v4 not read".

Mechanical steps on each decision (columns v3_final, v4_final, v5_final), each logged in instruction_changes.md;
v3 and v4 get the same steps without the v5 D7 branches, so the three sets are counted the same way:
  E6_WITHOUT_SI  an EXCLUDE:E6 whose file holds no SI breaks the rule that E6 is never excluded from
                 the main text alone -> NEEDS_SI if E1-E5 are YES, else UNRESOLVED (checked by hand).
  dates          an E2 UNCLEAR row takes E2 from reconcile/date_check.csv (ruling 10) when that row has a
                 date and no flag, or becomes EXCLUDE:E2 when the flag is OUTSIDE_WINDOW; the disposition is
                 re-derived from the six verdicts by the instructions' rule (step "dated" whether or not it
                 changes).  A re-derived NEEDS_SI stays UNRESOLVED when the file holds the SI (two or more
                 SI figure or table captions at line starts): NEEDS_SI means the SI is not in the file.
  versions       reconcile/version_groups.csv: a linked version is counted through its group's primary
                 ("collapsed"); an unlinked D3 form (conference abstract or paper, dissertation, report,
                 dataset) is EXCLUDE:E1 unless already excluded.  Unlinked preprints keep their own
                 decision (v4: awaiting a ruling; v5 D7: a complete preprint is judged on its own text).
                 v5 D7: a preprint is not collapsed into a journal version first published after the window
                 (2026-09-18; the primary's date from date_check.csv, else version_groups.csv); it keeps its own
                 decision (step "D7").  An unlinked report or dataset record in which every row deciding the v5
                 decision found an article manuscript (form journal or preprint) is judged as that manuscript,
                 not excluded as a D3 form (step "D7 wrapper").
  v5 triage A    V5_TRIAGE_A: a v5 row whose verdict conflicts with the v5 sentence that answers its entrant
                 question (reconcile/v5_questions_triage.md, section A) takes the verdict v5 gives, and the
                 disposition is re-derived; the source reads "...; v5 triage A".  The v5 output fields then
                 come from that row, and eta_form, eta_derivation and eta_note are null when E6 is no longer
                 YES (v5 D14).  Only an SI read that had the record's whole SI supersedes it.
  SI adjudication  explicit source-reviewed corrections in reconcile/si_adjudications_2026-09-29.json and the
                     non-overlapping approved case layer in mixed_si_review_2026-10-02/approved_policy_adjudications.json
                     replace only stated criteria/fields before the date/version joins. Raw read files and the v3/v4
                     branches stay unchanged. The original adjudication file is never rewritten. Unusable text
                     cannot be rescued by a date join. Earlier SI_VERIFY holds remain UNRESOLVED; E6 holds clear
                     eta descriptors rather than retaining invalid fields.
v5 output fields (form, eta_form, eta_derivation, eta_note, secondary, provenance) come from the rows that
decide the v5 decision (both passes where the passes decide) and are left blank where those rows differ, and
where the v5 decision is carried over from an earlier version (those rows predate the v5 schema; their entrant
questions were settled by the v4 and v5 rulings).
v5_check lists what reconciliation still has to settle by hand: "identity check" and "scope extension needed"
(written in a deciding row's note, v5 D9), "version primary not screened" (a live record collapsed into a
primary outside the full-text set) and "D7 primary date unclear" (a collapsed preprint whose primary's date
check is flagged).
Writes reconcile/current_state.csv and reconcile/current_state.json.
"""
import csv
import json
import pathlib
import re

from date_check import span
from reconcile import rows
from policy_reconciliation import merge_adjudications, policy_adjudications as load_policy_adjudications
from recovery_state import DEFAULT_RECOVERY_SOURCE
from v5_read import V5_FROM

HERE = pathlib.Path(__file__).resolve().parent
V4_FROM = "2026-09-27T07:50"
HI = "2026-09-18"
E6_WITHOUT_SI = {"S09618", "S23884", "S29788"}  # v4 EXCLUDE:E6, no SI in the file (checked 2026-09-27)
# v5 triage (reconcile/v5_questions_triage.md, section A): a v5 row whose verdict conflicts with a v5 sentence that
# answers its entrant question; the verdict v5 gives replaces it and the disposition is re-derived (step "v5 triage A")
V5_TRIAGE_A = {"S05043": {"E6": "UNCLEAR"},  # D4 largest-step condition not shown; RDS label alone (D13); Fig. 1d
               "S22122": {"E6": "UNCLEAR"},  # ruling 4 sends its 'kinetic overpotential' to SI review (D12)
               "S23639": {"E6": "UNCLEAR"}}  # 'limiting free energy barrier' is an RDS label (D4, D13)
# SI-read verification (2026-09-28): SI-read decisions a skeptic refuted and a judge upheld against v5; the record is
# UNRESOLVED until a fresh read settles it (reasons in instruction_changes.md). S26608: ELIGIBLE by the D4 route only
# if Q1/Q4 (unstated CHE reference) are ruled that way.
SI_VERIFY = {"S10906": "E4 (FCC vs rutile)", "S14755": "E4", "S16822": "E5", "S20248": "E6", "S25141": "E4",
             "S26256": "E6 (D4 assignment)", "S26608": "E6 (D4 route, Q1/Q4)", "S30061": "E6"}
SI_ADJUDICATION_FILE = HERE / "reconcile" / "si_adjudications_2026-09-29.json"
V5_FIELDS = ("form", "eta_form", "eta_derivation", "eta_note", "secondary", "provenance")
LIVE = ("ELIGIBLE", "NEEDS_SI", "UNRESOLVED")
NOTE_CHECKS = {"identity check": r"identity check", "scope extension needed": r"scope extension"}  # v5 D9 note markers
SI_CAPTION = re.compile(r"(?mi)^[ \t]*(?:supplementary |supporting )?(?:figure|fig\.?|table)[ \t]*S[ \t]?\d+[ \t]*[.:|]")


def si_in_file(sid):
    """The record's text holds SI: two or more SI figure or table captions at line starts."""
    p = HERE / "text" / (sid + ".txt")
    return p.exists() and len(SI_CAPTION.findall(p.read_text(encoding="utf-8"))) >= 2


def triage_a(sid, r):
    """The row with the V5_TRIAGE_A verdicts applied; eta_form, eta_derivation and eta_note become null when E6 is
    no longer YES (v5 D14)."""
    r = dict(r, **{c: dict(r.get(c) or {}, v=v) for c, v in V5_TRIAGE_A[sid].items()})
    if (r.get("E6") or {}).get("v") != "YES":
        r.update(eta_form=None, eta_derivation=None, eta_note=None)
    return r


def with_triage_a(sid, d, s, r, rs):
    """(decision, source, row, rows) after the V5_TRIAGE_A step."""
    r = triage_a(sid, r or rs[0])
    d = derive(r)
    if d == "NEEDS_SI" and si_in_file(sid):
        d = "UNRESOLVED"
    return d, s + "; v5 triage A", r, [r]


def derive(r):
    """The instructions' disposition rule applied to six verdicts."""
    v = {c: (r.get(c) or {}).get("v") for c in ("E1", "E2", "E3", "E4", "E5", "E6")}
    for c in ("E1", "E2", "E3", "E4", "E5", "E6"):
        if v[c] == "NO":
            return "EXCLUDE:" + c
    if all(v[c] == "YES" for c in v):
        return "ELIGIBLE"
    if all(v[c] == "YES" for c in ("E1", "E2", "E3", "E4")) and v["E5"] == "UNCLEAR":
        return "NEEDS_SI"
    if all(v[c] == "YES" for c in ("E1", "E2", "E3", "E4", "E5")) and v["E6"] == "UNCLEAR":
        return "NEEDS_SI"
    return "UNRESOLVED"


def final(sid, d, r, dates, si_whole=False):
    """(decision, step) after the E6 and date steps; r is the row that decided d (None for agreed passes);
    si_whole: r read the record's whole SI (an SI read with si_complete)."""
    def rederive(row):
        f = derive(row)
        return "UNRESOLVED" if f == "NEEDS_SI" and (si_whole or si_in_file(sid)) else f
    if not r:
        return d, ""
    if r.get("text_ok") is False:
        return "UNRESOLVED", "text not usable"
    if sid in E6_WITHOUT_SI and d == "EXCLUDE:E6":
        return derive(dict(r, E6={"v": "UNCLEAR"})), "E6_WITHOUT_SI"
    if (r.get("E2") or {}).get("v") == "UNCLEAR" and d in ("UNRESOLVED", "NEEDS_SI", "ELIGIBLE"):
        dc = dates.get(sid) or {}
        if dc.get("first_publication") and not dc.get("flag"):
            return rederive(dict(r, E2={"v": "YES"})), "dated"
        if dc.get("flag") == "OUTSIDE_WINDOW":
            return "EXCLUDE:E2", "dated"
    return d, ""


def member(vg, f, step, source, forms=None, primary_date=""):
    """(membership, step) after the version step.  forms: the form of each row deciding the v5 decision
    (None for v3 and v4, which have no D7 branches); primary_date: the primary's first publication."""
    v5, plus = forms is not None, lambda s: (step + ";" if step else "") + s
    if vg.get("status") == "collapses into primary":
        if v5 and vg.get("type") == "preprint" and primary_date and span(primary_date[:10])[0] > HI:
            return f or source, plus("D7")
        return "collapsed into " + vg["primary"], step
    if vg.get("status") == "unlinked D3 form" and f and not f.startswith("EXCLUDE"):
        if v5 and vg.get("type") in ("report", "dataset") and forms and set(forms) <= {"journal", "preprint"}:
            return f, plus("D7 wrapper")  # the read found an article manuscript in the report or repository record
        return "EXCLUDE:E1", plus("D3")
    return f or source, step


def label(r):
    return r and r["disposition"] + (":" + r["exclude_criterion"] if r.get("exclude_criterion") else "")


def at(r):
    return (r.get("_screener") or {}).get("at", "") if r else ""


def agreed(rs, k):
    """A field's value when every deciding row gives the same one, else None."""
    return rs[0].get(k) if rs and len({json.dumps(x.get(k)) for x in rs}) == 1 else None


def jsonl(p):
    return {json.loads(l)["screen_id"]: json.loads(l) for l in open(p, encoding="utf-8") if l.strip()} if p.exists() else {}


def si_adjudications():
    """Historical rulings plus a non-overlapping, approved additive policy layer."""
    historical = {}
    if SI_ADJUDICATION_FILE.exists():
        entries = json.loads(SI_ADJUDICATION_FILE.read_text(encoding="utf-8"))["records"]
        if len({r["screen_id"] for r in entries}) != len(entries):
            raise ValueError("Duplicate SI adjudication")
        historical = {r["screen_id"]: r for r in entries}
    approved = policy_adjudications()
    return merge_adjudications(historical, approved)


def policy_adjudications():
    """Explicitly approved case-scoped choices, with no scientific inference."""
    return load_policy_adjudications()


def adjudicated_row(row, ruling):
    """Overlay a recorded ruling without changing any historical read."""
    result = dict(row)
    result.update(ruling.get("criteria", {}))
    result.update(ruling.get("fields", {}))
    if "text_ok" in ruling:
        result["text_ok"] = ruling["text_ok"]
    if ruling.get("question_resolved") is True:
        result.pop("entrant_question", None)
    if result.get("text_ok") is False or (result.get("E6") or {}).get("v") != "YES":
        result.update(eta_form=None, eta_derivation=None, eta_note=None)
    return result


def main():
    from recovery_state import recovery_decisions
    recoveries = recovery_decisions()
    adjudications = si_adjudications()
    p1, p2 = rows("1"), rows("2")
    t3 = jsonl(HERE / "third_read" / "third_read.jsonl")
    v4 = jsonl(HERE / "v4_read" / "v4_read.jsonl")
    v5 = jsonl(HERE / "v5_read" / "v5_read.jsonl")
    v3s = jsonl(HERE / "v3_read" / "v3_read.jsonl")
    v4s = jsonl(HERE / "v4s_read" / "v4s_read.jsonl")
    si_t3 = jsonl(HERE / "si_read" / "third_read.jsonl")
    si_p = {n: jsonl(HERE / "si_read" / ("pass_%s.jsonl" % n)) for n in ("1", "2")}
    sq = HERE / "si_read" / "queue.csv"
    si_lane = {r["screen_id"]: r["lane"] for r in csv.DictReader(open(sq, encoding="utf-8"))} if sq.exists() else {}
    st = HERE / "si_texts.csv"
    si_whole = {r["screen_id"]: r["si_complete"] == "True" for r in csv.DictReader(open(st, encoding="utf-8"))} if st.exists() else {}
    dp = HERE / "reconcile" / "date_check.csv"
    dates = {r["screen_id"]: r for r in csv.DictReader(open(dp, encoding="utf-8"))} if dp.exists() else {}
    vp = HERE / "reconcile" / "version_groups.csv"
    vers = {r["screen_id"]: r for r in csv.DictReader(open(vp, encoding="utf-8"))} if vp.exists() else {}
    out, n3, nf3, n4, nf, n5, nf5 = [], {}, {}, {}, {}, {}, {}
    for q in csv.DictReader(open(HERE / "reconcile" / "queue.csv", encoding="utf-8")):
        sid, ln = q["screen_id"], q["lane"]
        a, b = p1.get(sid), p2.get(sid)
        v4_pass = any(x and at(x) >= V4_FROM for x in (a, b))
        v5_pass = all(x and at(x) >= V5_FROM for x in (a, b))
        if ln == "RERETRIEVE":
            d3, s3, r3 = "", "no readable text", None
        elif v4_pass:
            d3, s3, r3 = (label(v3s[sid]), "v3 sensitivity read", v3s[sid]) if sid in v3s else ("", "v3 not read", None)
        elif ln == "THIRD_READ":
            d3, s3, r3 = label(t3.get(sid)) or "", "third read" if sid in t3 else "third read pending", t3.get(sid)
        elif ln == "NEEDS_SI":
            d3, s3, r3 = "NEEDS_SI", "passes", None
        else:
            d3, s3, r3 = label(a), "passes agree", None
        if sid in v4:
            d4, s4, r4 = label(v4[sid]), "v4 read", v4[sid]
        elif v5_pass and ln != "RERETRIEVE":
            d4, s4, r4 = (label(v4s[sid]), "v4 sensitivity read", v4s[sid]) if sid in v4s else ("", "v4 not read", None)
        elif v4_pass and ln in ("AGREED_EXCLUDE", "AGREED_ELIGIBLE", "NEEDS_SI"):
            d4, s4, r4 = label(a) if ln != "NEEDS_SI" else "NEEDS_SI", "v4 passes", None
        elif v4_pass and ln == "THIRD_READ":
            d4, s4, r4 = label(t3.get(sid)) or "", "third read (v4)" if sid in t3 else "third read pending", t3.get(sid)
        else:
            d4, s4, r4 = d3, s3, None
        if ln == "RERETRIEVE":
            d5, s5, r5, rs5 = "", "no readable text", None, []
        elif sid in v5:
            d5, s5, r5, rs5 = label(v5[sid]), "v5 read", v5[sid], [v5[sid]]
        elif v5_pass and ln in ("AGREED_EXCLUDE", "AGREED_ELIGIBLE", "NEEDS_SI"):
            d5, s5, r5, rs5 = label(a) if ln != "NEEDS_SI" else "NEEDS_SI", "v5 passes", None, [a, b]
        elif v5_pass and ln == "THIRD_READ":
            d5, s5, r5 = label(t3.get(sid)) or "", "third read (v5)" if sid in t3 else "third read pending", t3.get(sid)
            rs5 = [r5] if r5 else []
        else:  # v5 cannot change this record (v5_read.py selection); its v4 decision stands
            d5, s5, r5, rs5 = d4, s4, r4, []
        pre = (d5, s5, r5, rs5)  # the v5 decision without the SI read, for v5_final_before_si
        si_state, whole = "", False
        if sid in si_t3:
            d5, s5, r5, rs5 = label(si_t3[sid]), "SI read: third read", si_t3[sid], [si_t3[sid]]
            si_state, whole = "third read", si_whole.get(sid, False)
        elif si_lane.get(sid) in ("AGREED", "NEEDS_SI"):
            a5, b5 = si_p["1"][sid], si_p["2"][sid]
            d5 = label(a5) if si_lane[sid] == "AGREED" else "NEEDS_SI"
            s5, r5, rs5, si_state = "SI read: passes agree", None, [a5, b5], si_lane[sid].lower()
            whole = si_whole.get(sid, False)
        elif sid in si_lane:
            si_state = si_lane[sid].lower().replace("_", " ") + " pending" if si_lane[sid] == "THIRD_READ" else si_lane[sid].lower()
        vg = vers.get(sid) or {}
        fields = {k: agreed(rs5, k) for k in V5_FIELDS}
        pd = dates.get(vg.get("primary")) or {}  # the primary's ruling-10 date, where it was checked
        pdate = (pd.get("first_publication") if pd.get("flag") in ("", "OUTSIDE_WINDOW") else "") if pd else vg.get("primary_date")
        f3, step3 = final(sid, d3, r3, dates)
        m3, step3 = member(vg, f3, step3, s3)
        f4, step4 = final(sid, d4, r4, dates)
        m4, step4 = member(vg, f4, step4, s4)
        if sid in V5_TRIAGE_A and (r5 or rs5) and not (si_state and whole):  # only a read with the whole SI supersedes it
            d5, s5, r5, rs5 = with_triage_a(sid, d5, s5, r5, rs5)
            fields = {k: agreed(rs5, k) for k in V5_FIELDS}
        if sid in adjudications and si_state in ("third read", "agreed", "needs_si"):
            r5 = adjudicated_row(dict(r5 or rs5[0], **fields), adjudications[sid])
            rs5 = [r5]
            d5 = "UNRESOLVED" if r5.get("text_ok") is False else derive(r5)
            if d5 == "NEEDS_SI" and (whole or si_in_file(sid)):
                d5 = "UNRESOLVED"
            entry_date = adjudications[sid].get("entry_date", "2026-09-29")
            s5 += "; SI adjudication " + entry_date
            fields = {k: agreed(rs5, k) for k in V5_FIELDS}
        if sid in recoveries:
            recovered = recoveries[sid]
            r5 = dict(recovered["row"])
            rs5 = [r5]
            d5 = label(r5)
            s5 = recovered.get("source", DEFAULT_RECOVERY_SOURCE)
            si_state, whole = "recovery reviewed", recovered["si_complete"]
            fields = {k: agreed(rs5, k) for k in V5_FIELDS}
        f5, step5 = final(sid, d5, r5, dates, whole)
        m5, step5 = member(vg, f5, step5, s5, [x.get("form") for x in rs5], pdate or "")
        m5_pre = m5
        if si_state in ("third read", "agreed", "needs_si", "recovery reviewed"):
            pd5, ps5, pr5, prs5 = pre
            if sid in V5_TRIAGE_A and (pr5 or prs5):
                pd5, ps5, pr5, prs5 = with_triage_a(sid, pd5, ps5, pr5, prs5)
            pf5, pstep5 = final(sid, pd5, pr5, dates)
            m5_pre, _ = member(vg, pf5, pstep5, ps5, [x.get("form") for x in prs5], pdate or "")
        if sid in SI_VERIFY and si_state in ("third read", "agreed", "needs_si"):
            m5, step5 = "UNRESOLVED", (step5 + ";" if step5 else "") + "SI verification: " + SI_VERIFY[sid]
            if SI_VERIFY[sid].startswith("E6"):
                fields.update(eta_form=None, eta_derivation=None, eta_note=None)
        check = sorted({c for x in rs5 for c, pat in NOTE_CHECKS.items() if re.search(pat, x.get("note") or "", re.I)})
        if m5.startswith("collapsed") and vg.get("primary_in_fulltext") != "True" and f5.startswith(LIVE):
            check.append("version primary not screened")
        if m5.startswith("collapsed") and vg.get("type") == "preprint" and pd and not pdate:
            check.append("D7 primary date unclear")
        out.append(dict(screen_id=sid, doi=q["doi"], lane=ln, v3_decision=d3, v3_source=s3, v3_final=m3, v3_step=step3,
                        v4_decision=d4, v4_source=s4, v4_final=m4, v4_step=step4,
                        v5_decision=d5, v5_source=s5, v5_final=m5, v5_step=step5, version_primary=vg.get("primary", ""),
                        v4_eta_form=(r4 or {}).get("eta_form"), v4_secondary=(r4 or {}).get("secondary"),
                        v4_question=bool((r4 or {}).get("entrant_question")),
                        **{"v5_" + k: v for k, v in fields.items()},
                        v5_question=any(bool(x.get("entrant_question")) for x in rs5), v5_check=";".join(check),
                        si_read=si_state, v5_final_before_si=m5_pre))
        for n, d, s in ((n3, d3, s3), (n4, d4, s4), (n5, d5, s5)):
            n[d or s] = n.get(d or s, 0) + 1
        for n, m in ((nf3, m3), (nf, m4), (nf5, m5)):
            key = "collapsed" if m.startswith("collapsed") else m
            n[key] = n.get(key, 0) + 1
    with open(HERE / "reconcile" / "current_state.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    json.dump(dict(records=len(out), v3=n3, v3_final=nf3, v4=n4, v4_final=nf, v5=n5, v5_final=nf5),
              open(HERE / "reconcile" / "current_state.json", "w"), indent=1)
    print(len(out), "records\nv3:", dict(sorted(n3.items())), "\nv3 final:", dict(sorted(nf3.items())),
          "\nv4:", dict(sorted(n4.items())),
          "\nv4 final:", dict(sorted(nf.items())), "\nv5:", dict(sorted(n5.items())),
          "\nv5 final:", dict(sorted(nf5.items())))


if __name__ == "__main__":
    main()
