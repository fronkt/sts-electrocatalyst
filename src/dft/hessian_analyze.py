#!/usr/bin/env python3
"""Score the block-1C Hessian pilot against docs/43 §3 + §3-A.

This is the other half of `build_hessian_pilot.py`. It reads the 19 `.out` files per state,
checks that they are comparable to each other at all, builds the adsorbate partial Hessian by
central differences, mass-weights it, diagonalises it, and reports every mode with its
out-of-plane character. Then it applies the pre-registered rule and prints a verdict.

WHERE THE RULE LIVES
--------------------
**docs/43-prereg-week1-factorial.md §3 (P14) and §3-A (amendment 1, 2026-08-09). That is the
only pre-registration.** An earlier revision of this file carried a module constant named
`PREREG` holding its own copy of the rule. It contradicted docs/43 in six places — including
one LOOSENING of a registered hard gate — and it is deleted. `--print-prereg` now *reads
those two sections out of docs/43* and prints them; it holds no copy, so a third version
cannot appear. If this code and docs/43 ever disagree, **docs/43 wins and this code is the
defect** (docs/43 amendment 1: "In-code rules must be a pointer to it, never a copy").

The constants below are the numbers docs/43 registers, and each carries the clause it comes
from. Changing one of them is changing the pre-registration, which this file may not do.

WHAT THE REVIEW FOUND HERE, AND WHAT CHANGED
--------------------------------------------
The most serious class of finding in the 2026-08-09 review was that **the verdict logic could
not return its own falsifying answer.**

  * Every quality-gate failure routed to AMBIGUOUS, and `campaign_verdict` then printed
    "NEITHER CONFIRMED -> R3 TRIGGERED. Do not spend the 378 SCFs." A reviewer fed it 19
    synthetic outputs whose only defect was a missed `conv_thr` and got exactly that sentence.
    A compute failure was indistinguishable from a scientific null at the decision layer.
    Fixed by **VOID** (docs/43 §3-A.1): any gate failure, not a scientific result, and the
    campaign returns "PILOT INVALID — no campaign decision".
  * REFUTED was unreachable: `elif inplane or soft:` routed *any* sub-floor imaginary
    eigenvalue to AMBIGUOUS, so a spectrum carrying one mode at i5 cm^-1 came back AMBIGUOUS
    and §3's declared R3 consequence — keyed on the words "both pilot states come back
    REFUTED" — could never fire. Fixed by docs/43 §3-A.2: sub-floor imaginary modes route to
    **REFUTED**, named, with the largest reported as a number.
  * The pilot can be structurally blind to the mode it exists to detect: the out-of-plane
    modes of *OOH are H-dominated and at the design sigma_F an H-carried mode's 3-sigma floor
    is ~i111 cm^-1 against a declared i50. Fixed by docs/43 §3-A.3: **UNDERPOWERED** when the
    floor on the y-character modes exceeds i80 cm^-1, whose declared response is a tighter
    rerun, **not** R3.
  * The reference was never checked against the relaxation it claims to be. All 19 jobs start
    from a fresh atomic superposition, so they can agree with each other while collectively
    sitting in the wrong basin — docs/41 §6f exactly. Fixed by **Q0** (docs/43 §3-A.5).

Three things this script will not do
------------------------------------
1. It will not average or symmetrise over a contaminated force row. If a displacement's total
   magnetisation moved by more than 0.1 mu_B from the reference, that SCF is in a different
   magnetic solution and its whole force row belongs to a different Hamiltonian. docs/43 §3
   tolerates up to 2 such exclusions of 18 and voids the state above that; below that the
   affected coordinate is dropped from BOTH the row and the column set, giving a smaller
   PRINCIPAL SUBMATRIX. That is the only completion that keeps the physics argument below
   valid — a principal submatrix of a symmetric H can only under-report instability, so a
   negative eigenvalue found in it is still a negative curvature of the full Hessian.
2. It will not build a Hessian across inconsistent Brillouin-zone samplings. Every job must
   report "No symmetry found" and the identical k count.
3. It will not read `JOB DONE` as success. pw.x prints it after "convergence NOT achieved",
   after nstep exhaustion, and after a user .EXIT (lessons.md, three separate incidents). The
   gate is a `!` total energy, a printed "convergence has been achieved", and a final
   `estimated scf accuracy` at or below the deck's own conv_thr.

Two pieces of physics the report leans on, stated so a referee can check them
-----------------------------------------------------------------------------
**A partial Hessian can only under-report instability.** For a symmetric H and the principal
submatrix H_AA on the adsorbate coordinates, if v^T H_AA v < 0 then the padded vector (v, 0)
gives the same negative curvature in the full Hessian. Mass-weighting is a congruence by a
positive-definite diagonal, which preserves the signs of the eigenvalues. So an imaginary mode
here is an imaginary mode of the full system, rigorously. The converse does not hold: an
all-real adsorbate spectrum does not prove the full Hessian is positive definite, only that no
unstable direction is confined to the adsorbate — **and, at q = 0 in a 1x1 cell, only that no
such direction exists at the zone centre.** The verdict wording respects both asymmetries and
it must survive into the report.

**At an exactly mirror-symmetric reference the out-of-plane block decouples exactly.** Every
adsorbate atom lies in the plane y = y_cus, so the mirror acts on displacements as
diag(1, -1, 1) atom by atom, forcing H_{x,y} = H_{z,y} = 0 identically. The 9x9 adsorbate
Hessian block-diagonalises into a 6x6 in-plane (x, z) block and a 3x3 out-of-plane (y) block,
and the three y modes are exactly the coordinates the production relaxations could not
explore: adsorbate yaw, out-of-plane tilt, and rigid y translation. Two consequences:

  * **docs/43 §3-A.8: the 1C verdict rests on the ±y block.** The ±x/±z decks are bought for
    block 2B's ZPE/-TS table; F_y is identically zero in all of them. Their modes are still
    reported, and an above-floor imaginary one still makes the state AMBIGUOUS, but they
    cannot produce a CONFIRMED.
  * the y block is at an EXACT stationary point even though the in-plane block is not. The
    source relaxations stopped at forc_conv_thr = 2e-3 Ry/au and carry residual in-plane
    gradients on the adsorbate (measured: 8.7e-4 Ry/au on Ir, 1.8e-3 on Cr), while max|F_y| is
    exactly 0.0000000000 because the mirror makes y stationary by symmetry, not by
    convergence. In-plane curvatures are therefore reported as curvatures at a point that is
    not an in-plane minimum, and are indicative only.

Usage
-----
  PYTHONPATH=src python src/dft/hessian_analyze.py runs/probe/Ir_hess
  PYTHONPATH=src python src/dft/hessian_analyze.py --print-prereg
  PYTHONPATH=src python src/dft/hessian_analyze.py runs/probe/Ir_hess --json out.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys

import numpy as np

RY_EV = 13.605693122
BOHR_A = 0.529177210903
RY_BOHR_TO_EV_A = RY_EV / BOHR_A                     # 25.711042 eV/A per Ry/bohr
CM1_PER_ROOT = 521.4708                              # nu[cm^-1] = 521.4708 * sqrt(eV/A^2/amu)

# ---------------------------------------------------------------------------------------
# Registered numbers. Each is docs/43's, with the clause it comes from. This file may not
# change any of them; changing one is amending the pre-registration.
# ---------------------------------------------------------------------------------------
NU_NOISE_CM1 = 50.0          # docs/43 §3 verdict table: the DECLARED floor
LAMBDA_NOISE = (NU_NOISE_CM1 / CM1_PER_ROOT) ** 2     # 9.194e-3 eV/(A^2 amu)
N_SIGMA = 3.0                # docs/43 §3-A.3: effective floor = max(50 cm^-1, 3 sigma)
FY_MIN = 0.50                # docs/43 §3 verdict table, RE-AFFIRMED §3-A.6 against the
#                            # builder's 0.90: "a registered threshold is not moved without
#                            # a stated reason", and none was given.
UNDERPOWERED_NU_CM1 = 80.0   # docs/43 §3-A.1/§3-A.3: floor above this on the y modes is
#                            # blindness, and blindness is not a null.
MAG_TOL_MUB = 0.10           # docs/43 §3 magnetic guard
MAG_EXCLUSIONS_MAX = 2       # docs/43 §3 "More than 2 exclusions of 18 voids the state",
#                            # RE-AFFIRMED §3-A.6 against the builder's "any single one".
Q0_E_TOL_EV = 0.010          # docs/43 §3-A.5
Q0_M_TOL_MUB = 0.10          # docs/43 §3-A.5
SIGMA_F_DESIGN = 1.0e-5      # Ry/bohr, the force noise conv_thr = 1e-10 was chosen to deliver
SIGMA_F_FACTOR = 5.0         # docs/43 §3-A.4: absolute cap, x design, before Q4a fails
OUTLIER_FACTOR = 5.0         # x rms before one element is an outlier
ASYM_REL_REPORTED = 0.05     # docs/43 §3's OLD relative gate. WITHDRAWN as a gate by §3-A.4
#                            # (max|H_ij| is dominated by the O-H stretch at ~48 eV/A^2/amu,
#                            # so 5% of it is ~2.4 against an expected asymmetry of ~0.05 --
#                            # the gate was toothless). Retained as a reported diagnostic
#                            # only, so the withdrawn number stays visible.

REGISTERED_STATES = ("Ir", "Cr")   # docs/43 §3; Cr is HELD by §3-A.7 pending block 1A

AXIS_I = {"x": 0, "y": 1, "z": 2}

#: Every coded gate traced to the docs/43 clause it enforces. Review finding [28](6) was that
#: Q1/Q2/Q5 "exist only in the code"; they are not new criteria, they are the enforcement of
#: §3's own "Method, fixed in advance", and this table is how a referee checks that claim.
GATE_PROVENANCE = {
    "Q0": "docs/43 §3-A.5 — the reference must be the state it claims to be",
    "Q1": "docs/43 §3 'Method': conv_thr = 1e-10. Enforced as: a '!' total energy, a printed "
          "'convergence has been achieved', and a final estimated scf accuracy <= conv_thr. "
          "'JOB DONE' is explicitly not accepted (lessons.md, three incidents).",
    "Q2": "docs/43 §3 'Method': nosym/noinv on EVERY displacement including the reference, "
          "and an identical k-point set throughout.",
    "Q3": "docs/43 §3 'Magnetic guard', tolerance 0.1 mu_B, >2 exclusions of 18 voids.",
    "Q4": "docs/43 §3-A.4 — the Hessian-symmetry gate, made absolute.",
    "Q5": "docs/43 §3 'Method': the mirror is asserted, so its exact prediction "
          "H_(y,xz) = 0 is checked rather than assumed.",
}

PREREG_POINTER = """\
The pre-registered rule for block 1C is docs/43-prereg-week1-factorial.md, §3 (P14) and §3-A
(amendment 1, 2026-08-09, written before any block-1C job ran).

