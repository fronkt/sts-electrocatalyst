"""Build round 4 of the S8 arm-C extension: one more run of the Fe25 s25/2 O state, from round 3's stopped
density, with one atom's Hubbard occupations and PAW block taken from the site's converged OH state and the
occupations held for the first iterations; launches nothing.

Decision of record: Frank, 2026-10-10, "Do the Fe25 O run", after round 3's readout. Neither the Cu8 s16/2 slab
nor the Fe25 s25/2 O converged in 300 iterations, and the occupation check set each run's last occupations against
every converged state at its site (docs/research/s8-arm-c-extension-2026-10-08.md, Round 3 readout). At Fe 22 the
stalled Fe25 O sat 0.77 from the slab's occupations and 0.90 from those the converged OH and OOH share.

The job is round 3's Fe25 O job with two deck lines changed:
- its own prefix;
- an added mixing_fixed_ns = 5 after mixing_ndim. QE holds the Hubbard occupations at their starting values for
  the first 5 iterations, so the density settles around them before they may move.
Everything else stays round 3's: mixing_beta 0.3, mixing_ndim 16, electron_maxstep 300 (the runner's ceiling)
and max_seconds 18400 (QE stops itself before the runner's 19,000 s wall).

The start is the save round 3's run wrote when QE stopped it at iteration 300. Its density and XML are copied on
Anvil, pinned by start_sources.json. Its occup.txt and paw.txt are rebuilt with atom 22's blocks (Fe 22, both
spins: the Hubbard occupations and the PAW on-site block) replaced by the converged OH state's (round 2's run,
whose files start_sources.py and round 3's site_occupations.py mirrored); every other atom keeps round 3's last
values, as round 1 rebuilt both files for each seeded state.

While QE holds the occupations it resets them to their input before mixing, so its convergence test then ignores
them (QE 7.5, electrons_scf). A convergence within the first 5 iterations is therefore not accepted
(arm_c_readout.py, HELD). start_check.py confirms, minutes after the job starts, that QE printed the starting
occupations as built and is holding them.

    python src/dft/arm_c_ext_r4_build.py            # write the deck, occup.txt, paw.txt, manifest, plan, spec
    python src/dft/arm_c_ext_r4_build.py --check    # rebuild and compare with the files on disk
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
import hea_deck as hd  # noqa: E402

ROOT = HERE.parents[1]
DATE = "2026-10-10"
PACKAGE = "results/arm_c_ext_r4_" + DATE
RUN_ROOT = "hea/arm_c_ext_r4_" + DATE
R3_SPEC = r3.PACKAGE + "/launch_spec.json"
R3_PLAN = r3.PACKAGE + "/ext_plan.json"
R3_READOUT = r3.PACKAGE + "/readout.json"
R3_COLLECTION = r3.PACKAGE + "/terminal_collection.json"
R3_SITE_OCCUPATIONS = r3.PACKAGE + "/site_occupations.json"
R3_REMOTE = "/anvil/projects/x-che260157/sts_arm_c_ext_r3_2026-10-09"
R3_TASKS = 2  # the two round-3 tasks accounted by sacct
START_SOURCES = PACKAGE + "/start_sources.json"
MANIFEST = {"r4_main": "runs/m_arm_c_ext_r4_" + DATE + "_main.txt"}
DESIGN = r2.DESIGN
DECISION = "Frank, 2026-10-10: \"Do the Fe25 O run\" (after round 3's readout)"
TARGET = ("Fe25Co25Ni25Cr25__s25_site2", "O")
JOB_SUFFIX = "__atomic_fe22oh_fixns5"
ATOM = 22  # Fe 22, numbered as QE prints it
SOURCE_STATE = "OH"  # the converged state whose Fe 22 occupations and PAW block start the run
FIXED_NS = 5
MIXING = dict(r3.MIXING, mixing_fixed_ns=FIXED_NS)
QE_MAX_SECONDS = r3.QE_MAX_SECONDS
LIMITS = {"r4_main": dict(r3.LIMITS["r3_main"])}
REMOTE_FILES = (r2.DENSITY, r2.XML)  # copied on Anvil from round 3's save
ROUND_3_LINES = {"  mixing_beta = ": "  mixing_beta = 0.3", "  mixing_ndim = ": "  mixing_ndim = 16",
                 "  max_seconds = ": "  max_seconds = 18400", "  electron_maxstep = ": "  electron_maxstep = 300",
                 "  startingpot = ": "  startingpot = 'file'"}


def target(readout: dict) -> dict:
    """Round 3's attempt at the Fe25 s25/2 O: the site's only missing state, stopped by QE with its density written."""
    site = next(s for s in readout["sites"] if r1.site_name(s["dir"]) == TARGET[0])
    missing = [s for s in ("slab", "OH", "O", "OOH") if not site["states"][s]["accepted"]]
    if missing != [TARGET[1]] or not site["states"][SOURCE_STATE]["accepted"]:
        raise ValueError("Fe25 s25/2 must miss exactly its O state, with OH converged: " + repr(missing))
    attempts = [a for a in site["extension_attempts"] if a.get("round") == 3]
    if (len(attempts) != 1 or attempts[0]["state"] != TARGET[1] or attempts[0]["failure"] != "CEILING"
            or attempts[0]["qe_stop"] != "iterations" or not attempts[0]["config_written"]):
        raise ValueError("round 3's Fe25 O attempt is not a QE stop with its density written")
    return attempts[0]


def r4_deck(text: str, job: str) -> str:
    """Round 3's deck with its own prefix and mixing_fixed_ns added after mixing_ndim."""
    lines = text.split("\n")

    def one(start):
        hits = [i for i, line in enumerate(lines) if line.startswith(start)]
        if len(hits) != 1:
            raise ValueError("deck line not unique: " + start.strip())
        return hits[0]

    if any(line.lstrip().startswith("mixing_fixed_ns") for line in lines):
        raise ValueError("round-3 deck already sets mixing_fixed_ns")
    for start, expected in ROUND_3_LINES.items():
        if lines[one(start)] != expected:
            raise ValueError("unexpected round-3 deck line: " + lines[one(start)])
    lines[one("  prefix = '")] = f"  prefix = '{job}'"
    lines.insert(one("  mixing_ndim = ") + 1, f"  mixing_fixed_ns = {FIXED_NS}")
    return "\n".join(lines)


