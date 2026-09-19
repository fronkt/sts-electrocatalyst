"""Focused clean-slab SCF diagnostic — decks, manifest, launch specification and Anvil wrappers.

Five fixed-geometry ``scf`` runs test whether a fresh atomic start reaches the
8.08e-8 Ry target that stopped array 20813525 task 1, under the frozen recipe
(mixing_beta 0.30) and under one mixing change (mixing_beta 0.10):

    Cu8Cr23Mn35Co34 s20/site2   coordinates entering cycle 5   beta 0.10 and 0.30
    Fe25Co25Ni25Cr25 s2/site0   pinned start coordinates       beta 0.10
    Ni31Cr29Cu5Mn35  s1/site0   pinned start coordinates       beta 0.10 and 0.30

Every other line of the pinned clean-slab decks is unchanged (cell, cutoffs,
k mesh, smearing, spin starts, Hubbard block, pseudopotentials, constraints).
The runs are executed by the existing ``src/dft/research_batch.py`` supervisor
(SCF iteration ceiling 126, wall cap 7,200 s, scratch preserved, no retry).
They are a numerical diagnostic; a converged SCF here is not a relaxed slab,
an adsorption reference or a census result.

Usage:
    python src/dft/lowtail_slab_scf_diag.py           # build decks, manifest, spec, wrappers
    python src/dft/lowtail_slab_scf_diag.py --check   # verify a rebuild is byte-identical
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SRC = Path("runs/hea/lowtail_validation_2026-09-16")
DST = Path("runs/hea/lowtail_slab_scf_diag_2026-09-19")
RES = Path("results/lowtail_slab_scf_diag_2026-09-19")
MANIFEST = Path("runs/m_lowtail_slab_scf_diag_2026-09-19.txt")
SPEC = RES / "launch_spec.json"
SLURM = Path("anvil/76_slab_scf_diag.slurm")
SUBMIT = Path("anvil/77_submit_slab_scf_diag.sh")
STAGE = "slab_scf_diag"
TARGET = "8.08d-8"
POSITIONS = RES / "cu8_cycle5_positions.txt"
BASE_SPEC = Path("results/research_launch_2026-09-16/launch_spec.json")

JOBS = [
    ("Cu8Cr23Mn35Co34__s20_site2", "slab_c5__b010", "cycle5", 0.10),
    ("Cu8Cr23Mn35Co34__s20_site2", "slab_c5__b030", "cycle5", 0.30),
    ("Fe25Co25Ni25Cr25__s2_site0", "slab_g0__b010", "start", 0.10),
    ("Ni31Cr29Cu5Mn35__s1_site0", "slab_g0__b030", "start", 0.30),
    ("Ni31Cr29Cu5Mn35__s1_site0", "slab_g0__b010", "start", 0.10),
]
PINNED_HELPERS = ["src/dft/research_batch.py", "src/dft/projection_qc.py", "src/dft/hea_force_audit.py",
                  "src/dft/queue_r1.sh"]
PROVENANCE = ["docs/research/lowtail-clean-slab-scf-stall-2026-09-19.md",
              "docs/research/lowtail-recovery-review-2026-09-19.md",
              str(RES / "cu8_cycle5_positions.txt"), str(RES / "cu8_cycle5_positions.json")]
SCF_SECONDS = 7200
PROJECTION_SECONDS = 900
MAX_ITERATIONS = 126
WALL_MINUTES = 150
CONCURRENCY = 2
NK = 8


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def split_deck(text: str):
    head, rest = text.split("ATOMIC_POSITIONS angstrom\n", 1)
    lines = rest.split("\n")
    nat = int(re.search(r"(?m)^\s*nat\s*=\s*(\d+)", head).group(1))
    block, tail = lines[:nat], "\n".join(lines[nat:])
    return head, block, tail


def traced_block(deck_block: list[str]) -> list[str]:
    """Replace coordinates with the cycle-5 coordinates; keep species order and constraint flags."""
    printed = POSITIONS.read_text(encoding="utf-8").splitlines()
    if len(printed) != len(deck_block):
        raise ValueError("position count mismatch")
    out = []
    for deck_line, printed_line in zip(deck_block, printed):
        d, p = deck_line.split(), printed_line.split()
        if d[0] != p[0]:
            raise ValueError("species order mismatch: " + deck_line)
        flags = d[4:7]
        pflags = p[4:7] if len(p) >= 7 else ["1", "1", "1"]
        if flags != pflags:
            raise ValueError("constraint flag mismatch: " + deck_line)
        if flags == ["0", "0", "0"]:
            for a, b in zip(d[1:4], p[1:4]):
                if abs(float(a) - float(b)) > 1e-8:
                    raise ValueError("fixed atom moved: " + deck_line)
        out.append("  " + " ".join([p[0]] + p[1:4] + flags))
    return out


def derive(text: str, job: str, beta: float, geometry: str) -> str:
    n = 0
    text, k = re.subn(r"calculation = 'relax'", "calculation = 'scf'", text); n += k
    text, k = re.subn(r"prefix = '[^']*'", f"prefix = '{job}'", text); n += k
    text, k = re.subn(r"conv_thr = 1\.0d-6", f"conv_thr = {TARGET}", text); n += k
    text, k = re.subn(r"mixing_beta = 0\.3\n", f"mixing_beta = {beta:.2f}\n", text); n += k
    text, k = re.subn(r"(  electron_maxstep = 300\n)",
                      "  startingwfc = 'atomic+random'\n  startingpot = 'atomic'\n\\1", text); n += k
    if n != 5:
        raise ValueError(f"expected five substitutions, made {n}")
    if geometry == "cycle5":
        head, block, tail = split_deck(text)
        text = head + "ATOMIC_POSITIONS angstrom\n" + "\n".join(traced_block(block)) + "\n" + tail
    return text


def write_or_check(path: Path, content: str, check: bool, seen: list) -> None:
    if check:
        if not path.exists() or path.read_bytes() != content.encode("utf-8"):
            raise SystemExit(f"CHECK FAILED {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    seen.append(str(path).replace("\\", "/"))


def build(check: bool) -> None:
    seen: list = []
    jobs, files = [], {}
    manifest_rows = []
    for site, job, geometry, beta in JOBS:
        src = SRC / site / "slab__atomic.in"
        deck = derive(src.read_text(encoding="utf-8"), job, beta, geometry)
        dst = DST / site / f"{job}.in"
        write_or_check(dst, deck, check, seen)
        digest = hashlib.sha256(deck.encode("utf-8")).hexdigest()
        rel_dir = str(DST / site).replace("\\", "/").replace("runs/", "", 1)
        jobs.append({"dir": rel_dir, "job": job, "nk": NK, "sha256": digest, "scf_seconds": SCF_SECONDS,
                     "projection_seconds": PROJECTION_SECONDS, "max_iterations": MAX_ITERATIONS,
                     "site": site, "geometry": geometry, "mixing_beta": beta, "source_deck": str(src).replace("\\", "/"),
                     "source_sha256": sha(src)})
        files[str(dst).replace("\\", "/")] = digest
        manifest_rows.append(f"{rel_dir} {job} .in {NK}")
    manifest = "\n".join([
        "# LICENSED 2026-09-19: focused clean-slab SCF diagnostic under the user's instruction of 2026-09-19 to continue the listed steps.",
        "# Specification: docs/research/lowtail-clean-slab-scf-stall-2026-09-19.md (review addendum) and docs/research/lowtail-recovery-review-2026-09-19.md.",
        "# Separate from array 20813525; fixed geometry; fresh atomic start; target 8.08e-8 Ry; ceiling 126 iterations / 7200 s; no retries.",
        "# SUBMIT WITH EXCLUDE=a024,a049,a050,a088,a196,a220,a223,a171,a120,a200",
        "# NP=128 NCONC=1",
    ] + manifest_rows) + "\n"
    write_or_check(MANIFEST, manifest, check, seen)
    files[str(MANIFEST)] = hashlib.sha256(manifest.encode("utf-8")).hexdigest()
    for helper in PINNED_HELPERS + PROVENANCE:
        files[helper] = sha(Path(helper))
    base = json.loads(BASE_SPEC.read_text(encoding="utf-8"))
    upf = set()
    for site, *_ in JOBS:
        upf |= set(re.findall(r"[A-Za-z0-9_.+-]+\.(?:UPF|upf)", (SRC / site / "slab__atomic.in").read_text(encoding="utf-8")))
    pseudo_md5 = {name: base["pseudo_md5"][name] for name in sorted(upf)}
    spec = {
        "schema": "research-batch-2026-09-16",
        "np": 128,
        "exclusions": base["exclusions"],
        "authorization": "User instruction 2026-09-19: continue the listed steps; diagnostic specified in the review addendum of the stall note.",
        "scope": "Fixed-geometry numerical diagnostic; not a relaxation, adsorption reference or census result; array 20813525 untouched.",
        "acceptance": {"tier_1": "estimated scf accuracy below 1e-6 Ry within 126 iterations",
                       "tier_2": "convergence achieved at 8.08e-8 Ry within 126 iterations (COMPLETE receipt)",
                       "readout": "src/dft/qe_relax_trace.py on each output; iteration of first crossing of 1e-6, 5e-7, 1e-7 recorded"},
        "files": files,
        "pseudo_md5": pseudo_md5,
        "stages": {STAGE: {"kind": STAGE, "manifest": str(MANIFEST), "concurrency": CONCURRENCY,
                           "wall_minutes": WALL_MINUTES, "jobs": jobs}},
        "ceiling": {"per_job_core_hours": round((SCF_SECONDS + PROJECTION_SECONDS) * 128 / 3600, 1),
                    "scheduler_core_hours": round(WALL_MINUTES * 60 * 128 / 3600 * len(jobs), 1)},
    }
    spec_text = json.dumps(spec, indent=1) + "\n"
    write_or_check(SPEC, spec_text, check, seen)
    spec_hash = hashlib.sha256(spec_text.encode("utf-8")).hexdigest()
    runner_hash = files["src/dft/research_batch.py"]
    slurm = f"""#!/bin/bash
