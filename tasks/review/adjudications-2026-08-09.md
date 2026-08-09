# Adjudications — Week-1 deck review, 2026-08-09

Six adversarial verifiers returned **31 blocking findings** against the three Week-1 deck
builders. All six verdicts were FIX_FIRST; none of the three blocks was safe to launch.

These are the rulings. They are binding on the fix round. Where a ruling differs from the
verifier's proposed fix, the reason is given — a verifier's suggestion is evidence, not an
instruction, and two of them proposed changes to a committed pre-registration that only the
pre-registration may make.

**The governing rule.** Three builders each wrote a `PREREG` block into a source file, and
all three contradicted docs/43. **docs/43 is the only pre-registration.** Every in-code rule
becomes a pointer to it. Delete the copies; do not reconcile them. The pre-registration
changes that were genuinely warranted are already in **docs/43 amendment 1** (commit
`0244f4e`), written before any block-1A/1B/1C job ran, with the previous wording quoted
beside the new one and the pre-amendment document archived.

---

## Block 1A — cell × symmetry

| # | ruling |
|---|---|
| **[1]** `*O` excluded | **ADOPT IN FULL.** docs/43 §2 already required it; the builder's physical argument is false by its own construction (`*O` can be *translated* off the plane even though it cannot be yawed, and `kick_y` already does exactly that for the spectator). Without ΔG_O in the 2×1 cells, ΔG₂ and ΔG₃ are uncomputable and P12's primary bin boundary cannot be evaluated for any metal. ~10 relaxations + 1 SCF; they are the cheapest jobs in the block. |
| **[7]** 2×1o spectator kick differs between arms | **ADOPT FIX (a)** — kick `ref__2x1o` only, never the 2×1o adslab `off` decks. With the working adsorbate yawed and `nosym` set the cell has no mirror, so the spectator is already free without being pushed *differently* between arms. **Also register (b)** as a contingency: if `ref__2x1o`'s spectator relaxes to \|Δy\| > 0.02 Å, add `ref__2x1o_mir` **before** the interaction is scored. Both are now in docs/43 §2-A.2. |
| **[3]** no Cr magnetic-basin control | **ADOPT BOTH PARTS.** (a) record total and absolute magnetisation for every Cr job; `mir` and `off` members of a pair must agree to 0.1 μ_B or the pair is CONFOUNDED and excluded. (b) one fresh-density fixed-geometry SCF per Cr 2×1 relaxation, ≤ 5 meV. Also extend GATE C to compare magnetisation, not energy alone. docs/43 §2-A.3–4. |
| **[4]** `MAG_MULT = 1.93` from a mismatched pair | **ADOPT.** The cited Ru denominator is `probe/Ru/slab__dipole`, the slowest Ru slab in the archive, not a base SCF. Set **MAG_MULT = 3.5** from the four same-wave `probe/Cr/*__base` ÷ `probe/Ru/*__base` pairs in `runs/probe/queue_scf.log`, and name the base runs in the comment. |
| **[5]** `CELL_MULT = 4.0` quoted as the headline | **ADOPT, AND MEASURE IT.** Quote **5.5** as planning and **8.0** as ceiling, with 4.0 labelled the floor it is. Then measure: run Cr `s0_OH__1x1_k8` and Cr `s0_OH__2x1o_mir` at identical NP/nk for ~15 min each and take the ratio of "total cpu time" increments per SCF iteration per k-point. Replace the assumption with the measurement before quoting a budget. |
| **[2]** ionic-step counts assumed *below* the measured 1×1 values | **ADOPT.** Re-quote every row from the measured counts (Cr `*OOH` 82, Cr `*OH` 44, Ru `*OOH` 68, Ir `*OOH` 60, Ir yaw90 54) in a cell with **twice** the free atoms and a spliced half-and-half start. Compute estimates in this project come in low every time (lessons.md, 2026-08-05); assuming *fewer* steps in a harder cell is that failure mode with the sign flipped. |
| **[6]** one manifest at one NP; critical path is a single job | **ADOPT.** Split: Ir/Ru jobs + the Cr SCFs at NP=4/NCONC=5; the Cr 2×1 jobs at NP=20/NCONC=1, one per box. 20 is an exact multiple of nk ∈ {2,4}, and 20 ≤ 23.04 cores. Order the Cr off-plane jobs **first**. Renting more boxes cannot shorten a single 234 h job — only ranks can. |
| **[8]** no `max_seconds`; stale `.out` skipped forever | **ADOPT ALL THREE PARTS.** (i) upload the three dirs and md5-verify; (ii) add a pre-flight loop that aborts if any manifest input is missing; (iii) emit `max_seconds` at ~2× the corrected estimate so pw.x stops cleanly and restartably. **And: never gate on `JOB DONE`** — gate on `bfgs converged` — and delete the `.out` before any re-run, because `queue_r1.sh` skips on `JOB DONE` and pw.x prints it on `nstep` exhaustion. |

