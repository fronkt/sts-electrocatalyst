"""Verify obtained supplement/article files, extract printed reference blocks, compare the
Lee article PDF bibliography with the 2026-09-21 web transcription, and write
receipts.json + verification.json. Nothing outside this directory is modified.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import unicodedata
import zipfile
from pathlib import Path

import docx
import fitz  # PyMuPDF
from PIL import Image

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[2]
FILES = OUT / "files"
FILES.mkdir(exist_ok=True)
LIM = "10.3389/fenrg.2021.606313"
LEE = "10.1002/cssc.202200015"
LEE_TITLE = "Epitaxial Core-Shell Oxide Nanoparticles"
LIM_TITLE = "First-Principles Design of Rutile Oxide Heterostructures for Oxygen Evolution Reactions"
# printed caption openings read visually from the composited TIFFs (2026-09-23)
VISUAL_LABELS = {
    "image1.tif": "Figure S1. Equation of state for bulk (A) VO2, (B) SnO2, (C) TaO2 and (D) OsO2",
    "image2.tif": "Figure S2. Linear relation between the ESSI and the overpotential of the OER (eta_OER). ...",
    "image3.tif": "Figure S3. Linear scaling relationship of dG3 as a function of dG2 for rutile-type metal oxides. ...",
}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def md5(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


receipts = [json.loads(l) for l in (OUT / "receipts.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
(OUT / "receipts.json").write_text(json.dumps(receipts, indent=2, ensure_ascii=False), encoding="utf-8")
by_label = {}
for r in receipts:
    by_label[r["label"]] = r  # last attempt wins


def body(label: str) -> bytes:
    return (OUT / by_label[label]["path"]).read_bytes()


# every body on disk still matches its receipt hash
hash_checks = []
for r in receipts:
    if r.get("path"):
        ok = sha((OUT / r["path"]).read_bytes()) == r["sha256"]
        hash_checks.append({"label": r["label"], "attempt": r["attempt"], "ok": ok})

checks: dict = {"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "receipt_count": len(receipts),
                "receipt_body_hashes_ok": all(c["ok"] for c in hash_checks),
                "methods": "NOT_CODED", "eligibility": "NOT_SCREENED"}

# ------------------------------------------------------------------ Lim 2021
xml_links = json.loads((REPO / "results/s2_2026-09-21/primary_access/lim_xml_links.json").read_text(encoding="utf-8"))
declared = []
for el in xml_links["supplement_elements"]:
    href = re.search(r'href="([^"]+)"', el).group(1)
    sid = re.search(r'id="([^"]+)"', el).group(1)
    declared.append({"xml_id": sid, "href": href})

manifest = json.loads((OUT / "lim2021_figshare_manifest.json").read_text(encoding="utf-8"))
lim_items = []
for d in declared:
    stem = d["href"].rsplit(".", 1)[0]
    m = [x for x in manifest if x["file"]["name"].startswith(stem + "_")]
    item = {"declared": d, "status": "OPEN"}
    if len(m) != 1:
        item["problem"] = f"{len(m)} figshare matches"
        lim_items.append(item)
        continue
    x = m[0]
    fid = x["file"]["id"]
    rec = by_label[f"lim2021_file_{fid}"]
    b = body(f"lim2021_file_{fid}")
    comp = json.loads(body(f"lim2021_si_doi_{x['doi'].rsplit('.', 1)[1]}_crossref"))["message"]
    ext = d["href"].rsplit(".", 1)[1]
    dest = FILES / f"lim2021_{d['xml_id']}_{d['href']}"
    dest.write_bytes(b)
    item.update({
        "si_doi": x["doi"], "figshare_article_id": x["article_id"], "figshare_file_id": fid,
        "figshare_file_name": x["file"]["name"], "download_url": rec["requested_url"],
        "http_status": rec["http_status"], "content_type": rec["content_type"],
        "bytes": len(b), "sha256": sha(b), "md5": md5(b),
        "figshare_computed_md5": x["file"]["computed_md5"],
        "md5_match": md5(b) == x["file"]["computed_md5"],
        "figshare_resource_doi": x["resource_doi"],
        "resource_doi_match": x["resource_doi"] == LIM,
        "crossref_component_title": comp.get("title"),
        "crossref_component_title_matches_href": comp.get("title") == [d["href"]],
        "crossref_is_component_of": comp.get("relation", {}).get("is-component-of"),
        "saved_as": dest.relative_to(OUT).as_posix(),
    })
    if ext == "docx":
        doc = docx.Document(str(dest))
        text = "\n".join(p.text for p in doc.paragraphs)
        cells = "\n".join(c.text for t in doc.tables for row in t.rows for c in row.cells)
        item["caption"] = text.strip()[:400]
        item["table_count"] = len(doc.tables)
        cite_hits = re.findall(r"\bet al\.|\bdoi\b|\(\d{4}\)|\[\d+\]", text + "\n" + cells, re.I)
        item["reference_list_present"] = bool(re.search(r"^\s*references?\b", text, re.I | re.M))
        item["citation_like_strings"] = cite_hits
    else:
        im = Image.open(dest)
        item.update({"image_format": im.format, "image_size": list(im.size), "image_mode": im.mode,
                     "tiff_extra_sample": "4th sample stored unassociated (ExtraSamples=0); composited as alpha on white for viewing",
                     "printed_caption_label_visual": VISUAL_LABELS[d["href"]],
                     "reference_list_present": False,
                     "reference_note": "raster figure; visual inspection of the composited image shows a figure "
                                       "with its printed caption and no reference list"})
    ok = item["md5_match"] and item["resource_doi_match"] and item["crossref_component_title_matches_href"] \
        and any(r.get("id") == LIM for r in item["crossref_is_component_of"] or []) and rec["http_status"] == 200
    item["status"] = "CLOSED" if ok else "OPEN"
    lim_items.append(item)
checks["lim2021"] = {"article_doi": LIM, "publisher": "Frontiers Media SA (Frontiers in Energy Research)",
                     "declared_files": lim_items,
                     "publisher_component_landing_behaviour":
                         "each Crossref-registered component URL (.../supplementary-material/<s00N DOI>) returned "
                         "HTTP 200 HTML identical in bytes to the article full-text page (no file); files obtained "
                         "from the publisher's figshare portal (frontiersin.figshare.com) instead"}

# ------------------------------------------------------------------ Lee 2022 SI
z = zipfile.ZipFile(OUT / by_label["lee2022_europepmc_supplementary"]["path"])
zip_si = z.read("CSSC-15-0-s001.pdf")
s3_si = body("lee2022_pmc_opendata_si_s001")
pmc_meta = json.loads(body("lee2022_pmc_opendata_meta"))
pmc_md5 = re.search(r"CSSC-15-0-s001\.pdf\?md5=([0-9a-f]+)", " ".join(pmc_meta["media_urls"])).group(1)
si_path = FILES / "lee2022_SI_CSSC-15-0-s001.pdf"
si_path.write_bytes(s3_si)
si_doc = fitz.open(str(si_path))
si_p1 = si_doc[0].get_text()
epmc_xml = body("lee2022_europepmc_fulltextxml").decode("utf-8")
lee_si = {
    "declared": {"article_statement": "Supporting information for this article is available on the WWW under "
                                      "https://doi.org/10.1002/cssc.202200015",
                 "publisher_file_name_2026_09_21": "cssc202200015-sup-0001-misc_information.pdf",
                 "pmc_xml_caption": "Supporting Information", "pmc_media_href": "CSSC-15-0-s001.pdf"},
    "copies": [
        {"route": "europepmc_supplementary_files_zip", "member": "CSSC-15-0-s001.pdf",
         "bytes": len(zip_si), "sha256": sha(zip_si), "md5": md5(zip_si)},
        {"route": "pmc_aws_open_data", "url": by_label["lee2022_pmc_opendata_si_s001"]["requested_url"],
         "bytes": len(s3_si), "sha256": sha(s3_si), "md5": md5(s3_si)},
    ],
    "two_copies_identical": sha(zip_si) == sha(s3_si),
    "pmc_record_md5": pmc_md5, "pmc_md5_match": md5(s3_si) == pmc_md5,
    "pmc_record_doi": pmc_meta["doi"], "pmc_record_doi_match": pmc_meta["doi"] == LEE,
    "pmc_license": pmc_meta.get("license_code"),
    "europepmc_xml_names_file": "CSSC-15-0-s001.pdf" in epmc_xml,
    "pages": si_doc.page_count,
    "title_page_has_title": LEE_TITLE.replace("-", "") in si_p1.replace("-", "").replace("‐", ""),
    "title_page_has_authors": all(a in si_p1 for a in ("Yonghyuk Lee", "Christoph Scheurer", "Karsten Reuter")),
    "title_page_says_supporting_information": "Supporting Information" in si_p1,
    "saved_as": si_path.relative_to(OUT).as_posix(),
    "publisher_byte_comparison": "not possible: every Wiley route returned HTTP 403 (receipts)",
}
lee_si["status"] = "CLOSED" if all(lee_si[k] for k in (
    "two_copies_identical", "pmc_md5_match", "pmc_record_doi_match", "title_page_has_title",
    "title_page_has_authors", "title_page_says_supporting_information")) else "OPEN"


def column_lines(doc, start_pat, end_pat):
    """Read two-column pages left column then right column; return (page1, col, line) tuples
    from the first line matching start_pat through the line matching end_pat."""
    out, started = [], False
    for pno in range(doc.page_count):
        page = doc[pno]
        w = page.rect.width
        h = page.rect.height  # body region excludes running header (y<55) and footer (y>760)
        for col, clip in (("L", fitz.Rect(0, 55, w / 2, 760)),
                          ("R", fitz.Rect(w / 2, 55, w, 760))):
            for ln in page.get_text("text", clip=clip, sort=True).splitlines():
                if not started and re.search(start_pat, ln):
                    started = True
                if started:
                    out.append((pno + 1, col, ln))
                    if re.search(end_pat, ln):
                        return out
    return out


def single_lines(doc, start_pat, end_pat):
    out, started = [], False
    for pno in range(doc.page_count):
        for ln in doc[pno].get_text("text", sort=True).splitlines():
            if not started and re.search(start_pat, ln):
                started = True
            if started:
                out.append((pno + 1, "-", ln))
                if re.search(end_pat, ln):
                    return out
    return out


def write_block(path, lines):
    txt = "\n".join(f"L{i + 1}@P{p}{c if c != '-' else ''}: {t}" for i, (p, c, t) in enumerate(lines)) + "\n"
    path.write_text(txt, encoding="utf-8")
    return sha(txt.encode("utf-8"))


si_lines = single_lines(si_doc, r"^\s*\[1\]\s", r"^THE_END_NEVER$")
si_block = OUT / "lee2022_si_reference_block.txt"
lee_si["reference_block"] = {"path": si_block.name, "sha256": write_block(si_block, si_lines),
                             "line_count": len(si_lines),
                             "numbered_starts": len(re.findall(r"^\s*\[(\d+)\]", "\n".join(t for _, _, t in si_lines), re.M)),
                             "locator_format": "L<n>@P<1-based PDF page>: text (PyMuPDF sorted text)"}

# ------------------------------------------------------------------ Lee 2022 article PDF
art = body("lee2022_pure_rest_content")
pure = json.loads(body("lee2022_pure_item_rest"))
pure_file = pure["files"][0]
art_path = FILES / "lee2022_article_publisher_version_pure.pdf"
art_path.write_bytes(art)
adoc = fitz.open(str(art_path))
p1 = adoc[0].get_text() + adoc[1].get_text()  # PDF page 1 is an image-only cover
lee_art = {
    "route": "MPG PuRe REST component content", "url": by_label["lee2022_pure_rest_content"]["requested_url"],
    "bytes": len(art), "sha256": sha(art), "md5": md5(art),
    "pure_checksum_md5": pure_file["checksum"], "pure_md5_match": md5(art) == pure_file["checksum"],
    "pure_content_category": pure_file["metadata"].get("contentCategory"),
    "pure_license": pure_file["metadata"].get("license"),
    "pure_item_doi": [i["id"] for i in pure["metadata"]["identifiers"] if i["type"] == "DOI"],
    "pdf_page1_text_chars": len(adoc[0].get_text()),
    "pdf_page1_note": "PDF page 1 is image-only (cover graphic); article pages 1-10 are PDF pages 2-11",
    "pdf_doi_on_first_text_page": "10.1002/cssc.202200015" in p1,
    "pdf_title_on_first_text_page": "Epitaxial Core" in p1 and "Shell Oxide Nanoparticles" in p1,
    "pages": adoc.page_count, "saved_as": art_path.relative_to(OUT).as_posix(),
}
art_lines = column_lines(adoc, r"^\s*\[1\]\s+M\. Carmo", r"1705.1718\.")
art_block = OUT / "lee2022_article_pdf_reference_block.txt"
lee_art["reference_block"] = {"path": art_block.name, "sha256": write_block(art_block, art_lines),
                              "line_count": len(art_lines),
                              "locator_format": "L<n>@P<1-based PDF page><L|R column>: text"}


def split_refs(text: str) -> dict:
    parts = re.split(r"(?:(?<=\s)|^)\[(\d+)\]\s", text)
    refs = {}
    for i in range(1, len(parts) - 1, 2):
        refs[int(parts[i])] = parts[i + 1]
    return refs


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


LAYOUT_PATTERNS = [
    r"L\d+@P[\d-]+:\s?",                                  # web-transcription locators (can sit mid-line)
    r"ChemSusChem 2022, 15, e202200015 \(\d+ of 10\)",    # running footer
    r"© 2022 The Authors\. ChemSusChem published by Wiley-VCH GmbH",
    r"Research Article", r"doi\.org/10\.1002/cssc\.202200015",   # running header
    r"\bChemSusChem\b", r"\b202200015\b",                 # header/footer residue; no cited ref contains these
]


def strip_layout(s: str) -> str:
    for pat in LAYOUT_PATTERNS:
        s = re.sub(pat, " ", s)
    return s


def join_lines(lines):
    return " ".join(t.strip() for t in lines)


web_raw = (REPO / "results/s2_2026-09-21/backward_reference_extension/lee2022_article_reference_block.txt").read_text(encoding="utf-8")
web_refs_raw = split_refs(join_lines([re.sub(r"^L\d+@P[\d-]+:\s?", "", l) for l in web_raw.splitlines()]))
web_refs = split_refs(strip_layout(join_lines(web_raw.splitlines())))
pdf_refs = split_refs(strip_layout(join_lines([t for _, _, t in art_lines])))
diffs = []
for n in sorted(set(web_refs) | set(pdf_refs)):
    a, b = norm(web_refs.get(n, "")), norm(pdf_refs.get(n, ""))
    if a != b:
        # tolerate only line-break artefacts: compare with all whitespace removed
        ws_only = re.sub(r"\s", "", a) == re.sub(r"\s", "", b)
        diffs.append({"ref": n, "web": a, "pdf": b, "whitespace_only": ws_only})
lee_art["comparison_with_web_transcription"] = {
    "web_block": "results/s2_2026-09-21/backward_reference_extension/lee2022_article_reference_block.txt",
    "web_block_sha256": sha(web_raw.encode("utf-8")),
    "web_ref_count_raw_split": len(web_refs_raw),
    "web_ref_count_raw_split_note": "raw split misses [58] because its label follows a footer on the same web line (L896)",
    "layout_patterns_removed_before_comparison": LAYOUT_PATTERNS,
    "web_ref_count": len(web_refs), "pdf_ref_count": len(pdf_refs),
    "numbers_equal": sorted(web_refs) == sorted(pdf_refs),
    "identical_after_whitespace_normalisation": sum(1 for n in pdf_refs if n in web_refs and norm(web_refs[n]) == norm(pdf_refs[n])),
    "differences": diffs,
    "refs_differing_before_layout_removal": {
        "web_vs_pdf": sorted(n for n in set(web_refs_raw) | set(pdf_refs)
                             if norm(web_refs_raw.get(n, "")) != norm(pdf_refs.get(n, ""))),
        "explanation": "with only line-start locators removed, the web transcription carries running header/footer text "
                       "inside ref 57 and prints the [58] label mid-line after a footer (L896), so a raw split loses [58]; "
                       "the PDF block is clipped to the page body region",
    },
    "note": "comparison is text-level only; differences are recorded, not resolved; existing indexes unchanged",
}

checks["lee2022"] = {"article_doi": LEE, "publisher": "Wiley-VCH (ChemSusChem 15(10) e202200015)",
                     "pmcid": "PMC9321688", "supplement": lee_si, "article_pdf": lee_art}
checks["summary"] = {
    "lim2021_declared_files": len(lim_items),
    "lim2021_closed": sum(1 for i in lim_items if i["status"] == "CLOSED"),
    "lee2022_supplement": lee_si["status"],
    "lee2022_article_pdf": "OBTAINED_VERIFIED" if lee_art["pure_md5_match"] and lee_art["pdf_doi_on_first_text_page"] and lee_art["pdf_title_on_first_text_page"] else "OPEN",
}
checks["receipt_body_hash_checks"] = hash_checks
(OUT / "verification.json").write_text(json.dumps(checks, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(checks["summary"], indent=2))
print("lee diffs:", len(diffs), "ws-only:", sum(d["whitespace_only"] for d in diffs))
