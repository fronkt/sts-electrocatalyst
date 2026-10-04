"""Build recovered_manifest.json (this directory) from downloads.jsonl + verify_si.py evidence.  Recomputes size and sha256
from disk and fails loudly on any mismatch; appends one final-outcome row per record to search_log.jsonl (idempotent).
Retrieval evidence only; no eligibility judgement."""
import json
import pathlib
import re
import sys
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

TARGETS = {t["screen_id"]: t for t in json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))["targets"]}
DL = {}
for line in open(L.PHASE / "downloads.jsonl", encoding="utf-8"):
    d = json.loads(line)
    DL[pathlib.Path(d["local_path"]).name] = d
ELS = "elsevier_article_asset_cdn_PII_addressed_mmc"
ROUTE_DETAIL = ("Plain HTTP GET (honest User-Agent, no key, no login, no api.elsevier.com) of "
                "ars.els-cdn.com/content/image/1-s2.0-<PII>-mmc<N>.<ext>, the file the article page's 'Appendix A. Supplementary data' "
                "links to; PII from the Crossref alternative-id of the exact DOI (confirmed equal to the PII in the checklist's "
                "ScienceDirect link); mmc1 found with the extension noted in the file name, mmc2+ tried with pdf/docx/zip/xlsx/doc")

# sid -> (files, caveat, checklist items text, page-count basis note)
PKG = [
    ("S22127", ["S22127_mmc1.docx", "S22127_mmc2.docx"],
     "Two files: mmc1 and mmc2 have identical paragraph text and identical media members (comparison recorded below); they differ only in "
     "Word markup (document.xml, footer, settings, docProps). Treated as one SI whose text is read once.", "Fig. S24, Fig. S24, S32"),
    ("S23544", ["S23544_mmc1.docx"], "", ""),
    ("S31125", ["S31125_mmc1.docx"],
     "The SI's own title ('Molybdenum-mediated electronic modulation of RuO2 for balancing oxygen intermediate adsorption and lattice oxygen "
     "participation in acidic oxygen evolution reaction') differs from the published title; identity rests on the exact PII-addressed file, "
     "the same four authors (Yuhan Wang, Yihao Qu, Min Yu and Ji Yang, whom the SI prints as 'Yang Ji'), the same sample names (Mo-17-RuO2, Mo-25-RuO2) and the main text's Fig. S1 / Tables S3-S4 "
     "matching the SI's own captions.", ""),
    ("S00882", ["S00882_mmc1.doc"],
     "Binary Word 97-2003 .doc: text and tables read with antiword; the file's one embedded image (the 'Fig. SI' Pourbaix diagram, PNG) "
     "is not in the text and needs visual reading. Main text names no numbered SI item; completeness rests on the exact PII-addressed "
     "file, its title/authors page, sections a)-f) and the 'Fig. SI' caption.", ""),
    ("S14386", ["S14386_mmc1.pdf"], "", "Table S2"),
    ("S21070", ["S21070_mmc1.docx"], "Caption-label census contains table-of-contents artefacts (the contents lines run the page number into the label, "
     "e.g. 'Figure S38' is Figure S3 on page 8); Figures S1-S34 and Tables S1-S7 are present and no main-referenced item is missing.",
     "Fig. S27a, Fig. S27b-29"),
    ("S30334", ["S30334_mmc1.pdf"],
     "The verify script listed 'Section S6' as missing; that is a false hit on the main text's 'Sections 6.6.1 and 6.6.2' (case-insensitive "
     "regex), not an SI item. No SI item named by the main text is missing.", ""),
    ("S21253", ["S21253_mmc1.docx"], "Word-stored page count is 1 (docProps), which does not match 29 figure captions and 2 tables; page count not relied on.", ""),
    ("S29795", ["S29795_mmc1.docx"], "Crossref lists 6 authors, OpenAlex 8; all 6 Crossref surnames are in the SI text.", ""),
]
NOT_RECOVERED = {
    "S22941": ("not-found",
               "mmc1 tried on ars.els-cdn.com with pdf, docx, zip, xlsx, doc, xls, pptx, txt, csv, mp4, docm, rtf: all HTTP 404 (exact names only; "
               "not evidence that no supplement exists). The main text says 'Structures and scripts are available in the electronic supplementary "
               "material at link: https://nano.ku.dk/english/research/theoretical-electrocatalysis/katladb/loer-runio2/' (a public University of "
               "Copenhagen page); that link is outside the approved Elsevier-CDN route and was not requested."),
}


