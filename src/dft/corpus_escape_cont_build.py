#!/usr/bin/env python3
"""Corpus escape continuation (2026-11-02): restart tier 1a's six escape relaxations from their last computed geometry.

Design note of record: docs/research/corpus-escape-2026-11-01.md, section "Tier 1a continuation". All six tier 1a
escape arms stopped unconverged (five at nstep = 100, RuO2 at the runner's wall ceiling after 92 steps). This file
launches nothing.

Per case one deck, <metal>__OOH-relax__cont. It is the tier 1a escape deck line for line, except
  - prefix = the new job name (runner contract: prefix = job name), and
  - each free atom's coordinates = the escape run's last geometry with an energy, i.e. the ATOMIC_POSITIONS block
    printed before the last '!' line (the block printed after it is the optimizer's next, uncomputed proposal).
Fixed atoms are checked unmoved in the escape output and their deck lines are kept verbatim. Every other setting
(nosym, forc_conv_thr 1e-4, nstep 100, k mesh, cutoffs, smearing, mixing, UPF files) is the escape deck's; the guard
re-parses each emitted deck to prove it. The held arms are not rerun: the rule pairs each continuation with its
tier 1a held output.

Inputs, all read-only: results/corpus_escape_2026-11-01/launch_spec.json (stage tier1a_escape: deck pins, runner pins,
QE pins, exclusions, UPF MD5s), results/corpus_escape_2026-11-01/cases.json, and the escape outputs in
runs/corpus_escape_2026-11-01/ (sha256 recorded in the new spec and cases).

    python src/dft/corpus_escape_cont_build.py --decision "<Frank's words>"   # write (refuses to overwrite differing files)
    python src/dft/corpus_escape_cont_build.py --decision "<Frank's words>" --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_escape_build as ceb  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DATE = "2026-11-02"
TAG = "corpus_escape_cont_2026-11-02"
DESIGN = ceb.DESIGN
PACKAGE = "results/" + TAG
RUN_DIR = TAG
SOURCE_PACKAGE = "results/corpus_escape_2026-11-01"
SOURCE_SPEC_REL = SOURCE_PACKAGE + "/launch_spec.json"
SOURCE_CASES_REL = SOURCE_PACKAGE + "/cases.json"
SOURCE_STAGE = "tier1a_escape"
GROUP = "tier1a_cont"
STAGE = GROUP + "_escape"          # launch_ops names the array from the suffix: ce-esc-tier1a_cont
SLURM_REL = "anvil/107_corpus_escape_cont.slurm"
REMOTE = "/anvil/projects/x-che260157/sts_" + TAG
WALL_MINUTES = 420                 # 7 h: RuO2, the slowest, used 222 s per step, so 100 steps take about 6.2 h
SCF_SECONDS = WALL_MINUTES * 60 - ceb.PROJECTION_SECONDS - 300   # the source builder's convention
BALANCE_2026_11_02 = 5444.4        # mybalance, 2026-11-02 20:13Z, after tier 1a
ENERGY = re.compile(r"^!\s+total energy\s+=\s+([-0-9.]+)\s+Ry", re.M)
OUT_POS = re.compile(r"ATOMIC_POSITIONS \(crystal\)\s*\n")
PREFIX = re.compile(r"^(\s*)prefix\s*=\s*'([^']+)'\s*$")


class Refuse(Exception):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def last_computed(text: str, nat: int) -> dict:
    """The last geometry with an energy: the ATOMIC_POSITIONS block printed before the last '!' line."""
    energies = list(ENERGY.finditer(text))
    if not energies:
        raise Refuse("no SCF energy in the escape output")
    before = [m for m in OUT_POS.finditer(text) if m.start() < energies[-1].start()]
    if len(before) != len(energies) - 1:
        raise Refuse("%d energies but %d geometries before the last one" % (len(energies), len(before)))
    rows = []
    for raw in text[before[-1].end():].splitlines()[:nat]:
        t = raw.split()
        if len(t) not in (4, 7):
            raise Refuse("geometry block malformed: " + raw)
        rows.append({"label": t[0], "s": [float(v) for v in t[1:4]], "if_pos": " ".join(t[4:7]) if len(t) == 7 else None})
    if len(rows) != nat:
        raise Refuse("geometry block has %d of %d atoms" % (len(rows), nat))
    return {"n_scf": len(energies), "E_Ry": float(energies[-1].group(1)), "atoms": rows}


def cont_deck(src_text: str, dep: dict, name: str, positions) -> str:
    """The escape deck with the prefix renamed and every free atom's coordinates replaced; nothing else touched."""
    lines = src_text.split("\n")
    hits = [i for i, line in enumerate(lines) if PREFIX.match(line)]
    if len(hits) != 1:
        raise Refuse("escape deck without exactly one prefix line")
    lines[hits[0]] = "%sprefix = '%s'" % (PREFIX.match(lines[hits[0]]).group(1), name)
    head = [i for i, line in enumerate(lines) if line.strip().upper().startswith("ATOMIC_POSITIONS")]
    if len(head) != 1:
        raise Refuse("escape deck without exactly one ATOMIC_POSITIONS card")
    for k, (atom, s) in enumerate(zip(dep["atoms"], positions)):
        if atom["if_pos"] == "1 1 1":
            lines[head[0] + 1 + k] = ceb.fmt_pos(atom["label"], s, atom["if_pos"])
    return "\n".join(lines)


