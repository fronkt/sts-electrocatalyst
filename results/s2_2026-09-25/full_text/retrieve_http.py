"""Full-text retrieval, scripted routes (see docs/research/full-text-access-amendment-2026-09-25.md).

For every record the pre-screen routed to full text, and every journal version in VERSION_PRIMARY, in
priority order (records with a LIKELY label first, then both-POSSIBLY, split, safety-net, version primaries),
try in turn:
  1. OpenAlex open-access PDF locations (from the hashed raw pages)
  2. Unpaywall open-access locations (contact address sent as the API requires; redacted in the log)
  3. Europe PMC full-text XML (when the work has a PMCID)
A PDF is accepted only if it starts with %PDF-; Europe PMC XML is accepted if it contains a <body>.
Resumable: records that already have a file are skipped.  Files stay local (public repository);
the attempt log (retrieval_log.jsonl) and status table (status.csv) are the committed record.
Records not reached here go to the browser queue (Sci-Hub, then Purdue institutional access).

  python retrieve_http.py [--limit N] [--workers 6]
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import pathlib
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCREEN = ROOT / "results/s2_2026-09-24/title_abstract_screen"
EMAIL_FILE = pathlib.Path.home() / ".config/unpaywall/email"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"}
PRIORITY = {"any_LIKELY": 0, "both_POSSIBLY": 1, "split": 2, "rescue": 3, "version_primary": 4}
# Journal versions the pre-screen excluded although a live full-text record collapses into them (version linking
# counts the work through its journal version).  Entrant, 2026-09-28: "A missing DOI does not itself disqualify the
# published version; establish its identity and screen it."  Identity: DOI, venue and date from Crossref.
VERSION_PRIMARY = {"S27700": "journal version of S25842 (Crossref has-preprint 10.21203/rs.3.rs-6646407/v1; "
                             "S25842 names it as its Version of Record)"}
FILES = HERE / "files"
LOCK = threading.Lock()


def stratum(r):
    if r["screen_id"] in VERSION_PRIMARY:
        return "version_primary"
    labels = {r["label_a"], r["label_b"]}
    if "LIKELY_RELEVANT" in labels:
        return "any_LIKELY"
    if r["label_a"] == r["label_b"] == "POSSIBLY_RELEVANT":
        return "both_POSSIBLY"
    return "rescue" if r["route"] == "FULL_TEXT_REVIEW_RESCUE" else "split"


def load_records():
    routes = [r for r in csv.DictReader(open(SCREEN / "passes/merge/merged_routes.csv", encoding="utf-8"))
              if r["route"].startswith("FULL_TEXT") or r["screen_id"] in VERSION_PRIMARY]
    ids = {r["screen_id"]: r for r in csv.DictReader(open(SCREEN / "screened_identities.csv", encoding="utf-8"))}
    pages, out = {}, []
    for r in routes:
        rec = dict(screen_id=r["screen_id"], doi=r["doi"].lower(), title=r["title"], stratum=stratum(r),
                   oa_pdfs=[], pmcid=None)
        m = ids.get(r["screen_id"])
        if m:
            page = m["raw_page"]
            if page not in pages:
                pages[page] = json.load(open(ROOT / page, encoding="utf-8"))["results"]
            w = pages[page][int(m["item_index"])]
            for loc in [w.get("best_oa_location")] + (w.get("locations") or []):
                if loc and loc.get("is_oa") and loc.get("pdf_url") and loc["pdf_url"] not in rec["oa_pdfs"]:
                    rec["oa_pdfs"].append(loc["pdf_url"])
            pmcid = (w.get("ids") or {}).get("pmcid")
            rec["pmcid"] = pmcid.rstrip("/").split("/")[-1] if pmcid else None
        out.append(rec)
    out.sort(key=lambda x: (PRIORITY[x["stratum"]], x["screen_id"]))
    return out


def log(entry):
    with LOCK, open(HERE / "retrieval_log.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry) + "\n")


def fetch(sid, route, url, params=None, accept="pdf"):
    entry = dict(screen_id=sid, route=route, url=url, at=dt.datetime.now(dt.timezone.utc).isoformat())
    try:
        resp = requests.get(url, params=params, headers=UA, timeout=45, allow_redirects=True)
        body = resp.content
        ok = body[:5] == b"%PDF-" if accept == "pdf" else (resp.ok and b"<body" in body)
        entry.update(status=resp.status_code, final_url=resp.url.split("?")[0], bytes=len(body),
                     content_type=resp.headers.get("content-type", ""), accepted=ok)
        if ok:
            entry["sha256"] = hashlib.sha256(body).hexdigest()
        log(entry)
        return body if ok else None, resp
    except Exception as e:
        entry.update(status="ERROR", accepted=False, error=type(e).__name__ + ": " + str(e)[:160])
        log(entry)
        return None, None


def retrieve(rec, email):
    sid = rec["screen_id"]
    if list(FILES.glob(sid + ".*")):
        return
    for url in rec["oa_pdfs"]:
        body, _ = fetch(sid, "openalex_oa", url)
        if body:
            (FILES / (sid + ".pdf")).write_bytes(body)
            return
        time.sleep(0.5)
    if rec["doi"] and email:
        entry = dict(screen_id=sid, route="unpaywall_lookup", url="https://api.unpaywall.org/v2/" + rec["doi"],
                     at=dt.datetime.now(dt.timezone.utc).isoformat())
        try:
            r = requests.get(entry["url"], params={"email": email}, timeout=30)
            locs = r.json().get("oa_locations", []) if r.ok else []
            entry.update(status=r.status_code, locations=len(locs))
        except Exception as e:
            locs = []
            entry.update(status="ERROR", error=type(e).__name__)
        log(entry)
        tried = set(rec["oa_pdfs"])
        for loc in locs:
            for url in (loc.get("url_for_pdf"), loc.get("url")):
                if url and url not in tried:
                    tried.add(url)
                    body, _ = fetch(sid, "unpaywall_oa", url)
                    if body:
                        (FILES / (sid + ".pdf")).write_bytes(body)
                        return
                    time.sleep(0.5)
    if rec["pmcid"]:
        body, _ = fetch(sid, "europepmc_xml",
                        "https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML" % rec["pmcid"], accept="xml")
        if body:
            (FILES / (sid + ".xml")).write_bytes(body)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--workers", type=int, default=6)
    a = p.parse_args()
    FILES.mkdir(exist_ok=True)
    email = EMAIL_FILE.read_text().strip() if EMAIL_FILE.exists() else None
    recs = load_records()[: a.limit]
    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(lambda r: retrieve(r, email), recs))
    got = {f.stem: f.suffix for f in FILES.iterdir()}
    with open(HERE / "status.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["screen_id", "doi", "stratum", "retrieved", "format"])
        for r in load_records():
            w.writerow([r["screen_id"], r["doi"], r["stratum"], r["screen_id"] in got, got.get(r["screen_id"], "")])
    print(len(recs), "records processed;", sum(1 for r in recs if r["screen_id"] in got), "retrieved")


if __name__ == "__main__":
    main()
