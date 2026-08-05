# STS 2027 — TODO

## Status (2026-07-24)
**FRAMING: HEA-OER electrocatalyst campaign REVIVED; thermal lane DROPPED** (owner
decision 2026-07-23). Revival plan + literature synthesis in
[`docs/28`](../docs/28-electrocatalyst-revival-plan.md). Thermal-era todo archived at
[`todo-archive-2026-07-24-pre-catalysis-revival.md`](todo-archive-2026-07-24-pre-catalysis-revival.md);
thermal artifacts (docs/24, 27, runs_cpa/) preserved as-is. Catalysis trackers
`plan-catalysis-hea.md` / `plan-her-discovery.md` unchanged.

Key corrections to the parked-project record (docs/28 §1–2):
- The endmember DFT queue DID complete (2026-07-13, docs/26) — 4/6 converged.
- The "UMA cannot rank rutile OER" verdict is CONFOUNDED: parity used the `oc20`
  (RPBE-metals) task head; the correct `oc22` (PBE+U oxides) head was never tested.
- 5 of 6 rutile endmembers are not physically realizable electrodes — a stability
  gate (Pourbaix ΔG_pbx) is required before any screening claim.

## Gate G-R0 (blocks all compute — Frank's call)
- [ ] Approve/adjust the R0–R4 revival plan in docs/28 §7 (incl. vast.ai spend)
- [ ] Revoke old HF token (frankcai222), mint fresh one (needed for gated
      `facebook/UMA` checkpoint) — carried from docs/23 §9
- [ ] Decide branch strategy: catalysis revival off `main` vs continuing on
      `thermal-round0` (repo currently dirty on thermal-round0)

## R0 — Kill the artifact — DONE 2026-07-25 (docs/29); GATE NOT MET
- [x] Re-run UMA parity with `uma-s-1p2` (fairchem 2.21.0 doesn't register 1p2p1;
      1p2 is the on-plan oc22 carrier) + `oc22`/`oc20`/`oc25`; per-head CHE chain
- [x] Built RuO₂/IrO₂(110) in-distribution anchors (same builder, verified to 3e-9 Å)
- [x] GATE RESULT: **oc22 ρ = −0.80** (anti-correlated), oc20 ρ = 0.0, oc25 ρ = +0.2
      (QC-tainted), baseline +0.4 → "~0 → negative result is REAL". docs/28 §2
      confound hypothesis REFUTED; no out-of-box head ranks rutile OER. Anchors
      exonerate the pipeline (oc20/oc25 nail IrO₂ 0.52/0.57 V vs lit 0.56).

## QC AUDIT — DONE 2026-07-31 (docs/30, commit 1a3a77b, $0 spent)
- [x] Strict QC tooling (`src/dft/qe_qc.py`); `parse_qe_energy` can no longer
      return an energy from a run that failed SCF or never converged
- [x] **η(NiO₂) = 1.751 V RETRACTED** — `s0_O`/`s0_OH` both died on a failed SCF
      while printing JOB DONE, at 7× and 13× the force threshold, energy still
      falling 0.013/0.040 eV per step and accelerating. The `.in.restart` files
      prepared in docs/26 §4 were never run. docs/29 §4b "NiO₂ breaks *OOH/*OH
      scaling" withdrawn — the bias runs in exactly that direction.
- [x] R0 restated at n=3: oc22 goes −0.80 → **−1.00**. Verdict SURVIVES and
      sharpens; but n=3 has no power (a perfect ordering gives p=1/3), so the
      campaign is short of DATA POINTS, not of another task head.
- [x] Slab constraint float-tie fixed (the mid-plane layer was decided by
      rounding: 11 free atoms for Cr/Mn/Fe/Cu/Ru, 10 Ir, 8 Co, 7 Ni — Co and Ir
      split symmetry-equivalent atoms). Does not affect the R0 parity; does bias
      the cross-metal η ranking.
- [x] Ru/Ir anchors made reproducible from committed code (byte-exact for Ru),
      wired for `eta`, and patched ~4× cheaper (nspin=1 for the non-magnetic
      anchors; nosym on the clean slab only). CRLF trap closed for `*.in`.
- [x] 785-frame MLIP training set extracted + validated (`src/dft/qe_frames.py`);
      ASE's espresso-out reader fails on 33 of 44 archived slab outputs

