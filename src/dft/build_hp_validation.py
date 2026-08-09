#!/usr/bin/env python3
"""Block 1B: decide whether hp.x can do anything useful on this chemistry, and what it costs.

Why this exists
---------------
docs/42 established that `hp.x` EXISTS in this build and prints `Program HP v.7.5`. Its own
caveat is the whole reason for this file: *"availability is not competence -- hp.x on a
magnetic 3d oxide slab is materially harder than on the bulk insulators in its tutorials."*
Risk R2 in `tasks/plan-maximal-rigor.md` is that hp.x never converges here and the entire S2
contribution -- first-principles Hubbard parameters, the one thing that answers P7 -- collapses
to a bracket. P7 is what killed the headline (eta(Cr) moves 1.122 V across U against a
pre-registered 0.15 V threshold), so this is not a refinement, it is the head of a
contribution.

Two things have to be settled before September, and they are settled by different artifacts:

  1. **Does the answer come out right?** -> the bulk validation, `runs/hp_tio2/`: the
     closed-shell TiO2 target AND the magnetic, metallic CrO2 arm that exercises the branch
     blocks 2C/3Y actually take (docs/43 s4-A.3).
  2. **What does the answer cost?**      -> the counting + timing decks, `runs/hp_costmodel/`.

Neither is a matter of opinion, so both are pre-registered in docs/43 before they run.

THE PRE-REGISTRATION IS docs/43, AND ONLY docs/43
--------------------------------------------------
This file registers **nothing**. It builds decks that let docs/43's criteria be evaluated;
it does not state, restate, widen, tighten or reinterpret them. The gate is
**docs/43 s4 (P15)** as amended by **docs/43 AMENDMENT 1 s4-A** (commit `0244f4e`, written
before any block-1B job ran). Read it there. The five things s4-A settled, listed here as
pointers so nobody has to guess which document is current -- NOT as a second copy of the rule:

  * s4-A.1  the external window on U(Ti-3d, atomic) is UNCHANGED. The 2026-08-09 build round
            proposed widening it with no physics reason; that widening is REJECTED. The
            numbers are deliberately not repeated here -- read them from docs/43, because a
            copy that goes stale is how this file would end up contradicting the rule it is
            supposed to be executing.
  * s4-A.2  the perturbation-amplitude criterion is WITHDRAWN, with its reason (hp.x is
            DFPT; the binary has no amplitude keyword, so the check was unperformable).
  * s4-A.3  it is replaced by check 4': the CrO2 arm below must print a finite U with ZERO
            "Convergence has not been reached" lines.
  * s4-A.4  the chi-symmetry check is a REPORTED DIAGNOSTIC, not a gate. Settled today by
            reading the source (see `CHI_SYMMETRY_IS_AN_IDENTITY` below): on anything hp.x
            reports it is an exact identity. The real reproducibility test is
            `find_atpert = 4`, two independently perturbed Ti within 0.05 eV.
  * s4-A.5  the cost model is per-(atom, q) and scales with the k-count hp.x prints for
            each q; the slab timing is taken at a general, non-Gamma q.

If this file and docs/43 ever disagree, docs/43 wins and this file is wrong.

What was measured on the box on 2026-08-09 (instance 47025043, /workspace/scratch_1b)
--------------------------------------------------------------------------------------
Everything below is a printed result, not a reading of the manual. The constraints were also
read out of the shipped binary (`grep -aoE "[ -~]{6,}" hp.x`), because docs/42's own lesson is
that shortcuts around running the code produce wrong capability claims.

* **hp.x refuses a gapped system presented as a metal.** Bulk rutile TiO2 at the campaign's
  `smearing='mv', degauss=0.01` stops with

      DOS(E_Fermi) = -0.1014E-33 ... the system has a gap, and hence it should NOT be
      treated as a metal ... Stopping...

  and then prints `JOB DONE.` The validation target therefore runs `occupations='fixed'`.
  The pw.x total energy is byte-identical either way (-405.93096624 Ry), so nothing is
  traded away. This is why `gen_rutile.make_input` grew an `occupations` argument.
* **hp.x runs on a magnetic, metallic, PAW 3d oxide.** Rutile FeO2, `Fe.pbe-spn-kjpaw` (PAW,
  Zval 16) as the Hubbard atom, nspin=2, reached the linear-response solver and printed finite
  Fermi-energy shifts (3.48E-01, -4.14E-01, -2.25E-01 Ry over three iterations). That is the
  code path docs/42 could not vouch for. (The underlying SCF was a deliberately cheap 30/240
  Ry run that did *not* converge, so the numbers are meaningless -- the *code path* is the
  result, and it is reported as such.)
* **`find_atpert` semantics, verified against both systems** (the QE docs and one of my own
  first readings disagreed; the binary settles it): 1 = group by unperturbed occupations
  (default), 2 = group by atomic TYPE, 3 = group by symmetry, 4 = perturb every Hubbard atom.
  On bulk TiO2, 1/2/3 all give n_pert = 1 and 4 gives 2. **On the clean CrO2(110) slab, 2
  gives 1 and 1/3/4 give 6** -- because all six Cr share one ATOMIC_SPECIES type. `find_atpert=2`
  on a slab is a silent 6x undercount and must never be used there.
* **Constraints, read out of the binary.** hp.x rejects: `Hubbard_projectors` = pseudo /
  norm-atomic / wf (only `atomic` and `ortho-atomic` survive); tetrahedra; a preceding
  vc-relax; Q-in-real-space; constrained magnetisation; hybrids; meta-GGA; the Liechtenstein
  DFT+U formulation; `assume_isolated='2D'`; two Fermi energies. It requires a `HUBBARD` card
  in the pw.x run. It warns -- does not stop -- if the Hubbard atoms are not listed first in
  `ATOMIC_POSITIONS`. `determine_q_mesh_only` is only legal together with `perturb_only_atom`.
  None of those rejects PAW or ultrasoft, and the FeO2 test confirms PAW works.
* **Pseudopotentials actually present** in `/usr/share/espresso/pseudo` (103 files, the SSSP
  efficiency .deb of tasks/lessons.md 2026-07-31). Exactly one Ti and exactly one O:
  `ti_pbe_v1.4.uspp.F.UPF` (GBRV **ultrasoft**, Zval 12) and `O.pbe-n-kjpaw_psl.0.1.UPF`
  (**PAW**, Zval 6). There is no second oxygen, so the O projector is not a free choice --
  which is fine, because O carries no Hubbard manifold here.

What was settled on 2026-08-09 in the fix round (findings 9-20)
---------------------------------------------------------------
* **Where the answer lives.** U, chi0, chi and the Hubbard matrix appear in
  `<cwd>/<prefix>.Hubbard_parameters.dat` and `<outdir>/HP/<prefix>.chi*.dat` and **NOWHERE
  in stdout**: `grep -ac 'Hubbard U parameters:' hp.out` = 0 on a run that produced
  U = 4.1543 eV. Confirmed in the source: `HP/src/hp_postproc.f90:alloc_pp` opens
  `trim(prefix)//".Hubbard_parameters.dat"` with a bare filename (so: the process CWD), and
  `HP/src/hp_write_chi_full.f90` writes `trim(tmp_dir)//trim(prefix)//".chi.dat"`. Both are
  keyed on **prefix alone**, so a second rung at the same prefix overwrites the first's
  answer in place -- measured: nq 1x1x1 gave 4.1543, then nq 2x2x2 in the same outdir left
  one file reading 4.1786. `queue_hp.sh` now renames both onto the deck basename immediately
  after the hp.x call and gates on the artifact.
* **The chi-symmetry gate was an identity, and this is now proven rather than suspected.**
  `HP/src/hp_postproc.f90` (QE 7.5, fetched from the QEF GitLab at tag `qe-7.5`) runs, in
  order: `read_chi` -> `average_similar_elements` -> `reconstruct_full_chi` -> invert ->
  `calculate_Hubbard_parameters` (which is what writes the .dat). The last block of
  `reconstruct_full_chi` is literally

      ! Symmetrization
      DO na = 1, nath_sc
         DO nb = 1, nath_sc
            chi_(na,nb) = 0.5d0 * ( chi_(na,nb) + chi_(nb,na) )
            chi_(nb,na) = chi_(na,nb)

  applied to chi0 and chi before anything is printed. So |chi_ij - chi_ji| is identically 0
  in every matrix hp.x reports, at any conv_thr, on any system, converged or not. See
  `CHI_SYMMETRY_IS_AN_IDENTITY`.
* **A validated k-count model** (`rutile_q_list`, `slab_q_list`). hp.x reduces the NSCF
  k-set with a SUBSET of the crystal group -- on bulk rutile it is the 8 operations that
  leave the perturbed Ti at the origin fixed, not the full 16 -- which is why its Gamma NSCF
  prints 65 k where the pw.x SCF on the same mesh prints 50. Encoding that subgroup and
  reducing the k- and q-meshes by hand reproduces **26 measured integers exactly**: all 7
  irreducible q-counts on bulk rutile, all 5 sym + 3 nosym q-counts on the slab, the slab's
  15 k at 9x4x1, all 4 measured hp.x k-counts on the production mesh *including which q
  index they belong to* (q#2 of 2x2x2 -> 130, q#2 of 3x3x3 -> 208, q#14 of 4x4x4 -> 576),
  and -- the part that is actually evidence rather than fitting -- all 6 per-q k-counts a
  today's out-of-sample smoke run printed on a k-mesh the model had never been shown
  (6, 12, 16, 16, 12, 12). Nothing in the cost model is a flat constant any more.

Ordering requirement
--------------------
hp.x wants the Hubbard atoms first in `ATOMIC_POSITIONS`. `gen_rutile.make_input` already
emits `M, M, O, O, O, O`, and `runs/Cr_slab/slab.in` already emits six Cr then twelve O, so
**no reordering was needed anywhere** -- but `_assert_hubbard_atoms_first` checks it on every
deck this file writes rather than trusting that, because the warning hp.x prints is easy to
miss in a 30 000-line output and the consequence is a silently wrong chi matrix.

Refuse-to-write guards
----------------------
The slab decks are derived from `runs/Cr_slab/slab.in` + the relaxed geometry in
`runs/Cr_slab/slab.out`. Exactly five things are allowed to differ from the source deck:
`calculation`, `prefix`/`outdir`, the coordinates (start -> relaxed), the Hubbard U value
(3.7 -> 1.0d-8, the from-scratch DFPT protocol), and -- in the `sym` arm only, declared -- the
removal of `nosym`/`noinv`. Every other field is compared token by token against the source
and the builder raises SystemExit and writes nothing if any of them moved. A U computed on a
different cutoff, k-mesh, smearing or magnetisation than the tier it is meant to correct is
not a correction, it is a second, undocumented protocol.

Usage
-----
  PYTHONPATH=src python src/dft/build_hp_validation.py --check-only
  PYTHONPATH=src python src/dft/build_hp_validation.py
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_rutile import RUTILE, METAL_SYMBOL, make_input          # noqa: E402
from probe_decks import parse_input_deck, parse_final_coordinates  # noqa: E402

# --------------------------------------------------------------------------- constants ---

PSEUDO_DIR = "/usr/share/espresso/pseudo"

#: The two UPFs that exist on the box for this validation. Listed, not guessed:
#: `ls /usr/share/espresso/pseudo | grep -Ei "^(Ti|O)[._]"` returns exactly these two.
TI_UPF = "ti_pbe_v1.4.uspp.F.UPF"          # GBRV ultrasoft, Zval 12
O_UPF = "O.pbe-n-kjpaw_psl.0.1.UPF"        # PSlibrary PAW, Zval 6

#: Cr for the magnetic arm (docs/43 s4-A.3). Listed, not guessed: it is the only Cr in
#: /usr/share/espresso/pseudo (`ls | grep -Ei '^cr[._]'` returns exactly this one, verified
#: on box 47025043 2026-08-09), and it is the same UPF the campaign's Cr slabs already use.
CR_UPF = "cr_pbe_v1.5.uspp.F.UPF"          # GBRV ultrasoft

#: hp.x accepts only these two projector types; the other three
#: (`pseudo`, `norm-atomic`, `wf`) are hard errors in the binary.
PROJECTORS = ("atomic", "ortho-atomic")

#: The from-scratch DFPT protocol perturbs a system with no U applied. QE will not switch on
#: the Hubbard machinery for U = 0 exactly, and hp.x refuses to run without it, so the
#: canonical HP-tutorial placeholder is used.
U_SEED = "1.d-8"

#: TiO2 q-mesh ladder. Internal criterion I1 is |U(4x4x4) - U(3x3x3)| <= 0.10 eV, so the
#: ladder must contain both, and 2x2x2 is carried as the cheap first return.
TIO2_QMESH_LADDER = ((2, 2, 2), (3, 3, 3), (4, 4, 4))

#: Measured today with `determine_q_mesh_only` -- irreducible q counts for the ladder, so the
#: cost model does not have to guess and a later run can be checked against it.
TIO2_NQ_MEASURED = {(1, 1, 1): 1, (2, 2, 2): 6, (2, 2, 3): 6, (3, 3, 3): 8,
                    (3, 3, 4): 12, (4, 4, 4): 21, (4, 4, 6): 28}
CRSLAB_NQ_MEASURED_SYM = {(1, 1, 1): 1, (2, 1, 1): 2, (3, 2, 1): 4, (4, 2, 1): 6, (9, 4, 1): 15}
CRSLAB_NQ_MEASURED_NOSYM = {(3, 2, 1): 6, (4, 2, 1): 8, (9, 4, 1): 36}

#: Campaign cutoffs. The validation target has no business drifting off them: an hp.x U
#: computed at a different basis than the tier it corrects is not the tier's U.
ECUTWFC, ECUTRHO = 80.0, 640.0
TIO2_KPTS = (6, 6, 8)

#: The magnetic arm, docs/43 s4-A.3. Same cell family, same cutoffs, same k-mesh as TiO2 so
#: that the ONLY things that move are the six differences the arm exists to test: nspin 1->2,
#: fixed->smeared occupations, insulator->half-metal, empty->partially-filled 3d manifold.
#: nq is 2x2x2 (the cheap first return) because this arm's registered job is "does it print a
#: finite U with zero non-convergence lines", not "is U q-converged".
CRO2_KPTS = (6, 6, 8)
CRO2_QMESH = (2, 2, 2)

CR_SLAB_RUN = "runs/Cr_slab"

# ------------------------------------------------------- symmetry / k-count model ---
# Findings [10] [11] [19]: the shipped cost model applied ONE core-h figure to all 102
# (atom, q) pairs. It was measured at nq = 2x2x2, the one mesh where every q is a
# time-reversal-invariant momentum, and the slab timing was taken at q = Gamma. Both are the
# cheapest points that exist. The fix is not a fudge factor: hp.x's cost per (atom, q) is
# very nearly linear in the number of irreducible k-points IT uses for that q, and that
# number is computable exactly, so the model computes it.
#
# The subtlety that makes the naive version wrong in the OTHER direction: the count hp.x
# prints ("number of k points= N") is the k set alone at q = Gamma and the k PLUS k+q sets
# at q != Gamma. The Sternheimer solve runs once per k, so the work scales with N_k, i.e.
# with the printed number HALVED at q != Gamma. This is measured, not argued: Gamma printed
# 65 and cost 7.63 s/LR-iteration; the zone boundary printed 130 -- twice as many -- and cost
# 8.0 s, five per cent more, not twice as much. Both have N_k = 65. Scaling on the printed
# number would have over-costed every non-Gamma q by 2x.

#: The eight operations that survive on bulk rutile MO2 when the Hubbard atom at the origin
#: is perturbed: point group mmm about z, [110] and [1-10]. The other eight operations of
#: P4_2/mnm carry the (1/2,1/2,1/2) translation and exchange the two metal sites, so they
#: cannot leave a single perturbed site invariant. Integer matrices because rutile is
#: tetragonal and all eight are signed permutations in the crystal basis; for orthogonal
#: integer R the reciprocal-space action on fractional k is R itself.
_RUTILE_OPS = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1)),        # E
    ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),      # C2z
    ((0, 1, 0), (1, 0, 0), (0, 0, -1)),       # C2 [110]
    ((0, -1, 0), (-1, 0, 0), (0, 0, -1)),     # C2 [1-10]
    ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),     # i
    ((1, 0, 0), (0, 1, 0), (0, 0, -1)),       # sigma_z
    ((0, -1, 0), (-1, 0, 0), (0, 0, 1)),      # sigma [110]
    ((0, 1, 0), (1, 0, 0), (0, 0, 1)),        # sigma [1-10]
)

#: The clean CrO2(110) slab, symmetry ON: mm2 about the surface normal z. Measured on the box
#: as "4 Sym. Ops." at production cutoff, and this set reproduces every symmetry count the
#: slab has ever printed (see _validate_symmetry_model). The nosym arm keeps only E.
_SLAB_OPS = (
    ((1, 0, 0), (0, 1, 0), (0, 0, 1)),        # E
    ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),      # C2z
    ((-1, 0, 0), (0, 1, 0), (0, 0, 1)),       # m_x
    ((1, 0, 0), (0, -1, 0), (0, 0, 1)),       # m_y
)
_SLAB_OPS_NOSYM = (_SLAB_OPS[0],)

CRSLAB_KMESH = (9, 4, 1)


def _apply(op, v):
    return tuple(sum(op[i][j] * v[j] for j in range(3)) for i in range(3))


def _mesh_orbits(mesh, ops):
    """Irreducible points of a Monkhorst-Pack mesh, in QE's own generation order.

    QE's `kpoint_grid` loops i (slowest) -> j -> k (fastest) and keeps the first member of
    each orbit, so the ordering here is not cosmetic: `start_q`/`last_q` address q by INDEX,
    and picking the wrong index is exactly how the shipped slab timing deck ended up on
    Gamma. The order is validated against three measured q indices (see the validator).
    """
    n1, n2, n3 = mesh
    seen, reps = set(), []
    for i in range(n1):
        for j in range(n2):
            for k in range(n3):
                p = (i, j, k)
                if p in seen:
                    continue
                reps.append(p)
                for op in ops:
                    w = _apply(op, p)
                    # integer arithmetic on mesh indices: exact, no float rounding anywhere
                    seen.add((w[0] % n1, w[1] % n2, w[2] % n3))
    return reps


def _small_group(qidx, mesh, ops):
    """Operations with R q = q + G, q given as integer mesh indices."""
    n1, n2, n3 = mesh
    out = []
    for op in ops:
        w = _apply(op, qidx)
        if (w[0] % n1, w[1] % n2, w[2] % n3) == (qidx[0] % n1, qidx[1] % n2, qidx[2] % n3):
            out.append(op)
    return out


def _ops_in_kmesh_basis(ops, qidx, qmesh, kmesh):
    """Re-express the small group of q so it can act on the k-mesh indices.

    The operations are signed permutations, so they act on mesh indices directly provided the
    mesh is compatible with the permutation (6x6x8 is: the x and y extents are equal, which
    is what the [110] mirrors need). Asserted rather than assumed.
    """
    if ops and any(op[0][1] or op[1][0] for op in ops) and kmesh[0] != kmesh[1]:
        raise SystemExit(f"refusing to cost: k-mesh {kmesh} is not compatible with a "
                         f"[110]-type operation in the small group of q={qidx}/{qmesh}")
    return ops


def q_table(qmesh, kmesh, ops):
    """[(index, q as mesh fractions, |small group|, N_k, printed_k)] for one nq mesh.

    `printed_k` is what hp.x writes as "number of k points=" for that q: N_k at Gamma,
    2*N_k elsewhere, because the NSCF also carries the k+q set.
    """
    rows = []
    for n, qidx in enumerate(_mesh_orbits(qmesh, ops), start=1):
        sg = _ops_in_kmesh_basis(_small_group(qidx, qmesh, ops), qidx, qmesh, kmesh)
        nk = len(_mesh_orbits(kmesh, sg))
        gamma = qidx == (0, 0, 0)
        rows.append(dict(index=n, q=[qidx[i] / qmesh[i] for i in range(3)],
                         n_small_ops=len(sg), n_k=nk, printed_k=nk if gamma else 2 * nk,
                         gamma=gamma))
    return rows


#: MEASURED hp.x k-counts, box 47025043, 2026-08-09, bulk rutile TiO2. Key is
#: (k-mesh, nq mesh, q index as hp.x numbers them); value is the integer hp.x printed after
#: "number of k points=". This is the direct evidence the cost model has, and the model is
#: required to reproduce every entry before it is allowed to extrapolate anything.
#:
#: The first four are on the production 6x6x8 k-mesh (the review's measurements, finding
#: [10]). The last six are OUT OF SAMPLE and are the stronger evidence: a 30/240, k 2x2x2,
#: nq 2x2x2 smoke run of `queue_hp.sh` printed 6, 12, 16, 16, 12, 12 for its six q, on a
#: k-mesh the model had never been shown, and the model predicts exactly those six integers.
#: Note the pattern inside them -- q#1 (Gamma) prints 6 and q#2 prints 12 for the SAME N_k --
#: which is the printed = 2 * N_k rule showing up again at a completely different scale.
TIO2_PRINTED_K_MEASURED = {
    ((6, 6, 8), (2, 2, 2), 1): 65, ((6, 6, 8), (2, 2, 2), 2): 130,
    ((6, 6, 8), (3, 3, 3), 2): 208, ((6, 6, 8), (4, 4, 4), 14): 576,
    ((2, 2, 2), (2, 2, 2), 1): 6, ((2, 2, 2), (2, 2, 2), 2): 12,
    ((2, 2, 2), (2, 2, 2), 3): 16, ((2, 2, 2), (2, 2, 2), 4): 16,
    ((2, 2, 2), (2, 2, 2), 5): 12, ((2, 2, 2), (2, 2, 2), 6): 12,
}

#: MEASURED with pw.x at production cutoff on the clean CrO2(110) slab (COST_BASIS below).
CRSLAB_PRINTED_K_MEASURED = {((1, 1, 1), 1): 15}


def _validate_symmetry_model():
    """Refuse to cost anything if the symmetry model contradicts a measured integer.

    Twenty-two integers, every one of them printed by QE on this box. If any single one
    disagrees the model is wrong somewhere and every extrapolation downstream of it is
    worthless, so this raises rather than warns -- the build_basin_restarts.py pattern.
    """
    bad = []
    for mesh, want in TIO2_NQ_MEASURED.items():
        got = len(_mesh_orbits(mesh, _RUTILE_OPS))
        if got != want:
            bad.append(f"rutile nq{mesh}: model {got} != measured {want}")
    for mesh, want in CRSLAB_NQ_MEASURED_SYM.items():
        got = len(_mesh_orbits(mesh, _SLAB_OPS))
        if got != want:
            bad.append(f"slab sym nq{mesh}: model {got} != measured {want}")
    for mesh, want in CRSLAB_NQ_MEASURED_NOSYM.items():
        got = len(_mesh_orbits(mesh, _SLAB_OPS_NOSYM))
        if got != want:
            bad.append(f"slab nosym nq{mesh}: model {got} != measured {want}")
    for (kmesh, mesh, idx), want in TIO2_PRINTED_K_MEASURED.items():
        rows = q_table(mesh, kmesh, _RUTILE_OPS)
        got = rows[idx - 1]["printed_k"]
        if got != want:
            bad.append(f"rutile k{kmesh} nq{mesh} q#{idx}: model {got} k != measured {want}")
    for (mesh, idx), want in CRSLAB_PRINTED_K_MEASURED.items():
        got = q_table(mesh, CRSLAB_KMESH, _SLAB_OPS)[idx - 1]["printed_k"]
        if got != want:
            bad.append(f"slab sym nq{mesh} q#{idx}: model {got} k != measured {want}")
    if bad:
        raise SystemExit("refusing to write: the symmetry model contradicts measured "
                         "output:\n  " + "\n  ".join(bad))
    return (len(TIO2_NQ_MEASURED) + len(CRSLAB_NQ_MEASURED_SYM) + len(CRSLAB_NQ_MEASURED_NOSYM)
            + len(TIO2_PRINTED_K_MEASURED) + len(CRSLAB_PRINTED_K_MEASURED))


#: Finding [13], settled by reading QE 7.5 HP/src/hp_postproc.f90 rather than by inference.
#: Kept as a named constant because the temptation to re-promote this to a hard gate will
#: recur, and the answer is in the source, not in an opinion.
CHI_SYMMETRY_IS_AN_IDENTITY = dict(
    answer="POST-symmetrisation. |chi_ij - chi_ji| is identically zero in anything hp.x "
           "reports, so the registered check passes vacuously on every run, converged or "
           "not, at any conv_thr_chi.",
    evidence="QE 7.5 HP/src/hp_postproc.f90, SUBROUTINE reconstruct_full_chi: after filling "
             "missing elements by distance matching it runs an unconditional "
             "chi_(na,nb) = 0.5*(chi_(na,nb)+chi_(nb,na)) loop over ALL (na,nb), on chi0 and "
             "chi both, and only then does calculate_Hubbard_parameters write the .dat. "
             "average_similar_elements runs one step earlier and smears equal-distance "
             "elements together as well.",
    consequence="Reported as a diagnostic, never gated (docs/43 s4-A.4). It is not quite "
                "content-free: the RAW <outdir>/HP/<prefix>.chi.dat written during the run "
                "by hp_write_chi_full is pre-symmetrisation, and when find_atpert = 4 "
                "perturbs both Ti independently its two columns ARE computed independently, "
                "so chi(1,2) vs chi(2,1) read off that file is a genuine measurement. That "
                "is only possible because queue_hp.sh now preserves the file per rung.")

# --------------------------------------------------------------------------- HP inputs ---


def hp_namelist(prefix: str, outdir: str, nq, *, determine_num_pert_only=False,
                determine_q_mesh_only=False, perturb_only_atom=None, find_atpert=None,
                start_q=None, last_q=None, conv_thr_chi="1.0d-5", niter_max=None,
                iverbosity=2):
    """Emit an `&INPUTHP` namelist.

    `iverbosity = 2` is kept, but the docstring it replaces was WRONG and the error mattered
    (finding [16]): iverbosity does **not** put chi0/chi into the output file. Those matrices
    are written to `<outdir>/HP/<prefix>.chi.dat` (raw, per perturbed column, by
    `hp_write_chi_full`) and, post-symmetrisation, into `<cwd>/<prefix>.Hubbard_parameters.dat`
    (by `hp_postproc:calculate_Hubbard_parameters`). U appears in neither stdout nor the .out.
    What iverbosity = 2 buys is the per-q response-occupation trace, which is how a stalled
    linear response is diagnosed after the fact. The audit trail comes from the .dat files,
    which is why `queue_hp.sh` renames them onto the deck basename the moment hp.x returns.
    """
    if determine_q_mesh_only and perturb_only_atom is None:
        # the binary's own guard: "determine_q_mesh_only can be set to .true. only if
        # perturb_only_atom is .true. for some atom"
        raise SystemExit("refusing to write: determine_q_mesh_only needs perturb_only_atom")
    if determine_num_pert_only and determine_q_mesh_only:
        raise SystemExit("refusing to write: the two determine_*_only modes are exclusive")
    lines = ["&INPUTHP",
              f"  prefix = '{prefix}'",
              f"  outdir = '{outdir}'",
              f"  nq1 = {nq[0]}, nq2 = {nq[1]}, nq3 = {nq[2]}",
              f"  conv_thr_chi = {conv_thr_chi}",
              f"  iverbosity = {iverbosity}"]
    if find_atpert is not None:
        lines.append(f"  find_atpert = {find_atpert}")
    if perturb_only_atom is not None:
        lines.append(f"  perturb_only_atom({perturb_only_atom}) = .true.")
    if start_q is not None:
        lines.append(f"  start_q = {start_q}")
    if last_q is not None:
        lines.append(f"  last_q = {last_q}")
    if niter_max is not None:
        lines.append(f"  niter_max = {niter_max}")
    if determine_num_pert_only:
        lines.append("  determine_num_pert_only = .true.")
    if determine_q_mesh_only:
        lines.append("  determine_q_mesh_only = .true.")
    lines.append("/")
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------- guards ---

_POS_RE = re.compile(r"ATOMIC_POSITIONS[^\n]*\n((?:\s*[A-Z][a-z]?\s+[-\d.eE+]+.*\n)+)")
_SPECIES_RE = re.compile(r"ATOMIC_SPECIES\s*\n((?:\s*\S+\s+[\d.]+\s+\S+\s*\n)+)")


def _hubbard_manifolds(text: str):
    """Species labels carrying a Hubbard manifold, e.g. {'Ti'} from `U Ti-3d 1.d-8`."""
    return {m.split("-")[0] for m in re.findall(r"^\s*U\s+(\S+)\s+\S+\s*$", text, re.M)}


def _assert_hubbard_atoms_first(text: str, where: str):
    """hp.x wants the Hubbard atoms first in ATOMIC_POSITIONS -- and it only WARNS.

    A warning buried in a 30k-line output that silently corrupts the response matrices is
    exactly the class of failure this campaign keeps paying for, so it is a hard error here.
    Checked on ATOMIC_SPECIES too: the species order fixes the `starting_magnetization(i)`
    indices, and getting those onto the wrong element is the same bug wearing a hat.
    """
    # Both halves are required. A bare `U Cr-3d 3.7` line with no `HUBBARD (...)` header is
    # silently ignored by pw.x, and hp.x then dies with "The HP code can be used only on top
    # of DFT+Hubbard" -- after the SCF has already been paid for. Found by deliberately
    # feeding this function a deck I knew was broken (tasks/lessons.md 2026-07-31).
    hub = _hubbard_manifolds(text)
    if not hub or not re.search(r"^\s*HUBBARD\s*\(", text, re.M):
        raise SystemExit(f"refusing to write {where}: no usable HUBBARD card, hp.x cannot run "
                         f"('The HP code can be used only on top of DFT+Hubbard')")
    m = _POS_RE.search(text)
    if not m:
        raise SystemExit(f"refusing to write {where}: no ATOMIC_POSITIONS block")
    order = [ln.split()[0] for ln in m.group(1).strip().split("\n") if ln.split()]
    seen_non_hubbard = False
    for sym in order:
        if sym in hub:
            if seen_non_hubbard:
                raise SystemExit(f"refusing to write {where}: Hubbard atom {sym!r} appears "
                                 f"after a non-Hubbard atom in ATOMIC_POSITIONS; hp.x only "
                                 f"warns about this and then computes the wrong chi")
        else:
            seen_non_hubbard = True
    ms = _SPECIES_RE.search(text)
    if ms:
        sorder = [ln.split()[0] for ln in ms.group(1).strip().split("\n") if ln.split()]
        if sorder and sorder[0] not in hub:
            raise SystemExit(f"refusing to write {where}: ATOMIC_SPECIES starts with "
                             f"{sorder[0]!r}, not a Hubbard species")
    return order


#: hp.x hard-errors on each of these; catching them here costs nothing and catching them on
#: the box costs a queue slot and a confusing log. Strings taken from the shipped binary.
_HP_FORBIDDEN = (
    (r"occupations\s*=\s*'tetrahedra", "HP with tetrahedra is not supported"),
    (r"calculation\s*=\s*'vc-relax'", "The HP code is not working after vc-relax"),
    (r"^\s*real_space\s*=\s*\.true\.", "The HP code with Q in real space is not supported"),
    (r"^\s*tqr\s*=\s*\.true\.", "The HP code with Q in real space is not supported"),
    (r"assume_isolated\s*=\s*'2D'", "The HP code does not support the 2D cutoff"),
    (r"^\s*constrained_magnetization\s*=\s*'(?!none)",
     "The HP code with constrained magnetization is not yet available"),
    (r"^\s*lda_plus_u_kind\s*=\s*1", "HP does not support the Liechtenstein formulation"),
    (r"^\s*two_chem\s*=\s*\.true\.", "HP with two Fermi energies is not available"),
    (r"^\s*input_dft\s*=\s*'(HSE|PBE0|B3LYP|SCAN|R2SCAN)", "HP: no hybrids / meta-GGA"),
)


def _assert_hp_compatible(text: str, where: str):
    for pat, why in _HP_FORBIDDEN:
        if re.search(pat, text, re.M | re.I):
            raise SystemExit(f"refusing to write {where}: {why}")
    m = re.search(r"HUBBARD\s*\(([^)]*)\)", text)
    if not m:
        raise SystemExit(f"refusing to write {where}: no HUBBARD card")
    proj = m.group(1).strip()
    if proj not in PROJECTORS:
        raise SystemExit(f"refusing to write {where}: Hubbard_projectors={proj!r}; hp.x "
                         f"accepts only {PROJECTORS}")


#: Fields that must be byte-identical between a derived slab deck and its source. If any of
#: these moves, the U is being computed for a different Hamiltonian than the tier it corrects.
_FROZEN_FIELDS = ("ecutwfc", "ecutrho", "degauss", "smearing", "nspin", "occupations",
                  "ibrav", "nat", "ntyp", "conv_thr", "mixing_mode", "mixing_beta")


def _scalars(text: str):
    out = {}
    for key in _FROZEN_FIELDS:
        m = re.search(rf"^\s*{key}\s*=\s*([^\s,!/]+)", text, re.M | re.I)
        out[key] = m.group(1).strip() if m else None
    out["starting_magnetization"] = sorted(
        re.findall(r"starting_magnetization\(\d+\)\s*=\s*[-\d.eEdD+]+", text))
    out["species"] = sorted(
        ln.strip() for ln in (_SPECIES_RE.search(text).group(1).strip().split("\n")
                              if _SPECIES_RE.search(text) else []))
    m = re.search(r"K_POINTS[^\n]*\n\s*([\d\s]+)\n", text)
    out["kpoints"] = " ".join(m.group(1).split()) if m else None
    m = re.search(r"CELL_PARAMETERS[^\n]*\n((?:[^\n]*\n){3})", text)
    out["cell"] = " ".join(m.group(1).split()) if m else None
    out["constraint_flags"] = [ln.split()[4:7] for ln in
                               (_POS_RE.search(text).group(1).strip().split("\n")
                                if _POS_RE.search(text) else []) if len(ln.split()) >= 7]
    return out


def _assert_only_intended_changes(src: str, new: str, allowed: set, where: str):
    """Field-by-field diff against the source deck. Anything unlisted moving is fatal."""
    a, b = _scalars(src), _scalars(new)
    moved = [k for k in a if a[k] != b[k]]
    unexpected = [k for k in moved if k not in allowed]
    if unexpected:
        detail = "; ".join(f"{k}: {a[k]!r} -> {b[k]!r}" for k in unexpected)
        raise SystemExit(f"refusing to write {where}: unintended change in {detail}")
    return moved


# ------------------------------------------------------------------------------ TiO2 ---


def build_tio2(outdir: str):
    """Bulk rutile TiO2 -- the GO/NO-GO validation target.

    Written from `gen_rutile.make_input` rather than by hand so that the geometry, the
    cutoffs and the species ordering are the same code path the rest of the tier uses. The
    only thing bolted on afterwards is the HUBBARD card, because `RUTILE['TiO2']['U'] = 0.0`
    (Materials Project applies no U to Ti) and hp.x needs a card to exist.
    """
    os.makedirs(outdir, exist_ok=True)
    written, jobs = [], []

    for proj in PROJECTORS:
        tag = "atomic" if proj == "atomic" else "ortho"
        scf = make_input("TiO2", ECUTWFC, ECUTRHO, TIO2_KPTS, PSEUDO_DIR, TI_UPF, O_UPF,
                         prefix=f"tio2_{tag}", outdir=f"./tmp_tio2_{tag}",
                         conv_thr="1.0d-10", with_u=False, occupations="fixed")
        # conv_thr 1e-10, not the campaign's 1e-6: hp.x differentiates this density, and a
        # loosely converged ground state is differentiated into noise. QE's own HP examples
        # run 1e-10 to 1e-15 for the same reason.
        scf += f"HUBBARD ({proj})\nU Ti-3d {U_SEED}\n"
        if "nspin = 1" not in scf:
            raise SystemExit("refusing to write tio2 scf: TiO2 must be nspin = 1")
        if "starting_magnetization" in scf:
            raise SystemExit("refusing to write tio2 scf: TiO2 must carry no magnetisation")
        if "occupations = 'fixed'" not in scf:
            raise SystemExit("refusing to write tio2 scf: hp.x stops on a gapped system run "
                             "with smearing (measured 2026-08-09)")
        for upf in (TI_UPF, O_UPF):
            if upf not in scf:
                raise SystemExit(f"refusing to write tio2 scf: {upf} missing")
        _assert_hp_compatible(scf, f"tio2 scf ({proj})")
        _assert_hubbard_atoms_first(scf, f"tio2 scf ({proj})")
        written.append((os.path.join(outdir, f"scf__{tag}.in"), scf))

        # counting decks -- seconds each, and they pin n_pert/n_q before anything is spent
        written.append((os.path.join(outdir, f"hp_npert__{tag}.in"),
                        hp_namelist(f"tio2_{tag}", f"./tmp_tio2_{tag}", (2, 2, 2),
                                    determine_num_pert_only=True, find_atpert=1)))
        # find_atpert = 3 (group by SYMMETRY). docs/43's criterion I5 compares the n_pert
        # that find_atpert = 1 and 3 return on bulk TiO2; the shipped batch had no
        # find_atpert = 3 deck anywhere, so the criterion was unmeetable by construction
        # (finding [14]). These cost ~3 s each -- there was never a reason not to ship them.
        written.append((os.path.join(outdir, f"hp_npert3__{tag}.in"),
                        hp_namelist(f"tio2_{tag}", f"./tmp_tio2_{tag}", (2, 2, 2),
                                    determine_num_pert_only=True, find_atpert=3)))
        for nq in TIO2_QMESH_LADDER:
            q = "".join(map(str, nq))
            written.append((os.path.join(outdir, f"hp_qmesh__{tag}_q{q}.in"),
                            hp_namelist(f"tio2_{tag}", f"./tmp_tio2_{tag}", nq,
                                        determine_q_mesh_only=True, perturb_only_atom=1)))

        # the q-mesh ladder itself -- internal criterion I1
        for nq in TIO2_QMESH_LADDER:
            q = "".join(map(str, nq))
            written.append((os.path.join(outdir, f"hp__{tag}_q{q}.in"),
                            hp_namelist(f"tio2_{tag}", f"./tmp_tio2_{tag}", nq,
                                        find_atpert=1)))
            jobs.append(dict(system="TiO2", projector=proj, nq=list(nq),
                             n_pert_expected=1, n_q_expected=TIO2_NQ_MEASURED.get(nq),
                             file=f"hp__{tag}_q{q}.in", role="q-mesh ladder (I1)"))

        # internal criterion I2: perturb BOTH Ti independently. They are related by the 4_2
        # screw, so their chi0/chi rows and their U must agree. With the default
        # find_atpert=1 hp.x perturbs one atom and RECONSTRUCTS the other by symmetry, which
        # makes the agreement an identity rather than a measurement. find_atpert=4 is the
        # only setting that turns it into a test (measured today: it lists 2 atoms).
        written.append((os.path.join(outdir, f"hp__{tag}_q333_allatoms.in"),
                        hp_namelist(f"tio2_{tag}", f"./tmp_tio2_{tag}", (3, 3, 3),
                                    find_atpert=4)))
        jobs.append(dict(system="TiO2", projector=proj, nq=[3, 3, 3], n_pert_expected=2,
                         n_q_expected=TIO2_NQ_MEASURED[(3, 3, 3)],
                         file=f"hp__{tag}_q333_allatoms.in",
                         role="two-site reproducibility (I2)"))

    # The timing probes, so the cost model is reproducible rather than remembered. q#1 and
    # q#2 of the 2x2x2 mesh were already measured (99.05 s and 85.61 s at NP=12) -- and BOTH
    # of them have N_k = 65, because q#1 is Gamma and q#2 = (0,0,1/2) is a zone-boundary TRIM
    # whose small group is the whole 8-operation set. Two measurements of the same point in
    # cost space. q#3 = (0,1/2,0) has a 4-operation small group and N_k = 100, so it is the
    # first TiO2 timing that can falsify the k-scaling law rather than confirm a tautology.
    for qi in (1, 2, 3):
        suffix = "" if qi == 1 else f"_q{qi}"
        written.append((os.path.join(outdir, f"hp_1atomq__atomic{suffix}.in"),
                        hp_namelist("tio2_atomic", "./tmp_tio2_atomic", (2, 2, 2),
                                    perturb_only_atom=1, start_q=qi, last_q=qi)))
    return written, jobs


# -------------------------------------------------------------------- bulk rutile CrO2 ---


def build_cro2(outdir: str):
    """The magnetic, metallic bulk arm -- docs/43 s4-A.3, finding [15].

    This is the highest-value deck in block 1B and it did not exist. A GO measured only on
    TiO2 licenses the sentence "hp.x validates on a closed-shell bulk insulator", which is
    not the claim blocks 2C and 3Y need: production is nspin = 2, smeared, metallic and
    partially-filled 3d, and hp.x demonstrably takes a different branch on gapped versus
    smeared systems (it hard-stops on the first). The only magnetic evidence in the archive
    is an FeO2 run whose underlying SCF printed "convergence NOT achieved after 200
    iterations", so it shows a code path was reached and nothing about whether the response
    converges.

    Everything except the six differences under test is held at the TiO2 arm's settings --
    same cutoffs, same 6x6x8 k-mesh, same conv_thr 1e-10, same atomic projectors, same
    U seed, same nq 2x2x2 -- so that a failure here is attributable.

    Registered success condition (docs/43 s4-A.3, quoted not restated): a finite U with ZERO
    "Convergence has not been reached" lines. A GAPSTOP would also be informative and is
    counted separately by queue_hp.sh: CrO2 is a half-metal, so if this SCF opens a gap the
    arm has found something about the ground state, not about hp.x.
    """
    os.makedirs(outdir, exist_ok=True)
    written, jobs = [], []
    scf = make_input("CrO2", ECUTWFC, ECUTRHO, CRO2_KPTS, PSEUDO_DIR, CR_UPF, O_UPF,
                     prefix="cro2_atomic", outdir="./tmp_cro2_atomic",
                     conv_thr="1.0d-10", with_u=False, occupations="smearing")
    scf += f"HUBBARD (atomic)\nU Cr-3d {U_SEED}\n"

    # The arm is worthless unless it really is the other branch. Each of these is one of the
    # six co-varying differences docs/43 s4-A.3 names; asserting them here is what stops a
    # later edit from quietly turning this into a second TiO2.
    for need, why in (("nspin = 2", "the arm exists to exercise the spin-polarised branch"),
                      ("starting_magnetization(1) = 0.6",
                       "an nspin=2 run seeded at zero moment is a closed-shell run again"),
                      ("occupations = 'smearing'", "production is smeared; hp.x branches on it"),
                      ("smearing = 'mv'", "the campaign's smearing, unchanged"),
                      ("degauss = 0.01", "the campaign's degauss, unchanged"),
                      (CR_UPF, "the only Cr pseudopotential on the box"),
                      (O_UPF, "the same O as the TiO2 arm"),
                      (f"U Cr-3d {U_SEED}", "from-scratch DFPT perturbs an unshifted state")):
        if need not in scf:
            raise SystemExit(f"refusing to write cro2 scf: missing {need!r} -- {why}")
    if "occupations = 'fixed'" in scf:
        raise SystemExit("refusing to write cro2 scf: fixed occupations would make this a "
                         "second closed-shell arm and test nothing new")
    _assert_hp_compatible(scf, "cro2 scf")
    order = _assert_hubbard_atoms_first(scf, "cro2 scf")
    if order[:2] != ["Cr", "Cr"]:
        raise SystemExit(f"refusing to write cro2 scf: expected 2 leading Cr, got {order[:2]}")
    written.append((os.path.join(outdir, "scf__cro2.in"), scf))

    q = "".join(map(str, CRO2_QMESH))
    written.append((os.path.join(outdir, "hp_npert__cro2.in"),
                    hp_namelist("cro2_atomic", "./tmp_cro2_atomic", CRO2_QMESH,
                                determine_num_pert_only=True, find_atpert=1)))
    written.append((os.path.join(outdir, "hp_npert3__cro2.in"),
                    hp_namelist("cro2_atomic", "./tmp_cro2_atomic", CRO2_QMESH,
                                determine_num_pert_only=True, find_atpert=3)))
    written.append((os.path.join(outdir, f"hp_qmesh__cro2_q{q}.in"),
                    hp_namelist("cro2_atomic", "./tmp_cro2_atomic", CRO2_QMESH,
                                determine_q_mesh_only=True, perturb_only_atom=1)))
    written.append((os.path.join(outdir, f"hp__cro2_q{q}.in"),
                    hp_namelist("cro2_atomic", "./tmp_cro2_atomic", CRO2_QMESH,
                                find_atpert=1)))
    jobs.append(dict(system="CrO2", projector="atomic", nq=list(CRO2_QMESH),
                     n_pert_expected=1,
                     n_q_expected=len(_mesh_orbits(CRO2_QMESH, _RUTILE_OPS)),
                     nspin=2, occupations="smearing mv 0.01",
                     file=f"hp__cro2_q{q}.in",
                     role="magnetic/metallic branch, docs/43 s4-A.3 check 4'",
                     pass_condition="a finite U with zero 'Convergence has not been reached'"))
    return written, jobs


# ------------------------------------------------------------------------- Cr(110) slab ---


def _slab_scf_from_source(src_text: str, positions, prefix: str, outdir: str, keep_nosym: bool):
    """Turn `runs/Cr_slab/slab.in` (a relax) into the hp.x-compatible SCF at its own answer.

    Text-patching, not rebuilding: `probe_decks.write_probe` would re-emit the deck from
    parsed fields and silently normalise anything it does not model. The whole point of the
    guard below is that nothing normalises, so the deck is edited in place.
    """
    txt = src_text
    txt = re.sub(r"^(\s*)calculation\s*=\s*'relax'", r"\1calculation = 'scf'", txt, count=1,
                 flags=re.M)
    if "calculation = 'scf'" not in txt:
        raise SystemExit("refusing to write: source deck was not calculation='relax'")
    txt = re.sub(r"^(\s*)prefix\s*=\s*'[^']*'", rf"\1prefix = '{prefix}'", txt, count=1, flags=re.M)
    txt = re.sub(r"^(\s*)outdir\s*=\s*'[^']*'", rf"\1outdir = '{outdir}'", txt, count=1, flags=re.M)
    # relax-only keys: harmless for pw.x but they make the deck lie about what it is
    txt = re.sub(r"^\s*forc_conv_thr\s*=.*\n", "", txt, flags=re.M)
    txt = re.sub(r"^\s*nstep\s*=.*\n", "", txt, flags=re.M)
    txt = re.sub(r"&IONS.*?\n/\n", "", txt, flags=re.S)
    # hp.x differentiates this density; 1e-6 is not enough to differentiate (see build_tio2)
    txt = re.sub(r"^(\s*)conv_thr\s*=\s*\S+", r"\g<1>conv_thr = 1.0d-10", txt, count=1, flags=re.M)
    if not keep_nosym:
        # DECLARED change, `sym` arm only. Production ran nosym/noinv because the adsorbate
        # relaxations needed it (orient_starts.py, docs/41 s2e). For hp.x it is pure cost:
        # measured today, the same slab goes from 15 to 36 irreducible q at nq = 9x4x1 with
        # symmetry off, and n_pert is 6 either way -- so nosym buys 2.4x the bill and no
        # extra information. The two arms exist so the campaign can measure that, not assume it.
        txt = re.sub(r"^\s*nosym\s*=\s*\.true\.\s*\n", "", txt, flags=re.M)
        txt = re.sub(r"^\s*noinv\s*=\s*\.true\.\s*\n", "", txt, flags=re.M)
    # geometry: production start -> the relaxation's own answer
    body = "ATOMIC_POSITIONS angstrom\n"
    src_flags = [ln.split()[4:7] for ln in _POS_RE.search(src_text).group(1).strip().split("\n")]
    if len(src_flags) != len(positions):
        raise SystemExit("refusing to write: coordinate/flag count mismatch")
    for (s, x, y, z), fl in zip(positions, src_flags):
        body += f"  {s}  {x:.8f}  {y:.8f}  {z:.8f}" + ("  " + " ".join(fl) if fl else "") + "\n"
    txt = _POS_RE.sub(lambda _m: body, txt, count=1)
    # U 3.7 -> 1.d-8: the from-scratch DFPT protocol perturbs an unshifted ground state.
    # Declared, and it is the ONE physics field allowed to move.
    # `[ \t]*$`, not `\s*$`: with re.M a greedy `\s*` eats the trailing newline and the deck
    # ends mid-card. pw.x tolerates that; hp.x's own reader is less forgiving, and a deck
    # whose last line has no terminator is exactly the kind of thing that dies silently
    # inside the box's tmux (tasks/lessons.md 2026-07-31, the CRLF lesson's cousin).
    txt = re.sub(r"^(U[ \t]+\S+[ \t]+)[\d.]+[ \t]*$", rf"\g<1>{U_SEED}", txt, count=1, flags=re.M)
    if U_SEED not in txt:
        raise SystemExit("refusing to write: HUBBARD U line not found in source deck")
    if not txt.endswith("\n"):
        txt += "\n"
    return txt


def build_costmodel(outdir: str, repo_root: str):
    os.makedirs(outdir, exist_ok=True)
    src_in = os.path.join(repo_root, CR_SLAB_RUN, "slab.in")
    src_out = os.path.join(repo_root, CR_SLAB_RUN, "slab.out")
    for p in (src_in, src_out):
        if not os.path.exists(p):
            raise SystemExit(f"refusing to write: missing {p}")
    src_text = open(src_in, encoding="utf-8", errors="replace").read()
    pos, prov = parse_final_coordinates(src_out)
    if pos is None or prov != "final":
        raise SystemExit(f"refusing to write: Cr slab geometry provenance is {prov!r}, "
                         f"not a converged 'final' block")
    deck = parse_input_deck(src_in)
    if len(pos) != len(deck["positions"]):
        raise SystemExit("refusing to write: relaxed/deck atom count mismatch")

    written, jobs = [], []
    for arm, keep_nosym in (("sym", False), ("nosym", True)):
        prefix = f"crslab_{arm}"
        scf = _slab_scf_from_source(src_text, pos, prefix, f"./tmp_{prefix}", keep_nosym)
        allowed = {"conv_thr"}          # the only frozen-list field intentionally moved
        moved = _assert_only_intended_changes(src_text, scf, allowed, f"crslab {arm} scf")
        # nosym/noinv are not scalars in _FROZEN_FIELDS, so they need their own assertion --
        # and they need it in BOTH directions. The two arms exist precisely to measure what
        # symmetry buys; an arm that quietly agrees with the other measures nothing.
        has_nosym = bool(re.search(r"^\s*nosym\s*=\s*\.true\.", scf, re.M))
        has_noinv = bool(re.search(r"^\s*noinv\s*=\s*\.true\.", scf, re.M))
        if keep_nosym and not (has_nosym and has_noinv):
            raise SystemExit("refusing to write: the nosym arm lost nosym/noinv")
        if not keep_nosym and (has_nosym or has_noinv):
            raise SystemExit("refusing to write: the sym arm still carries nosym/noinv")
        _assert_hp_compatible(scf, f"crslab {arm} scf")
        order = _assert_hubbard_atoms_first(scf, f"crslab {arm} scf")
        if order[:6] != ["Cr"] * 6:
            raise SystemExit(f"refusing to write: expected 6 leading Cr, got {order[:6]}")
        written.append((os.path.join(outdir, f"{prefix}__scf.in"), scf))

        nqmap = CRSLAB_NQ_MEASURED_SYM if arm == "sym" else CRSLAB_NQ_MEASURED_NOSYM
        written.append((os.path.join(outdir, f"{prefix}__hp_npert.in"),
                        hp_namelist(prefix, f"./tmp_{prefix}", (1, 1, 1),
                                    determine_num_pert_only=True, find_atpert=1)))
        for nq in sorted(nqmap):
            q = "".join(map(str, nq))
            written.append((os.path.join(outdir, f"{prefix}__hp_qmesh_q{q}.in"),
                            hp_namelist(prefix, f"./tmp_{prefix}", nq,
                                        determine_q_mesh_only=True, perturb_only_atom=1)))
        # The ONE measurement block 3Y must not be committed without: a single (atom, q)
        # solve on the real cell at production settings. Everything in the cost table for a
        # slab is currently an extrapolation from TiO2, and tasks/lessons.md 2026-08-05 is
        # explicit that this project's estimates come in low precisely when a cheap system
        # is used as the basis for an expensive one.
        #
        # Finding [11]: the shipped deck ran start_q = 1, and q#1 of ANY mesh is Gamma --
        # the cheapest point that exists. So a second deck at a general q is required, and
        # the index has to be chosen, not assumed. QE generates the mesh with the LAST index
        # fastest, so the 3x2x1 list is (0,0,0), (0,1/2,0), (1/3,0,0), (1/3,1/2,0) and
        # **q#2 is (0,1/2,0), whose small group is the whole 4-operation set: N_k = 15,
        # identical to Gamma.** Timing q#2 would have reproduced the defect. q#3 = (1/3,0,0)
        # keeps only {E, m_y}, N_k = 27, and it is the first slab point that can show what a
        # general q costs. The ordering is not a guess: the same rule predicts the three
        # measured TiO2 q indices (q#2 of 2x2x2 = (0,0,1/2), q#2 of 3x3x3 = (0,0,1/3),
        # q#14 of 4x4x4 = (1/4,1/2,1/4)) and their k-counts exactly.
        qrows = q_table((3, 2, 1), CRSLAB_KMESH,
                        _SLAB_OPS if arm == "sym" else _SLAB_OPS_NOSYM)
        for qi in (1, 3):
            suffix = "" if qi == 1 else f"_q{qi}"
            row = qrows[qi - 1]
            if qi == 3 and row["gamma"]:
                raise SystemExit("refusing to write: the general-q slab timing deck landed "
                                 "on Gamma; re-derive the q index")
            written.append((os.path.join(outdir, f"{prefix}__hp_1atomq{suffix}.in"),
                            hp_namelist(prefix, f"./tmp_{prefix}", (3, 2, 1),
                                        perturb_only_atom=1, start_q=qi, last_q=qi)))
        jobs.append(dict(system=f"CrO2(110) clean slab [{arm}]", n_pert_measured=6,
                         nq_measured={str(k): v for k, v in nqmap.items()},
                         scf_file=f"{prefix}__scf.in",
                         timing_files=[f"{prefix}__hp_1atomq.in (q#1 = Gamma)",
                                       f"{prefix}__hp_1atomq_q3.in (q#3 = general, "
                                       f"predicted N_k = {qrows[2]['n_k']} vs "
                                       f"{qrows[0]['n_k']} at Gamma)"],
                         q_table_3x2x1=qrows,
                         changes_vs_source=sorted(moved) + (
                             ["nosym/noinv removed"] if not keep_nosym else []) +
                         ["calculation", "prefix", "outdir", "positions", "HUBBARD U"]))
    return written, jobs


# ------------------------------------------------------------------------- cost model ---

#: Every number here is a wall-clock measurement, with where it came from. Nothing is a
#: manual figure and nothing is a guess presented as a measurement.
COST_BASIS = {
    "box": "Vast 47025043; cgroup cpu.max 2304000/100000 -> 23.04 usable cores (nproc lies: 48)",
    "tio2_scf_fixedocc": {"np": 12, "nk": 4, "wall_s": 40.5, "scf_iterations": 27,
                          "core_s": 486.0, "ecut": "80/640", "nk_points": 50,
                          "note": "occupations='fixed'; identical E to the smeared run"},
    "tio2_hp_1atomq_qGamma": {"np": 12, "nk": 4, "wall_s": 99.05, "setup_s": 7.49,
                              "lr_iterations": 12, "core_s": 1188.6},
    "tio2_hp_1atomq_q2": {"np": 12, "nk": 4, "wall_s": 85.61, "setup_s": 13.72,
                          "lr_iterations": 9, "core_s": 1027.3},
    "tio2_hp_determine_modes": {"np": 4, "wall_s": 2.9,
                                "note": "both determine_*_only modes exit in ~3 s"},
    "crslab_scf_production": {"np": 32, "nk": 8, "source": "runs/Cr_slab/slab.out",
                              "cold_scf_wall_s": 1795.8, "cold_scf_iterations": 19,
                              "warm_scf_wall_s": 910.6, "warm_scf_iterations": 10,
                              "wall_s_per_scf_iteration": 93.0, "core_s_per_scf_iteration": 2976.0,
                              "note": "measured on the campaign's own 32-core box, NOT this one"},
    "crslab_scf_cheap_thisbox": {"np": 12, "nk": 6, "ecut": "30/240", "kpts": "3 2 1",
                                 "sym_wall_s": 102.0, "nosym_wall_s": 112.9,
                                 "scf_iterations": 32,
                                 "note": "counting deck only -- n_pert and n_q are symmetry "
                                         "counts and do not depend on the cutoff"},
    "tio2_hp_1atomq_q333_q2": {"np": 12, "nk": 4, "printed_k": 208, "s_per_lr_iteration": 12.5,
                               "source": "measured during the 2026-08-09 adversarial review "
                                          "(finding [10]); the third and only non-TRIM point "
                                          "in the timing set, and the one that pins the "
                                          "k-scaling law rather than confirming it"},
    "tio2_hp_printed_k": {"q222_q1_Gamma": 65, "q222_q2_zone_boundary": 130,
                          "q333_q2": 208, "q444_q14_general": 576,
                          "note": "hp.x's 'number of k points=' per q. At Gamma it is the k "
                                  "set alone; elsewhere it is k AND k+q, i.e. 2 * N_k. The "
                                  "Sternheimer solve runs once per k, so the WORK scales "
                                  "with N_k, and q222_q1 and q222_q2 -- printed 65 and 130 "
                                  "-- both have N_k = 65 and cost the same to within 5%."},
    "crslab_symmetry_at_production_cutoff": {
        "np": 18, "nk": 6, "ecut": "80/640", "fft": "45 x 96 x 384", "g_vectors": 841263,
        "sym_ops": 4, "k_points_9x4x1": 15,
        "note": "run with max_seconds=20 so it stops after init; this is the check that the "
                "cheap-cutoff counting is valid. 4 Sym. Ops. at 80/640 == 4 at 30/240 == "
                "spglib Pmm2 on the same coordinates. The k-point count is the second, "
                "unlooked-for prize: 36 (nosym, production) -> 15 with symmetry on."},
}

#: Measured k-point counts for the clean CrO2(110) slab on its production 9x4x1 mesh.
#: The SCF cost scales roughly with this, and it is the largest single lever on the slab bill.
CRSLAB_KPTS = {"nosym": 36, "sym": 15}

#: Linear-response iteration counts. TiO2's are MEASURED (12 at q#1, 9 at q#2). The magnetic
#: ones are ASSUMED and are now the largest single unknown left in this file -- the k-count
#: fix removed the other one.
N_LR = {"TiO2": {"floor": 9, "plan": 12, "ceiling": 15},
        "magnetic": {"floor": 12, "plan": 25, "ceiling": 40}}

#: nspin = 2 uplift per LR iteration. ASSUMED. The Sternheimer system is solved per spin
#: channel so 2.0 is the naive count; the bracket admits shared setup on the low side and a
#: harder response mixing on a metal on the high side.
SPIN_UPLIFT = {"floor": 1.6, "plan": 2.0, "ceiling": 2.5}


def unit_costs():
    """The two constants the model rests on, DERIVED here from COST_BASIS, not remembered.

    Both are per k-point, which is the whole point of the rewrite (findings [10] [11] [19]).
    The shipped model applied one flat 0.308 core-h to all 102 (atom, q) pairs; it was
    measured at nq = 2x2x2, the one mesh whose every q is a time-reversal-invariant momentum,
    and the slab timing was taken at Gamma.

      c_nscf  core-seconds per PRINTED k  -- the NSCF that opens each q diagonalises the k
                                             and k+q sets, so it tracks the printed number
      c_lr    core-seconds per LR iteration per IRREDUCIBLE k (N_k) -- the Sternheimer solve
                                             runs once per k, so it tracks N_k = printed/2
                                             away from Gamma

    Three independent measurements, spanning N_k = 65 and 104 and two different q classes,
    agree on c_lr to a few per cent. That agreement is the evidence for the scaling law; the
    samples are returned so a reader can see the spread instead of taking it on trust.
    """
    g = COST_BASIS["tio2_hp_1atomq_qGamma"]
    z = COST_BASIS["tio2_hp_1atomq_q2"]
    r = COST_BASIS["tio2_hp_1atomq_q333_q2"]
    # N_k for the three timed points, from the validated symmetry model rather than by hand
    nk_g = q_table((2, 2, 2), TIO2_KPTS, _RUTILE_OPS)[0]["n_k"]      # 65, Gamma
    nk_z = q_table((2, 2, 2), TIO2_KPTS, _RUTILE_OPS)[1]["n_k"]      # 65, zone boundary
    nk_r = q_table((3, 3, 3), TIO2_KPTS, _RUTILE_OPS)[1]["n_k"]      # 104
    c_nscf_samples = [g["setup_s"] * g["np"] / nk_g,                 # Gamma prints N_k
                      z["setup_s"] * z["np"] / (2 * nk_z)]           # elsewhere prints 2*N_k
    c_lr_samples = [(g["wall_s"] - g["setup_s"]) * g["np"] / g["lr_iterations"] / nk_g,
                    (z["wall_s"] - z["setup_s"]) * z["np"] / z["lr_iterations"] / nk_z,
                    r["s_per_lr_iteration"] * r["np"] / nk_r]
    c_nscf = sum(c_nscf_samples) / len(c_nscf_samples)
    c_lr = sum(c_lr_samples) / len(c_lr_samples)
    return dict(c_nscf_core_s_per_printed_k=round(c_nscf, 3),
                c_lr_core_s_per_iteration_per_k=round(c_lr, 4),
                c_lr_samples=[round(x, 4) for x in c_lr_samples],
                c_lr_spread_pct=round(100 * (max(c_lr_samples) - min(c_lr_samples)) / c_lr, 1),
                c_nscf_samples=[round(x, 3) for x in c_nscf_samples],
                _c_nscf=c_nscf, _c_lr=c_lr)


def _model_check():
    """Predict the two fully-timed decks and report the residual.

    A cost model that cannot reproduce its own anchors is not a model, so this raises rather
    than warns. It is also the only thing standing between a future edit of COST_BASIS and a
    silently wrong 3Y budget.
    """
    u = unit_costs()
    out = []
    for key, mesh, qi in (("tio2_hp_1atomq_qGamma", (2, 2, 2), 1),
                          ("tio2_hp_1atomq_q2", (2, 2, 2), 2)):
        m = COST_BASIS[key]
        row = q_table(mesh, TIO2_KPTS, _RUTILE_OPS)[qi - 1]
        pred = u["_c_nscf"] * row["printed_k"] + u["_c_lr"] * m["lr_iterations"] * row["n_k"]
        meas = m["wall_s"] * m["np"]
        out.append(dict(deck=key, n_k=row["n_k"], printed_k=row["printed_k"],
                        predicted_core_s=round(pred, 1), measured_core_s=round(meas, 1),
                        residual_pct=round(100 * (pred - meas) / meas, 1)))
    worst = max(abs(o["residual_pct"]) for o in out)
    if worst > 10.0:
        raise SystemExit(f"refusing to write: the cost model misses its own measured anchors "
                         f"by {worst:.1f}% -- {out}")
    return out


def _atomq_core_s(rows, n_lr, uplift=1.0, cell_factor=1.0):
    """Core-seconds for ONE perturbed atom over a list of q rows from `q_table`."""
    u = unit_costs()
    return sum(cell_factor * uplift *
               (u["_c_nscf"] * r["printed_k"] + u["_c_lr"] * n_lr * r["n_k"]) for r in rows)


def slab_timing_projection(np_ranks=18):
    """What each slab timing deck is projected to cost, per arm and per q index.

    The manifest header carries these because under the corrected model they are NOT the
    incidental jobs the shipped header implied. Two of them are most of a working day each,
    and an operator who launches the manifest expecting "everything else exits in seconds"
    finds that out eight hours in.
    """
    slab_scf_per_iter_k = (COST_BASIS["crslab_scf_production"]["core_s_per_scf_iteration"]
                           / CRSLAB_KPTS["nosym"])
    t = COST_BASIS["tio2_scf_fixedocc"]
    cell = slab_scf_per_iter_k / (t["core_s"] / t["scf_iterations"] / t["nk_points"])
    out = {}
    for arm in ("sym", "nosym"):
        ops = _SLAB_OPS if arm == "sym" else _SLAB_OPS_NOSYM
        qr = q_table((3, 2, 1), CRSLAB_KMESH, ops)
        for qi in (1, 3):
            row = qr[qi - 1]
            core_h = {k: _atomq_core_s([row], N_LR["magnetic"][k], SPIN_UPLIFT[k], cell) / 3600.0
                      for k in ("floor", "plan", "ceiling")}
            out[f"{arm}_q{qi}"] = dict(
                n_k=row["n_k"], gamma=row["gamma"],
                q=[round(x, 4) for x in row["q"]],
                core_h=[round(core_h["floor"], 0), round(core_h["plan"], 0),
                        round(core_h["ceiling"], 0)],
                wall_h_at_np=[round(core_h["floor"] / np_ranks, 1),
                              round(core_h["plan"] / np_ranks, 1),
                              round(core_h["ceiling"] / np_ranks, 1)],
                np=np_ranks)
    return out


def cost_table():
    """The projection. Per (atom, q), scaled by the k-count hp.x uses at that q.

    docs/43 s4-A.5 registers the FORM of this model; what follows is its evaluation. Nothing
    here is a flat per-(atom, q) constant any more, and every q carries its own N_k from the
    symmetry model that `_validate_symmetry_model` has already checked against 26 integers
    QE printed on this box.

    The one number this table exists to protect is block 3Y's. It is still EXTRAPOLATED, and
    the assumption carrying it is now visible and singular: n_LR on a magnetic metal.
    """
    rows = []
    u = unit_costs()
    tio2 = N_LR["TiO2"]

    # --- bulk TiO2, per mesh, k-scaled ----------------------------------------------------
    ladder = {}
    for nq in TIO2_QMESH_LADDER:
        qr = q_table(nq, TIO2_KPTS, _RUTILE_OPS)
        ladder[nq] = qr
        core_h = {k: _atomq_core_s(qr, v) / 3600.0 for k, v in tio2.items()}
        rows.append(dict(system="bulk rutile TiO2, 1 perturbed atom", basis="MODEL on MEASURED",
                         arm="-", n_pert=1, nq_mesh="x".join(map(str, nq)), n_q=len(qr),
                         sum_n_k=sum(r["n_k"] for r in qr),
                         n_k_range=[min(r["n_k"] for r in qr), max(r["n_k"] for r in qr)],
                         core_h_floor=round(core_h["floor"], 2),
                         core_h_plan=round(core_h["plan"], 2),
                         core_h_ceiling=round(core_h["ceiling"], 2),
                         flat_model_core_h=round(len(qr) * 0.308, 2)))

    # --- the GO/NO-GO batch: everything in m_hp_tio2.txt that computes a U -----------------
    # 2 projectors x [ q222(6q) + q333(8q) + q444(21q) at 1 atom, + q333(8q) at 2 atoms ]
    batch = []
    for _proj in ("atomic", "ortho-atomic"):
        for nq in TIO2_QMESH_LADDER:
            batch.extend(ladder[nq])
        batch.extend(ladder[(3, 3, 3)] * 2)            # find_atpert = 4 -> both Ti perturbed
    n_atomq = len(batch)
    batch_h = {k: _atomq_core_s(batch, v) / 3600.0 for k, v in tio2.items()}
    scf_h = 2 * COST_BASIS["tio2_scf_fixedocc"]["core_s"] / 3600.0
    flat = n_atomq * 0.308 + 4 * 0.14
    rows.append(dict(system="TiO2 GO/NO-GO batch (2 projectors, every deck that computes U)",
                     basis="MODEL on MEASURED", arm="-", n_pert="1 and 2",
                     nq_mesh="2x2x2 + 3x3x3 + 4x4x4", n_atom_q=n_atomq,
                     sum_n_k=sum(r["n_k"] for r in batch),
                     core_h_floor=round(batch_h["floor"] + scf_h, 1),
                     core_h_plan=round(batch_h["plan"] + scf_h, 1),
                     core_h_ceiling=round(batch_h["ceiling"] + scf_h, 1),
                     flat_model_core_h=round(flat, 1),
                     correction_vs_flat_model=round((batch_h["plan"] + scf_h) / flat, 2),
                     box_hours_at_23_cores=round((batch_h["plan"] + scf_h) / 23.04, 1)))

    # --- the CrO2 arm, docs/43 s4-A.3 -----------------------------------------------------
    cro2 = q_table(CRO2_QMESH, CRO2_KPTS, _RUTILE_OPS)
    cro2_h = {k: _atomq_core_s(cro2, N_LR["magnetic"][k], SPIN_UPLIFT[k]) / 3600.0
              for k in ("floor", "plan", "ceiling")}
    # the CrO2 SCF: TiO2's measured 486 core-s, x2 for nspin and x2.5 for a metal's iteration
    # count at conv_thr 1e-10. Bracketed, not precise; it is 5% of the arm either way.
    cro2_scf_h = 486.0 * 2 * 2.5 / 3600.0
    rows.append(dict(system="bulk rutile CrO2 arm (magnetic, metallic) -- docs/43 s4-A.3",
                     basis="MODEL, spin uplift ASSUMED", arm="atomic", n_pert=1,
                     nq_mesh="x".join(map(str, CRO2_QMESH)), n_q=len(cro2),
                     sum_n_k=sum(r["n_k"] for r in cro2),
                     core_h_floor=round(cro2_h["floor"] + cro2_scf_h, 1),
                     core_h_plan=round(cro2_h["plan"] + cro2_scf_h, 1),
                     core_h_ceiling=round(cro2_h["ceiling"] + cro2_scf_h, 1),
                     wall_min_at_np20=round((cro2_h["plan"] + cro2_scf_h) * 60 / 20, 0),
                     note="docs/43 s4-A.3 estimates 'roughly ten minutes of the box'. The "
                          "measured-anchored model says 20-50 min at NP=20 including its "
                          "SCF. Still cheap, still required; the ten-minute figure should "
                          "not be quoted as the cost."))

    # --- block 2C: 7 metals, bulk ---------------------------------------------------------
    m3 = q_table((3, 3, 3), TIO2_KPTS, _RUTILE_OPS)
    for tag in ("floor", "plan", "ceiling"):
        per_metal = (_atomq_core_s(m3, N_LR["magnetic"][tag], SPIN_UPLIFT[tag]) / 3600.0
                     + cro2_scf_h)
        rows.append(dict(system="block 2C: 7 metals bulk, 2 projectors, nq 3x3x3",
                         basis="PROJECTED", arm=tag, n_pert=1, nq_mesh="3x3x3", n_q=len(m3),
                         sum_n_k=sum(r["n_k"] for r in m3),
                         core_h_total=round(per_metal * 7 * 2, 0)))

    # --- one clean slab, EXTRAPOLATED -- the number block 3Y rests on ----------------------
    # Per-k form. The slab SCF iteration was measured at 2976 core-s over 36 k = 82.7 core-s
    # per iteration per k; TiO2's is 486/27/50 = 0.36. Their ratio is the CELL factor, and
    # applying it per k is what stops the cell cost and the symmetry saving being conflated.
    # That conflation is exactly where the old R_iter = 5.54 came from: it divided a 65-k LR
    # iteration by a 50-k SCF iteration and kept the difference as physics.
    slab_scf_per_iter_k = (COST_BASIS["crslab_scf_production"]["core_s_per_scf_iteration"]
                           / CRSLAB_KPTS["nosym"])
    tio2_scf = COST_BASIS["tio2_scf_fixedocc"]
    tio2_scf_per_iter_k = (tio2_scf["core_s"] / tio2_scf["scf_iterations"]
                           / tio2_scf["nk_points"])
    cell_factor = slab_scf_per_iter_k / tio2_scf_per_iter_k
    for arm, nq, n_pert, note in (
            ("nosym", (3, 2, 1), 6, "as production runs today"),
            ("sym", (3, 2, 1), 6, "symmetry on"),
            ("sym", (2, 1, 1), 6, "+ smaller q-mesh"),
            ("sym", (2, 1, 1), 2, "+ split Cr into surface/subsurface ATOMIC_SPECIES types "
                                  "with identical U and perturb only the surface pair"),
            ("sym", (1, 1, 1), 2, "Gamma-only q -- CHEAPEST, and NOT a q-converged U")):
        ops = _SLAB_OPS if arm == "sym" else _SLAB_OPS_NOSYM
        qr = q_table(nq, CRSLAB_KMESH, ops)
        measured_nq = (CRSLAB_NQ_MEASURED_SYM if arm == "sym"
                       else CRSLAB_NQ_MEASURED_NOSYM).get(nq)
        if measured_nq is not None and len(qr) != measured_nq:
            raise SystemExit(f"refusing to cost: slab {arm} nq{nq} model q-count {len(qr)} "
                             f"disagrees with the measured {measured_nq}")
        tot = {k: n_pert * _atomq_core_s(qr, N_LR["magnetic"][k], SPIN_UPLIFT[k],
                                         cell_factor) / 3600.0
               for k in ("floor", "plan", "ceiling")}
        gamma_only = n_pert * len(qr) * _atomq_core_s(
            [qr[0]], N_LR["magnetic"]["plan"], SPIN_UPLIFT["plan"], cell_factor) / 3600.0
        rows.append(dict(system="CrO2(110) clean slab", basis="EXTRAPOLATED",
                         arm=f"{arm}: {note}", n_pert=n_pert,
                         nq_mesh="x".join(map(str, nq)), n_q=len(qr),
                         n_k_per_q=[r["n_k"] for r in qr],
                         core_h_floor=round(tot["floor"], 0),
                         core_h_plan=round(tot["plan"], 0),
                         core_h_ceiling=round(tot["ceiling"], 0),
                         gamma_anchored_core_h=round(gamma_only, 0),
                         gamma_understatement=round(tot["plan"] / gamma_only, 2),
                         box_days_at_23_cores=round(tot["plan"] / 23.04 / 24, 1)))

    return dict(
        prereg="docs/43 s4 (P15) + AMENDMENT 1 s4-A. This table EVALUATES the registered "
               "model; it does not define it, widen it or reinterpret it.",
        model=("core_s(atom, q) = c_nscf * printed_k(q) + c_lr * n_LR * N_k(q), where "
               "printed_k = N_k at Gamma and 2*N_k elsewhere, and N_k comes from the "
               "symmetry model validated against 26 measured integers."),
        unit_costs=u,
        model_self_check=_model_check(),
        symmetry_model=dict(
            measured_integers_reproduced=_validate_symmetry_model(),
            rutile_ops=len(_RUTILE_OPS), slab_ops_sym=len(_SLAB_OPS),
            why="hp.x reduces its NSCF k-set with the operations that leave the PERTURBED "
                "atom fixed -- 8 of rutile's 16 -- which is why its Gamma NSCF prints 65 k "
                "where the pw.x SCF on the same 6x6x8 mesh prints 50.",
            n_k_by_mesh={"x".join(map(str, nq)): [r["n_k"] for r in
                                                  q_table(nq, TIO2_KPTS, _RUTILE_OPS)]
                         for nq in TIO2_QMESH_LADDER},
            slab_n_k_by_mesh={f"{arm} {'x'.join(map(str, nq))}":
                              [r["n_k"] for r in q_table(
                                  nq, CRSLAB_KMESH,
                                  _SLAB_OPS if arm == "sym" else _SLAB_OPS_NOSYM)]
                              for arm in ("sym", "nosym") for nq in ((3, 2, 1), (2, 1, 1))}),
        what_changed_and_why=[
            "[10] the flat 0.308 core-h per (atom,q) is gone. It was measured at nq=2x2x2, "
            "the one mesh whose every q is a TRIM, so hp.x got maximum symmetry reduction at "
            "every point that fed the model. See correction_vs_flat_model in the batch row.",
            "[10] the review proposed scaling by the PRINTED k-count. Measured, that "
            "over-costs every non-Gamma q by 2x: q#1 printed 65 and cost 7.63 s per LR "
            "iteration; q#2 printed 130 -- twice as many -- and cost 8.0 s, five per cent "
            "more. The printed count includes the k+q set, which the NSCF diagonalises but "
            "the Sternheimer solve does not iterate over. The scaling variable is N_k = "
            "printed/2 away from Gamma, and the review's own third point settles it: 12.5 s "
            "at N_k = 104 against 7.8 s at N_k = 65 is a ratio of 1.60 against 1.60.",
            "[11] the slab timing decks. q#1 is Gamma on every mesh, and on the 3x2x1 slab "
            "mesh q#2 = (0,1/2,0) is ALSO fully symmetric (N_k = 15, the same as Gamma), so "
            "the review's proposed start_q=2 would have re-measured the defect. The added "
            "deck is q#3 = (1/3,0,0), N_k = 27. Each slab row carries the "
            "gamma_understatement factor the Gamma-only anchor was missing.",
            "the old R_iter = 5.54 conflated a 65-k LR iteration with a 50-k SCF iteration. "
            "Per k it is 4.3, and the slab extrapolation now carries the cell factor and the "
            "k count separately.",
        ],
        assumptions=[
            "n_LR on a magnetic metal is ASSUMED (floor 12 / plan 25 / ceiling 40); TiO2 "
            "measured 9 and 12. This is the largest single unknown in the table and it is "
            "what runs/hp_costmodel/*_hp_1atomq_q3.in exists to remove.",
            "the nspin = 2 uplift per LR iteration is ASSUMED (1.6 / 2.0 / 2.5).",
            "ortho-atomic projectors are costed at the same rate as atomic; unmeasured.",
            "slab SCF cost is the campaign's own measurement on a 32-core box "
            "(runs/Cr_slab/slab.out), not on this 23.04-core one; core-seconds are used "
            "throughout so the two are comparable, but parallel efficiency is not identical.",
            "hp.x on the slab may reduce the k-set further than pw.x did (it keeps only the "
            "operations that fix the perturbed Cr), so the slab N_k here are LOWER bounds "
            "between the measured 15 at Gamma and the unreduced 36.",
            "tasks/lessons.md 2026-08-05: this project's last three compute estimates came "
            "in 2.4x, 2.5x and 3.5x low, every one of them extrapolated from a cheaper "
            "system. The slab rows are exactly that shape. Treat 'plan' as a floor and run "
            "runs/hp_costmodel/crslab_sym__hp_1atomq_q3.in before committing block 3Y.",
        ],
        n_lr=N_LR, spin_uplift=SPIN_UPLIFT,
        slab_cell_factor_vs_tio2_per_iteration_per_k=round(cell_factor, 1),
        table=rows)


# ------------------------------------------------------------------------------ driver ---


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--tio2-out", default="runs/hp_tio2")
    ap.add_argument("--cost-out", default="runs/hp_costmodel")
    ap.add_argument("--check-only", action="store_true",
                    help="run every guard and print what WOULD be written; write nothing")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    # The cost model is only allowed to extrapolate if it still reproduces every
    # integer QE has printed. Checked FIRST so a mismatch costs nothing.
    n_int = _validate_symmetry_model()
    print(f"symmetry model reproduces {n_int} measured integers")

    root = os.path.abspath(a.repo_root)
    tio2_dir = os.path.join(root, a.tio2_out)
    cost_dir = os.path.join(root, a.cost_out)

    # Build EVERYTHING first, so that a guard tripping on the last deck leaves no half-written
    # batch on disk. build_basin_restarts.py's failure mode, avoided by construction.
    tio2_files, tio2_jobs = build_tio2(tio2_dir)
    cro2_files, cro2_jobs = build_cro2(tio2_dir)
    cost_files, cost_jobs = build_costmodel(cost_dir, root)
    tio2_files = tio2_files + cro2_files
    tio2_jobs = tio2_jobs + cro2_jobs

    # Manifest for queue_hp.sh: <dir> <scf-basename> <hp-basename> <nk>. One line per hp.x
    # job; the scf is named on every line and queue_hp.sh runs it once and reuses the .save,
    # because the q-mesh ladder is six hp.x runs against ONE ground state and re-running the
    # SCF per rung would triple the bill for nothing.
    #
    # NCONC: every line in a manifest that shares a prefix shares hp.x's Sternheimer buffers,
    # which are named from prefix and MPI rank only. Two rungs at one prefix were MEASURED
    # colliding (run B died, exit code 2) and, worse, could have survived reading each other's
    # half-written .wfcN. queue_hp.sh refuses NCONC > 1 on a repeated prefix; parallelism has
    # to come from different prefixes. NP x NCONC <= 23 (cgroup 23.04 cores).
    tio2_lines = ["# hp.x GO/NO-GO: bulk rutile TiO2 (2 projectors) + the magnetic, metallic",
                  "# bulk CrO2 arm that docs/43 s4-A.3 requires. Lines: <dir> <scf> <hp> <nk>.",
                  "# Acceptance criteria live in docs/43 s4 + s4-A; this manifest runs them,",
                  "# it does not judge them. Counting decks (hp_npert/hp_npert3/hp_qmesh)",
                  "# exit in ~3 s. hp_npert3 is find_atpert=3, which criterion I5 needs.",
                  "#",
                  "# RUN AS: bash queue_hp.sh m_hp_tio2.txt 20 1",
                  "#   nk=4  -> NP must be an exact multiple of 4 (pw.x and hp.x both abort",
                  "#            otherwise). NP x NCONC <= 23 (cgroup 2304000/100000 = 23.04",
                  "#            usable cores; nproc says 48 and is wrong).",
                  "#   NCONC MUST be 1: the three prefixes below each appear on many lines,",
                  "#            and hp.x names its scratch from prefix + rank alone.",
                  "# The CrO2 arm is the one that licenses block 2C. Order it LAST here only",
                  "# because its SCF is the most likely to fail; nothing depends on it first."]
    for tag in ("atomic", "ortho", "cro2"):
        for path, _ in tio2_files:
            base = os.path.basename(path)[:-3]
            if base.startswith((f"hp_npert__{tag}", f"hp_npert3__{tag}",
                                f"hp_qmesh__{tag}", f"hp__{tag}")):
                tio2_lines.append(f"hp_tio2 scf__{tag} {base} 4")
    # One timing rung, ~3 min, and it is the cheapest falsification available: q#3 of the
    # 2x2x2 mesh is (0,1/2,0) with N_k = 100, the first TiO2 point whose k-count differs from
    # the two already timed (both N_k = 65). If the k-scaling law is wrong, this is where it
    # shows -- on a six-atom cell, before the slab bill depends on it.
    tio2_lines.append("hp_tio2 scf__atomic hp_1atomq__atomic_q3 4")
    manifest_tio2 = "\n".join(tio2_lines) + "\n"

    stp = slab_timing_projection(np_ranks=18)
    manifest_cost = "\n".join(
        ["# hp.x cost model. The *_hp_1atomq* lines are the ONLY thing that has to run before",
         "# block 3Y can be costed honestly; everything else exits in seconds. They are NOT",
         "# cheap -- each is one linear-response solve on an 18-atom magnetic +U slab at",
         "# production cutoffs, and each needs a production SCF in front of it. Under the",
         "# k-scaled model these are the projections, floor / plan / ceiling WALL HOURS at",
         "# NP=18, and they are the reason this manifest is not a background errand:"]
        + [f"#     {k:<9} N_k={v['n_k']:<3} q={v['q']}  {v['wall_h_at_np']} h"
           + ("   <- Gamma" if v["gamma"] else "")
           for k, v in stp.items()]
        + ["# Launch the sym arm first and read its wall clock before paying for nosym.",
           "#"]
        + [
         "# RUN AS: bash queue_hp.sh m_hp_costmodel.txt 18 1",
         "#   nk=6  -> NP must be 6, 12 or 18. NP x NCONC <= 23 (cgroup = 23.04 usable",
         "#            cores), so NP=18 forces NCONC=1 by itself.",
         "#   NCONC MUST be 1 for a second reason: these lines are TIMINGS. A wall clock",
         "#            taken while another job competes for a throttled cgroup is not a cost",
         "#            basis, it is the mechanism behind the 2.4x/2.5x/3.5x mis-costings in",
         "#            tasks/lessons.md 2026-08-05.",
         "#",
         "# q#1 of EVERY mesh is Gamma -- the cheapest point that exists -- so the _q3 decks",
         "# are the ones block 3Y must be costed from. q#3 of the 3x2x1 mesh is (1/3,0,0),",
         "# predicted N_k = 27 against 15 at Gamma. (q#2 is (0,1/2,0), which is ALSO fully",
         "# symmetric and would have re-measured Gamma's cost under a different name.)",
         "# CHECK against the .out: hp.x prints the q coordinates and 'number of k points='.",
         "hp_costmodel crslab_sym__scf   crslab_sym__hp_npert      6",
         "hp_costmodel crslab_sym__scf   crslab_sym__hp_qmesh_q211 6",
         "hp_costmodel crslab_sym__scf   crslab_sym__hp_qmesh_q321 6",
         "hp_costmodel crslab_sym__scf   crslab_sym__hp_1atomq     6",
         "hp_costmodel crslab_sym__scf   crslab_sym__hp_1atomq_q3  6",
         "hp_costmodel crslab_nosym__scf crslab_nosym__hp_npert    6",
         "hp_costmodel crslab_nosym__scf crslab_nosym__hp_1atomq   6",
         "hp_costmodel crslab_nosym__scf crslab_nosym__hp_1atomq_q3 6"]) + "\n"

    payload = dict(
        note=("Block 1B artifacts. hp.x GO/NO-GO target + cost model. Every timing in "
              "cost_basis is a wall-clock measurement on the stated box; the slab "
              "per-(atom,q) figures are EXTRAPOLATIONS and are labelled as such."),
        prereg=dict(
            document="docs/43 s4 (P15) as amended by AMENDMENT 1 s4-A (commit 0244f4e)",
            rule="docs/43 is the ONLY pre-registration. This file and this JSON register "
                 "nothing; where they disagree with docs/43, docs/43 wins.",
            external_window="see docs/43 s4-A.1. NOT copied here on purpose: three builders "
                            "wrote a contradicting copy of a registered rule into a source "
                            "file on 2026-08-09, and a widened acceptance window sitting in "
                            "a build artifact is the single most damaging thing an STS judge "
                            "could find. The value is read from the pre-registration or not "
                            "at all. What is recorded here is only that the build round's "
                            "proposed widening was REJECTED.",
            withdrawn="perturbation-amplitude independence -- hp.x is DFPT and the binary "
                      "has no amplitude keyword, so the check was unperformable, not merely "
                      "unmet (docs/43 s4-A.2). Replaced by the CrO2 arm (s4-A.3).",
            demoted_to_diagnostic=CHI_SYMMETRY_IS_AN_IDENTITY),
        built="2026-08-09",
        pseudopotentials=dict(Ti=dict(file=TI_UPF, type="ultrasoft (GBRV)", zval=12),
                              Cr=dict(file=CR_UPF, type="ultrasoft (GBRV)"),
                              O=dict(file=O_UPF, type="PAW (PSlibrary)", zval=6),
                              note="the only Ti, only Cr and only O in "
                                   "/usr/share/espresso/pseudo"),
        hp_constraints_from_binary=[why for _, why in _HP_FORBIDDEN] + [
            "Hubbard_projectors must be 'atomic' or 'ortho-atomic'",
            "a HUBBARD card must be present in the pw.x run",
            "Hubbard atoms must be listed first in ATOMIC_POSITIONS (warning only)",
            "determine_q_mesh_only requires perturb_only_atom",
            "a gapped system must NOT be run with smearing (measured, not documented)"],
        tio2_jobs=tio2_jobs, costmodel_jobs=cost_jobs,
        slab_timing_projection=slab_timing_projection(np_ranks=18),
        cost_basis=COST_BASIS, cost_projection=cost_table())

    if a.check_only:
        for path, _ in tio2_files + cost_files:
            print(f"WOULD WRITE {path}")
        print(json.dumps(payload["cost_projection"], indent=2))
        print(f"\nall guards passed; {len(tio2_files) + len(cost_files)} decks pending")
        return 0

    for path, text in tio2_files + cost_files:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # LF only: a CRLF .in dies silently inside the box's tmux (lessons.md 2026-07-31)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"wrote {path}")

    for path, text in ((os.path.join(tio2_dir, "m_hp_tio2.txt"), manifest_tio2),
                       (os.path.join(cost_dir, "m_hp_costmodel.txt"), manifest_cost)):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"wrote {path}")

    with open(os.path.join(cost_dir, "cost_model.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    print(f"wrote {os.path.join(cost_dir, 'cost_model.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
