# 30 — QC audit of the archived DFT campaign, and the costed R1 plan

**Date:** 2026-07-31
**Status:** Audit COMPLETE (three defects found and fixed in code); R1 compute **BLOCKED on Frank**
— renting the box is the one step that spends money and it needs an explicit go.
**Follows:** [docs/29](29-r0-oc22-reparity.md) (R0 gate not met; A/B fork) ·
[docs/28](28-electrocatalyst-revival-plan.md) (R0–R4 plan)
**Code:** `src/dft/qe_qc.py` (new) · `src/dft/qe_frames.py` (new) ·
`src/dft/{setup_r1_box,queue_r1}.sh` (new) · `src/dft/qe_slab.py`,
`src/dft/parity_r0.py`, `src/hea_oer/surfaces_rutile.py` (fixed)
**Commit:** `1a3a77b` on `r0-catalysis-revival`

---

## 1. Why an audit came before more compute

docs/29 closed R0 with a negative result and handed Frank an A/B fork. Before spending
any of the **$6.52** of Vast.ai credit that remains, the archived DFT — the ground truth
that *every* number in docs/26 and docs/29 is measured against — was re-examined with
independent tooling. It did not survive intact.

The trigger was structural, not a hunch: `qe_slab.py::parse_qe_energy` accepted any
output containing `JOB DONE`, and docs/26 §4 already records that pw.x prints `JOB DONE`
after `convergence NOT achieved after N iterations: stopping`. That is a QC hole that had
been *patched by hand once* (eleven adslabs, 2026-07-05) but never closed in code, so
nothing prevented it recurring.

## 2. Finding 1 — η(NiO₂) = 1.751 V is retracted

`runs/Ni_slab/s0_O.out` and `s0_OH.out` both terminate on a failed SCF cycle and both
print `JOB DONE`. Neither was ever caught.

| | Ni `s0_O` | Ni `s0_OH` | (converged control: Ni `s0_OOH`) |
|---|---|---|---|
| completed ionic steps | 17 | 36 | 39 |
| SCF failures | 1 (terminal) | 1 (terminal) | 0 |
| `bfgs converged` | **no** | **no** | yes |
| free-atom fmax (eV/Å) | **0.363** | **0.673** | 0.056 |
| ΔE at the final step (eV) | **−0.0131** | **−0.0403** | −0.0006 |
| trend of that ΔE | **accelerating** | **accelerating** | flat |

The force target is 2×10⁻³ Ry/au = **0.051 eV/Å**, so the two adslabs finished 7× and 13×
over threshold. The energy diagnostic is the decisive one: a converged relaxation
plateaus below ~0.001 eV/step, and these two were still falling by 0.013 and 0.040 eV per
step **and speeding up** when the SCF died. They were nowhere near a minimum.

**The remediation was generated and never run.** `s0_O.in.restart` and `s0_OH.in.restart`
exist in `runs/Ni_slab/` (the docs/26 §4 cure, `mixing_beta = 0.1`,
`electron_maxstep = 500`). Both `.out` files begin from the **original** `.in` geometry,
matching it to 9×10⁻⁵ Å — i.e. the restarts were written, then forgotten.

`dft_eta.json` → `dft_eta.json.RETRACTED`, carrying a provenance block. Reinstating η(Ni)
costs exactly two relaxations, both already prepared.

### 2b. What the retraction does to the published conclusions

Both unconverged adslabs sit at geometries that are *too high* in energy, so ΔG_OH and
ΔG_O are biased high — and ΔG_OH more than ΔG_O, since `s0_OH` is the less-relaxed of the
two. Two consequences:

1. **η(Ni) = 1.751 V is a lower bound**, not a value. `ΔG_O − ΔG_OH = 2.981 eV` is biased
   low, and η is set by exactly that difference.
2. **docs/29 §4b finding #3 is withdrawn.** "NiO₂ breaks *OOH/*OH scaling by −0.51 eV"
   was computed as ΔG_OOH − ΔG_OH = 2.686 eV against a universal 3.2 ± 0.2. But ΔG_OOH
   comes from the one Ni adslab that *did* converge and ΔG_OH from the worst-converged
   job in the entire campaign, and an under-relaxed *OH biases that difference low —
   the precise direction of the claimed anomaly. Recovering ~0.5 eV on *OH puts NiO₂ back
   on the scaling line. It was filed as a hypothesis, and it dies as one.

