"""Crossref comparison of docs/references.bib and the docs/28 DOI audit.

Field comparison (bib value vs registrar value), per entry:

- title       MATCH (identical) | MARKUP (identical once markup/whitespace is
              removed -- the bib carries registrar markup) | CASE (identical up to
              case and punctuation) | MISMATCH
- first_author  MATCH | MISMATCH (accent/case-folded family name)
- year        MATCH | MISMATCH (registrar year = print > online > issued)
- journal     MATCH | MARKUP | MISSING_IN_BIB | EXTRA_IN_BIB | MISMATCH
- volume      MATCH | MISSING_IN_BIB | EXTRA_IN_BIB | MISMATCH
- pages       MATCH | MISSING_IN_BIB | EXTRA_IN_BIB | MISMATCH (dash-normalised)

Completeness flags (not mismatches): AUTHORS_TRUNCATED (registrar lists more
authors than the bib's author field), ISSUE_MISSING, PRINT_ONLINE_YEAR_SPLIT.
"""
from __future__ import annotations

import re

from . import bib
from .registry import Record, lookup, search
from .textnorm import clean_markup, fold, norm_pages, title_key

KIND = {"journal-article": "article", "book": "book", "book-chapter": "incollection",
        "posted-content": "misc", "proceedings-article": "inproceedings",
        "dataset": "misc", "report": "techreport", "monograph": "book",
        "reference-entry": "incollection", "other": "misc", "component": "misc",
        "text": "misc", "software": "misc", "preprint": "misc"}


def _cmp_simple(bv: str, rv: str) -> str:
    bv, rv = (bv or "").strip(), (rv or "").strip()
    if not bv and not rv:
        return "MATCH"
    if not bv:
        return "MISSING_IN_BIB"
    if not rv:
        return "EXTRA_IN_BIB"
    return "MATCH" if bv == rv else "MISMATCH"


def compare_entry(e: bib.Entry, rec: Record) -> dict:
    f = e.fields
    out = {}
    bt, rt = f.get("title", ""), rec.title_raw
    if bt == rt:
        out["title"] = "MATCH"
    elif clean_markup(bt) == clean_markup(rt):
        out["title"] = "MARKUP"
    elif title_key(bt) == title_key(rt):
        out["title"] = "CASE"
    else:
        out["title"] = "MISMATCH"
    out["first_author"] = "MATCH" if fold(f.get("author", "").split(" and ")[0].split(",")[0]) == \
        fold(rec.first_family) else "MISMATCH"
    ry = rec.year
    out["year"] = "MATCH" if str(ry or "") == f.get("year", "").strip() else "MISMATCH"
    bj, rj = f.get("journal", ""), rec.journal_raw
    if rec.registrar == "datacite":
        # DataCite has no container; the bib builder wrote the publisher there
        rj = rec.publisher
    if bj == rj:
        out["journal"] = "MATCH"
    elif bj and rj and clean_markup(bj) == clean_markup(rj):
        out["journal"] = "MARKUP"
    else:
        out["journal"] = _cmp_simple(bj, rj)
    out["volume"] = _cmp_simple(f.get("volume", ""), rec.volume)
    out["pages"] = _cmp_simple(norm_pages(f.get("pages", "")), rec.pages)
    flags = []
    if f.get("title", "") != clean_markup(f.get("title", "")):
        flags.append("TITLE_MARKUP_OR_WHITESPACE_IN_BIB")
    if f.get("journal", "") != clean_markup(f.get("journal", "")):
        flags.append("JOURNAL_MARKUP_OR_WHITESPACE_IN_BIB")
    n_bib_auth = len([a for a in f.get("author", "").split(" and ") if a.strip()])
    if len(rec.authors) > n_bib_auth:
        flags.append("AUTHORS_TRUNCATED")
    if rec.issue and not f.get("number"):
        flags.append("ISSUE_MISSING")
    if rec.year_print and rec.year_online and rec.year_print != rec.year_online:
        flags.append("PRINT_ONLINE_YEAR_SPLIT")
    return {"fields": out, "flags": flags}


