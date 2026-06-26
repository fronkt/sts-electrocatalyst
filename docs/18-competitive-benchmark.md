# 18 — Competitive benchmark: this project vs. real STS precedents

How the HEA-OER project ([docs/16](16-project-overview.md)) stacks up against actual
Regeneron STS Finalist/Scholar projects, on **complexity, scope, and stage**. Builds on
the landscape analysis ([docs/02](02-sts-materials-landscape.md)) with deep-dived specifics
(2026-06-26 web research; sources at the end). STS does **not** publish the 20-page reports,
so "specifics" = public abstracts, society/news writeups, posters, and any journal/arXiv
version the student later released.

## 1. The comparator set (closest analogs, with specifics)

| Project (year, placement) | Type | What they actually did | Stage at submission |
|---|---|---|---|
| **Sophie D'Halleweyn** (2024, **Finalist**) | ML + catalysis (*characterization*) | A multi-task ML model that reads **X-ray absorption spectra (XANES/EXAFS)** to output Pd-nanoparticle structure — coordination numbers, interatomic distances, H-fraction — for catalyst optimization. Mentor: A. Frenkel + postdoc, Stony Brook. | ML method built **and applied to real spectral data**. No fabrication; ML *characterizes*, doesn't design→make. |
| **Amy Guan** (2021, **Finalist**) | DFT catalysis | **DFT** optimization of metal + ligand effects for a **methane-activation** catalyst. Mentor: T. Cundari, UNT. | Pure computation; no synthesis. |
| **Evan Kim — ScGAN** (2023, **Finalist**) | ML generative discovery | A **GAN** trained on OQMD, transfer-learned on SuperCon, generates hypothetical superconductors; ~70 % pass a separate **classifier**, 99 % novel, ~23× hit-rate vs. manual search. **Published** (arXiv 2209.03444; peer-reviewed). | Pure computation, **new method**, journal-published. Validation is *in-silico* (a classifier), not experimental. |
| **Aiden Sanxhaku** (2025, **Finalist**) | Experimental electrochemistry | **Iron alkaline redox-flow battery**: metal-additive "cation effect" on electron-transfer kinetics — power density up, **resistance down ~115 %**. $25k winner. | **Full experimental loop**; the core project has **no ML**. |
| **Jana Aldosari** (2026, **Finalist**) | Experimental device | **WO₃/GQDs/MXene photoanode** for photoelectrochemical **water splitting** (H₂). | Device **fabricated + tested**; experimental. |
| **Brendan Hirshorn** (2026, **Scholar**) | ML alloy inverse design | "Explainable inverse design of **Al and Co alloys** through hierarchical generative modeling." | **Computational-only — no fabrication. → Scholar.** |
| **Anthony Low** (2026, **Scholar**) | Thermal materials | 0D/2D phase-change composite for HPC thermal management. | Experimental synthesis; thermal lane historically **Scholar-capped**. |

## 2. Complexity — how the *methods* compare

**Your computational pipeline is at or above a typical STS computational Finalist in
sophistication, and more physically rigorous than most:**
- A **universal MLIP foundation model** (Meta UMA) for adsorption energies, vs. the usual
  single bespoke GAN (Kim) or regressor/VAE (Hirshorn-class) or hand-run DFT (Guan).
- **Physically-grounded, multi-cus-site oxide surface** thermodynamics (rutile(110), CHE
  4-step OER, active-site *distribution*) — closer to publishable computational catalysis than
  a composition-only descriptor.
- Two things none of the comparators have: a **ρ self-calibration** (ML-vs-ML now, ML-vs-experiment
  later) and a **documented sampling-bias self-correction** (the heuristic→diverse fix). That kind
  of "I found my own pipeline's blind spot and fixed it on the record" is exactly the rigor judges
  reward.

**The honest caveat:** your novelty is the **integrated, calibrated loop**, *not a new ML
architecture*. ScGAN and the inverse-design projects built **bespoke generative models** — a
"new method" story. You lean on **off-the-shelf** models (UMA, pymatgen). So a *purely
computational* version of your project would have a **weaker method-novelty hook** than ScGAN.
Your differentiation has to come from the **experiment + correlation**, not the model.

## 3. Scope — broader than any single comparator

