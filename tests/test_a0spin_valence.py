"""Tests for src/dft/a0spin_valence.py (docs/43 A11.R8, registered 2026-09-03 at 07cfc4f).

A11.R8 changes exactly one thing from A11.R7 -- the predictor's spin treatment -- so
the tests that matter are the ones that pin *that it changed nothing else*:

  T1  the registered seed rule picks the lowest-energy CONVERGED nspin=2 seed, and
      breaks ties to the lowest seed label;
  T2  self-check 4 (carry-over identity) is FATAL on drift -- if Cr/Mn/Fe's |dq_c|
      stops reproducing A11.R7 exactly, the reader changed and the run must die;
  T3  R8-P1's separation test is correct at its exact registered boundary (strict <);
  T4  the QE readers agree with the files on disk (converged / nspin=2 / '!' energy);
  T5  the active-site rule returns a metal atom index in the spin arm;
  T6  ON REAL BANKED FILES, Cr/Mn/Fe reproduce A11.R7's |dq_c| to 0.0 exactly;
  T7  the CHE step construction used by R8-P2 reproduces A11.R7's own dq1/dq2/dq3
      on the carried-over metals -- the check that the pairing is R7's, not a new one;
  T8  the emitted JSON carries A11.R8's binding clause and its registered asymmetry.

Tests read runs/ and docs/figs/ but NEVER write, modify or delete anything there.
All writes go to tmp_path.
"""
import importlib.util
import json
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "dft", "a0spin_valence.py")
R8_JSON = os.path.join(ROOT, "docs", "figs", "a0spin_valence.json")
R7_JSON = os.path.join(ROOT, "docs", "figs", "a0lowdin_valence.json")


