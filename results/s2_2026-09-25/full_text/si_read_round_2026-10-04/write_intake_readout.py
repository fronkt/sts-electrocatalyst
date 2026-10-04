"""Assemble intake_readout.md from intake_manifest.json, pass plans, the reading-copy summary and the corpus state csv."""
import csv
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
FT = HERE.parent
man = json.loads((HERE / "intake_manifest.json").read_text(encoding="utf-8"))
pk = man["packages"]
plans = {n: json.loads((HERE / ("pass_" + n) / "plan.json").read_text(encoding="utf-8")) for n in ("1", "2")}
state = {r["screen_id"]: r for r in csv.DictReader(open(FT / "reconcile" / "current_state.csv", encoding="utf-8"))}
line = {}
for n, plan in plans.items():
    for b in plan["batches"]:
        for r in (json.loads(l) for l in (HERE / ("pass_" + n) / "batches" / (b + ".in.jsonl")).read_text(encoding="utf-8").splitlines()):
            if n == "1":
                line[r["screen_id"]] = r


def fmt_of(p):
    kinds = [f["kind"] for f in p["source_files"]]
    if kinds == ["pdf"]:
        return "PDF"
    if "doc" in kinds:
        return "binary .doc"
    return "Word" + (" + 3 videos" if "video" in kinds else "") + (" (2 files)" if kinds.count("docx") + sum(1 for f in p["source_files"] if f.get("duplicate_of")) > 1 else "")


def visual_short(p):
    out = []
    for v in p["visual_review"]:
        k = v["kind"]
        if k == "word_embedded_images":
            out.append("%d embedded image(s)" % v["count"])
        elif k == "pdf_figure_or_image_pages":
            out.append("%d of %d pages with images/drawings" % (v["count"], p["source_files"][0]["pages"]))
        elif k == "word_embedded_objects":
            out.append("%d equation objects (formulas only as images)" % v["count"])
        elif k == "doc_embedded_images":
            out.append("%d carved image" % v["count"])
        elif k == "table_only_as_image":
            out.append("TABLE ONLY AS IMAGE")
        elif k == "video":
            out.append("video")
        elif k == "no_preview":
            out.append("2 SVG without preview (PNG fallbacks previewed)")
    # collapse the three video flags
    vids = out.count("video")
    out = [x for x in out if x != "video"] + (["%d videos not viewed" % vids] if vids else [])
    return "; ".join(out)


tot_main = sum(p["main_text"]["chars"] for p in pk)
tot_si = sum(p["reading_copy"]["chars"] for p in pk)
o = []
o.append("# SI-read intake, 2026-10-04\n")
o.append("Inputs for two independent blind reads (pass 1 and pass 2) of the recovered SI packages. No read was run, no verdict or eligibility decision is made here.\n")
o.append("## 1. Packages included\n")
o.append("**%d packages**: the 13 packages of `public_si_recovery_2026-10-04/` other than S11392, plus the 9 recovered in `public_si_recovery_2026-10-04_ext/`. Main text: the corpus file `text/<SID>.txt` of each record. SI text: `si_read_round_2026-10-04/files/<SID>/<SID>_si_reading.txt` (%s main characters, %s SI-reading characters in all)." % (
    len(pk), format(tot_main, ","), format(tot_si, ",")))
o.append("Not included: **S11392** (Frank, 2026-10-04: linkage only, not sent to the reads; `decisions_2026-10-04.md`) and **S22941** (no SI recovered).")
o.append("Instructions: `eligibility_instructions.md` (v5, sha256 `%s`, unchanged since the 2026-09-28 SI round); brief: `SI_READ_BRIEF.md`.\n" % man["instructions"]["sha256"])
o.append("| id | SI format | main chars | SI chars | si_complete | batch | visual-review flags | state before (v5_final / lane) |")
o.append("|---|---|---|---|---|---|---|---|")
for p in pk:
    sid = p["screen_id"]
    s = state[sid]
    o.append("| %s | %s | %s | %s | %s | %s | %s | %s / %s |" % (
        sid, fmt_of(p), format(p["main_text"]["chars"], ","), format(p["reading_copy"]["chars"], ","), str(p["si_complete"]).lower(),
        p["batch_pass_1"].replace("SI1_", ""), visual_short(p), s["v5_final"], s["lane"]))
