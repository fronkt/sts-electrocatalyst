"""Stage A: public-API metadata sweep for every target (no publisher hosts, no downloads).

Routes per record (all open, unauthenticated except the OpenAlex key read at request time):
  crossref        works/{doi}: relation / link / license / PII / authors / container
  openalex        works/doi:{doi}: every location (repositories, preprint servers), PMCID, OA status
  epmc_doi        Europe PMC exact-DOI search (hasSuppl, PMCID, preprint ids)
  epmc_title      Europe PMC exact-title search (other versions: preprints, repository records)
  datacite_rel    DataCite DOIs whose relatedIdentifiers contain the article DOI (Zenodo, figshare, Materials Cloud ...)
  datacite_title  DataCite exact-title phrase (a deposit named after the paper)
  zenodo_doi      Zenodo records quoting the DOI (the 2026-10-02 attempt returned HTTP 500 = service failure)
  openaire        OpenAIRE research products by DOI (repository instances)
  arxiv_title     arXiv exact title
Prior routes (Unpaywall DOI lookup, figshare exact DOI, publisher pages) are not repeated.
"""
import json
import pathlib
import re
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

T = json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))
only = set(sys.argv[1].split(",")) if len(sys.argv) > 1 else None


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def title_phrase(t):
    t = re.sub(r"<[^>]+>", "", t or "")
    t = re.sub(r"\s+", " ", t).strip()
    return t