def guard(text: str, src_text: str, name: str, positions) -> None:
    new, src = ceb.parse_pw_input(text), ceb.parse_pw_input(src_text)
    if new["order"] != src["order"]:
        raise Refuse(name + ": namelist order changed")
    for nl in src["order"]:
        a = [(k, v) for k, v in new["namelists"][nl] if k.lower() != "prefix"]
        b = [(k, v) for k, v in src["namelists"][nl] if k.lower() != "prefix"]
        if a != b:
            raise Refuse("%s: &%s differs from the escape deck" % (name, nl))
    if dict(new["namelists"]["CONTROL"]).get("prefix") != "'%s'" % name:
        raise Refuse(name + ": prefix is not the job name")
    if dict(new["namelists"]["SYSTEM"]).get("nosym") != ".true.":
        raise Refuse(name + ": nosym missing")
    for card in ("K_POINTS", "ATOMIC_SPECIES", "CELL_PARAMETERS"):
        if new["cards"][card] != src["cards"][card]:
            raise Refuse("%s: card %s differs from the escape deck" % (name, card))
    if new["cards"]["ATOMIC_POSITIONS"]["header"] != src["cards"]["ATOMIC_POSITIONS"]["header"]:
        raise Refuse(name + ": ATOMIC_POSITIONS units changed")
    for a, b, s in zip(new["atoms"], src["atoms"], positions):
        if a["label"] != b["label"] or a["if_pos"] != b["if_pos"]:
            raise Refuse(name + ": species or if_pos order differs from the escape deck")
        want = b["s"] if b["if_pos"] == "0 0 0" else s
        if any(abs(x - y) > 6e-10 for x, y in zip(a["s"], want)):
            raise Refuse(name + ": emitted coordinate differs from the intended one")
    changed = [x for x, y in zip(text.split("\n"), src_text.split("\n")) if x != y]
    free = sum(b["if_pos"] == "1 1 1" for b in src["atoms"])
    if len(text.split("\n")) != len(src_text.split("\n")) or len(changed) > free + 1:
        raise Refuse(name + ": more lines changed than the prefix and the free atoms")