---

## Block 1C — Hessian

The most serious class of finding in the review: **the verdict logic as coded could not
return its own falsifying answer.** A pure compute failure and a genuine scientific null
produced the identical campaign-level sentence.

| # | ruling |
|---|---|
| **[21] [30]** gate failures scored as AMBIGUOUS → R3 fires on an artifact | **ADOPT.** New per-state verdict **VOID** for any failed gate, distinct from AMBIGUOUS. `campaign_verdict` returns **"PILOT INVALID — no campaign decision"** if any state is VOID. Only gate-clean CONFIRMED/REFUTED may reach the R3 branch. docs/43 §3-A.1. |
| **[24]** REFUTED unreachable | **ADOPT.** Route sub-floor imaginary modes to **REFUTED**, naming them and reporting the largest as a number. As coded, docs/43 §3's declared consequence — keyed on "both pilot states come back REFUTED" — could never fire, which is the exact quiet reframing that section exists to prevent. docs/43 §3-A.2. |
| **[31]** underpowered against the mode it exists to detect | **ADOPT.** Effective floor = max(50 cm⁻¹, 3σ) per mode. New verdict **UNDERPOWERED** when the highest-y-character mode's floor exceeds **i80 cm⁻¹**; its declared response is a tighter-`conv_thr` rerun, **not** R3. Correct the "~70 cm⁻¹" (a 1σ figure quoted against a 3σ rule) to the 3σ number. docs/43 §3-A.3. |
| **[22] [29]** `conv_thr = 1e-10` never reached anywhere in this repo | **ADOPT — AND IT IS ALREADY RUNNING.** One job, `probe/Ir_hess/s0_OOH__hess_ref`, was released at 18:55 UTC before the other 37 to measure iterations-to-1e-10, whether the accuracy plateaus, and the printed `ethr`. Registered in docs/43 amendment 1 as a **throwaway feasibility probe whose output will not be used as the Hessian reference.** Also set `electron_maxstep ≈ 120` so a stall costs 11 h, not 18.4 h. |
| **[26]** Cr `*OOH` is a proton-shared H-bonded chain at 1 ML (H···O = 1.338 Å) | **ADOPT, WITH A SPLIT.** Scope every verdict to "q = 0, 1×1 cell, 1 ML" and add the wavevector caveat to REFUTED. **Hold Cr** until 1A returns the cell verdict, then run it in the chosen production cell. **Run Ir now** — milder (2.516 Å) and it is the state with the known −291 meV escape, so it is the one the saddle-point claim most needs. Holding both would put R3 past Week 1; holding neither would let a coverage artifact be read as the symmetry trap. docs/43 §3-A.7. |
| **[23]** reference never checked against its source relaxation | **ADOPT.** New gate **Q0**: \|E_ref − E_source_relax\| ≤ 10 meV and, for nspin = 2, \|M_ref − M_source\| ≤ 0.1 μ_B. Record `source_final_energy_ev`, `source_final_total_mag`, `source_final_abs_mag` in the manifest. All 19 jobs start from a fresh superposition, so they can agree with each other while collectively sitting in the wrong basin — docs/41 §6f exactly. |
| **[27]** 6 decks carry zero information, 24 more measure a non-diagnostic block | **ADOPT, WITH THE REASON RESTATED.** The verdict rests on the **±y block**; keep the ±y central difference for its √2 noise gain. The ±x/±z decks are *retained* but their stated purpose changes: they are bought for block 2B's in-house ZPE/−TS table, not for the 1C verdict. Delete the six redundant `ym` decks only if the ±y central difference is preserved. docs/43 §3-A.8. |
| **[25] [28]** in-code `PREREG` contradicts docs/43 §3 in six places | **DO NOT RECONCILE — DELETE.** Replace `PREREG` with a pointer to docs/43 §3 + §3-A, and delete the "paste this into docs/43" instruction so a third copy cannot appear. The changes that were warranted are already in amendment 1; the ones that were not (y-character 0.50→0.90, single magnetic exclusion voiding a state) are **rejected** — neither came with a stated reason, and a registered threshold is not moved without one. |

---

## Block 1B — hp.x