## REFERENCE REPAIR — RUN AND CLOSED 2026-08-02 (docs/33 §5b, $2.64, instance destroyed)
- [x] Three structures that passed `qe_qc` were chemically wrong; all three re-run, all
      three superseded. **η(CrO₂) 1.726 → 0.491 V** (Cr–O 2.016 → 1.572 Å, −1.396 eV);
      Fe/Mn `*OOH` finally bound at 2.552/2.480 Å. η(Fe), η(Mn) unchanged (both pls=2).
- [x] MACE-MPA-0 had predicted all three: η(Cr) to **9 mV**, Fe–O to 0.013 Å, Mn–O to
      0.06 Å. **The MLIP was right and our DFT reference was wrong.**
- [x] `src/dft/adsorbate_qc.py` added (chemical validity, which `qe_qc` is blind to by
      construction). Two of its own thresholds were then falsified by the repair results
      and corrected — both pinned in `tests/test_adsorbate_qc.py`.
- [x] **2026-08-03: the repaired outputs had been written NEXT TO the reference**
      (`.out.shortbond` / `.out.bound`) so `dft_reference()` still returned the trapped Cr
      for a day. Files swapped, defective ones kept as `.out.trapped-*`/`.out.desorbed-*`,
      `tests/test_dft_reference.py` added to pin it. 59 tests pass.
- [x] Docs 29/30/32/33 corrected; pre-repair versions archived with provenance headers.
      **R0 headline changes shape**: oc22 goes ρ = −1.000 → **0.000** (n=5) / **+0.500**
      (n=3). "No out-of-box UMA head ranks rutile OER" SURVIVES (best is oc25 at +0.400,
      p = 0.52). "oc22 ranks them *backwards*" is WITHDRAWN — and a material part of that
      anti-correlation was our own trapped Cr. docs/29 §8.
- [ ] Cost overrun to note: $2.64 vs a $0.6–1.1 estimate. Magnetic 3d slabs with 32–36
      k-points run 10–12 h, not the 3–5 h projected off the non-magnetic anchors.

## R1 CAMPAIGN — RUN AND CLOSED 2026-08-01 (docs/32, $4.42, instance destroyed)
- [x] Ru/Ir DFT anchors, 8/8 jobs TRUSTWORTHY, geometries verified textbook.
      **η(RuO₂) = 0.787 V, η(IrO₂) = 0.781 V.**
- [x] **GATE NOT MET** (docs/30 §7): both η land inside 0.30–0.90 V (clauses 1–2
      PASS) but η(Ru) < η(Ir) **FAILS** — by 6 mV, which is a tie, not a
      mis-ordering. Absolute error +0.39 V (Ru) / +0.22 V (Ir) vs literature.
- [x] **The deliverable is the tier's measured resolution**: differential error
      between two similar rutiles ≈ 0.17 V, versus a true Ru–Ir gap of ~0.15 V.
      Supports **Cr > Fe > {Mn ≈ Ru ≈ Ir}** — three distinguishable levels over
      five materials. R0's negative result is untouched (ρ = −1.00 is far larger
      than any resolution question).
- [x] IrO₂ `*OOH`/`*OH` scaling = 3.652 eV (+0.45 outside band) while Ru = 3.180
      (textbook) — so not a pipeline systematic. H-bond explanation tested and
      REFUTED (both `*OH` near-identical, neither H-bonded). Unresolved, recorded
      both ways, η unaffected (`pls = 3` never touches ΔG_OH).
- [x] Ni rescue FAILED: `s0_O` stalled and was killed, `s0_OH` orphaned. Ni stays
      retracted, **n = 5**.
