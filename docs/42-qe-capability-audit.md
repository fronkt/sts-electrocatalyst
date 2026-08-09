# 42 — What this Quantum ESPRESSO build can actually do

**Date:** 2026-08-09. **Box:** Vast instance 47025043, `/workspace/qe/env` (QE 7.5, conda-forge
via micromamba). **Why this document exists:** the campaign is about to plan a program around
techniques it has never run — first-principles Hubbard *U*, solvation, error-bar ensembles.
Every one of those is worthless if the binary cannot do it, and "we assumed it was available"
is exactly the kind of thing that burns a week in September. So each was tested against the
actual build, not against the QE manual.

Tests were run directly on the box with minimal H-atom inputs. Results are what pw.x/hp.x
printed, not what the documentation promises.

## Verdict table

| capability | needed for | status | evidence |
|---|---|---|---|
| **hp.x** — DFPT linear-response Hubbard *U* | replacing the *chosen* U that triggered P7 | **AVAILABLE** | `/workspace/qe/env/bin/hp.x`; runs and prints `Program HP v.7.5` |
| **BEEF-vdW** — ensemble error bars on η | a calibrated uncertainty instead of a point value | **AVAILABLE** | `Initializing libbeef V0.1.2 with the BEEF-vdW functional.` / `Exchange-correlation= BEEF-VDW` |
| **ph.x** — phonons / vibrational free energy | ZPE and entropy corrections computed rather than borrowed | **AVAILABLE** | `/workspace/qe/env/bin/ph.x` |
| **ESM** — effective screening medium | charged slabs, constant-potential electrochemistry | **AVAILABLE** | `assume_isolated='esm'`, `esm_bc='bc1'` parse and run without error |
| **3D-RISM** — molecular solvation | implicit solvent without patching Environ in | **COMPILED, NEEDS DATA** | `trism=.true.` and the `&RISM` namelist parse; `pprism.x` present; fails only in `read_solvents` because **no `.MOL` solvent files ship with the conda package** (`find … -iname '*.MOL'` → 0). Fetch them from the QE source tree. |
| **libxc** | alternative functionals beyond the built-ins | **NOT LINKED** | 0 libxc libraries in `env/lib`. Note this did *not* block BEEF-vdW, which comes from a separately bundled `libbeef`. |
| **Environ** — SCCS continuum solvation | the other implicit-solvation route | **NOT INSTALLED** | would require patching and rebuilding QE; RISM/ESM likely make it unnecessary |

## What this means for the program

**Every one of the campaign's seven known foundational weaknesses has a QE-native route in
the build already installed.** That was not a given — hp.x and BEEF-vdW in particular are the
two that would have been hardest to work around, and both are present. Specifically:

- **The U problem (docs/41 P7, the withdrawn headline) is fixable in-house.** `hp.x` turns U
  from a chosen parameter into a computed one. This is the single most valuable thing the
  build makes possible, because P7 is what killed the headline: η(Cr) moved 1.122 V across U,
  so no activity claim survives while U is an assumption.
- **A calibrated error bar on η is reachable at near-zero marginal cost.** BEEF-vdW returns an
  ensemble of exchange-correlation parameterisations per single point, which is the standard
  route to a per-structure uncertainty. Combined with the observation that η is a positively
  biased estimator (docs/41 §2d), this is the difference between "our η is 0.79 V" and
  "our η is 0.79 ± X V, and here is why the bias is positive."
- **Solvation does not require Environ.** RISM plus ESM covers both the solvent and the
  charged-electrode axes. The only gap is the solvent `.MOL` parameter files, which are data,
  not code, and come from the QE source distribution.

## Caveats on these results

- Availability is not competence. hp.x on a *magnetic 3d oxide slab* is materially harder than
  on the bulk insulators in its tutorials — q-mesh convergence, choice of perturbed atom, and
  whether U should be computed for the bulk, the slab, or per-site (surface vs subsurface metal
  atoms are not equivalent) are all open and are being researched separately.
- BEEF-vdW ensembles give the **exchange-correlation** contribution to the error only. They say
  nothing about the geometry errors this campaign has actually been bitten by — the symmetry
  trap and the magnetic solution multiplicity are not XC errors and will not appear in the
  spread.
- The ESM and RISM tests confirm the input parses and the code path initialises. Neither has
  been run to a converged result on a real slab.
- `strings` and `file` are not installed on this box; an earlier negative result for RISM came
  from `strings` silently failing, not from missing support. Capability claims here rest on
  running the binary, which is the reason to distrust the shortcut.
