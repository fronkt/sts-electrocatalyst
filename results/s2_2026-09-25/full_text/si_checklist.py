"""SI download checklist: every live record whose supporting information is not in hand, with the SI location,
the SI file to download (never the article PDF again) and what the SI can settle.  Entrant, 2026-09-28: "Prioritize
supplements that can settle eligibility, and identify the exact missing files rather than requesting another
main-paper download."

  python si_checklist.py [--ids S1,S2]     -> si_checklist.csv, si_checklist.html

Records: v5_final NEEDS_SI or UNRESOLVED in reconcile/current_state.csv, plus --ids (currently eligible records
whose open question needs their SI), whose downloaded SI holds no SI document (retrieve_si_public.has_document).
Priority, from the verdicts of the rows that decide the v5 decision (a record takes the lowest tier that fits):
  1  the SI decides eligibility: E1-E5 YES and E6 UNCLEAR, or an --ids record
  2  E1-E4 YES and E5 UNCLEAR: the SI states the facet, then the SI decides E6
  3  E1-E3 YES and E4 UNCLEAR: the SI may establish rutile for the model (a card, a CIF, a stated cell)
  4  something the SI cannot settle by itself: E1 or E3 UNCLEAR, a disagreement between deciding rows
E2 UNCLEAR is settled from publisher and Crossref dates (date_check.py), not from the SI, and does not lower the
tier; where reconcile/date_check.csv already dates the record (no flag), E2 is shown as YES, as current_state.py
applies it.  SI items named in the deciding rows (Fig. S5, Table S2, Note S1 ...) are listed as what to look for.
Links: the publisher's SI location for the article.  File names follow each publisher's pattern where it is
fixed (Wiley <article>-sup-0001..., Elsevier 1-s2.0-<PII>-mmc1..., RSC <article>1.pdf, ACS <code>_si_001.pdf,
Springer Nature ..._MOESM1_ESM.pdf); the PII comes from Crossref (cached in si_read/crossref_pii.json).
Records whose article page loaded and showed no SI link (si_public_log NO_SI_LINK_ON_PAGE) are marked for the
v5 D10 check: whether any SI exists.  Nothing here decides eligibility.
"""
import argparse
import csv
import html
import json
import pathlib
import re
import time
import urllib.request

from current_state import adjudicated_row, si_adjudications, triage_a
from reconcile import rows
from retrieve_si_public import has_document

HERE = pathlib.Path(__file__).resolve().parent
PUB = {"10.1002": "Wiley", "10.1016": "Elsevier", "10.1039": "RSC", "10.1021": "ACS", "10.1038": "Nature",
       "10.1007": "Springer", "10.1149": "ECS", "10.1088": "IOP", "10.1063": "AIP", "10.1103": "APS", "10.3390": "MDPI",
       "10.1073": "PNAS", "10.1126": "Science", "10.1080": "Taylor & Francis", "10.26434": "ChemRxiv",
       "10.21203": "Research Square", "10.48550": "arXiv", "10.1360": "Science China", "10.1186": "BMC",
       "10.3389": "Frontiers", "10.1515": "De Gruyter", "10.1093": "Oxford", "10.1142": "World Scientific",
       "10.1166": "ASP", "10.1155": "Hindawi", "10.1246": "Chem. Soc. Japan", "10.20517": "OAE",
       "10.1557": "MRS/Springer", "10.1134": "Pleiades", "10.20944": "Preprints.org", "10.1117": "SPIE", "10.26599": "Tsinghua Univ. Press", "10.1051": "EDP"}
SI_ITEM = re.compile(r"\b(?:Supplementary |Supporting )?(?:Fig(?:ure)?s?\.?|Tables?|Notes?|Eqs?\.?|Sections?)\s*(?-i:S)\s?\d+[a-z]?"
                     r"(?:\s*(?:[-–,]|and)\s*(?-i:S)?\s?\d+[a-z]?)*", re.I)
CRIT = ("E1", "E2", "E3", "E4", "E5", "E6")


def jsonl(p):
    return {json.loads(l)["screen_id"]: json.loads(l) for l in open(p, encoding="utf-8") if l.strip()} if p.exists() else {}


def deciding(st, p1, p2, t3, v4, v5, v4s):
    s, sid = st["v5_source"], st["screen_id"]
    if s.startswith("SI read"):
        d = HERE / "si_read"
        if "third read" in s:
            rs = [jsonl(d / "third_read.jsonl")[sid]]
        else:
            rs = [jsonl(d / ("pass_%s.jsonl" % n))[sid] for n in ("1", "2")]
        if "v5 triage A" in s:
            rs = [triage_a(sid, x) for x in rs]
        ruling = si_adjudications().get(sid)
        return [adjudicated_row(x, ruling) for x in rs] if ruling else rs
    if "v5 triage A" in s:
        base = v5.get(sid) or t3.get(sid)
        return [triage_a(sid, base)] if base else []
    if s == "v5 read":
        return [v5[sid]]
    if s.startswith("third read"):
        return [t3[sid]] if sid in t3 else []
    if s == "v4 read":
        return [v4[sid]]
    if s == "v4 sensitivity read":
        return [v4s[sid]] if sid in v4s else []
    return [x for x in (p1.get(sid), p2.get(sid)) if x]


