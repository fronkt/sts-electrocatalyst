# READOUT — Amendment 12b. CrO₂ bulk linear-response U under both projectors.

> **COUNTERSIGNED 2026-09-04.** Adopted at `2ea343f` before submission; job `20382206`
> submitted after; outputs read after that. The adoption line does not discharge this
> countersignature and did not.

## Verdict against what was registered

Amendment 12b registered **no threshold on the size of the split**. It registered a
*measurement*, to be reported with the other three cells as a 2×2 table, under the
inherited 0.2 eV q-mesh threshold (`docs/43:276`), plus one **named risk pre-stated**:
that nspin = 2 crossed with ortho-atomic had never been run, and non-convergence would
return **NO U** as a methods limit.

**The named risk did not fire.** `Convergence has not been reached` appears **0** times;
`JOB DONE` present in both the SCF and the hp.x output; Slurm exit `0:0`. The artifact
test was never load-bearing — the convergence string is what passed.

## The grid, closed

All values read from the `Hubbard_parameters.dat` files on disk, not from notes.

| | **atomic** | **ortho-atomic** | **split** |
|---|---|---|---|
| **TiO₂** (nspin = 1, closed-shell d⁰) | 4.2245 (q222) · 4.2251 (q333) · 4.2245 (q444) | 5.6688 (q222) · 5.6743 (q333) · 5.6741 (q444) | **+1.4443** (q222) · +1.4492 (q333) · +1.4496 (q444) |
| **CrO₂** (nspin = 2, magnetic 3d) | 6.1635 (q222) | **7.2677 (q222)** | **+1.1042** |

The projector-split-in-U observable goes **n = 1 → n = 2 in materials**, on the flagship
material, and **crosses the spin axis**. Same sign both times; same order of magnitude.
Relative to the atomic value the split is 34.2 % on TiO₂ and 17.9 % on CrO₂ — **smaller on
CrO₂, absolutely and relatively.** That is the honest direction to report it in.

Against the inherited 0.2 eV threshold, TiO₂'s q-mesh spread is 0.0006 eV (atomic) and
0.0055 eV (ortho): the split is **≈ 263× the q-mesh sensitivity**.

## The isolation is airtight, and it is airtight for a reason worth stating

Both SCF ground states run at `U Cr-3d 1.d-8`. At U → 0 the projector cannot touch the
ground state, and the outputs confirm it exactly:

| | total E (Ry) | total mag (μB) | abs mag (μB) | SCF iters |
|---|---|---|---|---|
| CrO₂ atomic | −517.92950441 | 4.00 | 4.68 | 19 |
| CrO₂ ortho | −517.92950441 | 4.00 | 4.68 | 19 |

**Identical to eight decimals.** The banked TiO₂ pair shows the same signature
(−405.93096624 Ry on both legs), so this is a property of the method, not a coincidence
on one material.

Consequences, both of which matter:

1. **BASIN_DRIFT cannot explain this.** The two legs are in the same magnetic basin because
   they are in the *same ground state*. The campaign's standing magnetic-metastability trap
   does not reach this observable.
2. **The entire 1.1042 eV comes from the projector acting on the response function χ**, with
   the density held byte-identical. There is no other channel open.

As-run decks differ in exactly the audited lines — SCF in prefix, outdir and the `HUBBARD`
card; hp deck in prefix and outdir. Nothing else.

## Cost — under the registered floor

23:34 wall at 20 cores = 28 280 CPU-seconds = **7.86 core-hours**. Amendment 12b registered
an ~11 SU floor and ~72 SU ceiling; the arm came in **below its own floor estimate**. The
estimate was conservative; recording that so the next cost model is not inflated by it.

## Limits, stated rather than left for a reader to find

- **CrO₂ q-mesh convergence is NOT measured.** Only q222 exists, on both legs. TiO₂'s
  flatness is not evidence about CrO₂. What is protected is the *split*: both legs sit at
  the same q-mesh, so the comparison is like-for-like even though the absolute values are
  q-unverified. Closing this is one more q333 pair.
- **n = 2 is still small.** Two materials is not a law. It is one more than one.
- **This is bulk, not slab.** The CrO₂ *slab* hp.x is banked as 4/4 non-converged at np = 18
  (`runs/hp_costmodel`). No slab U exists and none is claimed here.

## POST-HOC — flagged as post-hoc, not registered, and not to be quoted as a prediction

The following was **not** foreseen in Amendment 12b and was noticed only after the number
landed. It is recorded here so that it is dated as an interpretation, and it must not be
written up as though it had been registered.

A7.1 compares atomic against ortho-atomic **at a fixed U = 7.15 eV**. The ab-initio U is now
known to be projector-dependent: **6.1635 eV for atomic, 7.2677 eV for ortho**. So U = 7.15
sits ≈ 0.12 eV below ortho's own self-consistent U but ≈ 0.99 eV above atomic's.

This cuts in two directions and both belong in the report:

- **Against us.** The two legs of the headline are not equally close to their own ab-initio U.
  A reviewer will find this. Better that the ledger finds it first.
- **For us, and more strongly.** The natural rebuttal to A7.1 is *"compute U from first
  principles and the ambiguity disappears."* This measurement says it does not: the ab-initio
  route inherits the projector **twice** — once in determining U, once in the total energy —
  so the choice does not cancel, it compounds. That is the **non-cancellation** framing
  `docs/75` asked for when it found C6's thesis sentence to be a non sequitur.

**The second reading is not yet earned.** It is an argument, not a measurement, until the CHE
legs are run at *each projector's own* self-consistent U (atomic @ 6.1635, ortho @ 7.2677)
and η is compared. That is 8 SCFs, ≈ 46 SU by the u750 partner cost, and it would need its
own dated adoption before it runs. It is proposed, not started, and it carries the known
approximation that a bulk U is being applied to a slab.

## Artifacts banked

`runs/hp_cro2_ortho/` — 9 files, md5-verified identical on Anvil and locally
(rollup `6c92702c77304a622e49236548a3c4ff`). Five outputs and the two source decks are
committed.

The two decks that **actually executed** are the `.run.in` pair, and `.gitignore:39` excludes
them **on purpose**: the wrapper rewrites `outdir` and `pseudo_dir` into them at run time, so
committing them would bake machine paths back into the repo — the exact defect that made
`queue_hp.sh` unportable in the first place. Their md5s are carried in
`runs/m_hp_cro2_ortho.txt` instead, which is the record that matters.
