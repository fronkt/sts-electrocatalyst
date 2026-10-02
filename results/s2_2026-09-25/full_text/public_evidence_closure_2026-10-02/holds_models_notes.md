# Targeted holds: new public-source routes

Scope was limited to distinct public author or journal evidence for the four
existing holds. No full article or SI was reread, no eligibility field changed,
no author was contacted, and no publisher challenge or access denial was
bypassed. Exact queries, URLs, identity checks, and route outcomes are retained
in `holds_models_routes.json`.

## Correction — authoritative disposition

Both Nature MOESM4 peer-review PDFs are duplicates already cached locally as
SI4, not new leads or bytes. S25856 is tagged at `text_si/S25856.txt:1266` as
`41467_2025_60083_MOESM4_ESM.pdf`; S26411 is tagged at
`text_si/S26411.txt:779` as `41467_2025_62036_MOESM4_ESM.pdf`. The S25856
10 MiB web-reader limit only blocked a repeat fetch; it is not missing local
evidence. S26411's cached content was included in historical SI material, and
checking it here is not a new independent read. Neither file supplies new
phase or coordinate evidence. Both authoritative lead classes are
`DUPLICATE_ALREADY_CACHED_SI4`; `new_leads` is empty and
`new_downloads` is zero. The initial “new primary-source lead”
classifications are retained in `holds_models_routes.json` under
`overall.correction_history`.

## Route findings

- **S24821 — DOI 10.1002/advs.202409249.** Exact DOI and title searches for
  repository data, a preprint, and the RuO2-200 DFT facet returned the same
  PMC/publisher article and its existing SI package. The official Wiley page
  and PMC record agree on article identity. No distinct dataset, author
  manuscript, correction, or review response surfaced. These routes do not
  supply the missing explicit OER facet or conventional CHE/common-reference
  statement. They are duplicate access routes, not new scientific evidence.

- **S25024 — DOI 10.1002/adma.202417374.** Searches targeted repository or
  author-manuscript copies and the identity of the RuO2@COF-O(3) DFT model.
  PubMed identifies PMID 39901501 / PMCID PMC11923516; the other returned page
  is the already recovered Wiley paper. No distinct dataset, correction, or
  review response surfaced. The existing reviewed package still does not
  establish that the rutile(110) AIMD model is also the static OER profile
  model, or give the conventional CHE/common-reference conditions required by
  the hold. PMC/PubMed are alternate routes to the same publication, not
  independent clarification.

- **S25856 — DOI 10.1038/s41467-025-60083-y.** Nature's DOI-matched article
  page exposes a transparent peer-review PDF, a genuinely distinct primary
  source route. The official attachment fetch returned a web-reader error
  because its content length exceeds 10 MiB. I stopped there. No alternate
  attachment route was guessed and no challenge was bypassed. Searches of the
  exact DOI with `author response`, `reviewer`, `FCC`, `rutile`, and `correction`
  did not surface a clarification. The peer-review file contents remain
  uninspected, so this lead cannot resolve the conflicting labels. The
  Crossmark page identifies the record as current but does not itself explain
  the phase discrepancy.

- **S26411 — DOI 10.1038/s41467-025-62036-x.** Nature's official, publicly
  readable 20-page transparent peer-review file is distinct primary evidence.
  It records a reviewer requesting the optimized CONTCAR in the SI and the
  authors saying they addressed the request. It contains no explicit model
  polymorph statement; targeted text searches for `rutile` and `facet` returned
  no matches. The same DOI's PMC article states that the DFT dopants were
  introduced into optimized RuO2(110) facets and lists the known coordinate
  SI file. This repeats the article/model description and points back to the
  already byte-verified SI3, not to a new complete coordinate artifact. The
  108-declared/53-row gate remains unresolved. I did not re-download SI3 or
  infer the 55 missing rows or a phase from the (110) surface label.

## Disposition

There are two distinct review-file leads: S25856's official file is presently
unreadable through the web reader's size ceiling, and S26411's accessible file
only explains the already known SI deposit history. The S24821 and S25024
searches returned duplicate article/SI access routes. All four holds remain
unresolved. Failed or duplicate routes are access/discovery outcomes, not
evidence that a file or clarification does not exist. No eligibility changes,
downloads, paid API calls, or coordinate reconstruction occurred.
