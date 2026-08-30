"""The gate-(h) AFM relax builder, and the HOLD it enforces mechanically.

docs/43:1645 (deposited) leaves the AFM family's scope open with NO DEFAULT and says
the gate-(h) relaxations stay HOLD until the entrant writes a dated line. The builder
encodes that: decks are written unconditionally (they cost no SU and are common to
both readings), the launch manifest is withheld until the line exists. These tests
cover the gate in both directions, because a HOLD nobody exercises is a HOLD that
silently stops working.
"""
import os
import re
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "src"))

from dft import build_h_afm_relax as B  # noqa: E402

pytestmark = pytest.mark.skipif(
    not os.path.isdir(os.path.join(REPO, "runs", "s0", "h_afm_anchor")),
    reason="gate-(h) AFM decks not present",
)


# ----------------------------------------------------------------- the gate ---

def test_the_real_prereg_resolves_standalone_four():
    """The entrant resolved the scope 2026-08-30 (docs/43 dated addendum).

    Before that line existed this test asserted the HOLD was live; it now pins the
    resolution so a botched edit to docs/43 cannot silently change the scope or
    re-open the HOLD without this suite noticing.
    """
    assert B.afm_scope_resolution() == ("2026-08-30", "STANDALONE_FOUR")


@pytest.mark.parametrize("scope", ["STANDALONE_FOUR", "SECOND_SEED_CROSSED"])
def test_resolution_line_lifts_the_gate(tmp_path, monkeypatch, scope):
    doc = tmp_path / "43.md"
    doc.write_text(
        "some registered prose\n"
        f"[AFM-SCOPE RESOLVED 2026-09-01: {scope}] and the entrant's own sentence\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(B, "PREREG", str(doc))
    assert B.afm_scope_resolution() == ("2026-09-01", scope)


@pytest.mark.parametrize(
    "line",
    [
        "[AFM-SCOPE RESOLVED 2026-09-01: MAYBE]",       # not one of the two scopes
        "[AFM-SCOPE RESOLVED soon: STANDALONE_FOUR]",   # undated
        "AFM-SCOPE RESOLVED 2026-09-01: STANDALONE_FOUR",  # unbracketed prose
        "the AFM scope is resolved, standalone four",   # prose alone never counts
    ],
)
def test_near_miss_lines_do_not_lift_the_gate(tmp_path, monkeypatch, line):
    doc = tmp_path / "43.md"
    doc.write_text(line + "\n", encoding="utf-8")
    monkeypatch.setattr(B, "PREREG", str(doc))
    assert B.afm_scope_resolution() is None, f"gate lifted by {line!r}"


def test_builder_exits_0_and_manifest_names_the_four_decks():
    """With the scope resolved, the builder emits the manifest and it is exact."""
    env = dict(os.environ, PYTHONPATH=os.path.join(REPO, "src"))
    r = subprocess.run(
        [sys.executable, os.path.join(REPO, "src", "dft", "build_h_afm_relax.py")],
        cwd=REPO, env=env, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"expected 0 post-resolution, got {r.returncode}\n{r.stdout}{r.stderr}"
    assert "MANIFEST WRITTEN (STANDALONE_FOUR" in r.stdout
    man = os.path.join(REPO, "runs", "s0", "m_h_afm_relax.txt")
    lines = [ln for ln in open(man).read().split("\n") if ln and not ln.startswith("#")]
    # 4-field rows in 42_s3_wave1.slurm's format, nk per m_s3_wave1's measured
    # 2x1v convention (clean ref 16, adsorbate rows 8).
    assert lines == [
        f"s0/h_afm_relax {s}__relax .in {16 if s.startswith('ref') else 8}"
        for s in B.STEMS
    ]
    for ln in lines:
        d, job, suf, nk = ln.split()
        assert os.path.exists(os.path.join(REPO, "runs", d, job + suf))
        assert 128 % int(nk) == 0  # the runner's hard rule 4


def test_builder_holds_when_the_resolution_line_is_absent(tmp_path, monkeypatch):
    """The HOLD path stays exercised even now the real prereg is resolved."""
    doc = tmp_path / "43.md"
    doc.write_text("deposited text with no resolution line\n", encoding="utf-8")
    monkeypatch.setattr(B, "PREREG", str(doc))
    assert B.afm_scope_resolution() is None


# ------------------------------------------------------------ the transform ---

def test_every_child_differs_from_its_parent_in_exactly_two_lines():
    src = os.path.join(REPO, "runs", "s0", "h_afm_anchor")
    dst = os.path.join(REPO, "runs", "s0", "h_afm_relax")
    for stem in B.STEMS:
        parent = open(os.path.join(src, stem + ".in")).read().split("\n")
        child = open(os.path.join(dst, stem + "__relax.in")).read().split("\n")
        assert len(parent) == len(child)
        diff = [i for i, (a, b) in enumerate(zip(parent, child)) if a != b]
        assert len(diff) == 2, f"{stem}: {len(diff)} lines differ"
        changed = " ".join(parent[i] for i in diff)
        assert "calculation" in changed and "prefix" in changed
        assert re.search(r"calculation\s*=\s*'relax'", "\n".join(child))
        # A11: prefix must equal the stem -- 46_a0.slurm rm -rf's dens/${prefix}.save
        pm = re.search(r"^\s*prefix\s*=\s*'([^']+)'", "\n".join(child), re.M)
        assert pm.group(1) == stem + "__relax"


def test_sublattice_pair_is_found_not_assumed():
    """A3/A4: the pair is derived from each deck's own ATOMIC_SPECIES.

    The metal sits at indices (1, 2) on the ntyp = 3 decks and (2, 3) on the ntyp = 4
    decks because H sorts first. A per-deck constant would seed H or O.
    """
    src = os.path.join(REPO, "runs", "s0", "h_afm_anchor")
    expected = {
        "ref__2x1v__afm": (1, 2),
        "s0_O__2x1v_off__afm": (1, 2),
        "s0_OH__2x1v_off__afm": (2, 3),
        "s0_OOH__2x1v_off__afm": (2, 3),
    }
    for stem, want in expected.items():
        txt = open(os.path.join(src, stem + ".in")).read()
        species = B.species_block(txt)
        ru1, ru2 = B.find_sublattice_pair(species)
        idx = {label: i + 1 for i, (label, _m, _p) in enumerate(species)}
        assert (idx[ru1], idx[ru2]) == want, f"{stem}: pair at {idx[ru1]},{idx[ru2]}"


def test_pair_finder_refuses_when_there_is_no_unique_pair():
    with pytest.raises(SystemExit):
        B.find_sublattice_pair([("Ru", "101.070", "x.upf"), ("O", "15.999", "y.upf")])
    with pytest.raises(SystemExit):
        # two candidate pairs -- ambiguous, must refuse rather than pick one
        B.find_sublattice_pair([
            ("Ru1", "101.070", "x.upf"), ("Ru2", "101.070", "x.upf"),
            ("Fe1", "55.845", "z.upf"), ("Fe2", "55.845", "z.upf"),
        ])


def test_gate1_refuses_while_the_relaxations_are_unrun():
    env = dict(os.environ, PYTHONPATH=os.path.join(REPO, "src"))
    r = subprocess.run(
        [sys.executable, os.path.join(REPO, "src", "dft", "build_h_afm_relax.py"), "--gate1"],
        cwd=REPO, env=env, capture_output=True, text=True,
    )
    assert r.returncode == 1
    assert "REFUSED" in r.stdout