### 2c. Restated R0 result, QC-gated

Re-running `parity_r0.py` with Ni excluded (`docs/figs/uma_oc22_parity_qc.{json,png}`):

| Variant | ρ (n=4, as published) | **ρ (n=3, QC-gated)** | Pearson r (n=3) | MAE (eV) |
|---|---|---|---|---|
| 1p1 / oc20 (docs/26 baseline) | +0.400 | −0.500 | −0.816 | 0.731 |
| 1p2 / oc20 | 0.000 | +0.500 | +0.111 | 0.654 |
| **1p2 / oc22 (the hypothesis)** | **−0.800** | **−1.000** | −0.946 | 0.698 |
| 1p2 / oc25 (exploratory) | +0.200 | +0.500 | +0.672 | 0.277 |

**The docs/29 verdict survives and sharpens**: across the three trustworthy endmembers the
oxide-specialised `oc22` head ranks rutile OER *perfectly backwards*. The anchors still
exonerate the pipeline (oc20/oc25 place IrO₂ at 0.52/0.57 V against a ~0.56 V literature
band). Nothing in R0's conclusion depended on Ni.

But n = 3 is the whole problem. `parity_r0.py` now refuses to quote a p-value below n = 5:
at n = 3 the only attainable |ρ| are 1.0 and 0.5, and the exact two-sided permutation p
for a *perfect* ordering is 1/3. At n = 4 it is 1/12; at n = 6 it is 1/360. **Statistical
power, not another head, is what R0 is now short of** — which is exactly what the
Ru/Ir anchors and the Ni rescue buy.

## 3. Finding 2 — the bottom-half constraint was decided by floating-point noise

`build_rutile110_hea` fixed the slab with `FixAtoms(mask = z < zmid)`,
`zmid = (z.min()+z.max())/2`. A symmetric rutile(110) slab places **four atoms exactly on
that mid-plane**, so their constraint was decided by a rounding difference at the 10⁻¹⁶
level. Every slab in the campaign has 7 atoms strictly above zmid; what differs is where
the mid-layer landed:

| run dir | free atoms | mid-layer (2 M + 2 O) |
|---|---|---|
| Cr, Mn, Fe, Cu, Ru | 11 | all 4 free |
| **Ir** | 10 | **1 metal fixed, its symmetry partner free** |
| **Co** | 8 | **3 fixed, 1 O free** |
| **Ni** | 7 | all 4 fixed |

Co and Ir are unambiguous bugs: two crystallographically equivalent atoms in the same
layer were given different constraints, breaking the slab's in-plane symmetry.

**Scope of the damage, stated honestly.** Within one metal the same constraint applies to
the clean slab and all three adslabs, so it largely cancels in ΔG. And UMA relaxed under
the *same* ASE constraint objects, so the docs/29 parity is still like-for-like per metal —
**the R0 verdict is not affected**. What it does contaminate is the *cross-metal*
comparison: Mn relaxes an 11-atom top region while Ni relaxes 7, and a more-constrained
slab cannot respond as much to adsorption. The η ordering and the volcano positions carry
that as a systematic, currently-unquantified bias.

Fixed by tolerancing the comparison (`z < zmid - tol`), which frees the whole mid-layer.
All six endmembers now build 11 free atoms. Archived inputs were **not** regenerated —
that would invalidate the converged runs; the legacy masks are recorded here instead.

## 4. Finding 3 — the anchors were unreproducible, unrunnable, and 4× overpriced

`runs/{Ru,Ir}_anchor/*.in` were written by a script that was never committed (`git log
--all` finds no anchor builder). Three separate problems, all now fixed:

- **Provenance.** Ru/Ir added to `RUTILE_AC` (Bolzan 1997 experimental constants) and to
  `ELEMENTS` (U = 0; the Materials Project assigns U only to Co/Cr/Fe/Mn/Mo/Ni/V/W, and
  Rossmeisl 2007 / Man 2011 ran these at plain GGA). `qe_slab.py build Ru` now reproduces
  the archived Ru inputs **byte-for-byte**; Ir differs by exactly the one tied constraint
  flag from §3 — a clean proof of both the reproducibility and the bug.
