"""CENSUS-1b *O2 fragment completion of H-TRANSFERRED OOH endpoints (docs/91:36).

For every CENSUS-1 site whose relaxed OOH endpoint is *O2 + H_b under readout (b) -- the
hydrogen H_TRANSFERRED to a slab oxygen and the fragment bound or weak (M-O < 3.00 A), which
is the pathway_state "*O2+H_b" of hea_oer.site_integrity (H_TRANSFERRED, not desorbed, O-O
not cleaved) -- this module builds the H-removed state (the retained relaxed OOH geometry with
the transferred hydrogen deleted; same cell, same FixAtoms constraint with the indices
re-numbered for the deleted atom) and relaxes it with hea_oer.relax.relax at the census
protocol (fmax, steps and dtype read from the result's embedded manifest: fmax 0.05 eV/A,
300 BFGS steps, float64, the same checkpoint), together with the O2 molecule relaxed by the
same calculator, so that

    dG_ads(O2) = E(*O2) - E_slab - E_O2(model) + (ZPE - TS)

is computable from the retained energies of one calculator. The (ZPE - TS) term is applied
by site_integrity.o2_fragment_diagnostic through the readout, never here. The per-site record
carries the fixed schema {"energy_eV", "E_O2_gas_eV", "converged_by_force"} (docs/91:36,
site_integrity.o2_fragment_diagnostic) plus keys the readout ignores (E_O2_box12_eV,
E_O2_slab_cell_eV, o2_cell, o2_cell_id, fragment_converged_by_force, o2_gas_converged_by_force).

Site selection. ``select_sites`` classifies the row with site_integrity.classify_row and
takes a site when its OOH pathway_state is "*O2+H_b"; every other OOH state is listed with
the reason (H ON_ADSORBATE, H_FREE, fragment desorbed, O-O cleaved, or the state missing).
docs/91:36 states the site set as "hydrogen H-TRANSFERRED, fragment bound or weak"; the third
condition, O-O not cleaved, is not in that sentence and is read in from readout (c)
(docs/91:63: an O-O-cleaved endpoint is pathway-undefined) through the "under readout (b)"
clause, so that the 1b set equals the bridge-pathway set of the readout. On the 144 CENSUS-1
sites the two wordings select the same 13 sites (no H-TRANSFERRED bound-or-weak state is
OO_CLEAVED); the reading is recorded here so it is visible, and it changes no count. Force
convergence of the OOH state is not a selection criterion (docs/91:36 names none); it is
carried in the selection record. The transferred hydrogen is identified independently of the
classification: the state must carry exactly one H, it must lie within h_bond_max_A (1.15 A,
the Proposed CENSUS-3 window) of a slab oxygen and not within that window of either
adsorbate oxygen, all distances periodic minimum-image.

O2 cell. docs/91:36 says "the O2 molecule in the same model and cell" and bounds the arm at
"144 + 1" relaxations, which reads as one O2 relaxation; which cell that one is, is not
pre-stated. The default here (o2_cell = "slab") is a reading of that sentence, not a
pre-stated value: ``E_O2_gas_eV`` is the O2 molecule relaxed in the slab cell of the
composition's retained states, so that E(*O2) - E_slab - E_O2 subtracts the same cell, one
relaxation per distinct cell (the twelve compositions carry twelve distinct cells, so twelve
composition-specific values). Across the twelve CENSUS-1 compositions the shortest lattice
vector of that cell is 5.856-5.984 A (results/site_census_2026-09-06/results/mpa0__*_result.json,
per_site_records[*].relaxed_states.*.cell_A); a molecule in it interacts with its own
periodic images under any model whose receptive field exceeds that length, and the *O2
fragment on the slab shares the cell and those images. The value in the project's 12 A gas
box (the hea_oer.relax.gas_reference_energies convention for H2O and H2) is always relaxed
as well and recorded beside it under ``E_O2_box12_eV``; o2_cell = "box12" swaps which of the
two feeds ``E_O2_gas_eV``. Both O2 energies are recorded per composition, the choice is
recorded in every record (``o2_cell``, ``o2_cell_id``) and in the audit header, and the
audit's fragment block carries the no-ZPE difference under both cells and the diagnostic at
(ZPE - TS) = 0.00, 0.05 and 0.10 eV for both (docs/91:36 asks for the 0.00 / 0.10 eV values
beside the Proposed 0.05 eV; the hash-pinned readout computes only the 0.05 eV value).

Force convergence. ``converged_by_force`` of the readout record is True only when BOTH the
fragment relaxation AND the O2 relaxation that feeds ``E_O2_gas_eV`` converged, since the
diagnostic subtracts the two; the two flags are carried separately beside it
(``fragment_converged_by_force``, ``o2_gas_converged_by_force``). Each follows the census
driver's own derivation (hea_oer.adsorption._screen_structure_record, adsorption.py:80-119):
the calculator's cached forces after the last BFGS step, constraint-adjusted, maximum per-atom
force norm < fmax; a non-current cache or a nonfinite force is reported under
``force_readout`` and never counts as converged. As in that derivation, FixAtoms.adjust_forces
zeroes the forces on fixed atoms before the finiteness check, so a nonfinite force on a
FIXED atom does not by itself mark the state unconverged (pinned by tests/test_o2_fragment.py).
Force convergence is numerical metadata, not adsorption-chemistry validation.

A site whose fragment relaxation raises is recorded in the audit with status "failed" and the
error text, gets no readout record, and the composition continues; the audit carries the
failed keys. Two hash-pinned modules (docs/91 section 7) are imported read-only:
hea_oer.site_integrity (classification, thresholds, record schema) and hea_oer.relax (relax);
the MACE calculator is constructed by the CLI (relax.make_mace_calculator), never here.
Nothing here scores a docs/43 prediction, registers a threshold, moves a banked value or
enters a ranking rule (docs/91 readout (c)); the records are a fragment-binding diagnostic,
reportable only as CALIBRATION under docs/43:3447-3455.
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
import math
import time

import numpy as np
from ase import Atoms
from ase.constraints import FixAtoms

from . import site_integrity as integrity
from .relax import relax

RECORD_SCHEMA = "census-1b-o2-fragment-v1"
#: The OOH pathway_state of site_integrity that qualifies a site (docs/91:36, readout (c)).
QUALIFYING_PATHWAY_STATE = "*O2+H_b"
O2_CELL_CHOICES = ("slab", "box12")
#: hea_oer.relax.gas_reference_energies default box edge (A).
GAS_BOX_A = 12.0
DEFAULT_FMAX = 0.05
DEFAULT_STEPS = 300
DEFAULT_DTYPE = "float64"
#: Keys of the per-site record the readout consumes (site_integrity.o2_fragment_diagnostic).
READOUT_KEYS = ("energy_eV", "E_O2_gas_eV", "converged_by_force")
#: (ZPE - TS) values at which the audit reports the diagnostic: the Proposed 0.05 eV
#: (site_integrity.ZPE_TS_O2_DEFAULT, CENSUS-7 slot) and the 0.00 / 0.10 eV box of docs/91:36.
ZPE_TS_REPORTED_EV = (0.0, float(integrity.ZPE_TS_O2_DEFAULT), 0.10)


def site_key(seed, site_index):
    """The readout's key format, site_census_readout.load_o2_records: 'seed/site_index'."""
    return f"{int(seed)}/{int(site_index)}"


