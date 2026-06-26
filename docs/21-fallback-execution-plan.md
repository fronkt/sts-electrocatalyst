# 21 — Execution Plan: Generative + DFT-Validated Discovery of Earth-Abundant HER Catalysts

**The project in one sentence:** Train a conditional generative model to propose *new*,
earth-abundant, platinum-group-free catalysts for the hydrogen-evolution reaction (HER),
screen them with a universal MLIP, **validate the best with first-principles DFT**, and
benchmark the predicted activity against an experimental dataset (OCx24) and known top
catalysts — a fully *computational* design→validate loop that needs **no wet lab**.

> Detailed spec for the best-bet fallback in [docs/20](20-fallback-bestbet-her-discovery.md)
> (which converged the [docs/19](19-computational-fallback.md) shortlist). This is the
> compute-only parachute to the main HEA-OER project ([docs/16](16-project-overview.md)); it
> **reuses the same UMA pipeline** (one-adsorbate swap) and only fully activates at the main
> project's Week-9 go/no-go — but the data + pilot can start in parallel now. Week-by-week
> checklist: [`../tasks/plan-her-discovery.md`](../tasks/plan-her-discovery.md).

---

## 1. Scientific framing

### The problem
Green hydrogen needs a cheap **cathode**. The HER cathode benchmark is **platinum** — scarce
and expensive. The field wants **earth-abundant, Pt-group-free** HER catalysts that approach Pt
activity. Activity is governed by a single, clean descriptor: the **hydrogen adsorption free
energy ΔG_H\***, whose optimum is **thermoneutral (ΔG_H\* ≈ 0)** — the Sabatier apex of the HER
volcano (Pt sits at ≈ −0.09 eV). One number per candidate makes HER the **fastest-to-validate**
catalytic reaction, which is exactly why it is the right target for a compute-only project.

### Why generative + DFT (the method)
Screening enumerated compositions explores only what you list. A **generative model** samples
*new* structures from a learned distribution, conditioned toward the target property — covering
chemistry the enumeration never wrote down. The honest risk is that a model proposes nonsense, so
the project is **validation-led**: every headline candidate is confirmed with the entrant's own
**DFT** (the same first-principles method the HER volcano was built on), and the pipeline is
benchmarked against **experiment** (OCx24) and **known catalysts** (positive control).

### Hypothesis (sharp, falsifiable)
> A structure+composition generative model, conditioned on ΔG_H\* ≈ 0, single-phase stability, and
> earth-abundance, will propose **≥1 novel, Pt-group-free composition** whose **DFT-computed ΔG_H\***
> lies within **±0.10 eV of thermoneutral**, while (a) reproducing known top HER catalysts as a
> positive control and (b) ranking generated/known catalysts in agreement with the experimental
> **OCx24** HER measurements (Spearman ρ reported with error bars).

### What "winning" looks like (define before starting)
| Tier | Concrete result |
|---|---|
| **Scholar floor** | A working generative→MLIP→DFT pipeline that rediscovers known HER catalysts (positive control), proposes novel candidates, and reports an honest predicted-vs-OCx24 correlation — *even if no novel candidate beats the apex.* |
| **Finalist stretch** | ≥1–2 **DFT-confirmed novel** Pt-free candidates at the volcano apex (|ΔG_H\*| < 0.10 eV), a **strong predicted-vs-experiment (OCx24) correlation**, beating random/heuristic baselines — and ideally one collaborator-measured experimental anchor. |

---

## 2. Locked scope decisions (kill ambiguity)

- **Reaction:** **HER only** (acidic + alkaline ΔG_H\* descriptor). *Not* OER/CO₂RR/ORR — one
  descriptor, fastest validation. (The HEA-OER pipeline is the surface-model donor, not the target.)
- **Descriptor / metric:** **ΔG_H\* = ΔE_H + 0.24 eV** (ZPE + entropy correction); primary target
  |ΔG_H\*| → 0. Secondary: exchange-current proxy, stability (energy above hull), abundance/cost.
- **Chemistry space:** **earth-abundant, Pt-group-free** — 3d/4d transition metals + p-block
  (phosphides, nitrides, carbides, chalcogenides, intermetallics). The abundance angle is the "so what."
- **Validation hierarchy:** **DFT (gold) > OCx24 experiment-benchmark > UMA screen > generator prior.**
- **Generator:** **conditional flow-matching** over composition+structure (reuse [[project_symmc_flow]]);
  **MatterGen fine-tune as the de-risk fallback** if from-scratch underperforms by the Week-2 gate.
- **Candidate budget:** generate ~10⁴–10⁵ → UMA-screen → ~10²–10³ ranked → **DFT-validate the top ~10–20**.
- **Framing lock:** **discovery-first, not method-first** — never pitched as "a new architecture"
  (the method lane is owned by MatterGen/CrystalFlow/Catalyst GFlowNet); the contribution is the
  *validated discovery + the experimental benchmark*.

