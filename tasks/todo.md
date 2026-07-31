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

## R1 CAMPAIGN — STAGED, blocked on one approval
- [ ] **Frank: approve the box** — machine 13822, interruptible $0.30 bid, ~$1.6
      expected for all 10 jobs, tripwire destroy at $3.20. Everything else is
      ready: `src/dft/{setup_r1_box,queue_r1}.sh` + `src/dft/jobs_r1.txt`.
- [ ] Ni rescue (2 prepared restarts) → n=4 [best value/$: p goes 1/3 → 1/12]
- [ ] Ru/Ir DFT anchors (8 jobs) → the DFT tier's FIRST external validation
      (lit. η RuO₂ 0.37–0.42 V, IrO₂ ≈0.56 V) and n→6. Gate pre-registered in
      docs/30 §7 before any number exists.

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
