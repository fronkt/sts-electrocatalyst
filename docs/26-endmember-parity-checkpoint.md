# 26 — Endmember Parity Checkpoint: UMA Cannot Rank Rutile-Oxide OER

> ## ⚠ READ THIS BEFORE QUOTING ANY NUMBER BELOW — amended 2026-08-06
>
> **Every ρ, r and MAE in this document was measured against a DFT reference now known
> to be defective**, and unlike docs/29 this document was never amended when the
> reference was repaired. Two of its four points were wrong: **Cr η 1.726 V** (a trapped
> `s0_O` at Cr–O 2.016 Å; the restart converged 1.396 eV lower → **0.491 V**) and
> **Ni η 1.751 V** (two unconverged adslabs plus a desorbed `*OOH`; retracted in
> docs/30 §2 → **1.084 V**). The headline "ρ = 0.40 (p = 0.60), r = −0.22, MAE 0.71 eV"
> is therefore **not UMA's performance** and must not be quoted as such.
>
> The same is true of `docs/figs/uma_dft_parity.json`, which still carries the retracted
> `dft_eta` values and now carries a `SUPERSEDED_BY` banner.
>
> **The verdict stands; the evidence for it changed.** Scored against the repaired n = 7
> tier, no UMA head reaches the ρ ≥ 0.8 gate: oc25 +0.357, oc22 +0.321, oc20 −0.036,
> and this document's own uma-s-1p1/oc20 at −0.300 (n = 5). See
> [`docs/38`](38-matched-protocol-parity.md) and `docs/figs/parity_matched.json` for the
> comparison on one footing, which is the only one that should be cited.

