# 53 — A7.5 SnO₂ condition: Mom 2014's stoichiometric rows are cus-site — CONFIRMED, 2026-08-23

**Registered condition** (docs/43:1415-1417, deposited with A7, 10.5281/zenodo.21963144):
"SnO₂ may be admitted as a declared control-stratum member only if Mom 2014's
stoichiometric rows are confirmed cus-site by Sep 1 (Man 2011's reduced-surface SnO₂ row
is bridge-site, with the cus site reported not to bind)."

**Verdict: CONFIRMED**, with one terminology caveat that is the entrant's to read (§4.1).
Verified 2026-08-23 by a three-agent chain (one extractor + two independent adversarial
refuters, each re-obtaining the sources without trusting the prior agent; both returned
NOT REFUTED — one with a 14/14 verbatim-quote check, one with an exhaustive site-term
sweep of the full text). Run wf_68b6fa91-041, 4 agents / 111 tool calls; per the standing
rule that AI literature claims get a refute pass before entering the record.

## 1. The paper

- Mom, R. V.; Cheng, J.; Koper, M. T. M.; Sprik, M. "Modeling the Oxygen Evolution
  Reaction on Metal Oxides: The Infuence of Unrestricted DFT Calculations",
  *J. Phys. Chem. C* 2014, 118 (8), 4095–4102. DOI **10.1021/jp409373c**. The missing-l
  "Infuence" typo is in the published title itself (identical in Crossref, OpenAlex
  W2330839297, Semantic Scholar, and the live ACS page). Author order verified from
  Crossref — the repo note "Mom/Cheng/Koper/Sprik" (round-2 synthesis :431) is correct.
  This is Divanis 2020's reference [7].
