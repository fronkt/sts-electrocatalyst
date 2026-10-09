"""Build round 3 of the S8 arm-C extension: the last missing state of one Cu8 and one Fe25 support site, run
again from round 2's moved densities with a longer mixing history and more iterations; launches nothing.

Decisions of record: Frank, 2026-10-09, "Lets do a round 3", after round 2's readout: 3 of 11 states converged,
and Cu8 and Fe25 still had no value (docs/research/s8-arm-c-extension-2026-10-08.md, Round 2 main readout).
Then "0.3 + longer memory": the pre-launch review found that mixing_beta 0.1, first proposed, had been
measured worse than 0.3 on these two alloys (docs/research/lowtail-clean-slab-scf-stall-2026-09-19.md,
2026-09-22 diagnostic).

Targets: the Cu8 and Fe25 support sites still missing exactly one state after round 2 (the Cu8 s16/2 slab and
Fe25 s25/2 O). Either one converging completes its site and gives its alloy a single-site value. Each job is
round 2's job with three deck lines changed and one added:
- its own prefix;
- mixing_ndim 16 instead of QE's default 8, added after mixing_beta (the ndim16 re-run's line); mixing_beta
  stays at production's 0.3;
- max_seconds 18400 instead of 165000. QE then stops itself and writes its last density before the runner's
  19,000 s SCF wall. Round 2's two runs were killed mid-iteration and kept nothing to continue from.
The runner's iteration ceiling is 300, which is QE's own electron_maxstep. The start is round 2's, byte for
byte: the moved density, the XML, occup.txt and paw.txt. Staging copies the density and XML from round 2's root
on Anvil and checks them against round 2's pins. There is no canary: QE already read these files as built in
round 2, and start_check.py confirms, minutes after release, that each job prints round 2's first lines.

    python src/dft/arm_c_ext_r3_build.py            # write decks, seed text files, manifest, plan, spec
    python src/dft/arm_c_ext_r3_build.py --check    # rebuild and compare with the files on disk
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
import hea_deck as hd  # noqa: E402

ROOT = HERE.parents[1]
DATE = "2026-10-09"
PACKAGE = "results/arm_c_ext_r3_" + DATE
RUN_ROOT = "hea/arm_c_ext_r3_" + DATE
R2_SPEC = r2.PACKAGE + "/launch_spec.json"
R2_PLAN = r2.PACKAGE + "/ext_plan.json"
R2_READOUT = r2.PACKAGE + "/readout.json"
R2_COLLECTION = r2.PACKAGE + "/terminal_collection.json"
R2_REMOTE = "/anvil/projects/x-che260157/sts_arm_c_ext_r2_2026-10-08"
R2_TASKS = 13  # the two canary and eleven main tasks accounted by sacct
MANIFEST = {"r3_main": "runs/m_arm_c_ext_r3_" + DATE + "_main.txt"}
DESIGN = r2.DESIGN
DECISION = ("Frank, 2026-10-09: \"Lets do a round 3\" (after round 2's readout), then \"0.3 + longer memory\" "
            "(after the pre-launch review)")
JOB_SUFFIX = "__atomic_moved_ndim16"
EXPECTED = [("Cu8Cr23Mn35Co34__s16_site2", "slab"), ("Fe25Co25Ni25Cr25__s25_site2", "O")]
MIXING = {"mixing_beta": 0.3, "mixing_ndim": 16}
QE_MAX_SECONDS = 18400
LIMITS = {"r3_main": {"max_iterations": 300, "scf_seconds": 19000, "projection_seconds": 600, "wall_minutes": 345}}
ROUND_2_LINES = {"  mixing_beta = ": "  mixing_beta = 0.3", "  max_seconds = ": "  max_seconds = 165000",
                 "  electron_maxstep = ": "  electron_maxstep = 300", "  startingpot = ": "  startingpot = 'file'"}


def targets(readout: dict) -> list:
    """(site, state) of every Cu8 or Fe25 support site still missing exactly one state after round 2."""
    out = []
    for site in readout["sites"]:
        if site["formula"] not in r1.ALLOYS or not {"support_lo", "support_hi"} & set(site["roles"]):
            continue
        missing = [s for s in ("slab", "OH", "O", "OOH") if not site["states"][s]["accepted"]]
        if len(missing) == 1:
            out.append((r1.site_name(site["dir"]), missing[0]))
    if out != EXPECTED:
        raise ValueError("round-3 targets differ: " + repr(out))
    return out


def r3_deck(text: str, job: str) -> str:
    """Round 2's deck with its own prefix, MIXING's mixing_beta, an added mixing_ndim and max_seconds 18400."""
    lines = text.split("\n")

    def one(start):
        hits = [i for i, line in enumerate(lines) if line.startswith(start)]
        if len(hits) != 1:
            raise ValueError("deck line not unique: " + start.strip())
        return hits[0]

    if any(line.lstrip().startswith("mixing_ndim") for line in lines):
        raise ValueError("round-2 deck already sets mixing_ndim")
    for start, expected in ROUND_2_LINES.items():
        if lines[one(start)] != expected:
            raise ValueError("unexpected round-2 deck line: " + lines[one(start)])
    lines[one("  prefix = '")] = f"  prefix = '{job}'"
    lines[one("  max_seconds = ")] = f"  max_seconds = {QE_MAX_SECONDS}"
    beta = one("  mixing_beta = ")
    lines[beta] = f"  mixing_beta = {MIXING['mixing_beta']}"
    lines.insert(beta + 1, f"  mixing_ndim = {MIXING['mixing_ndim']}")
    return "\n".join(lines)


def r2_cpu_su(root: Path) -> float:
    """CPU SU of round 2: the sacct CPU time of its 13 tasks (terminal_collection.json)."""
    collection = json.loads((root / R2_COLLECTION).read_text(encoding="utf-8"))
    rows = [line.split("|") for line in collection["sacct"].strip().splitlines()]
    seconds = [int(r[7]) for r in rows if "." not in r[0]]
    if len(seconds) != R2_TASKS:
        raise ValueError(f"expected {R2_TASKS} accounted round-2 tasks, found {len(seconds)}")
    return sum(seconds) / 3600


def manifest_text(stage: str, jobs: list) -> str:
    head = ["# APPROVED 2026-10-09: " + DESIGN + " (Frank: \"Lets do a round 3\", then \"0.3 + longer memory\")",
            "# S8 arm C extension, round 3 (" + stage + "): the last missing state of one Cu8 and one Fe25 support site, "
            "round 2's moved density with mixing_ndim 16 at mixing_beta 0.3, up to 300 iterations; exploratory; "
            "no automatic retries.",
            "# SUBMIT WITH EXCLUDE=" + hd.EXCLUDE,
            "# NP=128 NCONC=1"]
    return "\n".join(head + [f"{j['dir']} {j['job']} .in {j['nk']}" for j in jobs]) + "\n"


def build(root: Path = ROOT) -> dict:
    """Committed output path -> bytes; nothing is written here."""
    readout_bytes = (root / R2_READOUT).read_bytes()
    readout = json.loads(readout_bytes)
    r2_spec_bytes = (root / R2_SPEC).read_bytes()
    r2_spec = json.loads(r2_spec_bytes)
    r2_plan = json.loads((root / R2_PLAN).read_text(encoding="utf-8"))
    r2_jobs = {(r1.site_name(j["dir"]), j["job"]): j for j in r2_spec["stages"]["r2_main"]["jobs"]}
    r2_rows = {(r1.site_name(r["dir"]), r["job"]): r for r in r2_plan["selection"]}
    sites = {r1.site_name(s["dir"]): s for s in readout["sites"]}
    if LIMITS["r3_main"]["max_iterations"] != int(ROUND_2_LINES["  electron_maxstep = "].rsplit(" ", 1)[1]):
        raise ValueError("the runner ceiling must equal QE's electron_maxstep")
    if not QE_MAX_SECONDS < LIMITS["r3_main"]["scf_seconds"]:
        raise ValueError("QE must stop itself before the runner's SCF wall")
    files, jobs, rows = {}, [], []
    for site, state in targets(readout):
        old_name = state + r2.JOB_SUFFIX
        old, old_row = r2_jobs[(site, old_name)], r2_rows[(site, old_name)]
        source_deck = f"runs/{old['dir']}/{old_name}.in"
        old_deck = (root / source_deck).read_bytes()
        if cb.sha256(old_deck) != old["sha256"]:
            raise ValueError("round-2 deck differs from its pin: " + source_deck)
        name = state + JOB_SUFFIX
        job_dir = f"{RUN_ROOT}/{site}"
        deck = r3_deck(old_deck.decode("utf-8"), name).encode("utf-8")
        bundle = f"{PACKAGE}/seeds/{site}/{state}"
        pins = dict(old["scratch_source"]["files"])
        for text_file in ("occup.txt", "paw.txt"):  # round 2's files (round 1's rebuilt ones), byte for byte
            payload = (root / old["scratch_source"]["save_dir"] / text_file).read_bytes()
            if cb.sha256(payload) != pins[text_file]:
                raise ValueError("round-2 seed file differs from its pin: " + old["scratch_source"]["save_dir"] + "/" + text_file)
            files[f"{bundle}/{text_file}"] = payload
        files[f"runs/{job_dir}/{name}.in"] = deck
        jobs.append({"dir": job_dir, "job": name, "sha256": cb.sha256(deck), "nk": old["nk"],
                     **{k: LIMITS["r3_main"][k] for k in ("scf_seconds", "projection_seconds", "max_iterations")},
                     "recipe": "seeded", "role": "extension", "source_deck": source_deck, "seed": old["seed"],
                     "scratch_source": {"save_dir": bundle, "files": pins}})
        r2_attempt = next(a for a in sites[site]["extension_attempts"] if a["state"] == state)
        source = R2_REMOTE + "/" + old["scratch_source"]["save_dir"]
        row = {k: old_row[k] for k in ("site_dir", "formula", "state", "failure", "seed")}
        row.update(dir=job_dir, job=name, round=3, round_2_job=old_name, round_2_failure=r2_attempt["failure"],
                   seed_density="moved", bundle=bundle,
                   remote_copy={f: source + "/" + f for f in (r2.DENSITY, r2.XML)},
                   mixing=dict(MIXING), density=old_row["density"])
        rows.append(row)
    stages = {"r3_main": {"kind": "hea", "manifest": MANIFEST["r3_main"], "concurrency": len(jobs),
                          "wall_minutes": LIMITS["r3_main"]["wall_minutes"], "jobs": jobs}}
    files[MANIFEST["r3_main"]] = manifest_text("r3_main", jobs).encode("utf-8")
    stage_pins = {path: cb.sha256(data) for path, data in files.items()}
    for relative in r1.RUNNER_FILES:
        stage_pins[relative] = cb.sha256((root / relative).read_bytes())
        if stage_pins[relative] != r2_spec["files"][relative]:
            raise ValueError("runner file changed since round 2: " + relative)
    spent = round(r2_spec["allocation"]["spent_before_this_launch_cpu_su"] + r2_cpu_su(root), 1)
    ceilings = {s: len(stages[s]["jobs"]) * LIMITS[s]["wall_minutes"] * 128 // 60 for s in stages}
    ceiling = sum(ceilings.values())
    campaign = r2_spec["allocation"]["approved_campaign_ceiling_cpu_su"]
    if spent + ceiling > campaign:
        raise ValueError("round 3 does not fit the approved arm-C campaign ceiling")
    source_readout = {"path": R2_READOUT, "sha256": cb.sha256(readout_bytes)}
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
        "qe_binaries_sha256": r2_spec["qe_binaries_sha256"],
        "files": dict(sorted(stage_pins.items())),
        "pseudo_md5": r2_spec["pseudo_md5"],
        "stages": stages,
    }
    plan = {"schema": "s8-arm-c-ext-plan-v1", "date": DATE, "design": DESIGN, "decision_ref": DECISION,
            "source_readout": source_readout, "round": 3,
            "round_2": {"spec": R2_SPEC, "spec_sha256": cb.sha256(r2_spec_bytes), "plan": R2_PLAN,
                        "main": "21195261 read out: 3 of 11 converged; Cu8 and Fe25 still without a value"},
            "rule": ("the Cu8 and Fe25 support sites still missing exactly one state after round 2; round 2's job and start "
                     "(moved density, XML, occup.txt, paw.txt) byte for byte, with mixing_ndim 16 at production's "
                     "mixing_beta 0.3 and max_seconds 18400 so that QE stops itself and writes its last density before "
                     "the runner's wall; runner ceiling 300 iterations, QE's own electron_maxstep"),
            "mixing": dict(MIXING), "qe_max_seconds": QE_MAX_SECONDS,
            "status": "exploratory; arm C's registered readings stay final",
            "selection": rows}
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
