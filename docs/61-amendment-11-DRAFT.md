# 61 — AMENDMENT 11 (DRAFT): spin-treatment equalisation on the three nspin = 1 metals, and whether the spin effect on c_M is U-dependent

**Status: DRAFT for the entrant.** AI-drafted disclosed infrastructure. Every threshold
below is marked **PROPOSED** and is the entrant's to re-author before deposit; the
measurements, the deck mechanics and the guards are not opinions and are cited to files.

**Provenance:** written 2026-08-29, **before any deck of this arm was built or
submitted**. docs/43 is DOI-deposited (10.5281/zenodo.21963144) and may not be edited in
place — docs/43:4-5, verbatim: *"Nothing in this document may be edited after that
deposit; corrections go in a dated addendum at the bottom with the reason."* This is that
addendum, in the standalone-draft form set by docs/47 (Amendment 8) and docs/50
(Amendment 9). Until deposited, its authority is its commit timestamp.

---

## A11.0 Why this is being written now, and what changed under it

Three measured facts, all banked at commit `fa46611` before this amendment existed:

1. **A7.3 (P-FLOOR-U) was scored and it FAILED** — NOT MET at 3 of 6 against a registered
   ≥4 (`docs/figs/a0main_readout.json`, `a7_3.status`).
2. **The over/under split is perfectly confounded with the spin convention.**
   `a7_3.conditionality.spin_confound.perfectly_confounded = true`. The three metals over
   the 0.10 V floor (Cr 0.3435, Mn 0.6307, Fe 0.6102) are *exactly* the three whose A0
   decks carry `nspin = 2`; the three under it (Ru 0.0922, Ir 0.0637, Ti 0.0438) are
   *exactly* the three that run nonmagnetic.
3. **Ru is 15.5 meV of |Δc_M| from crossing the floor**, inside the still-open NM-vs-AFM
   class (33–64 meV) measured by gate (h), whose re-run is owed and acts on Ru itself.

Leaving a registered prediction scored on a treatment perfectly confounded with its own
outcome is not defensible when the fix costs zero relaxations. This amendment registers
the fix **and**, more importantly, registers in advance which census stays the headline —
because the obvious failure mode here is rescuing a failed prediction by changing a
convention after reading the failure.

**The counter-argument, recorded because it is strong.** The campaign has a standing,
committed reason for the nspin = 1 convention on these three metals (RuO₂/IrO₂ are
nonmagnetic in the reference literature; TiO₂ is d⁰). This amendment does not overturn
that convention for production. It runs a **matched second treatment** so the confound can
be priced. Production stays nspin = 1 on Ru and Ir (§A11.9).

## A11.1 The reframe — why "de-confounding" is the wrong word

A7.3's registered quantity is **span(c_M)/2 at FIXED endpoints U = 0 and U = U_max**
(docs/43:1368-1369), with c_M = ΔG_OOH − ΔG_OH. Write Δc_M(U) for the change in c_M under
spin equalisation. Then

>  Δ[span/2] = −D_M / 2,  where **D_M = Δc_M(U_max) − Δc_M(0)**

**A U-independent spin offset cancels EXACTLY.** The arm cannot move A7.3 through the
*size* of the spin effect, only through its *U-dependence*. This is arithmetic, not
expectation, and it is registered here so that no result can later be presented as though
a large spin effect implied a large change in the score.