for rec in T["targets"] + T["skipped_dead_end"][:0]:
    sid, doi, title = rec["screen_id"], rec["doi"], title_phrase(rec["title"])
    if only and sid not in only:
        continue
    meta = {"screen_id": sid, "doi": doi, "title_checklist": title}

    # 1 Crossref
    u = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    f = L.jget(u)
    cr = (f["json"] or {}).get("message", {}) if f["status"] == 200 else {}
    meta["crossref"] = {k: cr.get(k) for k in ("title", "container-title", "publisher", "relation", "link", "license",
                                              "alternative-id", "issued", "published-online", "published-print",
                                              "type", "subtype", "update-to", "is-referenced-by-count")}
    meta["crossref"]["authors"] = [(a.get("family"), a.get("given")) for a in cr.get("author", [])]
    rel = cr.get("relation") or {}
    L.log(sid, doi, "crossref_works", f["url_logged"], f["status"], "not-found",
          "Crossref record retrieved; relation keys=%s; no has-supplement/SI link" % (sorted(rel) or "none")
          if f["status"] == 200 else "Crossref lookup failed: %s" % (f.get("error") or f["status"]))

    # 2 OpenAlex
    f = L.jget("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi),
               secret_param={"api_key": L.openalex_key()})
    w = f["json"] or {}
    locs = []
    for loc in w.get("locations", []) or []:
        src = loc.get("source") or {}
        locs.append({"landing": loc.get("landing_page_url"), "pdf": loc.get("pdf_url"), "version": loc.get("version"),
                     "is_oa": loc.get("is_oa"), "source": src.get("display_name"), "stype": src.get("type"),
                     "license": loc.get("license")})
    meta["openalex"] = {"id": w.get("id"), "ids": w.get("ids"), "title": w.get("title"),
                        "open_access": w.get("open_access"), "locations": locs,
                        "best_oa_location": w.get("best_oa_location"), "publication_date": w.get("publication_date"),
                        "authors": [(a.get("author") or {}).get("display_name") for a in w.get("authorships", [])][:8]}
    nonpub = [x for x in locs if x["stype"] in ("repository", "preprint server") or (x["landing"] and "doi.org" not in x["landing"] and x["stype"] != "journal")]
    L.log(sid, doi, "openalex_work_locations", f["url_logged"], f["status"], "not-found",
          ("OpenAlex returned %d locations; non-publisher locations: %s" %
           (len(locs), [(x["source"], x["landing"]) for x in nonpub] or "none")) if f["status"] == 200
          else "OpenAlex lookup failed: %s" % (f.get("error") or f["status"]))

    # 3 Europe PMC exact DOI
    f = L.jget("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
               params={"query": 'DOI:"%s"' % doi, "format": "json", "resultType": "core"})
    hits = ((f["json"] or {}).get("resultList") or {}).get("result", [])
    meta["epmc_doi"] = [{k: h.get(k) for k in ("id", "source", "pmcid", "doi", "title", "isOpenAccess", "inEPMC",
                                              "hasSuppl", "fullTextUrlList", "journalTitle")} for h in hits]
    note = "no Europe PMC record for the DOI" if not hits else \
        "hits=%s" % [(h.get("source"), h.get("id"), h.get("pmcid"), "OA=" + str(h.get("isOpenAccess")),
                      "suppl=" + str(h.get("hasSuppl"))) for h in hits]
    L.log(sid, doi, "europepmc_doi_search", f["url_logged"], f["status"], "not-found", note)

    # 4 Europe PMC exact title (other versions)
    f = L.jget("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
               params={"query": 'TITLE:"%s"' % title.replace('"', ""), "format": "json", "resultType": "lite", "pageSize": 10})
    hits = ((f["json"] or {}).get("resultList") or {}).get("result", [])
    exact = [h for h in hits if norm(h.get("title")) == norm(title)]
    meta["epmc_title"] = [{k: h.get(k) for k in ("id", "source", "pmcid", "doi", "title", "isOpenAccess", "hasSuppl")}
                          for h in exact]
    L.log(sid, doi, "europepmc_title_search", f["url_logged"], f["status"], "not-found",
          "exact-title hits: %s" % ([(h.get("source"), h.get("id"), h.get("doi"), h.get("pmcid")) for h in exact] or "none"))

    # 5 DataCite related identifier + title
    f = L.jget("https://api.datacite.org/dois",
               params={"query": 'relatedIdentifiers.relatedIdentifier:"%s"' % doi, "page[size]": 20})
    data = (f["json"] or {}).get("data", [])
    meta["datacite_rel"] = [{"doi": d["id"], "title": (d["attributes"].get("titles") or [{}])[0].get("title"),
                             "publisher": d["attributes"].get("publisher"),
                             "types": d["attributes"].get("types"), "related": d["attributes"].get("relatedIdentifiers"),
                             "url": d["attributes"].get("url")} for d in data]
    L.log(sid, doi, "datacite_related_identifier", f["url_logged"], f["status"], "not-found",
          "datasets citing the DOI: %s" % ([(d["id"], d["attributes"].get("publisher")) for d in data] or "none"))
    f = L.jget("https://api.datacite.org/dois", params={"query": 'titles.title:"%s"' % title.replace('"', ""),
                                                        "page[size]": 10})
    data = (f["json"] or {}).get("data", [])
    exact = [d for d in data if norm((d["attributes"].get("titles") or [{}])[0].get("title")) == norm(title)]
    meta["datacite_title"] = [{"doi": d["id"], "publisher": d["attributes"].get("publisher"),
                               "types": d["attributes"].get("types"), "url": d["attributes"].get("url")} for d in exact]
    L.log(sid, doi, "datacite_title_phrase", f["url_logged"], f["status"], "not-found",
          "exact-title DataCite DOIs: %s" % ([(d["id"], d["attributes"].get("publisher")) for d in exact] or "none"))

    # 6 Zenodo
    f = L.jget("https://zenodo.org/api/records", params={"q": '"%s"' % doi, "size": 10})
    hh = ((f["json"] or {}).get("hits") or {}).get("hits", [])
    meta["zenodo"] = [{"id": h.get("id"), "doi": h.get("doi"), "title": (h.get("metadata") or {}).get("title"),
                       "files": [(x.get("key"), x.get("size")) for x in (h.get("files") or [])][:20]} for h in hh]
    L.log(sid, doi, "zenodo_api_doi_query", f["url_logged"], f["status"], "not-found",
          "Zenodo records quoting the DOI: %s" % ([(h["id"], h["title"]) for h in meta["zenodo"]] or "none")
          if f["status"] == 200 else "Zenodo query failed: %s" % (f.get("error") or f["status"]))

    # 7 OpenAIRE
    f = L.jget("https://api.openaire.eu/search/publications", params={"doi": doi, "format": "json"})
    meta["openaire_status"] = f["status"]
    inst = []

    def walk(o, key=None):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, key)
        elif isinstance(o, str) and key in ("url", "$") and o.startswith("http"):
            inst.append(o)
    walk((f["json"] or {}).get("response", {}).get("results"))
    inst = sorted(set(inst))
    meta["openaire_instances"] = inst
    L.log(sid, doi, "openaire_search_publications", f["url_logged"], f["status"], "not-found",
          "OpenAIRE instances=%d" % len(inst) if f["status"] == 200 else "OpenAIRE query failed: %s" % (f.get("error") or f["status"]))

    # 8 arXiv exact title
    f = L.fetch("https://export.arxiv.org/api/query", params={"search_query": 'ti:"%s"' % title.replace('"', ""), "max_results": 3})
    f.pop("resp", None)
    titles = re.findall(r"<entry>.*?<title>(.*?)</title>.*?<id>(.*?)</id>", f["text"], flags=re.S) if f["status"] == 200 else []
    exact = [(t, i) for t, i in titles if norm(t) == norm(title)]
    meta["arxiv"] = exact
    L.log(sid, doi, "arxiv_title_query", f["url_logged"], f["status"], "not-found",
          "arXiv exact-title match: %s" % (exact or "none"))

    L.save_meta("%s_sweep.json" % sid, meta)
    print(sid, "done", flush=True)
