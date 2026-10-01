"""Recover linked public Cambridge SI files, validate repository identity/checksums.

Never follows publisher or institutional routes and never assigns eligibility.
"""
import hashlib
import json
import pathlib
import time
import urllib.parse

import fitz
import requests

from si_read import Record

HERE = pathlib.Path(__file__).resolve().parent
D = HERE / "evidence_recovery_2026-10-01"
API = "https://api.repository.cam.ac.uk/server/api/core/"
ITEM = "4e54b534-55e3-45b7-8d50-0e581701e534"
BUNDLE = "88807a21-0bec-4975-9867-3619626d29e5"
TITLE = "Decoupling the catalytic and degradation mechanisms of cobalt active sites during acidic water oxidation"
DOI = "10.1038/s41560-025-01812-x"


def get(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "api.repository.cam.ac.uk":
        raise ValueError("Unexpected repository URL")
    time.sleep(1)
    r = requests.get(url, timeout=45, allow_redirects=False)
    r.raise_for_status()
    if r.status_code != 200:
        raise ValueError("Unexpected repository redirect")
    return r


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    meta_path = D / "s26375_recovery.json"
    if meta_path.exists():
        print("Existing verified recovery retained; no repeated requests")
        return
    item = get(API + "items/" + ITEM).json()
    metadata = item["metadata"]
    if metadata["dc.title"][0]["value"] != TITLE or not any(
            v["value"] == DOI.split("/")[1] for v in metadata["dc.identifier.other"]):
        raise ValueError("Cambridge item title/article identifier mismatch")
    hits = get(API + "bundles/" + BUNDLE + "/bitstreams").json()["_embedded"]["bitstreams"]
    names = {"41560_2025_1812_MOESM1_ESM.pdf", "additional-files.zip"}
    files = [f for f in hits if f["name"] in names]
    if {f["name"] for f in files} != names:
        raise ValueError("Expected linked SI files missing")
    dest = D / "files" / "S26375"
    dest.mkdir(parents=True, exist_ok=True)
    recovered, rec = [], Record()
    for f in files:
        # The existing extractor's file/page markers expect <sid>_SI<k> names.
        p = dest / ("S26375_SI1.pdf" if f["name"].endswith(".pdf") else "S26375_SI2.zip")
        legacy = dest / f["name"]
        cached = p if p.exists() else legacy
        body = cached.read_bytes() if cached.exists() else get(f["_links"]["content"]["href"]).content
        checksum = f.get("checkSum") or f.get("checksum")
        if not checksum or checksum["checkSumAlgorithm"].lower() != "md5" or hashlib.md5(body).hexdigest() != checksum["value"]:
            raise ValueError("Repository MD5 mismatch or missing")
        if p.suffix == ".pdf":
            doc = fitz.open(stream=body, filetype="pdf")
            if "Decoupling the catalytic" not in doc[0].get_text():
                raise ValueError("SI title mismatch")
        if not p.exists():
            p.write_bytes(body)
        rec.add(p, f["name"])
        recovered.append({"file": p.relative_to(HERE).as_posix(), "published_name": f["name"], "sha256": sha(p),
                          "bytes": len(body), "md5": checksum["value"],
                          "download_url": f["_links"]["content"]["href"]})
    text = dest / "si.txt"
    if text.exists():
        raise ValueError("Do not overwrite existing extraction")
    text.write_text("\n\n".join(rec.chunks) + "\n", encoding="utf-8")
    meta = {"screen_id": "S26375", "doi": DOI, "status": "IDENTITY_VERIFIED",
            "record_url": "https://www.repository.cam.ac.uk/handle/1810/388600",
            "item_api": API + "items/" + ITEM, "bundle_api": API + "bundles/" + BUNDLE + "/bitstreams",
            "files": recovered, "text": text.relative_to(HERE).as_posix(), "text_sha256": sha(text),
            "si_complete": not rec.incomplete, "incomplete": rec.incomplete, "pages": rec.pages,
            "main": "text/S26375.txt", "main_sha256": sha(HERE / "text" / "S26375.txt"),
            "identity": "Cambridge title/article identifier and SI title match; files are linked in the article bundle and MD5 verified."}
    meta_path.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    for n in (1, 2):
        inp = D / ("s26375_pass%d.in.jsonl" % n)
        inp.write_text(json.dumps({"screen_id": "S26375", "doi": DOI, "text": meta["main"],
                                   "si_text": meta["text"], "si_complete": meta["si_complete"],
                                   "si_files": [q["file"] for q in recovered], "facts": []}) + "\n", encoding="utf-8")
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
