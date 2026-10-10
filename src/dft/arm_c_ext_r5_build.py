"""Build round 5 of the S8 arm-C extension: a second start of the Fe25 s25/2 slab, from its own converged density,
with one atom's Hubbard occupations and PAW block taken from the site's converged OH state and the occupations held
for the first iterations; launches nothing.

Decision of record: Frank, 2026-10-10, "Just do the test since its so small", after round 4's readout. Round 4
completed the site, and Fe25's single-site value, 0.893 V, is set by step 1 (slab to OH). At Fe 22, 4.2 A from the
adsorbate, the slab's occupations lie 0.94 from the configuration the site's OH, OOH and O share, so that step
includes Fe 22's change (docs/research/s8-arm-c-extension-2026-10-08.md, Round 4 readout). This run asks whether the
slab holds Fe 22 in the adsorbed states' configuration at a lower energy.

The job is the production slab's deck with round 4's changes: its own prefix, startingpot = 'file', max_seconds
18400, mixing_ndim 16 and mixing_fixed_ns 5 (arm_c_ext_build.seeded_deck, arm_c_ext_r3_build.r3_deck and
arm_c_ext_r4_build.r4_deck, in turn). Everything that sets the energy (geometry, PBE+U, cutoffs, smearing,
conv_thr) stays the production deck's, as do mixing_beta 0.3 and electron_maxstep 300.

The start is the production slab's own save, which start_sources.json pins on Anvil against round 1's pins. Its
density and XML are copied on Anvil. Its occup.txt and paw.txt are rebuilt with atom 22's blocks (Fe 22, both spins)
replaced by the converged OH state's, as round 4 rebuilt them for the O (arm_c_ext_r4_build.occupations and .paw).

The plan row marks the run as a second start of an accepted state (second_start). The readout keeps the production
slab unless this run converges, after the held iterations, more than 1 meV lower (arm_c_readout.py).

    python src/dft/arm_c_ext_r5_build.py            # write the deck, occup.txt, paw.txt, manifest, plan, spec
    python src/dft/arm_c_ext_r5_build.py --check    # rebuild and compare with the files on disk
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arm_c_build as cb  # noqa: E402
import arm_c_ext_build as r1  # noqa: E402
import arm_c_ext_r2_build as r2  # noqa: E402
import arm_c_ext_r3_build as r3  # noqa: E402
import arm_c_ext_r4_build as r4  # noqa: E402
import hea_deck as hd  # noqa: E402

ROOT = HERE.parents[1]
DATE = "2026-10-10"
PACKAGE = "results/arm_c_ext_r5_" + DATE
RUN_ROOT = "hea/arm_c_ext_r5_" + DATE
R4_SPEC = r4.PACKAGE + "/launch_spec.json"
R4_PLAN = r4.PACKAGE + "/ext_plan.json"
R4_READOUT = r4.PACKAGE + "/readout.json"
R4_COLLECTION = r4.PACKAGE + "/terminal_collection.json"
R4_TASKS = 1  # the one round-4 task accounted by sacct
PRODUCTION_SPEC = r1.SOURCE_SPEC
START_SOURCES = PACKAGE + "/start_sources.json"
MANIFEST = {"r5_main": "runs/m_arm_c_ext_r5_" + DATE + "_main.txt"}
DESIGN = r2.DESIGN
DECISION = "Frank, 2026-10-10: \"Just do the test since its so small\" (after round 4's readout)"
TARGET = ("Fe25Co25Ni25Cr25__s25_site2", "slab")
FIRST_JOB = "slab__atomic"  # the accepted production slab
JOB_SUFFIX = r4.JOB_SUFFIX
ATOM = r4.ATOM  # Fe 22
SOURCE_STATE = r4.SOURCE_STATE  # OH
MIXING = dict(r4.MIXING)
QE_MAX_SECONDS = r4.QE_MAX_SECONDS
LIMITS = {"r5_main": dict(r4.LIMITS["r4_main"])}
REMOTE_FILES = r4.REMOTE_FILES  # copied on Anvil from the production slab's save


def target(readout: dict) -> dict:
    """The Fe25 s25/2 site after round 4: complete, with the production slab and a converged OH."""
    site = next(s for s in readout["sites"] if r1.site_name(s["dir"]) == TARGET[0])
    slab, source = site["states"][TARGET[1]], site["states"][SOURCE_STATE]
    if not site["complete"] or site["potential_limiting_step"] != 1:
        raise ValueError("Fe25 s25/2 must be complete, with step 1 limiting")
    if slab["job"] != FIRST_JOB or slab["recipe"] != "production" or not slab["accepted"] or not source["accepted"]:
        raise ValueError("the slab must be production's accepted run, with OH converged")
    return slab


def r5_deck(text: str, job: str) -> str:
    """The production deck with round 4's changes: round 2's, round 3's, then round 4's edits."""
    return r4.r4_deck(r3.r3_deck(r1.seeded_deck(text, job), job), job)


def r4_cpu_su(root: Path) -> float:
    """CPU SU of round 4: the sacct CPU time of its task (terminal_collection.json)."""
    collection = json.loads((root / R4_COLLECTION).read_text(encoding="utf-8"))
    rows = [line.split("|") for line in collection["sacct"].strip().splitlines()]
    seconds = [int(r[7]) for r in rows if "." not in r[0]]
    if len(seconds) != R4_TASKS:
        raise ValueError(f"expected {R4_TASKS} accounted round-4 task, found {len(seconds)}")
    return sum(seconds) / 3600


def manifest_text(stage: str, jobs: list) -> str:
    head = ["# APPROVED 2026-10-10: " + DESIGN + " (Frank: \"Just do the test since its so small\")",
            "# S8 arm C extension, round 5 (" + stage + "): a second start of the Fe25 s25/2 slab from its own converged "
            "density, Fe 22's occupations and PAW block from the converged OH state, the occupations held for 5 "
            "iterations (mixing_fixed_ns), up to 300 iterations; exploratory; no automatic retries.",
            "# SUBMIT WITH EXCLUDE=" + hd.EXCLUDE,
            "# NP=128 NCONC=1"]
    return "\n".join(head + [f"{j['dir']} {j['job']} .in {j['nk']}" for j in jobs]) + "\n"


def build(root: Path = ROOT) -> dict:
    """Committed output path -> bytes; nothing is written here."""
    readout_bytes = (root / R4_READOUT).read_bytes()
    readout = json.loads(readout_bytes)
    r4_spec_bytes = (root / R4_SPEC).read_bytes()
    r4_spec = json.loads(r4_spec_bytes)
    production = json.loads((root / PRODUCTION_SPEC).read_text(encoding="utf-8"))
    pins = json.loads((root / START_SOURCES).read_text(encoding="utf-8"))
    oh_pins = json.loads((root / r4.START_SOURCES).read_text(encoding="utf-8"))
    site_occupations = json.loads((root / r4.R3_SITE_OCCUPATIONS).read_text(encoding="utf-8"))
    if not QE_MAX_SECONDS < LIMITS["r5_main"]["scf_seconds"]:
        raise ValueError("QE must stop itself before the runner's SCF wall")
    if not MIXING["mixing_fixed_ns"] < LIMITS["r5_main"]["max_iterations"]:
        raise ValueError("the occupations must be released before the iteration ceiling")
    first = target(readout)
    site, state = TARGET
    old = next(j for stage in production["stages"].values() for j in stage["jobs"]
               if r1.site_name(j["dir"]) == site and j["job"] == FIRST_JOB)
    source_deck = f"runs/{old['dir']}/{FIRST_JOB}.in"
    old_deck = (root / source_deck).read_bytes()
    if cb.sha256(old_deck) != old["sha256"]:
        raise ValueError("production slab deck differs from its pin: " + source_deck)
    save = f"/anvil/projects/x-che260157/sts_arm_c_{cb.DATE}/runs/{old['dir']}/tmp_{FIRST_JOB}/{FIRST_JOB}.save"
    if pins["save"] != save or not pins["all_match"] or set(pins["files"]) != {*REMOTE_FILES, "occup.txt", "paw.txt"}:
        raise ValueError("the production slab's save pins do not match")
    by_state = {f["state"]: f for f in site_occupations["files"] if f["site"] == site}
    start_file, source = by_state[state], by_state[SOURCE_STATE]
    if start_file["job"] != FIRST_JOB or not site_occupations["all_match"]:
        raise ValueError("expected the mirrored, sha-matched occupations of the production slab")
    start = (root / r3.PACKAGE / start_file["local"]).read_bytes()
    source_bytes = (root / r3.PACKAGE / source["local"]).read_bytes()
    if cb.sha256(start) != pins["files"]["occup.txt"]["sha256"] or cb.sha256(start) != start_file["sha256"]:
        raise ValueError("the slab's mirrored occupations are not its saved ones")
    if cb.sha256(source_bytes) != source["sha256"]:
        raise ValueError("the OH occupations differ from their mirror receipt")
    slab_paw = (root / pins["fetched"]["slab_paw.txt"]["local"]).read_bytes()
    oh_paw = (root / oh_pins["fetched"]["oh_paw.txt"]["local"]).read_bytes()
    if (cb.sha256(slab_paw) != pins["files"]["paw.txt"]["sha256"]
            or cb.sha256(oh_paw) != oh_pins["fetched"]["oh_paw.txt"]["sha256"]):
        raise ValueError("a mirrored PAW file differs from its receipt")
    _, atoms = r1.geometry(old_deck.decode("utf-8"))
    if len(atoms) != r1.nat_of(state) or atoms[ATOM - 1][0] != "Fe":
        raise ValueError("atom 22 is not the slab's Fe")
    occup = r4.occupations(start, source_bytes, r1.nat_of(state))
    paw_text = r4.paw(slab_paw, oh_paw, r1.nat_of(state), r1.nat_of(SOURCE_STATE))
    name = state + JOB_SUFFIX
    job_dir = f"{RUN_ROOT}/{site}"
    deck = r5_deck(old_deck.decode("utf-8"), name).encode("utf-8")
    bundle = f"{PACKAGE}/seeds/{site}/{state}"
    files = {f"runs/{job_dir}/{name}.in": deck, f"{bundle}/occup.txt": occup, f"{bundle}/paw.txt": paw_text}
    scratch = {f: pins["files"][f]["sha256"] for f in REMOTE_FILES}
    scratch.update({"occup.txt": cb.sha256(occup), "paw.txt": cb.sha256(paw_text)})
    job = {"dir": job_dir, "job": name, "sha256": cb.sha256(deck), "nk": old["nk"],
           **{k: LIMITS["r5_main"][k] for k in ("scf_seconds", "projection_seconds", "max_iterations")},
           "recipe": "seeded", "role": "extension", "source_deck": source_deck,
           "seed": {"state": state, "job": FIRST_JOB, "recipe": "production", "save_dir": save},
           "scratch_source": {"save_dir": bundle, "files": dict(sorted(scratch.items()))}}
    row = {"site_dir": old["dir"], "formula": site.split("__")[0], "state": state, "second_start": True,
           "first": {"job": FIRST_JOB, "recipe": first["recipe"], "E_eV": first["E_eV"],
                     "total_magnetization": first["total_magnetization"]},
           "seed": {"state": state, "job": FIRST_JOB, "recipe": "production", "root": r1.PRODUCTION_ROOT,
                    "id": f"{site}__{FIRST_JOB}"},
           "dir": job_dir, "job": name, "round": 5, "seed_density": "own_converged", "bundle": bundle,
           "remote_copy": {f: save + "/" + f for f in REMOTE_FILES}, "mixing": dict(MIXING),
           "occupations": {"start": f"{r3.PACKAGE}/{start_file['local']}", "start_sha256": cb.sha256(start),
                           "atoms_replaced": [ATOM],
                           "from": {"state": SOURCE_STATE, "job": source["job"], "recipe": source["recipe"],
                                    "path": f"{r3.PACKAGE}/{source['local']}", "sha256": source["sha256"]},
                           "sha256": cb.sha256(occup)},
           "paw": {"start": pins["fetched"]["slab_paw.txt"]["local"], "start_sha256": cb.sha256(slab_paw),
                   "atoms_replaced": [ATOM],
                   "from": {"state": SOURCE_STATE, "job": source["job"], "path": oh_pins["fetched"]["oh_paw.txt"]["local"],
                            "remote": oh_pins["fetched"]["oh_paw.txt"]["remote"], "sha256": cb.sha256(oh_paw)},
                   "sha256": cb.sha256(paw_text)},
           "density": {"source": save + "/" + r2.DENSITY, "sha256": pins["files"][r2.DENSITY]["sha256"],
                       "bytes": pins["files"][r2.DENSITY]["bytes"]}}
    stages = {"r5_main": {"kind": "hea", "manifest": MANIFEST["r5_main"], "concurrency": 1,
                          "wall_minutes": LIMITS["r5_main"]["wall_minutes"], "jobs": [job]}}
    files[MANIFEST["r5_main"]] = manifest_text("r5_main", [job]).encode("utf-8")
    stage_pins = {path: cb.sha256(data) for path, data in files.items()}
    for relative in r1.RUNNER_FILES:
        stage_pins[relative] = cb.sha256((root / relative).read_bytes())
        if stage_pins[relative] != r4_spec["files"][relative]:
            raise ValueError("runner file changed since round 4: " + relative)
    spent = round(r4_spec["allocation"]["spent_before_this_launch_cpu_su"] + r4_cpu_su(root), 1)
    ceilings = {s: len(stages[s]["jobs"]) * LIMITS[s]["wall_minutes"] * 128 // 60 for s in stages}
    ceiling = sum(ceilings.values())
    campaign = r4_spec["allocation"]["approved_campaign_ceiling_cpu_su"]
    if spent + ceiling > campaign:
        raise ValueError("round 5 does not fit the approved arm-C campaign ceiling")
    source_readout = {"path": R4_READOUT, "sha256": cb.sha256(readout_bytes)}
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
        "qe_binaries_sha256": r4_spec["qe_binaries_sha256"],
        "files": dict(sorted(stage_pins.items())),
        "pseudo_md5": r4_spec["pseudo_md5"],
        "stages": stages,
    }
    plan = {"schema": "s8-arm-c-ext-plan-v1", "date": DATE, "design": DESIGN, "decision_ref": DECISION,
            "source_readout": source_readout, "round": 5,
            "round_4": {"spec": R4_SPEC, "spec_sha256": cb.sha256(r4_spec_bytes), "plan": R4_PLAN,
                        "main": "21224301 read out: the Fe25 s25/2 O converged; Fe25 0.893 V single-site, set by step 1, "
                                "which includes Fe 22's change between the slab and the adsorbed states"},
            "rule": ("a second start of the Fe25 s25/2 slab: the production slab's deck with round 4's changes "
                     "(mixing_ndim 16, mixing_fixed_ns 5, max_seconds 18400, startingpot 'file'), from its own converged "
                     "save (density and XML copied on Anvil; occup.txt and paw.txt rebuilt) with Fe 22's Hubbard "
                     "occupations and PAW block (both spins) from the converged OH state; it replaces the production "
                     "slab only if it converges after the held iterations more than 1 meV lower"),
            "mixing": dict(MIXING), "qe_max_seconds": QE_MAX_SECONDS,
            "status": "exploratory; arm C's registered readings stay final",
            "selection": [row]}
    files[PACKAGE + "/ext_plan.json"] = (json.dumps(plan, indent=2) + "\n").encode("utf-8")
    files[PACKAGE + "/launch_spec.json"] = (json.dumps(spec, indent=2) + "\n").encode("utf-8")
    return files


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare a fresh build with the files on disk")
    args = parser.parse_args(argv)
    files = build()
    problems, written = [], []
    for relative, data in files.items():
        if b"\r" in data:
            raise ValueError("CR byte in " + relative)
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
    print(json.dumps({"files": len(files), "mismatches": problems, "written": len(written),
                      "spec_sha256": cb.sha256(files[PACKAGE + "/launch_spec.json"])}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
