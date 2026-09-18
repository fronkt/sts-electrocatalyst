"""Run every F8 check and write results/s2_2026-09-16/f8/ plus the research note.

    PYTHONPATH=src python -m s2.f8.run            # fetch what is not cached
    PYTHONPATH=src python -m s2.f8.run --offline  # cache only; a miss is an error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from . import bib, bibcheck, intercept_floor, structures, sun2004, zpe
from .common import (OUT, REPO, Fetcher, migrate_cache_names, pdf_text_pages, read_lines,
                     rel, sha256_file, write_json, write_text)
from .registry import lookup

DATA = Path(__file__).resolve().parent / "data"
DOC = REPO / "docs/research/f8-clearance-2026-09-16.md"
REFS_BIB = REPO / "docs/references.bib"
DOCS28 = REPO / "docs/28-electrocatalyst-revival-plan.md"
DOCS43 = REPO / "docs/43-prereg-week1-factorial.md"
MLIP_SURVEY = REPO / "docs/research/2026-07-24-mlip-finetuning-survey.md"
JCAT_PDF = REPO / "docs/research/papers/1-s2.0-S0021951725000338-main.pdf"
CATBENCH_ZENODO = "https://zenodo.org/api/records/17157086"


def _doc_paths() -> list[Path]:
    paths = sorted((REPO / "docs").rglob("*.md")) + sorted((REPO / "tasks").rglob("*.md"))
    paths += [REPO / "README.md"]
    return [p for p in paths if p.resolve() != DOC.resolve()]


# ---------------------------------------------------------------------------

def part_sun(fc, fs, fa) -> dict:
    res = sun2004.run(fc, fs, fa, _doc_paths())
    for row in res["citing_lines"]:
        text = read_lines(REPO / row["file"])[row["line"] - 1]
        if row["file"].startswith("tasks/todo.md"):
            row["role"] = "TASK_ITEM"
        elif "crucial" in text:
            row["role"] = "CLAIM"
        else:
            row["role"] = "F8_REGISTRATION"
        row["verdicts"] = res["claim_verdicts"] if row["role"] == "CLAIM" else None
        m = re.search(r"Sun[,/ ][^;|]*?crucial[^;|]*?\(110\)", text)
        row["claim_quote"] = m.group(0) if (m and row["role"] == "CLAIM") else None
    return res


def part_structures(fs) -> dict:
    cod = {f: structures.cod_census(fs, f) for f in structures.FORMULAS}
    cod_ref = {f: structures.cod_census(fs, f) for f in structures.REFERENCE_FORMULAS}
    mp = {f: structures.mp_summary(fs, f) for f in structures.FORMULAS}
    claims_doc = structures.load_claims(DATA / "structure_claims.json")
    legacy = sorted({c["legacy_id"] for cl in claims_doc["claims"] for s in cl["subclaims"]
                     for c in s["checks"] if c["kind"] == "mp_id_sg"})
    mp_ids = {i: structures.mp_by_ids(fs, i) for i in legacy}
    claims = structures.evaluate_claims(claims_doc["claims"], {**cod, **cod_ref}, mp, mp_ids)
    ment = json.loads((DATA / "structure_mentions.json").read_text(encoding="utf-8"))
    vocab = re.compile(ment["vocabulary_regex"], re.I)
    form = re.compile(ment["formula_regex"])
    paths = []
    for root in ment["scan_roots"]:
        p = REPO / root
        if p.is_file():
            paths.append(p)
        else:
            paths += [q for q in sorted(p.rglob("*")) if q.is_file() and q.suffix in (".md", ".py")
                      and not set(ment["scan_exclude_parts"]) & set(q.relative_to(REPO).parts)
                      and q.resolve() != DOC.resolve()]
    scanned = structures.scan_mentions(paths, vocab, form)
    curated = {(m["file"], m["line"]): m for m in ment["mentions"]}
    for h in scanned:
        m = curated.get((h["file"], h["line"]))
        h["category"] = m["category"] if m else "UNCLASSIFIED"
        h["claims"] = (m or {}).get("claims", [])
        h["note"] = (m or {}).get("note", "")
    missing = [k for k in curated if k not in {(h["file"], h["line"]) for h in scanned}]
    return {"cod": cod, "cod_reference": cod_ref, "mp": mp, "mp_ids": mp_ids, "claims": claims,
            "verdict_rule": claims_doc["verdict_rule"],
            "scanned_files": [rel(p) for p in paths], "n_files_scanned": len(paths),
            "mentions": scanned, "curated_mentions_not_matched_by_scan": [list(k) for k in missing],
            "mention_counts": dict(sorted(Counter(h["category"] for h in scanned).items())),
            "prototype_rules": [{"prototype": n, "space_groups": sorted(s), "cation_wyckoff": sorted(c),
                                 "anion_wyckoff": sorted(a)} for n, s, c, a in structures.PROTOTYPES],
            "ambient_max_kPa": structures.AMBIENT_MAX_KPA, "symprec_A": structures.SYMPREC}


def part_intercept() -> dict:
    classes = json.loads((DATA / "intercept_floor_classes.json").read_text(encoding="utf-8"))
    paths = [p for p in intercept_floor.scan_files() if p.resolve() != DOC.resolve()]
    rows = intercept_floor.classify(intercept_floor.hits(paths), classes)
    swept = intercept_floor.sweep(paths)
    return {"patterns": {k: v.pattern for k, v in intercept_floor.PATTERNS.items()},
            "n_files_scanned": len(paths), "scanned_files": [rel(p) for p in paths],
            "summary": intercept_floor.summarise(rows),
            "rows": rows, "class_definitions": classes["class_definitions"],
            "sweep_pattern": intercept_floor.SWEEP.pattern, "n_sweep_lines": len(swept),
            "sweep_lines_not_matched_by_patterns": swept,
            "registration_lines": {str(n): read_lines(DOCS43)[n - 1] for n in (1944, 1945)}}


def _bibkey(rec) -> str:
    fam = re.sub(r"[^A-Za-z]", "", rec.first_family) or "anon"
    tail = re.sub(r"[^a-z0-9]", "", rec.doi.split("/")[-1])[-4:]
    return f"{fam.lower()}{rec.year or 'nd'}{tail}"


def part_bib(fc, fs) -> dict:
    text = REFS_BIB.read_text(encoding="utf-8")
    entries = bib.parse(text)
    res = bibcheck.check_bib(entries, fc)
    rows = res["rows"]
    d28 = bibcheck.audit_docs28(read_lines(DOCS28), fc)
    slash_name_check(d28, fc)
    echoes = bibcheck.label_echoes(read_lines(DOCS28), d28, fc)
    corrections = docs28_corrections(fc, fs, d28)
    # a DOI in the tree that points at the wrong work is replaced by the verified one
    replace = {c["cited_doi"]: c["corrected_doi"] for c in corrections.values()
               if c.get("corrected_doi") and not c["cited_doi"].endswith("-range")}
    additions = [sun2004.DOI]
    corrected, diff = [], []
    for e, r in zip(entries, rows):
        if r["state"] != "CHECKED":
            diff.append({"key": e.key, "doi": r["doi"], "state": r["state"]})
            continue
        if r["doi"].lower() in replace:
            rec = lookup(fc, replace[r["doi"].lower()])
            stub = bib.Entry(kind="article", key=_bibkey(rec))
            entry_text = bibcheck.corrected_entry(stub, rec)
            diff.append({"key": e.key, "doi": r["doi"], "state": "REPLACED", "replaced_by_key": stub.key,
                         "replaced_by_doi": rec.doi,
                         "reason": "the DOI resolves to a different work than the one the citing lines name "
                                   "(docs28_doi_audit.json)"})
            corrected.append(entry_text)
            continue
        corrected.append(r["corrected_bibtex"])
        new = bib.parse(r["corrected_bibtex"])[0]
        changes = {}
        for k in sorted(set(e.fields) | set(new.fields)):
            if e.fields.get(k, "") != new.fields.get(k, ""):
                changes[k] = {"old": e.fields.get(k), "new": new.fields.get(k)}
        if e.kind != new.kind:
            changes["@type"] = {"old": e.kind, "new": new.kind}
        diff.append({"key": e.key, "doi": r["doi"], "state": r["state"], "registrar": r["registrar"],
                     "field_status": r["fields"], "flags": r["flags"],
                     "doi_field_defect": r.get("doi_field_defect"), "changes": changes})
    added = []
    for d in additions:
        rec = lookup(fc, d)
        stub = bib.Entry(kind="article", key=_bibkey(rec))
        corrected.append(bibcheck.corrected_entry(stub, rec))
        added.append({"key": stub.key, "doi": rec.doi, "state": "ADDED",
                      "reason": "cited in the tree without a DOI and cleared in sun2004.json"})
    diff += added
    header = ("% Regenerated from Crossref (DataCite for non-Crossref DOIs) registrar records.\n"
              "% Source of keys and DOIs: docs/references.bib; full author lists, markup-free titles,\n"
              "% issue numbers and registered DOI stems from the cached registrar responses in\n"
              "% results/s2_2026-09-16/f8/crossref_cache/. One wrong-work DOI replaced and one entry\n"
              "% added, both listed in bib_crossref_diff.json with every changed field.\n\n")
    write_text(OUT / "references.crossref.bib", header + "\n".join(corrected))
    fstat = Counter((f, s) for r in rows if r["state"] == "CHECKED" for f, s in r["fields"].items())
    flags = Counter(fl for r in rows for fl in r.get("flags", []))
    summary = {
        "n_entries": len(entries), "n_with_doi": sum(1 for e in entries if e.fields.get("doi")),
        "n_without_doi": sum(1 for e in entries if not e.fields.get("doi")),
        "entries_without_doi": [e.key for e in entries if not e.fields.get("doi")],
        "states": dict(sorted(Counter(r["state"] for r in rows).items())),
        "registrars": dict(sorted(Counter(r.get("registrar", "") for r in rows).items())),
        "field_status_counts": {f"{f}|{s}": n for (f, s), n in sorted(fstat.items())},
        "flag_counts": dict(sorted(flags.items())),
        "non_match_rows": [{"key": r["key"], "doi": r["doi"], "registrar": r.get("registrar"),
                            "non_match_fields": r.get("non_match_fields"),
                            "bib": {k: r["bib"][k] for k in (r.get("non_match_fields") or {})},
                            "registrar_value": {k: (r.get("registrar_record") or {}).get(
                                "first_author_family" if k == "first_author" else k)
                                for k in (r.get("non_match_fields") or {})}}
                           for r in rows if r.get("non_match_fields")],
        "journal_markup_rows": [{"key": r["key"], "journal": r["bib"]["journal"]} for r in rows
                                if "JOURNAL_MARKUP_OR_WHITESPACE_IN_BIB" in r.get("flags", [])],
        "doi_field_defects": [{"key": r["key"], **r["doi_field_defect"]} for r in rows
                              if r.get("doi_field_defect")],
        "print_online_year_split": [{"key": r["key"], "doi": r["doi"],
                                     "print": r["registrar_record"]["year_print"],
                                     "online": r["registrar_record"]["year_online"]}
                                    for r in rows if "PRINT_ONLINE_YEAR_SPLIT" in r.get("flags", [])],
        "n_corrected_entries_written": len(corrected),
        "replaced": [d for d in diff if d.get("state") == "REPLACED"],
        "added": [d for d in diff if d.get("state") == "ADDED"],
    }
    write_json(OUT / "bib_crossref_diff.json", {"summary": summary, "entries": diff})
    return {"bib_summary": summary, "bib_rows": rows, "docs28": d28, "docs28_corrections": corrections,
            "docs28_label_echoes": echoes}


def slash_name_check(d28: list[dict], fc) -> None:
    """Label "A/B" name pairs where exactly one name is an author of the resolved work."""
    from .textnorm import fold
    for r in d28:
        if r["state"] != "RESOLVED":
            continue
        pairs = re.findall(r"([A-ZÀ-ÖØ-Þ][\w\-’']+)/([A-ZÀ-ÖØ-Þ][\w\-’']+)", r["label_segment"])
        rec = lookup(fc, r["doi"])
        fams = {fold(a.get("family") or a.get("name")) for a in rec.authors}
        for a, b in pairs:
            if (fold(a) in fams) != (fold(b) in fams):
                r["flags"].append("SLASH_NAME_NOT_AN_AUTHOR")
                r["slash_names"] = [a, b]


def docs28_corrections(fc, fs, d28) -> dict:
    out = {}
    # CatBench: docs/28:87 and :114 cite 10.1016/j.xcrp.2025.102847
    pii_line = next(t for t in read_lines(MLIP_SURVEY) if "S2666-3864" in t)
    pii = re.search(r"S\d{4}-\d{4}\(\d{2}\)\d{5}-[\dX]", pii_line).group(0)
    pii_norm = re.sub(r"[^0-9A-Z]", "", pii)
    cands = bibcheck.find_correction(
        fc, {"query.bibliographic": "CatBench benchmarking machine learning interatomic potentials "
                                    "adsorption energy heterogeneous catalysis", "rows": 10},
        {"title_contains": ["catbench"], "container": "Cell Reports Physical Science"})
    for c in cands:
        c["pii_matches_survey"] = any(re.sub(r"[^0-9A-Z]", "", a.upper()) == pii_norm
                                      for a in c["alternative_ids"])
    z = fs.get(CATBENCH_ZENODO, "zenodo_record_17157086", "json")
    zj = z.json() if z.status == 200 else {}
    related = [ri.get("identifier", "").lower() for ri in
               (zj.get("metadata") or {}).get("related_identifiers", []) or []]
    wrong = lookup(fc, "10.1016/j.xcrp.2025.102847")
    tree_lines = [f"{rel(p)}:{i}" for p in _doc_paths() for i, t in enumerate(read_lines(p), 1)
                  if "10.1016/j.xcrp.2025.102847" in t.lower()]
    out["catbench"] = {
        "cited_doi": "10.1016/j.xcrp.2025.102847", "docs28_lines": [r["line"] for r in d28
                                                                   if r["doi"] == "10.1016/j.xcrp.2025.102847"],
        "cited_doi_resolves_to": {"title": wrong.title, "first_author": wrong.first_family,
                                  "alternative_ids": wrong.alternative_ids},
        "pii_from_survey": pii, "survey_line_file": rel(MLIP_SURVEY),
        "all_citing_lines_in_docs_and_tasks": tree_lines,
        "candidates": cands,
        "zenodo_17157086_related_identifiers": related,
        "corrected_doi": cands[0]["doi"] if len(cands) == 1 and cands[0]["pii_matches_survey"] else None,
    }
    # J. Catal.: docs/28:90 cites 10.1016/j.jcat.2025.115963-range
    pages = pdf_text_pages(JCAT_PDF)
    pdf_dois = sorted(set(re.findall(r"10\.1016/j\.jcat\.\d{4}\.\d+", pages[0])))
    recs = [lookup(fc, d) for d in pdf_dois]
    out["jcat"] = {
        "cited_doi": "10.1016/j.jcat.2025.115963-range",
        "docs28_lines": [r["line"] for r in d28 if r["doi"].startswith("10.1016/j.jcat.2025.115963")],
        "stem_record": next((r.get("stem_record") for r in d28 if r.get("stem_record")), None),
        "local_pdf": rel(JCAT_PDF), "local_pdf_sha256": sha256_file(JCAT_PDF),
        "dois_printed_on_pdf_page1": pdf_dois,
        "candidates": [{"doi": r.doi, "title": r.title, "authors": [a.get("family") for a in r.authors],
                        "journal": r.journal, "volume": r.volume, "pages": r.pages, "year": r.year}
                       for r in recs],
        "corrected_doi": recs[0].doi if len(recs) == 1 and "gc-dft" in recs[0].title.lower()
        and recs[0].journal == "Journal of Catalysis" else None,
    }
    return out


def part_zpe(fc, fs) -> dict:
    return zpe.run(fc, fs)


# ---------------------------------------------------------------------------

def manifest(extra_inputs: list[Path], used_bodies: set[Path]) -> dict:
    """sha256 of every repository input and every cached response.

    Nothing is skipped silently: an input or cache file that cannot be read, a
    response body without its metadata, or a body read this run that the directory
    walk did not list (for example a path beyond the platform length limit) raises.
    Cached responses this run did not read are listed separately.
    """
    files = {}
    for p in sorted(set(extra_inputs)):
        try:
            files[rel(p)] = {"sha256": sha256_file(p), "bytes": p.stat().st_size}
        except OSError as e:
            raise RuntimeError(f"repository input unreadable: {p}: {e}") from e
    used = {rel(p) for p in used_bodies}
    cache, unused, listed = {}, {}, set()
    for d in (OUT / "crossref_cache", OUT / "source_cache"):
        for p in sorted(d.rglob("*")):
            if p.is_dir() or p.name.endswith(".meta.json"):
                continue
            meta_p = p.with_name(p.name.rsplit(".", 1)[0] + ".meta.json")
            try:
                meta = json.loads(meta_p.read_text(encoding="utf-8"))
                entry = {"sha256": sha256_file(p), "bytes": p.stat().st_size, "url": meta.get("url"),
                         "status": meta.get("status"), "fetched_utc": meta.get("fetched_utc")}
            except OSError as e:
                raise RuntimeError(f"cache file or its metadata unreadable: {p}: {e}") from e
            if entry["sha256"] != meta.get("sha256"):
                raise RuntimeError(f"cache body does not match its metadata hash: {p}")
            listed.add(rel(p))
            (cache if rel(p) in used else unused)[rel(p)] = entry
    not_listed = sorted(used - listed)
    if not_listed:
        raise RuntimeError(f"{len(not_listed)} cache files read this run were not listed: {not_listed[:3]}")
    return {"repo_inputs": files, "cached_responses": cache,
            "cached_responses_not_read_this_run": unused,
            "n_repo_inputs": len(files), "n_cached_responses": len(cache),
            "n_cached_responses_not_read_this_run": len(unused)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--no-doc", action="store_true")
    a = ap.parse_args(argv)
    renamed = [x for d in (OUT / "crossref_cache", OUT / "source_cache") for x in migrate_cache_names(d)]
    fc = Fetcher(OUT / "crossref_cache", min_interval=0.3, offline=a.offline)
    src = OUT / "source_cache"
    f_sun = Fetcher(src / "sun2004", min_interval=1.0, offline=a.offline)
    f_arxiv = Fetcher(src / "sun2004", min_interval=3.1, offline=a.offline)
    f_st = Fetcher(src / "structures", min_interval=0.5, offline=a.offline)
    f_zpe = Fetcher(src / "zpe", min_interval=1.0, offline=a.offline)
    f_28 = Fetcher(src / "docs28", min_interval=1.0, offline=a.offline)
    fetchers = [fc, f_sun, f_arxiv, f_st, f_zpe, f_28]

    sun = part_sun(fc, f_sun, f_arxiv)
    write_json(OUT / "sun2004.json", sun)
    st = part_structures(f_st)
    write_json(OUT / "structures.json", st)
    zp = part_zpe(fc, f_zpe)
    write_json(OUT / "zpe_ooh_040.json", zp)
    itf = part_intercept()
    write_json(OUT / "intercept_floor.json", itf)
    bb = part_bib(fc, f_28)
    write_json(OUT / "bib_crossref_check.json", {"summary": bb["bib_summary"], "rows": bb["bib_rows"]})
    write_json(OUT / "docs28_doi_audit.json", {"rows": bb["docs28"], "corrections": bb["docs28_corrections"],
                                               "label_echoes": bb["docs28_label_echoes"]})

    from . import report
    inputs = [REFS_BIB, DOCS28, DOCS43, MLIP_SURVEY, JCAT_PDF, zpe.MAN2011_PDF, zpe.DIVANIS_TXT,
              zpe.DIVANIS_SUMS, zpe.REFERENCING, *sorted(DATA.glob("*.json"))]
    inputs += [REPO / f for f in itf["scanned_files"]]
    inputs += [REPO / f for f in st["scanned_files"]]
    inputs += [p for p in _doc_paths()]
    inputs += [REPO / c["file"] for c in st["claims"]]
    man = manifest(inputs, set().union(*(f.used for f in fetchers)))
    write_json(OUT / "manifest.json", man)
    summary = report.build_summary(sun, st, zp, itf, bb)
    summary["manifest_counts"] = {"repo_inputs": man["n_repo_inputs"],
                                  "cached_responses": man["n_cached_responses"],
                                  "cached_responses_not_read_this_run": man["n_cached_responses_not_read_this_run"],
                                  "not_read_urls": [{"url": v["url"], "status": v["status"]} for v in
                                                    man["cached_responses_not_read_this_run"].values()]}
    write_json(OUT / "summary.json", summary)
    if not a.no_doc:
        write_text(DOC, report.render(summary))
    print(json.dumps({"cache_files_renamed_to_short_keys": len(renamed),
                      "network_requests": sum(f.n_network for f in fetchers),
                      "cached_reads": sum(f.n_cached for f in fetchers),
                      "verdicts": summary["verdicts"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
