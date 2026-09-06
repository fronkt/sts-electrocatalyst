"""ASE relaxation helpers + the MLIP calculator factories (fairchem/UMA, MACE).

Only the calculator factories need a specific MLIP package; the relaxation driver is
calculator-agnostic so the geometry can be exercised with any ASE calculator.
"""
from __future__ import annotations


def make_mace_calculator(model: str = "medium-mpa-0", device: str = "cpu",
                         dtype: str = "float64"):
    """Build a MACE-MP ASE calculator. Ungated, CPU-capable, no HF token.

    ``medium-mpa-0`` is the checkpoint that cleared the R3 gate against the QC-gated
    DFT tier (rho = +0.857, exact p = 0.0238, eta MAE 0.172 V at n = 7; docs/35), and
    the one that independently reproduced all three structures the 2026-08-02 DFT
    repair campaign had to pay to fix. It is the default for that reason and should
    not be changed without re-running `mlip_eval`.

    float64 matters: the campaign's eta differences run to a few tens of meV and the
    R3 numbers were measured in double precision.
    """
    try:
        from mace.calculators import mace_mp
    except ImportError as e:  # pragma: no cover - only on a box without mace
        raise ImportError(
            "mace-torch is required for the MACE backend: `uv pip install mace-torch`"
        ) from e
    return mace_mp(model=model, device=device, default_dtype=dtype)


def make_calculator(model: str = "uma-s-1p1", task: str = "oc20", device: str = "cuda"):
    """Build a fairchem UMA ASE calculator. Requires `fairchem-core` + (gated) HF access.

    UMA is gated on Hugging Face — authenticate the box first, e.g.
    ``huggingface-cli login`` after accepting the license at hf.co/facebook/UMA.
    """
    try:
        from fairchem.core import FAIRChemCalculator, pretrained_mlip
    except ImportError as e:  # pragma: no cover - only on a box without fairchem
        raise ImportError(
            "fairchem-core is required for the UMA backend: `uv pip install fairchem-core`"
        ) from e
    predict_unit = pretrained_mlip.get_predict_unit(model, device=device)
    return FAIRChemCalculator(predict_unit, task_name=task)


def relax(atoms, calc, fmax: float = 0.05, steps: int = 300):
    """BFGS-relax a copy of `atoms` with `calc`; return (energy_eV, relaxed_atoms)."""
    from ase.optimize import BFGS

    atoms = atoms.copy()
    atoms.calc = calc
    BFGS(atoms, logfile=None).run(fmax=fmax, steps=steps)
    return float(atoms.get_potential_energy()), atoms


def gas_reference_energies(calc, fmax: float = 0.05, steps: int = 300, box: float = 12.0,
                           *, record_callback=None):
    """Return (E_H2O, E_H2); optionally retain each existing relaxation immediately.

    record_callback(name, energy_eV, atoms) sees current calculator metadata before
    the shared calculator moves to the next molecule. The callback requests no work.
    """
    from ase.build import molecule

    energies = {}
    for name in ("H2O", "H2"):
        m = molecule(name)
        m.set_cell([box, box, box])
        m.center()
        m.pbc = True
        energies[name], relaxed = relax(m, calc, fmax=fmax, steps=steps)
        if record_callback is not None:
            record_callback(name, energies[name], relaxed)
    return energies["H2O"], energies["H2"]