def verdicts(rs):
    """Each criterion's verdict when the deciding rows agree, else 'SPLIT'."""
    out = {}
    for c in CRIT:
        vs = {(x.get(c) or {}).get("v") for x in rs}
        out[c] = vs.pop() if len(vs) == 1 else "SPLIT"
    return out


def tier(v, forced):
    if forced:
        return 1
    ok = lambda cs: all(v[c] in ("YES",) or (c == "E2" and v[c] == "UNCLEAR") for c in cs)
    if ok(CRIT[:5]) and v["E6"] == "UNCLEAR":
        return 1
    if ok(CRIT[:4]) and v["E5"] == "UNCLEAR":
        return 2
    if ok(CRIT[:3]) and v["E4"] == "UNCLEAR":
        return 3
    return 4


def pii(doi, cache):
    if doi not in cache:
        req = urllib.request.Request("https://api.crossref.org/works/" + doi, headers={"User-Agent": "sts-plit/1.0"})
        try:
            m = json.load(urllib.request.urlopen(req, timeout=30))["message"]
            cache[doi] = next((a for a in m.get("alternative-id", []) if re.match(r"S\d{4}", a)), "")
        except Exception:
            cache[doi] = ""
        time.sleep(1)
    return cache[doi]


def where(doi, pub, cache):
    """(link to the SI location, the file to download)."""
    suffix = doi.split("/", 1)[1]
    if pub == "Wiley":
        return ("https://onlinelibrary.wiley.com/doi/full/%s#support-information-section" % doi,
                "Supporting Information file(s) %s-sup-0001… (and -sup-0002… if listed)" % suffix.replace(".", ""))
    if pub == "Elsevier":
        p = pii(doi, cache)
        if p:
            return ("https://www.sciencedirect.com/science/article/pii/%s#appsec1" % p,
                    "Appendix A. Supplementary data: 1-s2.0-%s-mmc1 (and mmc2… if listed)" % p)
        return "https://doi.org/" + doi, "Appendix A. Supplementary data (mmc1…)"
    if pub == "RSC":
        return "https://doi.org/" + doi, "Electronic supplementary information (ESI): %s1.pdf" % suffix.lower()
    if pub == "ACS":
        return ("https://pubs.acs.org/doi/suppl/" + doi, "Supporting Information PDF (…_si_001.pdf; also _si_002… if listed)")
    if pub == "Nature":
        return ("https://www.nature.com/articles/%s#Sec-supplementary-information" % suffix,
                "Supplementary Information PDF (…_MOESM1_ESM.pdf)")
    return "https://doi.org/" + doi, "the Supplementary Information / Supporting Information file(s)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    forced = set(filter(None, ap.parse_args().ids.split(",")))
    p1, p2 = rows("1"), rows("2")
    t3 = jsonl(HERE / "third_read" / "third_read.jsonl")
    v4, v5 = jsonl(HERE / "v4_read" / "v4_read.jsonl"), jsonl(HERE / "v5_read" / "v5_read.jsonl")
    v4s = jsonl(HERE / "v4s_read" / "v4s_read.jsonl")
    title = {r["screen_id"]: r["title"] for r in csv.DictReader(open(HERE / "reconcile" / "version_groups.csv", encoding="utf-8"))}
    no_link = {json.loads(l)["screen_id"] for l in open(HERE / "si_public_log.jsonl", encoding="utf-8")
               if '"NO_SI_LINK_ON_PAGE"' in l}
    blocked = {json.loads(l)["screen_id"] for l in open(HERE / "si_public_log.jsonl", encoding="utf-8") if '"BLOCKED"' in l}
    dates = {r["screen_id"]: r for r in csv.DictReader(open(HERE / "reconcile" / "date_check.csv", encoding="utf-8"))}
    cp = HERE / "si_read" / "crossref_pii.json"
    cp.parent.mkdir(exist_ok=True)
    cache = json.load(open(cp)) if cp.exists() else {}
    out = []
    for st in csv.DictReader(open(HERE / "reconcile" / "current_state.csv", encoding="utf-8")):
        sid = st["screen_id"]
        if not (st["v5_final"] in ("NEEDS_SI", "UNRESOLVED") or sid in forced) or has_document(sid):
            continue
        rs = deciding(st, p1, p2, t3, v4, v5, v4s)
        v = verdicts(rs)
        dc = dates.get(sid) or {}
        if v["E2"] == "UNCLEAR" and dc.get("first_publication") and not dc.get("flag"):
            v["E2"] = "YES"  # settled by the date check, as in current_state.py
        blob = " ".join(json.dumps({c: x.get(c) for c in CRIT}, ensure_ascii=False) + " " + (x.get("note") or "") for x in rs)
        items = sorted({re.sub(r"\s+", " ", m.group(0)).strip() for m in SI_ITEM.finditer(blob)})
        pub = PUB.get(st["doi"].split("/")[0], st["doi"].split("/")[0])
        link, file = where(st["doi"], pub, cache)
        open_c = [c for c in CRIT if v[c] not in ("YES",)]
        out.append(dict(tier=tier(v, sid in forced), screen_id=sid, publisher=pub, doi=st["doi"], v5_final=st["v5_final"],
                        open_criteria=" ".join("%s %s" % (c, v[c]) for c in open_c), si_items=", ".join(items),
                        si_link=link, file=file, d10_check=sid in no_link, publisher_page_blocked=sid in blocked,
                        date_check_needed=v["E2"] == "UNCLEAR", title=title.get(sid, "")))
    json.dump(cache, open(cp, "w"), indent=1)
    out.sort(key=lambda r: (r["tier"], r["publisher"], r["screen_id"]))
    with open(HERE / "si_checklist.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    write_html(out)
    tiers = {}
    for r in out:
        tiers[r["tier"]] = tiers.get(r["tier"], 0) + 1
    print(len(out), "records; tiers", dict(sorted(tiers.items())), "; D10 checks", sum(r["d10_check"] for r in out))


TIER_TEXT = {1: "The SI decides eligibility", 2: "The SI states the facet, then decides the overpotential",
             3: "The SI may establish rutile for the model", 4: "Useful, but the SI cannot settle the record by itself"}


def write_html(out):
    e = html.escape
    rows_html = []
    for t in (1, 2, 3, 4):
        grp = [r for r in out if r["tier"] == t]
        if not grp:
            continue
        rows_html.append('<tr class="h"><td colspan="7">Priority %d: %s (%d)</td></tr>' % (t, TIER_TEXT[t], len(grp)))
        for r in grp:
            extra = []
            if r["d10_check"]:
                extra.append("<b>The article page showed no SI link on 2026-09-27. Check whether any SI exists; if none, say so.</b>")
            if r["v5_final"] == "ELIGIBLE":
                extra.append("Currently ELIGIBLE, with an open question in the v5 triage (reconcile/v5_questions_triage.md); "
                             "the SI can settle it before the freeze.")
            if r["si_items"]:
                extra.append("Look for: " + e(r["si_items"]))
            rows_html.append(
                '<tr><td><input type="checkbox" data-id="%s"></td><td>%s</td><td>%s</td><td><a href="%s" target="_blank">SI location</a><br><small>%s</small></td>'
                '<td>%s<br><small>%s</small></td><td>%s</td><td>%s</td></tr>' % (
                    r["screen_id"], e(r["publisher"]), r["screen_id"], e(r["si_link"]), e(r["doi"]), e(r["file"]),
                    "<br>".join(extra), e(r["open_criteria"]), e(r["title"][:140])))
    doc = """<!doctype html><meta charset="utf-8"><title>SI downloads</title>
<style>body{font:14px system-ui;margin:16px;max-width:1200px}td{padding:4px 8px;border-bottom:1px solid #ddd;vertical-align:top}
tr.h td{background:#eef;font-weight:600;padding-top:10px}tr.done td{color:#999}li{margin:3px 0}#n{font-weight:600}</style>
<h2>%d papers whose supporting information is still missing</h2>
<ol>
<li>Click "SI location". It opens the paper's supplementary section, not the article PDF. Download the SI file named in the row; article-identity or missing-main-text issues are tracked separately.</li>
<li>Use the public SI links. If access is blocked or a page asks for institutional login, leave the row open and report the access result.</li>
<li>Keep the default file name and the Downloads folder. The script matches each file by the article code in its name, or by the title printed on it.</li>
<li>If the page lists several SI files, download each PDF or Word file and any source-data spreadsheet or structure file needed for the named open criterion. Skip videos unless the row specifically needs them.</li>
<li>If the page shows no SI at all, tick the box and write "no SI" next to the ID in your message. That is evidence for the verified-no-SI rule (D10).</li>
<li>Go at a normal pace, one at a time. Priority 1 first: those files decide eligibility directly.</li>
<li>Tick the box when a paper is done (ticks are kept only in this browser). Send the completed IDs when you are finished, or partway.</li>
</ol>
<p><span id="n"></span></p>
<table><tr><th>Done</th><th>Publisher</th><th>ID</th><th>Link</th><th>File to download</th><th>Open criteria</th><th>Title</th></tr>
%s
</table>
<script>
const k="si_checklist_done";let d={};try{d=JSON.parse(localStorage.getItem(k)||"{}")}catch(e){}
function upd(){let n=0;document.querySelectorAll("input[data-id]").forEach(b=>{b.closest("tr").className=b.checked?"done":"";if(b.checked)n++});
document.getElementById("n").textContent=n+" of %d done"}
document.querySelectorAll("input[data-id]").forEach(b=>{b.checked=!!d[b.dataset.id];b.onchange=()=>{d[b.dataset.id]=b.checked;try{localStorage.setItem(k,JSON.stringify(d))}catch(e){};upd()}});upd();
</script>
""" % (len(out), "\n".join(rows_html), len(out))
    (HERE / "si_checklist.html").write_text(doc, encoding="utf-8")


if __name__ == "__main__":
    main()
