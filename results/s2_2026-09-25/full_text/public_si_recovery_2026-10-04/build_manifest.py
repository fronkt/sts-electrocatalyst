"""Build recovered_manifest.json from downloads.jsonl + verify_si.py evidence. Recomputes size and sha256 from disk and
fails loudly on any mismatch.  Retrieval evidence only; no eligibility judgement."""
import csv
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

T = json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))
REC = {t["screen_id"]: t for t in T["targets"] + T["skipped_dead_end"]}
DL = {}
for line in open(L.PHASE / "downloads.jsonl", encoding="utf-8"):
    d = json.loads(line)
    DL[pathlib.Path(d["local_path"]).name] = d

RS = "researchsquare_public_preprint_page_file_list"
ELS = "elsevier_article_asset_cdn_PII_addressed_mmc"
PKG = [
    # sid, main file, extra files, source_route, caveat, checklist items, ready
    ("S21177", "S21177_SupportingInformation.docx", [], RS, "", "Figs. S25-S28", True),
    ("S30575", "S30575_Supplementary.docx",
     ["S30575_MovieS1_FlexibleIrO2catalyst.mp4", "S30575_MovieS2_IrO2NPscatalyst.mp4", "S30575_MovieS3_ComIrO2Umicorecatalyst.mp4"], RS,
     "Movies S1-S3 are non-text media of the same package. The source's Supplementary Fig. S3 caption lacks its 'S3' label (text '3D AFM...' neighbours S2/S4); content is present.",
     "Fig. S46, Fig. S6", True),
    ("S11392", "S11392_VelascoVelezetal_NatureEnergySI2020.docx", [], RS,
     "PREPRINT-version SI (Fig. S1-S7, Table S1-S2, 25 pages). The journal version S13010 (JACS 10.1021/jacs.1c01655) has a different, already-read SI (17 pages, Fig. S1-S10). Handoff dead end concerned the journal lead; whether this preprint SI needs reads is for the coordinator.", "", True),
    ("S23135", "S23135_mmc1.docx", [], ELS, "", "Fig. S13", True),
    ("S31137", "S31137_mmc1.docx", [], ELS, "", "Tables S1-S2", True),
    ("S00358", "S00358_mmc1.pdf", [], ELS, "Main text names no specific SI item; completeness is by the exact PII-addressed file plus the SI's own title page and 'Tables 1-3' content.", "", True),
    ("S00887", "S00887_mmc1.docx", [], ELS, "", "", True),
    ("S05043", "S05043_mmc1.docx", [], ELS, "", "", True),
    ("S11279", "S11279_mmc1.pdf", [], ELS, "", "", True),
    ("S20599", "S20599_mmc1.docx", [], ELS, "", "", True),
    ("S23308", "S23308_mmc1.docx", [], ELS,
     "One-page SI whose only content is 'Table 1 - ZPE and TS corrections' as an EMF image; no title/authors inside, so identity rests on the PII-addressed file name; table values are only in the image (needs visual reading).", "", True),
    ("S27476", "S27476_mmc1.docx", [], ELS, "", "", True),
    ("S31037", "S31037_mmc1.docx", [], ELS, "", "", True),
    ("S14704", "S14704_mmc1.docx", [], ELS, "Handoff dead end (repository copies were main-only); recovered by a different route.", "Table S6", True),
]


def collapse(s):
    return re.sub(r"\s+", " ", s).strip()


def item_present(token_text, caps):
    out = {}
    for m in re.finditer(r"(Fig(?:ure)?s?\.?|Tables?)\s*S\s?(\d+)(?:\s*(?:-|and|,)\s*S?\s?(\d+))?", token_text, flags=re.I):
        kind = "Figure" if m.group(1).lower().startswith("fig") else "Table"
        a = int(m.group(2))
        b = int(m.group(3)) if m.group(3) else a
        for n in range(a, b + 1):
            out["%s S%d" % (kind, n)] = ("%s S%d" % (kind, n)) in caps
    return out


