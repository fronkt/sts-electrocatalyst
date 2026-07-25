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

## DECISION FORK — Frank's call (docs/29 §7)
- [ ] **Path A** embrace the benchmark negative as STS finding #3/#4 (zero compute,
      ready now; recommended floor) — OR —
- [ ] **Path B** R3 fine-tune on archived QE trajectories (78396b5) → re-screen
      (single GPU-days; A becomes the before/after figure if B runs)

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
- [ ] Convert archived QE trajectories (78396b5) → training set
- [ ] Fine-tune MACE-OMAT (naive, LR 1e-3, E0 reestimated) and/or UMA-small
      head-only (LR 4e-4); held-out Spearman ≥0.8 gate
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
