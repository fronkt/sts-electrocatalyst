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
- [ ] **THE BUY: Ni + Co, 4 concurrent jobs, ~$4.** Not Cu. Rationale in docs/34 §4: no
      candidate lands in clear space (Ni is 0.063 V from Fe, Co 0.009 V from Mn), so each
      brings its own unresolvable pair — which is exactly why n = 7 beats n = 6. If all
      three unresolvable pairs swap: n=7 → ρ 0.893, p **0.0123** (clears comfortably);
      n=6 → ρ 0.886, p **0.0333** (clears, zero margin); n=5 → p 0.083 (fails, as today).
      Both metals need the two-stage `degauss` protocol; both died on the same SCF plateau,
      so running both is the hedge against one failing.

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
