"""Main-text page images and 6-up contact sheets for the 22 records of the 2026-10-04 SI-read round.

Rendering method reused unchanged from download_si_review_2026-10-03/prepare_sources.py
(pdf_read + contacts): PyMuPDF page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) -> PNG, named
<SID>_main_pNNN.png; 6-up contact sheets of 1600x2100, each cell 785x650 thumbnail (ImageOps.contain),
page file name drawn at the cell's top-left, named main_01.png, main_02.png, ...

Source identity (per record), all must hold before anything is rendered:
  1. the PDF is the one ft_screen.py extract used: sha256 == texts.csv file_sha256, page count == texts.csv pages;
  2. re-running ft_screen.py's extraction (fitz text of every page joined by newline + reference-list cut)
     reproduces text/<SID>.txt exactly (this is the file named by the pass input's `text` path);
  3. sha256 of text/<SID>.txt == intake_manifest.json main_text.sha256, page count == pass input main_pages;
  4. every other corpus copy of the record (files_manual/, files_dup/) is byte-identical or is reported.

Write-once: an existing output file that differs is an error (as in retain() of the 10-03 script).
No network. Does not touch si_read_round_2026-10-04/files/.

  python render_main_visual.py [--only S31037,S31125]
"""
import argparse
import csv
import glob
import hashlib
import io
import json
import pathlib
import re
import sys

import fitz
from PIL import Image, ImageDraw, ImageOps

HERE = pathlib.Path(__file__).resolve().parent          # .../si_read_round_2026-10-04/main_visual
ROUND = HERE.parent
FT = ROUND.parent
ZOOM = 1.5
CANVAS = (1600, 2100)
CELL = (785, 650)
PER_SHEET = 6

# same expressions as ft_screen.py
RESUME = re.compile(r"^\s*(supporting information|supplementary (information|materials?|data|note|figures?|methods)|electronic supplementary|"
                    r"appendix\b|chapter\s+\d+|\d+\s+chapter)\b.*$", re.I | re.M)