| # | ruling |
|---|---|
| **[15]** nothing exercises the code path the campaign needs | **ADOPT — highest-value item in this lane.** TiO₂ is nspin = 1, fixed occupations, d⁰ closed-shell, empty Hubbard manifold; production is nspin = 2, smeared, metallic, partially-filled 3d. Six co-varying differences, and hp.x takes a different branch on gapped vs smeared. Add one **bulk rutile CrO₂ arm** (~10 min of box time), required to print a finite U with zero "Convergence has not been reached". Without it a GO licenses only "hp.x validates on a closed-shell bulk insulator". docs/43 §4-A.3. |
| **[12]** builder re-registered the gate, widening it | **REJECT THE WIDENING.** External window stays **[3.0, 7.0]** — no physics reason was given for [2.0, 8.0]. The amplitude-independence criterion is **withdrawn with its reason** (hp.x is DFPT; no amplitude keyword exists — the check was unperformable, not merely unmet) and replaced by the CrO₂ arm. Recorded as an amendment to P15, not a fresh registration. docs/43 §4-A.1–2. |
| **[13]** χ-symmetry gate is probably an identity | **DEMOTE TO A REPORTED DIAGNOSTIC**, pending one `iverbosity = 2` read of whether hp.x prints χ pre- or post-symmetrisation. A hard gate that cannot fail is not a gate. The real reproducibility test becomes `find_atpert = 4`, two independently perturbed Ti within 0.05 eV. Keep docs/43's 0.05 relative tolerance if the printed χ turns out to be pre-symmetrisation; do **not** adopt the builder's 50×-tighter 1e-3. docs/43 §4-A.4. |
| **[10] [11] [19]** cost model anchored on the cheapest possible mesh **and** on Γ | **ADOPT.** nq = 2×2×2 is the one mesh where every q is a TRIM, so hp.x gets maximum symmetry reduction at every measured point, and the slab timing deck measured Γ — the cheapest point that exists. Measured k-counts: 65 (Γ), 130 (zone boundary), 208, **576**. Re-cost per (atom, q) scaled by the k-count hp.x prints for every q, and take the slab timing at a **general, non-Γ** q. This model is what block 3Y's go/no-go rests on. docs/43 §4-A.5. |
| **[9] [16] [18]** shared prefix + outdir; concurrent rungs collide | **ADOPT.** Two hp.x runs at the same prefix+outdir were *measured* colliding — run B died with exit 2. Give each rung its own outdir, or serialise on the `(dir, prefix)` pair by holding the lock across the hp.x call. Enforce **NCONC = 1** where a manifest shares a prefix, and state `NP × NCONC ≤ 23` in both manifest headers. Parallelism comes from *different* prefixes (atomic vs ortho, sym vs nosym). |
| **[16] [17]** results overwritten in place; success grep matches nothing | **ADOPT.** U, χ⁰, χ and the Hubbard matrix appear **only** in `<prefix>.Hubbard_parameters.dat` and `<outdir>/HP/<prefix>.chi*.dat` — never in stdout. Measured: `grep 'Hubbard U parameters:' hp.out` = 0 on a run that produced U = 4.1543 eV, and a second run overwrote the first's `.dat` in place. Rename every artifact onto the deck basename `$hp` immediately after the call, and gate on the artifact, not on stdout. Fix the docstring claim that `iverbosity = 2` puts χ in the output file. |
| **[14]** criterion I5 has no deck | **ADOPT.** Add `find_atpert = 3` decks and manifest lines. They are ~3 s counting jobs; the cost is zero and the criterion is currently unmeetable. |
| **[20]** the run directories do not exist on the box | **ADOPT.** Upload and verify, plus a pre-flight in `queue_hp.sh` that reads the manifest once and exits non-zero if any directory or input is missing, before launching anything. |

---

## Standing instructions for the fix round

1. **docs/43 (with amendment 1) is the rule.** Read it. Where code and docs/43 disagree,
   docs/43 wins and the code changes. Do not edit docs/43.
2. **Fix, then prove.** For each finding, state what you changed and the check that shows
   it is fixed — a byte check, a mutation test, a re-count, a run. "Addressed" is not a
   result.
3. **Do not launch production jobs.** Parse-only and sub-60-second smoke tests under
   `/workspace/scratch_<lane>/`, cleaned up afterwards. The one exception already running
   is `probe/Ir_hess/s0_OOH__hess_ref`; leave it alone.
4. **Do not commit.** The orchestrator commits.
5. If you believe a ruling above is wrong, say so in your return value with the reason and
   implement it anyway. A disagreement recorded is useful; a ruling silently ignored is not.
