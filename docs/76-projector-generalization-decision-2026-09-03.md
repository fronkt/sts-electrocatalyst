# docs/76 — Generalizing the projector result, and the r4 re-rank verdict (2026-09-03)

## 0. Status

**Not a registration.** Nothing here licenses a deck, moves a threshold, scores a prediction, or
amends a deposited section. §2's registration text is a **draft for the entrant to re-author in his
own words and date before any deck is built**; per docs/43 A7.7 the report paraphrases and never
copies. Three **BLOCKING** defects were raised against the first version of this plan and are
applied below; §6 records them so the corrected form is checkable against the version it replaces.

**The question:** the single biggest attack on A7.1 is that it is **n = 1** — one metal (Cr), one U
(7.15 eV), one cell, one code — and Cr's eta(U) curve is a V with its minimum at U = 3.5, so Cr is
unusually sensitive exactly there. What is the cheapest defensible upgrade before the writing start?

---

## 1. A FREE RESULT, ALREADY ON DISK

The standard referee reduction — *"the projector is just a reparameterisation of U; you
re-discovered your own U grid"* — **is refutable today, on banked data, at zero compute.**

Fitting the Cr ortho-atomic leg onto Cr's own banked atomic ΔG(U) curves with a single free U shift,
searched over the registered 0-9 eV grid:

| leg | best-fit atomic | ortho | residual |
|---|---|---|---|
| ΔG_OH | 2.0374 | 2.8723 | **−0.8348 eV** |
| ΔG_O | 4.8186 | 4.6051 | +0.2135 eV |
| ΔG_OOH | 4.7956 | 4.7504 | +0.0452 eV |

Best-fit shift **+1.817 eV, pinned at the grid edge** (U → 8.967 of 9.0); RMS residual **0.4982 eV**.

Put the other way, **the implied U displacement is not single-valued**: ΔG_OH demands +11.32 eV,
ΔG_O +1.04 eV, ΔG_OOH +0.27 eV, η +2.14 eV — a **42x spread across four observables from the same
calculation**. And the ortho ΔG_OH sits **0.83 eV above the atomic curve's maximum anywhere on the
0-9 eV grid**, a displacement equal to **79 % of the entire nine-eV ΔG_OH sweep**.

**This establishes the mechanism, not just the magnitude: no value of U reproduces the ortho result.**

**Governance.** This was computed from data already seen. **Cr is calibration, not a scored
prediction**, and must be described in those words in the same sentence. The blind test is the five
other metals.

**Corrected statistic (BLOCKER A1).** The first version proposed registering the residual `R_M` as
the primary estimand on the argument that η = max(ladder step) − 1.23 makes an eV residual and a
volt commensurate. **The identity is real; the inference is false.** A uniform offset `c` on all
three cumulative ΔG moves step 1 by +c, step 4 by −c, and steps 2 and 3 by zero — so at pls 2 or 3,
**`R_M` = 0.40 eV with Δη = 0.0000 V exactly.** Across the six metals, a fixed `R_M` = 0.10 eV
corresponds to |Δη| spanning **0.0028 V (Fe) to 0.1277 V (Ti) — a 46x spread**. And under the
grid-decimation null the legs agree to 0.0035 eV while η disagrees by 0.155 V.

> **|Δη| is the primary statistic.** It is A7.1's registered estimand, it needs no new threshold and
> no borrowed transfer, and it is what the headline actually claims. `R_M` is a **named diagnostic**
> for U-irreducibility only; if registered at all, its threshold derives from its own null
> (the 0.0035 eV interpolation floor), never from A7.1's volts.

---

## 2. THE ONE ARM TO RUN — P-PROJ-6

**24 ortho-atomic fixed-geometry SCFs:** {Cr, Mn, Fe, Ti, Ru, Ir} x {slab, *O, *OH, *OOH} at
**U = 7.50 eV**, paired against banked atomic legs at byte-identical geometry. The atomic legs are
**not** re-run.