- [ ] ~~**Frank's call — Ni rescue round 2, ~$5–9?**~~ **SUPERSEDED 2026-08-03 — this is
      now the top-priority spend, re-costed at ~$4, and it beats the fine-tune.** See
      docs/32 §5 and docs/33 §6. Three changes:
      - **Price**: measured, not guessed — 4 concurrent magnetic-3d jobs ≈ $4 (from the
        repair run's 3 jobs / 12.1 h / $2.64), inside the $8.46 credit.
      - **Scope**: run Ni (`s0_O`, `s0_OH`) **and** Co (`s0_O`, `s0_OOH`) together. Both
        died on the same SCF-plateau pathology, so both need the two-stage `degauss`
        protocol and neither is safe alone; running both means one failure still gives
        n = 6, and success on both gives n = 7.
      - **Why it beats the $1.9 fine-tune**: at n = 5 *only* a perfect ordering reaches
        p < 0.05, and MACE's single error is the Ru/Ir pair our own DFT separates by
        6 mV — so the gate asks a model to reproduce an ordering the reference cannot
        resolve, and a perfect score would be indistinguishable from luck. At n = 6 the
        **free** model, keeping the error it already has, gives ρ = 0.943, p = 0.017.
- [x] **DONE 2026-08-03, $0 — predictions frozen in [docs/34](../docs/34-prereg-sixth-point.md).**
      Protocol validated on the five knowns from BUILDER geometries with zero DFT input:
      ρ(η) = **+0.900**, η MAE = **0.150 V**. Predictions: **Ni 1.200 V (outside the
      cluster — BUY)**, Co 0.883 V (inside, 9 mV from Mn), Cu 1.373 V (outside but needs
      4 jobs and has no working `slab.out`). All three pls = 2, descriptors 2.11–2.60.
- [x] **DONE 2026-08-03 — the constraint float-tie is 1–4 mV and does NOT matter.**
      Same metal, same geometries, mask swapped: Ni 1.200 → 1.196, Co 0.883 → 0.882,
      against a 0.17 V tier resolution. So Ni/Co **reuse their existing TRUSTWORTHY
      states — 2 jobs each, not 4** — and docs/30 §3's ranking concern is largely retired.
- [x] **LAUNCHED 2026-08-03 — instance 46726365 (Norway, 96 vCPU, $0.268/hr), 5 jobs.**
      Became 5 jobs not 4: `adsorbate_qc` found `Ni_slab/s0_OOH` **desorbed at 3.080 A**
      despite 39 converged ionic steps and a TRUSTWORTHY verdict — a fourth instance of
      the same defect. Every job starts from the MACE minimum, not the builder placement,
      because the builder's ~3.1 A `*OOH` has now failed on Mn, Fe AND Ni (and MACE says
      Co would follow: builder 2.983 A vs pulled-in 2.105 A at 0.427 eV lower).
      Two-stage SCF: `scf` at degauss 0.03 -> `relax` at production 0.01 with
      `startingpot='file'`. **Both metals that had never converged passed stage A**
      (Co 6134 s, Ni 6957 s) — the plateau that killed three prior attempts is beaten.
      All four pseudopotential MD5s verified identical to the archived runs.
      Infra cost of getting there: $0.044 on a broken box (3 new lessons in lessons.md).
- [x] **CLOSED 2026-08-04 — [docs/35](../docs/35-n7-campaign-result.md). GATE MET.**
      n=5 -> **n=7**. MACE-MPA-0, free and un-fine-tuned: rho=+0.857, exact p=**0.0238**.
      (n=6 with Ni alone: rho=+0.886, p=0.0333.) The binding constraint was n, exactly as
      docs/34 argued. **eta(Ni)=1.084 V, eta(Co)=0.544 V.**
      - Pre-registered test **1 hit / 1 miss**: Ni +0.116 V (within the 0.150 bar), Co
        **+0.339 V (2.3x out)** — and MACE's "Co is inside the cluster" call was wrong too.
      - Both `*OOH` jobs FAILED (Ni SCF diverged 3x; Co ran out of credit at 16 ionic).
        eta survives via `src/dft/eta_bounded.py`: dG3+dG4 = 4.92 - dG_O contains no
        dG_OOH, so eta is bounded from measured quantities. Co's tight high edge closed by
        its partial relax (a run stopped early sits ABOVE its minimum -> upper bound).
      - **Fourth desorbed `*OOH` found** (Ni, 3.080 A, TRUSTWORTHY by qe_qc, 39 ionic).
        Archived; it would have given dG4 = -0.282 eV.
      - **Spend $8.17 vs a $3.20 projection — 2.5x over.** docs/35 s6. The three jobs that
        mattered cost ~$4; the two `*OOH` jobs were worth $0 because the bound made them
        unnecessary. Deriving that bound BEFORE renting would have saved half the money. Not Cu. Rationale in docs/34 §4: no
      candidate lands in clear space (Ni is 0.063 V from Fe, Co 0.009 V from Mn), so each
      brings its own unresolvable pair — which is exactly why n = 7 beats n = 6. If all
      three unresolvable pairs swap: n=7 → ρ 0.893, p **0.0123** (clears comfortably);
      n=6 → ρ 0.886, p **0.0333** (clears, zero margin); n=5 → p 0.083 (fails, as today).
      Both metals need the two-stage `degauss` protocol; both died on the same SCF plateau,
      so running both is the hedge against one failing.

