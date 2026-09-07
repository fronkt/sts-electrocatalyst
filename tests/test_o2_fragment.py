"""CENSUS-1b *O2 fragment module: site selection on a synthetic row and on one real CENSUS-1
result (read-only), transferred-H identification, FixAtoms re-indexing, the record schema
through site_census_readout.load_o2_records, the CLI gate and refusals, checkpoint/resume,
per-site failure records, the lock and the retrying atomic write, and a dry run that imports
neither torch nor mace. Relaxations use a harmonic fake calculator; no model is loaded."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sys
import weakref

import numpy as np
import pytest
from ase import Atoms
from ase.calculators.calculator import Calculator, all_changes
from ase.constraints import FixAtoms

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from hea_oer import o2_fragment as fragment  # noqa: E402
from hea_oer import site_integrity as integrity  # noqa: E402
from scripts import site_census_o2_fragment as cli  # noqa: E402
from scripts import site_census_readout as readout  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REAL_RESULTS = ROOT / "results/site_census_2026-09-06/results"
REAL_FORMULA = "Ni31Cr29Cu5Mn35"
FORMULA = "Fe25Co25Ni25Cr25"  # a box formula, so the CLI accepts the synthetic result under it
FORMULA_2 = "Ni31Cr29Cu5Mn35"
LINE = "CENSUS-1b 2026-09-07: synthetic test line of tests/test_o2_fragment.py"
K, SHIFT = 2.0, np.array([0.0, 0.0, 0.3])


# ---- fake calculator -------------------------------------------------------------------

class HarmonicToShiftedStart(Calculator):
    """E = 1/2 k sum |r_i - (r_i(start) + shift)|^2 per relaxation; the start is captured on
    the first call for each Atoms object (hea_oer.relax.relax works on one copy). Free atoms
    relax onto the shifted start; fixed atoms cannot, so the converged energy is
    1/2 k |shift|^2 x n_fixed, which is what makes the FixAtoms restoration checkable.
    `stuck_sizes` names atom counts that cannot converge within the step cap: their target
    sits 1000 A away on a 1e-3 eV/A^2 spring, a 1 eV/A force that BFGS's 0.2 A maxstep cannot
    walk down inside a few hundred steps; `fail_sizes` names atom counts whose energy is NaN
    (a failing relaxation)."""
    implemented_properties = ["energy", "forces"]

    def __init__(self, k=K, shift=SHIFT, stuck_sizes=(), fail_sizes=()):
        super().__init__()
        self.k, self.shift = float(k), np.asarray(shift, dtype=float)
        self.stuck_sizes, self.fail_sizes = set(stuck_sizes), set(fail_sizes)
        self._ref, self._targets, self._k, self.n_calls, self.n_relaxations = None, None, None, 0, 0

    def calculate(self, atoms=None, properties=("energy",), system_changes=all_changes):
        super().calculate(atoms, list(properties), system_changes)
        if self._ref is None or self._ref() is not atoms:
            self._ref = weakref.ref(atoms)
            stuck = len(atoms) in self.stuck_sizes
            self._targets = atoms.positions + (np.array([1000.0, 0.0, 0.0]) if stuck else self.shift)
            self._k = 1e-3 if stuck else self.k
            self.n_relaxations += 1
        d = atoms.positions - self._targets
        energy, forces = 0.5 * self._k * float((d * d).sum()), -self._k * d
        if len(atoms) in self.fail_sizes:
            energy = float("nan")
        self.results = dict(energy=energy, forces=forces)
        self.n_calls += 1


# ---- synthetic row ---------------------------------------------------------------------

CELL = [[6.0, 0.0, 0.0], [0.0, 6.0, 0.0], [0.0, 0.0, 20.0]]
SLAB_SYMBOLS = ["Cr", "Ni", "Cr", "Ni", "O", "O", "O", "O"]
SLAB_POSITIONS = [[0, 0, 0], [3, 0, 0], [0, 3, 0], [3, 3, 0],
                  [1.5, 0, 1.2], [1.5, 3, 1.2], [0, 1.5, 1.2], [3, 1.5, 1.2]]
FIXED = [0, 1, 2, 3]
METAL_XY = {0: (0.0, 0.0), 1: (3.0, 0.0), 2: (0.0, 3.0), 3: (3.0, 3.0)}


def record(symbols, positions, energy, converged=True, fixed=FIXED):
    return dict(symbols=list(symbols), positions_A=[list(map(float, p)) for p in positions], cell_A=CELL,
                pbc=[True, True, True], fixed_atom_indices=list(fixed), other_constraint_types=[],
                fmax_target_eV_A=0.05, max_constrained_force_eV_A=0.01 if converged else 0.2,
                converged_by_force=converged, force_readout="cached", energy_eV=float(energy))


def state(extra_symbols, extra_positions, energy, converged=True):
    return record(SLAB_SYMBOLS + extra_symbols, SLAB_POSITIONS + extra_positions, energy, converged)


def site(seed, index, metal, ooh_symbols, ooh_positions, ooh_converged=True, eta=0.5):
    x, y = METAL_XY[metal]
    e = dict(slab=-100.0, H2O=-14.0, H2=-6.5, OH=-108.0, O=-104.0, OOH=-115.0)
    return dict(
        seed=seed, site_index=index, site_xy_A=[x, y], dG_OH=1.0, dG_O=2.0, dG_OOH=3.5, eta=eta, pls=2,
        bonds={}, energies_eV=e, initial_binding_metal_index=metal,
        initial_binding_metal=SLAB_SYMBOLS[metal],
        relaxed_states=dict(
            OH=state(["O", "H"], [[x, y, 1.9], [x + 0.7, y, 2.6]], e["OH"]),
            O=state(["O"], [[x, y, 1.9]], e["O"]),
            OOH=state(ooh_symbols, ooh_positions, e["OOH"], ooh_converged)),
        start_records={}, desorbed=[])


def synthetic_row(formula=FORMULA):
    """Five sites: A qualifies (H transferred to slab O6, fragment weak on Cr0); B cus (H on the
    terminal O); C desorbed with H transferred; D H free; E bound but O-O cleaved."""
    ooh = ["O", "O", "H"]
    sites = [
        site(0, 0, 0, ooh, [[0, 0, 2.6], [1.23, 0, 2.6], [0, 1.5, 2.17]]),                     # A
        site(0, 1, 1, ooh, [[3, 0, 2.0], [3, 0, 3.4], [3, 0.9, 3.75]]),                        # B
        site(1, 0, 2, ooh, [[0, 3, 3.6], [1.23, 3, 3.6], [1.5, 3.97, 1.2]]),                   # C
        site(1, 1, 0, ooh, [[0, 0, 2.6], [1.23, 0, 2.6], [4.5, 4.5, 6.0]], ooh_converged=False),  # D
        site(2, 0, 3, ooh, [[3, 3, 2.0], [3, 4.8, 2.0], [3, 1.5, 2.17]]),                      # E
    ]
    decorations = [dict(seed=s, n_cations=4, cation_counts={"Cr": 2, "Ni": 2},
                        cation_fractions={"Cr": 0.5, "Ni": 0.5}, energy_eV=-100.0,
                        relaxed_slab=record(SLAB_SYMBOLS, SLAB_POSITIONS, -100.0))
                   for s in (0, 1, 2)]
    return dict(formula=formula, per_site_records=sites, decoration_records=decorations,
                gas_reference_records={}, n_sites=5, eta=0.5)


def synthetic_result(model_bytes, formula=FORMULA):
    row = synthetic_row(formula)
    manifest = dict(schema="screen-diagnostic-v1", manifest_id="synthetic-manifest-" + formula,
                    model=dict(historical_label="medium-mpa-0", filename="model.bin",
                               sha256_bytes=hashlib.sha256(model_bytes).hexdigest()),
                    protocol=dict(fmax_eV_A=0.05, steps=300, dtype="float64", seeds=[0, 1, 2], n_sites=4))
    return dict(schema="screen-diagnostic-v1", manifest_id="synthetic-manifest-" + formula, manifest=manifest,
                status="complete", environment={}, results=[dict(candidate_id="x", formula=formula,
                                                                  status="evaluated", row=row, seconds=1.0)])


@pytest.fixture
def census(tmp_path):
    model = tmp_path / "model.bin"
    model.write_bytes(b"not a checkpoint")
    results = tmp_path / "results"
    results.mkdir()
    for formula in (FORMULA, FORMULA_2):
        (results / f"mpa0__{formula}_result.json").write_text(
            json.dumps(synthetic_result(model.read_bytes(), formula)), encoding="utf-8")
    source = tmp_path / "dated_lines.md"
    source.write_text("a file standing in for the dated-line source\n\n> " + LINE + "\n", encoding="utf-8")
    return dict(model=model, results=results, out=tmp_path / "o2" / "o2_records.json",
                manifests=tmp_path / "manifests",  # absent: cross-check skipped
                source=source)


def cli_args(census, *extra, formulas=(FORMULA,)):
    args = ["--results-dir", str(census["results"]), "--manifest-dir", str(census["manifests"]),
            "--out", str(census["out"]), "--model-file", str(census["model"]),
            "--dated-line-source", str(census["source"])]
    for formula in formulas:
        args += ["--formula", formula]
    return args + list(extra)


def counting_factory(calls, **calc_kwargs):
    def factory():
        calc = HarmonicToShiftedStart(**calc_kwargs)
        calls.append(calc)
        return calc
    return factory


# ---- selection ---------------------------------------------------------------------------

def test_select_sites_synthetic_row_qualifies_only_the_bridge_site():
    selection = fragment.select_sites(synthetic_row())
    by_key = {s["key"]: s for s in selection}
    assert fragment.qualifying_keys(selection) == [(0, 0)]
    a = by_key["0/0"]
    assert a["qualifies"] and a["reason"] is None and a["reason_class"] is None
    assert a["ooh"]["h_location"] == "H_TRANSFERRED" and a["ooh"]["bond_tier"] == "weak"
    assert a["ooh"]["pathway_state"] == "*O2+H_b" and a["pathway"] == "bridge"
    assert by_key["0/1"]["reason_class"] == "ON_ADSORBATE" and "cus pathway" in by_key["0/1"]["reason"]
    assert by_key["1/0"]["reason_class"] == "DESORBED" and "3.6" in by_key["1/0"]["reason"]
    assert by_key["1/1"]["reason_class"] == "H_FREE"
    assert by_key["2/0"]["reason_class"] == "OO_CLEAVED" and by_key["2/0"]["ooh"]["bond_tier"] == "bound"
    # the classified row is accepted as input too, with the same answer
    classified = integrity.classify_row(synthetic_row())
    assert fragment.select_sites(classified) == selection


def test_select_sites_on_a_real_census1_result_matches_the_dry_run(capsys):
    path = REAL_RESULTS / f"mpa0__{REAL_FORMULA}_result.json"
    if not path.exists():
        pytest.skip("CENSUS-1 result absent: " + str(path))
    row = json.loads(path.read_text(encoding="utf-8"))["results"][0]["row"]
    selection = fragment.select_sites(row)
    keys = fragment.qualifying_keys(selection)
    assert len(selection) == 12
    for s in selection:
        if s["qualifies"]:
            assert s["ooh"]["h_location"] == "H_TRANSFERRED" and s["ooh"]["bond_tier"] in ("bound", "weak")
            assert s["ooh"]["o_o_class"] != "OO_CLEAVED"
    # the docs/91:36 wording (H-TRANSFERRED, bound or weak) and the pathway_state agree on this row
    literal = [(s["seed"], s["site_index"]) for s in selection
               if s["ooh"] and s["ooh"]["h_location"] == "H_TRANSFERRED" and s["ooh"]["bond_tier"] != "desorbed"]
    assert literal == keys
    before = set(sys.modules)
    code = cli.main(["--dry-run", "--results-dir", str(REAL_RESULTS), "--formula", REAL_FORMULA,
                     "--manifest-dir", str(ROOT / "results/site_census_2026-09-06/manifests")])
    assert code == 0
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert summary["dry_run"] is True
    assert summary["per_formula"][REAL_FORMULA]["n_qualifying"] == len(keys)
    assert summary["per_formula"][REAL_FORMULA]["keys"] == [fragment.site_key(*k) for k in keys]
    assert summary["qualifying_total"] == len(keys)
    assert "mace" not in sys.modules
    assert not ({"torch", "mace"} & (set(sys.modules) - before))


# ---- geometry construction ---------------------------------------------------------------

def test_identify_transferred_h_and_its_refusals():
    row = synthetic_row()
    a = row["per_site_records"][0]["relaxed_states"]["OOH"]
    info = fragment.identify_transferred_h(a)
    assert info["h_index"] == len(a["symbols"]) - 1 and info["n_slab_atoms"] == 8
    assert info["slab_O_index"] == 6 and math.isclose(info["h_to_slab_O_A"], 0.97, abs_tol=1e-12)
    assert min(info["h_to_fragment_O_A"].values()) > 1.15
    b = row["per_site_records"][1]["relaxed_states"]["OOH"]  # H on the terminal O
    with pytest.raises(ValueError, match="adsorbate O"):
        fragment.identify_transferred_h(b)
    d = row["per_site_records"][3]["relaxed_states"]["OOH"]  # H free
    with pytest.raises(ValueError, match="outside"):
        fragment.identify_transferred_h(d)
    two_h = dict(a, symbols=a["symbols"][:-3] + ["O", "O", "H"], positions_A=a["positions_A"])
    two_h["symbols"][4] = "H"
    with pytest.raises(ValueError, match="exactly one H"):
        fragment.identify_transferred_h(two_h)


def test_identify_transferred_h_across_the_cell_boundary():
    a = synthetic_row()["per_site_records"][0]["relaxed_states"]["OOH"]
    positions = [list(p) for p in a["positions_A"]]
    positions[6] = [0.1, 1.5, 1.2]      # slab O6 near x = 0
    positions[-1] = [5.9, 1.5, 1.6]     # H across the boundary: 0.2 A in x through the wrap, 0.4 A in z
    wrapped = dict(a, positions_A=positions)
    info = fragment.identify_transferred_h(wrapped)
    assert info["slab_O_index"] == 6 and math.isclose(info["h_to_slab_O_A"], math.hypot(0.2, 0.4), abs_tol=1e-12)


def test_fixed_index_shift_matches_ase_and_refuses_a_fixed_atom():
    assert fragment.shift_fixed_indices([0, 5, 9], 3) == [0, 4, 8]
    assert fragment.shift_fixed_indices([0, 1, 2], 7) == [0, 1, 2]
    atoms = Atoms("H10", positions=np.random.default_rng(0).random((10, 3)) * 5, cell=[6, 6, 6], pbc=True)
    atoms.set_constraint(FixAtoms(indices=[0, 5, 9]))
    del atoms[3]
    assert sorted(atoms.constraints[0].get_indices().tolist()) == fragment.shift_fixed_indices([0, 5, 9], 3)
    with pytest.raises(ValueError, match="fixed atom"):
        fragment.shift_fixed_indices([0, 3], 3)


def test_build_fragment_atoms_restores_cell_pbc_and_constraints():
    a = synthetic_row()["per_site_records"][0]["relaxed_states"]["OOH"]
    atoms, info = fragment.build_fragment_atoms(a)
    assert len(atoms) == len(a["symbols"]) - 1 and "H" not in atoms.get_chemical_symbols()
    assert np.allclose(atoms.cell.array, CELL) and all(atoms.pbc)
    assert sorted(atoms.constraints[0].get_indices().tolist()) == FIXED
    assert info["fixed_atom_indices_after"] == FIXED and info["fragment_O_indices"] == [8, 9]
    assert np.allclose(atoms.positions[:8], SLAB_POSITIONS)
    assert np.allclose(atoms.positions[8:], [[0, 0, 2.6], [1.23, 0, 2.6]])


def test_build_o2_atoms_is_centred_in_the_given_cell_and_refuses_a_short_one():
    o2 = fragment.build_o2_atoms(CELL)
    assert np.allclose(o2.cell.array, CELL) and all(o2.pbc) and len(o2) == 2
    assert np.allclose(o2.positions.mean(axis=0), [3.0, 3.0, 10.0])
    assert math.isclose(o2.get_distance(0, 1, mic=True), 1.245956, abs_tol=1e-6)
    box = fragment.build_o2_atoms(fragment.box12_cell())
    assert np.allclose(box.cell.lengths(), 12.0)
    with pytest.raises(ValueError, match="cannot hold"):
        fragment.build_o2_atoms([[6, 0, 0], [0, 6, 0], [0, 0, 1.0]])   # minimum-image O-O would be 0.246 A
    with pytest.raises(ValueError, match="cannot hold"):
        fragment.build_o2_atoms([[6, 0, 0], [0, 6, 0], [0, 0, 2.4]])   # holds the bond but not twice it


def test_force_readout_follows_the_sealed_derivation_on_fixed_atoms():
    """FixAtoms.adjust_forces zeroes fixed-atom forces before the finiteness check, as
    adsorption.py:100-119 does; a nonfinite force on a FREE atom is 'nonfinite'."""

    class Fixed(Calculator):
        implemented_properties = ["energy", "forces"]

        def __init__(self, forces):
            super().__init__()
            self.forces = np.asarray(forces, dtype=float)

        def calculate(self, atoms=None, properties=("energy",), system_changes=all_changes):
            super().calculate(atoms, list(properties), system_changes)
            self.results = dict(energy=0.0, forces=self.forces.copy())

    atoms = Atoms("H4", positions=[[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]], cell=[6, 6, 6], pbc=True)
    atoms.set_constraint(FixAtoms(indices=[0, 1]))
    atoms.calc = Fixed([[np.nan, 0, 0], [9, 0, 0], [0.01, 0, 0], [0, 0.02, 0]])
    atoms.get_forces()
    out = fragment.force_readout(atoms, 0.05)
    assert out == dict(fmax_target_eV_A=0.05, max_constrained_force_eV_A=0.02, converged_by_force=True,
                       force_readout="cached")
    atoms.calc = Fixed([[0, 0, 0], [0, 0, 0], [np.nan, 0, 0], [0, 0.02, 0]])
    atoms.get_forces()
    assert fragment.force_readout(atoms, 0.05)["force_readout"] == "nonfinite"
    assert fragment.force_readout(atoms, 0.05)["converged_by_force"] is False


# ---- relaxation with the fake calculator -----------------------------------------------------

def test_run_row_records_energies_geometry_and_the_readout_schema():
    row = synthetic_row()
    calc = HarmonicToShiftedStart()
    result = fragment.run_row(row, calc, fmax=0.05, steps=300)
    records, audit = result["records"], result["audit"]
    assert list(records) == ["0/0"] and audit["n_qualifying"] == 1 and audit["n_sites"] == 5
    assert audit["n_failed"] == 0 and audit["failed_keys"] == []
    rec = records["0/0"]
    assert set(fragment.READOUT_KEYS) <= set(rec)
    assert rec["converged_by_force"] is True and rec["o2_cell"] == "slab"
    assert rec["fragment_converged_by_force"] is True and rec["o2_gas_converged_by_force"] is True
    assert rec["E_O2_gas_eV"] == rec["E_O2_slab_cell_eV"] and rec["o2_cell_id"] == fragment.cell_id(CELL)
    # fixed atoms stayed put and carry 1/2 k |shift|^2 each; free atoms reached the shifted start
    frag = audit["fragments"]["0/0"]
    assert frag["status"] == "relaxed"
    expected = 0.5 * K * float(SHIFT @ SHIFT) * len(FIXED)
    n_free = len(frag["symbols"]) - len(FIXED)
    assert abs(rec["energy_eV"] - expected) < n_free * 0.5 * K * (0.05 / K) ** 2 + 1e-9
    assert frag["energy_eV"] == rec["energy_eV"] and frag["fixed_atom_indices"] == FIXED
    positions = np.asarray(frag["positions_A"])
    assert np.allclose(positions[FIXED], np.asarray(SLAB_POSITIONS)[FIXED])
    assert np.allclose(positions[4:], np.asarray(frag["start"]["positions_A"])[4:] + SHIFT, atol=0.03)
    assert frag["force_readout"] == "cached" and frag["max_constrained_force_eV_A"] < 0.05
    geo = frag["geometry"]
    assert math.isclose(geo["o_o_A"], 1.23, abs_tol=0.03) and geo["o_o_class"] == "O2_LIKE"
    assert geo["binding_O"] == "proximal_O" and geo["binding_metal"] == "Cr"
    assert math.isclose(geo["min_m_o_A"], 2.9, abs_tol=0.03) and geo["bond_tier"] == "weak"
    assert geo["slab_displacement_from_clean"]["fixed_atom_max_A"] == 0.0
    assert geo["reconstruction_flag_from_clean"] is False  # 0.3 A free-atom shift, below the 0.5 A bar
    # O2: no constraint, so it relaxes onto the shifted start with energy ~0, O-O preserved
    slab_o2 = audit["o2_gas"]["slab_cell"][fragment.cell_id(CELL)]
    box_o2 = audit["o2_gas"]["box12"]
    for o2 in (slab_o2, box_o2):
        assert o2["converged_by_force"] is True and abs(o2["energy_eV"]) < 2 * 0.5 * K * (0.05 / K) ** 2
        assert math.isclose(o2["o_o_A"], o2["o_o_start_A"], abs_tol=1e-6) and o2["fixed_atom_indices"] == []
    assert box_o2["cell_lengths_A"] == [12.0, 12.0, 12.0] and slab_o2["label"] == "slab_cell"
    assert rec["E_O2_box12_eV"] == box_o2["energy_eV"]
    assert calc.n_relaxations == 3  # slab-cell O2, box12 O2, one fragment
    # the diagnostic the readout will compute from this record, and the audit's 0.00/0.05/0.10 box
    site0 = row["per_site_records"][0]
    diag = integrity.o2_fragment_diagnostic(rec, site0["energies_eV"], site0["dG_OOH"])
    assert diag["status"] == "computed"
    assert math.isclose(diag["dG_ads_O2_eV"], rec["energy_eV"] - (-100.0) - rec["E_O2_gas_eV"] + 0.05, abs_tol=1e-12)
    no_zpe = frag["E_frag_minus_slab_minus_O2_no_zpe_eV"]
    assert math.isclose(no_zpe["slab_cell"], rec["energy_eV"] + 100.0 - rec["E_O2_slab_cell_eV"], abs_tol=1e-12)
    box = frag["dG_ads_O2_by_zpe_ts_eV"]
    assert set(box["slab_cell"]) == {"0.00", "0.05", "0.10"}
    assert math.isclose(box["slab_cell"]["0.05"], diag["dG_ads_O2_eV"], abs_tol=1e-12)
    assert math.isclose(box["slab_cell"]["0.10"] - box["slab_cell"]["0.00"], 0.10, abs_tol=1e-12)
    assert math.isclose(box["box12"]["0.00"], no_zpe["box12"], abs_tol=1e-12)


def test_run_row_box12_choice_swaps_the_gas_energy_and_shares_the_o2_cache():
    row = synthetic_row()
    calc = HarmonicToShiftedStart()
    cache = {}
    first = fragment.run_row(row, calc, o2_cell="box12", o2_cache=cache)
    rec = first["records"]["0/0"]
    assert rec["E_O2_gas_eV"] == rec["E_O2_box12_eV"] and rec["o2_cell_id"] == fragment.cell_id(fragment.box12_cell())
    n = calc.n_relaxations
    fragment.run_row(row, calc, o2_cell="box12", o2_cache=cache)
    assert calc.n_relaxations == n + 1  # only the fragment again; both O2 cells came from the cache
    with pytest.raises(ValueError):
        fragment.run_row(row, calc, o2_cell="vacuum")
    # the cache rebuilt from the audit is the cache
    rebuilt = fragment.o2_cache_from_audits([first["audit"]])
    assert set(rebuilt) == set(cache) and all(rebuilt[c]["energy_eV"] == cache[c]["energy_eV"] for c in cache)


def test_unconverged_o2_gas_marks_the_readout_record_unconverged():
    """An O2 relaxation that hits the step cap must not feed a record the readout reports as
    computed: converged_by_force covers the fragment AND the O2 that feeds E_O2_gas_eV."""
    row = synthetic_row()
    calc = HarmonicToShiftedStart(stuck_sizes={2})  # the 2-atom O2 cannot converge in 30 steps
    result = fragment.run_row(row, calc, fmax=0.05, steps=30)
    rec = result["records"]["0/0"]
    audit = result["audit"]
    assert audit["o2_gas"]["box12"]["converged_by_force"] is False
    assert audit["o2_gas"]["slab_cell"][fragment.cell_id(CELL)]["converged_by_force"] is False
    assert rec["fragment_converged_by_force"] is True and rec["o2_gas_converged_by_force"] is False
    assert rec["converged_by_force"] is False
    assert audit["fragments"]["0/0"]["o2_gas_converged_by_force"] == {"slab_cell": False, "box12": False}
    site0 = row["per_site_records"][0]
    assert integrity.o2_fragment_diagnostic(rec, site0["energies_eV"], site0["dG_OOH"])["status"] == "unconverged_O2_record"


def test_failing_fragment_relaxation_is_recorded_per_site_and_the_composition_continues():
    row = synthetic_row()
    calc = HarmonicToShiftedStart(fail_sizes={10})  # the 10-atom H-removed fragment; O2 (2 atoms) is fine
    result = fragment.run_row(row, calc)
    assert result["records"] == {}
    audit = result["audit"]
    assert audit["n_qualifying"] == 1 and audit["n_failed"] == 1 and audit["failed_keys"] == ["0/0"]
    failed = audit["fragments"]["0/0"]
    assert failed["status"] == "failed" and "nonfinite fragment energy" in failed["error"]
    assert failed["seed"] == 0 and failed["site_index"] == 0 and "energy_eV" not in failed
    assert audit["o2_gas"]["box12"]["converged_by_force"] is True  # the O2 relaxations were kept


# ---- CLI ---------------------------------------------------------------------------------

def test_cli_end_to_end_roundtrips_through_load_o2_records(census, capsys):
    calcs = []
    factory = counting_factory(calcs)
    code = cli.main(cli_args(census, "--dated-line", LINE), calculator_factory=factory)
    assert code == 0 and len(calcs) == 1
    out, audit_path = census["out"], census["out"].with_name(cli.AUDIT_NAME)
    assert out.exists() and audit_path.exists() and not out.with_name(out.name + ".lock").exists()
    assert not out.with_name(out.name + ".pending").exists()
    loaded = readout.load_o2_records(out)
    assert list(loaded) == [FORMULA] and list(loaded[FORMULA]) == [(0, 0)]
    rec = loaded[FORMULA][(0, 0)]
    assert set(fragment.READOUT_KEYS) <= set(rec) and rec["converged_by_force"] is True
    raw = json.loads(out.read_text(encoding="utf-8"))
    assert set(raw) == {FORMULA}  # nothing but formulas at the top level
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    header = audit["header"]
    assert header["dated_line"] == LINE and header["status"] == "complete"
    assert header["dated_line_check"] == dict(source=str(census["source"].resolve()), found=True, date="2026-09-07")
    assert header["model"]["sha256_bytes"] == hashlib.sha256(b"not a checkpoint").hexdigest()
    assert header["inputs"][FORMULA]["sha256_lf"] == readout.sha256_lf(census["results"] / f"mpa0__{FORMULA}_result.json")
    assert header["protocol"][FORMULA] == dict(fmax_eV_A=0.05, steps=300, dtype="float64")
    assert set(header["implementation_sha256_lf"]) == set(cli.IMPLEMENTATION)
    assert "src/scripts/site_census_plan.py" in header["implementation_sha256_lf"]
    assert "CALIBRATION" in header["role"] and header["environment"]["threads"] == 2
    assert header["environment"]["torchinductor_cache_dir"] == os.environ["TORCHINDUCTOR_CACHE_DIR"]
    assert "reading of docs/91:36" in header["o2_cell_note"] and header["o2_cell"] == "slab"
    assert len(header["runs"]) == 1 and header["runs"][0]["compositions"] == [FORMULA]
    assert header["wall_seconds"] == header["runs"][0]["wall_seconds"]
    comp = audit["compositions"][FORMULA]
    assert comp["records"] == raw[FORMULA] and comp["n_qualifying"] == 1 and comp["n_failed"] == 0
    assert {s["key"] for s in comp["selection"]} == {"0/0", "0/1", "1/0", "1/1", "2/0"}
    site0 = synthetic_row()["per_site_records"][0]
    assert integrity.o2_fragment_diagnostic(rec, site0["energies_eV"], site0["dG_OOH"])["status"] == "computed"
    # no overwrite: a second run is refused and the files are untouched
    before = (out.read_bytes(), audit_path.read_bytes())
    with pytest.raises(SystemExit, match="no overwrite"):
        cli.main(cli_args(census, "--dated-line", LINE), calculator_factory=factory)
    assert (out.read_bytes(), audit_path.read_bytes()) == before and len(calcs) == 1
    # resume with a different dated line is refused; with the same line it finds nothing left to do
    other = LINE.replace("2026-09-07", "2026-09-08")
    census["source"].write_text(census["source"].read_text(encoding="utf-8") + "> " + other + "\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="dated_line differs"):
        cli.main(cli_args(census, "--dated-line", other, "--resume"), calculator_factory=factory)
    assert cli.main(cli_args(census, "--dated-line", LINE, "--resume"), calculator_factory=factory) == 0
    assert len(calcs) == 1 and (out.read_bytes(), audit_path.read_bytes()) == before
    assert "nothing left to do" in capsys.readouterr().out


def test_cli_resume_with_work_remaining_reuses_the_checkpointed_o2_energies(census, capsys):
    calcs = []
    factory = counting_factory(calcs)
    assert cli.main(cli_args(census, "--dated-line", LINE), calculator_factory=factory) == 0
    assert calcs[0].n_relaxations == 3  # slab-cell O2, box12 O2, one fragment
    audit_path = census["out"].with_name(cli.AUDIT_NAME)
    code = cli.main(cli_args(census, "--dated-line", LINE, "--resume", formulas=(FORMULA, FORMULA_2)),
                    calculator_factory=factory)
    assert code == 0 and len(calcs) == 2
    # the second composition shares the synthetic cell, so both O2 cells came from the checkpoint
    assert calcs[1].n_relaxations == 1
    raw = readout.load_o2_records(census["out"])
    assert set(raw) == {FORMULA, FORMULA_2}
    a, b = raw[FORMULA][(0, 0)], raw[FORMULA_2][(0, 0)]
    assert a["E_O2_gas_eV"] == b["E_O2_gas_eV"] and a["E_O2_box12_eV"] == b["E_O2_box12_eV"]
    assert a["o2_cell_id"] == b["o2_cell_id"]
    header = json.loads(audit_path.read_text(encoding="utf-8"))["header"]
    assert header["status"] == "complete" and len(header["runs"]) == 2 and len(header["resumed"]) == 1
    assert header["runs"][1]["compositions"] == [FORMULA_2]
    assert set(header["runs"][1]["o2_cells_from_checkpoint"]) == {fragment.cell_id(CELL),
                                                                    fragment.cell_id(fragment.box12_cell())}
    assert math.isclose(header["wall_seconds"], sum(r["wall_seconds"] for r in header["runs"]), abs_tol=1e-9)
    capsys.readouterr()


def test_cli_records_a_failure_in_the_audit_header_instead_of_leaving_it_running(census, capsys):
    def broken_factory():
        raise RuntimeError("model load failed")

    with pytest.raises(SystemExit, match="failed: RuntimeError: model load failed"):
        cli.main(cli_args(census, "--dated-line", LINE), calculator_factory=broken_factory)
    audit_path = census["out"].with_name(cli.AUDIT_NAME)
    header = json.loads(audit_path.read_text(encoding="utf-8"))["header"]
    assert header["status"] == "failed" and header["failure"]["error"] == "RuntimeError: model load failed"
    assert header["failure"]["formula"] is None  # the model load precedes every composition
    assert header["runs"][0]["wall_seconds"] is not None
    assert not census["out"].with_name(census["out"].name + ".lock").exists()
    with pytest.raises(SystemExit, match="no overwrite"):
        cli.main(cli_args(census, "--dated-line", LINE), calculator_factory=broken_factory)
    # a failure inside a composition (here the O2 relaxation) names the composition
    with pytest.raises(SystemExit, match="nonfinite O2 energy"):
        cli.main(cli_args(census, "--dated-line", LINE, "--resume"),
                 calculator_factory=counting_factory([], fail_sizes={2}))
    header = json.loads(audit_path.read_text(encoding="utf-8"))["header"]
    assert header["status"] == "failed" and header["failure"]["formula"] == FORMULA
    assert header["failure"]["error"] == "ValueError: nonfinite O2 energy" and len(header["runs"]) == 2
    # a per-site failure does not fail the run: the site is recorded and the audit completes
    calcs = []
    code = cli.main(cli_args(census, "--dated-line", LINE, "--resume"),
                    calculator_factory=counting_factory(calcs, fail_sizes={10}))
    assert code == 0
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["header"]["status"] == "complete"
    assert audit["compositions"][FORMULA]["n_failed"] == 1 and audit["compositions"][FORMULA]["records"] == {}
    assert readout.load_o2_records(census["out"]) == {FORMULA: {}}
    last = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert last["failed_sites"] == 1 and last["records"] == 0


def test_cli_gate_needs_a_dated_line_present_in_the_source(census):
    def factory():
        raise AssertionError("no relaxation may start")

    for args, match in [
        (cli_args(census), "dated-line"),
        (cli_args(census, "--dated-line", "   "), "dated-line"),
        (cli_args(census, "--dated-line", "x"), "dated form"),
        (cli_args(census, "--dated-line", "CENSUS-1b 2026-09-__: a blank slot"), "dated form"),
        (cli_args(census, "--dated-line", "CENSUS-1b 2026-13-40: not a date"), "calendar date"),
        (cli_args(census, "--dated-line", "CENSUS-1b 2026-09-07: a line the source does not carry"), "not present verbatim"),
        (cli_args(census, "--dated-line", LINE, "--dated-line-source", str(census["source"].with_name("absent.md"))),
         "does not exist"),
    ]:
        with pytest.raises(SystemExit, match=match):
            cli.main(args, calculator_factory=factory)
    assert not census["out"].exists() and not census["out"].parent.exists()
    other = census["model"].with_name("other.bin")
    other.write_bytes(b"different bytes")
    with pytest.raises(SystemExit, match="model bytes"):
        cli.main(cli_args(census, "--dated-line", LINE, "--model-file", str(other)), calculator_factory=factory)
    assert not census["out"].exists()
    with pytest.raises(SystemExit, match="outside the CENSUS-1 box"):
        cli.main(cli_args(census, "--dry-run", "--formula", "Fe50Ni50"))
    # the source file is read, never written
    assert "a file standing in" in census["source"].read_text(encoding="utf-8")


def test_cli_refuses_an_out_inside_the_runner_and_readout_directories(tmp_path):
    census_dir = tmp_path / "census"
    for sub in ("results", "manifests", "logs", "readout", "torch-cache"):
        with pytest.raises(SystemExit, match="inside the census tree"):
            cli.check_out_path((census_dir / sub / "o2_records.json").resolve(), census_dir)
    with pytest.raises(SystemExit, match="inside the census tree"):
        cli.check_out_path((census_dir / "o2_records.json").resolve(), census_dir)  # beside status.json
    cli.check_out_path((census_dir / cli.OUT_SUBDIR / "o2_records.json").resolve(), census_dir)
    cli.check_out_path((census_dir / cli.OUT_SUBDIR / "run2" / "o2_records.json").resolve(), census_dir)
    cli.check_out_path((tmp_path / "elsewhere" / "o2_records.json").resolve(), census_dir)
    assert cli.DEFAULT_OUT.parent.name == cli.OUT_SUBDIR


def test_cli_lock_handling_stale_pending_and_the_replace_retry(census, monkeypatch, capsys):
    out = census["out"]
    out.parent.mkdir(parents=True)
    lock = out.with_name(out.name + ".lock")
    # a lock held by a live pid is refused
    lock.write_text(str(os.getpid()), encoding="utf-8")
    with pytest.raises(SystemExit, match="held by live pid"):
        cli.main(cli_args(census, "--dated-line", LINE), calculator_factory=lambda: pytest.fail("no relaxation"))
    assert lock.exists()
    # a lock whose content is not a pid is refused, not removed
    lock.write_text("not a pid", encoding="utf-8")
    with pytest.raises(SystemExit, match="carries no pid"):
        cli.main(cli_args(census, "--dated-line", LINE), calculator_factory=lambda: pytest.fail("no relaxation"))
    assert lock.exists()
    # a stale lock (dead pid) and a stale .pending from a crash are cleared and the run proceeds
    lock.write_text("999999999", encoding="utf-8")
    assert not cli.pid_alive(999999999) and cli.pid_alive(os.getpid()) and not cli.pid_alive("x")
    audit_path = out.with_name(cli.AUDIT_NAME)
    audit_path.with_name(audit_path.name + ".pending").write_text("{}", encoding="utf-8")
    calcs = []
    assert cli.main(cli_args(census, "--dated-line", LINE), calculator_factory=counting_factory(calcs)) == 0
    assert not lock.exists() and not audit_path.with_name(audit_path.name + ".pending").exists()
    assert "stale lock removed" in capsys.readouterr().out
    # os.replace is retried through a transient PermissionError, and gives up after `attempts`
    calls = []
    real_replace = os.replace

    def flaky(src, dst):
        calls.append(1)
        if len(calls) < 3:
            raise PermissionError(5, "Access is denied")
        real_replace(src, dst)

    monkeypatch.setattr(cli.os, "replace", flaky)
    monkeypatch.setattr(cli, "REPLACE_DELAY_SECONDS", 0.0)
    target = out.parent / "probe.json"
    cli.atomic_write_json(target, {"a": 1})
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": 1} and len(calls) == 3
    calls.clear()
    monkeypatch.setattr(cli, "REPLACE_ATTEMPTS", 2)
    with pytest.raises(PermissionError):
        cli.atomic_write_json(target, {"a": 2})
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": 1}


def test_cli_dry_run_writes_nothing_and_loads_no_model(census, capsys):
    before = set(sys.modules)
    code = cli.main(cli_args(census, "--dry-run"), calculator_factory=lambda: pytest.fail("model loaded"))
    assert code == 0
    text = capsys.readouterr().out
    summary = json.loads(text.strip().splitlines()[-1])
    assert summary["per_formula"] == {FORMULA: dict(n_sites=5, n_qualifying=1, keys=["0/0"])}
    assert summary["planned_relaxations"] == 3 and summary["distinct_slab_cells"] == 1
    assert "ON_ADSORBATE 1" in text and "DESORBED 1" in text and "H_FREE 1" in text and "OO_CLEAVED 1" in text
    assert "reading of docs/91:36" in text and "read through readout (c)" in text
    assert not census["out"].parent.exists()
    assert "mace" not in sys.modules and not ({"torch", "mace"} & (set(sys.modules) - before))
