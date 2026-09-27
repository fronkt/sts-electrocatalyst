"""FT0 version linking: groups the full-text records that are versions of one piece of work.

  python version_link.py

Metadata only (the title/abstract screen identities plus the record texts); nothing is downloaded and
nothing decides eligibility.  Links, strongest first:
  doi        the same DOI (normalised)
  ange/anie  Angewandte German and international editions (10.1002/ange.X <-> 10.1002/anie.X)
  text       the record's own text names the published version ("Version of Record", "published in
             ... doi.org/...") or an arXiv identifier, and that DOI (10.48550/arxiv.<id>) is in the screened set
  title      identical normalised title and the same first-author surname
  similar    title word overlap (Jaccard) >= 0.8 over titles of 6+ words, same first-author surname;
             flagged "check" (probable, not certain)
Each group's primary is its journal article (type article or review), preferring one with a DOI, then
one inside the date window, then one in the full-text set, then the earliest.  Preprints, theses, conference abstracts and
reports collapse into it (rule D3).  A non-article form with no linked journal article is marked
"unlinked non-article" (D3: EXCLUDE:E1 unless its text names a journal article).
Writes reconcile/version_groups.csv and reconcile/version_groups.json.
"""
import collections
import csv
import json
import pathlib
import re

import retrieve_http as rh

HERE = pathlib.Path(__file__).resolve().parent
LO, HI = "2011-01-01", "2026-09-18"
JOURNAL = {"article", "review", "letter"}
DOI_IN_TEXT = re.compile(r"(?:version of record|published (?:version|article|in|at)|now published)[^\n]{0,200}?"
                         r"(?:doi\.org/|doi:\s*)(10\.\d{4,9}/[^\s\"<>)\]]+)", re.I)
ARXIV_IN_TEXT = re.compile(r"arxiv[:\s]*(\d{4}\.\d{4,5})", re.I)


def ntitle(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def surname(a):
    a = re.sub(r"[^a-z\- ]+", " ", (a or "").lower()).split()
    return a[-1] if a else ""


def ndoi(d):
    return (d or "").lower().strip().rstrip(".")


class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


def main():
    ids = {r["screen_id"]: r for r in csv.DictReader(open(rh.SCREEN / "screened_identities.csv", encoding="utf-8"))}
    ft = {r["screen_id"]: r for r in rh.load_records()}
    meta = {}
    for sid, r in ids.items():
        meta[sid] = dict(doi=ndoi(r["doi"]), title=r["title"], date=r["publication_date"], type=r["type"],
                         venue=r["venue"], sur=surname(r["first_author"]))
    for sid, r in ft.items():  # backward-reference records carry no screen identity
        meta.setdefault(sid, dict(doi=ndoi(r["doi"]), title=r["title"], date="", type="", venue="", sur=""))
    for m in meta.values():
        if m["doi"].startswith("10.1149/ma"):
            m["type"] = "conference-abstract"
    by_doi, by_title = collections.defaultdict(set), collections.defaultdict(set)
    by_sur = collections.defaultdict(set)
    for sid, m in meta.items():
        if m["doi"]:
            by_doi[m["doi"]].add(sid)
        nt = ntitle(m["title"])
        if nt:
            by_title[nt].add(sid)
        if m["sur"]:
            by_sur[m["sur"]].add(sid)
    uf, why = UF(), {}

    def link(a, b, reason):
        if a != b and uf.find(a) != uf.find(b):
            uf.union(a, b)
            for s in (a, b):
                why.setdefault(s, set()).add(reason)

    for sid in ft:
        m = meta[sid]
        for o in by_doi.get(m["doi"], ()):
            link(sid, o, "doi")
        if "/ange." in m["doi"] or "/anie." in m["doi"]:
            twin = m["doi"].replace("/ange.", "/anie.") if "/ange." in m["doi"] else m["doi"].replace("/anie.", "/ange.")
            for o in by_doi.get(twin, ()):
                link(sid, o, "ange/anie")
        tp = HERE / "text" / (sid + ".txt")
        if tp.exists():
            txt = tp.read_text(encoding="utf-8", errors="replace")
            found = DOI_IN_TEXT.findall(txt[:20000])
            if m["type"] not in JOURNAL:  # a thesis or report may name its preprint by arXiv number
                found += ["10.48550/arxiv." + a for a in ARXIV_IN_TEXT.findall(txt)]
            for d in found:
                for o in by_doi.get(ndoi(d), ()):
                    link(sid, o, "text")
        nt = ntitle(m["title"])
        for o in by_title.get(nt, ()):
            if o != sid and (not m["sur"] or not meta[o]["sur"] or m["sur"] == meta[o]["sur"]):
                link(sid, o, "title")
        words = set(nt.split())
        if len(words) >= 6 and m["sur"]:
            for o in by_sur[m["sur"]]:
                if o == sid:
                    continue
                w2 = set(ntitle(meta[o]["title"]).split())
                if len(w2) >= 6 and len(words & w2) / len(words | w2) >= 0.8:
                    link(sid, o, "similar")
    groups = collections.defaultdict(set)
    for sid in ft:
        groups[uf.find(sid)].add(sid)
    for s in list(uf.p):
        groups[uf.find(s)].add(s)
    rows, summary = [], collections.Counter()
    for g, members in groups.items():
        if not any(s in ft for s in members):
            continue
        journals = [s for s in members if meta[s]["type"] in JOURNAL]
        # a repository copy (no DOI, often a year-only date) is never preferred over the DOI-registered article
        primary = min(journals, key=lambda s: (not meta[s]["doi"], not (LO <= (meta[s]["date"] or "0") <= HI),
                                               s not in ft, meta[s]["date"] or "9999", s)) if journals else None
        gid = primary or min(members)
        for s in sorted(members):
            if s not in ft:
                continue
            m = meta[s]
            if len(members) == 1:
                role = "single"
            elif s == primary:
                role = "primary"
            elif primary:
                role = "linked"
            else:
                role = "group without journal article"
            nonart = m["type"] not in JOURNAL
            status = ("unlinked non-article" if nonart and not primary else
                      "collapses into primary" if role == "linked" else "")
            rows.append(dict(screen_id=s, group=gid, role=role, primary=primary or "", primary_in_fulltext=bool(primary in ft),
                             primary_date=primary and meta[primary]["date"], doi=m["doi"], type=m["type"],
                             link=";".join(sorted(why.get(s, ()))), check="yes" if "similar" in why.get(s, ()) and
                             not ({"doi", "title", "text", "ange/anie"} & why.get(s, set())) else "",
                             status=status, title=m["title"][:150]))
            summary[role] += 1
            if status:
                summary[status] += 1
    rows.sort(key=lambda r: (r["group"], r["role"] != "primary", r["screen_id"]))
    with open(HERE / "reconcile" / "version_groups.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    json.dump(dict(records=len(rows), counts=summary), open(HERE / "reconcile" / "version_groups.json", "w"), indent=1)
    print(len(rows), "records;", dict(summary))


if __name__ == "__main__":
    main()
