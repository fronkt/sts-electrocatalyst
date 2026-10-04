"""Other-version discovery by exact title: Crossref posted-content (preprints) and OpenAlex title search.
Public APIs, no downloads.  A title match with a first-author surname match is a LEAD (another version of the same
work), never a recovered SI by itself."""
import json
import pathlib
import re
import sys
import urllib.parse

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
    title = re.sub(r"<[^>]+>", "", rec["title"])
    sw = json.loads((L.META / ("%s_sweep.json" % sid)).read_text(encoding="utf-8"))
    first = ((sw["crossref"].get("authors") or [[None]])[0] or [None])[0]
    hits = []
    f = L.jget("https://api.crossref.org/works", params={"query.bibliographic": title, "filter": "type:posted-content", "rows": 5,
                                                          "select": "DOI,title,author,publisher,posted,institution"})
    for it in ((f["json"] or {}).get("message") or {}).get("items", []):
        t = (it.get("title") or [""])[0]
        sim = len(set(norm(t).split()) & set(norm(title).split())) / max(1, len(set(norm(title).split())))
        fa = [a.get("family") for a in it.get("author", [])]
        if sim >= 0.8:
            hits.append({"via": "crossref_posted_content", "doi": it.get("DOI"), "title": t, "sim": round(sim, 2),
                         "first_author_match": bool(first and first in fa), "publisher": it.get("publisher")})
    L.log(sid, doi, "crossref_posted_content_title", f["url_logged"], f["status"], "not-found",
          "preprint/other-version candidates (title similarity>=0.8): %s" % ([(h["doi"], h["sim"], h["first_author_match"]) for h in hits] or "none"))
    f = L.jget("https://api.openalex.org/works", params={"filter": "title.search:%s" % title.replace(",", " ").replace(":", " ")[:200],
                                                         "per-page": 8, "select": "id,doi,title,locations,type,publication_year"},
               secret_param={"api_key": L.openalex_key()})
    for w in ((f["json"] or {}).get("results") or []):
        if norm(w.get("title")) == norm(title) and (w.get("doi") or "").lower().replace("https://doi.org/", "") != doi.lower():
            hits.append({"via": "openalex_title", "doi": w.get("doi"), "id": w.get("id"), "type": w.get("type"),
                         "locations": [(x.get("landing_page_url"), x.get("pdf_url")) for x in w.get("locations", [])]})
    L.log(sid, doi, "openalex_title_search", f["url_logged"], f["status"], "not-found",
          "other works with the identical title: %s" % ([(h["doi"], h.get("type")) for h in hits if h["via"] == "openalex_title"] or "none"))
    out[sid] = hits
    print(sid, json.dumps(hits, ensure_ascii=False)[:500], flush=True)
L.save_meta("preprint_search.json", out)