**Why U = 7.50**, all five reasons measured rather than argued:

| | U = 4.50 | **U = 7.50** | per-metal own U | U = 3.70 |
|---|---|---|---|---|
| banked atomic partners | 225.1 SU | **138.7 SU — cheapest common rung** | 146.0 SU, six different U | n/a on 5 metals |
| non-convergence in partners | **Fe *O hit `electron_maxstep=200`; 266.5 SU over 4 submissions** | **zero — 24/24 clean** | mixed | — |
| distance from headline U = 7.15 | 2.65 eV | **0.35 eV** | 0.65-3.65 eV | 3.45 eV |
| atomic pls baselines spanned | 2, 3 | **1, 2 and 3 all present** | mixed | 2, 3 |
| known trap | Ir sits on its own pls flip bracket | — | six different geometry-to-probe U offsets | Cr's η is stationary here |

U = 7.50 carries a `HUBBARD (atomic)` card with each metal's own U on **all six** decks, so the
transformation is the same prefix-plus-one-keyword edit `src/dft/build_pproj.py` already asserts at
build time — and simpler, because the U value needs no edit. U = 0 rows are a literal no-op and are
excluded.

### Cost — corrected (BLOCKER B1)

The first version applied a realized-burn multiplier of 1.32 from a banked total of 30,467.4 SU.
**That total is not reproducible.** A complete sweep of every `runs/**/*.out` reporting
`running on 128 processor cores` with a `PWSCF … WALL` line — 563 outputs — gives **24,263.1 SU**
against **40,238.9 SU** billed (100,000 − 59,761.1). **The multiplier is 1.658, not 1.32**, so every
figure below is the first version's scaled by 1.256x.

| line | SU |
|---|---|
| banked atomic partners at u750 (24 decks, 128 cores) | 138.7 |
| ortho SCF penalty x1.24 (measured on the four existing pairs) | 172.0 |
| `projwfc.x` inline — **mandatory** per A6.5(1), omitted by every first-pass design | +8.2 |
| realized-burn x1.658 | — |
| **PLANNING** | **~299 SU** |
| high case (ortho x1.61, worst measured ratio) | ~385 SU |
| escalation reserve, 2 decks at `electron_maxstep=200` | +104 … +220 |
| **CEILING** | **~600 SU — 1.0 % of balance** |

Escalation risk is genuinely low: worst atomic iteration counts at u750 are Ti *OOH (50) and Fe *O
(32); at the measured x1.63 iteration inflation those reach ~82 and ~52, far short of 200.

**Wall clock: under two hours** from `sbatch` to the last JOB DONE. Longest deck is Mn *OOH at
10.2 SU = 4.8 min; x1.61 → ~7.7 min; the submitter runs `--array=1-N%6`, so 24 tasks drain in four
passes ≈ 35 min of compute. Queue is empty. The 48 h `-t` cap bounds any hang.

**Entrant-hours: 3.0-4.0**, none of it babysitting — 1.5-2.0 h for the registration line, 0.5-1.0 h
to countersign the readout, 1.0 h for the figure caption and disclosure paragraph.

### Dates

| | |
|---|---|
| **Arithmetic latest start** | **Sep 26** — 1 day compute, 1 day readout, 3 days slack for one escalation cycle, landing Oct 2 |
| **Recommended start** | **on or before Sep 8** |

**The real deadline is Sep 20, not Oct 6.** The six-row body-ledger displacement and the
claim-sentence re-test are both owed in writing by Sep 20 (docs/43:1930, :1932). Both are strictly
better decisions with an n = 6 result in hand than with a pending array. Sep 15-25 is already
double-booked against A10's Sep 18 deposit and, on another project, ICLR Sep 18 / Sep 25.

### Three registration blockers that must be closed BEFORE the decks are built

1. **(A1) Register |Δη| as primary, `R_M` as diagnostic** — see §1. A CONFIRM criterion on `R_M`
   can fire on a difference that moves the reported observable by nothing.