def cell_id(cell):
    """Short identity of a cell matrix (sha256 of its JSON float repr)."""
    arr = np.asarray(cell, dtype=float)
    if arr.shape != (3, 3) or not np.isfinite(arr).all():
        raise ValueError("cell must be a finite 3x3 matrix")
    return hashlib.sha256(json.dumps(arr.tolist()).encode()).hexdigest()[:16]


def box12_cell():
    return np.diag([GAS_BOX_A, GAS_BOX_A, GAS_BOX_A])


# ----------------------------------------------------------------------------------------
# Site selection
# ----------------------------------------------------------------------------------------

def ooh_reasons(state, thresholds=integrity.DEFAULT_THRESHOLDS):
    """Why a classified OOH state (site_integrity.classify_state output) is not *O2 + H_b:
    a list of (class, text) pairs, empty when it is. Every failing condition is listed, not
    only the first. Classes: ON_ADSORBATE, H_FREE, DESORBED, OO_CLEAVED."""
    reasons = []
    h = state.get("h_location")
    if h == "ON_ADSORBATE":
        reasons.append(("ON_ADSORBATE", f"H ON_ADSORBATE ({state.get('h_carrier')}): endpoint *OOH, cus pathway"))
    elif h == "H_FREE":
        reasons.append(("H_FREE", "H_FREE: endpoint pathway-undefined"))
    elif h != "H_TRANSFERRED":
        reasons.append(("H_LOCATION", f"h_location {h!r}"))
    if state.get("bond_tier") == "desorbed":
        reasons.append(("DESORBED", f"fragment desorbed: M-O {state.get('m_o_A')!r} A >= {thresholds.desorbed_min_A} A"))
    if state.get("o_o_class") == "OO_CLEAVED":
        reasons.append(("OO_CLEAVED", f"O-O cleaved: {state.get('o_o_A')!r} A > {thresholds.ooh_like_max_A} A"))
    return reasons


