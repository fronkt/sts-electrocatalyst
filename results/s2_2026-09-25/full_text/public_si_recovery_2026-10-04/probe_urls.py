"""Fetch candidate URLs (repository copies, landing pages) and report what each is. Retrieval only.

  python probe_urls.py probes.json
probes.json = list of {"sid","doi","route","url","name"}.  For each:
  * file kinds (pdf/docx/zip): saved to files/<name>, page count + SI-caption census printed; the final outcome row is
    logged by the caller after inspection (downloads.jsonl records the file)
  * html landing pages: saved to metadata/<name>.html and every file-like link is listed (no recursion)
  * failures / gates: logged immediately (not-found / gated)
"""
import json
import pathlib
import re
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

LINK = re.compile(r'''href=["']([^"']+)["']''', re.I)
FILEISH = re.compile(r"(\.pdf|\.docx?|\.zip|\.xlsx?|bitstream|download|/files/|suppl|\.cif|\.csv|\.txt)(\?|$|#|/)", re.I)
CAP = re.compile(r"(?im)^\s*(?:Supplementary\s+|Supporting\s+)?(?:Fig(?:ure)?\.?|Table)\s*S\s?(\d{1,3})\b")

for p in json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")):
    sid, doi, route, url, name = p["sid"], p["doi"], p["route"], p["url"], p["name"]
    dest = L.FILES / name
    r = L.download(url, dest, max_bytes=250 * 1024 * 1024, spacing=p.get("spacing"))
    if r.get("skipped"):
        L.log(sid, doi, route, url, None, "gated", "skipped: host %s already gated in this phase" % L.host_of(url))
        print(sid, "SKIPPED (gated host)", url)
        continue
    if r.get("error") or r["status"] != 200:
        L.log(sid, doi, route, url, r.get("status"), "gated" if r.get("gated") else "not-found",
              "request failed: %s" % (r.get("error") or ("HTTP %s" % r["status"])))
        print(sid, "FAIL", r.get("status"), r.get("error"), url)
        continue
    kind = r["kind"]
    if kind == "html":
        html = dest.read_text(encoding="utf-8", errors="ignore")
        dest.unlink()
        (L.META / (pathlib.Path(name).stem + ".html")).write_text(html, encoding="utf-8")
        if re.search(r"recaptcha|just a moment|client challenge", html[:6000], re.I):
            L.log(sid, doi, route, url, 200, "gated", "HTTP 200 but challenge page served; not read")
            L.gate_host(L.host_of(url), "challenge page")
            print(sid, "GATED(challenge)", url)
            continue
        links = []
        for h in LINK.findall(html):
            if FILEISH.search(h):
                links.append(urllib.parse.urljoin(url, h))
        links = sorted(set(links))
        print(sid, "HTML", len(html), url)
        for l in links[:40]:
            print("     link:", l)
        continue
    rec = {"screen_id": sid, "doi": doi, "route": route, "url": url, "at_utc": L.now(), "http_status": 200, "bytes": r["bytes"],
           "sha256": r["sha256"], "kind": kind, "ctype": r.get("ctype"), "local_path": str(dest.relative_to(L.FT)).replace("\\", "/")}
    with open(L.PHASE / "downloads.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    info = ""
    if kind == "pdf":
        try:
            import fitz
            doc = fitz.open(dest)
            txt = "\n".join(pg.get_text() for pg in doc)
            caps = sorted({int(m.group(1)) for m in CAP.finditer(txt)})
            info = "pages=%d chars=%d SIcaptions=%d first=%s" % (len(doc), len(txt), len(caps), txt[:100].replace("\n", " "))
        except Exception as e:
            info = "pdf open error %s" % e
    elif kind == "zip/ooxml":
        import zipfile
        try:
            info = "members=%s" % zipfile.ZipFile(dest).namelist()[:20]
        except Exception as e:
            info = "zip error %s" % e
    print(sid, "FILE", kind, r["bytes"], r["sha256"][:12], name, info)