2. **(A2) Denominator is FIVE, not six.** The first version made Cr calibration in one paragraph and
   counted it in a ">= 4 of 6" roll-up in the next. Since `R_Cr` > 0.10 is known today, that means
   only 3 of the 5 blind metals must fire — **denominator padding of exactly the kind that has
   already cost this project twice** (A7.2 confirmed 5/6 on exactly 3 robust members; A7.3 NOT MET
   at 3/6). State the threshold as a fraction of the blind five. The proposed spin rider is also
   **vacuous** — the classes are {Cr,Mn,Fe} and {Ti,Ru,Ir}, so every 4-subset of a 3+3 partition
   necessarily contains one of each.
3. **(A3) Register a PSEUDOPOTENTIAL-FAMILY confound clause with the same force as the spin one.**
   docs/45:35 records PP family as **"NOT MEASURED — TRANSFERRED, no size available… UNREGISTERED —
   no amendment carries a PP/basis arm."** The census: ultrasoft {Cr, Mn, Ti, Ir}, PAW {Fe},
   norm-conserving {Ru}. **A CONFIRM set of four has exactly the cardinality of the ultrasoft
   family.** If the over-threshold set is exactly {Cr, Mn, Ti, Ir} or exactly {Fe, Ru}, the result
   is DECLARED CONFOUNDED with pseudopotential family and may not be reported as a class claim.
   Without this clause the arm reproduces the A7.3 failure structurally.

Minor, but it must not appear in a cross-metal table unremarked: **the k-mesh is not uniform** —
Cr/Mn slabs are `9 4 1`, Fe/Ti/Ru/Ir are `8 4 1`. Harmless within a pair; two meshes across metals.

---

## 3. THE RE-RANK VERDICT — withdraw as a product, write as a readout of record

Three independent reasons, each verified from disk:

**(a) It is not registrable as a blind test — the answer is already determined.** The correction
vector is public inside the project, the candidates' `bonds.site_metal` values are on disk, and both
aggregations follow in one line each: **Kendall tau = 0.7333** against the frozen order under
**both** pre-declared aggregations, identical corrected order, **one inversion**. Registering a
prediction tomorrow for an outcome computable today is precisely the violation the governance rule
exists to prevent.

**(b) Its own pre-declared verdict is UNSCORABLE, and that is knowable now.** The sole inverting
candidate is decided by **Ni**, and `data/tiers/tier_v2.json` carries Ni at `source: "bounded"`,
`dG_OOH: null`, `hi_closed: false` — **open above.** There is no bound to score the inversion
against.

**(c) The corrections cannot cover the compositions.** The six gated candidates' eta-determining cus
sites are **Cr x3, Co x2, Ni x1**. `tier_v2` carries chain-quality corrections for Cr, Fe, Ir, Mn,
Ru; **Co and Ni are `bounded`; Cu is absent entirely and so is Ti** — the tier's seven metals and the
A0 roster's six are different sets. A7.5 forbids quoting an absolute eta for Cr, Fe, Co or Ni as a
materials claim, which covers the eta-determining metal of **all six** candidates. And the ranking
has **exactly one resolvable boundary of five**: adjacent eta gaps are 0.0131 / 0.0261 / 0.2467 /
0.0299 / 0.0399 V against the pipeline's own MAE (0.0996 V against tier_v2), with per-site eta_std
of 0.135-0.329 V on top.

**Substance of the dated line the entrant writes** (his words, not these):

1. **S8 make-and-measure is WITHDRAWN for this cycle.** Reason of record, in this order: the
   measurement would not have adjudicated the finding — the audit is about rutile(110) DFT+U, and a
   melted high-entropy alloy is a different material system that cannot say which projector is right
   — followed by the schedule. **Name Action M** (n >= 7 IrO2 replicates on the booked potentiostat,
   no ingot, docs/75 §6) as the option considered and refused, and say why, rather than leaving it
   unmentioned.
