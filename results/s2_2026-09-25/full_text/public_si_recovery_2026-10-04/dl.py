"""Download one candidate file into files/ and log the attempt.

  python dl.py SID DOI ROUTE URL LOCAL_NAME [outcome_if_ok] [note]
Failures are logged to search_log.jsonl (not-found/gated); a successful download is recorded in downloads.jsonl and
the final outcome row (recovered/main-only/wrong-version) is logged after identity/completeness checks.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

sid, doi, route, url, name = sys.argv[1:6]
ok_outcome = sys.argv[6] if len(sys.argv) > 6 else "main-only"
note = sys.argv[7] if len(sys.argv) > 7 else ""
dest = L.FILES / name
r = L.download(url, dest)
if r.get("error") or r["status"] != 200:
    L.log(sid, doi, route, url, r["status"], "gated" if r.get("gated") else "not-found",
          "download failed: %s" % (r.get("error") or ("HTTP %s" % r["status"])))
    print("FAILED", r["status"], r.get("error"))
else:
    rec = {"screen_id": sid, "doi": doi, "route": route, "url": url, "at_utc": L.now(), "http_status": r["status"],
           "bytes": r["bytes"], "sha256": r["sha256"], "kind": r["kind"], "ctype": r.get("ctype"),
           "local_path": str(dest.relative_to(L.FT)).replace("\\", "/"), "note": note}
    with open(L.PHASE / "downloads.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("OK", r["bytes"], r["kind"], r["sha256"], dest)
