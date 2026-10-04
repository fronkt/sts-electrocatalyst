"""Europe PMC supplementaryFiles for a PMCID (public OA REST route used by earlier phases), plus PMC OA service listing.

  python epmc_supp.py SID DOI PMCID
Downloads the package (zip) into files/ if one is served; logs both attempts.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

sid, doi, pmcid = sys.argv[1:4]
url = "https://www.ebi.ac.uk/europepmc/webservices/rest/%s/supplementaryFiles" % pmcid
dest = L.FILES / ("%s_%s_epmc_supp.zip" % (sid, pmcid))
r = L.download(url, dest, spacing=2.0)
if r.get("error") or r["status"] != 200 or r.get("kind") not in ("zip/ooxml", "pdf"):
    body = ""
    if dest.exists() and dest.stat().st_size < 4000:
        body = dest.read_text(encoding="utf-8", errors="ignore")[:200]
        dest.unlink()
    L.log(sid, doi, "europepmc_supplementaryFiles", url, r.get("status"), "not-found",
          "no supplementary package served (status=%s kind=%s err=%s %s)" % (r.get("status"), r.get("kind"), r.get("error"), body))
    print("no package", r.get("status"), r.get("kind"), body)
else:
    rec = {"screen_id": sid, "doi": doi, "route": "europepmc_supplementaryFiles", "url": url, "at_utc": L.now(),
           "http_status": r["status"], "bytes": r["bytes"], "sha256": r["sha256"], "kind": r["kind"],
           "local_path": str(dest.relative_to(L.FT)).replace("\\", "/")}
    with open(L.PHASE / "downloads.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    import zipfile
    names = zipfile.ZipFile(dest).namelist() if r["kind"] == "zip/ooxml" else []
    print("package", r["bytes"], r["sha256"], names)
