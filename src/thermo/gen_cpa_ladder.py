#!/usr/bin/env python
"""Generate the MuST KKR-CPA + Kubo validation ladder for Cu(1-x)Fe(x) fcc
(src/thermo/README.md): x = 0 (pure-Cu anchor), 1, 2, 5, 10 at.%.

Emits runs_cpa/<tag>/{position.dat, i_scf, i_kubo} from the CuZn KUBO tutorial
template (i_new_cuzn_kubo_template, shipped with MuST). Per rung:
  1. mpirun -np N mst2 < i_scf   -> converged potential CuFe_mt_w (XDR)
  2. mpirun -np N kubo < i_kubo  -> o_* file with RESISTIVITY TENSOR (muOhm-cm)
Gate: dilute d(rho)/dx vs Linde Fe-in-Cu ~9.3 uOhm-cm/at.% within ~2x.

Physics choices (v1, documented deliberately):
- fcc lattice fixed at pure Cu a = 3.615 A = 6.8309 Bohr for every x (dilute
  regime; Vegard shift is second-order against the 2x gate).
- Non-spin-polarized (Spin Index 1). Fe in Cu carries a local moment; if the
  slope gate fails low/high, the spin-polarized/DLM re-run is the follow-up.
- Muffin-tin, VWN LDA, 20x20x20 k, 30-point contour - tutorial defaults kept.
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TEMPLATE = HERE / "i_new_cuzn_kubo_template"
OUT = REPO / "runs_cpa"

A_CU_BOHR = 6.8309   # 3.615 A
XS = [0.0, 0.01, 0.02, 0.05, 0.10]

FCC = """{a}
# Bravais lattice
     0.50000000000    0.50000000000    0.00000000000
     0.00000000000    0.50000000000    0.50000000000
     0.50000000000    0.00000000000    0.50000000000
# Atomic position data
# Format: For random alloy calculations using CPA, use 'CPA' as the virtual atom
# name, followed by the Cartesian coordinates (x,y,z) of the 'atom' and by atomic
# species name and its concentration on the atomic site.
{site}
"""


def set_field(text: str, field: str, value: str) -> str:
    """Replace the value of `field  :: value` preserving the :: alignment."""
    pat = re.compile(rf"^({re.escape(field)}\s*::)\s*.*$", re.M)
    new, n = pat.subn(rf"\1  {value}", text)
    assert n == 1, f"field not found or ambiguous: {field}"
    return new


def build(tag: str, x: float) -> None:
    d = OUT / tag
    d.mkdir(parents=True, exist_ok=True)
    tmpl = TEMPLATE.read_text()

    if x == 0.0:
        site = "Cu   0.00000000000    0.00000000000    0.00000000000"
        pots = "Cu_mt_v"
    else:
        site = (f"CPA  0.00000000000    0.00000000000    0.00000000000   "
                f"Cu {1 - x:.2f} Fe {x:.2f}")
        pots = "Cu_mt_v, Fe_mt_v"
    (d / "position.dat").write_text(FCC.format(a=A_CU_BOHR, site=site))

    common = tmpl
    common = set_field(common, "Text Identification", tag)
    common = set_field(common, "Alloy System Description",
                       f"Cu{100 - x * 100:.0f}Fe{x * 100:.0f} fcc random alloy (validation ladder)")

    scf = common
    scf = set_field(scf, "Default Potential Input File Name", pots)
    scf = set_field(scf, "Default Potential Input File Form", "0")
    scf = set_field(scf, "Default Potential Output File Name", "CuFe_mt_w")
    scf = set_field(scf, "Conductivity Calculation", "0")
    (d / "i_scf").write_text(scf)

    kubo = common
    kubo = set_field(kubo, "Default Potential Input File Name", "CuFe_mt_w")
    kubo = set_field(kubo, "Default Potential Input File Form", "1")
    kubo = set_field(kubo, "Default Potential Output File Name", "CuFe_mt_wk")
    kubo = set_field(kubo, "Conductivity Calculation", "1")
    (d / "i_kubo").write_text(kubo)
    print(f"OK {tag}  x_Fe={x:.2f}  ({'pure-Cu anchor' if x == 0 else 'CPA'})")


def main() -> None:
    for x in XS:
        build(f"CuFe_x{round(x * 100):03d}", x)
    print(f"\nladder written to {OUT} - deploy with src/thermo/run_cpa_ladder.sh")


if __name__ == "__main__":
    main()