def _is_classified_row(obj):
    return isinstance(obj, Mapping) and "sites" in obj and "per_site_records" not in obj


def select_sites(row_or_classified, thresholds=integrity.DEFAULT_THRESHOLDS):
    """Per site of a screen-diagnostic-v1 row (results[].row) or of its classify_row output:
    dict(seed, site_index, key, qualifies, reason, ooh=<OOH summary>). A site qualifies when
    its OOH pathway_state is "*O2+H_b"; the explicit conditions (H_TRANSFERRED, not desorbed,
    O-O not cleaved) are checked to agree with that label."""
    if _is_classified_row(row_or_classified):
        classified = row_or_classified
    else:
        classified = integrity.classify_row(row_or_classified, thresholds)
    out = []
    for site in classified["sites"]:
        seed, index = site["seed"], site["site_index"]
        entry = dict(seed=seed, site_index=index, key=site_key(seed, index),
                     initial_metal=site.get("initial_binding_metal"), eta_V=site.get("eta_V"),
                     pathway=site.get("pathway"), qualifies=False, reason=None, reason_class=None, ooh=None)
        ooh = (site.get("states") or {}).get("OOH")
        if ooh is None:
            entry.update(reason="OOH state missing", reason_class="MISSING")
            out.append(entry)
            continue
        reasons = ooh_reasons(ooh, thresholds)
        qualifies = ooh.get("pathway_state") == QUALIFYING_PATHWAY_STATE
        if qualifies != (not reasons):
            raise RuntimeError(f"site {entry['key']}: pathway_state {ooh.get('pathway_state')!r} "
                               f"disagrees with the explicit conditions {reasons}")
        entry.update(qualifies=qualifies,
                     reason=None if qualifies else "; ".join(text for _, text in reasons),
                     reason_class=None if qualifies else "+".join(cls for cls, _ in reasons),
                     ooh={k: ooh.get(k) for k in (
                         "bond_tier", "m_o_A", "binding_O", "binding_metal", "binding_metal_index",
                         "o_o_A", "o_o_class", "h_location", "h_carrier", "h_nearest_slab_O_index",
                         "h_nearest_slab_O_A", "category", "converged_by_force", "pathway_state",
                         "energy_eV")})
        out.append(entry)
    return out


def qualifying_keys(selection):
    return [(int(s["seed"]), int(s["site_index"])) for s in selection if s["qualifies"]]


# ----------------------------------------------------------------------------------------
# Geometry construction
# ----------------------------------------------------------------------------------------

