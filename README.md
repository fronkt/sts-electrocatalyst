# STS 2027 — Materials + ML Project (Regeneron Science Talent Search)

Working repository for ideation, research, and planning of a Regeneron Science
Talent Search entry. "STS 2027" = the competition cycle culminating March 2027,
i.e. **entry due ~November 5, 2026**.

> Status: **ideation / scoping.** No project framing locked yet. This repo
> collects the competitive-landscape research and the candidate project ideas so
> a single framing can be chosen and turned into a week-by-week execution plan.

## The student / constraints

| | |
|---|---|
| Competition | **Regeneron STS** (solo only; ~20-page research paper) |
| Cycle | Entry due **~Nov 5, 2026** → Scholars (Jan), Finalists (late Jan), DC finals (March 2027) |
| Grade | Rising/current high-school senior |
| **Effective research runway** | **~3.5 months** (Jul → early Oct 2026; data must be frozen to write the paper) |
| Lab access | Fort Wayne Metals (alloys / fine wire / Fe-Ni) · Purdue lab (assistant researcher) · MIT industrial wet-lab connections |
| Existing ML stack | Generative crystal-structure prediction, alloy AI design, ML interatomic potentials / phonons (reuse to save months) |

## The strategic thesis (read first)

1. **Materials is a winnable-but-minority track at STS** (~2–4 of Top 40, ~15–25 of
   Top 300 each year). It is out-punched at the very top by biomed/comp-bio/math.
2. **The "high-κ material for heat dissipation" instinct has a proven ceiling.**
   The near-identical *Anthony Low '26 — "0D/2D Composite Phase Change Material for
   Thermal Management in HPC"* reached **Scholar, not Finalist**. Pure thermal-
   materials projects have historically capped at Scholar.
3. **The Top-40 computational template is inverse design / generative discovery**
   that *proposes **and** validates* candidates (Evan Kim's superconductor-GAN '23,
   Hirshorn's alloy inverse-design '26).
4. **The ceiling-breaker is a hybrid:** ML/simulation designs or screens a candidate →
   you **fabricate** it → you **measure** it and beat a baseline. Almost no STS
   entrant can close that loop; this student can.
5. **Rare-earth framings carry the strongest "so what"** (critical-materials /
   supply-chain / defense) — the kind of national-importance hook that lifts a
   materials project from Scholar to Finalist.

## Candidate directions (see [`docs/06-project-shortlist.md`](docs/06-project-shortlist.md))

- **Thermal:** heat-spreader alloy/composite inverse design · CFD-surrogate cold-plate · MLIP lattice-κ + defects
- **Rare earth:** RE-lean / RE-free magnet inverse design (incl. tetrataenite) · magnetocaloric solid-state cooling · ML-guided REE separation/recovery
- **Other screened lanes (full deep-dives in `docs/07`–`docs/11`):** batteries / energy storage · catalysis / electrocatalysis · solar / perovskites · computational-ML methods · metamaterials / metasurfaces

## Cross-lane verdict (after the lane deep-dives)

The deep-dives converge on one structural insight: **Fort Wayne Metals' real
superpower is melting custom Fe-based metal alloys**, so the highest-leverage
lanes are the ones that *consume* that capability with a fast, quantitative
measurement inside the 3.5-month window. Ranked by Finalist reward-to-risk:

1. **Catalysis — HEA electrocatalyst** (ML-screened → FWM-melted → OER/HER overpotential vs NiFe-LDH). *Fastest quantitative closed loop; strongest Finalist case.* → `docs/08`
2. **Batteries — all-iron redox flow** (ML electrolyte/composition → FWM iron → air-tolerant benchtop loop). *Same family as a recent Finalist (Sanxhaku '25).* → `docs/07`
3. **Rare-earth magnet** *or* **thermal heat-spreader alloy** — both FWM-fabricable, but VSM/PPMS (magnets) and laser-flash (κ) are slower, fussier measurements. → `docs/05`, `docs/04`
4. **Metamaterials** — feasible 3D-print + impedance-tube/Instron hybrid, but historically **Scholar-capped**. → `docs/11`
5. **Solar / perovskites** — air-sensitive, reproducibility risk, FWM weak fit. → `docs/09`
6. **Computational-only** — caps lower; best used as the *engine* feeding any hybrid above. → `docs/10`

## Repo map

| File | Contents |
|---|---|
| [`docs/01-strategy-and-timeline.md`](docs/01-strategy-and-timeline.md) | STS rules, timeline to Nov 5, ceiling analysis, strategic verdict |
| [`docs/02-sts-materials-landscape.md`](docs/02-sts-materials-landscape.md) | What places at STS — winners 2021–2026, lane-by-lane ceilings |
| [`docs/03-isef-reference.md`](docs/03-isef-reference.md) | ISEF materials analysis (secondary reference) |
| [`docs/04-thermal-materials.md`](docs/04-thermal-materials.md) | Thermal-management materials + where ML adds value |
| [`docs/05-rare-earth-ideas.md`](docs/05-rare-earth-ideas.md) | Rare-earth project ideation |
| [`docs/06-project-shortlist.md`](docs/06-project-shortlist.md) | Ranked candidate framings + decision gates |
| [`docs/07-batteries-energy-storage.md`](docs/07-batteries-energy-storage.md) | Batteries / energy storage / redox-flow deep-dive |
| [`docs/08-catalysis.md`](docs/08-catalysis.md) | Catalysis / electrocatalysis / photocatalysis deep-dive |
| [`docs/09-solar-perovskites-pv.md`](docs/09-solar-perovskites-pv.md) | Solar / perovskites / PV deep-dive |
| [`docs/10-computational-ml-materials.md`](docs/10-computational-ml-materials.md) | Computational / ML materials (methods/engine) deep-dive |
| [`docs/11-metamaterials-metasurfaces.md`](docs/11-metamaterials-metasurfaces.md) | Metamaterials / metasurfaces deep-dive |
| [`docs/12-catalysis-hea-execution-plan.md`](docs/12-catalysis-hea-execution-plan.md) | **Full execution plan for the lead candidate** (HEA OER electrocatalyst) |
| [`docs/13`](docs/13-round1-uma-results.md) · [`14`](docs/14-compute-log.md) · [`15`](docs/15-round1-melt-test-plan.md) | Round-1 UMA results · reproducible compute log · melt/test protocol |
| [`docs/16-project-overview.md`](docs/16-project-overview.md) | **Master dossier** — problem, glossary, novelty, every step + rationale (read first) |
| [`tasks/todo.md`](tasks/todo.md) | Open logistics gates + next actions |
| [`tasks/plan-catalysis-hea.md`](tasks/plan-catalysis-hea.md) | Week-by-week checkbox tracker for the HEA OER plan |

## Next decision

A **full execution plan for the lead candidate** (HEA OER electrocatalyst) is
drafted in [`docs/12`](docs/12-catalysis-hea-execution-plan.md) +
[`tasks/plan-catalysis-hea.md`](tasks/plan-catalysis-hea.md). To start executing,
answer the four logistics gates in [`tasks/todo.md`](tasks/todo.md) (instrument
access + booking lead time, FWM fabrication capability/turnaround, DFT
experience, STS sponsor) — **the FWM melt and potentiostat booking are the
critical path and must start in Week 0–1.**
