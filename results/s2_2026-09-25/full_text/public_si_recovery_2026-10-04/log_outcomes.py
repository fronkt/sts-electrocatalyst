"""Log the final outcome row for downloaded candidates (idempotent: each local file is logged once).

Outcome judgements are entered in OUTCOMES below after inspecting the file (page count / SI-caption census /
comparison with the exact record's local main copy).  Nothing here reads the science or decides eligibility.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

OUTCOMES = {
    "S05155_osti_1419931.pdf": ("main-only", "OSTI accepted manuscript, 12 pages, 3106989 bytes = byte size of the local main copy S05155.pdf; no SI section, Fig. S16/S17 absent."),
    "S05155_dtu_orbit_163016703.pdf": ("main-only", "DTU Orbit copy of the accepted manuscript, 13 pages (rights page + 12 main pages); no SI section."),
    "S05155_spiral_8030a318.pdf": ("main-only", "Imperial Spiral accepted manuscript, 14 pages incl. RSC acceptance cover; no SI section."),
    "S00759_radboud_111409.pdf": ("main-only", "Radboud repository copy, 6 pages = the article itself (J. Phys. Chem. C 2013); no SI."),
    "S00759_groningen_6793665.pdf": ("main-only", "Groningen Pure copy, 6 pages = the article itself; no SI."),
    "S08806_epfl_paper.pdf": ("main-only", "EPFL Infoscience author manuscript, 27 pages double-spaced = main text, references and TOC graphic only; no SI."),
    "S05043_osti_1425009.pdf": ("main-only", "OSTI accepted manuscript, 31 pages: main text and references; it mentions Fig. S1 and Tables S1-S4 but contains no SI pages."),
    "S26740_psi_dora_78821.pdf": ("main-only", "PSI DORA submitted/accepted manuscript, 23 pages: main text, references and TOC graphic; refers to Figure S1-S23 but contains no SI pages."),
    "S08766_nlr_75286.pdf": ("main-only", "NLR (ex-NREL) copy of the 10-page JES article F1243-F1252; no SI."),
    "S08766_osti_1580496.pdf": ("main-only", "OSTI copy, byte-identical to the NLR 10-page JES article; no SI."),
}
# files judged complete SI of the exact record (auto-note from verify_si.py evidence); value = extra caveat or ""
RECOVERED = {
    "S23135_mmc1.docx": "",
    "S31137_mmc1.docx": "",
    "S00358_mmc1.pdf": "main text names no specific SI item, so completeness rests on the exact PII-addressed file and the SI's own title page; SI text says its Tables 1-3 are 'below' and has 13 pages.",
    "S00887_mmc1.docx": "",
    "S05043_mmc1.docx": "",
    "S11279_mmc1.pdf": "",
    "S20599_mmc1.docx": "",
    "S23308_mmc1.docx": "one-page SI ('Supplementary information / Table 1 - ZPE and TS corrections', table supplied as an EMF image); the document carries no title or authors, so identity rests on the exact PII-addressed file name; main text names no specific SI item.",
    "S27476_mmc1.docx": "",
    "S31037_mmc1.docx": "",
    "S14704_mmc1.docx": "handoff dead end (repository copies main-only); this is a different route (publisher article-asset CDN).",
}
ELS_NOTE = "Elsevier article-asset CDN file addressed by the article's own PII (1-s2.0-<PII>-mmc1), the URL behind the page's 'Appendix A. Supplementary data' link; plain GET, no key/login; mmc2+ tried (all extensions) and absent. "


def verify_note(sid, name):
    stem = pathlib.Path(name).stem[:40]
    vp = L.META / ("%s_verify_%s.json" % (sid, stem))
    v = json.loads(vp.read_text(encoding="utf-8"))
    f = v["files"][0]
    i = v["identity"]
    return ("%s pages; title in SI text=%s; authors found %d/%d; main-text SI items referenced=%d, missing from SI=%d; SI caption labels=%d. "
            % (f.get("pages"), i["title_full_in_si_text"], len(i["author_surnames_found"]), len(i["author_surnames_checked"]),
               len(v["main_text_SI_items_referenced"]), len(v["main_referenced_items_missing_from_si_text"]), len(v["si_caption_labels_found"])))


for name, extra in RECOVERED.items():
    sid = name.split("_")[0]
    OUTCOMES[name] = ("recovered", ELS_NOTE + verify_note(sid, name) + extra)

done_p = L.PHASE / "outcomes_logged.json"
done = set(json.loads(done_p.read_text(encoding="utf-8"))) if done_p.exists() else set()
dl = {}
for line in open(L.PHASE / "downloads.jsonl", encoding="utf-8"):
    d = json.loads(line)
    dl[pathlib.Path(d["local_path"]).name] = d
for name, (outcome, note) in OUTCOMES.items():
    if name in done or name not in dl:
        continue
    d = dl[name]
    L.log(d["screen_id"], d["doi"], d["route"], d["url"], d["http_status"], outcome,
          "%s sha256=%s" % (note, d["sha256"]), local_path=d["local_path"], sha256=d["sha256"], bytes=d["bytes"],
          fetched_at_utc=d["at_utc"])
    done.add(name)
done_p.write_text(json.dumps(sorted(done), indent=1), encoding="utf-8")
print("logged", len(done), "outcomes total")