def _author_field(rec: Record) -> str:
    names = []
    for a in rec.authors:
        fam, giv, nm = a.get("family"), a.get("given"), a.get("name")
        if fam and giv:
            names.append(f"{fam}, {giv}")
        elif fam:
            names.append(fam)
        elif nm:
            names.append("{" + nm + "}")
    return " and ".join(names)


def corrected_entry(e: bib.Entry, rec: Record) -> str:
    kind = KIND.get(rec.type, e.kind) if rec.registrar == "crossref" else "misc"
    fields = [("title", rec.title), ("author", _author_field(rec)),
              ("year", str(rec.year or "")), ("journal", rec.journal),
              ("volume", rec.volume), ("number", rec.issue), ("pages", rec.pages),
              ("publisher", rec.publisher), ("doi", rec.doi)]
    if kind != "article":
        fields = [(k, v) for k, v in fields if k != "journal"] + (
            [("howpublished", rec.journal)] if rec.journal else [])
    return bib.format_entry(kind, e.key, fields)


def check_bib(entries: list[bib.Entry], fetcher) -> dict:
    rows = []
    for e in entries:
        doi = e.fields.get("doi", "").strip()
        row = {"key": e.key, "line": e.line, "kind": e.kind, "doi": doi,
               "bib": {k: e.fields.get(k, "") for k in ("title", "author", "year", "journal",
                                                          "volume", "pages")}}
        if not doi:
            row.update(state="NO_DOI")
            rows.append(row)
            continue
        rec = lookup(fetcher, doi)
        if rec.registrar == "none":
            # a website path glued to the identifier (".../full"): try the stems,
            # never below "10.prefix/suffix"
            stem = doi
            tried = []
            while stem.count("/") > 1 and rec.registrar == "none":
                stem = stem.rsplit("/", 1)[0]
                tried.append(stem)
                alt = lookup(fetcher, stem)
                if alt.registrar != "none":
                    row["doi_field_defect"] = {"as_written": doi, "registrar_valid": stem,
                                               "status_as_written": rec.status}
                    rec = alt
            row["stems_tried"] = tried
        row["registrar"] = rec.registrar
        row["registrar_status"] = rec.status
        row["cache_file"] = rec.cache_file
        if rec.registrar == "none":
            row.update(state="NOT_RESOLVED")
            rows.append(row)
            continue
        row["registrar_record"] = {
            "title": rec.title, "title_raw": rec.title_raw, "first_author_family": rec.first_family,
            "n_authors": len(rec.authors), "year": rec.year, "year_print": rec.year_print,
            "year_online": rec.year_online, "year_issued": rec.year_issued,
            "journal": rec.journal, "volume": rec.volume, "issue": rec.issue,
            "pages": rec.pages, "type": rec.type}
        cmp_ = compare_entry(e, rec)
        if "doi_field_defect" in row:
            cmp_["flags"].append("DOI_FIELD_NOT_A_REGISTERED_DOI")
        row.update(cmp_)
        bad = {k: v for k, v in cmp_["fields"].items() if v not in ("MATCH",)}
        row["state"] = "CHECKED"
        row["non_match_fields"] = bad
        row["corrected_bibtex"] = corrected_entry(e, rec)
        if rec.type in ("", "component", "other") or (rec.registrar == "crossref" and not rec.authors):
            row["flags"] = row.get("flags", []) + ["NO_AUTHORS_OR_NONARTICLE_TYPE"]
        rows.append(row)
    return {"rows": rows}


# ---------------------------------------------------------------------------
# docs/28

DOI_RE = re.compile(r"(?<![0-9A-Za-z])(10\.\d{4,9}/[^\s\"'<>,;\]}·]+)", re.I)
_TRAIL = ".,;:)]}>\"'*`"


