"""MACE-MPA-0 single points and constrained relaxations with the census protocol.

The checkpoint is loaded from explicit bytes whose sha256 must equal the value the census
manifest recorded (model.sha256_bytes), in float64 on CPU, through the same factory the
census used (mace.calculators.mace_mp; src/hea_oer/relax.py:make_mace_calculator). One
structure is evaluated at a time; arrays are copied out and the Atoms object dropped.
"""
from __future__ import annotations

import gc
from pathlib import Path

import numpy as np

from lt_common import sha256_file

DEFAULT_CHECKPOINT = Path.home() / ".cache" / "mace" / "macempa0mediummodel"


def load_calculator(checkpoint: Path, expected_sha256: str, threads: int = 2):
    checkpoint = Path(checkpoint)
    actual = sha256_file(checkpoint)
    if actual != expected_sha256:
        raise ValueError(f"checkpoint sha256 {actual} differs from the census record {expected_sha256}")
    import torch
    from mace.calculators import mace_mp

    torch.set_num_threads(int(threads))
    calc = mace_mp(model=str(checkpoint), device="cpu", default_dtype="float64")
    return calc


def _atoms(symbols, positions, cell, pbc=(True, True, True), fixed=()):
    from ase import Atoms
    from ase.constraints import FixAtoms

    atoms = Atoms(symbols=list(symbols), positions=np.asarray(positions, dtype=float),
                  cell=np.asarray(cell, dtype=float), pbc=list(pbc))
    if fixed:
        atoms.set_constraint(FixAtoms(indices=sorted(int(i) for i in fixed)))
    return atoms


def single_point(calc, symbols, positions, cell, pbc=(True, True, True)) -> dict:
    """Energy (eV) and unconstrained forces (eV/A) at exactly the given coordinates."""
    atoms = _atoms(symbols, positions, cell, pbc)
    atoms.calc = calc
    energy = float(atoms.get_potential_energy())
    forces = np.array(atoms.get_forces(apply_constraint=False), dtype=float, copy=True)
    atoms.calc = None
    del atoms
    gc.collect()
    return dict(energy_eV=energy, forces_eV_A=forces)


def relax(calc, symbols, positions, cell, fixed, fmax: float, steps: int, pbc=(True, True, True)) -> dict:
    """ASE BFGS with FixAtoms, as src/hea_oer/relax.py:relax (logfile None)."""
    from ase.optimize import BFGS

    atoms = _atoms(symbols, positions, cell, pbc, fixed)
    atoms.calc = calc
    opt = BFGS(atoms, logfile=None)
    converged = bool(opt.run(fmax=fmax, steps=steps))
    energy = float(atoms.get_potential_energy())
    constrained = np.array(atoms.get_forces(apply_constraint=True), dtype=float)
    out = dict(energy_eV=energy, positions_A=atoms.get_positions().tolist(),
               max_constrained_force_eV_A=float(np.max(np.linalg.norm(constrained, axis=1))),
               converged_by_force=bool(np.max(np.linalg.norm(constrained, axis=1)) <= fmax),
               optimizer_reported_converged=converged, steps_taken=int(opt.nsteps))
    atoms.calc = None
    del atoms, opt
    gc.collect()
    return out
