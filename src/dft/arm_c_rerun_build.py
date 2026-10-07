"""Build the S8 arm-C full re-run round; launches nothing.

Decision of record: Frank, 2026-10-07, "Go with the full rerun." The registered re-run rules
(docs/research/s8-arm-c-dft-design-2026-10-07.md §5) apply unchanged except the slot cap: every
failed SCF of the committed terminal readout (results/arm_c_2026-10-07/readout.json) is re-run once,
a ceiling stop with the probe-selected recipe and an IEEE stop as an identical re-run. Two
informative controls re-run, with the same recipe, the accepted production slab of each site whose
chain would otherwise pair a production slab with ceiling re-runs. Geometries, iteration ceiling,
runtime bounds and runner are those of the production launch.

    python src/dft/arm_c_rerun_build.py            # write decks, manifest, re-run plan and spec
    python src/dft/arm_c_rerun_build.py --check    # rebuild in memory and compare with the files
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arm_c_build as cb  # noqa: E402
import arm_c_readout as ro  # noqa: E402
import hea_deck as hd  # noqa: E402

ROOT = HERE.parents[1]
SOURCE = "results/arm_c_" + cb.DATE
READOUT = SOURCE + "/readout.json"
SOURCE_SPEC = SOURCE + "/launch_spec.json"
COLLECTION = SOURCE + "/terminal_collection.json"
PACKAGE = "results/arm_c_" + cb.DATE + "_rerun"
MANIFEST = "runs/m_arm_c_" + cb.DATE + "_rerun.txt"
STAGE = "arm_c_rerun"
DECISION = "Frank, 2026-10-07: \"Go with the full rerun.\""
CONTROLS = 2  # approved with the round: one per site with a production slab and a ceiling stop


def spent_cpu_su(collection: dict, jobs: dict) -> float:
    """CPU SU of the production launch from its sacct allocation rows (CPUTimeRAW, core-seconds)."""
    rows = [line.split("|") for line in collection["sacct"].strip().splitlines()]
    seconds = [int(r[7]) for r in rows if "." not in r[0] and r[0].split("_")[0] in jobs.values()]
    if len(seconds) != 66:
        raise ValueError("expected 66 accounted array tasks")
    return round(sum(seconds) / 3600, 1)


def rows(readout: dict) -> tuple:
    """Every failed state (registered order, all slots) and the recipe controls."""
    sites = readout["sites"]
    recipe = readout["probe"]["rerun_recipe_for_ceiling_stops"]
    if recipe != "ndim16":
        raise ValueError("the probe did not select ndim16")
    failed = {(s["dir"], state) for s in sites for state in s["original_failures"]}
    selection = ro.rerun_selection(sites, recipe, slots=len(failed))
    if {(r["site_dir"], r["state"]) for r in selection} != failed or len(selection) != len(failed):
        raise ValueError("the full round must cover every failed state exactly once")
    for row in selection:
        if (row["failure"], row["recipe"]) not in {("CEILING", recipe), ("IEEE", "production")}:
            raise ValueError("unregistered failure class or recipe: " + json.dumps(row))
    controls = []
    for site in sites:
        failures = site["original_failures"]
        if "slab" not in failures and "CEILING" in failures.values():
            name = site["dir"].rsplit("/", 1)[-1]
            controls.append({"site_dir": site["dir"], "state": "slab", "recipe": recipe,
                             "dir": f"{ro.RERUN_ROOT}/{name}", "job": "slab__atomic_" + recipe,
                             "control_of": "slab__atomic"})
    if len(controls) != CONTROLS:
        raise ValueError("expected the two approved recipe controls")
    pairs = [(r["dir"], r["job"]) for r in selection + controls]
    if len(set(pairs)) != len(pairs):
        raise ValueError("duplicate re-run job")
    return selection, controls


def manifest_text(jobs: list) -> str:
    head = ["# APPROVED 2026-10-07: docs/research/s8-arm-c-dft-design-2026-10-07.md section 6 (Frank: \"Go with the full rerun.\")",
            "# S8 arm C re-run round (" + STAGE + "): every failed SCF once under its registered recipe, plus 2 recipe controls; no automatic retries.",
            "# SUBMIT WITH EXCLUDE=" + hd.EXCLUDE,
            "# NP=128 NCONC=1"]
    return "\n".join(head + [f"{j['dir']} {j['job']} .in {j['nk']}" for j in jobs]) + "\n"


def build(root: Path = ROOT) -> dict:
    """Every output path -> bytes; nothing is written here."""
    readout_bytes = (root / READOUT).read_bytes()
    readout = json.loads(readout_bytes)
    source_spec = json.loads((root / SOURCE_SPEC).read_text(encoding="utf-8"))
    submitted = json.loads((root / SOURCE / "submit_receipt.json").read_text(encoding="utf-8"))["jobs"]
    spent = spent_cpu_su(json.loads((root / COLLECTION).read_text(encoding="utf-8")), submitted)
    selection, controls = rows(readout)
    files, jobs = {}, []
    for row in selection + controls:
        production = f"runs/{row['site_dir']}/{row['state']}__atomic.in"
        data = (root / production).read_bytes()
        if cb.sha256(data) != source_spec["files"][production]:
            raise ValueError("production deck differs from its launch pin: " + production)
        if row["recipe"] == "production":
            if row["job"] != row["state"] + "__atomic":
                raise ValueError("an identical re-run keeps the production job name")
            out = data
        else:
            out = cb.variant_deck(data.decode("utf-8"), row["recipe"], row["job"]).encode("utf-8")
        path = f"runs/{row['dir']}/{row['job']}.in"
        files[path] = out
        job = {"dir": row["dir"], "job": row["job"], "sha256": cb.sha256(out), "nk": cb.NK,
               "scf_seconds": cb.SCF_SECONDS, "projection_seconds": cb.PROJECTION_SECONDS,
               "max_iterations": cb.MAX_ITERATIONS, "recipe": row["recipe"], "source_deck": production}
        job["role"] = "control" if "control_of" in row else "rerun_" + row["failure"].lower()
        jobs.append(job)
    files[MANIFEST] = manifest_text(jobs).encode("utf-8")
    pins = {path: cb.sha256(data) for path, data in files.items()}
    for relative in cb.RUNNER_FILES:
        pins[relative] = cb.sha256((root / relative).read_bytes())
        if pins[relative] != source_spec["files"][relative]:
            raise ValueError("runner file changed since the production launch: " + relative)
    ceiling = len(jobs) * cb.WALL_MINUTES * 128 // 60
    campaign = source_spec["allocation"]["approved_campaign_ceiling_cpu_su"]
    if spent + ceiling > campaign:
        raise ValueError("the round does not fit the approved campaign ceiling")
    source_readout = {"path": READOUT, "sha256": cb.sha256(readout_bytes)}
    spec = {
        "schema": "research-batch-2026-09-16",
        "np": 128,
        "exclusions": hd.EXCLUDE,
        "date": cb.DATE,
        "design": "docs/research/s8-arm-c-dft-design-2026-10-07.md",
        "decision_ref": DECISION,
        "source_readout": source_readout,
        "allocation": {"account": "che260157", "partition": "wholenode", "cores_per_task": 128,
                       "approved_campaign_ceiling_cpu_su": campaign,
                       "spent_before_this_launch_cpu_su": spent,
                       "this_launch_ceiling_cpu_su": ceiling},
        "qe_binaries_sha256": source_spec["qe_binaries_sha256"],
        "files": dict(sorted(pins.items())),
        "pseudo_md5": source_spec["pseudo_md5"],
        "stages": {STAGE: {"kind": "hea", "manifest": MANIFEST, "concurrency": len(jobs),
                           "wall_minutes": cb.WALL_MINUTES, "jobs": jobs}},
    }
    plan = {"schema": "s8-arm-c-rerun-plan-v1", "date": cb.DATE, "design": spec["design"],
            "decision_ref": DECISION, "source_readout": source_readout,
            "probe_recipe": readout["probe"]["rerun_recipe_for_ceiling_stops"],
            "rule": ("every failed state of the terminal readout is re-run once: CEILING with the probe recipe, "
                     "IEEE as an identical production re-run; the registered 6-slot cap is lifted"),
            "slots": len(selection), "selection": selection,
            "controls_rule": ("informative: the accepted production slab of every site with a CEILING stop, "
                              "re-run with the probe recipe"),
            "controls": controls}
    files[PACKAGE + "/rerun_plan.json"] = (json.dumps(plan, indent=2) + "\n").encode("utf-8")
    files[PACKAGE + "/launch_spec.json"] = (json.dumps(spec, indent=2) + "\n").encode("utf-8")
    return files


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare a fresh build with the files on disk")
    args = parser.parse_args(argv)
    files = build()
    problems = []
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
    print(json.dumps({"files": len(files), "mismatches": problems,
                      "spec_sha256": cb.sha256(files[PACKAGE + "/launch_spec.json"])}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
