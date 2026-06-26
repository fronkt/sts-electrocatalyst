# Week-by-Week Tracker — Catalysis HEA OER (STS 2027)

Detailed spec: [`../docs/12-catalysis-hea-execution-plan.md`](../docs/12-catalysis-hea-execution-plan.md).
Anchor: today 2026-06-25 → **submit by ~Nov 5, 2026 (8 pm ET)**. **DATA FREEZE
early Oct.** Critical path = **FWM melt** (start Week 1) and **instrument
booking** (start Week 0).

> ⚠️ Gated: confirm the 4 logistics answers in [`todo.md`](todo.md) before melt.

## Phase 0 — Setup & access (Wk 0–2, Jun 25 – Jul 12) — *do in parallel*
- [ ] **Sponsor locked**; STS adult-sponsor + SRC/Risk-Assessment forms started (KOH, Cr(VI), metal dust).
- [ ] **Potentiostat/EIS time booked** at Purdue (recurring slots); reference electrode (Hg/HgO) sourced.
- [ ] **FWM melt channel confirmed** — turnaround quoted; composition-request template ready.
- [ ] Compute stood up: `fairchem`/OCP (OC22 model), `pymatgen`/`ASE`, `Ax`/`BoTorch`, GPU (Vast.ai/Purdue HPC).
- [ ] Lab notebook + git repo for the ML code initialized (independence evidence).
- [ ] Order EC consumables (GC electrodes, Nafion, 1 M KOH, Ni foam, NiFe precursors).

## Phase 1 — ML round 1 (Wk 1–4, Jun 29 – Jul 26)
- [ ] **Wk 1:** define composition space (Fe-Co-Ni-Cr/Mn/Cu); build slab/adsorbate enumerator; smoke-test OC22 inference on a known oxide.
- [ ] **Wk 2:** compute *OH/*O/*OOH descriptors → η_theo for candidate compositions; implement phase-stability filter (VEC, δ, ΔH_mix, ΔS_mix, Ω; pycalphad if available).
- [ ] **Wk 2:** **submit FWM round-1 melt request** (3–4 compositions) — *critical path; provisional list OK, refine before they cut metal.*
- [ ] **Wk 3:** multi-objective Bayesian opt (activity × cost × formability) → finalize round-1 shortlist; freeze the predicted ranking (for later correlation).
- [ ] **Wk 3–4:** synthesize/obtain **NiFe-LDH baseline**; build + dry-run EC protocol (RHE calibration, iR/EIS) on baseline + bare GC.

## Phase 2 — Fabrication & characterization (Wk 5–6, Jul 27 – Aug 9)
- [ ] Receive FWM ingots; **XRD** (single-phase?) + **SEM-EDS** (nominal vs actual composition).
- [ ] **Go/no-go (end Wk 6):** if multi-phase → re-anneal/down-select.
- [ ] Electrode fabrication (cut/polish/mask geometric area, or powder + ink on GC/Ni foam).
- [ ] CV activation protocol → form active (oxy)hydroxide.

## Phase 3 — OER round 1 (Wk 7–9, Aug 10 – Aug 30)
- [ ] LSV (iR-corrected) → **η @ 10 mA cm⁻²** for all candidates + baseline + controls, **triplicate**.
- [ ] Tafel slopes; **ECSA** (C_dl); EIS at onset.
- [ ] Ablation control (binary/ternary sub-alloy) measured.
- [ ] **Go/no-go (end Wk 9):** compute ML-vs-experiment rank correlation; decide **round-2 melt vs computational round-2**.

## Phase 4 — Active learning round 2 + stability (Wk 10–13, Aug 31 – Sep 27)
- [ ] Condition surrogate on measured η; **propose 1–2 refined compositions**; submit fast round-2 melt (if viable).
- [ ] **Stability:** chronopotentiometry @ 10 (±100) mA cm⁻², **≥12 h** (longer if time) on round-1 best.
- [ ] Post-mortem **XRD/SEM-EDS(/XPS)** → document reconstructed active phase.
- [ ] Measure round-2 samples; finalize all EC data + error bars.

## Phase 5 — Freeze & write (Wk 14–19, Sep 28 – Nov 5)
- [ ] **Wk 14 (by ~Oct 4): DATA FREEZE.** Final figures (F1–F7), statistics.
- [ ] **Wk 15–16:** draft Methods + Results; mentor review.
- [ ] **Wk 17:** draft Intro + Discussion + Conclusion; tighten to ≤20 pg.
- [ ] **Wk 18:** STS essays, project questions, recommendations, transcript, forms.
- [ ] **Wk 19 (by Nov 5, 8 pm ET):** final proof → **SUBMIT**.

## Standing reminders
- One reaction, one baseline, one metric — resist HER/CO₂RR scope creep.
- Triplicate everything; report std-dev; document iR + RHE calibration each session.
- ML is a *calibrated screening prior*, not an oracle — the honest correlation is the contribution.
- Push code + this tracker to GitHub after each phase (no co-author trailer).
