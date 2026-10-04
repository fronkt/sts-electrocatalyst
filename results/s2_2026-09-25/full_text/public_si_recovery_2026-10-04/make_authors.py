"""Cache Crossref author lists for recovered records that have no sweep file (S11392 from the linkage file, S14704 by one
Crossref call), so verify_si.py can check author surnames."""
import json
import pathlib
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

lk = json.loads((L.META / "S11392_S13010_linkage.json").read_text(encoding="utf-8"))
(L.META / "S11392_authors.json").write_text(json.dumps(lk["preprint_crossref"]["authors"], ensure_ascii=False), encoding="utf-8")
doi = "10.1016/j.jcat.2022.02.016"
f = L.jget("https://api.crossref.org/works/" + urllib.parse.quote(doi))
m = (f["json"] or {}).get("message", {})
auth = [(a.get("family"), a.get("given")) for a in m.get("author", [])]
(L.META / "S14704_authors.json").write_text(json.dumps(auth, ensure_ascii=False), encoding="utf-8")
L.log("S14704", doi, "crossref_works_authors", f["url_logged"], f["status"], "not-found", "Crossref author list cached for the SI identity check: %d authors" % len(auth))
print(len(lk["preprint_crossref"]["authors"]), len(auth))
