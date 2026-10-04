"""Elsevier supplementary files from the public article-asset CDN (ars.els-cdn.com), the same URL the article page's
'Appendix A. Supplementary data' links point to.  Plain GET, no key, no login, no API; PII from Crossref alternative-id.
Stops for the whole phase on the first 401/403/429 or challenge page.

  python els_cdn.py S23135,S31137,...
For each record: mmc1, mmc2, ... each tried with extensions pdf, docx, zip, xlsx, doc.  A 404 (XML 'NoSuchKey') is logged
as not-found for that exact URL; it is NOT evidence that the article has no supplement (other extensions/names exist).
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

EXTS = ("pdf", "docx", "zip", "xlsx", "doc")
_tj = json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))
T = {t["screen_id"]: t for t in _tj["targets"] + _tj["skipped_dead_end"]}
ids = sys.argv[1].split(",")
for sid in ids:
    rec = T[sid]
    swp = L.META / ("%s_sweep.json" % sid)
    if swp.exists():
        pii = (json.loads(swp.read_text(encoding="utf-8"))["crossref"].get("alternative-id") or [None])[0]
    else:
        import urllib.parse
        cf = L.jget("https://api.crossref.org/works/" + urllib.parse.quote(rec["doi"]))
        L.log(sid, rec["doi"], "crossref_works_pii", cf["url_logged"], cf["status"], "not-found", "Crossref lookup for the Elsevier PII only")
        pii = (((cf["json"] or {}).get("message") or {}).get("alternative-id") or [None])[0]
    if not pii:
        L.log(sid, rec["doi"], "els_cdn_mmc", "", None, "not-found", "no PII in Crossref alternative-id")
        continue
    got_any = False
    for n in range(1, 8):
        got_n = False
        for ext in EXTS:
            if "els-cdn.com" in L.gates():
                break
            url = "https://ars.els-cdn.com/content/image/1-s2.0-%s-mmc%d.%s" % (pii, n, ext)
            name = "%s_mmc%d.%s" % (sid, n, ext)
            r = L.download(url, L.FILES / name, spacing=5.0)
            if r.get("gated") or r.get("skipped"):
                L.log(sid, rec["doi"], "els_cdn_mmc", url, r.get("status"), "gated", "CDN refused/challenged (HTTP %s); els-cdn.com not requested again" % r.get("status"))
                break
            if r.get("error"):
                L.log(sid, rec["doi"], "els_cdn_mmc", url, None, "not-found", "request error %s" % r["error"])
                continue
            if r["status"] == 200 and r.get("kind") != "html" and r["bytes"] > 0:
                got_n = got_any = True
                rec_d = {"screen_id": sid, "doi": rec["doi"], "route": "els_cdn_mmc", "url": url, "at_utc": L.now(),
                         "http_status": 200, "bytes": r["bytes"], "sha256": r["sha256"], "kind": r["kind"], "ctype": r.get("ctype"),
                         "local_path": str((L.FILES / name).relative_to(L.FT)).replace("\\", "/")}
                with open(L.PHASE / "downloads.jsonl", "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec_d, ensure_ascii=False) + "\n")
                print(sid, "GOT", name, r["bytes"], r["kind"], flush=True)
                break
            else:
                try:
                    (L.FILES / name).unlink()
                except Exception:
                    pass
                L.log(sid, rec["doi"], "els_cdn_mmc", url, r["status"], "not-found",
                      "CDN URL absent (HTTP %s): this exact name/extension only; not evidence that no supplement exists" % r["status"])
        if "els-cdn.com" in L.gates() or not got_n:
            break
    print(sid, "done; any file:", got_any, flush=True)
