"""Independent adversarial review of results/s2_2026-09-23/{backward_reference_identity,supplement_access}.

Read-only with respect to both reviewed folders. Writes only a JSON scratch of the
automated recomputation (``_review_auto.json`` in the scratchpad passed as argv[1]);
the final review JSON is assembled separately. No network access.
"""
import collections
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path("C:/Users/frank/sts-electrocatalyst")
F1 = ROOT / "results/s2_2026-09-23/backward_reference_identity"
IN20 = "results/s2_2026-09-20/backward_reference_discovery/reference_occurrences.json"
IN21 = "results/s2_2026-09-21/backward_reference_extension/reference_occurrences.json"
UNION = "results/s2_2026-09-22/identity_handoff/provider_identity_union.jsonl"
EXPECTED = {
    IN20: "be7fde04d03eb59fd617ba02401caeecfac8240479ee34f59d9694d0ac993867",
    IN21: "8a16a6216c0a1ad49e199fac93a37709c0e1e7569ea0115e6837412fea8388e5",
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def letters(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z]", "", s.lower())


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s or "")


out = {"findings": [], "checks": {}}


def check(name, ok, detail=None):
    out["checks"][name] = {"pass": bool(ok), "detail": detail}


# ---------------- inputs ----------------
hashes = {k: sha(ROOT / k) for k in list(EXPECTED) + [UNION]}
check("input_sha256_unchanged", all(hashes[k] == v for k, v in EXPECTED.items()), hashes)
pre = json.loads((F1 / "input_hashes_before.json").read_text(encoding="utf-8"))
check("union_sha256_equals_recorded_before", pre["sha256"][UNION] == hashes[UNION], hashes[UNION])

occ = {}
for p in (IN20, IN21):
    d = json.loads((ROOT / p).read_text(encoding="utf-8"))
    for o in d["reference_occurrences"]:
        assert o["occurrence_id"] not in occ
        occ[o["occurrence_id"]] = (p, o)

