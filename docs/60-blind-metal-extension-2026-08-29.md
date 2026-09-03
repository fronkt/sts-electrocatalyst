# 60 — The blind-metal extension: Mn, Fe, Ti, and the two predictions off their rows — 2026-08-29

**Provenance:** AI-drafted disclosed infrastructure (analysis narrative over banked,
adversarially verified artifacts; every number below is quoted from a committed JSON or
raw output). Evidence: commits `7c84ec9` → `bb17152` plus this change set; banked
artifact `docs/figs/a0main_readout.json`; verification records
`docs/figs/a0_verification_findings_2026-08-29.txt` (wave 4) and the wave-5 audit
recorded in docs/45 "A0 wave 5". Registration: docs/43 A5.1(b), A6.3–A6.6, A7.2, A7.3,
A7.5, A7.7 (Zenodo 10.5281/zenodo.21963144, restricted deposit). Dated correction of
record for the roster: docs/59 (**still DRAFT — awaiting the entrant's countersignature**).

**This document supersedes docs/58 §7–§8 where they disagree.** docs/58 is the dated
record of A0 as it stood on 2026-08-28, when Mn/Fe/Ti were unbuilt; it is left intact.

---

**One-paragraph summary.** docs/58 closed A0 over Cr, Ru and Ir and left Mn, Fe and Ti
unbuilt, with A7.2 CONFIRMED and its sibling A7.3 filed as deferred future work. That
asymmetry was the problem: both predictions are scored off the *same* rows, and
reporting only the one that passed is the exact selectivity pre-registration exists to
prevent. Tranches 2/2b/3/2c built the three blind metals. A7.2 is now final at **5 of 6**
(CONFIRMED, threshold ≥3) and **A7.3 is NOT MET at 3 of 6 against a registered ≥4 — a
registered prediction that FAILS.** Neither number should be read bare. A7.2's threshold
is carried by exactly three robust members with zero margin; A7.3's over/under split is
*perfectly* confounded with the nspin=2 / nspin=1 partition and sits 15.5 meV from
flipping. Along the way TiO₂ was found to bind *OOH after two failed relaxations, and
A5.1(b) was found to have been scored on the wrong quantity for a week.

## 1. What was owed

A6.3 registers the grid over "Ru and Ir as well as the 3d metals"; A7.2 and A7.3 name
Mn, Fe and Ti as blind metals. Tranche 1 ran Cr/Ru/Ir only, on an allocation the entrant
chose 2026-08-27 with no dated amendment. docs/59 is the dated correction of record and
is **not yet countersigned**. The entrant directed the extension on 2026-08-28 ("Do them
over Mn/Fe/Ti then").

## 2. The four tranches

| Tranche | Builder (committed pre-launch) | What it bought |
|---|---|---|
| 2 | `build_a0main_w2.py` | Mn + Fe A0 grids |
| 2b | `build_a0main_w2b.py` | Fe *OOH starting-guess pilot (mag 0.1 vs 0.5; the 0.5 cold start is a measured +276.60 meV trap) |
| 3 | `build_a0main_w3.py` / `_w3b.py` | Ti slab + 3 adsorbates built and relaxed from scratch, then the *OOH ladder |
| 2c | `build_a0main_w2c.py` | the A6.5(2) escalation round that produced the Fe U = 4.5 point and the Ti *OOH geometry |

## 3. Fe: the branch that does not exist at U = 4.5

The s0_O moment ladder runs 18.91 / 21.36 / 22.90 up to u300, then 21.98 from u530 on;
U = 4.5 is the crossing. Rung (i) — restart from the converged neighbouring-U density —
failed there. Rung (ii) halved the mixing beta and ran from **both** legal converged
parents, a two-armed test fixed before either job was submitted. Exactly one converged:
`r2b`, seeded from the 22.90 branch, in **18 iterations at totmag 23.44**. `r2`, seeded
from 21.98, failed — the **third** failure on that branch.

The reading is not "two basins, take the lower". It is that **the 21.98 solution does not
exist at U = 4.5**: the branch terminates between 4.5 and 5.3, and the three failures
were the ladder walking off the end of it. E(U) is smooth and monotone across the branch
change (dE/dU 0.329 → 0.190, no kink). **Fe scores 8/8 with no gaps.**

## 4. Ti: the adsorbate that started too high

The TiO₂ *OOH relaxation failed twice. The defensible move was the registered terminus —
rung (iii), NOT_CONVERGED, plot a gap. The trajectory said otherwise: *O and *OH walked
**down** into bonds (1.735 / 1.829 Å) over 36 / 56 ionic steps, while *OOH walked **up**
(3.167 → 3.263 → 3.325 → 3.414 Å) into a region where it is an odd-electron radical
(157 electrons) that nspin=1 cannot describe. The SCF limit cycle was the symptom; the
**starting height** was the cause.

This is a **recurrence, not a new defect.** `hea_oer/surfaces_rutile.py` documents the
same failure in the 2026-07 campaign — *OOH left desorbed on Mn, Fe *and* Ni, "four
chemically-wrong structures that passed every numerical QC check" — and ships
`adsorbate_starts` as the remedy with registered pull-in distances `PULL_TO = (1.70,
2.10)`. The MACE screening path uses it. The DFT deck path (`qe_slab.py`) calls
single-start `add_oer_adsorbate_at` and **never inherited it**.

`s0_OOH_r3` re-anchored the adsorbate to the mean of Ti's own two converged Ti–O bond
lengths, **1.781905 Å — inside that registered `PULL_TO` window**, so the anchor is the
campaign's own remedy re-derived rather than a free parameter. It converged in **52 ionic
steps with zero SCF failures**, force 0.003092 Ry/bohr, while the plain continuation `r2`
failed again after 19 steps. Tranche 2c's exactly-one-converged selection rule was fixed
before either ran.

**TiO₂ binds *OOH**, at d(O,Ti) = **2.041 Å**, O–O 1.371 Å, O–H 0.986 Å — an O–O between
the HO₂ radical's 1.33 and H₂O₂'s 1.45, i.e. a genuine hydroperoxo. Two limits travel
with that: the adsorbate takes only **+0.035 e** of Löwdin charge from the surface against
*O's +0.347 and *OH's +0.230, so the binding is real but **weak**; and the residual open
question is the spin convention, not the geometry. Had this stopped at rung (iii) the
campaign would have banked a gap where a bound state exists, with "TiO₂ doesn't bind *OOH"
sitting in the failed walk for anyone to read.

## 5. A7.2 — CONFIRMED at 5 of 6, on exactly three robust legs

Cr, Fe, Ir, Mn and Ru all flip their potential-limiting step inside the grid; Ti is flat
across U ∈ [0, 9]. Registered threshold ≥3, so **CONFIRMED**, and the census is now closed
(no pending data, no unrun metals).

The strength is thinner than the count. Membership rests on a single row for **Fe** (pls 1
only at U = 9.0, margin 81.7 meV) and **Ru** (pls 2 only at U = 9.0, margin 44.3 meV) —
both inside measured error classes, and Ru's inside the still-open NM-vs-AFM class
(33–64 meV) whose re-run is owed, against an nspin=1 column. Strip those two and the
robust members are Cr, Ir and Mn: **exactly 3, the registered threshold, with zero
margin.** The monotonicity defence used before this landing ("more metals can only add
flips") no longer applies, because there are no more metals.

## 6. A7.3 — NOT MET at 3 of 6: a registered prediction fails

Registered: span(c_M)/2 > 0.10 V on ≥4 of the 6 metals with a converged *OOH geometry,
c_M = ΔG_OOH − ΔG_OH at the **fixed** endpoints U = 0 and U = U_max (never
max-minus-min). FALSIFIED only at ≤1 of 6.

| Metal | nspin | c_M(0) | c_M(9) | span/2 | vs 0.10 V | distance to floor |
|---|---|---|---|---|---|---|
| Mn | 2 | 3.6172 | 2.3558 | **0.6307** | EXCEEDS | −1061 meV |
| Fe | 2 | 3.5181 | 2.2977 | **0.6102** | EXCEEDS | −1020 meV |
| Cr | 2 | 3.4437 | 2.7567 | **0.3435** | EXCEEDS | −487 meV |
| Ru | 1 | 3.1801 | 2.9956 | 0.0922 | below | **+15.5 meV** |
| Ir | 1 | 3.6523 | 3.5249 | 0.0637 | below | +72.6 meV |
| Ti | 1 | 3.4569 | 3.3694 | 0.0438 | below | +112.5 meV |

**3 of 6 → NOT MET.** Not falsified (that needs ≤1). Five conditionality facts are banked
with it in `a7_3.conditionality`, and the status must not be read without them:

1. **The split is perfectly confounded with the spin treatment.** The three over the floor
   are *exactly* the three nspin=2 decks; the three under are *exactly* the three nspin=1
   decks. This readout cannot separate "U moves the physical limit" from "nspin=2 columns
   respond to U more than nspin=1 columns."
2. **One metal from flipping.** Ru is short by 15.5 meV of |Δc_M| — smaller than the top of
   *every* measured error class, and 2–4× smaller than the NM-vs-AFM class whose re-run
   (S0(h), RuO₂ AFM anchors) is owed and acts on **exactly the nearest metal**. NOT MET is
   not settled.
3. **Carrier endpoint quality.** Fe and Mn set c_M(9) on pls-1 rows where the registered
   closed-form identity does not run and the ΔG ladder has inverted (ΔG₃ = −0.199 and
   −0.125 eV). Two of the three carriers are not clean rows.
4. **Undefined band.** The registration names CONFIRMED (≥4) and FALSIFIED (≤1) and a
   consequence for FALSIFIED only. 3 of 6 is in neither. "NOT MET" is a token the scorer
   invents; it is **not** in A7.7's vocabulary (WITHDRAWN-UNSCORED / HELD / TRIGGERED) and
   nothing registered says what a middle outcome licenses. Reported, not mapped — the
   entrant decides the disposition.
5. **Licence-contingent rows.** Ti's seven 1×1 relaxations are new compute outside A6.6's
   footprint ("~160 fixed-geometry SCFs and **zero relaxations**"; it "does not license …
   any relaxation in any cell"). The licence is ungranted. **If withheld, the Ti rows are
   WITHDRAWN-UNSCORED, the denominator falls 6 → 5 and the status reverts to "NOT YET MET
   — UNDECIDED".** Two banked fields are provisional on a signature.
   **[ERRATUM 2026-09-03 — "the licence is ungranted" was true when written (2026-08-29)
   and is FALSE NOW. It was GRANTED under directive and completed by the entrant's own
   dated line `[§3c CONFIRMED 2026-08-31]` (docs/59 §5, verbatim: "i published the deposit,
   submit everything"), deposited at DOI 10.5281/zenodo.22213117. The withheld branch below
   is therefore counterfactual: A7.3's denominator STAYS 6 and the banked NOT MET 3/6 stands
   scored. The two fields are no longer provisional.]**

## 7. Why Ti came in lowest — and the story that turned out to be wrong

The tempting explanation is "TiO₂ is d⁰, so U has nothing to act on." **That is wrong**,
and the Löwdin data says so. Over U ∈ [0, 9] the mean substrate-metal d population moves
Ti **−0.295 e**, Ru +0.206 e, Ir +0.249 e — comparable in magnitude, **opposite in sign**.
Ti's Löwdin d ≈ 2.0 is back-donation from O 2p; U penalises that fractional occupation and
pushes density back onto oxygen. For genuinely partly-filled Ru (d⁴) and Ir (d⁵), U drives
the shell toward integer filling.

So U acts on Ti-3d perfectly well. What is small is the *difference*: Ti's response is a
substrate-internal Ti→O redistribution that is nearly identical in slab and adslab and
therefore largely **cancels** in the adsorption free energy. ΔG_OH moves 0.092 eV across
the whole window, against Cr's 1.052, Mn's 1.570 and Fe's 1.277. The weakly-bound *OOH
(+0.035 e transfer) points the same way: the species U would have to move barely shares
electrons with the substrate.

**Hedge that travels with this section:** Löwdin populations are basis-dependent and are
not observables. This is an internally consistent measured correlate, **not** a proof of
mechanism, and it is not a registered readout.

## 8. A5.1(b) was being scored on the wrong quantity

A5.1(b) (docs/43:958-964) admits a pairwise ordering only if all three legs hold: (1)
η_TD and G_max(η = 0.3 V) agree; (2) the **G_max gap** ≥ 0.20 eV; (3) the ordering is
stable across the U band. Leg 2's floor is a G_max gap. The readout had been applying that
0.20 eV number to **η margins** — the wrong quantity — and had never evaluated leg 1 at
all. Corrected here with the campaign's own `g_max` convention; zero new DFT.

| U | G_max(Ir) | G_max(Ru) | gap | leg 2 | leg 1 |
|---|---|---|---|---|---|
| 0.0 | 0.592 | 0.487 | 0.106 | fail | DISAGREE |
| 1.5 | 0.567 | 0.426 | 0.141 | fail | DISAGREE |
| 3.0 | 0.543 | 0.350 | 0.194 | fail | DISAGREE |
| 4.5 | 0.521 | 0.261 | 0.260 | pass | AGREE |
| 6.0 | 0.501 | 0.164 | 0.337 | pass | AGREE |
| 7.5 | 0.482 | 0.058 | 0.424 | pass | AGREE |
| 9.0 | 0.465 | 0.000 | 0.465 | pass | AGREE |

The shape is the **opposite** of what the η-margin reading implied. Under G_max, **Ru is
the better anchor at every measured U** (leg 3 stable). Under η_TD the ordering reverses.
The two metrics agree only at U ≥ 4.5 — *exactly* where η_TD reports the A6.3 inversion.
So the pair is **claimable at U ≥ 4.5 (Ru better) and not distinguishable at U ≤ 3.0,
production U = 0 included**, where the metrics disagree outright and the gap is 0.106 eV.

**Withdrawn:** docs/58's sentence that "the ordering was never *positively* resolved at
any measured U". It was an η-margin statement about a floor registered on G_max gaps. The
correct statement is narrower and sharper: unresolvable at production U, resolved in Ru's
favour at high U, and the registered prior η(Ir) < η(Ru) is **not recoverable at any U**
under the registered rule.

## 9. Verification record

Wave 4 (59 agents, pre-landing): 53 raised / 38 refuted / 15 survived + 9 sweep. Caught a
BLOCKER (pending repairs reported as convergence failures, so a row could bank "the
escalation ladder is exhausted" while repairs were still queued) and — from the
completeness critic — that **A7.3 had never been scored while A7.2 was reported
CONFIRMED**. Full record: `docs/figs/a0_verification_findings_2026-08-29.txt`.

Wave 5 (47 agents, this landing): 38 raised / 26 refuted / 7 survived + 7 critic. Five
verifier agents died on API safeguards; their findings were re-checked by hand rather than
counted as refuted. Traps 18–24 in docs/45. Everything in §5–§8 above is a wave-5 fix.

Controls that passed on the 8 new jobs:

- All 8 COMPLETED exit 0:0, converged, zero "convergence NOT achieved", Löwdin extracted.
- **Determinism control:** base and u000 are byte-identical decks except the prefix line,
  neither carrying a HUBBARD card, run on **different nodes** (a211 / a215) — agreeing to
  4.1e-7 Ry (5.6 µeV).
- **Geometry-splice control:** the base SCF reproduces the r3 relaxation's own final
  energy to 1.6e-7 Ry.
- **GATE 1:** now covers s0_OOH (the record was missing from `probe_manifest.json`; fixed
  by `src/dft/add_ti_ooh_manifest.py`) at +0.00 meV drift, and `probe_eta.py`
  independently returns η = 1.7407 V / pls 2, matching the A0 readout's Ti U = 0 row
  through a different script.
- **Independent re-derivation:** all seven Ti rows recomputed from raw `.out` files
  through a CHE ladder written from the documented convention rather than by calling the
  pipeline's functions — reproduces the scorer exactly.
- **Regression:** against the artifact banked at `bae6cd2`, Cr's 19 rows and Ru/Ir/Mn/Fe's
  8 each are **bit-identical** (max |Δ| = 0.000e+00).

## 10. What the report may and may not say

- **MAY:** A7.2 CONFIRMED at 5 of 6, *stating* that three robust members carry it with
  zero margin; A7.3 **NOT MET at 3 of 6 — a registered prediction that failed** — always
  with the spin confound and the 15.5 meV Ru distance; TiO₂ binds *OOH weakly at 2.041 Å;
  the Ir/Ru pair is claimable (Ru better) only at U ≥ 4.5 and not distinguishable at
  production U.
- **MAY NOT:** quote A7.3's status without `a7_3.conditionality`; claim the A7.3 split is
  a chemical result rather than one perfectly confounded with spin treatment; claim
  η(Ir) < η(Ru) at any U; call A7.3 "settled" while S0(h) is owed; present the Löwdin
  mechanism in §7 as a registered result or as proof; use any Ti row without the A6.6
  licence contingency; treat "NOT MET" as an A7.7 disposition.

## 11. Open items

**Frank's:** countersign + deposit docs/59 — including §3c, which asks him to license or
withhold the seven 1×1 Ti relaxations against A6.6, and whose outcome moves A7.3's
denominator; decide whether the Ti arm should run nspin=2 throughout; A7.5's Mn AFM arm
(currently UNMET — the Mn column is FM-initialised and may not be used as a
materials-facing absolute η); the disposition of a 3-of-6 outcome A7.7 has no token for;
RCAC ticket; the two dirty CI files.

**Still unscored (zero new DFT):** A5.1(a) valence classification — the Ti `.lowdin.txt`
extracts landed here and complete the coverage, and **no script in the repo reads a
`.lowdin.txt` at all**, while for Ru/Ir/Ti the nspin=1 decks make the moment-based tracker
structurally unavailable, so Löwdin is the only valence tracker those three can ever have;
A5.1(c) G_max maps (the `g_max` machinery now exists in the readout for A5.1(b) and
generalises); A5.1(d) intercept test — **its number is already banked** inside
`a7_3.per_metal`, since the scaling intercept *is* c_M; read across metals the cross-metal
mean intercept moves 3.478 → 2.883 eV and its spread nearly triples, against the
registered motivating prior that the intercept stays U-robust.

**Owed compute:** S0(h) RuO₂ AFM re-anchors — which act on exactly the metal nearest to
A7.3's floor, so this re-run can change a banked verdict.

> **UPDATED 2026-09-02 → docs/68.** "Owed compute: S0(h) RuO₂ AFM re-anchors … can change a
> banked verdict" — it ran and it cannot: the U = 9 AFM legs, like all 12 FM-seeded Ru rows
> at U = 9, do not converge (0 of 16), so the Ru cell equalises by selection to the nspin = 1
> row. §6's conditionality fact (1) (the nspin = 2 / nspin = 1 partition) is weakened by
> measurement: the spin-equalised sensitivity census keeps the same 3-over/3-under split
> (Cr, Mn, Fe over; Ru 0.0957 V, Ir 0.0591 V, Ti 0.0522 V under), all four non-Mn/Fe rows
> guard-3 flagged pending the entrant's adjudication. Fact (2) is closed as unpriceable at
> U = 9. The as-built 3-of-6 remains the headline (A11.5).