- **`eta` could not run.** The anchor manifests listed 4 jobs and no gas references, so
  `cmd_eta` aborted. Cr's H₂/H₂O inputs *and outputs* copied in (verified byte-identical
  across all five endmember directories — they contain only H and O at the same cutoffs,
  so they are metal-independent by construction) and the manifests extended.
- **Cost.** Two settings were pure waste. `nspin = 2` with every `starting_magnetization`
  at zero is a fixed point of the SCF — for non-magnetic RuO₂/IrO₂ it reproduces the
  `nspin = 1` answer at exactly twice the cost. And `nosym` belongs only on the clean slab
  (freezing the bottom half breaks the top–bottom mirror, so pw.x aborts in `checkallsym`
  without it), because an adsorbate lowers the symmetry by itself. The archive proves it:
  `runs/Cr_slab/s0_OH.in` carries no `nosym` and ran to `JOB DONE` at **15 k-points**,
  while `runs/Mn_slab/s0_O.in` carried it and paid for **36** — same physics, 2.4× the
  bill. `write_slab_input` now emits `nspin` only for magnetic species and `nosym` only
  for the clean slab. Together this is roughly a **4× cost reduction**, which is the
  difference between the anchors fitting in $6.52 and not.

Also: the builder emitted **CRLF** on Windows. `.gitattributes` already forced LF on
`*.sh` after a CRLF-in-tmux incident; `*.in` and `*.in.*` now get the same treatment, and
`qe_slab.py` writes with `newline="\n"` unconditionally. A stray `\r` inside a Fortran
namelist is one parse error away from wasting a rented box.

## 5. Finding 4 — the training set is real, but ASE cannot read it

docs/28 §5 calls the archived campaign "an in-domain training set already on disk". It is:
`src/dft/qe_frames.py` extracts **785 frames across 42 trajectories and 6 metals** (574
from primary outputs alone), each a complete (positions, cell, energy, forces) record at
one uniform level of theory.

Getting them out needed a new parser. `ase.io.read(..., format='espresso-out', index=':')`
(ASE 3.28) **fails on 33 of 44 archived slab outputs** — gas-phase runs parse fine, which
is why the failure was not obvious. The extractor is validated by two invariants that
would break under any frame misalignment: frame 0 reproduces the `.in` geometry exactly
(0.00 Å), and the fixed atoms move 0.00 Å across every frame of every trajectory. Its
final-frame force agrees with `qe_qc.py`'s independent read to 4 decimals.

One QC rule inverts here and must not be confused with §2: **unconverged geometries are
good training data** — an MLIP has to learn E(R) away from minima — and pw.x emits an
energy only for a *converged* SCF, so failed cycles contribute no frame at all. Only for η
does force-convergence matter.

## 6. What the design pass says the $6.52 should buy

Six parallel investigations (2026-07-31; QE protocol, training-data audit, fine-tune
recipe, R1 protocol, stability gate, Vast.ai market). Two independently reproduced the §3
constraint bug, and one independently reproduced the §2 Ni retraction — the findings above
are not single-source.

**Ranked by value per dollar:**

| # | Buy | Cost | What it delivers |
|---|---|---|---|
| 1 | **Ni rescue** — run the two prepared `.in.restart` jobs | ~$0.4 | n = 3 → 4. A perfect ordering goes from p = 1/3 to p = 1/12. |
| 2 | **Ru/Ir DFT anchors** — 8 patched jobs | ~$1.2 | The DFT tier has **no external validation today**. RuO₂(110) (lit. η 0.37–0.42 V) and IrO₂(110) (~0.56 V) through the identical stack tests it. Also n → 6. |
| 3 | **MACE-OMAT fine-tune**, LOMO CV | ~$1.9 | Turns the R0 negative into a before/after. |
| 4 | M2a — AFM β-MnO₂, fixed-geometry single points | $0.15 | The only physically real material in the set; supplies a measured spin-state spread. |
| 5 | M1a — U ladder Mn/Cr at fixed geometry | $0.55 | Answers "is the ranking a U artifact?" with a curve. |
| — | M4 surface-Pourbaix; Co/Cu OMC rescue | $14/metal | **No.** 2× the entire balance for one metal, at a demonstrated 0-for-4 base rate. |

