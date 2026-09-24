"""Build the title/abstract screening inputs for the full OpenAlex provider-identity union.

Deterministic, offline: reads the 2026-09-22 identity handoff and the hashed raw OpenAlex
pages it points to; makes no network request and changes no existing file.  Outputs:

  inputs/chunk_NNN.jsonl   lean screening view (one record per identity, 1,000 per chunk)
  screened_identities.csv  full record of every identity screened: DOI, title, date, type,
                           venue, authors, query membership and the raw-page locator
  manifest.json            input hashes, counts, chunk hashes

These are discovery records only.  Eligibility is decided later; method fields stay NOT_CODED.
"""
import csv
import datetime as dt
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HANDOFF = ROOT / "results/s2_2026-09-22/identity_handoff/provider_identity_union.jsonl"
OUT = pathlib.Path(__file__).resolve().parent
CHUNK = 1000
ABSTRACT_CAP = 4000  # characters; longer abstracts are cut and flagged


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def abstract(inverted):
    if not inverted:
        return ""
    slots = {}
    for word, positions in inverted.items():
        for p in positions:
            slots[p] = word
    return " ".join(slots[i] for i in sorted(slots))


def main():
    handoff_sha = sha256(HANDOFF)
    identities = [json.loads(line) for line in open(HANDOFF, encoding="utf-8")]
    identities.sort(key=lambda r: r["provider_id"])
    # read each raw page once: hash it, then pick out the items the identities point to
    wanted = {}
    for ident in identities:
        v = ident["metadata_variants"][0]
        wanted.setdefault(v["raw_page"], set()).add(v["item_index"])
    page_hash_ok, items = {}, {}
    for page, indices in wanted.items():
        page_hash_ok[page] = sha256(ROOT / page)
        results = json.load(open(ROOT / page, encoding="utf-8"))["results"]
        for i in indices:
            items[(page, i)] = results[i]
    records, rows = [], []
    for n, ident in enumerate(identities, 1):
        variant = ident["metadata_variants"][0]
        if page_hash_ok[variant["raw_page"]] != variant["raw_sha256"]:
            sys.exit("raw page hash mismatch: %s" % variant["raw_page"])
        full = items[(variant["raw_page"], variant["item_index"])]
        if full["id"] != ident["provider_id"]:
            sys.exit("raw item does not match identity: %s" % ident["provider_id"])
        text = abstract(full.get("abstract_inverted_index"))
        truncated = len(text) > ABSTRACT_CAP
        source = ((full.get("primary_location") or {}).get("source") or {})
        authors = [((a.get("author") or {}).get("display_name") or "") for a in full.get("authorships") or []]
        doi = (full.get("doi") or "").replace("https://doi.org/", "") or None
        sid = "S%05d" % n
        records.append(dict(
            screen_id=sid, provider_id=ident["provider_id"], doi=doi,
            title=full.get("display_name") or full.get("title") or "",
            publication_date=full.get("publication_date"), type=full.get("type"),
            venue=source.get("display_name"), language=full.get("language"),
            abstract=text[:ABSTRACT_CAP], abstract_available=bool(text), abstract_truncated=truncated))
        rows.append(dict(
            screen_id=sid, provider_id=ident["provider_id"], doi=doi or "",
            title=full.get("display_name") or "", publication_date=full.get("publication_date") or "",
            type=full.get("type") or "", venue=source.get("display_name") or "",
            first_author=authors[0] if authors else "", author_count=len(authors),
            language=full.get("language") or "", abstract_available=bool(text),
            membership=ident["membership"],
            query_indices=";".join(str(q) for q in sorted(set(ident["old_query_indices"]) | set(ident["new_query_indices"]))),
            raw_page=variant["raw_page"], item_index=variant["item_index"], raw_sha256=variant["raw_sha256"]))
    (OUT / "inputs").mkdir(exist_ok=True)
    chunks = []
    for i in range(0, len(records), CHUNK):
        path = OUT / "inputs" / ("chunk_%03d.jsonl" % (i // CHUNK + 1))
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for r in records[i:i + CHUNK]:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        chunks.append(dict(file=path.name, first=records[i]["screen_id"],
                           last=records[min(i + CHUNK, len(records)) - 1]["screen_id"],
                           count=len(records[i:i + CHUNK]), sha256=sha256(path)))
    with open(OUT / "screened_identities.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    manifest = dict(
        recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        scope="Title/abstract screening inputs for the full 2026-09-22 provider-identity union; discovery records only, no eligibility decision, methods NOT_CODED",
        handoff=dict(path=str(HANDOFF.relative_to(ROOT)).replace("\\", "/"), sha256=handoff_sha),
        identities=len(records), with_doi=sum(1 for r in records if r["doi"]),
        with_abstract=sum(1 for r in records if r["abstract_available"]),
        abstracts_truncated=sum(1 for r in records if r["abstract_truncated"]),
        raw_pages_verified=len(page_hash_ok), chunk_size=CHUNK, chunks=chunks,
        screened_identities_csv_sha256=sha256(OUT / "screened_identities.csv"))
    json.dump(manifest, open(OUT / "manifest.json", "w", encoding="utf-8"), indent=2)
    print(json.dumps({k: v for k, v in manifest.items() if k != "chunks"}, indent=2), len(chunks), "chunks")


if __name__ == "__main__":
    main()