## R4-PREP — MELT-LIST REGENERATION (started 2026-08-05; potentiostat BOOKED)
The docs/15 melt set was ranked by **UMA rutile**, and R0 voided that ranking (no
out-of-box UMA head ranks rutile OER; best oc25 ρ=+0.400, p=0.52). The compositions
are still meltable objects, but "ML-predicted best" is not a supportable claim about
them. Regenerating the list is free (MACE + MP), needs no Vast credit, and must
happen before a melt slot is spent — a frozen prediction table built on a void
ranking would contaminate the campaign's central contribution.
- [x] **A. DONE 2026-08-05 (commit 10189d0).** Multi-start adsorbate placement.
      places at 1.85–1.90 Å above the slab's TOPMOST atoms; on rutile(110) those are
      the bridging-O rows, so the adsorbate lands 3.07–3.13 Å off the cus metal —
      the exact defect docs/34 §4b priced at $2.64 and four wrong structures. The
      HEA path (`add_oer_adsorbate_at`) inherits it verbatim. Port the proven
      remedy: builder start + rigid pull-in to M–O 1.70/2.10 Å, lowest energy wins.
      Measured on the HEA path: `*O` 3.080 Å, `*OH`/`*OOH` 3.130 Å off the cus metal
      — every adsorbate started **past the 3.00 Å desorption cut**. Remedy = builder
      start + rigid pull-ins to M–O 1.70/2.10 Å, lowest energy wins; winning bond
      length recorded so a desorbed "minimum" cannot enter a melt list silently.
      Both pull-in and builder starts win on different states, so all three are kept.
- [x] **B. DONE 2026-08-05 (commit 10189d0).** MACE-MPA-0 backend
      (`relax.make_mace_calculator`, `"mace"` in the registry), CPU, float64.
- [x] **B2. DONE 2026-08-05 (commit 294fb01).** Pool cus sites over 3 decorations.
      A 2×2 slab has only 4 cus sites and seed 0 puts *only* Co/Fe on them for
      Fe32Ni17Co34Mn18 — Ni and Mn (34 at.%) never appear at an active site. The
      2026-06 UMA sweep had the same weakness.
- [x] **E. DONE 2026-08-05.** Multi-element Pourbaix (`src/dft/pourbaix_multi.py`,
      9 tests). Metric = **soluble cation fraction at pH 14 / 1.53 V vs RHE**, which
      avoids inventing a ΔG_pbx for an HEA oxide MP does not hold. Quaternary hull
      reproduces docs/31 §4's per-element assignments exactly (Fe→Fe₂O₃(s),
      Co→CoOOH(s), Mn→MnO₄⁻, Ni→Ni(OH)₃⁻). **docs/15 melt set, soluble fraction:**
      FeCoNi 33.3% < Fe32Ni17Co34Mn18 34.0% < Cr19Co28Fe25Ni28 47.0% <
      Co20Ni20Cr20Mn20Cu20 60.0% < Cr6Fe33Ni27Mn34 67.0% < Mn19Fe12Ni35Co16Cr18 72.0%.
      Every candidate ≥33% soluble; Ni soluble in all, Cr soluble in all Cr-bearing.
      Concentration sensitivity checked: Ni stays Ni(OH)₃⁻ from 1e-8 to 1e-4 M and
      only passivates as NiO at 1e-2 M, so the **ordering is robust** across the
      dilute range but the absolute % is not a physical constant.
- [x] **C. DONE 2026-08-05 — GATE MET ([docs/36](../docs/36-screen-validation-and-stability-gate.md)).**
      Pipeline scored on its OWN slabs vs the n=7 DFT tier: **ρ = +0.8571, exact
      p = 0.0238, η MAE = 0.130 V** — 42 mV BETTER than docs/35's 0.172 V, which
      scored the same model on the DFT tier's own geometries. Letting the MLIP find
      its own minimum beats scoring it on someone else's. Worst point is **IrO₂
      (−0.254 V)**, which moved from +0.131 in docs/35 — a caveat on any "beats
      IrO₂" claim. Two rank errors, both on pairs the reference cannot resolve
      (Co/Ir, Mn/Ni; tier resolution ~0.17 V).
- [~] **D. RUNNING 2026-08-05 09:35** — `screen_mace.py screen`, 12 diverse
      single-phase candidates (3339/4000 passed the Hume-Rothery/Ω–δ filter),
      4 cus sites × 3 decorations, checkpointed per candidate to
      `results/r4_screen.json`. ~15–20 h on this CPU-only box; partial results
      ranked and usable throughout. A GPU box does it in <1 h for ~$1 —
      **Vast credit is $0.295**, so that is a top-up decision, not a technical one.