Items 4 and 5 are cheap because they run as **fixed-geometry single points** on the
already-relaxed archived structures — 5–10% of the cost of re-relaxing.

**Free, no box, no key ($0):**
- **R2 stability gate.** pymatgen 2026.5.4 is installed locally and
  `pymatgen.analysis.pourbaix_diagram` ships no bundled thermodynamic data — which means
  it runs fully offline on hand-entered literature ΔG_f. Verified against the textbook
  β-MnO₂ diagram to <2 mV. The honest R2 result is a **phase-existence gate**: five of six
  endmembers fail before any energy is computed, and a ΔG_pbx number must **not** be
  printed next to FeO₂/CoO₂/NiO₂/CuO₂ — four of those phases do not exist, and a number
  for a nonexistent phase is fabrication. A free Materials Project key (one click) later
  adds ΔG_pbx for metastable CrO₂ and the Ru/Ir anchors, plus the multi-element HEA
  diagram that cannot be hand-entered.
- **Fine-tune Stage 0.** An E0-only recalibration control on CPU. If re-fitting per-element
  reference energies alone repairs the Mn < Fe < Cr ordering, that is a *sharper* result
  than any fine-tune ("the universal-MLIP failure here is a reference-energy failure") and
  costs nothing.

**Box selection.** Vast has no true CPU-only tier — every `num_gpus=0` listing is
storage-only. The best value by a wide margin is **machine 13822** (dual EPYC 9654, 192
physical Zen4 cores, 516 GB RAM, reliability 0.999, Norway): $0.8037/hr on-demand but
**$0.21/hr min-bid interruptible**, i.e. $0.0021 per effective-core-hour — simultaneously
the cheapest per core and the fastest wall-clock. All ten jobs (8 anchors + 2 Ni) fit in a
single concurrent wave at NP = 16 × NCONC = 10 = 160 ranks. Interruptible is safe here
because `queue_r1.sh` skips anything already carrying `JOB DONE`, so a preemption costs
only the in-flight jobs.

## 7. Pre-registered gate for the anchors (frozen before the run)

Recorded before any anchor number exists, in the docs/29 §2 style:

- **DFT tier validated** if η(RuO₂) and η(IrO₂) both land in **0.30–0.90 V** *and*
  η(Ru) < η(Ir).
- **η above ~1.2 V is not automatically a pipeline bug.** Pristine dry (110) cus sites at
  plain PBE are known to overestimate; at OER potentials the real cus row is O-covered
  (Hansen 2008, 10.1039/b803956a). That outcome gets written up as the resting-termination
  result (docs/28 §4 M4), not buried.
- **Acceptance per job**, machine-checked from `queue_r1.log`: `JOB_DONE=1` **and**
  `SCF_FAIL=0` **and** `qe_qc.py` verdict `TRUSTWORTHY`. Anything else is not an energy.
- **Ni reinstated** only if both restarts reach `bfgs converged` with free-atom fmax
  ≤ 0.051 eV/Å. If they do not, Ni stays retracted and the parity stays at n = 5.

## 8. Status and the one blocked step

Done, committed, pushed (`1a3a77b`), $0 spent:

- [x] Strict QC tooling; `parse_qe_energy` can no longer return a poisoned energy
- [x] η(NiO₂) retracted with provenance; R0 restated at n = 3 (verdict survives, sharpens)
- [x] Constraint float-tie fixed; anchors reproducible from committed code
- [x] Anchor inputs patched (~4× cheaper), gas refs and manifests wired for `eta`
- [x] 785-frame training set extracted and validated
- [x] Box scripts written; 10-job manifest built; input bundle staged

**Blocked on Frank — the only step that spends money:**

- [ ] Approve renting machine 13822 interruptible at a $0.30 bid (~$1.6 expected for all
      ten jobs; hard tripwire: destroy at $3.20 spend, which still protects the fine-tune)

Also owner-gated, both one click and $0:
- [ ] Free Materials Project API key (materialsproject.org → Dashboard → API key) to
      finish R2's quantitative half
- [ ] The A/B fork of docs/29 §7 is now effectively settled in favour of **A + B**: the
      benchmark negative is banked and QC-hardened, and B's training data is extracted and
      costed at ~$1.9. Confirm.