def identify_transferred_h(state_record, thresholds=integrity.DEFAULT_THRESHOLDS):
    """Locate the transferred hydrogen of a relaxed OOH state record.

    Requires exactly one H in the state, the appended-atom order of the census builder
    (site_integrity.APPENDED["OOH"]: proximal_O, distal_O, H after the slab), the H within
    thresholds.h_bond_max_A of a slab O and not within that window of either adsorbate O
    (periodic minimum-image distances). Raises ValueError otherwise.
    """
    atoms = integrity.atoms_from_record(state_record)
    symbols = atoms.get_chemical_symbols()
    h_indices = [i for i, s in enumerate(symbols) if s == "H"]
    if len(h_indices) != 1:
        raise ValueError(f"OOH state must carry exactly one H, found {len(h_indices)}")
    n_ads = len(integrity.APPENDED["OOH"])
    n_slab = len(atoms) - n_ads
    expected = ["O", "O", "H"]
    if n_slab <= 0 or symbols[n_slab:] != expected:
        raise ValueError(f"appended atoms are {symbols[max(n_slab, 0):]}, expected {expected}")
    h = h_indices[0]
    fragment_o = [n_slab, n_slab + 1]
    slab_o = [i for i in range(n_slab) if symbols[i] == "O"]
    if not slab_o:
        raise ValueError("slab carries no oxygen for the transferred H")
    window = thresholds.h_bond_max_A
    d_fragment = np.asarray(atoms.get_distances(h, fragment_o, mic=True), dtype=float)
    d_slab = np.asarray(atoms.get_distances(h, slab_o, mic=True), dtype=float)
    k = int(np.argmin(d_slab))
    if (d_fragment <= window).any():
        raise ValueError(f"H lies within {window} A of an adsorbate O ({d_fragment.tolist()}): not transferred")
    if not d_slab[k] <= window:
        raise ValueError(f"H is {d_slab[k]:.6f} A from the nearest slab O, outside the {window} A window")
    return dict(h_index=h, n_slab_atoms=n_slab, fragment_O_indices=fragment_o,
                slab_O_index=int(slab_o[k]), h_to_slab_O_A=float(d_slab[k]),
                h_to_fragment_O_A={"proximal_O": float(d_fragment[0]), "distal_O": float(d_fragment[1])},
                h_bond_max_A=float(window))


def shift_fixed_indices(fixed_indices, removed_index):
    """FixAtoms indices after deleting one atom: indices above it move down by one."""
    removed = int(removed_index)
    fixed = sorted({int(i) for i in fixed_indices})
    if removed in fixed:
        raise ValueError(f"atom {removed} is a fixed atom and cannot be removed")
    return [i - 1 if i > removed else i for i in fixed]


def build_fragment_atoms(state_record, thresholds=integrity.DEFAULT_THRESHOLDS):
    """The H-removed *O2 state: ase.Atoms with cell, pbc and FixAtoms restored (indices
    shifted for the deleted atom). Returns (atoms, info)."""
    info = identify_transferred_h(state_record, thresholds)
    other = state_record.get("other_constraint_types") or []
    if other:
        raise ValueError("state carries constraint types this module does not restore: " + ", ".join(other))
    atoms = integrity.atoms_from_record(state_record)
    h = info["h_index"]
    fixed_before = sorted({int(i) for i in (state_record.get("fixed_atom_indices") or [])})
    if fixed_before and (fixed_before[0] < 0 or fixed_before[-1] >= len(atoms)):
        raise ValueError("fixed_atom_indices outside the state")
    fixed_after = shift_fixed_indices(fixed_before, h)
    del atoms[h]
    atoms.set_constraint(FixAtoms(indices=fixed_after))
    info.update(fixed_atom_indices_before=fixed_before, fixed_atom_indices_after=fixed_after,
                fragment_O_indices=[i - 1 if i > h else i for i in info["fragment_O_indices"]],
                n_atoms=len(atoms))
    return atoms, info


