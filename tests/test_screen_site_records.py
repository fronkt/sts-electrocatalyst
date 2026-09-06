"""Retain site-level screen evidence without changing the favorable-tail rule."""
from __future__ import annotations

import json

import numpy as np
import pytest
from ase import Atoms

from hea_oer.adsorption import MACESurfaceBackend, _screen_structure_record
from hea_oer.composition import Composition
from hea_oer.referencing import ZPE_TS_CORRECTION
from scripts.screen_mace import evaluate


@pytest.fixture
def screen_fixture(monkeypatch):
    """Exercise the full aggregation loop with deterministic site energies, no MLIP."""
    import hea_oer.relax as relax_module
    import hea_oer.surfaces_rutile as surface

    triples = {
        (0, 0): (1.4, 2.8, 4.2),
        (0, 1): (1.8, 3.3, 4.7),
        (1, 0): (1.6, 3.1, 4.3),
        (1, 1): (1.3, 2.6, 3.9),
    }
    invalid_sites = {(0, 0)}

    def build_slab(comp, supercell, seed):
        slab = Atoms("FeNiO4" if seed == 0 else "NiFeO4")
        slab.info["seed"] = seed
        return slab

    def add_adsorbate(slab, species, xy):
        atoms = slab.copy()
        atoms += Atoms(species)
        atoms.info.update(species=species, site_index=int(xy[0]))
        return atoms

    def starts(slab, species, xy):
        records = []
        for tag in ("builder", "pull1.70", "pull2.10"):
            atoms = add_adsorbate(slab, species, xy)
            atoms.info["start"] = tag
            atoms.positions[-1, 2] = {"builder": 3.0, "pull1.70": 1.7, "pull2.10": 2.1}[tag]
            records.append((tag, atoms))
        return records

    def relax(atoms, calc, fmax, steps):
        if "species" not in atoms.info:
            return 0.0, atoms.copy()
        state = atoms.info
        key = (state["seed"], state["site_index"])
        species = state["species"]
        energy = triples[key][("OH", "O", "OOH").index(species)]
        energy -= ZPE_TS_CORRECTION[species]
        if state["start"] == "builder":
            energy += 0.2
        elif state["start"] == "pull2.10":
            energy += 0.3
        return energy, atoms.copy()

    def distance(atoms, n_slab):
        state = atoms.info
        key = (state["seed"], state["site_index"])
        return 3.1 if key in invalid_sites and state["species"] == "OOH" else 1.8

    monkeypatch.setattr(surface, "build_rutile110_hea", build_slab)
    monkeypatch.setattr(surface, "cus_site_xy", lambda slab, n_sites: [(0.0, 0.0), (1.0, 0.0)])
    monkeypatch.setattr(surface, "add_oer_adsorbate_at", add_adsorbate)
    monkeypatch.setattr(surface, "adsorbate_starts", starts)
    monkeypatch.setattr(surface, "binding_metal_index", lambda atoms, n: atoms.info["site_index"])
    monkeypatch.setattr(surface, "m_o_distance", distance)
    monkeypatch.setattr(relax_module, "relax", relax)
    backend = MACESurfaceBackend(calculator=object(), seeds=(0, 1), n_sites=2)
    backend._gas = (0.0, 0.0)
    # The finite mock cell has 1:1 cations, deliberately distinct from the target.
    comp = Composition(("Fe", "Ni"), (0.4, 0.6))
    return backend, comp, triples, invalid_sites


