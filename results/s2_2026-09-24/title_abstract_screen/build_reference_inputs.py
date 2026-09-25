"""Build screening inputs for the DOIs that the one-generation reference pass added to the union.

The 2026-09-23 reference identity pass resolved 238 DOIs that are not in the provider union
(`summary.json` -> `new_to_union_dois`).  This script gives them the same lean screening view as
the union's chunks, so both passes screen them under the same instructions:

  reference_inputs/chunk_ref.jsonl      one record per DOI, screen_id R0001.. in sorted-DOI order
  reference_inputs/raw/openalex_*.json  raw OpenAlex responses (filter=doi:..., 50 DOIs per request)
  reference_inputs/manifest.json        input hashes, request receipts, counts

Title, date, type and venue come from OpenAlex when it has the DOI, else from the Crossref
/works record already saved by the reference pass; the abstract comes from OpenAlex's inverted
index, else Crossref's JATS abstract, else is empty.  These records seed no further expansion.
"""
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_screen_inputs import ABSTRACT_CAP, abstract  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[3]
REF = ROOT / "results/s2_2026-09-23/backward_reference_identity"
OUT = pathlib.Path(__file__).resolve().parent / "reference_inputs"
KEY = pathlib.Path.home() / ".config/openalex/api_key"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def fetch(dois, n):
    params = {"filter": "doi:" + "|".join(dois), "per-page": "200"}
    key = os.environ.get("OPENALEX_API_KEY") or (KEY.read_text().strip() if KEY.exists() else None)
    if key:
        params["api_key"] = key
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params, safe=":|/")
    with urllib.request.urlopen(url, timeout=60) as r:
        body = r.read()
    path = OUT / "raw" / ("openalex_%02d.json" % n)
    path.write_bytes(body)
    shown = re.sub(r"api_key=[^&]+", "api_key=<redacted>", url)
    return json.loads(body), dict(url=shown, raw_path=path.relative_to(ROOT).as_posix(), sha256=sha256(body),
                                  retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat())


def crossref(doi):
    path = REF / "crossref_works" / (doi.replace("/", "__") + ".json")
    if not path.exists():
        return {}
    d = json.loads(path.read_text(encoding="utf-8"))
    return d.get("message", d)


def main():
    (OUT / "raw").mkdir(parents=True, exist_ok=True)
    summary_path = REF / "summary.json"
    dois = sorted(d.lower() for d in json.loads(summary_path.read_text(encoding="utf-8"))["new_to_union_dois"])
    found, receipts = {}, []
    for n, i in enumerate(range(0, len(dois), 50), 1):
        body, receipt = fetch(dois[i:i + 50], n)
        receipts.append(receipt)
        for w in body["results"]:
            if w.get("doi"):
                found[w["doi"].lower().replace("https://doi.org/", "")] = w
        time.sleep(1)
    rows = []
    for k, doi in enumerate(dois, 1):
        w, c = found.get(doi), crossref(doi)
        if w:
            text = abstract(w.get("abstract_inverted_index"))
            src = (w.get("primary_location") or {}).get("source") or {}
            row = dict(title=w.get("title") or "", publication_date=w.get("publication_date") or "",
                       type=w.get("type") or "", venue=src.get("display_name") or "", language=w.get("language") or "",
                       provider_id=w.get("id"), metadata_source="openalex")
        else:
            text = ""
            parts = ((c.get("issued") or {}).get("date-parts") or [[None]])[0]
            row = dict(title=(c.get("title") or [""])[0], publication_date="-".join("%02d" % p if j else str(p)
                       for j, p in enumerate(parts) if p), type=c.get("type") or "",
                       venue=(c.get("container-title") or [""])[0], language=c.get("language") or "",
                       provider_id=None, metadata_source="crossref" if c else "none")
        if not text and c.get("abstract"):
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c["abstract"])).strip()
            row["abstract_source"] = "crossref"
        else:
            row["abstract_source"] = "openalex" if text else "none"
        row["abstract_truncated"] = len(text) > ABSTRACT_CAP
        rows.append(dict(screen_id="R%04d" % k, doi=doi, abstract=text[:ABSTRACT_CAP], **row,
                         membership="REFERENCE_PASS_ONE_GENERATION"))
    chunk = OUT / "chunk_ref.jsonl"
    chunk.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8", newline="\n")
    manifest = dict(recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                    source=dict(path=summary_path.relative_to(ROOT).as_posix(), sha256=sha256(summary_path.read_bytes())),
                    dois=len(dois), openalex_found=len(found), no_openalex=[r["doi"] for r in rows if not r["provider_id"]],
                    with_abstract=sum(bool(r["abstract"]) for r in rows),
                    abstract_sources={s: sum(r["abstract_source"] == s for r in rows) for s in ("openalex", "crossref", "none")},
                    requests=receipts, chunk=dict(path=chunk.relative_to(ROOT).as_posix(), sha256=sha256(chunk.read_bytes())))
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: manifest[k] for k in ("dois", "openalex_found", "with_abstract", "abstract_sources")}))


if __name__ == "__main__":
    main()