def build_o2_atoms(cell, pbc=(True, True, True)):
    """The O2 molecule (ase.build.molecule('O2'), the start relax.gas_reference_energies uses
    for its molecules) centred in `cell`, no constraint."""
    from ase.build import molecule  # ase.build is a 2 s import on this machine; deferred

    o2 = molecule("O2")
    o2.set_cell(np.asarray(cell, dtype=float))
    o2.pbc = [bool(x) for x in pbc]
    o2.center()
    # The cell must hold the molecule: its minimum-image O-O must be the bond itself, not a
    # contact with a periodic image, and every lattice vector must exceed twice the bond.
    bond = float(o2.get_distance(0, 1, mic=False))
    mic = float(o2.get_distance(0, 1, mic=True))
    shortest = float(min(o2.cell.lengths()))
    if abs(mic - bond) > 1e-9 or shortest <= 2.0 * bond:
        raise ValueError(f"cell cannot hold an O2 molecule: shortest lattice vector {shortest:.4f} A, "
                         f"O-O {bond:.4f} A, minimum-image O-O {mic:.4f} A")
    return o2


# ----------------------------------------------------------------------------------------
# Records
# ----------------------------------------------------------------------------------------

def force_readout(atoms, fmax):
    """converged_by_force as the census driver derives it (adsorption.py:100-119): cached
    forces of the current state, constraint-adjusted, maximum norm < fmax."""
    record = dict(fmax_target_eV_A=float(fmax), max_constrained_force_eV_A=None,
                  converged_by_force=None, force_readout="unavailable")
    calc = atoms.calc
    if calc is None or "forces" not in getattr(calc, "results", {}):
        return record
    if calc.check_state(atoms):
        record["force_readout"] = "cache_not_current"
        return record
    forces = np.asarray(calc.results["forces"], dtype=float).copy()
    if forces.shape != (len(atoms), 3):
        record["force_readout"] = "invalid_shape"
        return record
    for constraint in atoms.constraints:
        constraint.adjust_forces(atoms, forces)
    if not np.isfinite(forces).all():
        record.update(converged_by_force=False, force_readout="nonfinite")
        return record
    maximum = float(np.linalg.norm(forces, axis=1).max()) if len(forces) else 0.0
    record.update(max_constrained_force_eV_A=maximum, converged_by_force=bool(maximum < fmax),
                  force_readout="cached")
    return record


def structure_record(atoms, fmax):
    """Geometry snapshot in the census's record layout plus the force readout."""
    fixed = sorted({int(i) for c in atoms.constraints if isinstance(c, FixAtoms) for i in c.get_indices()})
    record = dict(symbols=atoms.get_chemical_symbols(), positions_A=atoms.positions.tolist(),
                  cell_A=atoms.cell.array.tolist(), pbc=[bool(x) for x in atoms.pbc],
                  fixed_atom_indices=fixed,
                  other_constraint_types=[type(c).__name__ for c in atoms.constraints
                                          if not isinstance(c, FixAtoms)])
    record.update(force_readout(atoms, fmax))
    return record


def _nearest_metal(atoms, source, metals):
    d = np.asarray(atoms.get_distances(source, metals, mic=True), dtype=float)
    k = int(np.argmin(d))
    return int(metals[k]), float(d[k])


