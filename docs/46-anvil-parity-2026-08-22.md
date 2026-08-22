# Anvil parity gate: the Cr *OOH deck is spin-multistable

**Date:** 2026-08-22
**Jobs:** Anvil 20082478 (`30_parity.slurm`), 20082656 (`31_parity_any.slurm`)
**Status of this document:** measurement record. The threshold call and any
science conclusion are the entrant's (A7 authorship rule); what follows is what
the machine returned and the mechanism behind it.

## What was asked

Before any science-bearing work moves from Vast box 47662258 to Purdue Anvil,
re-run one already-banked deck and measure the difference. The deck chosen was
`probe/Cr_lit3/oosh__1x1_off_magp__g1`, the fixed-geometry GATE-1 child that
finished on Vast at 11:44:23Z on 2026-08-20.

The pre-registered expectation, written into `30_parity.slurm` before the run:
the conda builds are byte-identical, so any difference is microarchitecture
(Vast EPYC 7B12 / Zen 2 vs Anvil EPYC 7763 / Zen 3, different OpenBLAS kernels),
and should land at ~1e-8 to 1e-6 Ry. Proposed tolerance 1e-5 Ry.

## What came back

    reference (Vast):  -1636.57057718 Ry   totmag 14.90  absmag 21.28
    measured  (Anvil): -1636.57118588 Ry   totmag 11.00  absmag 21.30
    delta = -6.087e-04 Ry  (-8.2818 meV)      PARITY_FAIL over-threshold

Both runs converged legitimately -- `convergence has been achieved` in 51
iterations (Vast) and 56 (Anvil). Neither hit a cap, neither errored.

## The mechanism

The SCF trajectories are **bit-identical at the start** and separate later:

| quantity | Anvil | Vast | delta |
|---|---|---|---|
| iter 1 total energy | -1638.41386991 | -1638.41386986 | **5e-8 Ry** |
| iter 13 magnetization | 11.10 | 11.00 | first visible split |
| final total magnetization | 11.00 | 14.90 | different basin |
| final total energy | -1636.57118588 | -1636.57057718 | 8.28 meV |
| Fermi energy | 0.8043 eV | 0.8152 eV | |
| smearing contrib (-TS) | -0.00039019 Ry | -0.00052687 Ry | |

Iterations 1-12 agree to the digit (23.13, 19.10, 1.58, 9.83, 11.22, 11.22, ...).

So the platform difference **is** what was predicted: 5e-8 Ry at iteration 1,
squarely inside the 1e-8 to 1e-6 Ry band. The 8.28 meV is not that difference.
It is the SCF amplifying a 5e-8 Ry seed across ~12 iterations until the run
commits to a different self-consistent magnetic solution.

The deck is `nspin = 2` with `starting_magnetization(1) = 0.6` and no constraint
on the total moment, `smearing = 'mv'`, `degauss = 0.01`, `mixing_mode =
'local-TF'`, `mixing_beta = 0.3`. Under those settings this system has at least
two self-consistent magnetic states, and which one is reached is decided by
accumulated floating-point noise, not by the input.

## Two consequences

**1. The parity instrument was mis-specified, not the platform.** A
spin-multistable deck cannot measure platform parity -- it measures its own
multistability, and it will do so again on any pair of machines, any two runs.
`31_parity_any.slurm` re-asks the platform question of
`probe/Cr_lit3/s0_OOH__1x1_yaw90_ns1__g1`: same family, same size class, same
fixed-geometry `scf`, but `nspin = 1`, so the solution is unique.

**2. A banked number sits in a metastable state.** The Anvil solution is 8.28 meV
**lower** than the banked one. The banked `totmag 14.90` state is therefore not
the ground state of that deck; an accessible `totmag 11.00` state is lower. This
is independent corroboration of the effect already recorded for this system --
Cr's *OOH relaxation coming out 175 meV up in a metastable magnetic state
(docs/41). It is the same failure mode, found by a different route.

Note the size against the project's own science tolerance: GATE-1 works to 5 meV.
An 8.28 meV basin difference is **larger than the tolerance the campaign uses to
call two numbers the same**.

## What must not happen

The threshold must not be loosened to make this pass. A gate widened until the
measurement fits is precisely the unmeasured-numerical-change failure this
project exists to indict, and doing it here would be self-refuting.

## Incidental control

Iteration-1 energies agreeing to 5e-8 Ry is strong evidence that the staged
inputs and the refetched pseudopotentials are byte-equivalent to the box's. A
substituted UPF or an altered input shifts total energies by mRy or more, not by
5e-8 Ry. The pseudopotential recovery documented in `anvil/README.md` (SSSP
1.3.0, `ti_pbe_v1.4.uspp.F.UPF` md5 `88a00a6731bd790ddea75d31a80cb452`) is
independently confirmed by this run.

## Open, for the entrant

- The tolerance for platform parity (1e-5 Ry is a proposal only).
- Whether the Cr *OOH multistability warrants its own amendment, and whether any
  banked Cr number needs re-running with the magnetic state pinned.
- Whether other `nspin = 2` decks in the campaign share this multistability, and
  how that would be surveyed.
