"""Additional public repository routes for every target: Zenodo exact-title, figshare exact-title (the earlier phases
only queried figshare by DOI), NOMAD archive entries that cite the article DOI.  No downloads; hits are leads."""
import json
import pathlib
import re
import sys

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

T = json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))
SKIP = {"S21177", "S30575"}


def norm(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


out = {}
for rec in T["targets"]:
    sid, doi = rec["screen_id"], rec["doi"]
    if sid in SKIP:
        continue
    title = re.sub(r"<[^>]+>", "", rec["title"]).replace('"', "")
    res = {}
    f = L.jget("https://zenodo.org/api/records", params={"q": 'title:"%s"' % title[:180], "size": 5})
    hh = ((f["json"] or {}).get("hits") or {}).get("hits", [])
    ex = [h for h in hh if norm((h.get("metadata") or {}).get("title")) == norm(title)]
    res["zenodo_title"] = [(h.get("id"), h.get("doi"), (h.get("metadata") or {}).get("title")) for h in ex]
    L.log(sid, doi, "zenodo_title_query", f["url_logged"], f["status"], "not-found",
          "exact-title Zenodo records: %s" % (res["zenodo_title"] or "none") if f["status"] == 200 else "Zenodo query failed: %s" % (f.get("error") or f["status"]))
    # figshare title search (POST JSON API)
    try:
        r = requests.post("https://api.figshare.com/v2/articles/search", json={"search_for": ':title: "%s"' % title[:180], "page_size": 5},
                          headers={"User-Agent": L.UA}, timeout=40)
        arts = r.json() if r.status_code == 200 else []
        ex = [a for a in arts if norm(a.get("title")) == norm(title)]
        res["figshare_title"] = [(a.get("id"), a.get("doi"), a.get("title")) for a in ex]
        L.log(sid, doi, "figshare_title_search", "https://api.figshare.com/v2/articles/search", r.status_code, "not-found",
              "exact-title figshare items: %s" % (res["figshare_title"] or "none"))
    except Exception as e:
        L.log(sid, doi, "figshare_title_search", "https://api.figshare.com/v2/articles/search", None, "not-found", "request error %s" % type(e).__name__)
    # NOMAD entries referencing the DOI
    try:
        r = requests.post("https://nomad-lab.eu/prod/v1/api/v1/entries/query",
                          json={"query": {"references:any": ["https://doi.org/" + doi, "doi:" + doi, doi]}, "pagination": {"page_size": 3},
                                "required": {"include": ["entry_id", "upload_id", "mainfile", "references"]}},
                          headers={"User-Agent": L.UA}, timeout=60)
        j = r.json() if r.status_code == 200 else {}
        n = ((j.get("pagination") or {}).get("total"))
        res["nomad_total"] = n
        L.log(sid, doi, "nomad_entries_references", "https://nomad-lab.eu/prod/v1/api/v1/entries/query", r.status_code, "not-found",
              "NOMAD entries referencing the DOI: %s" % n)
    except Exception as e:
        L.log(sid, doi, "nomad_entries_references", "https://nomad-lab.eu/prod/v1/api/v1/entries/query", None, "not-found", "request error %s" % type(e).__name__)
    out[sid] = res
    print(sid, json.dumps(res, ensure_ascii=False)[:300], flush=True)
L.save_meta("extra_repos.json", out)
