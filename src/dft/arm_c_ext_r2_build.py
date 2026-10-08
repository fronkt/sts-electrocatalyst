"""Build round 2 of the S8 arm-C extension: round 1's eleven seeded SCFs, each now reading its seed's
density moved onto the target's atoms; launches nothing.

Decision of record: Frank, 2026-10-08, "repair". Round 1's canary (21181502) failed because QE read each
seed's density unchanged: the seed adsorbate's charge stayed where the target has no atom, and the
target's new atoms had none (docs/research/s8-arm-c-extension-2026-10-08.md, Canary readout).

Round 2 changes only the density a job reads. qe_density_move.py subtracts the seed's superposed atomic
charges and adds the target's (QE's charge extrapolation between ionic steps, extended to atoms that
appear or vanish), keeping the magnetization. Everything else is round 1's:
- the targets and seeds;
- the decks (production deck, own prefix, startingpot = 'file');
- the rebuilt occup.txt and paw.txt;
- the seeded runner and the canary gate.

The canary's SCF wall is longer, because QE starts a file density's first diagonalisation at ethr 1e-5
(738 s in round 1).

The moved densities (about 150 MB each) stay out of git. The spec pins their sha256, and staging uploads
them. They are rebuilt only when the seed densities are present locally (density_inputs/, fetched by
results/arm_c_ext_r2_2026-10-08/density_fetch.py); otherwise the density pins are taken from the spec on
disk and every other file is still rebuilt.

    python src/dft/arm_c_ext_r2_build.py            # write decks, seed files, densities, manifests, plan, spec
    python src/dft/arm_c_ext_r2_build.py --check    # rebuild and compare with the files on disk
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arm_c_build as cb  # noqa: E402
import arm_c_ext_build as r1  # noqa: E402
import hea_deck as hd  # noqa: E402
import qe_density_move as move  # noqa: E402

ROOT = HERE.parents[1]
DATE = "2026-10-08"
PACKAGE = "results/arm_c_ext_r2_" + DATE
RUN_ROOT = "hea/arm_c_ext_r2_" + DATE
CANARY_ROOT = RUN_ROOT + "/canary"
INPUTS = PACKAGE + "/density_inputs"
R1_SPEC = r1.PACKAGE + "/launch_spec.json"
R1_SNAPSHOT = r1.PACKAGE + "/status_snapshot_20261008T195838Z.json"  # canary FAILED, main CANCELLED
R1_JOBS = {"21181502_1": "FAILED", "21181502_2": "FAILED", "21181503_[1-11%11]": "CANCELLED"}
MANIFEST = {"r2_canary": "runs/m_arm_c_ext_r2_" + DATE + "_canary.txt",
            "r2_main": "runs/m_arm_c_ext_r2_" + DATE + "_main.txt"}
DESIGN = "docs/research/s8-arm-c-extension-2026-10-08.md"
DECISION = "Frank, 2026-10-08: \"repair\" (after the round-1 canary failed)"
JOB_SUFFIX = "__atomic_moved"
DENSITY = "charge-density.hdf5"
XML = "data-file-schema.xml"
LIMITS = {"r2_canary": {"max_iterations": 8, "scf_seconds": 2400, "projection_seconds": 600, "wall_minutes": 45},
          "r2_main": {"max_iterations": 200, "scf_seconds": 12600, "projection_seconds": 600, "wall_minutes": 225}}
POSITION_TOLERANCE = 1.0e-9   # fractional; seed deck vs the seed run's own XML


def species_files(deck_text: str) -> dict:
    block = deck_text.split("ATOMIC_SPECIES", 1)[1].split("CELL_PARAMETERS", 1)[0]
    return dict(re.findall(r"^\s+(\w+)\s+[0-9.]+\s+(\S+\.(?:UPF|upf))\s*$", block, re.M))


def r1_extension_su(root: Path) -> float:
    """CPU SU of round 1: its two canary tasks (the main array was cancelled before it ran)."""
    snapshot = json.loads((root / R1_SNAPSHOT).read_text(encoding="utf-8"))
    rows = [line.split("|") for line in snapshot["remote"]["commands"]["sacct"]["stdout"].strip().splitlines()]
    states = {r[0]: r[2].split()[0] for r in rows}
    if states != R1_JOBS:
        raise ValueError("round-1 accounting differs: " + json.dumps(states))
    return sum(int(r[5]) for r in rows) / 3600


def manifest_text(stage: str, jobs: list) -> str:
    head = ["# APPROVED 2026-10-08: " + DESIGN + " (Frank: \"repair\", after the round-1 canary failed)",
            "# S8 arm C extension, round 2 (" + stage + "): seeded fixed-geometry SCFs at the Cu8 and Fe25 support sites, "
            "seed density moved onto the target's atoms; exploratory; no automatic retries.",
            "# SUBMIT WITH EXCLUDE=" + hd.EXCLUDE,
            "# NP=128 NCONC=1"]
    return "\n".join(head + [f"{j['dir']} {j['job']} .in {j['nk']}" for j in jobs]) + "\n"


def moved_density(root: Path, row: dict, deck_text: str, fetched: dict, r1_spec: dict, cache: dict) -> tuple:
    """(file bytes, record) of the target's moved density; cache holds one seed's arrays and form factors."""
    seed = row["seed"]
    folder = root / INPUTS / seed["id"]
    for name in (DENSITY, XML):
        if cb.sha256((folder / name).read_bytes()) != fetched["sha256"][name]:
            raise ValueError("local seed file differs from its Anvil sha256: " + seed["id"] + "/" + name)
    seed_deck = (root / f"runs/{r1.PRODUCTION_ROOT}/{r1.site_name(row['site_dir'])}/{seed['state']}__atomic.in").read_text()
    files = species_files(deck_text)
    files.update(species_files(seed_deck))
    for name in files.values():
        if hashlib.md5((root / INPUTS / "pseudo" / name).read_bytes()).hexdigest() != r1_spec["pseudo_md5"][name]:
            raise ValueError("local pseudopotential differs from the launch pin: " + name)
    cell = move.read_xml_cell(folder / XML)
    seed_atoms = move.read_xml_atoms(folder / XML)
    seed_cell_a, seed_deck_atoms = r1.geometry(seed_deck)
    target_cell_a, target_deck_atoms = r1.geometry(deck_text)
    if not np.allclose(seed_cell_a, target_cell_a, rtol=0, atol=1e-12):
        raise ValueError("seed and target cells differ: " + row["site_dir"])
    deck_seed = move.fractional(seed_cell_a, seed_deck_atoms)
    if ([s for s, _ in deck_seed] != [s for s, _ in seed_atoms] or
            max(float(np.abs((p - q) - np.round(p - q)).max()) for (_, p), (_, q) in zip(deck_seed, seed_atoms)) > POSITION_TOLERANCE):
        raise ValueError("seed deck geometry differs from the seed run's XML: " + seed["id"])
    target_atoms = move.fractional(target_cell_a, target_deck_atoms)
    if cache.get("id") != seed["id"]:
        cache.clear()
        density = move.read_density(folder / DENSITY)
        cache.update(id=seed["id"], density=density, shells=move.shells(density["miller"], cell),
                     omega=abs(np.linalg.det(cell)), upfs={}, factors={},
                     g0=int(np.nonzero(~density["miller"].any(axis=1))[0][0]))
    for species, name in sorted(files.items()):
        if species not in cache["factors"]:
            q, index = cache["shells"]
            cache["upfs"][species] = move.read_upf(root / INPUTS / "pseudo" / name)
            cache["factors"][species] = move.form_factor(cache["upfs"][species], q)[index] / cache["omega"]
    density, omega, g0 = cache["density"], cache["omega"], cache["g0"]
    rho = move.moved_charge(density, seed_atoms, target_atoms, cache["factors"])
    electrons = sum(cache["upfs"][s]["z_valence"] for s, _ in target_atoms)
    data = move.moved_file_bytes(folder / DENSITY, rho)
    record = {"seed_density_sha256": fetched["sha256"][DENSITY], "sha256": cb.sha256(data), "bytes": len(data),
              "seed_electrons": round(float(density["rho"][g0].real * omega), 6),
              "electrons": round(float(rho[g0].real * omega), 6), "target_valence_electrons": electrons,
              "moment_carried_over": round(float(density["mag"][g0].real * omega), 6)}
    if abs(record["electrons"] - electrons) > 1e-3:
        raise ValueError("moved density does not integrate to the target's electron count: " + row["dir"])
    return data, record


def build(root: Path = ROOT, densities: bool = True, sink=None) -> dict:
    """Committed output path -> bytes. With densities, each moved density is rebuilt and handed to
    sink(path, bytes) (one at a time); without, the density pins come from the spec on disk."""
    readout_bytes = (root / r1.READOUT).read_bytes()
    readout = json.loads(readout_bytes)
    source_spec = json.loads((root / r1.SOURCE_SPEC).read_text(encoding="utf-8"))
    r1_spec = json.loads((root / R1_SPEC).read_text(encoding="utf-8"))
    fetch = json.loads((root / r1.FETCH).read_text(encoding="utf-8"))
    r1_jobs = {(j["dir"].rsplit("/", 1)[-1], j["job"]): j for j in r1_spec["stages"]["ext_main"]["jobs"]}
    recorded = None
    if not densities:  # the density records of the plan on disk (its spec pins the same sha256)
        on_disk = json.loads((root / PACKAGE / "ext_plan.json").read_text(encoding="utf-8"))
        recorded = {(r["dir"], r["job"]): r["density"] for r in on_disk["selection"]}
    files, main_jobs, plan_rows, cache = {}, [], [], {}
    for row in sorted(r1.targets(readout), key=lambda r: (r["seed"]["id"], r["state"])):
        site = r1.site_name(row["site_dir"])
        r1_job = r1_jobs[(site, row["job"])]
        production = r1_job["source_deck"]
        data = (root / production).read_bytes()
        if cb.sha256(data) != source_spec["files"][production]:
            raise ValueError("production deck differs from its launch pin: " + production)
        text = data.decode("utf-8")
        job_name = row["state"] + JOB_SUFFIX
        job_dir = f"{RUN_ROOT}/{site}"
        deck = r1.seeded_deck(text, job_name).encode("utf-8")
        seed = row["seed"]
        fetched = fetch["seeds"][seed["id"]]
        bundle = f"{PACKAGE}/seeds/{site}/{row['state']}"
        pins = dict(r1_job["scratch_source"]["files"])
        for name in ("occup.txt", "paw.txt"):  # round 1's rebuilt files, byte for byte
            payload = (root / r1_job["scratch_source"]["save_dir"] / name).read_bytes()
            if cb.sha256(payload) != pins[name]:
                raise ValueError("round-1 seed file differs from its pin: " + r1_job["scratch_source"]["save_dir"] + "/" + name)
            files[f"{bundle}/{name}"] = payload
        if densities:
            moved, record = moved_density(root, row, text, fetched, r1_spec, cache)
            if sink is not None:
                sink(f"{bundle}/{DENSITY}", moved)
            del moved
        else:
            record = recorded[(job_dir, job_name)]
        pins[DENSITY] = record["sha256"]
        files[f"runs/{job_dir}/{job_name}.in"] = deck
        main_jobs.append({"dir": job_dir, "job": job_name, "sha256": cb.sha256(deck), "nk": cb.NK,
                          **{k: LIMITS["r2_main"][k] for k in ("scf_seconds", "projection_seconds", "max_iterations")},
                          "recipe": "seeded", "role": "extension", "source_deck": production, "seed": r1_job["seed"],
                          "scratch_source": {"save_dir": bundle, "files": pins}})
        seed_roles, target_roles = r1.ROLES[seed["state"]], r1.ROLES[row["state"]]
        plan_row = {k: row[k] for k in ("site_dir", "formula", "state", "failure", "seed")}
        plan_row.update(dir=job_dir, job=job_name, round_1_job=r1_job["job"], seed_density="moved", bundle=bundle,
                        remote_copy={XML: fetched["save_dir"] + "/" + XML}, upload={DENSITY: f"{bundle}/{DENSITY}"},
                        atoms_removed=[r for r in seed_roles if r not in target_roles],
                        atoms_added=[r for r in target_roles if r not in seed_roles], density=record)
        plan_rows.append(plan_row)
    main_jobs.sort(key=lambda j: (j["dir"], j["job"]))
    plan_rows.sort(key=lambda r: (r["dir"], r["job"]))
    canary_jobs = []
    for site, state in r1.CANARY:
        job = next(j for j in main_jobs if j["dir"].endswith("/" + site) and j["job"] == state + JOB_SUFFIX)
        canary_dir = f"{CANARY_ROOT}/{site}"
        files[f"runs/{canary_dir}/{job['job']}.in"] = files[f"runs/{job['dir']}/{job['job']}.in"]
        canary_jobs.append(dict(job, dir=canary_dir, role="canary",
                                **{k: LIMITS["r2_canary"][k] for k in ("scf_seconds", "projection_seconds", "max_iterations")}))
    stages = {}
    for stage, jobs in (("r2_canary", canary_jobs), ("r2_main", main_jobs)):
        files[MANIFEST[stage]] = manifest_text(stage, jobs).encode("utf-8")
        stages[stage] = {"kind": "hea", "manifest": MANIFEST[stage], "concurrency": len(jobs),
                         "wall_minutes": LIMITS[stage]["wall_minutes"], "jobs": jobs}
    stage_pins = {path: cb.sha256(data) for path, data in files.items()}
    for relative in r1.RUNNER_FILES:
        stage_pins[relative] = cb.sha256((root / relative).read_bytes())
        if stage_pins[relative] != r1_spec["files"][relative]:
            raise ValueError("runner file changed since round 1: " + relative)
    spent = round(r1.spent_cpu_su(root) + r1_extension_su(root), 1)
    ceilings = {s: len(stages[s]["jobs"]) * LIMITS[s]["wall_minutes"] * 128 // 60 for s in stages}
    ceiling = sum(ceilings.values())
    campaign = source_spec["allocation"]["approved_campaign_ceiling_cpu_su"]
    if spent + ceiling > campaign:
        raise ValueError("round 2 does not fit the approved arm-C campaign ceiling")
    source_readout = {"path": r1.READOUT, "sha256": cb.sha256(readout_bytes)}
    spec = {
        "schema": "research-batch-2026-09-16",
        "np": 128,
        "exclusions": hd.EXCLUDE,
        "date": DATE,
        "design": DESIGN,
        "decision_ref": DECISION,
        "source_readout": source_readout,
        "allocation": {"account": "che260157", "partition": "wholenode", "cores_per_task": 128,
                       "approved_campaign_ceiling_cpu_su": campaign,
                       "spent_before_this_launch_cpu_su": spent,
                       "stage_ceilings_cpu_su": ceilings,
                       "this_launch_ceiling_cpu_su": ceiling},
        "qe_binaries_sha256": r1_spec["qe_binaries_sha256"],
        "files": dict(sorted(stage_pins.items())),
        "pseudo_md5": r1_spec["pseudo_md5"],
        "stages": stages,
    }
    plan = {"schema": "s8-arm-c-ext-plan-v1", "date": DATE, "design": DESIGN, "decision_ref": DECISION,
            "source_readout": source_readout, "round": 2,
            "round_1": {"spec": R1_SPEC, "spec_sha256": cb.sha256((root / R1_SPEC).read_bytes()),
                        "canary": "21181502 failed (design record, Canary readout)", "main": "21181503 cancelled, never ran"},
            "rule": ("round 1's targets, seeds, decks and rebuilt occup.txt/paw.txt; each seed's converged density moved "
                     "onto the target's atoms (seed atomic charges subtracted, target atomic charges added; magnetization "
                     "carried over) before QE reads it with startingpot = 'file'"),
            "density_move": {"module": "src/dft/qe_density_move.py",
                             "sha256": cb.sha256((root / "src/dft/qe_density_move.py").read_bytes()),
                             "validation": PACKAGE + "/density_validation.json"},
            "status": "exploratory; arm C's registered readings stay final",
            "selection": plan_rows,
            "canary": [{"site": s, "state": st, "dir": f"{CANARY_ROOT}/{s}", "job": st + JOB_SUFFIX} for s, st in r1.CANARY]}
    files[PACKAGE + "/ext_plan.json"] = (json.dumps(plan, indent=2) + "\n").encode("utf-8")
    files[PACKAGE + "/launch_spec.json"] = (json.dumps(spec, indent=2) + "\n").encode("utf-8")
    return files


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare a fresh build with the files on disk")
    args = parser.parse_args(argv)
    densities = (ROOT / INPUTS).is_dir()
    problems, written = [], []

    def place(relative: str, data: bytes) -> None:
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_bytes() != data:
                problems.append(relative)
        elif path.exists():
            if path.read_bytes() != data:
                raise ValueError("refusing to overwrite a differing file: " + relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "xb") as handle:
                handle.write(data)
            written.append(relative)

    files = build(densities=densities, sink=place)
    for relative, data in files.items():
        if b"\r" in data:
            raise ValueError("CR byte in " + relative)
        place(relative, data)
    print(json.dumps({"files": len(files), "densities_rebuilt": densities, "mismatches": problems,
                      "written": len(written), "spec_sha256": cb.sha256(files[PACKAGE + "/launch_spec.json"])}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
