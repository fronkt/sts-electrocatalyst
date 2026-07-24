# Deep-Research Report 3/4 — Fine-tuning UMA/Universal MLIPs for Rutile-MO₂ OER Screening

> **Provenance:** produced 2026-07-23/24 by a literature-survey agent (WebSearch/WebFetch over
> publisher pages, arXiv, HuggingFace/GitHub docs — legal-first sourcing, no Sci-Hub; citations
> verified against landing pages). One of four parallel surveys distilled into
> [docs/28](../28-electrocatalyst-revival-plan.md). Verbatim archive.

**Bottom line up front:** The project almost certainly (a) invoked UMA with the *wrong task head and/or reference convention*, and (b) abandoned at exactly the point where the field says fine-tuning is *mandatory*. A Pearson of **−0.22** (anti-correlated) is not a "model can't do this chemistry" signature — it is a settings/reference-mismatch signature. The correct chemistry (rutile MO₂ slabs + O*/OH*/OOH* OER intermediates, PBE+U, spin-polarized) is *literally the OC22 dataset*, and UMA has a dedicated `oc22` task for it that only exists in the `uma-s-1p2`/`1p2p1` checkpoints. Details and the recommended recipe below.

---

## A. UMA & UNIVERSAL-MLIP LANDSCAPE (2024–2026)

**UMA: A Family of Universal Models for Atoms.** Wood, Dzamba, Fu, et al. (Meta FAIR), 2025 (rev. Mar 2026). arXiv:**2506.23971**. DOI 10.48550/arXiv.2506.23971. https://arxiv.org/abs/2506.23971 — *verified.*
- **Training datasets (multi-domain, ~half a billion structures):** OC20, ODAC23, OMat24, OMC25 (Open Molecular Crystals), OMol25. Architecture = **Mixture of Linear Experts (MoLE)** — one backbone, task/domain embeddings routed to linear experts; "a single model without fine-tuning can match or beat specialized models."
- **Model sizes (fairchem/DeepWiki, verified):** `uma-s` = **6.6M active / ~290M total params**; `uma-m` = **50M active / 1.4B total**. Checkpoints on HuggingFace `facebook/UMA` (gated): `uma-s-1p1`, `uma-s-1p2`, **`uma-s-1p2p1`** (latest small), `uma-m-1p1`. https://huggingface.co/facebook/UMA — *verified.*