**What is already measured at one endpoint.** Eight `nspin = 2` SCFs exist and are banked
at `runs/probe/{Ru,Ir}_spin/<state>__spin0.5.out` (P11's FM leg, run 2026-08-07). Their
geometry blocks are byte-identical to the A0-main `u000` decks (ATOMIC_POSITIONS md5
match, all 8 pairs; `diff` returns only the prefix line). From them, at U = 0:

| metal | ΔE_slab | ΔE_*O | ΔE_*OH | ΔE_*OOH | **Δc_M(0)** |
|---|---|---|---|---|---|
| Ru | −71.94 | −88.02 | −73.68 | −66.54 | **+7.145 meV** |
| Ir | +0.59 | −173.71 | −0.50 | −9.20 | **−8.705 meV** |

(meV; ΔE = E(nspin=2) − E(nspin=1). E_slab and every gas reference cancel *identically* in
c_M — `referencing.py` `_REF_COEFFS`, so Δc_M = ΔE_*OOH − ΔE_*OH exactly.)

So individual state energies move by up to 174 meV while **c_M moves by under 9 meV**.
Ru crosses the floor if and only if Δc_M(9.0) ≤ **−8.35 meV** — i.e. only if the spin
correction to c_M *swings by ≥15.5 meV across the U band*. That is the whole experiment,
and it is genuinely open.

**Honest expectation, registered before the data:** this arm most likely **prices** the
confound rather than overturning it.

## A11.2 The design

Fixed-geometry single-point SCFs on the already-relaxed, already-banked geometries — no
relaxation of any kind (§A11.10). The only keys added to any deck are `nspin = 2` and one
`starting_magnetization(i)` line per species.

- **The species index is read from each deck's own ATOMIC_SPECIES block.** Measured:
  `qe_slab.py` sorts species alphabetically with O last, so `slab` and `s0_O` are
  `ntyp = 2` `[M, O]` → **metal at index 1**, while `s0_OH` and `s0_OOH` are `ntyp = 3`
  `[H, M, O]` → **metal at index 2** for Ru/Ir/Ti. A per-metal constant is wrong and
  would seed **oxygen** on half of every ladder.
- **FM, metal-only**, O and H written explicitly `0.0`. FM is what Cr/Mn/Fe received; an
  AFM treatment here would replace one spin-treatment confound with another.
- Tree `runs/a0/spin/<M>/`, stems `<state>__<utok>__sp2m<NNN>`. **Never** written into
  `runs/a0/main/`, which the readout addresses literally.
- Xu anchor rungs (Ru u673, Ir u591) are **excluded by design** — they are already
  PROJECTOR-MISMATCHED — and that exclusion is registered here so the readout does not
  emit them as convergence gaps.

## A11.3 The registered predictions — two, not one

**P-FLOOR-U-SPIN (the count).** Same quantity, **inherited** 0.10 V floor and
**inherited** ≥4-of-6 count, computed on spin-equalised rows and reported as a *second*
census labelled `a7_3_spin`. Inheriting rather than inventing is deliberate: a new
threshold chosen now, after the failure, would be fitted by construction.

**P-SPIN-DELTA (the mechanism).** Quantity **D_M** per metal. **PROPOSED** threshold:
|D_M| ≥ 0.033 eV on ≥2 of 3 metals — the *bottom* of gate (h)'s measured 33–64 meV class,
so it is anchored to a prior measurement rather than invented. **PROPOSED** falsification:
all three show |D_M| < 0.005 eV. *Both numbers are the entrant's to re-author.*

## A11.4 Both outcomes, before the fact

| prediction | claim scope if HELD | claim scope if FALSIFIED / NOT MET |
|---|---|---|
| P-FLOOR-U-SPIN | The report may say the floor is cleared by ≥4 of 6 **under spin-equalised treatment**, always naming the treatment, and always beside the as-built census. It may **not** replace the as-built number (§A11.5). | The report may say A7.3's failure survives spin equalisation — which is a *stronger* statement than the as-built one, because it removes the confound the audit found. |
| P-SPIN-DELTA | The spin convention is worth ≥33 meV of U-dependent movement in c_M; every A0 span on an nspin = 1 metal is spin-treatment-conditional at that size, and the caveat quotes it. | The spin convention is worth <5 meV on c_M at both endpoints, so **the 3/3 split is not a spin artifact** and the confound — while real as a correlation — carries no measured consequence for A7.3. |

These are scope statements, not wording; the report's sentences are the entrant's.

## A11.5 Which census is the headline — decided before any deck runs

**This is the section that prevents the arm from being fitting.**

**PROPOSED, and recommended:** the as-built **3 of 6 remains the registered score of A7.3
and remains the headline**. The spin-equalised census is a registered **sensitivity** whose
only power is to select which caveat sentence is true. It cannot promote A7.3 to CONFIRMED.

The reasoning is recorded so it can be attacked. docs/60 §10 already licenses the report to
say *"A7.3 NOT MET at 3 of 6 — a registered prediction that failed."* Converting that into
a contested 4-of-6 by moving one metal across a 15.5 meV line — under a spin convention
chosen **after** reading the failure, on a margin the artifact itself banks as sitting
inside a measured 33–64 meV error class, in a 1×1 cell the 1A verdict did **not** adopt —
trades a highly credible sentence for a weak one. A failed pre-registered prediction,
reported as failed, is worth more than a rescued one.

*The entrant may instead elect the equalised census as primary. That election must be
dated and committed before any Stage 1 deck is submitted, not after.*

## A11.6 The starting-guess rule, registered before any deck runs

In the tranche-2b form (`build_a0main_w2b.py`, whose rule was registered in
`build_a0main_w2.py` **before** any pilot ran): a fixed acceptance criterion, mechanical
selection, no further guesses.

**PROPOSED seed set S = {0.10, 0.30, 0.50}** — fractional, so per-metal-atom moments are
1.6/4.8/8.0 μB on Ru, 1.5/4.5/7.5 on Ir, 1.2/3.6/6.0 on Ti.

- **0.50** is mandatory, not merely incumbent: it is the seed of the eight banked P11 SCFs,
  so keeping it makes the U = 0 rungs free and supplies the campaign's **only** cross-machine
  determinism control on a spin-polarised code path. It is also Mn's value on all four
  states and Fe's on three.
- **0.10** is the only seed this campaign has ever scored and selected (the Fe *OOH pilot
  winner, chosen mechanically under a pre-registered rule).
- **0.30** is that pilot's middle guess and the detector for a non-monotone seed→basin map.

**Why not one seed.** The Fe pilot *measured* the map to be non-monotone: 0.1/0.3/0.7 all
land the good branch within 0.004 meV while **0.5, sandwiched between two that work, traps
+276.57 meV up**. There is no "safe because small". A single-seed arm is a coin flip
dressed as a convention.

**Exactly 0.0 is separately fatal** and the repo says so in its own words (`qe_slab.py`):
`nspin=2` with every seed at zero is a fixed point of the SCF — it reproduces the nspin = 1
answer at twice the cost. Two decks deliberately exploit this as machinery controls
(§A11.7) and are the only whitelisted exemption.

**Selection (PROPOSED):** lowest converged total energy per (metal, state, U) across the
three seeds **and** the banked nspin = 1 energy, with a hard variational floor; ties within
1 meV to the smallest |seed|; both total and absolute magnetization reported per cell.

## A11.7 The three new guards

1. **Symmetry/k-set guard.** Adding `nspin = 2` can change the symmetry group pw.x keeps,
   which changes k-folding, which changes the energy for a reason that is **not** spin.
   Every equalised output's `Sym. Ops.` line and k-point count is compared with its
   as-built twin; a mismatch disqualifies the row from being differenced.
2. **Variational floor.** nspin = 2 is a strict superset of nspin = 1 on the same
   functional. Any converged candidate landing **above** its banked nspin = 1 counterpart
   is a *search failure*, rejected, not banked. **Not hypothetical:** Ir slab at seed 0.50
   converged +0.592 meV above its nspin = 1 energy at absmag 0.17 — measured, in the banked
   P11 data.
3. **Endpoint branch continuity.** A7.3's quantity differences two independently converged
   SCFs. If the winning candidates at U = 0 and U = U_max sit in different magnetic
   branches, the pair is flagged **BRANCH-CONDITIONAL** and may not be scored into a span.
   The campaign has measured branch changes worth 276.57 meV (Fe) and 47.77 meV (GATE-1).

**Machinery controls (Stage 0, 10 jobs), read before Stage 1 submits:** eight decks must
reproduce the banked P11 energies (Ru slab −1630.67301371, s0_O −1672.26143725, s0_OH
−1673.53455401, s0_OOH −1715.01193102; Ir slab −1589.74818250, s0_O −1631.35200572, s0_OH
−1632.64860176, s0_OOH −1674.09243750 Ry); two **null-seed** decks — deliberately one of
*each* ntyp class, Ti `slab` (ntyp 2, metal index 1) and Ti `s0_OOH` (ntyp 3, index 2) —
must reproduce the banked nspin = 1 Ti energies with totmag ≈ 0. An all-ntyp-3 control set
would be **structurally blind** to the index rule on exactly the decks where it differs.

## A11.8 Corrections of record entering with this amendment

1. **The odd-electron caveat is not Ti-specific.** pw.x reports 175/181 electrons for Ru
   *OH/*OOH and 169/175 for Ir, alongside Ti's 151/157. **All three** nspin = 1 metals run
   both odd-electron adsorbate states without the ability to spin-split them. The banked
   `caveats.spin_state` presents this as a Ti problem; it is a three-metal problem.
2. **The species index is state-dependent, not metal-dependent** (§A11.2). Any prior
   statement implying a per-metal index is withdrawn.
3. **`nosym`/`noinv` presence is state-dependent on Ru and Ir** — their `slab` decks carry
   both; their adsorbate decks carry neither. An insertion rule keyed to those lines would
   misplace the spin block.
4. **The Löwdin extraction recipe exists only in shell history**; no script is in the repo,
   and the nspin = 2 Löwdin block has a different internal shape (spin-up/spin-down/
   polarization rows). It must be committed before this arm's Löwdin is extracted.

## A11.9 What this amendment does NOT license

No relaxation of any kind, in any cell. No change to the production convention (U = 0,
nspin = 1 on Ru and Ir). No replacement of any banked A0 row. It does **not** discharge the
owed S0(h) RuO₂ AFM re-anchors, which stay HOLD. It does **not** license reporting a bare
"4 of 6". And it does not license re-scoring **only** the prediction that failed — if the
equalised rows are read for A7.3, A7.2 is re-read on the same rows or the omission is
stated with its reason (docs/60 exists because of exactly that selectivity).

## A11.10 Scope relation to A6.6

A6.6 registers block 6A as *"~160 fixed-geometry SCFs and zero relaxations"* and states it
*"does not license … any relaxation in any cell"* (docs/43:1285, 1288-1289).

- **Calculation-class overage: NO.** The clause A6.6 polices is *relaxation*, and this arm
  runs zero. A6.4 defines an A0 point by its class — a fixed-geometry single-point SCF —
  and every deck here is one.
- **Scale overage: YES, and disclosed.** This arm adds SCFs beyond the registered count.
  docs/59 already records the count actually run against the registered figure; this
  amendment extends that disclosure rather than restarting it.
- **Ti contingency, live.** docs/59 §3c is **not yet countersigned**. It sets whether Ti's
  rows survive at all, and therefore the denominator this arm is scored against.
  **PROPOSED sequencing: Ru first, then Ir, and Ti only after countersignature** — running
  Ti first spends SCFs on rows that may be WITHDRAWN-UNSCORED and lets the target move
  mid-flight.

## A11.11 Deposit obligation

Committed and pushed **before** any deck of this arm is staged or submitted — docs/59's own
standard. DOI line left blank for the dated fill. Whether this deposits as its own Zenodo
version now or is appended with A10 on Sep 18 is the entrant's call; under A7.8/A8.9/A9.7
the deposit precedes the first *governed* job either way.

---

## Decisions the entrant owes before Stage 1 submits

Ordered by what blocks what. Items 1–4 gate the first scored deck.

1. **The headline census election** (§A11.5) — dated and committed *before* Stage 1, not after.
2. **The seed set and the selection tolerances** (§A11.6).
3. **P-SPIN-DELTA's movement threshold and falsification band** (§A11.3).
4. **docs/59 §3c countersignature**, which sets the denominator and gates every Ti deck.
5. **The A7.7 disposition mapping for a middle band.** A7.3 registered consequences for ≥4
   and ≤1 only; 2-or-3 maps to nothing, in the old census and the new one alike.
6. **The denominator rule** — rewrite "≥4 of the 6" as a fraction or an explicit
   per-denominator table, so the count survives Ti's rows being withdrawn (6 → 5). "≥4 of
   the 6" is undefined against five metals and that contingency is live right now.
7. **Whether Cr/Mn/Fe owe a matching seed search** (~28 SCFs). Without it the arm equalises
   the spin *keyword* but not the search *effort*: Cr ran one seed, Mn one, and only Fe
   *OOH got a three-seed pilot — so the three new metals would be searched harder than the
   three they are compared against. **Recommended: yes.**
8. **Whether A7.2 is re-read on the equalised rows**, or explicitly not re-scored with the
   reason stated (§A11.9).
9. **Whether Mn's A7.5 AFM condition is in scope or explicitly deferred.** Mn is
   FM-initialised against a registered AFM condition and carries the largest span in the
   numerator (0.6307 V).
10. **Whether the Ru AFM probe runs** (4 SCFs, gate-(h) recipe, recorded either way, not
    entering the A7.3 score) and whether it is sequenced with the owed S0(h) re-anchors,
    since both act on Ru.
11. **Amendment number and ledger placement.** The body cap at docs/43:1930 is already
    reached; P-FLOOR-U-SPIN and P-SPIN-DELTA cannot silently become a seventh and eighth
    body row.
12. **Commit the Löwdin extractor** before this arm's Löwdin is extracted (§A11.8 item 4).
