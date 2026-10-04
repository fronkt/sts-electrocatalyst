"""Identity + completeness evidence for a downloaded candidate SI (PDF, DOCX or ZIP of those).

  python verify_si.py SID PATH            -> prints a JSON evidence block and saves metadata/<SID>_verify_<name>.json

Evidence collected (no scientific reading, no eligibility judgement):
  * format, bytes, sha256, page count (PDF: pages; DOCX: Word-stored Pages in docProps/app.xml, paragraphs, tables, media)
  * identity: checklist title / DOI / first-author surname found in the SI text (exact, case-insensitive, whitespace-collapsed)
  * completeness: every SI item (Figure/Table/Note/Text/Section S<n>) named by the exact record's main text
    (text/<SID>.txt) is looked up in the SI text; captions present vs referenced-but-missing are listed
"""
import csv
import hashlib
import json
import pathlib
import re
import sys
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

sid, path = sys.argv[1], pathlib.Path(sys.argv[2]).resolve()
T = json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))
rec = next((t for t in T["targets"] + T["skipped_dead_end"] + T["not_reached"] if t["screen_id"] == sid), {})
title = rec.get("title", "")
doi = rec.get("doi", "")

ITEM = re.compile(r"\b(Fig(?:ure)?s?\.?|Tables?|Notes?|Texts?|Sections?|Schemes?)\s*(?:S|S-)\s?(\d{1,3})([a-z])?"
                  r"(?:\s*(?:[-–—]|to|and|,|&)\s*(?:S|S-)?\s?(\d{1,3}))?", re.I)


def items_in(text):
    out = {}
    for m in ITEM.finditer(text):
        kind = m.group(1).lower()
        kind = "Figure" if kind.startswith("fig") else "Table" if kind.startswith("tab") else "Note" if kind.startswith("note") \
            else "Text" if kind.startswith("text") else "Section" if kind.startswith("sec") else "Scheme"
        a = int(m.group(2))
        b = int(m.group(4)) if m.group(4) else a
        if b < a or b - a > 60:
            b = a
        for n in range(a, b + 1):
            out.setdefault("%s S%d" % (kind, n), 0)
            out["%s S%d" % (kind, n)] += 1
    return out


def collapse(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def text_of_pdf(p):
    import fitz
    doc = fitz.open(p)
    pages = [pg.get_text() for pg in doc]
    return "\n".join(pages), len(pages), {"pdf_pages": len(pages), "pdf_images": sum(len(pg.get_images()) for pg in doc),
                                          "pdf_meta_title": (doc.metadata or {}).get("title")}


def text_of_docx(p):
    """All w:t text of the main document part, paragraph by paragraph, including paragraphs inside text boxes and
    tables (python-docx's paragraph list misses text-box captions)."""
    import docx
    from lxml import etree
    z = zipfile.ZipFile(p)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    root = etree.fromstring(z.read("word/document.xml"))
    paras = []
    for para in root.iter("{%s}p" % ns["w"]):
        t = "".join(x.text or "" for x in para.iter("{%s}t" % ns["w"]))
        if t.strip():
            paras.append(t)
    d = docx.Document(str(p))
    app = z.read("docProps/app.xml").decode("utf-8", "ignore") if "docProps/app.xml" in z.namelist() else ""
    pages = re.search(r"<Pages>(\d+)</Pages>", app)
    media = [n for n in z.namelist() if n.startswith("word/media/")]
    info = {"docx_pages_word_stored": int(pages.group(1)) if pages else None, "docx_paragraphs": len(d.paragraphs),
            "docx_text_paragraphs_xml": len(paras), "docx_tables": len(d.tables), "docx_media_files": len(media),
            "docx_embedded_objects": len([n for n in z.namelist() if n.startswith("word/embeddings/")])}
    return "\n".join(paras), info.get("docx_pages_word_stored"), info


def analyse(p):
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        return text_of_pdf(p)
    if suffix in (".docx", ".docm"):
        return text_of_docx(p)
    raise SystemExit("unsupported suffix " + suffix)


blocks = []
members = [path]
if path.suffix.lower() == ".zip":
    z = zipfile.ZipFile(path)
    out = L.FILES / ("_unz_" + path.stem)
    z.extractall(out)
    members = [m for m in out.rglob("*") if m.suffix.lower() in (".pdf", ".docx")]

main_txt = (L.FT / "text" / ("%s.txt" % sid))
main_items = items_in(main_txt.read_text(encoding="utf-8", errors="ignore")) if main_txt.exists() else {}
authors = []
meta_files = sorted(L.META.glob("%s_sweep.json" % sid))
if meta_files:
    sw = json.loads(meta_files[0].read_text(encoding="utf-8"))
    authors = [a[0] for a in (sw.get("crossref", {}).get("authors") or []) if a and a[0]]
elif (L.META / ("%s_authors.json" % sid)).exists():
    authors = [a[0] for a in json.loads((L.META / ("%s_authors.json" % sid)).read_text(encoding="utf-8")) if a and a[0]]

all_text = ""
for m in members:
    text, pages, info = analyse(m)
    all_text += "\n" + text
    flat = collapse(text)
    block = {"file": str(m.relative_to(L.FT)).replace("\\", "/"), "bytes": m.stat().st_size, "sha256": L.sha256_file(m),
             "pages": pages, "text_chars": len(text)}
    block.update(info)
    blocks.append(block)

flat = collapse(all_text)
t_flat = collapse(title)
ident = {"title_full_in_si_text": bool(t_flat and t_flat in flat),
         "title_first8_words_in_si_text": bool(t_flat and " ".join(t_flat.split()[:8]) in flat),
         "doi_in_si_text": bool(doi and doi.lower() in all_text.lower()),
         "author_surnames_found": [a for a in authors if collapse(a) and collapse(a) in flat][:12],
         "author_surnames_checked": authors[:12]}
si_items = items_in(all_text)
# captions: lines that begin with the item label
captions = sorted({"%s S%s" % ("Figure" if m.group(1).lower().startswith("fig") else "Table", m.group(2))
                   for m in re.finditer(r"(?im)^\s*(?:Supplementary\s+)?(Fig(?:ure)?\.?|Table)\s*S\s?(\d{1,3})\b", all_text)},
                  key=lambda s: (s.split()[0], int(s.split("S")[-1])))
missing = sorted([k for k in main_items if k not in si_items], key=lambda s: (s.split()[0], int(s.split("S")[-1])))
ev = {"screen_id": sid, "doi": doi, "title_checklist": title, "files": blocks, "identity": ident,
      "main_text_SI_items_referenced": sorted(main_items, key=lambda s: (s.split()[0], int(s.split("S")[-1]))),
      "main_referenced_items_missing_from_si_text": missing,
      "si_caption_labels_found": captions, "si_items_mentioned_count": len(si_items)}
dest = L.META / ("%s_verify_%s.json" % (sid, path.stem[:40]))
dest.write_text(json.dumps(ev, indent=1, ensure_ascii=False), encoding="utf-8")
(L.META / ("%s_si_text_%s.txt" % (sid, path.stem[:40]))).write_text(all_text, encoding="utf-8")
print(json.dumps(ev, indent=1, ensure_ascii=False))
