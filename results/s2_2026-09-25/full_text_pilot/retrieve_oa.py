"""Full-text pilot, retrieval step (open-access routes only).

Draws a seeded sample of routed records (25 per pre-screen signal stratum) plus the known-eligible
sentinels, tries every OpenAlex open-access PDF location recorded in the hashed raw pages, and logs
every attempt.  Retrieved files and extracted text stay local (never committed: public repository);
the attempt log with hashes is the committed record.  No eligibility decision is made here.

  python retrieve_oa.py
"""
import csv
import datetime as dt
import hashlib
import json
import pathlib
import random
import time

import fitz
import requests

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCREEN = ROOT / "results/s2_2026-09-24/title_abstract_screen"
SEED, PER_STRATUM = 20260925, 25
UA = {"User-Agent": "Mozilla/5.0 (literature-review retrieval; open-access copies only)"}


def stratum(r):
    labels = {r["label_a"], r["label_b"]}
    if "LIKELY_RELEVANT" in labels:
        return "any_LIKELY"
    if r["label_a"] == r["label_b"] == "POSSIBLY_RELEVANT":
        return "both_POSSIBLY"
    return "rescue" if r["route"] == "FULL_TEXT_REVIEW_RESCUE" else "split"


def oa_locations(sid, ids, pages):
    m = ids.get(sid)
    if not m:
        return []
    page = m["raw_page"]
    if page not in pages:
        pages[page] = json.load(open(ROOT / page, encoding="utf-8"))["results"]
    work = pages[page][int(m["item_index"])]
    urls = []
    for loc in [work.get("best_oa_location")] + (work.get("locations") or []):
        if loc and loc.get("is_oa") and loc.get("pdf_url") and loc["pdf_url"] not in urls:
            urls.append(loc["pdf_url"])
    return urls


def main():
    routes = list(csv.DictReader(open(SCREEN / "passes/merge/merged_routes.csv", encoding="utf-8")))
    routed = [r for r in routes if r["route"].startswith("FULL_TEXT")]
    ids = {r["screen_id"]: r for r in csv.DictReader(open(SCREEN / "screened_identities.csv", encoding="utf-8"))}
    sentinels = json.load(open(SCREEN / "pilot/pilot_key.json"))["known_eligible_sentinels"]
    rng = random.Random(SEED)
    sample = []
    for s in ("any_LIKELY", "both_POSSIBLY", "split", "rescue"):
        pool = sorted((r for r in routed if stratum(r) == s and r["screen_id"] not in sentinels), key=lambda r: r["screen_id"])
        sample += [dict(r, stratum=s) for r in rng.sample(pool, PER_STRATUM)]
    by_id = {r["screen_id"]: r for r in routed}
    sample += [dict(by_id[s], stratum="sentinel") for s in sentinels]
    files, text = HERE / "files", HERE / "text"
    files.mkdir(exist_ok=True)
    text.mkdir(exist_ok=True)
    pages, log, rows = {}, [], []
    for r in sample:
        sid = r["screen_id"]
        got = None
        for url in oa_locations(sid, ids, pages):
            rec = dict(screen_id=sid, url=url, at=dt.datetime.now(dt.timezone.utc).isoformat())
            try:
                resp = requests.get(url, headers=UA, timeout=40, allow_redirects=True)
                body = resp.content
                rec.update(status=resp.status_code, final_url=resp.url, bytes=len(body),
                           content_type=resp.headers.get("content-type", ""), is_pdf=body[:5] == b"%PDF-")
                if rec["is_pdf"]:
                    rec["sha256"] = hashlib.sha256(body).hexdigest()
                    (files / (sid + ".pdf")).write_bytes(body)
                    got = rec
            except Exception as e:  # network failure is a logged outcome, not a crash
                rec.update(status="ERROR", error=type(e).__name__ + ": " + str(e)[:200])
            log.append(rec)
            time.sleep(1)
            if got:
                break
        chars = pages_n = None
        if got:
            try:
                doc = fitz.open(files / (sid + ".pdf"))
                t = "\n".join(p.get_text() for p in doc)
                pages_n, chars = doc.page_count, len(t)
                (text / (sid + ".txt")).write_text(t, encoding="utf-8")
            except Exception as e:
                chars = "EXTRACT_ERROR: " + type(e).__name__
        rows.append(dict(screen_id=sid, stratum=r["stratum"], doi=r["doi"], title=r["title"][:200],
                         retrieved=bool(got), pdf_sha256=(got or {}).get("sha256", ""),
                         pages=pages_n, text_chars=chars, attempts=sum(1 for x in log if x["screen_id"] == sid)))
    with open(HERE / "retrieval_log.jsonl", "w", encoding="utf-8", newline="\n") as f:
        f.writelines(json.dumps(x) + "\n" for x in log)
    with open(HERE / "sample.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    by = {}
    for x in rows:
        b = by.setdefault(x["stratum"], [0, 0])
        b[0] += 1
        b[1] += x["retrieved"]
    sizes = sorted(x["text_chars"] for x in rows if isinstance(x["text_chars"], int))
    summary = dict(recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(), seed=SEED, sample=len(rows),
                   retrieved_by_stratum=by, attempts=len(log),
                   text_chars_median=sizes[len(sizes) // 2] if sizes else None,
                   text_chars_p90=sizes[int(len(sizes) * 0.9)] if sizes else None)
    json.dump(summary, open(HERE / "retrieval_summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