def test_retains_all_sites_without_changing_winner_or_spread(screen_fixture):
    backend, comp, triples, _ = screen_fixture
    result = evaluate(backend, comp)
    sites = result["per_site_records"]

    assert [(r["seed"], r["site_index"]) for r in sites] == list(triples)
    for record in sites:
        key = (record["seed"], record["site_index"])
        assert [record[k] for k in ("dG_OH", "dG_O", "dG_OOH")] == pytest.approx(triples[key])
        assert record["site_xy_A"] == [float(key[1]), 0.0]
        assert record["bonds"]["seed"] == key[0]
        assert all(record["bonds"][s + "_start"] == "pull1.70" for s in ("OH", "O", "OOH"))
        for state in record["relaxed_states"].values():
            assert state["positions_A"][-1][2] == 1.7  # lowest energy start, not last trial
            assert state["fmax_target_eV_A"] == 0.05
            assert state["max_constrained_force_eV_A"] is None
            assert state["converged_by_force"] is None
            assert state["force_readout"] == "unavailable"

    expected_eta = np.array([0.17, 0.57, 0.37, 0.07])
    assert [r["eta"] for r in sites] == pytest.approx(expected_eta)
    assert sites[0]["desorbed"] == ["OOH"]
    assert sites[-1]["desorbed"] == []
    assert sites[0]["bonds"]["site_metal"] == "Fe"
    assert sites[-1]["bonds"]["site_metal"] == "Fe"
    assert result["eta"] == pytest.approx(0.07)
    assert [result[k] for k in ("dG_OH", "dG_O", "dG_OOH")] == pytest.approx(triples[(1, 1)])
    assert result["eta_min"] == pytest.approx(expected_eta.min())
    assert result["eta_mean"] == pytest.approx(expected_eta.mean())
    assert result["eta_std"] == pytest.approx(expected_eta.std())
    assert result["eta_max"] == pytest.approx(expected_eta.max())
    assert result["n_sites"] == 4
    assert result["n_decorations"] == 2
    assert result["bonds"] == sites[-1]["bonds"]
    assert result["desorbed"] == []
    assert "all_bonds" not in result
    assert len(backend.site_records[comp.formula()]["all_bonds"]) == 4
    assert json.loads(json.dumps(result))["per_site_records"] == sites
    assert backend.partial_site_records[comp.formula()]["status"] == "complete"
    assert backend.partial_site_records[comp.formula()]["in_progress_site"] is None


def test_records_actual_cation_counts_separately_from_nominal_composition(screen_fixture):
    backend, comp, _, _ = screen_fixture
    result = evaluate(backend, comp)
    decorations = result["decoration_records"]
    assert [r["seed"] for r in decorations] == [0, 1]
    for record in decorations:
        assert record["n_cations"] == 2
        assert record["cation_counts"] == {"Fe": 1, "Ni": 1}
        assert record["cation_fractions"] == {"Fe": 0.5, "Ni": 0.5}
        assert record["cation_fractions"] != comp.as_dict()
        assert len(record["relaxed_slab"]["symbols"]) == 6
        assert record["relaxed_slab"]["converged_by_force"] is None
    assert json.loads(json.dumps(result))["decoration_records"] == decorations


def test_retains_invalid_winner_without_silently_selecting_runner_up(screen_fixture):
    backend, comp, _, invalid_sites = screen_fixture
    invalid_sites.add((1, 1))
    result = evaluate(backend, comp)
    assert result["eta"] == pytest.approx(0.07)
    assert result["desorbed"] == ["OOH"]
    assert len(result["per_site_records"]) == 4
    assert sum(not r["desorbed"] for r in result["per_site_records"]) == 2


@pytest.mark.parametrize("force, expected", [(0.049, True), (0.05, False), (0.1, False)])
def test_force_snapshot_respects_constraints_and_threshold(force, expected):
    from ase.calculators.singlepoint import SinglePointCalculator
    from ase.constraints import FixAtoms

    atoms = Atoms("FeO", positions=[[0, 0, 0], [0, 0, 1.8]], cell=[5, 5, 5], pbc=True)
    atoms.set_constraint(FixAtoms(indices=[0]))
    atoms.calc = SinglePointCalculator(atoms, forces=[[9.0, 0, 0], [force, 0, 0]])
    record = _screen_structure_record(atoms, 0.05)
    assert record["max_constrained_force_eV_A"] == pytest.approx(force)
    assert record["converged_by_force"] is expected
    assert record["fixed_atom_indices"] == [0]
    assert record["force_readout"] == "cached"
    assert record["symbols"] == ["Fe", "O"]
    assert record["positions_A"] == [[0, 0, 0], [0, 0, 1.8]]
    assert record["cell_A"] == [[5, 0, 0], [0, 5, 0], [0, 0, 5]]
    assert record["pbc"] == [True, True, True]
    assert json.loads(json.dumps(record)) == record
    # Reading a record must not modify the calculator's unconstrained force array.
    assert atoms.calc.results["forces"][0, 0] == 9.0


def test_stale_force_cache_is_unknown_and_never_recomputed():
    from ase.calculators.singlepoint import SinglePointCalculator

    atoms = Atoms("FeO", positions=[[0, 0, 0], [0, 0, 1.8]])
    atoms.calc = SinglePointCalculator(atoms, forces=np.zeros((2, 3)))
    atoms.positions[-1, 2] += 0.1
    # Asking SinglePointCalculator for new forces would fail for the changed structure.
    record = _screen_structure_record(atoms, 0.05)
    assert record["force_readout"] == "cache_not_current"
    assert record["converged_by_force"] is None
    assert record["max_constrained_force_eV_A"] is None