---

## 3. The ML pipeline (the core intellectual contribution)

**(a) Data.**
- **OC20 / OC22** (`fairchem`) — \*H adsorption energies for the surrogate/eval reference.
- **Materials Project / OQMD / Alexandria** — structures + formation energy / energy-above-hull, to
  **train the generator** and gate stability.
- **OCx24** (Open Catalyst Experiments 2024) — **experimental HER** measurements = the benchmark
  (confirm license/access in Week 0).

**(b) Generator.** Conditional **flow-matching** over crystal composition+structure, conditioned on
(ΔG_H\* ≈ 0, energy-above-hull ↓, abundance/cost ↑) via classifier-free guidance. Reuses the entrant's
flow-matching CSP stack. **Fallback:** fine-tune open-weights **MatterGen** with a property head if the
from-scratch generator fails the Week-2 validity/stability gate.

**(c) Screen / evaluator.** **UMA** (`uma-s-1p1`) relaxes each generated structure + the \*H
adsorbate → ΔG_H\* via CHE referencing — **the existing HEA backend with a one-adsorbate swap**
(\*OH/\*O/\*OOH → \*H). The single-phase / synthesizability gate (`phase_stability.py`) carries over.

**(d) Validation & active learning.**
1. **Positive control** — the pipeline must rank known top HER catalysts correctly (Pt(111) ≈ −0.09 eV;
   MoS₂ edge; Ni₂P; CoP) before any novel claim is trusted.
2. **DFT (entrant-run VASP/QE)** on the top ~10–20 novel candidates → confirm ΔG_H\*; report **UMA-vs-DFT
   error** (bounds the OOD risk).
3. **OCx24 experimental benchmark** — predicted activity vs measured HER, **Spearman ρ** (no lab).
4. **Active-learning loop** — feed the DFT labels back to re-condition the generator for a round 2.

**Honest framing for judges:** the generator is a **proposer**, the MLIP a **fast filter**, and **DFT +
experiment are the truth** — the contribution is the *calibrated, validated discovery loop*, reported
with its correlation and failure modes.

### Compute & software stack
| Purpose | Tool |
|---|---|
| Generator | flow-matching (own stack) / **MatterGen** fine-tune fallback; PyTorch |
| Structures / adsorbates / slabs | `pymatgen`, `ASE` |
| MLIP screen | `fairchem` UMA `uma-s-1p1` (reuse HEA backend) |
| DFT validation | **VASP / Quantum ESPRESSO** (entrant-run) |
| Datasets | OC20/OC22 (`fairchem`), Materials Project API, OQMD, Alexandria, **OCx24** |
| Compute | Vast.ai GPU (generator training, ~GPU-weeks) + Purdue HPC / Vast for DFT |

---

## 4. The from-scratch vs. fine-tune pilot (first decision gate)

Before committing GPU-weeks, run a **1–2 week pilot**: (i) train a *small* from-scratch flow-matching
generator on a subset; (ii) stand up MatterGen fine-tuning in parallel. **Gate (end Week 2):** whichever
produces the higher **valid + stable** structure rate (validity by `pymatgen` + energy-above-hull <
0.1 eV/atom via MLIP) wins the full run. This converts the riskiest item (from-scratch convergence) into
a bounded, early, reversible decision — protecting the Oct deadline.

---

## 5. Validation & benchmarking (the placement engine)

- **Positive control:** rediscovery of known top HER catalysts (rank + ΔG_H\* sanity).
- **DFT matrix:** top novel candidates × {bulk relax, surface, \*H adsorption} in VASP/QE; consistent
  functional (e.g., RPBE for adsorption), k-point/convergence documented; UMA-vs-DFT parity plot.
- **Experiment benchmark:** predicted vs OCx24 measured HER → ρ + Pearson with error bars.
- **Baselines to beat:** random sampling from MP, the composition heuristic, and a published ΔG_H\*
  descriptor/volcano baseline.
- **Metrics:** DFT-confirmed hit-rate (|ΔG_H\*| < 0.10 eV), novelty fraction (not in training/known),
  structure validity + stability rate, ρ vs OCx24, hit cost/abundance.

---

