# READOUT — CENSUS-2 (model ensemble) and CENSUS-3 (seeds 3-29) of the site-integrity census (docs/91) with the rank-resolution readout (docs/research/2026-09-06-rank-resolution-spec.md): the complete readout of 2026-09-13T03:35:47+00:00 (2026-09-13)

> **Reviewed 2026-09-13:** See the [scientific review and errata](research/census-review-2026-09-13.md). The five T1 tables understate declared coverage: each gated composition has 30 decorations / 120 total sites, and coverage is complete. Bootstrap depth and numerical results are correct. The original automated report and all rank outputs are preserved; directory references, cost and rank interpretations are qualified in the review.

> **CALIBRATION READOUT OF AN UNREGISTERED PROTOCOL. NOT A REGISTERED ARM.** docs/91 is not a docs/43 amendment and
> nothing in it is registered (`docs/91:3`); this readout is descriptive, labelled CALIBRATION under `docs/43:3447-3455`,
> and **scores no docs/43 prediction, registers no THRESHOLD, widens no pre-stated bar, fills no entrant slot, moves
> `results/r4_melt_list.json` nowhere and validates, ranks or certifies no electrode** (`docs/91:63`, `:90`). Every value
> docs/91 marks **Proposed** is reported below as Proposed beside its blank slot in the docs/92 form
> `[CENSUS-<n> 2026-09-__: ____]`, and every elective rank-resolution setting beside its blank `[RANK-<n> ...: ______]` slot; no slot is filled here.
> Blind boundary: commit `818409c`, 2026-09-07T03:26:32Z (`docs/91:14`; the rank-resolution readout carries the same pair, spec:5, asserted).
> Readout stamp: `generated` **2026-09-13T03:35:47+00:00** (`readout/ranking.json`; the same stamp on `reproduction.json`, `distribution.json`, `per_site.json`), `partial: false`:
> **103 manifests read, 0 listed missing** (; `ranking.json` `missing[].reason`);
> `o2_records_supplied: true` with `o2_fragment/o2_records.json` sha256_lf `20721f24a1c37d87e6dd4c1bae545626c9dbcb2c2dc03683b9ed06ec74a6cb60` (equal to `docs/94:131`, asserted); `scores_docs43_prediction: false`.
> Landed by arm (stems of `manifests_read` under the stem grammar of `site_census_plan.py:73-91`; arm sizes are the stem counts of `MANIFESTS.sha256`, equal to `docs/91:67`, asserted): CENSUS-1 12/12 (`mpa0__`), ENDMEMBER-2x2 1/1,
> **CENSUS-2: 36/36 landed (omat0 12/12, mp0 12/12, matpes 12/12)**, **CENSUS-3: 54/54** (`mpa0_ext__`); live `.lock` files in `results/` at emit time (names only, `docs/91:73`): none.
> "Landed" throughout this file means present in `manifests_read` at the readout stamp; the `results/` and `logs/` listings are read at emit time. Result files on disk at emit time that are neither in `manifests_read` nor beside a `.lock` (name, `status` and `results[].seconds` read from the file; they enter no count, sum or table of this file): none.
> omat0: landed in full (12/12).
> mp0: landed in full (12/12).
> matpes: landed in full (12/12).
> CENSUS-3: landed in full (54/54).
> docs/93 is the CENSUS-1 readout of record (its `readout/` stamp 2026-09-07T20:13:00+00:00, `docs/93:11`) and docs/94 the CENSUS-1b readout; this file re-reads the same twelve `mpa0__` results and the endmember (hashes equal `docs/93:228-240`, asserted) only for the per-model comparisons and the 120-site set, and re-derives no (a)/(d) verdict of docs/93; where a docs/93 verdict is restated below it is cited to docs/93 and asserted equal.
> Where a reading below is not pre-stated in `docs/91:52-69` or spec:41-92 it is marked **post-hoc** and changes no verdict.
> Rank resolution: `--admit all`: `status complete`, `B` 10000, `seed` 0, coverage expected 60 / present 66 / missing 0, deficient none; `--admit no-desorbed`: `status complete`, `B` 10000, `seed` 0, coverage expected 60 / present 66 / missing 0, deficient none; `--admit intact`: `status complete`, `B` 10000, `seed` 0, coverage expected 60 / present 66 / missing 0, deficient none; `--admit adsorbate-intact`: `status complete`, `B` 10000, `seed` 0, coverage expected 60 / present 66 / missing 0, deficient none; `--admit two-pathway`: `status complete`, `B` 10000, `seed` 0, coverage expected 60 / present 66 / missing 0, deficient none.
> spec:45 fixes the command of record at `--B 10000 --seed 0`; these files carry `B` = 10000, 10000, 10000, 10000, 10000; a file with `B` below 10000 is a dry run of the same code and not the readout of record.

## Verdict against what was pre-stated (`docs/91:52-69`; spec:41-92)

- **(b) INTEGRITY, per model** (`readout/per_site.csv`, rows `arm == CENSUS-2`, `tag == <tag>`, gated six; per-model fractions post-hoc). Over the 72 omat0 sites of the gated six the OOH endpoint reads DESORPTION 18, NORMAL 48, DISSOCIATION 5, MIGRATION 0, RECONSTRUCTION 1; OOH H_TRANSFERRED on 23/72 = 0.3194; INTACT 36 sites, ADSORBATE-INTACT 47; unconverged sites 3; over the 72 mp0 sites of the gated six the OOH endpoint reads DESORPTION 42, NORMAL 29, DISSOCIATION 1, MIGRATION 0, RECONSTRUCTION 0; OOH H_TRANSFERRED on 42/72 = 0.5833; INTACT 21 sites, ADSORBATE-INTACT 27; unconverged sites 1; over the 72 matpes sites of the gated six the OOH endpoint reads DESORPTION 10, NORMAL 48, DISSOCIATION 13, MIGRATION 0, RECONSTRUCTION 1; OOH H_TRANSFERRED on 18/72 = 0.2500; INTACT 37 sites, ADSORBATE-INTACT 49; unconverged sites 5. MPA-0 120-site set (`arm in (CENSUS-1, CENSUS-3)`, `tag mpa0`, gated six): 720 sites landed of 720; OOH DESORPTION 551, NORMAL 119, DISSOCIATION 48, MIGRATION 0, RECONSTRUCTION 2; INTACT 72, ADSORBATE-INTACT 109.
- **(c) RANKING.** banked: banked order, tau-a 1.0; intact_only: EXCLUDED Ni31Cr29Cu5Mn35, Cu26Ni9Cr31Co33, tau not reported (`complete: false`); adsorbate_intact_only: order differs from banked, tau-a 0.7333333333333333; two_pathway: banked order, tau-a 1.0 (`readout/ranking.json` `orders`). Ensemble spread (max − min of the models' min-site eta, `ranking.ensemble_spread.<f>.spread_V`, `n_models` in parentheses): Ni31Cr29Cu5Mn35 0.13661152833791412 (4), Fe25Co25Ni25Cr25 0.5518500778007338 (4), Cu26Ni9Cr31Co33 0.08414900960531035 (4), Ni34Fe6Cu29Co31 0.27448169029545344 (4), Cu8Cr23Mn35Co34 0.37418173698063306 (4), Cu22Fe30Co32Mn15 0.27474975561355475 (4) for the gated six; the column is complete only at `n_models` 4. The per-model distributions behind these minima are in (c′) below (post-hoc).
- **(d) DECISIVE SITE per model (post-hoc extension of `docs/91:65`).** Under mpa0 the leader's winner is seed 1 / site 0 / Cr, eta 0.4399960638886986 V, OOH INTACT, O-O 1.3797783290461472 A = OOH_LIKE, hydrogen ON_ADSORBATE, pathway cus, `unconverged_states` 0 (`docs/93:24`, restated from `reproduction.json` `decisive_site` and the same site's `per_site.csv` row); under omat0 it is seed 2 / site 2 / Cr, eta 0.5766075922266127 V, OOH NORMAL, NOT the same (seed, site) as the mpa0 winner; under mp0 it is seed 1 / site 2 / Cr, eta 0.46160080294844175 V, OOH DESORPTION, NOT the same (seed, site) as the mpa0 winner; under matpes it is seed 0 / site 0 / Cr, eta 0.4483130168751339 V, OOH NORMAL, NOT the same (seed, site) as the mpa0 winner (section (d) below).
- **(e) COST.** 103 landed manifests: candidate seconds sum 1744845.943 s = 484.68 h; per checkpoint mean: mpa0 (CENSUS-1) 18126.3 s, omat0 11097.4 s (0.61x the CENSUS-1 mean), mp0 13558.5 s (0.75x the CENSUS-1 mean), matpes 10422.8 s (0.58x the CENSUS-1 mean), mpa0_ext 20400.5 s (1.13x); log-stamp wall, first launch → last exit line 2026-09-07T03:28:35Z → 2026-09-13T03:35:24Z = 144.11 h and 3.36 candidate-seconds per wall-second (post-hoc arithmetic on `results/<stem>_result.json` `results[].seconds` and `logs/<stem>.log` stamps, in place of the pre-stated `status.json` runner wall, which this file does not open; section (e)).
- **(f) DISTRIBUTION.** 120 sites per gated composition; sample sd (V): Ni31Cr29Cu5Mn35 0.23544011681940277, Fe25Co25Ni25Cr25 0.276953080072374, Cu26Ni9Cr31Co33 0.22873300125420917, Ni34Fe6Cu29Co31 0.2533764079411902, Cu8Cr23Mn35Co34 0.2271542401856481, Cu22Fe30Co32Mn15 0.21482872715592694; the descriptive placement against the `docs/91:44` spreads is in section (f).
- **Rank resolution.** `--admit all`: status `complete`, resolved boundaries min/median/p10/mean = 2/2/2/2 of 5 (`resolved_boundaries`); inverted = 2/2/3/2 (`inverted_boundaries`); secondary policies: no-desorbed: `complete`, deficient none; intact: `complete`, deficient none; adsorbate-intact: `complete`, deficient none; two-pathway: `complete`, deficient none; `--compare`: 11 of 20 POLICY-DEPENDENT.

## (b) INTEGRITY per model — counts per category, per state, per composition (`readout/per_site.csv`; thresholds `reproduction.json thresholds`)

Thresholds as applied (`readout/reproduction.json` `thresholds`): bound < 2.2 A, desorbed >= 3.0 A (INHERITED, `docs/33:317-322`, `src/hea_oer/data.py:20`); O-O bands O2_LIKE <= 1.28, SUPEROXO_LIKE <= 1.36, OOH_LIKE <= 1.6 A, OO_CLEAVED above — Proposed `[CENSUS-2 2026-09-__: ____]`; hydrogen window 1.15 A — Proposed `[CENSUS-3 2026-09-__: ____]`; reconstruction per-atom 0.5 A — Proposed `[CENSUS-4 2026-09-__: ____]`; label priority DESORPTION > DISSOCIATION > MIGRATION > RECONSTRUCTION > NORMAL — Proposed `[CENSUS-5 2026-09-__: ____]` (`docs/91:55-58`, as `docs/93:73`).

What is reported, `docs/91:61` verbatim: "- Reported: per state, per site, per composition, per model, the counts of each category, of INTACT and ADSORBATE-INTACT sites, of unconverged states and sites, of weak-tier states and of reconstruction flags; the fraction of the 144 CENSUS-1 sites whose OOH is H-TRANSFERRED; and, per composition, whether the banked winner's site is INTACT and ADSORBATE-INTACT."

The per-state level of `docs/91:61` is delegated to `readout/per_site.csv` (one row per site; the same rows as `per_site.json` `rows[]`): the per-state columns are `OH_m_o_A`, `OH_tier`, `OH_h_location`, `OH_category`, `O_m_o_A`, `O_tier`, `O_category`, `OOH_m_o_A`, `OOH_tier`, `OOH_o_o_A`, `OOH_o_o_class`, `OOH_h_location`, `OOH_h_carrier`, `OOH_binding_O`, `OOH_binding_metal`, `OOH_category`, `OOH_slab_rms_A`, `OOH_slab_max_A` — `<S>_m_o_A` is the tiering distance of the nearest adsorbate oxygen to its metal, `OOH_slab_rms_A` the RMS displacement over the free slab atoms and `OOH_slab_max_A` the largest single free-atom displacement of `docs/91:58`; the site-level columns are `manifest`, `arm`, `tag`, `formula`, `candidate_status`, `seed`, `site_index`, `initial_metal`, `eta_V`, `pls`, `dG_OH`, `dG_O`, `dG_OOH`, `unconverged_states`, `weak_states`, `reconstructed_states`, `pathway`, `all_states_intact`, `all_states_adsorbate_intact`. The second O-metal distance of `docs/91:55` and the fixed-atom displacement of `docs/91:58` are not columns of the readout files (no column of `per_site.csv` names either) and are not reprinted here.

Rows with `candidate_status == evaluated` and an empty `eta_V` (kept in every integrity count, left out of every minimum and eta arithmetic, printed as "no eta"): none.

**Table B1 — totals per model over the gated six** (rows `arm in (CENSUS-1, CENSUS-2)`, `tag == <model>`, `formula` in the gated six, `candidate_status == evaluated`; categories from `<S>_category`, tiers from `<S>_tier`):

| model | n sites | state | NORMAL | DESORPTION | DISSOCIATION | MIGRATION | RECONSTRUCTION | tier bound / weak / desorbed |
|---|---|---|---|---|---|---|---|---|
| mpa0 | 72 | *OH | 65 | 0 | 0 | 1 | 6 | 71 / 1 / 0 |
| mpa0 | 72 | *O | 37 | 9 | 0 | 1 | 25 | 60 / 3 / 9 |
| mpa0 | 72 | *OOH | 15 | 51 | 5 | 0 | 1 | 10 / 11 / 51 |
| omat0 | 72 | *OH | 67 | 0 | 0 | 0 | 5 | 72 / 0 / 0 |
| omat0 | 72 | *O | 52 | 1 | 0 | 1 | 18 | 70 / 1 / 1 |
| omat0 | 72 | *OOH | 48 | 18 | 5 | 0 | 1 | 50 / 4 / 18 |
| mp0 | 72 | *OH | 62 | 0 | 0 | 0 | 10 | 72 / 0 / 0 |
| mp0 | 72 | *O | 51 | 4 | 0 | 0 | 17 | 68 / 0 / 4 |
| mp0 | 72 | *OOH | 29 | 42 | 1 | 0 | 0 | 29 / 1 / 42 |
| matpes | 72 | *OH | 71 | 0 | 0 | 0 | 1 | 72 / 0 / 0 |
| matpes | 72 | *O | 56 | 0 | 0 | 0 | 16 | 72 / 0 / 0 |
| matpes | 72 | *OOH | 48 | 10 | 13 | 0 | 1 | 49 / 13 / 10 |

Per model over every landed site of that model (arms CENSUS-1 and CENSUS-2, all landed compositions; the mpa0 fraction over 144 is the `docs/91:61` statement, every other fraction is post-hoc):

- **mpa0** (144 sites, 12 manifests): OOH hydrogen H_TRANSFERRED on **115 of 144 sites = 0.7986** (`docs/93:22`); ON_ADSORBATE 29, H_FREE 0. OOH O-O band: O2_LIKE 114, SUPEROXO_LIKE 25, OOH_LIKE 5, OO_CLEAVED 0. Pathway: cus 27, bridge 13, undefined 104. Sites INTACT **17**, ADSORBATE-INTACT **23**; unconverged states 8 on 8 sites (`unconverged_states`); weak-tier states 31 on 26 sites (`weak_states`); reconstruction flags 102 states on 76 sites (`reconstructed_states`). OH hydrogen ON_ADSORBATE on 144 of 144 (`OH_h_location`).
- **omat0** (144 sites, 12 manifests): OOH hydrogen H_TRANSFERRED on 46 of 144 sites = 0.3194 (post-hoc; 144 sites landed); ON_ADSORBATE 98, H_FREE 0. OOH O-O band: O2_LIKE 46, SUPEROXO_LIKE 7, OOH_LIKE 91, OO_CLEAVED 0. Pathway: cus 95, bridge 10, undefined 39. Sites INTACT **75**, ADSORBATE-INTACT **91**; unconverged states 3 on 3 sites (`unconverged_states`); weak-tier states 10 on 10 sites (`weak_states`); reconstruction flags 39 states on 30 sites (`reconstructed_states`). OH hydrogen ON_ADSORBATE on 144 of 144 (`OH_h_location`).
- **mp0** (144 sites, 12 manifests): OOH hydrogen H_TRANSFERRED on 84 of 144 sites = 0.5833 (post-hoc; 144 sites landed); ON_ADSORBATE 60, H_FREE 0. OOH O-O band: O2_LIKE 84, SUPEROXO_LIKE 9, OOH_LIKE 51, OO_CLEAVED 0. Pathway: cus 56, bridge 1, undefined 87. Sites INTACT **44**, ADSORBATE-INTACT **51**; unconverged states 2 on 2 sites (`unconverged_states`); weak-tier states 2 on 2 sites (`weak_states`); reconstruction flags 49 states on 33 sites (`reconstructed_states`). OH hydrogen ON_ADSORBATE on 144 of 144 (`OH_h_location`).
- **matpes** (144 sites, 12 manifests): OOH hydrogen H_TRANSFERRED on 37 of 144 sites = 0.2569 (post-hoc; 144 sites landed); ON_ADSORBATE 104, H_FREE 3. OOH O-O band: O2_LIKE 44, SUPEROXO_LIKE 10, OOH_LIKE 90, OO_CLEAVED 0. Pathway: cus 96, bridge 25, undefined 23. Sites INTACT **74**, ADSORBATE-INTACT **96**; unconverged states 7 on 7 sites (`unconverged_states`); weak-tier states 23 on 23 sites (`weak_states`); reconstruction flags 42 states on 34 sites (`reconstructed_states`). OH hydrogen ON_ADSORBATE on 144 of 144 (`OH_h_location`).

**Table B2 — per composition x model, gated six** (columns as `docs/93:88`; the winner is the min-`eta_V` site of `per_site.csv` for that (tag, formula) and its flags are `all_states_intact` / `all_states_adsorbate_intact` — for the mpa0 rows that is the banked winner of `docs/91:61`, for every other model it is the census min-site row, post-hoc; site counts cross-checked against `ranking.json` `convergence.per_formula.<f>.<tag>`, asserted):

| composition | model | OOH N/D/X/M/R | O N/D/X/M/R | OH N/D/X/M/R | H_TRANSF | INTACT | ADS-INTACT | cus/bridge/undef | unconv states / sites | weak states | recon states | winner (seed/site/metal, eta V) | winner OOH (category, o_o_class, h_location) | winner INTACT / ADS-INTACT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | mpa0 | 2/9/1/0/0 | 4/3/0/0/5 | 11/0/0/1/0 | 9 | 0 | 2 | 2/1/9 | 0 / 0 | 2 | 7 | 1/0/Cr, 0.4399960638886986 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Ni31Cr29Cu5Mn35 | omat0 | 11/1/0/0/0 | 6/1/0/0/5 | 12/0/0/0/0 | 1 | 5 | 9 | 11/0/1 | 1 / 1 | 0 | 6 | 2/2/Cr, 0.5766075922266127 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Ni31Cr29Cu5Mn35 | mp0 | 4/8/0/0/0 | 6/1/0/0/5 | 10/0/0/0/2 | 7 | 4 | 4 | 4/0/8 | 0 / 0 | 0 | 9 | 1/2/Cr, 0.46160080294844175 | DESORPTION (O2_LIKE, H_TRANSFERRED) | no / no |
| Ni31Cr29Cu5Mn35 | matpes | 9/0/3/0/0 | 6/0/0/0/6 | 12/0/0/0/0 | 3 | 4 | 9 | 9/3/0 | 0 / 0 | 3 | 6 | 0/0/Cr, 0.4483130168751339 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Fe25Co25Ni25Cr25 | mpa0 | 4/7/1/0/0 | 10/0/0/0/2 | 11/0/0/0/1 | 8 | 3 | 4 | 4/1/7 | 0 / 0 | 2 | 4 | 2/0/Cr, 0.4530565522419163 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Fe25Co25Ni25Cr25 | omat0 | 7/5/0/0/0 | 11/0/0/0/1 | 12/0/0/0/0 | 5 | 6 | 7 | 7/0/5 | 1 / 1 | 0 | 1 | 2/0/Cr, 0.6915009330926596 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Fe25Co25Ni25Cr25 | mp0 | 2/10/0/0/0 | 11/0/0/0/1 | 12/0/0/0/0 | 10 | 2 | 2 | 2/0/10 | 0 / 0 | 0 | 1 | 1/0/Co, 0.9022344882710467 | DESORPTION (O2_LIKE, H_TRANSFERRED) | no / no |
| Fe25Co25Ni25Cr25 | matpes | 9/1/2/0/0 | 11/0/0/0/1 | 12/0/0/0/0 | 3 | 8 | 9 | 9/2/1 | 1 / 1 | 2 | 1 | 2/0/Cr, 0.3503844104703129 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Cu26Ni9Cr31Co33 | mpa0 | 1/10/0/0/1 | 2/1/0/1/8 | 9/0/0/0/3 | 10 | 0 | 1 | 2/0/10 | 0 / 0 | 2 | 19 | 1/0/Cr, 0.4791918879560475 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Cu26Ni9Cr31Co33 | omat0 | 4/5/2/0/1 | 3/0/0/0/9 | 7/0/0/0/5 | 7 | 1 | 5 | 5/2/5 | 0 / 0 | 1 | 17 | 2/2/Cr, 0.5121988465266036 | RECONSTRUCTION (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Cu26Ni9Cr31Co33 | mp0 | 9/3/0/0/0 | 5/1/0/0/6 | 9/0/0/0/3 | 3 | 4 | 7 | 9/0/3 | 1 / 1 | 0 | 10 | 1/0/Cr, 0.4572539172497043 | DESORPTION (O2_LIKE, H_TRANSFERRED) | no / no |
| Cu26Ni9Cr31Co33 | matpes | 3/6/2/0/1 | 7/0/0/0/5 | 11/0/0/0/1 | 3 | 1 | 4 | 4/2/6 | 4 / 4 | 2 | 12 | 1/2/Cr, 0.5414029268550147 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Ni34Fe6Cu29Co31 | mpa0 | 2/9/1/0/0 | 6/3/0/0/3 | 12/0/0/0/0 | 10 | 2 | 2 | 2/1/9 | 1 / 1 | 3 | 6 | 2/3/Ni, 0.7258416589359067 | DISSOCIATION (O2_LIKE, H_TRANSFERRED) | no / no |
| Ni34Fe6Cu29Co31 | omat0 | 6/4/2/0/0 | 11/0/0/1/0 | 12/0/0/0/0 | 6 | 6 | 6 | 6/2/4 | 1 / 1 | 3 | 1 | 2/3/Ni, 0.7128337563325617 | DESORPTION (O2_LIKE, H_TRANSFERRED) | no / no |
| Ni34Fe6Cu29Co31 | mp0 | 3/9/0/0/0 | 10/2/0/0/0 | 12/0/0/0/0 | 9 | 3 | 3 | 3/0/9 | 0 / 0 | 0 | 2 | 0/3/Co, 0.9873154466280152 | DESORPTION (O2_LIKE, H_TRANSFERRED) | no / no |
| Ni34Fe6Cu29Co31 | matpes | 9/1/2/0/0 | 12/0/0/0/0 | 12/0/0/0/0 | 3 | 9 | 9 | 9/2/1 | 0 / 0 | 2 | 0 | 1/0/Fe, 0.764198298107444 | NORMAL (OOH_LIKE, ON_ADSORBATE) | INTACT / yes |
| Cu8Cr23Mn35Co34 | mpa0 | 1/9/2/0/0 | 9/0/0/0/3 | 12/0/0/0/0 | 11 | 1 | 1 | 1/2/9 | 0 / 0 | 2 | 3 | 2/1/Co, 0.7557679417210732 | NORMAL (OOH_LIKE, ON_ADSORBATE) | INTACT / yes |
| Cu8Cr23Mn35Co34 | omat0 | 11/1/0/0/0 | 9/0/0/0/3 | 12/0/0/0/0 | 1 | 9 | 11 | 11/0/1 | 0 / 0 | 0 | 3 | 2/3/Cr, 0.4769722746170424 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Cu8Cr23Mn35Co34 | mp0 | 7/4/1/0/0 | 9/0/0/0/3 | 9/0/0/0/3 | 5 | 5 | 7 | 7/1/4 | 0 / 0 | 1 | 6 | 2/1/Co, 0.8363970071222182 | NORMAL (OOH_LIKE, ON_ADSORBATE) | INTACT / yes |
| Cu8Cr23Mn35Co34 | matpes | 9/0/3/0/0 | 8/0/0/0/4 | 12/0/0/0/0 | 3 | 6 | 9 | 9/3/0 | 0 / 0 | 3 | 4 | 0/1/Cr, 0.46221527014158514 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Cu22Fe30Co32Mn15 | mpa0 | 5/7/0/0/0 | 6/2/0/0/4 | 10/0/0/0/2 | 7 | 3 | 5 | 5/0/7 | 2 / 2 | 4 | 8 | 0/0/Co, 0.7956531821512538 | NORMAL (SUPEROXO_LIKE, ON_ADSORBATE) | no / yes |
| Cu22Fe30Co32Mn15 | omat0 | 9/2/1/0/0 | 12/0/0/0/0 | 12/0/0/0/0 | 3 | 9 | 9 | 9/1/2 | 0 / 0 | 1 | 0 | 1/3/Co, 0.7824106890637879 | NORMAL (OOH_LIKE, ON_ADSORBATE) | INTACT / yes |
| Cu22Fe30Co32Mn15 | mp0 | 4/8/0/0/0 | 10/0/0/0/2 | 10/0/0/0/2 | 8 | 3 | 4 | 4/0/8 | 0 / 0 | 0 | 4 | 1/3/Co, 0.934320589166175 | NORMAL (OOH_LIKE, ON_ADSORBATE) | INTACT / yes |
| Cu22Fe30Co32Mn15 | matpes | 9/2/1/0/0 | 12/0/0/0/0 | 12/0/0/0/0 | 3 | 9 | 9 | 9/1/2 | 0 / 0 | 1 | 0 | 1/2/Fe, 0.6595708335526203 | NORMAL (OOH_LIKE, ON_ADSORBATE) | INTACT / yes |

**Table B2 (other six compositions)** — the tags that have landed them (CENSUS-2 covers twelve, `docs/91:38`); the mpa0 rows are `docs/93:96-101` and are not reprinted:

| composition | model | OOH N/D/X/M/R | O N/D/X/M/R | OH N/D/X/M/R | H_TRANSF | INTACT | ADS-INTACT | cus/bridge/undef | unconv states / sites | weak states | recon states | winner (seed/site/metal, eta V) | winner OOH (category, o_o_class, h_location) | winner INTACT / ADS-INTACT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cr33Co5Ni29Cu33 | omat0 | 9/3/0/0/0 | 7/2/0/0/3 | 9/0/0/0/3 | 2 | 5 | 8 | 9/0/3 | 0 / 0 | 0 | 8 | 2/3/Cr, 0.5875500753086769 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Cr33Co5Ni29Cu33 | mp0 | 6/6/0/0/0 | 7/1/0/0/4 | 9/0/0/0/3 | 5 | 4 | 5 | 6/0/6 | 0 / 0 | 1 | 11 | 0/2/Cr, 0.7821676713976897 | DESORPTION (O2_LIKE, H_TRANSFERRED) | no / no |
| Cr33Co5Ni29Cu33 | matpes | 3/5/2/0/2 | 7/0/0/0/5 | 9/0/0/0/3 | 3 | 2 | 5 | 5/2/5 | 2 / 2 | 1 | 12 | 0/2/Cr, 0.1528846513813571 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Mn31Ni31Co33Cu6 | omat0 | 8/2/2/0/0 | 12/0/0/0/0 | 12/0/0/0/0 | 4 | 8 | 8 | 8/2/2 | 0 / 0 | 2 | 0 | 2/1/Co, 0.8357995710311386 | NORMAL (OOH_LIKE, ON_ADSORBATE) | INTACT / yes |
| Mn31Ni31Co33Cu6 | mp0 | 2/10/0/0/0 | 12/0/0/0/0 | 12/0/0/0/0 | 10 | 2 | 2 | 2/0/10 | 0 / 0 | 0 | 0 | 1/1/Mn, 1.0017444153347537 | DESORPTION (O2_LIKE, H_TRANSFERRED) | no / no |
| Mn31Ni31Co33Cu6 | matpes | 10/0/2/0/0 | 12/0/0/0/0 | 12/0/0/0/0 | 2 | 10 | 10 | 10/2/0 | 0 / 0 | 2 | 0 | 2/1/Co, 0.9482817552551657 | NORMAL (OOH_LIKE, ON_ADSORBATE) | INTACT / yes |
| Fe31Cu25Cr13Ni31 | omat0 | 6/5/1/0/0 | 11/0/0/0/1 | 12/0/0/0/0 | 6 | 5 | 6 | 6/1/5 | 0 / 0 | 1 | 1 | 1/3/Cr, 0.7371467865463801 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Fe31Cu25Cr13Ni31 | mp0 | 6/6/0/0/0 | 9/2/0/0/1 | 12/0/0/0/0 | 5 | 4 | 4 | 6/0/6 | 0 / 0 | 0 | 3 | 1/1/Fe, 1.0933257730468267 | NORMAL (OOH_LIKE, ON_ADSORBATE) | INTACT / yes |
| Fe31Cu25Cr13Ni31 | matpes | 5/5/2/0/0 | 11/0/0/0/1 | 12/0/0/0/0 | 5 | 4 | 5 | 5/2/5 | 0 / 0 | 2 | 1 | 1/3/Cr, 0.3334729857099754 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Mn34Cu7Fe33Cr27 | omat0 | 8/3/1/0/0 | 11/0/0/0/1 | 12/0/0/0/0 | 2 | 7 | 8 | 8/1/3 | 0 / 0 | 1 | 1 | 2/0/Cr, 0.7618964711276321 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Mn34Cu7Fe33Cr27 | mp0 | 6/6/0/0/0 | 11/0/0/0/1 | 11/0/0/0/1 | 5 | 6 | 6 | 6/0/6 | 0 / 0 | 0 | 2 | 0/1/Mn, 0.9976474473711345 | DESORPTION (O2_LIKE, H_TRANSFERRED) | no / no |
| Mn34Cu7Fe33Cr27 | matpes | 8/1/3/0/0 | 10/0/0/0/2 | 12/0/0/0/0 | 4 | 6 | 8 | 8/3/1 | 0 / 0 | 2 | 2 | 2/0/Cr, 0.3679492415189296 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Co5Cu33Ni28Mn34 | omat0 | 12/0/0/0/0 | 12/0/0/0/0 | 12/0/0/0/0 | 0 | 12 | 12 | 12/0/0 | 0 / 0 | 0 | 0 | 1/1/Co, 0.8881492702465339 | NORMAL (OOH_LIKE, ON_ADSORBATE) | INTACT / yes |
| Co5Cu33Ni28Mn34 | mp0 | 7/5/0/0/0 | 11/1/0/0/0 | 12/0/0/0/0 | 5 | 7 | 7 | 7/0/5 | 1 / 1 | 0 | 1 | 1/1/Co, 0.981240977035652 | DESORPTION (O2_LIKE, H_TRANSFERRED) | no / no |
| Co5Cu33Ni28Mn34 | matpes | 11/1/0/0/0 | 9/0/0/0/3 | 12/0/0/0/0 | 1 | 8 | 11 | 11/0/1 | 0 / 0 | 0 | 3 | 2/1/Mn, 0.746428894783107 | NORMAL (OOH_LIKE, ON_ADSORBATE) | no / yes |
| Ni34Fe29Mn30Co7 | omat0 | 3/8/1/0/0 | 11/1/0/0/0 | 12/0/0/0/0 | 9 | 2 | 2 | 3/1/8 | 0 / 0 | 1 | 1 | 0/1/Ni, 1.1034307066303697 | DISSOCIATION (O2_LIKE, H_TRANSFERRED) | no / no |
| Ni34Fe29Mn30Co7 | mp0 | 0/12/0/0/0 | 12/0/0/0/0 | 12/0/0/0/0 | 12 | 0 | 0 | 0/0/12 | 0 / 0 | 0 | 0 | 2/1/Mn, 1.042341134052367 | DESORPTION (O2_LIKE, H_TRANSFERRED) | no / no |
| Ni34Fe29Mn30Co7 | matpes | 8/1/3/0/0 | 11/0/0/0/1 | 12/0/0/0/0 | 4 | 7 | 8 | 8/3/1 | 0 / 0 | 3 | 1 | 2/2/Fe, 0.6516787612295181 | NORMAL (OOH_LIKE, ON_ADSORBATE) | INTACT / yes |

**Table B3 — the MPA-0 120-site set (CENSUS-1 + CENSUS-3), gated six** (rows `tag == mpa0`, `arm in (CENSUS-1, CENSUS-3)`; manifests landed = distinct `manifest` values, asserted equal to `distribution.json` `per_formula.<f>.manifests`):

| composition | manifests landed (of 10) | n sites (of 120) | OOH N/D/X/M/R | O N/D/X/M/R | OH N/D/X/M/R | H_TRANSF (n, fraction) | INTACT | ADS-INTACT | cus/bridge/undef | unconv states / sites | weak states | recon states |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 10 | 120 | 8/87/25/0/0 | 48/17/0/9/46 | 109/0/0/1/10 | 109, 0.9083 | 3 | 8 | 8/25/87 | 3 / 3 | 35 | 71 |
| Fe25Co25Ni25Cr25 | 10 | 120 | 22/88/10/0/0 | 65/7/0/1/47 | 95/0/0/0/25 | 84, 0.7000 | 11 | 19 | 22/10/88 | 6 / 5 | 15 | 94 |
| Cu26Ni9Cr31Co33 | 10 | 120 | 12/104/2/0/2 | 54/17/0/2/47 | 101/0/0/1/18 | 99, 0.8250 | 6 | 13 | 14/2/104 | 3 / 3 | 8 | 113 |
| Ni34Fe6Cu29Co31 | 10 | 120 | 19/94/7/0/0 | 52/52/0/1/15 | 120/0/0/0/0 | 101, 0.8417 | 15 | 15 | 19/7/94 | 5 / 5 | 13 | 68 |
| Cu8Cr23Mn35Co34 | 10 | 120 | 18/100/2/0/0 | 80/3/0/1/36 | 117/0/0/1/2 | 101, 0.8417 | 4 | 16 | 18/2/100 | 3 / 3 | 4 | 42 |
| Cu22Fe30Co32Mn15 | 10 | 120 | 40/78/2/0/0 | 88/16/0/0/16 | 117/0/0/0/3 | 79, 0.6583 | 33 | 38 | 40/2/78 | 5 / 5 | 14 | 35 |

Post-hoc sub-table per seed block (`manifest` = `mpa0_ext__<f>__sNN-NN`), same counts:

| composition | manifest | n sites | OOH N/D/X/M/R | O N/D/X/M/R | OH N/D/X/M/R | H_TRANSF (n, fraction) | INTACT | ADS-INTACT | cus/bridge/undef | unconv states / sites | weak states | recon states |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | `mpa0_ext__Ni31Cr29Cu5Mn35__s03-05` | 12 | 1/8/3/0/0 | 7/1/0/0/4 | 11/0/0/0/1 | 10, 0.8333 | 0 | 1 | 1/3/8 | 0 / 0 | 3 | 8 |
| Ni31Cr29Cu5Mn35 | `mpa0_ext__Ni31Cr29Cu5Mn35__s06-08` | 12 | 1/5/6/0/0 | 6/2/0/2/2 | 11/0/0/0/1 | 11, 0.9167 | 1 | 1 | 1/6/5 | 0 / 0 | 8 | 6 |
| Ni31Cr29Cu5Mn35 | `mpa0_ext__Ni31Cr29Cu5Mn35__s09-11` | 12 | 1/9/2/0/0 | 6/0/0/1/5 | 12/0/0/0/0 | 11, 0.9167 | 0 | 1 | 1/2/9 | 1 / 1 | 3 | 6 |
| Ni31Cr29Cu5Mn35 | `mpa0_ext__Ni31Cr29Cu5Mn35__s12-14` | 12 | 1/8/3/0/0 | 7/1/0/0/4 | 12/0/0/0/0 | 11, 0.9167 | 1 | 1 | 1/3/8 | 1 / 1 | 3 | 4 |
| Ni31Cr29Cu5Mn35 | `mpa0_ext__Ni31Cr29Cu5Mn35__s15-17` | 12 | 0/9/3/0/0 | 2/2/0/2/6 | 11/0/0/0/1 | 12, 1.0000 | 0 | 0 | 0/3/9 | 0 / 0 | 5 | 7 |
| Ni31Cr29Cu5Mn35 | `mpa0_ext__Ni31Cr29Cu5Mn35__s18-20` | 12 | 0/11/1/0/0 | 3/4/0/1/4 | 9/0/0/0/3 | 12, 1.0000 | 0 | 0 | 0/1/11 | 0 / 0 | 2 | 9 |
| Ni31Cr29Cu5Mn35 | `mpa0_ext__Ni31Cr29Cu5Mn35__s21-23` | 12 | 0/10/2/0/0 | 5/2/0/0/5 | 10/0/0/0/2 | 12, 1.0000 | 0 | 0 | 0/2/10 | 0 / 0 | 2 | 9 |
| Ni31Cr29Cu5Mn35 | `mpa0_ext__Ni31Cr29Cu5Mn35__s24-26` | 12 | 1/8/3/0/0 | 5/1/0/0/6 | 12/0/0/0/0 | 10, 0.8333 | 0 | 1 | 1/3/8 | 0 / 0 | 3 | 7 |
| Ni31Cr29Cu5Mn35 | `mpa0_ext__Ni31Cr29Cu5Mn35__s27-29` | 12 | 1/10/1/0/0 | 3/1/0/3/5 | 10/0/0/0/2 | 11, 0.9167 | 1 | 1 | 1/1/10 | 1 / 1 | 4 | 8 |
| Fe25Co25Ni25Cr25 | `mpa0_ext__Fe25Co25Ni25Cr25__s03-05` | 12 | 2/8/2/0/0 | 6/1/0/1/4 | 9/0/0/0/3 | 9, 0.7500 | 1 | 2 | 2/2/8 | 2 / 1 | 3 | 13 |
| Fe25Co25Ni25Cr25 | `mpa0_ext__Fe25Co25Ni25Cr25__s06-08` | 12 | 5/6/1/0/0 | 7/0/0/0/5 | 11/0/0/0/1 | 5, 0.4167 | 3 | 4 | 5/1/6 | 2 / 2 | 2 | 6 |
| Fe25Co25Ni25Cr25 | `mpa0_ext__Fe25Co25Ni25Cr25__s09-11` | 12 | 0/11/1/0/0 | 1/3/0/0/8 | 4/0/0/0/8 | 9, 0.7500 | 0 | 0 | 0/1/11 | 0 / 0 | 1 | 23 |
| Fe25Co25Ni25Cr25 | `mpa0_ext__Fe25Co25Ni25Cr25__s12-14` | 12 | 2/8/2/0/0 | 9/0/0/0/3 | 12/0/0/0/0 | 9, 0.7500 | 0 | 2 | 2/2/8 | 1 / 1 | 2 | 3 |
| Fe25Co25Ni25Cr25 | `mpa0_ext__Fe25Co25Ni25Cr25__s15-17` | 12 | 3/9/0/0/0 | 5/2/0/0/5 | 10/0/0/0/2 | 9, 0.7500 | 3 | 3 | 3/0/9 | 0 / 0 | 0 | 10 |
| Fe25Co25Ni25Cr25 | `mpa0_ext__Fe25Co25Ni25Cr25__s18-20` | 12 | 0/12/0/0/0 | 7/0/0/0/5 | 10/0/0/0/2 | 11, 0.9167 | 0 | 0 | 0/0/12 | 0 / 0 | 0 | 7 |
| Fe25Co25Ni25Cr25 | `mpa0_ext__Fe25Co25Ni25Cr25__s21-23` | 12 | 1/10/1/0/0 | 5/0/0/0/7 | 11/0/0/0/1 | 8, 0.6667 | 0 | 0 | 1/1/10 | 1 / 1 | 1 | 8 |
| Fe25Co25Ni25Cr25 | `mpa0_ext__Fe25Co25Ni25Cr25__s24-26` | 12 | 4/7/1/0/0 | 8/1/0/0/3 | 11/0/0/0/1 | 8, 0.6667 | 0 | 3 | 4/1/7 | 0 / 0 | 1 | 6 |
| Fe25Co25Ni25Cr25 | `mpa0_ext__Fe25Co25Ni25Cr25__s27-29` | 12 | 1/10/1/0/0 | 7/0/0/0/5 | 6/0/0/0/6 | 8, 0.6667 | 1 | 1 | 1/1/10 | 0 / 0 | 3 | 14 |
| Cu26Ni9Cr31Co33 | `mpa0_ext__Cu26Ni9Cr31Co33__s03-05` | 12 | 1/10/1/0/0 | 8/0/0/1/3 | 12/0/0/0/0 | 11, 0.9167 | 0 | 1 | 1/1/10 | 1 / 1 | 2 | 6 |
| Cu26Ni9Cr31Co33 | `mpa0_ext__Cu26Ni9Cr31Co33__s06-08` | 12 | 1/11/0/0/0 | 6/3/0/0/3 | 11/0/0/0/1 | 11, 0.9167 | 1 | 1 | 1/0/11 | 0 / 0 | 0 | 8 |
| Cu26Ni9Cr31Co33 | `mpa0_ext__Cu26Ni9Cr31Co33__s09-11` | 12 | 2/9/0/0/1 | 6/3/0/0/3 | 8/0/0/1/3 | 9, 0.7500 | 0 | 3 | 3/0/9 | 0 / 0 | 2 | 16 |
| Cu26Ni9Cr31Co33 | `mpa0_ext__Cu26Ni9Cr31Co33__s12-14` | 12 | 0/12/0/0/0 | 7/1/0/0/4 | 12/0/0/0/0 | 11, 0.9167 | 0 | 0 | 0/0/12 | 0 / 0 | 0 | 7 |
| Cu26Ni9Cr31Co33 | `mpa0_ext__Cu26Ni9Cr31Co33__s15-17` | 12 | 2/9/1/0/0 | 5/4/0/0/3 | 11/0/0/0/1 | 10, 0.8333 | 2 | 2 | 2/1/9 | 0 / 0 | 1 | 12 |
| Cu26Ni9Cr31Co33 | `mpa0_ext__Cu26Ni9Cr31Co33__s18-20` | 12 | 0/12/0/0/0 | 3/1/0/0/8 | 11/0/0/0/1 | 10, 0.8333 | 0 | 0 | 0/0/12 | 0 / 0 | 0 | 11 |
| Cu26Ni9Cr31Co33 | `mpa0_ext__Cu26Ni9Cr31Co33__s21-23` | 12 | 1/11/0/0/0 | 4/3/0/0/5 | 6/0/0/0/6 | 10, 0.8333 | 0 | 1 | 1/0/11 | 1 / 1 | 0 | 19 |
| Cu26Ni9Cr31Co33 | `mpa0_ext__Cu26Ni9Cr31Co33__s24-26` | 12 | 3/9/0/0/0 | 6/1/0/0/5 | 10/0/0/0/2 | 7, 0.5833 | 3 | 3 | 3/0/9 | 1 / 1 | 1 | 9 |
| Cu26Ni9Cr31Co33 | `mpa0_ext__Cu26Ni9Cr31Co33__s27-29` | 12 | 1/11/0/0/0 | 7/0/0/0/5 | 11/0/0/0/1 | 10, 0.8333 | 0 | 1 | 1/0/11 | 0 / 0 | 0 | 6 |
| Ni34Fe6Cu29Co31 | `mpa0_ext__Ni34Fe6Cu29Co31__s03-05` | 12 | 0/12/0/0/0 | 3/6/0/0/3 | 12/0/0/0/0 | 12, 1.0000 | 0 | 0 | 0/0/12 | 0 / 0 | 1 | 9 |
| Ni34Fe6Cu29Co31 | `mpa0_ext__Ni34Fe6Cu29Co31__s06-08` | 12 | 1/10/1/0/0 | 2/7/0/0/3 | 12/0/0/0/0 | 11, 0.9167 | 0 | 0 | 1/1/10 | 2 / 2 | 2 | 10 |
| Ni34Fe6Cu29Co31 | `mpa0_ext__Ni34Fe6Cu29Co31__s09-11` | 12 | 3/9/0/0/0 | 6/6/0/0/0 | 12/0/0/0/0 | 9, 0.7500 | 2 | 2 | 3/0/9 | 0 / 0 | 0 | 6 |
| Ni34Fe6Cu29Co31 | `mpa0_ext__Ni34Fe6Cu29Co31__s12-14` | 12 | 4/7/1/0/0 | 5/4/0/0/3 | 12/0/0/0/0 | 8, 0.6667 | 3 | 3 | 4/1/7 | 0 / 0 | 2 | 7 |
| Ni34Fe6Cu29Co31 | `mpa0_ext__Ni34Fe6Cu29Co31__s15-17` | 12 | 2/9/1/0/0 | 5/6/0/0/1 | 12/0/0/0/0 | 10, 0.8333 | 2 | 2 | 2/1/9 | 0 / 0 | 1 | 7 |
| Ni34Fe6Cu29Co31 | `mpa0_ext__Ni34Fe6Cu29Co31__s18-20` | 12 | 1/10/1/0/0 | 6/5/0/1/0 | 12/0/0/0/0 | 11, 0.9167 | 1 | 1 | 1/1/10 | 0 / 0 | 2 | 6 |
| Ni34Fe6Cu29Co31 | `mpa0_ext__Ni34Fe6Cu29Co31__s21-23` | 12 | 3/9/0/0/0 | 7/5/0/0/0 | 12/0/0/0/0 | 9, 0.7500 | 2 | 2 | 3/0/9 | 0 / 0 | 0 | 5 |
| Ni34Fe6Cu29Co31 | `mpa0_ext__Ni34Fe6Cu29Co31__s24-26` | 12 | 0/11/1/0/0 | 5/5/0/0/2 | 12/0/0/0/0 | 12, 1.0000 | 0 | 0 | 0/1/11 | 2 / 2 | 1 | 7 |
| Ni34Fe6Cu29Co31 | `mpa0_ext__Ni34Fe6Cu29Co31__s27-29` | 12 | 3/8/1/0/0 | 7/5/0/0/0 | 12/0/0/0/0 | 9, 0.7500 | 3 | 3 | 3/1/8 | 0 / 0 | 1 | 5 |
| Cu8Cr23Mn35Co34 | `mpa0_ext__Cu8Cr23Mn35Co34__s03-05` | 12 | 2/10/0/0/0 | 5/0/0/1/6 | 12/0/0/0/0 | 10, 0.8333 | 2 | 2 | 2/0/10 | 1 / 1 | 1 | 7 |
| Cu8Cr23Mn35Co34 | `mpa0_ext__Cu8Cr23Mn35Co34__s06-08` | 12 | 1/11/0/0/0 | 8/0/0/0/4 | 12/0/0/0/0 | 11, 0.9167 | 0 | 1 | 1/0/11 | 1 / 1 | 0 | 4 |
| Cu8Cr23Mn35Co34 | `mpa0_ext__Cu8Cr23Mn35Co34__s09-11` | 12 | 2/10/0/0/0 | 10/0/0/0/2 | 11/0/0/1/0 | 10, 0.8333 | 0 | 0 | 2/0/10 | 1 / 1 | 1 | 2 |
| Cu8Cr23Mn35Co34 | `mpa0_ext__Cu8Cr23Mn35Co34__s12-14` | 12 | 2/10/0/0/0 | 7/1/0/0/4 | 10/0/0/0/2 | 10, 0.8333 | 0 | 2 | 2/0/10 | 0 / 0 | 0 | 7 |
| Cu8Cr23Mn35Co34 | `mpa0_ext__Cu8Cr23Mn35Co34__s15-17` | 12 | 1/11/0/0/0 | 8/1/0/0/3 | 12/0/0/0/0 | 10, 0.8333 | 0 | 1 | 1/0/11 | 0 / 0 | 0 | 4 |
| Cu8Cr23Mn35Co34 | `mpa0_ext__Cu8Cr23Mn35Co34__s18-20` | 12 | 3/9/0/0/0 | 7/0/0/0/5 | 12/0/0/0/0 | 9, 0.7500 | 0 | 3 | 3/0/9 | 0 / 0 | 0 | 5 |
| Cu8Cr23Mn35Co34 | `mpa0_ext__Cu8Cr23Mn35Co34__s21-23` | 12 | 1/11/0/0/0 | 10/0/0/0/2 | 12/0/0/0/0 | 11, 0.9167 | 0 | 1 | 1/0/11 | 0 / 0 | 0 | 2 |
| Cu8Cr23Mn35Co34 | `mpa0_ext__Cu8Cr23Mn35Co34__s24-26` | 12 | 1/11/0/0/0 | 8/1/0/0/3 | 12/0/0/0/0 | 11, 0.9167 | 0 | 1 | 1/0/11 | 0 / 0 | 0 | 4 |
| Cu8Cr23Mn35Co34 | `mpa0_ext__Cu8Cr23Mn35Co34__s27-29` | 12 | 4/8/0/0/0 | 8/0/0/0/4 | 12/0/0/0/0 | 8, 0.6667 | 1 | 4 | 4/0/8 | 0 / 0 | 0 | 4 |
| Cu22Fe30Co32Mn15 | `mpa0_ext__Cu22Fe30Co32Mn15__s03-05` | 12 | 3/8/1/0/0 | 9/0/0/0/3 | 12/0/0/0/0 | 9, 0.7500 | 3 | 3 | 3/1/8 | 0 / 0 | 3 | 3 |
| Cu22Fe30Co32Mn15 | `mpa0_ext__Cu22Fe30Co32Mn15__s06-08` | 12 | 4/8/0/0/0 | 9/3/0/0/0 | 12/0/0/0/0 | 8, 0.6667 | 4 | 4 | 4/0/8 | 0 / 0 | 1 | 3 |
| Cu22Fe30Co32Mn15 | `mpa0_ext__Cu22Fe30Co32Mn15__s09-11` | 12 | 2/10/0/0/0 | 11/1/0/0/0 | 12/0/0/0/0 | 10, 0.8333 | 2 | 2 | 2/0/10 | 0 / 0 | 0 | 1 |
| Cu22Fe30Co32Mn15 | `mpa0_ext__Cu22Fe30Co32Mn15__s12-14` | 12 | 8/4/0/0/0 | 12/0/0/0/0 | 12/0/0/0/0 | 4, 0.3333 | 8 | 8 | 8/0/4 | 0 / 0 | 0 | 0 |
| Cu22Fe30Co32Mn15 | `mpa0_ext__Cu22Fe30Co32Mn15__s15-17` | 12 | 2/10/0/0/0 | 10/1/0/0/1 | 12/0/0/0/0 | 9, 0.7500 | 2 | 2 | 2/0/10 | 2 / 2 | 1 | 2 |
| Cu22Fe30Co32Mn15 | `mpa0_ext__Cu22Fe30Co32Mn15__s18-20` | 12 | 5/7/0/0/0 | 6/3/0/0/3 | 12/0/0/0/0 | 7, 0.5833 | 3 | 4 | 5/0/7 | 0 / 0 | 1 | 6 |
| Cu22Fe30Co32Mn15 | `mpa0_ext__Cu22Fe30Co32Mn15__s21-23` | 12 | 1/11/0/0/0 | 10/1/0/0/1 | 12/0/0/0/0 | 11, 0.9167 | 1 | 1 | 1/0/11 | 1 / 1 | 1 | 2 |
| Cu22Fe30Co32Mn15 | `mpa0_ext__Cu22Fe30Co32Mn15__s24-26` | 12 | 6/6/0/0/0 | 7/3/0/0/2 | 12/0/0/0/0 | 6, 0.5000 | 4 | 5 | 6/0/6 | 0 / 0 | 1 | 5 |
| Cu22Fe30Co32Mn15 | `mpa0_ext__Cu22Fe30Co32Mn15__s27-29` | 12 | 4/7/1/0/0 | 8/2/0/0/2 | 11/0/0/0/1 | 8, 0.6667 | 3 | 4 | 4/1/7 | 0 / 0 | 2 | 5 |

**Banked winner status per model** (`docs/91:61` last clause; banked `seed` / `site_metal` from `r4_gated.json` `rows[].bonds`). For mpa0 the winner row is `reproduction.json` `reproduction.<f>.winner` with `winner_site_intact` / `winner_site_adsorbate_intact` (docs/93 readout (a)); for the other models `reproduction.json` carries no entry (`site_census_readout.py:139` restricts (a) to CENSUS-1, and `docs/91:80`: "The three other checkpoints carry no historical claim at all"), so their row is the census min-site row of that model beside whether its (seed, site_index) equals the mpa0 winner's — post-hoc:

| composition | banked seed / metal | model | site(s) with that seed and `initial_metal` == banked metal: seed/site_index, eta_V, INTACT, ADS-INTACT | winner or min-site row: seed/site_index/metal, eta_V, INTACT / ADS-INTACT | same (seed, site) as mpa0 winner |
|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 1 / Cr | mpa0 | 1/0, 0.4399960638886986, False, True; 1/2, 0.4945995053835457, False, True; 1/3, 1.4147997253705862, False, False | 1/0/Cr, 0.4399960638886986, no / yes (`reproduction.json`, REPRODUCED) | — (reference) |
| Ni31Cr29Cu5Mn35 | 1 / Cr | omat0 | 1/0, 0.7462145715236561, False, True; 1/2, 0.6621899293671349, False, False; 1/3, 0.8809935406969389, False, True | 2/2/Cr, 0.5766075922266127, no / yes (census min-site row, post-hoc) | no |
| Ni31Cr29Cu5Mn35 | 1 / Cr | mp0 | 1/0, 0.5293929098039483, False, False; 1/2, 0.46160080294844175, False, False; 1/3, 1.1459822425623996, False, False | 1/2/Cr, 0.46160080294844175, no / no (census min-site row, post-hoc) | no |
| Ni31Cr29Cu5Mn35 | 1 / Cr | matpes | 1/0, 0.5727018240266242, False, True; 1/2, 0.5505108332959461, False, True; 1/3, 0.7131885643189415, False, True | 0/0/Cr, 0.4483130168751339, no / yes (census min-site row, post-hoc) | no |
| Fe25Co25Ni25Cr25 | 2 / Cr | mpa0 | 2/0, 0.4530565522419163, False, True | 2/0/Cr, 0.4530565522419163, no / yes (`reproduction.json`, REPRODUCED) | — (reference) |
| Fe25Co25Ni25Cr25 | 2 / Cr | omat0 | 2/0, 0.6915009330926596, False, True | 2/0/Cr, 0.6915009330926596, no / yes (census min-site row, post-hoc) | yes |
| Fe25Co25Ni25Cr25 | 2 / Cr | mp0 | 2/0, 1.0163209735342091, False, False | 1/0/Co, 0.9022344882710467, no / no (census min-site row, post-hoc) | no |
| Fe25Co25Ni25Cr25 | 2 / Cr | matpes | 2/0, 0.3503844104703129, False, True | 2/0/Cr, 0.3503844104703129, no / yes (census min-site row, post-hoc) | yes |
| Cu26Ni9Cr31Co33 | 1 / Cr | mpa0 | 1/0, 0.4791918879560475, False, True; 1/2, 0.7137723316313904, False, False; 1/3, 0.6112965884603758, False, False | 1/0/Cr, 0.4791918879560475, no / yes (`reproduction.json`, REPRODUCED) | — (reference) |
| Cu26Ni9Cr31Co33 | 1 / Cr | omat0 | 1/0, 0.5351618934343678, False, True; 1/2, 0.6015169493387882, False, False; 1/3, 0.6663593525016447, False, False | 2/2/Cr, 0.5121988465266036, no / yes (census min-site row, post-hoc) | no |
| Cu26Ni9Cr31Co33 | 1 / Cr | mp0 | 1/0, 0.4572539172497043, False, False; 1/2, 0.6485132199649, False, True; 1/3, 1.1212455602425164, False, True | 1/0/Cr, 0.4572539172497043, no / no (census min-site row, post-hoc) | yes |
| Cu26Ni9Cr31Co33 | 1 / Cr | matpes | 1/0, 0.605862131036063, False, True; 1/2, 0.5414029268550147, False, True; 1/3, 2.1530754707381883, False, False | 1/2/Cr, 0.5414029268550147, no / yes (census min-site row, post-hoc) | no |
| Ni34Fe6Cu29Co31 | 2 / Ni | mpa0 | 2/3, 0.7258416589359067, False, False | 2/3/Ni, 0.7258416589359067, no / no (`reproduction.json`, REPRODUCED) | — (reference) |
| Ni34Fe6Cu29Co31 | 2 / Ni | omat0 | 2/3, 0.7128337563325617, False, False | 2/3/Ni, 0.7128337563325617, no / no (census min-site row, post-hoc) | yes |
| Ni34Fe6Cu29Co31 | 2 / Ni | mp0 | 2/3, 1.168130128582379, True, True | 0/3/Co, 0.9873154466280152, no / no (census min-site row, post-hoc) | no |
| Ni34Fe6Cu29Co31 | 2 / Ni | matpes | 2/3, 1.1689900352699985, True, True | 1/0/Fe, 0.764198298107444, INTACT / yes (census min-site row, post-hoc) | no |
| Cu8Cr23Mn35Co34 | 2 / Co | mpa0 | 2/0, 0.9680595766804156, False, False; 2/1, 0.7557679417210732, True, True | 2/1/Co, 0.7557679417210732, INTACT / yes (`reproduction.json`, REPRODUCED) | — (reference) |
| Cu8Cr23Mn35Co34 | 2 / Co | omat0 | 2/0, 1.0061872684679471, True, True; 2/1, 0.9872067335637595, True, True | 2/3/Cr, 0.4769722746170424, no / yes (census min-site row, post-hoc) | no |
| Cu8Cr23Mn35Co34 | 2 / Co | mp0 | 2/0, 1.0506954158553752, True, True; 2/1, 0.8363970071222182, True, True | 2/1/Co, 0.8363970071222182, INTACT / yes (census min-site row, post-hoc) | yes |
| Cu8Cr23Mn35Co34 | 2 / Co | matpes | 2/0, 0.8246131964402954, True, True; 2/1, 1.74967009534548, False, False | 0/1/Cr, 0.46221527014158514, no / yes (census min-site row, post-hoc) | no |
| Cu22Fe30Co32Mn15 | 0 / Co | mpa0 | 0/0, 0.7956531821512538, False, True; 0/3, 0.9632241904766952, False, False | 0/0/Co, 0.7956531821512538, no / yes (`reproduction.json`, REPRODUCED) | — (reference) |
| Cu22Fe30Co32Mn15 | 0 / Co | omat0 | 0/0, 0.9101383543384642, True, True; 0/3, 0.9069909905280085, False, False | 1/3/Co, 0.7824106890637879, INTACT / yes (census min-site row, post-hoc) | no |
| Cu22Fe30Co32Mn15 | 0 / Co | mp0 | 0/0, 1.0512803005157023, False, False; 0/3, 1.0470196022265439, False, False | 1/3/Co, 0.934320589166175, INTACT / yes (census min-site row, post-hoc) | no |
| Cu22Fe30Co32Mn15 | 0 / Co | matpes | 0/0, 0.9379122919393827, True, True; 0/3, 2.2549230053052023, False, False | 1/2/Fe, 0.6595708335526203, INTACT / yes (census min-site row, post-hoc) | no |

## (c) DESCRIPTOR-DEFINED RANKING of the gated six under the four rules (`readout/ranking.json`)

Site set: the twelve CENSUS-1 sites per composition (seeds 0, 1, 2 x site_index 0..3); every rule is a minimum over its qualifying sites, an extreme-value statistic that is comparable only at equal site count (`ranking.site_set`). Banked order and gaps as pre-stated at `docs/91:63`: `banked_adjacent_gaps` 0.01306048799396553 / 0.026135336045984836 / 0.24664973155099723 / 0.029926322477609624 / 0.03988526123725933 V. The pathway-undefined exclusion of the two-pathway rule is Proposed `[CENSUS-6 2026-09-__: ____]`; the CENSUS-1b diagnostic is supplied (`o2_records_supplied: true`); `per_formula.<f>.o2_fragment_diagnostics.<seed/site>` blocks carry `dG_ads_O2_eV`, `dG_O2_reference_cancelled_eV`, `hb_deprotonation_step_eV`, `o2_release_eV`, `zpe_ts_O2_eV`, `role`; the values equal `docs/94:82-86` (asserted) and change no value (`docs/91:63`).

CENSUS-1b fragment diagnostic beside the bridge sites (`docs/91:63`; rows `tag == mpa0`, `pathway == bridge` of `per_site.csv` against `ranking.per_formula.<f>.o2_fragment_diagnostics.<seed/site>`, key sets asserted equal): Ni31Cr29Cu5Mn35: seed 1 site 1 (Ni, eta 1.3371918852495819 V, OOH DISSOCIATION) `dG_ads_O2_eV` -0.7417308668444551, `role` "diagnostic; enters no ranking rule" | Fe25Co25Ni25Cr25: seed 0 site 2 (Fe, eta 1.5252116739357584 V, OOH DISSOCIATION) `dG_ads_O2_eV` -0.6026081669935575, `role` "diagnostic; enters no ranking rule" | Cu26Ni9Cr31Co33: no bridge site | Ni34Fe6Cu29Co31: seed 2 site 3 (Ni, eta 0.7258416589359067 V, OOH DISSOCIATION) `dG_ads_O2_eV` -0.6148257205044387, `role` "diagnostic; enters no ranking rule" | Cu8Cr23Mn35Co34: seed 0 site 2 (Cr, eta 0.9451884339539456 V, OOH DISSOCIATION) `dG_ads_O2_eV` -0.4097098319308781, `role` "diagnostic; enters no ranking rule"; seed 2 site 0 (Co, eta 0.9680595766804156 V, OOH DISSOCIATION) `dG_ads_O2_eV` -0.5103430071613626, `role` "diagnostic; enters no ranking rule" | Cu22Fe30Co32Mn15: no bridge site.

**Table C1 — per rule** (`ranking.orders.<rule>`; tau printed only when `complete`, `docs/91:63`: "tau is reported only when all six have a value"):

| rule | order (ascending, V) | Kendall tau-a vs banked | adjacent gaps (V) | EXCLUDED (`n_intact_sites` / `n_adsorbate_intact_sites` / `n_pathway_defined_sites` of 12) |
|---|---|---|---|---|
| banked | Ni31Cr29Cu5Mn35 0.4399960638886986 < Fe25Co25Ni25Cr25 0.4530565522419163 < Cu26Ni9Cr31Co33 0.4791918879560475 < Ni34Fe6Cu29Co31 0.7258416589359067 < Cu8Cr23Mn35Co34 0.7557679417210732 < Cu22Fe30Co32Mn15 0.7956531821512538 | 1.0 | 0.013060488353217714 / 0.02613533571413118 / 0.24664977097985918 / 0.029926282785166514 / 0.0398852404301806 | none |
| intact_only | Cu8Cr23Mn35Co34 0.7557679417210732 < Ni34Fe6Cu29Co31 1.0834958748019101 < Cu22Fe30Co32Mn15 1.209540229659778 < Fe25Co25Ni25Cr25 1.2723422287315014 | not reported (`complete: false`) | 0.3277279330808369 / 0.1260443548578678 / 0.06280199907172346 | Ni31Cr29Cu5Mn35 (0 / 2 / 3), Cu26Ni9Cr31Co33 (0 / 1 / 2) |
| adsorbate_intact_only | Ni31Cr29Cu5Mn35 0.4399960638886986 < Fe25Co25Ni25Cr25 0.4530565522419163 < Cu26Ni9Cr31Co33 0.4791918879560475 < Cu8Cr23Mn35Co34 0.7557679417210732 < Cu22Fe30Co32Mn15 0.7956531821512538 < Ni34Fe6Cu29Co31 1.0834958748019101 | 0.7333333333333333 | 0.013060488353217714 / 0.02613533571413118 / 0.2765760537650257 / 0.0398852404301806 / 0.2878426926506563 | none |
| two_pathway | Ni31Cr29Cu5Mn35 0.4399960638886986 < Fe25Co25Ni25Cr25 0.4530565522419163 < Cu26Ni9Cr31Co33 0.4791918879560475 < Ni34Fe6Cu29Co31 0.7258416589359067 < Cu8Cr23Mn35Co34 0.7557679417210732 < Cu22Fe30Co32Mn15 0.7956531821512538 | 1.0 | 0.013060488353217714 / 0.02613533571413118 / 0.24664977097985918 / 0.029926282785166514 / 0.0398852404301806 | none |

The four orders and tau values are unchanged from `docs/93:113-116` (asserted cell by cell; the rule site set is CENSUS-1 only and cannot change).

**Table C2 — per composition, gated six** (`ranking.per_formula`, `ranking.ensemble_spread.<f>.{spread_V, n_models, min_site_eta_by_model_V}`; a spread cell at `n_models` < 4 names the pending tags):

| composition | banked (V) | intact_only | adsorbate_intact_only | two_pathway | n_intact_sites | n_adsorbate_intact_sites | n_pathway_defined_sites | n_bridge_sites | n_undefined_pathway_sites | n_unconverged_sites | n_weak_sites | n_reconstructed_sites | ensemble spread (V) [n_models] | min-site eta by model (V) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.4399960638886986 | EXCLUDED | 0.4399960638886986 | 0.4399960638886986 | 0 | 2 | 3 | 1 | 9 | 0 | 2 | 7 | 0.13661152833791412 [n_models 4] | mpa0 0.4399960638886986, omat0 0.5766075922266127, mp0 0.46160080294844175, matpes 0.4483130168751339 |
| Fe25Co25Ni25Cr25 | 0.4530565522419163 | 1.2723422287315014 | 0.4530565522419163 | 0.4530565522419163 | 3 | 4 | 5 | 1 | 7 | 0 | 2 | 3 | 0.5518500778007338 [n_models 4] | mpa0 0.4530565522419163, omat0 0.6915009330926596, mp0 0.9022344882710467, matpes 0.3503844104703129 |
| Cu26Ni9Cr31Co33 | 0.4791918879560475 | EXCLUDED | 0.4791918879560475 | 0.4791918879560475 | 0 | 1 | 2 | 0 | 10 | 0 | 1 | 11 | 0.08414900960531035 [n_models 4] | mpa0 0.4791918879560475, omat0 0.5121988465266036, mp0 0.4572539172497043, matpes 0.5414029268550147 |
| Ni34Fe6Cu29Co31 | 0.7258416589359067 | 1.0834958748019101 | 1.0834958748019101 | 0.7258416589359067 | 2 | 2 | 3 | 1 | 9 | 1 | 2 | 6 | 0.27448169029545344 [n_models 4] | mpa0 0.7258416589359067, omat0 0.7128337563325617, mp0 0.9873154466280152, matpes 0.764198298107444 |
| Cu8Cr23Mn35Co34 | 0.7557679417210732 | 0.7557679417210732 | 0.7557679417210732 | 0.7557679417210732 | 1 | 1 | 3 | 2 | 9 | 0 | 2 | 3 | 0.37418173698063306 [n_models 4] | mpa0 0.7557679417210732, omat0 0.4769722746170424, mp0 0.8363970071222182, matpes 0.46221527014158514 |
| Cu22Fe30Co32Mn15 | 0.7956531821512538 | 1.209540229659778 | 0.7956531821512538 | 0.7956531821512538 | 3 | 5 | 5 | 0 | 7 | 2 | 4 | 6 | 0.27474975561355475 [n_models 4] | mpa0 0.7956531821512538, omat0 0.7824106890637879, mp0 0.934320589166175, matpes 0.6595708335526203 |

The same table for the other six compositions that carry a CENSUS-2 manifest (the `per_formula` rule values exist only for the gated six):

| composition | ensemble spread (V) [n_models] | min-site eta by model (V) |
|---|---|---|
| Cr33Co5Ni29Cu33 | 0.6292830200163326 [n_models 4] | mpa0 0.5172986131125741, omat0 0.5875500753086769, mp0 0.7821676713976897, matpes 0.1528846513813571 |
| Mn31Ni31Co33Cu6 | 0.3334108831273275 [n_models 4] | mpa0 0.6683335322074262, omat0 0.8357995710311386, mp0 1.0017444153347537, matpes 0.9482817552551657 |
| Fe31Cu25Cr13Ni31 | 0.7598527873368512 [n_models 4] | mpa0 0.6771430805058989, omat0 0.7371467865463801, mp0 1.0933257730468267, matpes 0.3334729857099754 |
| Mn34Cu7Fe33Cr27 | 0.6296982058522049 [n_models 4] | mpa0 0.7363354674562137, omat0 0.7618964711276321, mp0 0.9976474473711345, matpes 0.3679492415189296 |
| Co5Cu33Ni28Mn34 | 0.2364840521330498 [n_models 4] | mpa0 0.7447569249026023, omat0 0.8881492702465339, mp0 0.981240977035652, matpes 0.746428894783107 |
| Ni34Fe29Mn30Co7 | 0.4517519454008516 [n_models 4] | mpa0 0.8720706667688054, omat0 1.1034307066303697, mp0 1.042341134052367, matpes 0.6516787612295181 |

**Table C3 — unconverged sites per composition and per model** (`docs/91:63`: "the unconverged-site counts per composition and per model"; risk 7 `docs/91:85`; `ranking.convergence.per_formula.<f>.<tag>.{n_unconverged_sites, n_sites}`, totals `convergence.per_model`):

| composition | mpa0 n_unconverged / n_sites | omat0 | mp0 | matpes |
|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0 / 12 | 1 / 12 | 0 / 12 | 0 / 12 |
| Fe25Co25Ni25Cr25 | 0 / 12 | 1 / 12 | 0 / 12 | 1 / 12 |
| Cu26Ni9Cr31Co33 | 0 / 12 | 0 / 12 | 1 / 12 | 4 / 12 |
| Ni34Fe6Cu29Co31 | 1 / 12 | 1 / 12 | 0 / 12 | 0 / 12 |
| Cu8Cr23Mn35Co34 | 0 / 12 | 0 / 12 | 0 / 12 | 0 / 12 |
| Cu22Fe30Co32Mn15 | 2 / 12 | 0 / 12 | 0 / 12 | 0 / 12 |
| Cr33Co5Ni29Cu33 | 3 / 12 | 0 / 12 | 0 / 12 | 2 / 12 |
| Mn31Ni31Co33Cu6 | 0 / 12 | 0 / 12 | 0 / 12 | 0 / 12 |
| Fe31Cu25Cr13Ni31 | 0 / 12 | 0 / 12 | 0 / 12 | 0 / 12 |
| Mn34Cu7Fe33Cr27 | 0 / 12 | 0 / 12 | 0 / 12 | 0 / 12 |
| Co5Cu33Ni28Mn34 | 1 / 12 | 0 / 12 | 1 / 12 | 0 / 12 |
| Ni34Fe29Mn30Co7 | 1 / 12 | 0 / 12 | 0 / 12 | 0 / 12 |
| **total** | 8 / 144 | 3 / 144 | 2 / 144 | 7 / 144 |

Whether a model's min-site eta sits on an unconverged site (winner row `unconverged_states > 0` in `per_site.csv`, every landed (tag, formula); the mpa0 entries are the pre-stated reading, the other models' are post-hoc): omat0 Ni34Fe6Cu29Co31 (seed 2 site 3, `unconverged_states` 1). `docs/91:85`: "a composition whose banked minimum sits on an unconverged site is reported with that fact beside the number".

**Table C4 — post-hoc, per-model winner persistence** (min-`eta_V` row of `per_site.csv` per (tag, formula), gated six x landed tags; the last column compares (`seed`, `site_index`) with the mpa0 winner's):

| composition | model | min-site eta (V) | winning seed / site_index | initial metal | OOH binding metal | OOH category | O-O class | H location | pathway | site INTACT / ADS-INTACT | same (seed, site) as mpa0 winner? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | mpa0 | 0.4399960638886986 | 1 / 0 | Cr | Cr | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | no / yes | — |
| Ni31Cr29Cu5Mn35 | omat0 | 0.5766075922266127 | 2 / 2 | Cr | Cr | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | no / yes | no |
| Ni31Cr29Cu5Mn35 | mp0 | 0.46160080294844175 | 1 / 2 | Cr | Cr | DESORPTION | O2_LIKE | H_TRANSFERRED | undefined | no / no | no |
| Ni31Cr29Cu5Mn35 | matpes | 0.4483130168751339 | 0 / 0 | Cr | Cr | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | no / yes | no |
| Fe25Co25Ni25Cr25 | mpa0 | 0.4530565522419163 | 2 / 0 | Cr | Cr | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | no / yes | — |
| Fe25Co25Ni25Cr25 | omat0 | 0.6915009330926596 | 2 / 0 | Cr | Cr | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | no / yes | yes |
| Fe25Co25Ni25Cr25 | mp0 | 0.9022344882710467 | 1 / 0 | Co | Co | DESORPTION | O2_LIKE | H_TRANSFERRED | undefined | no / no | no |
| Fe25Co25Ni25Cr25 | matpes | 0.3503844104703129 | 2 / 0 | Cr | Cr | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | no / yes | yes |
| Cu26Ni9Cr31Co33 | mpa0 | 0.4791918879560475 | 1 / 0 | Cr | Cr | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | no / yes | — |
| Cu26Ni9Cr31Co33 | omat0 | 0.5121988465266036 | 2 / 2 | Cr | Cr | RECONSTRUCTION | OOH_LIKE | ON_ADSORBATE | cus | no / yes | no |
| Cu26Ni9Cr31Co33 | mp0 | 0.4572539172497043 | 1 / 0 | Cr | Cr | DESORPTION | O2_LIKE | H_TRANSFERRED | undefined | no / no | yes |
| Cu26Ni9Cr31Co33 | matpes | 0.5414029268550147 | 1 / 2 | Cr | Cr | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | no / yes | no |
| Ni34Fe6Cu29Co31 | mpa0 | 0.7258416589359067 | 2 / 3 | Ni | Ni | DISSOCIATION | O2_LIKE | H_TRANSFERRED | bridge | no / no | — |
| Ni34Fe6Cu29Co31 | omat0 | 0.7128337563325617 | 2 / 3 | Ni | Ni | DESORPTION | O2_LIKE | H_TRANSFERRED | undefined | no / no | yes |
| Ni34Fe6Cu29Co31 | mp0 | 0.9873154466280152 | 0 / 3 | Co | Co | DESORPTION | O2_LIKE | H_TRANSFERRED | undefined | no / no | no |
| Ni34Fe6Cu29Co31 | matpes | 0.764198298107444 | 1 / 0 | Fe | Fe | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | INTACT / yes | no |
| Cu8Cr23Mn35Co34 | mpa0 | 0.7557679417210732 | 2 / 1 | Co | Co | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | INTACT / yes | — |
| Cu8Cr23Mn35Co34 | omat0 | 0.4769722746170424 | 2 / 3 | Cr | Cr | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | no / yes | no |
| Cu8Cr23Mn35Co34 | mp0 | 0.8363970071222182 | 2 / 1 | Co | Co | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | INTACT / yes | yes |
| Cu8Cr23Mn35Co34 | matpes | 0.46221527014158514 | 0 / 1 | Cr | Cr | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | no / yes | no |
| Cu22Fe30Co32Mn15 | mpa0 | 0.7956531821512538 | 0 / 0 | Co | Co | NORMAL | SUPEROXO_LIKE | ON_ADSORBATE | cus | no / yes | — |
| Cu22Fe30Co32Mn15 | omat0 | 0.7824106890637879 | 1 / 3 | Co | Co | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | INTACT / yes | no |
| Cu22Fe30Co32Mn15 | mp0 | 0.934320589166175 | 1 / 3 | Co | Co | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | INTACT / yes | no |
| Cu22Fe30Co32Mn15 | matpes | 0.6595708335526203 | 1 / 2 | Fe | Fe | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | INTACT / yes | no |

Post-hoc: omat0 keeps the mpa0 winning site in 2 of its 6 landed gated compositions; mp0 keeps the mpa0 winning site in 2 of its 6 landed gated compositions; matpes keeps the mpa0 winning site in 1 of its 6 landed gated compositions. Per-model orders of `min_site_eta_by_model_V` with Kendall tau-a against `banked_order`, computed by this script only when all six are present for that model (the pre-stated tau of `docs/91:63` is per rule, not per model): mpa0: Ni31Cr29Cu5Mn35 0.4399960638886986 < Fe25Co25Ni25Cr25 0.4530565522419163 < Cu26Ni9Cr31Co33 0.4791918879560475 < Ni34Fe6Cu29Co31 0.7258416589359067 < Cu8Cr23Mn35Co34 0.7557679417210732 < Cu22Fe30Co32Mn15 0.7956531821512538, tau-a 1.0 against `banked_order` (computed here); omat0: Cu8Cr23Mn35Co34 0.4769722746170424 < Cu26Ni9Cr31Co33 0.5121988465266036 < Ni31Cr29Cu5Mn35 0.5766075922266127 < Fe25Co25Ni25Cr25 0.6915009330926596 < Ni34Fe6Cu29Co31 0.7128337563325617 < Cu22Fe30Co32Mn15 0.7824106890637879, tau-a 0.2 against `banked_order` (computed here); mp0: Cu26Ni9Cr31Co33 0.4572539172497043 < Ni31Cr29Cu5Mn35 0.46160080294844175 < Cu8Cr23Mn35Co34 0.8363970071222182 < Fe25Co25Ni25Cr25 0.9022344882710467 < Cu22Fe30Co32Mn15 0.934320589166175 < Ni34Fe6Cu29Co31 0.9873154466280152, tau-a 0.3333333333333333 against `banked_order` (computed here); matpes: Fe25Co25Ni25Cr25 0.3503844104703129 < Ni31Cr29Cu5Mn35 0.4483130168751339 < Cu8Cr23Mn35Co34 0.46221527014158514 < Cu26Ni9Cr31Co33 0.5414029268550147 < Cu22Fe30Co32Mn15 0.6595708335526203 < Ni34Fe6Cu29Co31 0.764198298107444, tau-a 0.4666666666666667 against `banked_order` (computed here).

### (c′) post-hoc — the ensemble beyond the minimum: per-model site distributions on the gated six

This subsection was added to the emitter on 2026-09-08 after the gated six had landed under all four checkpoints (readout stamp 2026-09-08T11:09:17+00:00); every threshold in it is a reading rule chosen after seeing those rows, not a pre-stated bar, and nothing in it enters any rule of readout (c) or fills any slot. Post-hoc throughout. The readout read here carries `generated` 2026-09-13T03:35:47+00:00. Rows: `per_site.csv` `candidate_status == evaluated`, `formula` in the gated six, arm CENSUS-1 for mpa0 and CENSUS-2 for omat0 / mp0 / matpes, seeds 0, 1, 2 x site_index 0..3 — 72 rows per model; a model with fewer rows prints pending and is left out of the pairwise tables. Every statistic below is arithmetic of this script on the named csv columns (`eta_V`, `pls`, `dG_OH`, `dG_O`, `dG_OOH`, `OOH_o_o_A`, `OOH_category`, `initial_metal`, `unconverged_states`); a row with an empty `eta_V` is counted in the n of Table C′1 and left out of every eta arithmetic (the n of Tables C′4 and C′5 count rows with an eta). Nothing here scores, ranks or changes a verdict.

**Table C′1 — site eta per model** (n; mean; sample sd, ddof = 1; median; p10, linear interpolation as `distribution.json` `statistics`; min; max; sites with `unconverged_states` > 0; `pls` counts 1 / 2 / 3 / 4):

| model | n (with eta) | mean (V) | sd (V) | median (V) | p10 (V) | min (V) | max (V) | unconverged sites | pls 1 / 2 / 3 / 4 |
|---|---|---|---|---|---|---|---|---|---|
| mpa0 | 72 (72) | 1.0036 | 0.2618 | 0.9764 | 0.7095 | 0.4400 | 1.5301 | 3 | 9 / 39 / 3 / 21 |
| omat0 | 72 (72) | 1.0331 | 0.2809 | 1.0435 | 0.6626 | 0.4770 | 2.1989 | 3 | 9 / 56 / 4 / 3 |
| mp0 | 72 (72) | 1.0908 | 0.2991 | 1.1157 | 0.9119 | 0.4573 | 3.1699 | 1 | 43 / 25 / 4 / 0 |
| matpes | 72 (72) | 1.7102 | 2.0639 | 1.0227 | 0.5527 | 0.3504 | 10.2869 | 5 | 0 / 36 / 0 / 36 |

**Table C′2 — descriptor means per model** (over the 72 rows: mean `dG_OH`, `dG_O`, `dG_OOH`; over the rows with `OOH_category` NORMAL: n, mean eta, mean `dG_OH`, mean `dG_OOH`, mean and sample sd of `dG_OOH` − `dG_OH`; eV except eta):

| model | mean dG_OH | mean dG_O | mean dG_OOH | NORMAL n | NORMAL mean eta (V) | NORMAL mean dG_OH | NORMAL mean dG_OOH | NORMAL mean (dG_OOH − dG_OH) | NORMAL sd (dG_OOH − dG_OH) |
|---|---|---|---|---|---|---|---|---|---|
| mpa0 | 1.7765 | 3.4869 | 3.3645 | 15 | 0.9793 | 1.7871 | 4.6720 | 2.8849 | 0.0990 |
| omat0 | 1.8298 | 3.9585 | 4.6006 | 48 | 1.0679 | 1.8241 | 5.1400 | 3.3159 | 0.1356 |
| mp0 | 2.2079 | 4.1346 | 4.4078 | 29 | 1.1319 | 2.1893 | 5.5230 | 3.3336 | 0.1905 |
| matpes | 0.8437 | 2.8248 | 2.2785 | 48 | 0.8540 | 0.8338 | 3.2839 | 2.4502 | 0.1392 |

**Table C′3 — O-O distance of the OOH endpoint per model** (`OOH_o_o_A` over the 72 rows: min, 5th percentile, median, max; rows below 1.10 A — a post-hoc reading rule, not a docs/91 band):

| model | n with an O-O value | min (A) | p5 (A) | median (A) | max (A) | rows below 1.10 A |
|---|---|---|---|---|---|---|
| mpa0 | 72 | 1.2232 | 1.2257 | 1.2340 | 1.3942 | 0 |
| omat0 | 72 | 1.2375 | 1.2383 | 1.3819 | 1.4069 | 0 |
| mp0 | 72 | 1.2316 | 1.2327 | 1.2353 | 1.4054 | 0 |
| matpes | 72 | 0.8011 | 1.0355 | 1.3775 | 1.3964 | 4 |

**Collapsed O-O rows** (every row with `OOH_o_o_A` < 1.10 A; cells are the csv values):

| model | composition | seed | site | initial metal | O-O (A) | M-O of the OOH (A) | OOH tier / category / H location | dG_OOH (eV) | eta (V) | pls | unconverged_states | OOH_slab_max_A |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| matpes | Cu26Ni9Cr31Co33 | 0 | 2 | Cu | 0.8082275198618786 | 4.702769728446979 | desorbed / DESORPTION / ON_ADSORBATE | -6.596898662750148 | 10.286898662750147 | 4 | 1 | 1.9385429579902342 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 0 | Co | 0.8057690312825309 | 4.469226967412291 | desorbed / DESORPTION / ON_ADSORBATE | -5.746246397551074 | 9.436246397551074 | 4 | 0 | 0.16749781842359424 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 2 | Cr | 0.812833321549264 | 4.5415840773607465 | desorbed / DESORPTION / ON_ADSORBATE | -5.706316758904093 | 9.396316758904092 | 4 | 1 | 0.5217033804235295 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 3 | Cu | 0.8010525042843333 | 4.526158065585832 | desorbed / DESORPTION / ON_ADSORBATE | -6.140334004780113 | 9.830334004780113 | 4 | 1 | 0.5889154269007126 |

Reading of the collapsed rows (post-hoc, from the cells above): their O-O separations span 0.8011-0.8128 A, shorter than the shortest O-O length among the `docs/91:56` anchors, 1.22994 A (the 9 anchor lengths of that line read here: 1.3721922129981474, 1.34313, 1.33854, 1.22994, 1.23780, 1.233, 1.309, 1.483, 1.479 A). The `docs/91:56` bands read "O2_LIKE <= 1.28 A; SUPEROXO_LIKE (1.28, 1.36]; OOH_LIKE (1.36, 1.60]; OO_CLEAVED > 1.60 A": the O2_LIKE band has no lower edge, so every O-O below 1.28 A is O2_LIKE by construction and the classifier reads these rows as O2_LIKE (4) (`OOH_o_o_class`).
`dG_OOH` of these rows spans -6.5969 to -5.7063 eV; 4 of 4 are negative.
4 of 4 carry `pls` 4 and satisfy eta + 1.23 = 4.92 − `dG_OOH` to 1e-9 (`src/hea_oer/descriptors.py:10`, `:34-35`, read as text; asserted per row), so their eta of 9.3963-10.2869 V is the step-4 term 4.92 − dG_OOH minus the equilibrium potential 1.23 V.
`unconverged_states` > 0 on 3 of 4.
Whether a collapsed row is the min-site row of its composition under its model (against `ranking.ensemble_spread.<f>.min_site_eta_by_model_V`, the (c) values): matpes Cu26Ni9Cr31Co33 seed 0 site 2: not the min-site row (min-site row seed 1 site 2, eta 0.5414029268550147 V); matpes Cu26Ni9Cr31Co33 seed 2 site 0: not the min-site row (min-site row seed 1 site 2, eta 0.5414029268550147 V); matpes Cu26Ni9Cr31Co33 seed 2 site 2: not the min-site row (min-site row seed 1 site 2, eta 0.5414029268550147 V); matpes Cu26Ni9Cr31Co33 seed 2 site 3: not the min-site row (min-site row seed 1 site 2, eta 0.5414029268550147 V) — so the (c) rule values and the `ensemble_spread` minima are untouched by them.

**Table C′4 — pairwise site-level agreement** (matched (`formula`, `seed`, `site_index`) rows of the two models; Pearson r and Spearman rho (average ranks) of `eta_V`; shift = eta(b) − eta(a) in V, mean and median; fraction of matched rows with the same `OOH_category`; each pair once over every matched row and once over the matched rows with no collapsed-O-O row under either model of the pair):

| pair a, b | rows | n matched | Pearson r | Spearman rho | mean shift b − a (V) | median shift (V) | same OOH category |
|---|---|---|---|---|---|---|---|
| mpa0, omat0 | all | 72 | 0.426 | 0.427 | 0.0296 | 0.0075 | 0.3889 |
| mpa0, omat0 | excluding collapsed | 72 | 0.426 | 0.427 | 0.0296 | 0.0075 | 0.3889 |
| mpa0, mp0 | all | 72 | 0.386 | 0.362 | 0.0872 | -0.0009 | 0.4306 |
| mpa0, mp0 | excluding collapsed | 72 | 0.386 | 0.362 | 0.0872 | -0.0009 | 0.4306 |
| mpa0, matpes | all | 72 | 0.079 | 0.050 | 0.7066 | 0.0565 | 0.3333 |
| mpa0, matpes | excluding collapsed | 68 | 0.051 | 0.026 | 0.2380 | 0.0306 | 0.2941 |
| omat0, mp0 | all | 72 | 0.391 | 0.538 | 0.0576 | 0.0275 | 0.4444 |
| omat0, mp0 | excluding collapsed | 72 | 0.391 | 0.538 | 0.0576 | 0.0275 | 0.4444 |
| omat0, matpes | all | 72 | 0.073 | 0.369 | 0.6770 | -0.0465 | 0.5972 |
| omat0, matpes | excluding collapsed | 68 | 0.325 | 0.412 | 0.2025 | -0.0655 | 0.6176 |
| mp0, matpes | all | 72 | 0.397 | 0.025 | 0.6194 | -0.0620 | 0.3611 |
| mp0, matpes | excluding collapsed | 68 | 0.078 | 0.019 | 0.1760 | -0.0780 | 0.3676 |

**Table C′5 — site eta per model x `initial_metal`** (n and mean `eta_V`; metals as present in the rows; the second block leaves out each model's own collapsed-O-O rows):

*all rows*:

| model | Co n, mean (V) | Cr n, mean (V) | Cu n, mean (V) | Fe n, mean (V) | Mn n, mean (V) | Ni n, mean (V) |
|---|---|---|---|---|---|---|
| mpa0 | 17, 0.9237 | 14, 0.7953 | 7, 1.0825 | 12, 1.2183 | 9, 1.1266 | 13, 1.0065 |
| omat0 | 17, 0.9094 | 14, 0.6531 | 7, 1.3338 | 12, 1.1069 | 9, 1.3251 | 13, 1.1722 |
| mp0 | 17, 1.0157 | 14, 0.8980 | 7, 1.4494 | 12, 1.1515 | 9, 1.0830 | 13, 1.1528 |
| matpes | 17, 1.9180 | 14, 1.3775 | 7, 3.9534 | 12, 0.9784 | 9, 1.4827 | 13, 1.4217 |

*excluding collapsed-O-O rows*:

| model | Co n, mean (V) | Cr n, mean (V) | Cu n, mean (V) | Fe n, mean (V) | Mn n, mean (V) | Ni n, mean (V) |
|---|---|---|---|---|---|---|
| mpa0 | 17, 0.9237 | 14, 0.7953 | 7, 1.0825 | 12, 1.2183 | 9, 1.1266 | 13, 1.0065 |
| omat0 | 17, 0.9094 | 14, 0.6531 | 7, 1.3338 | 12, 1.1069 | 9, 1.3251 | 13, 1.1722 |
| mp0 | 17, 1.0157 | 14, 0.8980 | 7, 1.4494 | 12, 1.1515 | 9, 1.0830 | 13, 1.1528 |
| matpes | 16, 1.4481 | 13, 0.7607 | 5, 1.5113 | 12, 0.9784 | 9, 1.4827 | 13, 1.4217 |

**Table C′6 — extreme rows** (post-hoc thresholds: `eta_V` > 2.0 V or `dG_OOH` < 2.0 eV; every gated-six row of a complete model, eta descending):

| model | composition | seed | site | initial metal | eta (V) | dG_OH | dG_O | dG_OOH | pls | OH tier | O tier / category | OOH tier / category / O-O (A) / O-O class / H location | OOH_slab_max_A | unconverged_states |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| matpes | Cu26Ni9Cr31Co33 | 0 | 2 | Cu | 10.286898662750147 | 0.9295818896015472 | 3.288919617292783 | -6.596898662750148 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 0.8082275198618786 / O2_LIKE / ON_ADSORBATE | 1.9385429579902342 | 1 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 3 | Cu | 9.830334004780113 | 1.111531409047768 | 3.5811623972729256 | -6.140334004780113 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 0.8010525042843333 / O2_LIKE / ON_ADSORBATE | 0.5889154269007126 | 1 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 0 | Co | 9.436246397551074 | 0.7468314676697329 | 2.7204380324061566 | -5.746246397551074 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 0.8057690312825309 / O2_LIKE / ON_ADSORBATE | 0.16749781842359424 | 0 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 2 | Cr | 9.396316758904092 | 1.1176604256006724 | 2.212293747318319 | -5.706316758904093 | 4 | bound | bound / RECONSTRUCTION | desorbed / DESORPTION / 0.812833321549264 / O2_LIKE / ON_ADSORBATE | 0.5217033804235295 | 1 |
| mp0 | Cu26Ni9Cr31Co33 | 2 | 3 | Cu | 3.1699140824949184 | 2.26297430616509 | 1.3159115823829597 | 5.715825664877878 | 3 | bound | desorbed / DESORPTION | bound / NORMAL / 1.3774762631968942 / OOH_LIKE / ON_ADSORBATE | 0.18294225403772446 | 0 |
| matpes | Ni34Fe6Cu29Co31 | 0 | 2 | Ni | 2.562378101517923 | 0.8901761152931268 | 3.37181860381009 | 1.1276218984820772 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2177695139253721 / O2_LIKE / H_TRANSFERRED | 0.14252251148348352 | 0 |
| matpes | Ni34Fe6Cu29Co31 | 0 | 3 | Co | 2.544395111496713 | 1.0629060288342882 | 3.335081088834051 | 1.145604888503287 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2188377207456633 / O2_LIKE / H_TRANSFERRED | 0.11597241611198092 | 0 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 1 | Co | 2.4948548957465144 | 0.9235468866203401 | 3.182393141850077 | 1.1951451042534855 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2186600115824848 / O2_LIKE / H_TRANSFERRED | 0.12322089743973236 | 0 |
| matpes | Ni31Cr29Cu5Mn35 | 2 | 1 | Mn | 2.4877412087403608 | 0.7351332314821203 | 2.8724657400167706 | 1.2022587912596392 | 4 | bound | bound / RECONSTRUCTION | weak / DISSOCIATION / 1.2243878137904451 / O2_LIKE / H_TRANSFERRED | 0.1043988192467131 | 0 |
| matpes | Cu8Cr23Mn35Co34 | 1 | 3 | Mn | 2.464518158300323 | 0.4433947419086163 | 2.6687171555928506 | 1.2254818416996769 | 4 | bound | bound / RECONSTRUCTION | weak / DISSOCIATION / 1.224942162957036 / O2_LIKE / H_TRANSFERRED | 0.14429199720414132 | 0 |
| matpes | Cu22Fe30Co32Mn15 | 1 | 1 | Cu | 2.4434857266632415 | 1.1475223921861581 | 3.5373876246634444 | 1.2465142733367585 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.220258269360634 / O2_LIKE / H_TRANSFERRED | 0.18400013019069847 | 0 |
| matpes | Ni31Cr29Cu5Mn35 | 2 | 0 | Mn | 2.4433180001649797 | 0.6201509876488099 | 2.744993660317397 | 1.2466819998350203 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2283830954836092 / O2_LIKE / H_TRANSFERRED | 0.11542531002690008 | 0 |
| matpes | Ni31Cr29Cu5Mn35 | 2 | 3 | Ni | 2.4427944860349706 | 0.7172136792526199 | 3.116347197957004 | 1.2472055139650293 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2217183811427188 / O2_LIKE / H_TRANSFERRED | 0.10894460792653496 | 0 |
| matpes | Cu8Cr23Mn35Co34 | 0 | 3 | Co | 2.407603412039678 | 0.8003821307438667 | 2.833435388555592 | 1.282396587960322 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2201137393988342 / O2_LIKE / H_TRANSFERRED | 0.15250434334046006 | 0 |
| matpes | Cu22Fe30Co32Mn15 | 0 | 3 | Co | 2.2549230053052023 | 0.8801544640266566 | 3.0371582637043337 | 1.4350769946947977 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.221530866236198 / O2_LIKE / H_TRANSFERRED | 0.11585054647509295 | 0 |
| matpes | Ni34Fe6Cu29Co31 | 0 | 1 | Ni | 2.2507231782897614 | 0.8075065529260538 | 3.2339948449740694 | 1.4392768217102385 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2206582968239987 / O2_LIKE / H_TRANSFERRED | 0.1336517535028758 | 0 |
| matpes | Cu22Fe30Co32Mn15 | 0 | 2 | Fe | 2.2034975832873878 | 0.8889549598308232 | 2.8810260957521967 | 1.4865024167126122 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2207145289763095 / O2_LIKE / H_TRANSFERRED | 0.12706277019474022 | 0 |
| omat0 | Ni31Cr29Cu5Mn35 | 2 | 1 | Mn | 2.1989156922026205 | 1.5069267933873225 | 1.560876170637844 | 4.989791862840464 | 3 | bound | desorbed / DESORPTION | bound / NORMAL / 1.3943331555559202 / OOH_LIKE / ON_ADSORBATE | 0.1460321230611419 | 0 |
| matpes | Cu26Ni9Cr31Co33 | 1 | 3 | Cr | 2.1530754707381883 | 1.1692389865234074 | 2.352990204381178 | 1.5369245292618117 | 4 | bound | bound / RECONSTRUCTION | desorbed / DESORPTION / 1.22123082690612 / O2_LIKE / H_TRANSFERRED | 0.2155410595772455 | 0 |
| matpes | Cu26Ni9Cr31Co33 | 0 | 0 | Cr | 1.953373450362208 | 1.1205195237529435 | 1.4174403385184242 | 1.736626549637792 | 4 | bound | bound / RECONSTRUCTION | desorbed / DESORPTION / 1.3360355632314367 / SUPEROXO_LIKE / ON_ADSORBATE | 2.0445891586213536 | 1 |
| matpes | Fe25Co25Ni25Cr25 | 1 | 2 | Co | 1.7971154896963961 | 0.6794936832834647 | 2.7573438335807685 | 1.8928845103036038 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2228949150088324 / O2_LIKE / H_TRANSFERRED | 0.21735704356357685 | 0 |
| matpes | Cu8Cr23Mn35Co34 | 2 | 1 | Co | 1.74967009534548 | 0.6919776556538973 | 2.6755201699248863 | 1.94032990465452 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2236690011895688 / O2_LIKE / H_TRANSFERRED | 0.20551755371005662 | 0 |
| matpes | Fe25Co25Ni25Cr25 | 1 | 1 | Fe | 1.7156541508805256 | 0.7948234052276003 | 2.647787357241106 | 1.9743458491194743 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2207036138290746 / O2_LIKE / H_TRANSFERRED | 0.29769720842192854 | 0 |
| matpes | Fe25Co25Ni25Cr25 | 0 | 3 | Ni | 1.7008020531068704 | 0.8372816118981173 | 3.15315409327821 | 1.9891979468931296 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2220366813547903 / O2_LIKE / H_TRANSFERRED | 0.183323006346978 | 1 |

Rows in the extreme table per model (of 72): mpa0 0; omat0 1; mp0 1; matpes 22.

**Closing (post-hoc, every number from the tables above and Table C2).** Lowest min-site eta per model (`min_site_eta_by_model_V`, read, not ranked): under mpa0: Ni31Cr29Cu5Mn35 (0.4399960638886986 V); under omat0: Cu8Cr23Mn35Co34 (0.4769722746170424 V); under mp0: Cu26Ni9Cr31Co33 (0.4572539172497043 V); under matpes: Fe25Co25Ni25Cr25 (0.3503844104703129 V) — no composition holds the lowest value under two models. Spread: the largest `ensemble_spread.spread_V` of Table C2 is Fe25Co25Ni25Cr25 at 0.5518500778007338 V (`n_models` 4), made by matpes 0.3503844104703129 against mp0 0.9022344882710467. Per-model median site eta beside the per-model minimum (Table C′1): mpa0 min 0.4400, median 0.9764 V; omat0 min 0.4770, median 1.0435 V; mp0 min 0.4573, median 1.1157 V; matpes min 0.3504, median 1.0227 V. Mean shift of Table C′4 with and without the collapsed-O-O rows (4 distinct (formula, seed, site) keys collapsed): mpa0, omat0: 0.0296 V over 72, no row excluded, the two figures coincide; mpa0, mp0: 0.0872 V over 72, no row excluded, the two figures coincide; mpa0, matpes: 0.7066 V over 72 against 0.2380 V over 68 — a difference of 0.4686 V carried by the 4 excluded rows; omat0, mp0: 0.0576 V over 72, no row excluded, the two figures coincide; omat0, matpes: 0.6770 V over 72 against 0.2025 V over 68 — a difference of 0.4746 V carried by the 4 excluded rows; mp0, matpes: 0.6194 V over 72 against 0.1760 V over 68 — a difference of 0.4434 V carried by the 4 excluded rows. The same readings over all twelve CENSUS-2 compositions are in (c′′) below (post-hoc).

### (c′′) post-hoc — the same readings over all twelve CENSUS-2 compositions (144 sites per model)

This block was added to the emitter on 2026-09-09 after all 36 CENSUS-2 manifests had landed (readout stamp 2026-09-09T01:20:23+00:00); every threshold in it is a reading rule chosen after seeing those rows, not a pre-stated bar, and nothing in it enters any rule of readout (c) or fills any slot. Post-hoc throughout; it scores nothing, ranks nothing and changes no verdict. The readout read here carries `generated` 2026-09-13T03:35:47+00:00. Site set: `per_site.csv` `candidate_status == evaluated`, `formula` in the twelve keys of `ranking.ensemble_spread`, arm CENSUS-1 for mpa0 and CENSUS-2 for omat0 / mp0 / matpes, seeds 0, 1, 2 x site_index 0..3 — 144 rows per model; a model with fewer rows prints pending and is left out of the order and pairwise tables. The banked twelve-order is the twelve `ensemble_spread` keys sorted by their `banked_eta_V` (asserted equal to `banked_order` on the gated six): Ni31Cr29Cu5Mn35 0.43999606379672596, Fe25Co25Ni25Cr25 0.4530565517906915, Cu26Ni9Cr31Co33 0.4791918878366763, Cr33Co5Ni29Cu33 0.5151978336124718, Mn31Ni31Co33Cu6 0.6683335303354587, Fe31Cu25Cr13Ni31 0.6771430802173617, Ni34Fe6Cu29Co31 0.7258416193876736, Mn34Cu7Fe33Cr27 0.7363354672577165, Co5Cu33Ni28Mn34 0.7447569249586499, Cu8Cr23Mn35Co34 0.7557679418652832, Cu22Fe30Co32Mn15 0.7956532031025425, Ni34Fe29Mn30Co7 0.8720706667379394. Every statistic below is arithmetic of this script on the named csv columns; the collapsed-O-O and extreme-row thresholds are the (c′) reading rules, the negative-*OOH threshold is a reading rule of this block alone, and none is a docs/91 band.

**Table C′′1 — site eta per model over the twelve** (columns as Table C′1, then `OOH_category` counts NORMAL / DESORPTION / DISSOCIATION / MIGRATION / RECONSTRUCTION, sites with `all_states_intact` True and with `all_states_adsorbate_intact` True):

| model | n (with eta) | mean (V) | sd (V) | median (V) | p10 (V) | min (V) | max (V) | unconverged sites | pls 1 / 2 / 3 / 4 | OOH N/D/X/M/R | INTACT | ADS-INTACT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mpa0 | 144 (144) | 1.0450 | 0.2900 | 1.0194 | 0.7265 | 0.4400 | 2.1327 | 8 | 23 / 70 / 12 / 39 | 26/104/13/0/1 | 17 | 23 |
| omat0 | 144 (144) | 1.1231 | 0.2836 | 1.1580 | 0.7558 | 0.4770 | 2.2900 | 3 | 15 / 119 / 7 / 3 | 94/39/10/0/1 | 75 | 91 |
| mp0 | 144 (144) | 1.1599 | 0.3024 | 1.1476 | 0.9678 | 0.4573 | 3.1699 | 2 | 89 / 48 / 7 / 0 | 56/87/1/0/0 | 44 | 51 |
| matpes | 144 (144) | 1.5763 | 1.6299 | 1.0841 | 0.6008 | 0.1529 | 10.2869 | 7 | 1 / 80 / 0 / 63 | 93/23/25/0/3 | 74 | 96 |

**Table C′′2 — the twelve-composition order of min-site eta per model** (`ranking.ensemble_spread.<f>.min_site_eta_by_model_V.<model>`, ascending; Kendall tau-a against the banked twelve-order, computed here; the lowest composition's min-site row from `per_site.csv`: seed / site_index / `initial_metal`, `OOH_category`, `OOH_o_o_class`, `O_tier`):

| model | order of min-site eta (ascending, V) | Kendall tau-a vs banked twelve-order | lowest composition | its min-site row: seed / site / initial metal, OOH category, O-O class, O tier |
|---|---|---|---|---|
| mpa0 | Ni31Cr29Cu5Mn35 0.4399960638886986 < Fe25Co25Ni25Cr25 0.4530565522419163 < Cu26Ni9Cr31Co33 0.4791918879560475 < Cr33Co5Ni29Cu33 0.5172986131125741 < Mn31Ni31Co33Cu6 0.6683335322074262 < Fe31Cu25Cr13Ni31 0.6771430805058989 < Ni34Fe6Cu29Co31 0.7258416589359067 < Mn34Cu7Fe33Cr27 0.7363354674562137 < Co5Cu33Ni28Mn34 0.7447569249026023 < Cu8Cr23Mn35Co34 0.7557679417210732 < Cu22Fe30Co32Mn15 0.7956531821512538 < Ni34Fe29Mn30Co7 0.8720706667688054 | 1.0 | Ni31Cr29Cu5Mn35 (0.4399960638886986 V) | 1 / 0 / Cr, NORMAL, OOH_LIKE, bound |
| omat0 | Cu8Cr23Mn35Co34 0.4769722746170424 < Cu26Ni9Cr31Co33 0.5121988465266036 < Ni31Cr29Cu5Mn35 0.5766075922266127 < Cr33Co5Ni29Cu33 0.5875500753086769 < Fe25Co25Ni25Cr25 0.6915009330926596 < Ni34Fe6Cu29Co31 0.7128337563325617 < Fe31Cu25Cr13Ni31 0.7371467865463801 < Mn34Cu7Fe33Cr27 0.7618964711276321 < Cu22Fe30Co32Mn15 0.7824106890637879 < Mn31Ni31Co33Cu6 0.8357995710311386 < Co5Cu33Ni28Mn34 0.8881492702465339 < Ni34Fe29Mn30Co7 1.1034307066303697 | 0.45454545454545453 | Cu8Cr23Mn35Co34 (0.4769722746170424 V) | 2 / 3 / Cr, NORMAL, OOH_LIKE, bound |
| mp0 | Cu26Ni9Cr31Co33 0.4572539172497043 < Ni31Cr29Cu5Mn35 0.46160080294844175 < Cr33Co5Ni29Cu33 0.7821676713976897 < Cu8Cr23Mn35Co34 0.8363970071222182 < Fe25Co25Ni25Cr25 0.9022344882710467 < Cu22Fe30Co32Mn15 0.934320589166175 < Co5Cu33Ni28Mn34 0.981240977035652 < Ni34Fe6Cu29Co31 0.9873154466280152 < Mn34Cu7Fe33Cr27 0.9976474473711345 < Mn31Ni31Co33Cu6 1.0017444153347537 < Ni34Fe29Mn30Co7 1.042341134052367 < Fe31Cu25Cr13Ni31 1.0933257730468267 | 0.30303030303030304 | Cu26Ni9Cr31Co33 (0.4572539172497043 V) | 1 / 0 / Cr, DESORPTION, O2_LIKE, bound |
| matpes | Cr33Co5Ni29Cu33 0.1528846513813571 < Fe31Cu25Cr13Ni31 0.3334729857099754 < Fe25Co25Ni25Cr25 0.3503844104703129 < Mn34Cu7Fe33Cr27 0.3679492415189296 < Ni31Cr29Cu5Mn35 0.4483130168751339 < Cu8Cr23Mn35Co34 0.46221527014158514 < Cu26Ni9Cr31Co33 0.5414029268550147 < Ni34Fe29Mn30Co7 0.6516787612295181 < Cu22Fe30Co32Mn15 0.6595708335526203 < Co5Cu33Ni28Mn34 0.746428894783107 < Ni34Fe6Cu29Co31 0.764198298107444 < Mn31Ni31Co33Cu6 0.9482817552551657 | 0.21212121212121213 | Cr33Co5Ni29Cu33 (0.1528846513813571 V) | 0 / 2 / Cr, NORMAL, OOH_LIKE, bound |

Of the 4 complete models, 4 put a Cr site lowest (`initial_metal` of the lowest composition's min-site row: mpa0 Cr, omat0 Cr, mp0 Cr, matpes Cr; by metal Cr 4); no two models share the lowest composition.

**Table C′′2b — per-composition ensemble spread over the twelve** (`ranking.ensemble_spread.<f>.{banked_eta_V, spread_V, n_models, min_site_eta_by_model_V}`, banked twelve-order; a spread cell at `n_models` < 4 names the pending tags; the values are those of `ranking.json`, anchored, not recomputed):

| composition (banked twelve-order) | banked_eta_V | ensemble spread (V) [n_models] | min-site eta by model (V) |
|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.43999606379672596 | 0.13661152833791412 [n_models 4] | mpa0 0.4399960638886986, omat0 0.5766075922266127, mp0 0.46160080294844175, matpes 0.4483130168751339 |
| Fe25Co25Ni25Cr25 | 0.4530565517906915 | 0.5518500778007338 [n_models 4] | mpa0 0.4530565522419163, omat0 0.6915009330926596, mp0 0.9022344882710467, matpes 0.3503844104703129 |
| Cu26Ni9Cr31Co33 | 0.4791918878366763 | 0.08414900960531035 [n_models 4] | mpa0 0.4791918879560475, omat0 0.5121988465266036, mp0 0.4572539172497043, matpes 0.5414029268550147 |
| Cr33Co5Ni29Cu33 | 0.5151978336124718 | 0.6292830200163326 [n_models 4] | mpa0 0.5172986131125741, omat0 0.5875500753086769, mp0 0.7821676713976897, matpes 0.1528846513813571 |
| Mn31Ni31Co33Cu6 | 0.6683335303354587 | 0.3334108831273275 [n_models 4] | mpa0 0.6683335322074262, omat0 0.8357995710311386, mp0 1.0017444153347537, matpes 0.9482817552551657 |
| Fe31Cu25Cr13Ni31 | 0.6771430802173617 | 0.7598527873368512 [n_models 4] | mpa0 0.6771430805058989, omat0 0.7371467865463801, mp0 1.0933257730468267, matpes 0.3334729857099754 |
| Ni34Fe6Cu29Co31 | 0.7258416193876736 | 0.27448169029545344 [n_models 4] | mpa0 0.7258416589359067, omat0 0.7128337563325617, mp0 0.9873154466280152, matpes 0.764198298107444 |
| Mn34Cu7Fe33Cr27 | 0.7363354672577165 | 0.6296982058522049 [n_models 4] | mpa0 0.7363354674562137, omat0 0.7618964711276321, mp0 0.9976474473711345, matpes 0.3679492415189296 |
| Co5Cu33Ni28Mn34 | 0.7447569249586499 | 0.2364840521330498 [n_models 4] | mpa0 0.7447569249026023, omat0 0.8881492702465339, mp0 0.981240977035652, matpes 0.746428894783107 |
| Cu8Cr23Mn35Co34 | 0.7557679418652832 | 0.37418173698063306 [n_models 4] | mpa0 0.7557679417210732, omat0 0.4769722746170424, mp0 0.8363970071222182, matpes 0.46221527014158514 |
| Cu22Fe30Co32Mn15 | 0.7956532031025425 | 0.27474975561355475 [n_models 4] | mpa0 0.7956531821512538, omat0 0.7824106890637879, mp0 0.934320589166175, matpes 0.6595708335526203 |
| Ni34Fe29Mn30Co7 | 0.8720706667379394 | 0.4517519454008516 [n_models 4] | mpa0 0.8720706667688054, omat0 1.1034307066303697, mp0 1.042341134052367, matpes 0.6516787612295181 |

**Table C′′3 — O-O distance of the OOH endpoint per model over the twelve** (`OOH_o_o_A` over the 144 rows: min, 5th percentile, median, max; rows below 1.10 A — the (c′) reading rule):

| model | n with an O-O value | min (A) | p5 (A) | median (A) | max (A) | rows below 1.10 A |
|---|---|---|---|---|---|---|
| mpa0 | 144 | 1.2232 | 1.2252 | 1.2336 | 1.3942 | 0 |
| omat0 | 144 | 1.2357 | 1.2380 | 1.3789 | 1.4069 | 0 |
| mp0 | 144 | 1.2301 | 1.2326 | 1.2356 | 1.4054 | 0 |
| matpes | 144 | 0.8011 | 1.2182 | 1.3743 | 1.3964 | 4 |

**Collapsed O-O rows over the twelve** (every row with `OOH_o_o_A` < 1.10 A; cells are the csv values):

| model | composition | seed | site | initial metal | O-O (A) | M-O of the OOH (A) | OOH tier / category / H location | dG_OOH (eV) | eta (V) | pls | unconverged_states | OOH_slab_max_A |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| matpes | Cu26Ni9Cr31Co33 | 0 | 2 | Cu | 0.8082275198618786 | 4.702769728446979 | desorbed / DESORPTION / ON_ADSORBATE | -6.596898662750148 | 10.286898662750147 | 4 | 1 | 1.9385429579902342 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 0 | Co | 0.8057690312825309 | 4.469226967412291 | desorbed / DESORPTION / ON_ADSORBATE | -5.746246397551074 | 9.436246397551074 | 4 | 0 | 0.16749781842359424 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 2 | Cr | 0.812833321549264 | 4.5415840773607465 | desorbed / DESORPTION / ON_ADSORBATE | -5.706316758904093 | 9.396316758904092 | 4 | 1 | 0.5217033804235295 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 3 | Cu | 0.8010525042843333 | 4.526158065585832 | desorbed / DESORPTION / ON_ADSORBATE | -6.140334004780113 | 9.830334004780113 | 4 | 1 | 0.5889154269007126 |

**Negative *OOH formation rows** (`dG_OOH` < 0.0 eV, a post-hoc reading rule of this block; every twelve-composition row of a complete model; cells are the csv values):

| model | composition | seed | site | initial metal | dG_OOH (eV) | eta (V) | pls | OOH tier / M-O (A) / category / O-O (A) / O-O class / H location | unconverged_states | OOH_slab_max_A |
|---|---|---|---|---|---|---|---|---|---|---|
| matpes | Cu26Ni9Cr31Co33 | 0 | 2 | Cu | -6.596898662750148 | 10.286898662750147 | 4 | desorbed / 4.702769728446979 / DESORPTION / 0.8082275198618786 / O2_LIKE / ON_ADSORBATE | 1 | 1.9385429579902342 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 0 | Co | -5.746246397551074 | 9.436246397551074 | 4 | desorbed / 4.469226967412291 / DESORPTION / 0.8057690312825309 / O2_LIKE / ON_ADSORBATE | 0 | 0.16749781842359424 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 2 | Cr | -5.706316758904093 | 9.396316758904092 | 4 | desorbed / 4.5415840773607465 / DESORPTION / 0.812833321549264 / O2_LIKE / ON_ADSORBATE | 1 | 0.5217033804235295 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 3 | Cu | -6.140334004780113 | 9.830334004780113 | 4 | desorbed / 4.526158065585832 / DESORPTION / 0.8010525042843333 / O2_LIKE / ON_ADSORBATE | 1 | 0.5889154269007126 |
| matpes | Cr33Co5Ni29Cu33 | 1 | 0 | Co | -1.7946685705587542 | 5.484668570558753 | 4 | desorbed / 5.772028625300088 / DESORPTION / 1.2470430301154527 / O2_LIKE / H_FREE | 0 | 0.051011220685027996 |
| matpes | Cr33Co5Ni29Cu33 | 2 | 2 | Ni | -1.644650975437783 | 5.334650975437782 | 4 | desorbed / 5.912961846419162 / DESORPTION / 1.2466822874118237 / O2_LIKE / H_FREE | 1 | 0.07730245624931718 |
| matpes | Fe31Cu25Cr13Ni31 | 0 | 3 | Ni | -1.809846834745811 | 5.49984683474581 | 4 | desorbed / 5.429171986519998 / DESORPTION / 1.2481321143488784 / O2_LIKE / H_FREE | 0 | 0.10675911008642379 |

Rows in the negative-*OOH table per model (of 144): mpa0 0; omat0 0; mp0 0; matpes 7.

A negative `dG_OOH` is a *OOH formation free energy below zero; these rows are read here, by a post-hoc rule of this block, as broken endpoints for the excluding lines of Table C′′5, not as site values. `dG_OOH` of the 7 rows spans -6.5969 to -1.6447 eV.

4 of the 7 are rows of the collapsed-O-O table above; the other 3 (matpes Cr33Co5Ni29Cu33 seed 1 site 0; matpes Cr33Co5Ni29Cu33 seed 2 site 2; matpes Fe31Cu25Cr13Ni31 seed 0 site 3) read, from the tier, H-location and O-O class columns, tier desorbed on 3 of 3, hydrogen H_FREE on 3 of 3 and O-O class O2_LIKE on 3 of 3 (`OOH_tier` desorbed 3; `OOH_m_o_A` 5.4292-5.9130 A; `OOH_o_o_A` 1.2467-1.2481 A, `OOH_o_o_class` O2_LIKE 3; `OOH_h_location` H_FREE 3): a desorbed O2 fragment with a free hydrogen, an O-O separation inside the O2_LIKE band and no O-O collapse.

Whether a negative-*OOH row is the min-site row of its composition under its model (against `ranking.ensemble_spread.<f>.min_site_eta_by_model_V`; the (c) rule values concern the gated six and are read in (c′)): matpes Cu26Ni9Cr31Co33 seed 0 site 2: not the min-site row (min-site row seed 1 site 2, eta 0.5414029268550147 V); matpes Cu26Ni9Cr31Co33 seed 2 site 0: not the min-site row (min-site row seed 1 site 2, eta 0.5414029268550147 V); matpes Cu26Ni9Cr31Co33 seed 2 site 2: not the min-site row (min-site row seed 1 site 2, eta 0.5414029268550147 V); matpes Cu26Ni9Cr31Co33 seed 2 site 3: not the min-site row (min-site row seed 1 site 2, eta 0.5414029268550147 V); matpes Cr33Co5Ni29Cu33 seed 1 site 0: not the min-site row (min-site row seed 0 site 2, eta 0.1528846513813571 V); matpes Cr33Co5Ni29Cu33 seed 2 site 2: not the min-site row (min-site row seed 0 site 2, eta 0.1528846513813571 V); matpes Fe31Cu25Cr13Ni31 seed 0 site 3: not the min-site row (min-site row seed 1 site 3, eta 0.3334729857099754 V) — so no `ensemble_spread` minimum of any composition under any complete model (mpa0, omat0, mp0, matpes) rests on a negative-*OOH row.

**Table C′′4 — extreme rows over the twelve** (post-hoc thresholds as Table C′6: `eta_V` > 2.0 V or `dG_OOH` < 2.0 eV; every twelve-composition row of a complete model, eta descending):

| model | composition | seed | site | initial metal | eta (V) | dG_OH | dG_O | dG_OOH | pls | OH tier | O tier / category | OOH tier / category / O-O (A) / O-O class / H location | OOH_slab_max_A | unconverged_states |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| matpes | Cu26Ni9Cr31Co33 | 0 | 2 | Cu | 10.286898662750147 | 0.9295818896015472 | 3.288919617292783 | -6.596898662750148 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 0.8082275198618786 / O2_LIKE / ON_ADSORBATE | 1.9385429579902342 | 1 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 3 | Cu | 9.830334004780113 | 1.111531409047768 | 3.5811623972729256 | -6.140334004780113 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 0.8010525042843333 / O2_LIKE / ON_ADSORBATE | 0.5889154269007126 | 1 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 0 | Co | 9.436246397551074 | 0.7468314676697329 | 2.7204380324061566 | -5.746246397551074 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 0.8057690312825309 / O2_LIKE / ON_ADSORBATE | 0.16749781842359424 | 0 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 2 | Cr | 9.396316758904092 | 1.1176604256006724 | 2.212293747318319 | -5.706316758904093 | 4 | bound | bound / RECONSTRUCTION | desorbed / DESORPTION / 0.812833321549264 / O2_LIKE / ON_ADSORBATE | 0.5217033804235295 | 1 |
| matpes | Fe31Cu25Cr13Ni31 | 0 | 3 | Ni | 5.49984683474581 | 0.808544384221943 | 3.102466702079261 | -1.809846834745811 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2481321143488784 / O2_LIKE / H_FREE | 0.10675911008642379 | 0 |
| matpes | Cr33Co5Ni29Cu33 | 1 | 0 | Co | 5.484668570558753 | 0.901174760765468 | 3.0084319771660892 | -1.7946685705587542 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2470430301154527 / O2_LIKE / H_FREE | 0.051011220685027996 | 0 |
| matpes | Cr33Co5Ni29Cu33 | 2 | 2 | Ni | 5.334650975437782 | 0.7575332682867039 | 3.028326210818597 | -1.644650975437783 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2466822874118237 / O2_LIKE / H_FREE | 0.07730245624931718 | 1 |
| mp0 | Cu26Ni9Cr31Co33 | 2 | 3 | Cu | 3.1699140824949184 | 2.26297430616509 | 1.3159115823829597 | 5.715825664877878 | 3 | bound | desorbed / DESORPTION | bound / NORMAL / 1.3774762631968942 / OOH_LIKE / ON_ADSORBATE | 0.18294225403772446 | 0 |
| mp0 | Cr33Co5Ni29Cu33 | 0 | 3 | Cu | 2.635364390685018 | 1.9835310333083087 | 1.6046873346034476 | 5.4700517252884655 | 3 | bound | desorbed / DESORPTION | bound / NORMAL / 1.374237454534201 / OOH_LIKE / ON_ADSORBATE | 0.1261638754660663 | 0 |
| matpes | Ni34Fe6Cu29Co31 | 0 | 2 | Ni | 2.562378101517923 | 0.8901761152931268 | 3.37181860381009 | 1.1276218984820772 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2177695139253721 / O2_LIKE / H_TRANSFERRED | 0.14252251148348352 | 0 |
| matpes | Ni34Fe6Cu29Co31 | 0 | 3 | Co | 2.544395111496713 | 1.0629060288342882 | 3.335081088834051 | 1.145604888503287 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2188377207456633 / O2_LIKE / H_TRANSFERRED | 0.11597241611198092 | 0 |
| matpes | Mn31Ni31Co33Cu6 | 2 | 3 | Mn | 2.503413280892503 | 0.8465009891649625 | 3.141308777506885 | 1.1865867191074968 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.218146093762027 / O2_LIKE / H_TRANSFERRED | 0.11457774676042302 | 0 |
| matpes | Cu26Ni9Cr31Co33 | 2 | 1 | Co | 2.4948548957465144 | 0.9235468866203401 | 3.182393141850077 | 1.1951451042534855 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2186600115824848 / O2_LIKE / H_TRANSFERRED | 0.12322089743973236 | 0 |
| matpes | Ni31Cr29Cu5Mn35 | 2 | 1 | Mn | 2.4877412087403608 | 0.7351332314821203 | 2.8724657400167706 | 1.2022587912596392 | 4 | bound | bound / RECONSTRUCTION | weak / DISSOCIATION / 1.2243878137904451 / O2_LIKE / H_TRANSFERRED | 0.1043988192467131 | 0 |
| mp0 | Fe31Cu25Cr13Ni31 | 1 | 2 | Cu | 2.473594780811473 | 2.3025750355401144 | 1.88890846105533 | 5.592503241866803 | 3 | bound | desorbed / DESORPTION | bound / NORMAL / 1.3641045576266908 / OOH_LIKE / ON_ADSORBATE | 0.12088709507743207 | 0 |
| matpes | Mn31Ni31Co33Cu6 | 2 | 2 | Ni | 2.4695504916789313 | 0.8745282061240797 | 3.210761843572306 | 1.2204495083210687 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.217168259682136 / O2_LIKE / H_TRANSFERRED | 0.12491977306717628 | 0 |
| matpes | Cu8Cr23Mn35Co34 | 1 | 3 | Mn | 2.464518158300323 | 0.4433947419086163 | 2.6687171555928506 | 1.2254818416996769 | 4 | bound | bound / RECONSTRUCTION | weak / DISSOCIATION / 1.224942162957036 / O2_LIKE / H_TRANSFERRED | 0.14429199720414132 | 0 |
| matpes | Cu22Fe30Co32Mn15 | 1 | 1 | Cu | 2.4434857266632415 | 1.1475223921861581 | 3.5373876246634444 | 1.2465142733367585 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.220258269360634 / O2_LIKE / H_TRANSFERRED | 0.18400013019069847 | 0 |
| matpes | Ni31Cr29Cu5Mn35 | 2 | 0 | Mn | 2.4433180001649797 | 0.6201509876488099 | 2.744993660317397 | 1.2466819998350203 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2283830954836092 / O2_LIKE / H_TRANSFERRED | 0.11542531002690008 | 0 |
| matpes | Ni31Cr29Cu5Mn35 | 2 | 3 | Ni | 2.4427944860349706 | 0.7172136792526199 | 3.116347197957004 | 1.2472055139650293 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2217183811427188 / O2_LIKE / H_TRANSFERRED | 0.10894460792653496 | 0 |
| mp0 | Fe31Cu25Cr13Ni31 | 1 | 0 | Cu | 2.440184360426136 | 2.318169005190468 | 1.9113275192040577 | 5.5815118796301935 | 3 | bound | desorbed / DESORPTION | bound / NORMAL / 1.3604496327493196 / OOH_LIKE / ON_ADSORBATE | 0.11369673955187157 | 0 |
| matpes | Cr33Co5Ni29Cu33 | 0 | 0 | Ni | 2.4385402504672564 | 0.6787628509918132 | 3.0038121937899467 | 1.2514597495327435 | 4 | bound | bound / NORMAL | bound / DISSOCIATION / 1.2332086972480312 / O2_LIKE / H_TRANSFERRED | 0.11689362103511887 | 0 |
| matpes | Cu8Cr23Mn35Co34 | 0 | 3 | Co | 2.407603412039678 | 0.8003821307438667 | 2.833435388555592 | 1.282396587960322 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2201137393988342 / O2_LIKE / H_TRANSFERRED | 0.15250434334046006 | 0 |
| matpes | Co5Cu33Ni28Mn34 | 1 | 0 | Cu | 2.3992426594573297 | 1.1940399008966662 | 3.6755060624874494 | 1.2907573405426702 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2181558938864372 / O2_LIKE / H_TRANSFERRED | 0.11317160049045973 | 0 |
| matpes | Cr33Co5Ni29Cu33 | 0 | 1 | Cr | 2.3639977036446433 | 1.2770803215771704 | 2.6796711379263405 | 1.3260022963553566 | 4 | bound | bound / RECONSTRUCTION | weak / DISSOCIATION / 1.220834693229711 / O2_LIKE / H_TRANSFERRED | 0.11534032259544381 | 0 |
| matpes | Mn34Cu7Fe33Cr27 | 0 | 2 | Mn | 2.326169370462865 | 0.5613511711387783 | 2.662234428871108 | 1.363830629537135 | 4 | bound | bound / NORMAL | bound / DISSOCIATION / 1.2268848093661855 / O2_LIKE / H_TRANSFERRED | 0.13454568862899832 | 0 |
| matpes | Ni34Fe29Mn30Co7 | 0 | 3 | Mn | 2.3164415569915926 | 0.8182223037124569 | 3.009734161706894 | 1.3735584430084073 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2228070384559344 / O2_LIKE / H_TRANSFERRED | 0.127755988537041 | 0 |
| matpes | Ni34Fe29Mn30Co7 | 1 | 3 | Fe | 2.311938316974236 | 1.034152716726123 | 3.0192611354899617 | 1.3780616830257642 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.219177821974009 / O2_LIKE / H_TRANSFERRED | 0.13853219383083515 | 0 |
| omat0 | Cr33Co5Ni29Cu33 | 0 | 0 | Ni | 2.290045816570642 | 1.9225975186816986 | 1.5906255250929215 | 5.110671341663563 | 3 | bound | desorbed / DESORPTION | bound / NORMAL / 1.3884682975953517 / OOH_LIKE / ON_ADSORBATE | 0.11121678609904512 | 0 |
| matpes | Ni34Fe29Mn30Co7 | 1 | 2 | Fe | 2.2799538724064385 | 0.9340508308803347 | 2.8170148087336946 | 1.4100461275935614 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2199049513791727 / O2_LIKE / H_TRANSFERRED | 0.14864872871522994 | 0 |
| matpes | Cu22Fe30Co32Mn15 | 0 | 3 | Co | 2.2549230053052023 | 0.8801544640266566 | 3.0371582637043337 | 1.4350769946947977 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.221530866236198 / O2_LIKE / H_TRANSFERRED | 0.11585054647509295 | 0 |
| matpes | Ni34Fe6Cu29Co31 | 0 | 1 | Ni | 2.2507231782897614 | 0.8075065529260538 | 3.2339948449740694 | 1.4392768217102385 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2206582968239987 / O2_LIKE / H_TRANSFERRED | 0.1336517535028758 | 0 |
| omat0 | Ni34Fe29Mn30Co7 | 2 | 1 | Mn | 2.2239782348109025 | 1.6196905904867553 | 1.601105214759546 | 5.055083449570448 | 3 | bound | desorbed / DESORPTION | bound / NORMAL / 1.386950493196312 / OOH_LIKE / ON_ADSORBATE | 0.1547907761854696 | 0 |
| matpes | Cu22Fe30Co32Mn15 | 0 | 2 | Fe | 2.2034975832873878 | 0.8889549598308232 | 2.8810260957521967 | 1.4865024167126122 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2207145289763095 / O2_LIKE / H_TRANSFERRED | 0.12706277019474022 | 0 |
| omat0 | Ni31Cr29Cu5Mn35 | 2 | 1 | Mn | 2.1989156922026205 | 1.5069267933873225 | 1.560876170637844 | 4.989791862840464 | 3 | bound | desorbed / DESORPTION | bound / NORMAL / 1.3943331555559202 / OOH_LIKE / ON_ADSORBATE | 0.1460321230611419 | 0 |
| matpes | Ni34Fe29Mn30Co7 | 0 | 2 | Ni | 2.1869367695739337 | 0.9793994174683686 | 3.2910628921635015 | 1.5030632304260663 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2216447570347253 / O2_LIKE / H_TRANSFERRED | 0.12671253543041017 | 0 |
| matpes | Cu26Ni9Cr31Co33 | 1 | 3 | Cr | 2.1530754707381883 | 1.1692389865234074 | 2.352990204381178 | 1.5369245292618117 | 4 | bound | bound / RECONSTRUCTION | desorbed / DESORPTION / 1.22123082690612 / O2_LIKE / H_TRANSFERRED | 0.2155410595772455 | 0 |
| matpes | Fe31Cu25Cr13Ni31 | 2 | 2 | Cu | 2.151680504821841 | 1.2596783495005295 | 3.7419161924357303 | 1.538319495178159 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.218307498855459 / O2_LIKE / H_TRANSFERRED | 0.14350701323579698 | 0 |
| mpa0 | Ni34Fe29Mn30Co7 | 0 | 2 | Ni | 2.132684876041582 | 2.10405465009111 | 1.3119061601174489 | 4.674591036159031 | 3 | bound | weak / MIGRATION | bound / NORMAL / 1.3312700953621497 / SUPEROXO_LIKE / ON_ADSORBATE | 0.10546077788609036 | 1 |
| mpa0 | Co5Cu33Ni28Mn34 | 2 | 3 | Cu | 2.129268139717498 | 2.12111110083057 | 1.7813758729082887 | 5.140644012625787 | 3 | bound | desorbed / DESORPTION | bound / NORMAL / 1.3384468394455242 / SUPEROXO_LIKE / ON_ADSORBATE | 0.08650956954262216 | 0 |
| matpes | Mn34Cu7Fe33Cr27 | 0 | 3 | Fe | 2.102613137804995 | 0.8040146104344895 | 2.5509896449979186 | 1.5873868621950051 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2208147224334251 / O2_LIKE / H_TRANSFERRED | 0.13543222454598916 | 0 |
| matpes | Fe31Cu25Cr13Ni31 | 2 | 3 | Fe | 2.1014045828017496 | 0.9881038045211991 | 3.0342455631687306 | 1.5885954171982504 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2195279827495773 / O2_LIKE / H_TRANSFERRED | 0.1492508401152484 | 0 |
| matpes | Fe31Cu25Cr13Ni31 | 1 | 2 | Cu | 2.0673187377804405 | 1.2114405143966107 | 3.7664571307364048 | 1.6226812622195594 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2185121089217699 / O2_LIKE / H_TRANSFERRED | 0.12165087300489223 | 0 |
| mpa0 | Fe31Cu25Cr13Ni31 | 1 | 3 | Cr | 2.0673104155862227 | 1.9012904109165683 | 1.4757912435210054 | 4.773101659107228 | 3 | bound | desorbed / DESORPTION | desorbed / DESORPTION / 1.3421247163584853 / SUPEROXO_LIKE / ON_ADSORBATE | 0.06081761965700524 | 0 |
| matpes | Cu26Ni9Cr31Co33 | 0 | 0 | Cr | 1.953373450362208 | 1.1205195237529435 | 1.4174403385184242 | 1.736626549637792 | 4 | bound | bound / RECONSTRUCTION | desorbed / DESORPTION / 1.3360355632314367 / SUPEROXO_LIKE / ON_ADSORBATE | 2.0445891586213536 | 1 |
| matpes | Fe31Cu25Cr13Ni31 | 0 | 0 | Cu | 1.8024760666590263 | 1.0934788479733126 | 3.5373925906266157 | 1.8875239333409737 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2195967273536052 / O2_LIKE / H_TRANSFERRED | 0.37261706269077577 | 0 |
| matpes | Fe25Co25Ni25Cr25 | 1 | 2 | Co | 1.7971154896963961 | 0.6794936832834647 | 2.7573438335807685 | 1.8928845103036038 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2228949150088324 / O2_LIKE / H_TRANSFERRED | 0.21735704356357685 | 0 |
| matpes | Cr33Co5Ni29Cu33 | 0 | 3 | Cu | 1.768832520153567 | 0.8986455907399996 | 3.267554501049182 | 1.9211674798464329 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2207747015940595 / O2_LIKE / H_TRANSFERRED | 0.7106666763682515 | 0 |
| matpes | Cu8Cr23Mn35Co34 | 2 | 1 | Co | 1.74967009534548 | 0.6919776556538973 | 2.6755201699248863 | 1.94032990465452 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2236690011895688 / O2_LIKE / H_TRANSFERRED | 0.20551755371005662 | 0 |
| matpes | Fe31Cu25Cr13Ni31 | 0 | 1 | Fe | 1.746967371297317 | 0.8740070917138038 | 2.8549321437160478 | 1.943032628702683 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2197834518006399 / O2_LIKE / H_TRANSFERRED | 0.3922057641969575 | 0 |
| matpes | Fe25Co25Ni25Cr25 | 1 | 1 | Fe | 1.7156541508805256 | 0.7948234052276003 | 2.647787357241106 | 1.9743458491194743 | 4 | bound | bound / NORMAL | desorbed / DESORPTION / 1.2207036138290746 / O2_LIKE / H_TRANSFERRED | 0.29769720842192854 | 0 |
| matpes | Fe25Co25Ni25Cr25 | 0 | 3 | Ni | 1.7008020531068704 | 0.8372816118981173 | 3.15315409327821 | 1.9891979468931296 | 4 | bound | bound / NORMAL | weak / DISSOCIATION / 1.2220366813547903 / O2_LIKE / H_TRANSFERRED | 0.183323006346978 | 1 |

Rows in the extreme table per model (of 144): mpa0 3; omat0 3; mp0 4; matpes 42.

**Table C′′5 — pairwise site-level agreement over the twelve** (matched (`formula`, `seed`, `site_index`) rows of the two models, columns as Table C′4; each pair once over every matched row and once over the matched rows whose key is in the negative-*OOH table under neither model of the pair; n is the matched count of each line):

| pair a, b | rows | n matched | Pearson r | Spearman rho | mean shift b − a (V) | median shift (V) | same OOH category |
|---|---|---|---|---|---|---|---|
| mpa0, omat0 | all | 144 | 0.273 | 0.282 | 0.0781 | 0.0555 | 0.3403 |
| mpa0, omat0 | excluding negative-*OOH | 144 | 0.273 | 0.282 | 0.0781 | 0.0555 | 0.3403 |
| mpa0, mp0 | all | 144 | 0.178 | 0.186 | 0.1148 | 0.0347 | 0.4375 |
| mpa0, mp0 | excluding negative-*OOH | 144 | 0.178 | 0.186 | 0.1148 | 0.0347 | 0.4375 |
| mpa0, matpes | all | 144 | 0.007 | -0.049 | 0.5313 | 0.0813 | 0.3125 |
| mpa0, matpes | excluding negative-*OOH | 137 | 0.019 | -0.053 | 0.2073 | 0.0571 | 0.2774 |
| omat0, mp0 | all | 144 | 0.348 | 0.423 | 0.0368 | 0.0196 | 0.4375 |
| omat0, mp0 | excluding negative-*OOH | 144 | 0.348 | 0.423 | 0.0368 | 0.0196 | 0.4375 |
| omat0, matpes | all | 144 | 0.042 | 0.302 | 0.4532 | -0.0530 | 0.5764 |
| omat0, matpes | excluding negative-*OOH | 137 | 0.292 | 0.355 | 0.1261 | -0.0634 | 0.5912 |
| mp0, matpes | all | 144 | 0.253 | 0.149 | 0.4165 | -0.0746 | 0.3750 |
| mp0, matpes | excluding negative-*OOH | 137 | 0.149 | 0.168 | 0.1060 | -0.0857 | 0.3796 |

**Closing (post-hoc, every number from the tables above).** Lowest min-site eta per model over the twelve (`min_site_eta_by_model_V`, read, not ranked): under mpa0: Ni31Cr29Cu5Mn35 (0.4399960638886986 V); under omat0: Cu8Cr23Mn35Co34 (0.4769722746170424 V); under mp0: Cu26Ni9Cr31Co33 (0.4572539172497043 V); under matpes: Cr33Co5Ni29Cu33 (0.1528846513813571 V) — no composition holds the lowest value under two models. Spread: the largest `ensemble_spread.spread_V` of Table C′′2b is Fe31Cu25Cr13Ni31 at 0.7598527873368512 V (`n_models` 4), made by matpes 0.3334729857099754 against mp0 1.0933257730468267. Per-model median site eta beside the per-model minimum (Table C′′1): mpa0 min 0.4400, median 1.0194 V; omat0 min 0.4770, median 1.1580 V; mp0 min 0.4573, median 1.1476 V; matpes min 0.1529, median 1.0841 V. Mean shift of Table C′′5 with and without the negative-*OOH rows (7 distinct (formula, seed, site) keys (all under matpes)): mpa0, omat0: 0.0781 V over 144, no row excluded, the two figures coincide; mpa0, mp0: 0.1148 V over 144, no row excluded, the two figures coincide; mpa0, matpes: 0.5313 V over 144 against 0.2073 V over 137 — a difference of 0.3239 V carried by the 7 excluded rows; omat0, mp0: 0.0368 V over 144, no row excluded, the two figures coincide; omat0, matpes: 0.4532 V over 144 against 0.1261 V over 137 — a difference of 0.3272 V carried by the 7 excluded rows; mp0, matpes: 0.4165 V over 144 against 0.1060 V over 137 — a difference of 0.3104 V carried by the 7 excluded rows.

## (d) DECISIVE SITE under each model — post-hoc extension of `docs/91:65` (the mpa0 line is the pre-stated reading)

`docs/91:65` verbatim: "**(d) DECISIVE SITE.** The leader Ni31Cr29Cu5Mn35's winning site in CENSUS-1 (min eta over its 12 sites), with its seed and site_index, and whether the seed is 1 as banked: its OOH state is reported as INTACT or by its category (DESORPTION / DISSOCIATION / MIGRATION / RECONSTRUCTION), with the O-O band, the hydrogen location, its pathway label and its convergence. All three Cr-centred seed-1 sites are reported alongside. This is the one number this census exists to produce; it is written before the run and cannot be reworded after it."

mpa0 (`reproduction.json` `decisive_site`, `docs/93:133`, unchanged): winner seed 1, site_index 0, Cr, eta 0.4399960638886986 V, `winner_seed_matches_banked: true`, OOH INTACT, `winner_site_intact: false`, `winner_pathway: cus`; from the same site's `per_site.csv` row (seed and site_index asserted equal): O-O 1.3797783290461472 A = OOH_LIKE, hydrogen ON_ADSORBATE on the terminal_O, `unconverged_states` 0, OOH tier bound.

- **omat0** (post-hoc; min-`eta_V` row of `per_site.csv` for `omat0__Ni31Cr29Cu5Mn35`): seed 2, site_index 2, initial metal Cr, eta 0.5766075922266127 V; OOH NORMAL (INTACT by the csv columns: NORMAL, site `unconverged_states` 0, tier bound), tier bound, O-O 1.3900948935804858 A = OOH_LIKE, hydrogen ON_ADSORBATE on the terminal_O, binding metal Cr, pathway cus; `all_states_intact` False, `all_states_adsorbate_intact` True; seed equals 1 (banked): no.
- **mp0** (post-hoc; min-`eta_V` row of `per_site.csv` for `mp0__Ni31Cr29Cu5Mn35`): seed 1, site_index 2, initial metal Cr, eta 0.46160080294844175 V; OOH DESORPTION, tier desorbed, O-O 1.2344090793121503 A = O2_LIKE, hydrogen H_TRANSFERRED on the slab_O, binding metal Cr, pathway undefined; `all_states_intact` False, `all_states_adsorbate_intact` False; seed equals 1 (banked): yes.
- **matpes** (post-hoc; min-`eta_V` row of `per_site.csv` for `matpes__Ni31Cr29Cu5Mn35`): seed 0, site_index 0, initial metal Cr, eta 0.4483130168751339 V; OOH NORMAL (INTACT by the csv columns: NORMAL, site `unconverged_states` 0, tier bound), tier bound, O-O 1.3929251283192128 A = OOH_LIKE, hydrogen ON_ADSORBATE on the terminal_O, binding metal Cr, pathway cus; `all_states_intact` False, `all_states_adsorbate_intact` True; seed equals 1 (banked): no.

**Table D1 — the leader's four seed-1 sites under each model** (rows `formula == Ni31Cr29Cu5Mn35`, `seed == 1`; the mpa0 rows equal `decisive_site.seed1_sites[]`, asserted):

| model | site_index | initial metal | eta (V) | OOH category | O-O class | H location | pathway | unconverged states | all states INTACT |
|---|---|---|---|---|---|---|---|---|---|
| mpa0 | 0 | Cr | 0.4399960638886986 | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | 0 | false |
| mpa0 | 1 | Ni | 1.3371918852495819 | DISSOCIATION | O2_LIKE | H_TRANSFERRED | bridge | 0 | false |
| mpa0 | 2 | Cr | 0.4945995053835457 | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | 0 | false |
| mpa0 | 3 | Cr | 1.4147997253705862 | DESORPTION | O2_LIKE | H_TRANSFERRED | undefined | 0 | false |
| omat0 | 0 | Cr | 0.7462145715236561 | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | 0 | false |
| omat0 | 1 | Ni | 1.2756942866374672 | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | 0 | true |
| omat0 | 2 | Cr | 0.6621899293671349 | DESORPTION | O2_LIKE | H_TRANSFERRED | undefined | 0 | false |
| omat0 | 3 | Cr | 0.8809935406969389 | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | 0 | false |
| mp0 | 0 | Cr | 0.5293929098039483 | DESORPTION | O2_LIKE | H_TRANSFERRED | undefined | 0 | false |
| mp0 | 1 | Ni | 1.1881540955928198 | DESORPTION | O2_LIKE | H_TRANSFERRED | undefined | 0 | false |
| mp0 | 2 | Cr | 0.46160080294844175 | DESORPTION | O2_LIKE | H_TRANSFERRED | undefined | 0 | false |
| mp0 | 3 | Cr | 1.1459822425623996 | DESORPTION | O2_LIKE | H_TRANSFERRED | undefined | 0 | false |
| matpes | 0 | Cr | 0.5727018240266242 | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | 0 | false |
| matpes | 1 | Ni | 1.0716329329947163 | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | 0 | true |
| matpes | 2 | Cr | 0.5505108332959461 | NORMAL | OOH_LIKE | ON_ADSORBATE | cus | 0 | false |
| matpes | 3 | Cr | 0.7131885643189415 | NORMAL | SUPEROXO_LIKE | ON_ADSORBATE | cus | 0 | false |

## (e) COST realised — every landed manifest beside the planning figure

`docs/91:67` verbatim: "**(e) COST.** Planning figure from the measured one-site chains at 2 threads on this machine: 511.016 s (equiatomic) and 854.829 s (leader) per candidate evaluation (results/cr_site_chains_2026-09-06/equiatomic-execution.log:8, leader-execution.log:8), each = model load + 2 gas + 1 clean-slab + 9 adsorbate relaxations. That basis is contaminated: the two chain processes overlapped, so they are not serial benchmarks (docs/cr-site-chain-readout-2026-09-06.md:44), and the figure is an upper-leaning planning number, not a measurement of the census. Linear scaling to 12 sites gives 6132.192-10257.948 s per composition (1.70-2.85 h), an over-count because the slab and gas relaxations are shared across sites. CENSUS-1: 73586.304-123095.376 s serial (20.44-34.19 h); with four concurrent 2-thread processes on 8 cores, 5.11-8.55 h wall if concurrency scales (unmeasured). CENSUS-2 (36 manifests, other checkpoints, MPA-0 figure used): 61.32-102.58 h serial, 15.33-25.64 h wall. CENSUS-3 (648 sites = 54 CENSUS-1-manifest equivalents): 91.98-153.87 h serial, 23.00-38.47 h wall. ENDMEMBER-2x2: the r4_validate.json `seconds` sum 3552.3 s (Cr 667.2, Mn 223.0, Fe 408.7, Co 253.9, Ni 622.5, Ru 844.9, Ir 532.1; device not recorded in that file), ~1 h. Total planning figure 44.42-73.65 h wall at four 2-thread workers, 313 clean-slab and up to 11,079 adsorbate relaxations plus 206 gas relaxations (2 per process, 103 processes) from the manifests' `work_estimate`. Per-checkpoint smoke, steps = 2, one site, one seed, Fe25Co25Ni25Cr25, run one after another at 2 threads with nothing else queued: candidate `seconds` 32.531 (mpa0), 32.656 (omat0), 33.547 (mp0), 30.281 (matpes); wall 33.808 / 33.903 / 34.705 / 31.560 s; every one `complete`; the MH-1 smoke is the 5.078 s error of §1. A 2-step chain measures fixed overhead (model load, hashing, the two gas references, the builder), not relaxation cost, so the ensemble checkpoints carry the MPA-0 planning figure until their first gated manifest lands; that realised figure is reported before the other five of that checkpoint are treated as planned. The realised figure — per manifest `seconds`, runner wall time from results/site_census_2026-09-06/status.json — is reported beside this planning figure, as the 5.8x miss of the q333 pair was (docs/43:4453-4456). The earlier smoke of the runner itself (a steps = 2 mpa0 manifest through site_census_runner.py, one worker): 35.0 s wall, 32.719 s inside the candidate, status complete; deleted."

`docs/91:86` (risk 8) verbatim: "8. Ensemble checkpoint cost. The CENSUS-2 checkpoints have no measured per-step cost (the 2-step smokes of (e) measure overhead only); the queue runs their gated six before their other six so that the first realised manifest per checkpoint is available before the bulk of that checkpoint's cost is spent."

Realised: `results[0].seconds` of each result file (the endmember: the sum over `results[i].seconds`) and the `=== <iso> launch:` / `=== <iso> exit <code>` stamps of `logs/<stem>.log`, printed as UTC `Z`; a log without an exit line, or a landed stem without a log, is marked as such and no file time stands in for the stamp. CENSUS-1 mean = mean of the twelve `mpa0__` `seconds` = 18126.3 s (reproduces `docs/93:166`).

**Table E1** (`manifests_read` order): | manifest | model (`manifest.model.filename`) | launch (UTC, log) | exit (UTC, log) | `seconds` | h | `seconds` / n sites | realised / planning 10257.948-6132.192 s | / CENSUS-1 mean |

| manifest | model | launch (UTC, log) | exit (UTC, log) | seconds | h | seconds / n sites | realised / planning | / CENSUS-1 mean |
|---|---|---|---|---|---|---|---|---|
| mpa0__Ni31Cr29Cu5Mn35 | macempa0mediummodel | 2026-09-07T03:28:35Z | 2026-09-07T08:18:08Z (exit 0) | 17364.766 | 4.82 | 1447.1 (12 sites) | 1.69x-2.83x | 0.96x |
| mpa0__Fe25Co25Ni25Cr25 | macempa0mediummodel | 2026-09-07T03:28:35Z | 2026-09-07T08:19:08Z (exit 0) | 17424.516 | 4.84 | 1452.0 (12 sites) | 1.70x-2.84x | 0.96x |
| mpa0__Cu26Ni9Cr31Co33 | macempa0mediummodel | 2026-09-07T03:28:35Z | 2026-09-07T10:05:47Z (exit 0) | 23828.031 | 6.62 | 1985.7 (12 sites) | 2.32x-3.89x | 1.31x |
| mpa0__Ni34Fe6Cu29Co31 | macempa0mediummodel | 2026-09-07T03:28:35Z | 2026-09-07T09:20:49Z (exit 0) | 21127.625 | 5.87 | 1760.6 (12 sites) | 2.06x-3.45x | 1.17x |
| mpa0__Cu8Cr23Mn35Co34 | macempa0mediummodel | 2026-09-07T08:18:08Z | 2026-09-07T13:13:04Z (exit 0) | 17680.500 | 4.91 | 1473.4 (12 sites) | 1.72x-2.88x | 0.98x |
| mpa0__Cu22Fe30Co32Mn15 | macempa0mediummodel | 2026-09-07T08:19:08Z | 2026-09-07T12:34:46Z (exit 0) | 15334.453 | 4.26 | 1277.9 (12 sites) | 1.49x-2.50x | 0.85x |
| mpa0__Cr33Co5Ni29Cu33 | macempa0mediummodel | 2026-09-07T09:20:49Z | no exit line | 19749.704 | 5.49 | 1645.8 (12 sites) | 1.93x-3.22x | 1.09x |
| mpa0__Mn31Ni31Co33Cu6 | macempa0mediummodel | 2026-09-07T10:05:47Z | no exit line | 15912.609 | 4.42 | 1326.1 (12 sites) | 1.55x-2.59x | 0.88x |
| mpa0__Fe31Cu25Cr13Ni31 | macempa0mediummodel | 2026-09-07T12:34:46Z | no exit line | 19534.266 | 5.43 | 1627.9 (12 sites) | 1.90x-3.19x | 1.08x |
| mpa0__Mn34Cu7Fe33Cr27 | macempa0mediummodel | 2026-09-07T13:13:04Z | no exit line | 16025.546 | 4.45 | 1335.5 (12 sites) | 1.56x-2.61x | 0.88x |
| mpa0__Co5Cu33Ni28Mn34 | macempa0mediummodel | 2026-09-07T14:31:03Z | 2026-09-07T20:11:57Z (exit 0) | 20448.047 | 5.68 | 1704.0 (12 sites) | 1.99x-3.33x | 1.13x |
| mpa0__Ni34Fe29Mn30Co7 | macempa0mediummodel | 2026-09-07T14:50:01Z | 2026-09-07T18:28:12Z (exit 0) | 13085.141 | 3.63 | 1090.4 (12 sites) | 1.28x-2.13x | 0.72x |
| endmember_2x2__mpa0 (7 candidates) | macempa0mediummodel | 2026-09-07T17:40:15Z | 2026-09-07T18:59:42Z (exit 0) | 4756.422 | 1.32 | — | vs 3552.3 s planned: 1.34x | — |
| omat0__Ni31Cr29Cu5Mn35 | maceomat0mediummodel | 2026-09-07T18:00:23Z | 2026-09-07T20:59:50Z (exit 0) | 10759.547 | 2.99 | 896.6 (12 sites) | 1.05x-1.75x | 0.59x |
| omat0__Fe25Co25Ni25Cr25 | maceomat0mediummodel | 2026-09-07T18:28:12Z | 2026-09-07T21:41:37Z (exit 0) | 11598.907 | 3.22 | 966.6 (12 sites) | 1.13x-1.89x | 0.64x |
| omat0__Cu26Ni9Cr31Co33 | maceomat0mediummodel | 2026-09-07T18:59:42Z | 2026-09-07T23:08:01Z (exit 0) | 14893.031 | 4.14 | 1241.1 (12 sites) | 1.45x-2.43x | 0.82x |
| omat0__Ni34Fe6Cu29Co31 | maceomat0mediummodel | 2026-09-07T20:11:57Z | 2026-09-07T23:36:52Z (exit 0) | 12286.687 | 3.41 | 1023.9 (12 sites) | 1.20x-2.00x | 0.68x |
| omat0__Cu8Cr23Mn35Co34 | maceomat0mediummodel | 2026-09-07T20:59:50Z | 2026-09-07T23:22:44Z (exit 0) | 8567.765 | 2.38 | 714.0 (12 sites) | 0.84x-1.40x | 0.47x |
| omat0__Cu22Fe30Co32Mn15 | maceomat0mediummodel | 2026-09-07T21:41:37Z | 2026-09-08T00:30:42Z (exit 0) | 10139.235 | 2.82 | 844.9 (12 sites) | 0.99x-1.65x | 0.56x |
| mp0__Ni31Cr29Cu5Mn35 | 20231203mace128L1_epoch199model | 2026-09-07T23:08:01Z | 2026-09-08T03:01:16Z (exit 0) | 13986.922 | 3.89 | 1165.6 (12 sites) | 1.36x-2.28x | 0.77x |
| mp0__Fe25Co25Ni25Cr25 | 20231203mace128L1_epoch199model | 2026-09-07T23:22:44Z | 2026-09-08T03:11:41Z (exit 0) | 13729.344 | 3.81 | 1144.1 (12 sites) | 1.34x-2.24x | 0.76x |
| mp0__Cu26Ni9Cr31Co33 | 20231203mace128L1_epoch199model | 2026-09-07T23:36:52Z | 2026-09-08T03:48:09Z (exit 0) | 15068.391 | 4.19 | 1255.7 (12 sites) | 1.47x-2.46x | 0.83x |
| mp0__Ni34Fe6Cu29Co31 | 20231203mace128L1_epoch199model | 2026-09-08T00:30:42Z | 2026-09-08T04:21:31Z (exit 0) | 13844.172 | 3.85 | 1153.7 (12 sites) | 1.35x-2.26x | 0.76x |
| mp0__Cu8Cr23Mn35Co34 | 20231203mace128L1_epoch199model | 2026-09-08T03:01:16Z | 2026-09-08T06:52:50Z (exit 0) | 13888.422 | 3.86 | 1157.4 (12 sites) | 1.35x-2.26x | 0.77x |
| mp0__Cu22Fe30Co32Mn15 | 20231203mace128L1_epoch199model | 2026-09-08T03:11:41Z | 2026-09-08T06:34:55Z (exit 0) | 12187.157 | 3.39 | 1015.6 (12 sites) | 1.19x-1.99x | 0.67x |
| matpes__Ni31Cr29Cu5Mn35 | MACEmatpesr2scanomatftmodel | 2026-09-08T03:48:09Z | 2026-09-08T06:49:29Z (exit 0) | 10873.125 | 3.02 | 906.1 (12 sites) | 1.06x-1.77x | 0.60x |
| matpes__Fe25Co25Ni25Cr25 | MACEmatpesr2scanomatftmodel | 2026-09-08T04:21:31Z | 2026-09-08T06:43:02Z (exit 0) | 8486.125 | 2.36 | 707.2 (12 sites) | 0.83x-1.38x | 0.47x |
| matpes__Cu26Ni9Cr31Co33 | MACEmatpesr2scanomatftmodel | 2026-09-08T06:34:55Z | 2026-09-08T11:06:43Z (exit 0) | 16297.968 | 4.53 | 1358.2 (12 sites) | 1.59x-2.66x | 0.90x |
| matpes__Ni34Fe6Cu29Co31 | MACEmatpesr2scanomatftmodel | 2026-09-08T06:43:02Z | 2026-09-08T09:08:37Z (exit 0) | 8730.079 | 2.43 | 727.5 (12 sites) | 0.85x-1.42x | 0.48x |
| matpes__Cu8Cr23Mn35Co34 | MACEmatpesr2scanomatftmodel | 2026-09-08T06:49:29Z | 2026-09-08T09:13:39Z (exit 0) | 8646.953 | 2.40 | 720.6 (12 sites) | 0.84x-1.41x | 0.48x |
| matpes__Cu22Fe30Co32Mn15 | MACEmatpesr2scanomatftmodel | 2026-09-08T06:52:50Z | 2026-09-08T09:09:07Z (exit 0) | 8173.610 | 2.27 | 681.1 (12 sites) | 0.80x-1.33x | 0.45x |
| omat0__Cr33Co5Ni29Cu33 | maceomat0mediummodel | 2026-09-08T09:08:37Z | 2026-09-08T13:22:02Z (exit 0) | 15195.906 | 4.22 | 1266.3 (12 sites) | 1.48x-2.48x | 0.84x |
| omat0__Mn31Ni31Co33Cu6 | maceomat0mediummodel | 2026-09-08T09:09:07Z | 2026-09-08T11:57:37Z (exit 0) | 10105.625 | 2.81 | 842.1 (12 sites) | 0.99x-1.65x | 0.56x |
| omat0__Fe31Cu25Cr13Ni31 | maceomat0mediummodel | 2026-09-08T09:13:39Z | 2026-09-08T12:05:19Z (exit 0) | 10293.766 | 2.86 | 857.8 (12 sites) | 1.00x-1.68x | 0.57x |
| omat0__Mn34Cu7Fe33Cr27 | maceomat0mediummodel | 2026-09-08T11:06:43Z | 2026-09-08T13:44:59Z (exit 0) | 9491.500 | 2.64 | 791.0 (12 sites) | 0.93x-1.55x | 0.52x |
| omat0__Co5Cu33Ni28Mn34 | maceomat0mediummodel | 2026-09-08T11:57:37Z | 2026-09-08T14:17:29Z (exit 0) | 8387.109 | 2.33 | 698.9 (12 sites) | 0.82x-1.37x | 0.46x |
| omat0__Ni34Fe29Mn30Co7 | maceomat0mediummodel | 2026-09-08T12:05:19Z | 2026-09-08T15:16:13Z (exit 0) | 11449.782 | 3.18 | 954.1 (12 sites) | 1.12x-1.87x | 0.63x |
| mp0__Cr33Co5Ni29Cu33 | 20231203mace128L1_epoch199model | 2026-09-08T13:22:02Z | 2026-09-08T17:45:06Z (exit 0) | 15773.188 | 4.38 | 1314.4 (12 sites) | 1.54x-2.57x | 0.87x |
| mp0__Mn31Ni31Co33Cu6 | 20231203mace128L1_epoch199model | 2026-09-08T13:44:59Z | 2026-09-08T17:41:55Z (exit 0) | 14208.641 | 3.95 | 1184.1 (12 sites) | 1.39x-2.32x | 0.78x |
| mp0__Fe31Cu25Cr13Ni31 | 20231203mace128L1_epoch199model | 2026-09-08T14:17:29Z | 2026-09-08T18:14:16Z (exit 0) | 14201.172 | 3.94 | 1183.4 (12 sites) | 1.38x-2.32x | 0.78x |
| mp0__Mn34Cu7Fe33Cr27 | 20231203mace128L1_epoch199model | 2026-09-08T15:16:13Z | 2026-09-08T18:23:10Z (exit 0) | 11211.953 | 3.11 | 934.3 (12 sites) | 1.09x-1.83x | 0.62x |
| mp0__Co5Cu33Ni28Mn34 | 20231203mace128L1_epoch199model | 2026-09-08T17:41:55Z | 2026-09-08T20:55:53Z (exit 0) | 11632.547 | 3.23 | 969.4 (12 sites) | 1.13x-1.90x | 0.64x |
| mp0__Ni34Fe29Mn30Co7 | 20231203mace128L1_epoch199model | 2026-09-08T17:45:06Z | 2026-09-08T21:21:23Z (exit 0) | 12970.281 | 3.60 | 1080.9 (12 sites) | 1.26x-2.12x | 0.72x |
| matpes__Cr33Co5Ni29Cu33 | MACEmatpesr2scanomatftmodel | 2026-09-08T18:14:16Z | 2026-09-08T22:19:16Z (exit 0) | 14691.969 | 4.08 | 1224.3 (12 sites) | 1.43x-2.40x | 0.81x |
| matpes__Mn31Ni31Co33Cu6 | MACEmatpesr2scanomatftmodel | 2026-09-08T18:23:10Z | 2026-09-08T20:16:29Z (exit 0) | 6794.719 | 1.89 | 566.2 (12 sites) | 0.66x-1.11x | 0.37x |
| matpes__Fe31Cu25Cr13Ni31 | MACEmatpesr2scanomatftmodel | 2026-09-08T20:16:29Z | 2026-09-08T23:33:16Z (exit 0) | 11800.516 | 3.28 | 983.4 (12 sites) | 1.15x-1.92x | 0.65x |
| matpes__Mn34Cu7Fe33Cr27 | MACEmatpesr2scanomatftmodel | 2026-09-08T20:55:53Z | 2026-09-09T00:07:00Z (exit 0) | 11458.719 | 3.18 | 954.9 (12 sites) | 1.12x-1.87x | 0.63x |
| matpes__Co5Cu33Ni28Mn34 | MACEmatpesr2scanomatftmodel | 2026-09-08T21:21:23Z | 2026-09-08T23:40:54Z (exit 0) | 8365.265 | 2.32 | 697.1 (12 sites) | 0.82x-1.36x | 0.46x |
| matpes__Ni34Fe29Mn30Co7 | MACEmatpesr2scanomatftmodel | 2026-09-08T22:19:16Z | 2026-09-09T01:18:41Z (exit 0) | 10754.875 | 2.99 | 896.2 (12 sites) | 1.05x-1.75x | 0.59x |
| mpa0_ext__Ni31Cr29Cu5Mn35__s03-05 | macempa0mediummodel | 2026-09-08T23:33:16Z | 2026-09-09T04:12:17Z (exit 0) | 16732.750 | 4.65 | 1394.4 (12 sites) | 1.63x-2.73x | 0.92x |
| mpa0_ext__Ni31Cr29Cu5Mn35__s06-08 | macempa0mediummodel | 2026-09-08T23:40:54Z | 2026-09-09T05:34:38Z (exit 0) | 21215.391 | 5.89 | 1767.9 (12 sites) | 2.07x-3.46x | 1.17x |
| mpa0_ext__Ni31Cr29Cu5Mn35__s09-11 | macempa0mediummodel | 2026-09-09T00:07:00Z | 2026-09-09T05:31:26Z (exit 0) | 19460.250 | 5.41 | 1621.7 (12 sites) | 1.90x-3.17x | 1.07x |
| mpa0_ext__Ni31Cr29Cu5Mn35__s12-14 | macempa0mediummodel | 2026-09-09T01:18:41Z | 2026-09-09T06:15:06Z (exit 0) | 17772.547 | 4.94 | 1481.0 (12 sites) | 1.73x-2.90x | 0.98x |
| mpa0_ext__Ni31Cr29Cu5Mn35__s15-17 | macempa0mediummodel | 2026-09-09T04:12:17Z | 2026-09-09T08:49:29Z (exit 0) | 16625.797 | 4.62 | 1385.5 (12 sites) | 1.62x-2.71x | 0.92x |
| mpa0_ext__Ni31Cr29Cu5Mn35__s18-20 | macempa0mediummodel | 2026-09-09T05:31:26Z | 2026-09-09T10:55:04Z (exit 0) | 19412.515 | 5.39 | 1617.7 (12 sites) | 1.89x-3.17x | 1.07x |
| mpa0_ext__Ni31Cr29Cu5Mn35__s21-23 | macempa0mediummodel | 2026-09-09T05:34:38Z | 2026-09-09T10:44:49Z (exit 0) | 18602.687 | 5.17 | 1550.2 (12 sites) | 1.81x-3.03x | 1.03x |
| mpa0_ext__Ni31Cr29Cu5Mn35__s24-26 | macempa0mediummodel | 2026-09-09T06:15:06Z | 2026-09-09T11:22:53Z (exit 0) | 18462.000 | 5.13 | 1538.5 (12 sites) | 1.80x-3.01x | 1.02x |
| mpa0_ext__Ni31Cr29Cu5Mn35__s27-29 | macempa0mediummodel | 2026-09-09T08:49:29Z | 2026-09-09T13:22:21Z (exit 0) | 16357.860 | 4.54 | 1363.2 (12 sites) | 1.59x-2.67x | 0.90x |
| mpa0_ext__Fe25Co25Ni25Cr25__s03-05 | macempa0mediummodel | 2026-09-09T10:44:49Z | 2026-09-09T15:54:10Z (exit 0) | 18547.703 | 5.15 | 1545.6 (12 sites) | 1.81x-3.02x | 1.02x |
| mpa0_ext__Fe25Co25Ni25Cr25__s06-08 | macempa0mediummodel | 2026-09-09T10:55:04Z | 2026-09-09T15:10:35Z (exit 0) | 15320.594 | 4.26 | 1276.7 (12 sites) | 1.49x-2.50x | 0.85x |
| mpa0_ext__Fe25Co25Ni25Cr25__s09-11 | macempa0mediummodel | 2026-09-09T11:22:53Z | 2026-09-09T16:17:16Z (exit 0) | 17658.031 | 4.91 | 1471.5 (12 sites) | 1.72x-2.88x | 0.97x |
| mpa0_ext__Fe25Co25Ni25Cr25__s12-14 | macempa0mediummodel | 2026-09-09T13:22:21Z | 2026-09-09T17:59:12Z (exit 0) | 16598.687 | 4.61 | 1383.2 (12 sites) | 1.62x-2.71x | 0.92x |
| mpa0_ext__Fe25Co25Ni25Cr25__s15-17 | macempa0mediummodel | 2026-09-09T15:10:35Z | 2026-09-09T20:25:33Z (exit 0) | 18892.234 | 5.25 | 1574.4 (12 sites) | 1.84x-3.08x | 1.04x |
| mpa0_ext__Fe25Co25Ni25Cr25__s18-20 | macempa0mediummodel | 2026-09-09T15:54:10Z | 2026-09-09T21:43:31Z (exit 0) | 20952.437 | 5.82 | 1746.0 (12 sites) | 2.04x-3.42x | 1.16x |
| mpa0_ext__Fe25Co25Ni25Cr25__s21-23 | macempa0mediummodel | 2026-09-09T16:17:16Z | 2026-09-09T21:34:11Z (exit 0) | 19005.156 | 5.28 | 1583.8 (12 sites) | 1.85x-3.10x | 1.05x |
| mpa0_ext__Fe25Co25Ni25Cr25__s24-26 | macempa0mediummodel | 2026-09-09T17:59:12Z | 2026-09-09T22:23:07Z (exit 0) | 15825.344 | 4.40 | 1318.8 (12 sites) | 1.54x-2.58x | 0.87x |
| mpa0_ext__Fe25Co25Ni25Cr25__s27-29 | macempa0mediummodel | 2026-09-09T20:25:33Z | 2026-09-10T01:56:42Z (exit 0) | 19858.891 | 5.52 | 1654.9 (12 sites) | 1.94x-3.24x | 1.10x |
| mpa0_ext__Cu26Ni9Cr31Co33__s03-05 | macempa0mediummodel | 2026-09-09T21:34:11Z | 2026-09-10T02:39:52Z (exit 0) | 18329.938 | 5.09 | 1527.5 (12 sites) | 1.79x-2.99x | 1.01x |
| mpa0_ext__Cu26Ni9Cr31Co33__s06-08 | macempa0mediummodel | 2026-09-09T21:43:31Z | 2026-09-10T02:14:46Z (exit 0) | 16265.312 | 4.52 | 1355.4 (12 sites) | 1.59x-2.65x | 0.90x |
| mpa0_ext__Cu26Ni9Cr31Co33__s09-11 | macempa0mediummodel | 2026-09-09T22:23:07Z | 2026-09-10T03:31:59Z (exit 0) | 18519.891 | 5.14 | 1543.3 (12 sites) | 1.81x-3.02x | 1.02x |
| mpa0_ext__Cu26Ni9Cr31Co33__s12-14 | macempa0mediummodel | 2026-09-10T01:56:42Z | 2026-09-10T06:52:14Z (exit 0) | 17723.297 | 4.92 | 1476.9 (12 sites) | 1.73x-2.89x | 0.98x |
| mpa0_ext__Cu26Ni9Cr31Co33__s15-17 | macempa0mediummodel | 2026-09-10T02:14:46Z | 2026-09-10T06:58:03Z (exit 0) | 16991.329 | 4.72 | 1415.9 (12 sites) | 1.66x-2.77x | 0.94x |
| mpa0_ext__Cu26Ni9Cr31Co33__s18-20 | macempa0mediummodel | 2026-09-10T02:39:52Z | 2026-09-10T06:56:37Z (exit 0) | 15398.390 | 4.28 | 1283.2 (12 sites) | 1.50x-2.51x | 0.85x |
| mpa0_ext__Cu26Ni9Cr31Co33__s21-23 | macempa0mediummodel | 2026-09-10T11:47:20Z | 2026-09-10T18:57:04Z (exit 0) | 25775.563 | 7.16 | 2148.0 (12 sites) | 2.51x-4.20x | 1.42x |
| mpa0_ext__Cu26Ni9Cr31Co33__s24-26 | macempa0mediummodel | 2026-09-10T11:47:20Z | 2026-09-10T17:04:47Z (exit 0) | 19037.953 | 5.29 | 1586.5 (12 sites) | 1.86x-3.10x | 1.05x |
| mpa0_ext__Cu26Ni9Cr31Co33__s27-29 | macempa0mediummodel | 2026-09-10T11:47:20Z | 2026-09-10T17:02:40Z (exit 0) | 18911.203 | 5.25 | 1575.9 (12 sites) | 1.84x-3.08x | 1.04x |
| mpa0_ext__Ni34Fe6Cu29Co31__s03-05 | macempa0mediummodel | 2026-09-10T11:47:20Z | 2026-09-10T18:44:10Z (exit 0) | 25002.172 | 6.95 | 2083.5 (12 sites) | 2.44x-4.08x | 1.38x |
| mpa0_ext__Ni34Fe6Cu29Co31__s06-08 | macempa0mediummodel | 2026-09-10T17:02:40Z | 2026-09-10T23:01:42Z (exit 0) | 21533.046 | 5.98 | 1794.4 (12 sites) | 2.10x-3.51x | 1.19x |
| mpa0_ext__Ni34Fe6Cu29Co31__s09-11 | macempa0mediummodel | 2026-09-10T17:04:47Z | 2026-09-10T21:29:32Z (exit 0) | 15880.156 | 4.41 | 1323.3 (12 sites) | 1.55x-2.59x | 0.88x |
| mpa0_ext__Ni34Fe6Cu29Co31__s12-14 | macempa0mediummodel | 2026-09-10T18:44:10Z | 2026-09-10T23:24:29Z (exit 0) | 16810.204 | 4.67 | 1400.9 (12 sites) | 1.64x-2.74x | 0.93x |
| mpa0_ext__Ni34Fe6Cu29Co31__s15-17 | macempa0mediummodel | 2026-09-10T18:57:04Z | 2026-09-10T23:23:18Z (exit 0) | 15969.656 | 4.44 | 1330.8 (12 sites) | 1.56x-2.60x | 0.88x |
| mpa0_ext__Ni34Fe6Cu29Co31__s18-20 | macempa0mediummodel | 2026-09-10T21:29:32Z | 2026-09-11T02:17:23Z (exit 0) | 17262.453 | 4.80 | 1438.5 (12 sites) | 1.68x-2.82x | 0.95x |
| mpa0_ext__Ni34Fe6Cu29Co31__s21-23 | macempa0mediummodel | 2026-09-10T23:01:42Z | 2026-09-11T03:54:26Z (exit 0) | 17555.484 | 4.88 | 1463.0 (12 sites) | 1.71x-2.86x | 0.97x |
| mpa0_ext__Ni34Fe6Cu29Co31__s24-26 | macempa0mediummodel | 2026-09-10T23:23:18Z | 2026-09-11T05:09:19Z (exit 0) | 20756.032 | 5.77 | 1729.7 (12 sites) | 2.02x-3.38x | 1.15x |
| mpa0_ext__Ni34Fe6Cu29Co31__s27-29 | macempa0mediummodel | 2026-09-10T23:24:29Z | 2026-09-11T04:06:09Z (exit 0) | 16892.719 | 4.69 | 1407.7 (12 sites) | 1.65x-2.75x | 0.93x |
| mpa0_ext__Cu8Cr23Mn35Co34__s03-05 | macempa0mediummodel | 2026-09-11T02:17:23Z | 2026-09-11T12:54:51Z (exit 0) | 38241.829 | 10.62 | 3186.8 (12 sites) | 3.73x-6.24x | 2.11x |
| mpa0_ext__Cu8Cr23Mn35Co34__s06-08 | macempa0mediummodel | 2026-09-11T03:54:26Z | 2026-09-11T16:36:58Z (exit 0) | 45745.828 | 12.71 | 3812.2 (12 sites) | 4.46x-7.46x | 2.52x |
| mpa0_ext__Cu8Cr23Mn35Co34__s09-11 | macempa0mediummodel | 2026-09-11T04:06:09Z | 2026-09-11T17:16:02Z (exit 0) | 47389.469 | 13.16 | 3949.1 (12 sites) | 4.62x-7.73x | 2.61x |
| mpa0_ext__Cu8Cr23Mn35Co34__s12-14 | macempa0mediummodel | 2026-09-11T05:09:19Z | 2026-09-11T19:01:03Z (exit 0) | 49897.718 | 13.86 | 4158.1 (12 sites) | 4.86x-8.14x | 2.75x |
| mpa0_ext__Cu8Cr23Mn35Co34__s15-17 | macempa0mediummodel | 2026-09-11T12:54:51Z | 2026-09-11T20:55:56Z (exit 0) | 28857.828 | 8.02 | 2404.8 (12 sites) | 2.81x-4.71x | 1.59x |
| mpa0_ext__Cu8Cr23Mn35Co34__s18-20 | macempa0mediummodel | 2026-09-11T16:36:58Z | 2026-09-11T21:40:30Z (exit 0) | 18200.156 | 5.06 | 1516.7 (12 sites) | 1.77x-2.97x | 1.00x |
| mpa0_ext__Cu8Cr23Mn35Co34__s21-23 | macempa0mediummodel | 2026-09-11T17:16:02Z | 2026-09-11T22:31:42Z (exit 0) | 18933.547 | 5.26 | 1577.8 (12 sites) | 1.85x-3.09x | 1.04x |
| mpa0_ext__Cu8Cr23Mn35Co34__s24-26 | macempa0mediummodel | 2026-09-11T19:01:03Z | 2026-09-11T23:39:23Z (exit 0) | 16693.594 | 4.64 | 1391.1 (12 sites) | 1.63x-2.72x | 0.92x |
| mpa0_ext__Cu8Cr23Mn35Co34__s27-29 | macempa0mediummodel | 2026-09-11T20:55:56Z | 2026-09-12T00:39:59Z (exit 0) | 13435.110 | 3.73 | 1119.6 (12 sites) | 1.31x-2.19x | 0.74x |
| mpa0_ext__Cu22Fe30Co32Mn15__s03-05 | macempa0mediummodel | 2026-09-11T21:40:30Z | 2026-09-12T01:40:10Z (exit 0) | 14373.312 | 3.99 | 1197.8 (12 sites) | 1.40x-2.34x | 0.79x |
| mpa0_ext__Cu22Fe30Co32Mn15__s06-08 | macempa0mediummodel | 2026-09-11T22:31:42Z | 2026-09-12T02:16:41Z (exit 0) | 13492.313 | 3.75 | 1124.4 (12 sites) | 1.32x-2.20x | 0.74x |
| mpa0_ext__Cu22Fe30Co32Mn15__s09-11 | macempa0mediummodel | 2026-09-11T23:39:23Z | 2026-09-12T03:25:58Z (exit 0) | 13590.438 | 3.78 | 1132.5 (12 sites) | 1.32x-2.22x | 0.75x |
| mpa0_ext__Cu22Fe30Co32Mn15__s12-14 | macempa0mediummodel | 2026-09-12T00:39:59Z | 2026-09-12T04:05:43Z (exit 0) | 12339.672 | 3.43 | 1028.3 (12 sites) | 1.20x-2.01x | 0.68x |
| mpa0_ext__Cu22Fe30Co32Mn15__s15-17 | macempa0mediummodel | 2026-09-12T01:40:11Z | 2026-09-12T06:40:14Z (exit 0) | 17992.312 | 5.00 | 1499.4 (12 sites) | 1.75x-2.93x | 0.99x |
| mpa0_ext__Cu22Fe30Co32Mn15__s18-20 | macempa0mediummodel | 2026-09-12T02:16:41Z | 2026-09-12T06:14:33Z (exit 0) | 14263.625 | 3.96 | 1188.6 (12 sites) | 1.39x-2.33x | 0.79x |
| mpa0_ext__Cu22Fe30Co32Mn15__s21-23 | macempa0mediummodel | 2026-09-12T20:05:21Z | 2026-09-13T03:35:24Z (exit 0) | 26995.797 | 7.50 | 2249.6 (12 sites) | 2.63x-4.40x | 1.49x |
| mpa0_ext__Cu22Fe30Co32Mn15__s24-26 | macempa0mediummodel | 2026-09-12T20:05:21Z | 2026-09-13T02:46:31Z (exit 0) | 24061.093 | 6.68 | 2005.1 (12 sites) | 2.35x-3.92x | 1.33x |
| mpa0_ext__Cu22Fe30Co32Mn15__s27-29 | macempa0mediummodel | 2026-09-12T20:05:21Z | 2026-09-13T03:05:39Z (exit 0) | 25210.031 | 7.00 | 2100.8 (12 sites) | 2.46x-4.11x | 1.39x |

**Totals per checkpoint.** **mpa0 (CENSUS-1)**: 12 / 12 landed; sum 217515.204 s = 60.42 h; mean 18126.3 s = 5.04 h per manifest, min 13085.1 s (`mpa0__Ni34Fe29Mn30Co7`), max 23828.0 s (`mpa0__Cu26Ni9Cr31Co33`); mean / CENSUS-1 mean 1.00x; mean / planning band 1.77x-2.96x; **mpa0_ext (CENSUS-3)**: 54 / 54 landed; sum 1101629.344 s = 306.01 h; mean 20400.5 s = 5.67 h per manifest, min 12339.7 s (`mpa0_ext__Cu22Fe30Co32Mn15__s12-14`), max 49897.7 s (`mpa0_ext__Cu8Cr23Mn35Co34__s12-14`); mean / CENSUS-1 mean 1.13x; mean / planning band 1.99x-3.33x; **omat0**: 12 / 12 landed; sum 133168.860 s = 36.99 h; mean 11097.4 s = 3.08 h per manifest, min 8387.1 s (`omat0__Co5Cu33Ni28Mn34`), max 15195.9 s (`omat0__Cr33Co5Ni29Cu33`); mean / CENSUS-1 mean 0.61x; mean / planning band 1.08x-1.81x; **mp0**: 12 / 12 landed; sum 162702.190 s = 45.20 h; mean 13558.5 s = 3.77 h per manifest, min 11212.0 s (`mp0__Mn34Cu7Fe33Cr27`), max 15773.2 s (`mp0__Cr33Co5Ni29Cu33`); mean / CENSUS-1 mean 0.75x; mean / planning band 1.32x-2.21x; **matpes**: 12 / 12 landed; sum 125073.923 s = 34.74 h; mean 10422.8 s = 2.90 h per manifest, min 6794.7 s (`matpes__Mn31Ni31Co33Cu6`), max 16298.0 s (`matpes__Cu26Ni9Cr31Co33`); mean / CENSUS-1 mean 0.58x; mean / planning band 1.02x-1.70x; **endmember_2x2__mpa0**: 1 / 1; 4756.422 s = 1.32 h against the 3552.3 s of `r4_validate.json` (1.34x).

**Wall (post-hoc arithmetic).** First launch over the 103 landed logs 2026-09-07T03:28:35Z → last exit line over the 99 landed logs that carry one 2026-09-13T03:35:24Z = **144.11 h** — a log-stamp wall in place of the pre-stated `status.json` runner wall of `docs/91:67`, which this file does not open; 4 landed logs carry no exit line (`mpa0__Cr33Co5Ni29Cu33`, `mpa0__Mn31Ni31Co33Cu6`, `mpa0__Fe31Cu25Cr13Ni31`, `mpa0__Mn34Cu7Fe33Cr27`), and those stems are outside the wall. Against the `docs/91:67` planning wall of the arms represented (CENSUS-1 5.11-8.55 h; CENSUS-2 15.33-25.64 h; CENSUS-3 23.0-38.47 h). Candidate-seconds per wall-second = 1744845.943 / 518809 = **3.36** (sum of every landed `seconds`, endmember included), with the `docs/93:166` caveat that seconds accrued by workers still running at the readout stamp are in neither figure. The result files carry no BFGS step counts (`docs/93:166`), so per-manifest seconds mix throughput with work content and are not separated here.

**The `docs/91:67` ordering** ("that realised figure is reported before the other five of that checkpoint are treated as planned"), read post-hoc from log stamps (the logs are read at emit time and may carry launches later than the readout stamp) as the first exit of each tag against the launch stamps of its other five gated manifests: omat0: first exit `omat0__Ni31Cr29Cu5Mn35` 2026-09-07T20:59:50Z; launches of the other five before it: omat0__Fe25Co25Ni25Cr25 2026-09-07T18:28:12Z, omat0__Cu26Ni9Cr31Co33 2026-09-07T18:59:42Z, omat0__Ni34Fe6Cu29Co31 2026-09-07T20:11:57Z; after it: omat0__Cu8Cr23Mn35Co34 2026-09-07T20:59:50Z, omat0__Cu22Fe30Co32Mn15 2026-09-07T21:41:37Z; no log yet: none — not met by launch order (3 of the other five launched before that exit); `docs/93:266` reads that the ordering "was not met" — a reporting-time reading of the same rule, cited beside this launch-order one and not compared with it; mp0: first exit `mp0__Ni31Cr29Cu5Mn35` 2026-09-08T03:01:16Z; launches of the other five before it: mp0__Fe25Co25Ni25Cr25 2026-09-07T23:22:44Z, mp0__Cu26Ni9Cr31Co33 2026-09-07T23:36:52Z, mp0__Ni34Fe6Cu29Co31 2026-09-08T00:30:42Z; after it: mp0__Cu8Cr23Mn35Co34 2026-09-08T03:01:16Z, mp0__Cu22Fe30Co32Mn15 2026-09-08T03:11:41Z; no log yet: none — not met by launch order (3 of the other five launched before that exit); matpes: first exit `matpes__Fe25Co25Ni25Cr25` 2026-09-08T06:43:02Z; launches of the other five before it: matpes__Ni31Cr29Cu5Mn35 2026-09-08T03:48:09Z, matpes__Cu26Ni9Cr31Co33 2026-09-08T06:34:55Z; after it: matpes__Ni34Fe6Cu29Co31 2026-09-08T06:43:02Z, matpes__Cu8Cr23Mn35Co34 2026-09-08T06:49:29Z, matpes__Cu22Fe30Co32Mn15 2026-09-08T06:52:50Z; no log yet: none — not met by launch order (2 of the other five launched before that exit).

**Contention (named risk 1, `docs/91:79`).** Only what the logs of the landed stems show is used above (launch and exit stamps); the runner restart, the power-throttling interval and the orphaned workers are the events of `docs/93:170-171`, cited and not re-derived (`status.json` `runner_started` is not read by this file).

## (f) SITE-ETA DISTRIBUTION per gated composition (`readout/distribution.json` `distribution.per_formula.<f>`)

`docs/91:69` verbatim: "**(f) SITE-ETA DISTRIBUTION (CENSUS-3 with CENSUS-1).** Per gated composition, over its MACE-MPA-0 sites from CENSUS-1 (seeds 0-2) and CENSUS-3 (seeds 3-29), 120 sites when complete: n; mean; sample standard deviation (ddof = 1); median; 10th percentile (linear interpolation); minimum; maximum — once over all sites and once over INTACT sites — the number of unconverged sites, the O-O band counts and the O-O distance statistics of the OOH endpoints, and the exact expected minimum of k sites drawn without replacement from the empirical site set, E[min_k] = sum_i x_(i) C(n−i, k−1) / C(n, k) over the ascending order statistics, for k = 1, 2, 3, 4, 6, 12, 24, 48, 96, 120, with the twelve-site minimum of CENSUS-1 printed beside the k = 12 value as one draw from that curve. No bar is set on any of these; the readout exists so that the composition value of record (a 12-site minimum) can be seen against the site population it was drawn from, and so that the site-to-site sigma can be compared with the 0.19-0.27 eV (Potter) and ~0.5 eV (Baek) spreads of §1."

`distribution.site_set`: CENSUS-1 (seeds 0-2) and CENSUS-3 (seeds 3-29) MACE-MPA-0 sites of the gated six. `distribution.statistics`: mean; sample standard deviation (ddof = 1); median; 10th percentile (linear interpolation); min; max; expected minimum of k draws without replacement from the empirical site set, exact.

**Table F1** (`manifests`, `n_sites`, `n_unconverged_sites`, `all_sites.{n, mean, std, median, p10, min, max}`, `intact_sites.{...}`, `twelve_site_min_V`):

| composition | manifests landed (of 10) | n / unconverged | mean | std | median | p10 | min | max | INTACT n | INTACT mean | INTACT std | INTACT median | INTACT p10 | INTACT min | INTACT max | twelve_site_min_V |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 10 | 120 / 3 | 1.0140754099305964 | 0.23544011681940277 | 1.0636215667684747 | 0.6857593581363084 | 0.4399960638886986 | 1.598591364767402 | 3 | 1.0831486665265908 | 0.14075120148524226 | 1.0994745463015914 | 0.967852066532173 | 0.9349464465898185 | 1.2150250066883626 | 0.4399960638886986 |
| Fe25Co25Ni25Cr25 | 10 | 120 / 5 | 1.0305335553778923 | 0.276953080072374 | 1.0359351350452055 | 0.6563876633672938 | 0.4530565522419163 | 1.8504808924130765 | 11 | 1.1693515004551147 | 0.17869729379043817 | 1.2293487396470066 | 0.9033552626798649 | 0.8637036860196456 | 1.3569616833799198 | 0.4530565522419163 |
| Cu26Ni9Cr31Co33 | 10 | 120 / 3 | 0.8725209393813259 | 0.22873300125420917 | 0.8630688595672349 | 0.6100416171169606 | 0.4491684937492817 | 1.9780766670756287 | 6 | 0.9018936380806895 | 0.23271512448355458 | 0.9198856028358744 | 0.6585355921972167 | 0.5936955227013225 | 1.2601538435706328 | 0.4791918879560475 |
| Ni34Fe6Cu29Co31 | 10 | 120 / 5 | 0.9965816652642783 | 0.2533764079411902 | 0.9403118949783074 | 0.7512312370186314 | 0.6071660769726472 | 2.147914980095481 | 15 | 0.9652606865062096 | 0.16054152022823312 | 0.9615557456723689 | 0.7387097348381626 | 0.6790912935495492 | 1.2254775956805286 | 0.7258416589359067 |
| Cu8Cr23Mn35Co34 | 10 | 120 / 3 | 0.9543819215276454 | 0.2271542401856481 | 0.9907774788574368 | 0.5706091801589954 | 0.3622195377546671 | 1.2802728101548535 | 4 | 0.9335073312552833 | 0.22887956627784092 | 0.9405996983387848 | 0.7278622910935308 | 0.7159027265388698 | 1.1369272018046939 | 0.7557679417210732 |
| Cu22Fe30Co32Mn15 | 10 | 120 / 5 | 1.0494893211972791 | 0.21482872715592694 | 1.0499502624908095 | 0.8050174117376667 | 0.45594879091650764 | 2.16430707623009 | 33 | 1.1266872883385195 | 0.19654627703141422 | 1.209540229659778 | 0.8480415633179474 | 0.6855536132758706 | 1.352625879567908 | 0.7956531821512538 |

**Table F2** (`expected_min_vs_k[].{k, expected_min}`; `twelve_site_min_V` printed beside k = 12, `docs/91:69`: "printed beside the k = 12 value as one draw from that curve"; `o_o_A.{...}`, `o_o_class_counts`):

| composition | E[min_1] | E[min_2] | E[min_3] | E[min_4] | E[min_6] | E[min_12] ‖ twelve-site min | E[min_24] | E[min_48] | E[min_96] | E[min_120] | OOH O-O (A): n, mean, std, median, p10, min, max | O-O class counts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 1.0140754099305964 | 0.8826739154057479 | 0.8120356837944231 | 0.7636903485812283 | 0.6996968508180913 | 0.6068625940552372 ‖ 0.4399960638886986 | 0.5341935484680692 | 0.47866574879059987 | 0.44658190155636024 | 0.4399960638886986 | 120, 1.246666521382743, 0.03617032852610459, 1.2354254787933878, 1.2286280041123239, 1.2232423606668505, 1.3836242786786723 | O2_LIKE 108, OOH_LIKE 5, SUPEROXO_LIKE 7 |
| Fe25Co25Ni25Cr25 | 1.0305335553778923 | 0.8727057520445644 | 0.7946879173058424 | 0.745569963516985 | 0.6854708965453055 | 0.6048079947574148 ‖ 0.4530565522419163 | 0.5465824191750427 | 0.5029894542818205 | 0.46415268826955974 | 0.4530565522419163 | 120, 1.2689592956454978, 0.05706766782097143, 1.2340503689277513, 1.22828978416441, 1.2216982145437532, 1.4087801762168766 | O2_LIKE 84, OOH_LIKE 12, SUPEROXO_LIKE 24 |
| Cu26Ni9Cr31Co33 | 0.8725209393813259 | 0.7484661920869174 | 0.6937261811227602 | 0.65983022573689 | 0.6174497066769699 | 0.5579582342623927 ‖ 0.4791918879560475 | 0.5117392960548361 | 0.47717643495883577 | 0.4547980739429963 | 0.4491684937492817 | 120, 1.2565848401680024, 0.050740855017907045, 1.2346238986294573, 1.2300512465740527, 1.2244471711866622, 1.415862827507119 | O2_LIKE 99, OOH_LIKE 10, SUPEROXO_LIKE 11 |
| Ni34Fe6Cu29Co31 | 0.9965816652642784 | 0.8640821707842241 | 0.8126698831042063 | 0.7834687219539339 | 0.7498987280017743 | 0.7062963472347411 ‖ 0.7258416589359067 | 0.6721126859843461 | 0.6427108614549377 | 0.6158192450688521 | 0.6071660769726472 | 120, 1.248591517608477, 0.04352621010302054, 1.2315782994394833, 1.224737985257762, 1.222138074453097, 1.358781683751386 | O2_LIKE 101, SUPEROXO_LIKE 19 |
| Cu8Cr23Mn35Co34 | 0.9543819215276454 | 0.8315674450553574 | 0.756892846541978 | 0.7031492452429566 | 0.6267732360019486 | 0.5028434197558397 ‖ 0.7557679417210732 | 0.4152410811739435 | 0.3791593477759377 | 0.3661640892822486 | 0.3622195377546671 | 120, 1.2550419348247526, 0.05096171168232188, 1.2333705739925145, 1.2308540856769574, 1.2263364604633, 1.3818007881345382 | O2_LIKE 101, OOH_LIKE 18, SUPEROXO_LIKE 1 |
| Cu22Fe30Co32Mn15 | 1.0494893211972791 | 0.9345966716081605 | 0.8761485458714571 | 0.8377821497390491 | 0.7875353480711595 | 0.7058301283822618 ‖ 0.7956531821512538 | 0.6224186738570883 | 0.541557440880611 | 0.4751147017035726 | 0.45594879091650764 | 120, 1.2705439600101522, 0.053787974629675245, 1.2350571985815872, 1.2293417358339738, 1.222972887983976, 1.363894322715663 | O2_LIKE 79, OOH_LIKE 2, SUPEROXO_LIKE 39 |

The site-to-site sample sd spans 0.2148-0.2770 V across the six (n = 120 per composition; `all_sites.std`, ddof = 1), beside the site-energy spreads `docs/91:44` names: "120 permutations per active site with a ~0.5 eV spread (Baek et al., Nat. Commun. 2023, 10.1038/s41467-023-41359-7); 768 sites per composition with site-energy sigma 0.19-0.27 eV (Potter et al., arXiv:2504.11587)" (`docs/91:44`, `:69`). No bar is set on any of these (`docs/91:69`).
Ni31Cr29Cu5Mn35: sd 0.23544011681940277 V lies inside 0.19-0.27 and below 0.5 (descriptive placement, `docs/91:69`); Fe25Co25Ni25Cr25: sd 0.276953080072374 V lies above 0.19-0.27 and below 0.5 (descriptive placement, `docs/91:69`); Cu26Ni9Cr31Co33: sd 0.22873300125420917 V lies inside 0.19-0.27 and below 0.5 (descriptive placement, `docs/91:69`); Ni34Fe6Cu29Co31: sd 0.2533764079411902 V lies inside 0.19-0.27 and below 0.5 (descriptive placement, `docs/91:69`); Cu8Cr23Mn35Co34: sd 0.2271542401856481 V lies inside 0.19-0.27 and below 0.5 (descriptive placement, `docs/91:69`); Cu22Fe30Co32Mn15: sd 0.21482872715592694 V lies inside 0.19-0.27 and below 0.5 (descriptive placement, `docs/91:69`).

Post-hoc: sd of the 12-site slice against the landed n-site value — Ni31Cr29Cu5Mn35: 12-site sd 0.33841073880772743 (`docs/93:181`, cited) against 0.23544011681940277 at n = 120; Fe25Co25Ni25Cr25: 12-site sd 0.3425629199920179 (`docs/93:182`, cited) against 0.276953080072374 at n = 120; Cu26Ni9Cr31Co33: 12-site sd 0.2853300160529606 (`docs/93:183`, cited) against 0.22873300125420917 at n = 120; Ni34Fe6Cu29Co31: 12-site sd 0.20279091187652185 (`docs/93:184`, cited) against 0.2533764079411902 at n = 120; Cu8Cr23Mn35Co34: 12-site sd 0.14097909055842525 (`docs/93:185`, cited) against 0.2271542401856481 at n = 120; Cu22Fe30Co32Mn15: 12-site sd 0.19216949113478188 (`docs/93:186`, cited) against 0.21482872715592694 at n = 120.

## Rank resolution (spec:41-92) — one block per admission policy, then T7 and T8

Command of record, spec:45 verbatim: `python src/scripts/rank_resolution_readout.py --results results/site_census_2026-09-06/results/ --gated results/ranking_adequacy_2026-09-06/inputs/r4_gated.json --B 10000 --seed 0 --admit all --out results/site_census_2026-09-06/readout/rank_resolution.json`

spec:47 verbatim: "run once per admission policy (`--admit all` primary; `--admit no-desorbed`, `--admit intact`, `--admit adsorbate-intact`, `--admit two-pathway` secondary, each to its own `--out`, e.g. `rank_resolution_intact.json`), then"

Input guards, spec:51 verbatim: "Input guards, all fail-closed: only stems matching `--stems` (default `mpa0__*,mpa0_ext__*`, i.e. the MACE-MPA-0 P-CENSUS-1 and P-CENSUS-3 manifests; the endmember and ensemble stems are excluded) are read; a result whose `manifest_id` differs from `manifests/<stem>.json`, whose stem is absent from `MANIFESTS.sha256`, or whose status is not `complete`/`complete_with_errors` is refused and listed under `coverage.refused`; two model files in one table are refused (exit 2); when any expected stem of the selected set is missing the readout refuses to run unless `--partial`, and a partial readout carries `status: partial` with the missing stems under `coverage.missing`. Exit 3 with the message `insufficient decorations` if any composition has fewer than the minimum usable decorations; the census statistics are still written, no interval is invented."

R7, spec:74 verbatim: "- **R7 (no movement).** No banked value changes. The census `min` over the banked seeds per composition is the reproduction check of T2 against the banked `eta` at the bar inherited from docs/91 §2 (a) (1e-6 V; the retained equiatomic site reproduces within 4.5e-10 V); a difference above the bar is reported as NOT REPRODUCED for that composition, not as a new number, and the composition stays in every table with that label."

Elective settings (spec:78-89), every slot blank; the draft value is the spec's column 3 and the file value is `settings.<key>` of the policy files (identical across them, asserted where present):

| slot | setting | draft value (spec) | flag | file value |
|---|---|---|---|---|
| [RANK-1 order-probability target: ______] | P(order) at which a boundary is RESOLVED and a rank STABLE | 0.95 | `--target-prob` | `target_prob` 0.95 |
| [RANK-2 interval level: ______] | central percentile interval of the bootstrap | 0.90 | `--level` | `level` 0.9 |
| [RANK-3 ICC band: ______] | ICC above which R4 applies | 0.2 | applied at reading | applied at reading (no `settings` key) |
| [RANK-4 ridge site floor: ______] | sites below which the ridge is `insufficient_sites` (p + 2 = 14 is the algebraic floor) | 30 | `RIDGE_MIN_SITES` | applied at reading (no `settings` key) |
| [RANK-5 neighbour cutoff: ______] | cation neighbour cutoff | 3.8 A | `--cutoff-A` | `cutoff_A` 3.8 |
| [RANK-6 ridge penalty: ______] | ridge alpha | 1.0 | `--alpha` | `ridge_alpha` 1.0 |
| [RANK-7 minimum decorations: ______] | usable decorations per composition below which no interval is reported | 2 | `--min-decorations` | `min_decorations` 2 |
| [RANK-8 replicates and seed: ______] | bootstrap B and seed | 10000, 0 | `--B`, `--seed` | `B` 10000; `seed` 0 |
| [RANK-9 depth ceiling and reversal tolerance: ______] | grid ceiling of the decorations-needed scan; P drop that flags SPREAD-DECIDED | 10000; 0.01 | `max_decorations`, `REVERSAL_TOLERANCE` | applied at reading (no `settings` key) |
| [RANK-10 near-extreme floor: ______] | admitted sites below which p10 is labelled near-extreme | 50 | `P10_NEAR_EXTREME_SITES` | applied at reading (no `settings` key) |

Model line: `model.filename` macempa0mediummodel, `model.sha256_bytes` 75428afe3a1d7d8062e19bcaabd5c433623cabf308242ec9fb493e38604fb638 (equal to `docs/91:34`, asserted).

Coverage (`--admit all`; identical across the policy files, asserted): expected 60, present 66, missing 0, refused 0, `unverified` false, `partial` false; missing: none.

### `--admit all`

`status complete`; `settings.admit_definition`: "every site (the banked rule)"; `B` 10000, `seed` 0, `level` 0.9, `target_prob` 0.95, `min_decorations` 2, `stems` `mpa0__*,mpa0_ext__*`, `reproduction_tolerance_V` 1e-06; `n_site_rows` 720; sha256_lf `409a6d582ef442cbd69d8ebaf3f2881b99c155d90b374ba637bac5bbdf83edaf`.

**T1 census** (spec:55): coverage is complete when observed = declared for every composition and `coverage.missing` is empty — no (0 stems missing in `coverage.missing`).

| composition | decorations (usable) | sites (admitted) | declared decorations x sites | bootstrap support C(2D-1, D) |
|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 30 (30) | 120 (120) | 3 x 12 | 59132290782430712 |
| Fe25Co25Ni25Cr25 | 30 (30) | 120 (120) | 3 x 12 | 59132290782430712 |
| Cu26Ni9Cr31Co33 | 30 (30) | 120 (120) | 3 x 12 | 59132290782430712 |
| Ni34Fe6Cu29Co31 | 30 (30) | 120 (120) | 3 x 12 | 59132290782430712 |
| Cu8Cr23Mn35Co34 | 30 (30) | 120 (120) | 3 x 12 | 59132290782430712 |
| Cu22Fe30Co32Mn15 | 30 (30) | 120 (120) | 3 x 12 | 59132290782430712 |

**T2 statistics** (spec:56, R7; intervals at `settings.level` 0.9; the reproduction verdict at `tolerance_V` 1e-06 equals the docs/93 (a) verdict for the gated six, asserted):

| composition | banked rank | banked eta (V) | abs(census min − banked eta) (V) | reproduction | min [interval] | median [interval] | p10 [interval] | mean [interval] |
|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 1 | 0.43999606379672596 | 9.197e-11 | REPRODUCED | 0.4399960638886986 [0.4399960638886986, 0.48712508309465274] | 1.0636215667684747 [1.0090335663486907, 1.0994745463015914] | 0.6857593581363084 [0.6159440389549067, 0.7420098474320943] | 1.0140754099305964 [0.9747245300744298, 1.0545644769982745] |
| Fe25Co25Ni25Cr25 | 2 | 0.4530565517906915 | 4.512e-10 | REPRODUCED | 0.4530565522419163 [0.4530565522419163, 0.5430917214803648] | 1.0359351350452055 [0.9452697871438698, 1.1245305625156714] | 0.6563876633672938 [0.6033577444367261, 0.7416431176619064] | 1.0305335553778923 [0.9785002335037408, 1.080875835832715] |
| Cu26Ni9Cr31Co33 | 3 | 0.4791918878366763 | 1.194e-10 | REPRODUCED | 0.4491684937492817 [0.4491684937492817, 0.4791918879560475] | 0.8630688595672349 [0.8281346763090749, 0.8802181066882744] | 0.6100416171169606 [0.5638465386000311, 0.6493126064001453] | 0.8725209393813259 [0.8356469274046264, 0.9089087739612147] |
| Ni34Fe6Cu29Co31 | 4 | 0.7258416193876736 | 3.955e-08 | REPRODUCED | 0.6071660769726472 [0.6071660769726472, 0.6642244627704494] | 0.9403118949783074 [0.8994011922063829, 0.9965797830934102] | 0.7512312370186314 [0.7110212490034197, 0.7723126365715797] | 0.9965816652642783 [0.9574577217843679, 1.0357052837810183] |
| Cu8Cr23Mn35Co34 | 5 | 0.7557679418652832 | 1.442e-10 | REPRODUCED | 0.3622195377546671 [0.3622195377546671, 0.3862926021756987] | 0.9907774788574368 [0.9559402818380955, 1.0198407055086118] | 0.5706091801589954 [0.45940196833819125, 0.752724117591147] | 0.9543819215276454 [0.9259792232938736, 0.9825584566397192] |
| Cu22Fe30Co32Mn15 | 6 | 0.7956532031025425 | 2.095e-08 | REPRODUCED | 0.45594879091650764 [0.45594879091650764, 0.5911953179263365] | 1.0499502624908095 [0.9994658644232346, 1.1045880766803275] | 0.8050174117376667 [0.7826384983785033, 0.8643627070881813] | 1.0494893211972791 [1.019738731411116, 1.0803355990240555] |

Census orders per rule (`census_orders.<rule>`; tau printed only when `complete`, `docs/91:63`): min: Cu8Cr23Mn35Co34 < Ni31Cr29Cu5Mn35 < Cu26Ni9Cr31Co33 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 < Ni34Fe6Cu29Co31 (tau-a 0.2); median: Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 < Ni31Cr29Cu5Mn35 (tau-a -0.06666666666666667); p10: Cu8Cr23Mn35Co34 < Cu26Ni9Cr31Co33 < Fe25Co25Ni25Cr25 < Ni31Cr29Cu5Mn35 < Ni34Fe6Cu29Co31 < Cu22Fe30Co32Mn15 (tau-a 0.06666666666666667); mean: Cu26Ni9Cr31Co33 < Cu8Cr23Mn35Co34 < Ni34Fe6Cu29Co31 < Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 (tau-a 0.06666666666666667).
R7 / spec:33: `mpa0_ext__` stems are present, so the `min` statistic above is the rank statistic of the second wave, not a re-screen value; the reproduction column uses the banked seeds only.

**T3 rank matrix** (spec:57; STABLE iff `stable.<f>.stable`, P(banked rank) >= `target_prob` 0.95):

*min* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0 | 0.6474 | 0.0689 | 0.1465 | 0.128 | 0.0092 | 1.7827 | 1 | 0.0 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.0877 | 0.3024 | 0.3681 | 0.2418 | 0.0 | 2.764 | 2 | 0.0877 | not stable |
| Cu26Ni9Cr31Co33 | 0.0 | 0.2367 | 0.4627 | 0.1637 | 0.1369 | 0.0 | 2.2008 | 3 | 0.4627 | not stable |
| Ni34Fe6Cu29Co31 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0221 | 0.9779 | 4.9779 | 4 | 0.0 | not stable |
| Cu8Cr23Mn35Co34 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 5 | 0.0 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0282 | 0.166 | 0.3217 | 0.4712 | 0.0129 | 3.2746 | 6 | 0.0129 | not stable |

*median* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0 | 0.0014 | 0.0159 | 0.193 | 0.3988 | 0.3909 | 4.1619 | 1 | 0.0 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.0842 | 0.223 | 0.2125 | 0.1291 | 0.3512 | 3.4401 | 2 | 0.0842 | not stable |
| Cu26Ni9Cr31Co33 | 0.9988 | 0.0012 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0012 | 3 | 0.0 | not stable |
| Ni34Fe6Cu29Co31 | 0.0012 | 0.8198 | 0.133 | 0.0426 | 0.0034 | 0.0 | 1.2272 | 4 | 0.0426 | not stable |
| Cu8Cr23Mn35Co34 | 0.0 | 0.091 | 0.6049 | 0.2761 | 0.0256 | 0.0024 | 2.2435 | 5 | 0.0256 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0024 | 0.0232 | 0.2758 | 0.4431 | 0.2555 | 3.9261 | 6 | 0.2555 | not stable |

*p10* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0124 | 0.1164 | 0.3818 | 0.4297 | 0.0566 | 0.0031 | 2.4110000000000005 | 1 | 0.0124 | not stable |
| Fe25Co25Ni25Cr25 | 0.0463 | 0.2638 | 0.4271 | 0.2214 | 0.04 | 0.0014 | 1.9492 | 2 | 0.2638 | not stable |
| Cu26Ni9Cr31Co33 | 0.2882 | 0.5959 | 0.1091 | 0.0068 | 0.0 | 0.0 | 0.8345 | 3 | 0.1091 | not stable |
| Ni34Fe6Cu29Co31 | 0.0 | 0.0014 | 0.0229 | 0.1535 | 0.8017 | 0.0205 | 3.817 | 4 | 0.1535 | not stable |
| Cu8Cr23Mn35Co34 | 0.6531 | 0.0224 | 0.0588 | 0.1854 | 0.0737 | 0.0066 | 1.024 | 5 | 0.0737 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0001 | 0.0003 | 0.0032 | 0.028 | 0.9684 | 4.964300000000001 | 6 | 0.9684 | STABLE |

*mean* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0 | 0.0196 | 0.2331 | 0.4212 | 0.2461 | 0.08 | 3.1338 | 1 | 0.0 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.0134 | 0.1237 | 0.2346 | 0.3545 | 0.2738 | 3.7516 | 2 | 0.0134 | not stable |
| Cu26Ni9Cr31Co33 | 0.9982 | 0.0018 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0018 | 3 | 0.0 | not stable |
| Ni34Fe6Cu29Co31 | 0.0001 | 0.0703 | 0.5419 | 0.2675 | 0.1002 | 0.02 | 2.4574000000000003 | 4 | 0.2675 | not stable |
| Cu8Cr23Mn35Co34 | 0.0017 | 0.8949 | 0.0926 | 0.0106 | 0.0002 | 0.0 | 1.1127 | 5 | 0.0002 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0 | 0.0087 | 0.0661 | 0.299 | 0.6262 | 4.5427 | 6 | 0.6262 | not stable |

**T4 adjacent gaps** (spec:58, R1-R3):

| pair | rule | observed gap (V) | P(order) | gap interval (V) | verdict | decorations needed [MC bracket] |
|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | min | 0.013060488353217714 | 0.7488 | [-0.03406853085273642, 0.10309565759166617] | UNRESOLVED / SPREAD-DECIDED | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.05445, best 0.463 at D = 1; `order_reverses_at_depth` |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | min | -0.0038880584926346273 | 0.2447 | [-0.09392322773108308, 0.02613533571413118] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | min | 0.15799758322336555 | 1.0 | [0.12797418901659974, 0.21505596902116775] | RESOLVED / SPREAD-DECIDED | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.7388, best 0.76165 at D = 140; `order_reverses_at_depth` |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | min | -0.24494653921798015 | 0.0 | [-0.30200492501578236, -0.22087347479694852] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | min | 0.09372925316184055 | 1.0 | [0.06965618874080892, 0.22897578017166942] | RESOLVED | 9284 [6759, None] (P = 0.95) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | median | -0.027686431723269234 | 0.4044 | [-0.1325427228410538, 0.0898536806632413] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | median | -0.17286627547797062 | 0.0 | [-0.28020451073631564, -0.07829267895355807] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | median | 0.07724303541107247 | 0.9988 | [0.029446560797106832, 0.1487524464153629] | RESOLVED | 21 [20, 21] (P = 0.95405) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | median | 0.05046558387912947 | 0.8806 | [-0.016769824159837823, 0.0990508251897344] | UNRESOLVED | 48 [46, 50] (P = 0.95085) |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | median | 0.05917278363337264 | 0.9621 | [0.004715881744248243, 0.12235132173840883] | RESOLVED | 30 [29, 31] (P = 0.9524) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | p10 | -0.029371694769014578 | 0.3368 | [-0.11401184153458532, 0.06656705430306709] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | p10 | -0.04634604625033323 | 0.1421 | [-0.13777895359402237, 0.031068738150788325] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | p10 | 0.14118961990167078 | 0.9998 | [0.0790233960133424, 0.18034437137163095] | RESOLVED | 17 [17, 19] (P = 0.95005) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | p10 | -0.18062205685963595 | 0.0859 | [-0.2930267678877365, 0.017254924639342972] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | p10 | 0.2344082315786713 | 0.9921 | [0.04726835722434147, 0.36313846151085727] | RESOLVED | 2 [2, 3] (P = 0.953) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | mean | 0.016458145447295847 | 0.6605 | [-0.04943767750014918, 0.07994206287611921] | UNRESOLVED | 328 [328, 328] (P = 0.9502062935056337) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | mean | -0.15801261599656635 | 0.0 | [-0.22092075676418851, -0.094755568060809] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | mean | 0.12406072588295236 | 0.9999 | [0.07001330488036488, 0.17713554853794009] | RESOLVED | 6 [6, 6] (P = 0.9631094484465975) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | mean | -0.04219974373663282 | 0.0746 | [-0.09064765397469532, 0.005666384535783026] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | mean | 0.09510739966963366 | 0.9999 | [0.05461548170223469, 0.1362297604670667] | RESOLVED | 8 [8, 8] (P = 0.9580070865844676) |

R1 (spec:68 verbatim: "- **R1 (boundary verdict).** An adjacent boundary is RESOLVED under a rule when P(order preserved) >= the target in T4; UNRESOLVED otherwise. The screen is reported as "resolving k of 5 boundaries under the mean rule, k' under the median and k'' under the min rule", each on that rule's own observed gap. The min-rule count is labelled descriptive (section 2); the mean and median counts are the calibrated ones; the p10 count is labelled near-extreme whenever the admitted site count is below 50. No verdict is read from the point gap alone."): resolving 2 of 5 boundaries under the mean rule, 2 under the median and 2 under the min rule; the min count is descriptive, the mean and median counts are the calibrated ones, and the p10 count is 2.
R2 (spec:69): INVERTED boundaries — min 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); median 2 (Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25, Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33); p10 3 (Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25, Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); mean 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34).
R3 (spec:70): SPREAD-DECIDED — Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 under min (`near_extreme` false); Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 under min (`near_extreme` false); every count above assumes normal i.i.d. sites and the figures are "lower bounds on the depth under any heavier left tail" (spec:70).

**T5 variance components** (spec:59, R4):

| composition | sites | decorations | site sd (population) | within sd | between sd | ICC | status |
|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 120 | 30 | 0.2344570640213994 | 0.2238023155011226 | 0.07404589035652656 | 0.09866415709081808 | ok |
| Fe25Co25Ni25Cr25 | 120 | 30 | 0.2757966947292184 | 0.2480458404083938 | 0.12477483459880792 | 0.2019412247648717 | ok |
| Cu26Ni9Cr31Co33 | 120 | 30 | 0.2277779532364105 | 0.22297894573510138 | 0.05163715407340541 | 0.05089900697476139 | ok |
| Ni34Fe6Cu29Co31 | 120 | 30 | 0.25231846424773846 | 0.24914055778860292 | 0.04672939351770249 | 0.033984094395729386 | ok |
| Cu8Cr23Mn35Co34 | 120 | 30 | 0.22620578410089293 | 0.23700077302547648 | 0.0 | 0.0 | ok |
| Cu22Fe30Co32Mn15 | 120 | 30 | 0.21393173481589964 | 0.2179167745488296 | 0.0 | 0.0 | ok |

R4 (spec:71; ICC band 0.2, the RANK-3 draft): Fe25Co25Ni25Cr25 (0.2019412247648717) — i.i.d. depth understated; decorations-needed figures for its pairs are lower bounds.

**T6 ridge** (spec:60, R5; `cutoff_A` 3.8, `ridge_alpha` 1.0; `n_sites_with_environment` 720):

| target | sites | status | R² in-sample | R² LOO | sigma in-sample | sigma LOO |
|---|---|---|---|---|---|---|
| eta | 720 | ok (`meaningful` true, `min_sites` 30) | 0.2534503436415766 | 0.227898274078004 | 0.21290617305637322 | 0.21651907614396407 |
| dG_OH | 720 | ok (`meaningful` true, `min_sites` 30) | 0.44400063830817993 | 0.4225653274256943 | 0.15048947941044324 | 0.15336293888250552 |
| dG_O | 720 | ok (`meaningful` true, `min_sites` 30) | 0.28595979472880984 | 0.26101160651715904 | 0.8118693492779453 | 0.8259307229987581 |
| dG_OOH | 720 | ok (`meaningful` true, `min_sites` 30) | 0.16838779187397068 | 0.1406468405027116 | 0.6754490843644956 | 0.6866224959806367 |

R5 (spec:72): `sigma_loo` (eta) 0.21651907614396407 V against the pooled site sd 0.24641032624300896 V (population sd over every `site_rows[].eta`, 720 sites — the same 720 sites the ridge is fitted on, so the comparison is on one population and identical in every policy block; computed by this script — post-hoc arithmetic on file values): sigma_LOO lies below the pooled site sd; the fit is descriptive and no R² threshold is a success criterion. Beside it, post-hoc and not the R5 comparison: the population sd over the 720 sites this policy admits is 0.24641032624300896 V.

### `--admit no-desorbed`

`status complete`; `settings.admit_definition`: "no species' winning M-O distance reached the desorption cut"; `B` 10000, `seed` 0, `level` 0.9, `target_prob` 0.95, `min_decorations` 2, `stems` `mpa0__*,mpa0_ext__*`, `reproduction_tolerance_V` 1e-06; `n_site_rows` 720; sha256_lf `a6b7b6652af29c5969d433e3947b8c8d91dc8194c024cf517dc430e6d8d8070b`.

**T1 census** (spec:55): coverage is complete when observed = declared for every composition and `coverage.missing` is empty — no (0 stems missing in `coverage.missing`).

| composition | decorations (usable) | sites (admitted) | declared decorations x sites | bootstrap support C(2D-1, D) |
|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 30 (18) | 120 (23) | 3 x 12 | 4537567650 |
| Fe25Co25Ni25Cr25 | 30 (18) | 120 (28) | 3 x 12 | 4537567650 |
| Cu26Ni9Cr31Co33 | 30 (12) | 120 (13) | 3 x 12 | 1352078 |
| Ni34Fe6Cu29Co31 | 30 (16) | 120 (19) | 3 x 12 | 300540195 |
| Cu8Cr23Mn35Co34 | 30 (14) | 120 (20) | 3 x 12 | 20058300 |
| Cu22Fe30Co32Mn15 | 30 (23) | 120 (36) | 3 x 12 | 4116715363800 |

**T2 statistics** (spec:56, R7; intervals at `settings.level` 0.9; the reproduction verdict at `tolerance_V` 1e-06 equals the docs/93 (a) verdict for the gated six, asserted):

| composition | banked rank | banked eta (V) | abs(census min − banked eta) (V) | reproduction | min [interval] | median [interval] | p10 [interval] | mean [interval] |
|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 1 | 0.43999606379672596 | 9.197e-11 | REPRODUCED | 0.4399960638886986 [0.4399960638886986, 0.6739686895136137] | 1.0994745463015914 [0.9846289236647561, 1.1517097196819472] | 0.5304733422095593 [0.4588476715710803, 0.944882942004806] | 1.0187800210377733 [0.8969782760123572, 1.1428632983563956] |
| Fe25Co25Ni25Cr25 | 2 | 0.4530565517906915 | 4.512e-10 | REPRODUCED | 0.4530565522419163 [0.4530565522419163, 0.5430917214803648] | 1.1293093804679155 [0.9390148231931885, 1.2829310153736326] | 0.5529628167121606 [0.49951402505948117, 0.7863812091728476] | 1.0493750037518925 [0.933371231010393, 1.1468143423370376] |
| Cu26Ni9Cr31Co33 | 3 | 0.4791918878366763 | 1.194e-10 | REPRODUCED | 0.4491684937492817 [0.4491684937492817, 0.5936955227013225] | 0.7249862610187696 [0.6585355921972167, 0.9943655948473218] | 0.5020926149051025 [0.4491684937492817, 0.7031553576639302] | 0.8113936254913021 [0.7045106858287452, 0.9278205896568417] |
| Ni34Fe6Cu29Co31 | 4 | 0.7258416193876736 | 3.955e-08 | REPRODUCED | 0.7023703785556004 [0.7023703785556004, 0.7258416589359067] | 0.996406899168532 [0.9282988826285412, 1.0834958748019101] | 0.7221170073021523 [0.7023703785556004, 0.8855932386233901] | 0.9892592672783415 [0.9258197635899699, 1.0523083147425583] |
| Cu8Cr23Mn35Co34 | 5 | 0.7557679418652832 | 1.442e-10 | REPRODUCED | 0.3622195377546671 [0.3622195377546671, 0.3862926021756987] | 0.6453899344432217 [0.47162467901359273, 0.9451884339539456] | 0.38574376161291574 [0.363985080340021, 0.42655874667232574] | 0.7016798169108617 [0.6059222402257529, 0.7930269423426701] |
| Cu22Fe30Co32Mn15 | 6 | 0.7956532031025425 | 2.095e-08 | REPRODUCED | 0.6855536132758706 [0.6855536132758706, 0.8038151059702994] | 1.1877779250779934 [0.9340957706041082, 1.2114037958517923] | 0.823596120929265 [0.7956531821512538, 0.886400976579046] | 1.0940001011447 [1.0233017309615386, 1.1535952894196018] |

Census orders per rule (`census_orders.<rule>`; tau printed only when `complete`, `docs/91:63`): min: Cu8Cr23Mn35Co34 < Ni31Cr29Cu5Mn35 < Cu26Ni9Cr31Co33 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 < Ni34Fe6Cu29Co31 (tau-a 0.2); median: Cu8Cr23Mn35Co34 < Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 < Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 (tau-a -0.06666666666666667); p10: Cu8Cr23Mn35Co34 < Cu26Ni9Cr31Co33 < Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 < Ni34Fe6Cu29Co31 < Cu22Fe30Co32Mn15 (tau-a 0.2); mean: Cu8Cr23Mn35Co34 < Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 < Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 (tau-a -0.06666666666666667).
R7 / spec:33: `mpa0_ext__` stems are present, so the `min` statistic above is the rank statistic of the second wave, not a re-screen value; the reproduction column uses the banked seeds only.

**T3 rank matrix** (spec:57; STABLE iff `stable.<f>.stable`, P(banked rank) >= `target_prob` 0.95):

*min* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0 | 0.6422 | 0.0956 | 0.2336 | 0.0172 | 0.0114 | 1.66 | 1 | 0.0 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.0898 | 0.3757 | 0.5338 | 0.0001 | 0.0006 | 2.446 | 2 | 0.0898 | not stable |
| Cu26Ni9Cr31Co33 | 0.0001 | 0.268 | 0.5282 | 0.1945 | 0.0041 | 0.0051 | 1.9498000000000002 | 3 | 0.5282 | not stable |
| Ni34Fe6Cu29Co31 | 0.0 | 0.0 | 0.0 | 0.0065 | 0.3626 | 0.6309 | 4.6244 | 4 | 0.0065 | not stable |
| Cu8Cr23Mn35Co34 | 0.9999 | 0.0 | 0.0 | 0.0001 | 0.0 | 0.0 | 0.00030000000000000003 | 5 | 0.0 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0 | 0.0005 | 0.0315 | 0.616 | 0.352 | 4.319500000000001 | 6 | 0.352 | not stable |

*median* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0023 | 0.017 | 0.1082 | 0.4805 | 0.3299 | 0.0621 | 3.3049999999999997 | 1 | 0.0023 | not stable |
| Fe25Co25Ni25Cr25 | 0.0043 | 0.0202 | 0.0897 | 0.2015 | 0.3301 | 0.3542 | 3.8955 | 2 | 0.0202 | not stable |
| Cu26Ni9Cr31Co33 | 0.2468 | 0.6332 | 0.0921 | 0.0244 | 0.0033 | 0.0002 | 0.9048 | 3 | 0.0921 | not stable |
| Ni34Fe6Cu29Co31 | 0.0031 | 0.0855 | 0.62 | 0.2438 | 0.0435 | 0.0041 | 2.2514 | 4 | 0.2438 | not stable |
| Cu8Cr23Mn35Co34 | 0.7425 | 0.2263 | 0.0287 | 0.0025 | 0.0 | 0.0 | 0.2912 | 5 | 0.0 | not stable |
| Cu22Fe30Co32Mn15 | 0.001 | 0.0178 | 0.0613 | 0.0473 | 0.2932 | 0.5794 | 4.352100000000001 | 6 | 0.5794 | not stable |

*p10* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0016 | 0.2927 | 0.237 | 0.3224 | 0.0435 | 0.1028 | 2.4219 | 1 | 0.0016 | not stable |
| Fe25Co25Ni25Cr25 | 0.0002 | 0.2042 | 0.4596 | 0.28 | 0.0248 | 0.0312 | 2.2186 | 2 | 0.2042 | not stable |
| Cu26Ni9Cr31Co33 | 0.0032 | 0.4999 | 0.291 | 0.1947 | 0.0096 | 0.0016 | 1.7124 | 3 | 0.291 | not stable |
| Ni34Fe6Cu29Co31 | 0.0 | 0.0002 | 0.0097 | 0.177 | 0.6823 | 0.1308 | 3.9337999999999997 | 4 | 0.177 | not stable |
| Cu8Cr23Mn35Co34 | 0.995 | 0.003 | 0.0013 | 0.0005 | 0.0002 | 0.0 | 0.0079 | 5 | 0.0002 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0 | 0.0014 | 0.0254 | 0.2396 | 0.7336 | 4.7054 | 6 | 0.7336 | not stable |

*mean* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0001 | 0.0181 | 0.2819 | 0.287 | 0.2473 | 0.1656 | 3.2600999999999996 | 1 | 0.0001 | not stable |
| Fe25Co25Ni25Cr25 | 0.0001 | 0.008 | 0.158 | 0.2601 | 0.346 | 0.2278 | 3.6273 | 2 | 0.008 | not stable |
| Cu26Ni9Cr31Co33 | 0.1039 | 0.8602 | 0.0305 | 0.0049 | 0.0005 | 0.0 | 0.9379 | 3 | 0.0305 | not stable |
| Ni34Fe6Cu29Co31 | 0.0 | 0.0096 | 0.5183 | 0.359 | 0.1038 | 0.0093 | 2.5848999999999998 | 4 | 0.359 | not stable |
| Cu8Cr23Mn35Co34 | 0.8959 | 0.1039 | 0.0002 | 0.0 | 0.0 | 0.0 | 0.1043 | 5 | 0.0 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0002 | 0.0111 | 0.089 | 0.3024 | 0.5973 | 4.4855 | 6 | 0.5973 | not stable |

**T4 adjacent gaps** (spec:58, R1-R3):

| pair | rule | observed gap (V) | P(order) | gap interval (V) | verdict | decorations needed [MC bracket] |
|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | min | 0.013060488353217714 | 0.72 | [-0.22091213727169734, 0.10309565759166617] | UNRESOLVED / SPREAD-DECIDED | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.2061, best 0.49045 at D = 1; `order_reverses_at_depth` |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | min | -0.0038880584926346273 | 0.2752 | [-0.09392322773108308, 0.1406389704594062] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | min | 0.25320188480631867 | 0.9928 | [0.10867485585427783, 0.276673165186625] | RESOLVED | 2 [2, 2] (P = 0.9745) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | min | -0.3401508408009333 | 0.0 | [-0.3636221211812396, -0.31607777637990164] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | min | 0.3233340755212035 | 1.0 | [0.2992610111001719, 0.4415955682156323] | RESOLVED | 1 [1, 1] (P = 0.96055) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | median | 0.029834834166324153 | 0.6683 | [-0.16246682091127695, 0.2560741773278892] | UNRESOLVED | 227 [220, 234] (P = 0.9502) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | median | -0.4043231194491459 | 0.0284 | [-0.562973953354784, -0.056653593730118246] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | median | 0.27142063814976236 | 0.9152 | [-0.03598355966090594, 0.3689653069669552] | UNRESOLVED | 1 [1, 1] (P = 0.955) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | median | -0.3510169647253103 | 0.022 | [-0.5481015895824787, -0.04905790613099725] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | median | 0.5423879906347717 | 0.9952 | [0.19801728622067127, 0.7099062788301814] | RESOLVED | 1 [1, 1] (P = 0.99825) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | p10 | 0.022489474502601303 | 0.4966 | [-0.3988254980131498, 0.1872866119409613] | UNRESOLVED / SPREAD-DECIDED | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.0016, best 0.49825 at D = 1; `order_reverses_at_depth` |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | p10 | -0.050870201807058146 | 0.37 | [-0.2331461374472626, 0.14633641452359653] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | p10 | 0.22002439239704985 | 0.9874 | [0.04755695992459441, 0.3933312392887124] | RESOLVED | 2 [2, 2] (P = 0.98125) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | p10 | -0.3363732456892366 | 0.0002 | [-0.5013350952999076, -0.299754863894807] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | p10 | 0.4378523593163493 | 1.0 | [0.39210671869636826, 0.5035688954304305] | RESOLVED | 1 [1, 1] (P = 0.9936) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | mean | 0.0305949827141192 | 0.5879 | [-0.14081006983137148, 0.186580354628779] | UNRESOLVED | 138 [138, 138] (P = 0.9501371333434907) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | mean | -0.2379813782605904 | 0.0091 | [-0.3822147251751228, -0.07627127864148128] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | mean | 0.17786564178703934 | 0.9873 | [0.04505375180273727, 0.30231696825364046] | RESOLVED | 2 [2, 2] (P = 0.957652767614528) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | mean | -0.2875794503674798 | 0.0 | [-0.40356516654579144, -0.17587508167575291] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | mean | 0.39232028423383836 | 1.0 | [0.276471738437855, 0.5061270548187081] | RESOLVED | 1 [1, 1] (P = 0.9899600317515332) |

R1 (spec:68 verbatim: "- **R1 (boundary verdict).** An adjacent boundary is RESOLVED under a rule when P(order preserved) >= the target in T4; UNRESOLVED otherwise. The screen is reported as "resolving k of 5 boundaries under the mean rule, k' under the median and k'' under the min rule", each on that rule's own observed gap. The min-rule count is labelled descriptive (section 2); the mean and median counts are the calibrated ones; the p10 count is labelled near-extreme whenever the admitted site count is below 50. No verdict is read from the point gap alone."): resolving 2 of 5 boundaries under the mean rule, 1 under the median and 2 under the min rule; the min count is descriptive, the mean and median counts are the calibrated ones, and the p10 count is 2, labelled near-extreme (`n_admitted` minimum 13 < the RANK-10 floor 50).
R2 (spec:69): INVERTED boundaries — min 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); median 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); p10 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); mean 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34).
R3 (spec:70): SPREAD-DECIDED — Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 under min (`near_extreme` false); Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 under p10 (`near_extreme` false); every count above assumes normal i.i.d. sites and the figures are "lower bounds on the depth under any heavier left tail" (spec:70).

**T5 variance components** (spec:59, R4):

| composition | sites | decorations | site sd (population) | within sd | between sd | ICC | status |
|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 23 | 18 | 0.29539268251712486 | 0.17000597762471548 | 0.2521457843774811 | 0.6874764313970438 | ok |
| Fe25Co25Ni25Cr25 | 28 | 18 | 0.3215791714148845 | 0.3093370177530641 | 0.10968739023707656 | 0.11168997229790222 | ok |
| Cu26Ni9Cr31Co33 | 13 | 12 | 0.23609102886956648 | 0.05473735155287536 | 0.2411078714915834 | 0.950986133123075 | ok |
| Ni34Fe6Cu29Co31 | 19 | 16 | 0.1714836273329334 | 0.19497147059368494 | 0.0 | 0.0 | ok |
| Cu8Cr23Mn35Co34 | 20 | 14 | 0.27810934955940564 | 0.3100816364288015 | 0.0 | 0.0 | ok |
| Cu22Fe30Co32Mn15 | 36 | 23 | 0.191213043657435 | 0.1092969586556888 | 0.16226503196719905 | 0.6879010796819117 | ok |

R4 (spec:71; ICC band 0.2, the RANK-3 draft): Ni31Cr29Cu5Mn35 (0.6874764313970438), Cu26Ni9Cr31Co33 (0.950986133123075), Cu22Fe30Co32Mn15 (0.6879010796819117) — i.i.d. depth understated; decorations-needed figures for its pairs are lower bounds.

**T6 ridge** (spec:60, R5; `cutoff_A` 3.8, `ridge_alpha` 1.0; `n_sites_with_environment` 720):

| target | sites | status | R² in-sample | R² LOO | sigma in-sample | sigma LOO |
|---|---|---|---|---|---|---|
| eta | 720 | ok (`meaningful` true, `min_sites` 30) | 0.2534503436415766 | 0.227898274078004 | 0.21290617305637322 | 0.21651907614396407 |
| dG_OH | 720 | ok (`meaningful` true, `min_sites` 30) | 0.44400063830817993 | 0.4225653274256943 | 0.15048947941044324 | 0.15336293888250552 |
| dG_O | 720 | ok (`meaningful` true, `min_sites` 30) | 0.28595979472880984 | 0.26101160651715904 | 0.8118693492779453 | 0.8259307229987581 |
| dG_OOH | 720 | ok (`meaningful` true, `min_sites` 30) | 0.16838779187397068 | 0.1406468405027116 | 0.6754490843644956 | 0.6866224959806367 |

R5 (spec:72): `sigma_loo` (eta) 0.21651907614396407 V against the pooled site sd 0.24641032624300896 V (population sd over every `site_rows[].eta`, 720 sites — the same 720 sites the ridge is fitted on, so the comparison is on one population and identical in every policy block; computed by this script — post-hoc arithmetic on file values): sigma_LOO lies below the pooled site sd; the fit is descriptive and no R² threshold is a success criterion. Beside it, post-hoc and not the R5 comparison: the population sd over the 139 sites this policy admits is 0.2889277290282289 V.

### `--admit intact`

`status complete`; `settings.admit_definition`: "site_integrity all_states_intact: OH, O and OOH all NORMAL and force-converged"; `B` 10000, `seed` 0, `level` 0.9, `target_prob` 0.95, `min_decorations` 2, `stems` `mpa0__*,mpa0_ext__*`, `reproduction_tolerance_V` 1e-06; `n_site_rows` 720; sha256_lf `338da000c7fdfe5513b926850eca2386765d29d6d4e7023f300c1c082a07cfd2`.

**T1 census** (spec:55): coverage is complete when observed = declared for every composition and `coverage.missing` is empty — no (0 stems missing in `coverage.missing`).

| composition | decorations (usable) | sites (admitted) | declared decorations x sites | bootstrap support C(2D-1, D) |
|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 30 (3) | 120 (3) | 3 x 12 | 10 |
| Fe25Co25Ni25Cr25 | 30 (9) | 120 (11) | 3 x 12 | 24310 |
| Cu26Ni9Cr31Co33 | 30 (5) | 120 (6) | 3 x 12 | 126 |
| Ni34Fe6Cu29Co31 | 30 (13) | 120 (15) | 3 x 12 | 5200300 |
| Cu8Cr23Mn35Co34 | 30 (3) | 120 (4) | 3 x 12 | 10 |
| Cu22Fe30Co32Mn15 | 30 (23) | 120 (33) | 3 x 12 | 4116715363800 |

**T2 statistics** (spec:56, R7; intervals at `settings.level` 0.9; the reproduction verdict at `tolerance_V` 1e-06 equals the docs/93 (a) verdict for the gated six, asserted):

| composition | banked rank | banked eta (V) | abs(census min − banked eta) (V) | reproduction | min [interval] | median [interval] | p10 [interval] | mean [interval] |
|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 1 | 0.43999606379672596 | 9.197e-11 | REPRODUCED | 0.9349464465898185 [0.9349464465898185, 1.0994745463015914] | 1.0994745463015914 [0.9349464465898185, 1.2150250066883626] | 0.967852066532173 [0.9349464465898185, 1.1225846383789455] | 1.0831486665265908 [0.9897891464937428, 1.176508186559439] |
| Fe25Co25Ni25Cr25 | 2 | 0.4530565517906915 | 4.512e-10 | REPRODUCED | 0.8637036860196456 [0.8637036860196456, 0.9746743837065122] | 1.2293487396470066 [0.9746743837065122, 1.2886251927133952] | 0.9033552626798649 [0.8637036860196456, 1.1370036168122664] | 1.1693515004551147 [1.0683278094658402, 1.2494442742116447] |
| Cu26Ni9Cr31Co33 | 3 | 0.4791918878366763 | 1.194e-10 | REPRODUCED | 0.5936955227013225 [0.5936955227013225, 0.8634141924469798] | 0.9198856028358744 [0.7233756616931108, 0.9943655948473218] | 0.6585355921972167 [0.5936955227013225, 0.8751644726121057] | 0.9018936380806895 [0.7257015927272377, 1.0370403030657869] |
| Ni34Fe6Cu29Co31 | 4 | 0.7258416193876736 | 3.955e-08 | REPRODUCED | 0.6790912935495492 [0.6790912935495492, 0.7859467359447043] | 0.9615557456723689 [0.9048504014100711, 1.0474846756205505] | 0.7387097348381626 [0.6790912935495492, 0.9118849457756122] | 0.9652606865062096 [0.9022566636805149, 1.0357755558951234] |
| Cu8Cr23Mn35Co34 | 5 | 0.7557679418652832 | 1.442e-10 | REPRODUCED | 0.7159027265388698 [0.7159027265388698, 0.7557679417210732] | 0.9405996983387848 [0.7557679417210732, 1.1369272018046939] | 0.7278622910935308 [0.7159027265388698, 0.8387613450641578] | 0.9335073312552833 [0.8382175162343781, 1.0287971462761885] |
| Cu22Fe30Co32Mn15 | 6 | 0.7956532031025425 | 2.095e-08 | REPRODUCED | 0.6855536132758706 [0.6855536132758706, 0.8051510012673742] | 1.209540229659778 [1.1366539284832395, 1.2348775499805225] | 0.8480415633179474 [0.8038151059702994, 0.8922617398212918] | 1.1266872883385195 [1.0610472629231904, 1.1822128157526746] |

Census orders per rule (`census_orders.<rule>`; tau printed only when `complete`, `docs/91:63`): min: Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 < Cu22Fe30Co32Mn15 < Cu8Cr23Mn35Co34 < Fe25Co25Ni25Cr25 < Ni31Cr29Cu5Mn35 (tau-a -0.3333333333333333); median: Cu26Ni9Cr31Co33 < Cu8Cr23Mn35Co34 < Ni34Fe6Cu29Co31 < Ni31Cr29Cu5Mn35 < Cu22Fe30Co32Mn15 < Fe25Co25Ni25Cr25 (tau-a -0.06666666666666667); p10: Cu26Ni9Cr31Co33 < Cu8Cr23Mn35Co34 < Ni34Fe6Cu29Co31 < Cu22Fe30Co32Mn15 < Fe25Co25Ni25Cr25 < Ni31Cr29Cu5Mn35 (tau-a -0.3333333333333333); mean: Cu26Ni9Cr31Co33 < Cu8Cr23Mn35Co34 < Ni34Fe6Cu29Co31 < Ni31Cr29Cu5Mn35 < Cu22Fe30Co32Mn15 < Fe25Co25Ni25Cr25 (tau-a -0.06666666666666667).
R7 / spec:33: `mpa0_ext__` stems are present, so the `min` statistic above is the rank statistic of the second wave, not a re-screen value; the reproduction column uses the banked seeds only.

**T3 rank matrix** (spec:57; STABLE iff `stable.<f>.stable`, P(banked rank) >= `target_prob` 0.95):

*min* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0 | 0.0 | 0.0001 | 0.0047 | 0.1109 | 0.8843 | 4.8794 | 1 | 0.0 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.0 | 0.0017 | 0.0711 | 0.8527 | 0.0745 | 4.0 | 2 | 0.0 | not stable |
| Cu26Ni9Cr31Co33 | 0.6662 | 0.038 | 0.1164 | 0.1689 | 0.0037 | 0.0068 | 0.8262999999999999 | 3 | 0.1164 | not stable |
| Ni34Fe6Cu29Co31 | 0.252 | 0.5358 | 0.1342 | 0.0542 | 0.0232 | 0.0006 | 1.0626000000000002 | 4 | 0.0542 | not stable |
| Cu8Cr23Mn35Co34 | 0.0102 | 0.1352 | 0.4197 | 0.3988 | 0.0023 | 0.0338 | 2.3491999999999997 | 5 | 0.0023 | not stable |
| Cu22Fe30Co32Mn15 | 0.0716 | 0.291 | 0.3279 | 0.3023 | 0.0072 | 0.0 | 1.8824999999999998 | 6 | 0.0 | not stable |

*median* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0447 | 0.1156 | 0.247 | 0.3291 | 0.1776 | 0.086 | 2.7373000000000003 | 1 | 0.0447 | not stable |
| Fe25Co25Ni25Cr25 | 0.0069 | 0.0183 | 0.0366 | 0.1013 | 0.2253 | 0.6116 | 4.3546 | 2 | 0.0183 | not stable |
| Cu26Ni9Cr31Co33 | 0.4846 | 0.2971 | 0.1653 | 0.0494 | 0.0035 | 0.0001 | 0.7904 | 3 | 0.1653 | not stable |
| Ni34Fe6Cu29Co31 | 0.1051 | 0.3688 | 0.3926 | 0.1249 | 0.0084 | 0.0002 | 1.5633000000000001 | 4 | 0.1249 | not stable |
| Cu8Cr23Mn35Co34 | 0.3542 | 0.1906 | 0.1515 | 0.2516 | 0.0504 | 0.0017 | 1.4585 | 5 | 0.0504 | not stable |
| Cu22Fe30Co32Mn15 | 0.0045 | 0.0096 | 0.007 | 0.1437 | 0.5348 | 0.3004 | 4.0959 | 6 | 0.3004 | not stable |

*p10* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0 | 0.0 | 0.0007 | 0.015 | 0.2821 | 0.7022 | 4.6858 | 1 | 0.0 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.0014 | 0.0282 | 0.1673 | 0.5497 | 0.2534 | 4.0255 | 2 | 0.0014 | not stable |
| Cu26Ni9Cr31Co33 | 0.6328 | 0.1522 | 0.1294 | 0.057 | 0.0226 | 0.006 | 0.7024 | 3 | 0.1294 | not stable |
| Ni34Fe6Cu29Co31 | 0.1898 | 0.3591 | 0.275 | 0.1208 | 0.0527 | 0.0026 | 1.4953 | 4 | 0.1208 | not stable |
| Cu8Cr23Mn35Co34 | 0.1691 | 0.4308 | 0.3087 | 0.0554 | 0.0047 | 0.0313 | 1.3897 | 5 | 0.0047 | not stable |
| Cu22Fe30Co32Mn15 | 0.0083 | 0.0565 | 0.258 | 0.5845 | 0.0882 | 0.0045 | 2.7013000000000003 | 6 | 0.0045 | not stable |

*mean* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0044 | 0.0301 | 0.1143 | 0.5061 | 0.2245 | 0.1206 | 3.2779999999999996 | 1 | 0.0044 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.0012 | 0.0079 | 0.0959 | 0.2254 | 0.6696 | 4.5543 | 2 | 0.0012 | not stable |
| Cu26Ni9Cr31Co33 | 0.5725 | 0.2271 | 0.1676 | 0.031 | 0.0016 | 0.0002 | 0.6627 | 3 | 0.1676 | not stable |
| Ni34Fe6Cu29Co31 | 0.1045 | 0.3626 | 0.4716 | 0.0595 | 0.0018 | 0.0 | 1.4915 | 4 | 0.0595 | not stable |
| Cu8Cr23Mn35Co34 | 0.3185 | 0.3786 | 0.2255 | 0.0562 | 0.0177 | 0.0035 | 1.0865 | 5 | 0.0177 | not stable |
| Cu22Fe30Co32Mn15 | 0.0001 | 0.0004 | 0.0131 | 0.2513 | 0.529 | 0.2061 | 3.927 | 6 | 0.2061 | not stable |

**T4 adjacent gaps** (spec:58, R1-R3):

| pair | rule | observed gap (V) | P(order) | gap interval (V) | verdict | decorations needed [MC bracket] |
|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | min | -0.07124276057017287 | 0.078 | [-0.23577086028194572, 0.039727937116693646] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | min | -0.2700081633183231 | 0.0103 | [-0.38097886100518963, -0.0002894935726658332] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | min | 0.0853957708482267 | 0.6942 | [-0.1843228988974306, 0.1922512132433818] | UNRESOLVED | 9 [9, 10] (P = 0.95165) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | min | 0.03681143298932055 | 0.8885 | [-0.07004400940583455, 0.07667664817152398] | UNRESOLVED / SPREAD-DECIDED | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.0197, best 0.49455 at D = 1; `order_reverses_at_depth` |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | min | -0.03034911326299916 | 0.3479 | [-0.07021432844520259, 0.08924827472850438] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | median | 0.12987419334541528 | 0.8432 | [-0.1248001625950792, 0.33739578214168287] | UNRESOLVED | 3 [3, 3] (P = 0.9677) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | median | -0.30946313681113224 | 0.0279 | [-0.5602155160500213, -0.10868803130117044] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | median | 0.041670142836494506 | 0.752 | [-0.059782371205462814, 0.3241090139274396] | UNRESOLVED | 43 [41, 44] (P = 0.9513) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | median | -0.020956047333584138 | 0.4515 | [-0.27871172104426023, 0.20862831917615265] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | median | 0.26894053132099316 | 0.9808 | [0.04709407819538569, 0.4745364827318781] | RESOLVED | 1 [1, 1] (P = 0.96305) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | p10 | -0.06449680385230816 | 0.2623 | [-0.24778388259061324, 0.1895841159258529] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | p10 | -0.2448196704826482 | 0.0297 | [-0.4938327147457813, -0.028190790067759153] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | p10 | 0.08017414264094591 | 0.7285 | [-0.1561957916798451, 0.2827313043305033] | UNRESOLVED | 6 [6, 6] (P = 0.96335) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | p10 | -0.010847443744631757 | 0.4913 | [-0.1730498981775952, 0.1529085001882481] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | p10 | 0.1201792722244166 | 0.8786 | [-0.03494623909385841, 0.16824602569263936] | UNRESOLVED | 9 [9, 9] (P = 0.95715) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | mean | 0.0862028339285239 | 0.8304 | [-0.057847040133271715, 0.22246548765242188] | UNRESOLVED | 4 [4, 4] (P = 0.9533049392669303) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | mean | -0.26745786237442526 | 0.0022 | [-0.4611861739105009, -0.10280684835603614] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | mean | 0.0633670484255201 | 0.7524 | [-0.08262910842230714, 0.2559091192971761] | UNRESOLVED | 12 [12, 12] (P = 0.9524488712969189) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | mean | -0.03175335525092626 | 0.3444 | [-0.1706798911799518, 0.11198474479988975] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | mean | 0.1931799570832362 | 0.9777 | [0.04751120763799104, 0.323185746168786] | RESOLVED | 2 [2, 2] (P = 0.9757115697789726) |

R1 (spec:68 verbatim: "- **R1 (boundary verdict).** An adjacent boundary is RESOLVED under a rule when P(order preserved) >= the target in T4; UNRESOLVED otherwise. The screen is reported as "resolving k of 5 boundaries under the mean rule, k' under the median and k'' under the min rule", each on that rule's own observed gap. The min-rule count is labelled descriptive (section 2); the mean and median counts are the calibrated ones; the p10 count is labelled near-extreme whenever the admitted site count is below 50. No verdict is read from the point gap alone."): resolving 1 of 5 boundaries under the mean rule, 1 under the median and 0 under the min rule; the min count is descriptive, the mean and median counts are the calibrated ones, and the p10 count is 0, labelled near-extreme (`n_admitted` minimum 3 < the RANK-10 floor 50).
R2 (spec:69): INVERTED boundaries — min 3 (Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25, Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15); median 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); p10 3 (Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25, Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); mean 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34).
R3 (spec:70): SPREAD-DECIDED — Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 under min (`near_extreme` false); every count above assumes normal i.i.d. sites and the figures are "lower bounds on the depth under any heavier left tail" (spec:70).

**T5 variance components** (spec:59, R4):

| composition | sites | decorations | site sd (population) | within sd | between sd | ICC | status |
|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 3 | 3 | 0.11492287477416978 | null | null | null | insufficient decorations |
| Fe25Co25Ni25Cr25 | 11 | 9 | 0.17038118442861147 | 0.09002225000120977 | 0.1572511182550767 | 0.7531668701570498 | ok |
| Cu26Ni9Cr31Co33 | 6 | 5 | 0.2124388719204427 | 0.20067466321680844 | 0.12197485999560147 | 0.2697797933110061 | ok |
| Ni34Fe6Cu29Co31 | 15 | 13 | 0.15509784353555459 | 0.1678807541798694 | 0.0 | 0.0 | ok |
| Cu8Cr23Mn35Co34 | 4 | 3 | 0.19821551880377436 | 0.28958054095480773 | 0.0 | 0.0 | ok |
| Cu22Fe30Co32Mn15 | 33 | 23 | 0.19354539428987005 | 0.11849695937973717 | 0.1587753146916506 | 0.6422643270515094 | ok |

R4 (spec:71; ICC band 0.2, the RANK-3 draft): Fe25Co25Ni25Cr25 (0.7531668701570498), Cu26Ni9Cr31Co33 (0.2697797933110061), Cu22Fe30Co32Mn15 (0.6422643270515094) — i.i.d. depth understated; decorations-needed figures for its pairs are lower bounds.

**T6 ridge** (spec:60, R5; `cutoff_A` 3.8, `ridge_alpha` 1.0; `n_sites_with_environment` 720):

| target | sites | status | R² in-sample | R² LOO | sigma in-sample | sigma LOO |
|---|---|---|---|---|---|---|
| eta | 720 | ok (`meaningful` true, `min_sites` 30) | 0.2534503436415766 | 0.227898274078004 | 0.21290617305637322 | 0.21651907614396407 |
| dG_OH | 720 | ok (`meaningful` true, `min_sites` 30) | 0.44400063830817993 | 0.4225653274256943 | 0.15048947941044324 | 0.15336293888250552 |
| dG_O | 720 | ok (`meaningful` true, `min_sites` 30) | 0.28595979472880984 | 0.26101160651715904 | 0.8118693492779453 | 0.8259307229987581 |
| dG_OOH | 720 | ok (`meaningful` true, `min_sites` 30) | 0.16838779187397068 | 0.1406468405027116 | 0.6754490843644956 | 0.6866224959806367 |

R5 (spec:72): `sigma_loo` (eta) 0.21651907614396407 V against the pooled site sd 0.24641032624300896 V (population sd over every `site_rows[].eta`, 720 sites — the same 720 sites the ridge is fitted on, so the comparison is on one population and identical in every policy block; computed by this script — post-hoc arithmetic on file values): sigma_LOO lies below the pooled site sd; the fit is descriptive and no R² threshold is a success criterion. Beside it, post-hoc and not the R5 comparison: the population sd over the 72 sites this policy admits is 0.20437771497726478 V.

### `--admit adsorbate-intact`

`status complete`; `settings.admit_definition`: "site_integrity all_states_adsorbate_intact: not desorbed, not dissociated, not migrated, converged; reconstruction ignored"; `B` 10000, `seed` 0, `level` 0.9, `target_prob` 0.95, `min_decorations` 2, `stems` `mpa0__*,mpa0_ext__*`, `reproduction_tolerance_V` 1e-06; `n_site_rows` 720; sha256_lf `f840674bdbf56456dcb5432ef77cf1483a5d1affea8a956cc4e558f31f1579e8`.

**T1 census** (spec:55): coverage is complete when observed = declared for every composition and `coverage.missing` is empty — no (0 stems missing in `coverage.missing`).

| composition | decorations (usable) | sites (admitted) | declared decorations x sites | bootstrap support C(2D-1, D) |
|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 30 (7) | 120 (8) | 3 x 12 | 1716 |
| Fe25Co25Ni25Cr25 | 30 (12) | 120 (19) | 3 x 12 | 1352078 |
| Cu26Ni9Cr31Co33 | 30 (11) | 120 (13) | 3 x 12 | 352716 |
| Ni34Fe6Cu29Co31 | 30 (13) | 120 (15) | 3 x 12 | 5200300 |
| Cu8Cr23Mn35Co34 | 30 (11) | 120 (16) | 3 x 12 | 352716 |
| Cu22Fe30Co32Mn15 | 30 (25) | 120 (38) | 3 x 12 | 63205303218876 |

**T2 statistics** (spec:56, R7; intervals at `settings.level` 0.9; the reproduction verdict at `tolerance_V` 1e-06 equals the docs/93 (a) verdict for the gated six, asserted):

| composition | banked rank | banked eta (V) | abs(census min − banked eta) (V) | reproduction | min [interval] | median [interval] | p10 [interval] | mean [interval] |
|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 1 | 0.43999606379672596 | 9.197e-11 | REPRODUCED | 0.4399960638886986 [0.4399960638886986, 0.6862106123389671] | 0.8105785294643928 [0.4945995053835457, 1.2150250066883626] | 0.4729863773328665 [0.4399960638886986, 0.835452112889478] | 0.8311683531015022 [0.6375829690779385, 1.0694121293441445] |
| Fe25Co25Ni25Cr25 | 2 | 0.4530565517906915 | 4.512e-10 | REPRODUCED | 0.4530565522419163 [0.4530565522419163, 0.557193286097216] | 1.1165669898739718 [0.9033552626798649, 1.250845484189254] | 0.5543729731738457 [0.4683471066707566, 0.8341228673633351] | 1.0065502389734828 [0.910539161913224, 1.1075059892789816] |
| Cu26Ni9Cr31Co33 | 3 | 0.4791918878366763 | 1.194e-10 | REPRODUCED | 0.4491684937492817 [0.4491684937492817, 0.5936955227013225] | 0.7249862610187696 [0.6475759560843093, 0.9943655948473218] | 0.5020926149051025 [0.4491684937492817, 0.7031553576639302] | 0.8145679578115901 [0.6926328261156854, 0.9343236498357588] |
| Ni34Fe6Cu29Co31 | 4 | 0.7258416193876736 | 3.955e-08 | REPRODUCED | 0.6790912935495492 [0.6790912935495492, 0.7859467359447043] | 0.9615557456723689 [0.9048504014100711, 1.0474846756205505] | 0.7387097348381626 [0.6790912935495492, 0.9118849457756122] | 0.9652606865062096 [0.9011076461743828, 1.036083856551227] |
| Cu8Cr23Mn35Co34 | 5 | 0.7557679418652832 | 1.442e-10 | REPRODUCED | 0.3622195377546671 [0.3622195377546671, 0.3862926021756987] | 0.5416822166677795 [0.41792914046578566, 0.7159027265388698] | 0.38354839936178386 [0.3622195377546671, 0.40354646345488554] | 0.6349393684660509 [0.5300923385886351, 0.729215321653557] |
| Cu22Fe30Co32Mn15 | 6 | 0.7956532031025425 | 2.095e-08 | REPRODUCED | 0.6855536132758706 [0.6855536132758706, 0.8038151059702994] | 1.2040631015188108 [1.1366539284832395, 1.2303044244529513] | 0.8309741687940214 [0.7972855669150629, 0.8868514214485534] | 1.11684068102403 [1.0558817922016102, 1.171324328150254] |

Census orders per rule (`census_orders.<rule>`; tau printed only when `complete`, `docs/91:63`): min: Cu8Cr23Mn35Co34 < Ni31Cr29Cu5Mn35 < Cu26Ni9Cr31Co33 < Fe25Co25Ni25Cr25 < Ni34Fe6Cu29Co31 < Cu22Fe30Co32Mn15 (tau-a 0.3333333333333333); median: Cu8Cr23Mn35Co34 < Cu26Ni9Cr31Co33 < Ni31Cr29Cu5Mn35 < Ni34Fe6Cu29Co31 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 (tau-a 0.06666666666666667); p10: Cu8Cr23Mn35Co34 < Ni31Cr29Cu5Mn35 < Cu26Ni9Cr31Co33 < Fe25Co25Ni25Cr25 < Ni34Fe6Cu29Co31 < Cu22Fe30Co32Mn15 (tau-a 0.3333333333333333); mean: Cu8Cr23Mn35Co34 < Cu26Ni9Cr31Co33 < Ni31Cr29Cu5Mn35 < Ni34Fe6Cu29Co31 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 (tau-a 0.06666666666666667).
R7 / spec:33: `mpa0_ext__` stems are present, so the `min` statistic above is the rank statistic of the second wave, not a re-screen value; the reproduction column uses the banked seeds only.

**T3 rank matrix** (spec:57; STABLE iff `stable.<f>.stable`, P(banked rank) >= `target_prob` 0.95):

*min* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0001 | 0.6733 | 0.0929 | 0.1472 | 0.0351 | 0.0514 | 1.6981 | 1 | 0.0001 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.078 | 0.3593 | 0.5553 | 0.0004 | 0.007 | 2.4991000000000003 | 2 | 0.078 | not stable |
| Cu26Ni9Cr31Co33 | 0.0 | 0.2487 | 0.5467 | 0.1987 | 0.0028 | 0.0031 | 1.9648999999999999 | 3 | 0.5467 | not stable |
| Ni34Fe6Cu29Co31 | 0.0 | 0.0 | 0.0005 | 0.0734 | 0.6891 | 0.237 | 4.1626 | 4 | 0.0734 | not stable |
| Cu8Cr23Mn35Co34 | 0.9999 | 0.0 | 0.0 | 0.0001 | 0.0 | 0.0 | 0.00030000000000000003 | 5 | 0.0 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0 | 0.0006 | 0.0253 | 0.2726 | 0.7015 | 4.675 | 6 | 0.7015 | not stable |

*median* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.1801 | 0.3071 | 0.1941 | 0.1538 | 0.1042 | 0.0607 | 1.8769999999999998 | 1 | 0.1801 | not stable |
| Fe25Co25Ni25Cr25 | 0.0003 | 0.018 | 0.0832 | 0.2133 | 0.523 | 0.1622 | 3.7273 | 2 | 0.018 | not stable |
| Cu26Ni9Cr31Co33 | 0.0253 | 0.4507 | 0.4114 | 0.0886 | 0.0237 | 0.0003 | 1.6356 | 3 | 0.4114 | not stable |
| Ni34Fe6Cu29Co31 | 0.0001 | 0.0354 | 0.2839 | 0.5249 | 0.1524 | 0.0033 | 2.8040000000000003 | 4 | 0.5249 | not stable |
| Cu8Cr23Mn35Co34 | 0.7942 | 0.1866 | 0.0187 | 0.0004 | 0.0001 | 0.0 | 0.22560000000000002 | 5 | 0.0001 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0022 | 0.0087 | 0.019 | 0.1966 | 0.7735 | 4.7305 | 6 | 0.7735 | not stable |

*p10* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0008 | 0.6252 | 0.181 | 0.1191 | 0.0328 | 0.0411 | 1.6812 | 1 | 0.0008 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.1024 | 0.3693 | 0.4436 | 0.0438 | 0.0409 | 2.5515000000000003 | 2 | 0.1024 | not stable |
| Cu26Ni9Cr31Co33 | 0.0003 | 0.2713 | 0.4395 | 0.2777 | 0.0097 | 0.0015 | 2.0297 | 3 | 0.4395 | not stable |
| Ni34Fe6Cu29Co31 | 0.0 | 0.0003 | 0.0093 | 0.1389 | 0.6528 | 0.1987 | 4.0403 | 4 | 0.1389 | not stable |
| Cu8Cr23Mn35Co34 | 0.9989 | 0.0008 | 0.0002 | 0.0001 | 0.0 | 0.0 | 0.0015 | 5 | 0.0 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0 | 0.0007 | 0.0206 | 0.2609 | 0.7178 | 4.6958 | 6 | 0.7178 | not stable |

*mean* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0644 | 0.3662 | 0.3536 | 0.1043 | 0.0864 | 0.0251 | 1.8574000000000002 | 1 | 0.0644 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.0052 | 0.0679 | 0.2806 | 0.5883 | 0.058 | 3.6260000000000003 | 2 | 0.0052 | not stable |
| Cu26Ni9Cr31Co33 | 0.0226 | 0.5375 | 0.4082 | 0.0258 | 0.0059 | 0.0 | 1.4549 | 3 | 0.4082 | not stable |
| Ni34Fe6Cu29Co31 | 0.0 | 0.0097 | 0.1645 | 0.5853 | 0.238 | 0.0025 | 3.0591 | 4 | 0.5853 | not stable |
| Cu8Cr23Mn35Co34 | 0.913 | 0.0814 | 0.0056 | 0.0 | 0.0 | 0.0 | 0.0926 | 5 | 0.0 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0 | 0.0002 | 0.004 | 0.0814 | 0.9144 | 4.91 | 6 | 0.9144 | not stable |

**T4 adjacent gaps** (spec:58, R1-R3):

| pair | rule | observed gap (V) | P(order) | gap interval (V) | verdict | decorations needed [MC bracket] |
|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | min | 0.013060488353217714 | 0.7487 | [-0.23315406009705075, 0.11719722220851736] | UNRESOLVED | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.86485, best 0.86485 at D = 10000 |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | min | -0.0038880584926346273 | 0.2639 | [-0.10802479234793427, 0.1406389704594062] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | min | 0.22992279980026753 | 0.995 | [0.0853957708482267, 0.33677824219542263] | RESOLVED | 2 [2, 2] (P = 0.9796) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | min | -0.31687175579488214 | 0.0 | [-0.42372719819003724, -0.2927986913738505] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | min | 0.3233340755212035 | 1.0 | [0.2992610111001719, 0.4415955682156323] | RESOLVED | 1 [1, 1] (P = 0.95875) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | median | 0.30598846040957906 | 0.823 | [-0.1629417058073841, 0.6691108396914198] | UNRESOLVED | 2 [2, 2] (P = 0.9545) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | median | -0.39158072885520223 | 0.0541 | [-0.5261933819830764, 5.752415972892777e-05] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | median | 0.23656948465359928 | 0.8789 | [-0.04596924443512762, 0.3488309430842227] | UNRESOLVED | 2 [2, 2] (P = 0.9783) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | median | -0.4198735290045894 | 0.0005 | [-0.6015714120510438, -0.22572041154239741] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | median | 0.6623808848510313 | 1.0 | [0.4623200586246594, 0.7922446556711975] | RESOLVED | 1 [1, 1] (P = 0.99975) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | p10 | 0.08138659584097918 | 0.7666 | [-0.26681392662482084, 0.3317545021542182] | UNRESOLVED | 27 [26, 29] (P = 0.9517) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | p10 | -0.05228035826874322 | 0.3453 | [-0.2936806204175392, 0.1406389704594062] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | p10 | 0.23661711993306012 | 0.9862 | [0.04341246712073503, 0.42016514452757675] | RESOLVED | 1 [1, 1] (P = 0.9608) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | p10 | -0.35516133547637874 | 0.0 | [-0.5276600923833947, -0.2949940536249824] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | p10 | 0.44742576943223755 | 1.0 | [0.40374253926914205, 0.5080153944278796] | RESOLVED | 1 [1, 1] (P = 0.9941) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | mean | 0.17538188587198067 | 0.8651 | [-0.07895311833364273, 0.394711584503258] | UNRESOLVED | 5 [5, 5] (P = 0.9623612466173631) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | mean | -0.19198228116189275 | 0.0175 | [-0.3556173670858561, -0.03930817132717108] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | mean | 0.15069272869461947 | 0.9679 | [0.01660953873244126, 0.29483635041206324] | RESOLVED | 3 [3, 3] (P = 0.9654218760463937) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | mean | -0.33032131804015863 | 0.0 | [-0.4576861156568763, -0.2149121197351113] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | mean | 0.48190131255797897 | 1.0 | [0.3704644901720574, 0.6010537844476239] | RESOLVED | 1 [1, 1] (P = 0.9980122239921267) |

R1 (spec:68 verbatim: "- **R1 (boundary verdict).** An adjacent boundary is RESOLVED under a rule when P(order preserved) >= the target in T4; UNRESOLVED otherwise. The screen is reported as "resolving k of 5 boundaries under the mean rule, k' under the median and k'' under the min rule", each on that rule's own observed gap. The min-rule count is labelled descriptive (section 2); the mean and median counts are the calibrated ones; the p10 count is labelled near-extreme whenever the admitted site count is below 50. No verdict is read from the point gap alone."): resolving 2 of 5 boundaries under the mean rule, 1 under the median and 2 under the min rule; the min count is descriptive, the mean and median counts are the calibrated ones, and the p10 count is 2, labelled near-extreme (`n_admitted` minimum 8 < the RANK-10 floor 50).
R2 (spec:69): INVERTED boundaries — min 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); median 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); p10 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); mean 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34).
R3 (spec:70): SPREAD-DECIDED — none; every count above assumes normal i.i.d. sites and the figures are "lower bounds on the depth under any heavier left tail" (spec:70).

**T5 variance components** (spec:59, R4):

| composition | sites | decorations | site sd (population) | within sd | between sd | ICC | status |
|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 8 | 7 | 0.32559842148935636 | 0.03861046375712929 | 0.35227919929554624 | 0.9881300161809787 | ok |
| Fe25Co25Ni25Cr25 | 19 | 12 | 0.29734522716803075 | 0.3528171800650349 | 0.0 | 0.0 | ok |
| Cu26Ni9Cr31Co33 | 13 | 11 | 0.2417580042972581 | 0.14708245665646627 | 0.20683620464205915 | 0.6641554162074579 | ok |
| Ni34Fe6Cu29Co31 | 15 | 13 | 0.15509784353555459 | 0.1678807541798694 | 0.0 | 0.0 | ok |
| Cu8Cr23Mn35Co34 | 16 | 11 | 0.27243059112615453 | 0.3329774341799532 | 0.0 | 0.0 | ok |
| Cu22Fe30Co32Mn15 | 38 | 25 | 0.19433802240930464 | 0.14169985409544109 | 0.13836504330971472 | 0.48809440932006465 | ok |

R4 (spec:71; ICC band 0.2, the RANK-3 draft): Ni31Cr29Cu5Mn35 (0.9881300161809787), Cu26Ni9Cr31Co33 (0.6641554162074579), Cu22Fe30Co32Mn15 (0.48809440932006465) — i.i.d. depth understated; decorations-needed figures for its pairs are lower bounds.

**T6 ridge** (spec:60, R5; `cutoff_A` 3.8, `ridge_alpha` 1.0; `n_sites_with_environment` 720):

| target | sites | status | R² in-sample | R² LOO | sigma in-sample | sigma LOO |
|---|---|---|---|---|---|---|
| eta | 720 | ok (`meaningful` true, `min_sites` 30) | 0.2534503436415766 | 0.227898274078004 | 0.21290617305637322 | 0.21651907614396407 |
| dG_OH | 720 | ok (`meaningful` true, `min_sites` 30) | 0.44400063830817993 | 0.4225653274256943 | 0.15048947941044324 | 0.15336293888250552 |
| dG_O | 720 | ok (`meaningful` true, `min_sites` 30) | 0.28595979472880984 | 0.26101160651715904 | 0.8118693492779453 | 0.8259307229987581 |
| dG_OOH | 720 | ok (`meaningful` true, `min_sites` 30) | 0.16838779187397068 | 0.1406468405027116 | 0.6754490843644956 | 0.6866224959806367 |

R5 (spec:72): `sigma_loo` (eta) 0.21651907614396407 V against the pooled site sd 0.24641032624300896 V (population sd over every `site_rows[].eta`, 720 sites — the same 720 sites the ridge is fitted on, so the comparison is on one population and identical in every policy block; computed by this script — post-hoc arithmetic on file values): sigma_LOO lies below the pooled site sd; the fit is descriptive and no R² threshold is a success criterion. Beside it, post-hoc and not the R5 comparison: the population sd over the 109 sites this policy admits is 0.2926124686487553 V.

### `--admit two-pathway`

`status complete`; `settings.admit_definition`: "site_integrity pathway in {cus, bridge}: OOH state is *OOH or *O2+H_b; eta unchanged"; `B` 10000, `seed` 0, `level` 0.9, `target_prob` 0.95, `min_decorations` 2, `stems` `mpa0__*,mpa0_ext__*`, `reproduction_tolerance_V` 1e-06; `n_site_rows` 720; sha256_lf `31fb63eba1d3ed09c5793b4dc632e543c5036443625de3103dadccdc2f9c7149`. The two-pathway site set is the rule whose pathway-undefined exclusion is Proposed `[CENSUS-6 2026-09-__: ____]` (`docs/91:63`).

**T1 census** (spec:55): coverage is complete when observed = declared for every composition and `coverage.missing` is empty — no (0 stems missing in `coverage.missing`).

| composition | decorations (usable) | sites (admitted) | declared decorations x sites | bootstrap support C(2D-1, D) |
|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 30 (22) | 120 (33) | 3 x 12 | 1052049481860 |
| Fe25Co25Ni25Cr25 | 30 (19) | 120 (32) | 3 x 12 | 17672631900 |
| Cu26Ni9Cr31Co33 | 30 (14) | 120 (16) | 3 x 12 | 20058300 |
| Ni34Fe6Cu29Co31 | 30 (19) | 120 (26) | 3 x 12 | 17672631900 |
| Cu8Cr23Mn35Co34 | 30 (14) | 120 (20) | 3 x 12 | 20058300 |
| Cu22Fe30Co32Mn15 | 30 (25) | 120 (42) | 3 x 12 | 63205303218876 |

**T2 statistics** (spec:56, R7; intervals at `settings.level` 0.9; the reproduction verdict at `tolerance_V` 1e-06 equals the docs/93 (a) verdict for the gated six, asserted):

| composition | banked rank | banked eta (V) | abs(census min − banked eta) (V) | reproduction | min [interval] | median [interval] | p10 [interval] | mean [interval] |
|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 1 | 0.43999606379672596 | 9.197e-11 | REPRODUCED | 0.4399960638886986 [0.4399960638886986, 0.6076117841441677] | 1.0302754377200056 [0.9349464465898185, 1.1438443786578016] | 0.6092782351063155 [0.48712508309465274, 0.6868020261105491] | 1.0066941902309863 [0.9136077758369106, 1.1064328385069242] |
| Fe25Co25Ni25Cr25 | 2 | 0.4530565517906915 | 4.512e-10 | REPRODUCED | 0.4530565522419163 [0.4530565522419163, 0.5430917214803648] | 1.196610243867438 [1.0226636296325164, 1.288066720716186] | 0.5600329556650654 [0.49951402505948117, 0.8637036860196456] | 1.0994674098873185 [0.9878263334805021, 1.2026252880125528] |
| Cu26Ni9Cr31Co33 | 3 | 0.4791918878366763 | 1.194e-10 | REPRODUCED | 0.4491684937492817 [0.4491684937492817, 0.5150704178544048] | 0.7942002267328747 [0.6745241536402725, 1.032390458829438] | 0.49713115290522614 [0.4491684937492817, 0.6475759560843093] | 0.8414404063614656 [0.7235418837806922, 0.9555483165185441] |
| Ni34Fe6Cu29Co31 | 4 | 0.7258416193876736 | 3.955e-08 | REPRODUCED | 0.6790912935495492 [0.6790912935495492, 0.7072184007671347] | 1.040982169192942 [0.9393920596009178, 1.1371864013040645] | 0.7165300298515207 [0.6977145615543902, 0.8286523799498554] | 1.0986178871862764 [0.9878466509541839, 1.2182493900989348] |
| Cu8Cr23Mn35Co34 | 5 | 0.7557679418652832 | 1.442e-10 | REPRODUCED | 0.3622195377546671 [0.3622195377546671, 0.3862926021756987] | 0.6453899344432217 [0.4329082507142896, 0.9451884339539456] | 0.38574376161291574 [0.3640780036339873, 0.42655874667232574] | 0.7016798169108617 [0.6044630539916223, 0.7948320973841582] |
| Cu22Fe30Co32Mn15 | 6 | 0.7956532031025425 | 2.095e-08 | REPRODUCED | 0.6855536132758706 [0.6855536132758706, 0.8038151059702994] | 1.2040631015188108 [1.1305190767403968, 1.2303044244529513] | 0.8446798175460384 [0.8021827212064903, 0.8884745169603749] | 1.1414625861655976 [1.0772529252850265, 1.1982724539841225] |

Census orders per rule (`census_orders.<rule>`; tau printed only when `complete`, `docs/91:63`): min: Cu8Cr23Mn35Co34 < Ni31Cr29Cu5Mn35 < Cu26Ni9Cr31Co33 < Fe25Co25Ni25Cr25 < Ni34Fe6Cu29Co31 < Cu22Fe30Co32Mn15 (tau-a 0.3333333333333333); median: Cu8Cr23Mn35Co34 < Cu26Ni9Cr31Co33 < Ni31Cr29Cu5Mn35 < Ni34Fe6Cu29Co31 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 (tau-a 0.06666666666666667); p10: Cu8Cr23Mn35Co34 < Cu26Ni9Cr31Co33 < Fe25Co25Ni25Cr25 < Ni31Cr29Cu5Mn35 < Ni34Fe6Cu29Co31 < Cu22Fe30Co32Mn15 (tau-a 0.06666666666666667); mean: Cu8Cr23Mn35Co34 < Cu26Ni9Cr31Co33 < Ni31Cr29Cu5Mn35 < Ni34Fe6Cu29Co31 < Fe25Co25Ni25Cr25 < Cu22Fe30Co32Mn15 (tau-a 0.06666666666666667).
R7 / spec:33: `mpa0_ext__` stems are present, so the `min` statistic above is the rank statistic of the second wave, not a re-screen value; the reproduction column uses the banked seeds only.

**T3 rank matrix** (spec:57; STABLE iff `stable.<f>.stable`, P(banked rank) >= `target_prob` 0.95):

*min* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0 | 0.6432 | 0.0973 | 0.257 | 0.0021 | 0.0004 | 1.6192 | 1 | 0.0 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.0871 | 0.3624 | 0.5496 | 0.0 | 0.0009 | 2.4652000000000003 | 2 | 0.0871 | not stable |
| Cu26Ni9Cr31Co33 | 0.0 | 0.2697 | 0.5403 | 0.1882 | 0.0005 | 0.0013 | 1.9234 | 3 | 0.5403 | not stable |
| Ni34Fe6Cu29Co31 | 0.0 | 0.0 | 0.0 | 0.0045 | 0.7697 | 0.2258 | 4.2213 | 4 | 0.0045 | not stable |
| Cu8Cr23Mn35Co34 | 1.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 5 | 0.0 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0 | 0.0 | 0.0007 | 0.2277 | 0.7716 | 4.7709 | 6 | 0.7716 | not stable |

*median* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0064 | 0.0568 | 0.3901 | 0.4576 | 0.0837 | 0.0054 | 2.5716 | 1 | 0.0064 | not stable |
| Fe25Co25Ni25Cr25 | 0.0003 | 0.0098 | 0.0406 | 0.0701 | 0.3945 | 0.4847 | 4.3028 | 2 | 0.0098 | not stable |
| Cu26Ni9Cr31Co33 | 0.2132 | 0.6565 | 0.0957 | 0.0319 | 0.0026 | 0.0001 | 0.9545 | 3 | 0.0957 | not stable |
| Ni34Fe6Cu29Co31 | 0.0038 | 0.0668 | 0.4458 | 0.4155 | 0.0574 | 0.0107 | 2.488 | 4 | 0.4155 | not stable |
| Cu8Cr23Mn35Co34 | 0.7761 | 0.2041 | 0.018 | 0.0018 | 0.0 | 0.0 | 0.2455 | 5 | 0.0 | not stable |
| Cu22Fe30Co32Mn15 | 0.0002 | 0.006 | 0.0098 | 0.0231 | 0.4618 | 0.4991 | 4.4376 | 6 | 0.4991 | not stable |

*p10* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0005 | 0.186 | 0.2856 | 0.5136 | 0.0107 | 0.0036 | 2.3588 | 1 | 0.0005 | not stable |
| Fe25Co25Ni25Cr25 | 0.0002 | 0.1745 | 0.4817 | 0.2569 | 0.0362 | 0.0505 | 2.3059000000000003 | 2 | 0.1745 | not stable |
| Cu26Ni9Cr31Co33 | 0.0032 | 0.6374 | 0.229 | 0.1214 | 0.0079 | 0.0011 | 1.4966999999999997 | 3 | 0.229 | not stable |
| Ni34Fe6Cu29Co31 | 0.0 | 0.0 | 0.0023 | 0.1042 | 0.8467 | 0.0468 | 3.938 | 4 | 0.1042 | not stable |
| Cu8Cr23Mn35Co34 | 0.9961 | 0.0021 | 0.0014 | 0.0004 | 0.0 | 0.0 | 0.0060999999999999995 | 5 | 0.0 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0 | 0.0 | 0.0035 | 0.0985 | 0.898 | 4.894500000000001 | 6 | 0.898 | not stable |

*mean* (`n_replicates` 10000, `n_dropped` 0):

| composition | r1 | r2 | r3 | r4 | r5 | r6 | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 0.0 | 0.0314 | 0.7172 | 0.1825 | 0.057 | 0.0119 | 2.3008 | 1 | 0.0 | not stable |
| Fe25Co25Ni25Cr25 | 0.0 | 0.0024 | 0.1165 | 0.3313 | 0.3235 | 0.2263 | 3.6548 | 2 | 0.0024 | not stable |
| Cu26Ni9Cr31Co33 | 0.0619 | 0.9025 | 0.0324 | 0.0031 | 0.0001 | 0.0 | 0.9769999999999999 | 3 | 0.0324 | not stable |
| Ni34Fe6Cu29Co31 | 0.0 | 0.0018 | 0.1252 | 0.3623 | 0.2772 | 0.2335 | 3.6154 | 4 | 0.3623 | not stable |
| Cu8Cr23Mn35Co34 | 0.9381 | 0.0619 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0619 | 5 | 0.0 | not stable |
| Cu22Fe30Co32Mn15 | 0.0 | 0.0 | 0.0087 | 0.1208 | 0.3422 | 0.5283 | 4.3901 | 6 | 0.5283 | not stable |

**T4 adjacent gaps** (spec:58, R1-R3):

| pair | rule | observed gap (V) | P(order) | gap interval (V) | verdict | decorations needed [MC bracket] |
|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | min | 0.013060488353217714 | 0.7208 | [-0.1545552319022514, 0.10309565759166617] | UNRESOLVED / SPREAD-DECIDED | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.2555, best 0.4952 at D = 1; `order_reverses_at_depth` |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | min | -0.0038880584926346273 | 0.2574 | [-0.09392322773108308, 0.06201386561248845] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | min | 0.22992279980026753 | 0.9982 | [0.16402087569514445, 0.258049907017853] | RESOLVED / SPREAD-DECIDED | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.058, best 0.6641 at D = 1; `order_reverses_at_depth` |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | min | -0.31687175579488214 | 0.0 | [-0.3449988630124676, -0.2927986913738505] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | min | 0.3233340755212035 | 1.0 | [0.2992610111001719, 0.4415955682156323] | RESOLVED | 3 [2, 3] (P = 0.96045) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | median | 0.16633480614743235 | 0.9068 | [-0.04115274295012169, 0.3051549027197211] | UNRESOLVED | 8 [8, 9] (P = 0.95) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | median | -0.40241001713456326 | 0.0129 | [-0.5696655056951121, -0.0955311675932804] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | median | 0.24678194246006724 | 0.9206 | [-0.03280984917495289, 0.4138107396109536] | UNRESOLVED | 4 [3, 4] (P = 0.96635) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | median | -0.3955922347497203 | 0.0131 | [-0.6042864567800749, -0.08821094926959328] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | median | 0.5586731670755891 | 0.999 | [0.24727937496854854, 0.7379275154881652] | RESOLVED | 1 [1, 1] (P = 0.99725) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | p10 | -0.04924527944125012 | 0.4191 | [-0.15183443014277898, 0.2517562715467125] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | p10 | -0.06290180275983925 | 0.2501 | [-0.31862818316148833, 0.09882806311527814] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | p10 | 0.21939887694629456 | 0.9906 | [0.06936287032267041, 0.32777897035990267] | RESOLVED | 46 [44, 47] (P = 0.9518) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | p10 | -0.33078626823860496 | 0.0 | [-0.4435225660450646, -0.2927986913738505] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | p10 | 0.45893605593312264 | 1.0 | [0.40073328677862946, 0.5069306412023395] | RESOLVED | 1 [1, 1] (P = 0.9833) |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | mean | 0.09277321965633223 | 0.8528 | [-0.05502538303162889, 0.2324896229162532] | UNRESOLVED | 18 [18, 18] (P = 0.9539440390658319) |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | mean | -0.25802700352585295 | 0.0034 | [-0.4152842506938588, -0.09565105735612538] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | mean | 0.25717748082481084 | 0.9967 | [0.09874805598419006, 0.4251442258556975] | RESOLVED | 3 [3, 3] (P = 0.9764736065930983) |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | mean | -0.3969380702754147 | 0.0 | [-0.5517709383723667, -0.24828136955645747] | INVERTED | observed gap is not positive under this rule; the banked order is inverted here |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | mean | 0.4397827692547359 | 1.0 | [0.32786588905223696, 0.5509830365779015] | RESOLVED | 1 [1, 1] (P = 0.9909564822147898) |

R1 (spec:68 verbatim: "- **R1 (boundary verdict).** An adjacent boundary is RESOLVED under a rule when P(order preserved) >= the target in T4; UNRESOLVED otherwise. The screen is reported as "resolving k of 5 boundaries under the mean rule, k' under the median and k'' under the min rule", each on that rule's own observed gap. The min-rule count is labelled descriptive (section 2); the mean and median counts are the calibrated ones; the p10 count is labelled near-extreme whenever the admitted site count is below 50. No verdict is read from the point gap alone."): resolving 2 of 5 boundaries under the mean rule, 1 under the median and 2 under the min rule; the min count is descriptive, the mean and median counts are the calibrated ones, and the p10 count is 2, labelled near-extreme (`n_admitted` minimum 16 < the RANK-10 floor 50).
R2 (spec:69): INVERTED boundaries — min 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); median 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); p10 3 (Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25, Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34); mean 2 (Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33, Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34).
R3 (spec:70): SPREAD-DECIDED — Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 under min (`near_extreme` false); Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 under min (`near_extreme` false); every count above assumes normal i.i.d. sites and the figures are "lower bounds on the depth under any heavier left tail" (spec:70).

**T5 variance components** (spec:59, R4):

| composition | sites | decorations | site sd (population) | within sd | between sd | ICC | status |
|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 | 33 | 22 | 0.31881122415675445 | 0.33152637622248426 | 0.0 | 0.0 | ok |
| Fe25Co25Ni25Cr25 | 32 | 19 | 0.3417410486417324 | 0.3201750457186892 | 0.13682696662519955 | 0.1544258905371715 | ok |
| Cu26Ni9Cr31Co33 | 16 | 14 | 0.2630521957609137 | 0.14708245665646627 | 0.23034897435106838 | 0.7103746178209777 | ok |
| Ni34Fe6Cu29Co31 | 26 | 19 | 0.3634104627717708 | 0.39601470360734514 | 0.0 | 0.0 | ok |
| Cu8Cr23Mn35Co34 | 20 | 14 | 0.27810934955940564 | 0.3100816364288015 | 0.0 | 0.0 | ok |
| Cu22Fe30Co32Mn15 | 42 | 25 | 0.2472013512959582 | 0.274345136304408 | 0.0 | 0.0 | ok |

R4 (spec:71; ICC band 0.2, the RANK-3 draft): Cu26Ni9Cr31Co33 (0.7103746178209777) — i.i.d. depth understated; decorations-needed figures for its pairs are lower bounds.

**T6 ridge** (spec:60, R5; `cutoff_A` 3.8, `ridge_alpha` 1.0; `n_sites_with_environment` 720):

| target | sites | status | R² in-sample | R² LOO | sigma in-sample | sigma LOO |
|---|---|---|---|---|---|---|
| eta | 720 | ok (`meaningful` true, `min_sites` 30) | 0.2534503436415766 | 0.227898274078004 | 0.21290617305637322 | 0.21651907614396407 |
| dG_OH | 720 | ok (`meaningful` true, `min_sites` 30) | 0.44400063830817993 | 0.4225653274256943 | 0.15048947941044324 | 0.15336293888250552 |
| dG_O | 720 | ok (`meaningful` true, `min_sites` 30) | 0.28595979472880984 | 0.26101160651715904 | 0.8118693492779453 | 0.8259307229987581 |
| dG_OOH | 720 | ok (`meaningful` true, `min_sites` 30) | 0.16838779187397068 | 0.1406468405027116 | 0.6754490843644956 | 0.6866224959806367 |

R5 (spec:72): `sigma_loo` (eta) 0.21651907614396407 V against the pooled site sd 0.24641032624300896 V (population sd over every `site_rows[].eta`, 720 sites — the same 720 sites the ridge is fitted on, so the comparison is on one population and identical in every policy block; computed by this script — post-hoc arithmetic on file values): sigma_LOO lies below the pooled site sd; the fit is descriptive and no R² threshold is a success criterion. Beside it, post-hoc and not the R5 comparison: the population sd over the 169 sites this policy admits is 0.3376792512213231 V.

### T7 banked reference (spec:61) — from `banked_reference.pairs[]` (identical in every policy file, asserted; `target_prob` 0.95, `n_sites_per_decoration` 4; columns: `pairs[].{better, worse, sigma_a, sigma_b}`, "own" cells from `pairs[].own_gap.<rule>.{gap_V, gap_source, decorations_needed, decorations_needed_bracket, achieved_prob}`, "at the banked min gap" cells from `pairs[].hypothetical_min_gap.<rule>.{...}` with `log10_n_sites_asymptotic` where `equal_spreads`)

| pair | sigma a / b | rule | own banked gap (V, source) | decorations on own gap [bracket] | P | decorations at the banked min gap [bracket] | P | log10 N Gumbel (sa = sb only) |
|---|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | 0.3241490799729384 / 0.3285840051032546 | min | 0.01306048799396553 (banked eta (min rule)) | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.489, best 0.5161 at D = 1; `order_reverses_at_depth` | P(10000) = 0.489 | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.489, best 0.5161 at D = 1; `order_reverses_at_depth` | P(10000) = 0.489 | — |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | 0.3241490799729384 / 0.3285840051032546 | median | — (no box estimate) | no box estimate of this rule's gap | — | 1331 [1284, 1375] (P = 0.95005) | 0.95005 | — |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | 0.3241490799729384 / 0.3285840051032546 | p10 | — (no box estimate) | no box estimate of this rule's gap | — | 7748 [7477, 8012] (P = 0.95) | 0.95 | — |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | 0.3241490799729384 / 0.3285840051032546 | mean | 0.1363938479267347 (banked eta_mean) | 8 [8, 8] (P = 0.9527009531092878) | 0.9527009531092878 | 845 [845, 845] (P = 0.9500233737666804) | 0.9500233737666804 | — |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | 0.3285840051032546 / 0.27299855829648617 | min | 0.026135336045984836 (banked eta (min rule)) | 790 [680, 912] (P = 0.95) | 0.95 | 790 [680, 912] (P = 0.95) | 0.95 | — |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | 0.3285840051032546 / 0.27299855829648617 | median | — (no box estimate) | no box estimate of this rule's gap | — | 286 [274, 296] (P = 0.95015) | 0.95015 | — |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | 0.3285840051032546 / 0.27299855829648617 | p10 | — (no box estimate) | no box estimate of this rule's gap | — | 38 [36, 39] (P = 0.9509) | 0.9509 | — |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | 0.3285840051032546 / 0.27299855829648617 | mean | -0.13069789524184616 (banked eta_mean) | INVERTED: the banked gap under this rule is not positive | — | 181 [181, 181] (P = 0.9501342203916995) | 0.9501342203916995 | — |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | 0.27299855829648617 / 0.19446118295446618 | min | 0.24664973155099723 (banked eta (min rule)) | 2 [2, 2] (P = 0.96215) | 0.96215 | 2 [2, 2] (P = 0.96215) | 0.96215 | — |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | 0.27299855829648617 / 0.19446118295446618 | median | — (no box estimate) | no box estimate of this rule's gap | — | 2 [2, 2] (P = 0.9636) | 0.9636 | — |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | 0.27299855829648617 / 0.19446118295446618 | p10 | — (no box estimate) | no box estimate of this rule's gap | — | 2 [2, 2] (P = 0.9809) | 0.9809 | — |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | 0.27299855829648617 / 0.19446118295446618 | mean | 0.08505928424484421 (banked eta_mean) | 11 [11, 11] (P = 0.9538462939327911) | 0.9538462939327911 | 2 [2, 2] (P = 0.981300551716995) | 0.981300551716995 | — |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | 0.19446118295446618 / 0.13523748906747102 | min | 0.029926322477609624 (banked eta (min rule)) | 17 [16, 18] (P = 0.95095) | 0.95095 | 17 [16, 18] (P = 0.95095) | 0.95095 | — |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | 0.19446118295446618 / 0.13523748906747102 | median | — (no box estimate) | no box estimate of this rule's gap | — | 67 [65, 70] (P = 0.9504) | 0.9504 | — |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | 0.19446118295446618 / 0.13523748906747102 | p10 | — (no box estimate) | no box estimate of this rule's gap | — | 10 [9, 10] (P = 0.95425) | 0.95425 | — |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | 0.19446118295446618 / 0.13523748906747102 | mean | 0.05739712498921734 (banked eta_mean) | 12 [12, 12] (P = 0.9534096126948831) | 0.9534096126948831 | 43 [43, 43] (P = 0.9512390574824467) | 0.9512390574824467 | — |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | 0.13523748906747102 / 0.18412911957317757 | min | 0.03988526123725933 (banked eta (min rule)) | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.0053, best 0.48695 at D = 1; `order_reverses_at_depth` | P(10000) = 0.0053 | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.0053, best 0.48695 at D = 1; `order_reverses_at_depth` | P(10000) = 0.0053 | — |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | 0.13523748906747102 / 0.18412911957317757 | median | — (no box estimate) | no box estimate of this rule's gap | — | 35 [33, 36] (P = 0.9521) | 0.9521 | — |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | 0.13523748906747102 / 0.18412911957317757 | p10 | — (no box estimate) | no box estimate of this rule's gap | — | not resolvable by this statistic at <= 10000 decorations; P(10000) = 0.0, best 0.49735 at D = 1; `order_reverses_at_depth` | P(10000) = 0.0 | — |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | 0.13523748906747102 / 0.18412911957317757 | mean | 0.02930725189842609 (banked eta_mean) | 42 [42, 42] (P = 0.9518179324959004) | 0.9518179324959004 | 23 [23, 23] (P = 0.9529899735038732) | 0.9529899735038732 | — |

These rows reproduce spec Tables A / A' (spec:101-117) at `settings.seed` 0; spec:171 notes that simulated counts move within their brackets between random streams. The five min-rule cells against spec:103-107, cell by cell ("equal" for a count is equality of the integer count; for a saturated cell it is equality at the three decimals the spec prints): spec:103 "sat., P(10000) = 0.489, best 0.516 at D = 1, rev." — equal at the spec's printed precision (file P(10000) 0.489, best 0.5161 at D = 1); spec:104 "790 [680, 912] (P = 0.9500)" — equal; spec:105 "2 [2, 2] (P = 0.962)" — equal; spec:106 "17 [16, 18] (P = 0.951)" — equal; spec:107 "sat., P(10000) = 0.005, best 0.487 at D = 1, rev." — equal at the spec's printed precision (file P(10000) 0.0053, best 0.48695 at D = 1).

### T8 comparison (spec:62, R6) — `--compare`

`policies`: all, no-desorbed, intact, adsorbate-intact, two-pathway; `target_prob` 0.95; `inputs[]` (each `sha256_lf` equals this script's own hash of that file where the file is present, asserted): all `complete` `409a6d582ef4…`; no-desorbed `complete` `a6b7b6652af2…`; intact `complete` `338da000c7fd…`; adsorbate-intact `complete` `f840674bdbf5…`; two-pathway `complete` `31fb63eba1d3…`.

| pair | rule | all: verdict (P) | no-desorbed: verdict (P) | intact: verdict (P) | adsorbate-intact: verdict (P) | two-pathway: verdict (P) | R6 |
|---|---|---|---|---|---|---|---|
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | min | UNRESOLVED / SPREAD-DECIDED (0.7488) | UNRESOLVED / SPREAD-DECIDED (0.72) | INVERTED (0.078) | UNRESOLVED (0.7487) | UNRESOLVED / SPREAD-DECIDED (0.7208) | POLICY-DEPENDENT |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | min | INVERTED (0.2447) | INVERTED (0.2752) | INVERTED (0.0103) | INVERTED (0.2639) | INVERTED (0.2574) | - |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | min | RESOLVED / SPREAD-DECIDED (1.0) | RESOLVED (0.9928) | UNRESOLVED (0.6942) | RESOLVED (0.995) | RESOLVED / SPREAD-DECIDED (0.9982) | POLICY-DEPENDENT |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | min | INVERTED (0.0) | INVERTED (0.0) | UNRESOLVED / SPREAD-DECIDED (0.8885) | INVERTED (0.0) | INVERTED (0.0) | POLICY-DEPENDENT |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | min | RESOLVED (1.0) | RESOLVED (1.0) | INVERTED (0.3479) | RESOLVED (1.0) | RESOLVED (1.0) | POLICY-DEPENDENT |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | median | INVERTED (0.4044) | UNRESOLVED (0.6683) | UNRESOLVED (0.8432) | UNRESOLVED (0.823) | UNRESOLVED (0.9068) | POLICY-DEPENDENT |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | median | INVERTED (0.0) | INVERTED (0.0284) | INVERTED (0.0279) | INVERTED (0.0541) | INVERTED (0.0129) | - |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | median | RESOLVED (0.9988) | UNRESOLVED (0.9152) | UNRESOLVED (0.752) | UNRESOLVED (0.8789) | UNRESOLVED (0.9206) | POLICY-DEPENDENT |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | median | UNRESOLVED (0.8806) | INVERTED (0.022) | INVERTED (0.4515) | INVERTED (0.0005) | INVERTED (0.0131) | POLICY-DEPENDENT |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | median | RESOLVED (0.9621) | RESOLVED (0.9952) | RESOLVED (0.9808) | RESOLVED (1.0) | RESOLVED (0.999) | - |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | p10 | INVERTED (0.3368) | UNRESOLVED / SPREAD-DECIDED (0.4966) | INVERTED (0.2623) | UNRESOLVED (0.7666) | INVERTED (0.4191) | POLICY-DEPENDENT |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | p10 | INVERTED (0.1421) | INVERTED (0.37) | INVERTED (0.0297) | INVERTED (0.3453) | INVERTED (0.2501) | - |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | p10 | RESOLVED (0.9998) | RESOLVED (0.9874) | UNRESOLVED (0.7285) | RESOLVED (0.9862) | RESOLVED (0.9906) | POLICY-DEPENDENT |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | p10 | INVERTED (0.0859) | INVERTED (0.0002) | INVERTED (0.4913) | INVERTED (0.0) | INVERTED (0.0) | - |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | p10 | RESOLVED (0.9921) | RESOLVED (1.0) | UNRESOLVED (0.8786) | RESOLVED (1.0) | RESOLVED (1.0) | POLICY-DEPENDENT |
| Ni31Cr29Cu5Mn35 < Fe25Co25Ni25Cr25 | mean | UNRESOLVED (0.6605) | UNRESOLVED (0.5879) | UNRESOLVED (0.8304) | UNRESOLVED (0.8651) | UNRESOLVED (0.8528) | - |
| Fe25Co25Ni25Cr25 < Cu26Ni9Cr31Co33 | mean | INVERTED (0.0) | INVERTED (0.0091) | INVERTED (0.0022) | INVERTED (0.0175) | INVERTED (0.0034) | - |
| Cu26Ni9Cr31Co33 < Ni34Fe6Cu29Co31 | mean | RESOLVED (0.9999) | RESOLVED (0.9873) | UNRESOLVED (0.7524) | RESOLVED (0.9679) | RESOLVED (0.9967) | POLICY-DEPENDENT |
| Ni34Fe6Cu29Co31 < Cu8Cr23Mn35Co34 | mean | INVERTED (0.0746) | INVERTED (0.0) | INVERTED (0.3444) | INVERTED (0.0) | INVERTED (0.0) | - |
| Cu8Cr23Mn35Co34 < Cu22Fe30Co32Mn15 | mean | RESOLVED (0.9999) | RESOLVED (1.0) | RESOLVED (0.9777) | RESOLVED (1.0) | RESOLVED (1.0) | - |

Policy-dependent boundaries: `n_policy_dependent` 11 of 20.
R6 (spec:73 verbatim: "- **R6 (policy dependence).** A boundary whose R1 verdict differs between the admission policies is reported as POLICY-DEPENDENT by the `--compare` readout, with every policy's P value (T8)."): stated as written from the table above.

## What changed and what did not; named risks (`docs/91:77-87`)

- **Nothing registered moved.** No line of docs/43 is added or edited, no THRESHOLD is registered, no prediction is scored, no S8 or melt decision is taken, `results/r4_melt_list.json` is untouched, nothing enters the body-figure ledger (`docs/91:90`). `results/r4_validate.json`, `r4_screen_box.json` and `r4_gated.json` are read from their tracked LF copies and not rewritten (`docs/91:73`).
- **Every entrant slot remains blank** (each slot string read from its docs/91 line): `[CENSUS-1 2026-09-__: ____]` reproduction bars (`:52`); `[CENSUS-2 2026-09-__: ____]` O-O bands (`:56`); `[CENSUS-3 2026-09-__: ____]` hydrogen window (`:57`); `[CENSUS-4 2026-09-__: ____]` per-atom reconstruction bar (`:58`); `[CENSUS-5 2026-09-__: ____]` label priority (`:58`); `[CENSUS-6 2026-09-__: ____]` pathway-undefined exclusion (`:63`); `[CENSUS-7 2026-09-__: ____]` fragment (ZPE − TS) (`:36`); `[CENSUS-8 2026-09-__: MH-1 head ____ / not run]` the elective MH-1 leg (`:40`); `[CENSUS-9 2026-09-__: UMA-S-1p2 oc22 leg — build and run / defer ____]` the elective UMA-S-1p2 leg (`:42`); and the rank-resolution slots `[RANK-1 order-probability target: ______]`, `[RANK-2 interval level: ______]`, `[RANK-3 ICC band: ______]`, `[RANK-4 ridge site floor: ______]`, `[RANK-5 neighbour cutoff: ______]`, `[RANK-6 ridge penalty: ______]`, `[RANK-7 minimum decorations: ______]`, `[RANK-8 replicates and seed: ______]`, `[RANK-9 depth ceiling and reversal tolerance: ______]`, `[RANK-10 near-extreme floor: ______]` (spec:80-89).
- **Pending.** 0 manifests listed missing (). omat0: landed in full (12/12). mp0: landed in full (12/12). matpes: landed in full (12/12). CENSUS-3: landed in full (54/54). CENSUS-3 also gates the rank-resolution second wave (`coverage.missing`). MH-1 and UMA-S-1p2 are not run (`docs/91:40`, `:42`).
- **Named risks, each decided from a file value.** Risk 1 (contention): wall 144.11 h over the landed window against the planning walls of section (e); the events are `docs/93:170-171`. Risk 2 (weight identity): the CENSUS-1 verdicts are those of `docs/93:21` and are unchanged (T2 asserts them); `docs/91:80`: "The three other checkpoints carry no historical claim at all". Risk 3 (thread count): every landed result records `environment.threads` 2 (asserted over 103 results). Risk 4 (site enumeration): a standing caveat, not an event. Risk 5 (kill granularity): stems with a log and neither a result file nor a live lock — none (from the `logs/` and `results/` directory listings). Risk 6: `manifest.model.historical_label` reads `medium-mpa-0` on every landed manifest (asserted) while `model.filename` differs per tag: mpa0 `macempa0mediummodel`, omat0 `maceomat0mediummodel`, mp0 `20231203mace128L1_epoch199model`, matpes `MACEmatpesr2scanomatftmodel`. Risk 7 (BFGS cap): unconverged sites per model mpa0 8 of 144, omat0 3 of 144, mp0 2 of 144, matpes 7 of 144 (Table C3); a model's min-site eta on an unconverged site: omat0 Ni34Fe6Cu29Co31. Risk 8 (ensemble cost): per-checkpoint realised mean against the CENSUS-1 mean 18126.3 s — omat0 0.61x (`docs/93:266` reads 0.63x on its six: DIFFERS at two decimals), mp0 0.75x, matpes 0.58x (the MPA-0 planning band 6132.192-10257.948 s, `docs/91:67`).
- **Post-hoc readings in this file, each changing no verdict:** per-model H_TRANSFERRED fractions and per-model INTEGRITY on non-CENSUS-1 sites (b); the non-mpa0 winner columns of B2 and the non-mpa0 entries of the unconverged-min-site sentence of (c); per-model winner persistence (C4) and the per-model tau; section (d) under the other models; the log-stamp wall / throughput arithmetic and the launch-order reading of (e); the sd placement sentence of (f); the ABSENT / POLICY-DEPENDENT caveat of T8; the pooled-sd arithmetic of R5 and the admitted-subset sd beside it.

## Hashes — sha256 of the LF-normalised bytes (CRLF → LF before hashing, the repository's `sha256_lf`)
The census data directory for this report is `readout_full` relative to the census root. In the preceding sections, `readout/` is shorthand for this supplied census data directory; rank-resolution files use the separately supplied rank-resolution directory.

Readout files carry `generated: 2026-09-13T03:35:47+00:00`; every result hash equals `manifests_read[stem].result_sha256_lf` (asserted); the twelve `mpa0__` and the endmember hashes equal `docs/93:228-240` (asserted); `o2_records.json` equals `docs/94:131` (asserted when supplied); `MANIFESTS.sha256` equals the `docs/91:92` pin (asserted). Paths are relative to `results/site_census_2026-09-06/` for census files and to the rank-resolution directory for the `rank_resolution` files.

```
5ba521d6162f901645cccbcad5cc97bac289a0eb309a3d70b4463a56e9ddf950  results/mpa0__Ni31Cr29Cu5Mn35_result.json
dd596f1b98207a4b9a2a6354514adcbdd07c8c0cbcf395d26f21bc4fcb2ea29a  results/mpa0__Fe25Co25Ni25Cr25_result.json
49b4fe562b59a1bb36dffb8b2f8fd8d21b341679a165acf175bd1883a76f9a96  results/mpa0__Cu26Ni9Cr31Co33_result.json
88e26bbc62b4d9c227218f38b5c8607f6d550b0ae7eda6027aa76a883baab8ea  results/mpa0__Ni34Fe6Cu29Co31_result.json
f042c705a6b17e66cb5b2263edf7c1719c4891ec5870bfdb8b25b639ea351cbe  results/mpa0__Cu8Cr23Mn35Co34_result.json
41ba0bea40295bad7af13ccbc9d4379e93c1eadf7961dd90e409f872b323ebb9  results/mpa0__Cu22Fe30Co32Mn15_result.json
3783fafef46ecdd629f6bfa0236e0e3c9d70dbba4decf1e821830331ac635480  results/mpa0__Cr33Co5Ni29Cu33_result.json
b5fd4f58771f0c4fc549adcdf3eb6017de0ec90125ba352b2131662b5a6b58ea  results/mpa0__Mn31Ni31Co33Cu6_result.json
fc3d38f9d7c59cf43629b305369a71cfc727cd9c1edc07a9a587863d53ebf408  results/mpa0__Fe31Cu25Cr13Ni31_result.json
3438a5c466cec06aa70d7f0b7402e75f2ef919b3d246bd8ce50cdd34a3822a64  results/mpa0__Mn34Cu7Fe33Cr27_result.json
cc48b8180010c2c331f283da15cbddfa8d08c2bdbf9dd3545ee72930ed4c8a66  results/mpa0__Co5Cu33Ni28Mn34_result.json
e1fa19ae8ff8b89e520cd853469715cd19f7f12a9a43af78bf4b8ead0fe9aaaa  results/mpa0__Ni34Fe29Mn30Co7_result.json
8ee988de1ba3a6bd9d997ee2f84ad386d4875709b79eb98faa1b02d856cf3516  results/endmember_2x2__mpa0_result.json
21328a1c4e898f2695644cc3a6741c8db63135511f3af7f8639e2bd373d0c3da  results/omat0__Ni31Cr29Cu5Mn35_result.json
43c85f53532f9a8e8dfa8e1e896d94f9afcf0b7cf4b14399af6c93c018ee6351  results/omat0__Fe25Co25Ni25Cr25_result.json
3eacc7dfba9ac3b33fc2770d27d1bc6c33cb6103c66f371cbb4c8f651884f0a5  results/omat0__Cu26Ni9Cr31Co33_result.json
2bfaa29b6dfdfe213ede8f20b6222689be8d7668026b982b31f934aff13f0832  results/omat0__Ni34Fe6Cu29Co31_result.json
b4f6183b77d42672cc113adb668afa2cf314e409c53d58bf46f0828dcfa8f5f9  results/omat0__Cu8Cr23Mn35Co34_result.json
f581d27a86cdaf54c2c5c6d66950180e3325113c11486d4beaa76e88f5267d41  results/omat0__Cu22Fe30Co32Mn15_result.json
ab7f4aca43da801d85a115750b7fda23a1733b0c504ef2de9f0a8e9a1e7667ae  results/mp0__Ni31Cr29Cu5Mn35_result.json
e55731c1e0c436e0c2fdaa496c473deeb2e20779dcb32d270d64589f78e32989  results/mp0__Fe25Co25Ni25Cr25_result.json
34e50d3533df1294292b22b82bec721c4970ec2537f13ec48c57e6aa498af5f3  results/mp0__Cu26Ni9Cr31Co33_result.json
f51fdc198fcd4d43efa0215ab1c5d78937863758487f2d44c94afdb1cb2728dd  results/mp0__Ni34Fe6Cu29Co31_result.json
0ec1f245f8fdb23c56f7dd1af088596c00caa544d5bb88f45fba9495dfeb8470  results/mp0__Cu8Cr23Mn35Co34_result.json
03d857b662d774b9214d960abd1f6e8701eeae5008d89b4f48d318eed9c16afd  results/mp0__Cu22Fe30Co32Mn15_result.json
4354d2528e931797b11553ec8149e5491eb27ef6e2f300a3574ab970ef0d9412  results/matpes__Ni31Cr29Cu5Mn35_result.json
1e8d148fd9d03dc89af628b93c739a52ea62068a6869cacbb07417c23aec3211  results/matpes__Fe25Co25Ni25Cr25_result.json
3354ee3c8e53bcf6b283da237ab44c98a117a5cb0d384d91be6e86d137f59487  results/matpes__Cu26Ni9Cr31Co33_result.json
f75930c3b5642f7794a0d04a33e1cf1d34b2cfc7fd39378901e5abf0054b61e0  results/matpes__Ni34Fe6Cu29Co31_result.json
0f5b644edba1d2d6ea679b981cbd98262bbf14e082b80962546202fe3d27fae9  results/matpes__Cu8Cr23Mn35Co34_result.json
8d06d8dd4650a227c695c973907e241fcac7aac266d339140e66fb09a6c1b36c  results/matpes__Cu22Fe30Co32Mn15_result.json
44669e88d94108778a7127ba095981c251c55cd9450a13b0c1b6168fe5389583  results/omat0__Cr33Co5Ni29Cu33_result.json
6b0985087bc80e2225ab2aad194471655d34656e30de9eaf4ed5edb6aa158ddd  results/omat0__Mn31Ni31Co33Cu6_result.json
8ce48608ebfa29276d2a1b28dcf425c81c7d7bbce0063d9b0c23b0fdfa1d2ea0  results/omat0__Fe31Cu25Cr13Ni31_result.json
243549f7e9c4555ea1efaa1d4af9d1e474ca3a80a1bcc6ed75eb9cbf737a68c9  results/omat0__Mn34Cu7Fe33Cr27_result.json
588729577ea08b82ba618fda555f688c3ef08289619a4ee9ac2683ff62b412f5  results/omat0__Co5Cu33Ni28Mn34_result.json
64ea9f7347689765023fac848af3696be466d429149c4e52032a89c200f09002  results/omat0__Ni34Fe29Mn30Co7_result.json
15883965e707d1e9b53f739da5d8f373a3dea7418fc10860386daebca75d2849  results/mp0__Cr33Co5Ni29Cu33_result.json
39d9a54a8823ba086d6967a81ecbfd19c8144e50b01640cc6eaa76d32b3735f8  results/mp0__Mn31Ni31Co33Cu6_result.json
5c5d5d052b27a822ebbaf56ab46fd2a94069ed0c91aa44cffafd5a67612281a8  results/mp0__Fe31Cu25Cr13Ni31_result.json
86d2b82cbedbbd48c6e7873e832b71b5b5d6f3c3c0b38350c5e3dd0c5c5a0947  results/mp0__Mn34Cu7Fe33Cr27_result.json
cc1dbdfec32b7105b6d33c4066e25b8f7e97fbbe61ed74df68eac9ae8d3c07d1  results/mp0__Co5Cu33Ni28Mn34_result.json
51df07bd0be4e962a4021c0b2934b781188901038b3eaa086ea31c0bfeedd108  results/mp0__Ni34Fe29Mn30Co7_result.json
60a8ac4c5e7438aceb643fee8b0df797182f4107f4e5295313b0a74874c44828  results/matpes__Cr33Co5Ni29Cu33_result.json
08f11b3f59bcd8b5815b09bb61b2569b14ecba7f2a2b6cf1325122cfd2230d7b  results/matpes__Mn31Ni31Co33Cu6_result.json
44cd1479b4064fe45b729f5f2eb03ca015f9532d6a719191362e99225ee8f2c1  results/matpes__Fe31Cu25Cr13Ni31_result.json
372e2470aa42a79b6e9585a756044289fd5f5935c96b8c88d167fd1599e73d82  results/matpes__Mn34Cu7Fe33Cr27_result.json
f49e927b4c8f58c1638f877045f53c8a24c42c7a6b59d78de9a0e088efa22ea6  results/matpes__Co5Cu33Ni28Mn34_result.json
9e4b05ad0ae8a78b85d100a4f81815627708567755ccbb93c1b955c310afeeaa  results/matpes__Ni34Fe29Mn30Co7_result.json
e9d87c6807d045f8ebe025c2813028f3d4199d6d172da33e0eb54514db5a88e1  results/mpa0_ext__Ni31Cr29Cu5Mn35__s03-05_result.json
457f2874e501b076347157694e6aadf51feac76aa832f664906aa5f90b10ff9c  results/mpa0_ext__Ni31Cr29Cu5Mn35__s06-08_result.json
dd60e5fe44a011bb28a54827a475ae07939f5cffa6c739e6a278fd858f6cf981  results/mpa0_ext__Ni31Cr29Cu5Mn35__s09-11_result.json
1a164c8027876fd81d5fdd247a82d010f20724d013a34fedb842d94625ec66b5  results/mpa0_ext__Ni31Cr29Cu5Mn35__s12-14_result.json
73a2ed71e9412d5b0d712f4b562edab594d350d515232c01cd52094d59cf26e5  results/mpa0_ext__Ni31Cr29Cu5Mn35__s15-17_result.json
04e09511f7499081a64a89068e9bc10c4c18f74fd61de54251a14b62d2236f12  results/mpa0_ext__Ni31Cr29Cu5Mn35__s18-20_result.json
142ad00ee341e4438438c3aca04887704338f90ce65c23314f882e8f0df6a89c  results/mpa0_ext__Ni31Cr29Cu5Mn35__s21-23_result.json
216aaa70f670a5a8e12fb2d6a9a26afe6c654d162ff15633e0384d54f6cfb216  results/mpa0_ext__Ni31Cr29Cu5Mn35__s24-26_result.json
29e83420c42cbd0a611ad2ce638503518356142acf4069c6897ed8daaeea011e  results/mpa0_ext__Ni31Cr29Cu5Mn35__s27-29_result.json
1be294505bf35e43253ddcc4ac4131ac3304e59c320f9c7cdc36562fed7c5e24  results/mpa0_ext__Fe25Co25Ni25Cr25__s03-05_result.json
465382791e1331fa972ec3c9b6e1f99e2375fb7467015162816d239cc4fe53a1  results/mpa0_ext__Fe25Co25Ni25Cr25__s06-08_result.json
c9e5926ec0ed83fa0db406cbaac09c4812d0e3c5e16b2fedefe52f2552558a95  results/mpa0_ext__Fe25Co25Ni25Cr25__s09-11_result.json
b66975fb33920922d1a8c06dd68c11b191f874fe1107a81c356c53cf23ac5db5  results/mpa0_ext__Fe25Co25Ni25Cr25__s12-14_result.json
05efbb453004951e8f5700d7bc4dd952dedd220c73507997cc7d4f3282aa11ee  results/mpa0_ext__Fe25Co25Ni25Cr25__s15-17_result.json
32bc9c2c8a8190fcee096f4e0d3143d9b12a0a1e405f944c240a4d5972f0f867  results/mpa0_ext__Fe25Co25Ni25Cr25__s18-20_result.json
031eee199f39054c25674f13c58d75a70f3313576c1831b7f39b95494c5ae5a4  results/mpa0_ext__Fe25Co25Ni25Cr25__s21-23_result.json
0b2a685c5f173df30069d936cc632801df9bb07ced317dfefba6054cce7bb7f4  results/mpa0_ext__Fe25Co25Ni25Cr25__s24-26_result.json
ce310a53bd39c39579599b1c090f23fbb69746ad74a6d3124d7131aa99958782  results/mpa0_ext__Fe25Co25Ni25Cr25__s27-29_result.json
7741ab315250f7e63650eea6b69416212a81d6f21f795057bd652a3e30764244  results/mpa0_ext__Cu26Ni9Cr31Co33__s03-05_result.json
ca47b08db2aeef04a8546adeb1c9f9fcff426d30b0e3302729a8d145c5ba7211  results/mpa0_ext__Cu26Ni9Cr31Co33__s06-08_result.json
4150e5adb8df48c2ff029b6097fe24b2cff834aa18d92ca8bdf705833451b76f  results/mpa0_ext__Cu26Ni9Cr31Co33__s09-11_result.json
09979b743f86b60a09b104cfe74d1f0a6819d79fad1b91b9d468008e46137a0c  results/mpa0_ext__Cu26Ni9Cr31Co33__s12-14_result.json
e44bcae3e525015a91cff521ad971458944ec265ff81b94f7cf51267c2ce3295  results/mpa0_ext__Cu26Ni9Cr31Co33__s15-17_result.json
2e9d12c4def8a70331be625d5cc4f8e2003d3c48f0339b010d2ea822f57beb3c  results/mpa0_ext__Cu26Ni9Cr31Co33__s18-20_result.json
a4d0dbd877e873594ace48ee4e7104d305e696d823f8fb1c62ed0f0a7e2e94eb  results/mpa0_ext__Cu26Ni9Cr31Co33__s21-23_result.json
90fe8316e90ea310bc3e207ae8f303278b5bab3c265c775515b96bb76cd3c23e  results/mpa0_ext__Cu26Ni9Cr31Co33__s24-26_result.json
4686b5520b860a4cd5e19a92d6961b691d52c8e2e8cd758d82b26c4a8de5eb86  results/mpa0_ext__Cu26Ni9Cr31Co33__s27-29_result.json
df655b8db4c990d967c1a589b5b7c7c9f8e223ad749e6070ec7d0f9666c819a2  results/mpa0_ext__Ni34Fe6Cu29Co31__s03-05_result.json
55caee614a1c8db097253a0d60d08fe8fb2bcdaf5be5af138a05e1dde8c8532d  results/mpa0_ext__Ni34Fe6Cu29Co31__s06-08_result.json
63e25e142e4eab292b71fa1396ebd503f24ec90031009f6ab9c83bc12359d456  results/mpa0_ext__Ni34Fe6Cu29Co31__s09-11_result.json
c4ea881626e562fcd39760c703c65483e88a9c5df2ba855dad336c92676b0233  results/mpa0_ext__Ni34Fe6Cu29Co31__s12-14_result.json
5a032a680715c686bfaca380ed7547caa159707fe6620826c697fc68f19e9f37  results/mpa0_ext__Ni34Fe6Cu29Co31__s15-17_result.json
dcbb09e318aa4aa9a466234bb6c27448533680a1ae2b2375afec4e45d43ebce7  results/mpa0_ext__Ni34Fe6Cu29Co31__s18-20_result.json
697360b4d63d8eb179f70701411af0e1e0d1bdb4ed89badaba38b40a31ce3cfc  results/mpa0_ext__Ni34Fe6Cu29Co31__s21-23_result.json
54787343c3d13dde8cac8ee5505d0c64d9feae0f24d8145aadc40a41570e289e  results/mpa0_ext__Ni34Fe6Cu29Co31__s24-26_result.json
33a220cb02069b247b89436fec8b997275062c2a5a6e5bddfd3d9f82b90ab04b  results/mpa0_ext__Ni34Fe6Cu29Co31__s27-29_result.json
bcbd13e2e3b2c345e3a045cb2e0db1485058fc04de71ce3c73019df21a46b4b2  results/mpa0_ext__Cu8Cr23Mn35Co34__s03-05_result.json
2be03372da0d1e89a7fe1e94d9a76b6ce513e3e6f7ab3f214298ef9528c42755  results/mpa0_ext__Cu8Cr23Mn35Co34__s06-08_result.json
a63c52bcd081c7b307a1309b1195ea6cac7b08574cf4d7f6b839c6a05634eda6  results/mpa0_ext__Cu8Cr23Mn35Co34__s09-11_result.json
4324d96c564954d7f9efd5221a98967d91110de7212c63ba04524888daafcc59  results/mpa0_ext__Cu8Cr23Mn35Co34__s12-14_result.json
282695fa22839b5ea8478789ad6ececcad3bfc7db3745bdd40ab075c5b72bc0d  results/mpa0_ext__Cu8Cr23Mn35Co34__s15-17_result.json
412b41700a894a76d17686de2ecdeb24180bf0d0a48306d4e5c75322b6d88b7a  results/mpa0_ext__Cu8Cr23Mn35Co34__s18-20_result.json
280e1e807492f7904fbae0054c2c61b4b909874c2e74926f0acb040bdf86b881  results/mpa0_ext__Cu8Cr23Mn35Co34__s21-23_result.json
0c7bacfb170dc1f95e0bb34fdf5db6aebe70b45cebc7a8452211ad8caa106990  results/mpa0_ext__Cu8Cr23Mn35Co34__s24-26_result.json
a1aec134efe397cd7400a5b513b4b28e31da611c128f39b8ebc8165e39d41f03  results/mpa0_ext__Cu8Cr23Mn35Co34__s27-29_result.json
c6a205ea66eccda70b524b3ef0f5795f133660adfd3e65c2b5ae49cbfb661a10  results/mpa0_ext__Cu22Fe30Co32Mn15__s03-05_result.json
996f6c39b7cecea60061c63503170ecfb257886a967d49c52f0541abfa615c55  results/mpa0_ext__Cu22Fe30Co32Mn15__s06-08_result.json
362f293985808e1b331a609b7e5e36021c418d5345decf79afecc48b9a3b95fe  results/mpa0_ext__Cu22Fe30Co32Mn15__s09-11_result.json
042fecd110c29e624264c8d40932bb96f47e290ffd210e07a077e2f3320a7cfa  results/mpa0_ext__Cu22Fe30Co32Mn15__s12-14_result.json
ab1f9d66438edd03607fe0fccb73b3c2de581e130586a9d5a6d7b3e68f382a4b  results/mpa0_ext__Cu22Fe30Co32Mn15__s15-17_result.json
3850510620f6eeff8903e6a3ab4e5db30fc417a397c8c3662766672c618fec09  results/mpa0_ext__Cu22Fe30Co32Mn15__s18-20_result.json
b10e074d2ad849c2562d634d6954e8617553de5cca3cd1ba9dea421e0a0c795c  results/mpa0_ext__Cu22Fe30Co32Mn15__s21-23_result.json
ed57f9f3c2462f3c497e4bd1aea76b19cba5ca53e646cb645850edec03156a56  results/mpa0_ext__Cu22Fe30Co32Mn15__s24-26_result.json
3a38fd226257ac9bee410e9a4ffc705a2bbeeaef650ab8fd95a25e377838eebe  results/mpa0_ext__Cu22Fe30Co32Mn15__s27-29_result.json
cae673682a7ee204fd128de08bd67657f4222e8f97146ef49fdbfb5a5d64e073  readout_full/per_site.csv
586c41a1ea75d84b5fa3ddb7541c0b411832394d3783af0367ea03f03d540475  readout_full/per_site.json
3be3601ce6f859ecc9b0aa1e73102039f5c493924964cc22a27554a7627ef325  readout_full/reproduction.json
f444beffe4319d89248170b80f134254355d029f9a81ccd1856c7f823a6492df  readout_full/ranking.json
b5351086d4ca1103cda3d64fb5683d2aed335eaeba510175c29f08889b2377c8  readout_full/distribution.json
20721f24a1c37d87e6dd4c1bae545626c9dbcb2c2dc03683b9ed06ec74a6cb60  o2_fragment/o2_records.json
3339a5326015f3233537e078a69109cbd1ea9249d67f689a1a53028f14469788  MANIFESTS.sha256
409a6d582ef442cbd69d8ebaf3f2881b99c155d90b374ba637bac5bbdf83edaf  rank_resolution.json
a6b7b6652af29c5969d433e3947b8c8d91dc8194c024cf517dc430e6d8d8070b  rank_resolution_no-desorbed.json
338da000c7fdfe5513b926850eca2386765d29d6d4e7023f300c1c082a07cfd2  rank_resolution_intact.json
f840674bdbf56456dcb5432ef77cf1483a5d1affea8a956cc4e558f31f1579e8  rank_resolution_adsorbate-intact.json
31fb63eba1d3ed09c5793b4dc632e543c5036443625de3103dadccdc2f9c7149  rank_resolution_two-pathway.json
e9163eba52c0b268a9a4b28d1bf299208595e4c2067da310e3cfbcf716351ad0  rank_resolution_compare.json
```

Implementation hashes the rank-resolution readouts record (`implementation_sha256_lf`, identical across the policy files, asserted): `src/hea_oer/rank_resolution.py` 2764ac09553aa36078663f942ad377440b9072bafda22f3512d7d3fdb0391871; `src/scripts/rank_resolution_readout.py` e00e62c7f5893ffd4975016de9e8fc87d06a0b2a2e4d87644c014e9f20e599b1.

The ten `manifest.implementation_sha256_lf` keys (identical across every landed result, asserted): `src/scripts/screen_diagnostic.py` 7c8b163f7510ec7f3dd8d8bf227693c5dddc03b80bb1518c29657f84fdbe7d7f; `src/hea_oer/adsorption.py` 246150440bf2d4bd316bd185557191cadf21c517715ebf6e7002da5749e2fc9f; `src/hea_oer/relax.py` e2f0e5417a925347fe2cbdf1f96a9b846d6378a091e63a07f2163874cc0c5369; `src/hea_oer/composition.py` 1357f5fbf25d19b7d6d7e56549bfc43535fb4dce49b483825356d8d8ff2deee7; `src/hea_oer/surfaces_rutile.py` 2ba9aaede3e8debf9f51db11b7f43005052f543c21172dcdce4bcbc5342d8c44; `src/hea_oer/surfaces.py` e4719c6f19db2b0ed2f3ed4420a516407b5fc577ea0f7e1d27c9d4cb62533eb9; `src/hea_oer/referencing.py` 2873802d0ddf14bfd3640f8f31a93c3b8a5ff5205a31fd519cef6a8e9cc1e6c7; `src/hea_oer/descriptors.py` 893e8058bf89500cc6d93ad8d7ab06f93f4230ec65dbd5ed86a047c0120425a9; `src/hea_oer/data.py` 65129cb3ebc7bdcac6127644db0f743fe7404362de8ccb9e9b4cf413cd496e08; `src/hea_oer/site_evidence.py` cfe63c638af77b1e7fccc0494e8a694dec55ee2d84efacc2134de7fda7a48026.

On-disk scorer hashes against the docs/91 pins (the pin exists to make post-hoc change visible, `docs/91:204`; no edit is made): `src/hea_oer/site_integrity.py` on disk 352ee8e939b1157000d27478b6e02b943ff9cd8e3dba460051ca758b2ef6fb85 against the `docs/91:207` pin 352ee8e939b1157000d27478b6e02b943ff9cd8e3dba460051ca758b2ef6fb85: equal; `src/scripts/site_census_readout.py` on disk 1d405dd868ec9c1cfd70b57ef8c27a82be5447cf34421c540cd0f96c47fff188 against the `docs/91:212` pin 1d405dd868ec9c1cfd70b57ef8c27a82be5447cf34421c540cd0f96c47fff188: equal.

Paths are relative to `results/site_census_2026-09-06/`, which is gitignored (`.gitignore:14`); the manifests and `MANIFESTS.sha256` are in the boundary commit (`docs/91:5-14`), the results and readout are not (`docs/93:248`).