def fragment_geometry(atoms, n_slab, fragment_o, start_positions, clean_slab_record=None,
                      thresholds=integrity.DEFAULT_THRESHOLDS):
    """Audit geometry of a relaxed *O2 fragment: O-O distance and band, each O's nearest
    metal, the binding tier on the nearer O, the fragment's displacement from its start
    (the OOH geometry minus H), the free-slab-atom displacement from the start and, when the
    decoration's relaxed clean slab is given, from that slab (site_integrity.slab_displacement,
    the same per-atom bar as readout (b); reported, deciding nothing)."""
    symbols = atoms.get_chemical_symbols()
    metals = [i for i in range(n_slab) if symbols[i] in integrity.METALS]
    if not metals:
        raise ValueError("slab lacks metal atoms")
    contacts = {}
    for name, index in zip(("proximal_O", "distal_O"), fragment_o):
        m_index, m_o = _nearest_metal(atoms, index, metals)
        contacts[name] = dict(index=int(index), metal_index=m_index, metal=symbols[m_index], distance_A=m_o)
    binding_o = min(contacts, key=lambda name: contacts[name]["distance_A"])
    binding = contacts[binding_o]
    o_o = float(atoms.get_distance(fragment_o[0], fragment_o[1], mic=True))
    from ase.geometry import find_mic
    delta = atoms.positions - np.asarray(start_positions, dtype=float)
    _, lengths = find_mic(delta, atoms.cell, atoms.pbc)
    lengths = np.asarray(lengths, dtype=float)
    fixed = set(int(i) for c in atoms.constraints if isinstance(c, FixAtoms) for i in c.get_indices())
    free_slab = [i for i in range(n_slab) if i not in fixed]
    out = dict(
        o_o_A=o_o, o_o_class=integrity.o_o_class(o_o, thresholds),
        m_o_by_O_A={name: c["distance_A"] for name, c in contacts.items()},
        nearest_metal_by_O={name: dict(index=c["metal_index"], symbol=c["metal"]) for name, c in contacts.items()},
        binding_O=binding_o, min_m_o_A=binding["distance_A"],
        bond_tier=integrity.bond_tier(binding["distance_A"], thresholds),
        binding_metal=binding["metal"], binding_metal_index=binding["metal_index"],
        fragment_O_displacement_from_start_A={name: float(lengths[c["index"]]) for name, c in contacts.items()},
        free_slab_atom_max_displacement_from_start_A=float(lengths[free_slab].max()) if free_slab else 0.0,
        slab_displacement_from_clean=None, reconstruction_flag_from_clean=None,
    )
    if clean_slab_record is not None:
        clean = integrity.atoms_from_record(clean_slab_record)
        disp = integrity.slab_displacement(atoms, clean, n_slab, sorted(fixed))
        out["slab_displacement_from_clean"] = disp
        out["reconstruction_flag_from_clean"] = bool(disp["free_atom_max_A"] > thresholds.reconstruction_max_A)
    return out


def relax_fragment(state_record, calc, *, fmax=DEFAULT_FMAX, steps=DEFAULT_STEPS,
                   thresholds=integrity.DEFAULT_THRESHOLDS, clean_slab_record=None):
    """Relax the H-removed *O2 state with `calc` via hea_oer.relax.relax. Returns the full
    audit record: energy_eV, converged_by_force, the relaxed geometry, the start info and the
    fragment geometry summary."""
    atoms, info = build_fragment_atoms(state_record, thresholds)
    start_positions = atoms.positions.copy()
    t0 = time.monotonic()
    energy, relaxed = relax(atoms, calc, fmax=fmax, steps=steps)
    seconds = time.monotonic() - t0
    if not math.isfinite(energy):
        raise ValueError("nonfinite fragment energy")
    record = structure_record(relaxed, fmax)
    record.update(energy_eV=float(energy), steps_cap=int(steps), seconds=round(seconds, 6),
                  start=dict(info, positions_A=start_positions.tolist(),
                             source_OOH_energy_eV=state_record.get("energy_eV"),
                             source_OOH_converged_by_force=state_record.get("converged_by_force")),
                  geometry=fragment_geometry(relaxed, info["n_slab_atoms"], info["fragment_O_indices"],
                                             start_positions, clean_slab_record, thresholds))
    return record


def relax_o2(cell, calc, *, fmax=DEFAULT_FMAX, steps=DEFAULT_STEPS, label=None):
    """Relax the O2 molecule in `cell` with `calc`. Returns the audit record with energy_eV,
    converged_by_force, the relaxed geometry and the O-O distance before and after."""
    o2 = build_o2_atoms(cell)
    start_o_o = float(o2.get_distance(0, 1, mic=True))
    t0 = time.monotonic()
    energy, relaxed = relax(o2, calc, fmax=fmax, steps=steps)
    seconds = time.monotonic() - t0
    if not math.isfinite(energy):
        raise ValueError("nonfinite O2 energy")
    record = structure_record(relaxed, fmax)
    record.update(energy_eV=float(energy), steps_cap=int(steps), seconds=round(seconds, 6),
                  cell_id=cell_id(cell), label=label, o_o_start_A=start_o_o,
                  o_o_A=float(relaxed.get_distance(0, 1, mic=True)),
                  cell_lengths_A=[float(x) for x in relaxed.cell.lengths()])
    return record


# ----------------------------------------------------------------------------------------
# Per-composition run
# ----------------------------------------------------------------------------------------

