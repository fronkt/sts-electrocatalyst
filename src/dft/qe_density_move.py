"""Move a converged Quantum ESPRESSO charge density onto a related structure, to seed its SCF.

QE extrapolates the charge between ionic steps (pot_extrapolation = 'atomic', PW/src/update_pot.f90) by
subtracting the superposed atomic charges at the old positions and adding them at the new ones. The same
formula moves a converged density onto a neighbouring structure, including atoms that appear or vanish:

    rho(G) = rho_seed(G) - sum_{i in seed} f_s(i)(|G|) exp(-i G.tau_i) / Omega
                         + sum_{j in target} f_s(j)(|G|) exp(-i G.tau_j) / Omega

f_s(q) is QE's atomic charge form factor (atomic_rho_g): the UPF PP_RHOATOM (4 pi r^2 times the atomic
valence density) times sin(qr)/(qr), integrated with QE's Simpson rule over QE's msh points (the first
mesh point beyond r = 10 bohr, rounded down to an odd count; read_pseudo.f90). QE 7.5 tabulates this
integral at dq = 0.01 bohr^-1 and interpolates it (rhoat_mod.f90); here it is integrated directly. The
moved density integrates to the target's valence charge.

The magnetization density is carried over unchanged. QE's own extrapolation keeps zeta = m / (rho + rho_core)
fixed instead (update_pot.f90). Here atoms are added in vacuum, where zeta is a ratio of two vanishing
densities, so the added charge would take an arbitrary polarisation; carried over, it starts unpolarised.

Charge-density files use QE's HDF5 layout (io_base.f90, write_rhog): the file attributes gamma_only,
ngm_g and nspin; MillerIndices (ngm, 3); rhotot_g and, for nspin = 2, rhodiff_g (the magnetization),
each as interleaved real/imaginary float64, normalised so that rho(G=0) * Omega is the electron count.
A moved file is the seed file's bytes with only the values of rhotot_g replaced.
"""
from __future__ import annotations

import re
from pathlib import Path

import h5py
import numpy as np

R_CUT = 10.0      # bohr, QE's msh cutoff for atomic radial integrals (read_pseudo.f90)
E2 = 2.0          # e^2 in Rydberg atomic units


def numbers(text: str) -> np.ndarray:
    return np.array([float(t.replace("D", "E").replace("d", "e")) for t in text.split()])


def _block(text: str, tag: str) -> str:
    match = re.search(r"<%s(?:\s[^>]*)?>(.*?)</%s>" % (tag, tag), text, re.S)
    if match is None:
        raise ValueError("UPF block missing: " + tag)
    return match.group(1)


def read_upf(path) -> dict:
    """Radial mesh, its integration weights, PP_RHOATOM and the valence charge of a UPF (v1 or v2)."""
    text = Path(path).read_text(errors="replace")
    r, rab, rho = numbers(_block(text, "PP_R")), numbers(_block(text, "PP_RAB")), numbers(_block(text, "PP_RHOATOM"))
    match = (re.search(r'z_valence\s*=\s*"\s*([-+0-9.EeDd]+)\s*"', text)
             or re.search(r"([-+0-9.EeDd]+)\s+Z valence", text))
    if match is None or not len(r) == len(rab) == len(rho):
        raise ValueError("unreadable UPF: " + str(path))
    return {"r": r, "rab": rab, "rho_atom": rho, "z_valence": float(match.group(1).replace("D", "E").replace("d", "e"))}


