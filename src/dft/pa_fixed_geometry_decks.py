"""Build the seven fixed-geometry diagnostic decks from the retained trial decks.

Offline only: no QE, no Anvil access. Every deck is the retained, hash-pinned
input of job 21075231 with a declared list of line edits; the receipt records
each changed line so that a reviewer can see that nothing else moved.

G2 is the first resumed evaluation geometry: the bohr ATOMIC_POSITIONS block of
the trial's resumed deck, equal to the candidate checkpoint's XML output
positions to 7.1e-15 bohr and to the continuous control's evaluation-2
positions to 1.45e-10 bohr (readout 2026-10-05).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIRROR = ROOT / "results/pa_catalyst_retest_readout_2026-10-05/raw_mirror/trial_results"
MANIFEST = ROOT / "results/pa_catalyst_retest_readout_2026-10-05/raw_manifest.json"
BASE = "/anvil/projects/x-che260157/sts_pa_fixed_geometry_diag_2026-10-05"
TRIAL_OUT = "/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04/trial_results"
NAT = 72

# Each arm: template deck, then ordered (key, new value) edits in &CONTROL/&ELECTRONS.
# "insert_after" adds a namelist line that the template does not contain.
ARMS = {
    "A_replay": {
        "template": "resumed",
        "set": {"outdir": f"'{BASE}/runs/A_replay/outdir'"},
        "insert_after": [],
        "positions": "template",
    },
    "B_ethr": {
        "template": "resumed",
        "set": {"outdir": f"'{BASE}/runs/B_ethr/outdir'"},
        "insert_after": [("conv_thr", "diago_thr_init", "1.0d-6")],
        "positions": "template",
    },
    "C1_warm_1e-6": {
        "template": "resumed",
        "set": {"restart_mode": "'from_scratch'", "calculation": "'scf'",
                "outdir": f"'{BASE}/runs/C1_warm_1e-6/outdir'"},
        "insert_after": [],
        "positions": "template",
    },
    "C2_warm_1e-8": {
        "template": "resumed",
        "set": {"restart_mode": "'from_scratch'", "calculation": "'scf'",
                "outdir": f"'{BASE}/runs/C2_warm_1e-8/outdir'",
                "conv_thr": "1.0d-8", "electron_maxstep": "80"},
        "insert_after": [("electron_maxstep", "scf_must_converge", ".false.")],
        "positions": "template",
    },
    "C3_warm_1e-10": {
        "template": "resumed",
        "set": {"restart_mode": "'from_scratch'", "calculation": "'scf'",
                "outdir": f"'{BASE}/runs/C3_warm_1e-10/outdir'",
                "conv_thr": "1.0d-10", "electron_maxstep": "75"},
        "insert_after": [("electron_maxstep", "scf_must_converge", ".false.")],
        "positions": "template",
    },
    "D1_fresh_1e-8": {
        "template": "fresh",
        "set": {"outdir": f"'{BASE}/runs/D1_fresh_1e-8/outdir'",
                "conv_thr": "1.0d-8", "electron_maxstep": "80"},
        "insert_after": [("electron_maxstep", "scf_must_converge", ".false.")],
        "positions": "G2",
    },
    "D2_fresh_1e-10": {
        "template": "fresh",
        "set": {"outdir": f"'{BASE}/runs/D2_fresh_1e-10/outdir'",
                "conv_thr": "1.0d-10", "electron_maxstep": "75",
                "startingwfc": "'file'", "startingpot": "'file'"},
        "insert_after": [("electron_maxstep", "scf_must_converge", ".false.")],
        "positions": "G2",
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned_template(name: str) -> str:
    """Read a retained trial deck only if it matches the terminal raw manifest."""
    rel = f"trial_results/{name}/input.in"
    rows = {row["path"]: row for row in json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
            if row["kind"] == "file"}
    data = (MIRROR / name / "input.in").read_bytes()
    if len(data) != rows[rel]["bytes"] or sha256_bytes(data) != rows[rel]["sha256"]:
        raise ValueError(f"retained trial deck {rel} differs from the raw manifest")
    if b"\r" in data:
        raise ValueError("trial deck must be LF")
    return data.decode("ascii")


def positions_block(text: str) -> list:
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("ATOMIC_POSITIONS"))
    block = lines[start:start + 1 + NAT]
    if len(block) != NAT + 1 or not lines[start + 1 + NAT].startswith("K_POINTS"):
        raise ValueError("unexpected ATOMIC_POSITIONS layout")
    return block


def build(arm: str) -> tuple:
    plan = ARMS[arm]
    text = pinned_template(plan["template"])
    lines = text.split("\n")
    changes = []
    for key, value in plan["set"].items():
        pattern = re.compile(r"^(\s*)" + re.escape(key) + r"\s*=")
        hits = [i for i, line in enumerate(lines) if pattern.match(line)]
        if len(hits) != 1:
            raise ValueError(f"{arm}: {key} must appear exactly once in the template")
        i = hits[0]
        new = f"{pattern.match(lines[i]).group(1)}{key} = {value}"
        if new == lines[i]:
            raise ValueError(f"{arm}: declared edit of {key} changes nothing")
        changes.append({"line": i + 1, "old": lines[i], "new": new})
        lines[i] = new
    for anchor, key, value in plan["insert_after"]:
        if any(re.match(r"^\s*" + re.escape(key) + r"\s*=", line) for line in lines):
            raise ValueError(f"{arm}: {key} already present")
        hits = [i for i, line in enumerate(lines) if re.match(r"^\s*" + re.escape(anchor) + r"\s*=", line)]
        if len(hits) != 1:
            raise ValueError(f"{arm}: anchor {anchor} must appear exactly once")
        new = f"  {key} = {value}"
        lines.insert(hits[0] + 1, new)
        changes.append({"inserted_after_line": hits[0] + 1, "new": new})
    if plan["positions"] == "G2":
        g2 = positions_block(pinned_template("resumed"))
        old = positions_block("\n".join(lines))
        start = lines.index(old[0])
        lines[start:start + NAT + 1] = g2
        changes.append({"positions": "replaced by the resumed deck's bohr G2 block",
                        "old_header": old[0], "new_header": g2[0]})
    deck = "\n".join(lines)
    return deck, changes


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=True)
    receipt = {"schema": "pa-fixed-geometry-decks-v1", "anvil_base": BASE, "decks": {}}
    for arm in ARMS:
        deck, changes = build(arm)
        path = args.out / f"{arm}.in"
        path.write_bytes(deck.encode("ascii"))
        receipt["decks"][arm] = {"path": path.relative_to(ROOT).as_posix(),
                                 "sha256": sha256_bytes(deck.encode("ascii")),
                                 "template": f"trial_results/{ARMS[arm]['template']}/input.in",
                                 "changes": changes}
    (args.out / "deck_receipt.json").write_bytes((json.dumps(receipt, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({arm: row["sha256"] for arm, row in receipt["decks"].items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