Each comparator did **one** of {compute, fabricate, measure}; the experimental Finalists
(Sanxhaku, Aldosari) measured but did **not** ML-design, and the ML Finalists (Kim, Guan,
D'Halleweyn) never fabricated a designed material. **Your intended scope spans all three in a
closed loop** — ML screen → **self-melt the alloy by hand at FWM** → measure η vs. NiFe-LDH →
**ML-vs-experiment correlation** → active-learning round 2. The **self-fabrication** (you run the
melts, not a vendor) is an independence edge essentially none of these had. If executed, this is a
*larger* and more complete project than any single row above.

## 4. Stage — this is the gap, and it's the whole ballgame

At submission, every Finalist above had **completed their core result**: Sanxhaku had the
−115 % resistance data; Kim had the published, classifier-validated GAN; Aldosari had a working
photoanode; even the pure-compute Finalists (Guan, D'Halleweyn) had a *finished* computational
deliverable applied to real systems.

**You are at "computational prediction complete, zero experimental data."** The half that
actually separates Finalist from Scholar — the **measured result and the ML-vs-experiment
correlation** — is entirely ahead of you, on a ~3.5-month clock, first melt ~1 week out.

> **Hirshorn (2026) is the precise warning shot:** ML alloy inverse design, no fabrication →
> **Scholar.** A sophisticated ML screening study *without* the experiment is, on the STS
> historical record, a Scholar-tier result. Your computational work alone, however rigorous,
> most resembles Hirshorn's tier — **not** the Finalists'.

## 5. Verdict

- **Ceiling: Finalist-credible — conditional on the wet-lab loop landing.** The computational
  component is already competitive with Finalist-level work in rigor; the **differentiator and the
  risk are the same thing — the experiment**. The ML-vs-experiment correlation is a contribution
  **none of these seven comparators reported**, and it's publishable even as a calibrated *negative*
  result (model wrong but honestly characterized) — that's your Scholar floor with a Finalist upside.
- **If the experiment slips** (potentiostat unbooked, melts multi-phase, time runs out), you land
  in the **Hirshorn tier (Scholar)**: an elegant screening pipeline without the validation that
  makes it land at the top.
- **Where you are genuinely ahead of the field:** (1) closed design→**self-fabricate**→measure loop;
  (2) physically-grounded foundation-MLIP screening with a calibration metric; (3) the documented
  self-correction; (4) you personally run **both** the DFT and the melting — an independence story
  D'Halleweyn/Guan/Kim (mentor-lab-dependent) can't fully claim.
- **Where you're behind / exposed:** (1) **0 % experimental** vs. comparators' finished results;
  (2) **no bespoke-model novelty** — don't pitch this as "a new ML method," pitch it as "a
  calibrated, self-fabricated discovery loop"; (3) **HEA-OER is a crowded *professional* topic**
  (MoZn, AlFeNiCoMo, CoFeNiCr, FeCoNiRu HEAs are all published OER catalysts), so the catalyst
  *class* isn't novel — the **integrated method and the abundant/Cr-free angle** are.

### Priorities that follow directly
1. **Book the potentiostat now** — it is the single gate between you and the Finalist-tier half.
2. **Get ≥3 melts cast + EDS-confirmed single-phase fast** — bank the structural result early.
3. **Protect the ML-vs-experiment correlation** — it's the one thing no comparator has; freeze the
   predictions (done, [docs/15](15-round1-melt-test-plan.md) §2) and report ρ with error bars.
4. **Reframe novelty** away from "new model" → "first calibrated, self-fabricated ML→make→measure
   loop for earth-abundant HEA OER," with the entrant running both the simulation and the metallurgy.

---

### Sources
- 2024 Finalist — Sophie D'Halleweyn: <https://www.societyforscience.org/regeneron-sts/2024-student-finalists/sophie-dhalleweyn/> · Stony Brook mentor writeup: <https://news.stonybrook.edu/university/eight-sbu-faculty-mentored-regeneron-science-competition-scholars/>
- 2021 Finalist — Amy Guan: <https://www.societyforscience.org/regeneron-sts/2021-finalists/>
- 2023 Finalist — Evan Kim, ScGAN: <https://arxiv.org/abs/2209.03444> · <https://pubmed.ncbi.nlm.nih.gov/37757835/>
- 2025 Finalist — Aiden Sanxhaku: <https://www.societyforscience.org/regeneron-sts/2025-student-finalists/aiden-sanxhaku/> · poster: <https://sspcdn.blob.core.windows.net/files/Documents/SEP/STS/2025/posters/2025_STS_Poster_Sanxhaku_Aiden.pdf>
- 2026 Finalists/Scholars (Aldosari, Hirshorn, Low): <https://www.societyforscience.org/regeneron-sts/2026-finalists/> · <https://www.societyforscience.org/regeneron-sts/2026-scholars/>
- HEA-OER professional context: <https://www.science.org/doi/10.1126/sciadv.adq6758> · <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11206725/> (CoFeNiCr HEA OER) · <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10190517/> (FeCoNiRu self-reconstruction)