# Focused clean-slab SCF diagnostic, 2026-09-19; scheduler resources set at submission.
#SBATCH -p shared
#SBATCH -N 1
#SBATCH -n 128
#SBATCH -o logs/slabdiag_%A_%a.out
#SBATCH -e logs/slabdiag_%A_%a.out
set -euo pipefail
[ "${{PROJECT:-}}" = /anvil/projects/x-che260157 ] || {{ echo 'REFUSE: project'; exit 2; }}
[ "${{SLURM_NTASKS:-}}" = 128 ] || {{ echo 'REFUSE: requires 128 ranks'; exit 2; }}
[ "${{STAGE:-}}" = {STAGE} ] || exit 2
ROOT="$PROJECT/sts"
SPEC="$ROOT/{SPEC}"
RUNNER="$ROOT/src/dft/research_batch.py"
check_hash() {{ [ "$(sha256sum "$1" | awk '{{print $1}}')" = "$2" ] || {{ echo "REFUSE: hash $1"; exit 2; }}; }}
check_hash "$SPEC" {spec_hash}
check_hash "$RUNNER" {runner_hash}
PYTHON=/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3
echo "STAGE $STAGE TASK ${{SLURM_ARRAY_TASK_ID:?}} NODE $(hostname) START $(date -u)"
exec "$PYTHON" "$RUNNER" --spec "$SPEC" --root "$ROOT" --stage "$STAGE" \\
     --row "$SLURM_ARRAY_TASK_ID" --pseudo "$PROJECT/pseudo" --qe "$PROJECT/qe/env"
"""
    submit = f"""#!/bin/bash
# Submit the clean-slab SCF diagnostic held; caller verifies scheduler fields before release. No retry/override.
set -euo pipefail
export PROJECT=/anvil/projects/x-che260157
export STAGE={STAGE}
ROOT="$PROJECT/sts"
SPEC="$ROOT/{SPEC}"
RUNNER="$ROOT/src/dft/research_batch.py"
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
    --export=ALL,PROJECT,STAGE "$ROOT/{SLURM}"
"""
    write_or_check(SLURM, slurm, check, seen)
    write_or_check(SUBMIT, submit, check, seen)
    receipt = {"spec_sha256": spec_hash, "runner_sha256": runner_hash, "written": seen,
               "slurm_sha256": hashlib.sha256(slurm.encode()).hexdigest(),
               "submit_sha256": hashlib.sha256(submit.encode()).hexdigest()}
    print(("CHECK OK " if check else "built ") + json.dumps(receipt, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    build(ap.parse_args().check)
