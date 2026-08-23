#!/usr/bin/env python3
"""LIT-2 readout: the static CHE surface Pourbaix of docs/43 A5.2, scored against docs/43.

WHAT THIS MEASURES
------------------
docs/43 AMENDMENT 5 §A5.2 registers a *static* computational-hydrogen-electrode (CHE)
surface Pourbaix over the terminations a 2x1 rutile(110) cell can hold:

    clean / 1 ML *O_cus ("O_full") / mixed 1:1 *OH-*O ("mixed_OH_O") / 1 ML *OH ("OH_full")
    (+ an O-depleted variant for Cr, "cov_Ovac": the 2x1 clean cell minus one bridging O)

with block-1A outputs REUSED where they already are these states (A5.2: "reused, not
re-run") and three genuinely new relaxations (Cr cov_2OH, Cr cov_Ovac, Ru cov_2OH). The
manifest of record is `runs/probe/lit2_manifest.json`; this program reads it and scores
whatever is on disk. Two registered readouts come out:

  1. the RuO2 benchmark (A5.2, two-sided, registered before any job ran): the lowest-dG
     termination with falling potential must run full-O -> mixed -> full-*OH, and the two
     transition potentials must land within +/-0.25 V of Qiu 2026's AIMD brackets (~1.50 V
     and ~1.24 V). PASS -> the Cr column is "validated-by-proxy"; FAIL -> "vacuum-CHE-only"
     with the measured RuO2 discrepancy attached as its systematic error. Neither outcome
     gates any 1A/1B/1C result.
  2. the Cr decision rule (Cao's oxygen-environment finding in CHE-at-U form): if Cr
     prefers an O-covered termination by > 0.1 eV PER SITE at U* = 1.23 V + eta(Cr), every
     clean-termination Cr energetics row carries a CONDITIONAL-ON-TERMINATION flag. The flag
     qualifies; it does not retract (P7's withdrawal already stands on U-sensitivity alone).

WHERE THE RULE LIVES
--------------------
**docs/43-prereg-week1-factorial.md A5.2 and A5.7 (AMENDMENT 5), with the GATE-1 child
rule of amendment 4 §2 / §2-A.3(b) / §5 (P16), the §1 sign constraint on mirror-vs-off
arms, the §2-A.1 off-plane start (>= 0.30 A + nosym/noinv) and the §0a.2 obligation to
cite a measured max|F_y|.** This file holds NO copy of the rule: `--print-prereg` reads
those clauses out of docs/43 and prints them. The registered numbers below each carry the
clause they come from, and at runtime the program checks that the anchor phrase still
appears in the document (a restructured docs/43 prints a loud warning rather than silently
scoring against a stale constant). **Where this file and docs/43 disagree, docs/43 wins and
this file is the defect** (docs/43 amendment 1: "In-code rules must be a pointer to it,
never a copy").

This is analysis infrastructure in the sense of `hessian_analyze.py`: AI-written,
disclosed, changes no registered threshold. Thresholds are READ (0.25 V, ~1.50/~1.24 V,
0.1 eV per site, 1.23 V + eta(Cr), 5 meV, +0.02 eV, 0.30 A) and quoted with their clause.

WHAT IS COMPUTED, EXACTLY
-------------------------
Per metal, per registered rung, with E_clean the 2x1 clean slab (ref__2x1v) as reference,
for a termination carrying n_O extra *O and n_OH extra *OH relative to clean:

    dG(U) = [E_term - E_clean - n_O*(E_H2O - E_H2) - n_OH*(E_H2O - 1/2 E_H2)]
            + n_O*corr_O + n_OH*corr_OH - (2 n_O + n_OH) * e * U          (RHE scale)

with corr_O = 0.05 eV, corr_OH = 0.35 eV = `hea_oer.referencing.ZPE_TS_CORRECTION` (the
project's CHE convention; Man 2011 / Valdes 2008). E_H2O, E_H2 are the metal's registered
gas references from the manifest (`geometry.gas_references`, Martyna-Tuckerman boxes,
reuse is exact, and they must pass QC). n_e = 2 n_O + n_OH is the electron count of the
termination relative to clean. dG_clean(U) = 0 by construction. "Per site" divides by the
TWO cus sites of a 2x1 cell (N_SITES = 2, verified from the cell vector against the
manifest's a1; docs/43 does not define "site" -- see C8). The ladder also prints a
per-adsorbate-unit column (per cell / (|n_O| + |n_OH|)) because per-site equals
per-adsorbate only at full coverage (the 1/2 ML context rung and cov_Ovac differ by 2x).

n_O / n_OH are NOT taken from the rung's name. They are derived from the deck's
ATOMIC_POSITIONS by stoichiometry against the clean deck (dO = n_O_atoms - n_O_atoms,clean,
dH likewise; n_OH = dH, n_O = dO - dH; metal count must be unchanged), cross-checked
geometrically (every added atom must sit above the clean slab's top atomic layer by
> 0.30 A; every H must have an O within 1.15 A; every removed atom is identified by
nearest-neighbour matching against the clean deck and must lie in the clean top layer),
and then compared with the nominal composition of the rung (O_full 2 *O; mixed 1 *O + 1
*OH; OH_full 2 *OH; cov_Ovac n_O = -1; clean 0). The termination's IDENTITY is then re-verified on the
parent's FINAL geometry ('Begin final coordinates' of the .out): atom identities cannot
change during a relaxation, so what is re-checked is geometric -- every ADDED atom (no
clean counterpart within 0.60 A at start) must still sit > 0.30 A above the clean top
layer, every H must still have an O within 1.15 A, and an ADDED H's nearest O must be an
ADDED O (an H whose nearest O is a lattice O has migrated off its *OH: same stoichiometry,
no longer the registered termination -- the failure mode a start-deck-only check cannot
see). Any disagreement (start or final) is printed and the rung is NOT scored.

QC is strict and reused, not reinvented: `src/dft/qe_qc.py::scan` is the record and
`trusted_energy_ev(strict=True)` the energy (the predicate is verdict == TRUSTWORTHY; this
file adds belt-and-braces 'bfgs converged' on relax decks and a 'convergence has been
achieved' line). 'JOB DONE' alone is never success -- three incidents in tasks/lessons.md.
Energies are pw.x Ry x RY_EV from qe_qc (13.605693122 eV/Ry; CODATA-2018 is
13.605693122994 -- the 1e-9 eV/Ry truncation is below 1e-5 eV on every dG here because dG
is a difference of ~3300 Ry quantities, so no number changes to the printed 4 decimals).

GATE-1 (Cr, required): for every Cr rung the `__g1` fresh-density fixed-geometry SCF next
to the parent (...__g1.out) is read. The child must be THE REGISTERED CHILD (am.4 §2: "at
its own final coordinates, at the parent's own symmetry treatment, k-mesh and cell" --
"a GATE-1 child that changes nosym or the k-set at the same time attributes nothing"; am.4
§4: "a control that cannot fail controls nothing"). Checked, all of them, and the message
says which: calculation = 'scf'; fresh density ('Initial potential from superposition of
free atoms' in the child .out, no startingpot/startingwfc = 'file' in the deck);
nosym/noinv equal to the parent deck's; the pw.x symmetry line equal; K_POINTS card and
the printed k-point count equal; CELL_PARAMETERS equal to 1e-3 A; nat, nspin, ecutwfc,
ecutrho, pseudopotentials and the HUBBARD card equal; child ATOMIC_POSITIONS equal to the
parent's 'Begin final coordinates' (same species sequence, max|dx| <= 1e-4 A, same unit).
A failure -> 'CHILD NOT THE REGISTERED CHILD' and the row is NOT SCOREABLE. A child .out
without its __g1.in -> 'CHILD DECK MISSING'.

  The energy of record of a Cr row is the CHILD's (am.4 §2; the block-1A evaluator
  `build_cellsym_pilot.py::gate1_passed` scores from the child in every case, provenance
  'gate1 SCF'). Verdicts: |E_child - E_parent| <= 5 meV -> AGREE (child quoted; parent
  identical to <= 5 meV, both printed). Otherwise BASIN_DRIFT, either sign. docs/43 gives
  two readings of a drift and this program prints BOTH, applying one as the default and
  naming the fork (C9, `--gate1-drift`):
    am.4 §2 (DEFAULT): "else BASIN_DRIFT, in which case the GATE-1 SCF energy is the
      corrected value ... and the pair is scored from it" -> the row IS scored, from the
      child, provenance 'gate1 SCF (am.4 §2), 4 meV residual (§5)'; the parent-based dG0
      is printed beside it.
    §5-strict: "If that SCF lands >= 5 meV lower, the state is re-relaxed from it and the
      loop repeats" -> the row is NOT SCOREABLE, re-relax owed; the child-based dG0 (§5's
      own permitted substitution "with a stated 4 meV residual") is printed beside it.
  A child ABOVE the parent by > 5 meV is BASIN_DRIFT too under am.4 §2's wording but is
  marked INTERPRETIVE (§5's loop names only "lands >= 5 meV lower"; the LIT-3 GATE-1 readout
  recorded children above parents as an entrant call). Child missing -> NOT SCOREABLE
  'GATE-1 child pending' (am.4 §2: "a precondition of the readout"). Total AND absolute
  magnetisation of child vs parent are reported with the 0.1 mu_B channels of amendment 4
  §3; they are REPORTED, not gated, for GATE-1 (am.4 §3 names pairs and GATE C, not GATE-1).

GATE-1 (Ru, not required): the manifest sets gate1_required = false for every Ru row and
the Ru deck is nspin = 1 (no magnetic basin to drift); am.4 §2 and A5.7 name Cr. docs/43 is
not unambiguous (§5 P16: "Every relaxation in this campaign, in every block, gets a GATE-1
fresh-density fixed-geometry SCF"; A5.2's standing-protocol sentence qualifies only the
magnetisation channels 'for Cr'). Stated as C10; if a Ru __g1.out is ever on disk it is
read and reported (informational; the parent stays the energy of record).

OFF-PLANE RECORD (A5.7 + §0a.2 + §2-A.1): A5.7 registers that "every new relaxation of any
metal follows the off-plane/nosym standing protocol with measured max|F_y| recorded
(§0a.2)", and §0a.2 that "any claim that a state was searched off-plane must cite its
measured max|F_y|, never the presence of the flag". For EVERY row this program prints the
deck's nosym/noinv, the measured start off-plane displacement (per atom: half the y-gap
between the atom and the nearest same-species atom at its sigma_y image position, which is
0 for on-plane or mirror-paired atoms and the applied kick for a y-displaced one), the
atoms started >= 0.30 A off-plane ("kicked"), max|F_y| on the kicked atoms and on all free
atoms at the FIRST ionic step, the start->final |dy| of the kicked atoms and their final
off-plane distance, and (for the three LIT-2 relaxations) the manifest's recorded
max_start_dy beside the measured one. An arm is labelled 'off (measured)' only when the
deck has nosym AND noinv, at least one atom was started >= 0.30 A off-plane and a first-
step F_y was read from the .out; otherwise 'off (by name only: <why>)'. Nothing is gated
on this record; it is the citation A5.7/§0a.2 require.

EVERY CHOICE THIS PROGRAM MAKES THAT docs/43 A5.2 DOES NOT MAKE FOR IT
----------------------------------------------------------------------
These are printed in the output under "ENTRANT DECISIONS FLAGGED" and carried in the JSON.

  C1  The _mir/_off arm. The O_full and mixed rungs each have a mirror-constrained arm
      and an off-plane arm on disk (block 1A). A5.2 is silent on which energy is the
      rung's, but docs/43 §1 is NOT silent on the comparison: "dE_sym = E(off-plane,
      GATE-1-passed) - E(mirror, GATE-1-passed) <= 0 by construction -- an additional
      search direction cannot raise the minimum. Any dE_sym > +0.02 eV is a failure of the
      search or of the comparison, not a physical result, and voids that arm". So, on the
      energies of record: dE_sym > +0.02 eV -> the off arm is VOID (§1), the mirror arm is
      the rung and the entrant must confirm the pair is comparable (same spectator
      arrangement / final composition, magnetisation within 0.1 mu_B -- printed); if it is
      not comparable the mirror arm simply stands alone, if it is comparable the off-plane
      search failed and a re-search is owed. |dE_sym| <= 0.02 eV -> degenerate within the
      §1 tolerance: lowest-energy scoreable arm (C1 default; <= 5 meV is additionally
      flagged as below the relaxation's resolution). dE_sym < -0.02 eV -> the off arm is
      lower, as §1 expects: taken. §1 is applied only when BOTH arms are scoreable (it is
      stated on GATE-1-passed energies); when only one arm is scoreable that arm is taken
      and, if the unscoreable arm is LOWER on disk, the rung is flagged PROVISIONAL. Both
      arms are always printed with their energies, statuses and the flag that applied.
  C2  "O-covered termination" in the Cr rule is read as the *O-bearing rungs (O_full,
      mixed) -- the DEFAULT. The inclusive reading (OH_full counted too: Cao's three-way
      O-covered / stoichiometric / O-depleted classification does not exclude a full *OH
      cover) is evaluated and printed as a SECOND verdict line (NOT SCOREABLE while
      OH_full is pending). cov_Ovac is a registered rung (it enters the Cr envelope) but is
      CONTEXT for the decision rule. The 1/2 ML context rung is printed at U* too (C7).
  C3  The benchmark ordering (i) is judged on the ANALYTIC lower envelope of the registered
      terminations (clean included, it is the reference state): start at the largest-n_e
      rung (stable as U -> +inf) and repeatedly take the highest remaining crossing below
      the current U until the smallest-n_e rung is reached -- the exact sequence of lowest-
      dG terminations with falling U over ALL U, no scan window (a 2.0 -> 0.8 V scan is
      printed as a table only). (i) holds iff O_full -> mixed -> OH_full is a subsequence.
      Equivalently: mixed is on the envelope iff U(O_full/mixed) > max(U(mixed/OH_full),
      U(mixed/clean)); OH_full then follows iff U(mixed/OH_full) > U(OH_full/clean) -- so
      (i) couples to clean: if clean undercuts mixed before OH_full does, OH_full never
      appears (it cannot undercut clean at lower U, its slope is steeper). The ALTERNATIVE
      reading that ignores clean ("U(O_full/mixed) > U(mixed/OH_full), a non-empty mixed
      window") is printed beside it. The transition potentials for (ii) are analytic line
      crossings U(A/B) = [dG_A(0) - dG_B(0)] / (n_e,A - n_e,B).
  C4  The benchmark PASS rule is a conjunction. The program reports FAIL as soon as one
      conjunct is falsified by rungs on disk (PASS unreachable), marking the verdict
      basis PARTIAL until the ladder completes; whether to HOLD the public verdict until
      the ladder completes is a reporting choice for the entrant -- the outcome cannot
      change.
  C5  ZPE/TS for the Cr O-vacancy rung: the formula's n_O*corr_O is applied literally
      with n_O = -1 (i.e. -0.05 eV). A5.2 registers no separate correction for a
      removed lattice O; the choice is 0.05 eV either way and is flagged.
  C6  eta(Cr) is read from `data/tiers/tier_v2.json` (the frozen tier of record,
      docs/43 §0; tier_v1 + the three docs/41 §6f basin restarts) -- the tier version and
      its provenance string are printed. A different tier changes U*, not the rule.
  C7  The CONTEXT-ONLY ref__2x1o rung (1/2 ML *O) is printed with its dG0 AND its value at
      U* but never enters the scored ladder, the envelope, or either verdict (manifest
      registered_ambiguities; entering would need its own amendment). Because it is the
      most decision-relevant Cr number on disk, the decision block states whether the
      flag WOULD read ON or OFF if it were admitted by amendment.
  C8  "per site" = per cus site, N_SITES = 2 for a 2x1 cell. docs/43 does not define
      "site"; the per-cell reading (threshold applied to the per-cell number) is printed
      beside the per-site verdict.
  C9  GATE-1 BASIN_DRIFT: am.4 §2 (score from the child) is the default, §5-strict
      (NOT SCOREABLE, re-relax owed) the alternative; both readings are always printed
      and `--gate1-drift s5strict` swaps the default. No Cr row drifts today.
  C10 Ru GATE-1 child not required (manifest; am.4 §2 + A5.7 name Cr; §5 P16 and A5.2's
      unqualified sentence read broader; Ru runs nspin = 1 so no magnetic basin to drift).
      A Ru __g1.out on disk is read and reported, never substituted.

Sign logic of the benchmark, stated once so a referee can check it: dG_term(U) =
dG_term(0) - n_e*U with n_e = 4 (O_full), 3 (mixed), 2 (OH_full), 0 (clean). The lower
envelope of lines with these slopes is concave, so with FALLING U the stable termination
moves monotonically from the most oxidised (full-O, stable at high U) to the most reduced
-- which is precisely A5.2's "ordering with falling potential is full-O -> mixed ->
full-*OH". Hence U(O_full/mixed) is the HIGHER transition (Qiu ~1.50 V) and
U(mixed/OH_full) the LOWER (~1.24 V); the brackets are assigned in that order.

Usage
-----
  PYTHONPATH=src python src/dft/lit2_readout.py
  PYTHONPATH=src python src/dft/lit2_readout.py --manifest runs/probe/lit2_manifest.json \\
      --tier data/tiers/tier_v2.json --json out.json [--gate1-drift am4s2|s5strict]
  PYTHONPATH=src python src/dft/lit2_readout.py --print-prereg
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, ".."))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from dft.qe_qc import RY_EV, scan as qc_scan, trusted_energy_ev  # noqa: E402  (strict QC, reused)
from hea_oer.referencing import ZPE_TS_CORRECTION, reference_energy  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, "..", ".."))

# ---------------------------------------------------------------------------------------
# Registered numbers. Each is docs/43's, with the clause it comes from. This file may not
# change any of them; changing one is amending the pre-registration. `ANCHORS` are the
# phrases the program looks for in docs/43 at runtime to confirm each number is still there.
# ---------------------------------------------------------------------------------------
QIU_TOL_V = 0.25                 # docs/43 A5.2: "within +/-0.25 V of Qiu's AIMD brackets"
QIU_U_OFULL_MIXED_V = 1.50       # docs/43 A5.2: "~1.50 V" (full-O/mixed)
QIU_U_MIXED_OHFULL_V = 1.24      # docs/43 A5.2: "~1.24 V" (mixed/full-*OH)
CR_FLAG_EV_PER_SITE = 0.10       # docs/43 A5.2: "> 0.1 eV per site at U = 1.23 V + eta(Cr)"
U_EQ_V = 1.23                    # docs/43 A5.2: the 1.23 V of U* = 1.23 V + eta(Cr)
GATE1_TOL_EV = 0.005             # docs/43 §2-A.3(b) / am.4 §2 / §5: "<= 5 meV"
GATE1_RESIDUAL_EV = 0.004        # docs/43 §5: GATE-1 energy quoted as the correction "with a stated 4 meV residual"
MAG_TOL_MUB = 0.10               # docs/43 am.4 §3: 0.1 mu_B, total AND absolute (reported here)
SIGN_RULE_MAX_DE_SYM_EV = 0.02   # docs/43 §1: "Any dE_sym > +0.02 eV is a failure of the search or of the comparison ... voids that arm"
OFFPLANE_MIN_DY_A = 0.30         # docs/43 §2-A.1: "y-translation of >= 0.30 A plus nosym/noinv" (manifest anchor offplane_min_dy_A)
N_SITES = 2                      # two cus sites per 2x1 cell ("per site" in A5.2's Cr rule; C8 -- docs/43 does not define "site")

# Tolerances of THIS FILE (not registered numbers; stated so they can be challenged).
CHILD_POS_TOL_A = 1e-4           # child ATOMIC_POSITIONS vs parent 'Begin final coordinates'
CELL_TOL_A = 1e-3                # CELL_PARAMETERS equality
SYM_XZ_TOL_A = 0.30              # (x,z) window for finding an atom's sigma_y image partner

ANCHORS = {  # clause -> phrase that must be found in that clause's text
    "A5.2 tolerance 0.25 V": ("A5.2", "±0.25 V"),
    "A5.2 Qiu brackets 1.50 / 1.24 V": ("A5.2", "~1.50 V and ~1.24 V"),
    "A5.2 ordering": ("A5.2", "full-O → mixed → full-*OH"),
    "A5.2 Cr threshold 0.1 eV per site": ("A5.2", "0.1 eV per site"),
    "A5.2 U* = 1.23 V + η(Cr)": ("A5.2", "1.23 V + η(Cr)"),
    "A5.2 reuse rule": ("A5.2", "reused, not re-run"),
    "A5.2 flag qualifies": ("A5.2", "The flag qualifies; it does not retract"),
    "A5.2 new relaxations: off-plane, nosym/noinv, __g1 child": ("A5.2", "off-plane starts, nosym/noinv, a `__g1` GATE-1 child"),
    "A5.7 GATE-1 child for every new Cr relaxation": ("A5.7", "Every new Cr relaxation gets its GATE-1 child"),
    "A5.7 off-plane protocol with measured max|F_y|": ("A5.7", "with measured max|F_y| recorded"),
    "am.4 §2 5 meV": ("AM4S2", "≤ 5 meV"),
    "am.4 §2 child at the parent's own symmetry/k-mesh/cell": ("AM4S2", "at the parent's own symmetry"),
    "am.4 §2 BASIN_DRIFT scored from the child": ("AM4S2", "the pair is scored from it"),
    "§5 P16 every relaxation gets a GATE-1 SCF": ("S5", "gets a GATE-1 fresh-density"),
    "§5 4 meV residual": ("S5", "with a stated 4 meV residual"),
    "§1 sign constraint +0.02 eV": ("S1", "ΔE_sym > +0.02 eV"),
    "§1 voids that arm": ("S1", "voids that arm"),
    "§2-A.1 off-plane start ≥ 0.30 Å": ("S2A", "y-translation of ≥ 0.30 Å"),
    "§0a.2 cite the measured max|F_y|": ("S0A", "must cite its measured max"),
}

#: Every coded rule traced to the docs/43 clause it enforces (hessian_analyze.py style).
GATE_PROVENANCE = {
    "QC": "lessons.md three incidents / qe_qc.py: a '!' total energy, no 'convergence NOT "
          "achieved', 'bfgs converged' on relax decks, free-atom fmax under threshold. "
          "'JOB DONE' alone is never success.",
    "GATE-1": "docs/43 §2-A.3(b) + amendment 4 §2 + §5 (P16): every Cr relaxation has a "
              "__g1 fresh-density fixed-geometry SCF at its own final coordinates, at the "
              "parent's own symmetry/k-mesh/cell. am.4 §2: 'verdict AGREE within tolerance "
              "[<= 5 meV], else BASIN_DRIFT, in which case the GATE-1 SCF energy is the "
              "corrected value ... and the pair is scored from it' -> the CHILD is the energy "
              "of record (AGREE or drift; default). §5: 'If that SCF lands >= 5 meV lower, the "
              "state is re-relaxed from it and the loop repeats' and the GATE-1 energy may be "
              "quoted 'with a stated 4 meV residual' -> the §5-strict reading (NOT SCOREABLE, "
              "re-relax owed) is printed beside it (C9, --gate1-drift). No scoreable child -> "
              "PENDING_GATE1 (am.4 §2: 'a precondition of the readout'). LIT-2 scores GATE-1-"
              "passed Cr energies only (manifest gate1_note; A5.7).",
    "GATE-1-CHILD-ID": "am.4 §2 ('a GATE-1 child that changes nosym or the k-set at the same "
                       "time attributes nothing') + am.4 §4 ('a control that cannot fail "
                       "controls nothing'): the child is verified to be THE registered child -- "
                       "calculation scf; fresh density (superposition of free atoms, no "
                       "startingpot/startingwfc=file); nosym/noinv, symmetry line, K_POINTS + "
                       "nk, CELL_PARAMETERS, nat, nspin, ecutwfc/ecutrho, pseudos, HUBBARD equal "
                       "to the parent's; ATOMIC_POSITIONS = parent's 'Begin final coordinates' "
                       "to 1e-4 A. Else CHILD NOT THE REGISTERED CHILD -> NOT SCOREABLE.",
    "MAG": "docs/43 amendment 4 §3: total AND absolute magnetisation, 0.1 mu_B channels, "
           "recorded for every Cr job. REPORTED for child-vs-parent and arm-vs-arm here; "
           "gating on it is registered for pairs/GATE C, not for GATE-1.",
    "CHE": "docs/43 A5.2 'static CHE surface Pourbaix'; formulas = hea_oer.referencing "
           "(ZPE_TS_CORRECTION OH 0.35 / O 0.05), gas references = manifest "
           "geometry.gas_references (A5.2 reuse rule).",
    "COMPOSITION": "docs/43 A5.2 names the rungs; n_O/n_OH are derived from the START deck, "
                   "cross-checked against the nominal composition, and the termination identity is "
                   "re-verified on the parent's FINAL geometry (added atoms still above the clean "
                   "top layer; every added H still bonded to an ADDED O, i.e. no H migration to a "
                   "lattice O) (this file, stated rule).",
    "BENCH-(i)": "docs/43 A5.2: 'the ordering with falling potential is full-O -> mixed -> "
                 "full-*OH' (judged on the analytic envelope over the registered terminations, "
                 "clean included, C3; the clean-ignoring alternative reading printed beside it).",
    "BENCH-(ii)": "docs/43 A5.2: 'the full-O/mixed and mixed/full-*OH transition potentials "
                  "fall within +/-0.25 V of Qiu's AIMD brackets (~1.50 V and ~1.24 V)'.",
    "BENCH-OUTCOME": "docs/43 A5.2: PASS -> Cr 'validated-by-proxy'; FAIL -> Cr "
                     "'vacuum-CHE-only' with the measured RuO2 discrepancy attached. Neither "
                     "gates any 1A/1B/1C result.",
    "CR-RULE": "docs/43 A5.2: 'if Cr prefers an O-covered termination by > 0.1 eV per site at "
               "U = 1.23 V + eta(Cr), every clean-termination Cr energetics row ... carries a "
               "conditional-on-termination flag. The flag qualifies; it does not retract.' "
               "'O-covered' read as O_full/mixed (C2, default) with the inclusive reading "
               "printed; 'per site' = per cus site (C8) with the per-cell reading printed.",
    "CONTEXT": "manifest registered_ambiguities: ref__2x1o is NOT a registered rung (printed "
               "with its dG0 and its value at U*; never scored; C7); cov_Ovac = 'one bridging O "
               "removed' (A5.2's O-depleted variant, the O unnamed).",
    "ARM": "docs/43 §1 (P12): 'dE_sym = E(off-plane, GATE-1-passed) - E(mirror, GATE-1-passed) "
           "<= 0 by construction ... Any dE_sym > +0.02 eV is a failure of the search or of "
           "the comparison, not a physical result, and voids that arm'. Applied on the "
           "energies of record when both arms are scoreable: off arm VOID -> mirror arm is "
           "the rung, entrant to confirm comparability. Within +/-0.02 eV: lowest-energy "
           "scoreable arm (C1 default, A5.2 silent). Flagged in every case.",
    "OFF-PLANE RECORD": "docs/43 A5.7 ('every new relaxation of any metal follows the off-plane/"
                        "nosym standing protocol with measured max|F_y| recorded') + §0a.2 "
                        "('Any claim that a state was searched off-plane must cite its measured "
                        "max|F_y|, never the presence of the flag') + §2-A.1 (y-translation >= "
                        "0.30 A plus nosym/noinv): deck flags, measured start dy, first-step "
                        "max|F_y|, start->final |dy| printed per row; 'off (measured)' only when "
                        "all three are present. Recorded, not gated.",
}

RUNG_ORDER = ("clean", "O_full", "mixed_OH_O", "OH_full", "cov_Ovac")
NOMINAL = {  # rung -> (n_O, n_OH) relative to clean; from A5.2's names + manifest notes
    "clean": (0, 0), "O_full": (2, 0), "mixed_OH_O": (1, 1), "OH_full": (0, 2),
    "cov_Ovac": (-1, 0), "CONTEXT_half_O": (1, 0),
}
RUNG_LABEL = {
    "clean": "clean (ref__2x1v)", "O_full": "O_full  (1 ML *O_cus)",
    "mixed_OH_O": "mixed   (1:1 *OH-*O)", "OH_full": "OH_full (1 ML *OH_cus)",
    "cov_Ovac": "cov_Ovac (clean - 1 bridging O)", "CONTEXT_half_O": "CONTEXT ref__2x1o (1/2 ML *O)",
}
Z_ABOVE_A = 0.30      # an added atom must sit this far above the clean top layer
OH_BOND_A = 1.15      # an H must have an O within this distance
MATCH_A = 0.60        # nearest-neighbour match radius for identifying a removed atom
U_SCAN = (2.00, 0.80, 0.01)   # printed table only; (i) is judged analytically (C3)
DRIFT_MODES = ("am4s2", "s5strict")


# ------------------------------------------------------------------ prereg text ---

PREREG_SECTIONS = (
    ("A5.2", r"^## A5\.2 .*?(?=^## )", "A5.2 (LIT-2 trimmed core)"),
    ("A5.7", r"^## A5\.7 .*?(?=^## )", "A5.7 (scope guard)"),
    ("AM4S2", r"^## 2\. GATE-1 extends to every Cr relaxation.*?(?=^## )", "amendment 4 §2 (GATE-1)"),
    ("S5", r"^## 5\. P16 .*?(?=^## )", "§5 (P16: GATE-1 loop, 4 meV residual)"),
    ("S1", r"^## 1\. Closing the P10 gap.*?(?=^## )", "§1 (P12 sign constraint on dE_sym)"),
    ("S2A", r"^## §2-A .*?(?=^## )", "§2-A (amendment 1, block 1A: off-plane start >= 0.30 A)"),
    ("S0A", r"^## 0a\. .*?(?=^## )", "§0a (archive audit; §0a.2: cite the measured max|F_y|)"),
)


def read_prereg(path: str | None = None) -> tuple[dict, str]:
    """{'A5.2': text, 'A5.7': text, 'AM4S2': text, 'S5', 'S1', 'S2A', 'S0A'}, read out of docs/43 itself."""
    if path is None:
        path = os.path.join(REPO, "docs", "43-prereg-week1-factorial.md")
    if not os.path.exists(path):
        raise SystemExit(f"cannot read the pre-registration: {path} does not exist. "
                         f"Pass --prereg-path. This program keeps no copy on purpose.")
    txt = open(path, encoding="utf-8").read()
    out = {}
    for key, pat, label in PREREG_SECTIONS:
        m = re.search(pat, txt, re.M | re.S)
        if not m:
            raise SystemExit(f"cannot find {label} in {path}. docs/43 has been restructured; "
                             f"fix the extractor rather than pasting a copy in here.")
        out[key] = m.group(0).rstrip()
    return out, path


def check_anchors(prereg: dict) -> list[str]:
    warns = []
    for name, (sec, phrase) in ANCHORS.items():
        if phrase not in prereg.get(sec, ""):
            warns.append(f"ANCHOR MISSING: '{phrase}' not found in docs/43 {sec} -- the "
                         f"registered number for [{name}] coded here may be stale; docs/43 wins.")
    return warns


# ------------------------------------------------------------------ parsing ---

_CARDS = ("K_POINTS", "CELL_PARAMETERS", "ATOMIC_SPECIES", "HUBBARD", "OCCUPATIONS",
          "CONSTRAINTS", "ATOMIC_VELOCITIES", "ATOMIC_POSITIONS", "ATOMIC_FORCES")
_RE_FATOM = re.compile(r"^\s*atom\s+(\d+)\s+type\s+(\d+)\s+force\s+=\s+"
                       r"(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)")


def _is_float(tok: str) -> bool:
    try:
        float(tok)
        return True
    except ValueError:
        return False


def _qe_bool(v) -> bool:
    return str(v).strip().strip(".").lower() in ("true", "t")


def _pos_unit(header: str) -> str | None:
    s = header.replace("(", " ").replace(")", " ").replace("{", " ").replace("}", " ").split()
    return s[1].lower() if len(s) > 1 else None


def parse_deck(path: str) -> dict:
    """Species, positions (+ if_pos flags + unit), cell, k-line, Hubbard lines and the namelist params."""
    d = {"path": path, "exists": os.path.exists(path), "atoms": [], "flags": [], "pos_unit": None,
         "cell": None, "kpoints": None, "hubbard": [], "species": {}, "params": {}}
    if not d["exists"]:
        return d
    txt = open(path, errors="ignore").read()
    for m in re.finditer(r"^\s*([A-Za-z_]+(?:\(\d+\))?)\s*=\s*([^\n!]+)", txt, re.M):
        d["params"][m.group(1).lower()] = m.group(2).strip().rstrip(",").strip().strip("'\"")
    lines = txt.splitlines()
    i = 0
    while i < len(lines):
        head = lines[i].strip().upper()
        if head.startswith("ATOMIC_POSITIONS"):
            d["pos_unit"] = _pos_unit(lines[i])
            i += 1
            while i < len(lines):
                s = lines[i].split()
                if not s or s[0].upper().split("(")[0] in _CARDS or len(s) < 4 \
                        or not all(_is_float(t) for t in s[1:4]):
                    break
                d["atoms"].append((s[0], float(s[1]), float(s[2]), float(s[3])))
                d["flags"].append(tuple(int(t) for t in s[4:7]) if len(s) >= 7 and
                                  all(t in ("0", "1") for t in s[4:7]) else (1, 1, 1))
                i += 1
            continue
        if head.startswith("CELL_PARAMETERS"):
            d["cell"] = [[float(t) for t in lines[i + k].split()[:3]] for k in (1, 2, 3)]
            i += 4
            continue
        if head.startswith("K_POINTS"):
            d["kpoints"] = lines[i + 1].strip() if i + 1 < len(lines) else None
            i += 2
            continue
        if head.startswith("ATOMIC_SPECIES"):
            i += 1
            while i < len(lines):
                s = lines[i].split()
                if len(s) < 3 or not _is_float(s[1]):
                    break
                d["species"][s[0]] = s[2]
                i += 1
            continue
        if head.startswith("HUBBARD"):
            i += 1
            while i < len(lines) and lines[i].strip() and \
                    lines[i].split()[0].upper().split("(")[0] not in _CARDS:
                d["hubbard"].append(lines[i].strip())
                i += 1
            continue
        i += 1
    return d


def parse_final_coordinates(path: str) -> dict | None:
    """The LAST 'Begin final coordinates' block of a pw.x output: unit, atoms, if_pos flags, cell."""
    if not os.path.exists(path):
        return None
    txt = open(path, errors="ignore").read()
    i = txt.rfind("Begin final coordinates")
    if i < 0:
        return None
    j = txt.find("End final coordinates", i)
    lines = txt[i:(j if j > 0 else None)].splitlines()
    out = {"unit": None, "atoms": [], "flags": [], "cell": None}
    k = 0
    while k < len(lines):
        s = lines[k].split()
        if s and s[0].upper().startswith("ATOMIC_POSITIONS"):
            out["unit"] = _pos_unit(lines[k])
            k += 1
            while k < len(lines):
                t = lines[k].split()
                if len(t) < 4 or not all(_is_float(v) for v in t[1:4]):
                    break
                out["atoms"].append((t[0], float(t[1]), float(t[2]), float(t[3])))
                out["flags"].append(tuple(int(v) for v in t[4:7]) if len(t) >= 7 and
                                    all(v in ("0", "1") for v in t[4:7]) else (1, 1, 1))
                k += 1
            continue
        if s and s[0].upper().startswith("CELL_PARAMETERS"):
            out["cell"] = [[float(t) for t in lines[k + m].split()[:3]] for m in (1, 2, 3)]
            k += 4
            continue
        k += 1
    return out if out["atoms"] else None


def force_blocks(path: str) -> list[list[tuple[float, float, float]]]:
    """Every 'Forces acting on atoms' block (Ry/au), in order; [] if none / no file."""
    if not os.path.exists(path):
        return []
    blocks, cur = [], None
    with open(path, errors="ignore") as fh:
        for ln in fh:
            if "Forces acting on atoms" in ln:
                cur = []
                continue
            if cur is not None:
                m = _RE_FATOM.match(ln)
                if m:
                    cur.append((float(m.group(3)), float(m.group(4)), float(m.group(5))))
                    continue
                if "Total force" in ln:
                    if cur:
                        blocks.append(cur)
                    cur = None
    return blocks


def parse_out_extras(path: str) -> dict:
    """Magnetisation (last printed), k count, symmetry line, fresh-density line -- informational."""
    r = {"mag_tot": None, "mag_abs": None, "nk": None, "symmetry": None, "fresh_density": None}
    if not os.path.exists(path):
        return r
    txt = open(path, errors="ignore").read()
    mt = re.findall(r"total magnetization\s+=\s+(-?\d+\.\d+)", txt)
    ma = re.findall(r"absolute magnetization\s+=\s+(-?\d+\.\d+)", txt)
    r["mag_tot"] = float(mt[-1]) if mt else None
    r["mag_abs"] = float(ma[-1]) if ma else None
    mk = re.search(r"number of k points=\s*(\d+)", txt)
    r["nk"] = int(mk.group(1)) if mk else None
    if "No symmetry found" in txt:
        r["symmetry"] = "No symmetry found"
    else:
        ms = re.search(r"(\d+)\s+Sym\. Ops\.[^\n]*", txt)
        r["symmetry"] = ms.group(0).strip() if ms else None
    r["fresh_density"] = "Initial potential from superposition of free atoms" in txt
    return r


def qc_record(out_path: str, in_path: str | None) -> dict:
    """Strict QC via qe_qc.scan (record) + trusted_energy_ev (energy); the verdict and the reasons."""
    inp = in_path if (in_path and os.path.exists(in_path)) else None
    rec = qc_scan(out_path, inp)
    ok = rec["verdict"] == "TRUSTWORTHY"
    if rec["calculation"] == "relax" and ok and not rec["bfgs_converged"]:
        ok = False  # belt and braces: a relax deck must say 'bfgs converged'
        rec["reasons"].append("relax deck without 'bfgs converged'")
    if ok and not rec["n_scf_ok"]:
        ok = False
        rec["reasons"].append("no 'convergence has been achieved' line")
    e_trusted = trusted_energy_ev(out_path, inp, strict=True) if rec["exists"] else None
    if ok and e_trusted is None:
        ok = False
        rec["reasons"].append("trusted_energy_ev(strict) returned None while scan said TRUSTWORTHY")
    if ok and e_trusted is not None and rec["energy_ev"] is not None and abs(e_trusted - rec["energy_ev"]) > 1e-9:
        ok = False
        rec["reasons"].append("trusted_energy_ev and scan disagree on the energy")
    return {"path": out_path, "in": in_path, "exists": rec["exists"], "verdict": rec["verdict"],
            "qc_pass": ok, "calculation": rec["calculation"], "energy_ev": rec["energy_ev"],
            "energy_ry": rec["energy_ry"], "n_ionic": rec["n_ionic"],
            "bfgs_converged": rec["bfgs_converged"], "job_done": rec["job_done"],
            "n_scf_fail": rec["n_scf_fail"], "fmax_free_ev_ang": rec["fmax_free_ev_ang"],
            "nat": rec["nat"], "reasons": rec["reasons"],
            "mtime": datetime.datetime.fromtimestamp(os.path.getmtime(out_path)).isoformat(timespec="seconds")
            if rec["exists"] else None}


# ------------------------------------------------------------------ composition ---

def composition(clean: dict, deck: dict, metal: str) -> dict:
    """n_O / n_OH relative to the clean deck, by stoichiometry, with geometric cross-checks."""
    r = {"ok": False, "notes": [], "n_O": None, "n_OH": None}
    if not clean["exists"] or not deck.get("exists", True) or not clean["atoms"] or not deck["atoms"]:
        r["notes"].append("deck or clean deck missing/unparsable")
        return r

    def counts(atoms):
        c = {}
        for sp, *_ in atoms:
            c[sp] = c.get(sp, 0) + 1
        return c
    cc, dc = counts(clean["atoms"]), counts(deck["atoms"])
    r["counts_clean"], r["counts_deck"] = cc, dc
    dO = dc.get("O", 0) - cc.get("O", 0)
    dH = dc.get("H", 0) - cc.get("H", 0)
    dM = dc.get(metal, 0) - cc.get(metal, 0)
    other = set(dc) | set(cc)
    if other - {"O", "H", metal}:
        r["notes"].append(f"unexpected species {sorted(other - {'O', 'H', metal})}")
    if dM != 0:
        r["notes"].append(f"metal count differs from clean by {dM:+d}")
    if dH < 0:
        r["notes"].append(f"stoichiometry dH={dH:+d}: H removed relative to clean, not an *O/*OH/O-vacancy unit")
    n_OH, n_O = dH, dO - dH          # n_O < 0 is an O depletion (A5.2's O-depleted variant)
    if n_O < 0 and n_OH > 0:
        r["notes"].append(f"stoichiometry dO={dO:+d}, dH={dH:+d} mixes O depletion with *OH: not a registered rung")
    r.update(dO=dO, dH=dH, n_O=n_O, n_OH=n_OH)

    # cell must be the same cell
    if clean["cell"] and deck.get("cell"):
        dev = max(abs(a - b) for ra, rb in zip(clean["cell"], deck["cell"]) for a, b in zip(ra, rb))
        r["cell_max_dev_A"] = dev
        if dev > CELL_TOL_A:
            r["notes"].append(f"CELL_PARAMETERS differ from clean by up to {dev:.4f} A")

    # geometric cross-check
    z_top = max(z for _, _, _, z in clean["atoms"])
    r["z_top_clean_A"] = z_top
    above = [(sp, x, y, z) for sp, x, y, z in deck["atoms"] if z > z_top + Z_ABOVE_A]
    r["n_above"] = len(above)
    r["above"] = [{"species": sp, "x": x, "y": y, "z": z, "dz_above_top": z - z_top}
                  for sp, x, y, z in above]
    expected_added = max(dO, 0) + max(dH, 0)
    if len(above) != expected_added:
        r["notes"].append(f"{len(above)} atom(s) above the clean top layer (+{Z_ABOVE_A} A) "
                          f"but stoichiometry adds {expected_added}")
    # every H must be bonded to an O
    for sp, x, y, z in deck["atoms"]:
        if sp != "H":
            continue
        dmin = min((math.dist((x, y, z), (ox, oy, oz)) for s2, ox, oy, oz in deck["atoms"] if s2 == "O"),
                   default=9e9)
        if dmin > OH_BOND_A:
            r["notes"].append(f"an H at z={z:.2f} has no O within {OH_BOND_A} A (d={dmin:.2f})")
    # removed atoms: clean atoms with no counterpart within MATCH_A
    removed = []
    for sp, x, y, z in clean["atoms"]:
        dmin = min((math.dist((x, y, z), (ax, ay, az)) for s2, ax, ay, az in deck["atoms"] if s2 == sp),
                   default=9e9)
        if dmin > MATCH_A:
            removed.append({"species": sp, "x": x, "y": y, "z": z, "dz_below_top": z_top - z})
    r["removed"] = removed
    expected_removed = max(-dO, 0) + max(-dH, 0)
    if len(removed) != expected_removed:
        r["notes"].append(f"{len(removed)} clean atom(s) unmatched within {MATCH_A} A but "
                          f"stoichiometry removes {expected_removed}")
    for a in removed:
        if a["species"] != "O" or a["dz_below_top"] > Z_ABOVE_A:
            r["notes"].append(f"removed atom {a['species']} at z={a['z']:.2f} is not a clean "
                              f"top-layer (bridging) O")
    r["ok"] = not r["notes"]
    return r


def final_geometry_check(clean: dict, deck: dict, final: dict | None) -> dict:
    """The registered-termination identity, re-verified on the FINAL geometry.

    Atom identities cannot change during a relaxation, so the stoichiometry is the start
    deck's; what can change is WHERE the atoms are. Checked here: (a) every ADDED atom
    (no same-species clean counterpart within MATCH_A at start) still sits > Z_ABOVE_A
    above the clean top layer; (b) every H still has an O within OH_BOND_A, and an ADDED
    H's nearest O is an ADDED O -- an H whose nearest O is a lattice O has migrated off
    its *OH (same stoichiometry, different termination), which every start-deck check
    would miss. A full re-match against the clean deck is deliberately NOT run on the
    final geometry: relaxed lattice atoms legitimately move and would false-positive the
    removed-atom matcher.
    """
    r = {"ok": False, "notes": [], "added": [],
         "checked": "added-atoms-above-clean-top + H-within-1.15A-of-an-ADDED-O, on the final geometry"}
    if final is None or not final.get("atoms"):
        r["notes"].append("no 'Begin final coordinates' in the .out")
        return r
    if not (clean.get("atoms") and deck.get("atoms")):
        r["notes"].append("clean or start deck unparsable")
        return r
    if len(final["atoms"]) != len(deck["atoms"]) or \
            any(a[0] != b[0] for a, b in zip(final["atoms"], deck["atoms"])):
        r["notes"].append("final coordinates do not match the start deck's species sequence")
        return r
    z_top = max(z for _, _, _, z in clean["atoms"])
    added = []
    for i, (sp, x, y, z) in enumerate(deck["atoms"]):
        dmin = min((math.dist((x, y, z), (cx, cy, cz)) for s2, cx, cy, cz in clean["atoms"] if s2 == sp),
                   default=9e9)
        if dmin > MATCH_A:
            added.append(i)
    r["added"] = [{"atom": i + 1, "species": deck["atoms"][i][0]} for i in added]
    added_O = {i for i in added if deck["atoms"][i][0] == "O"}
    for i in added:
        sp, x, y, z = final["atoms"][i]
        if z <= z_top + Z_ABOVE_A:
            r["notes"].append(f"added atom {sp}{i+1} ended at z={z:.2f}, not > {Z_ABOVE_A} A above the "
                              f"clean top layer (z_top={z_top:.2f}): desorbed/absorbed, not the registered termination")
    for i, (sp, x, y, z) in enumerate(final["atoms"]):
        if sp != "H":
            continue
        best_j, best_d = None, 9e9
        for j, (s2, ox, oy, oz) in enumerate(final["atoms"]):
            if s2 == "O" and j != i:
                dd = math.dist((x, y, z), (ox, oy, oz))
                if dd < best_d:
                    best_j, best_d = j, dd
        if best_d > OH_BOND_A:
            r["notes"].append(f"H{i+1} has no O within {OH_BOND_A} A in the final geometry (d={best_d:.2f})")
        elif i in added and best_j not in added_O:
            r["notes"].append(f"H{i+1} ended bonded to LATTICE O{best_j+1} (d={best_d:.2f} A): the H migrated -- "
                              f"same stoichiometry, not the registered termination")
    r["ok"] = not r["notes"]
    return r


# ------------------------------------------------------------------ off-plane record ---

def y_asymmetry(atoms: list, cell: list, y_mirror: float) -> list:
    """Per atom: half the y-gap to the nearest same-species atom at its sigma_y image (x, 2*y_m - y, z).

    0 for an on-plane or mirror-paired atom; the applied kick for a single y-displaced atom;
    None when no same-species atom sits within SYM_XZ_TOL_A in (x, z) of the image position.
    Periodic in x (a1) and y (a2); the cell is taken orthorhombic as every 2x1 deck here is.
    """
    ax, ay = cell[0][0], cell[1][1]
    out = []
    for sp, x, y, z in atoms:
        yi = 2.0 * y_mirror - y
        best = None
        for sp2, x2, y2, z2 in atoms:
            if sp2 != sp:
                continue
            dx = abs(x2 - x) % ax
            dx = min(dx, ax - dx)
            if dx > SYM_XZ_TOL_A or abs(z2 - z) > SYM_XZ_TOL_A:
                continue
            dy = abs(y2 - yi) % ay
            dy = min(dy, ay - dy)
            best = dy if best is None or dy < best else best
        out.append(None if best is None else best / 2.0)
    return out


def offplane_record(row: dict, deck: dict, final: dict | None, y_mirror: float | None,
                    clean_deck: dict) -> dict:
    """docs/43 A5.7 + §0a.2 + §2-A.1: the measured off-plane record of one relaxation (recorded, not gated)."""
    p = deck.get("params", {})
    rec = {"nosym": _qe_bool(p.get("nosym", ".false.")), "noinv": _qe_bool(p.get("noinv", ".false.")),
           "y_mirror_A": y_mirror, "planes_verified_on_clean": None,
           "start_dy_max_A": None, "start_dy_max_atom": None, "kicked": [], "n_unpaired_start": None,
           "first_step_max_Fy_kicked_ry_au": None, "first_step_max_Fy_free_ry_au": None,
           "last_step_max_Fy_free_ry_au": None, "n_force_blocks": 0,
           "final_dy_max_kicked_A": None, "final_offplane_kicked_A": None, "final_dy_max_free_A": None,
           "manifest_max_start_dy_A": row.get("manifest_max_start_dy"),
           "arm_label": row["arm"], "notes": []}
    if not deck.get("exists") or not deck.get("atoms") or not deck.get("cell") or y_mirror is None:
        rec["notes"].append("no deck / cell / y_mirror: off-plane record not measurable")
        rec["arm_label"] = row["arm"] + (" (by name only: deck unreadable)" if row["arm"] == "off" else "")
        return rec
    # the mirror-plane model, verified on the clean deck rather than assumed
    if clean_deck.get("atoms") and clean_deck.get("cell"):
        cd = [d for d in y_asymmetry(clean_deck["atoms"], clean_deck["cell"], y_mirror) if d is not None]
        rec["planes_verified_on_clean"] = bool(cd) and max(cd) < 1e-3
        if not rec["planes_verified_on_clean"]:
            rec["notes"].append("clean deck is not mirror-symmetric about y_mirror under this model; "
                                "dy numbers are relative to y_mirror + n*a2/2 regardless")
    dys = y_asymmetry(deck["atoms"], deck["cell"], y_mirror)
    rec["n_unpaired_start"] = sum(1 for d in dys if d is None)
    known = [(d, i) for i, d in enumerate(dys) if d is not None]
    if known:
        dmax, imax = max(known)
        rec["start_dy_max_A"], rec["start_dy_max_atom"] = dmax, imax + 1
    kicked = [i for i, d in enumerate(dys) if d is not None and d >= OFFPLANE_MIN_DY_A]
    rec["kicked"] = [{"atom": i + 1, "species": deck["atoms"][i][0], "start_dy_A": dys[i]} for i in kicked]
    flags = deck.get("flags") or [(1, 1, 1)] * len(deck["atoms"])
    free_y = [i for i, f in enumerate(flags) if f[1] == 1]
    blocks = force_blocks(row["out"])
    rec["n_force_blocks"] = len(blocks)
    if blocks:
        f0, fl = blocks[0], blocks[-1]
        if len(f0) == len(deck["atoms"]):
            if kicked:
                rec["first_step_max_Fy_kicked_ry_au"] = max(abs(f0[i][1]) for i in kicked)
            if free_y:
                rec["first_step_max_Fy_free_ry_au"] = max(abs(f0[i][1]) for i in free_y)
                rec["last_step_max_Fy_free_ry_au"] = max(abs(fl[i][1]) for i in free_y)
        else:
            rec["notes"].append(f"first force block has {len(f0)} atoms, deck {len(deck['atoms'])}: F_y not attributed")
    if final and final.get("atoms") and len(final["atoms"]) == len(deck["atoms"]):
        fa = final["atoms"]
        if kicked:
            rec["final_dy_max_kicked_A"] = max(abs(fa[i][2] - deck["atoms"][i][2]) for i in kicked)
            fdy = y_asymmetry(fa, deck["cell"], y_mirror)
            kd = [fdy[i] for i in kicked if fdy[i] is not None]
            rec["final_offplane_kicked_A"] = max(kd) if kd else None
        if free_y:
            rec["final_dy_max_free_A"] = max(abs(fa[i][2] - deck["atoms"][i][2]) for i in free_y)
    if row.get("manifest_max_start_dy") is not None and rec["start_dy_max_A"] is not None:
        if abs(row["manifest_max_start_dy"] - rec["start_dy_max_A"]) > 0.02:
            rec["notes"].append(f"measured start dy {rec['start_dy_max_A']:.3f} A != manifest max_start_dy "
                                f"{row['manifest_max_start_dy']:.3f} A")
    # the label A5.7/§0a.2 allow
    if row["arm"] == "off":
        why = []
        if not (rec["nosym"] and rec["noinv"]):
            why.append("deck lacks nosym/noinv")
        if not kicked:
            why.append(f"no atom started >= {OFFPLANE_MIN_DY_A} A off-plane")
        if rec["first_step_max_Fy_kicked_ry_au"] is None:
            why.append("no first-step F_y read from the .out" + ("" if os.path.exists(row["out"]) else " (.out pending)"))
        rec["arm_label"] = "off (measured)" if not why else "off (by name only: " + "; ".join(why) + ")"
    elif row["arm"] == "mir":
        rec["arm_label"] = "mir" + (" (!! deck has nosym/noinv)" if rec["nosym"] or rec["noinv"] else "")
        if kicked:
            rec["notes"].append(f"mirror arm has {len(kicked)} atom(s) >= {OFFPLANE_MIN_DY_A} A off-plane at start")
    else:
        rec["arm_label"] = "-" + (" (nosym/noinv)" if rec["nosym"] and rec["noinv"] else "")
    return rec


# ------------------------------------------------------------------ ladder build ---

def manifest_rung_key(rung: str) -> str:
    if rung.startswith("CONTEXT-ONLY"):
        return "CONTEXT_half_O"
    return rung


def lit2_rung_key(job: str) -> str:
    if job.startswith("cov_2OH"):
        return "OH_full"
    if job.startswith("cov_Ovac"):
        return "cov_Ovac"
    raise ValueError(f"unrecognised LIT-2 job name {job}")


def arm_of(job: str) -> str:
    """'mir' / 'off' / '-' from the job NAME; the measured off-plane record (A5.7/§0a.2) qualifies it."""
    base = os.path.basename(job)
    if base.endswith("_mir"):
        return "mir"
    if base.endswith("_off"):
        return "off"
    return "-"


def build_rows(manifest: dict, repo: str) -> list[dict]:
    rows = []
    for r in manifest["reused_rungs"]:
        job = r["job"]
        base = os.path.join(repo, "runs", *job.split("/"))
        rows.append({"metal": r["metal"], "rung": manifest_rung_key(r["rung"]),
                     "rung_manifest": r["rung"], "job": job, "arm": arm_of(job),
                     "origin": "reused (block 1A)", "manifest_status": r["status"],
                     "gate1_required": bool(r.get("gate1_required")),
                     "gate1_not_required_reason": None if r.get("gate1_required") else
                     "manifest gate1_required=false (reused block-1A row; am.4 §2 + A5.7 name Cr)",
                     "manifest_max_start_dy": None, "manifest_nspin": None,
                     "out": base + ".out", "in": base + ".in",
                     "g1_out": base + "__g1.out", "g1_in": base + "__g1.in"})
    for j in manifest["jobs"]:
        job = j["job"]
        base = os.path.join(repo, "runs", "probe", f"{j['metal']}_lit2", job)
        req = j["metal"] == "Cr"
        rows.append({"metal": j["metal"], "rung": lit2_rung_key(job), "rung_manifest": j["termination"],
                     "job": f"probe/{j['metal']}_lit2/{job}", "arm": arm_of(job),
                     "origin": "new (LIT-2)", "manifest_status": "deployed (see manifest.status)",
                     "gate1_required": req,
                     "gate1_not_required_reason": None if req else
                     (f"manifest: GATE-1 children registered for the two Cr rows only (am.4 §2 + A5.7 name Cr; "
                      f"§5 P16 / A5.2 read broader -- C10); deck nspin={j.get('nspin')} "
                      + ("(no magnetic basin to drift)" if j.get("nspin") == 1 else "")),
                     "manifest_max_start_dy": j.get("max_start_dy"), "manifest_nspin": j.get("nspin"),
                     "out": base + ".out", "in": base + ".in",
                     "g1_out": base + "__g1.out", "g1_in": base + "__g1.in"})
    return rows


def child_identity_check(row: dict, deck: dict, final: dict | None, cq: dict, cx: dict) -> dict:
    """am.4 §2: is the __g1 child THE registered child of this parent? Every comparison named."""
    cdeck = parse_deck(row["g1_in"])
    compared, fail = [], []
    p, c = deck.get("params", {}), cdeck.get("params", {})
    if not cdeck["exists"]:
        return {"ok": False, "compared": [], "fail": ["child deck __g1.in missing"], "deck_missing": True}
    # (1) calculation
    compared.append("calculation")
    ccalc = (c.get("calculation") or cq.get("calculation") or "").lower()
    if ccalc != "scf":
        fail.append(f"calculation='{ccalc}' != 'scf'")
    # (2) fresh density
    compared.append("fresh density (superposition of free atoms; no startingpot/startingwfc=file)")
    if not cx.get("fresh_density"):
        fail.append("child .out lacks 'Initial potential from superposition of free atoms'")
    for key in ("startingpot", "startingwfc"):
        if str(c.get(key, "")).lower() == "file":
            fail.append(f"child deck sets {key}='file' (not a fresh-density child)")
    # (3) symmetry treatment
    compared.append("nosym/noinv")
    for key in ("nosym", "noinv"):
        if _qe_bool(p.get(key, ".false.")) != _qe_bool(c.get(key, ".false.")):
            fail.append(f"{key}: parent {p.get(key, 'default')} vs child {c.get(key, 'default')}")
    compared.append("pw.x symmetry line")
    if row["extras"]["symmetry"] != cx.get("symmetry"):
        fail.append(f"symmetry line: parent '{row['extras']['symmetry']}' vs child '{cx.get('symmetry')}'")
    # (4) k-set
    compared.append("K_POINTS card + printed k count")
    if (deck.get("kpoints") or "").split() != (cdeck.get("kpoints") or "").split():
        fail.append(f"K_POINTS: parent '{deck.get('kpoints')}' vs child '{cdeck.get('kpoints')}'")
    if cx.get("nk") is not None and row["extras"]["nk"] is not None and cx["nk"] != row["extras"]["nk"]:
        fail.append(f"nk: parent {row['extras']['nk']} vs child {cx['nk']}")
    # (5) cell
    compared.append(f"CELL_PARAMETERS (<= {CELL_TOL_A} A)")
    if deck.get("cell") and cdeck.get("cell"):
        dev = max(abs(a - b) for ra, rb in zip(deck["cell"], cdeck["cell"]) for a, b in zip(ra, rb))
        if dev > CELL_TOL_A:
            fail.append(f"CELL_PARAMETERS differ by up to {dev:.4f} A")
    else:
        fail.append("CELL_PARAMETERS missing in parent or child deck")
    # (6) Hamiltonian identity
    compared.append("nat, nspin, ecutwfc, ecutrho, pseudopotentials, HUBBARD")
    if cq.get("nat") != row["qc"].get("nat"):
        fail.append(f"nat: parent {row['qc'].get('nat')} vs child {cq.get('nat')}")
    for key in ("nspin", "ecutwfc", "ecutrho"):
        pv, cv = p.get(key), c.get(key)
        try:
            same = (pv is None and cv is None) or (float(pv) == float(cv))
        except (TypeError, ValueError):
            same = pv == cv
        if not same:
            fail.append(f"{key}: parent {pv} vs child {cv}")
    if deck.get("species") != cdeck.get("species"):
        fail.append(f"pseudopotentials: parent {deck.get('species')} vs child {cdeck.get('species')}")
    if [h.split() for h in deck.get("hubbard", [])] != [h.split() for h in cdeck.get("hubbard", [])]:
        fail.append("HUBBARD card differs")
    # (7) geometry: child positions == parent final coordinates
    compared.append(f"ATOMIC_POSITIONS vs parent 'Begin final coordinates' (<= {CHILD_POS_TOL_A} A, same unit)")
    if final is None:
        fail.append("parent .out has no 'Begin final coordinates' block: child geometry cannot be verified")
    else:
        if (cdeck.get("pos_unit") or "") != (final.get("unit") or "") or (cdeck.get("pos_unit") or "") not in ("angstrom",):
            fail.append(f"position units: child '{cdeck.get('pos_unit')}' vs parent final '{final.get('unit')}' "
                        f"(only angstrom/angstrom is compared)")
        elif len(cdeck["atoms"]) != len(final["atoms"]):
            fail.append(f"child has {len(cdeck['atoms'])} atoms, parent final {len(final['atoms'])}")
        else:
            sp_ok = all(a[0] == b[0] for a, b in zip(cdeck["atoms"], final["atoms"]))
            if not sp_ok:
                fail.append("species sequence differs from the parent's final coordinates")
            dmax = max(max(abs(a[k] - b[k]) for k in (1, 2, 3)) for a, b in zip(cdeck["atoms"], final["atoms"]))
            if dmax > CHILD_POS_TOL_A:
                fail.append(f"child positions differ from the parent's final coordinates by up to {dmax:.2e} A")
    return {"ok": not fail, "compared": compared, "fail": fail, "deck_missing": False,
            "child_pos_vs_parent_final_max_A": None}


def score_row(row: dict, clean_deck: dict, geom: dict | None, drift_mode: str) -> None:
    """Attach QC, extras, composition (start + final), off-plane record, GATE-1; set row['status']."""
    row["qc"] = qc_record(row["out"], row["in"])
    row["extras"] = parse_out_extras(row["out"])
    deck = parse_deck(row["in"])
    final = parse_final_coordinates(row["out"])
    row["deck_exists"] = deck["exists"]
    row["deck_mtime"] = (datetime.datetime.fromtimestamp(os.path.getmtime(row["in"])).isoformat(timespec="seconds")
                         if deck["exists"] else None)
    row["kpoints"] = deck.get("kpoints")
    row["composition"] = composition(clean_deck, deck, row["metal"]) if deck["exists"] else \
        {"ok": False, "notes": ["deck .in missing"], "n_O": None, "n_OH": None}
    row["final_check"] = final_geometry_check(clean_deck, deck, final)
    nom = NOMINAL[row["rung"]]
    row["nominal"] = {"n_O": nom[0], "n_OH": nom[1]}
    comp = row["composition"]
    row["composition_matches_nominal"] = bool(comp["ok"] and (comp["n_O"], comp["n_OH"]) == nom)
    row["final_check_ok"] = row["final_check"]["ok"] if row["qc"]["exists"] else None
    # choose the nominal if the deck agrees; never score otherwise
    row["n_O"], row["n_OH"] = (comp["n_O"], comp["n_OH"]) if comp["ok"] else (None, None)
    row["offplane"] = offplane_record(row, deck, final, (geom or {}).get("y_mirror"), clean_deck)
    row["arm_label"] = row["offplane"]["arm_label"]

    blockers = []
    if not row["qc"]["exists"]:
        blockers.append("no .out on disk")
    elif not row["qc"]["qc_pass"]:
        blockers.append("QC " + row["qc"]["verdict"] + (": " + "; ".join(row["qc"]["reasons"])
                                                         if row["qc"]["reasons"] else ""))
    if not deck["exists"]:
        blockers.append("no .in deck (composition unknown)")
    elif not comp["ok"]:
        blockers.append("composition check failed (start deck): " + "; ".join(comp["notes"]))
    elif (comp["n_O"], comp["n_OH"]) != nom:
        blockers.append(f"deck composition n_O={comp['n_O']}, n_OH={comp['n_OH']} != nominal {nom}")
    if row["qc"]["exists"] and row["qc"]["qc_pass"] and not row["final_check"]["ok"]:
        blockers.append("final-geometry identity check failed: " + "; ".join(row["final_check"]["notes"]))

    # energy of record: parent by default; the GATE-1 child for Cr (am.4 §2)
    row["energy_parent_ev"] = row["qc"]["energy_ev"]
    row["E_rec"] = row["qc"]["energy_ev"]
    row["E_rec_provenance"] = ("parent relax (GATE-1 not required: " + (row.get("gate1_not_required_reason") or "") + ")"
                               if not row["gate1_required"] else "parent relax (PROVISIONAL: GATE-1 child not yet scoreable)")

    # GATE-1
    g = {"required": row["gate1_required"], "status": "n/a", "verdict": None, "dE_meV": None,
         "child_energy_ev": None, "child_qc": None, "child_identity": None, "dM_tot": None, "dM_abs": None,
         "mag_flags": [], "am4s2_reading": None, "s5_strict_reading": None, "applied": None,
         "child_on_disk": os.path.exists(row["g1_out"])}
    if row["gate1_required"] or g["child_on_disk"]:
        cq = qc_record(row["g1_out"], row["g1_in"])
        cx = parse_out_extras(row["g1_out"])
        g["child_qc"] = cq
        g["child_energy_ev"] = cq["energy_ev"]
        g["child_mag_tot"], g["child_mag_abs"] = cx["mag_tot"], cx["mag_abs"]
        g1_in_exists = os.path.exists(row["g1_in"])
        if not cq["exists"]:
            g["status"] = "PENDING (GATE-1 child pending: no __g1.out)"
            if row["gate1_required"]:
                blockers.append("GATE-1 child pending")
        elif not g1_in_exists:
            g["status"] = "CHILD DECK MISSING (__g1.in absent: the child cannot be verified as the registered child)"
            if row["gate1_required"]:
                blockers.append("GATE-1 child deck __g1.in missing")
        elif not cq["qc_pass"]:
            g["status"] = "CHILD QC FAIL: " + "; ".join(cq["reasons"])
            if row["gate1_required"]:
                blockers.append("GATE-1 child failed QC")
        elif row["qc"]["energy_ev"] is None:
            g["status"] = "parent has no energy"
        else:
            ident = child_identity_check(row, deck, final, cq, cx)
            g["child_identity"] = ident
            if not ident["ok"]:
                g["status"] = ("CHILD NOT THE REGISTERED CHILD: " + "; ".join(ident["fail"]) +
                               " (am.4 §2: at the parent's own final coordinates / symmetry / k-mesh / cell, "
                               "fresh density; compared: " + "; ".join(ident["compared"]) + ")")
                if row["gate1_required"]:
                    blockers.append("GATE-1 child not the registered child")
            else:
                dE = (cq["energy_ev"] - row["qc"]["energy_ev"])
                g["dE_meV"] = dE * 1000.0
                tag = "" if row["gate1_required"] else " [INFO: child on disk, not required -- parent stays the energy of record, C10]"
                if abs(dE) <= GATE1_TOL_EV:
                    g["verdict"] = "AGREE"
                    g["status"] = f"AGREE ({dE*1000:+.3f} meV <= 5 meV)" + ("; E_rec = child (am.4 §2)" if row["gate1_required"] else tag)
                    g["applied"] = "child energy of record (am.4 §2; parent identical to <= 5 meV)"
                else:
                    interp = dE > 0
                    g["verdict"] = "BASIN_DRIFT" + (" (child ABOVE parent: INTERPRETIVE)" if interp else "")
                    g["am4s2_reading"] = (f"SCORED from the child (am.4 §2: 'the GATE-1 SCF energy is the corrected value "
                                          f"... scored from it'; {GATE1_RESIDUAL_EV*1000:.0f} meV residual, §5)")
                    g["s5_strict_reading"] = ("NOT SCOREABLE: re-relax owed (§5: 'the state is re-relaxed from it and "
                                              "the loop repeats')" if not interp else
                                              "INTERPRETIVE (§5's loop names only 'lands >= 5 meV lower'; entrant call)")
                    word = "LOWER" if dE < 0 else "HIGHER"
                    if not row["gate1_required"]:
                        g["status"] = f"BASIN_DRIFT child {word} by {abs(dE)*1000:.1f} meV" + tag
                    elif drift_mode == "am4s2":
                        g["status"] = (f"BASIN_DRIFT child {word} by {abs(dE)*1000:.1f} meV -> {g['am4s2_reading']} "
                                       f"| §5-strict reading: {g['s5_strict_reading']}")
                        g["applied"] = "am.4 §2 (scored from the child; --gate1-drift am4s2)"
                    else:
                        g["status"] = (f"BASIN_DRIFT child {word} by {abs(dE)*1000:.1f} meV -> {g['s5_strict_reading']} "
                                       f"| am.4 §2 reading: {g['am4s2_reading']}")
                        g["applied"] = "§5-strict (--gate1-drift s5strict)"
                        blockers.append("GATE-1 BASIN_DRIFT: re-relax owed (§5-strict mode; am.4 §2 reading printed)")
                if row["gate1_required"] and not any(b.startswith("GATE-1") for b in blockers):
                    row["E_rec"] = cq["energy_ev"]
                    row["E_rec_provenance"] = ("gate1 SCF (am.4 §2; AGREE)" if g["verdict"] == "AGREE" else
                                               f"gate1 SCF (am.4 §2), {GATE1_RESIDUAL_EV*1000:.0f} meV residual (§5)")
            for ch, key in (("total", "mag_tot"), ("absolute", "mag_abs")):
                pm, cm = row["extras"][key], cx[key]
                if pm is not None and cm is not None:
                    d = cm - pm
                    g["dM_tot" if ch == "total" else "dM_abs"] = d
                    if abs(d) > MAG_TOL_MUB:
                        g["mag_flags"].append(f"{ch} magnetisation child-parent = {d:+.2f} mu_B > 0.1")
    row["gate1"] = g
    row["blockers"] = blockers
    row["scoreable"] = not blockers          # data quality: QC + composition (start+final) + GATE-1
    row["enters_ladder"] = row["rung"] != "CONTEXT_half_O"
    if not row["enters_ladder"]:
        row["status"] = "CONTEXT (never scored)" + ("" if not blockers else " -- " + "; ".join(blockers))
    else:
        row["status"] = "SCORED" if not blockers else "NOT SCOREABLE: " + "; ".join(blockers)
    if row["scoreable"] and row["gate1_required"] and g["verdict"] and g["verdict"].startswith("BASIN_DRIFT"):
        row["status"] = "SCORED (from the GATE-1 child, am.4 §2; BASIN_DRIFT -- §5-strict reading NOT SCOREABLE, printed)"


# ------------------------------------------------------------------ CHE ---

def dG0(E_term: float, E_clean: float, n_O: int, n_OH: int, E_H2O: float, E_H2: float) -> float:
    dE = E_term - E_clean - n_O * reference_energy("O", E_H2O, E_H2) \
        - n_OH * reference_energy("OH", E_H2O, E_H2)
    return dE + n_O * ZPE_TS_CORRECTION["O"] + n_OH * ZPE_TS_CORRECTION["OH"]


def n_electrons(n_O: int, n_OH: int) -> int:
    return 2 * n_O + n_OH


def choose_arm(rows: list[dict]) -> dict:
    """C1 + docs/43 §1: per rung, both arms printed; the chosen arm and WHY, relative to what was chosen."""
    arms = {r["arm"]: r for r in rows}
    scoreable = [r for r in rows if r["scoreable"]]
    out = {"arms": {a: {"job": r["job"], "status": r["status"], "E_parent_ev": r["energy_parent_ev"],
                        "E_rec_ev": r["E_rec"], "E_rec_provenance": r["E_rec_provenance"],
                        "arm_label": r["arm_label"], "scoreable": r["scoreable"],
                        "mag_tot": r["extras"]["mag_tot"], "mag_abs": r["extras"]["mag_abs"],
                        "gate1": r["gate1"]["status"]} for a, r in arms.items()},
           "chosen": None, "reason": None, "flag": None, "rule": None, "dE_sym_meV": None, "provisional": False}
    if not scoreable:
        have = [f"{r['arm']} E={r['E_rec']:.4f}" for r in rows if r["E_rec"] is not None]
        out["reason"] = "no scoreable arm" + (f" (energies on disk but not scoreable: {', '.join(have)})" if have else "")
        return out
    best = min(scoreable, key=lambda r: r["E_rec"])
    out["chosen"] = best["arm"]
    if len(rows) == 1:
        out["reason"] = "single arm on disk (manifest: new terminations emitted off-plane only; clean/context have one arm)"
        out["rule"] = "single arm"
    elif "mir" in arms and "off" in arms and arms["mir"]["E_rec"] is not None and arms["off"]["E_rec"] is not None:
        d = (arms["off"]["E_rec"] - arms["mir"]["E_rec"]) * 1000.0     # dE_sym = E_off - E_mir (docs/43 §1)
        out["dE_sym_meV"] = d
        both = arms["mir"]["scoreable"] and arms["off"]["scoreable"]
        if both:
            if d > SIGN_RULE_MAX_DE_SYM_EV * 1000:
                out["chosen"] = "mir"
                out["rule"] = "docs/43 §1: off arm VOID"
                out["reason"] = (f"dE_sym = E_off - E_mir = {d:+.1f} meV > +{SIGN_RULE_MAX_DE_SYM_EV*1000:.0f} meV: the off arm "
                                 f"is VOID (docs/43 §1 sign constraint: 'a failure of the search or of the comparison, "
                                 f"not a physical result'); the mirror arm is the rung")
                out["flag"] = (f"off arm VOID under docs/43 §1 (dE_sym = {d:+.1f} meV > +{SIGN_RULE_MAX_DE_SYM_EV*1000:.0f} meV); "
                               f"mirror arm taken. ENTRANT TO CONFIRM the pair is comparable -- same spectator arrangement "
                               f"/ final composition and magnetisation within 0.1 mu_B (printed in the arm-choice block): if NOT "
                               f"comparable the mirror arm simply stands alone as the rung; if comparable the off-plane "
                               f"search failed and a re-search of the off arm is owed. 'Higher local minimum' is NOT an "
                               f"admissible reading (§1: 'not a physical result')")
            elif abs(d) <= SIGN_RULE_MAX_DE_SYM_EV * 1000:
                out["rule"] = "C1 default (within the §1 tolerance)"
                out["reason"] = (f"|dE_sym| = {abs(d):.1f} meV <= {SIGN_RULE_MAX_DE_SYM_EV*1000:.0f} meV (§1 tolerance): "
                                 f"lowest-energy scoreable arm taken (C1 default) = {out['chosen']}")
                if abs(d) <= GATE1_TOL_EV * 1000:
                    out["flag"] = f"arms degenerate within {abs(d):.1f} meV (below the relaxation's resolution); choice immaterial"
                elif d > 0:
                    out["flag"] = (f"mirror arm is LOWER by {d:.1f} meV -- within the §1 +{SIGN_RULE_MAX_DE_SYM_EV*1000:.0f} meV "
                                   f"tolerance (NOT void); the lowest-energy arm (mir) is taken (C1 default) -- A5.2 is "
                                   f"silent, entrant may prefer the off arm as the registered search (changes the rung "
                                   f"by {d:.1f} meV)")
                # d < -5 meV: the off arm is lower, §1's expected sign, and is taken -- nothing to flag
            else:
                out["rule"] = "docs/43 §1: off arm lower (physical sign)"
                out["reason"] = (f"dE_sym = {d:+.1f} meV < -{SIGN_RULE_MAX_DE_SYM_EV*1000:.0f} meV: the off-plane search "
                                 f"found a lower minimum, as §1 expects; off arm taken")
        else:
            other = arms["mir"] if best["arm"] == "off" else arms["off"]
            out["rule"] = "only one arm scoreable"
            out["reason"] = (f"only the {best['arm']} arm is scoreable; the {other['arm']} arm is on disk with "
                             f"E = {other['E_rec']:.4f} eV but NOT scoreable ({'; '.join(other['blockers'])}); "
                             f"§1 not applied (it is stated on GATE-1-passed energies)")
            if other["E_rec"] < best["E_rec"]:
                out["provisional"] = True
                out["flag"] = (f"a LOWER arm ({other['arm']}, dE = {(other['E_rec'] - best['E_rec'])*1000:+.1f} meV vs the "
                               f"chosen {best['arm']}) is on disk but NOT scoreable ({'; '.join(other['blockers'])}) -- "
                               f"the higher, scoreable {best['arm']} arm is taken; the rung dG0 is PROVISIONAL and may "
                               f"drop when the {other['arm']} arm becomes scoreable")
            else:
                out["flag"] = (f"the unscoreable {other['arm']} arm is higher on disk by "
                               f"{(other['E_rec'] - best['E_rec'])*1000:.1f} meV; would not change the choice "
                               f"(§1 would then be applied on its energy of record)")
    else:
        have = [a for a, r in arms.items() if r["E_rec"] is not None]
        out["rule"] = "only one arm with an energy"
        out["reason"] = f"lowest-energy scoreable arm (C1 default); arms with an energy on disk: {have}"
    # magnetisation agreement between arms (am.4 §3, reported)
    if len(rows) == 2:
        mags = [(r["extras"]["mag_tot"], r["extras"]["mag_abs"]) for r in rows]
        if all(m[0] is not None and m[1] is not None for m in mags):
            dt, da = mags[0][0] - mags[1][0], mags[0][1] - mags[1][1]
            out["arm_dM_tot"], out["arm_dM_abs"] = dt, da
            comparable = abs(dt) <= MAG_TOL_MUB and abs(da) <= MAG_TOL_MUB
            out["arms_mag_comparable"] = comparable
            if not comparable:
                out["flag"] = (out["flag"] or "") + (f" | arms differ in magnetisation "
                                                     f"(dM_tot={dt:+.2f}, dM_abs={da:+.2f} mu_B > 0.1: "
                                                     f"docs/43 §2-A.3(a) CONFOUNDED pair -- not comparable)")
        cf = [r["final_check_ok"] for r in rows]
        out["arms_final_composition_ok"] = all(c is True for c in cf)
    return out


def envelope_walk(lines: dict) -> tuple[list, list]:
    """Exact lowest-dG sequence with FALLING U over all U, from the line crossings (C3).

    lines: {name: {'dG0_cell': float, 'n_e': int}}. Start at the largest-n_e line (stable as
    U -> +inf); repeatedly take the highest crossing below the current U among lines with a
    smaller n_e (ties -> the smaller n_e, which is lower just below the crossing); stop at the
    smallest n_e. Returns (sequence, [(from, to, U_cross), ...]).
    """
    avail = {k: v for k, v in lines.items() if v.get("dG0_cell") is not None}
    if not avail:
        return [], []
    cur = min(avail, key=lambda k: (-avail[k]["n_e"], avail[k]["dG0_cell"]))
    seq, trans = [cur], []
    U_cur = float("inf")
    while True:
        nc, gc = avail[cur]["n_e"], avail[cur]["dG0_cell"]
        cands = []
        for k, v in avail.items():
            if v["n_e"] < nc:
                Ux = (gc - v["dG0_cell"]) / (nc - v["n_e"])
                if Ux <= U_cur + 1e-12:
                    cands.append((Ux, -v["n_e"], k))
        if not cands:
            break
        Ux, _, nxt = max(cands)
        trans.append((cur, nxt, Ux))
        seq.append(nxt)
        cur, U_cur = nxt, Ux
    return seq, trans


def envelope_table(ladder: dict, u_from: float, u_to: float, step: float) -> list:
    """Printed table only (every 0.10 V): dG per site of every rung and the lowest one."""
    avail = {k: v for k, v in ladder.items() if v.get("dG0_cell") is not None}
    table = []
    n = int(round((u_from - u_to) / step)) + 1
    for i in range(n):
        U = round(u_from - i * step, 6)
        if not (abs((U * 100) - round(U * 100)) < 1e-6 and round(U * 100) % 10 == 0):
            continue
        vals = {k: v["dG0_cell"] - v["n_e"] * U for k, v in avail.items()}
        vals["clean"] = 0.0
        table.append({"U_V": U, "lowest": min(vals, key=vals.get),
                      "dG_site_eV": {k: vals[k] / N_SITES for k in vals}})
    return table


# ------------------------------------------------------------------ per-metal ---

def analyse_metal(metal: str, rows: list[dict], gas: dict, eta_cr: float | None) -> dict:
    res = {"metal": metal, "rows": rows, "gas": gas, "ladder": {}, "context": {}, "arm_choice": {},
           "missing": [], "notes": []}
    by_rung: dict[str, list[dict]] = {}
    for r in rows:
        by_rung.setdefault(r["rung"], []).append(r)

    # clean reference
    clean_rows = by_rung.get("clean", [])
    clean = clean_rows[0] if clean_rows else None
    E_clean = clean["E_rec"] if (clean and clean["scoreable"]) else None
    res["E_clean_ev"] = E_clean
    res["E_clean_provenance"] = clean["E_rec_provenance"] if (clean and clean["scoreable"]) else None
    if E_clean is None:
        res["notes"].append("clean reference (ref__2x1v) not scoreable -> no dG can be formed for this metal"
                            + (f" ({'; '.join(clean['blockers'])})" if clean else " (no clean row on the manifest)"))
    gas_ok = gas["H2O"]["qc_pass"] and gas["H2"]["qc_pass"]
    if not gas_ok:
        bad = [sp for sp in ("H2O", "H2") if not gas[sp]["qc_pass"]]
        res["notes"].append(f"gas reference(s) {bad} failed QC -> no dG can be formed for this metal")
    E_H2O, E_H2 = gas["H2O"]["energy_ev"], gas["H2"]["energy_ev"]
    ref_missing = []
    if E_clean is None:
        ref_missing.append("clean reference not scoreable")
    if not gas_ok:
        ref_missing.append("gas reference failed QC: " + ", ".join(sp for sp in ("H2O", "H2") if not gas[sp]["qc_pass"]))

    for rung in RUNG_ORDER + ("CONTEXT_half_O",):
        rs = by_rung.get(rung, [])
        if not rs:
            continue
        ch = choose_arm(rs)
        res["arm_choice"][rung] = ch
        is_ctx = rung == "CONTEXT_half_O"
        entry = {"rung": rung, "label": RUNG_LABEL[rung], "arm": ch["chosen"], "arm_label": None,
                 "job": None, "E_ev": None, "E_provenance": None, "E_parent_ev": None,
                 "n_O": None, "n_OH": None, "n_e": None, "n_ads": None,
                 "dG0_cell": None, "dG0_site": None, "dG0_ads": None, "dG0_cell_parent": None,
                 "dG0_cell_child": None, "status": None, "context_only": is_ctx,
                 "provisional": ch.get("provisional", False)}
        if ch["chosen"] is not None:
            row = next(r for r in rs if r["arm"] == ch["chosen"])
            n_ads = abs(row["n_O"]) + abs(row["n_OH"])
            entry.update(job=row["job"], E_ev=row["E_rec"], E_provenance=row["E_rec_provenance"],
                         E_parent_ev=row["energy_parent_ev"], arm_label=row["arm_label"],
                         n_O=row["n_O"], n_OH=row["n_OH"], n_e=n_electrons(row["n_O"], row["n_OH"]), n_ads=n_ads)
            if E_clean is not None and gas_ok:
                entry["dG0_cell"] = dG0(row["E_rec"], E_clean, row["n_O"], row["n_OH"], E_H2O, E_H2)
                entry["dG0_site"] = entry["dG0_cell"] / N_SITES
                entry["dG0_ads"] = entry["dG0_cell"] / n_ads if n_ads else None
                entry["status"] = "CONTEXT" if is_ctx else ("SCORED" + (" (PROVISIONAL, C1)" if entry["provisional"] else ""))
                g = row["gate1"]
                if g.get("verdict") and g["verdict"].startswith("BASIN_DRIFT") and row["energy_parent_ev"] is not None:
                    # both readings (C9): the one not applied is printed beside the ladder value
                    entry["dG0_cell_parent"] = dG0(row["energy_parent_ev"], E_clean, row["n_O"], row["n_OH"], E_H2O, E_H2)
                    entry["dG0_cell_child"] = dG0(g["child_energy_ev"], E_clean, row["n_O"], row["n_OH"], E_H2O, E_H2)
                    entry["status"] += " [BASIN_DRIFT: am.4 §2 child-based value in the ladder; parent-based printed]"
            else:
                entry["status"] = "NOT SCOREABLE: " + "; ".join(ref_missing)
        else:
            entry["status"] = "NOT SCOREABLE: " + "; ".join(sorted({b for r in rs for b in r["blockers"]}))
            # a rung whose arms are all BASIN_DRIFT under s5strict still gets the am.4 §2 number printed
            for r in rs:
                g = r["gate1"]
                if (g.get("verdict") and g["verdict"].startswith("BASIN_DRIFT") and g["child_energy_ev"] is not None
                        and E_clean is not None and gas_ok and r["n_O"] is not None):
                    entry["dG0_cell_child"] = dG0(g["child_energy_ev"], E_clean, r["n_O"], r["n_OH"], E_H2O, E_H2)
                    entry["status"] += f" [am.4 §2 reading would score it from the child: dG0/cell = {entry['dG0_cell_child']:.4f} eV]"
        if is_ctx:
            entry["dG0_cell_note"] = "context only; never enters the ladder, the envelope or a verdict (C7)"
            res["context"][rung] = entry
        else:
            res["ladder"][rung] = entry

    # what's missing (exact paths), branched on WHY
    for r in rows:
        is_ctx = r["rung"] == "CONTEXT_half_O"
        tag = f"{metal} {r['rung']} [{r['arm']}]"
        if not r["qc"]["exists"]:
            if not is_ctx:
                res["missing"].append({"need": f"{tag} relaxation output", "path": os.path.relpath(r["out"], REPO)})
            continue
        if not r["qc"]["qc_pass"] and not is_ctx:
            res["missing"].append({"need": f"{tag} QC-clean output (currently {r['qc']['verdict']})",
                                   "path": os.path.relpath(r["out"], REPO)})
        if not r["deck_exists"] and not is_ctx:
            res["missing"].append({"need": f"{tag} deck (.in) for the composition check", "path": os.path.relpath(r["in"], REPO)})
        if r["gate1_required"]:
            g, st = r["gate1"], r["gate1"]["status"]
            if not g["child_qc"]["exists"]:
                res["missing"].append({"need": f"{tag} GATE-1 child (fresh-density SCF at the parent's final coordinates)",
                                       "path": os.path.relpath(r["g1_out"], REPO)})
            elif st.startswith("CHILD DECK MISSING"):
                res["missing"].append({"need": f"{tag} GATE-1 child deck (__g1.in) so the child can be verified",
                                       "path": os.path.relpath(r["g1_in"], REPO)})
            elif st.startswith("CHILD QC FAIL"):
                res["missing"].append({"need": f"{tag} QC-clean GATE-1 child ({st[:60]}...)",
                                       "path": os.path.relpath(r["g1_out"], REPO)})
            elif st.startswith("CHILD NOT THE REGISTERED CHILD"):
                res["missing"].append({"need": f"{tag} GATE-1 child at the parent's final geometry/symmetry/k-set/cell, fresh density",
                                       "path": os.path.relpath(r["g1_out"], REPO)})
            elif g.get("verdict", "") and g["verdict"].startswith("BASIN_DRIFT"):
                if "ABOVE" in g["verdict"]:
                    res["missing"].append({"need": f"{tag} interpretive: child ABOVE parent by {abs(g['dE_meV']):.1f} meV -- "
                                                   f"re-relax or entrant call (§5 names only 'lands >= 5 meV lower')",
                                           "path": os.path.relpath(r["out"], REPO)})
                else:
                    res["missing"].append({"need": f"{tag} re-relaxation from the GATE-1 density (§5 loop; child LOWER by "
                                                   f"{abs(g['dE_meV']):.1f} meV; scored meanwhile from the child under am.4 §2)",
                                           "path": os.path.relpath(r["out"], REPO)})
    for sp in ("H2O", "H2"):
        if not gas[sp]["qc_pass"]:
            res["missing"].append({"need": f"{metal} gas reference {sp} (manifest geometry.gas_references) QC-clean output "
                                           f"(currently {gas[sp]['verdict']})", "path": os.path.relpath(gas[sp]["path"], REPO)})
    if clean is None:
        res["missing"].append({"need": f"{metal} clean reference row (ref__2x1v) on the manifest", "path": "runs/probe/lit2_manifest.json"})

    # envelope over the registered terminations (CONTEXT excluded), analytic (C3) + printed table
    lad = dict(res["ladder"])
    lad_with_clean = dict(lad)
    lad_with_clean["clean"] = {"dG0_cell": 0.0 if E_clean is not None and gas_ok else None, "n_e": 0}
    seq, walk = envelope_walk(lad_with_clean)
    table = envelope_table(lad, *U_SCAN)
    res["envelope"] = {"method": "analytic lower envelope over all U (C3); U_scan table is printed only",
                       "U_scan": {"from_V": U_SCAN[0], "to_V": U_SCAN[1], "step_V": U_SCAN[2]},
                       "sequence_with_falling_U": seq,
                       "crossings_with_falling_U": [{"from": a, "to": b, "U_V": u} for a, b, u in walk],
                       "table_every_0p1V": table,
                       "rungs_in_envelope": [k for k, v in lad_with_clean.items() if v.get("dG0_cell") is not None]}

    # analytic transitions between registered rungs
    def trans(a, b):
        A, B = lad_with_clean.get(a), lad_with_clean.get(b)
        if not A or not B or A.get("dG0_cell") is None or B.get("dG0_cell") is None:
            return None
        return (A["dG0_cell"] - B["dG0_cell"]) / (A["n_e"] - B["n_e"])
    res["transitions_V"] = {
        "O_full/mixed": trans("O_full", "mixed_OH_O"),
        "mixed/OH_full": trans("mixed_OH_O", "OH_full"),
        "OH_full/clean": trans("OH_full", "clean"),
        "O_full/clean": trans("O_full", "clean"),
        "mixed/clean": trans("mixed_OH_O", "clean"),
    }
    if "cov_Ovac" in lad_with_clean and lad_with_clean["cov_Ovac"].get("dG0_cell") is not None:
        res["transitions_V"]["clean/cov_Ovac"] = trans("clean", "cov_Ovac")
    return res


# ------------------------------------------------------------------ verdicts ---

def ru_benchmark(ru: dict) -> dict:
    t = ru["transitions_V"]
    b = {"rule": "docs/43 A5.2: PASS iff (i) ordering with falling U is full-O -> mixed -> full-*OH "
                 "AND (ii) U(O_full/mixed), U(mixed/OH_full) within +/-0.25 V of ~1.50 V, ~1.24 V",
         "sign_logic": "dG(U) = dG(0) - n_e*U, n_e = 4/3/2/0 for O_full/mixed/OH_full/clean; the most "
                       "oxidised termination is stable at HIGH U, so FALLING U reads O_full -> mixed -> "
                       "OH_full; U(O_full/mixed) is the higher transition (bracket ~1.50 V), "
                       "U(mixed/OH_full) the lower (~1.24 V)",
         "U_Ofull_mixed_V": t["O_full/mixed"], "U_mixed_OHfull_V": t["mixed/OH_full"],
         "U_OHfull_clean_V": t["OH_full/clean"], "U_mixed_clean_V": t["mixed/clean"],
         "bracket_Ofull_mixed_V": [QIU_U_OFULL_MIXED_V - QIU_TOL_V, QIU_U_OFULL_MIXED_V + QIU_TOL_V],
         "bracket_mixed_OHfull_V": [QIU_U_MIXED_OHFULL_V - QIU_TOL_V, QIU_U_MIXED_OHFULL_V + QIU_TOL_V],
         "discrepancy_Ofull_mixed_V": None, "discrepancy_mixed_OHfull_V": None,
         "ordering_observed": ru["envelope"]["sequence_with_falling_U"],
         "i_ordering": None, "i_ordering_alt_clean_ignored": None, "i_reading": None,
         "ii_a": None, "ii_b": None,
         "verdict": None, "verdict_basis": None, "pass_reachable": None, "reason": None,
         "held_verdict": None, "cr_column_label": None}
    seq = ru["envelope"]["sequence_with_falling_U"]
    have = ru["envelope"]["rungs_in_envelope"]
    need = ("O_full", "mixed_OH_O", "OH_full")
    complete = all(k in have for k in need)
    refs_ok = ru.get("E_clean_ev") is not None and ru["gas"]["H2O"]["qc_pass"] and ru["gas"]["H2"]["qc_pass"]

    def subseq(needle, hay):
        it = iter(hay)
        return all(any(x == n for x in it) for n in needle)
    if complete:
        b["i_ordering"] = subseq(list(need), seq)
        b["i_ordering_alt_clean_ignored"] = (t["O_full/mixed"] > t["mixed/OH_full"])
        b["i_reading"] = ("DEFAULT (C3): analytic envelope incl. clean -> O_full -> mixed -> OH_full is a subsequence: "
                          f"{b['i_ordering']}  [mixed on the envelope iff U(O_full/mixed) > max(U(mixed/OH_full), "
                          f"U(mixed/clean)) = {t['O_full/mixed']:.3f} > max({t['mixed/OH_full']:.3f}, {t['mixed/clean']:.3f}); "
                          f"OH_full follows iff U(mixed/OH_full) > U(OH_full/clean) = {t['mixed/OH_full']:.3f} > "
                          f"{t['OH_full/clean']:.3f}]  |  ALTERNATIVE (clean ignored): U(O_full/mixed) > U(mixed/OH_full): "
                          f"{b['i_ordering_alt_clean_ignored']}")
    if t["O_full/mixed"] is not None:
        b["discrepancy_Ofull_mixed_V"] = t["O_full/mixed"] - QIU_U_OFULL_MIXED_V
        b["ii_a"] = abs(b["discrepancy_Ofull_mixed_V"]) <= QIU_TOL_V + 1e-12
    if t["mixed/OH_full"] is not None:
        b["discrepancy_mixed_OHfull_V"] = t["mixed/OH_full"] - QIU_U_MIXED_OHFULL_V
        b["ii_b"] = abs(b["discrepancy_mixed_OHfull_V"]) <= QIU_TOL_V + 1e-12

    missing_rungs = [k for k in need if k not in have]
    pend_why = missing_rungs + ([] if refs_ok else ["clean/gas reference not scoreable"])
    conj = [b["i_ordering"], b["ii_a"], b["ii_b"]]
    if all(c is True for c in conj):
        b["verdict"], b["verdict_basis"], b["pass_reachable"] = "PASS", "complete ladder", True
        b["reason"] = "ordering full-O -> mixed -> full-*OH observed and both transitions inside their brackets"
    elif any(c is False for c in conj):
        b["verdict"] = "FAIL"
        b["pass_reachable"] = False
        b["verdict_basis"] = "complete ladder" if complete else "PARTIAL ladder (C4: a falsified conjunct decides; hold is a reporting choice)"
        why = []
        if b["i_ordering"] is False:
            why.append(f"(i) analytic ordering with falling U = {' -> '.join(seq)} (registered subsequence absent; "
                       f"clean-ignored alternative reading: {b['i_ordering_alt_clean_ignored']})")
        if b["ii_a"] is False:
            why.append(f"(ii)(a) U(O_full/mixed) = {t['O_full/mixed']:.3f} V is {b['discrepancy_Ofull_mixed_V']:+.3f} V "
                       f"from ~1.50 V, outside +/-0.25 V")
        if b["ii_b"] is False:
            why.append(f"(ii)(b) U(mixed/OH_full) = {t['mixed/OH_full']:.3f} V is {b['discrepancy_mixed_OHfull_V']:+.3f} V "
                       f"from ~1.24 V, outside +/-0.25 V")
        pend = [n for n, c in zip(("(i)", "(ii)(a)", "(ii)(b)"), conj) if c is None]
        if pend:
            why.append("still NOT SCOREABLE: " + ", ".join(pend) + " (pending: " + ", ".join(pend_why or ["?"]) + ")")
        b["reason"] = "; ".join(why)
    else:
        b["verdict"], b["pass_reachable"] = "NOT SCOREABLE", None
        b["verdict_basis"] = "incomplete ladder"
        b["reason"] = "needs " + ", ".join(pend_why or ["?"])

    b["held_verdict"] = (b["verdict"] if complete else
                         f"NOT SCOREABLE (incomplete ladder) -- the reading if the verdict is HELD until "
                         f"{', '.join(pend_why)} land(s); the data-decided reading is {b['verdict']}")
    if b["verdict"] == "PASS":
        b["cr_column_label"] = "validated-by-proxy"
    elif b["verdict"] == "FAIL":
        disc = []
        if b["discrepancy_Ofull_mixed_V"] is not None:
            disc.append(f"dU(O_full/mixed) = {b['discrepancy_Ofull_mixed_V']:+.3f} V")
        else:
            disc.append("dU(O_full/mixed) = pending")
        if b["discrepancy_mixed_OHfull_V"] is not None:
            disc.append(f"dU(mixed/OH_full) = {b['discrepancy_mixed_OHfull_V']:+.3f} V")
        else:
            disc.append("dU(mixed/OH_full) = pending")
        b["cr_column_label"] = "vacuum-CHE-only (RuO2 discrepancy attached as systematic error: " + \
                               "; ".join(disc) + ")" + ("" if complete else " [PARTIAL]")
    else:
        b["cr_column_label"] = "PENDING (benchmark not scoreable)"
    return b


def cr_decision(cr: dict, eta_cr: float | None, tier_src: str) -> dict:
    d = {"rule": "docs/43 A5.2: if Cr prefers an O-covered termination by > 0.1 eV per site at "
                 "U* = 1.23 V + eta(Cr), every clean-termination Cr row carries a conditional-on-"
                 "termination flag. The flag qualifies; it does not retract.",
         "eta_Cr_V": eta_cr, "eta_source": tier_src, "U_star_V": None,
         "per_site_at_Ustar_eV": {}, "per_cell_at_Ustar_eV": {}, "best_O_covered": None, "best_dG_site_eV": None,
         "threshold_eV_per_site": -CR_FLAG_EV_PER_SITE,
         "flag": None, "reason": None, "verdict_basis": None, "context": {}, "flip": None,
         "inclusive_reading": {}, "per_cell_reading": {}}
    if eta_cr is None:
        d["flag"], d["reason"] = "NOT SCOREABLE", "eta(Cr) unavailable from the tier file"
        d["verdict_basis"] = "no U*"
        return d
    U = U_EQ_V + eta_cr
    d["U_star_V"] = U
    lad = dict(cr["ladder"])
    lad.update(cr.get("context", {}))
    gas_ok = cr["gas"]["H2O"]["qc_pass"] and cr["gas"]["H2"]["qc_pass"]

    def at(rung):
        e = lad.get(rung)
        if not e or e.get("dG0_cell") is None:
            return None
        return (e["dG0_cell"] - e["n_e"] * U) / N_SITES
    for rung in ("O_full", "mixed_OH_O", "OH_full", "cov_Ovac", "CONTEXT_half_O"):
        d["per_site_at_Ustar_eV"][rung] = at(rung)
        d["per_cell_at_Ustar_eV"][rung] = None if at(rung) is None else at(rung) * N_SITES
    d["per_site_at_Ustar_eV"]["clean"] = 0.0 if cr.get("E_clean_ev") is not None else None
    d["per_cell_at_Ustar_eV"]["clean"] = d["per_site_at_Ustar_eV"]["clean"]
    d["context"]["OH_full_at_Ustar_site_eV"] = at("OH_full")
    d["context"]["cov_Ovac_at_Ustar_site_eV"] = at("cov_Ovac")
    h = at("CONTEXT_half_O")
    d["context"]["half_O_at_Ustar_site_eV"] = h
    d["context"]["half_O_would_flip"] = None if h is None else bool(h < -CR_FLAG_EV_PER_SITE)
    d["context"]["half_O_note"] = ("C7: ref__2x1o (1/2 ML *O) is NOT a registered rung (manifest registered_ambiguities); "
                                   "never enters the verdict; printed because it is the most decision-relevant Cr number "
                                   "on disk -- if admitted by amendment the flag would read "
                                   + ("-" if h is None else ("ON" if h < -CR_FLAG_EV_PER_SITE else "OFF")))
    d["context"]["note"] = ("OH_full and cov_Ovac are context under C2's default: OH_full is not read as 'O-covered' "
                            "(the inclusive reading is evaluated separately); cov_Ovac is the registered O-depleted "
                            "variant, compared for context only")
    need = {"clean": cr.get("E_clean_ev") is not None, "O_full": at("O_full") is not None,
            "mixed_OH_O": at("mixed_OH_O") is not None}
    missing = [k for k, ok in need.items() if not ok]
    pending_ctx = [k for k in ("OH_full", "cov_Ovac") if at(k) is None]
    if missing:
        d["flag"] = "NOT SCOREABLE"
        if not gas_ok:
            d["reason"] = "gas reference(s) failed QC -> no dG can be formed (see GAS REFERENCES)"
        elif cr.get("E_clean_ev") is None:
            d["reason"] = "clean reference (ref__2x1v) not scoreable -> no dG can be formed (see the Cr ladder)"
        else:
            d["reason"] = "needed rung(s) not scored: " + ", ".join(missing) + \
                          " -- see the ladder statuses (missing / QC / composition / GATE-1)"
        d["verdict_basis"] = "comparator rungs incomplete: " + ", ".join(missing)
        d["inclusive_reading"] = {"flag": "NOT SCOREABLE", "reason": d["reason"]}
        d["per_cell_reading"] = {"flag": "NOT SCOREABLE"}
        return d
    cand = {k: at(k) for k in ("O_full", "mixed_OH_O")}
    best = min(cand, key=cand.get)
    d["best_O_covered"], d["best_dG_site_eV"] = best, cand[best]
    on = cand[best] < -CR_FLAG_EV_PER_SITE
    d["flag"] = "CONDITIONAL-ON-TERMINATION FLAG = " + ("ON" if on else "OFF")
    prov = [f"{k}: {lad[k]['arm']} arm, {lad[k]['E_provenance']}" for k in ("O_full", "mixed_OH_O")]
    d["verdict_basis"] = ("comparator rungs scored: O_full, mixed_OH_O (C2 default, per cus site C8); "
                          + ("context rungs pending: " + ", ".join(pending_ctx) if pending_ctx else "context rungs scored: OH_full, cov_Ovac")
                          + "; energies of record: " + "; ".join(prov)
                          + ("; PROVISIONAL arm choice (C1)" if any(lad[k].get("provisional") for k in cand) else ""))
    d["reason"] = (f"at U* = {U:.3f} V the best O-covered termination ({best}) sits "
                   f"{cand[best]:+.3f} eV per site relative to clean; threshold is < -0.1 eV per site "
                   f"(A5.2). " + ("Every clean-termination Cr energetics row carries the flag. "
                                  if on else "No flag. ") +
                   "The flag qualifies, it does not retract (A5.2).")
    # the inclusive reading (C2 alternative): OH_full counted as 'O-covered'
    if at("OH_full") is None:
        d["inclusive_reading"] = {"flag": "NOT SCOREABLE", "best": None, "best_dG_site_eV": None,
                                  "reason": "OH_full not scored (pending / blocked) -- under the inclusive reading the rule cannot be read yet"}
    else:
        cand_i = dict(cand)
        cand_i["OH_full"] = at("OH_full")
        bi = min(cand_i, key=cand_i.get)
        d["inclusive_reading"] = {"flag": "ON" if cand_i[bi] < -CR_FLAG_EV_PER_SITE else "OFF", "best": bi,
                                  "best_dG_site_eV": cand_i[bi],
                                  "reason": f"OH_full counted as O-covered (Cao's O-covered/stoichiometric/O-depleted "
                                            f"classes do not exclude it): best = {bi} at {cand_i[bi]:+.4f} eV per site"}
    # the per-cell reading (C8 alternative): threshold applied to the per-cell number
    best_cell = cand[best] * N_SITES
    d["per_cell_reading"] = {"flag": "ON" if best_cell < -CR_FLAG_EV_PER_SITE else "OFF", "best": best,
                             "best_dG_cell_eV": best_cell,
                             "reason": f"'per site' read as per 2x1 cell: best = {best} at {best_cell:+.4f} eV per cell vs -0.1 eV"}
    # sensitivity: the U at which the flag first turns ON, min over BOTH O-covered rungs (slopes differ)
    flips = {}
    for k in ("O_full", "mixed_OH_O"):
        e = lad[k]
        if e.get("dG0_cell") is not None and e["n_e"]:
            flips[k] = (e["dG0_cell"] + CR_FLAG_EV_PER_SITE * N_SITES) / e["n_e"]
    if flips:
        k_flip = min(flips, key=flips.get)
        U_flip = flips[k_flip]
        d["flip"] = {"U_flip_V": U_flip, "eta_flip_V": U_flip - U_EQ_V, "set_by": k_flip, "per_rung_V": flips,
                     "note": f"context only: the flag would first turn ON for U* >= {U_flip:.3f} V (set by {k_flip}; "
                             f"per rung: " + ", ".join(f"{k} {v:.3f} V" for k, v in flips.items()) +
                             f"), i.e. eta(Cr) >= {U_flip - U_EQ_V:.3f} V (tier of record gives {eta_cr:.3f} V); "
                             f"not a registered quantity"}
    return d


# ------------------------------------------------------------------ printing ---

def fmt(x, w=12, p=4):
    return ("-" * 1).rjust(w) if x is None else f"{x:{w}.{p}f}"


def fmte(x, w=10):
    return ("-").rjust(w) if x is None else f"{x:{w}.2e}"


def print_report(R: dict) -> None:
    P = print
    P("=" * 100)
    P("LIT-2 READOUT -- static CHE surface Pourbaix -- docs/43 A5.2 (+A5.7), GATE-1 am.4 §2, §1 sign rule, §0a.2 off-plane record")
    P("=" * 100)
    P(f"manifest : {R['manifest_path']}  (mtime {R['input_mtimes'].get('manifest')})")
    P(f"prereg   : {R['prereg_path']}  (mtime {R['input_mtimes'].get('prereg')}; docs/43 wins wherever this program disagrees with it)")
    P(f"tier     : {R['tier_path']}  version={R['tier_version']}  (mtime {R['input_mtimes'].get('tier')})")
    P(f"run date : {R['date']}   GATE-1 drift mode: {R['gate1_drift_mode']} (C9)")
    for w in R["anchor_warnings"]:
        P("!! " + w)
    if not R["anchor_warnings"]:
        P(f"anchors  : all {len(ANCHORS)} registered-number anchor phrases found in docs/43")
    P()
    P("REGISTERED NUMBERS (read, not set):")
    P(f"  Qiu brackets {QIU_U_OFULL_MIXED_V:.2f} V (O_full/mixed), {QIU_U_MIXED_OHFULL_V:.2f} V (mixed/OH_full), "
      f"tolerance +/-{QIU_TOL_V:.2f} V        [A5.2]")
    P(f"  Cr rule: > {CR_FLAG_EV_PER_SITE:.1f} eV per site at U* = {U_EQ_V:.2f} V + eta(Cr)                      [A5.2]")
    P(f"  GATE-1: |E_child - E_parent| <= {GATE1_TOL_EV*1000:.0f} meV; else BASIN_DRIFT scored from the child (am.4 §2) / "
      f"re-relax owed (§5, {GATE1_RESIDUAL_EV*1000:.0f} meV residual); magnetisation channels {MAG_TOL_MUB} mu_B   "
      f"[§2-A.3(b), am.4 §2/§3, §5]")
    P(f"  Sign rule: dE_sym = E_off - E_mir > +{SIGN_RULE_MAX_DE_SYM_EV*1000:.0f} meV voids the off arm                 [§1]")
    P(f"  Off-plane start: y-translation >= {OFFPLANE_MIN_DY_A:.2f} A + nosym/noinv; cite measured max|F_y|   [§2-A.1, §0a.2, A5.7]")
    P(f"  N_SITES = {N_SITES} cus sites per 2x1 cell (per-site = per-cell / 2) -- an interpretation, C8 (docs/43 does not define 'site')")
    P(f"  this file's tolerances (not registered): child positions <= {CHILD_POS_TOL_A:g} A, cell <= {CELL_TOL_A:g} A, "
      f"sigma_y partner window {SYM_XZ_TOL_A} A")
    P()
    P("GATE PROVENANCE (coded rule -> docs/43 clause):")
    for k, v in GATE_PROVENANCE.items():
        P(f"  {k:<16} {v}")
    P()
    P("GAS REFERENCES (manifest geometry.gas_references; reuse is exact but they must pass QC):")
    for metal, g in R["gas"].items():
        for sp in ("H2O", "H2"):
            q = g[sp]
            P(f"  {metal:<3} {sp:<4} {os.path.relpath(q['path'], REPO):<32} QC={q['verdict']:<12} "
              f"E={fmt(q['energy_ev'], 14, 6)} eV  isolated={q.get('assume_isolated')}  mtime={q.get('mtime')}"
              + ("" if q["qc_pass"] else "  <-- FAIL: " + "; ".join(q["reasons"])))
    P()
    P(f"eta(Cr) = {R['eta_Cr_V']}  V  from {R['tier_path']} [{R['tier_version']}] -- {R['tier_provenance']}")
    for m, c in R.get("n_sites_check", {}).items():
        P(f"N_SITES check {m}: clean cell a_x = {fmt(c.get('a_x'), 8, 4).strip()} A vs 2*a1(manifest) = "
          f"{fmt(c.get('two_a1'), 8, 4).strip()} A -> {'OK' if c.get('ok') else '!! MISMATCH'}")
    P()

    for metal in ("Ru", "Cr"):
        M = R["metals"][metal]
        P("-" * 100)
        P(f"{metal}: TERMINATION LADDER -- every rung on the manifest, with status (E_rec = energy of record; E_par = parent relax)")
        P("-" * 100)
        hdr = (f"{'rung':<16}{'arm':<5}{'job':<36}{'origin':<19}{'QC':<12}{'E_par (eV)':>15}{'E_rec (eV)':>15}"
               f"{'M_tot':>7}{'M_abs':>7}  {'GATE-1':<46}  status")
        P(hdr)
        for r in M["rows"]:
            g = r["gate1"]["status"] if (r["gate1_required"] or r["gate1"].get("child_on_disk")) else "n/a"
            P(f"{r['rung']:<16}{r['arm']:<5}{r['job']:<36}{r['origin']:<19}{r['qc']['verdict']:<12}"
              f"{fmt(r['energy_parent_ev'], 15, 4)}{fmt(r['E_rec'], 15, 4)}{fmt(r['extras']['mag_tot'], 7, 2)}"
              f"{fmt(r['extras']['mag_abs'], 7, 2)}  {g:<46}  {r['status']}")
            P(f"{'':<21}  E_rec provenance: {r['E_rec_provenance']}"
              + (f"; child E = {r['gate1']['child_energy_ev']:.4f} eV" if r['gate1'].get('child_energy_ev') is not None else ""))
            if r["gate1"]["mag_flags"]:
                P(f"{'':<21}  !! GATE-1 magnetisation channel: " + "; ".join(r["gate1"]["mag_flags"])
                  + "  (am.4 §3, reported not gated)")
            if r["gate1"].get("child_identity") and r["gate1"]["child_identity"].get("compared"):
                ci = r["gate1"]["child_identity"]
                P(f"{'':<21}  GATE-1 child identity: {'OK' if ci['ok'] else 'FAIL'} -- compared: " + "; ".join(ci["compared"])
                  + ("" if ci["ok"] else " -- FAILED: " + "; ".join(ci["fail"])))
            if r["manifest_status"].startswith("PENDING") and r["qc"]["exists"]:
                P(f"{'':<21}  note: manifest recorded '{r['manifest_status']}' but the .out is on disk now")
        for n in M["notes"]:
            P(f"  !! {n}")
        P()
        P(f"{metal}: COMPOSITION (START deck vs clean ref__2x1v; rule: stoichiometric delta, n_OH = dH, n_O = dO - dH;")
        P(f"     cross-checks: added atoms > {Z_ABOVE_A} A above the clean top layer, each H within {OH_BOND_A} A "
          f"of an O, removed atoms matched to clean top-layer O within {MATCH_A} A; then compared to nominal.")
        P(f"     FINAL = identity re-verified on 'Begin final coordinates': added atoms still above; every added H "
          f"still on an ADDED O -- no H migration to a lattice O)")
        P(f"{'rung':<16}{'arm':<5}{'deck counts':<26}{'dO':>4}{'dH':>4}{'n_O':>5}{'n_OH':>5}"
          f"{'above':>6}{'removed':>8}  {'nominal':<10}{'start':<10}final")
        for r in M["rows"]:
            c, cf = r["composition"], r["final_check"]
            cnt = " ".join(f"{k}{v}" for k, v in sorted(c.get("counts_deck", {}).items())) if c.get("counts_deck") else "(no deck)"
            nom = f"O{r['nominal']['n_O']:+d} OH{r['nominal']['n_OH']:+d}"
            chk = "OK" if r["composition_matches_nominal"] else "MISMATCH: " + "; ".join(c.get("notes", []) or ["?"])
            chkf = ("(no .out)" if not r["qc"]["exists"] else
                    ("OK" if cf["ok"] else "FAIL: " + "; ".join(cf.get("notes", []) or ["?"])))
            P(f"{r['rung']:<16}{r['arm']:<5}{cnt:<26}{str(c.get('dO', '-')):>4}{str(c.get('dH', '-')):>4}"
              f"{str(c.get('n_O', '-')):>5}{str(c.get('n_OH', '-')):>5}{str(c.get('n_above', '-')):>6}"
              f"{str(len(c.get('removed', [])) if c.get('removed') is not None else '-'):>8}  {nom:<10}{chk:<10}{chkf}")
            for a in c.get("removed", []) or []:
                P(f"{'':<21}  removed (start): {a['species']} at (x={a['x']:.2f}, y={a['y']:.2f}, z={a['z']:.2f}), "
                  f"{a['dz_below_top']:.2f} A below the clean top layer (bridging-O row)")
        P()
        P(f"{metal}: OFF-PLANE RECORD (A5.7 + §0a.2 + §2-A.1: measured, never the flag; kicked = started >= {OFFPLANE_MIN_DY_A} A off-plane)")
        P(f"{'rung':<16}{'arm':<5}{'nosym':<7}{'noinv':<7}{'start dy max':>13}{'manifest dy':>12}  {'kicked':<9}"
          f"{'Fy1 kicked':>11}{'Fy1 free':>10}{'FyN free':>10}{'|dy| kicked':>12}{'final off':>10}  label")
        for r in M["rows"]:
            o = r["offplane"]
            kk = ",".join(f"{k['species']}{k['atom']}" for k in o["kicked"]) or "-"
            P(f"{r['rung']:<16}{r['arm']:<5}{str(o['nosym']):<7}{str(o['noinv']):<7}{fmt(o['start_dy_max_A'], 13, 3)}"
              f"{fmt(o['manifest_max_start_dy_A'], 12, 3)}  {kk:<9}{fmte(o['first_step_max_Fy_kicked_ry_au'], 11)}"
              f"{fmte(o['first_step_max_Fy_free_ry_au'], 10)}{fmte(o['last_step_max_Fy_free_ry_au'], 10)}"
              f"{fmt(o['final_dy_max_kicked_A'], 12, 3)}{fmt(o['final_offplane_kicked_A'], 10, 3)}  {o['arm_label']}")
            for n in o["notes"]:
                P(f"{'':<21}  note: {n}")
        P(f"  (Fy in Ry/au at the first / last ionic step; 'start dy' = per-atom half y-gap to the sigma_y image partner, "
          f"0 on-plane; planes verified on the clean deck: "
          f"{ {r['offplane']['planes_verified_on_clean'] for r in M['rows'] if r['offplane']['planes_verified_on_clean'] is not None} })")
        P()
        P(f"{metal}: ARM CHOICE (C1 + docs/43 §1 on the energies of record; both arms printed; ENTRANT DECISION where §1 is silent)")
        for rung, ch in M["arm_choice"].items():
            if len(ch["arms"]) < 2 and rung not in ("O_full", "mixed_OH_O"):
                continue
            P(f"  {rung:<14} chosen={str(ch['chosen']):<5} rule={ch.get('rule')}")
            P(f"      reason: {ch['reason']}")
            for a, info in ch["arms"].items():
                P(f"      {a:<4} {info['job']:<36} E_rec={fmt(info['E_rec_ev'], 14, 4)} ({info['E_rec_provenance']})  "
                  f"M_tot={fmt(info['mag_tot'], 6, 2)} M_abs={fmt(info['mag_abs'], 6, 2)}  [{info['arm_label']}]  {info['status']}")
            if "arm_dM_tot" in ch:
                P(f"      comparability: dM_tot={ch['arm_dM_tot']:+.2f}, dM_abs={ch['arm_dM_abs']:+.2f} mu_B "
                  f"(within 0.1: {ch.get('arms_mag_comparable')}); final compositions both nominal: {ch.get('arms_final_composition_ok')}")
            if ch.get("flag"):
                P(f"      !! {ch['flag']}")
        P()
        P(f"{metal}: CHE LADDER  dG(U) = dG0 - n_e*U  (RHE; clean = 0; per site = per cell / {N_SITES} [C8]; "
          f"per ads = per cell / (|n_O|+|n_OH|) -- equals per site only at full coverage)")
        P(f"{'rung':<32}{'arm':<5}{'n_O':>4}{'n_OH':>5}{'n_e':>4}{'dG0/cell eV':>13}{'dG0/site eV':>13}{'dG0/ads eV':>12}  status")
        dash = lambda v: "-" if v is None else str(v)  # noqa: E731
        for rung, e in M["ladder"].items():
            P(f"{e['label']:<32}{dash(e['arm']):<5}{dash(e['n_O']):>4}{dash(e['n_OH']):>5}{dash(e['n_e']):>4}"
              f"{fmt(e['dG0_cell'], 13, 4)}{fmt(e['dG0_site'], 13, 4)}{fmt(e['dG0_ads'], 12, 4)}  {e['status']}")
            if e.get("dG0_cell_parent") is not None or e.get("dG0_cell_child") is not None:
                P(f"{'':<37}  BASIN_DRIFT readings (C9): child-based dG0/cell = {fmt(e.get('dG0_cell_child'), 9, 4).strip()} eV "
                  f"(am.4 §2); parent-based = {fmt(e.get('dG0_cell_parent'), 9, 4).strip()} eV")
        P(f"  CONTEXT (never scored; C7):")
        for rung, e in M["context"].items():
            P(f"{e['label']:<32}{dash(e['arm']):<5}{dash(e['n_O']):>4}{dash(e['n_OH']):>5}{dash(e['n_e']):>4}"
              f"{fmt(e['dG0_cell'], 13, 4)}{fmt(e['dG0_site'], 13, 4)}{fmt(e['dG0_ads'], 12, 4)}  {e['status']} -- {e.get('dG0_cell_note')}")
        P()
        E = M["envelope"]
        P(f"{metal}: ENVELOPE (analytic, all U; registered terminations incl. clean, CONTEXT excluded; rungs with a dG0: "
          f"{E['rungs_in_envelope'] or 'none'})")
        P(f"  sequence with falling U: {' -> '.join(E['sequence_with_falling_U']) or '(nothing scoreable)'}")
        if E["crossings_with_falling_U"]:
            P("  crossings: " + "; ".join(f"{c['from']} -> {c['to']} at {c['U_V']:.3f} V" for c in E["crossings_with_falling_U"]))
        tab = E["table_every_0p1V"]
        if tab:
            keys = [k for k in ("clean", "O_full", "mixed_OH_O", "OH_full", "cov_Ovac") if k in tab[0]["dG_site_eV"]]
            P(f"  table (printed only, {U_SCAN[0]:.2f} -> {U_SCAN[1]:.2f} V):")
            P("  " + f"{'U (V)':>6}  " + "".join(f"{k:>12}" for k in keys) + "   lowest      (dG per site, eV)")
            for t in tab:
                P("  " + f"{t['U_V']:>6.2f}  " + "".join(fmt(t["dG_site_eV"][k], 12, 3) for k in keys) + f"   {t['lowest']}")
        P("  analytic transitions (V):  " + "  ".join(f"{k}={fmt(v, 7, 3).strip()}" for k, v in M["transitions_V"].items()))
        P()

    B = R["ru_benchmark"]
    P("=" * 100)
    P("RuO2 BENCHMARK (docs/43 A5.2, two-sided)")
    P("=" * 100)
    P("  " + B["sign_logic"])
    P(f"  U(O_full/mixed)  = {fmt(B['U_Ofull_mixed_V'], 7, 3).strip():>8} V   bracket {B['bracket_Ofull_mixed_V'][0]:.2f}..{B['bracket_Ofull_mixed_V'][1]:.2f} V (~1.50 +/- 0.25)"
      f"   discrepancy {fmt(B['discrepancy_Ofull_mixed_V'], 7, 3).strip()} V   (ii)(a)={B['ii_a']}")
    P(f"  U(mixed/OH_full) = {fmt(B['U_mixed_OHfull_V'], 7, 3).strip():>8} V   bracket {B['bracket_mixed_OHfull_V'][0]:.2f}..{B['bracket_mixed_OHfull_V'][1]:.2f} V (~1.24 +/- 0.25)"
      f"   discrepancy {fmt(B['discrepancy_mixed_OHfull_V'], 7, 3).strip()} V   (ii)(b)={B['ii_b']}")
    P(f"  U(OH_full/clean) = {fmt(B['U_OHfull_clean_V'], 7, 3).strip():>8} V   U(mixed/clean) = {fmt(B['U_mixed_clean_V'], 7, 3).strip()} V   (context; clean coupling of (i), C3)")
    P(f"  ordering observed with falling U (analytic): {' -> '.join(B['ordering_observed']) or '(incomplete)'}   (i)={B['i_ordering']}"
      f"   (i, clean ignored)={B['i_ordering_alt_clean_ignored']}")
    if B["i_reading"]:
        P(f"  (i) readings: {B['i_reading']}")
    P(f"  VERDICT: {B['verdict']}   [{B['verdict_basis']}]")
    P(f"  reason : {B['reason']}")
    P(f"  held   : {B['held_verdict']}")
    P(f"  Cr column label: {B['cr_column_label']}")
    P()
    D = R["cr_decision"]
    P("=" * 100)
    P("Cr DECISION RULE (docs/43 A5.2)")
    P("=" * 100)
    P(f"  eta(Cr) = {fmt(D['eta_Cr_V'], 7, 4).strip()} V from {D['eta_source']}")
    P(f"  U* = 1.23 V + eta(Cr) = {fmt(D['U_star_V'], 7, 4).strip()} V")
    for k, v in D["per_site_at_Ustar_eV"].items():
        if k in ("O_full", "mixed_OH_O", "clean"):
            tag = ""
        elif k == "CONTEXT_half_O":
            tag = "  (context, C7: NOT a registered rung; if admitted by amendment the flag would read " + \
                  ("-" if D["context"].get("half_O_would_flip") is None else ("ON" if D["context"]["half_O_would_flip"] else "OFF")) + ")"
        else:
            tag = "  (context, C2)"
        pc = D["per_cell_at_Ustar_eV"].get(k)
        P(f"    dG({k:<14}) at U* = {fmt(v, 9, 4).strip():>9} eV per site  = {fmt(pc, 9, 4).strip():>9} eV per cell{tag}")
    P(f"  best O-covered (C2 default): {D['best_O_covered']}  ->  {fmt(D['best_dG_site_eV'], 9, 4).strip()} eV per site vs clean; "
      f"threshold < {D['threshold_eV_per_site']:.1f} eV per site")
    P(f"  {D['flag']}   [basis: {D['verdict_basis']}]")
    P(f"  {D['reason']}")
    ir, pr = D.get("inclusive_reading") or {}, D.get("per_cell_reading") or {}
    if ir:
        P(f"  under the inclusive reading (OH_full counted; C2 alternative): best={ir.get('best')}, "
          f"dG={fmt(ir.get('best_dG_site_eV'), 9, 4).strip()} eV per site, FLAG={ir.get('flag')} -- {ir.get('reason', '')}")
    if pr:
        P(f"  under the per-cell reading (C8 alternative): best={pr.get('best')}, dG={fmt(pr.get('best_dG_cell_eV'), 9, 4).strip()} "
          f"eV per cell, FLAG={pr.get('flag')}")
    if D["context"].get("half_O_at_Ustar_site_eV") is not None:
        P(f"  {D['context']['half_O_note']} ({D['context']['half_O_at_Ustar_site_eV']:+.4f} eV per site at U*; NOT applied)")
    if D.get("flip"):
        P(f"  sensitivity: {D['flip']['note']}")
    P()
    P("WHAT IS MISSING FOR A FULL READOUT (exact paths expected):")
    allm = [(m, x) for m in ("Ru", "Cr") for x in R["metals"][m]["missing"]]
    if not allm:
        P("  nothing -- the ladder is complete")
    for m, x in allm:
        P(f"  [{m}] {x['need']:<70} -> {x['path']}")
    P()
    P("ENTRANT DECISIONS FLAGGED (docs/43 A5.2 is silent or gives two readings; defaults applied and stated, alternatives printed):")
    for k, v in R["entrant_decisions"].items():
        P(f"  {k}: {v}")
    P()
    P("INPUT FILES READ (mtimes):")
    for k, v in R["input_mtimes"].items():
        if k not in ("manifest", "prereg", "tier"):
            P(f"  {k:<60} {v}")
    P()


# ------------------------------------------------------------------ main ---

def _need_file(path: str, what: str) -> None:
    if not os.path.exists(path):
        raise SystemExit(f"cannot read the {what}: {path} does not exist.")


def main(argv=None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=os.path.join(REPO, "runs", "probe", "lit2_manifest.json"))
    ap.add_argument("--tier", default=os.path.join(REPO, "data", "tiers", "tier_v2.json"))
    ap.add_argument("--json", help="write the full readout here")
    ap.add_argument("--print-prereg", action="store_true",
                    help="print docs/43 A5.2 + A5.7 + am.4 §2 + §5 + §1 + §2-A + §0a read from the document, and exit")
    ap.add_argument("--prereg-path", default=None, help="docs/43 location if not at the repo default")
    ap.add_argument("--gate1-drift", choices=DRIFT_MODES, default="am4s2",
                    help="C9: how a GATE-1 BASIN_DRIFT row is scored -- am4s2 (default: scored from the child, "
                         "docs/43 am.4 §2) or s5strict (NOT SCOREABLE, re-relax owed, docs/43 §5); the other reading "
                         "is always printed beside it")
    args = ap.parse_args(argv)

    prereg, prereg_path = read_prereg(args.prereg_path)
    if args.print_prereg:
        print(f"# read from {prereg_path} -- this program holds no copy\n")
        for key, _, label in PREREG_SECTIONS:
            print(f"# ---- {label} ----")
            print(prereg[key])
            print()
        return 0

    _need_file(args.manifest, "LIT-2 manifest (--manifest)")
    _need_file(args.tier, "tier file (--tier)")
    manifest = json.load(open(args.manifest, encoding="utf-8"))
    tier = json.load(open(args.tier, encoding="utf-8"))
    eta_cr = tier.get("tier", {}).get("Cr", {}).get("eta")
    tier_src = f"{os.path.relpath(args.tier, REPO)} [{tier.get('version')}]"

    def mtime(p):
        return datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(timespec="seconds") if os.path.exists(p) else None

    R = {"manifest_path": os.path.relpath(args.manifest, REPO), "prereg_path": os.path.relpath(prereg_path, REPO),
         "tier_path": os.path.relpath(args.tier, REPO), "tier_version": tier.get("version"),
         "tier_provenance": tier.get("provenance"),
         "date": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
         "gate1_drift_mode": args.gate1_drift, "eta_Cr_V": eta_cr,
         "anchor_warnings": check_anchors(prereg), "registered": {
             "QIU_TOL_V": QIU_TOL_V, "QIU_U_OFULL_MIXED_V": QIU_U_OFULL_MIXED_V,
             "QIU_U_MIXED_OHFULL_V": QIU_U_MIXED_OHFULL_V, "CR_FLAG_EV_PER_SITE": CR_FLAG_EV_PER_SITE,
             "U_EQ_V": U_EQ_V, "GATE1_TOL_EV": GATE1_TOL_EV, "GATE1_RESIDUAL_EV": GATE1_RESIDUAL_EV,
             "MAG_TOL_MUB": MAG_TOL_MUB, "SIGN_RULE_MAX_DE_SYM_EV": SIGN_RULE_MAX_DE_SYM_EV,
             "OFFPLANE_MIN_DY_A": OFFPLANE_MIN_DY_A, "N_SITES": N_SITES,
             "ZPE_TS_CORRECTION": ZPE_TS_CORRECTION, "RY_EV": RY_EV},
         "file_tolerances": {"CHILD_POS_TOL_A": CHILD_POS_TOL_A, "CELL_TOL_A": CELL_TOL_A, "SYM_XZ_TOL_A": SYM_XZ_TOL_A},
         "gate_provenance": GATE_PROVENANCE, "gas": {}, "metals": {}, "n_sites_check": {},
         "input_mtimes": {"manifest": mtime(args.manifest), "prereg": mtime(prereg_path), "tier": mtime(args.tier)},
         "manifest_registered_ambiguities": manifest.get("registered_ambiguities", [])}

    # gas references per metal
    for g in manifest["geometry"]:
        metal = g["metal"]
        recs = {}
        for p in g["gas_references"]:
            name = os.path.basename(p).split(".")[0]
            out = os.path.join(REPO, *p.split("/"))
            rec = qc_record(out, out[:-4] + ".in")
            deck = parse_deck(out[:-4] + ".in")
            rec["assume_isolated"] = deck["params"].get("assume_isolated")
            recs[name] = rec
            R["input_mtimes"][os.path.relpath(out, REPO)] = rec["mtime"]
        R["gas"][metal] = recs
        R["gas"][metal]["a1_manifest"] = g.get("a1")

    rows = build_rows(manifest, REPO)
    for metal in ("Ru", "Cr"):
        mrows = [r for r in rows if r["metal"] == metal]
        geom = next((g for g in manifest["geometry"] if g["metal"] == metal), None)
        clean_row = next((r for r in mrows if r["rung"] == "clean"), None)
        clean_deck = parse_deck(clean_row["in"]) if clean_row else {"exists": False, "atoms": [], "cell": None}
        # verify the 2x1 cell against the manifest a1 (N_SITES = 2), recorded in the JSON
        a1 = geom.get("a1") if geom else None
        chk = {"a_x": None, "two_a1": 2 * a1 if a1 else None, "ok": None}
        if clean_deck.get("cell") and a1:
            chk["a_x"] = clean_deck["cell"][0][0]
            chk["ok"] = abs(chk["a_x"] - 2 * a1) <= 0.01
            if not chk["ok"]:
                print(f"!! {metal}: clean cell a_x = {chk['a_x']:.4f} A is not 2 x a1 = {2*a1:.4f} A; "
                      f"N_SITES = {N_SITES} may be wrong", file=sys.stderr)
        R["n_sites_check"][metal] = chk
        for r in mrows:
            score_row(r, clean_deck, geom, args.gate1_drift)
            for key in ("out", "in", "g1_out", "g1_in"):
                if os.path.exists(r[key]):
                    R["input_mtimes"][os.path.relpath(r[key], REPO)] = mtime(r[key])
        R["metals"][metal] = analyse_metal(metal, mrows, R["gas"][metal], eta_cr)

    R["ru_benchmark"] = ru_benchmark(R["metals"]["Ru"])
    R["cr_decision"] = cr_decision(R["metals"]["Cr"], eta_cr, tier_src)
    D = R["cr_decision"]
    hO = D["context"].get("half_O_at_Ustar_site_eV")
    half_sentence = ("1/2 ML *O context rung at U*: " + ("not scoreable" if hO is None else
                     f"{hO:+.4f} eV per site -> if admitted by amendment the flag would read "
                     f"{'ON' if D['context'].get('half_O_would_flip') else 'OFF'} (NOT applied; needs its own amendment)"))
    R["entrant_decisions"] = {
        "C1 arm choice": "O_full/mixed rungs have _mir and _off arms; A5.2 silent on which is the rung, docs/43 §1 not "
                         "silent on the comparison (dE_sym = E_off - E_mir > +20 meV voids the off arm). Applied on the "
                         "energies of record when both arms score; lowest-energy scoreable arm within the §1 tolerance "
                         "(default). " + "; ".join(
                             f"{m} {rung}: chosen={ch['chosen']} [{ch.get('rule')}; dE_sym={fmt(ch.get('dE_sym_meV'), 6, 1).strip()} meV]"
                             + (f" !! {ch['flag']}" if ch.get("flag") else "")
                             for m in ("Ru", "Cr") for rung, ch in R["metals"][m]["arm_choice"].items()
                             if rung in ("O_full", "mixed_OH_O")),
        "C2 'O-covered'": "DEFAULT: the *O-bearing rungs (O_full, mixed) -> " + str(D.get("flag")) +
                          "; INCLUSIVE reading (OH_full counted): FLAG=" + str((D.get("inclusive_reading") or {}).get("flag")) +
                          " (best " + str((D.get("inclusive_reading") or {}).get("best")) + "); cov_Ovac = registered rung, "
                          "context for the rule; " + half_sentence,
        "C3 ordering (i)": "judged on the ANALYTIC lower envelope over all U (clean included: mixed is on the envelope iff "
                           "U(O_full/mixed) > max(U(mixed/OH_full), U(mixed/clean)); OH_full follows iff U(mixed/OH_full) > "
                           "U(OH_full/clean) -- if clean undercuts mixed first, OH_full never appears); the clean-ignored "
                           "alternative 'U(O_full/mixed) > U(mixed/OH_full)' is printed beside it; the 2.0 -> 0.8 V scan "
                           "is a printed table only; transition potentials are analytic line crossings. Today: (i)="
                           + str(R["ru_benchmark"]["i_ordering"]) + ", (i, clean ignored)=" + str(R["ru_benchmark"]["i_ordering_alt_clean_ignored"]),
        "C4 partial verdict": "a falsified conjunct of the PASS rule yields FAIL on a partial ladder "
                              "(PASS unreachable); holding the public verdict until the ladder completes "
                              "is a reporting choice -- the outcome cannot change",
        "C5 Ovac ZPE": "n_O*corr_O applied literally with n_O = -1 (-0.05 eV); A5.2 registers no "
                       "separate correction for a removed lattice O",
        "C6 eta(Cr)": f"from {tier_src} (frozen tier of record, docs/43 §0); eta(Cr) = {eta_cr}",
        "C7 context rung": "ref__2x1o (1/2 ML *O) printed (dG0 and value at U*), never scored; " + half_sentence,
        "C8 'per site'": f"per cus site, N_SITES = {N_SITES} (docs/43 does not define 'site'); per-cell reading: "
                         f"FLAG={(D.get('per_cell_reading') or {}).get('flag')} at "
                         f"{fmt((D.get('per_cell_reading') or {}).get('best_dG_cell_eV'), 8, 4).strip()} eV per cell",
        "C9 GATE-1 drift": f"BASIN_DRIFT rows: am.4 §2 ('the GATE-1 SCF energy is the corrected value ... scored from it') "
                           f"vs §5-strict ('re-relaxed from it and the loop repeats'; the GATE-1 energy may be quoted with a "
                           f"stated 4 meV residual). DEFAULT applied: {args.gate1_drift}; both readings printed per row and "
                           f"per rung (--gate1-drift swaps). AGREE rows quote the child as the energy of record (as the "
                           f"block-1A evaluator does). Rows drifting today: "
                           + (", ".join(f"{r['metal']} {r['rung']} [{r['arm']}] {r['gate1']['verdict']}"
                                        for m in ("Ru", "Cr") for r in R["metals"][m]["rows"]
                                        if r["gate1"].get("verdict") and r["gate1"]["verdict"].startswith("BASIN_DRIFT")) or "none"),
        "C10 Ru GATE-1": "Ru GATE-1 child not required (manifest gate1_required=false; am.4 §2 + A5.7 name Cr; §5 P16 and "
                         "A5.2's unqualified 'a __g1 GATE-1 child' sentence read broader; Ru decks run nspin=1 so there is "
                         "no magnetic basin to drift). Ru __g1.out on disk today: "
                         + (", ".join(f"{r['rung']} [{r['arm']}]: {r['gate1']['status']}" for r in R["metals"]["Ru"]["rows"]
                                      if r["gate1"].get("child_on_disk")) or "none (reported if one appears; never substituted)"),
    }

    print_report(R)
    if args.json:
        d = os.path.dirname(os.path.abspath(args.json))
        os.makedirs(d, exist_ok=True)
        json.dump(R, open(args.json, "w", encoding="utf-8"), indent=1, default=str)
        print(f"-> {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
