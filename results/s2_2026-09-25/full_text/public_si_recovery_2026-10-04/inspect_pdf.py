"""Quick structural look at a candidate PDF: page count, pages whose text mentions Supporting/Supplementary, S-label census.

  python inspect_pdf.py PATH [SID]
Prints per-page first line for the last pages and every page that starts an SI-like section.
"""
import pathlib
import re
import sys

import fitz

path = pathlib.Path(sys.argv[1])
doc = fitz.open(path)
print(path.name, "pages", len(doc))
sec = re.compile(r"supporting information|supplementary (?:information|material|data|figures)|electronic supplementary", re.I)
lab = re.compile(r"\b(?:Fig(?:ure)?s?\.?|Tables?)\s*S\s?(\d{1,3})", re.I)
labels = set()
for i, pg in enumerate(doc):
    t = pg.get_text()
    for m in lab.finditer(t):
        labels.add(m.group(0).replace("  ", " "))
    hits = sec.findall(t)
    first = " ".join(t.strip().split())[:90]
    flag = "SECTION" if hits else ""
    if hits or i >= len(doc) - 6 or i < 2:
        print("  p%02d %-8s %s" % (i + 1, flag, first))
print("S-labels mentioned:", len(labels), sorted(labels)[:15])