links = [json.loads(l) for l in (F1 / "reference_identity_links.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
ids = collections.Counter(r["occurrence_id"] for r in links)
check("every_occurrence_linked_exactly_once",
      set(ids) == set(occ) and all(v == 1 for v in ids.values()) and len(links) == len(occ),
      {"inputs": len(occ), "links": len(links), "dupes": [k for k, v in ids.items() if v > 1],
       "missing": sorted(set(occ) - set(ids)), "extra": sorted(set(ids) - set(occ))})

field_map = [("bibliography_verbatim", "printed_citation_verbatim"),
             ("display_whitespace_normalized", "printed_citation_normalized"),
             ("explicit_dois_as_transcribed", "printed_dois_as_transcribed"),
             ("doi_basis", "doi_basis"), ("parent_doi", "parent_doi"), ("document_id", "document_id"),
             ("document_role", "document_role"), ("reference_number", "reference_number"),
             ("subreference_letter", "subreference_letter"), ("parent_reference_group", "parent_reference_group"),
             ("discovery_generation", "discovery_generation")]
mism = []
for r in links:
    p, o = occ[r["occurrence_id"]]
    if r["source_input"] != p or r["source_input_sha256"] != EXPECTED[p]:
        mism.append((r["link_id"], "source_input"))
    for a, b in field_map:
        if o.get(a) != r.get(b):
            mism.append((r["link_id"], a))
    for a in ("reference_ordinal", "label_kind"):
        if o.get(a) != r.get(a):
            mism.append((r["link_id"], a))
    loc = r["locators"]
    for a in ("source_pdf_pages", "source_text_line_start", "source_text_line_end"):
        if o.get(a) != loc.get(a):
            mism.append((r["link_id"], "locator:" + a))
check("printed_fields_unchanged", not mism, mism[:50])

# ---------------- status / rule-level recount ----------------
st = collections.Counter(r["resolution"]["status"] for r in links)
top = collections.Counter(r["identity_validation_status"] for r in links)
check("top_status_equals_resolution_status",
      all(r["identity_validation_status"] == r["resolution"]["status"] for r in links))
by_doc = collections.Counter(r["document_id"] for r in links)
by_in = collections.Counter(r["source_input"] for r in links)
printed = [r for r in links if r["printed_dois_as_transcribed"]]
resolved = [r for r in links if r["resolution"]["status"] in ("RESOLVED_PRINTED_DOI", "RESOLVED_BIBLIOGRAPHIC")]
rdois = collections.Counter(r["resolution"]["doi"].lower() for r in resolved)
cand_cls = collections.Counter(r["resolution"].get("candidate_class") for r in links if r["resolution"]["status"] == "CANDIDATE")
unres = collections.Counter(r["resolution"].get("unresolved_reason") for r in links if r["resolution"]["status"] == "UNRESOLVED")
flags = [r["link_id"] for r in resolved if r["resolution"].get("review_flags")]
flag_kinds = collections.Counter(f for r in resolved for f in r["resolution"].get("review_flags", []))

# route consistency
route_bad = []
for r in links:
    res = r["resolution"]
    s = res["status"]
    if s == "RESOLVED_PRINTED_DOI" and (not r["printed_dois_as_transcribed"] or res["route"] != "PRINTED_DOI"):
        route_bad.append(r["link_id"])
    if s == "RESOLVED_BIBLIOGRAPHIC" and (r["printed_dois_as_transcribed"] or res["route"] != "BIBLIOGRAPHIC_QUERY"):
        route_bad.append(r["link_id"])
    if s == "RESOLVED_PRINTED_DOI" and res["doi"].lower() not in [d.lower() for d in r["printed_dois_as_transcribed"]]:
        route_bad.append(r["link_id"] + ":doi_not_printed")
check("route_consistency", not route_bad, route_bad)

# ---------------- union re-derivation ----------------
union_dois = collections.defaultdict(set)
with open(ROOT / UNION, encoding="utf-8") as f:
    for line in f:
        u = json.loads(line)
        for v in u["metadata_variants"]:
            d = v["metadata"].get("doi")
            if d:
                d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d.strip(), flags=re.I).lower()
                union_dois[d].add(u["provider_id"])
matched_occ = [r for r in resolved if r["resolution"]["doi"].lower() in union_dois]
matched_dois = {r["resolution"]["doi"].lower() for r in matched_occ}
new_dois = set(rdois) - matched_dois
new_occ = [r for r in resolved if r["resolution"]["doi"].lower() in new_dois]
union_rec_bad = []
for r in links:
    res = r["resolution"]
    for key, dkey in (("openalex_union", "doi"), ("candidate_openalex_union", "candidate_doi")):
        if key in res:
            d = res[dkey].lower() if res.get(dkey) else res[key]["doi_checked"].lower()
            exp = d in union_dois
            if res[key]["matched"] != exp or (exp and set(res[key]["openalex_ids"]) != union_dois[d]):
                union_rec_bad.append((r["link_id"], key, d, res[key]["matched"], exp))
    if res["status"].startswith("RESOLVED") and "openalex_union" not in res:
        union_rec_bad.append((r["link_id"], "missing_openalex_union"))
check("union_match_rederived", not union_rec_bad, union_rec_bad[:30])
summ = json.loads((F1 / "summary.json").read_text(encoding="utf-8"))
check("new_to_union_list_equals_rederived", set(summ["new_to_union_dois"]) == new_dois,
      {"summary_minus_mine": sorted(set(summ["new_to_union_dois"]) - new_dois),
       "mine_minus_summary": sorted(new_dois - set(summ["new_to_union_dois"]))})
cand_in_union = {r["resolution"]["candidate_doi"].lower() for r in links
                 if r["resolution"]["status"] == "CANDIDATE" and r["resolution"].get("candidate_doi")
                 and r["resolution"]["candidate_doi"].lower() in union_dois}

recount = {
    "occurrences": len(links),
    "occurrences_by_input": dict(by_in),
    "occurrences_by_document": dict(by_doc),
    "occurrences_with_printed_doi": len(printed),
    "status": dict(st),
    "resolved_doi_occurrences": len(resolved),
    "resolved_distinct_dois": len(rdois),
    "matched_to_openalex_union_occurrences": len(matched_occ),
    "matched_to_openalex_union_distinct_dois": len(matched_dois),
    "new_to_union_distinct_dois": len(new_dois),
    "new_to_union_occurrences": len(new_occ),
    "candidates_by_class": dict(cand_cls),
    "unresolved_by_reason": dict(unres),
    "resolved_with_review_flags": len(flags),
    "review_flag_kinds": dict(flag_kinds),
    "candidate_dois_in_union_distinct": len(cand_in_union),
    "discovery_generation_values": sorted({r["discovery_generation"] for r in links}),
    "seeds_further_expansion_true": sum(1 for r in links if r["seeds_further_expansion"] is not False),
    "eligibility_status_values": dict(collections.Counter(r["eligibility_status"] for r in links)),
    "method_coding_status_values": dict(collections.Counter(r["method_coding_status"] for r in links)),
}
out["recount_folder1"] = recount
sc = summ["counts"]
diffs = {k: (sc.get(k), v) for k, v in recount.items() if k in sc and sc.get(k) != v}
check("summary_counts_equal_recount", not diffs, diffs)

# ---------------- receipts & raw hashes ----------------
recs = [json.loads(l) for l in (F1 / "request_receipts.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
final = {}
for rc in recs:
    final[rc["request_key"]] = rc
hash_bad = []
nfiles = 0
for rc in recs:
    if rc.get("raw_path"):
        nfiles += 1
        p = ROOT / rc["raw_path"]
        if not p.exists() or sha(p) != rc["sha256"] or p.stat().st_size != rc["bytes"]:
            hash_bad.append(rc["request_key"])
    for a in rc.get("attempts", []):
        if a.get("error_path"):
            p = ROOT / a["error_path"]
            if not p.exists() or sha(p) != a["error_sha256"]:
                hash_bad.append(a["error_path"])
    if rc["status"] == "CACHE_REUSED":
        src = ROOT / rc["cache_source_path"]
        if not src.exists() or sha(src) != rc["sha256"]:
            hash_bad.append("cache_source:" + rc["request_key"])
        if not (ROOT / rc["cache_receipt_path"]).exists():
            hash_bad.append("cache_receipt_missing:" + rc["request_key"])
# every file on disk referenced by some receipt?
referenced = {str((ROOT / rc["raw_path"]).resolve()).lower() for rc in recs if rc.get("raw_path")}
referenced |= {str((ROOT / a["error_path"]).resolve()).lower() for rc in recs for a in rc.get("attempts", []) if a.get("error_path")}
disk = [p for sub in ("crossref_works", "crossref_bibliographic", "crossref_failures") for p in (F1 / sub).iterdir()]
orphans = [str(p) for p in disk if str(p.resolve()).lower() not in referenced]
check("receipt_raw_hashes_match_disk", not hash_bad, hash_bad)
check("no_orphan_raw_files", not orphans, orphans)
ua_bad = [rc["request_key"] for rc in recs if rc["status"] != "CACHE_REUSED" and "mailto:<contact-email-redacted>" not in rc.get("user_agent", "")]
check("user_agent_mailto", not ua_bad, ua_bad)
hosts = collections.Counter(re.match(r"https?://[^/]+", rc["url"]).group(0) for rc in recs)
check("only_crossref_api", set(hosts) == {"https://api.crossref.org"}, dict(hosts))
out["receipts"] = {"lines": len(recs), "keys": len(final), "files_with_hash": nfiles,
                   "final_status": dict(collections.Counter(v["status"] for v in final.values())),
                   "http_attempts": sum(len(rc.get("attempts", [])) for rc in recs),
                   "disk_files": len(disk)}

# link-record receipts consistent with receipt log and raw file content
link_bad = []
for r in links:
    res = r["resolution"]
    for key in ("crossref_works_receipt",):
        if key in res and res[key].get("raw_path"):
            rc = res[key]
            if sha(ROOT / rc["raw_path"]) != rc["sha256"]:
                link_bad.append((r["link_id"], "works_hash"))
            raw = json.loads((ROOT / rc["raw_path"]).read_text(encoding="utf-8"))
            msg = raw.get("message", raw)
            if msg.get("DOI", "").lower() != res["doi"].lower():
                link_bad.append((r["link_id"], "raw_doi_mismatch", msg.get("DOI")))
            md = res.get("crossref_metadata", {})
            if md.get("title") != msg.get("title") or md.get("container_title") != msg.get("container-title"):
                link_bad.append((r["link_id"], "metadata_not_from_raw"))
    bq = res.get("bibliographic_query")
    if bq and bq["receipt"].get("raw_path"):
        raw = json.loads((ROOT / bq["receipt"]["raw_path"]).read_text(encoding="utf-8"))
        items = raw["message"]["items"]
        rawdois = [i["DOI"].lower() for i in items]
        for it in bq["items_evaluated"]:
            if rawdois[it["rank"] - 1] != it["doi"].lower():
                link_bad.append((r["link_id"], "bib_item_not_in_raw", it["doi"]))
        if res["status"] == "RESOLVED_BIBLIOGRAPHIC":
            ch = [i for i in bq["items_evaluated"] if i["rank"] == bq["chosen_rank"]][0]
            if ch["doi"].lower() != res["doi"].lower() or not all(ch["four_field_agreement"].values()):
                link_bad.append((r["link_id"], "chosen_not_four_field"))
            if ch.get("is_correction_or_erratum_notice"):
                link_bad.append((r["link_id"], "chosen_is_erratum"))
check("link_receipts_consistent_with_raw", not link_bad, link_bad[:40])

# ---------------- independent agreement on resolved records ----------------
MONTHS = r"(19|20)\d\d"


def years_of(msg):
    ys = set()
    for k in ("issued", "published-print", "published-online", "published", "created"):
        dp = (msg.get(k) or {}).get("date-parts") or []
        if dp and dp[0] and dp[0][0]:
            ys.add(int(dp[0][0]))
    return ys


def indep(r):
    res = r["resolution"]
    msg = json.loads((ROOT / res["crossref_works_receipt"]["raw_path"]).read_text(encoding="utf-8"))["message"]
    cit = r["printed_citation_normalized"]
    L = letters(cit)
    title = strip_tags((msg.get("title") or [""])[0])
    tl = letters(title)
    words = [w for w in re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", title).lower()) if len(w) > 2]
    cw = set(re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", cit).lower()))
    cov = sum(w in cw for w in words) / len(words) if words else 0
    t_ok = (tl and tl in L) or cov >= 0.8
    auth = [a for a in msg.get("author", []) if a.get("sequence") == "first"] or msg.get("author", [])
    fam = letters(auth[0].get("family", auth[0].get("name", ""))) if auth else ""
    a_ok = bool(fam) and fam in L[:60]
    py = {int(y) for y in re.findall(r"\b((?:19|20)\d\d)\b", cit)}
    cy = years_of({k: v for k, v in msg.items() if k != "created"})
    y_ok = bool(py & cy)
    cont = (msg.get("container-title") or [""]) + (msg.get("short-container-title") or [])
    # journal: all capital initials of container significant words appear in order? use loose check:
    j_ok = False
    for c in cont:
        toks = [t for t in re.findall(r"[a-z]+", c.lower()) if t not in ("of", "the", "and", "for", "in", "de", "a", "an", "on")]
        if not toks:
            continue
        # each printed abbreviation must be a prefix of successive container tokens
        ptoks = re.findall(r"[a-z]+", cit.lower())
        # search in-order prefix-match of the first 3 container tokens
        k = 0
        for pt in ptoks:
            if k < len(toks) and toks[k].startswith(pt) and len(pt) >= 1:
                k += 1
            elif k and k < len(toks):
                k = 0 if not toks[0].startswith(pt) else 1
            if k == len(toks):
                break
        if k == len(toks) or letters(c) in L:
            j_ok = True
    vol_ok = msg.get("volume") and re.search(r"\b" + re.escape(msg["volume"]) + r"\b", cit)
    return {"title": bool(t_ok), "title_cov": round(cov, 2), "author": a_ok, "year": y_ok, "journal": j_ok,
            "volume": bool(vol_ok), "cr_title": title, "cr_first": fam, "cr_years": sorted(cy),
            "cr_journal": cont[0] if cont else None, "cr_type": msg.get("type")}


indep_rows = {}
for r in resolved:
    indep_rows[r["link_id"]] = indep(r)
out["independent_agreement"] = indep_rows
weak = {k: v for k, v in indep_rows.items() if not (v["author"] and v["year"] and (v["journal"] or v["volume"]))}
out["independent_weak_resolved"] = sorted(weak)
bib_title_fail = sorted(k for k, v in indep_rows.items()
                        if next(r for r in resolved if r["link_id"] == k)["resolution"]["status"] == "RESOLVED_BIBLIOGRAPHIC"
                        and not v["title"])
out["independent_bib_title_fail"] = bib_title_fail

# conflicts keep both sides
conf = [r for r in links if r["resolution"]["status"] == "CONFLICT"]
conf_bad = []
for r in conf:
    res = r["resolution"]
    if not (r["printed_citation_verbatim"] and res.get("crossref_metadata") and res.get("doi")
            and res.get("disagreeing_fields") and "supplementary_bibliographic_evidence" in res):
        conf_bad.append(r["link_id"])
check("conflicts_keep_both_sides", not conf_bad, {"conflicts": [r["link_id"] for r in conf], "bad": conf_bad})
out["conflict_detail"] = {r["link_id"]: {"printed": r["printed_citation_normalized"], "doi": r["resolution"]["doi"],
                                         "disagreeing": r["resolution"]["disagreeing_fields"],
                                         "cr_title": (r["resolution"]["crossref_metadata"]["title"] or [""])[0][:120]}
                          for r in conf}

# no eligibility / method coding / seeding anywhere
txt = (F1 / "reference_identity_links.jsonl").read_text(encoding="utf-8")
bad_keys = [k for k in ("INCLUDED", "EXCLUDED", "ELIGIBLE\"", "\"eligible\"", "method_code\"") if k in txt]
check("no_eligibility_or_method_coding",
      recount["eligibility_status_values"] == {"NOT_SCREENED": 529}
      and recount["method_coding_status_values"] == {"NOT_CODED": 529} and not bad_keys, bad_keys)
check("no_seeding", recount["seeds_further_expansion_true"] == 0 and recount["discovery_generation_values"] == [1])

# document title style vs RESOLVED_BIBLIOGRAPHIC
style = collections.defaultdict(collections.Counter)
for r in links:
    style[r["document_id"]][(r["title_printed_in_citation_style"], r["resolution"]["status"])] += 1
out["style_by_document"] = {d: {f"{k[0]}|{k[1]}": v for k, v in c.items()} for d, c in style.items()}
nontitle_resolved_bib = [r["link_id"] for r in links if not r["title_printed_in_citation_style"]
                         and r["resolution"]["status"] == "RESOLVED_BIBLIOGRAPHIC"]
check("no_resolved_bibliographic_without_printed_title", not nontitle_resolved_bib, nontitle_resolved_bib)

json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
for k, v in out["checks"].items():
    print(("PASS " if v["pass"] else "FAIL ") + k, "" if v["pass"] else json.dumps(v["detail"], default=str)[:600])
print(json.dumps(recount, indent=0, default=str))
print("weak", len(weak), sorted(weak)[:60])
print("bib_title_fail", bib_title_fail)
