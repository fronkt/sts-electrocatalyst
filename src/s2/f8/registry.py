"""Crossref / DataCite lookups (cached) and a normalised metadata record."""
from __future__ import annotations

import urllib.parse
from dataclasses import asdict, dataclass, field

from .common import Fetcher, cache_key
from .textnorm import clean_markup, norm_pages

CROSSREF_WORKS = "https://api.crossref.org/works/"
CROSSREF_SEARCH = "https://api.crossref.org/works?"
DATACITE_DOIS = "https://api.datacite.org/dois/"


@dataclass
class Record:
    doi: str
    registrar: str                 # crossref | datacite | none
    status: int                    # HTTP status of the registrar that answered
    type: str = ""
    title_raw: str = ""
    title: str = ""
    authors: list = field(default_factory=list)   # [{"family","given","name"}]
    year_print: int | None = None
    year_online: int | None = None
    year_issued: int | None = None
    journal_raw: str = ""
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    publisher: str = ""
    alternative_ids: list = field(default_factory=list)
    cache_file: str = ""

    @property
    def year(self) -> int | None:
        """Precedence print > online > issued (the rule docs/references.bib was built with)."""
        for y in (self.year_print, self.year_online, self.year_issued):
            if y:
                return y
        return None

    @property
    def first_family(self) -> str:
        if not self.authors:
            return ""
        a = self.authors[0]
        return a.get("family") or a.get("name") or ""

    def as_dict(self) -> dict:
        d = asdict(self)
        d["year"] = self.year
        d["first_author_family"] = self.first_family
        return d


def _year(msg: dict, k: str) -> int | None:
    parts = (msg.get(k) or {}).get("date-parts") or []
    if parts and parts[0] and parts[0][0]:
        return int(parts[0][0])
    return None


def from_crossref(doi: str, msg: dict, status: int = 200, cache_file: str = "") -> Record:
    authors = []
    for a in msg.get("author") or []:
        authors.append({"family": clean_markup(a.get("family")), "given": clean_markup(a.get("given")),
                        "name": clean_markup(a.get("name")), "sequence": a.get("sequence", "")})
    title_raw = (msg.get("title") or [""])[0] or ""
    journal_raw = (msg.get("container-title") or [""])[0] or ""
    return Record(
        doi=doi, registrar="crossref", status=status, type=msg.get("type", ""),
        title_raw=title_raw, title=clean_markup(title_raw), authors=authors,
        year_print=_year(msg, "published-print"), year_online=_year(msg, "published-online"),
        year_issued=_year(msg, "issued"), journal_raw=journal_raw, journal=clean_markup(journal_raw),
        volume=str(msg.get("volume") or ""), issue=str(msg.get("issue") or ""),
        pages=norm_pages(msg.get("page") or msg.get("article-number") or ""),
        publisher=clean_markup(msg.get("publisher")),
        alternative_ids=list(msg.get("alternative-id") or []), cache_file=cache_file)


def from_datacite(doi: str, attrs: dict, status: int = 200, cache_file: str = "") -> Record:
    authors = []
    for c in attrs.get("creators") or []:
        authors.append({"family": c.get("familyName") or "", "given": c.get("givenName") or "",
                        "name": c.get("name") or "", "sequence": ""})
    titles = attrs.get("titles") or []
    title_raw = (titles[0].get("title") if titles else "") or ""
    y = attrs.get("publicationYear")
    types = attrs.get("types") or {}
    return Record(
        doi=doi, registrar="datacite", status=status,
        type=(types.get("resourceTypeGeneral") or "").lower(), title_raw=title_raw,
        title=clean_markup(title_raw), authors=authors, year_issued=int(y) if y else None,
        journal_raw="", journal="", publisher=clean_markup(attrs.get("publisher") if isinstance(
            attrs.get("publisher"), str) else (attrs.get("publisher") or {}).get("name", "")),
        cache_file=cache_file)


def lookup(fetcher: Fetcher, doi: str) -> Record:
    """Crossref first; DataCite only when Crossref answers 404."""
    doi = doi.strip().lower()
    q = urllib.parse.quote(doi, safe="")
    r = fetcher.get(CROSSREF_WORKS + q, cache_key(doi, "crossref_"), "json", accept="application/json")
    if r.status == 200:
        return from_crossref(doi, r.json()["message"], 200, r.body_path.name)
    if r.status != 404:
        return Record(doi=doi, registrar="none", status=r.status, cache_file=r.body_path.name)
    d = fetcher.get(DATACITE_DOIS + q, cache_key(doi, "datacite_"), "json", accept="application/json")
    if d.status == 200:
        return from_datacite(doi, d.json()["data"]["attributes"], 200, d.body_path.name)
    return Record(doi=doi, registrar="none", status=404 if d.status == 404 else d.status,
                  cache_file=d.body_path.name)


def search(fetcher: Fetcher, params: dict) -> list[dict]:
    qs = urllib.parse.urlencode(sorted(params.items()))
    r = fetcher.get(CROSSREF_SEARCH + qs, cache_key(qs, "crossref_search_"), "json",
                    accept="application/json")
    if r.status != 200:
        return []
    return r.json()["message"].get("items", [])
