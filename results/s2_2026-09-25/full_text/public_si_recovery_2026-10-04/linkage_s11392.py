"""S11392 (Research Square preprint rs-118932/v1) vs S13010 (JACS 10.1021/jacs.1c01655): pairwise version-linkage evidence.
Public APIs only. Reports the evidence; makes no decision about version collapse or screening."""
import json
import pathlib
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

PRE, JOUR = "10.21203/rs.3.rs-118932/v1", "10.1021/jacs.1c01655"
out = {}
for tag, doi, sid in (("preprint", PRE, "S11392"), ("journal", JOUR, "S13010")):
    f = L.jget("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    m = (f["json"] or {}).get("message", {})
    out[tag + "_crossref"] = {"status": f["status"], "title": m.get("title"), "relation": m.get("relation"),
                              "authors": [(a.get("family"), a.get("given")) for a in m.get("author", [])],
                              "issued": m.get("issued"), "posted": m.get("posted"), "subtype": m.get("subtype"),
                              "update-to": m.get("update-to")}
    L.log(sid, doi, "crossref_works_linkage", f["url_logged"], f["status"], "not-found",
          "linkage check; Crossref relation=%s" % (json.dumps(m.get("relation")) if f["status"] == 200 else f.get("error")))
    f = L.jget("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi), secret_param={"api_key": L.openalex_key()})
    w = f["json"] or {}
    out[tag + "_openalex"] = {"status": f["status"], "id": w.get("id"), "title": w.get("title"),
                              "locations": [{"landing": x.get("landing_page_url"), "pdf": x.get("pdf_url"),
                                             "version": x.get("version"), "source": (x.get("source") or {}).get("display_name")}
                                            for x in w.get("locations", [])],
                              "ids": w.get("ids"), "related_works": (w.get("related_works") or [])[:10],
                              "authors": [(a.get("author") or {}).get("display_name") for a in w.get("authorships", [])]}
    L.log(sid, doi, "openalex_work_linkage", f["url_logged"], f["status"], "not-found",
          "linkage check; locations=%s" % ([(x["source"], x["landing"]) for x in out[tag + "_openalex"]["locations"]]))
f = L.jget("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
           params={"query": 'DOI:"%s"' % PRE, "format": "json", "resultType": "core"})
out["epmc_preprint"] = [{k: h.get(k) for k in ("id", "source", "title", "doi", "pmcid", "pubYear", "bookOrReportDetails", "fullTextUrlList", "versionNumber", "commentCorrectionList")}
                        for h in ((f["json"] or {}).get("resultList") or {}).get("result", [])]
L.log("S11392", PRE, "europepmc_preprint_record", f["url_logged"], f["status"], "not-found",
      "Europe PMC preprint record: %s" % json.dumps(out["epmc_preprint"], ensure_ascii=False)[:600])
f = L.jget("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
           params={"query": 'DOI:"%s"' % JOUR, "format": "json", "resultType": "core"})
out["epmc_journal"] = [{k: h.get(k) for k in ("id", "source", "title", "doi", "pmcid", "pmid", "isOpenAccess", "hasSuppl", "commentCorrectionList")}
                       for h in ((f["json"] or {}).get("resultList") or {}).get("result", [])]
L.log("S13010", JOUR, "europepmc_journal_record", f["url_logged"], f["status"], "not-found",
      "Europe PMC journal record: %s" % json.dumps(out["epmc_journal"], ensure_ascii=False)[:600])
L.save_meta("S11392_S13010_linkage.json", out)
print(json.dumps(out, indent=1, ensure_ascii=False)[:6000])
