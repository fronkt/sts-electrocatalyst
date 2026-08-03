"""The canonical DFT reference must be the REPAIRED one.

Why this file exists
--------------------
On 2026-08-02 three defective relaxations were re-run and the corrected outputs were
written alongside the originals as `s0_O.out.shortbond` / `s0_OOH.out.bound`. The
originals kept the canonical names, so `mlip_eval.dft_reference()` -- which reads
`<state>.out` -- went on silently returning the *defective* numbers for another day.
Every evaluation run through that path would have been scored against a Cr whose
`*O` was trapped at 2.016 A, i.e. against an eta that is wrong by 1.235 V.

The files were swapped on 2026-08-03 (defective ones kept as `.out.trapped-*` /
`.out.desorbed-*`). This test pins the outcome so the same shape of mistake -- a repair
that lands next to the reference instead of replacing it -- fails loudly next time.

The expected values are the repaired reference of record, docs/32 §3.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ROOT = os.path.join(os.path.dirname(__file__), "..")
RUNS = os.path.join(ROOT, "runs")

#: docs/32 s3, post-repair. Cr/Mn/Fe are the three that were re-run.
EXPECTED_ETA = {"Cr": 0.4907, "Mn": 0.8917, "Fe": 1.2631, "Ru": 0.7868, "Ir": 0.7806}
#: what the defective files gave, and must never come back
DEFECTIVE_ETA = {"Cr": 1.7260}

pytestmark = pytest.mark.skipif(
    not os.path.isdir(os.path.join(RUNS, "Cr_slab")),
    reason="DFT outputs are not present in this checkout")


@pytest.fixture(scope="module")
def ref():
    from dft.mlip_eval import dft_reference
    return dft_reference(RUNS)


@pytest.mark.parametrize("metal,eta", sorted(EXPECTED_ETA.items()))
def test_canonical_path_returns_the_repaired_eta(ref, metal, eta):
    assert ref[metal]["eta"] == pytest.approx(eta, abs=5e-4)


def test_the_defective_cr_cannot_come_back(ref):
    """eta(Cr) = 1.726 V is the signature of the trapped `*O`. It is retracted."""
    assert abs(ref["Cr"]["eta"] - DEFECTIVE_ETA["Cr"]) > 1.0


def test_repaired_states_are_chemically_bound(ref):
    """The three re-run structures must pass the check that condemned the originals."""
    from ase.io import read
    from dft.adsorbate_qc import check_structure
    for d, state, metal in (("Cr_slab", "s0_O", "Cr"), ("Mn_slab", "s0_OOH", "Mn"),
                            ("Fe_slab", "s0_OOH", "Fe")):
        atoms = read(os.path.join(RUNS, d, state + ".in"), format="espresso-in")
        r = check_structure(atoms, metal)
        assert r["tier"] != "desorbed", f"{d}/{state} starts from a desorbed geometry"


def test_stored_repaired_json_matches_the_files(ref):
    """`results/` is gitignored, so the JSON can drift from the outputs. Catch that."""
    p = os.path.join(ROOT, "results", "r3_dft_reference_repaired.json")
    if not os.path.exists(p):
        pytest.skip("results/ not populated in this checkout")
    stored = json.load(open(p))
    for m, v in stored.items():
        assert ref[m]["eta"] == pytest.approx(v["eta"], abs=1e-9), f"{m} drifted"
