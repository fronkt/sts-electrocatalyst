"""SI-read intake of 2026-10-04: pinned local reading copies and visual inventories for the recovered SI packages.
No eligibility decision, no verdict, no network.

Method reused from the most recent completed SI-read phase (download_si_review_2026-10-03/prepare_sources.py,
inspect_word_extras.py, decode_wdp.ps1; mixed_format reading in inspect_mixed_formats.py) and from si_read.py of the
2026-09-28 round (SI file header, [<file> p. N] markers):
  * PDF   : PyMuPDF page text in native order, one '[<tag> p. N]' marker per page, 1.5x page PNGs, 6-up contact sheets.
  * Word  : paragraph-by-paragraph accepted-revision text ('[<file> paragraph N]', N counts every w:p of the part as in
            inspect_word_extras.py), embedded-image markers, original media + PNG previews + 6-up contact sheets, OMML,
            revisions and embedded-object inventory (word_extras.json), Pandoc accepted-revision view appended as a
            'structured equation/table reading aid' when the file has tables, equations or embedded objects.
  * Refinements, each recorded in the reading file or here: text-box paragraphs are read once (the mc:Fallback copy is
    skipped), w:sym symbols and no-break hyphens are kept, tabs and manual line breaks are kept, RGBA/palette images are
    flattened on white for previews (10-03 noted black backgrounds), EMF/WMF are rendered at 150 dpi.
  * Binary .doc (not met in 10-02/10-03; si_read.py marked it 'not extracted'): text and tables with antiword, blank-line
    blocks numbered for location only, embedded PNG carved by signature.
  * Video: ffprobe inventory only (as in inspect_mixed_formats.py); not viewed.

  python prepare_si_round.py [--only S23135,S00358] [--clean]
Never overwrites a differing reading copy (write-once, like 10-03's retain()); --clean removes this script's own
files/<SID> directory first.  Reads the two recovery manifests, verifies every source sha256 against them.
"""
import argparse
import hashlib
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.parse
import zipfile

import fitz
from lxml import etree
from PIL import Image, ImageDraw, ImageOps

HERE = pathlib.Path(__file__).resolve().parent
FT = HERE.parent
NOWIN = 0x08000000
Image.MAX_IMAGE_PIXELS = None
PRIOR = FT / "public_si_recovery_2026-10-04"
EXT = FT / "public_si_recovery_2026-10-04_ext"
PANDOC = pathlib.Path("C:/Users/frank/AppData/Local/Pandoc/pandoc.exe")
XSL = pathlib.Path("C:/Program Files/Microsoft Office/root/Office16/OMML2MML.XSL")

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "o": "urn:schemas-microsoft-com:office:office", "v": "urn:schemas-microsoft-com:vml",
      "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006"}
W = "{%s}" % NS["w"]
M = "{%s}" % NS["m"]
A = "{%s}" % NS["a"]
R = "{%s}" % NS["r"]
O = "{%s}" % NS["o"]
V = "{%s}" % NS["v"]
MC = "{%s}" % NS["mc"]

# Adobe Symbol font code (w:sym w:font="Symbol" w:char="F0xx") -> Unicode, the part of the table that matters for chemistry
SYMBOL = {0x41: "Α", 0x42: "Β", 0x43: "Χ", 0x44: "Δ", 0x45: "Ε", 0x46: "Φ", 0x47: "Γ", 0x48: "Η", 0x49: "Ι", 0x4A: "ϑ", 0x4B: "Κ",
          0x4C: "Λ", 0x4D: "Μ", 0x4E: "Ν", 0x4F: "Ο", 0x50: "Π", 0x51: "Θ", 0x52: "Ρ", 0x53: "Σ", 0x54: "Τ", 0x55: "Υ", 0x56: "ς",
          0x57: "Ω", 0x58: "Ξ", 0x59: "Ψ", 0x5A: "Ζ", 0x61: "α", 0x62: "β", 0x63: "χ", 0x64: "δ", 0x65: "ε", 0x66: "φ", 0x67: "γ",
          0x68: "η", 0x69: "ι", 0x6A: "ϕ", 0x6B: "κ", 0x6C: "λ", 0x6D: "μ", 0x6E: "ν", 0x6F: "ο", 0x70: "π", 0x71: "θ", 0x72: "ρ",
          0x73: "σ", 0x74: "τ", 0x75: "υ", 0x76: "ϖ", 0x77: "ω", 0x78: "ξ", 0x79: "ψ", 0x7A: "ζ", 0xA3: "≤", 0xA5: "∞", 0xAB: "↔",
          0xAC: "←", 0xAD: "↑", 0xAE: "→", 0xAF: "↓", 0xB0: "°", 0xB1: "±", 0xB3: "≥", 0xB4: "×", 0xB5: "∝", 0xB6: "∂", 0xB7: "•",
          0xB9: "≠", 0xBA: "≡", 0xBB: "≈", 0xD2: "®", 0xD3: "©", 0xD4: "™", 0xD6: "√", 0xD7: "⋅", 0xE5: "∑", 0xF2: "∫"}