def collapse(s):
    return re.sub(r"\s+", " ", s).strip()


def parse_items(s):
    """'Fig. S24, Fig. S24, S32' / 'Fig. S27a, Fig. S27b-29' / 'Table S2' -> {'Figure S24', ...}"""
    out, kind = [], "Figure"
    for tok in re.split(r"[;,]", s):
        m = re.search(r"(Fig(?:ure)?s?\.?|Tables?)?\s*S?\s*(\d+)[a-z]?(?:\s*[-–]\s*S?\s*(\d+)[a-z]?)?", tok.strip(), re.I)
        if not m:
            continue
        if m.group(1):
            kind = "Figure" if m.group(1).lower().startswith("fig") else "Table"
        a = int(m.group(2))
        b = int(m.group(3)) if m.group(3) else a
        out += ["%s S%d" % (kind, n) for n in range(a, max(a, b) + 1)]
    return out


def docx_pair_evidence(a, b):
    from lxml import etree
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    za, zb = zipfile.ZipFile(a), zipfile.ZipFile(b)

    def paras(z):
        root = etree.fromstring(z.read("word/document.xml"))
        return ["".join(x.text or "" for x in p.iter(W + "t")) for p in root.iter(W + "p")]
    pa, pb = paras(za), paras(zb)
    media_a = {n: za.read(n) for n in za.namelist() if n.startswith("word/media/")}
    media_b = {n: zb.read(n) for n in zb.namelist() if n.startswith("word/media/")}
    differing = [n for n in za.namelist() if n in zb.namelist() and za.read(n) != zb.read(n)]
    ev = {"paragraphs_mmc1": len(pa), "paragraphs_mmc2": len(pb), "paragraph_text_identical": pa == pb,
          "media_members_mmc1": len(media_a), "media_members_mmc2": len(media_b), "media_members_byte_identical": media_a == media_b,
          "zip_members_differing": differing}
    assert ev["paragraph_text_identical"] and ev["media_members_byte_identical"], ev
    return ev


