# 22 — Multi-fidelity DFT calibration (UMA → QE → consensus melt)

The DFT *protocol* for the project's middle tier — the analogue of [docs/15](15-round1-melt-test-plan.md)
(the melt protocol) but for first-principles validation. It turns the project from a
single-model screen into a **multi-fidelity funnel** where each tier cross-validates the
one above it:

```
proposer            screen (cheap)          validate (mid, you run)     confirm (real)
heuristic prior  →  UMA (universal MLIP)  →  Quantum ESPRESSO (DFT)   →  melt + measure
(or generator)      ~thousands of comps      top ~3–5 + references       consensus pick (FWM/Purdue)
                    ──────── calibrate (Spearman ρ, parity) ──────►   ──── DFT-bless ────►
```

This doc is what a judge reads to confirm the DFT is real and the calibration is honest.
It is the **entrant-run validation** already in scope ([docs/16](16-project-overview.md) §6, §9).

---

## 1. Why this tier exists

UMA (`uma-s-1p1`) screens the whole composition space in seconds/composition, but its
OC20 head is metal-dominated, so oxide adsorption is partly **out-of-distribution** — its
*absolute* η is unphysical and only the *ranking* is trusted ([docs/13](13-round1-uma-results.md),
[docs/16](16-project-overview.md) §6). A first-principles tier closes that gap three ways:

1. **Calibrates UMA** — UMA-rank vs DFT-rank → Spearman ρ + a parity plot on a shared
   reference set. Converts "trust the ranking" into a *measured* agreement between the cheap
   universal model and DFT, **with the same method the OER scaling relations were built on.**
2. **DFT-blesses the melt list** — the compositions sent to FWM are the UMA↔DFT *consensus*,
   not UMA-only.
3. **De-risks the generative fallback for free** — [docs/20](20-fallback-bestbet-her-discovery.md)/[docs/21](21-fallback-execution-plan.md)
   reuse this exact UMA→DFT validation loop with a one-adsorbate swap, so this calibration is
   shared infrastructure, not duplicated work.

## 2. What DFT does and does **not** claim (the honest scope)

- **Does:** re-rank and validate **within the UMA-surfaced top tier**, and quantify the
  UMA↔DFT agreement on a shared reference set.
- **Does NOT:** independently search the whole composition space. DFT is far too expensive to
  scan thousands of HEAs; it only re-computes what UMA already surfaced. The legitimate claim
  is *"DFT validates / corrects the UMA ranking,"* **not** *"DFT searched and found a different
  global winner."* Overselling the latter is a known judging trap and is avoided in the paper.
- **Three honest outcomes, all reportable** (mirrors the experimental calibration in [docs/15](15-round1-melt-test-plan.md) §6):
  - UMA↔DFT agree (high ρ) → the cheap screen is validated; melt the consensus pick.
  - UMA↔DFT disagree → a real finding (UMA fails for these HEA oxides, *here*); melt the DFT
    pick and report the failure mode.
  - Partial → report ρ with its confidence interval; the calibration *is* the science.

## 3. Engine & compute

- **Engine: Quantum ESPRESSO** (open-source, plane-wave PW). *No VASP* (no license).
- **Compute home: Vast.ai**, primary = a **high-core CPU box** (QE over MPI is battle-tested;
  k-point + plane-wave parallelism scales cleanly; no GPU-build risk). **QE-GPU on Blackwell
  (sm_120) is a stretch only** — the NVHPC/CUDA-Fortran toolchain on the RTX 5090 is the same
  build-headache class as the `fairchem`/torch install ([feedback_vast_workflow], [docs/14](14-compute-log.md) §1);
  if used, go through a prebuilt container (e.g. NGC `quantum_espresso`) rather than compiling.
  For the small/medium cells boxed below, a many-core CPU box is comparable on cost and far
  lower on risk — start there.
- **Parallelism:** `mpirun -np <cores> pw.x -nk <#k-pools>`; pick `-nk` to divide the k-point
  set; reserve a few cores. Run in **tmux**; cache pseudopotentials + `outdir` on the
  persistent volume so SSH drops don't lose a relaxation.

## 4. DFT specification (boxed for the runway)

| Setting | Choice | Note |
|---|---|---|
| Code | Quantum ESPRESSO `pw.x` | PWscf, plane-wave/pseudopotential |
| Functional | **PBE + U** (Dudarev, spin-polarized) | the standard for 3d-TM oxide OER energetics |
| Hubbard U_eff (eV) | Cr 3.7 · Mn 3.9 · Fe 5.3 · Co 3.32 · Ni 6.2 · Cu 0 | Materials-Project–calibrated values (Jain 2011 / Wang 2006); document them |
| Pseudopotentials | **SSSP Efficiency (PBE)** | one consistent library across O + all 3d metals |
| ecutwfc / ecutrho | take the **max** recommended across the SSSP set (≈90 / 720 Ry typical with PAW/USPP) | converge η to <50 meV; record the convergence test |
| k-points (slab) | Γ-centered Monkhorst–Pack, **1 in the vacuum axis** (e.g. 3×3×1, converge to 4×4×1) | |
| Magnetism | spin-polarized; initialize FM + one AFM guess, relax | 3d-TM oxides; magnetism convergence is the usual pain point |
| Smearing | Marzari–Vanderbilt, ~0.01 Ry | metallic-character HEA surfaces |
| Slab | **rutile(110)**, matched to the UMA cell; bottom layers fixed, ≥15 Å vacuum, **dipole correction** | identical facet/site to the screen → apples-to-apples |
| Adsorbates | **\*OH, \*O, \*OOH** on the **cus site** | same intermediates as UMA |
| Free-energy ref | **CHE** vs gas-phase H₂O/H₂; add standard ZPE + TS gas-phase + adsorbate corrections | same referencing as the UMA pipeline; η = max(ΔG₁…₄)/e − 1.23 V |
| Convergence | E 1e-6 Ry · force 1e-3 Ry/Bohr | report it |