# ---------------------------------------------------------------- generic helpers
def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def rel(path):
    return pathlib.Path(path).resolve().relative_to(FT).as_posix()


def retain(path, data):
    """Write-once: a differing existing file is refused (10-03's rule)."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Refusing differing intake copy: " + str(path))
    else:
        with path.open("xb") as stream:
            stream.write(data)


def jsonbytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def flatten(im):
    """RGB copy; transparent areas on white (10-03 saw black backgrounds from convert('RGB'))."""
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        return bg.convert("RGB")
    if im.mode in ("I;16", "I;16L", "I;16B", "I"):
        im = im.point(lambda i: i / 256.0).convert("L")
    return im.convert("RGB")


def is_blank(rgb):
    ext = rgb.getextrema()
    return all(lo >= 250 for lo, hi in ext) or all(hi <= 5 for lo, hi in ext)


def contacts(items, directory, stem):
    """6-up contact sheets (1600 x 2100) of (label, image path) pairs, as prepare_sources.contacts()."""
    outputs = []
    for start in range(0, len(items), 6):
        canvas = Image.new("RGB", (1600, 2100), "white")
        draw = ImageDraw.Draw(canvas)
        for j, (label, path) in enumerate(items[start:start + 6]):
            with Image.open(path) as source:
                thumb = ImageOps.contain(flatten(source), (785, 650))
            x, y = (j % 2) * 800, (j // 2) * 700
            canvas.paste(thumb, (x + (800 - thumb.width) // 2, y + 30))
            draw.text((x + 10, y + 8), label, fill="black")
        output = directory / (stem + "_" + str(start // 6 + 1).zfill(2) + ".png")
        buffer = io.BytesIO()
        canvas.save(buffer, format="PNG")
        retain(output, buffer.getvalue())
        outputs.append(rel(output))
    return outputs


# ---------------------------------------------------------------- PDF
def pdf_package(path, tag, out, sid):
    texts, pages, flags_pages = [], [], []
    with fitz.open(path) as doc:
        if doc.is_encrypted or not len(doc):
            raise ValueError("Unreadable/empty PDF " + str(path))
        embedded = doc.embfile_names()
        for number, page in enumerate(doc, 1):
            text = page.get_text()
            texts.append("[" + tag + " p. " + str(number) + "]\n" + text)
            image = out / "si_pages" / (sid + "_si_p" + str(number).zfill(3) + ".png")
            retain(image, page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).tobytes("png"))
            n_img, n_draw = len(page.get_images(full=True)), len(page.get_drawings())
            pages.append({"page": number, "chars": len(text), "images": n_img, "vector_drawings": n_draw, "image": rel(image)})
            if n_img or n_draw >= 20 or len(text.strip()) < 100:
                flags_pages.append(number)
        meta = dict(doc.metadata or {})
    sheets = contacts([("p. %d" % p["page"], FT / p["image"]) for p in pages], out / "contacts", "si")
    return {"text": "\n\n".join(texts), "pages": pages, "n_pages": len(pages), "embedded_files": embedded, "metadata": meta,
            "contacts": sheets, "figure_like_pages": flags_pages}


# ---------------------------------------------------------------- Word (docx)
def rels_map(z, part):
    name = pathlib.PurePosixPath(part)
    rname = str(name.parent / "_rels" / (name.name + ".rels"))
    if rname not in z.namelist():
        return {}
    return {n.attrib["Id"]: (n.attrib.get("Target"), n.attrib.get("Type", "").rsplit("/", 1)[-1], n.attrib.get("TargetMode"))
            for n in etree.fromstring(z.read(rname))}


def in_fallback(el):
    return any(a.tag == MC + "Fallback" for a in el.iterancestors())


def para_text(p):
    """Accepted-revision text of one paragraph: w:del / w:moveFrom skipped, nested text-box paragraphs left to their own entry."""
    parts = []

    def walk(n):
        tag = n.tag
        if tag in (W + "del", W + "moveFrom", W + "txbxContent", MC + "Fallback", W + "delText", W + "instrText"):
            return
        if tag in (W + "t", M + "t"):
            parts.append(n.text or "")
            return
        if tag == W + "tab" and n.getparent().tag == W + "r":
            parts.append("\t")
            return
        if tag == W + "br" and n.attrib.get(W + "type") != "page":
            parts.append("\n")
            return
        if tag == W + "noBreakHyphen":
            parts.append("-")
            return
        if tag == W + "sym":
            font, code = n.attrib.get(W + "font", ""), n.attrib.get(W + "char", "")
            try:
                num = int(code, 16)
            except ValueError:
                num = None
            ch = SYMBOL.get(num & 0xFF) if (font == "Symbol" and num is not None) else None
            if font == "Wingdings" and num is not None and (num & 0xFF) == 0xE0:
                ch = "→"  # Wingdings 0xE0 is a right arrow
            parts.append(ch if ch else "[sym %s %s]" % (font, code))
            return
        for c in n:
            walk(c)
    walk(p)
    return "".join(parts)


def media_refs(p, rels):
    """Targets of the images (a:blip, v:imagedata) and OLE objects referenced inside paragraph p (own content only)."""
    out = []
    for el in p.iter():
        if el is p:
            continue
        nearest = next((a for a in el.iterancestors() if a.tag == W + "p"), None)
        if nearest is not p:  # inside a nested (text-box) paragraph: that paragraph's own entry carries it
            continue
        if any(a.tag == MC + "Fallback" for a in el.iterancestors()):
            continue
        rid = None
        if el.tag == A + "blip":
            rid = el.attrib.get(R + "embed")
        elif el.tag == V + "imagedata":
            rid = el.attrib.get(R + "id")
        elif el.tag == O + "OLEObject":
            rid = el.attrib.get(R + "id")
        if rid and rid in rels and rels[rid][0]:
            out.append((rid, rels[rid][0], el.tag.rsplit("}", 1)[-1]))
    return out


def wmf_or_open(data, dpi=150):
    im = Image.open(io.BytesIO(data))
    fmt = im.format
    frames = getattr(im, "n_frames", 1)
    if fmt == "WMF":
        im.load(dpi=dpi)
    else:
        im.load()
    return im, fmt, frames


PS_EXE = "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"


def render_metafile(src, dst, long_side=1600):
    """GDI+ rendering of a WMF/EMF to PNG (render_metafile.ps1); Pillow's stub garbles MathType equation metafiles."""
    dst = pathlib.Path(dst)
    if dst.exists():
        return True, "existing"
    r = subprocess.run([PS_EXE, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(HERE / "render_metafile.ps1"),
                        "-SourcePath", str(src), "-TargetPath", str(dst), "-LongSide", str(long_side)],
                       capture_output=True, creationflags=NOWIN, timeout=120)
    return r.returncode == 0 and dst.exists(), (r.stdout + r.stderr).decode("utf-8", "replace").strip()[:200]


