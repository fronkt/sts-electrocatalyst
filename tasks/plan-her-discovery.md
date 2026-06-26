# Tracker — Generative + DFT HER Catalyst Discovery (fallback)

Week-by-week checkbox tracker for [docs/21](../docs/21-fallback-execution-plan.md). This is the
compute-only parachute ([docs/20](../docs/20-fallback-bestbet-her-discovery.md)); it shares the UMA
pipeline with the main HEA-OER project and **fully activates only if the main project's Week-9
go/no-go fails** — but Phase 0–1 (data + pilot) can run in parallel now at low intensity.

## Phase 0 — Setup & data (Week 0–1)
- [ ] Confirm **OCx24** access/license (experimental HER benchmark); curate a literature-HER fallback set if blocked
- [ ] Pull OC20/OC22 (`fairchem`), Materials Project (API key), OQMD, Alexandria subsets
- [ ] **Swap the UMA backend adsorbate** `*OH/*O/*OOH → *H`; add ΔG_H\* = ΔE_H + 0.24 eV referencing
- [ ] Positive-control sanity: reproduce known ΔG_H\* (Pt(111) ≈ −0.09 eV, MoS₂ edge, Ni₂P)
- [ ] **GATE:** pipeline reproduces known ΔG_H\* within tolerance → proceed

## Phase 1 — Generator pilot (Week 1–2)
- [ ] Train a *small* from-scratch flow-matching generator on a subset
- [ ] Stand up **MatterGen** fine-tuning (open weights) with a property head, in parallel
- [ ] Score both on validity (`pymatgen`) + stability (e-above-hull < 0.1 eV/atom via MLIP)
- [ ] **GATE (decision):** commit to the higher valid+stable generator (from-scratch vs MatterGen fine-tune)

## Phase 2 — Full generator training (Week 2–4)
- [ ] Train the chosen generator, conditioned on (ΔG_H\* ≈ 0, stability ↑, abundance/cost)
- [ ] Validate conditioning: does steering the target shift the output distribution as intended?
- [ ] Lock the trained generator checkpoint (versioned)

## Phase 3 — Generate → screen → rank (Week 4–6)
- [ ] Generate ~10⁴–10⁵ candidates; filter validity + single-phase/synthesizability gate
- [ ] UMA-screen → ΔG_H\*; rank by |ΔG_H\*| + stability + abundance
- [ ] Novelty filter (not in training set / not a known catalyst)
- [ ] **GATE:** ≥ N novel near-apex candidates → proceed to DFT; else widen conditioning/space

## Phase 4 — DFT validation (Week 6–8)
- [ ] DFT (VASP/QE) on top ~10–20 novel candidates: bulk relax → surface → \*H adsorption
- [ ] Document functional (e.g., RPBE), k-points, convergence; UMA-vs-DFT parity plot
- [ ] **GATE:** ≥ 1–2 DFT-confirmed novel hits (|ΔG_H\*| < 0.10 eV) → Finalist path; else honest screening writeup (Scholar floor)

## Phase 5 — Benchmark & iterate (Week 8–11)
- [ ] **OCx24 benchmark:** predicted vs experimental HER → Spearman ρ + Pearson (error bars)
- [ ] Positive-control rediscovery report; baseline comparison (random, heuristic, descriptor baseline)
- [ ] Active-learning round 2: feed DFT labels back → re-condition generator → re-propose
- [ ] (Optional, Scholar→Finalist) one collaborator-measured experimental anchor

## Phase 6 — Write (Week 11–13)
- [ ] Figures F1–F7 ([docs/21](../docs/21-fallback-execution-plan.md) §7)
- [ ] Paper draft; limitations + AI-disclosure sections
- [ ] **Early Oct: DATA FREEZE — write.**

## Decision log
- _(record the Week-2 generator choice, the Week-6 candidate count, the Week-8 DFT outcome, and the fork decision here)_
