"""Build the two same-state reproducibility probe decks from the launched C3 deck.

Offline only: no QE, no Anvil access. Each probe deck is the committed, spec-pinned
C3_warm_1e-10 deck of the fixed-geometry diagnostic with exactly one line changed:
its outdir (licensed 2026-10-07, docs/research/pa-repro-probe-2026-10-07.md).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "runs/hea/pa_fixed_geometry_diag_2026-10-05/decks/C3_warm_1e-10.in"
TEMPLATE_SHA256 = "0f86122331fe084a394b28d5412430e9100df515115028b15d4101e5f5e9a19b"
TEMPLATE_OUTDIR = "  outdir = '/anvil/projects/x-che260157/sts_pa_fixed_geometry_diag_2026-10-05/runs/C3_warm_1e-10/outdir'"
BASE = "/anvil/projects/x-che260157/sts_pa_repro_probe_2026-10-07"
ARMS = ("P1_C3_repeat", "P2_C3_repeat")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def template() -> str:
    data = TEMPLATE.read_bytes()
    if sha256_bytes(data) != TEMPLATE_SHA256:
        raise SystemExit("C3 deck differs from its launched pin")
    return data.decode("ascii")


def build(arm: str) -> tuple:
    text = template()
    lines = text.split("\n")
    if lines.count(TEMPLATE_OUTDIR) != 1:
        raise SystemExit("C3 deck outdir line not found exactly once")
    new = f"  outdir = '{BASE}/runs/{arm}/outdir'"
    index = lines.index(TEMPLATE_OUTDIR)
    lines[index] = new
    return "\n".join(lines), [{"line": index + 1, "old": TEMPLATE_OUTDIR, "new": new}]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "runs/hea/pa_repro_probe_2026-10-07/decks")
    args = parser.parse_args(argv)
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=True)
    receipt = {"template": str(TEMPLATE.relative_to(ROOT)).replace("\\", "/"),
               "template_sha256": TEMPLATE_SHA256, "decks": {}}
    for arm in ARMS:
        deck, changes = build(arm)
        data = deck.encode("ascii")
        (args.out / (arm + ".in")).write_bytes(data)
        receipt["decks"][arm] = {"sha256": sha256_bytes(data), "changes": changes}
    (args.out / "deck_receipt.json").write_bytes((json.dumps(receipt, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({k: v["sha256"] for k, v in receipt["decks"].items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
