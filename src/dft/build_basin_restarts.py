"""Re-relax the states that GATE 1 caught in the wrong SCF solution (docs/41 s6d/s6e).

The defect these repair is NOT a convergence failure. Each of these relaxations converged
cleanly -- `bfgs converged`, textbook fmax -- while carrying an electronic state that a
fresh SCF at the relaxation's own final coordinates finds *below* it. The mechanism is
path dependence: pw.x extrapolates the charge density from one ionic step to the next, so
the basin chosen at ionic step 1 (at the STARTING geometry) is carried all the way to the
end. Ni's production run made it worse by reading `startingpot = 'file'` from a prior
attempt, locking in that attempt's basin.

So the repair is not a harder mixing recipe -- `build_attempt3/4.py` already walked that
ladder for a different problem. It is simply: start the relaxation FROM the final geometry
with a FRESH density. Ionic step 1 then reproduces the audit SCF exactly (same coordinates,
same electronic settings, same atomic-superposition start), lands in the lower basin, and
relaxes from there.

Which means the audit deck already IS the recipe. The only edit is `calculation`.

Three states qualify -- the ones where the fresh SCF came out LOWER, i.e. where the
production relaxation was the excited one:

    Cr s0_OOH   -175 meV    eta(Cr) 0.491 -> 0.330 V, pls 3 -> 2
    Co s0_OH    -405 meV    eta(Co) 0.544 -> 0.783 V, pls 1 -> 2
    Ni s0_OH    -173 meV    eta(Ni) 1.084 -> 1.185 V, pls 1 -> 2

Fe s0_OOH (+277 meV) and the Co clean slab (+59 meV) are deliberately NOT here: there the
fresh SCF was the one that got trapped high, so the production value is already the lower
solution and stands. The sign of the drift decides who is wrong.

Those eta shifts are fixed-geometry estimates and therefore LOWER BOUNDS -- relaxing on the
correct surface can only go further down.

    PYTHONPATH=src python src/dft/build_basin_restarts.py --out runs/probe
"""
from __future__ import annotations

import argparse
import os
import re
import sys

#: (audit deck to convert, job name, new run dir).  The audit deck's geometry is the
#: production relaxation's final geometry, which is exactly where we want to restart.
JOBS = [
    ("runs/probe/Cr/s0_OOH__base.in", "s0_OOH", "Cr_basin"),
    ("runs/probe/Co_uladder/s0_OH__base.in", "s0_OH", "Co_basin"),
    ("runs/probe/Ni_audit/s0_OH__base.in", "s0_OH", "Ni_basin"),
]


def to_relax(text: str, prefix: str) -> str:
    """Turn the fixed-geometry audit SCF deck into a relaxation from the same start.

    Everything else is left byte-identical on purpose: same cutoffs, same k-mesh, same
    Hubbard U, same smearing, same starting_magnetization, same constraint mask. If any
    of those moved, the restart would no longer be comparable to the tier it is repairing.
    """
    # leading whitespace is significant here only in that the regex must tolerate it --
    # the same trap build_restarts.py hit, where an indented key silently failed to match
    out, n_calc = re.subn(
        r"^(\s*)calculation\s*=\s*'scf'",
        r"\1calculation = 'relax'",
        text,
        count=1,
        flags=re.M,
    )
    if n_calc != 1:
        raise SystemExit("refusing to write: did not find exactly one calculation='scf'")

    out, n_pre = re.subn(
        r"^(\s*)prefix\s*=\s*'[^']*'", rf"\1prefix = '{prefix}'", out, count=1, flags=re.M
    )
    if n_pre != 1:
        raise SystemExit("refusing to write: did not find exactly one prefix")

    # A fresh start is the whole point -- if the audit deck ever grows a startingpot/
    # startingwfc line, this restart would inherit a basin instead of choosing one.
    if re.search(r"^\s*starting(pot|wfc)\s*=", out, flags=re.M):
        raise SystemExit("refusing to write: deck carries startingpot/startingwfc")

    if "&IONS" not in out:
        raise SystemExit("refusing to write: no &IONS namelist, cannot relax")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="runs/probe")
    ap.add_argument("--manifest", default="runs/probe/m_basin.txt")
    ap.add_argument("--nk", type=int, default=4)
    args = ap.parse_args()

    lines = []
    for src_path, job, dirname in JOBS:
        if not os.path.exists(src_path):
            print(f"MISSING {src_path}", file=sys.stderr)
            return 1
        with open(src_path, encoding="utf-8") as fh:
            text = fh.read()

        dest_dir = os.path.join(args.out, dirname)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, f"{job}.in")
        # LF only: a CRLF .in dies silently inside the box's tmux (lessons.md #8)
        with open(dest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(to_relax(text, job))
        print(f"wrote {dest}")
        lines.append(f"probe/{dirname} {job} .in {args.nk}")

    with open(args.manifest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"wrote {args.manifest} ({len(lines)} jobs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