def strips(items, directory, stem, per_sheet=10):
    """Sheets of wide, short items (equations): one per row, 1600 x 2100."""
    outputs = []
    for start in range(0, len(items), per_sheet):
        canvas = Image.new("RGB", (1600, 2100), "white")
        draw = ImageDraw.Draw(canvas)
        for j, (label, path) in enumerate(items[start:start + per_sheet]):
            with Image.open(path) as source:
                thumb = ImageOps.contain(flatten(source), (1560, 180))
            y = j * 210
            draw.text((10, y + 4), label, fill="black")
            canvas.paste(thumb, (20, y + 20))
        output = directory / (stem + "_" + str(start // per_sheet + 1).zfill(2) + ".png")
        buffer = io.BytesIO()
        canvas.save(buffer, format="PNG")
        retain(output, buffer.getvalue())
        outputs.append(rel(output))
    return outputs


def docx_package(path, tag, out, sid):
    z = zipfile.ZipFile(path)
    assert z.testzip() is None, "DOCX CRC failure: " + str(path)
    names = z.namelist()
    parts = ["word/document.xml"] + sorted(n for n in names if n.startswith("word/") and n.count("/") == 1 and n.endswith(".xml")
                                              and pathlib.PurePosixPath(n).name.startswith(("header", "footer", "footnotes", "endnotes", "comments")))
    chunks, paragraphs_total = [], 0
    media_use = {}  # member -> list of (part, paragraph index, kind)
    para_records = []  # for caption lookup (document.xml only)
    objects, equations, revisions = [], [], []
    xml_main = z.read("word/document.xml")
    transform = etree.XSLT(etree.parse(str(XSL))) if XSL.exists() else None
    for part in parts:
        data = z.read(part)
        root = etree.fromstring(data)
        rels = rels_map(z, part)
        lines, any_text = [], False
        for i, p in enumerate(root.iter(W + "p"), 1):
            if in_fallback(p):
                continue
            text = para_text(p)
            refs = media_refs(p, rels)
            if part == "word/document.xml":
                para_records.append((i, text))
                for rid, target, kind in refs:
                    member = str(pathlib.PurePosixPath("word") / target) if not target.startswith("/") else target.lstrip("/")
                    media_use.setdefault(member, []).append({"paragraph": i, "kind": kind})
                for formula in p.findall(".//" + M + "oMath"):
                    idx = len(equations) + 1
                    src = etree.tostring(formula, encoding="utf-8")
                    mml = None
                    if transform is not None:
                        mml = etree.tostring(transform(etree.fromstring(src)), encoding="utf-8").decode("utf-8")
                    equations.append({"paragraph": i, "index": idx, "omml": src.decode("utf-8"), "mathml": mml})
                for tg in ("ins", "del", "moveFrom", "moveTo"):
                    for ch in p.findall(".//" + W + tg):
                        revisions.append({"paragraph": i, "kind": tg, "text": "".join((e.text or "") for e in ch.iter() if e.tag in (W + "t", W + "delText", M + "t"))})
                for obj in p.findall(".//" + W + "object"):
                    ole = obj.find(".//" + O + "OLEObject")
                    info = {"paragraph": i, "context": text[:200]}
                    if ole is not None:
                        info["progid"] = ole.attrib.get("ProgID")
                        t = rels.get(ole.attrib.get(R + "id", ""))
                        if t and t[0]:
                            member = str(pathlib.PurePosixPath("word") / t[0])
                            blob = z.read(member)
                            info.update({"target": t[0], "bytes": len(blob), "sha256": sha_bytes(blob), "magic_hex": blob[:16].hex()})
                            retain(out / "embedded_objects" / pathlib.PurePosixPath(t[0]).name, blob)
                    pv = obj.find(".//" + V + "imagedata")
                    if pv is not None:
                        pt = rels.get(pv.attrib.get(R + "id", ""))
                        info["preview_target"] = pt[0] if pt else None
                    objects.append(info)
            if text.strip() or refs:
                any_text = any_text or bool(text.strip())
                img = ""
                if refs:
                    img = "\n[embedded image relationship IDs: " + ", ".join("%s (%s)" % (rid, target) for rid, target, kind in refs) + "]"
                lines.append("[" + tag + " paragraph " + str(i) + "]\n" + text + img)
        paragraphs_total += len(lines) if part == "word/document.xml" else 0
        if part == "word/document.xml" or any_text:
            chunks.append("[DOCX part " + part + "]\n\n" + "\n\n".join(lines))
    # media: originals, previews, contact sheets
    media, previews = [], []
    members = [n for n in names if n.startswith("word/media/") and not n.endswith("/")]
    for member in members:
        p = pathlib.PurePosixPath(member)
        if len(p.parts) != 3 or p.name in (".", ".."):
            raise ValueError("Unsafe embedded media path " + member)
        data = z.read(member)
        target = out / "docx_media" / p.name
        retain(target, data)
        entry = {"member": member, "file": rel(target), "sha256": sha_bytes(data), "bytes": len(data), "used_at": media_use.get(member, []),
                 "preview": None, "note": None}
        suffix = p.suffix.lower()
        if suffix == ".svg":
            entry["note"] = "SVG: no raster preview (Pillow cannot render SVG); the picture's PNG fallback, if any, is a separate media item"
        else:
            try:
                rendered = None
                if suffix in (".wmf", ".emf"):
                    cand = target.with_name(target.name + ".png")
                    ok, msg = render_metafile(target, cand)
                    if ok:
                        rendered = cand
                        entry["renderer"] = "GDI+ (render_metafile.ps1)"
                    else:
                        entry["renderer"] = "Pillow fallback (GDI+ failed: %s); MathType equation metafiles may be garbled" % msg
                if rendered is not None:
                    im = Image.open(rendered)
                    im.load()
                    fmt, frames = "WMF/EMF metafile", 1
                else:
                    im, fmt, frames = wmf_or_open(data)
                entry.update({"image_format": fmt, "frames": frames, "pixels": list(im.size)})
                rgb = flatten(im)
                if frames != 1:
                    entry["note"] = "multi-frame (%d frames): preview shows frame 1 only" % frames
                if is_blank(rgb):
                    entry["note"] = (entry["note"] + "; " if entry["note"] else "") + "preview is uniformly blank/black (renderer limitation or empty image)"
                if rendered is not None:
                    display = rendered  # GDI+ output is already RGB on white
                elif suffix in (".png", ".jpg", ".jpeg") and im.mode in ("RGB", "L") and frames == 1:
                    display = target
                else:
                    display = target.with_name(target.name + ".png")
                    buf = io.BytesIO()
                    rgb.save(buf, format="PNG")
                    retain(display, buf.getvalue())
                entry["preview"] = rel(display)
                previews.append((p.name, display, entry))
            except Exception as e:  # noqa: BLE001 - recorded, never silent
                entry["note"] = "preview failed: %s: %s" % (type(e).__name__, str(e)[:160])
        media.append(entry)
    order = lambda e: (min([u["paragraph"] for u in e["used_at"]] or [10 ** 9]), e["member"])  # document order, unused last
    previews_sorted = sorted(previews, key=lambda t: order(t[2]))
    sheet_items, wide_items = [], []
    for name, display, e in previews_sorted:
        at = ",".join(str(u["paragraph"]) for u in e["used_at"][:2])
        label = "%s%s" % (name, (" (para %s)" % at) if at else " (unused in body)")
        with Image.open(display) as probe:
            wide = probe.width / probe.height >= 4 and probe.height <= 600
        (wide_items if wide else sheet_items).append((label, display))
    sheets = contacts(sheet_items, out / "contacts", "word") if sheet_items else []
    sheets += strips(wide_items, out / "contacts", "word_wide") if wide_items else []
    # nearest caption candidates (reading aid)
    cap_re = re.compile(r"^\s*(?:Supplementary\s+)?(?:Fig(?:ure)?\.?|Table|Scheme)\s*S?[\s\-]*\d", re.I)
    texts_by_idx = dict(para_records)
    idxs = sorted(texts_by_idx)
    for e in media:
        for u in e["used_at"]:
            k = u["paragraph"]
            cand = None
            for j in [x for x in idxs if x > k][:6]:
                if texts_by_idx[j].strip() and cap_re.match(texts_by_idx[j]):
                    cand = (j, texts_by_idx[j].strip()[:140])
                    break
            if cand is None:
                for j in [x for x in idxs if x < k][-4:][::-1]:
                    if texts_by_idx[j].strip() and cap_re.match(texts_by_idx[j]):
                        cand = (j, texts_by_idx[j].strip()[:140])
                        break
            u["nearest_caption_candidate"] = {"paragraph": cand[0], "text": cand[1]} if cand else None
    app = z.read("docProps/app.xml").decode("utf-8", "ignore") if "docProps/app.xml" in names else ""
    pages_m = re.search(r"<Pages>(\d+)</Pages>", app)
    n_tables = len(etree.fromstring(xml_main).findall(".//" + W + "tbl"))
    text = "\n\n".join(chunks)
    aid = None
    if n_tables or equations or objects:
        receipt = subprocess.run([str(PANDOC), "--from=docx", "--to=markdown", "--track-changes=accept", str(path)],
                                 capture_output=True, creationflags=NOWIN, timeout=300)
        if receipt.returncode:
            raise ValueError("pandoc failed: " + receipt.stderr.decode("utf-8", "replace"))
        retain(out / (sid + "_" + pathlib.Path(path).stem.split("_", 1)[-1] + "_pandoc_accepted.md"), receipt.stdout)
        aid = receipt.stdout.decode("utf-8").replace("\r\n", "\n")  # Pandoc on Windows writes CRLF
    extras = {"source": pathlib.Path(path).name, "equations": equations, "revisions": revisions, "embedded_objects": objects,
              "accepted_text_policy": "Exclude w:del/w:moveFrom; include w:ins/w:moveTo. Text-box paragraphs read once (mc:Fallback copy skipped).",
              "xsl_present": transform is not None, "docx_page_layout_rendered": False, "embedded_object_executed": False,
              "ole_stream_inventory": "olefile unavailable; embedded objects not parsed or executed (bytes, hash and magic only)"}
    return {"text": text, "aid": aid, "paragraph_entries": paragraphs_total, "media": media, "contacts": sheets, "tables": n_tables,
            "equations": len(equations), "revisions": len(revisions), "objects": objects, "extras": extras,
            "word_pages_stored": int(pages_m.group(1)) if pages_m else None, "parts": parts}


# ---------------------------------------------------------------- binary .doc
def doc_package(path, tag, out, sid):
    r = subprocess.run(["antiword", "-m", "UTF-8.txt", str(path)], capture_output=True, creationflags=NOWIN, timeout=120)
    if r.returncode:
        raise ValueError("antiword failed: " + r.stderr.decode("utf-8", "replace"))
    body = r.stdout.decode("utf-8", "replace").replace("\r\n", "\n")
    blocks = [b for b in re.split(r"\n\s*\n", body) if b.strip()]
    text = "\n\n".join("[" + tag + " block " + str(i) + "]\n" + b.strip("\n") for i, b in enumerate(blocks, 1))
    raw = pathlib.Path(path).read_bytes()
    sigs = {"png": raw.count(b"\x89PNG\r\n\x1a\n"), "jpeg": raw.count(b"\xff\xd8\xff"), "gif": raw.count(b"GIF8"),
            "emf": raw.count(b" EMF"), "wmf": raw.count(b"\xd7\xcd\xc6\x9a")}
    carved, previews = [], []
    pos = 0
    while True:
        i = raw.find(b"\x89PNG\r\n\x1a\n", pos)
        if i < 0:
            break
        j = raw.find(b"IEND", i)
        if j < 0:
            break
        data = raw[i:j + 8]
        pos = j + 8
        n = len(carved) + 1
        target = out / "doc_media" / ("carved_png_%d.png" % n)
        retain(target, data)
        with Image.open(io.BytesIO(data)) as im:
            entry = {"file": rel(target), "sha256": sha_bytes(data), "bytes": len(data), "pixels": list(im.size), "mode": im.mode,
                     "note": "carved from the .doc by PNG signature (offset %d); position in the document not recoverable without Word" % i}
            rgb = flatten(im)
        if rgb.size and is_blank(rgb):
            entry["note"] += "; preview is uniformly blank/black"
        display = target.with_name(target.name + ".display.png")
        buf = io.BytesIO()
        rgb.save(buf, format="PNG")
        retain(display, buf.getvalue())
        entry["preview"] = rel(display)
        carved.append(entry)
        previews.append((target.name, display))
    sheets = contacts(previews, out / "contacts", "doc") if previews else []
    other = {k: v for k, v in sigs.items() if k != "png" and v}
    return {"text": text, "blocks": len(blocks), "pic_markers": body.count("[pic]"), "signatures": sigs, "carved": carved,
            "other_signatures_not_carved": other, "contacts": sheets, "antiword_stderr": r.stderr.decode("utf-8", "replace")}


# ---------------------------------------------------------------- video
def video_package(path, out):
    p = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(path)],
                       capture_output=True, text=True, creationflags=NOWIN, timeout=60)
    if p.returncode:
        raise ValueError("Video probe failed: " + pathlib.Path(path).name)
    probe = json.loads(p.stdout)
    retain(out / "video_inventory" / (pathlib.Path(path).name + ".ffprobe.json"), jsonbytes(probe))
    v = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {})
    return {"duration_s": float(probe["format"].get("duration", 0)), "width": v.get("width"), "height": v.get("height"),
            "codec": v.get("codec_name"), "visual_review_complete": False}


