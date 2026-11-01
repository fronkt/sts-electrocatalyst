"""Build round 7 of the S8 arm-C extension: two more attempts at the one SCF that keeps Cu8 without a value (the
Cu8 s16/2 clean slab), each from round 3's start with one solver change; launches nothing.

Decision of record: Frank, 2026-11-01, "yeah launch the two Cu8 runs", after the proposal of two variants of the
Cu8 s16/2 slab at about 600 SU each (docs/research/s8-arm-c-extension-2026-10-08.md, Round 7). The site's O, OH
and OOH converged in round 2; the slab stalled in rounds 2 and 3 (best 5.3e-6 Ry at iteration 68 of round 3, then
drifting back up). This round runs after the first Cu8 electrode was measured (2026-10-30, activation CVs only), so
any value it gives is labelled as computed after that measurement.

Both jobs are round 3's job (same deck, same start byte for byte: the moved density, the XML, occup.txt and
paw.txt) with its own prefix, a lower QE max_seconds and one solver change that leaves the converged energy
unchanged:
- `slab__atomic_moved_cg`: diagonalization = 'cg' (about 3x slower per iteration than Davidson; never run on
  these states, dropped from arm C's probes only for time);
- `slab__atomic_moved_nbnd470`: nbnd = 470 instead of QE's default 390 (1.2 x 325 occupied) and
  diago_full_acc = .true., so the partly filled states near the Fermi level are converged to full accuracy at
  every iteration.
Mixing stays round 3's (local-TF, beta 0.3, ndim 16). Limits: QE max_seconds 16,800 s, runner SCF wall 17,400 s,
projection 600 s, Slurm 300 min; 2 x 300 min x 128 cores = 1,280 SU ceiling.

Rule written before launch: a converged slab counts only in the magnetic state of the site's converged states
(49.6-50.1 muB total; flag above 1.5 muB, as in round 3). If both converge in that state, the lower total energy
is used, as in round 5.

    python src/dft/arm_c_ext_r7_build.py            # write decks, seed text files, manifest, plan, spec
    python src/dft/arm_c_ext_r7_build.py --check    # rebuild and compare with the files on disk
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
DATE = "2026-11-01"
PACKAGE = "results/arm_c_ext_r7_" + DATE
RUN_ROOT = "hea/arm_c_ext_r7_" + DATE
R3_SPEC = r3.PACKAGE + "/launch_spec.json"
R3_PLAN = r3.PACKAGE + "/ext_plan.json"
R3_REMOTE = "/anvil/projects/x-che260157/sts_arm_c_ext_r3_2026-10-09"
R6_SPEC = "results/arm_c_ext_r6_2026-10-11/launch_spec.json"
R6_COLLECTION = "results/arm_c_ext_r6_2026-10-11/terminal_collection.json"
R6_TASKS = 4
MANIFEST = {"r7_main": "runs/m_arm_c_ext_r7_" + DATE + "_main.txt"}
DESIGN = r2.DESIGN
DECISION = "Frank, 2026-11-01: \"yeah launch the two Cu8 runs\" (two solver variants of the Cu8 s16/2 slab, about 600 SU each)"
SITE, STATE = "Cu8Cr23Mn35Co34__s16_site2", "slab"
R3_JOB = STATE + r3.JOB_SUFFIX
VARIANTS = {
    "slab__atomic_moved_cg": {"electrons_add": ["  diagonalization = 'cg'"], "system_add": []},
    "slab__atomic_moved_nbnd470": {"electrons_add": ["  diago_full_acc = .true."], "system_add": ["  nbnd = 470"]},
}
QE_MAX_SECONDS = 16800
LIMITS = {"r7_main": {"max_iterations": 300, "scf_seconds": 17400, "projection_seconds": 600, "wall_minutes": 300}}
CAMPAIGN_CEILING = 23821  # 23,680 approved for arm C; Frank's 2026-11-01 approval adds this launch (22,540.7 + 1,280)


def r7_deck(text: str, job: str, variant: dict) -> str:
    """Round 3's deck with its own prefix, max_seconds 16800 and the variant's added lines."""
    lines = text.split("\n")

    def one(start):
        hits = [i for i, line in enumerate(lines) if line.startswith(start)]
        if len(hits) != 1:
            raise ValueError("deck line not unique: " + start.strip())
        return hits[0]

    for key in ("diagonalization", "nbnd", "diago_full_acc"):
        if any(line.lstrip().startswith(key) for line in lines):
            raise ValueError("round-3 deck already sets " + key)
    if lines[one("  max_seconds = ")] != "  max_seconds = " + str(r3.QE_MAX_SECONDS):
        raise ValueError("unexpected round-3 max_seconds line")
    lines[one("  prefix = '")] = f"  prefix = '{job}'"
    lines[one("  max_seconds = ")] = f"  max_seconds = {QE_MAX_SECONDS}"
    ndim = one("  mixing_ndim = ")
    lines[ndim + 1:ndim + 1] = variant["electrons_add"]
    if variant["system_add"]:
        degauss = one("  degauss = ")
        lines[degauss + 1:degauss + 1] = variant["system_add"]
    return "\n".join(lines)


def r6_cpu_su(root: Path) -> float:
    collection = json.loads((root / R6_COLLECTION).read_text(encoding="utf-8"))
    rows = [line.split("|") for line in collection["sacct"].strip().splitlines()]
    seconds = [int(r[7]) for r in rows if "." not in r[0]]
    if len(seconds) != R6_TASKS:
        raise ValueError(f"expected {R6_TASKS} accounted round-6 tasks, found {len(seconds)}")
    return sum(seconds) / 3600


def manifest_text(stage: str, jobs: list) -> str:
    head = ["# APPROVED 2026-11-01: " + DESIGN + " (Frank: \"yeah launch the two Cu8 runs\")",
            "# S8 arm C extension, round 7 (" + stage + "): the Cu8 s16/2 slab from round 3's start, once with CG "
            "diagonalization and once with 470 bands and full-accuracy Davidson; exploratory; no automatic retries.",
            "# SUBMIT WITH EXCLUDE=" + hd.EXCLUDE,
            "# NP=128 NCONC=1"]
    return "\n".join(head + [f"{j['dir']} {j['job']} .in {j['nk']}" for j in jobs]) + "\n"


def build(root: Path = ROOT) -> dict:
    """Committed output path -> bytes; nothing is written here."""
    r3_spec_bytes = (root / R3_SPEC).read_bytes()
    r3_spec = json.loads(r3_spec_bytes)
    r3_plan = json.loads((root / R3_PLAN).read_text(encoding="utf-8"))
    r6_spec = json.loads((root / R6_SPEC).read_text(encoding="utf-8"))
    old = next(j for j in r3_spec["stages"]["r3_main"]["jobs"] if r1.site_name(j["dir"]) == SITE and j["job"] == R3_JOB)
    old_row = next(r for r in r3_plan["selection"] if r1.site_name(r["dir"]) == SITE and r["job"] == R3_JOB)
    source_deck = f"runs/{old['dir']}/{R3_JOB}.in"
    old_deck = (root / source_deck).read_bytes()
    if cb.sha256(old_deck) != old["sha256"]:
        raise ValueError("round-3 deck differs from its pin: " + source_deck)
    if LIMITS["r7_main"]["max_iterations"] != 300 or not QE_MAX_SECONDS < LIMITS["r7_main"]["scf_seconds"]:
        raise ValueError("QE must stop itself before the runner's SCF wall, at the runner's iteration ceiling")
    if (LIMITS["r7_main"]["scf_seconds"] + LIMITS["r7_main"]["projection_seconds"]) / 60 > LIMITS["r7_main"]["wall_minutes"]:
        raise ValueError("SCF and projection walls exceed the Slurm wall")
    files, jobs, rows = {}, [], []
    bundle = f"{PACKAGE}/seeds/{SITE}/{STATE}"
    pins = dict(old["scratch_source"]["files"])
    for text_file in ("occup.txt", "paw.txt"):  # round 3's files, byte for byte
        payload = (root / old["scratch_source"]["save_dir"] / text_file).read_bytes()
        if cb.sha256(payload) != pins[text_file]:
            raise ValueError("round-3 seed file differs from its pin: " + text_file)
        files[f"{bundle}/{text_file}"] = payload
    job_dir = f"{RUN_ROOT}/{SITE}"
    source = R3_REMOTE + "/" + old["scratch_source"]["save_dir"]
    for name, variant in VARIANTS.items():
        deck = r7_deck(old_deck.decode("utf-8"), name, variant).encode("utf-8")
        files[f"runs/{job_dir}/{name}.in"] = deck
        jobs.append({"dir": job_dir, "job": name, "sha256": cb.sha256(deck), "nk": old["nk"],
                     **{k: LIMITS["r7_main"][k] for k in ("scf_seconds", "projection_seconds", "max_iterations")},
                     "recipe": "seeded", "role": "extension", "source_deck": source_deck, "seed": old["seed"],
                     "scratch_source": {"save_dir": bundle, "files": pins}})
        row = {k: old_row[k] for k in ("site_dir", "formula", "state", "failure", "seed")}
        row.update(dir=job_dir, job=name, round=7, round_3_job=R3_JOB, seed_density="moved", bundle=bundle,
                   remote_copy={f: source + "/" + f for f in (r2.DENSITY, r2.XML)},
                   mixing=dict(r3.MIXING), solver={"electrons_add": variant["electrons_add"],
                                                   "system_add": variant["system_add"]},
                   density=old_row["density"])
        rows.append(row)
    stages = {"r7_main": {"kind": "hea", "manifest": MANIFEST["r7_main"], "concurrency": len(jobs),
                          "wall_minutes": LIMITS["r7_main"]["wall_minutes"], "jobs": jobs}}
    files[MANIFEST["r7_main"]] = manifest_text("r7_main", jobs).encode("utf-8")
    stage_pins = {path: cb.sha256(data) for path, data in files.items()}
    for relative in r1.RUNNER_FILES:
        stage_pins[relative] = cb.sha256((root / relative).read_bytes())
        if stage_pins[relative] != r3_spec["files"][relative]:
            raise ValueError("runner file changed since round 3: " + relative)
    spent = round(r6_spec["allocation"]["spent_before_this_launch_cpu_su"] + r6_cpu_su(root), 1)
    ceilings = {s: len(stages[s]["jobs"]) * LIMITS[s]["wall_minutes"] * 128 // 60 for s in stages}
    ceiling = sum(ceilings.values())
    if spent + ceiling > CAMPAIGN_CEILING:
        raise ValueError("round 7 does not fit the approved arm-C campaign ceiling")
    source_spec = {"path": R3_SPEC, "sha256": cb.sha256(r3_spec_bytes)}
    spec = {
        "schema": "research-batch-2026-09-16",
        "np": 128,
        "exclusions": hd.EXCLUDE,
        "date": DATE,
        "design": DESIGN,
        "decision_ref": DECISION,
        "source_readout": source_spec,
        "allocation": {"account": "che260157", "partition": "wholenode", "cores_per_task": 128,
                       "approved_campaign_ceiling_cpu_su": CAMPAIGN_CEILING,
                       "spent_before_this_launch_cpu_su": spent,
                       "stage_ceilings_cpu_su": ceilings,
                       "this_launch_ceiling_cpu_su": ceiling},
        "qe_binaries_sha256": r3_spec["qe_binaries_sha256"],
        "files": dict(sorted(stage_pins.items())),
        "pseudo_md5": r3_spec["pseudo_md5"],
        "stages": stages,
    }
    plan = {"schema": "s8-arm-c-ext-plan-v1", "date": DATE, "design": DESIGN, "decision_ref": DECISION,
            "source_readout": source_spec, "round": 7,
            "round_3": {"spec": R3_SPEC, "spec_sha256": cb.sha256(r3_spec_bytes), "plan": R3_PLAN,
                        "main": "21199937 read out: neither state converged (Cu8 s16/2 slab best 5.3e-6 Ry at iteration 68)"},
            "rule": ("the Cu8 s16/2 slab, round 3's job and start byte for byte, once with diagonalization 'cg' and once "
                     "with nbnd 470 and diago_full_acc; max_seconds 16800 so QE stops itself before the runner's "
                     "17,400 s wall; a converged slab counts only in the site's magnetic state (49.6-50.1 muB, flag "
                     "above 1.5 muB); if both converge there, the lower total energy is used"),
            "after_measurement": "computed after the first Cu8 electrode was measured (2026-10-30, activation CVs only)",
            "qe_max_seconds": QE_MAX_SECONDS,
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