def build(root: Path, decision: dict) -> dict:
    spec0 = json.loads((root / SOURCE_SPEC_REL).read_text(encoding="utf-8"))
    cases0 = {c["decks"]["escape"]: c for c in json.loads((root / SOURCE_CASES_REL).read_text(encoding="utf-8"))["cases"]}
    for rel in ceb.RUNNER_FILES:
        if sha256((root / rel).read_bytes()) != spec0["files"][rel]:
            raise Refuse("runner file differs from the tier 1a pin: " + rel)
    files, jobs, cases = {}, [], []
    for job0 in spec0["stages"][SOURCE_STAGE]["jobs"]:
        deck_rel = "runs/%s/%s.in" % (job0["dir"], job0["job"])
        src_bytes = (root / deck_rel).read_bytes()
        if sha256(src_bytes) != job0["sha256"] or spec0["files"].get(deck_rel) != job0["sha256"]:
            raise Refuse("escape deck differs from its pin: " + deck_rel)
        case0 = cases0[deck_rel]
        out_rel = deck_rel[:-3] + ".out"
        out_bytes = (root / out_rel).read_bytes()
        receipt = json.loads((root / (deck_rel[:-3] + ".qc.json")).read_text(encoding="utf-8"))
        if receipt.get("input_sha256") != job0["sha256"] or receipt.get("status") == "COMPLETE":
            raise Refuse("escape receipt does not belong to this deck or the run converged: " + deck_rel)
        src_text = src_bytes.decode("utf-8")
        dep = ceb.parse_pw_input(src_text)
        last = last_computed(out_bytes.decode("utf-8", "replace"), dep["nat"])
        for a, p in zip(dep["atoms"], last["atoms"]):
            if a["label"] != p["label"]:
                raise Refuse(job0["job"] + ": output species order differs from the deck")
            if a["if_pos"] not in ("0 0 0", "1 1 1"):
                raise Refuse(job0["job"] + ": partly fixed atom")
            if a["if_pos"] == "0 0 0" and any(abs(x - y) > 1e-9 for x, y in zip(a["s"], p["s"])):
                raise Refuse(job0["job"] + ": a fixed atom moved")
        positions = [[round(v, 9) for v in p["s"]] for p in last["atoms"]]
        name = "%s__%s__cont" % (job0["metal"], job0["census_job"])
        text = cont_deck(src_text, dep, name, positions)
        guard(text, src_text, name, positions)
        data = text.encode("utf-8")
        if b"\r" in data:
            raise Refuse("CR byte in " + name)
        rel = "runs/%s/%s.in" % (RUN_DIR, name)
        files[rel] = data
        L = ceb.lengths(dep["cell"])
        axis, plane = ceb.AXIS_INDEX[case0["locked_axis"]], case0["plane_crystal"]
        off = max(abs(ceb.min_image(positions[i][axis] - plane)) * L[axis] for i in case0["adsorbate_index0"])
        continues = {"job": job0["job"], "deck": deck_rel, "deck_sha256": job0["sha256"], "output": out_rel,
                     "output_sha256": sha256(out_bytes), "receipt_status": receipt.get("status"),
                     "receipt_reason": receipt.get("reason"), "n_scf": last["n_scf"], "last_E_Ry": last["E_Ry"],
                     "geometry": "last geometry with an energy (block printed before the last '!' line)"}
        jobs.append({"dir": RUN_DIR, "job": name, "sha256": sha256(data), "nk": job0["nk"],
                     "scf_seconds": SCF_SECONDS, "projection_seconds": job0["projection_seconds"],
                     "max_iterations": job0["max_iterations"], "recipe": "relax", "role": "corpus_escape_cont",
                     "arm": "escape_cont", "tier": job0["tier"], "launch_group": GROUP, "metal": job0["metal"],
                     "census_job": job0["census_job"], "locked_axis": job0["locked_axis"],
                     "source_output": job0["source_output"], "source_output_sha256": job0["source_output_sha256"],
                     "continues": continues})
        record = {k: case0[k] for k in ("tier", "metal", "job", "state", "locked_axis", "plane_crystal",
                                        "adsorbate_index0", "adsorbate_index1", "nat", "nspin", "tot_magnetization",
                                        "cell_lengths_A", "deposited_n_symops", "displacement", "census_output")}
        record.update(launch_group=GROUP, continues=continues,
                      start={"max_adsorbate_off_plane_A": round(off, 6)},
                      decks={"held": case0["decks"]["held"], "escape": rel, "escape_tier1a": deck_rel})
        cases.append(record)
    manifest = "runs/m_%s_%s.txt" % (TAG, STAGE)
    head = ["# APPROVED %s: %s (Frank: \"%s\")" % (decision["date"], DESIGN, decision["words"]),
            "# Corpus escape continuation (%s): tier 1a escape relaxations restarted from their last computed "
            "geometry; exploratory, post-census; no automatic retries." % STAGE,
            "# SUBMIT WITH EXCLUDE=" + spec0["exclusions"],
            "# NP=128 NCONC=1"]
    files[manifest] = ("\n".join(head + ["%s %s .in %d" % (j["dir"], j["job"], j["nk"]) for j in jobs]) + "\n").encode()
    ceiling = len(jobs) * WALL_MINUTES * 128 // 60
    pinned = {p: sha256(d) for p, d in files.items()}
    pinned.update({rel: spec0["files"][rel] for rel in ceb.RUNNER_FILES})
    spec = {
        "schema": spec0["schema"], "np": spec0["np"], "exclusions": spec0["exclusions"], "date": DATE,
        "design": DESIGN,
        "decision_ref": "Frank, %s: \"%s\"" % (decision["date"], decision["words"]),
        "status": "exploratory, post-census; continuation decided after the tier 1a readout; results reported "
                  "whatever they show",
        "continues": {"spec": SOURCE_SPEC_REL, "spec_sha256": sha256((root / SOURCE_SPEC_REL).read_bytes()),
                      "stage": SOURCE_STAGE},
        "allocation": {"account": "che260157", "partition": "wholenode", "cores_per_task": 128,
                       "balance_cpu_su_2026_11_02": BALANCE_2026_11_02,
                       "stage_ceilings_cpu_su": {STAGE: ceiling}, "group_ceilings_cpu_su": {GROUP: ceiling}},
        "launch_groups": {GROUP: {"tier": "tier1", "deposited_converged": True, "stages": [STAGE]}},
        "qe_binaries_sha256": spec0["qe_binaries_sha256"],
        "files": dict(sorted(pinned.items())),
        "pseudo_md5": spec0["pseudo_md5"],
        "pseudo_substitution": spec0["pseudo_substitution"],
        "stages": {STAGE: {"kind": "relax", "manifest": manifest, "concurrency": len(jobs),
                           "wall_minutes": WALL_MINUTES, "jobs": jobs}},
    }
    spec_bytes = (json.dumps(spec, indent=2) + "\n").encode("utf-8")
    files[PACKAGE + "/launch_spec.json"] = spec_bytes
    files[SLURM_REL] = slurm_text(sha256(spec_bytes), spec0["files"]["src/dft/research_batch_seeded.py"]).encode()
    table = {"schema": "corpus-escape-cont-cases-v1", "date": DATE, "design": DESIGN, "continues": SOURCE_CASES_REL,
             "wall_minutes": WALL_MINUTES, "scf_seconds": SCF_SECONDS, "group_ceiling_cpu_su": ceiling,
             "cases": cases}
    files[PACKAGE + "/cases.json"] = (json.dumps(table, indent=2) + "\n").encode("utf-8")
    return files


