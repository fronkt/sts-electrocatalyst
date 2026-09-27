"""Picks up the hand-downloaded priority papers (manual_priority.csv) whatever their file names.

  python ingest_manual.py [--src DIR ...] [--since 2026-09-27]
  python ingest_manual.py --place

Looks at PDFs in the source folders (default: files_manual/ and ~/Downloads; only files modified on or
after --since), reads the first two pages, and matches each PDF to a record by the DOI printed on it,
with the title as a fallback.  A match is copied to files_manual/<screen_id>.pdf; the downloaded file is
left where it is.  Every copy goes to manual_ingest_log.jsonl (source name, sha256, how it matched).
Prints which records are in, which PDFs matched nothing, and which records are still missing.
Nothing here reads beyond page 2 or decides eligibility.

--place (after the matches have been checked) copies each files_manual/<screen_id>.pdf into files/, where
ft_screen.py extract picks it up, for records that have no file there yet, and logs route "manual_purdue"
to retrieval_log.jsonl like every other retrieval route.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys

import fitz

HERE = pathlib.Path(__file__).resolve().parent
DEST = HERE / "files_manual"
LOG = HERE / "manual_ingest_log.jsonl"


def squash(s):
    return re.sub(r"\s+", "", s).lower()


def letters(s):
    # letters only: accepted manuscripts put line numbers inside the title, and sub/superscripts split words
    return re.sub(r"[^a-z]", "", s.lower())


def wanted():
    return {r["screen_id"]: r for r in csv.DictReader(open(HERE / "manual_priority.csv", encoding="utf-8"))}


def keys(doi):
    """Strings that identify the record in page text: the DOI, and its suffix when distinctive
    (Elsevier prints the PII, e.g. S1872-2067(26)64993-5, on pages that omit the DOI)."""
    d = doi.lower()
    suffix = d.split("/", 1)[1]
    return [d] + ([suffix] if len(suffix) >= 10 else [])


def match(pdf, want):
    """(screen_id, how) or (None, reason)."""
    if pdf.read_bytes()[:5] != b"%PDF-":
        return None, "not a PDF (often a saved login or error page)"
    try:
        doc = fitz.open(pdf)
        pages = [doc[i].get_text() for i in range(min(2, doc.page_count))]
        meta = " ".join(v for v in (doc.metadata or {}).values() if isinstance(v, str)) + (doc.get_xml_metadata() or "")
    except Exception as e:
        return None, "not a readable PDF (%s)" % type(e).__name__
    def found(text):
        t = squash(text)
        return sorted({s for s, r in want.items() for k in keys(r["doi"]) if k in t})

    # page 1 first: a short paper's page 2 can cite other DOIs
    for where, text in [("page 1", pages[0] if pages else ""), ("PDF metadata", meta)] + [("page 2", t) for t in pages[1:2]]:
        hits = found(text)
        if len(hits) == 1:
            return hits[0], "DOI in %s" % where
        if len(hits) > 1:
            # a corrigendum's page 1 also prints the corrected article's DOI; the publisher's metadata names the file's own
            own = [s for s in found(meta) if s in hits] if where != "PDF metadata" else []
            if len(own) == 1:
                return own[0], "DOI in PDF metadata (%s also names %s)" % (where, ", ".join(s for s in hits if s != own[0]))
            return None, "several listed DOIs in %s: %s" % (where, ", ".join(hits))
    t = letters(pages[0]) if pages else ""
    hits = [s for s, r in want.items() if len(letters(r["title"])) >= 30 and letters(r["title"])[:60] in t]
    if len(hits) == 1:
        return hits[0], "title on page 1"
    return None, "no listed DOI or title on pages 1-2"


def place(want):
    files = HERE / "files"
    have = {f.stem for f in files.iterdir()}
    src = {json.loads(l)["screen_id"]: json.loads(l) for l in open(LOG, encoding="utf-8") if l.strip()}
    n = 0
    for f in sorted(DEST.glob("S*.pdf")):
        sid = f.stem
        if sid not in want or sid in have:
            continue
        body = f.read_bytes()
        (files / f.name).write_bytes(body)
        with open(HERE / "retrieval_log.jsonl", "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(dict(screen_id=sid, route="manual_purdue", url="https://doi.org/" + want[sid]["doi"],
                                     status="downloaded by hand by the entrant (Purdue library)", bytes=len(body),
                                     accepted=True, sha256=hashlib.sha256(body).hexdigest(),
                                     source_name=src.get(sid, {}).get("source_name"),
                                     at=dt.datetime.now(dt.timezone.utc).isoformat())) + "\n")
        n += 1
    print(n, "files placed in files/")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", nargs="*", default=[str(DEST), str(pathlib.Path.home() / "Downloads")])
    p.add_argument("--since", default="2026-09-27")
    p.add_argument("--place", action="store_true")
    a = p.parse_args()
    sys.stdout.reconfigure(errors="replace")  # titles carry Greek letters; a cp1252 console can't print them
    if a.place:
        return place(wanted())
    since = dt.datetime.fromisoformat(a.since).timestamp()
    want = wanted()
    DEST.mkdir(exist_ok=True)
    got, unmatched = {}, []
    for src in map(pathlib.Path, a.src):
        if not src.exists():
            continue
        for f in sorted(src.glob("*.pdf")):
            if src != DEST and f.stat().st_mtime < since:
                continue
            if src == DEST and re.fullmatch(r"S\d{5}\.pdf", f.name) and f.stem in want:
                got.setdefault(f.stem, "already in place")
                continue
            sid, how = match(f, want)
            if not sid:
                unmatched.append("%s  (%s)" % (f.name, how))
                continue
            body = f.read_bytes()
            h = hashlib.sha256(body).hexdigest()
            out = DEST / (sid + ".pdf")
            if out.exists() and hashlib.sha256(out.read_bytes()).hexdigest() != h:
                unmatched.append("%s  (matches %s, but a different file is already there; left alone)" % (f.name, sid))
                continue
            if not out.exists():
                out.write_bytes(body)
                with open(LOG, "a", encoding="utf-8", newline="\n") as fh:
                    fh.write(json.dumps(dict(screen_id=sid, doi=want[sid]["doi"], source_name=f.name, sha256=h,
                                             bytes=len(body), matched_by=how, route="manual (entrant, Purdue library)",
                                             at=dt.datetime.now(dt.timezone.utc).isoformat())) + "\n")
            got.setdefault(sid, how)
    print("in files_manual: %d of %d" % (len(got), len(want)))
    for s in sorted(got):
        print("  %s  %s" % (s, got[s]))
    if unmatched:
        print("PDFs that matched nothing:")
        for u in unmatched:
            print("  " + u)
    missing = sorted(set(want) - set(got))
    if missing:
        print("still missing (%d):" % len(missing))
        for s in missing:
            print("  %s  %s  %s" % (s, want[s]["doi"], want[s]["title"][:70]))


if __name__ == "__main__":
    main()
