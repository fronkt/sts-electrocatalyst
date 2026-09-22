"""Licensed 2026-09-22 (second line): one relaxation restart from the low state, two seeded SCFs — decks, manifests, specifications, wrappers.

Readout of array 20845364 (docs/research/lowtail-clean-slab-scf-stall-2026-09-19.md, "Discriminating
SCFs from the retained density"): the relaxation's retained density carries a stationary second
state 94.7 meV above the fresh-start state, differing by an orbital reorientation of two
minority-spin d electrons on one surface Co (atom 20); its residual never falls below ≈3.5e-7 Ry.

Two batches, each executed by ``src/dft/research_batch_seeded.py`` (content-pinned scratch seed):

  slab_relax_seeded   one leg   Cu8Cr23Mn35Co34 s20/site2 clean slab, ``calculation = 'relax'`` at the
                                cycle-5 coordinates, density/occupations/PAW seeded from the LOW state
                                (array 20840139 task 2, ``tmp_slab_c5__b030``), production settings.
                                Tests whether the low orbital configuration is stable along the
                                relaxation and whether the leg then converges.
  slab_scf_seeded2    two legs  (1) Cu8 s20/site2 O_unrecon at the killed relaxation's last geometry,
                                seeded from its retained density; (2) Fe25Co25Ni25Cr25 s2/site0 clean
                                slab at the start geometry, seeded from the killed 0.10-mixing SCF's
                                retained density; both at production mixing (0.3, local-TF), fresh
                                wavefunctions, at each stall's own last threshold (5.53e-8 and 8.08e-8 Ry). Tests whether the same single-site
                                mechanism is at work in those two stalls.

Usage:
    python src/dft/lowtail_low_state_restart.py           # build both batches
    python src/dft/lowtail_low_state_restart.py --check   # verify a rebuild is byte-identical
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from lowtail_slab_scf_diag import (BASE_SPEC, MAX_ITERATIONS, NK, POSITIONS, PROJECTION_SECONDS, SRC, sha,
                                   split_deck, traced_block, write_or_check)

RUNNER = "src/dft/research_batch_seeded.py"
PINNED = [RUNNER, "src/dft/research_batch.py", "src/dft/projection_qc.py", "src/dft/hea_force_audit.py",
          "src/dft/hea_panel_readout.py", "src/dft/queue_r1.sh"]
DIAG_SPEC = Path("results/lowtail_slab_scf_diag_2026-09-19/launch_spec.json")
ARRAY_SPEC = Path("results/lowtail_dft_2026-09-18/launch_spec.json")
EXCLUDE = "a024,a049,a050,a088,a196,a220,a223,a171,a120,a200"
AUTHORIZATION = ("Entrant's election of 2026-09-22, from the session record: \"Restart from low state + seed two more\"; "
                 "A11.R3 dated line in docs/43, second addendum of 2026-09-22.")
CU8 = "Cu8Cr23Mn35Co34__s20_site2"
FE25 = "Fe25Co25Ni25Cr25__s2_site0"
O_UNRECON_POSITIONS = Path("results/lowtail_low_state_restart_2026-09-22/o_unrecon_last_positions.txt")

# Retained save directories on Anvil, hashed 2026-09-22 12:00 UTC; the runner copies the four files into a
# fresh <job>.save and refuses the job on any drift; sources are never written.
SEEDS = {
    "low_state_cu8_slab": {
        "save_dir": "runs/hea/lowtail_slab_scf_diag_2026-09-19/Cu8Cr23Mn35Co34__s20_site2/tmp_slab_c5__b030/slab_c5__b030.save",
        "files": {"charge-density.hdf5": "0aa143855c85a12e0e3ac2cc741b9b324faec9ca4ccbe85183b6550e4fe2f645",
                  "data-file-schema.xml": "2360316d4d5d759bfce9e8f6dbb024acd3315df12f1039a71fb28898ae2ae0fd",
                  "occup.txt": "0de270621acad688e345b1253cfef5dbe185a3deb1b65811aa3b4bbe44000f14",
                  "paw.txt": "0972e5ad8882198aff44573a91144e50b370786454b68004c330330ab8a8449d"},
        "state": "fresh-start SCF converged at 8.08e-8 Ry, -7551.86633525 Ry (array 20840139 task 2)"},
    "retained_cu8_o_unrecon": {
        "save_dir": ("runs/hea/lowtail_validation_2026-09-16/Cu8Cr23Mn35Co34__s20_site2/tmp_O_unrecon__atomic/"
                     "lt__Cu8Cr23Mn35Co34__s20_site2__O_unrecon__atomic.save"),
        "files": {"charge-density.hdf5": "32c22017ffd1e0d31fc128274866c713c449b60d9c2e837b929a9e290234870d",
                  "data-file-schema.xml": "3573a520d5b9e8bb789eff3df5327eb1ece63d511bf6b8e847cb472932923b13",
                  "occup.txt": "b3b5b66bbea492c738a632cc24c4834d667382dad8d8dabb693c3d6294c7c607",
                  "paw.txt": "ab5da29c6180701d8df99d0f18d7eb949013ce1b2009ef05a8f339276562b504"},
        "state": "array 20813525 task 3, KILLED at the SCF iteration ceiling after 606 iterations"},
    "retained_fe25_slab_b010": {
        "save_dir": "runs/hea/lowtail_slab_scf_diag_2026-09-19/Fe25Co25Ni25Cr25__s2_site0/tmp_slab_g0__b010/slab_g0__b010.save",
        "files": {"charge-density.hdf5": "d00704b594f66fe779e8d32c20549623c3a07508c954d19bf4bdce12c34a0a01",
                  "data-file-schema.xml": "4c0b6ca3c8da7c25052299553d09efbe50b1b62e0bdf841de0918df2da7391c8",
                  "occup.txt": "83b0b90be4af700a4d80a92546681136bdfcb0fc0ffbfc0b8fb9ea6d486f4b7f",
                  "paw.txt": "da25f58bea466ed71915d28dcf671bde067e1849e83166a46e11b7d1f2d1a785"},
        "state": "array 20840139 task 3 (mixing 0.10), KILLED at the 126-iteration cap, floor 1.2e-5 Ry"},
}

BATCHES = {
    "slab_relax_seeded": dict(
        res=Path("results/lowtail_low_state_restart_2026-09-22/relax"),
        dst=Path("runs/hea/lowtail_low_state_restart_2026-09-22"),
        manifest=Path("runs/m_lowtail_slab_relax_seeded_2026-09-22.txt"),
        slurm=Path("anvil/80_slab_relax_seeded.slurm"), submit=Path("anvil/81_submit_slab_relax_seeded.sh"),
        kind="relax", concurrency=1, wall_minutes=780, scf_seconds=46000, log="slabrelaxseed",
        jobs=[dict(site=CU8, job="slab_c5low__relax", source="slab__atomic.in", geometry="cycle5",
                   seed="low_state_cu8_slab", conv_thr=None)]),
    "slab_scf_seeded2": dict(
        res=Path("results/lowtail_low_state_restart_2026-09-22/scf"),
        dst=Path("runs/hea/lowtail_low_state_restart_2026-09-22"),
        manifest=Path("runs/m_lowtail_slab_scf_seeded2_2026-09-22.txt"),
        slurm=Path("anvil/82_slab_scf_seeded2.slurm"), submit=Path("anvil/83_submit_slab_scf_seeded2.sh"),
        kind="slab_scf_seeded2", concurrency=2, wall_minutes=150, scf_seconds=7200, log="slabscfseed2",
        jobs=[dict(site=CU8, job="O_unrecon_last__rho", source="O_unrecon__atomic.in", geometry="o_unrecon_last",
                   seed="retained_cu8_o_unrecon", conv_thr="5.53d-8"),  # the killed relaxation's own last announced threshold
              dict(site=FE25, job="slab_g0__rho", source="slab__atomic.in", geometry="start",
                   seed="retained_fe25_slab_b010", conv_thr="8.08d-8")]),
}


def replace_positions(text: str, rows: list[str]) -> str:
    head, block, tail = split_deck(text)
    if len(rows) != len(block):
        raise ValueError("position count mismatch")
    out = []
    for deck_line, printed_line in zip(block, rows):
        d, p = deck_line.split(), printed_line.split()
        if d[0] != p[0]:
            raise ValueError("species order mismatch: " + deck_line)
        flags = d[4:7]
        if flags == ["0", "0", "0"]:
            for a, b in zip(d[1:4], p[1:4]):
                if abs(float(a) - float(b)) > 1e-8:
                    raise ValueError("fixed atom moved: " + deck_line)
        out.append("  " + " ".join([p[0]] + p[1:4] + flags))
    return head + "ATOMIC_POSITIONS angstrom\n" + "\n".join(out) + "\n" + tail


def derive_leg(text: str, job: str, kind: str, geometry: str, conv_thr) -> str:
    n = 0
    if kind != "relax":
        text, k = re.subn(r"calculation = 'relax'", "calculation = 'scf'", text); n += k
        if k != 1:
            raise ValueError("calculation line not unique")
    text, k = re.subn(r"prefix = '[^']*'", f"prefix = '{job}'", text); n += k
    if conv_thr is not None:
        text, k = re.subn(r"conv_thr = 1\.0d-6", f"conv_thr = {conv_thr}", text); n += k
    text, k = re.subn(r"(  electron_maxstep = 300\n)",
                      "  startingwfc = 'atomic+random'\n  startingpot = 'file'\n\\1", text); n += k
    if k != 1:
        raise ValueError("electrons namelist anchor not unique")
    if geometry == "cycle5":
        head, block, tail = split_deck(text)
        text = head + "ATOMIC_POSITIONS angstrom\n" + "\n".join(traced_block(block)) + "\n" + tail
    elif geometry == "o_unrecon_last":
        text = replace_positions(text, O_UNRECON_POSITIONS.read_text(encoding="utf-8").splitlines())
    elif geometry != "start":
        raise ValueError("unknown geometry " + geometry)
    return text


def wrappers(stage: str, spec_path: Path, spec_hash: str, runner_hash: str, slurm_path: Path, log: str, title: str):
    slurm = f"""#!/bin/bash