# ---------------------------------------------------------------- facts (si_read.py facts(), same rule)
def facts_for(sid):
    import csv
    out = []
    p = FT / "reconcile" / "identity_check.csv"
    for r in csv.DictReader(open(p, encoding="utf-8")):
        if r["supplied_to_reads"] != "yes":
            continue
        if sid in r["records"].split(";"):
            out.append("Identity check at reconciliation (v5 D9): %s = %s; rutile-type (P4_2/mnm): %s. Source: %s" % (
                r["item"], r["identity"], r["rutile_type"], r["source"]))
    return out


# ---------------------------------------------------------------- packages
# sid -> (manifest path, extra reading notes)
SKIP = {"S11392": "Frank 2026-10-04: linkage only, not sent to the reads (decisions_2026-10-04.md)"}
KNOWN_FALSE_MISSING = {"S30334": {"Section S6": "regex false hit on the main text's 'Sections 6.6.1 and 6.6.2'"}}


def load_packages():
    pk = []
    for base in (PRIOR, EXT):
        m = json.loads((base / "recovered_manifest.json").read_text(encoding="utf-8"))
        for p in m["packages"]:
            if p["screen_id"] in SKIP:
                continue
            p["_manifest"] = rel(base / "recovered_manifest.json")
            pk.append(p)
    return pk


