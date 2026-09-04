#!/usr/bin/env python3
"""F8: resolve every DOI in the report-bearing tree against Crossref/DataCite.

WHY THIS EXISTS
---------------
`docs/43:1945` (F8) requires the bibliography to be regenerated from Crossref
before the report quotes anything. The published number-one reason projects
failed to qualify in 2026 is "Fake references and/or citations in Research
Report", and this repository has a *recorded* instance of the failure mode:

    docs/research/2026-08-15-lit-sweep-lens-digest.md:416
    "APS DOIs quoted as 10.1103/PhysRevB.<vol>.<article> for [seven works]
     follow APS's deterministic pattern; ... the Houchins, Nishihara/Otani and
     Timrov DOIs were seen verbatim. THE OTHERS ARE PATTERN-DERIVED."

A pattern-derived DOI is a guess that resolves often enough to look right. Four
of those seven were never resolved. The same file flags Rossmeisl 2007 as
"inferred from the ScienceDirect PII ... not read off the publisher record".

WHAT IT DOES
------------
Extracts DOIs from a named file set, resolves each one, and reports four states:

  RESOLVED       the DOI exists and its metadata is recorded here
  NOT_FOUND      the registrar has no such DOI -- a fabricated or mistyped cite
  AMBIGUOUS      resolved, but the stored metadata could not be read cleanly
  ERROR          transport failure; retried, and never silently counted as OK

Crossref covers journal literature; Zenodo/DataCite DOIs (10.5281/*) resolve on
the DataCite API instead, so both backends are tried before anything is called
NOT_FOUND.

WHAT IT DOES NOT DO
-------------------
It does not decide whether a citation is APPROPRIATE, and it cannot: a DOI that
resolves to a real paper can still be attached to a claim that paper does not
make. That is the hand-check at `tasks/todo.md:1559`. This tool clears the
mechanical half -- does the identifier exist, and is it the work you named --
and it prints TITLE MISMATCH warnings where a nearby title in the source text
disagrees with the registrar's, which is where the second half starts.

No email is sent to the API. Crossref's "polite pool" asks for a mailto and
returns slightly better latency; the entrant's address is not this tool's to
hand to a third party, so the public pool is used.

USAGE
    python src/lit/verify_dois.py --scan docs tasks README.md
    python src/lit/verify_dois.py --doi 10.1103/PhysRevB.65.035406
    python src/lit/verify_dois.py --scan docs --json out.json --md out.md --bib refs.bib
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Deliberately CONSERVATIVE. A permissive character class swallows ordinary
# prose punctuation -- "OC20 (10.1021/acscatal.0c04525): slab relaxations" -- and
# manufactures "malformed DOIs" that are really sentence commas and colons. We
# stop at whitespace and at trailing punctuation, then strip a closing bracket.
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>,;)\]}]+)", re.I)

# Trailing characters that are prose or markup, never the end of a DOI.
# `*` and backtick matter specifically: these documents write DOIs inside bold
# and code spans, so "10.1002/anie.202521856**" is a bold marker, not an
# identifier. Getting this wrong manufactures NOT_FOUND rows that look exactly
# like fabricated citations, which is the one error this tool must not make.
_TRAIL = ".,;:)]}>\"'*`"
# `_` and `~` ARE legal DOI characters, so they are only stripped when doubled --
# markdown emphasis (__bold__, ~~strike~~) rather than part of the identifier.
_TRAIL_DOUBLED = ("__", "~~", "**")

USER_AGENT = "sts-electrocatalyst-F8-bibliography-check/1.0 (github.com/fronkt/sts-electrocatalyst)"


def normalise(doi: str) -> str:
    d = doi.strip()
    changed = True
    while changed and d:
        changed = False
        for pair in _TRAIL_DOUBLED:
            if d.endswith(pair):
                d = d[: -len(pair)]
                changed = True
        while d and d[-1] in _TRAIL:
            d = d[:-1]
            changed = True
    return d.lower()


def scan(paths):
    """Return {doi: [(file, line_no, line_text), ...]}."""
    found = {}
    for p in paths:
        full = p if os.path.isabs(p) else os.path.join(ROOT, p)
        files = []
        if os.path.isfile(full):
            files = [full]
        else:
            for dirpath, dirnames, filenames in os.walk(full):
                dirnames[:] = [d for d in dirnames
                               if d not in (".git", "__pycache__", "node_modules")
                               and not d.startswith(".venv")]
                for fn in filenames:
                    if fn.lower().endswith((".md", ".txt", ".toml", ".yml", ".yaml", ".py", ".json")):
                        files.append(os.path.join(dirpath, fn))
        for f in files:
            try:
                with open(f, encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        for m in DOI_RE.finditer(line):
                            d = normalise(m.group(1))
                            if d:
                                found.setdefault(d, []).append(
                                    (os.path.relpath(f, ROOT).replace("\\", "/"), i, line.strip()))
            except OSError:
                continue
    return found


def _get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _crossref(doi):
    data = _get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
    m = data.get("message", {})
    title = (m.get("title") or [""])[0]
    authors = m.get("author") or []
    first = ""
    if authors:
        first = (authors[0].get("family") or authors[0].get("name") or "").strip()
    year = ""
    for k in ("published-print", "published-online", "issued", "created"):
        parts = (m.get(k) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            year = str(parts[0][0])
            break
    return {
        "registrar": "crossref",
        "title": title,
        "first_author": first,
        "n_authors": len(authors),
        "year": year,
        "container": (m.get("container-title") or [""])[0],
        "type": m.get("type", ""),
        "volume": m.get("volume", ""),
        "page": m.get("page", "") or m.get("article-number", ""),
        "publisher": m.get("publisher", ""),
    }


def _datacite(doi):
    data = _get("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe=""))
    a = (data.get("data") or {}).get("attributes", {})
    titles = a.get("titles") or []
    creators = a.get("creators") or []
    first = ""
    if creators:
        first = (creators[0].get("familyName") or creators[0].get("name") or "").strip()
    return {
        "registrar": "datacite",
        "title": (titles[0].get("title") if titles else "") or "",
        "first_author": first,
        "n_authors": len(creators),
        "year": str(a.get("publicationYear") or ""),
        "container": a.get("publisher") or "",
        "type": ((a.get("types") or {}).get("resourceTypeGeneral") or ""),
        "volume": "",
        "page": "",
        "publisher": a.get("publisher") or "",
    }


def resolve(doi, retries=2, pause=0.4):
    """Try Crossref, then DataCite. ERROR is never collapsed into NOT_FOUND."""
    last_err = ""
    for backend in (_crossref, _datacite):
        for attempt in range(retries + 1):
            try:
                meta = backend(doi)
                meta["state"] = "RESOLVED" if meta.get("title") else "AMBIGUOUS"
                return meta
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    last_err = "404 from %s" % backend.__name__.strip("_")
                    break                      # try the other registrar
                last_err = "HTTP %s from %s" % (e.code, backend.__name__.strip("_"))
                if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                    time.sleep(pause * (2 ** attempt) + 1.0)
                    continue
                break
            except Exception as e:                       # noqa: BLE001
                last_err = "%s: %s" % (type(e).__name__, e)
                if attempt < retries:
                    time.sleep(pause * (2 ** attempt))
                    continue
        time.sleep(pause)
    state = "NOT_FOUND" if "404" in last_err else "ERROR"
    return {"state": state, "error": last_err, "registrar": "", "title": "",
            "first_author": "", "n_authors": 0, "year": "", "container": "",
            "type": "", "volume": "", "page": "", "publisher": ""}


_STOP = {"the", "a", "an", "of", "and", "for", "in", "on", "with", "to", "by", "from"}


def _toks(s):
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if w not in _STOP and len(w) > 2}


def title_agreement(meta, contexts):
    """Cheap sanity check: does any citing line share vocabulary with the title?

    Not a verdict -- many citations name only an author and a year. It flags the
    case worth a human eye: a DOI that resolves to something whose title has
    nothing in common with the sentence citing it.
    """
    t = _toks(meta.get("title"))
    # No title, or no citing line to compare against (e.g. --doi mode), means the
    # check is INAPPLICABLE. Returning 0.0 here would flag every such row as a
    # mismatch, which is a false positive in the one direction that matters.
    if not t or not contexts:
        return None
    best = 0.0
    fam = (meta.get("first_author") or "").lower()
    for _f, _i, line in contexts:
        c = _toks(line)
        if not c:
            continue
        best = max(best, len(t & c) / float(len(t)))
        if fam and len(fam) > 2 and fam in line.lower():
            best = max(best, 0.34)
    return best


def bibkey(meta, doi):
    fam = re.sub(r"[^A-Za-z]", "", meta.get("first_author") or "") or "anon"
    yr = meta.get("year") or "nd"
    tail = re.sub(r"[^a-z0-9]", "", doi.split("/")[-1])[-4:]
    return "%s%s%s" % (fam.lower(), yr, tail)


def to_bib(doi, meta):
    kind = {"journal-article": "article", "book": "book",
            "book-chapter": "incollection", "posted-content": "misc",
            "proceedings-article": "inproceedings"}.get(meta.get("type"), "misc")
    fields = [("title", meta.get("title")), ("author", meta.get("first_author")),
              ("year", meta.get("year")), ("journal", meta.get("container")),
              ("volume", meta.get("volume")), ("pages", meta.get("page")),
              ("publisher", meta.get("publisher")), ("doi", doi)]
    body = ",\n".join("  %s = {%s}" % (k, v) for k, v in fields if v)
    return "@%s{%s,\n%s\n}\n" % (kind, bibkey(meta, doi), body)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="verify_dois.py")
    ap.add_argument("--scan", nargs="*", default=["docs", "tasks", "README.md"],
                    help="paths to scan for DOIs")
    ap.add_argument("--doi", nargs="*", default=None,
                    help="verify only these DOIs (skips scanning)")
    ap.add_argument("--json", default=None)
    ap.add_argument("--md", default=None)
    ap.add_argument("--bib", default=None)
    ap.add_argument("--pause", type=float, default=0.4,
                    help="seconds between requests")
    ap.add_argument("--limit", type=int, default=0, help="stop after N DOIs (0 = all)")
    args = ap.parse_args(argv)

    if args.doi:
        found = {normalise(d): [] for d in args.doi}
    else:
        found = scan(args.scan)
    dois = sorted(found)
    if args.limit:
        dois = dois[: args.limit]
    print("scanning %s -> %d unique DOIs" % (", ".join(args.scan), len(found)), file=sys.stderr)

    results = {}
    counts = {}
    for n, d in enumerate(dois, 1):
        meta = resolve(d, pause=args.pause)
        # A DOI that 404s but resolves once a trailing character is removed was
        # never a bad citation -- it is markup or punctuation glued on by the
        # source text. Report it as RESOLVED and name the cleanup, rather than
        # leaving a row that reads like a fabricated reference.
        if meta["state"] == "NOT_FOUND":
            trimmed = d
            for _ in range(4):
                if not trimmed or trimmed[-1].isalnum():
                    break
                trimmed = trimmed[:-1]
                alt = resolve(trimmed, retries=0, pause=args.pause)
                if alt["state"] == "RESOLVED":
                    alt["cited_as"] = d
                    alt["note"] = ("source text appends %r to the DOI; identifier is valid"
                                   % d[len(trimmed):])
                    meta = alt
                    break
        meta["contexts"] = [{"file": f, "line": i, "text": t} for f, i, t in found[d]]
        meta["n_citations"] = len(found[d])
        meta["title_agreement"] = title_agreement(meta, found[d])
        results[d] = meta
        counts[meta["state"]] = counts.get(meta["state"], 0) + 1
        flag = ""
        if meta["state"] == "RESOLVED" and meta["title_agreement"] is not None \
                and meta["title_agreement"] < 0.10:
            flag = "  [TITLE MISMATCH?]"
        print("[%3d/%3d] %-11s %-48s %s%s"
              % (n, len(dois), meta["state"], d[:48],
                 (meta.get("title") or meta.get("error", ""))[:60], flag),
              file=sys.stderr)
        time.sleep(args.pause)

    print("\n" + json.dumps(counts, indent=1), file=sys.stderr)

    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"counts": counts, "n_unique": len(found), "results": results},
                      fh, indent=1, sort_keys=True)
            fh.write("\n")
        print("wrote %s" % args.json, file=sys.stderr)

    if args.bib:
        os.makedirs(os.path.dirname(os.path.abspath(args.bib)), exist_ok=True)
        with open(args.bib, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("% Generated by src/lit/verify_dois.py from registrar metadata.\n")
            fh.write("% Every entry below resolved against Crossref or DataCite.\n")
            fh.write("% Entries that did NOT resolve are absent by design -- see the report.\n\n")
            for d in sorted(results):
                if results[d]["state"] == "RESOLVED":
                    fh.write(to_bib(d, results[d]))
                    fh.write("\n")
        print("wrote %s" % args.bib, file=sys.stderr)

    if args.md:
        L = ["# F8 — DOI resolution report", "",
             "Every DOI in the scanned tree, resolved against Crossref and then DataCite.",
             "`NOT_FOUND` means the registrar has no such identifier.", "",
             "| state | n |", "|---|---|"]
        for k in sorted(counts):
            L.append("| %s | %d |" % (k, counts[k]))
        for state, head in (("NOT_FOUND", "## NOT FOUND — these do not exist at any registrar"),
                            ("ERROR", "## ERROR — transport failure, state unknown, NOT cleared"),
                            ("AMBIGUOUS", "## AMBIGUOUS — resolved but metadata unreadable")):
            rows = [d for d in sorted(results) if results[d]["state"] == state]
            if not rows:
                continue
            L += ["", head, ""]
            for d in rows:
                L.append("- `%s` — %s" % (d, results[d].get("error", "")))
                for c in results[d]["contexts"][:6]:
                    L.append("    - %s:%d" % (c["file"], c["line"]))
        sus = [d for d in sorted(results)
               if results[d]["state"] == "RESOLVED"
               and results[d]["title_agreement"] is not None
               and results[d]["title_agreement"] < 0.10]
        if sus:
            L += ["", "## RESOLVED but no vocabulary overlap with any citing line",
                  "", "Not a verdict — many citations name only an author and a year.",
                  "These are the ones worth a human eye.", ""]
            for d in sus:
                L.append("- `%s` -> %s (%s %s)" % (d, results[d]["title"],
                                                   results[d]["first_author"],
                                                   results[d]["year"]))
                for c in results[d]["contexts"][:3]:
                    L.append("    - %s:%d — %s" % (c["file"], c["line"], c["text"][:120]))
        os.makedirs(os.path.dirname(os.path.abspath(args.md)), exist_ok=True)
        with open(args.md, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(L) + "\n")
        print("wrote %s" % args.md, file=sys.stderr)

    return 1 if counts.get("NOT_FOUND") else 0


if __name__ == "__main__":
    sys.exit(main())
