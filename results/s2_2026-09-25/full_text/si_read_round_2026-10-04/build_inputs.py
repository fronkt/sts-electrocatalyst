"""Pass inputs of the 2026-10-04 SI-read intake: per-paper lines in the schema of SI_READ_BRIEF.md (screen_id, doi, text,
si_text, si_complete, si_files, facts; plus chars/si_chars as in si_read.py and the visual_root/main_pages/si_pages/word_media/
word_extras/limitations fields of the 2026-10-03 inputs), batched as ft_screen.py / si_read.py batch (480,000 characters of text
and at most 10 papers per batch) after grouping by SI format as in 2026-10-03 (pdf_*, word_*).  Pass 1 and pass 2 get
byte-identical content in separate files.  Writes intake_manifest.json and pass_<n>/plan.json.  No verdict, no eligibility decision.

  python build_inputs.py        (run prepare_si_round.py first)
"""
import csv
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
FT = HERE.parent
sys.path.insert(0, str(HERE))
from prepare_si_round import facts_for, load_packages, rel, sha_file  # noqa: E402

# constants of ft_screen.py, read from the file (not imported: importing would write a __pycache__ into the corpus root)
_src = (FT / "ft_screen.py").read_text(encoding="utf-8")
BUDGET = int(re.search(r"^BUDGET\s*=\s*([0-9_]+)", _src, re.M).group(1).replace("_", ""))
MAX_PER_BATCH = int(re.search(r"^MAX_PER_BATCH\s*=\s*(\d+)", _src, re.M).group(1))
assert (BUDGET, MAX_PER_BATCH) == (480000, 10), (BUDGET, MAX_PER_BATCH)
INSTR = FT / "eligibility_instructions.md"
INSTR_SHA = "e910951616a433cecff859996be6c922d4e9f22808c1d19aa568198014913fb9"  # v5, as pinned in si_read/pass_1/plan.json
assert sha_file(INSTR) == INSTR_SHA, "eligibility_instructions.md changed"

KNOWN_FALSE_MISSING = {"S30334": {"Section S6": "regex false hit on the main text's 'Sections 6.6.1 and 6.6.2'"}}
# Reader-facing notes about the SI file itself (format / identity facts), in addition to the format limitations
PACKAGE_NOTE = {
    "S23308": "The SI's only content ('Supplementary information / Table 1 - ZPE and TS corrections') is a table stored as an EMF image; its values are not in the text. "
              "The document has no title or authors inside, so identity rests on the PII-addressed file name (exact article PII in the download URL).",
    "S00358": "The main text names no specific SI item; the SI says its Fermi smearing values are in Tables 1-3 below.",
    "S30575": "Movies S1-S3 are video files of the same package; not text, not viewed. The source's Supplementary Fig. S3 caption lacks its 'S3' label (its text neighbours S2 and S4).",
    "S22127": "mmc2.docx has the same paragraph text and media as mmc1.docx (differs only in Word markup); its text is not repeated.",
    "S31125": "The SI's own title differs from the published article title; identity rests on the exact PII-addressed file, the same authors and the same sample names.",
    "S00882": "Binary .doc: no page layout; one figure ('Fig. SI', a Pourbaix diagram) is an image outside the text.",
}
IDENTITY_NOTE = {
    "S23308": "PII file name only (no title/authors inside the SI)",
    "S31125": "exact PII file + authors + sample names (SI title differs from the published title)",
}


def main_info(sid):
    p = FT / "text" / (sid + ".txt")
    t = p.read_text(encoding="utf-8")
    pages = None
    for r in csv.DictReader(open(FT / "texts.csv", encoding="utf-8")):
        if r["screen_id"] == sid:
            pages = int(r["pages"]) if r.get("pages") else None
    return p, len(t), sha_file(p), pages


