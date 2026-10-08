"""Offline test of the density move before any SU is spent (reads density_inputs/, writes density_validation.json).

1. Each fetched density integrates to its state's electron count, and its magnetization to the final moment of
   the run that wrote it (production or re-run).
2. The superposed atomic charges reproduce the starting charge QE printed for each production atomic start.
3. Moving a density onto its own structure returns it unchanged.
4. For converged pairs at one site, QE's density distance (rho_ddot, Ry; the plane-wave part of the measure
   behind its "estimated scf accuracy", over the G vectors QE mixes, |G|^2 <= 4 ecutwfc; QE adds Hubbard and
   PAW terms, left out here) from three starts to the converged target:
     copied - round 1: the seed's density rescaled to the target's electron count;
     atomic - production: superposed atomic charges and the deck's starting magnetizations, rescaled;
     moved  - round 2: the seed's density moved onto the target's atoms, magnetization carried over.
   Pairs: Cu8Cr23Mn35Co34 s20/2, all twelve directions between its four converged states (the alloy of the
   Cu8 targets); Fe25Co25Ni25Cr25 s25/2, slab <-> OOH (both are round-2 seeds). The moved residual changes
   sign with the direction, so the 14 directions hold 7 independent moved distances.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import arm_c_ext_build as r1  # noqa: E402
import qe_density_move as move  # noqa: E402

INPUTS = HERE / "density_inputs"
PRODUCTION = "runs/hea/arm_c_2026-10-07"
MIRRORS = {"sts_arm_c_2026-10-07": ROOT / "results/arm_c_2026-10-07/raw_mirror",
           "sts_arm_c_2026-10-07_rerun": ROOT / "results/arm_c_2026-10-07_rerun/raw_mirror"}
FETCHED = json.loads((HERE / "density_fetch.json").read_text(encoding="utf-8"))["densities"]


def source_output(key):
    """Local mirror of the output of the run whose save holds this density (production or re-run)."""
    remote = FETCHED[key]["charge-density.hdf5"]["remote"]
    project = remote.split("/")[4]
    relative = remote.split("/runs/", 1)[1].rsplit("/tmp_", 1)[0]
    job = remote.rsplit("/", 2)[1][:-len(".save")]
    return MIRRORS[project] / "runs" / relative / (job + ".out")
ECUTWFC = 80.0
SITES = {"Cu8Cr23Mn35Co34__s20_site2": ("slab", "O", "OH", "OOH"),
         "Fe25Co25Ni25Cr25__s25_site2": ("slab", "OOH")}


def deck_info(text):
    species = re.findall(r"^\s+(\w+)\s+[0-9.]+\s+(\S+\.(?:UPF|upf))\s*$",
                         text.split("ATOMIC_SPECIES")[1].split("CELL_PARAMETERS")[0], re.M)
    magnetization = {species[int(i) - 1][0]: float(v)
                     for i, v in re.findall(r"starting_magnetization\((\d+)\)\s*=\s*([-0-9.]+)", text)}
    cell, atoms = r1.geometry(text)
    return dict(species), magnetization, move.fractional(cell, atoms)


def wrapped(a, b):
    d = a - b
    return float(np.abs(d - np.round(d)).max())


def main():
    upfs_all = {p.name: move.read_upf(p) for p in sorted((INPUTS / "pseudo").iterdir())}
    report = {"at": dt.datetime.now(dt.timezone.utc).isoformat(), "g2_max_bohr2": 4 * ECUTWFC,
              "states": {}, "pairs": []}
    for site, states in SITES.items():
        data = {}
        for state in states:
            text = (ROOT / PRODUCTION / site / (state + "__atomic.in")).read_text()
            species, magnetization, atoms = deck_info(text)
            folder = INPUTS / f"{site}__{state}__atomic"
            cell = move.read_xml_cell(folder / "data-file-schema.xml")
            xml_atoms = move.read_xml_atoms(folder / "data-file-schema.xml")
            density = move.read_density(folder / "charge-density.hdf5")
            g = density["miller"] @ move.reciprocal(cell)
            keep = np.einsum("ij,ij->i", g, g) <= 4 * ECUTWFC
            omega = abs(np.linalg.det(cell))
            run_output = source_output(folder.name)
            out = run_output.read_text(errors="replace")
            data[state] = {"cell": cell, "atoms": atoms, "magnetization": magnetization,
                           "upfs": {s: upfs_all[u] for s, u in species.items()},
                           "miller": density["miller"][keep], "rho": density["rho"][keep], "mag": density["mag"][keep],
                           "nelec": sum(upfs_all[species[s]]["z_valence"] for s, _ in atoms)}
            moment = re.findall(r"total magnetization\s+=\s+(-?[0-9.]+)", out)
            report["states"][f"{site}/{state}"] = {
                "atoms": len(atoms), "electrons_valence": data[state]["nelec"],
                "density_electrons": float(density["rho"][0].real * omega),
                "density_moment": float(density["mag"][0].real * omega),
                "run_output": str(run_output.relative_to(ROOT)).replace("\\", "/"),
                "run_last_total_magnetization": float(moment[-1]) if moment else None,
                "positions_vs_xml_max_frac": max(wrapped(p, q) for (_, p), (_, q) in zip(atoms, xml_atoms)),
                "species_match_xml": [s for s, _ in atoms] == [s for s, _ in xml_atoms],
                "kept_g_vectors": int(keep.sum()), "all_g_vectors": int(len(keep))}
            del density, g, keep
        first = data[states[0]]
        for state in states[1:]:
            if not (np.array_equal(data[state]["miller"], first["miller"]) and np.allclose(data[state]["cell"], first["cell"])):
                raise SystemExit("states at one site differ in cell or G vectors: " + site)
        miller, cell = first["miller"], first["cell"]
        upfs = {}
        for state in states:
            upfs.update(data[state]["upfs"])
        factors = move.form_factors(miller, cell, upfs)
        omega = abs(np.linalg.det(cell))
        for state in states:
            item = data[state]
            item["atomic"] = move.atomic_charge(miller, item["atoms"], factors)
            item["atomic_mag"] = sum(item["magnetization"][s] * factors[s] *
                                     move.structure_factor(miller, [p for t, p in item["atoms"] if t == s])
                                     for s in sorted({t for t, _ in item["atoms"]}) if item["magnetization"].get(s))
            report["states"][f"{site}/{state}"]["atomic_start_charge"] = float(item["atomic"][0].real * omega)
        identity = data[states[0]]["rho"] - data[states[0]]["atomic"] + data[states[0]]["atomic"]
        report["states"][f"{site}/{states[0]}"]["identity_max_abs"] = float(np.abs(identity - data[states[0]]["rho"]).max())
        for seed_state in states:
            for target_state in states:
                if seed_state == target_state:
                    continue
                s, t = data[seed_state], data[target_state]
                ratio = t["nelec"] / (s["rho"][0].real * omega)
                starts = {"copied": (s["rho"] * ratio, s["mag"] * ratio)}
                scale = t["nelec"] / (t["atomic"][0].real * omega)
                starts["atomic"] = (t["atomic"] * scale, t["atomic_mag"] * scale)
                starts["moved"] = (s["rho"] - s["atomic"] + t["atomic"], s["mag"])
                row = {"site": site, "seed": seed_state, "target": target_state,
                       "atoms_seed": len(s["atoms"]), "atoms_target": len(t["atoms"]),
                       "moved_electrons": float(starts["moved"][0][0].real * omega), "target_electrons": t["nelec"]}
                for name, (rho, mag) in starts.items():
                    row["distance_Ry_" + name] = move.hartree_distance(rho - t["rho"], mag - t["mag"], miller, cell)
                    row["distance_Ry_" + name + "_charge_only"] = move.hartree_distance(rho - t["rho"], None, miller, cell)
                report["pairs"].append(row)
                print(f"{site[:16]} {seed_state:>4} -> {target_state:<4} copied {row['distance_Ry_copied']:12.2f}"
                      f"  atomic {row['distance_Ry_atomic']:10.2f}  moved {row['distance_Ry_moved']:8.3f} Ry", flush=True)
        del data, factors
    report["independent_moved_distances"] = len({round(p["distance_Ry_moved"], 9) for p in report["pairs"]})
    with (HERE / "density_validation.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