2. **The r4 re-rank hook within S6 is CLOSED as a readout of record, not as a prediction** — tau =
   0.7333, identical order, one inversion, verdict **UNSCORABLE** because the inverting candidate's
   eta-determining metal has an open upper bound. No registration attaches.
3. **`results/r4_melt_list.json` is reported as a FROZEN CONTINGENT SHORTLIST** with three named
   caveats: one resolvable cut of five; composition-weighted chain coverage 0.060-0.637; A7.5's ban
   covering every candidate's eta-determining metal.
4. **Narrow the scope.** S6 is five deliverables; only the re-rank hook closes here. P-SYMCOV
   scoring is already implemented at 464 lines.
5. **The consensus is two sessions, not three.** docs/72 explicitly declines to say which way the
   call goes and records a live argument *for* a go (the potentiostat is booked). **Do not write
   "three independent sessions recommend NO-GO."**

**Two mechanical requirements.** Regenerate to `results/r4_melt_list_2026-09-03.json`, **not** over
the 2026-08-05 file — `results/` is gitignored wholesale and that file is the only copy of the frozen
record. And frame the regeneration as **executing the deferred freeze-time step**, not correcting
four weeks of neglect: `tasks/todo.md` item F already records the corrected output and states the
deferral in terms.

---

## 4. WHAT 59,761 SU ACTUALLY BUYS

1 SU = 1 core-hour exactly. Balance **59,761.1 SU, queue empty, nothing running.**

| in this project's own units | count |
|---|---|
| whole 128-core node-hours | **467** — 19.4 days of one node flat out |
| complete A0-main grids (239 SCFs, the entire headline dataset, 1,811.2 SU) | **33** |
| complete P-PROJ flagship experiments (8 SCFs, both projectors, 54.5 SU) | **1,096** |
| 1x1 fixed-geometry nspin=2 SCFs at the median 7.67 SU | **7,790** |
| **P-PROJ-6 as corrected** | **0.5 % of balance — runnable 200 times** |

**Two cautions and one conclusion.** The realized-burn multiplier is **1.658** — banked np=128 work
is 24,263 SU against 40,239 billed, and the gap is unbanked work: idle burn on a sick node, cancelled
jobs, superseded runs. **The tail, not the mean, is what costs**: retries are 5.6 % of decks but
~20 % of all banked core-hours; one deck (`Fe/s0_O__u450`) cost 266.5 SU over four submissions, and
the Ru nspin=2 ladder cost **5,216.7 SU for 0 of 16 converged.** And none of it is the constraint —
at 3-4 entrant-hours per arm against six already-owed decisions plus Sep 18 and Sep 20, the budget
supports **two compute arms, not six. Compute is 0.5 % spent; attention is ~100 % spent.**

---

## 5. THE GENERALIZATION VERDICT

**It becomes a class claim about the METHOD. It stays an existence proof about MATERIALS. Both are
true, both must be written, and the upgrade costs ~299 SU and 3-4 entrant-hours.**

**YES, by Oct 6:** that the projector split is not a property of CrO2. P-PROJ-6 crosses six metals,
three pseudopotential families, 3d/4d/5d, both spin conventions, and three distinct atomic pls
baselines — and with §1 it establishes the *mechanism* (irreducible to a U shift), not merely the
magnitude.

**NO, at any price before Oct 6, for four things** — state them as limits rather than leave them to
a referee:
1. **Relaxation.** Both legs are single points on geometries relaxed under the atomic projector, and
   residual forces are unequal (ortho ~20 % further from its own minimum). ~1,700 SU and **12-25
   entrant-hours** — cut.