# {title}; scheduler resources set at submission.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -o logs/{log}_%A_%a.out
#SBATCH -e logs/{log}_%A_%a.out
set -euo pipefail
[ "${{PROJECT:-}}" = /anvil/projects/x-che260157 ] || {{ echo 'REFUSE: project'; exit 2; }}
[ "${{SLURM_NTASKS:-}}" = 128 ] || {{ echo 'REFUSE: requires 128 ranks'; exit 2; }}
[ "${{STAGE:-}}" = {stage} ] || exit 2
ROOT="$PROJECT/sts"
SPEC="$ROOT/{spec_path.as_posix()}"
RUNNER="$ROOT/{RUNNER}"
check_hash() {{ [ "$(sha256sum "$1" | awk '{{print $1}}')" = "$2" ] || {{ echo "REFUSE: hash $1"; exit 2; }}; }}
check_hash "$SPEC" {spec_hash}
check_hash "$RUNNER" {runner_hash}
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
echo "STAGE $STAGE TASK ${{SLURM_ARRAY_TASK_ID:?}} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \\
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
"""
    submit = f"""#!/bin/bash
# Submit {title} held; caller verifies scheduler fields before release. No retry/override.
set -euo pipefail
export PROJECT=/anvil/projects/x-che260157
export STAGE={stage}
ROOT="$PROJECT/sts"
SPEC="$ROOT/{spec_path.as_posix()}"
RUNNER="$ROOT/{RUNNER}"
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
check_hash() {{ [ "$(sha256sum "$1" | awk '{{print $1}}')" = "$2" ] || {{ echo "REFUSE: hash $1"; exit 2; }}; }}
check_hash "$SPEC" {spec_hash}
check_hash "$RUNNER" {runner_hash}
[ -f "$PROJECT/parity/PARITY_PASS" ] || {{ echo 'REFUSE: parity absent'; exit 2; }}
[ -f "$ROOT/anvil/pseudo_md5_preflight_2026-08-23.md" ] || exit 2
"$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" --pseudo "$PROJECT/pseudo" --preflight
read -r MANIFEST N CONC MINUTES EXCLUDE < <("$PYTHON" -c 'import json,sys; s=json.load(open(sys.argv[1])); g=s["stages"][sys.argv[2]]; print(g["manifest"],len(g["jobs"]),g["concurrency"],g["wall_minutes"],s["exclusions"])' "$SPEC" "$STAGE")
export RUNS="$ROOT/runs" QE_PREFIX="$PROJECT/qe/env" PSEUDO_DIR="$PROJECT/pseudo"
PREFLIGHT_ONLY=1 LOG=/dev/stdout bash "$ROOT/src/dft/queue_r1.sh" "$ROOT/$MANIFEST" 128 1
cd "$PROJECT"
mkdir -p logs
echo "HELD $STAGE tasks=$N concurrency=$CONC minutes=$MINUTES cores=128"
sbatch --parsable --hold --no-requeue -A che260157 -p shared -N 1 -n 128 \\
    --cpus-per-task=1 --mem=237G --time="$MINUTES" --exclude="$EXCLUDE" \\
    --job-name="research-$STAGE" --array="1-$N%$CONC" \\
    --export=ALL,PROJECT,STAGE "$ROOT/{slurm_path.as_posix()}"