## 6. Risk register & mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| **Crowded method lane** (MatterGen/GFlowNet) → "what's new?" | High | **Discovery-first framing**; novelty = validated novel hits + OCx24 benchmark + UMA relaxation (Catalyst GFlowNet's stated gaps). |
| From-scratch generator doesn't converge in time | Med | **MatterGen fine-tune fallback**, decided at the Week-2 pilot gate. |
| UMA out-of-distribution on novel chemistries | Med | DFT validation bounds it; report UMA-vs-DFT error; restrict to chemistries near OC20 support. |
| **OCx24 access / license** | Med | Confirm Week 0; fallback to a curated **literature** HER benchmark if blocked. |
| DFT throughput too slow | Low–Med | Single descriptor keeps it cheap (~1 adsorption energy/candidate); cap at top ~10–20; Purdue HPC. |
| Generated structures unsynthesizable | Med | Stability + synthesizability gate; report e-above-hull; flag as "predicted, pending synthesis." |
| Pure-compute Scholar ceiling | Med | Keep an **optional experimental anchor** open (one collaborator HER measurement). |
| Scope creep (add OER/CO₂RR) | High (self-inflicted) | **One reaction, one descriptor.** Locked §2. |

---

## 7. STS ~20-page paper outline (write as you go)

1. **Abstract** (½ pg)
2. **Introduction** — green H₂, HER, Pt scarcity, ΔG_H\* volcano, the generative-discovery gap, hypothesis. (~2.5 pg)
3. **Objectives & hypothesis** (½ pg)
4. **Methods** — data; generator + conditioning; UMA screen; DFT protocol; OCx24 benchmark; baselines. (~5 pg)
5. **Results** — positive control; generated candidates; **DFT-validated novel hits**; UMA-vs-DFT calibration; **predicted-vs-OCx24 correlation**; baseline comparison. (~6 pg, figure-heavy)
6. **Discussion** — why it works, model failure modes, abundance/cost angle, limitations. (~2.5 pg)
7. **Conclusion & future work** (½ pg)
8. **References.**

**Figures:** (F1) concept + HER volcano; (F2) pipeline schematic; (F3) generator validity/stability +
novelty; (F4) UMA-screened volcano with hits; (F5) **DFT parity + the validated novel candidates**;
(F6) **predicted-vs-OCx24 correlation**; (F7) baseline/ablation comparison.

---

## 8. Independence & sponsor notes

- **Yours (defend in interview):** the hypothesis, the generative-discovery design, the conditioning
  scheme, the UMA-screen + DFT-validation loop, the OCx24 benchmark, the analysis. **The entrant runs
  the DFT personally** — the gold-standard validation is the entrant's own work.
- **Acknowledged:** open datasets/models (OC20, MatterGen) and any HPC allocation — disclosed, standard.
- Reuses the entrant's **own** flow-matching + MLIP stack (skills, not a re-submitted paper — see
  [docs/19](19-computational-fallback.md) rule 2). Keep the dated git history as independence evidence.

---

## 9. Rough budget

| Item | Est. |
|---|---|
| Generator training (Vast.ai GPU, ~GPU-weeks) | ~$1,000–3,000 |
| UMA screening + DFT validation (Vast / Purdue HPC) | ~$200–800 (or in-kind HPC) |
| Datasets / models (OC20, MP, OQMD, Alexandria, OCx24, MatterGen) | open / free |
| Wet lab | **$0** (none required) |

---

## 10. Go / no-go checkpoints & timeline (≈12 weeks; compresses if activated at the main Week-9 fork)

- **Week 0–1 — Setup & data.** Env; pull OC20/OCx24/MP; **swap the UMA backend to \*H**; positive-control
  ΔG_H\* sanity (Pt, MoS₂). *Gate: pipeline reproduces known ΔG_H\* → proceed.*
- **Week 1–2 — Pilot.** Small from-scratch generator **vs** MatterGen fine-tune. *Gate (§4): pick the
  higher valid+stable generator → commit.*
- **Week 2–4 — Full generator training** (chosen path), conditioned on ΔG_H\*/stability/abundance.
- **Week 4–6 — Generate → UMA-screen → rank** → candidate pool; novelty filter. *Gate: ≥N novel
  near-apex candidates → proceed to DFT; else widen conditioning/space.*
- **Week 6–8 — DFT validation** (VASP/QE) on top ~10–20; UMA-vs-DFT calibration. *Gate: ≥1–2
  DFT-confirmed novel hits → Finalist path; else write the honest screening result (Scholar floor).*
- **Week 8–9 — OCx24 benchmark** (ρ) + positive-control writeup + baselines.
- **Week 9–11 — Active-learning round 2** (DFT labels → re-condition), finalize discoveries, ablations.
- **Week 11–13 — Figures, draft, polish.** **Early Oct: DATA FREEZE — write.**

## 11. Definition of done

A reproducible generative→MLIP→DFT HER pipeline that (1) passes the known-catalyst positive control,
(2) proposes novel Pt-free candidates with a documented novelty/stability rate, (3) **DFT-confirms ≥1**
at the volcano apex, (4) reports the **predicted-vs-OCx24** correlation with error bars and beats the
random/heuristic baselines — with a dated git history and an honest limitations section.
