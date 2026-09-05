"""The two small-arm readouts of 2026-09-05: thresholds come from docs/43 at run time,
and both refuse to score while outputs are missing."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "dft"))

import eproj_np128_readout as ep  # noqa: E402
import hp_cro2_q333_readout as hq  # noqa: E402


def test_hp_thresholds_are_parsed_from_the_registration():
    reg = hq.registered()
    assert reg["q_mesh_dU_max_eV"] == 0.2
    assert reg["rerun_dE_max_Ry"] == 1e-5


def test_eproj_tolerance_is_parsed_from_the_registration():
    assert ep.registered() == 1e-5


def test_hp_readout_refuses_on_a_moved_threshold(tmp_path):
    bad = tmp_path / "43.md"
    bad.write_text("nothing registered here", encoding="utf-8")
    with pytest.raises(hq.Fatal):
        hq.registered(str(bad))
    with pytest.raises(ep.Fatal):
        ep.registered(str(bad))


def test_eproj_pending_when_outputs_absent(tmp_path):
    res = ep.score(1e-5, new_dir=str(tmp_path))
    assert sorted(res["pending"]) == sorted(ep.STEMS)
    assert "pair_new_Ry" not in res


def _fake_out(path, energy, cores=128, done=True, iterations=19, mag=4.00):
    lines = [
        "     Parallel version (MPI & OpenMP), running on     %d processor cores" % cores,
        "     convergence has been achieved in  %d iterations" % iterations,
        "     total magnetization       =     %.2f Bohr mag/cell" % mag,
        "     absolute magnetization    =     %.2f Bohr mag/cell" % (mag + 0.68),
        "!    total energy              =   %.8f Ry" % energy,
    ]
    if done:
        lines.append("   JOB DONE.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_eproj_agrees_and_disagrees_by_the_registered_tolerance(tmp_path):
    new = tmp_path / "new"
    old = tmp_path / "old"
    new.mkdir()
    old.mkdir()
    _fake_out(old / "s0_O__u715_atomic.out", -1592.51110015, cores=20)
    _fake_out(old / "s0_O__u715_ortho.out", -1592.78131312, cores=20)
    _fake_out(new / "s0_O__u715_atomic.out", -1592.51110015 + 4e-6)
    _fake_out(new / "s0_O__u715_ortho.out", -1592.78131312 - 2e-5)
    res = ep.score(1e-5, new_dir=str(new), banked_dir=str(old))
    assert res["pending"] == []
    assert res["legs"]["s0_O__u715_atomic"]["verdict"] == "AGREES"
    assert res["legs"]["s0_O__u715_ortho"]["verdict"] == "DISAGREES"
    assert abs(res["pair_banked_Ry"] - 0.27021297) < 1e-9


def _fake_dat(path, u):
    path.write_text(
        "\n\n\n                                 Hubbard U parameters:\n\n"
        "       site n.  type  label  spin  new_type  new_label  manifold  Hubbard U (eV)\n"
        "         1        1   Cr       1      1         Cr         3d       %.4f\n"
        "         2        1   Cr       1      1         Cr         3d       %.4f\n\n"
        "  =----=\n" % (u, u),
        encoding="utf-8",
    )


def test_hp_pair_scores_pass_and_unconverged_with_isolation(tmp_path):
    new = tmp_path / "q333"
    new.mkdir()
    banked = {}
    for leg, u222, u333, machine, e_new in (
        ("atomic", 6.1635, 6.2000, "vast", -517.92950441 + 3e-6),
        ("ortho", 7.2677, 7.6000, "anvil", -517.92950441),
    ):
        bdir = tmp_path / ("banked_" + leg)
        bdir.mkdir()
        _fake_dat(bdir / ("cro2_%s.Hubbard_parameters.dat" % leg), u222)
        _fake_out(bdir / ("scf__cro2_%s.out" % leg), -517.92950441, cores=20)
        banked[leg] = {"dat": str(bdir / ("cro2_%s.Hubbard_parameters.dat" % leg)),
                       "scf": str(bdir / ("scf__cro2_%s.out" % leg)), "machine": machine}
        _fake_dat(new / ("hp__cro2_%s_q333.cro2_%s_q333.Hubbard_parameters.dat" % (leg, leg)), u333)
        (new / ("hp__cro2_%s_q333.out" % leg)).write_text("   JOB DONE.\n", encoding="utf-8")
        _fake_out(new / ("scf__cro2_%s_q333.out" % leg), e_new)
    reg = {"q_mesh_dU_max_eV": 0.2, "rerun_dE_max_Ry": 1e-5}
    res = hq.score(reg, new_dir=str(new), banked=banked)
    assert res["pending"] == []
    assert res["legs"]["atomic"]["q_mesh"] == "PASS"
    assert res["legs"]["ortho"]["q_mesh"].startswith("UNCONVERGED")
    assert res["legs"]["atomic"]["scf_isolation"]["verdict"] == "AGREES (A8.5)"
    assert res["legs"]["ortho"]["scf_isolation"]["verdict"] == "MATCH"
    assert abs(res["split_q222_eV"] - 1.1042) < 1e-9
    assert abs(res["split_q333_eV"] - 1.4) < 1e-9
