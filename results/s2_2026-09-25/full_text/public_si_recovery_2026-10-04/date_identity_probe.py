"""Cheap date/identity evidence (public Crossref/OpenAlex only; reported, not decided).
  1. Elsevier items already flagged SOURCES_STRADDLE_BOUNDARY (S31137, S31037): Crossref created/deposited/issued/online dates.
  2. Angewandte dual-edition DOIs: for each target whose DOI is an 'ange.' (German edition) or 'anie.' (International Edition)
     DOI, fetch the counterpart edition's Crossref record and compare title and authors."""
import json
import pathlib
import re
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

T = {t["screen_id"]: t for t in json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))["targets"]}
out = {"dates": {}, "dual_edition": {}}
for sid in ("S31137", "S31037"):
    doi = T[sid]["doi"]
    f = L.jget("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    m = (f["json"] or {}).get("message", {})
    out["dates"][sid] = {k: (m.get(k) or {}).get("date-time") or (m.get(k) or {}).get("date-parts") for k in
                         ("created", "deposited", "indexed", "issued", "published-online", "published-print", "published")}
    out["dates"][sid]["license_starts"] = sorted({(x.get("start") or {}).get("date-time") for x in m.get("license", [])})
    L.log(sid, doi, "crossref_works_dates", f["url_logged"], f["status"], "not-found",
          "date evidence only (existing date_check flag SOURCES_STRADDLE_BOUNDARY): %s" % json.dumps(out["dates"][sid], default=str)[:500])
    f = L.jget("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi), secret_param={"api_key": L.openalex_key()})
    w = f["json"] or {}
    out["dates"][sid]["openalex"] = {k: w.get(k) for k in ("publication_date", "created_date", "updated_date")}
    L.log(sid, doi, "openalex_work_dates", f["url_logged"], f["status"], "not-found",
          "OpenAlex dates: %s" % json.dumps(out["dates"][sid]["openalex"]))
for sid, t in T.items():
    doi = t["doi"]
    mm = re.match(r"10\.1002/(ange|anie)\.(.+)$", doi)
    if not mm:
        continue
    other = "10.1002/%s.%s" % ("anie" if mm.group(1) == "ange" else "ange", mm.group(2))
    a = L.jget("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    b = L.jget("https://api.crossref.org/works/" + urllib.parse.quote(other))
    ma, mb = (a["json"] or {}).get("message", {}), (b["json"] or {}).get("message", {})
    ra = {"title": (ma.get("title") or [""])[0], "authors": [x.get("family") for x in ma.get("author", [])], "pages": ma.get("page"),
          "container": (ma.get("container-title") or [""])[0], "issued": ma.get("issued", {}).get("date-parts")}
    rb = {"status": b["status"], "title": (mb.get("title") or [""])[0], "authors": [x.get("family") for x in mb.get("author", [])],
          "pages": mb.get("page"), "container": (mb.get("container-title") or [""])[0], "issued": mb.get("issued", {}).get("date-parts"),
          "relation": mb.get("relation")}
    same = bool(rb["title"]) and ra["authors"] == rb["authors"]
    out["dual_edition"][sid] = {"record_doi": doi, "counterpart_doi": other, "record": ra, "counterpart": rb, "same_authors_list": same,
                                "same_title_lowercase": ra["title"].lower() == rb["title"].lower()}
    L.log(sid, doi, "crossref_counterpart_edition", b["url_logged"], b["status"], "not-found",
          "identity evidence: counterpart-edition DOI %s %s; same author list=%s; same title=%s; record container '%s', counterpart '%s'" %
          (other, "resolves in Crossref" if b["status"] == 200 else "not in Crossref", same, ra["title"].lower() == rb["title"].lower(),
           ra["container"], rb["container"]))
L.save_meta("date_identity_probe.json", out)
print(json.dumps(out, indent=1, ensure_ascii=False, default=str)[:5000])
