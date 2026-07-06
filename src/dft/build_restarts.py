"""Build restart inputs for adslab relaxations that died on mid-relax SCF failures.

For each (element, job) in RESTARTS: take the last ATOMIC_POSITIONS block from the
dead .out (BFGS's most recent geometry), splice it into the original .in, and
robustify the ELECTRONS namelist (mixing_beta 0.1, electron_maxstep 500) plus
nstep=100. Writes <job>.in.restart next to the originals; deployment renames it
over <job>.in on the box after archiving the dead .out.

Fe/s0_O died on its FIRST SCF (no geometry progress) -> keep original positions,
robustify electrons only.
"""
import re
import sys
from pathlib import Path

RUNS = Path(__file__).resolve().parents[2] / "runs"

RESTARTS = [
    ("Cr", "s0_OH"), ("Cr", "s0_OOH"),
    ("Mn", "s0_OOH"),
    ("Fe", "s0_O"), ("Fe", "s0_OOH"),
    ("Co", "s0_O"), ("Co", "s0_OH"), ("Co", "s0_OOH"),
    ("Ni", "s0_O"), ("Ni", "s0_OH"), ("Ni", "s0_OOH"),
    ("Cu", "s0_O"), ("Cu", "s0_OH"), ("Cu", "s0_OOH"),
]


def last_positions_block(out_path: Path) -> list[str] | None:
    """Return the lines of the final ATOMIC_POSITIONS block (header included)."""
    lines = out_path.read_text(errors="replace").splitlines()
    starts = [i for i, l in enumerate(lines) if l.startswith("ATOMIC_POSITIONS")]
    if not starts:
        return None
    i = starts[-1]
    block = [lines[i]]
    for l in lines[i + 1:]:
        # position lines: species + 3 floats (+ optional 3 constraint flags)
        if re.match(r"^[A-Z][a-z]?\s+[-\d]", l):
            block.append(l.rstrip())
        else:
            break
    return block


def robustify(text: str) -> str:
    text = re.sub(r"mixing_beta\s*=\s*[\d.]+", "mixing_beta = 0.1", text)
    text = re.sub(r"electron_maxstep\s*=\s*\d+", "electron_maxstep = 500", text)
    if "nstep" not in text:
        text = text.replace("&CONTROL", "&CONTROL\n  nstep = 100", 1)
    return text


def main() -> None:
    n_ok = 0
    for elem, job in RESTARTS:
        d = RUNS / f"{elem}_slab"
        inp, out = d / f"{job}.in", d / f"{job}.out"
        text = inp.read_text()
        nat = int(re.search(r"nat\s*=\s*(\d+)", text).group(1))

        block = last_positions_block(out)
        if block is not None and len(block) - 1 == nat:
            new_text = re.sub(
                r"ATOMIC_POSITIONS[^\n]*\n(?:[ \t]*[A-Z][a-z]?\s+[^\n]*\n?)+",
                "\n".join(block) + "\n",
                text,
            )
            if new_text == text:
                print(f"FAIL {elem}/{job}: ATOMIC_POSITIONS splice did not match")
                sys.exit(1)
            text = new_text
            src = "geometry: last BFGS step"
        elif block is None:
            src = "geometry: original (no progress in dead run)"
        else:
            print(f"FAIL {elem}/{job}: block has {len(block)-1} atoms, nat={nat}")
            sys.exit(1)

        (d / f"{job}.in.restart").write_text(robustify(text))
        print(f"OK {elem}/{job} ({src})")
        n_ok += 1
    print(f"{n_ok}/{len(RESTARTS)} restart inputs written")


if __name__ == "__main__":
    main()