def _load():
    spec = importlib.util.spec_from_file_location("a0spin_valence", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def M():
    return _load()


@pytest.fixture(scope="module")
def out():
    if not os.path.exists(R8_JSON):
        pytest.skip("a0spin_valence.json not generated yet")
    with open(R8_JSON, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def r7():
    if not os.path.exists(R7_JSON):
        pytest.skip("a0lowdin_valence.json missing")
    with open(R7_JSON, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- T1: seeds ---

def test_T1_seed_rule_picks_lowest_energy_converged(M, tmp_path, monkeypatch):
    """The registered rule is lowest TOTAL ENERGY among CONVERGED nspin=2 seeds."""
    d = tmp_path / "runs" / "a0" / "spin" / "Xx"
    d.mkdir(parents=True)

    def write(seed, energy, conv=True, nspin2=True):
        stem = "s0_OH__u000__sp2%s" % seed
        (d / (stem + ".in")).write_text(
            "&system\n  nspin = %d\n/\n" % (2 if nspin2 else 1), encoding="utf-8")
        tail = ("convergence has been achieved\n!    total energy = %f Ry\n" % energy
                if conv else "convergence NOT achieved\n")
        (d / (stem + ".out")).write_text(tail, encoding="utf-8")
        return stem

    # m030 is lowest but NOT converged; m050 is lowest among converged
    cands = [("m010", write("m010", -100.0)),
             ("m030", write("m030", -999.0, conv=False)),
             ("m050", write("m050", -100.5)),
             ("m070", write("m070", -99.0, nspin2=False))]
    monkeypatch.setattr(M, "ROOT", str(tmp_path))
    excl = []
    pick = M.pick_seed("Xx", "s0_OH", cands, excl)
    assert pick["seed"] == "m050", "must pick the lowest-energy CONVERGED seed"
    assert pick["n_converged_seeds"] == 2
    reasons = {e["seed"]: e["reason"] for e in excl}
    assert "not converged" in reasons["m030"]
    assert "nspin = 2" in reasons["m070"]


def test_T1b_ties_break_to_lowest_seed_label(M, tmp_path, monkeypatch):
    d = tmp_path / "runs" / "a0" / "spin" / "Xx"
    d.mkdir(parents=True)
    cands = []
    for seed, e in (("m050", -100.0000000), ("m010", -100.0000001)):
        stem = "s0_OH__u000__sp2%s" % seed
        (d / (stem + ".in")).write_text("&system\n nspin = 2\n/\n", encoding="utf-8")
        (d / (stem + ".out")).write_text(
            "convergence has been achieved\n!    total energy = %.9f Ry\n" % e,
            encoding="utf-8")
        cands.append((seed, stem))
    monkeypatch.setattr(M, "ROOT", str(tmp_path))
    pick = M.pick_seed("Xx", "s0_OH", cands, [])
    assert abs(pick["energy_ry"] - (-100.0000001)) < 1e-12
    assert set(pick["tied_within_1e-6_Ry"]) == {"m010", "m050"}, \
        "both seeds are inside the registered 1e-6 Ry tie window"


# ------------------------------------------------- T2: carry-over is fatal ---

def test_T2_carry_over_drift_is_fatal(M, tmp_path, r7):
    """If Cr/Mn/Fe stop reproducing A11.R7 exactly, the run must die, not warn."""
    doctored = json.loads(json.dumps(r7))
    cr = doctored["per_metal"]["Cr"]
    key = "abs_dq_c" if "abs_dq_c" in cr else "dq_c"
    cr[key] = cr[key] + 0.01                      # 10 milli-electron drift
    figs = tmp_path / "docs" / "figs"
    figs.mkdir(parents=True)
    (figs / "a0lowdin_valence.json").write_text(json.dumps(doctored), encoding="utf-8")

    with pytest.raises(M.Fatal) as ei:
        M.main(["--json", str(tmp_path / "o.json"),
                "--md", str(tmp_path / "o.md"),
                "--r7-json", str(figs / "a0lowdin_valence.json")])
    assert "CHECK 4 FAILED" in str(ei.value)
    assert "the reader changed" in str(ei.value)


# ----------------------------------------------------- T3: the P1 boundary ---

def test_T3_separation_boundary_is_strict(M):
    # clean separation: every under value below every over value
    s = M.separation([0.50, 0.60, 0.70], [0.10, 0.20, 0.30])
    assert s["verdict"] == "SEPARATES" and s["gap"] == pytest.approx(0.20)
    # exact touch is NOT a separation -- the registered test is strict <
    s = M.separation([0.30, 0.60, 0.70], [0.10, 0.20, 0.30])
    assert s["verdict"] == "DOES NOT SEPARATE"
    # interleaved
    s = M.separation([0.05, 0.40, 0.70], [0.10, 0.20, 0.60])
    assert s["verdict"] == "DOES NOT SEPARATE" and s["gap"] < 0


# --------------------------------------------------------- T4: QE readers ---

def test_T4_readers_agree_with_disk(M):
    p = os.path.join(ROOT, "runs", "a0", "spin", "Ti", "slab__u000__sp2m010")
    if not os.path.exists(p + ".out"):
        pytest.skip("Ti spin slab not banked here")
    assert M.converged(p + ".out") is True
    assert M.deck_is_nspin2(p + ".in") is True
    e = M.total_energy_ry(p + ".out")
    assert e is not None and e < 0, "a QE total energy is negative Ry"


def test_T4b_not_converged_is_rejected(M, tmp_path):
    f = tmp_path / "x.out"
    f.write_text("convergence has been achieved\nconvergence NOT achieved\n",
                 encoding="utf-8")
    assert M.converged(str(f)) is False, \
        "a later failure must override an earlier success line"


# -------------------------------------------------------- T5: active site ---

def test_T5_active_site_is_a_metal(M, out):
    for metal in ("Ti", "Ru", "Ir"):
        pm = out["per_metal"][metal]
        assert pm["arm"] == "spin" and pm["nspin"] == 2
        assert isinstance(pm["active_site_index"], int) and pm["active_site_index"] >= 1
        assert 1.2 < pm["active_site_distance_A"] < 3.0, \
            "A(M) should be a bonded metal-O distance, got %r" % pm[
                "active_site_distance_A"]


# ------------------------------------------- T6: the carry-over, on real files ---

def test_T6_carry_over_is_exact_on_real_files(out, r7):
    for metal in ("Cr", "Mn", "Fe"):
        mine = out["per_metal"][metal]["abs_dq_c"]
        theirs = r7["per_metal"][metal].get("abs_dq_c")
        if theirs is None:
            theirs = abs(r7["per_metal"][metal]["dq_c"])
        assert mine == theirs, (
            "%s must reproduce A11.R7 EXACTLY -- same files, same rule" % metal)
        assert out["per_metal"][metal]["carried_over_from_A11_R7"] is True


# ------------------------------------- T7: the R8-P2 pairing is A11.R7's own ---

def test_T7_che_step_construction_matches_R7(out, r7):
    """R8-P2 pairs |dq_step| against span_dG_i.  On the carried-over metals the step
    increments must reproduce A11.R7's own dq1/dq2/dq3, or the pairing is a new one
    invented here rather than R7's held fixed."""
    for metal in ("Cr", "Mn", "Fe"):
        dq = out["per_metal"][metal]["delta_q_d"]
        steps = {1: dq["s0_OH"],
                 2: dq["s0_O"] - dq["s0_OH"],
                 3: dq["s0_OOH"] - dq["s0_O"]}
        for i in (1, 2, 3):
            ref = r7["per_metal"][metal]["dq%d" % i]
            assert steps[i] == pytest.approx(ref, abs=1e-9), (
                "%s step %d: %r vs A11.R7's %r" % (metal, i, steps[i], ref))


def test_T7b_p2_is_unscoreable_and_says_so(out):
    p2 = out["R8_P2"]
    assert "NEVER SCORED" in p2["status"]
    if p2["n"]:
        assert p2["n"] == 18
        assert "NOMINAL" in p2["note"], \
            "the non-independence of a metal's three steps must be disclosed"


# ----------------------------------------------------------- T8: the JSON ---

def test_T8_binding_and_asymmetry_present(out):
    b = out["binding"]
    assert "cannot move A7.2 or A7.3" in b
    assert "NOT MET at 3 of 6" in b
    a = out["R8_P1"]["registered_asymmetry"]
    assert "separation proves nothing" in a
    assert "FAILURE to separate falsifies" in a
    assert out["zero_su"] is True
    # the single-variable claim must be on the face of the artifact
    assert "single_variable" in out["design"]
    assert "BRANCH-CONDITIONAL" in out["design"]["why_not_equalised_response"]
