# docs/78 — Action board: what is free, what is cheap, what is declined (2026-09-03)

## 0. Status

**Not a registration.** Every arm below needs a dated line written by the entrant before decks are
built. This file consolidates what a feasibility review established against the tree and against
Anvil directly, and supersedes four sentences of record that are false — §1.

---

## 1. FOUR SENTENCES OF RECORD THAT ARE FALSE — strike these first, 0.5 h

A report that inherits a false premise loses on the premise, not on the science.

| where | the false sentence | measured |
|---|---|---|
| **docs/76 §5.2** (this session's own) | "**cannot run hp.x on Anvil**" | **hp.x is on Anvil.** `/anvil/projects/x-che260157/qe/env/bin/hp.x`, beside the production `pw.x`, and it starts: *"Program HP v.7.5 starts on 3Sep2026"*. docs/51:22 says no hp.x **path** — a statement about the driver script. docs/76 escalated it to a capability claim. **That escalation is mine and it is wrong.** |
| **docs/51:24, docs/54:288** | the Cu PAW pseudo "is not among the 12 UPFs staged on Anvil (preflight would refuse)" | **False, and the repo already says so.** `$PROJECT/pseudo` holds `Cu.paw.z_11.ld1.psl.v1.0.0-low.upf` — the exact string `runs/Cu_slab/slab.in:35` names. `anvil/pseudo_md5_preflight_2026-08-23.md:23` already flags both citations: *"registration, not staging, excludes Cu."* |
| **docs/51:23** | "No converged Co \*OOH exists anywhere" | **Stale by hours.** `runs/s3/Co/s0_OOH__2x1v_mir.out` (bfgs=1, scffail=0, −4662.69189747 Ry) and `…__off.out` (−4662.68039155). S3 launched the same day docs/51 was written. |
| passim | "the comparator machine" (singular) | **Two Vast.ai boxes.** 47662258 (`root@ssh8.vast.ai:22258`, `anvil/20_stage.sh:9`, np=20) and **47025043** (`src/dft/queue_hp.sh:67`, np=18). The "108 core-hour" hp.x figure is an **np=18 slab** number. |

The last one matters beyond bookkeeping: **the 108 core-hour hp.x cost is the SLAB.** The **bulk**
CrO₂ hp.x ran clean — 37.44 s SCF + 19 m 36 s HP at np=20 = **6.75 core-hours**, zero
non-convergence. **16× cheaper, opposite outcome.** docs/76 §6 refused hp.x on the strength of the
slab number applied to a bulk arm.

---

## 2. THE GOVERNING DISTINCTION, and it is already deposited

`docs/43:1396-1399`, verbatim:

> "the measured quantity of every arm is a **difference between two treatments of the SAME slab**; a
> difference is a valid method measurement whether or not the slab is a synthesisable electrode. The
> report may therefore never quote an absolute η for Cr, Fe, Co or Ni **as a materials claim**; they
> appear only inside paired within-metal differences."

And `docs/43:1405`: *"FeO₂, CoO₂, NiO₂ = MODEL PHASE, method test systems only."*

**A7.5 bans a number, not a calculation.** For a projector Δη — a within-slab paired difference —
Co and Ni are licensed by the same sentence that licenses **Fe, which is already in the six**. The
phase-reality objection does not bite on a paired difference. That answers the expansion question
in principle. It does **not** follow that expanding is right — see §5.

---

## 3. TIER 0 — free, owed regardless, ~5 hours, 0 SU

| # | action | hrs |
|---|---|---|
| **0.1** | **Open the three Zenodo deposits** (or publish an open companion carrying hypotheses, thresholds, freeze dates, SHA-256s). All three are **restricted** — a judge who clicks the DOI in November hits a permission wall, and pre-registration has zero mentions in nine years of the public record. Highest ratio on the board. | **1** |
| **0.2** | **Strike the four false sentences** in §1. | **0.5** |
| **0.3** | **Twin methods-paragraph figure** — the two projector arms' methods paragraphs side by side, byte-identical, with 1.155 V / 1.642 V and the two limiting steps beneath. | **1-2** |
| **0.4** | **Bank two zero-SU products already paid for** — §4. | **1-1.5** |
| **0.5** | **Disclosure line** for the AI Xu `.in` parses this review round; precedent `docs/43:1811`. | **0.5** |

---

## 4. TWO RESULTS ALREADY ON DISK, UNBANKED, 0 SU

### 4.1 Co — a magnetic-metastability datum, and it is the better of the two

`runs/s3/Co/s0_OOH__2x1v_mir__g1.out` = **−4662.63696095 Ry** against its parent's
**−4662.69189747 Ry**. The fresh-density GATE-1 child lands **+747.5 meV ABOVE its parent at
byte-identical geometry**, with total magnetization moving **20.13 → 24.86 μ_B**. Both sides clean
(scffail = 0, JOB DONE).

That is the C8 magnetic-metastability class firing **on a metal outside the roster**, and in the
**opposite direction** to the three banked BASIN_DRIFT rows — where the child landed *below* the
parent. A class that fires both ways is a stronger claim than one that only ever fires downward,
because "the optimizer keeps finding lower states" has a benign reading and "the converged state
depends on the starting density in both directions" does not.

**Take the finding. Decline the arm.** Co's four converged 2×1v states also give η = 0.4625 V at
PLS 2, invariant to which \*OOH is used — but that is a materials-shaped number A7.5 will not let
the report quote, and it buys nothing the finding does not.

### 4.2 Ni — one deck from closing a converged chain

The 2×1v-off chain is converged and internally consistent — `ref__2x1v`, `s0_O__2x1v_off`,
`s0_OH__2x1v_off`, `s0_OOH__2x1v_off`, all bfgs = 1 / scffail = 0 — giving ΔG_OH 2.4777, ΔG_O
4.5094, ΔG_OOH 4.8149, **η = 1.2477 V, PLS 1**. One deck blocks banking it: `s0_OH__2x1v_off__g1`
SCF-failed at 500 iterations. **The repair deck already exists and is unrun** —
`runs/s3/Ni/s0_OH__2x1v_off__g1.fromparent.in`, `startingpot = 'file'` on line 27. The
`.fromparent` idiom has converged before in this exact directory. Submit-only, ~50 SU.

**Do NOT touch the Ni 1×1 tier row.** Every 1×1 \*OOH trajectory *started desorbed* — 3.075, 3.124,
3.327, 3.353 Å — and the only deck that started bound (2.225 Å, the PULL_TO repair) SCF-failed with
**zero `ATOMIC_POSITIONS` blocks**. `src/hea_oer/surfaces_rutile.py:189-200` names this defect with
Ni in the sentence, and `PULL_TO = (1.70, 2.10)` at `:171` is the registered remedy. **Ni 1×1 \*OOH
is untested, not unbound.** Any "coverage-driven binding transition" reading is a re-publication of
this campaign's own quarantined builder defect, and `docs/35:88-92` already archived the 5.202 eV
bound it would resurrect (ΔG₄ = −0.282 eV, thermodynamically impossible). **Leave
`hi_closed: false` alone and say why.**

---

## 5. THE ANSWER ON Ni, Co, Cu — and on expanding

| metal | as a paired-difference test system | as a materials claim | verdict |
|---|---|---|---|
| **Ni** | OPENABLE, ~50 SU + 0.5 h, deck already exists | CLOSED (A7.5) | **Do it** — submit-only |
| **Co** | OPENABLE at 0 SU, four states already converged | CLOSED (A7.5) | **Take the finding (§4.1), decline the roster row** |
| **Cu** | Legal in principle — **but there is nothing to pair.** `runs/Cu_slab/slab.out` does not exist; `s0_OH`/`s0_OOH` both carry `convergence NOT achieved`; `s0_O` is a partial. Absent from `tier_v2` entirely. ~3,000+ SU, 12-25 h, unbounded tail on a d10 oxide 0.180 eV/atom above hull | Banned outright (exclusion table, `docs/43:1408`) | **Decline. Write the withdrawal line.** |

**Cu's withdrawal line is worth more than a rescued number:** *the one metal whose SCF would not
converge under this protocol, twice, and which is therefore absent from every table.*

**Do we expand the roster to the excluded metals? No.** `docs/43:1962` (A9.6, deposited) caps
in-house n at 8; V, Nb, Mo, W, Re, Rh, Pt, Ta, Ge, Pb, Os, Tc have **no pseudopotential staged**
(verified live) and `47_submit_a0.sh:40-44` fail-closes; each needs four unlicensed relaxations.
**And you reach five of them through the Xu deposit at zero SU** — §7.

**Do not add Co and Ni to P-PROJ-6 either.** Both are ultrasoft. Adding them takes the PP census
from 4-of-6 to **6-of-8 ultrasoft**, which makes docs/77's confound clause *harder* to rule out on
the metals that fire, not easier. **The cheap de-confounder is not a metal at all**: a
second-pseudopotential control on Ru at fixed geometry, ~50-100 SU, already priced at `docs/45`
row 10 and already declared "an anchor-pair comparability control, NOT a new error class."

---

## 6. TIER 2 — compute. One registration sitting, ~7 entrant-hours, ~360 SU total

| # | action | SU | hrs |
|---|---|---|---|
| **2.1** | **P-PROJ-6** — 24 decks built at `runs/a0/pproj6/`, **none licensed**. Close the three blockers in the dated line (docs/77 §§3-6). | ~299 / ~600 | **3-4** |
| **2.2** | **hp.x CrO₂ bulk ortho leg** — the `{TiO₂, CrO₂} × {atomic, ortho}` grid is missing **exactly one cell**, and it is on the flagship material. Verified: `runs/hp_tio2/` holds `hp__atomic_q*`, `hp__ortho_q*` and `hp__cro2_q222` — no `cro2_ortho`. Takes the projector U-split from **n = 1 to n = 2** and crosses the nspin axis. | ~11 floor / ~72 ceiling | **2.5-3** |
| **2.3** | **Submit `runs/s3/Ni/s0_OH__2x1v_off__g1.fromparent.in`** (§4.2). | ~50 | **0.5** |
| **2.4** | **Re-realize `runs/s0/e_proj/s0_O__u715_{atomic,ortho}` on Anvil at np=128**, in a copy dir. **Deletes the flagship's only structural defect** — it is currently a cross-machine composite, that pair having run at np=20 on the destroyed box. A8.8 permits it explicitly: *"a re-run is a new measurement reported alongside… never a silent overwrite."* Nobody proposed the cheapest fix to it. | ~10 | **0.5** |

**hp.x riders, each a deposited rule rather than a preference.** Write into an isolated copy dir per
A8.8 — `queue_hp.sh`'s `run_one` writes `> "${hp}.out"` unconditionally with no stale-output
refusal, so pointed at `$RUNS/hp_tio2` it would **overwrite banked evidence**. Inherit the deposited
**0.2 eV** q-mesh threshold (`docs/43:276`); do not invent a tighter one off TiO₂'s known flatness,
because *"a threshold invented after the quantity is known is worth nothing."* And pre-state the
named risk: **nspin=2 × ortho-atomic has never been run in this campaign**; a stalled ortho leg
returns **no number** and is written up as a methods limit, not as a ΔU. `queue_hp.sh:334-337`
proves hp.x writes the `.dat` even after non-convergence, so an artifact alone is not a pass.

**What actually blocks hp.x is ~30 lines and 2.5-3 hours:** no Slurm wrapper exports
`QE_PREFIX`/`PSEUDO_DIR`/`RUNS` into `queue_hp.sh`; `queue_hp.sh` has **no `pseudo_dir` rewrite**
where `queue_r1.sh:293` does, so the decks still name the Vast path
`/usr/share/espresso/pseudo`; and a dated line. `anvil/46_a0.slurm` already runs `pw.x` then a
*second* binary (`projwfc.x`) in one job against one shared scratch, gated on the SCF succeeding —
structurally identical to SCF-then-hp.x. The "array races one shared SCF" objection is a
`queue_r1.sh` property; `queue_hp.sh` already holds an flock, and the arm worth running is a single
non-array job.

---

## 7. THE CEILING — P-XU-SPAN

The review's judgement, and it revises docs/75 §1: the **lock census (P-XU)** does need the full
silentgate core, three-class logic, a per-corpus noise floor, seven spec rulings and the P-CTRL
apparatus — that is the 30-55 hours, and it does not fit.

**P-XU-SPAN (A9.3.3) is a different, already-deposited prediction**: `span_U(c_M) > 0.20 eV on ≥5
of the 10 rutiles, FALSIFIED below 3 of 10`, gas-reference-free, computable from the 680-file U
ladder **by text reading alone**. It is **blind on 10 of 10 metals**, five of which sit on this
project's own exclusion row — so it reaches excluded metals at zero SU, which §5 says the in-house
route cannot. The zip is already on Anvil and md5-matched. **12-18 hours, < 1 SU, start no later
than Sep 8; if it slips past Sep 20, cut it** — a half-written reader in October is worse than none.

---

## 8. DECLINED, with the reason recorded

| route | reason |
|---|---|
| **Ortho relaxation** | Destroys the byte-identical construction — the estimand *is* a difference between two treatments of one slab. **Do not cite cost as the reason**: ~1,700 SU is affordable, and docs/76's figure was not derived from any relaxation on disk. **Do not say "the code cannot do it"** — `pw.x` refuses ortho forces only for gamma-only and Hubbard-background cases, neither applying here, and `runs/a0/p_proj/s0_OH__u715_ortho.out:2036` prints forces with no warning. A referee refutes that in one grep. |
| **CrO₂ *slab* hp.x** | 4/4 non-converged, 108 core-h per (atom,q) pair, no pre-statable success criterion. |
| **hp.x on a new material** | No bulk cell exists anywhere in the tree for β-MnO₂, RuO₂ or IrO₂. |
| **Cu as a metal** | §5. |
| **Excluded metals in-house** | §5. |
| **Adding Co/Ni to P-PROJ-6** | Worsens the PP confound. §5. |
| **Reinstating a Ni dG_OOH bound** | §4.2. |

**What is honestly owed on the relaxation question instead**, and it strengthens the paper: the
fixed-geometry pair sits on geometries relaxed at **U = 3.70** and is evaluated at **U = 7.15**,
leaving residual forces 39×-79× outside the decks' own `forc_conv_thr` **on both legs** — a
U-transfer displacement, not a projector one (the leg ratio is only 1.077-1.231). The project's one
measurement of what relaxing buys over a transferred single point is
`runs/s0/h_afm_relax/README.md`: **−2.4 / −2.2 / −8.8 meV**, converging in 2-3 ionic steps.
Volunteer both numbers in one paragraph.

---

## 9. CALENDAR

- **Tier 0 by Sep 7.** Free, owed regardless.
- **Tier 1 (P-XU-SPAN) starts Sep 8**, lands by Sep 20 or is cut.
- **Tier 2 registration sitting Sep 8-9**; decks drain the same week — the queue is empty and the
  longest arm is under two hours wall clock.
- **Sep 18** (A10 deposit or withdrawal) and **Sep 20** (six-row displacement + claim sentence) are
  both better decisions with Tier 2's readout in hand. That is the argument for submitting on Sep 8
  rather than at the Sep 26 arithmetic latest.

Total across the whole board: **~30-42 entrant-hours, ~2,600-3,000 SU — 4-5 % of the balance.**
