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

## The control run settles it (job 20082656)

`probe/Cr_lit3/s0_OOH__1x1_yaw90_ns1__g1` -- same family, same size class, same
fixed-geometry `scf`, `nspin = 1` so the solution is unique -- returned:

    reference (Vast):  -1635.73491496 Ry
    measured  (Anvil): -1635.73491391 Ry
    delta = +1.050e-06 Ry  (+0.0143 meV)      PARITY_PASS

638 s wall, 10:40 elapsed, COMPLETED 0:0.

That is inside the pre-registered 1e-8 to 1e-6 Ry band, an order of magnitude
inside the proposed 1e-5 Ry tolerance, and **350x smaller than GATE-1's own 5 meV
science tolerance**. Anvil reproduces a banked Vast number to 0.014 meV when the
deck has one solution to reproduce.

The two effects are now separated by measurement, not by argument:

| source | delta | in meV | ratio |
|---|---|---|---|
| platform, Zen 2 -> Zen 3 (`ns1` deck) | 1.05e-06 Ry | 0.0143 | 1x |
| magnetic basin selection (`nspin=2` deck) | 6.09e-04 Ry | 8.2818 | **580x** |

The migration is sound. The spin-multistability is a property of the physics and
the input settings, not of the machine -- it would reproduce this way between any
two platforms, and between two runs on one platform.

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

---

# Addendum, same day — the panel. The platform question is answered 5/5.

**Job:** Anvil 20082912, array 1–5, `anvil/32_parity_panel.slurm`, table
`anvil/parity_panel.tsv`. Each task isolated in its own `$PROJECT/parity3/t<id>`
tree, so no task can see, overwrite, or race another, and no banked `.out` is in
reach.

## Why a panel replaced the single deck

Scoring the whole LIT-3 GATE-1 family against its own parents, before running
anything, showed the deck the first gate had picked was not a neutral choice:

| deck | parent E (Ry) | parent µ | child E (Ry) | child µ | Δ child−parent |
|---|---|---|---|---|---|
| `oosh__1x1_off_magm` | −1636.57116531 | 11.00 | −1636.57116516 | 11.00 | +0.002 meV |
| `s0_OOH__1x1_yaw270_magm` | −1636.56955293 | 11.00 | −1636.56955277 | 11.00 | +0.002 meV |
| `s0_OOH__1x1_yaw270_magp` | −1636.56975169 | 11.00 | −1636.56975161 | 11.00 | +0.001 meV |
| `oosh__1x1_off_magp` | −1636.57118655 | 11.00 | −1636.57057718 | **14.90** | **+8.29 meV** |
| `s0_OOH__1x1_yaw90_magm` | −1636.56961270 | 11.00 | −1636.56610153 | **14.71** | **+47.77 meV** |

`oosh__1x1_off_magp__g1` — the deck `30_parity.slurm` used as its reference — is
one of the two rows the GATE-1 review had already flagged BASIN_DRIFT. Its Vast
child sits 8.29 meV *above* its own Vast parent while every moment-preserving row
in the family reproduces to 0.002 meV. **The first gate measured that drift and
attributed it to the platform.**

## What the panel returned

All five decks are `nspin = 2`. All five reproduce their Vast counterpart:

| # | deck | class | Anvil E (Ry) | µ | Δ vs Vast child | verdict |
|---|---|---|---|---|---|---|
| 1 | `oosh__1x1_off_magm__g1` | AGREE | −1636.57116494 | 11.00 | +2.2e−7 Ry (+0.0030 meV) | PANEL_PASS |
| 2 | `s0_OOH__1x1_yaw270_magp__g1` | AGREE | −1636.56975117 | 11.00 | +4.4e−7 Ry (+0.0060 meV) | PANEL_PASS |
| 3 | `s0_OOH__1x1_yaw270_magm__g1` | AGREE | −1636.56955278 | 11.00 | −1.0e−8 Ry (−0.0001 meV) | PANEL_PASS |
| 4 | `s0_OOH__1x1_yaw90_magm__g1` | DRIFT | −1636.56610102 | 14.71 | +5.1e−7 Ry (+0.0069 meV) | reproduced |
| 5 | `oosh__1x1_off_magp__g1` | DRIFT | −1636.57057740 | 14.90 | −2.2e−7 Ry (−0.0030 meV) | reproduced |

**Largest deviation across the panel: 6.9e−7 Ry, 0.0069 meV — fourteen times
inside the proposed 1e−5 Ry tolerance, on spin-polarised decks.** Rows 4 and 5
land in the drifted basin their Vast counterparts landed in, to the same
precision. The platform reproduces Vast whichever basin the deck chooses.

## The finding this actually produced

Row 5 is the deck that failed the first gate. Two Anvil runs of that one file:

| | job 20082478 | job 20082912_5 |
|---|---|---|
| iteration-1 energy | −1638.41386991 | −1638.41386991 |
| iterations to converge | 56 | 49 |
| final total magnetisation | **11.00** | **14.90** |
| final total energy | −1636.57118588 | −1636.57057740 |

Same cluster, same binary, same deck, same NP=20 / −nk 4, **bit-identical at
iteration 1** — and two different self-consistent magnetic states 8.29 meV apart.

So the 8.28 meV was never a Vast-versus-Anvil quantity. It is a run-versus-run
quantity, and it appears on one machine. The likely mechanism is MPI collective
algorithm selection varying with rank placement under `--bind-to none`, which
changes floating-point summation order; the SCF then amplifies that into a
different basin. The seed is ~1e−8 Ry, the outcome is 1e−2 eV.

For the error ledger this strengthens class 2 rather than adding to it: magnetic
multistability is not merely a cross-machine hazard to be controlled by pinning a
platform. **It is not reproducible on a fixed platform.** Any protocol that banks
one run of a multistable deck as "the" energy of that state is banking a coin
flip, and the coin is worth 8–48 meV on these rows.

## Status of the gate

Against the tolerance written into `30_parity.slurm` before any Anvil job ran,
the platform question is **5/5 within 1e−5 Ry, worst case 6.9e−7**. Two
independent instruments now agree: the `nspin = 1` control (+0.0143 meV) and this
five-deck spin-polarised panel.

**Still the entrant's, and deliberately not done here:** creating
`$PROJECT/parity/PARITY_PASS`. `41_submit_wave.sh` refuses every wave until it
exists. The panel is evidence for that decision, not the decision.

## Revised open list

- ~~Which instrument is authoritative~~ — answered; both agree, and the deck that
  disagreed was measuring its own drift.
- **New, and load-bearing:** whether a `__g1` child that lands *above* its parent
  is admissible at all. Two of five in this family do, by 8.29 and 47.77 meV. A
  fixed-geometry re-run at the parent's own relaxed geometry landing above the
  parent is thermodynamically backwards; it is a diagnostic, not a datum.
  Proposed rule drafted in docs/47 §A8.3 for the entrant to re-author.
- Whether banked Cr numbers from multistable decks need re-running with the moment
  pinned, and how many decks campaign-wide are affected.
- Cost: this panel spent 30 SU. The bring-up total stands at 42 SU of 100,000.

---

**Gate opened (2026-08-22, later the same day).** `$PROJECT/parity/PARITY_PASS` was
created on the entrant's instruction after reviewing the panel above; the file itself
carries the two job ids and the worst-case deviation as its provenance. First wave through
the gate: the 19-deck Cr *OOH Hessian (block 1C), Anvil job 20085020.