packages = []
for sid, main, extra, route, caveat, chk, ready in PKG:
    rec = REC[sid]
    files = []
    for name in [main] + extra:
        d = DL[name]
        p = L.FILES / name
        sha = L.sha256_file(p)
        assert sha == d["sha256"] and p.stat().st_size == d["bytes"], "hash/size mismatch for " + name
        files.append({"local_path": d["local_path"], "bytes": d["bytes"], "sha256": sha, "source_url": d["url"],
                      "fetched_at_utc": d["at_utc"], "http_status": d["http_status"]})
    stem = pathlib.Path(main).stem[:40]
    v = json.loads((L.META / ("%s_verify_%s.json" % (sid, stem))).read_text(encoding="utf-8"))
    text = (L.META / ("%s_si_text_%s.txt" % (sid, stem))).read_text(encoding="utf-8")
    caps = set(v["si_caption_labels_found"])
    ident = v["identity"]
    checklist_items = item_present(chk, caps) if chk else {}
    f0 = v["files"][0]
    pages = f0.get("pages")
    packages.append({
        "screen_id": sid, "doi": rec["doi"], "title_checklist": rec["title"], "publisher": rec["publisher"],
        "checklist_tier": 1, "checklist_priority_group": rec["priority_group"], "v5_final_at_start": rec["current_v5_final"],
        "source_route": route,
        "source_route_detail": ("Plain HTTP GET of the public Research Square preprint page; its embedded __NEXT_DATA__ file list names this file with role=supplement, "
                                "and the role=manuscript-pdf entry has the same byte size as the local main copy; file fetched from assets-eu.researchsquare.com"
                                if route == RS else
                                "Plain HTTP GET (honest User-Agent, no key, no login) of ars.els-cdn.com/content/image/1-s2.0-<PII>-mmc1.<ext>, the file the article page's "
                                "'Appendix A. Supplementary data' links to; PII from the Crossref alternative-id of the exact DOI; mmc2+ tried and absent"),
        "files": files,
        "pages": pages,
        "pages_basis": "PDF page count" if f0["file"].lower().endswith(".pdf") else "Word-stored page count (docProps/app.xml); no layout render available",
        "identity_evidence": {
            "quoted_head_of_si_text": collapse(text[:420]),
            "title_full_in_si_text": ident["title_full_in_si_text"], "title_first8_words_in_si_text": ident["title_first8_words_in_si_text"],
            "author_surnames_found_in_si": "%d of %d Crossref author surnames, first 12 at most (%s)" % (len(ident["author_surnames_found"]), len(ident["author_surnames_checked"]),
                                                                            ", ".join(sorted(set(ident["author_surnames_found"])))) if ident["author_surnames_checked"] else "not checked (no Crossref author list cached for this record)",
            "doi_string_in_si_text": ident["doi_in_si_text"],
            "addressing": ("exact article PII in the URL: " + files[0]["source_url"]) if route == ELS else
                          "file listed on the preprint page of the exact DOI; manuscript-pdf byte size = local main copy",
        },
        "completeness_evidence": {
            "main_text_SI_items_referenced": v["main_text_SI_items_referenced"],
            "main_referenced_items_missing_from_SI_text": v["main_referenced_items_missing_from_si_text"],
            "SI_caption_labels_found": v["si_caption_labels_found"],
            "checklist_items_present": checklist_items,
            "docx_media_files": f0.get("docx_media_files"), "docx_tables": f0.get("docx_tables"), "pdf_images": f0.get("pdf_images"),
        },
        "caveats": caveat,
        "ready_for_two_blind_reads": ready,
        "outcome": "recovered",
    })
out = {"phase": "public_si_recovery_2026-10-04", "retrieval_only": True, "packages": packages,
       "note": "Binaries stay under public_si_recovery_2026-10-04/files/ (ignored by git via results/). sha256 and sizes were recomputed from disk."}
(L.PHASE / "recovered_manifest.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(len(packages), "packages")
for p in packages:
    miss = [k for k, ok in p["completeness_evidence"]["checklist_items_present"].items() if not ok]
    print(p["screen_id"], p["pages"], "refs", len(p["completeness_evidence"]["main_text_SI_items_referenced"]),
          "missing", p["completeness_evidence"]["main_referenced_items_missing_from_SI_text"], "checklist-miss", miss)