def msh(r: np.ndarray) -> int:
    """QE's msh: the first (1-based) mesh point beyond R_CUT, rounded down to odd."""
    beyond = np.nonzero(r > R_CUT)[0]
    n = int(beyond[0]) + 1 if len(beyond) else len(r)
    return 2 * ((n + 1) // 2) - 1


def simpson_weights(n: int) -> np.ndarray:
    """QE's simpson(): 1, 4, 2, 4, ..., 4, 1 over an odd number of points, divided by 3."""
    if n % 2 == 0:
        raise ValueError("simpson needs an odd number of points")
    w = np.ones(n)
    w[1:-1:2], w[2:-1:2] = 4.0, 2.0
    return w / 3.0


def form_factor(upf: dict, q: np.ndarray, chunk: int = 2048) -> np.ndarray:
    """f(q) = int_0^{r(msh)} rho_at(r) sin(qr)/(qr) dr for q in bohr^-1 (q = 0 gives the integrated charge)."""
    n = msh(upf["r"])
    r = upf["r"][:n]
    weighted = upf["rho_atom"][:n] * upf["rab"][:n] * simpson_weights(n)
    q = np.asarray(q, dtype=float)
    out = np.empty(len(q))
    for start in range(0, len(q), chunk):
        x = np.outer(q[start:start + chunk], r)
        with np.errstate(invalid="ignore", divide="ignore"):
            j0 = np.where(x > 0.0, np.sin(x) / np.where(x > 0.0, x, 1.0), 1.0)
        j0[:, r < 1.0e-8] = 1.0
        out[start:start + chunk] = j0 @ weighted
    return out


def read_xml_cell(path) -> np.ndarray:
    """Cell vectors (rows, bohr) from a QE data-file-schema.xml."""
    text = Path(path).read_text()
    return np.array([numbers(re.search(r"<%s>(.*?)</%s>" % (a, a), text).group(1)) for a in ("a1", "a2", "a3")])


def read_xml_atoms(path) -> list:
    """[(species, fractional position)] of the structure in a QE data-file-schema.xml."""
    text = Path(path).read_text()
    cell = read_xml_cell(path)
    block = re.search(r"<atomic_positions>(.*?)</atomic_positions>", text, re.S).group(1)
    atoms = re.findall(r'<atom name="([^"]+)" index="\d+">([^<]*)</atom>', block)
    return [(name, numbers(xyz) @ np.linalg.inv(cell)) for name, xyz in atoms]


def fractional(cell_angstrom, atoms) -> list:
    """Deck atoms [(species, (x, y, z) angstrom)] as [(species, fractional position)]."""
    inverse = np.linalg.inv(np.array(cell_angstrom, dtype=float))
    return [(species, np.array(position, dtype=float) @ inverse) for species, position in atoms]


def read_density(path) -> dict:
    with h5py.File(path, "r") as f:
        if f.attrs["gamma_only"].strip() != b".FALSE.":
            raise ValueError("gamma_only densities are not handled")
        data = {"nspin": int(f.attrs["nspin"]), "miller": f["MillerIndices"][()]}
        data["rho"] = f["rhotot_g"][()].view(np.complex128)
        data["mag"] = f["rhodiff_g"][()].view(np.complex128) if data["nspin"] == 2 else None
    if len(data["rho"]) != len(data["miller"]):
        raise ValueError("density and Miller index counts differ")
    return data


def reciprocal(cell_bohr) -> np.ndarray:
    """Reciprocal vectors (rows, bohr^-1, with the 2 pi)."""
    return 2.0 * np.pi * np.linalg.inv(np.asarray(cell_bohr, dtype=float)).T


def shells(miller: np.ndarray, cell_bohr) -> tuple:
    """|G| of each distinct shell (bohr^-1) and each G vector's shell index."""
    g = miller @ reciprocal(cell_bohr)
    g2 = np.einsum("ij,ij->i", g, g)
    unique, index = np.unique(np.round(g2, 10), return_inverse=True)
    return np.sqrt(unique), index


def structure_factor(miller: np.ndarray, positions) -> np.ndarray:
    """sum over the given fractional positions of exp(-2 pi i m . f), via separable phase tables."""
    lo = miller.min(axis=0)
    span = miller.max(axis=0) - lo + 1
    m = (miller - lo).T
    total = np.zeros(len(miller), dtype=np.complex128)
    for f in positions:
        tables = [np.exp(-2j * np.pi * f[k] * (np.arange(span[k]) + lo[k])) for k in range(3)]
        total += tables[0][m[0]] * tables[1][m[1]] * tables[2][m[2]]
    return total


def form_factors(miller, cell_bohr, upfs: dict) -> dict:
    """species -> f_s(|G|) / Omega for every G vector of the Miller list."""
    q, index = shells(miller, cell_bohr)
    omega = abs(np.linalg.det(np.asarray(cell_bohr, dtype=float)))
    return {species: form_factor(upf, q)[index] / omega for species, upf in sorted(upfs.items())}


def atomic_charge(miller, atoms, factors: dict) -> np.ndarray:
    """Superposed atomic charges rho_at(G) (QE's normalisation) of [(species, fractional position)]."""
    out = np.zeros(len(miller), dtype=np.complex128)
    for species in sorted({s for s, _ in atoms}):
        out += factors[species] * structure_factor(miller, [p for s, p in atoms if s == species])
    return out


def moved_charge(seed: dict, seed_atoms, target_atoms, factors: dict) -> np.ndarray:
    """rho_seed - atomic charges at the seed's atoms + atomic charges at the target's atoms."""
    return (seed["rho"] - atomic_charge(seed["miller"], seed_atoms, factors)
            + atomic_charge(seed["miller"], target_atoms, factors))


def moved_file_bytes(seed_path, rho: np.ndarray) -> bytes:
    """The seed file's bytes with the stored rhotot_g values replaced by rho; every other byte is the seed's.

    rhotot_g is a contiguous, unfiltered little-endian float64 dataset, so its values occupy one byte range
    of the file; nothing else (layout, attributes, MillerIndices, rhodiff_g) changes."""
    with h5py.File(seed_path, "r") as f:
        stored = f["rhotot_g"]
        if (stored.chunks is not None or stored.compression is not None or stored.dtype != np.dtype("<f8")
                or stored.shape != (2 * len(rho),)):
            raise ValueError("rhotot_g is not a contiguous little-endian float64 array of this size")
        offset, size = stored.id.get_offset(), stored.id.get_storage_size()
    payload = np.ascontiguousarray(rho, dtype=np.complex128).view("<f8").tobytes()
    data = bytearray(Path(seed_path).read_bytes())
    if offset is None or size != len(payload) or offset + size > len(data):
        raise ValueError("rhotot_g storage does not match its shape")
    data[offset:offset + size] = payload
    return bytes(data)


def hartree_distance(d_rho, d_mag, miller, cell_bohr, g2_max=None) -> float:
    """QE's rho_ddot of a density difference with itself (Ry): Hartree term over G != 0 plus the
    magnetization term with a 1 bohr screening length; g2_max (bohr^-2) limits the sum like QE's ngms."""
    g = miller @ reciprocal(cell_bohr)
    g2 = np.einsum("ij,ij->i", g, g)
    keep = np.ones(len(g2), dtype=bool) if g2_max is None else g2 <= g2_max
    nonzero = keep & (g2 > 1.0e-12)
    omega = abs(np.linalg.det(np.asarray(cell_bohr, dtype=float)))
    value = E2 * 4.0 * np.pi * np.sum(np.abs(d_rho[nonzero]) ** 2 / g2[nonzero])
    if d_mag is not None:
        value += E2 * 4.0 * np.pi / (2.0 * np.pi) ** 2 * np.sum(np.abs(d_mag[keep]) ** 2)
    return float(value * omega * 0.5)