- [ ] **F. New frozen melt list** (docs/36) + weigh sheet, superseding docs/15 §1.
      Framing: activity ORDERS, stability GATES, and since every candidate is ≥33%
      soluble the list should deliberately SPAN the activity/stability tension rather
      than scalarize it away — that tension is the HEA thesis's subject (docs/31 §8).
      Must retain a predicted-poor anchor for correlation dynamic range (docs/15 §6).

## DECISION FORK (docs/29 §7) — now effectively A **and** B; confirm
- [x] **Path A** banked and QC-hardened (the negative is stronger after the audit)
- [ ] **Path B** R3 fine-tune: data extracted, MACE-OMAT recipe costed at ~$1.9,
      leave-one-metal-out CV drafted. Free Stage 0 (E0-only recalibration on the
      laptop CPU) may settle it for $0 — run that first.

## R1 — DFT hygiene
- [x] Free reanalysis: volcano positions, G_max, ±0.3 V error bars (DONE, docs/29
      §4b): all 4 on the scaling line far off-apex, step-2 limited; Mn only one near
      a real-electrode band; NiO₂ breaks OOH/OH scaling −0.51 eV (hypothesis only)
- [ ] U-sensitivity + magnetic protocol + dipole/solvation (MODERATE, CPU-box-weeks):
      DEFERRED until Path A/B chosen — B reframes what these re-runs are for

## R2 — Stability gate (mostly free)
- [ ] MP Pourbaix ΔG_pbx for all 6 endmembers + candidate HEA oxide products
- [ ] Integrate stability into the screening objective (Tran-2024-style)

## R3 — Fine-tuned screener (single GPU-days)
- [x] Convert archived QE trajectories (78396b5) → training set (785 frames,
      `src/dft/qe_frames.py`). **Verified uncontaminated 2026-07-31**: pw.x emits
      `!  total energy` only for a converged SCF, so a failed cycle contributes no
      frame. Checked on all four POISONED trajectories — `n_energies == n_scf_ok`
      exactly. They still donate their *good* frames (17 from Ni s0_O, 36 from Ni
      s0_OH, 6 from Cu s0_OOH): rejected for η, salvaged for training.
- [x] **Stage 0 CLOSED analytically — do not run it** (`src/dft/e0_stage0.py`).
      The CHE reference is stoichiometrically closed, so an arbitrary per-element
      E0 shift leaves every ΔG unchanged (verified through the real referencing
      path, max |Δη| = 3.6e-15 eV over 8 systems). Therefore the oc22 ρ = −1.00 is
      **not** a reference-energy artefact — the whole composition-linear subspace of
      model error is projected out of the descriptor, and being force-free it does
      not move geometries either. The failure is geometry-dependent local chemistry:
      relative *O vs *OH binding across metals.
- [ ] Fine-tune MACE-OMAT (naive, LR 1e-3, E0 reestimated) and/or UMA-small
      head-only (LR 4e-4). **Gate must be the CHE observable, not energy MAE** —
      E0 alone can cut total-energy MAE a long way while leaving every η identical.
- [ ] **Gate arithmetic (exact permutation, not asymptotic).** LOMO CV yields one
      held-out η per metal; Spearman is computed across those. At the n available:
      | n | ρ needed for p<0.05 | ranking errors tolerated |
      |---|---------------------|--------------------------|
      | 4 | unreachable (ρ=1 → p=0.083) | — |
      | 5 | **1.000 only** (p=0.017); ρ=0.9 → p=0.083 | **zero** |
      | 6 | 0.886 (p=0.033); ρ=1 → p=0.0028 | two |
      So "Spearman ≥ 0.8" is only a meaningful gate at n ≥ 6. At n = 5 the fine-tune
      must rank all five *perfectly* to claim anything.
- [ ] Re-screen HEA space: activity × stability × cost; optional AL loop
      (3–10 DFT/loop)

## R4 — HEA tier + write (Sep → data freeze ~mid-Oct)
- [ ] SQS approximants of top-3 compositions, DFT-blessed
- [ ] Oxyhydroxide-termination spot-check (alkaline active-surface story)
- [ ] Melt decision at FWM — Frank's call
- [ ] STS report framing (AI-assistance rules per docs/25) — Frank writes

## Standing non-technical (carried over)
- [ ] STS sponsor of record still unresolved (docs/16 §10) — highest-priority
      non-technical item; **application due Nov 5, 2026, 8pm ET**