> **Final close-out of the catalysis compute campaign** (docs/12–23, parked per
> docs/24 §9). This is the keystone calibration deliverable promised in
> [docs/22](22-multifidelity-dft-calibration.md) §6: the UMA↔DFT parity across the
> rutile MO₂(110) endmembers, run to completion 2026-07-01 → 2026-07-13 on two
> rented Vast.ai CPU boxes. It supersedes every DFT η quoted earlier (docs/23 §6/§9
> and the original PR #15 headline are **retracted**, §4).

| | |
|---|---|
| **Question** | Does UMA (`uma-s-1p1`, OC20) *rank* rutile-oxide OER activity like DFT+U, even if its absolute energies are off? (If yes, the funnel's cheap tier is trustworthy for down-selection.) |
| **Answer** | **No.** 4-point Spearman ρ = 0.40 (p = 0.60), Pearson r = −0.22, MAE(η) = 0.71 eV. UMA's *worst* endmember (Mn, η_UMA 2.35 V) is DFT's *best* (η_DFT 0.89 V). |
| **Deliverable** | [`docs/figs/uma_dft_parity.png`](figs/uma_dft_parity.png) + [`.json`](figs/uma_dft_parity.json); per-element `runs/<M>_slab/dft_eta.json` |
| **Consequence** | The UMA-screening premise is dead for correlated oxides without fine-tuning (§7) — which independently validates the thermal pivot (docs/24). |

## 1. Result

Identical 18-atom MO₂(110) slab geometries, identical CHE referencing
(`referencing.delta_G` + `descriptors.oer_overpotential`), identical adsorbate
placement — **only the relaxer differs** (QE 7.5 PBE+U vs the UMA MLIP). Shared gas
refs H₂ −2.33323818 Ry / H₂O −44.04119711 Ry.

| Endmember | η_UMA (V) | η_DFT (V) | DFT ΔG_OH / ΔG_O / ΔG_OOH (eV) | DFT limiting step | Status |
|---|---|---|---|---|---|
| MnO₂ | 2.347 | **0.892** | 1.907 / 4.029 / 4.989 | 2 (\*OH→\*O) | converged |
| FeO₂ | 1.105 | 1.263 | 2.134 / 4.627 / 5.221 | 2 | converged |
| CrO₂ | 1.147 | 1.726 | 1.518 / 4.474 / 4.799 | 2 | converged |
| NiO₂ | 2.382 | 1.751 | 2.516 / 5.497 / 5.202 | 2 | converged |
| CoO₂ | 2.389 | — | — | — | **excluded** (§6) |
| CuO₂ | 2.418 | — | — | — | **excluded** (§6) |

**Statistics (n = 4):** Spearman ρ = 0.400 (p = 0.60) · Pearson r = −0.216 (p = 0.78)
· MAE = 0.706 eV · mean bias (UMA − DFT) = +0.337 eV.

Acceptance criterion for "converged" (§4): `JOB DONE` **and** zero
`convergence NOT achieved` SCF failures **and** final total force ≤ ~0.005 Ry/bohr
(norm over 19 atoms; per-component threshold 1e-3).

## 2. Reading the numbers

- **No usable ranking.** ρ = 0.40 at n = 4 is indistinguishable from chance
  (p = 0.60); the *linear* correlation is actually negative. A screen whose top
  pick order can invert the truth is worse than no screen.
- **The inversion is the story:** UMA puts Mn dead last (2.35 V) and Fe/Cr on the
  volcano apex; DFT+U says Mn is comfortably the most active endmember (0.89 V,
  a plausible value — MnOₓ *is* a known OER catalyst family) and pushes Cr/Ni to
  ~1.7 V. Both methods at least agree Fe is good.
- **Different limiting steps.** All four DFT points are limited by \*OH→\*O
  (step 2); UMA's CrO₂ point was limited by \*O→\*OOH (step 3). UMA is not making
  a correctable systematic offset — it reshapes the free-energy landscape.
- **Why:** `uma-s-1p1` is OC20-trained (metal-dominated, no Hubbard U). Correlated
  rutile oxides are out-of-distribution; the model over-binds intermediates by
  2–3.5 eV (docs/23 §6 first flagged this on CrO₂) and scrambles the ΔG spacings
  that set η.

## 3. Methods (what "same footing" means here)

- **DFT:** QE 7.5 `pw.x` (conda-forge), PBE+U (HUBBARD atomic card, MP-calibrated
  U: Cr 3.7 / Mn 3.9 / Fe 5.3 / Co 3.32 / Ni 6.2 / Cu —), SSSP-Efficiency pseudos,
  ecutwfc 80 / ecutrho 640 Ry (locked by the docs/23 §4 sweep), nspin = 2,
  MV smearing 0.01 Ry, `mixing_mode='local-TF'`, bottom slab half fixed, **no
  dipole correction (deliberately matching UMA)**, nk = 4 adslabs / 6 clean slabs.
- **UMA:** `uma-s-1p1` (OC20 task) relaxing the *same* six structures per element
  (`src/dft/uma_endmembers.py`), η via the same code path.
- **η:** CHE — ΔG₁…₄ from ΔE + fixed ZPE−TΔS corrections; η = max(ΔGᵢ)/e − 1.23 V
  (`src/dft/qe_slab.py eta`, `src/dft/parity_plot.py`).
- **Compute:** two Vast.ai CPU containers, each cgroup-capped at 15.36 vCPU
  (`nproc` lied: 64 and 192 — see docs/23 §8 and `tasks/lessons.md`); `NP=12,
  NCONC=1` via the throttled queue `src/dft/queue_dft.sh`.

## 4. The QC crisis and the retraction

The first full pass "completed" 20/20 jobs — and **12 of the 16 needed adslab
relaxations were silently unconverged**. `pw.x` prints `JOB DONE` and exits 0 even
when a mid-relax SCF hits `electron_maxstep` and BFGS stops on an unconverged
geometry; final forces ran 0.017–0.066 Ry/bohr (17–66× threshold). The η pipeline
accepted them.

**Retracted values** (geometry error, never to be quoted): Cr 2.03 V — the
original PR #15 headline and the docs/23 §6/§9 anchor — plus interim Mn 1.57 V and
Co 1.68 V. The corrected Cr point moved 2.03 → 1.726 V; corrected Mn moved
1.57 → 0.892 V (only ΔG_OOH changed, 6.83 → 4.99 eV — one bad geometry flipped the
element's entire story).

Fixes now baked into the tooling: the queue logs `SCF_FAIL` (count of
`convergence NOT achieved`) and `F_LAST` (final force) per job, and the η step
refuses nothing — **acceptance is a documented human check against §1's criterion**,
not a parser default.

## 5. The convergence-escalation ladder

What it actually took to converge 4 elements × 3 adsorbates of correlated-oxide
adslab relaxations (builders in `src/dft/`; every attempt's output archived as
`runs/<M>_slab/<job>.out.attempt*`):

| Attempt | Recipe | Seeded from | Outcome |
|---|---|---|---|
| 1 | production (Davidson, β = 0.3) | UMA-matched input geometry | 4/16 adslabs converged |
| 2 `build_restarts.py` | β = 0.1, maxstep 500 | last BFGS geometry of the dead run | +7 (incl. Fe both, Cu \*OOH, Cr \*OOH) |
| 3 `build_attempt3.py` | CG diagonalization | **min-force** geometry across all attempts | 0 — but diagnostic (§6); 31 h to fail on Co \*O |
| 4 `build_attempt4.py` | Davidson β = 0.05, ndim 16, maxstep 800 | min-force | +2 (Cr \*OH, Mn \*OOH) |
| 5 (`.in.lastshot`) | Davidson β = 0.03, ndim 20, maxstep 1500 | min-force | +1 (Ni \*OOH, 24.2 h, F = 0.0034) |

Two operational lessons that cost real wall-time are recorded in
`tasks/lessons.md` / the vast-workflow notes: seeding a restart from the *last*
BFGS proposal (often a pathological step right before an SCF explosion) dies on
SCF #1 — always mine the **minimum-force** geometry; and two mid-campaign account
pauses (Jul 10, 11) killed healthy runs whose salvage used the same min-force
protocol.

## 6. Exclusion protocol (Co, Cu)

**Pre-registered time-box (2026-07-12):** compute parity from whatever satisfies
the §1 acceptance criterion by the deadline; exclude the rest with the record
below. Decided *before* Ni's final attempt landed, so the exclusion rule could not
be tuned to the result.

- **CoO₂:** \*O and \*OOH failed **all four** solver recipes (0-for-4 each). The
  smoking gun for *why*: CG (attempt 3) re-evaluated a geometry Davidson had
  scored at F = 0.0098 and got **F = 0.050** — the two solvers converge to
  *different self-consistent spin states* on the same nuclear coordinates. Forces
  are not reproducible between electronic minima → BFGS cannot converge →
  **spin/charge multistability**, a property of the system, not a tuning failure.
- **CuO₂:** \*O oscillated and stalled at F = 0.020 over a 30 h relax; \*OH died
  on the first SCF twice under different recipes; \*OOH *did* converge (F = 0.003).
  2 of 3 adsorbates missing ⇒ no η.
- Degauss/smearing bumps were rejected as an escape hatch: changing the electronic
  temperature mid-chain breaks ΔG consistency across an element's four jobs.

This is itself a reportable observation: DFT+U SCF multistability in late-3d
rutile MO₂(110) adslabs is exactly the pathology the multi-fidelity literature
hand-waves past, and it consumed ~17 failed relaxation attempts across 4 recipes
here.

## 7. Implications

1. **For the catalysis funnel (docs/22):** the premise — UMA preserves ranking,
   DFT calibrates offset — is **falsified** for rutile oxides. Any revival needs
   (a) an MLIP fine-tuned on oxide+U data (the exact prescription docs/24 §3
   already adopts for thermal, with the PES-softening before/after figure), or
   (b) DFT-heavy screening, which the §5 ladder prices at ~1–5 box-days per
   composition — unaffordable for a 3000-candidate sweep.
2. **The calibration tier did its job.** The funnel's design put a parity gate
   *before* any melt; the gate caught a screen that would have sent the melt list
   in inverted order. Zero experimental effort was wasted on UMA's ranking.
3. **For the thermal project (docs/24):** independent, concrete evidence for the
   pivot's central design decision — never trust an un-fine-tuned foundation model
   as an oracle. The thermal κ oracle is first-principles CPA (κ_e) plus an
   explicitly fine-tuned NEP (κ_L) with the fine-tune benchmarked before use.
4. **For the STS narrative:** this is the docs/15 §6 "honest outcome" pattern in
   action — a rigorous, pre-registered negative result with full provenance
   (frozen protocol, archived failures, retraction trail). It reads as integrity,
   and it motivates the thermal project's architecture in one figure.

## 8. Campaign ledger

- **Wall time:** 2026-07-01 → 07-13 (~12.5 days), two 15.36-vCPU boxes
  (box A: Mn/Fe/Cu + Cr redo; box B: Co/Ni). Longest single job: Ni \*OOH,
  5 attempts, final one 24.2 h.
- **Incidents survived:** stdin-drain queue bug (9 h idle), a `pkill -f` friendly
  fire (2.5 h), two vast.ai account pauses (~12 h each + salvage), the §4 QC
  crisis. All fixes are committed, not tribal knowledge: `queue_dft.sh`
  (idempotent skip-guard, `</dev/null`, SCF_FAIL/F_LAST logging), the three
  restart builders, `tasks/lessons.md`.
- **Boxes:** both drained 2026-07-13. Box A (120.238.149.205) is repurposed for
  MuST KKR-CPA per docs/24 §9; box B (137.175.76.24) should be destroyed.

## 9. Provenance

- Final numbers: `runs/{Cr,Mn,Fe,Ni}_slab/dft_eta.json`; UMA side
  `runs/<M>_slab/uma_eta.json` (all six).
- Raw evidence: every element's final `.out` + the full `.out.attempt*` failure
  trail committed on this branch (`runs/<M>_slab/`); inputs `.in` + every
  escalation variant (`.in.restart/.attempt3/.attempt4/.resume/.lastshot`).
- Figure: `docs/figs/uma_dft_parity.png` (+ machine-readable `.json`), built by
  `python src/dft/parity_plot.py runs`.
- Key commits: `b3eecdd` (queue stdin fix), `da87f7e` (QC crisis + restarts),
  `abd78c7` (attempt 3), `70f5521` (attempt 4), `704f848` (final parity),
  `78396b5` (evidence archive).
