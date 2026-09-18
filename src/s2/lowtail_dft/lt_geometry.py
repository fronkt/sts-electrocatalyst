"""Periodic geometry for the Cr-site reconstruction question on orthogonal slab cells.

Every cell used here is checked orthogonal with c along +z before component-wise
minimum-image arithmetic (the same precondition the endpoint audit states). The surface
normal is +z, pointing from the fixed bottom layers toward the adsorbate side; a negative
normal force on the site metal pushes it back toward the slab.
"""
from __future__ import annotations

import numpy as np

ORTHO_TOL_A = 1e-9


def cell_lengths(cell) -> np.ndarray:
    cell = np.asarray(cell, dtype=float)
    if cell.shape != (3, 3):
        raise ValueError("cell must be 3x3")
    off = cell - np.diag(np.diag(cell))
    if np.max(np.abs(off)) > ORTHO_TOL_A:
        raise ValueError("cell is not orthogonal within 1e-9 A")
    lengths = np.diag(cell).copy()
    if np.any(lengths <= 0):
        raise ValueError("cell diagonal must be positive")
    return lengths


def mic(vector, cell) -> np.ndarray:
    lengths = cell_lengths(cell)
    v = np.asarray(vector, dtype=float)
    return v - lengths * np.round(v / lengths)


def vector(positions, i: int, j: int, cell) -> np.ndarray:
    """Minimum-image vector from atom i to atom j."""
    p = np.asarray(positions, dtype=float)
    return mic(p[j] - p[i], cell)


def distance(positions, i: int, j: int, cell) -> float:
    return float(np.linalg.norm(vector(positions, i, j, cell)))


NORMAL = np.array([0.0, 0.0, 1.0])


def nearest(symbols, positions, index: int, cell, *, want=lambda s: s != "O", exclude=()) -> tuple[int, float]:
    best = None
    for j, s in enumerate(symbols):
        if j == index or j in exclude or not want(s):
            continue
        d = distance(positions, index, j, cell)
        if best is None or d < best[1]:
            best = (j, d)
    if best is None:
        raise ValueError("no candidate atom")
    return best


def axial_oxygen(symbols, clean_positions, site: int, cell, n_slab: int, cutoff_A: float = 2.4) -> dict:
    """Lattice O bonded to the site metal from BELOW in the clean slab (most negative z offset)."""
    candidates = []
    for j in range(n_slab):
        if symbols[j] != "O":
            continue
        v = vector(clean_positions, site, j, cell)
        d = float(np.linalg.norm(v))
        if d <= cutoff_A:
            candidates.append((v[2] / d, d, j))
    if not candidates:
        raise ValueError("no lattice O within the cutoff of the site metal")
    cos_z, d, j = min(candidates)
    return dict(index=j, clean_distance_A=d, cos_to_normal=cos_z)


def site_geometry(symbols, positions, cell, site: int, ads_o: int, clean_positions, axial_index: int) -> dict:
    """Site metal lift and bonds for one state against the same decoration's clean slab."""
    p = np.asarray(positions, dtype=float)
    c = np.asarray(clean_positions, dtype=float)
    disp = mic(p[site] - c[site], cell)
    return dict(
        site_lift_z_A=float(disp[2]),
        site_displacement_A=float(np.linalg.norm(disp)),
        site_to_adsO_A=distance(p, site, ads_o, cell),
        site_to_axialO_A=distance(p, site, axial_index, cell),
        site_to_axialO_clean_A=distance(c, site, axial_index, cell),
        adsO_height_above_site_A=float(vector(p, site, ads_o, cell)[2]),
    )


def pair_forces(forces, positions, cell, site: int, ads_o: int) -> dict:
    """Normal and bond projections of the forces on the site metal and the appended O.

    bond unit u points from the site metal to the O. ``bond_stretch`` = (F_O - F_M).u is
    positive when the forces act to lengthen the M-O contact, negative to shorten it.
    ``pair_normal`` = (F_O + F_M).z is the net outward force on the two-atom unit.
    """
    f = np.asarray(forces, dtype=float)
    u = vector(positions, site, ads_o, cell)
    u = u / np.linalg.norm(u)
    fm, fo = f[site], f[ads_o]
    return dict(
        site_force_eV_A=fm.tolist(), adsO_force_eV_A=fo.tolist(),
        site_normal_eV_A=float(fm @ NORMAL), adsO_normal_eV_A=float(fo @ NORMAL),
        site_along_bond_eV_A=float(fm @ u), adsO_along_bond_eV_A=float(fo @ u),
        bond_stretch_eV_A=float((fo - fm) @ u), pair_normal_eV_A=float((fo + fm) @ NORMAL),
        site_normal_direction=("toward slab" if fm[2] < 0 else "away from slab" if fm[2] > 0 else "zero"),
    )