o.append("")
o.append("`si_complete` is true for all %d: each package is the exact article-addressed file set (hash-pinned to the recovery manifests), every SI item the main text names is present in the SI text (the one script hit, S30334 'Section S6', is a regex false hit on 'Sections 6.6.1 and 6.6.2'), and the SI text was extracted without error. It does not mean the images are in the text: figures, and for S23308 the only table, are images (section 3). The basis per package is in `intake_manifest.json` (`si_complete_basis`)." % len(pk))
o.append("")
o.append("## 2. Pass inputs and batches\n")
o.append("Layout mirrors `si_read/pass_<N>/batches/<batch>.in.jsonl` under this directory: `si_read_round_2026-10-04/pass_<N>/batches/<batch>.in.jsonl` and `pass_<N>/plan.json`. Batching follows `ft_screen.py` (480,000 characters of main plus SI text, at most 10 papers per batch) after grouping by SI format as in 2026-10-03 (`pdf_*`, `word_*`); records in screen_id order. **Pass 1 and pass 2 files are byte-identical in content** (verified by `verify_intake.py`), in separate files: only the batch name differs (`SI1_...` versus `SI2_...`).\n")
o.append("| batch (pass 1 / pass 2) | records | characters |")
o.append("|---|---|---|")
for b, v in plans["1"]["batches"].items():
    o.append("| `%s` / `%s` | %s | %s |" % (b, b.replace("SI1_", "SI2_"), ", ".join(v["records"]), format(v["chars"], ",")))