def occupations(start: bytes, source: bytes, nat: int) -> bytes:
    """Round 3's last occupations with atom ATOM's block (both spins) taken from the source state's."""
    ns, other = r1.numbers(start.decode("ascii")), r1.numbers(source.decode("ascii"))
    if len(ns) != nat * r1.NS_BLOCK or len(other) % r1.NS_BLOCK or len(other) < r1.SLAB_ATOMS * r1.NS_BLOCK:
        raise ValueError("occupation sizes do not match the atom counts")
    lo, hi = (ATOM - 1) * r1.NS_BLOCK, ATOM * r1.NS_BLOCK
    if not any(other[lo:hi]) or other[lo:hi] == ns[lo:hi]:
        raise ValueError("the source block is empty or already in place")
    return r1.render(ns[:lo] + other[lo:hi] + ns[hi:])


def paw(start: bytes, source: bytes, nat: int, nat_source: int) -> bytes:
    """Round 3's last becsum(171, nat, nspin=2) with atom ATOM's block in each spin taken from the source state's."""
    bec, other = r1.numbers(start.decode("ascii")), r1.numbers(source.decode("ascii"))
    if len(bec) != r1.BEC_BLOCK * nat * 2 or len(other) != r1.BEC_BLOCK * nat_source * 2:
        raise ValueError("PAW sizes do not match the atom counts")
    for spin in range(2):
        lo, src = r1.BEC_BLOCK * (spin * nat + ATOM - 1), r1.BEC_BLOCK * (spin * nat_source + ATOM - 1)
        block = other[src:src + r1.BEC_BLOCK]
        if not any(block) or block == bec[lo:lo + r1.BEC_BLOCK]:
            raise ValueError("the source PAW block is empty or already in place")
        bec[lo:lo + r1.BEC_BLOCK] = block
    return r1.render(bec)


def r3_cpu_su(root: Path) -> float:
    """CPU SU of round 3: the sacct CPU time of its two tasks (terminal_collection.json)."""
    collection = json.loads((root / R3_COLLECTION).read_text(encoding="utf-8"))
    rows = [line.split("|") for line in collection["sacct"].strip().splitlines()]
    seconds = [int(r[7]) for r in rows if "." not in r[0]]
    if len(seconds) != R3_TASKS:
        raise ValueError(f"expected {R3_TASKS} accounted round-3 tasks, found {len(seconds)}")
    return sum(seconds) / 3600


def manifest_text(stage: str, jobs: list) -> str:
    head = ["# APPROVED 2026-10-10: " + DESIGN + " (Frank: \"Do the Fe25 O run\")",
            "# S8 arm C extension, round 4 (" + stage + "): the Fe25 s25/2 O from round 3's stopped density, Fe 22's "
            "occupations and PAW block from the converged OH state, the occupations held for 5 iterations "
            "(mixing_fixed_ns), up to 300 iterations; exploratory; no automatic retries.",
            "# SUBMIT WITH EXCLUDE=" + hd.EXCLUDE,
            "# NP=128 NCONC=1"]
    return "\n".join(head + [f"{j['dir']} {j['job']} .in {j['nk']}" for j in jobs]) + "\n"


