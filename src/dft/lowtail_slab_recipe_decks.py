"""Build the clean-slab SCF-recipe test decks (BUILT, NOT LICENSED).

Derives fixed-geometry ``calculation = 'scf'`` decks from the three pinned
clean-slab relaxation decks of ``runs/hea/lowtail_validation_2026-09-16`` by
changing only the ``&CONTROL calculation`` line and the ``&ELECTRONS`` mixing
lines.  Geometry, cell, cutoffs, k mesh, smearing, spin starts, Hubbard block
and pseudopotentials are byte-identical to the pinned decks.  A manifest with
SHA-256 values and the cost ceiling is written beside the decks.

Usage:
    python src/dft/lowtail_slab_recipe_decks.py [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SRC = Path("runs/hea/lowtail_validation_2026-09-16")
DST = Path("runs/hea/lowtail_slab_scf_recipe_2026-09-19")
SITES = ["Cu8Cr23Mn35Co34__s20_site2", "Ni31Cr29Cu5Mn35__s1_site0", "Fe25Co25Ni25Cr25__s2_site0"]
RECIPES = {
    # name: (mixing_beta, mixing_ndim)
    "b010n16": (0.1, 16),
    "b020n16": (0.2, 16),
}
# Observed wall per SCF iteration on one 128-rank node for these slabs (52-53 s);
# ceiling = 126 iterations (supervisor stop at 127) at 53 s.
WALL_PER_ITER_S = 53.0
MAX_ITER = 126
RANKS = 128


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def derive(text: str, prefix: str, beta: float, ndim: int) -> str:
    """Change only calculation, prefix and the two mixing lines; outdir stays './tmp' as in the pinned decks."""
    n = 0
    text, k = re.subn(r"calculation = 'relax'", "calculation = 'scf'", text); n += k
    text, k = re.subn(r"prefix = '[^']*'", f"prefix = '{prefix}'", text); n += k
    text, k = re.subn(r"mixing_beta = [0-9.]+", f"mixing_beta = {beta}", text); n += k
    text, k = re.subn(r"(  electron_maxstep = 300\n)", f"  mixing_ndim = {ndim}\n\\1", text); n += k
    assert n == 4, f"expected exactly four substitutions, made {n}"
    return text


def build(check: bool) -> dict:
    manifest = {"schema": "lowtail-slab-scf-recipe-decks-v1", "date": "2026-09-19", "status": "BUILT, NOT LICENSED",
                "source_decks": {}, "decks": [], "recipes": RECIPES,
                "ceiling": {"iterations": MAX_ITER, "wall_per_iteration_s": WALL_PER_ITER_S, "ranks": RANKS}}
    per_deck_core_h = MAX_ITER * WALL_PER_ITER_S * RANKS / 3600
    for site in SITES:
        src = SRC / site / "slab__atomic.in"
        text = src.read_text(encoding="utf-8")
        manifest["source_decks"][site] = sha(src)
        for name, (beta, ndim) in RECIPES.items():
            prefix = f"lsr__{site}__slab__{name}"
            out = derive(text, prefix, beta, ndim)
            dst = DST / site / f"slab__{name}.in"
            if check:
                assert dst.exists() and dst.read_text(encoding="utf-8") == out, f"CHECK FAILED {dst}"
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(out, encoding="utf-8", newline="\n")
            manifest["decks"].append({"site": site, "recipe": name, "path": str(dst).replace("\\", "/"),
                                      "sha256": hashlib.sha256(out.encode()).hexdigest(),
                                      "mixing_beta": beta, "mixing_ndim": ndim,
                                      "ceiling_core_hours": round(per_deck_core_h, 1)})
    manifest["ceiling"]["per_deck_core_hours"] = round(per_deck_core_h, 1)
    manifest["ceiling"]["total_core_hours"] = round(per_deck_core_h * len(manifest["decks"]), 1)
    mpath = DST / "manifest.json"
    if check:
        assert json.loads(mpath.read_text())["decks"] == manifest["decks"], "manifest differs"
        print("CHECK OK", len(manifest["decks"]), "decks")
    else:
        mpath.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
        print("built", len(manifest["decks"]), "decks; ceiling", manifest["ceiling"]["total_core_hours"], "core-h")
    return manifest


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="verify existing decks are byte-identical to a rebuild")
    build(ap.parse_args().check)