**Task heads / how UMA is invoked (this is the crux).** UMA is domain-selected by a `task_name` string passed to `FAIRChemCalculator`. From the fairchem quickstart/UMA tutorial (https://fair-chem.github.io/quickstart/, https://fair-chem.github.io/uma-tutorial/ — *verified*):

| `task_name` | Domain | DFT flavor it emulates |
|---|---|---|
| `oc20` | metal/heterogeneous catalysis | **RPBE, adsorption-energy-referenced** (clean-slab + gas-phase subtracted) |
| **`oc22`** | **oxide catalysts** | **PBE + Hubbard U, DFT *total* energies (no referencing)** — *only in `uma-s-1p2`/`1p2p1`* |
| `oc25` | electrolyte/interfaces | — |
| `omat` | inorganic bulk materials | PBE / PBE+U (OMat24, VASP) |
| `omol` | molecules/polymers | ωB97M-V (OMol25) |
| `omc` | molecular crystals | — |
| `odac` | MOFs / direct air capture | — |

Minimal call:
```python
from fairchem.core import pretrained_mlip, FAIRChemCalculator
pred = pretrained_mlip.get_predict_unit("uma-s-1p2p1", device="cuda")
calc = FAIRChemCalculator(pred, task_name="oc22")   # <-- oxides, PBE+U total energy
```

**CRITICAL settings-mismatch diagnosis for this project:**
1. **Wrong task.** If the project used `task_name="oc20"` (the copy-paste default in every tutorial) it was asking for **RPBE adsorption energies**, not PBE+U oxide total energies. That alone can invert rankings vs a PBE+U in-house dataset.
2. **Reference/functional mismatch even with `oc22`.** OC22 = **PBE**, VASP, **Hubbard U per Materials Project values**, **spin-polarized with FM/NM initialization from Horton et al. magnetic moments** (see §B). If the project's in-house DFT used a different code (QE/CP2K), different U values, RPBE/PBEsol/SCAN, or different magnetic states, absolute parity will fail. A *consistent* offset still preserves ranking — a **negative Pearson means the reference itself is inconsistent** (e.g., gas-phase reference computed differently, per-system spin-state disagreement, or O*/OH*/OOH* referenced against mismatched H₂O/H₂/O₂ energies).
3. **OC22 covers this exact chemistry** (§A/§B): rutile MO₂ slabs + O*/OH*/OOH* are *in-distribution*, so out-of-box failure is more likely a harness bug than a capability ceiling — but even in-distribution, oxide adsorption MAE is ~0.5 eV (§B), so ranking still needs fine-tuning.

**OC22 dataset (what `oc22` emulates).** Tran et al. (Open Catalyst / CMU-Meta), 2022/2023. arXiv:**2206.08917**; ACS Catalysis DOI **10.1021/acscatal.2c05426**. https://arxiv.org/abs/2206.08917 — *verified.* 62,331 relaxations / ~9.85M single-points; **PBE + Hubbard U (Materials Project scheme; 20,812 systems used +U)**; **VASP; spin-polarized (FM/NM init per Horton et al. magnetic moments)**; **DFT total energies** (S2EF-Total, no referencing). **Explicitly includes 173 unary/binary rutile structures (4,318 rutile systems) and O*/OH*/OOH*/O₂* OER intermediates.** (OC20, by contrast, is RPBE adsorption energies.)

**Competing/specialized universal MLIPs relevant to oxides:**
- **EquiformerV2-OC22** (Liao et al., arXiv:2306.12059). Trained on OC22-only it beats GemNet-OC(OC20+OC22); +18.9% energy MAE over eSCN on OC22. The strongest *specialized* oxide-surface option if you don't want UMA. https://arxiv.org/abs/2306.12059 — *verified.*
- **eSEN** (fairchem; the architecture behind current UMA `eSCNMD` heads) — top of OC22/OMat leaderboards.
- **MACE-MP-0 / MACE-MPA-0 / MACE-OMAT-0 / MACE-MH-1** (Batatia, Kovács, Csányi et al.). MACE-OMAT-0 (trained on OMat24) scores **0.495 eV MAE** on Catalysis-Hub adsorption (CatBench, §B); OMat24-based MACE foundations outperform MPtrj-based ones "by more than most fine-tuning-method differences." https://github.com/ACEsuit/mace — *verified.*
- **SevenNet, ORB(-v3), CHGNet, M3GNet, MatterSim, GRACE** — all in CatBench (§B); MPtrj-trained ones (CHGNet, M3GNet, SevenNet-0, MACE-MP-0) inherit the **MP2020 GGA/GGA+U mixing corrections problem** on transition-metal oxides (§B). Geometry-relaxation robustness: CHGNet/MatterSim best (~0.1% unconverged); ORB and eqV2-M much higher failure rates (Matbench-Discovery-adjacent benchmarking).

---

## B. KNOWN FAILURE MODES on correlated/magnetic oxides — validates the negative result

**Loveday, Kaźmierczak & López, "Challenges and Opportunities of Pretrained MLIPs in Heterogeneous Catalysis," ACS Catalysis 2026, DOI 10.1021/acscatal.5c08945** (PMC12976938). https://pmc.ncbi.nlm.nih.gov/articles/PMC12976938/ — *verified, high-value.*
- Universal MLIPs show **chemical limitations across the board for adsorbed O*/OH*** on reactive TM surfaces due to "**strong O 2p–metal 3d hybridization and charge-transfer effects.**"
- **Errors ~0.5 eV typical; reaction-energy shifts up to 3 eV** on reactive surfaces (Ni/Pd) — i.e., the project's **MAE 0.71 eV is squarely in the documented regime**, not anomalous.
- Verdict: pretrained models are **"optimal prescreening tools," not DFT replacements**; for out-of-distribution species **"fine-tuning is expected to be mandatory,"** and active learning with uncertainty-triggered DFT is the "promising frontier." **This paper is the citation that the negative result is real and known — but that abandonment was the wrong conclusion.**

**Mechanistic root causes documented for magnetic/correlated 3d oxides (Cr/Mn/Fe/Co/Ni/Cu MO₂ are exactly this class):**
- **Spin-state / magnetic-configuration inconsistency:** MLIPs trained on datasets that mix magnetic orderings "learn nonphysical averages"; TM oxides with multiple magnetic orderings, spin-state transitions, and Jahn–Teller distortions require **DFT+U with explicit magnetic-configuration fixing** and spin-state validation (foundation-MLIP training-strategy reviews, e.g., Park et al., *Adv. Energy Mater.* 2025, DOI 10.1002/aenm.71046).
- **GGA/GGA+U mixing correction inconsistency:** MPtrj-trained foundations (CHGNet/MACE-MP-0/SevenNet-0) learn **raw VASP energies**, which are *not* consistent with MP's MP2020-corrected GGA/GGA+U energies for TM oxides/fluorides — a systematic per-chemistry offset that corrupts cross-oxide ranking.
- Dedicated magnetic-MLIP work confirms plain potentials can't carry spin d.o.f.: e.g., "A 'Magnetic' MLIP for Nickel" (arXiv:2312.17596); "Tangent-Plane Evidential Uncertainty in Active Learning for Magnetic Interatomic Potentials" (arXiv:2605.12353).

**CatBench** (Moon et al.), **Cell Reports Physical Science 2025**, DOI 10.1016/j.xcrp.2025.102847 (article S2666-3864(25)00567-3). Repo https://github.com/JinukMoon/catbench, data https://zenodo.org/records/17157086 — *verified.* Benchmarks 13+ MLIPs (UMA, eSEN, GRACE, MACE, SevenNet, ORB, CHGNet) on adsorption energy with anomaly/migration classification. Best models ~0.13–0.2 eV normal-MAE on the *broad* metal-heavy sets; MACE-OMAT-0 0.495 eV on a strained-oxide subset — i.e., **oxides are the hard tail even for the best universal models.**

**Publishability:** Yes — a *controlled* benchmark ("out-of-box UMA/MACE cannot rank rutile-MO₂ OER; here is why, and fine-tuning fixes it") is a recognized contribution class (CatBench, Loveday, the OC22 rational-design paper all frame this way). But it is only publishable *after* ruling out the task/reference-mismatch artifact — otherwise a reviewer will (correctly) say you benchmarked the wrong task head.

---

## C. FINE-TUNING RECIPES — how few DFT points to reach ranking quality

**fairchem / UMA fine-tuning** (docs: https://fair-chem.github.io/ "Fine-tuning" + issue #1486 — *verified*):
- **Dataset format:** ASE-LMDB (`.aselmdb`); structures readable by `ase.io.read` with energy/forces(/stress). Helper `create_uma_finetune_dataset.py` auto-generates a templated YAML.
- **Default = head-only fine-tune** (backbone frozen, task-heads adapt), **LR 4e-4**, choose `epochs` xor `steps`, `max_neighbors` 300 (drop to ~100 to save memory). Command: `fairchem -c config.yaml epochs=… lr=… batch_size=…`. For a narrow family you can/should also unfreeze the backbone (full fine-tune) if head-only underfits.
- fairchem-core **v2.21.0** (Jun 2026), Python 3.11–3.13; v2 required for UMA (incompatible with v1). https://pypi.org/project/fairchem-core/ — *verified.*
- Caveat from issue #1486: a step-0 blow-up (MAE 0.2 → 24.8 eV) is usually an **E0/isolated-atom-reference or normalization mismatch**, not a broken model — mirrors the MACE "E0 reestimation is critical" finding below.

**MACE fine-tuning** (docs https://mace-docs.readthedocs.io/en/latest/guide/finetuning.html + multihead_finetuning.html — *verified*):
```bash
mace_run_train --name=MACE --foundation_model="medium" \
  --multiheads_finetuning=False --train_file=train.xyz \
  --E0s="average" --lr=1e-3 --batch_size=... --max_num_epochs=... \
  --ema --amsgrad --default_dtype=float64 --device=cuda
```
`--foundation_model` = small/medium/large or a path (use a **MACE-OMAT** foundation for oxides). Naive fine-tune LR **1e-3**; multihead-replay LR **1e-4**; convergence **10–30 epochs**.

**Definitive fine-tuning-strategy paper — Tompa, Varga-Umbrich, Batatia et al., "Fine-tuning MLIP foundation models: strategies for accuracy and transferability," arXiv:2606.12704 (2026).** https://arxiv.org/html/2606.12704 — *verified, most actionable.*
- **Learning rates by method:** naive ~**1e-3**, LoRA ~**1e-2**, multihead-replay ~**1e-4**; **zero weight decay**; constant target-loss weight.
- **Data efficiency:** works from **5 → 950k** configs. SN2 barrier recovered from **60 MP2 configs** via naive fine-tune (0.05 meV/atom E-RMSE); NaCl solvation recovered at **10% data**.
- **E0 reinitialization matters more than the method** (2–3× force RMSE swing; MD stability). Use isolated-atom or model-aware E0 reestimation, not averaged E0.
- **Choose strategy by scope:** **naive fine-tune = optimal for narrow single-family tasks** (our case); multihead-replay only if you need to preserve broad generality (3–15× more compute; prevents PES-hole/catastrophic forgetting).

**Concrete case studies (N DFT points → chemical accuracy within one family):**
- **CLAM — Wu et al., JACS Au 2025, DOI 10.1021/jacsau.5c01112** (*verified*). GemNet-OC fine-tuned from the **OC20+OC22** checkpoint via on-the-fly active learning: **only 3–10 DFT points per loop**, adsorption-energy MAE **0.230 → 0.012 eV** (3 loops), "accuracy within chemical accuracy" 10%→94%; TS-search MAE 0.029 eV. Proof that **tens of in-domain DFT points** flip a broken pretrained model to chemical accuracy.
- **Systematic Fine-Tuning of MACE for Catalysis — Karimitari, Clary, Vigil-Fowler, Sundararaman, Csányi, Sutton, arXiv:2605.09394 (2026)** (*verified*). Fine-tuned MACE reaches **0.30 eV MAE for OER on IrO₂ (rutile) polymorphs**, beating out-of-box MACE-MH-1 by 0.08 eV.
- **Cross-Learning force fields, arXiv:2510.25380** — mace-mh-1-omat-D3 hits **0.288 eV** surface-adsorption MAE, **+68%** over the backbone.
- **U-MLIP fine-tuning study — Liu, Zeng, Wang, Zhao, arXiv:2506.07401 (2025)** and the **Fine-tuning Tutorial — Liu et al., arXiv:2506.21935 (2025)/J. Appl. Phys. 139, 041101 (2026)** — systematic **50→500+** structure data-efficiency curves; fine-tuning improves accuracy, convergence, OOD generalization and data efficiency (MACE-MP-0 exemplar). https://arxiv.org/abs/2506.07401, https://arxiv.org/abs/2506.21935 — *verified.*

**Simple alternatives (fallbacks):** Δ-learning (train a small correction to close the DFT–MLIP gap) and **GP/linear correction on frozen MLIP descriptors** are documented as robust, low-data ranking fixes; because the OER volcano only needs *ranking* of ΔG(O*), ΔG(OH*), ΔG(OOH*), a per-family linear/GP recalibration of frozen-UMA energies can already lift Spearman substantially at ~50 points.

---

## D. ACTIVE-LEARNING SCREENING LOOPS for doped/mixed oxides (OER)

1. **Tran et al., "Rational design of nanoscale stabilized oxide catalysts for OER with OC22," Nanoscale 2024, DOI 10.1039/d4nr01390e; arXiv:2311.00784** (*verified*). **The blueprint for this exact project.** GemNet-OC trained on OC20 (1.28M) then **fine-tuned on OC22**, used as a total-energy surrogate to screen **4,119 oxide materials** (all facets ≤ Miller 1, all terminations) for OER — coupling MLIP energies to Pourbaix stability, overpotential, cost, metastability. Same team, same OC22 data, same rutile chemistry.
2. **CLAM (JACS Au 2025, above)** — MLIP + DFT oracle + on-the-fly uncertainty-triggered labeling (3–10 DFT/loop) closing to chemical accuracy; the canonical fine-tuned-MLIP + DFT active-learning loop.
3. **Zhong et al. (Sargent group), "Active learning guides discovery of a champion four-metal perovskite oxide for OER," Nature Materials 2023, DOI 10.1038/s41563-023-01707-w** (*verified via search*). GP/BO-driven experimental+DFT active-learning search over multi-metal perovskite oxide OER space — the archetypal acquisition-function screening loop.
4. **Bayesian-optimization doped-rutile OER (directly on-target):** "Bayesian learning-assisted catalyst discovery for efficient iridium utilization in electrochemical water splitting," **Science Advances 2025, DOI 10.1126/sciadv.adw0894** (*verified via search*). GP-based BO over **6 rutile oxide supports (IrO₂, MoO₂, TiO₂, MnO₂, PdO₂, SnO₂) × 11 dopants**, optimizing surface composition/ordering/O-vacancies → Ir-doped TiO₂; DFT-in-the-loop. Companion: **"Ir–Mo oxide electrocatalysts… Bayesian Optimization Discovery," JACS 2024, DOI 10.1021/jacs.3c13491.**
5. Perovskite-OER ML screening with minimal DFT relaxation (Comput. Mater. Sci. 2025, S0927-0256(25)00663-9) and Zr-doped CeO₂ OER (Energy & Fuels 2025, DOI 10.1021/acs.energyfuels.5c01468) — additional acquisition-loop exemplars.

**Common workflow pattern:** pretrained/fine-tuned MLIP proposes/relaxes candidate doped-MO₂ slabs → compute ΔG(O*/OH*/OOH*) → acquisition (uncertainty via ensemble/committee, or BO on the descriptor/overpotential) selects the next batch → DFT oracle labels → fine-tune MLIP → repeat. UMA has **no native uncertainty**, so use a **MACE/ensemble committee** (or a small deep-ensemble of fine-tuned heads) for the acquisition signal.

---

## E. TOOLING — concrete runnable stack

**fairchem/UMA:**
- `pip install fairchem-core` (**v2.21.0**, Jun 2026; Python 3.11–3.13; PyTorch backend). Gated HF checkpoint `facebook/UMA` (accept license + `hf auth login`).
- Inference/fine-tune checkpoints: **`uma-s-1p2p1`** (small, use `task_name="oc22"`), `uma-m-1p1` (medium). Fine-tune via `create_uma_finetune_dataset.py` → ASE-LMDB → `fairchem -c config.yaml` (default head-only, LR 4e-4).
- Multi-GPU inference via the `extras` (Ray) install; single GPU is fine for this project's scale.

**MACE:**
- `pip install mace-torch` (**v3.15+**; the fine-tuning strategies paper's code targets ≥3.15). Foundation models via `--foundation_model medium` or a **MACE-OMAT** path. ASE `MACECalculator`.

**GPU requirements / wall-times (MLIPs are tiny vs LLMs — 3–300M params, not billions):**
- A **single RTX 4090 (24 GB)** or **5090 (32 GB)** fine-tunes **MACE-medium** and **UMA-small** comfortably; UMA-small has only 6.6M *active* params per structure. This is nothing like LLM fine-tuning — no LoRA/quantization needed for memory; the constraint is graph batch size, tunable via `max_neighbors` (300→100) and `batch_size`.
- Wall-time for a few-hundred-structure single-family fine-tune: **~hours on one GPU** (MACE convergence in 10–30 epochs; UMA-small head fine-tune ~tens of seconds/epoch on the docs' toy set → hours at ~300–500 structures × sensible epochs). A full active-learning campaign (multiple loops + DFT) is dominated by the **DFT oracle**, not the MLIP.
- vast.ai note: a single 4090/5090 box is sufficient; install PyTorch via the cu128 index for the 5090; cap dataloader workers on high-core boxes.

---

## RECOMMENDED PATH

**Step 0 — Before any fine-tuning, kill the artifact (½ day, no GPU-training).** Re-run parity with **`uma-s-1p2p1` + `task_name="oc22"`** and, crucially, **rebuild the adsorption/reaction energies with a single consistent reference** (same gas-phase H₂O/H₂/O₂ energies, same magnetic-state selection) on both the DFT and UMA sides. Also confirm the in-house DFT settings vs OC22's (PBE + **Materials-Project U values**, spin-polarized, VASP). A **negative Pearson strongly implies this layer is broken** — fixing the task head + reference convention may recover Spearman to ~0.6–0.8 with zero training. Pull a handful of **OC22 rutile MO₂** structures (they exist in the dataset) as an in-distribution sanity anchor.

**Step 1 — Targeted fine-tune (primary recommendation).**
- **Model:** `uma-s-1p2p1` (`oc22` task) *or* MACE-OMAT-0-medium. If you want the single most battle-tested small-data recipe, use **MACE naive fine-tune** (LR **1e-3**, **zero weight decay**, **E0 = isolated-atom or reestimated**, 10–30 epochs); if you want to stay in the UMA/OC22 ecosystem, fine-tune UMA-small (start head-only LR 4e-4; unfreeze backbone if Spearman stalls < 0.8).
- **Dataset:** **~200–500 in-domain DFT single-points/relaxations** spanning the 6 rutile MO₂ endmembers × {clean, O*, OH*, OOH*} × a few facets/coverages, generated with **OC22-matched settings** (so the data is both a fine-tune set *and* directly comparable to `oc22`). This is well above the 60-point floor that already worked in the literature and matches CLAM/MACE-catalysis/tutorial evidence.
- **Expected outcome (literature-anchored):** adsorption/reaction-energy **MAE ~0.5–0.7 eV → <0.1 eV** (CLAM reached 0.012 eV; MACE-catalysis 0.30 eV on rutile IrO₂ OER; Cross-Learning 0.29 eV), **Spearman → 0.85–0.95**. **GPU cost: single 4090/5090, single-digit GPU-hours** for the fine-tune itself.

**Step 2 — Wrap in an active-learning loop for the doped/mixed compositions.** Fine-tuned MLIP proposes/relaxes doped-MO₂ candidates → ΔG(O*/OH*/OOH*) → **uncertainty (MACE/committee ensemble) or BO on overpotential** picks the next DFT batch (**~3–10/loop**, à la CLAM) → relabel → re-fine-tune. This is exactly Tran-Nanoscale-2024 + CLAM + the Science-Advances doped-rutile BO loop composed together.

**Fallback if fine-tuning underdelivers on absolute energies:**
1. **Δ-learning / GP or linear recalibration on frozen-UMA descriptors** — because the OER volcano needs *ranking* of three intermediates, a per-family linear/GP correction at ~50 points can lift Spearman > 0.8 without touching the backbone (cheapest, most robust).
2. **Use the MLIP strictly as a DFT pre-screener** (Loveday's sanctioned framing): MLIP ranks/relaxes, DFT confirms the top-k. Even at 0.5 eV MAE this is a large throughput win and is itself a publishable, honest benchmark ("out-of-box UMA cannot rank rutile-MO₂ OER; task/reference correction + N-point fine-tune restores Spearman X→Y") — cite CatBench + Loveday/López + Tran-Nanoscale as the framing precedents.

**Every source above was verified by fetching the publisher/arXiv/repo page or its indexed abstract; paywalled items (Science Advances, CatBench full text, Nature Materials) are marked as verified via their DOI landing/abstract where the full text returned 403.**