REF = re.compile(r"^\s*(references|references and notes|bibliography|literature cited)\s*$", re.I | re.M)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def retain(path, data):
    """Write-once like the 10-03 script: never overwrite a differing file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Refusing differing copy: " + str(path))
    else:
        with path.open("xb") as stream:
            stream.write(data)


def jsonbytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def rel(path):
    return pathlib.Path(path).resolve().relative_to(FT).as_posix()


def ft_extract_text(path):
    """Exactly ft_screen.extract() for a PDF; returns (text, pages)."""
    doc = fitz.open(path)
    t = "\n".join(p.get_text() for p in doc)
    pages = doc.page_count
    doc.close()
    m = [x for x in REF.finditer(t) if x.start() > 0.55 * len(t)]
    if m:
        cut = m[-1].start()
        after = RESUME.search(t, cut + 20)
        kept = ("\n[text resumes: %s]\n" % after.group(0).strip() + t[after.start():]) if after else ""
        t = t[:cut] + "\n[reference list removed at character %d]\n" % cut + kept
    return t, pages


def contacts(image_paths, directory):
    outputs = []
    for start in range(0, len(image_paths), PER_SHEET):
        canvas = Image.new("RGB", CANVAS, "white")
        draw = ImageDraw.Draw(canvas)
        for j, path in enumerate(image_paths[start:start + PER_SHEET]):
            with Image.open(path) as source:
                thumb = ImageOps.contain(source.convert("RGB"), CELL)
                x, y = (j % 2) * 800, (j // 2) * 700
                canvas.paste(thumb, (x + (800 - thumb.width) // 2, y + 30))
                draw.text((x + 10, y + 8), path.name, fill="black")
        output = directory / ("main_" + str(start // PER_SHEET + 1).zfill(2) + ".png")
        buffer = io.BytesIO()
        canvas.save(buffer, format="PNG")
        retain(output, buffer.getvalue())
        outputs.append({"file": rel(output), "sha256": sha_file(output),
                        "pages": [p.name for p in image_paths[start:start + PER_SHEET]]})
    return outputs


def load_inputs():
    records = {}
    for f in sorted(glob.glob(str(ROUND / "pass_1" / "batches" / "*.in.jsonl"))):
        for line in open(f, encoding="utf-8"):
            d = json.loads(line)
            records[d["screen_id"]] = dict(d, batch=pathlib.Path(f).name)
    return records


def corpus_copies(sid):
    found = []
    for sub in ("files", "files_manual", "files_dup"):
        for p in sorted((FT / sub).glob(sid + "*")):
            found.append(p)
    return found


def process(sid, rec, texts_row, manifest_row, logs):
    note = {"screen_id": sid, "checks": {}, "problems": []}
    copies = corpus_copies(sid)
    copy_info = [{"path": rel(p), "bytes": p.stat().st_size, "sha256": sha_file(p)} for p in copies]
    note["corpus_copies"] = copy_info
    pdfs = [c for c in copy_info if c["path"].lower().endswith(".pdf")]
    primary = next((c for c in pdfs if c["path"] == "files/%s.pdf" % sid), None)
    if primary is None:
        note["status"] = "no PDF in files/"
        note["problems"].append("no files/%s.pdf" % sid)
        return note
    src = FT / primary["path"]
    ck = note["checks"]
    ck["texts_csv_file"] = texts_row["file"]
    ck["texts_csv_sha256_equal"] = texts_row["file_sha256"] == primary["sha256"]
    ck["other_copies_identical"] = all(c["sha256"] == primary["sha256"] for c in pdfs)
    ck["non_pdf_copies"] = [c["path"] for c in copy_info if not c["path"].lower().endswith(".pdf")]
    text, pages = ft_extract_text(src)
    ck["pdf_pages"] = pages
    ck["texts_csv_pages_equal"] = str(pages) == str(texts_row["pages"])
    ck["input_main_pages_equal"] = pages == rec["main_pages"]
    on_disk = (FT / rec["text"]).read_bytes()
    ck["text_file_sha256"] = sha_bytes(on_disk)
    ck["text_sha256_equals_manifest"] = ck["text_file_sha256"] == manifest_row["main_text"]["sha256"]
    ck["manifest_main_pages_equal"] = pages == manifest_row["main_text"]["pages"]
    on_disk_text = on_disk.decode("utf-8").replace("\r\n", "\n")
    ck["reextracted_text_equals_text_file"] = (text == on_disk_text)
    ck["reextracted_chars"] = len(text)
    ck["text_file_chars_pass_input"] = rec["chars"]
    ck["chars_equal_pass_input"] = len(text) == rec["chars"]
    # DOI and title on the PDF itself (supporting identity evidence, not the gate)
    doc = fitz.open(src)
    first = "\n".join(doc[i].get_text() for i in range(min(2, len(doc))))
    ck["doi_in_first_two_pages"] = rec["doi"].lower() in first.lower().replace(" ", "")
    ck["doi_in_whole_pdf"] = any(rec["doi"].lower() in doc[i].get_text().lower().replace(" ", "") for i in range(len(doc)))
    title = manifest_row.get("title", "")
    norm = lambda s: re.sub(r"[^a-z0-9]+", "", s.lower())
    ck["title_in_first_two_pages"] = bool(title) and norm(title)[:60] in norm(first)
    doc.close()
    log = logs.get(sid)
    if log:
        ck["manual_ingest_log"] = {"source_name": log.get("source_name"), "matched_by": log.get("matched_by"),
                                   "route": log.get("route"), "sha256_equal": log.get("sha256") == primary["sha256"]}
    gate = ("texts_csv_sha256_equal", "texts_csv_pages_equal", "input_main_pages_equal", "text_sha256_equals_manifest",
            "manifest_main_pages_equal", "reextracted_text_equals_text_file", "other_copies_identical")
    failed = [g for g in gate if not ck[g]]
    if failed:
        note["status"] = "IDENTITY GATE FAILED: " + ", ".join(failed)
        note["problems"].extend(failed)
        return note
    # render
    out = HERE / sid
    page_dir = out / "pages"
    page_files, page_rows = [], []
    with fitz.open(src) as doc:
        if doc.is_encrypted or not len(doc):
            note["status"] = "unreadable/empty PDF"
            return note
        for number, page in enumerate(doc, 1):
            pix = page.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM))
            image = page_dir / (sid + "_main_p" + str(number).zfill(3) + ".png")
            retain(image, pix.tobytes("png"))
            page_files.append(image)
            page_rows.append({"page": number, "file": rel(image), "width": pix.width, "height": pix.height,
                              "sha256": sha_file(image)})
    sheets = contacts(page_files, out / "contacts")
    index = {
        "screen_id": sid, "doi": rec["doi"], "title": manifest_row.get("title"),
        "pass_input_text_path": rec["text"], "batch": rec["batch"],
        "source": {"path": primary["path"], "absolute": str(src), "sha256": primary["sha256"], "bytes": primary["bytes"],
                   "pages": pages, "other_corpus_copies": [c for c in copy_info if c["path"] != primary["path"]],
                   "identity_checks": ck},
        "render": {"library": "PyMuPDF " + fitz.VersionBind, "page_matrix": [ZOOM, ZOOM], "format": "PNG",
                   "colorspace": "RGB (get_pixmap default), no alpha",
                   "method_source": "download_si_review_2026-10-03/prepare_sources.py pdf_read() and contacts()",
                   "contact_sheet": {"canvas": list(CANVAS), "cell_thumbnail_max": list(CELL), "per_sheet": PER_SHEET,
                                     "grid": "2 columns x 3 rows, 800x700 pitch, label = page file name at cell top-left"},
                   "page_naming": sid + "_main_pNNN.png (3-digit page number)",
                   "contact_naming": "main_NN.png"},
        "pages": page_rows, "contacts": sheets,
    }
    retain(out / "main_visual_index.json", jsonbytes(index))
    note["status"] = "rendered"
    note["pages_rendered"] = len(page_rows)
    note["contacts"] = len(sheets)
    note["source"] = index["source"]
    return note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    inputs = load_inputs()
    only = [s for s in args.only.split(",") if s] or sorted(inputs)
    texts = {r["screen_id"]: r for r in csv.DictReader(open(FT / "texts.csv", encoding="utf-8", newline=""))}
    manifest = {p["screen_id"]: p for p in json.load(open(ROUND / "intake_manifest.json", encoding="utf-8"))["packages"]}
    logs = {}
    for line in open(FT / "manual_ingest_log.jsonl", encoding="utf-8"):
        d = json.loads(line)
        logs[d["screen_id"]] = d
    results = []
    for sid in only:
        r = process(sid, inputs[sid], texts[sid], manifest[sid], logs)
        results.append(r)
        print(sid, r["status"], r.get("pages_rendered", ""), flush=True)
    if not args.only:
        retain(HERE / "main_visual_summary.json", jsonbytes({"round": ROUND.name, "records": len(results),
               "rendered": sum(r["status"] == "rendered" for r in results),
               "results": [{k: v for k, v in r.items() if k != "source"} | {"source_path": r.get("source", {}).get("path"),
                            "source_sha256": r.get("source", {}).get("sha256")} for r in results]}))


if __name__ == "__main__":
    main()