def build():
    summary = json.loads((HERE / "reading_copies_summary.json").read_text(encoding="utf-8"))
    packages = {p["screen_id"]: p for p in load_packages()}
    missing = sorted(set(packages) - set(summary))
    assert not missing, "prepare_si_round.py has not processed: %s" % missing
    lines, manifest = {}, []
    for sid in sorted(packages):
        pkg, s = packages[sid], summary[sid]
        reading = FT / s["reading"]
        assert sha_file(reading) == s["reading_sha256"], "reading copy changed: " + sid
        si_text = reading.read_text(encoding="utf-8")
        mp, m_chars, m_sha, m_pages = main_info(sid)
        ce = pkg["completeness_evidence"]
        false_hits = KNOWN_FALSE_MISSING.get(sid, {})
        real_missing = [k for k in ce["main_referenced_items_missing_from_SI_text"] if k not in false_hits]
        unreadable = [f for f in s["flags"] if f["kind"] in ("no_preview", "preview_blank")]
        si_complete = not real_missing and pkg.get("ready_for_two_blind_reads", False)
        basis = ("exact article-addressed package (Elsevier PII file or Research Square preprint-page file list) retrieved and hash-pinned; every SI item the main text names is present in the SI text "
                 "(%d referenced, %d missing%s); SI text extracted without error; figures/images are in contact sheets and previews, not in the text"
                 % (len(ce["main_text_SI_items_referenced"]), len(real_missing),
                    ("; %d regex false hit(s) set aside: %s" % (len(false_hits), "; ".join("%s (%s)" % kv for kv in false_hits.items()))) if false_hits else ""))
        kinds = {f["kind"] for f in s["flags"]}
        pdf_only = all(m["kind"] == "pdf" for m in s["files"])
        word_media = sum(m.get("media_items", 0) for m in s["files"] if m["kind"] == "docx") or None
        doc_media = sum(m.get("carved_images", 0) for m in s["files"] if m["kind"] == "doc") or None
        limitations = "; ".join(s["limitations"] + ([PACKAGE_NOTE[sid]] if sid in PACKAGE_NOTE else []))
        limitations = limitations.replace("; 1 embedded media items are images", "; 1 embedded media item is an image")
        visual = []
        for f in s["flags"]:
            if f["kind"] == "no_preview" and sid == "S27476":  # checked by hand: both SVG pictures carry a PNG fallback (image19.png, image20.png) with its own preview
                f = dict(f, why="two SVG members have no raster preview; the same two pictures also carry PNG fallbacks (image19.png, image20.png) that are previewed")
            visual.append(f)
        if sid == "S23308":
            visual.append({"kind": "table_only_as_image", "visual": ["si_read_round_2026-10-04/files/S23308/docx_media/image1.emf.png"],
                           "why": "the SI's single table (ZPE and TS corrections) exists only as an EMF image; no title/authors inside, identity rests on the PII file name"})
        line = {"screen_id": sid, "doi": pkg["doi"], "text": "text/%s.txt" % sid, "si_text": s["reading"], "chars": m_chars, "si_chars": len(si_text),
                "si_complete": si_complete, "si_files": s["si_files"], "facts": facts_for(sid),
                "visual_root": "si_read_round_2026-10-04/files/%s" % sid, "main_pages": m_pages,
                "si_pages": sum(m.get("pages", 0) for m in s["files"] if m["kind"] == "pdf") or None,
                "word_media": word_media, "doc_media": doc_media,
                "word_extras": ("si_read_round_2026-10-04/files/%s/word_extras.json" % sid) if "word_embedded_images" in kinds else None,
                "visual_review": visual, "limitations": limitations}
        group = "pdf" if pdf_only else "word"
        lines[sid] = (group, line)
        manifest.append({"screen_id": sid, "doi": pkg["doi"], "title": pkg["title_checklist"], "source_route": pkg["source_route"],
                         "recovery_manifest": pkg["_manifest"], "format_group": group,
                         "source_files": s["files"], "reading_copy": {"path": s["reading"], "sha256": s["reading_sha256"], "chars": len(si_text)},
                         "main_text": {"path": "text/%s.txt" % sid, "sha256": m_sha, "chars": m_chars, "pages": m_pages},
                         "si_complete": si_complete, "si_complete_basis": basis, "completeness_false_hits_set_aside": false_hits,
                         "identity_basis": IDENTITY_NOTE.get(sid, "title and Crossref author surnames in the SI text; exact article addressing (PII file or preprint-page file list)"),
                         "identity_evidence": pkg["identity_evidence"], "visual_review": visual, "limitations": limitations,
                         "facts": line["facts"], "recovery_caveats": pkg.get("caveats", "")})
    # batches: group by SI format, ft_screen.py budget rules, fixed order (screen_id); identical for both passes
    plan_batches = {}
    for group in ("pdf", "word"):
        todo = [lines[s][1] for s in sorted(lines) if lines[s][0] == group]
        batch, size, k = [], 0, 0
        chunks = []
        for x in todo:
            c = x["chars"] + x["si_chars"]
            if batch and (size + c > BUDGET or len(batch) >= MAX_PER_BATCH):
                chunks.append((batch, size))
                batch, size = [], 0
            batch.append(x)
            size += c
        if batch:
            chunks.append((batch, size))
        for k, (b, size) in enumerate(chunks, 1):
            plan_batches["%s_%02d" % (group, k)] = (b, size)
    out = {}
    for n in ("1", "2"):
        d = HERE / ("pass_" + n) / "batches"
        d.mkdir(parents=True, exist_ok=True)
        plan = {"batches": {}}
        for key, (b, size) in plan_batches.items():
            name = "SI%s_%s" % (n, key)
            p = d / (name + ".in.jsonl")
            data = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in b).encode("utf-8")
            if p.exists() and p.read_bytes() != data:
                raise ValueError("Refusing differing pass input: " + str(p))
            p.write_bytes(data)
            plan["batches"][name] = {"records": [x["screen_id"] for x in b], "chars": size, "sha256": hashlib.sha256(data).hexdigest()}
        plan.update(pass_=n, budget_chars=BUDGET, max_per_batch=MAX_PER_BATCH, instructions_version="v5", instructions_sha256=INSTR_SHA,
                    grouping="by SI format (pdf: all SI files PDF; word: Word/binary-Word SI, with its videos), then ft_screen.py batching in screen_id order",
                    content_identical_across_passes=True, brief="SI_READ_BRIEF.md (root)")
        (HERE / ("pass_" + n) / "plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding="utf-8")
        out[n] = plan
    for m in manifest:
        for n in ("1", "2"):
            m["batch_pass_" + n] = next(k for k, v in out[n]["batches"].items() if m["screen_id"] in v["records"])
    (HERE / "intake_manifest.json").write_text(json.dumps(
        {"round": "si_read_round_2026-10-04", "created_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "instructions": {"file": "eligibility_instructions.md", "version": "v5", "sha256": INSTR_SHA},
         "not_sent_to_reads": {"S11392": "Frank, in session, 2026-10-04: linkage only; not sent to the reads (see decisions_2026-10-04.md)",
                               "S22941": "no SI recovered (public_si_recovery_2026-10-04_ext/readout.md)"},
         "packages": manifest}, indent=1, ensure_ascii=False), encoding="utf-8")
    for n in ("1", "2"):
        print("pass", n, {k: (v["records"], v["chars"]) for k, v in out[n]["batches"].items()})


if __name__ == "__main__":
    build()