packages, outcome_rows = [], []
for sid, names, caveat, chk in PKG:
    rec = TARGETS[sid]
    files = []
    for name in names:
        d = DL[name]
        p = L.FILES / name
        sha = L.sha256_file(p)
        assert sha == d["sha256"] and p.stat().st_size == d["bytes"], "hash/size mismatch for " + name
        files.append({"local_path": d["local_path"], "bytes": d["bytes"], "sha256": sha, "source_url": d["url"],
                      "fetched_at_utc": d["at_utc"], "http_status": d["http_status"]})
    stem = pathlib.Path(names[0]).stem[:40]
    v = json.loads((L.META / ("%s_verify_%s.json" % (sid, stem))).read_text(encoding="utf-8"))
    text = (L.META / ("%s_si_text_%s.txt" % (sid, stem))).read_text(encoding="utf-8")
    ident = v["identity"]
    idm = json.loads((L.META / ("%s_identity.json" % sid)).read_text(encoding="utf-8"))["identity_checks"]
    caps = set(v["si_caption_labels_found"])
    si_items_text = text
    present = {k: (k in caps) for k in parse_items(chk)} if chk else {}
    f0 = v["files"][0]
    pages = f0.get("pages")
    suffix = pathlib.Path(names[0]).suffix.lower()
    pair = docx_pair_evidence(L.FILES / names[0], L.FILES / names[1]) if len(names) == 2 else None
    pkg = {
        "screen_id": sid, "doi": rec["doi"], "title_checklist": rec["title"], "publisher": rec["publisher"],
        "checklist_tier": rec["checklist_tier"], "v5_final_at_start": rec["current_v5_final"],
        "source_route": ELS, "source_route_detail": ROUTE_DETAIL,
        "files": files, "pages": pages,
        "pages_basis": ("PDF page count" if suffix == ".pdf" else
                        "not claimed (binary .doc, text read with antiword)" if suffix == ".doc" else
                        "Word-stored page count (docProps/app.xml); no layout render available"),
        "identity_confirmation_crossref_openalex": idm,
        "identity_evidence": {
            "quoted_head_of_si_text": collapse(text[:420]),
            "title_full_in_si_text": ident["title_full_in_si_text"], "title_full_compact_in_si_text": ident["title_full_compact_in_si_text"],
            "title_first8_words_in_si_text": ident["title_first8_words_in_si_text"],
            "author_surnames_found_in_si": "%d of %d Crossref author surnames, first 12 at most (%s)" % (
                len(ident["author_surnames_found"]), len(ident["author_surnames_checked"]), ", ".join(sorted(set(ident["author_surnames_found"])))),
            "doi_string_in_si_text": ident["doi_in_si_text"],
            "addressing": "exact article PII in the URL: " + files[0]["source_url"],
        },
        "completeness_evidence": {
            "main_text_SI_items_referenced": v["main_text_SI_items_referenced"],
            "main_referenced_items_missing_from_SI_text": v["main_referenced_items_missing_from_si_text"],
            "SI_caption_labels_found": v["si_caption_labels_found"],
            "checklist_items_present": present,
            "docx_media_files": f0.get("docx_media_files"), "docx_tables": f0.get("docx_tables"), "pdf_images": f0.get("pdf_images"),
            "mmc1_mmc2_comparison": pair,
        },
        "caveats": caveat,
        "ready_for_two_blind_reads": True,
        "outcome": "recovered",
    }
    packages.append(pkg)
    note = ("Final: Elsevier article-asset CDN file(s) addressed by the article PII; %s pages; title in SI text=%s; authors found %d/%d; "
            "main-text SI items referenced=%d, missing=%d; SI caption labels=%d. %s") % (
        pages, ident["title_full_in_si_text"] or ident["title_full_compact_in_si_text"], len(ident["author_surnames_found"]),
        len(ident["author_surnames_checked"]), len(v["main_text_SI_items_referenced"]),
        len(v["main_referenced_items_missing_from_si_text"]), len(v["si_caption_labels_found"]), caveat)
    outcome_rows.append((sid, rec["doi"], "recovered", note))
for sid, (outc, note) in NOT_RECOVERED.items():
    outcome_rows.append((sid, TARGETS[sid]["doi"], outc, note))

out = {"phase": "public_si_recovery_2026-10-04_ext", "retrieval_only": True,
       "approval": "Frank, in session, 2026-10-04: extend the Elsevier asset-CDN route to the ten non-tier-1 Elsevier checklist records",
       "packages": packages,
       "not_recovered": [{"screen_id": s, "doi": TARGETS[s]["doi"], "title_checklist": TARGETS[s]["title"], "outcome": o, "note": n}
                         for s, (o, n) in NOT_RECOVERED.items()],
       "note": "Binaries stay under public_si_recovery_2026-10-04_ext/files/ (ignored by git via results/). sha256 and sizes were recomputed from disk."}
(L.PHASE / "recovered_manifest.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

logged = L.PHASE / "outcomes_logged.json"
done = set(json.loads(logged.read_text(encoding="utf-8"))) if logged.exists() else set()
for sid, doi, outc, note in outcome_rows:
    if sid not in done:
        L.log(sid, doi, "record_final_outcome", "", None, outc, note)
        done.add(sid)
logged.write_text(json.dumps(sorted(done), indent=1), encoding="utf-8")
print(len(packages), "packages;", len(NOT_RECOVERED), "not recovered")
for p in packages:
    miss = [k for k, ok in p["completeness_evidence"]["checklist_items_present"].items() if not ok]
    print(p["screen_id"], p["pages"], "refs", len(p["completeness_evidence"]["main_text_SI_items_referenced"]),
          "missing", p["completeness_evidence"]["main_referenced_items_missing_from_SI_text"], "checklist-miss", miss)