2. **Self-consistent per-projector U.** ~~cannot run hp.x on Anvil~~ — **WITHDRAWN 2026-09-03, see
   docs/78 §1.** This was wrong and the error was mine: docs/51:22 says no hp.x *path*, a statement
   about the driver script, and this file escalated it to a capability claim. **hp.x is on Anvil** at
   `/anvil/projects/x-che260157/qe/env/bin/hp.x`, beside the production `pw.x`, and it starts:
   "Program HP v.7.5". What blocks it is ~30 lines of driver work (no Slurm wrapper exports the env;
   `queue_hp.sh` lacks the `pseudo_dir` rewrite that `queue_r1.sh:293` has) — 2.5-3 entrant-hours.
   The 108 core-hour figure quoted in §6 is the **slab** at np=18; the **bulk** CrO2 hp.x ran clean
   at **6.75 core-hours**, 16x cheaper, opposite outcome. The `{TiO2, CrO2} x {atomic, ortho}` grid
   is missing exactly one cell, on the flagship material, at ~11-72 SU.
3. **Coverage** — unless the A3 rider runs (~106 SU, ~1 h). Recommended.
4. **Any statement about real catalysts.** A7.5 bans the absolute-eta framing for the metals that
   carry it.

**The honest headline is not "DFT+U studies are wrong."** It is:

> In the protocol under which the overwhelming majority of published OER ladders and screening
> datasets are computed — a fixed, already-relaxed geometry with a transferred Hubbard U — swapping
> between two Hubbard-projector conventions that ship in the same Quantum ESPRESSO binary moves the
> overpotential by up to 0.49 V and changes which step limits, on N of 6 rutile endmembers. The
> change is not a reparameterisation of U: no value of U anywhere on the registered 0-9 eV grid
> reproduces the ortho-atomic result, and the best one-parameter U-shift fit leaves a 0.50 eV
> residual with its optimum pinned at the grid edge. The same projector pair splits the
> linear-response U on a second material by 1.45 eV. This is an existence proof about a widely used
> protocol, not a ranking of catalysts, **and it does not say which projector is right.**

That last clause is load-bearing and must never be dropped. **The result measures how much the
answer moves when a documented convention changes; it does not adjudicate the convention.**

**Two facts to volunteer rather than defend.** The flagship as it stands is a **cross-machine
composite** — the *O pair ran at np=20 on the destroyed Vast box, the other three at np=128 on
Anvil. And the complete ortho-atomic inventory of the entire campaign is **five input files in three
directories.** P-PROJ-6 takes that to twenty-nine.

---

## 6. WHAT NOT TO RUN

- **Relaxation under the ortho projector.** The claim *is* a difference between two treatments of a
  byte-identical slab; relaxing destroys the construction. ~1,700 SU is affordable; 12-25
  entrant-hours of babysitting inside the runway is not. No relax set in this project has ever
  completed without retries.
- **Any hp.x arm on a new material.** No Anvil hp.x path, comparator machine destroyed, 6-12
  entrant-hours before deck one. The VOID branch is mispriced 3-4x: `niter_max = 80` means a
  non-converging run burns all 80 iterations at every q — measured at **108 core-hours for one
  (atom, q) pair.** beta-MnO2 has no bulk SCF anywhere in this repo.
- **A fourth arm on the Ru U = 9 cell**, per docs/70 — the ladder is exhausted and A11.5 means no
  outcome can promote A7.3.
- **Any new error class**, **any MLIP re-screen**, **n = 25** — all previously closed.

---

## 7. THE SEQUENCE

1. **Now:** the three registration blockers in §2, then the dated P-PROJ-6 line. **Start by Sep 8.**
2. **Same week, 0 SU:** the §1 U-irreducibility fit written up as calibration, and the §3 dated
   S8 / re-rank disposition.
3. **Sep 18:** A10 — deposit or withdraw. docs/74 says NOT DEPOSITABLE with 9 blockers; withdrawing
   frees a body-ledger row and eases the Sep 20 displacement.
4. **Sep 20:** six-row displacement and claim sentence, with P-PROJ-6 in hand.
5. **Oct 6:** writing starts. Everything above is done or withdrawn by then, in writing.
