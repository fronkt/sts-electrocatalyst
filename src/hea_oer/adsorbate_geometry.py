"""Calculator-free geometry flags; no eligibility, energy or ranking changes."""
from __future__ import annotations
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
import math
from numbers import Real
import numpy as np
from ase import Atoms
from ase.data import atomic_numbers

STATES = ("OH", "O", "OOH")
APPENDED = {"OH": ["O", "H"], "O": ["O"], "OOH": ["O", "O", "H"]}
DEFAULT_METALS = ("Al", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Ru", "Ir")


def _finite(value):
    return isinstance(value, Real) and not isinstance(value, (bool, np.bool_)) and math.isfinite(value)


@dataclass(frozen=True)
class GeometryThresholds:
    """Exploratory angstrom windows; inclusive endpoints, preserved nearest ties."""
    oo_min_A: float = 1.10
    oo_max_A: float = 1.80
    oh_min_A: float = 0.70
    oh_max_A: float = 1.25
    h_slab_o_max_A: float = 1.25
    metal_contact_max_A: float = 3.00
    nearest_tie_tolerance_A: float = 1e-6

    def __post_init__(self):
        for name, value in asdict(self).items():
            if not _finite(value) or value <= 0:
                raise ValueError(name + " must be finite and positive")
        if self.oo_min_A >= self.oo_max_A or self.oh_min_A >= self.oh_max_A:
            raise ValueError("distance windows must have increasing endpoints")
        if self.nearest_tie_tolerance_A >= min(self.oo_min_A, self.oh_min_A):
            raise ValueError("nearest tie tolerance must be smaller than window minima")


class _MissingGeometry(ValueError):
    pass


def _index(value, name):
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(name + " must be a nonnegative integer")
    return value


def _atoms(record):
    if record is None:
        raise _MissingGeometry("retained structure absent")
    if not isinstance(record, Mapping):
        raise ValueError("retained structure must be a mapping")
    absent = [key for key in ("symbols", "positions_A", "cell_A", "pbc") if record.get(key) is None]
    if absent:
        raise _MissingGeometry("retained geometry missing: " + ", ".join(absent))
    symbols = record["symbols"]
    if not isinstance(symbols, list) or not symbols or any(not isinstance(s, str) or s not in atomic_numbers or s == "X" for s in symbols):
        raise ValueError("symbols must be a nonempty list of chemical elements")
    pbc = record["pbc"]
    if not isinstance(pbc, list) or len(pbc) != 3 or any(type(x) is not bool for x in pbc):
        raise ValueError("pbc must contain three explicit booleans")
    arrays = {}
    for key, shape in (("positions_A", (len(symbols), 3)), ("cell_A", (3, 3))):
        raw = np.asarray(record[key], dtype=object)
        if raw.shape != shape or any(not _finite(x) for x in raw.flat):
            raise ValueError(key + " has invalid shape or nonfinite/nonnumeric coordinates")
        arrays[key] = np.asarray(raw, dtype=float)
    vectors = arrays["cell_A"][np.asarray(pbc)]
    if len(vectors) and np.linalg.matrix_rank(vectors) != len(vectors):
        raise ValueError("periodic cell vectors must be nonzero and independent")
    return Atoms(symbols=symbols, positions=arrays["positions_A"], cell=arrays["cell_A"], pbc=pbc)


def _contact(atoms, source, candidates, maximum, tolerance):
    if not candidates:
        return dict(distance_A=None, nearest_indices=[], nearest_symbols=[], within_threshold_indices=[], unique_nearest_index=None)
    distances = np.asarray(atoms.get_distances(source, candidates, mic=True), dtype=float)
    if not np.isfinite(distances).all():
        raise ValueError("minimum-image distances are nonfinite")
    minimum = float(distances.min())
    nearest = [int(i) for i, d in zip(candidates, distances) if d <= minimum + tolerance]
    return dict(distance_A=minimum, nearest_indices=nearest, nearest_symbols=[atoms[i].symbol for i in nearest],
                within_threshold_indices=[int(i) for i, d in zip(candidates, distances) if d <= maximum],
                unique_nearest_index=nearest[0] if len(nearest) == 1 else None)


def _numerical_metadata(record):
    record = record if isinstance(record, Mapping) else {}
    flag = record.get("converged_by_force")
    return dict(converged_by_force=flag if type(flag) is bool else None,
                **{key: float(record[key]) if _finite(record.get(key)) else None for key in
                   ("energy_eV", "max_constrained_force_eV_A", "fmax_target_eV_A")},
                interpretation="Reported metadata only; numerical and energy consistency checks are separate.")


def _state_geometry(record, state, slab, thresholds, metals):
    atoms = _atoms(record)
    n = len(slab)
    if atoms.get_chemical_symbols() != slab.get_chemical_symbols() + APPENDED[state]:
        raise ValueError("atom count/order differs from clean-slab prefix plus " + state)
    if not np.array_equal(atoms.pbc, slab.pbc) or not np.allclose(atoms.cell, slab.cell, rtol=0, atol=1e-10):
        raise ValueError("selected state cell or periodicity differs from clean slab")
    slab_metals = [i for i in range(n) if atoms[i].symbol in metals]
    slab_oxygen = [i for i in range(n) if atoms[i].symbol == "O"]
    unsupported = sorted(set(slab.get_chemical_symbols()) - set(metals) - {"O", "H"})
    issues, flags = [], []
    if unsupported:
        issues.append("slab species outside explicit metal/O/H classification: " + ", ".join(unsupported))
    if not slab_metals:
        issues.append("no slab metal in explicit metal classification")
    tol = thresholds.nearest_tie_tolerance_A
    oxygen_indices = {"proximal_O": n}
    if state == "OOH":
        oxygen_indices["distal_O"] = n + 1
    contacts = {role: _contact(atoms, i, slab_metals, thresholds.metal_contact_max_A, tol) for role, i in oxygen_indices.items()}
    substrate_contacts = {role: _contact(atoms, i, list(range(n)), thresholds.metal_contact_max_A, tol) for role, i in oxygen_indices.items()}
    distances, h_contact = {}, None
    if state != "O":
        h = len(atoms) - 1
        for role, i in oxygen_indices.items():
            distances[role + "_H_A"] = float(atoms.get_distance(i, h, mic=True))
        h_contact = _contact(atoms, h, slab_oxygen, thresholds.h_slab_o_max_A, tol)
        ads_oh = min(distances.values())
        if not thresholds.oh_min_A <= ads_oh <= thresholds.oh_max_A:
            flags.append("nearest_adsorbate_O_H_outside_exploratory_window")
        if h_contact["distance_A"] is not None and h_contact["distance_A"] <= thresholds.h_slab_o_max_A:
            flags.append("short_H_to_slab_O_contact")
            if h_contact["distance_A"] + tol < ads_oh:
                flags.append("H_closer_to_slab_O_than_adsorbate_O")
    if state == "OOH":
        distances["O_O_A"] = float(atoms.get_distance(n, n + 1, mic=True))
        if distances["O_O_A"] < thresholds.oo_min_A:
            flags.append("O_O_below_exploratory_window")
        elif distances["O_O_A"] > thresholds.oo_max_A:
            flags.append("O_O_above_exploratory_window")
        prox, dist = distances["proximal_O_H_A"], distances["distal_O_H_A"]
        h_nearest = "proximal_O" if prox + tol < dist else "distal_O" if dist + tol < prox else "ambiguous"
    else:
        h_nearest = "proximal_O" if state == "OH" else None
    if not all(math.isfinite(value) for value in distances.values()):
        raise ValueError("minimum-image distances are nonfinite")
    prox = contacts["proximal_O"]
    if prox["distance_A"] is not None and not prox["within_threshold_indices"]:
        flags.append("proximal_O_without_metal_contact_within_exploratory_threshold")
    different = None
    if state == "OOH":
        distal = contacts["distal_O"]
        if prox["unique_nearest_index"] is not None and distal["unique_nearest_index"] is not None:
            different = prox["unique_nearest_index"] != distal["unique_nearest_index"]
    return dict(geometry_status="unknown" if issues else "observed", issues=issues,
                exploratory_screen="unknown" if issues else "review" if flags else "no_flags", flags=flags,
                n_slab_atoms=n, adsorbate_indices={**oxygen_indices, **({"H": len(atoms)-1} if state != "O" else {})},
                distances_A=distances, oxygen_metal_contacts=contacts, oxygen_substrate_contacts=substrate_contacts,
                H_nearest_slab_O=h_contact, H_nearest_adsorbate_O=h_nearest,
                oxygens_have_different_unique_nearest_metals=different,
                interpretation="Distance flags request inspection, not established cleavage/proton transfer. Different nearest metals are not automatic failures or evidence of adsorption.")


def _binding_changes(site, states, slab, metals):
    initial = site.get("initial_binding_metal_index")
    if not isinstance(initial, int) or isinstance(initial, bool) or initial < 0 or slab is None or initial >= len(slab) or slab[initial].symbol not in metals:
        initial = None
    nearest = {}
    for state, detail in states.items():
        contact = detail.get("oxygen_metal_contacts", {}).get("proximal_O", {})
        nearest[state] = contact.get("nearest_indices", []) if detail["geometry_status"] == "observed" else []
    unique = {state: ids[0] if len(ids) == 1 else None for state, ids in nearest.items()}
    known = [i for i in unique.values() if i is not None]
    different = True if len(set(known)) > 1 else False if len(known) == len(STATES) else None
    return dict(initial_index=initial, nearest_indices_by_state=nearest, unique_nearest_index_by_state=unique,
                cross_state_unique_partners_differ=different,
                changed_nearest_index_states=[state for state, index in unique.items() if index is not None and initial is not None and index != initial],
                unresolved_states=[state for state, index in unique.items() if index is None],
                interpretation="Index identity assumes retained atom order. Ties remain unresolved. Nearest does not establish a chemical bond or physical migration event.")


def analyze_adsorbate_geometry(row, *, thresholds=None, metal_symbols=DEFAULT_METALS):
    """Audit ordered sites using actual PBC and skew cells; missing/invalid fail closed."""
    thresholds = GeometryThresholds() if thresholds is None else thresholds
    if not isinstance(thresholds, GeometryThresholds):
        raise ValueError("thresholds must be a GeometryThresholds instance")
    if not isinstance(metal_symbols, Sequence) or isinstance(metal_symbols, (str, bytes)) or not metal_symbols or any(not isinstance(s, str) or s not in atomic_numbers or s in ("O", "H", "X") for s in metal_symbols) or len(set(metal_symbols)) != len(metal_symbols):
        raise ValueError("metal_symbols must be an explicit nonempty distinct element sequence")
    if not isinstance(row, Mapping):
        raise ValueError("row must be a mapping")
    records, decorations = row.get("per_site_records"), row.get("decoration_records", [])
    if not isinstance(records, list) or not records:
        raise ValueError("nonempty per_site_records required")
    if not isinstance(decorations, list):
        raise ValueError("decoration_records must be a list")
    by_seed = {}
    for record in decorations:
        if not isinstance(record, Mapping):
            raise ValueError("decoration record must be a mapping")
        seed = _index(record.get("seed"), "decoration seed")
        if seed in by_seed:
            raise ValueError("duplicate decoration seed")
        by_seed[seed] = record
    sites, seen = [], set()
    for site in records:
        if not isinstance(site, Mapping):
            raise ValueError("site record must be a mapping")
        seed, index = _index(site.get("seed"), "site seed"), _index(site.get("site_index"), "site index")
        name = f"seed={seed}/site={index}"
        if name in seen:
            raise ValueError("duplicate site identity: " + name)
        seen.add(name)
        slab, slab_error, slab_status = None, None, None
        try:
            slab = _atoms(by_seed.get(seed, {}).get("relaxed_slab"))
        except _MissingGeometry as exc:
            slab_error, slab_status = "clean slab: " + str(exc), "unknown"
        except (ValueError, TypeError, np.linalg.LinAlgError) as exc:
            slab_error, slab_status = "clean slab: " + str(exc), "invalid"
        selected, states = site.get("relaxed_states"), {}
        for state in STATES:
            record = selected.get(state) if isinstance(selected, Mapping) else None
            try:
                if selected is not None and not isinstance(selected, Mapping):
                    raise ValueError("relaxed_states must be a mapping")
                detail = dict(geometry_status=slab_status, exploratory_screen="unknown", issues=[slab_error], flags=[]) if slab_error else _state_geometry(record, state, slab, thresholds, metal_symbols)
            except _MissingGeometry as exc:
                detail = dict(geometry_status="unknown", exploratory_screen="unknown", issues=[str(exc)], flags=[])
            except (ValueError, TypeError, np.linalg.LinAlgError) as exc:
                detail = dict(geometry_status="invalid", exploratory_screen="unknown", issues=[str(exc)], flags=[])
            detail["numerical_metadata"] = _numerical_metadata(record)
            states[state] = detail
        sites.append(dict(site_id=name, seed=seed, site_index=index, states=states, binding_changes=_binding_changes(site, states, slab, metal_symbols)))
    return dict(schema_version=1, analysis="selected_adsorbate_geometry_diagnostic",
                formula=row.get("formula") if isinstance(row.get("formula"), str) else None,
                thresholds_A=asdict(thresholds), metal_symbols=list(metal_symbols), sites=sites,
                n_observed_site_records=len(sites), state_geometry_counts={status: sum(s["states"][state]["geometry_status"] == status for s in sites for state in STATES) for status in ("observed", "unknown", "invalid")},
                ranking_modified=False, eligibility_modified=False, chemistry_validated=False,
                scope="Coordinates supplied in relaxed_states only; no audit of absent attempted-start coordinates.",
                interpretation="Exploratory flags request inspection, not automatic rejection. No flags does not establish intact adsorbates, convergence, complete basin search, mechanism or performance.")
