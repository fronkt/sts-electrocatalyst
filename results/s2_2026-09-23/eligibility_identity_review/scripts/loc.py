"""Locator helper: print PDF page (1-based, from pdftotext form feeds) and context for regex hits.

usage: python loc.py TEXTFILE REGEX [context_chars]
"""
import re
import sys

path, pat = sys.argv[1], sys.argv[2]
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 200
t = open(path, encoding="utf-8", errors="replace").read()
for m in re.finditer(pat, t, flags=re.I):
    page = t.count("\f", 0, m.start()) + 1
    s = re.sub(r"\s+", " ", t[max(0, m.start() - ctx): m.end() + ctx])
    print(f"[p{page}] {s}\n")
