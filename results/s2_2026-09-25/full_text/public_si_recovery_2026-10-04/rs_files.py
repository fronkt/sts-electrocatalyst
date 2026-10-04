"""Research Square preprint page -> file list from the page's embedded __NEXT_DATA__ (plain HTTP GET of the public page).

  python rs_files.py S21177 10.21203/rs.3.rs-3710432/v1 [save]
Prints each file entry (name, type, URL, size, description) found under any 'files'/'supplementary' key.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

sid, doi = sys.argv[1], sys.argv[2]
m = re.match(r"10\.21203/rs\.3\.rs-(\d+)/v(\d+)", doi)
rs, ver = m.group(1), m.group(2)
url = "https://www.researchsquare.com/article/rs-%s/v%s" % (rs, ver)
f = L.fetch(url)
f.pop("resp", None)
print("status", f["status"], "gated", f["gated"], "bytes", len(f["content"]))
if f["status"] != 200:
    L.log(sid, doi, "researchsquare_page_source_http", url, f["status"], "gated" if f["gated"] else "not-found",
          "page source fetch failed: %s" % (f.get("error") or f["status"]))
    sys.exit()
t = f["text"]
(L.META / ("%s_rs_page.html" % sid)).write_text(t, encoding="utf-8")
m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', t, flags=re.S)
data = json.loads(m.group(1)) if m else {}
found = []


def walk(o, path=""):
    if isinstance(o, dict):
        if any(k in o for k in ("url", "fileUrl", "link")) and any(k in o for k in ("name", "filename", "fileName", "title", "label")):
            found.append({k: o[k] for k in o if isinstance(o[k], (str, int, float, bool)) and len(str(o[k])) < 300})
        for k, v in o.items():
            walk(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + "[%d]" % i)


walk(data)
urls = sorted(set(re.findall(r"https?://assets[-a-z]*\.researchsquare\.com/files/[^\"'\s<>\\]+", t)))
print("asset urls:", len(urls))
for u in urls:
    print("  ", u)
print("structured file-like entries:", len(found))
for x in found[:40]:
    print("  ", json.dumps(x, ensure_ascii=False)[:300])
json.dump({"page": url, "asset_urls": urls, "entries": found}, open(L.META / ("%s_rs_files.json" % sid), "w", encoding="utf-8"), indent=1)
