"""Identity confirmation for each target through Crossref and OpenAlex (open APIs; the OpenAlex key is read at request
time and never printed, logged or saved).  Saves metadata/<SID>_identity.json and logs two route rows per record.
Records what the exact DOI is (title, authors, PII, dates, container) and whether it agrees with the checklist title,
the PII in the checklist's ScienceDirect link, and the corpus main text (text/<SID>.txt).  No eligibility judgement."""
import json
import pathlib
import re
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import si_recovery_lib as L  # noqa: E402

T = json.loads((L.PHASE / "targets.json").read_text(encoding="utf-8"))["targets"]


def norm(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


for rec in T:
    sid, doi, title = rec["screen_id"], rec["doi"], rec["title"]
    meta = {"screen_id": sid, "doi": doi, "title_checklist": title}
    f = L.jget("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    cr = (f["json"] or {}).get("message", {}) if f["status"] == 200 else {}
    meta["crossref"] = {k: cr.get(k) for k in ("title", "container-title", "publisher", "alternative-id", "issued",
                                              "published-online", "published-print", "type", "ISSN", "relation")}
    meta["crossref"]["authors"] = [(a.get("family"), a.get("given")) for a in cr.get("author", [])]
    L.log(sid, doi, "crossref_works_identity", f["url_logged"], f["status"], "not-found",
          "Crossref record retrieved for the exact DOI (identity check only; its api.elsevier.com text-mining links are not used)"
          if f["status"] == 200 else "Crossref lookup failed: %s" % (f.get("error") or f["status"]))
    f = L.jget("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi), secret_param={"api_key": L.openalex_key()})
    w = f["json"] or {}
    meta["openalex"] = {"id": w.get("id"), "title": w.get("title"), "publication_date": w.get("publication_date"),
                        "type": w.get("type"),
                        "authors": [(a.get("author") or {}).get("display_name") for a in w.get("authorships", [])],
                        "source": ((w.get("primary_location") or {}).get("source") or {}).get("display_name")}
    L.log(sid, doi, "openalex_work_identity", f["url_logged"], f["status"], "not-found",
          "OpenAlex record retrieved for the exact DOI (identity check only)" if f["status"] == 200
          else "OpenAlex lookup failed: %s" % (f.get("error") or f["status"]))
    pii = (meta["crossref"].get("alternative-id") or [None])[0]
    cr_title = (meta["crossref"].get("title") or [""])[0]
    oa_title = meta["openalex"].get("title") or ""
    main = (L.FT / rec["main_text"]).read_text(encoding="utf-8", errors="ignore")
    head = norm(main[:6000])
    surn = [a[0] for a in meta["crossref"]["authors"] if a and a[0]]
    meta["identity_checks"] = {
        "crossref_title_equals_checklist_title": norm(cr_title) == norm(title),
        "openalex_title_equals_checklist_title": norm(oa_title) == norm(title),
        "crossref_title": cr_title, "openalex_title": oa_title,
        "crossref_pii": pii, "checklist_pii_from_si_link": rec["checklist_pii_from_si_link"],
        "pii_agrees": pii == rec["checklist_pii_from_si_link"],
        "crossref_author_count": len(surn), "openalex_author_count": len(meta["openalex"]["authors"]),
        "first_author_surname_in_main_text_head": bool(surn and norm(surn[0]) in head),
        "crossref_title_first8_words_in_main_text_head": " ".join(norm(cr_title).split()[:8]) in head,
        "crossref_issued": (meta["crossref"].get("issued") or {}).get("date-parts"),
        "crossref_published_online": (meta["crossref"].get("published-online") or {}).get("date-parts"),
        "crossref_container": (meta["crossref"].get("container-title") or [None])[0],
        "crossref_publisher": meta["crossref"].get("publisher"),
        "openalex_publication_date": meta["openalex"].get("publication_date"),
    }
    L.save_meta("%s_identity.json" % sid, meta)
    print(sid, json.dumps(meta["identity_checks"], ensure_ascii=False))