This program holds NO copy of it. `--print-prereg` reads those two sections out of docs/43
and prints them verbatim. If the file below cannot be read, the rule cannot be printed, and
that is deliberate: a copy is how the code and the pre-registration came apart in the first
place."""


def read_prereg(path: str | None = None) -> tuple[str, str]:
    """(text, source_path) — docs/43 §3 and §3-A, read out of the document itself."""
    if path is None:
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.normpath(os.path.join(here, "..", "..", "docs",
                                             "43-prereg-week1-factorial.md"))
    if not os.path.exists(path):
        raise SystemExit(f"cannot read the pre-registration: {path} does not exist. "
                         f"Pass --prereg-path. This program keeps no copy on purpose.")
    txt = open(path, encoding="utf-8").read()
    out = []
    for pat, label in ((r"^## 3\. P14.*?(?=^## \d+\.)", "§3 (P14)"),
                       (r"^## §3-A.*?(?=^## §|\Z)", "§3-A (amendment 1)")):
        m = re.search(pat, txt, re.M | re.S)
        if not m:
            raise SystemExit(f"cannot find {label} in {path}. docs/43 has been restructured; "
                             f"fix the extractor rather than pasting a copy in here.")
        out.append(m.group(0).rstrip())
    return "\n\n".join(out), path


# ------------------------------------------------------------------ parsing ---

def parse_scf_out(path: str) -> dict:
    """Everything the gates need from one pw.x SCF output."""
    r = dict(path=path, exists=os.path.exists(path))
    if not r["exists"]:
        return r
    txt = open(path, errors="replace").read()
    e = re.findall(r"^!\s+total energy\s+=\s+([-\d.]+)\s+Ry", txt, re.M)
    r["energy_ev"] = float(e[-1]) * RY_EV if e else None
    r["job_done"] = "JOB DONE" in txt
    r["scf_fail"] = "convergence NOT achieved" in txt
    r["scf_converged"] = "convergence has been achieved" in txt
    acc = re.findall(r"estimated scf accuracy\s+<\s+([\d.eE+-]+)\s*Ry", txt)
    r["scf_accuracy"] = float(acc[-1]) if acc else None
    m = re.search(r"number of k points=\s*(\d+)", txt)
    r["nk"] = int(m.group(1)) if m else None
    r["no_symmetry"] = "No symmetry found" in txt
    sym = re.findall(r"^\s+(\d+)\s+Sym\. Ops", txt, re.M)
    r["sym_ops"] = int(sym[0]) if sym else (1 if r["no_symmetry"] else None)
    mag = re.findall(r"total magnetization\s+=\s+([-\d.]+)\s+Bohr mag/cell", txt)
    r["total_mag"] = float(mag[-1]) if mag else None
    amag = re.findall(r"absolute magnetization\s+=\s+([-\d.]+)\s+Bohr mag/cell", txt)
    r["abs_mag"] = float(amag[-1]) if amag else None
    blocks = re.findall(
        r"Forces acting on atoms.*?\n\n((?:\s*atom\s+\d+ type\s+\d+\s+force =.*\n)+)", txt)
    r["forces"] = ([[float(v) for v in line.split("force =")[1].split()]
                    for line in blocks[-1].strip().split("\n")] if blocks else None)
    return r


def _conv_thr_value(s: str) -> float:
    return float(s.lower().replace("d", "e"))


# -------------------------------------------------------------------- gates ---

def run_gates(man: dict, outs: dict) -> dict:
    """Q0-Q3. Q4/Q5 need the Hessian and are applied in score_state."""
    thr = _conv_thr_value(man["conv_thr"])
    ref_job = man["reference_job"]
    ref = outs[ref_job]
    fails, notes = [], []

    # ---- Q0: the reference must be the state it claims to be (docs/43 §3-A.5) ----
    e_src = man.get("source_final_energy_ev", man.get("reference_relax_energy_ev"))
    if e_src is None:
        fails.append("Q0: manifest carries no source_final_energy_ev — the reference cannot "
                     "be checked against the relaxation it claims to be (docs/43 §3-A.5)")
    elif ref.get("energy_ev") is None:
        pass                       # Q1 already reports the missing energy; do not double-count
    else:
        dE = ref["energy_ev"] - e_src
        notes.append(f"Q0 energy: reference SCF {ref['energy_ev']:.6f} eV vs source "
                     f"relaxation {e_src:.6f} eV, delta = {dE * 1000:+.3f} meV "
                     f"(tolerance +/-{Q0_E_TOL_EV * 1000:.0f} meV)")
        if abs(dE) > Q0_E_TOL_EV:
            fails.append(
                f"Q0 {ref_job}: reference SCF is {dE * 1000:+.1f} meV from the source "
                f"relaxation's final energy (tolerance {Q0_E_TOL_EV * 1000:.0f} meV). All 19 "
                f"jobs start from a fresh superposition, so they can agree with each other "
                f"while collectively sitting in the wrong basin — docs/41 §6f. This Hessian "
                f"would not be the Hessian of the state the eta was computed in.")
    if man["nspin"] == 2:
        m_src = man.get("source_final_total_mag")
        if m_src is None:
            fails.append("Q0: nspin = 2 but the manifest carries no source_final_total_mag "
                         "(docs/43 §3-A.5)")
        elif ref.get("total_mag") is not None:
            dM = ref["total_mag"] - m_src
            notes.append(f"Q0 magnetisation: reference {ref['total_mag']:.3f} vs source "
                         f"{m_src:.3f} mu_B, delta = {dM:+.3f}")
            if abs(dM) > Q0_M_TOL_MUB:
                fails.append(
                    f"Q0 {ref_job}: reference M = {ref['total_mag']:.3f} mu_B vs the source "
                    f"relaxation's {m_src:.3f} (|d| = {abs(dM):.3f} > {Q0_M_TOL_MUB}). "
                    f"DIFFERENT MAGNETIC BASIN — this is docs/41 §6f, where a fresh SCF at "
                    f"identical coordinates sat 175 meV away in another solution.")

    # ---- Q1/Q2 per job ----
    for rec in man["jobs"]:
        o = outs[rec["job"]]
        if not o["exists"]:
            fails.append(f"Q1 {rec['job']}: no .out")
            continue
        if o["energy_ev"] is None:
            fails.append(f"Q1 {rec['job']}: no total energy "
                         f"(JOB_DONE={o['job_done']} — 'JOB DONE' is not success)")
        if o["scf_fail"]:
            fails.append(f"Q1 {rec['job']}: convergence NOT achieved")
        elif not o["scf_converged"]:
            fails.append(f"Q1 {rec['job']}: no 'convergence has been achieved' line "
                         f"(JOB_DONE={o['job_done']} — pw.x prints JOB DONE after nstep "
                         f"exhaustion and after a user .EXIT too)")
        if o["scf_accuracy"] is not None and o["scf_accuracy"] > thr:
            fails.append(f"Q1 {rec['job']}: final scf accuracy {o['scf_accuracy']:.2e} "
                         f"> conv_thr {thr:.0e}")
        if not o["no_symmetry"]:
            fails.append(f"Q2 {rec['job']}: symmetry was NOT switched off "
                         f"(sym_ops={o['sym_ops']}) — this deck is not comparable to the rest")
        if o["nk"] != ref["nk"]:
            fails.append(f"Q2 {rec['job']}: nk={o['nk']} vs reference {ref['nk']}")
        if man.get("expected_nk") and o["nk"] != man["expected_nk"]:
            fails.append(f"Q2 {rec['job']}: nk={o['nk']} vs expected full mesh "
                         f"{man['expected_nk']}")

    # ---- Q3: magnetic-basin guard (docs/43 §3) ----
    contaminated = []
    if man["nspin"] == 2:
        mref = ref.get("total_mag")
        if mref is None:
            fails.append("Q3 reference: nspin=2 but no total magnetization printed")
        else:
            for rec in man["jobs"]:
                if rec["kind"] != "displacement":
                    continue
                m = outs[rec["job"]].get("total_mag")
                if m is None:
                    fails.append(f"Q3 {rec['job']}: no total magnetization")
                    contaminated.append(rec["job"])
                elif abs(m - mref) > MAG_TOL_MUB:
                    # docs/43 §3: "Such rows are excluded and LISTED. More than 2
                    # exclusions of 18 voids the state." So an exclusion inside the
                    # tolerated count is a NOTE, not a gate failure — scoring it as a
                    # failure is the "any single exclusion voids the state" behaviour
                    # §3-A.6 explicitly rejects.
                    notes.append(f"Q3 {rec['job']}: total magnetization {m:.3f} vs "
                                 f"reference {mref:.3f} mu_B (|d|={abs(m - mref):.3f} > "
                                 f"{MAG_TOL_MUB}) — DIFFERENT MAGNETIC BASIN, force row "
                                 f"EXCLUDED (not averaged, not symmetrised over)")
                    contaminated.append(rec["job"])
        notes.append(f"Q3 magnetic guard: reference M = {mref} mu_B, tolerance "
                     f"{MAG_TOL_MUB} mu_B, {len(contaminated)} exclusion(s) of "
                     f"{sum(1 for r in man['jobs'] if r['kind'] == 'displacement')} "
                     f"(docs/43 §3 voids the state above {MAG_EXCLUSIONS_MAX})")
        if len(contaminated) > MAG_EXCLUSIONS_MAX:
            fails.append(f"Q3: {len(contaminated)} magnetic exclusions > "
                         f"{MAG_EXCLUSIONS_MAX} of 18 — docs/43 §3 voids the state.")
    else:
        notes.append("Q3 magnetic guard: NOT APPLICABLE (nspin = 1). Not a pass.")

    return dict(fails=fails, notes=notes, contaminated=contaminated)


# ------------------------------------------------------------------ hessian ---

def build_hessian(man: dict, outs: dict, contaminated) -> dict:
    """Principal submatrix of the adsorbate Hessian on the coordinates that are USABLE.

    H[a, b] = -[F_b(+delta on a) - F_b(-delta on a)] / (delta_plus - delta_minus)

    A coordinate whose +/- pair is incomplete, contaminated or force-less is dropped from
    BOTH the row and the column set (docs/43 §3: "such rows are excluded and listed"; made
    square so it can be diagonalised). A principal submatrix of a symmetric H can only
    under-report instability, so the physics argument in the module docstring survives the
    reduction intact — which is the whole reason exclusion is a reduction and not an average.

    The denominator is the REALISED step read back out of the emitted decks, not the nominal
    2*delta: coordinates are written to 8 decimals while pw.x prints its relaxed geometry to
    10, so +delta and -delta each carry up to 5e-9 A of rounding.
    """
    ads0 = [i - 1 for i in man["adsorbate_indices_1based"]]
    pairs = {}
    for rec in man["jobs"]:
        if rec["kind"] != "displacement":
            continue
        pairs.setdefault((rec["atom_index0"], rec["axis"]), {})[rec["sign"]] = rec

    coords, dropped, rows = [], [], {}
    for (atom0, axis), sgn in sorted(pairs.items(), key=lambda kv: (ads0.index(kv[0][0]),
                                                                   AXIS_I[kv[0][1]])):
        tag = f"a{atom0 + 1}{axis}"
        if +1 not in sgn or -1 not in sgn:
            dropped.append(f"{tag}: incomplete +/- pair")
            continue
        jp, jm = sgn[+1], sgn[-1]
        if jp["job"] in contaminated or jm["job"] in contaminated:
            dropped.append(f"{tag}: excluded, magnetic-basin contamination")
            continue
        fp, fm = outs[jp["job"]].get("forces"), outs[jm["job"]].get("forces")
        if not fp or not fm:
            dropped.append(f"{tag}: missing force block")
            continue
        step = jp["displacement_A"] - jm["displacement_A"]      # ~ +0.02 A
        if abs(step) < 1e-6:
            dropped.append(f"{tag}: degenerate step {step}")
            continue
        coords.append((atom0, axis))
        rows[(atom0, axis)] = (fp, fm, step)

    n = len(coords)
    H = np.zeros((n, n))
    for a, (atom0, axis) in enumerate(coords):
        fp, fm, step = rows[(atom0, axis)]
        for b, (atomq, axq) in enumerate(coords):
            i = AXIS_I[axq]
            dF = (fp[atomq][i] - fm[atomq][i]) * RY_BOHR_TO_EV_A    # eV/A
            H[a, b] = -dF / step                                    # eV/A^2

    mass_of = {i - 1: m for i, m in zip(man["adsorbate_indices_1based"],
                                        man["adsorbate_masses_amu"])}
    masses = np.array([mass_of[a] for a, _ in coords], float) if n else np.zeros(0)
    w = 1.0 / np.sqrt(masses) if n else np.zeros(0)
    D = H * np.outer(w, w) if n else H
    return dict(H=H, D=D, coords=coords, dropped=dropped, masses=masses,
                n_expected=len(pairs))


def spectrum(D: np.ndarray, coords, masses: np.ndarray, sig_D: np.ndarray) -> list:
    """Modes of the mass-weighted Hessian, each with its own propagated noise floor.

    sigma_lambda_k^2 = sum_ij (v_i v_j)^2 sigma(D_ij)^2, which follows from lambda = v^T D v
    with v fixed to first order. The floor is mass dependent because
    sigma(D_ij) = sigma(H)/sqrt(m_i m_j) and this adsorbate contains both O and H — which is
    the whole reason docs/43 §3-A.3 needed an UNDERPOWERED verdict.
    """
    Ds = 0.5 * (D + D.T)
    vals, vecs = np.linalg.eigh(Ds)
    is_y = np.array([ax == "y" for _a, ax in coords])
    atoms = [a for a, _ax in coords]
    uniq = sorted(set(atoms), key=atoms.index)
    w = np.sqrt(masses)
    out = []
    for k in range(len(vals)):
        lam = float(vals[k])
        v = vecs[:, k]
        v2 = v ** 2
        sig_lam = float(np.sqrt(np.einsum("i,j,ij->", v2, v2, sig_D ** 2)))
        lam_floor = max(LAMBDA_NOISE, N_SIGMA * sig_lam)
        fy_mw = float(v2[is_y].sum() / v2.sum())
        u = v / w
        u2 = u ** 2
        fy_ca = float(u2[is_y].sum() / u2.sum())
        amp = np.array([v2[[i for i, a in enumerate(atoms) if a == at]].sum() for at in uniq])
        out.append(dict(index=k, lam=lam, imaginary=lam < 0,
                        nu_cm1=CM1_PER_ROOT * math.sqrt(abs(lam)),
                        sigma_lambda=sig_lam,
                        lambda_floor=lam_floor,
                        nu_floor_cm1=CM1_PER_ROOT * math.sqrt(lam_floor),
                        significant=abs(lam) >= lam_floor,
                        fy_massweighted=fy_mw, fy_cartesian=fy_ca,
                        atom_weights=[float(a) for a in amp / amp.sum()]))
    return out


# ------------------------------------------------------------------ verdict ---

def _scope(man: dict) -> str:
    return man.get("verdict_scope") or "q = 0, 1x1 cell, 1 ML"


def score_state(man: dict, outs: dict) -> dict:
    """One state's per-state verdict, exactly the five of docs/43 §3-A.1.

    PRECEDENCE, stated because §3-A.1 lists conditions that can co-occur:

        VOID > CONFIRMED > UNDERPOWERED > AMBIGUOUS > REFUTED

    VOID first because a failed gate means there is no measurement to interpret. CONFIRMED
    over UNDERPOWERED because a mode found ABOVE a high floor has been found — the power
    verdict exists for the case where nothing was seen and nothing could have been (§3-A.3,
    "blindness is not a null"), so it must outrank the two not-seen verdicts and only those.
    AMBIGUOUS over REFUTED because an above-floor imaginary mode is a positive observation,
    just not of the right character.
    """
    g = run_gates(man, outs)
    hb = build_hessian(man, outs, g["contaminated"])
    H, D, coords = hb["H"], hb["D"], hb["coords"]
    scope = _scope(man)

    res = dict(state=man["state"], job=man["job"], source_run=man["source_run"],
               scope=scope, cell=man.get("cell_label", "1x1"),
               coverage_ML=man.get("coverage_ML", 1.0),
               wavevector=man.get("wavevector", "Gamma (q = 0)"),
               gate_failures=list(g["fails"]), gate_notes=list(g["notes"]),
               contaminated=g["contaminated"], dropped_coordinates=hb["dropped"],
               coordinates_used=[f"a{a+1}{ax}" for a, ax in coords],
               mirror_plane=man.get("mirror_plane", True),
               prereg="docs/43 §3 + §3-A", gate_provenance=dict(GATE_PROVENANCE))

    def void(reason):
        res["verdict"] = "VOID"
        res["reason"] = reason
        res.setdefault("modes", [])
        return res

    n_y = sum(1 for _a, ax in coords if ax == "y")
    if hb["dropped"]:
        res["gate_notes"].append(
            f"{len(hb['dropped'])} coordinate(s) dropped -> the Hessian is the "
            f"{len(coords)}x{len(coords)} PRINCIPAL SUBMATRIX on the survivors, not the full "
            f"{hb['n_expected']}x{hb['n_expected']}: {'; '.join(hb['dropped'])}")
    if n_y == 0:
        res["gate_failures"].append(
            f"the +/-y block is empty ({len(coords)} of {hb['n_expected']} coordinates "
            f"usable). docs/43 §3-A.8 puts the 1C verdict on that block, so with no y "
            f"coordinate there is no verdict to give — not a null, an absence.")
        return void(f"{len(res['gate_failures'])} gate failure(s); the y block is empty. "
                    f"NOT a scientific result: rerun the failing jobs.")

    # ---- Q4: noise, measured from the Hessian's own asymmetry (docs/43 §3-A.4) ----
    asym_D = float(np.abs(D - D.T).max())
    asym_H = float(np.abs(H - H.T).max())
    rel = asym_D / float(np.abs(D).max()) if np.abs(D).max() > 0 else float("nan")
    # The asymmetry is a pure noise observable: an exact Hessian is symmetric, so whatever is
    # left is error. H_ij and H_ji come from DIFFERENT pairs of SCFs, so they are independent
    # and sigma(H_ij - H_ji) = 2 sigma_F / (2 delta) = sigma_F / delta.
    off = np.abs(H - H.T)[np.triu_indices_from(H, 1)]
    rms_asym = float(np.sqrt(np.mean(off ** 2))) if off.size else 0.0
    delta_A = man["delta_nominal_angstrom"]
    sigma_F_eV_A = rms_asym * delta_A
    sigma_F_ry = sigma_F_eV_A / RY_BOHR_TO_EV_A
    sigma_H = sigma_F_eV_A / (math.sqrt(2) * delta_A)       # per-element sigma of H, eV/A^2
    root_m = np.sqrt(hb["masses"])
    sig_D = sigma_H / np.outer(root_m, root_m)              # per-element sigma of D
    res.update(hessian_asymmetry_D=asym_D, hessian_asymmetry_H_eV_A2=asym_H,
               hessian_asymmetry_relative=rel, lambda_noise_declared=LAMBDA_NOISE,
               measured_sigma_F_eV_per_A=sigma_F_eV_A,
               measured_sigma_F_Ry_per_bohr=sigma_F_ry,
               design_sigma_F_Ry_per_bohr=SIGMA_F_DESIGN)

    if sigma_F_ry > SIGMA_F_FACTOR * SIGMA_F_DESIGN:
        res["gate_failures"].append(
            f"Q4a measured sigma_F = {sigma_F_ry:.2e} Ry/bohr > {SIGMA_F_FACTOR:.0f} x the "
            f"{SIGMA_F_DESIGN:.0e} design value that justified conv_thr = 1e-10. The SCFs are "
            f"not as converged as the threshold assumed. Declared escalation: rerun at "
            f"conv_thr = 1e-12. Do not widen this gate. NOTE, measured 2026-08-09: at "
            f"conv_thr = 1e-12 the Davidson threshold QE would need is ~2.5 decades below its "
            f"own MAX(ethr, 1e-13) clamp, so probe ONE job before spending 19 on it.")
    if len(off) >= 6 and rms_asym > 0 and asym_H > OUTLIER_FACTOR * rms_asym:
        i, j = np.unravel_index(int(np.argmax(np.abs(H - H.T))), H.shape)
        ci = f"a{coords[i][0] + 1}{coords[i][1]}"
        cj = f"a{coords[j][0] + 1}{coords[j][1]}"
        res["gate_failures"].append(
            f"Q4b element ({ci},{cj}) asymmetry {asym_H:.3e} eV/A^2 is "
            f"{asym_H / rms_asym:.1f}x the rms — uniform noise cannot do that. One of the "
            f"jobs feeding {ci} or {cj} is bad (magnetic basin too small for the "
            f"{MAG_TOL_MUB} mu_B guard, or an unconverged SCF).")
    if not math.isnan(rel) and rel > ASYM_REL_REPORTED:
        res["gate_notes"].append(
            f"reported diagnostic (docs/43 §3's OLD relative gate, WITHDRAWN as a gate by "
            f"§3-A.4 because max|D_ij| is dominated by the O-H stretch): relative asymmetry "
            f"{rel:.1%} > {ASYM_REL_REPORTED:.0%}")

    # ---- Q5: mirror block structure (only meaningful at a mirror-symmetric reference) ----
    idx_y = [k for k, (_a, ax) in enumerate(coords) if ax == "y"]
    idx_xz = [k for k, (_a, ax) in enumerate(coords) if ax != "y"]
    if res["mirror_plane"] and idx_y and idx_xz:
        cross = float(np.abs(D[np.ix_(idx_y, idx_xz)]).max())
        cross_gate = max(LAMBDA_NOISE, N_SIGMA * float(sig_D[np.ix_(idx_y, idx_xz)].max()))
        res["mirror_cross_block_max"] = cross
        res["mirror_cross_block_gate"] = cross_gate
        if cross > cross_gate:
            res["gate_failures"].append(
                f"Q5 y/xz cross-block max|D| = {cross:.3e} > {cross_gate:.3e}. The mirror "
                f"predicts exactly zero here; a value above noise means the reference is not "
                f"the symmetric state claimed, or the numerics leak.")
    elif not res["mirror_plane"]:
        res["gate_notes"].append("Q5 NOT APPLICABLE: manifest says mirror_plane = false")
    else:
        res["gate_notes"].append("Q5 NOT APPLICABLE: no y/xz cross block survives")

    modes = spectrum(D, coords, hb["masses"], sig_D)
    res["modes"] = modes

    oop = [m for m in modes if m["imaginary"] and m["significant"]
           and m["fy_massweighted"] >= FY_MIN]
    inplane = [m for m in modes if m["imaginary"] and m["significant"]
               and m["fy_massweighted"] < FY_MIN]
    soft = [m for m in modes if m["imaginary"] and not m["significant"]]
    ymodes = [m for m in modes if m["fy_massweighted"] >= FY_MIN]
    # docs/43 §3-A.3 asks for "the effective floor on the highest-y-character mode". At an
    # exactly mirror-symmetric reference the y block decouples, so EVERY y mode has
    # f_y = 1 and an argmax over f_y is an arbitrary tie-break. The quantity §3-A.3 is about
    # is whether an imaginary y mode could have been seen, so the binding number is the
    # WORST floor among the y-character modes. Stated here because it is an interpretation.
    worst_y = max(ymodes, key=lambda m: m["nu_floor_cm1"]) if ymodes else None
    res.update(n_imag_out_of_plane=len(oop), n_imag_in_plane=len(inplane),
               n_imag_below_floor=len(soft),
               y_mode_worst_floor_cm1=(worst_y["nu_floor_cm1"] if worst_y else None),
               underpowered_threshold_cm1=UNDERPOWERED_NU_CM1)

    confined = ("Report as: NO UNSTABLE DIRECTION IS CONFINED TO THE ADSORBATE. This is "
                "weaker than 'the geometry is a minimum' and must be written that way; a "
                "partial Hessian cannot exclude an instability involving slab coordinates.")
    wavevec = (f"And it is scoped to {scope}: an all-real Gamma-point spectrum in a 1x1 cell "
               f"does not exclude an instability at another wavevector (docs/43 §3-A.7).")

    # ---------------- the five verdicts, in the precedence above ----------------
    if res["gate_failures"]:
        return void(
            f"{len(res['gate_failures'])} quality gate(s) failed; see the list. **This is "
            f"NOT a scientific result and it is not a null.** docs/43 §3-A.1: a state with a "
            f"failed gate is VOID, the declared response is to rerun the failing jobs, and "
            f"it may not reach the R3 branch.")

    if oop:
        res["verdict"] = "CONFIRMED"
        res["reason"] = (
            f"{len(oop)} out-of-plane imaginary mode(s) at {scope}: "
            + ", ".join(f"i{m['nu_cm1']:.0f} cm^-1 (f_y={m['fy_massweighted']:.3f}, floor "
                        f"i{m['nu_floor_cm1']:.0f})" for m in oop)
            + ". A negative curvature in a principal submatrix is a negative curvature of the "
              "full Hessian, so the on-record constrained geometry is a saddle point.")
    elif worst_y is not None and worst_y["nu_floor_cm1"] > UNDERPOWERED_NU_CM1:
        res["verdict"] = "UNDERPOWERED"
        res["reason"] = (
            f"gates passed, but the effective floor on the y-character modes reaches "
            f"i{worst_y['nu_floor_cm1']:.0f} cm^-1 (mode #{worst_y['index']}, "
            f"f_y={worst_y['fy_massweighted']:.3f}, atom weights "
            f"{['%.2f' % w for w in worst_y['atom_weights']]}), above the declared "
            f"i{UNDERPOWERED_NU_CM1:.0f} cm^-1. The out-of-plane modes of *OOH are "
            f"H-dominated and the floor is mass dependent, so this run could not have "
            f"resolved the mode it exists to detect. **Blindness is not a null "
            f"(docs/43 §3-A.3).** Declared response: rerun at tighter conv_thr — NOT R3. "
            f"Measured 2026-08-09: conv_thr = 1e-12 needs a Davidson threshold ~2.5 decades "
            f"below QE's MAX(ethr, 1e-13) clamp, so probe one job before spending 19.")
    elif inplane:
        res["verdict"] = "AMBIGUOUS"
        res["reason"] = (
            f"{len(inplane)} imaginary mode(s) above their effective floor but IN-PLANE "
            f"(f_y < {FY_MIN:.2f}): "
            + ", ".join(f"i{m['nu_cm1']:.0f} cm^-1 (f_y={m['fy_massweighted']:.3f})"
                        for m in inplane)
            + f". An in-plane or mixed instability does not support the out-of-plane claim, "
              f"and at this geometry the in-plane block is not even at a stationary point "
              f"(residual gradient up to 1.8e-3 Ry/au). Scope: {scope}.")
    else:
        res["verdict"] = "REFUTED"
        soft_txt = ""
        if soft:
            biggest = max(soft, key=lambda m: m["nu_cm1"])
            soft_txt = (
                f" {len(soft)} imaginary mode(s) sit BELOW their own effective floor and are "
                f"reported as noise, not as a result: "
                + ", ".join(f"#{m['index']} i{m['nu_cm1']:.1f} cm^-1 (floor "
                            f"i{m['nu_floor_cm1']:.0f}, f_y={m['fy_massweighted']:.2f})"
                            for m in soft)
                + f"; the largest is i{biggest['nu_cm1']:.1f} cm^-1 against a floor of "
                  f"i{biggest['nu_floor_cm1']:.0f} cm^-1.")
        res["reason"] = (
            f"No imaginary mode reaches its effective floor (declared i{NU_NOISE_CM1:.0f} "
            f"cm^-1, measured {N_SIGMA:.0f}-sigma per mode).{soft_txt} {confined} {wavevec}")
    return res


def campaign_verdict(results: list) -> str:
    """docs/43 §3 'Declared consequence' as amended by §3-A.1.

    Only gate-clean CONFIRMED/REFUTED states may reach the R3 branch. A VOID state stops the
    campaign decision outright; an UNDERPOWERED state routes to a tighter rerun. Before this
    was fixed, 19 synthetic outputs whose only defect was a missed conv_thr printed
    "NEITHER CONFIRMED -> R3 TRIGGERED" — a compute failure wearing a scientific null's
    clothes, and the one outcome that cannot be repaired after the jobs run.
    """
    by = {r["state"]: r["verdict"] for r in results}
    void = [r["state"] for r in results if r["verdict"] == "VOID"]
    under = [r["state"] for r in results if r["verdict"] == "UNDERPOWERED"]
    conf = [r["state"] for r in results if r["verdict"] == "CONFIRMED"]
    refu = [r["state"] for r in results if r["verdict"] == "REFUTED"]
    amb = [r["state"] for r in results if r["verdict"] == "AMBIGUOUS"]
    listing = ", ".join(f"{k}={v}" for k, v in by.items())

    if void:
        nf = sum(len(r["gate_failures"]) for r in results if r["verdict"] == "VOID")
        return (f"PILOT INVALID - no campaign decision. VOID: {', '.join(void)} "
                f"({nf} gate failure(s) total). [{listing}]\n"
                f"  A VOID state is a COMPUTE failure, not a scientific null. The declared "
                f"response is to rerun the failing jobs and re-score; the R3 branch of "
                f"docs/43 §3 is NOT reachable from here and block 2B is neither authorised "
                f"nor cancelled.")

    if under:
        return (f"RERUN AT TIGHTER conv_thr - no campaign decision. UNDERPOWERED: "
                f"{', '.join(under)}. [{listing}]\n"
                f"  The effective floor on the y-character modes exceeds "
                f"i{UNDERPOWERED_NU_CM1:.0f} cm^-1, so the pilot could not have resolved the "
                f"mode it exists to detect. docs/43 §3-A.3: blindness is not a null, and the "
                f"declared response is a tighter conv_thr, NOT R3.\n"
                f"  Before spending 19 SCFs on conv_thr = 1e-12: the 2026-08-09 feasibility "
                f"probe measured ethr = 1.79E-13 on the last iteration at 1e-10, i.e. one "
                f"decade above QE's MAX(ethr, 1e-13) clamp. 1e-12 would run its last decades "
                f"against a FIXED diagonalisation floor. Probe one job first.")

    missing = [s for s in REGISTERED_STATES if s not in by]
    if missing:
        held = [s for s in missing]
        return (f"PARTIAL PILOT - no campaign decision yet. Scored: [{listing}]. "
                f"Not scored: {', '.join(held)} (docs/43 §3-A.7 holds Cr until block 1A "
                f"returns its cell verdict).\n"
                f"  docs/43 §3's consequence is keyed on BOTH registered states. In "
                f"particular a single REFUTED cannot fire R3: with one state held, "
                f"'no unstable direction confined to the adsorbate' has been shown for that "
                f"state at q = 0 in a 1x1 cell and for nothing else.")

    if len(conf) == len(results):
        return (f"BOTH CONFIRMED -> the lead contribution keeps its proof. Block 2B "
                f"(21 states x 18 SCFs = 378 SCFs) is authorised as planned. [{listing}]\n"
                f"  Scoped to q = 0, 1x1 cell, 1 ML.")
    if len(conf) == 1:
        cls = "nspin = 1 anchors" if conf[0] == "Ir" else "magnetic 3d oxides"
        return (f"EXACTLY ONE CONFIRMED ({conf[0]}) -> the proof is per state, not per tier. "
                f"Block 2B is authorised only for the {cls}, and the report says so. "
                f"[{listing}]")
    if len(refu) == len(results):
        return (f"NEITHER CONFIRMED, both gate-clean REFUTED -> R3 TRIGGERED. Do not spend "
                f"the 378 SCFs. [{listing}]\n"
                f"  Reweight the lead to S1 (scaling floor) + S4 (error budget and "
                f"resolution); report the symmetry result as an energy measurement with a "
                f"number and no saddle-point claim, and state that P10's -0.291 eV on Ir is "
                f"a finite-rotation basin change over a barrier.\n"
                f"  Scope that must travel with this: q = 0, 1x1 cell, 1 ML. An all-real "
                f"Gamma-point spectrum in a 1x1 cell does not exclude an instability at "
                f"another wavevector.")
    return (f"NO CAMPAIGN DECISION. [{listing}] {len(amb)} state(s) AMBIGUOUS: the gates "
            f"passed and the spectrum does not decide. docs/43 §3-A.1 lets only gate-clean "
            f"CONFIRMED/REFUTED states reach the R3 branch, and AMBIGUOUS is neither, so R3 "
            f"is NOT triggered and block 2B is NOT authorised.")


# ------------------------------------------------------------------ reporting ---

def report(res: dict, man: dict) -> None:
    print(f"\n{'=' * 78}\n{res['state']}  {res['job']}   ({res['source_run']})\n{'=' * 78}")
    print(f"  RULE                   : {res['prereg']} (no copy lives in this program; "
          f"--print-prereg reads it out of the doc)")
    print(f"  SCOPE                  : {res['scope']}  [cell {res['cell']}, "
          f"{res['coverage_ML']} ML, {res['wavevector']}]")
    if man.get("min_image_contact_angstrom"):
        print(f"  min image contact      : {man['min_image_contact_angstrom']:.3f} A "
              f"{man.get('min_image_contact_label', '')} — the coverage the scope is about")
    print(f"  reference geometry     : {man['geometry_provenance']}, source relaxation "
          f"E = {man.get('source_final_energy_ev', man['reference_relax_energy_ev']):.4f} eV"
          + (f", M = {man['source_final_total_mag']} mu_B"
             if man.get("source_final_total_mag") is not None else ""))
    print(f"  adsorbate              : {man['adsorbate_species']} at atoms "
          f"{man['adsorbate_indices_1based']}, masses {man['adsorbate_masses_amu']} amu")
    print(f"  mirror plane           : {man['mirror_plane']} at y = "
          f"{man['mirror_y_angstrom']:.6f} A (spread "
          f"{man['mirror_y_spread_angstrom']:.1e} A)")
    print(f"  source relax residual  : max|F| component on adsorbate = "
          f"{man['source_relax_adsorbate_max_abs_F_component_ry_bohr']:.3e} Ry/au IN-PLANE; "
          f"max|F_y| = {man['source_relax_adsorbate_max_abs_Fy_ry_bohr']:.10f} Ry/au "
          f"(exactly zero by symmetry, so the y block IS at a stationary point)")
    print(f"  protocol               : nosym+noinv, conv_thr {man['conv_thr']}, "
          f"electron_maxstep {man.get('electron_maxstep', '?')}, delta "
          f"{man['delta_nominal_angstrom']} A, {man['expected_nk']} k-points, nspin "
          f"{man['nspin']}, U {man['hubbard'] or 'none'}")
    print(f"  coordinates used       : {len(res['coordinates_used'])} "
          f"({', '.join(res['coordinates_used']) or 'none'}); the 1C verdict rests on the "
          f"y coordinates (docs/43 §3-A.8)")

    for n in res["gate_notes"]:
        print(f"  note   : {n}")
    if res["gate_failures"]:
        print(f"  GATE FAILURES ({len(res['gate_failures'])}):")
        for f in res["gate_failures"]:
            print(f"    ! {f}")
    else:
        print("  gates  : Q0-Q5 pass")

    if "hessian_asymmetry_D" in res:
        print(f"\n  force noise measured from the Hessian asymmetry: sigma_F = "
              f"{res['measured_sigma_F_Ry_per_bohr']:.2e} Ry/bohr "
              f"({res['measured_sigma_F_eV_per_A']:.2e} eV/A)   [Q4a gate "
              f"{SIGMA_F_FACTOR * SIGMA_F_DESIGN:.0e}, design {SIGMA_F_DESIGN:.0e}]")
        print(f"  Hessian symmetry  max|D_ij-D_ji| = {res['hessian_asymmetry_D']:.3e} "
              f"eV/(A^2 amu), relative {res['hessian_asymmetry_relative']:.2%}   "
              f"[relative is REPORTED not gated, docs/43 §3-A.4]")
        if "mirror_cross_block_max" in res:
            print(f"  mirror decoupling max|D_(y,xz)| = "
                  f"{res['mirror_cross_block_max']:.3e}   [Q5 gate "
                  f"{res['mirror_cross_block_gate']:.3e}; symmetry says exactly 0]")

    if res.get("modes"):
        print(f"\n  {'#':>2}  {'nu (cm^-1)':>11}  {'lambda':>11}  {'floor':>10}  "
              f"{'f_y(mw)':>7}  {'f_y(ca)':>7}  atom wt")
        for m in res["modes"]:
            nu = f"i{m['nu_cm1']:.1f}" if m["imaginary"] else f"{m['nu_cm1']:.1f}"
            wt = " ".join(f"{w:.2f}" for w in m["atom_weights"])
            flag = ""
            if m["imaginary"] and m["significant"]:
                flag = ("  <== OUT-OF-PLANE IMAGINARY"
                        if m["fy_massweighted"] >= FY_MIN else "  <== imaginary, IN-PLANE")
            elif m["imaginary"]:
                flag = "  (imaginary, below its own floor -> noise, routes to REFUTED)"
            print(f"  {m['index']:>2}  {nu:>11}  {m['lam']:>11.4e}  "
                  f"{m['nu_floor_cm1']:>10.1f}  {m['fy_massweighted']:>7.3f}  "
                  f"{m['fy_cartesian']:>7.3f}  {wt}{flag}")
        print(f"  'floor' = max(declared i{NU_NOISE_CM1:.0f} cm^-1, {N_SIGMA:.0f}*sigma "
              f"propagated per mode from the measured sigma_F; it is mass dependent, so "
              f"H-carried modes have a higher floor than O-carried ones)")
        if res.get("y_mode_worst_floor_cm1") is not None:
            print(f"  worst floor among the y-character modes: "
                  f"i{res['y_mode_worst_floor_cm1']:.1f} cm^-1  "
                  f"[UNDERPOWERED above i{UNDERPOWERED_NU_CM1:.0f}, docs/43 §3-A.3]")

    print(f"\n  VERDICT: {res['verdict']}")
    print(f"  {res['reason']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="*", help="runs/probe/<M>_hess directories")
    ap.add_argument("--json", default=None, help="also write the full result as JSON")
    ap.add_argument("--print-prereg", action="store_true",
                    help="print docs/43 §3 + §3-A (read from the doc; no copy is held here)")
    ap.add_argument("--prereg-path", default=None,
                    help="override the path to docs/43-prereg-week1-factorial.md")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if a.print_prereg:
        text, src = read_prereg(a.prereg_path)
        print(PREREG_POINTER)
        print(f"\nsource: {src}\n{'=' * 78}\n")
        print(text)
        return 0
    if not a.dirs:
        ap.error("give at least one runs/probe/<M>_hess directory, or --print-prereg")

    results = []
    for d in a.dirs:
        mp = os.path.join(d, "hess_manifest.json")
        if not os.path.exists(mp):
            print(f"SKIP {d}: no hess_manifest.json", file=sys.stderr)
            continue
        man = json.load(open(mp, encoding="utf-8"))
        outs = {rec["job"]: parse_scf_out(os.path.join(d, rec["job"] + ".out"))
                for rec in man["jobs"]}
        res = score_state(man, outs)
        res["dir"] = d
        report(res, man)
        results.append(res)

    if results:
        print(f"\n{'=' * 78}\nCAMPAIGN DECISION (docs/43 §3 + §3-A.1)\n{'=' * 78}")
        print(campaign_verdict(results))
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(dict(prereg="docs/43-prereg-week1-factorial.md §3 + §3-A",
                           results=results), fh, indent=2, default=float)
        print(f"\nwrote {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