def test_nonfinite_cached_force_is_not_converged():
    from ase.calculators.singlepoint import SinglePointCalculator

    atoms = Atoms("FeO")
    atoms.calc = SinglePointCalculator(atoms, forces=[[float("nan"), 0, 0], [0, 0, 0]])
    record = _screen_structure_record(atoms, 0.05)
    assert record["force_readout"] == "nonfinite"
    assert record["converged_by_force"] is False
    assert record["max_constrained_force_eV_A"] is None


def test_raw_energy_records_reconstruct_every_site_with_nonzero_gas_refs(screen_fixture):
    from hea_oer.referencing import delta_G

    backend, comp, _, _ = screen_fixture
    backend._gas = (-10.0, -4.0)
    result = evaluate(backend, comp)
    for site in result["per_site_records"]:
        energies = site["energies_eV"]
        assert energies["H2O"] == -10.0
        assert energies["H2"] == -4.0
        for species in ("OH", "O", "OOH"):
            assert delta_G(energies["slab"], energies[species], species,
                           energies["H2O"], energies["H2"]) == pytest.approx(site["dG_" + species])
            assert energies[species] == min(r["energy_eV"] for r in site["start_records"][species])
            assert site["relaxed_states"][species]["energy_eV"] == energies[species]
        decoration = next(r for r in result["decoration_records"] if r["seed"] == site["seed"])
        assert decoration["energy_eV"] == energies["slab"]
        assert decoration["relaxed_slab"]["energy_eV"] == energies["slab"]
    for name, energy in (("H2O", -10.0), ("H2", -4.0)):
        gas = result["gas_reference_records"][name]
        assert gas["energy_eV"] == energy
        assert gas["converged_by_force"] is None
        assert gas["force_readout"] == "unavailable"


def test_all_start_qc_survives_even_when_bad_start_does_not_win(screen_fixture, monkeypatch):
    from ase.calculators.singlepoint import SinglePointCalculator
    import hea_oer.relax as relax_module

    backend, comp, _, _ = screen_fixture
    original_relax = relax_module.relax

    def with_forces(atoms, calc, fmax, steps):
        energy, relaxed = original_relax(atoms, calc, fmax, steps)
        # The last, higher-energy start misses convergence; the winner is converged.
        force = 0.1 if atoms.info.get("start") == "pull2.10" else 0.01
        relaxed.calc = SinglePointCalculator(relaxed, forces=np.full((len(relaxed), 3), force / np.sqrt(3)))
        return energy, relaxed

    monkeypatch.setattr(relax_module, "relax", with_forces)
    result = evaluate(backend, comp)
    assert result["eta"] == pytest.approx(0.07)
    for site in result["per_site_records"]:
        for species in ("OH", "O", "OOH"):
            starts = site["start_records"][species]
            assert [r["start"] for r in starts] == ["builder", "pull1.70", "pull2.10"]
            assert [r["converged_by_force"] for r in starts] == [True, True, False]
            assert starts[-1]["max_constrained_force_eV_A"] == pytest.approx(0.1)
            assert site["relaxed_states"][species]["converged_by_force"] is True
            assert "positions_A" not in starts[0]  # full geometries retained only for winners


def test_final_binding_migration_is_distinct_from_legacy_site_metal(screen_fixture, monkeypatch):
    import hea_oer.surfaces_rutile as surface

    backend, comp, _, _ = screen_fixture

    def binding_index(atoms, n_slab):
        initial = atoms.info["site_index"]
        # Only the relaxed OH trials migrate; the reference-site construction does not.
        return 1 - initial if "start" in atoms.info and atoms.info["species"] == "OH" else initial

    monkeypatch.setattr(surface, "binding_metal_index", binding_index)
    result = evaluate(backend, comp)
    first = result["per_site_records"][0]
    assert first["initial_binding_metal_index"] == 0
    assert first["initial_binding_metal"] == first["bonds"]["site_metal"] == "Fe"
    assert first["relaxed_states"]["OH"]["final_binding_metal_index"] == 1
    assert first["relaxed_states"]["OH"]["final_binding_metal"] == "Ni"
    assert first["relaxed_states"]["O"]["final_binding_metal"] == "Fe"
    assert all(r["final_binding_metal"] == "Ni" for r in first["start_records"]["OH"])
    assert result["eta"] == pytest.approx(0.07)
    assert result["bonds"]["site_metal"] == "Fe"


