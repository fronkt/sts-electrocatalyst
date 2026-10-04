"""Run verify_si.py for several (SID, file) pairs and print a compact summary line each.

  python verify_summary.py S23135:files/S23135_mmc1.docx S00358:files/S00358_mmc1.pdf ...
"""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
for arg in sys.argv[1:]:
    sid, path = arg.split(":", 1)
    p = subprocess.run([sys.executable, str(HERE / "verify_si.py"), sid, path], capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        print(sid, path, "VERIFY ERROR", p.stderr[-300:])
        continue
    d = json.loads(p.stdout)
    f = d["files"][0]
    ident = d["identity"]
    print("%s %s | pages=%s chars=%s | title_full=%s title8=%s doi=%s authors %d/%d | main-refs=%d missing=%s | captions=%d | extra=%s" % (
        sid, pathlib.Path(path).name, f.get("pages"), f.get("text_chars"), ident["title_full_in_si_text"],
        ident["title_first8_words_in_si_text"], ident["doi_in_si_text"], len(ident["author_surnames_found"]),
        len(ident["author_surnames_checked"]), len(d["main_text_SI_items_referenced"]),
        d["main_referenced_items_missing_from_si_text"], len(d["si_caption_labels_found"]),
        {k: v for k, v in f.items() if k.startswith(("docx_", "pdf_"))}))