def texts_row(sid):
    import csv
    for r in csv.DictReader(open(FT / "texts.csv", encoding="utf-8")):
        if r["screen_id"] == sid:
            return r
    raise KeyError(sid)


def process(pkg):
    sid = pkg["screen_id"]
    out = HERE / "files" / sid
    chunks, files_meta, tags = [], [], []
    detail = {"pdf": [], "docx": [], "doc": [], "video": []}
    si_files = []
    for f in pkg["files"]:
        path = FT / f["local_path"]
        assert path.stat().st_size == f["bytes"] and sha_file(path) == f["sha256"], "source hash/size mismatch: " + str(path)
        tag = path.name.split("_", 1)[1]  # 'mmc1.docx' (si_read.py convention: the name after the record id)
        published = urllib.parse.unquote(f["source_url"].split("?")[0].rstrip("/").split("/")[-1])
        head = "[SI file %s: %s (published as %s)]" % (tag, path.name, published)
        suffix = path.suffix.lower()
        si_files.append(path.name)
        tags.append(tag)
        meta = {"file": f["local_path"], "tag": tag, "bytes": f["bytes"], "sha256": f["sha256"], "published_as": published, "source_url": f["source_url"]}
        if suffix == ".pdf":
            d = pdf_package(path, tag, out, sid)
            chunks.append(head + "\n" + d["text"])
            detail["pdf"].append(d)
            meta["kind"] = "pdf"
            meta["pages"] = d["n_pages"]
        elif suffix == ".docx":
            # a second Word file with identical paragraph text and media (S22127 mmc2) is read once and said so
            twin = next((x for x in detail["docx"] if x.get("_twin_key") == docx_key(path)), None)
            if twin is not None:
                chunks.append(head + " identical in paragraph text and media to %s (comparison verified by this script); text not repeated" % twin["_tag"])
                meta.update({"kind": "docx", "duplicate_of": twin["_tag"]})
                files_meta.append(meta)
                continue
            d = docx_package(path, tag, out, sid)
            d["_twin_key"] = docx_key(path)
            d["_tag"] = tag
            chunks.append(head + "\n" + d["text"])
            detail["docx"].append(d)
            meta.update({"kind": "docx", "word_pages_stored": d["word_pages_stored"], "tables": d["tables"], "media_items": len(d["media"]),
                         "equations": d["equations"], "embedded_objects": len(d["objects"])})
        elif suffix == ".doc":
            d = doc_package(path, tag, out, sid)
            chunks.append(head + " binary Word 97-2003; text and tables read with antiword (blocks are blank-line-separated runs, numbered for location only); images are not in the text\n" + d["text"])
            detail["doc"].append(d)
            meta.update({"kind": "doc", "blocks": d["blocks"], "carved_images": len(d["carved"])})
        elif suffix == ".mp4":
            d = video_package(path, out)
            chunks.append(head + " video, %.1f s, %sx%s %s, %d bytes; not text; not viewed" % (d["duration_s"], d["width"], d["height"], d["codec"], f["bytes"]))
            detail["video"].append(dict(d, tag=tag))
            meta.update({"kind": "video", "duration_s": d["duration_s"]})
        else:
            raise ValueError("Unhandled format: " + path.name)
        files_meta.append(meta)
    # reading copy
    text = "\n\n".join(chunks)
    aids = [d["aid"] for d in detail["docx"] if d["aid"]]
    if aids:
        text += "\n\n[Structured equation/table reading aid: Pandoc accepted-revision view; not additional author evidence]\n" + "\n\n".join(aids)
    text += "\n"
    reading = out / (sid + "_si_reading.txt")
    retain(reading, text.encode("utf-8"))
    return {"out": out, "text": text, "reading": reading, "files": files_meta, "tags": tags, "si_files": si_files, "detail": detail}