def normalise_doi(d: str) -> str:
    d = d.strip()
    while d and d[-1] in _TRAIL:
        if d[-1] == ")" and d.count(")") <= d.count("("):
            break
        d = d[:-1]
    return d.lower()


_STOP = {"the", "a", "an", "of", "and", "for", "in", "on", "with", "to", "by", "from", "et", "al"}


def _toks(s: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", title_key(s)) if w not in _STOP and len(w) > 2}


def label_segment(line: str, start: int) -> str:
    """Citation label text before a DOI: back to the previous ' · ', ':' or line start,
    skipping the parenthesis the DOI sits in."""
    left = line[:start]
    cut = max(left.rfind(" · "), left.rfind(": "), left.rfind("; "))
    seg = left[cut + 1:] if cut >= 0 else left
    return seg


def audit_docs28(lines: list[str], fetcher) -> list[dict]:
    rows = []
    for i, line in enumerate(lines, 1):
        for m in DOI_RE.finditer(line):
            raw = m.group(1)
            doi = normalise_doi(raw)
            seg = label_segment(line, m.start())
            years = [int(y) for y in re.findall(r"(?<!\d)(19\d{2}|20\d{2})(?!\d)", seg)]
            rec = lookup(fetcher, doi)
            row = {"line": i, "doi_as_written": raw, "doi": doi, "label_segment": seg.strip(),
                   "registrar": rec.registrar, "status": rec.status}
            if rec.registrar == "none":
                row["state"] = "NOT_FOUND"
                row["flags"] = ["DOI_NOT_REGISTERED"]
                # the registrar-valid prefix, if a trailing token was glued on
                stem = re.sub(r"-[a-z]+$", "", doi)
                if stem != doi:
                    alt = lookup(fetcher, stem)
                    row["stem_tried"] = stem
                    row["stem_record"] = {"registrar": alt.registrar, "title": alt.title,
                                          "n_authors": len(alt.authors), "journal": alt.journal,
                                          "volume": alt.volume, "pages": alt.pages,
                                          "year": alt.year}
                rows.append(row)
                continue
            fams = {fold(a.get("family") or a.get("name")) for a in rec.authors}
            words = {fold(w) for w in re.findall(r"[A-ZÀ-ÖØ-Þ][\w\-’']+", seg)}
            words |= {fold(p) for w in list(words) for p in w.split("-")}
            author_hit = sorted(w for w in words if w and w in fams)
            ryears = {y for y in (rec.year_print, rec.year_online, rec.year_issued) if y}
            vocab = len(_toks(rec.title) & _toks(line)) / max(1, len(_toks(rec.title)))
            row.update(title=rec.title, first_author=rec.first_family, n_authors=len(rec.authors),
                       journal=rec.journal, volume=rec.volume, pages=rec.pages,
                       registrar_years=sorted(ryears), label_years=years,
                       label_author_match=author_hit, title_vocab_overlap=round(vocab, 3))
            jwords = [w for w in re.findall(r"[a-z]+", rec.journal.casefold())
                      if w not in {"the", "of", "and", "for", "in"}]
            covered = {jw for tok in re.findall(r"[A-Za-z]{3,}", seg)
                       for jw in jwords if jw.startswith(tok.casefold())}
            row["label_journal_words_matched"] = sorted(covered)
            row["label_journal_and_year_consistent"] = bool(jwords) and \
                len(covered) >= min(2, len(jwords)) and bool(set(years) & ryears)
            flags = []
            if not rec.authors:
                flags.append("REGISTRAR_RECORD_HAS_NO_AUTHORS")
            if years and not (set(years) & ryears):
                flags.append("LABEL_YEAR_NOT_IN_REGISTRAR_YEARS")
            if not author_hit and vocab < 0.10:
                flags.append("NO_AUTHOR_OR_TITLE_AGREEMENT")
            row["flags"] = flags
            row["state"] = "RESOLVED"
            rows.append(row)
    return rows


def find_correction(fetcher, query: dict, must: dict) -> list[dict]:
    """Crossref search; keep items satisfying every predicate in ``must``.

    must keys: title_contains (list of lower-case substrings), container (exact,
    case-folded), first_family (folded).
    """
    out = []
    for it in search(fetcher, query):
        from .registry import from_crossref
        rec = from_crossref(it.get("DOI", "").lower(), it)
        ok = all(s in rec.title.lower() for s in must.get("title_contains", []))
        if "container" in must:
            ok = ok and rec.journal.casefold() == must["container"].casefold()
        if "first_family" in must:
            ok = ok and fold(rec.first_family) == fold(must["first_family"])
        if ok:
            out.append({"doi": rec.doi, "title": rec.title, "first_author": rec.first_family,
                        "authors": [a.get("family") for a in rec.authors], "journal": rec.journal,
                        "volume": rec.volume, "pages": rec.pages, "year": rec.year,
                        "alternative_ids": rec.alternative_ids})
    return out


# ---------------------------------------------------------------------------
# label defects repeated on docs/28 lines that carry no DOI

_CLAUSE_SPLIT = re.compile(r" · |; |[()]")


def _journal_words(journal: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]+", journal.casefold()) if w not in {"the", "of", "and", "for", "in"}]


def _journal_named(clause: str, jwords: list[str]) -> bool:
    covered = {jw for tok in re.findall(r"[A-Za-z]{3,}", clause) for jw in jwords
               if jw.startswith(tok.casefold())}
    return bool(jwords) and len(covered) >= min(2, len(jwords))


def author_journal_year_works(fetcher, family: str, journal: str, year: int) -> list[dict]:
    """Registrar works in ``journal`` dated ``year`` with ``family`` among the authors (Crossref
    search, post-filtered on exact container, folded family name and any of the three years)."""
    items = search(fetcher, {"query.author": family, "query.container-title": journal,
                             "filter": f"from-pub-date:{year}-01-01,until-pub-date:{year}-12-31",
                             "rows": 50})
    from .registry import from_crossref
    out = []
    for it in items:
        rec = from_crossref(it.get("DOI", "").lower(), it)
        years = {y for y in (rec.year_print, rec.year_online, rec.year_issued) if y}
        fams = [fold(a.get("family")) for a in rec.authors]
        if rec.journal.casefold() == journal.casefold() and year in years and fold(family) in fams:
            out.append({"doi": rec.doi, "title": rec.title, "years": sorted(years),
                        "authors": [a.get("family") for a in rec.authors],
                        "author_position": fams.index(fold(family)) + 1})
    return out


def label_echoes(lines: list[str], rows: list[dict], fetcher) -> list[dict]:
    """Repeat a DOI line's label defect search over every other line of the document.

    A year defect (LABEL_YEAR_NOT_IN_REGISTRAR_YEARS) is echoed where a clause names
    the same author family (when the DOI label named one) and one of the wrong years
    and carries no DOI. The echo is SAME_LABEL when the clause also names the
    registrar journal, otherwise AUTHOR_AND_YEAR_ONLY (listed, not linked to the
    work). For SAME_LABEL echoes a registrar search lists any work in that journal
    and year with that author, which could make the year a different citation rather
    than a defect. resolution: UNIQUE (no such work), TOPIC_MATCH (the DOI row's work
    shares more title words with the clause's line than every such work), AMBIGUOUS,
    or SAME_LABEL_STRING_AS_LINE_n (an ambiguous clause whose label string equals a
    resolved clause). The correction applies only to resolved SAME_LABEL echoes. A
    slash-name defect (SLASH_NAME_NOT_AN_AUTHOR) is echoed where the same "A/B" pair
    appears.
    """
    out = []
    doi_lines = {}
    for r in rows:
        doi_lines.setdefault(r["line"], []).append(r)
    for r in rows:
        if r["state"] != "RESOLVED":
            continue
        if "LABEL_YEAR_NOT_IN_REGISTRAR_YEARS" in r["flags"]:
            # years in the label that no DOI on the same line carries
            line_years = {y for x in doi_lines[r["line"]] for y in x.get("registrar_years", [])}
            wrong = sorted(set(r["label_years"]) - line_years)
            r["wrong_label_years"] = wrong
            if not wrong:
                continue
            fams = r.get("label_author_match") or []
            jwords = _journal_words(r["journal"])
            searched = {}
            for i, t in enumerate(lines, 1):
                if i == r["line"] or r["doi"] in t.lower():
                    continue
                for clause in _CLAUSE_SPLIT.split(t):
                    if DOI_RE.search(clause):
                        continue
                    words = {fold(w) for w in re.findall(r"[A-ZÀ-ÖØ-Þ][\w\-’']+", clause)}
                    if fams and not set(fams) <= words:
                        continue
                    years = [int(y) for y in re.findall(r"(?<!\d)(19\d{2}|20\d{2})(?!\d)", clause)]
                    bad = sorted(set(years) & set(wrong))
                    if not bad:
                        continue
                    named = _journal_named(clause, jwords)
                    if not fams and not named:
                        continue
                    row = {"kind": "LABEL_YEAR", "line": i, "clause": clause.strip(), "source_line": r["line"],
                           "source_doi": r["doi"], "label_years": years, "wrong_years": bad,
                           "registrar_years": r["registrar_years"],
                           "status": "SAME_LABEL" if named else "AUTHOR_AND_YEAR_ONLY"}
                    if named and fams:
                        for y in bad:
                            if (fams[0], y) not in searched:
                                searched[(fams[0], y)] = author_journal_year_works(fetcher, fams[0], r["journal"], y)
                        others = [dict(w, line_title_words=sorted(_toks(w["title"]) & _toks(t)))
                                  for y in bad for w in searched[(fams[0], y)]]
                        row["other_works_same_author_journal_year"] = {
                            str(y): [o for o in others if y in o["years"]] for y in bad}
                        row["source_line_title_words"] = sorted(_toks(r["title"]) & _toks(t))
                        best_other = max((len(o["line_title_words"]) for o in others), default=None)
                        if best_other is None:
                            row["resolution"] = "UNIQUE"
                        elif len(row["source_line_title_words"]) > best_other:
                            row["resolution"] = "TOPIC_MATCH"
                        else:
                            row["resolution"] = "AMBIGUOUS"
                    elif named:
                        row["resolution"] = "AUTHOR_NOT_NAMED"
                    out.append(row)
        if "SLASH_NAME_NOT_AN_AUTHOR" in r["flags"]:
            pair = "/".join(r["slash_names"])
            for i, t in enumerate(lines, 1):
                if i != r["line"] and pair in t and r["doi"] not in t.lower():
                    out.append({"kind": "SLASH_NAME", "line": i, "clause": pair, "source_line": r["line"],
                                "source_doi": r["doi"], "status": "SAME_LABEL", "resolution": "UNIQUE"})
    # an ambiguous clause whose label string is identical to a resolved clause in the same
    # document is taken to cite the same work
    resolved = {(fold(e["clause"]), e["source_doi"]): e["line"] for e in out
                if e.get("resolution") in ("UNIQUE", "TOPIC_MATCH")}
    for e in out:
        if e.get("resolution") == "AMBIGUOUS" and (fold(e["clause"]), e["source_doi"]) in resolved:
            e["resolution"] = f"SAME_LABEL_STRING_AS_LINE_{resolved[(fold(e['clause']), e['source_doi'])]}"
    for e in out:
        e["correction_applies"] = e["status"] == "SAME_LABEL" and (
            e.get("resolution") in ("UNIQUE", "TOPIC_MATCH") or
            str(e.get("resolution", "")).startswith("SAME_LABEL_STRING_AS_LINE_"))
    return out
