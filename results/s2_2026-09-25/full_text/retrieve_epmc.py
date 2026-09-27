"""Full-text retrieval through Europe PMC (open-access copies deposited in PMC).

For every record with a DOI and no file yet: look the DOI up in the Europe PMC search API and,
when the article has an open-access PMC copy, fetch its JATS full text into files/<sid>.xml
(ft_screen.py extract already reads JATS).  Mainly for MDPI, whose own site answers scripted
requests with a challenge page, but any publisher's PMC copy is taken.  Requests are spaced
0.5 s apart.  Every attempt goes to retrieval_log.jsonl with route "epmc".

  python retrieve_epmc.py [--limit N]
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import time
import urllib.parse
import urllib.request

from retrieve_http import load_records

HERE = pathlib.Path(__file__).resolve().parent
FILES = HERE / "files"
API = "https://www.ebi.ac.uk/europepmc/webservices/rest/"


def log(entry):
    entry["at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    with open(HERE / "retrieval_log.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry) + "\n")


def get(url):
    time.sleep(0.5)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sts-plit-screen"}), timeout=60) as r:
        return r.read()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None)
    a = p.parse_args()
    have = {f.stem for f in FILES.iterdir()}
    todo = [r for r in load_records() if r["doi"] and r["screen_id"] not in have][: a.limit]
    print(len(todo), "records without a file", flush=True)
    got = 0
    for r in todo:
        sid, doi = r["screen_id"], r["doi"]
        try:
            q = urllib.parse.quote('DOI:"%s"' % doi)
            hits = json.loads(get(API + "search?query=%s&format=json&resultType=lite" % q))["resultList"]["result"]
            hit = next((h for h in hits if h.get("pmcid") and h.get("isOpenAccess") == "Y"), None)
            if not hit:
                log(dict(screen_id=sid, route="epmc", url=doi, status="NO_OA_PMC", accepted=False))
                continue
            body = get(API + "%s/fullTextXML" % hit["pmcid"])
        except Exception as e:
            log(dict(screen_id=sid, route="epmc", url=doi, status="ERROR", accepted=False, error=str(e)[:160]))
            continue
        ok = b"<body" in body
        entry = dict(screen_id=sid, route="epmc", url=hit["pmcid"], status=200, bytes=len(body), accepted=ok)
        if ok:
            entry["sha256"] = hashlib.sha256(body).hexdigest()
            (FILES / (sid + ".xml")).write_bytes(body)
            got += 1
        log(entry)
        print(sid, hit["pmcid"], "OK" if ok else "no body", flush=True)
    print(got, "of", len(todo), "retrieved from Europe PMC")


if __name__ == "__main__":
    main()