def axial_forces(forces, positions, cell, site: int, axial: int) -> dict:
    """Forces on the site metal / axial lattice O pair; ``axial_stretch`` > 0 lengthens M-O(axial)."""
    f = np.asarray(forces, dtype=float)
    u = vector(positions, site, axial, cell)
    u = u / np.linalg.norm(u)
    return dict(site_normal_eV_A=float(f[site] @ NORMAL), axial_O_normal_eV_A=float(f[axial] @ NORMAL),
                axial_O_force_eV_A=f[axial].tolist(), axial_stretch_eV_A=float((f[axial] - f[site]) @ u))


def atomic_mass(symbol: str) -> float:
    """Standard atomic mass (amu) from ase.data, the table the census calculators use."""
    from ase.data import atomic_masses, atomic_numbers
    return float(atomic_masses[atomic_numbers[symbol]])


def axial_decomposition(forces, positions, symbols, cell, site: int, axial: int, ads_o: int | None = None) -> dict:
    """The site-metal / axial-O contact read as two bodies instead of one two-atom difference.

    u points from the site metal to the axial lattice O. The "unit" is the site metal plus, when
    present, the appended O bonded to it (H atoms are not included). ``axial_stretch`` of
    axial_forces equals site_away_from_axial - axial_O_toward_site, so a large Cr=O compression
    force on the metal can make it positive while the axial O itself is pushed toward the metal.

    * axial_O_toward_site = -F_axial . u   (> 0: axial O pushed toward the site metal)
    * site_away_from_axial = -F_site . u   (> 0: site metal alone pushed away from the axial O)
    * unit_toward_axial   = F_unit . u     (> 0: site unit pushed toward the axial O)
    * relative_acceleration = F_axial.u / m_axial - F_unit.u / m_unit, eV/(A amu); < 0 means the
      mass-weighted axial gap closes at first order, > 0 that it opens.
    """
    f = np.asarray(forces, dtype=float)
    u = vector(positions, site, axial, cell)
    u = u / np.linalg.norm(u)
    members = [site] + ([ads_o] if ads_o is not None else [])
    f_unit = f[members].sum(axis=0)
    m_unit = sum(atomic_mass(symbols[i]) for i in members)
    m_axial = atomic_mass(symbols[axial])
    rel = float(f[axial] @ u) / m_axial - float(f_unit @ u) / m_unit
    return dict(u_z=float(u[2]), unit_members=members, unit_mass_amu=m_unit, axial_O_mass_amu=m_axial,
                axial_O_toward_site_eV_A=float(-(f[axial] @ u)), site_away_from_axial_eV_A=float(-(f[site] @ u)),
                unit_toward_axial_eV_A=float(f_unit @ u), relative_acceleration_eV_A_amu=rel,
                gap_first_order=("closing" if rel < 0 else "opening" if rel > 0 else "zero"))


def force_agreement(f_dft, f_mace, if_pos) -> dict:
    """DFT-vs-MACE force agreement over free Cartesian components (fixed components excluded)."""
    a = np.asarray(f_dft, dtype=float)
    b = np.asarray(f_mace, dtype=float)
    mask = np.asarray(if_pos, dtype=bool)
    if a.shape != b.shape or a.shape != mask.shape:
        raise ValueError("force arrays and mask must share shape")
    da, db = a[mask], b[mask]
    diff = da - db
    free_atoms = mask.any(axis=1)
    per_atom = np.linalg.norm((a - b) * mask, axis=1)[free_atoms]
    return dict(
        n_free_components=int(mask.sum()), n_free_atoms=int(free_atoms.sum()),
        component_mae_eV_A=float(np.mean(np.abs(diff))),
        component_rmse_eV_A=float(np.sqrt(np.mean(diff ** 2))),
        max_atom_vector_difference_eV_A=float(per_atom.max()),
        dft_free_component_mean_abs_eV_A=float(np.mean(np.abs(da))),
        mace_free_component_mean_abs_eV_A=float(np.mean(np.abs(db))),
    )


def basin(site_lift_z_A: float, site_to_axialO_A: float, site_to_adsO_A: float,
          adsO_nearest_metal_is_site: bool, thresholds: dict) -> str:
    """Operating-decision basin label for a relaxed *O state (see operating_decisions.json)."""
    if not adsO_nearest_metal_is_site or site_to_adsO_A >= thresholds["desorbed_min_A"]:
        return "O_OFF_SITE"
    lifted = site_lift_z_A >= thresholds["lift_min_A"]
    broken = site_to_axialO_A >= thresholds["axial_break_A"]
    if lifted and broken:
        return "RECONSTRUCTED"
    if not lifted and not broken:
        return "UNRECONSTRUCTED"
    return "MIXED_UNASSIGNED"