def run_row(row, calc, *, fmax=DEFAULT_FMAX, steps=DEFAULT_STEPS, o2_cell="slab",
            thresholds=integrity.DEFAULT_THRESHOLDS, o2_cache=None, log=None):
    """CENSUS-1b on one screen-diagnostic-v1 row with an already-built calculator.

    Returns dict(records={key: readout record}, audit=dict(selection, o2_gas, fragments,
    n_sites, n_qualifying, seconds)). `o2_cache` ({cell_id: O2 record}) is shared across rows
    so each distinct cell (and the 12 A box) is relaxed once per calculator.
    """
    if o2_cell not in O2_CELL_CHOICES:
        raise ValueError("o2_cell must be one of " + ", ".join(O2_CELL_CHOICES))
    o2_cache = {} if o2_cache is None else o2_cache
    t0 = time.monotonic()
    selection = select_sites(row, thresholds)
    sites = {site_key(s["seed"], s["site_index"]): s for s in row.get("per_site_records", [])}
    clean_by_seed = {d.get("seed"): d.get("relaxed_slab") for d in row.get("decoration_records", [])}
    qualifying = [s for s in selection if s["qualifies"]]

    # One O2 relaxation per distinct cell of the qualifying states; when the composition has
    # no qualifying site its relaxed-slab cell is used so every composition carries the pair.
    cells = {}
    for s in qualifying:
        cell = sites[s["key"]]["relaxed_states"]["OOH"]["cell_A"]
        cells.setdefault(cell_id(cell), cell)
    if not cells:
        for d in row.get("decoration_records", []):
            slab = d.get("relaxed_slab") or {}
            if slab.get("cell_A") is not None:
                cells.setdefault(cell_id(slab["cell_A"]), slab["cell_A"])
                break
    box_cid = cell_id(box12_cell())
    for cid, cell in list(cells.items()) + [(box_cid, box12_cell().tolist())]:
        if cid not in o2_cache:
            label = "box12" if cid == box_cid else "slab_cell"
            if log:
                log(f"O2 relaxation in {label} cell {cid}")
            o2_cache[cid] = relax_o2(cell, calc, fmax=fmax, steps=steps, label=label)

    records, fragments, failed = {}, {}, []
    for s in qualifying:
        site = sites[s["key"]]
        state = site["relaxed_states"]["OOH"]
        if log:
            log(f"fragment relaxation {s['key']} ({s['initial_metal']}, OOH M-O {s['ooh']['m_o_A']:.4f} A)")
        try:
            frag = relax_fragment(state, calc, fmax=fmax, steps=steps, thresholds=thresholds,
                                  clean_slab_record=clean_by_seed.get(site["seed"]))
        except Exception as error:  # noqa: BLE001 - one site's failure must not lose the others
            failed.append(s["key"])
            fragments[s["key"]] = dict(status="failed", error=f"{type(error).__name__}: {error}",
                                       seed=site["seed"], site_index=site["site_index"],
                                       initial_metal=s["initial_metal"], site_eta_V=s["eta_V"],
                                       selection=s["ooh"])
            if log:
                log(f"fragment relaxation {s['key']} FAILED: {type(error).__name__}: {error}")
            continue
        cid = cell_id(state["cell_A"])
        slab_o2, box_o2 = o2_cache[cid], o2_cache[box_cid]
        chosen = slab_o2 if o2_cell == "slab" else box_o2
        both_converged = (frag["converged_by_force"] is True and chosen["converged_by_force"] is True)
        records[s["key"]] = dict(
            energy_eV=frag["energy_eV"], E_O2_gas_eV=chosen["energy_eV"],
            converged_by_force=both_converged,
            fragment_converged_by_force=frag["converged_by_force"],
            o2_gas_converged_by_force=chosen["converged_by_force"],
            E_O2_box12_eV=box_o2["energy_eV"], E_O2_slab_cell_eV=slab_o2["energy_eV"],
            o2_cell=o2_cell, o2_cell_id=cid if o2_cell == "slab" else box_cid)
        energies = site.get("energies_eV") or {}
        e_slab = energies.get("slab")
        no_zpe = {
            "slab_cell": (frag["energy_eV"] - e_slab - slab_o2["energy_eV"]) if e_slab is not None else None,
            "box12": (frag["energy_eV"] - e_slab - box_o2["energy_eV"]) if e_slab is not None else None}
        fragments[s["key"]] = dict(
            frag, status="relaxed", seed=site["seed"], site_index=site["site_index"],
            initial_metal=s["initial_metal"], site_eta_V=s["eta_V"], selection=s["ooh"],
            E_slab_eV=e_slab, E_O2Hb_eV=state.get("energy_eV"),
            o2_gas_converged_by_force={"slab_cell": slab_o2["converged_by_force"],
                                       "box12": box_o2["converged_by_force"]},
            # No ZPE-TS enters the readout record: the readout adds the Proposed 0.05 eV
            # (site_integrity.o2_fragment_diagnostic). The audit reports the diagnostic at
            # 0.00 / 0.05 / 0.10 eV beside it (docs/91:36), for both O2 cells; diagnostic only.
            E_frag_minus_slab_minus_O2_no_zpe_eV=no_zpe,
            dG_ads_O2_by_zpe_ts_eV={
                cell: (None if value is None else {f"{z:.2f}": value + z for z in ZPE_TS_REPORTED_EV})
                for cell, value in no_zpe.items()},
        )
    audit = dict(selection=selection, n_sites=len(selection), n_qualifying=len(qualifying),
                 qualifying_keys=[s["key"] for s in qualifying], n_failed=len(failed), failed_keys=failed,
                 o2_gas={"slab_cell": {cid: o2_cache[cid] for cid in cells}, "box12": o2_cache[box_cid]},
                 o2_cell=o2_cell, fragments=fragments, seconds=round(time.monotonic() - t0, 6))
    return dict(records=records, audit=audit)