## 5. Structure targets (what actually gets DFT'd)

DFT cost is controlled by **what** you compute, not just how. Three sets, smallest first:

1. **Ordered oxide endmembers (anchor the parity plot, cheap):** rutile MO₂ for the
   constituent metals M ∈ {Cr, Mn, Fe, Co, Ni, Cu}. Small unit cells, fast. *(Note: several of
   these are non-ground-state rutiles — model surfaces, same as UMA used; flagged in
   [docs/16](16-project-overview.md) §8. They still anchor a like-for-like UMA↔DFT comparison.)*
2. **SQS / small ordered approximants of the top HEAs:** for each of the **top 3–5** consensus
   candidates, build a **special-quasirandom structure** on the cation sublattice at the target
   at.% in a tractable surface supercell (e.g. 2×2 or 3×2 rutile(110)), via `icet`/ATAT
   `mcsqs` or `pymatgen`'s SQS. **1–2 SQS cells per composition** — *not* full random HEA cells,
   *not* the whole sweep.
3. **The headline Cr-free pick (Fe₃₂Ni₁₇Co₃₄Mn₁₈) gets the most care:** it is melted first and
   is the robust UMA #1 across runs B and C — DFT it most thoroughly (more cus-site samples).

This keeps the entire tier to a **bounded GPU/CPU-week or two**, not an open-ended sink.

## 6. The calibration deliverable

For the shared reference set (endmembers + SQS picks) compute DFT η/descriptor and pair with
the UMA value already on file ([docs/14](14-compute-log.md) §3):

- **Parity plot:** UMA descriptor/η vs DFT descriptor/η; report **Spearman ρ and Pearson r**
  with the regression and its confidence interval.
- **Re-ranking table:** UMA rank vs DFT rank for the top tier; flag any swaps.
- **Failure-mode notes:** where (which chemistries/sites) UMA diverges most from DFT.

This parity is a **first-class figure** (new F-DFT, §7 of [docs/12](12-catalysis-hea-execution-plan.md))
and the bridge between the screen and the experiment: it is the *computational* analogue of the
predicted-vs-measured ρ in [docs/15](15-round1-melt-test-plan.md) §6.

## 7. The consensus melt list

The melt set in [docs/15](15-round1-melt-test-plan.md) §1 was UMA-selected. After this tier:

- **Confirmed** picks (UMA-high AND DFT-high) → melt with high confidence (priority for EC slots).
- **Demoted** picks (UMA-high but DFT-low) → flagged; keep only if the cost/abundance angle
  justifies it, and report the disagreement.
- **Round-2 proposals** (the active-learning melt) are chosen against the **DFT-calibrated**
  ranking, not UMA alone.

The headline **Fe₃₂Ni₁₇Co₃₄Mn₁₈** is melted first regardless (robust, Cr-free, [docs/15](15-round1-melt-test-plan.md) §7);
this tier confirms it and locks the *test priority* for the rest.

## 8. Go / no-go gate (end of the DFT tier)

- **Endmember parity established** (UMA↔DFT ρ on the reference oxides computed, with a CI) →
  proceed to SQS HEAs. *If the endmember parity is already poor → the screen needs the
  caveat sharpened, but the calibration is still the result; do not silently drop it.*
- **Top-tier re-ranking done** → lock the EC test priority; if DFT **overturns the headline
  pick**, investigate (re-check magnetism/convergence) before committing the round-2 melt.
- This gate sits **before the round-2 active-learning melt** and **informs** (does not block)
  the long-lead round-1 melt, which can proceed in parallel given FWM scheduling.

## 9. Definition of done (DFT tier)

A documented QE setup (functional/U/pseudos/cutoffs/k-points/convergence, all recorded for
reproduction), a UMA↔DFT **parity plot with ρ and a CI** over endmembers + the top SQS HEAs, a
UMA-vs-DFT **re-ranking table** for the top tier, an honest failure-mode paragraph, and a
**DFT-blessed consensus melt list** feeding [docs/15](15-round1-melt-test-plan.md).

## 10. Provenance

All inputs (`pw.x` `.in` files), pseudopotential versions, and `outdir` logs are committed to
the repo as the DFT analogue of [docs/14](14-compute-log.md) — dated, reproducible, entrant-run.
This is independence evidence ([docs/16](16-project-overview.md) §9): the entrant designs and runs
the DFT personally, on rented Vast.ai compute, with no VASP license and no external DFT service.