o.append("")
o.append("Line schema (SI_READ_BRIEF.md step 2 fields first): `screen_id`, `doi`, `text`, `si_text`, `chars`, `si_chars`, `si_complete`, `si_files`, `facts`; then, as in the 2026-10-03 inputs, `visual_root`, `main_pages`, `si_pages` (PDF only), `word_media`, `doc_media`, `word_extras`, plus `visual_review` (list of flags with the contact-sheet paths) and `limitations`. `facts` are the identity facts of `reconcile/identity_check.csv` marked supplied_to_reads = yes (same rule as `si_read.py`): S21070, S27476 and S30575 carry one each; S30334's identity check is not marked for the reads and is not supplied.\n")
o.append("## 3. Visual-review flags\n")
o.append("Markers in the SI text: `[SI file <tag>: <local name> (published as <name>)]` per file; PDFs `[<tag> p. N]`; Word and binary Word have no pages, so locations use `[<tag> paragraph N]` (N counts every paragraph of the part, as in 2026-10-02/03) or, for the binary .doc, `[<tag> block N]`. Word page layout is not rendered (as before). Per package, `files/<SID>/` holds the page images or media previews and 6-up contact sheets (`contacts/`), `visual_index.json` (every image with the paragraph it sits at and a nearest-caption candidate; a mechanical reading aid) and, for Word, `word_extras.json`.\n")
o.append("- **S23308, table only as an image.** The SI's only content ('Table 1 - ZPE and TS corrections') is one EMF image; the text has just the caption. No title or authors inside, so **identity rests on the PII-addressed file name** (exact article PII in the download URL). Rendered preview: `files/S23308/docx_media/image1.emf.png`. A reader without image access cannot read the table.")
o.append("- **S31137, formulas only as images.** 53 MathType equation objects (the OER-step and free-energy equations) appear in the text as empty paragraphs with an image marker; their content is in the WMF previews (rendered with GDI+ because Pillow garbles these metafiles). All 78 media items (53 equation previews, 25 PNG figures) are in document order on `files/S31137/contacts/word_01.png` to `word_11.png` (6 per sheet), except 12 wide equation strips that are on `word_wide_01.png` and `word_wide_02.png`; `visual_index.json` gives each item's paragraph.")
o.append("- **S00882, one figure outside the text.** Binary .doc read with antiword (text and tables complete, block markers numbered for location only); its single embedded image (the 'Fig. SI' Pourbaix diagram) was carved by PNG signature: `files/S00882/contacts/doc_01.png`.")
o.append("- **S30575, videos.** Movies S1-S3 (5 s each) are part of the package; inventory only (`files/S30575/video_inventory/`), not viewed.")
o.append("- **S27476, two SVG members** have no raster preview; the same two pictures carry PNG fallbacks that are previewed.")
o.append("- **S22127, duplicate file.** mmc2.docx has the same paragraph text and media as mmc1.docx (differs in Word markup only; verified by `prepare_si_round.py`); its text is not repeated in the reading copy.")
o.append("- **S31125, identity.** The SI's own title differs from the published title; identity rests on the exact PII file, the same four authors and the same sample names (`intake_manifest.json`).")
o.append("- **All other Word packages and all PDFs:** figures (plots, spectra, micrographs, structure images) are images; the text holds captions and printed labels, not plotted values (brief step 3). PDF pages with images, vector drawings or little text are listed per package in `visual_review`.")
o.append("- Word-stored page counts are not reliable (S21253 reports 1 page for 29 figures); they are given only as recovery metadata.\n")
o.append("## 4. Method (reused from 2026-10-03 and 2026-09-28; refinements listed)\n")
o.append("PDFs: PyMuPDF page text in native order, 1.5x page images, 6-up contact sheets (`prepare_sources.pdf_read` / `contacts`). Word: paragraph-by-paragraph accepted-revision text with embedded-image markers, original media plus previews, OMML / revision / embedded-object inventory (`word_extras.json`), and the Pandoc accepted-revision view appended as a 'structured equation/table reading aid' where a file has tables, equations or objects (`inspect_word_extras.py`). Refinements: text-box paragraphs read once (S23135 has 17 text-box pairs), `w:sym` symbols (Greek letters, arrows) and no-break hyphens kept, tabs and manual line breaks kept, transparent images flattened on white (2026-10-03 noted black backgrounds), WMF/EMF rendered with GDI+ via `render_metafile.ps1` (the same local-PowerShell approach as `decode_wdp.ps1`). Binary .doc: antiword text, which `si_read.py` had marked 'not extracted'. Scripts: `prepare_si_round.py`, `build_inputs.py`, `verify_intake.py`, `render_metafile.ps1`, `write_intake_readout.py`.\n")
o.append("## 5. What affects running the reads\n")
o.append("No blocker. Points for the reader prompts:")
o.append("1. **Visual folders.** SI_READ_BRIEF.md step 10 forbids opening `files/` and `files_si/` (the corpus-root folders). The visual material for this round is under `si_read_round_2026-10-04/files/<SID>/` (`visual_root`); readers need an explicit instruction to open it (the 2026-10-03 inputs carry the same `visual_root` field for this purpose). Without image access the flagged items (S23308 table, S31137 equations, S00882 figure, all figure-borne values) are unreadable and `si_complete` does not cover them.")
big = max(plans["1"]["batches"].items(), key=lambda kv: kv[1]["chars"])
s21177 = next(p for p in pk if p["screen_id"] == "S21177")["reading_copy"]["chars"]
o.append("2. **Reading load.** Word reading copies contain the Pandoc aid as a second copy of the text for files with tables or equations (S21177: %s characters of SI reading text; the biggest batch is `%s` at %s of 480,000 characters)." % (format(s21177, ","), big[0].replace("SI1_", ""), format(big[1]["chars"], ",")))
o.append("3. **Earlier reads without SI.** S21070, S27476 and S30575 were read in the 2026-09-28 SI round on their main text alone (they carry reconciliation facts; `si_read/queue.csv`); S30575 stands at AGREED_ELIGIBLE with v5_final NEEDS_SI. These reads add the SI.")
o.append("4. **Dates and identities** are not part of this intake (existing reconciliation: `reconcile/date_check.csv`, `identity_check.csv`).\n")
o.append("## 6. Files\n")
o.append("In `results/s2_2026-09-25/full_text/si_read_round_2026-10-04/`: `decisions_2026-10-04.md`, `intake_readout.md`, `intake_manifest.json` (per package: source pins, reading-copy pin, si_complete basis, identity basis, visual flags, batch names), `reading_copies_summary.json`, `pass_1/` and `pass_2/` (`batches/*.in.jsonl`, `plan.json`), `files/<SID>/` (reading copies, previews, contact sheets, indexes; local only, ignored by git through the `results/` rule), and the scripts. Source binaries stay in the two recovery directories; nothing was copied out of them. No existing file was changed.")
(HERE / "intake_readout.md").write_text("\n".join(o) + "\n", encoding="utf-8")
print("intake_readout.md written", sum(len(x) for x in o))