def slurm_text(spec_sha: str, runner_sha: str) -> str:
    return f"""#!/bin/bash
# Corpus escape continuation ({DESIGN}, section "Tier 1a continuation"). The six tier 1a escape relaxations (nosym)
# restarted from their last computed geometry, one pw.x relaxation per array task through the pinned seeded runner as
# a stage of kind "relax". Resources, held state, time limit and the array throttle are set at submission and
# validated before release. No retry or requeue.
#SBATCH --account=che260157
#SBATCH --partition=wholenode
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=200G
#SBATCH --no-requeue
#SBATCH --output={REMOTE}/logs/corpus_escape_cont_%A_%a.log
#SBATCH --error={REMOTE}/logs/corpus_escape_cont_%A_%a.log
set -euo pipefail
PROJECT=/anvil/projects/x-che260157
ROOT="$PROJECT/sts_{TAG}"
SPEC="$ROOT/{PACKAGE}/launch_spec.json"
RUNNER="$ROOT/src/dft/research_batch_seeded.py"
PYTHON={ceb.PYTHON_ANVIL}
[ "${{SLURM_NTASKS:-}}" = 128 ] || {{ echo 'REFUSE: requires 128 ranks'; exit 2; }}
case "${{STAGE:-}}" in {STAGE}) ;; *) echo 'REFUSE: stage'; exit 2;; esac
check_hash() {{ [ "$(sha256sum "$1" | awk '{{print $1}}')" = "$2" ] || {{ echo "REFUSE: hash $1"; exit 2; }}; }}
check_hash "$SPEC" {spec_sha}
check_hash "$RUNNER" {runner_sha}
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 OMP_DYNAMIC=FALSE MKL_DYNAMIC=FALSE
echo "STAGE $STAGE TASK ${{SLURM_ARRAY_TASK_ID:?}} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \\
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$ROOT/pseudo" --qe "$PROJECT/qe/env"
"""


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--decision", required=True, help="Frank's words licensing the continuation")
    p.add_argument("--decision-date", default=DATE)
    p.add_argument("--check", action="store_true", help="compare a fresh build with the files on disk")
    a = p.parse_args(argv)
    try:
        files = build(ROOT, {"words": a.decision, "date": a.decision_date})
    except (Refuse, ceb.Refuse) as error:
        print("REFUSE: " + str(error))
        return 2
    problems, written = [], []
    for rel, data in files.items():
        if b"\r" in data:
            raise SystemExit("CR byte in " + rel)
        path = ROOT / rel
        if a.check:
            if not path.exists() or path.read_bytes() != data:
                problems.append(rel)
            continue
        if path.exists() and path.read_bytes() == data:
            continue
        if path.exists():
            raise SystemExit("refusing to overwrite a differing file: " + rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)
        written.append(rel)
    print(json.dumps({"files": len(files), "mismatches": problems, "written": written,
                      "spec_sha256": sha256(files[PACKAGE + "/launch_spec.json"])}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
