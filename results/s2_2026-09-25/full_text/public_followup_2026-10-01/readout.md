# Public-only SI follow-up — 2026-10-01

One additional eligibility gap is settled: **S19909 is ELIGIBLE** under existing
v5 D4, with `eta_form=relative` and `eta_derivation=equivalent`. Current totals:
172 ELIGIBLE, 105 NEEDS_SI, 116 UNRESOLVED. The SI download checklist is 162
records, priorities 69/38/48/7, with 17 D10 checks.

## Recovered evidence and scientific decision

The [public Europe PMC OA package](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10410748/supplementaryFiles)
contains the complete 51-page S19909 SI. Its exact filename and MD5 match the
article's supplementary-media metadata; title and five authors match the
visually inspected cover. The article DOI is 10.1073/pnas.2306835120.
`s19909_recovery.json` records source/file hashes, completeness, correction and
visual coverage. Reading copies remain local.

Two independent GPT-6 Luna readers covered the complete main, all SI pages,
and the [separate correction](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11441541/fullTextXML).
Their blind primary-only rows remain in `s19909_pass{1,2}_primary.out.jsonl`.
Both initially referred the unnamed phase/card to reconciliation. Existing C05
already verifies PDF88-2348 as rutile-type Sb-substituted SnO2; the main explicitly
connects characterized electrodes to the corresponding models. Both readers
checked that connection independently, without another identity search.

The initial E6 disagreement concerned assignment to a common potential. A
focused Fig.5D check resolved it; the reader revised the objection, rather than
root silently changing the output. The final independent rows agree on all
criteria, disposition and eligibility fields. Exact fragment checks prompted
the pass2 reader to correct the quoted SI species order; the original and
quote-checked outputs remain separate, with no new independent read counted.
Root checked the complete main
and SI plus the decisive source visuals: cover, main Fig.5D, SI pp.7,26,27,42.

The authors compare the OER RDS barriers for Cu-Sb-SnO2 and Sb-SnO2. Fig.5D shows
all adjacent-intermediate levels for each surface at the same documented U=0
and1.23 V vs SHE, T=298.15 K. The *OH→*O increment is the largest rise for both
surfaces at each common potential, and the stated Cu/Sb ranking agrees with the
curves. The blue *O→*OOH rise is smaller, not downhill. SI Text S13 identifies
conventional one-electron OER steps and the same surfaces. This is an
author-reported **relative equivalent** under D4, not a new numerical eta.
No curve digitization, step subtraction or experimental-potential conversion
was used. The 2.87 V experimental OER potential in SI Table S4 is not counted.

The correction concerns Cu-state/Raman and probe-description wording, not the
computed model or OER free-energy comparison. Some superseded wording persists
in the deposited main XML; the original and separate correction remain distinct.

## Other exact-record outcomes

`repository_outcomes.json` distinguishes actual attachment checks from unresolved
discovery:

- S14704: NSF PAR accepted manuscript only, no verified new SI/Table S6.
- S11549: laboratory repository main article only, no verified new SI.
- S23244: matching Bicocca item has no associated files; not proof of SI absence.
- S22690: no matching repository attachment found in two focused queries.
- S13316: public package contains 17 main-figure images, no SI document. Its
  NEEDS_SI decision remains unchanged; a successful package request is not SI recovery.
- S11392: promising journal-version lead is **existing S13010**, whose SI reads
  are complete. Crossref's relation is empty and no authoritative pairwise link
  was verified. No duplicate read, new paper count or version collapse.

Access boundaries remain intact: initial PMC browser checks met reCAPTCHA and
stopped; Europe PMC documentation-page opens met403; one ACS supplementary
check met403 and publisher checks stopped. No challenge bypass, institutional
login, Purdue/proxy route or keyed publisher API. Public OA REST endpoints used
the documented retrieval route, without credentials. No paid OpenAI request in
this phase; the prior pilot ledger and control report remain byte-identical.

## Verification and preservation

- Only S19909 changes in the 2,496-record current state; all v3/v4 fields remain
  unchanged. Old recovery rulings and completed SI-round reads remain intact.
- The dated verifier checks 119 immutable pinned files, all recovery input/output
  identities, file hashes, every assessed excerpt, row enums/disposition, exact
  ruling-to-state agreement, and retained checklist contents, not just IDs.
- Recovery read paths must resolve within the evidence root and resolve to
  distinct files. A dated additive ruling layer leaves the previous layer intact.
- 26 regression tests pass. Dated recovery and completed-round verifiers report
  zero errors. All 109 historical raw outputs, 104 required third reads, 130
  audit targets and 21 triaged questions remain verified.
- Two complete independent reads are new in this phase; the dated report's six
  reads include four earlier completed recovery reads reused for verification,
  not repeated screening.

Seven entrant policy choices remain unadopted. Inclusion freeze and method coding
remain open. Missing access is never an exclusion. The next public-source work
is distinct exact-record repository/SI discovery, skipping completed routes and
reads; a blocked institutional route does not pause that work.
