"""Retrieve one declared PMC media file for a read-only eligibility figure check.

Uses NLM's public Cloud Service metadata, checks DOI and the declared MD5,
and preserves reading copies locally. No browser, institutional access or keys.
The service layout is documented at https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/
and https://pmc-oa-opendata.s3.amazonaws.com/README.txt (checked 2026-09-29).
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
BASE = "https://pmc-oa-opendata.s3.amazonaws.com/"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "sts-plit-figure-review/1.0"})
    with urllib.request.urlopen(req, timeout=30) as fh:
        return fh.read()


def main(sid, filename):
    if Path(filename).name != filename or Path(filename).suffix.lower() not in (".pdf", ".jpg", ".png", ".gif"):
        raise ValueError("Specify one PDF or image basename")
    st = next(r for r in csv.DictReader((HERE / "reconcile/current_state.csv").open(encoding="utf-8"))
              if r["screen_id"] == sid)
    xml = ET.parse(HERE / "files" / (sid + ".xml"))
    pmcid = xml.findtext('.//article-id[@pub-id-type="pmcid"]')
    version = xml.findtext('.//article-id[@pub-id-type="pmcid-ver"]') or pmcid + ".1"
    metadata_url = BASE + version + "/" + version + ".json"
    meta = json.loads(get(metadata_url))
    if meta["doi"].lower() != st["doi"].lower():
        raise ValueError("DOI mismatch; do not use these media")
    urls = meta.get("media_urls", []) + ([meta["pdf_url"]] if meta.get("pdf_url") else [])
    declared = next(u for u in urls if Path(urllib.parse.urlsplit(u).path).name == filename)
    url = declared.replace("s3://pmc-oa-opendata/", BASE)
    body = get(url)
    md5 = hashlib.md5(body).hexdigest()
    expected = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)["md5"][0]
    if md5 != expected:
        raise ValueError("Declared media MD5 mismatch")
    dest = HERE / "si_read" / "visual_review" / sid
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / filename
    if path.exists() and path.read_bytes() != body:
        raise ValueError("Existing reading copy differs; preserve it")
    if not path.exists():
        path.write_bytes(body)
    record = dict(screen_id=sid, doi=meta["doi"], pmc_version=version, license_code=meta.get("license_code"),
                  is_manuscript=meta.get("is_manuscript"), metadata_url=metadata_url, media_url=url,
                  md5=md5, sha256=hashlib.sha256(body).hexdigest(), bytes=len(body),
                  file=str(path.relative_to(HERE)).replace("\\", "/"),
                  source="NIH NLM NCBI PubMed Central Article Datasets on AWS, accessed 2026-09-29")
    sidecar = path.with_suffix(path.suffix + ".json")
    sidecar.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("screen_id")
    ap.add_argument("filename")
    args = ap.parse_args()
    main(args.screen_id, args.filename)