def docx_key(path):
    z = zipfile.ZipFile(path)
    root = etree.fromstring(z.read("word/document.xml"))
    paras = ["".join(x.text or "" for x in p.iter(W + "t")) for p in root.iter(W + "p")]
    media = {n: sha_bytes(z.read(n)) for n in z.namelist() if n.startswith("word/media/")}
    return sha_bytes(json.dumps([paras, sorted(media.items())], ensure_ascii=False).encode("utf-8"))


def flags_and_limits(sid, pkg, res):
    d = res["detail"]
    flags, limits = [], []
    for k, pd in enumerate(d["pdf"]):
        n = len(pd["figure_like_pages"])
        flags.append({"kind": "pdf_figure_or_image_pages", "count": n, "pages": pd["figure_like_pages"],
                      "visual": pd["contacts"], "why": "figures/plots/scans are images or vector drawings; the text has captions and printed labels, not plotted values"})
        limits.append("PDF pages with images, vector drawings or little text: %s (page images and contact sheets provided)" % pd["figure_like_pages"])
    for wd in d["docx"]:
        used = [e for e in wd["media"] if e["used_at"]]
        flags.append({"kind": "word_embedded_images", "count": len(wd["media"]), "referenced_in_body": len(used), "visual": wd["contacts"],
                      "index": rel(res["out"] / "visual_index.json"),
                      "why": "figure images (plots, spectra, micrographs, tables-as-image) are not in the text; captions are"})
        limits.append("Word page layout not rendered (locations use paragraph numbers and figure labels); %d embedded media items are images, read from contact sheets and previews" % len(wd["media"]))
        if wd["objects"]:
            flags.append({"kind": "word_embedded_objects", "count": len(wd["objects"]),
                          "why": "OLE objects (e.g. equation objects) show their content only as preview images; objects were not executed or parsed"})
            limits.append("%d embedded OLE objects retained; their visible content is the preview image only" % len(wd["objects"]))
        if wd["equations"]:
            limits.append("%d OMML equation(s) transformed to MathML and shown as Pandoc TeX in the reading aid" % wd["equations"])
        if wd["revisions"]:
            limits.append("%d tracked revision(s); accepted view used" % wd["revisions"])
        blank = [e["member"] for e in wd["media"] if e.get("note") and "blank" in e["note"]]
        nopv = [e["member"] for e in wd["media"] if not e.get("preview")]
        if blank:
            flags.append({"kind": "preview_blank", "members": blank, "why": "preview rendered uniformly blank/black; open the original media item"})
        if nopv:
            flags.append({"kind": "no_preview", "members": nopv, "why": "no raster preview could be made; see visual_index.json"})
    for dd in d["doc"]:
        flags.append({"kind": "doc_embedded_images", "count": len(dd["carved"]), "pic_markers_in_text": dd["pic_markers"], "visual": dd["contacts"],
                      "why": "the [pic] in the text is an image (the carved PNG); its values are not in the text"})
        limits.append("Binary .doc read with antiword: no page layout; %d embedded PNG carved by signature (position in the document not recoverable); other image signatures: %s" % (
            len(dd["carved"]), dd["other_signatures_not_carved"] or "none"))
    for v in d["video"]:
        flags.append({"kind": "video", "file": v["tag"], "why": "video of the same SI package; not text, not viewed (inventory only)"})
    if d["video"]:
        limits.append("%d video file(s) of the package are not text and were not viewed" % len(d["video"]))
    return flags, limits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--clean", action="store_true")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    summary = {}
    for pkg in load_packages():
        sid = pkg["screen_id"]
        if only and sid not in only:
            continue
        if a.clean and (HERE / "files" / sid).exists():
            shutil.rmtree(HERE / "files" / sid)
        res = process(pkg)
        # visual index (Word media -> paragraphs -> caption candidates)
        idx = {"screen_id": sid, "note": "Reading aid built from the file's own structure; nearest_caption_candidate is a mechanical guess, not author evidence.",
               "word_media": [e for wd in res["detail"]["docx"] for e in wd["media"]],
               "doc_media": [c for dd in res["detail"]["doc"] for c in dd["carved"]],
               "pdf_pages": [p for pd in res["detail"]["pdf"] for p in pd["pages"]]}
        retain(res["out"] / "visual_index.json", jsonbytes(idx))
        for wd in res["detail"]["docx"]:
            retain(res["out"] / "word_extras.json", jsonbytes(wd["extras"]))
        flags, limits = flags_and_limits(sid, pkg, res)
        summary[sid] = {"files": res["files"], "reading": rel(res["reading"]), "reading_sha256": sha_file(res["reading"]),
                        "chars": len(res["text"]), "flags": flags, "limitations": limits, "si_files": res["si_files"], "tags": res["tags"]}
        retain(res["out"] / "source_metadata.json", jsonbytes({"screen_id": sid, "doi": pkg["doi"], "title": pkg["title_checklist"], "recovery_manifest": pkg["_manifest"],
                                                              "source_route": pkg["source_route"], **summary[sid]}))
        print(sid, "chars", len(res["text"]), "files", [m["kind"] for m in res["files"]], "flags", [f["kind"] for f in flags], flush=True)
    sp = HERE / "reading_copies_summary.json"
    old = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    old.update(summary)
    sp.write_bytes(jsonbytes(old))


if __name__ == "__main__":
    sys.exit(main())
