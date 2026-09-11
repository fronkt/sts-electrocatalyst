"""Independent fixed-geometry readout of the eight historical-winner SCFs.

This is a targeted audit, not selection of a new best composition. Molecular
references enable electronic adsorption energies only; no relaxed free energy,
overpotential, calibrated uncertainty or catalytic ranking is asserted here.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import hea_force_audit as force
import hea_followup_qc as qc
import hea_geometry as geometry
import hea_numerical_readout as numerical
import hea_winner_guard as guard
import qe_qc
from hea_oer.referencing import reference_energy

STATES = ("slab", "OH", "O", "OOH")


def input_geometry(text):
    """Read explicit angstrom coordinates and Cartesian masks for SCF or relax."""
    clean = "\n".join(line.split("!", 1)[0] for line in text.splitlines())
    counts = re.findall(r"\bnat\s*=\s*(\d+)\b", clean, re.I)
    blocks = re.findall(r"(?im)^ATOMIC_POSITIONS\s+angstrom\s*\n", clean)
    if len(counts) != 1 or len(blocks) != 1:
        raise ValueError("one atom count and explicit angstrom coordinate card required")
    start = re.search(r"(?im)^ATOMIC_POSITIONS\s+angstrom\s*\n", clean).end()
    rows = [line.split() for line in clean[start:].splitlines() if line.strip()][:int(counts[0])]
    if len(rows) != int(counts[0]) or not rows:
        raise ValueError("incomplete atom coordinates")
    labels, positions, masks = [], [], []
    for row in rows:
        if len(row) not in (4, 7) or not re.fullmatch(r"[A-Z][a-z]?\d*", row[0]):
            raise ValueError("invalid atom row")
        xyz = [force.number(x) for x in row[1:4]]
        mask = row[4:] or ["1", "1", "1"]
        if any(x not in ("0", "1") for x in mask):
            raise ValueError("invalid Cartesian mask")
        labels.append(row[0]); positions.append(xyz); masks.append([int(x) for x in mask])
    return labels, positions, masks


def printed_potentials(text):
    blocks = re.split(r"PseudoPot\.\s*#\s*\d+\s+for\s+([A-Za-z][A-Za-z0-9]*)\s+read from file:", text)
    found = {}
    for species, body in zip(blocks[1::2], blocks[2::2]):
        matches = re.findall(r"MD5 check sum:\s*([0-9a-fA-F]{32})", body)
        if len(matches) != 1 or species in found:
            raise ValueError("ambiguous printed pseudopotential identity")
        found[species] = matches[0].lower()
    if not found:
        raise ValueError("missing printed pseudopotential identities")
    return found


def electronic_chains(energies, gas):
    """Reference-subtracted electronic energies; shared gas terms cancel in delta."""
    if set(energies) != {"atomic", "ortho"} or set(gas) != {"H2", "H2O"}:
        raise ValueError("exact projector and molecular-reference sets required")
    for row in energies.values():
        if set(row) != set(STATES):
            raise ValueError("complete slab/OH/O/OOH chain required")
    if not all(type(v) in (int, float) and math.isfinite(v)
               for v in list(gas.values()) + [v for row in energies.values() for v in row.values()]):
        raise ValueError("finite real energies required")
    chains = {p: {s: row[s] - row["slab"] - reference_energy(s, gas["H2O"], gas["H2"])
                  for s in STATES[1:]} for p, row in energies.items()}
    delta = {s: (energies["ortho"][s] - energies["ortho"]["slab"])
                   - (energies["atomic"][s] - energies["atomic"]["slab"])
             for s in STATES[1:]}
    return dict(electronic_adsorption_eV=chains,
                projector_delta_ortho_minus_atomic_eV=delta,
                gas_references_shared=True, vibrational_or_entropy_corrections_added=False,
                relaxed_free_energies=False, overpotential=None, ranking_validated=False)


def verify_pair_geometry(left, right):
    if left["geometry_signature"] != right["geometry_signature"]:
        raise ValueError("projectors do not share exact coordinates, species, masks and cell")


def gas_reference(root, molecule, expected_potentials):
    directory = root / "runs/Cr_slab"
    inp, out = directory / (molecule + ".in"), directory / (molecule + ".out")
    text = out.read_text(encoding="utf-8")
    audit = qe_qc.scan(str(out), str(inp))
    if (audit["verdict"] != "TRUSTWORTHY" or not audit["bfgs_converged"]
            or qc.FAILURES.search(text) or audit["reasons"]
            or audit["n_scf_ok"] != audit["n_energies"]):
        raise ValueError("molecular reference fails converged-relaxation checks: " + molecule)
    if audit["fmax_free_ry_au"] is None or audit["fmax_free_ry_au"] > 0.002:
        raise ValueError("molecular reference exceeds its force threshold")
    if not math.isfinite(audit["energy_ev"]):
        raise ValueError("nonfinite molecular energy")
    labels, _, masks = input_geometry(inp.read_text(encoding="utf-8"))
    expected_atoms = ["H", "H"] if molecule == "H2" else ["H", "H", "O"]
    if sorted(labels) != expected_atoms or not all(all(m) for m in masks):
        raise ValueError("unexpected molecule or constraints")
    potentials = printed_potentials(text)
    if set(potentials) != set(expected_atoms) or any(expected_potentials.get(k) != v for k, v in potentials.items()):
        raise ValueError("molecular/slab pseudopotential mismatch")
    for label, value in (("kinetic-energy cutoff", 80), ("charge density cutoff", 640)):
        values = re.findall(re.escape(label) + r"\s*=\s*([\d.]+)\s+Ry", text)
        if len(values) != 1 or float(values[0]) != value:
            raise ValueError("molecular cutoff mismatch")
    functional = re.findall(r"Exchange-correlation\s*=\s*([^\n]+)", text)
    if len(functional) != 1 or functional[0].strip() not in ("PBE", "SLA  PW   PBX  PBC"):
        raise ValueError("unsupported molecular functional")
    return dict(status="COMPATIBLE_EXISTING_REFERENCE", energy_eV=audit["energy_ev"],
                qc=audit, printed_potential_md5=potentials,
                files={"input": numerical.evidence(inp), "output": numerical.evidence(out)},
                limitations=["Original molecular protocol; no new cell/force-convergence study.",
                             "Molecules carry no metal Hubbard correction; common H/O references are used for both projector branches."])


def build_readout(root, spec_path):
    root = Path(root).resolve(strict=True)
    spec_path = Path(spec_path)
    spec = guard.validate_batch(spec_path, root / "runs", fresh=False)["spec"]
    endpoints, potentials, energies = [], {}, {p: {} for p in ("atomic", "ortho")}
    for index, job in enumerate(spec["jobs"], 1):
        guard.verify_runtime(spec_path, root / "runs", index)
        folder = root / "runs" / job["dir"]
        prepared = guard.runtime_bytes((root / "runs" / job["source"]).read_bytes(), job["job"]).decode()
        endpoint = numerical.accepted_endpoint(folder, job["job"], prepared)
        if endpoint["status"] != "ACCEPTED":
            raise ValueError(job["job"] + ": " + "; ".join(endpoint["reasons"]))
        text = (folder / (job["job"] + ".out")).read_text(encoding="utf-8")
        printed = printed_potentials(text)
        for label, value in printed.items():
            if label in potentials and potentials[label] != value:
                raise ValueError("pseudopotential changes within winner chain")
            potentials[label] = value
        symbols, positions, masks = input_geometry(prepared)
        match = re.search(r"(?m)^CELL_PARAMETERS\s+angstrom\s*\n((?:[^\n]+\n){3})", prepared)
        if match is None:
            raise ValueError("explicit angstrom cell required")
        cell = [[float(x) for x in line.split()] for line in match[1].splitlines()]
        signature = dict(species=symbols, positions_A=positions, if_pos=masks, cell_A=cell)
        symbols = [re.match(r"[A-Z][a-z]?", s)[0] for s in symbols]
        endpoint.update(state=job["state"], projector=job["projector"],
                        geometry=geometry.analyse(symbols, positions, cell),
                        geometry_signature=signature,
                        printed_potential_md5=printed)
        energies[job["projector"]][job["state"]] = endpoint["audit"]["scf"]["energy_eV"]
        endpoints.append(endpoint)
    refs = {m: gas_reference(root, m, potentials) for m in ("H2", "H2O")}
    pairs = []
    for state in STATES:
        pair = [e for e in endpoints if e["state"] == state]
        verify_pair_geometry(*pair)
        pairs.append(dict(state=state, **numerical.endpoint_difference(*pair)))
    return dict(schema="hea-winner-readout-v1", status="ACCEPTED_FIXED_GEOMETRY_AUDIT",
                spec=numerical.evidence(spec_path), endpoints=endpoints, projector_pairs=pairs,
                gas_references=refs,
                electronic_chains=electronic_chains(energies, {m: r["energy_eV"] for m, r in refs.items()}),
                limitations=["Historical selected site, not a new best-candidate selection or held-out validation.",
                             "Large residual forces: no relaxed thermodynamics, catalytic ranking or overpotential claim.",
                             "Projector comparisons change the Hubbard subspace; lower absolute energy does not select the physically better projector.",
                             "Printed occupations and moments do not establish a magnetic ground state.",
                             "The census remains the basis for candidate-focused expansion priorities."])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=HERE.parents[1])
    ap.add_argument("--spec", type=Path, default=Path("results/hea_winner_2026-09-10/launch_spec.json"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.out.exists():
        ap.error("refusing to overwrite existing readout")
    spec = args.spec if args.spec.is_absolute() else args.root / args.spec
    result = build_readout(args.root, spec)
    with args.out.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps(dict(status=result["status"], endpoints=len(result["endpoints"]),
                         electronic_chains=result["electronic_chains"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