def build(root: Path = ROOT) -> dict:
    """Committed output path -> bytes; nothing is written here."""
    readout_bytes = (root / R3_READOUT).read_bytes()
    readout = json.loads(readout_bytes)
    r3_spec_bytes = (root / R3_SPEC).read_bytes()
    r3_spec = json.loads(r3_spec_bytes)
    r3_plan = json.loads((root / R3_PLAN).read_text(encoding="utf-8"))
    pins = json.loads((root / START_SOURCES).read_text(encoding="utf-8"))
    site_occupations = json.loads((root / R3_SITE_OCCUPATIONS).read_text(encoding="utf-8"))
    if not QE_MAX_SECONDS < LIMITS["r4_main"]["scf_seconds"]:
        raise ValueError("QE must stop itself before the runner's SCF wall")
    if not FIXED_NS < LIMITS["r4_main"]["max_iterations"]:
        raise ValueError("the occupations must be released before the iteration ceiling")
    attempt = target(readout)
    site, state = TARGET
    old_name = state + r3.JOB_SUFFIX
    old = next(j for j in r3_spec["stages"]["r3_main"]["jobs"] if r1.site_name(j["dir"]) == site and j["job"] == old_name)
    old_row = next(r for r in r3_plan["selection"] if r1.site_name(r["dir"]) == site and r["job"] == old_name)
    if attempt["job"] != old_name:
        raise ValueError("round 3's attempt is not the planned job")
    source_deck = f"runs/{old['dir']}/{old_name}.in"
    old_deck = (root / source_deck).read_bytes()
    if cb.sha256(old_deck) != old["sha256"]:
        raise ValueError("round-3 deck differs from its pin: " + source_deck)
    # round 3's stopped save: pinned on Anvil; its occup.txt is round 3's committed mirror of it
    save = f"{R3_REMOTE}/runs/{old['dir']}/tmp_{old_name}/{old_name}.save"
    mirror = f"{r3.PACKAGE}/raw_mirror/runs/{old['dir']}/tmp_{old_name}/{old_name}.save/occup.txt"
    start = (root / mirror).read_bytes()
    if (pins["save"] != save or set(pins["files"]) != {*REMOTE_FILES, "occup.txt", "paw.txt"} or not pins["all_match"]
            or not pins["occup_matches_mirror"] or pins["files"]["occup.txt"]["sha256"] != cb.sha256(start)):
        raise ValueError("round 3's save pins do not match its mirrored occupations")
    fetched = {name: (root / f["local"]).read_bytes() for name, f in pins["fetched"].items()}
    if any(cb.sha256(data) != pins["fetched"][name]["sha256"] for name, data in fetched.items()):
        raise ValueError("a mirrored start source differs from its receipt")
    if cb.sha256(fetched["r3_stop_paw.txt"]) != pins["files"]["paw.txt"]["sha256"]:
        raise ValueError("the mirrored PAW file is not round 3's saved one")
    source = [f for f in site_occupations["files"] if f["site"] == site and f["state"] == SOURCE_STATE]
    if len(source) != 1 or not site_occupations["all_match"]:
        raise ValueError("expected one mirrored, sha-matched source state")
    source = source[0]
    source_bytes = (root / r3.PACKAGE / source["local"]).read_bytes()
    if cb.sha256(source_bytes) != source["sha256"] or source_bytes != fetched["oh_occup.txt"]:
        raise ValueError("source occupations differ from their mirror receipt or from the OH save")
    _, atoms = r1.geometry(old_deck.decode("utf-8"))
    if ATOM > r1.SLAB_ATOMS or atoms[ATOM - 1][0] != "Fe":
        raise ValueError("atom 22 is not the slab's Fe")
    occup = occupations(start, source_bytes, r1.nat_of(state))
    paw_text = paw(fetched["r3_stop_paw.txt"], fetched["oh_paw.txt"], r1.nat_of(state), r1.nat_of(SOURCE_STATE))
    name = state + JOB_SUFFIX
    job_dir = f"{RUN_ROOT}/{site}"
    deck = r4_deck(old_deck.decode("utf-8"), name).encode("utf-8")
    bundle = f"{PACKAGE}/seeds/{site}/{state}"
    files = {f"runs/{job_dir}/{name}.in": deck, f"{bundle}/occup.txt": occup, f"{bundle}/paw.txt": paw_text}
    scratch = {f: pins["files"][f]["sha256"] for f in REMOTE_FILES}
    scratch.update({"occup.txt": cb.sha256(occup), "paw.txt": cb.sha256(paw_text)})
    job = {"dir": job_dir, "job": name, "sha256": cb.sha256(deck), "nk": old["nk"],
           **{k: LIMITS["r4_main"][k] for k in ("scf_seconds", "projection_seconds", "max_iterations")},
           "recipe": "seeded", "role": "extension", "source_deck": source_deck,
           "seed": {"state": state, "job": old_name, "recipe": "seeded", "save_dir": save},
           "scratch_source": {"save_dir": bundle, "files": dict(sorted(scratch.items()))}}
    row = {k: old_row[k] for k in ("site_dir", "formula", "state", "failure")}
    row.update(seed={"state": state, "job": old_name, "recipe": "seeded", "root": r3.RUN_ROOT,
                     "id": f"{site}__{old_name}"},
               dir=job_dir, job=name, round=4, round_3_job=old_name, round_3_failure=attempt["failure"],
               seed_density="stopped", bundle=bundle, remote_copy={f: save + "/" + f for f in REMOTE_FILES},
               mixing=dict(MIXING),
               occupations={"start": mirror, "start_sha256": cb.sha256(start), "atoms_replaced": [ATOM],
                            "from": {"state": SOURCE_STATE, "job": source["job"], "recipe": source["recipe"],
                                     "path": f"{r3.PACKAGE}/{source['local']}", "sha256": source["sha256"]},
                            "sha256": cb.sha256(occup)},
               paw={"start": pins["fetched"]["r3_stop_paw.txt"]["local"],
                    "start_sha256": pins["fetched"]["r3_stop_paw.txt"]["sha256"], "atoms_replaced": [ATOM],
                    "from": {"state": SOURCE_STATE, "job": source["job"], "path": pins["fetched"]["oh_paw.txt"]["local"],
                             "remote": pins["fetched"]["oh_paw.txt"]["remote"],
                             "sha256": pins["fetched"]["oh_paw.txt"]["sha256"]},
                    "sha256": cb.sha256(paw_text)},
               density={"source": save + "/" + r2.DENSITY, "sha256": pins["files"][r2.DENSITY]["sha256"],
                        "bytes": pins["files"][r2.DENSITY]["bytes"]})
    stages = {"r4_main": {"kind": "hea", "manifest": MANIFEST["r4_main"], "concurrency": 1,
                          "wall_minutes": LIMITS["r4_main"]["wall_minutes"], "jobs": [job]}}
    files[MANIFEST["r4_main"]] = manifest_text("r4_main", [job]).encode("utf-8")
    stage_pins = {path: cb.sha256(data) for path, data in files.items()}
    for relative in r1.RUNNER_FILES:
        stage_pins[relative] = cb.sha256((root / relative).read_bytes())
        if stage_pins[relative] != r3_spec["files"][relative]:
            raise ValueError("runner file changed since round 3: " + relative)
    spent = round(r3_spec["allocation"]["spent_before_this_launch_cpu_su"] + r3_cpu_su(root), 1)
    ceilings = {s: len(stages[s]["jobs"]) * LIMITS[s]["wall_minutes"] * 128 // 60 for s in stages}
    ceiling = sum(ceilings.values())
    campaign = r3_spec["allocation"]["approved_campaign_ceiling_cpu_su"]
    if spent + ceiling > campaign:
        raise ValueError("round 4 does not fit the approved arm-C campaign ceiling")
    source_readout = {"path": R3_READOUT, "sha256": cb.sha256(readout_bytes)}
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
        "qe_binaries_sha256": r3_spec["qe_binaries_sha256"],
        "files": dict(sorted(stage_pins.items())),
        "pseudo_md5": r3_spec["pseudo_md5"],
        "stages": stages,
    }
    plan = {"schema": "s8-arm-c-ext-plan-v1", "date": DATE, "design": DESIGN, "decision_ref": DECISION,
            "source_readout": source_readout, "round": 4,
            "round_3": {"spec": R3_SPEC, "spec_sha256": cb.sha256(r3_spec_bytes), "plan": R3_PLAN,
                        "main": "21199937 read out: neither state converged in 300 iterations; the Fe25 O stopped "
                                "with Fe 22 in a configuration no converged state at its site has"},
            "rule": ("the Fe25 s25/2 O, its site's last missing state after round 3: round 3's job with mixing_fixed_ns 5 "
                     "added, from round 3's stopped save (density and XML copied on Anvil; occup.txt and paw.txt "
                     "rebuilt) with Fe 22's Hubbard occupations and PAW block (both spins) from the converged OH state; "
                     "a convergence within the first 5 iterations is not accepted (held occupations); runner ceiling "
                     "300 iterations, QE's own electron_maxstep; max_seconds 18400"),
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