- **Access:** closed everywhere (OpenAlex oa_status=closed, no repository fulltext; the
  Leiden repository holds Mom's later OER papers but not this one; Aberdeen Pure is
  metadata-only). Full text was read 2026-08-23 through the entrant's Purdue Libraries
  entitlement on pubs.acs.org. The Supporting Information is free to everyone: ACS
  figshare item 2319313, file 3956950 (`jp409373c_si_001.pdf`, 395,982 bytes, md5
  `8b1c0a6ee0380410d018e76aefaf7ae3`, matching figshare's own checksum). Filed at
  `docs/research/papers/Mom-2014_JPCC_unrestricted-DFT-OER-oxides_SI.pdf`. A duplicate of
  the same free SI file auto-saved to the entrant's `Downloads/jp409373c_si_001.pdf`
  during the browser session (left in place).
- **Stack:** CP2K/Quickstep, PBE, GTH pseudopotentials, GPW with 280 Ry density cutoff —
  NOT this project's QE stack. Any numeric anchor use crosses codes.

## 2. What the paper computes

Ten surfaces. Rutile (110), 4×2 cell, 5 trilayers: SnO₂, reduced SnO₂ ("SnO₂ red."),
TiO₂, PbO₂, PtO₂. Rock salt (100), 3×3, 7 layers: MgO, CdO. Perovskite (100), B-cation
termination: SrTiO₃, BaTiO₃, NaTaO₃. Stoichiometric SnO₂ and reduced SnO₂ are two
separate materials rows everywhere they appear (main-text Tables 1 and 3; SI Tables
S1–S4). OER intermediates *OH / *O / *OOH; restricted vs unrestricted DFT is the paper's
subject.

## 3. The decisive text

Methods, the paragraph immediately after Figure 2 — verified verbatim on the live ACS
full text by all three agents independently:

> "Two adsorbates per unit cell were used in all calculations. For rutile and rock salt
> surfaces, the adsorbates were placed on both sides of the slabs, at the vacant sites on
> top of metal atoms. Exception to this was reduced SnO₂, for which the bridge site is
> more favorable."

and Methods, paragraph 1, final sentences:

> "Except for reduced SnO₂, all surfaces were stoichiometric. For reduced SnO₂, the
> bridging oxygen atoms were removed from the top and bottom layers of the slab."

So the stoichiometric "SnO₂" rows are on-top-of-metal-atom adsorption, and the ONLY
bridge-site assignment in the entire paper belongs to the reduced surface (regex sweep
over the retrieved full text: no other site assignment exists). On stoichiometric rutile
(110) the bridging oxygens are present — the paper removes them only to construct the
reduced surface — so the only metal atoms with a *vacant* on-top site are the
5-fold-coordinated rows: the cus site. This matches, from the opposite direction, Man
2011's statement that the SnO₂ bridge data belong to the reduced/nonstoichiometric
surface.

## 4. Caveats — all three are part of the record

### 4.1 The word "cus" never appears; the entrant reads the condition

The literal tokens "cus", "coordinatively unsaturated", and "5-fold" appear nowhere in
the article or SI (exhaustive sweep; the two regex hits on "cus" are substrings of
"discuss"/"focus"). The confirmation rests on the explicit methods statement PLUS a
zero-degrees-of-freedom crystallographic identity (on stoichiometric rutile (110) the
vacant on-top metal site is uniquely the 5f/cus row). If A7.5's "confirmed cus-site" is
read as requiring the literal word, the honest classification drops to
AMBIGUOUS-leaning-confirmed. The quotes in §3 let the entrant make that call; the AI
classification (CONFIRMED_CUS) is disclosed as an AI classification.

### 4.2 Binding at the stoichiometric SnO₂ cus site is robust only in unrestricted DFT

Man 2011 reports the cus site does not bind on SnO₂. Mom 2014 has converged adsorbed
states on stoichiometric SnO₂ in every dataset — but in the RESTRICTED-DFT set the
ΔE_O / ΔE_OOH values (5.22 / 4.92 eV, SI Table S1) sit essentially at the gas-phase
reference values (5.24 / 4.91 eV per SI eqs S1–S3), i.e. near-zero binding; in
unrestricted DFT the derived binding energies are ≈ −1.31 (*OH) / −0.80 (*O) /
−0.52 (*OOH) eV (2-adsorbate set; agent arithmetic from the SI equations + Table S2 —
DERIVED numbers, not printed in the paper). Consequence for any future SnO₂ deck design:
the round-2 warning (docs/research/2026-08-15-lit-sweep-round2-synthesis.md:109) that a
cus-site pair on SnO₂ could be "a difference between two non-binding geometries" is
answered only for spin-polarized calculations — an nspin=1 SnO₂ protocol would sit in
exactly the weak-binding regime Mom's restricted numbers show. SnO₂ is d¹⁰; this needs a
deliberate nspin choice at deck time, not an inherited default.

### 4.3 Adjacent-fact tension, recorded but not resolved here

Mom's Results compares BOTH its stoichiometric SnO₂ and its reduced SnO₂ against Man
et al. data ("acceptable mean absolute difference of 0.25 eV" over five oxides). That
coexists awkwardly with the repo's premise (round-2 synthesis :109, quoting Man's Figure
5b) that Man's own SnO₂ rows are reduced-surface bridge-site only. Nothing in this
verification depends on resolving it; it is recorded so nobody later treats the two
papers' SnO₂ columns as same-site comparable without checking which Man rows Mom used.

## 5. What this does and does not do

- The Sep 1 leg of A7.5 is **DISCHARGED** — both preconditions now hold: the pseudo
  capability PASS (gate (i), 1.188 meV/atom, job 20094699, banked 2026-08-23) and this
  cus-site confirmation.
- It does **NOT** admit SnO₂. Admission is a separate registered declaration by the
  entrant ("declared control-stratum member" that "never enters a headline rate", per the
  round-2 basis A7.5 encodes), naturally taken inside A8/A10. That decision now has no
  open dependency.
- No registered rule, threshold, or verdict changed. §4.1 is the one open reading and it
  belongs to the entrant.

Record updates in this commit: this file; the SI PDF filed on disk under
docs/research/papers/ and indexed in its README (PDFs are gitignored there by
convention — the durable provenance is the figshare id + md5 above, re-fetchable by
anyone);
runs/s0/i_cutoff_ladder/README.md §A7.5; runs/s0/i_cutoff_ladder/manifest.json
admission field; docs/45 §E S0 row; tasks/todo.md.