def test_gas_callback_keeps_each_molecule_qc_and_reuses_cached_energies(monkeypatch):
    from ase.calculators.singlepoint import SinglePointCalculator
    import hea_oer.relax as relax_module

    calls = []

    def gas_relax(atoms, calc, fmax, steps):
        relaxed = atoms.copy()
        name = "H2O" if len(atoms) == 3 else "H2"
        calls.append(name)
        energy = -14.0 if name == "H2O" else -6.0
        force = 0.01 if name == "H2O" else 0.1
        relaxed.calc = SinglePointCalculator(relaxed, forces=np.full((len(relaxed), 3), force / np.sqrt(3)))
        return energy, relaxed

    monkeypatch.setattr(relax_module, "relax", gas_relax)
    backend = MACESurfaceBackend(calculator=object())
    assert backend._gas_refs() == (-14.0, -6.0)
    assert backend._gas_records["H2O"]["converged_by_force"] is True
    assert backend._gas_records["H2"]["converged_by_force"] is False
    assert backend._gas_records["H2O"]["energy_eV"] == -14.0
    assert backend._gas_records["H2"]["energy_eV"] == -6.0
    assert len(backend._gas_records["H2O"]["symbols"]) == 3
    assert len(backend._gas_records["H2"]["symbols"]) == 2
    assert backend._gas_refs() == (-14.0, -6.0)
    assert calls == ["H2O", "H2"]
    # The public helper still returns its original tuple without a callback.
    assert relax_module.gas_reference_energies(object()) == (-14.0, -6.0)


def test_mid_site_exception_retains_completed_sites_and_current_starts(screen_fixture, monkeypatch):
    import hea_oer.relax as relax_module

    backend, comp, _, _ = screen_fixture
    original_relax = relax_module.relax

    def fail_mid_site(atoms, calc, fmax, steps):
        state = atoms.info
        if (state.get("seed"), state.get("site_index"), state.get("species"),
                state.get("start")) == (1, 1, "O", "pull1.70"):
            raise RuntimeError("mock mid-site calculation failure")
        return original_relax(atoms, calc, fmax, steps)

    monkeypatch.setattr(relax_module, "relax", fail_mid_site)
    with pytest.raises(RuntimeError, match="mock mid-site"):
        evaluate(backend, comp)
    assert comp.formula() not in backend.site_records
    partial = backend.partial_site_records[comp.formula()]
    assert partial["status"] == "incomplete"
    assert partial["stage"] == "adsorbate_relaxation"
    assert len(partial["decoration_records"]) == 2
    assert all("energy_eV" in r for r in partial["decoration_records"])
    assert [(r["seed"], r["site_index"]) for r in partial["per_site_records"]] == [(0, 0), (0, 1), (1, 0)]
    pending = partial["in_progress_site"]
    assert (pending["seed"], pending["site_index"]) == (1, 1)
    assert pending["completed_species"] == ["OH"]
    assert pending["active_species"] == "O"
    assert pending["active_start"] == "pull1.70"
    assert len(pending["start_records"]["OH"]) == 3
    assert [r["start"] for r in pending["start_records"]["O"]] == ["builder"]
    assert "OH" in pending["energies_eV"]
    assert "O" not in pending["energies_eV"]
    assert "OOH" not in pending["start_records"]
    assert json.loads(json.dumps(partial)) == partial


def test_gas_exception_retains_first_molecule_before_any_site(monkeypatch):
    from ase.calculators.singlepoint import SinglePointCalculator
    import hea_oer.relax as relax_module

    def fail_second_molecule(atoms, calc, fmax, steps):
        if len(atoms) == 2:
            raise RuntimeError("mock gas failure")
        relaxed = atoms.copy()
        relaxed.calc = SinglePointCalculator(relaxed, forces=np.zeros((len(relaxed), 3)))
        return -14.0, relaxed

    monkeypatch.setattr(relax_module, "relax", fail_second_molecule)
    backend = MACESurfaceBackend(calculator=object())
    comp = Composition(("Fe", "Ni"), (0.4, 0.6))
    with pytest.raises(RuntimeError, match="mock gas failure"):
        backend.predict(comp)
    partial = backend.partial_site_records[comp.formula()]
    assert partial["status"] == "incomplete"
    assert partial["stage"] == "gas_references"
    assert set(partial["gas_reference_records"]) == {"H2O"}
    assert partial["gas_reference_records"]["H2O"]["energy_eV"] == -14.0
    assert partial["gas_reference_records"]["H2O"]["converged_by_force"] is True
    assert partial["per_site_records"] == []
    assert partial["decoration_records"] == []
    assert partial["in_progress_site"] is None
    assert comp.formula() not in backend.site_records