"""
    return slurm, submit


def build(check: bool) -> None:
    seen: list = []
    base = json.loads(BASE_SPEC.read_text(encoding="utf-8"))
    diag = json.loads(DIAG_SPEC.read_text(encoding="utf-8"))
    array = json.loads(ARRAY_SPEC.read_text(encoding="utf-8"))
    receipts = {}
    for stage, b in BATCHES.items():
        jobs, files, manifest_rows, upf = [], {}, [], set()
        for j in b["jobs"]:
            src = SRC / j["site"] / j["source"]
            text = src.read_text(encoding="utf-8")
            upf |= set(re.findall(r"[A-Za-z0-9_.+-]+\.(?:UPF|upf)", text))
            deck = derive_leg(text, j["job"], b["kind"], j["geometry"], j["conv_thr"])
            dst = b["dst"] / j["site"] / f"{j['job']}.in"
            write_or_check(dst, deck, check, seen)
            digest = hashlib.sha256(deck.encode("utf-8")).hexdigest()
            rel_dir = str(b["dst"] / j["site"]).replace("\\", "/").replace("runs/", "", 1)
            seed = SEEDS[j["seed"]]
            jobs.append({"dir": rel_dir, "job": j["job"], "nk": NK, "sha256": digest, "scf_seconds": b["scf_seconds"],
                         "projection_seconds": PROJECTION_SECONDS, "max_iterations": MAX_ITERATIONS, "site": j["site"],
                         "geometry": j["geometry"], "mixing_beta": 0.30, "mixing_mode": "local-TF",
                         "startingpot": "file", "startingwfc": "atomic+random",
                         "scratch_source": {"save_dir": seed["save_dir"], "files": seed["files"]},
                         "seed_state": seed["state"], "source_deck": str(src).replace("\\", "/"), "source_sha256": sha(src)})
            files[str(dst).replace("\\", "/")] = digest
            manifest_rows.append(f"{rel_dir} {j['job']} .in {NK}")
        manifest = "\n".join([
            f"# LICENSED 2026-09-22: {stage} — the entrant's election of 2026-09-22 (\"Restart from low state + seed two more\"),",
            "# dated A11.R3 line in docs/43, second addendum of 2026-09-22. Densities seeded from retained save directories pinned by content;",
            "# executed by src/dft/research_batch_seeded.py; SCF iteration ceiling 126; no retries; a stopped leg is no result.",
            f"# SUBMIT WITH EXCLUDE={EXCLUDE}",
            "# NP=128 NCONC=1",
        ] + manifest_rows) + "\n"
        write_or_check(b["manifest"], manifest, check, seen)
        files[b["manifest"].as_posix()] = hashlib.sha256(manifest.encode("utf-8")).hexdigest()
        for helper in PINNED:
            files[helper] = sha(Path(helper))
        for positions in (POSITIONS, POSITIONS.with_suffix(".json")):
            files[positions.as_posix()] = sha(positions)
        if any(j["geometry"] == "o_unrecon_last" for j in b["jobs"]):
            files[O_UNRECON_POSITIONS.as_posix()] = sha(O_UNRECON_POSITIONS)
        pseudo_md5 = {name: base["pseudo_md5"][name] for name in sorted(upf)}
        per_job_ceiling = round((b["scf_seconds"] + PROJECTION_SECONDS) * 128 / 3600, 1)
        spec = {
            "schema": "research-batch-2026-09-16", "np": 128, "exclusions": EXCLUDE,
            "authorization": AUTHORIZATION,
            "scope": ("Seeded numerical diagnostic under HEA-4 supervision; densities read by copy from retained scratch, "
                      "sources never written; arrays 20813525, 20840139 and 20845364 untouched. A converged relaxation "
                      "leg here is a numerical outcome for the stall question, not a census result or a claim."),
            "acceptance": dict(diag["acceptance"], relax=(
                "COMPLETE requires hea_panel_readout.parse_out(allow_relax) CONVERGED with every SCF within 126 iterations; "
                "the readout compares the first-cycle energy with -7551.86633525 Ry (low state) and -7551.8594 Ry (stagnating state) "
                "and reports whether the orbital configuration of atom 20 (spin-down occupation diagonal) is retained"),
                seeded_scf=("COMPLETE near the fresh-start energy of the same geometry reads as the retained density lying in "
                            "the low basin; KILLED with a flat residual reads as a stationary second state; the atom-resolved "
                            "occupation comparison against the retained occup.txt is the readout")),
            "reference_energies_Ry": {"cu8_slab_cycle5_low_state": -7551.86633525, "cu8_slab_cycle5_stagnating": -7551.85936520,
                                      "cu8_slab_relax_cycle4_converged": -7551.85641872},
            "seeds": {k: SEEDS[k] for k in {j["seed"] for j in b["jobs"]}},
            "relaxation_supervisor": array["jobs"][0]["supervisor_limits"] if b["kind"] == "relax" else None,
            "files": files, "pseudo_md5": pseudo_md5,
            "stages": {stage: {"kind": b["kind"], "manifest": b["manifest"].as_posix(), "concurrency": b["concurrency"],
                               "wall_minutes": b["wall_minutes"], "jobs": jobs}},
            "ceiling": {"per_job_core_hours": per_job_ceiling,
                        "scheduler_core_hours": round(b["wall_minutes"] * 60 * 128 / 3600 * len(jobs), 1),
                        "planning_core_hours": 590.0 if b["kind"] == "relax" else 130.0 * len(jobs)},
        }
        spec_path = b["res"] / "launch_spec.json"
        spec_text = json.dumps(spec, indent=1) + "\n"
        write_or_check(spec_path, spec_text, check, seen)
        spec_hash = hashlib.sha256(spec_text.encode("utf-8")).hexdigest()
        slurm, submit = wrappers(stage, spec_path, spec_hash, files[RUNNER], b["slurm"], b["log"],
                                 "Low-state relaxation restart, 2026-09-22" if b["kind"] == "relax" else "Seeded SCFs on two more retained densities, 2026-09-22")
        write_or_check(b["slurm"], slurm, check, seen)
        write_or_check(b["submit"], submit, check, seen)
        receipts[stage] = {"spec_sha256": spec_hash, "runner_sha256": files[RUNNER], "jobs": len(jobs),
                           "slurm_sha256": hashlib.sha256(slurm.encode()).hexdigest(),
                           "submit_sha256": hashlib.sha256(submit.encode()).hexdigest()}
    print(("CHECK OK " if check else "built ") + json.dumps({"written": seen, "batches": receipts}, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    build(ap.parse_args().check)
