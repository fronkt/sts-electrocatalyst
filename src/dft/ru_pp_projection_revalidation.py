"""Review Ru projection format rejections without rerunning or altering receipts.

The frozen runner expected one total-charge row per atom; nonmagnetic QE prints
separate angular-channel rows. This additive review admits only that specific
recorded rejection, validates unchanged raw artifacts against their retrieval
hashes, repeats SCF/force/projection checks, and verifies retention evidence.
The original runner outcome remains REJECTED. Frozen docs/89 estimators and
bands are reused unchanged from ru_pp_readout.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dft import research_batch as batch
from dft import ru_pp_readout as ru
from dft.hea_force_audit import audit_files as force_audit
from dft.projection_qc import projection_check

EVIDENCE = Path("results/research_readout_2026-09-17")
SPEC = Path("results/research_launch_2026-09-16/launch_spec.json")
REASON = "incomplete/failed projection"
SUFFIXES = (".out", ".run.in", ".projwfc.in", ".projwfc.out", ".qc.json", ".REJECTED")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def retention_check(inventory, job, row):
    found = [r for r in inventory["rows"] if r["stage"] == "ru_pp" and r["job"] == job["job"]]
    require(len(found) == 1 and found[0]["row"] == row, "retention row mismatch")
    prefix = "runs/" + job["dir"] + "/tmp_" + job["job"] + "/" + job["job"] + ".save/"
    entries = found[0]["retained"]
    xml = [r for r in entries if r["path"] == prefix + "data-file-schema.xml"]
    density = [r for r in entries if r["path"] in
               (prefix + "charge-density.dat", prefix + "charge-density.hdf5")]
    require(len(xml) == 1 and xml[0]["size"] > 0
            and re.fullmatch(r"[a-f0-9]{64}", xml[0].get("sha256") or ""), "retained XML not verified")
    require(len(density) == 1 and density[0]["size"] > 0, "retained density absent or empty")
    return {"status": "REMOTE_EXISTENCE_VERIFIED", "observed_at": inventory["at"],
            "files": entries, "limit": "XML hash recorded; density existence and size, not content hash"}


def review_job(root, job, row, spec, retrieved, inventory):
    root = Path(root)
    directory = root / "runs" / job["dir"]
    name = job["job"]
    artifact = lambda ext: directory / (name + ext)
    result = {"job": name, "row": row, "runner_status": "REJECTED", "review_status": "UNSCORED",
              "energy_eV": None, "reasons": [], "artifacts_sha256": {}}
    try:
        require(not artifact(".KILLED").exists(), "KILLED sidecar cannot be reconciled")
        for suffix in SUFFIXES:
            p = artifact(suffix)
            key = p.relative_to(root).as_posix()
            expected = [r for r in retrieved["files"] if r["path"] == key]
            require(len(expected) == 1 and ru.checksum(p) == expected[0]["sha256"], "retrieval hash mismatch: " + key)
            result["artifacts_sha256"][suffix] = expected[0]["sha256"]
        receipt = json.loads(artifact(".qc.json").read_text(encoding="utf-8"))
        result["runner_status"] = receipt.get("status")
        result["original_rejection_reason"] = receipt.get("reason")
        require(receipt.get("stage") == "ru_pp" and receipt.get("row") == row
                and receipt.get("job") == name and receipt.get("status") == "REJECTED"
                and receipt.get("reason") == REASON and artifact(".REJECTED").read_text().strip() == REASON,
                "not the identified projection-format rejection")
        for phase in ("scf_process", "projection_process"):
            record = receipt.get(phase, {})
            require(record.get("rc") == 0 and record.get("stop_reason") is None,
                    "unclean original process: " + phase)
        require(ru.checksum(artifact(".in")) == job["sha256"] == receipt.get("input_sha256"),
                "approved input identity mismatch")
        source_stem = name.removesuffix("_gbrv")
        source = root / "runs/a0/main/Ru" / (source_stem + ".in")
        require(not ru.deck_pair_check(artifact(".in"), source), "control is not the frozen ONCV deck substitution")
        original = artifact(".in").read_text()
        runtime = artifact(".run.in").read_text()
        paths = {}
        expected_runtime = original
        for field in ("outdir", "pseudo_dir"):
            matches = re.findall(r"(?m)^\s*" + field + r"\s*=\s*'([^']+)'", runtime)
            require(len(matches) == 1, "runtime path not unique: " + field)
            paths[field] = matches[0]
            expected_runtime, count = re.subn(r"(?m)^(\s*" + field + r"\s*=\s*)'[^']*'",
                                              lambda m: m[1] + "'" + matches[0] + "'", expected_runtime)
            require(count == 1, "approved path not unique: " + field)
        require(runtime == expected_runtime, "runtime changed beyond the two allowed path substitutions")
        require(paths["outdir"] == receipt["scratch_retained"], "runtime scratch differs from receipt")
        projection_input = "&PROJWFC\n prefix = '" + name + "'\n outdir = '" + paths["outdir"] + "'\n lsym = .true.\n/\n"
        require(artifact(".projwfc.in").read_text() == projection_input, "projection input differs")
        scf_text = artifact(".out").read_text(encoding="utf-8")
        scf = batch.scf_check(scf_text)
        require(scf == receipt["scf"], "raw SCF differs from original receipt")
        pseudos = re.findall(r"PseudoPot\.\s*#\s*\d+\s+for\s+\w+\s+read from file:\s*\n"
                             r"\s*([^\n]+)\n\s*MD5 check sum:\s*([a-f0-9]{32})", scf_text)
        actual = {Path(p.strip()).name: digest for p, digest in pseudos}
        expected = {p: spec["pseudo_md5"][p]
                    for p in set(re.findall(r"[A-Za-z0-9_.+-]+\.(?:UPF|upf)", original))}
        require(len(actual) == len(pseudos) and actual == expected, "raw pseudopotential hashes differ")
        force = force_audit(artifact(".run.in"), artifact(".out"))
        require(force["status"] == "VALID_SCF" and receipt.get("force", {}).get("status") == "VALID_SCF",
                "force/SCF validation failed")
        nat = int(re.search(r"(?m)^\s*nat\s*=\s*(\d+)", original)[1])
        projection = projection_check(artifact(".projwfc.out").read_text(), nat)
        require(projection["format"] == "split-angular-channels", "identified format defect not reproduced")
        retention = retention_check(inventory, job, row)
        result.update(review_status="VALIDATED_FORMAT_CORRECTION", energy_eV=scf["energy_Ry"] * ru.qe_qc.RY_EV,
                      scf=scf, projection=projection, retention=retention, pseudo_md5=actual,
                      fmax_free_eV_A=force["fmax_free_ev_A"], input_sha256=job["sha256"])
    except (ValueError, KeyError, TypeError, OSError, UnicodeError) as exc:
        result["reasons"].append(str(exc))
    return result


def build_review(root=ru.ROOT, retrieval=None, retention=None):
    root = Path(root)
    retrieval = Path(retrieval or root / EVIDENCE / "retrieval_initial.json")
    retention = Path(retention or root / EVIDENCE / "retained_scratch_initial.json")
    spec = json.loads((root / SPEC).read_text())
    retrieved = json.loads(retrieval.read_text())
    inventory = json.loads(retention.read_text())
    jobs = spec["stages"]["ru_pp"]["jobs"]
    expected = {s + "__" + u + "_gbrv" for s in ru.STATES for u in ru.RUNGS}
    require(len(jobs) == 12 and {j["job"] for j in jobs} == expected, "fixed Ru job set differs")
    result = ru.build_readout(root)
    controls = {u: {} for u in ru.RUNGS}
    reviews = []
    for row, job in enumerate(jobs, 1):
        review = review_job(root, job, row, spec, retrieved, inventory)
        reviews.append(review)
        state, u = job["job"].removesuffix("_gbrv").split("__")
        controls[u][state] = review["energy_eV"]
        result["records"][u + "/" + state]["GBRV_review"] = review
    result["primary_original_strict"] = result["primary"]
    result["primary"] = ru.primary_readout(controls)
    gas = {g: row["energy_eV"] for g, row in result["gas_records"].items()}
    for u in ru.RUNGS:
        scored = ru.eta_readout(controls[u], gas)
        if scored["status"] == "SCORED":
            scored["comparison"] = ru.secondary_band(u, scored["eta_V"])
        result["secondary"][u]["GBRV_reviewed"] = scored
    count = sum(r["review_status"] == "VALIDATED_FORMAT_CORRECTION" for r in reviews)
    bank_ready = all(r["ONCV"]["status"] == "SCOREABLE" for r in result["records"].values())
    ready = (count == 12 and bank_ready and result["ONCV_primary_agrees_with_printed_comparator"]
             and all(v is not None for v in gas.values()))
    result.update(schema_version=2, readiness="REVIEWED_COMPLETE" if ready else "INCOMPLETE",
                  original_runner_status="REJECTED", control_original_strict_scoreable_outputs=result["control_scoreable_outputs"],
                  control_reviewed_scoreable_outputs=count, ONCV_all_rows_scoreable=bank_ready,
                  review_method="Independent validation of unchanged artifacts; nonmagnetic angular rows grouped per atom",
                  review_evidence={"retrieval_sha256": ru.checksum(retrieval), "retention_sha256": ru.checksum(retention),
                                   "launch_spec_sha256": ru.checksum(root / SPEC),
                                   "review_code_sha256": ru.checksum(Path(__file__)),
                                   "projection_code_sha256": ru.checksum(Path(__file__).with_name("projection_qc.py"))},
                  reviews=reviews)
    result["limits"].append("Original scheduler/runner outcomes remain FAILED/REJECTED; only the documented projection-format parser defect is reconciled.")
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ru.ROOT)
    p.add_argument("--retrieval", type=Path)
    p.add_argument("--retention", type=Path)
    p.add_argument("--json", type=Path, required=True)
    args = p.parse_args(argv)
    target = args.json.resolve()
    require(target.name == "ru_pp_reviewed_readout_2026-09-17.json", "use the separate dated review artifact")
    require((args.root / "runs").resolve() not in target.parents, "no output inside run tree")
    result = build_review(args.root, args.retrieval, args.retention)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(result["readiness"] + ": " + str(result["control_reviewed_scoreable_outputs"]) + "/12 reviewed")
    return 0 if result["readiness"] == "REVIEWED_COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
