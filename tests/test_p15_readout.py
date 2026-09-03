"""Tests for src/dft/p15_readout.py (docs/43 §4 as amended by §4-A, AMENDMENT 1).

P15's value is in what the gate REFUSES to conflate, so that is what these pin:

  T1  the thresholds are PARSED from docs/43 and are not written down in the
      script -- the whole point, since three builders have already copied a
      registered rule into a source file and contradicted it;
  T2  §4's window and §4-A.1's window must AGREE, or the script refuses rather
      than picking one;
  T3  an unparseable pre-registration is FATAL, never a default;
  T4  the demoted (χ-symmetry) and withdrawn (amplitude-independence) checks
      never enter the gate -- a withdrawn check is neither a pass nor a failure;
  T5  the slab is scored as its own gate and is never folded into the bulk one;
  T6  the slab gate arm is the U-attempt decks ONLY -- the cost-model/k-count
      probes are not gate rows, which is the difference between "4 runs, 0 clean"
      and a misleading "10 runs, 6 clean";
  T7  the literature side-check is reported and never gates;
  T8  the readout applies no countersignature -- the scoring act is the entrant's.

Tests read docs/figs/ but NEVER write there. All writes go to tmp_path.
"""
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "dft", "p15_readout.py")
PREREG = os.path.join(ROOT, "docs", "43-prereg-week1-factorial.md")


def _load():
    spec = importlib.util.spec_from_file_location("p15_readout", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def out(mod, tmp_path_factory):
    d = tmp_path_factory.mktemp("p15")
    j = str(d / "p15.json")
    assert mod.main(["--json", j, "--xu-u", "4.95"]) == 0
    with open(j, encoding="utf-8") as fh:
        return json.load(fh)


# -- T1/T2/T3: the thresholds come from the pre-registration ----------------

def test_thresholds_are_parsed_not_hardcoded(mod):
    """T1. The gate values must not appear as literals in the script."""
    src = open(SRC, encoding="utf-8").read()
    body = src.split('"""', 2)[2]          # skip the module docstring
    code = "\n".join(l for l in body.splitlines()
                     if not l.lstrip().startswith("#"))
    for lit in ("3.0, 7.0", "[3.0", "7.0]"):
        assert lit not in code, "window literal %r is hardcoded in the script" % lit
    t = mod.registered_thresholds(PREREG)
    assert t["window_eV"] == [3.0, 7.0]
    assert t["q_mesh_dU_max_eV"] == 0.2
    assert t["perturbed_atom_tol_eV"] == 0.05


def test_window_disagreement_is_fatal(mod, tmp_path):
    """T2. If an amendment moved one window and not the other, refuse."""
    text = open(PREREG, encoding="utf-8").read()
    tampered = text.replace("The external window stays [3.0, 7.0] eV",
                            "The external window stays [2.0, 8.0] eV", 1)
    assert tampered != text, "anchor for the §4-A.1 window not found"
    p = tmp_path / "prereg.md"
    p.write_text(tampered, encoding="utf-8")
    with pytest.raises(mod.Fatal, match="disagrees"):
        mod.registered_thresholds(str(p))


def test_unparseable_prereg_is_fatal(mod):
    """T3. No silent default when the registration cannot be read."""
    with pytest.raises(mod.Fatal):
        mod.registered_thresholds(os.path.join(ROOT, "README.md"))


# -- T4: demoted and withdrawn checks stay out of the gate ------------------

def test_demoted_and_withdrawn_checks_never_gate(out):
    """T4. §4-A.2 withdrew amplitude independence as UNPERFORMABLE and §4-A.4
    demoted χ-symmetry to a reported diagnostic. Neither may carry a verdict."""
    for key in ("chi_symmetry", "amplitude_independence"):
        c = out["checks"][key]
        assert c["gated"] is False
        assert "verdict" not in c, "%s must not carry a verdict" % key
    assert "WITHDRAWN" in out["checks"]["amplitude_independence"]["status"]
    assert "DEMOTED" in out["checks"]["chi_symmetry"]["status"]


def test_bulk_verdict_rests_only_on_the_three_live_gated_checks(out):
    """The bulk verdict is a function of external + q-mesh + perturbed atoms."""
    live = [out["checks"]["external"]["verdict"] == "MET",
            out["checks"]["q_mesh"]["verdict"] == "PASS",
            out["checks"]["perturbed_atoms"]["verdict"] == "PASS"]
    assert out["bulk_verdict"] == ("GO" if all(live) else "NO-GO")


# -- T5/T6: the slab is separate, and scoped to the U attempts --------------

def test_slab_is_its_own_gate(out):
    """T5. docs/43 §4: a successful bulk validation does not license a slab U."""
    assert "slab_verdict" in out and out["slab_verdict"] in ("GO", "NO-GO")
    assert "separate gate" in out["checks"]["slab"]["registered"]
    assert "never combined" in out["binding"]


def test_slab_gate_arm_excludes_cost_model_probes(out):
    """T6. Only the U-attempt decks are gate rows. Folding in the k-count probes
    would report six timing runs as clean slab validations."""
    slab = out["checks"]["slab"]
    assert all("_1atomq_" in fn for fn in slab["runs"]), slab["runs"].keys()
    assert all("_1atomq_" not in fn for fn in slab["cost_model_probes"])
    assert slab["n"] == len(slab["runs"])
    # every gate row is a real U attempt that failed to produce one
    assert slab["n_produced_U"] == 0
    assert slab["verdict"] == "NO-GO"


# -- T7/T8: reported-not-gated, and no countersignature ---------------------

def test_literature_side_check_never_gates(out):
    """T7. docs/43 §4: reported as an additional check, NOT as the gate."""
    lit = out["checks"]["literature_side_check"]
    assert lit["gated"] is False
    assert "verdict" not in lit
    # and it does not appear in the bulk decision
    assert out["bulk_verdict"] == "GO"


def test_readout_applies_no_countersignature(out):
    """T8. The registered scoring act is the entrant's dated line."""
    assert "no countersignature" in out["binding"]
    assert out["zero_su"] is True


def test_numbers_match_the_banked_files(out):
    """The gate is only as good as its extraction; pin the read-out values."""
    ext = out["checks"]["external"]["U_eV"]
    assert ext["q222"] == pytest.approx(4.2245, abs=1e-6)
    assert ext["q333"] == pytest.approx(4.2251, abs=1e-6)
    assert ext["q444"] == pytest.approx(4.2245, abs=1e-6)
    assert out["checks"]["q_mesh"]["max_dU_eV"] == pytest.approx(0.0006, abs=1e-6)
    assert out["checks"]["perturbed_atoms"]["spread_eV"] == pytest.approx(0.0, abs=1e-9)
    assert out["checks"]["check_4prime"]["U_Cr_3d_eV"] == pytest.approx(6.1635, abs=1e-6)
    assert out["checks"]["check_4prime"]["verdict"] == "PASS"