def o2_cache_from_audits(composition_audits):
    """Rebuild the {cell_id: O2 record} cache from checkpointed composition audits (the
    `audit` dicts of run_row, or the composition blocks of the CLI's o2_audit.json), so a
    resumed process reuses the checkpointed O2 energies instead of relaxing them again."""
    cache = {}
    for comp in composition_audits:
        gas = (comp or {}).get("o2_gas") or {}
        for cid, record in (gas.get("slab_cell") or {}).items():
            cache.setdefault(cid, record)
        box = gas.get("box12")
        if box and box.get("cell_id"):
            cache.setdefault(box["cell_id"], box)
    return cache


def run_census(rows_by_formula, calculator_factory, *, protocol_by_formula=None,
               o2_cell="slab", thresholds=integrity.DEFAULT_THRESHOLDS, completed=None,
               on_composition=None, on_composition_start=None, o2_cache=None, log=None):
    """Run CENSUS-1b over {formula: row} with one calculator from `calculator_factory()`.

    `protocol_by_formula` maps formula -> dict(fmax_eV_A, steps) (the result's embedded
    manifest protocol); `completed` names formulas to skip; `on_composition_start(formula)`
    is called before and `on_composition(formula, result)` after each composition
    (checkpointing); `o2_cache` ({cell_id: O2 record}, see o2_cache_from_audits) seeds the
    shared O2 cache so a resumed run relaxes no O2 cell twice. Returns {formula: run_row result}.
    """
    calc = None
    o2_cache = {} if o2_cache is None else o2_cache
    out = {}
    for formula, row in rows_by_formula.items():
        if completed and formula in completed:
            continue
        if calc is None:
            calc = calculator_factory()
        if on_composition_start is not None:
            on_composition_start(formula)
        protocol = (protocol_by_formula or {}).get(formula) or {}
        result = run_row(row, calc, fmax=protocol.get("fmax_eV_A", DEFAULT_FMAX),
                         steps=protocol.get("steps", DEFAULT_STEPS), o2_cell=o2_cell,
                         thresholds=thresholds, o2_cache=o2_cache, log=log)
        out[formula] = result
        if on_composition is not None:
            on_composition(formula, result)
    return out
