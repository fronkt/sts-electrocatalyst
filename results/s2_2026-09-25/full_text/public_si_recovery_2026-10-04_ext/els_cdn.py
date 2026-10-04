"""Elsevier supplementary files from the public article-asset CDN (ars.els-cdn.com), the URL pattern the article page's
'Appendix A. Supplementary data' links point to.  Same method as public_si_recovery_2026-10-04/els_cdn.py: plain GET,
honest User-Agent, no key, no login, no api.elsevier.com; the PII comes from Crossref alternative-id (metadata/<SID>_identity.json).
Stops for the whole phase on the first 401/403/429 or challenge page (host recorded in host_gates.json).

  python els_cdn.py S22127,S23544,...            standard extensions pdf, docx, zip, xlsx, doc
  python els_cdn.py S22127,... --extra           additional extensions for exact mmc1 names only (xls, pptx, txt, csv, mp4, docm, rtf)

For each record: mmc1, mmc2, ... each tried with the extensions above.  A 404 (XML 'NoSuchKey') is logged as not-found for
that exact URL; it is NOT evidence that the article has no supplement (other extensions or names exist)."""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

EXTRA = "--extra" in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith("--")]
EXTS = ("xls", "pptx", "txt", "csv", "mp4", "docm", "rtf") if EXTRA else ("pdf", "docx", "zip", "xlsx", "doc")
T = {t["screen_id"]: t for t in json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))["targets"]}
for sid in args[0].split(","):
    rec = T[sid]
    ident = json.loads((L.META / ("%s_identity.json" % sid)).read_text(encoding="utf-8"))
    pii = (ident["crossref"].get("alternative-id") or [None])[0]
    if not pii:
        L.log(sid, rec["doi"], "els_cdn_mmc", "", None, "not-found", "no PII in Crossref alternative-id")
        continue
    got_any = False
    for n in range(1, 8 if not EXTRA else 2):
        got_n = False
        for ext in EXTS:
            if "els-cdn.com" in L.gates():
                break
            url = "https://ars.els-cdn.com/content/image/1-s2.0-%s-mmc%d.%s" % (pii, n, ext)
            name = "%s_mmc%d.%s" % (sid, n, ext)
            r = L.download(url, L.FILES / name, spacing=5.0)
            if r.get("gated") or r.get("skipped"):
                L.log(sid, rec["doi"], "els_cdn_mmc", url, r.get("status"), "gated",
                      "CDN refused/challenged (HTTP %s); els-cdn.com not requested again" % r.get("status"))
                break
            if r.get("error"):
                L.log(sid, rec["doi"], "els_cdn_mmc", url, None, "not-found", "request error %s" % r["error"])
                continue
            if r["status"] == 200 and r.get("kind") != "html" and r["bytes"] > 0:
                got_n = got_any = True
                rec_d = {"screen_id": sid, "doi": rec["doi"], "route": "els_cdn_mmc", "url": url, "at_utc": L.now(),
                         "http_status": 200, "bytes": r["bytes"], "sha256": r["sha256"], "kind": r["kind"],
                         "ctype": r.get("ctype"), "local_path": str((L.FILES / name).relative_to(L.FT)).replace("\\", "/")}
                with open(L.PHASE / "downloads.jsonl", "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec_d, ensure_ascii=False) + "\n")
                L.log(sid, rec["doi"], "els_cdn_mmc", url, 200, "recovered",
                      "CDN file retrieved: %s, %d bytes, sha256 %s" % (name, r["bytes"], r["sha256"]))
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
