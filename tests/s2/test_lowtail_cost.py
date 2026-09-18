"""Cost arithmetic, anchors and relaxation survey of the low-tail track."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "s2" / "lowtail_dft"))

import lt_cost as cost  # noqa: E402


def test_nearest_rank_and_nbnd_rule():
    assert cost.nearest_rank([5, 1, 3, 2, 4], 50) == 3
    assert cost.nearest_rank([36, 37, 37, 40, 53, 87], 90) == 87
    assert cost.nearest_rank([], 50) is None
    assert cost.fortran_nint(333.5) == 334 and cost.fortran_nint(-0.5) == -1
    assert cost.nbnd_rule(667) == 401 and cost.nbnd_rule(674) == 404 and cost.nbnd_rule(312) == 187


def test_cost_model_inputs_parse_the_valence_table_only():
    inp = cost.cost_model_inputs()
    assert inp["valence"] == dict(Cr=14.0, Mn=15.0, Fe=16.0, Co=17.0, Ni=18.0, Cu=11.0, O=6.0, H=1.0)
    assert inp["ceiling_factor"] == 3.0 and inp["node_memory_GB"] == 237.0 and inp["ranks"] == 128


def test_measured_anchor_rows_follow_the_banked_nbnd_rule():
    rows = cost.measured_hea_scfs()
    assert rows and all(r["nbnd_rule_check"] for r in rows)
    assert all(r["procs"] == 128 and r["npool"] == 8 for r in rows)
    a = cost.anchors(rows, "atomic")
    assert a["n_from_scratch_record_start"] >= 4 and a["first_iterations_p50"] <= a["first_iterations_p90"]


def test_deck_cost_formula():
    anchor = dict(per_iteration_norm=1e-4, forces_norm=2e-4, init_s=30.0, rest_s=4.0, ram_norm=1e-4, maxrss_norm=1.1e-4,
                  first_iterations_p50=40, first_iterations_p90=80)
    band = dict(scf_cycles_p50=20, scf_cycles_p90=50, subsequent_iterations_p50=14, subsequent_iterations_p90=19)
    inputs = dict(valence=dict(Cr=14.0, O=6.0), ceiling_factor=3.0, node_memory_GB=237.0, ranks=128)
    cell = [[10.0, 0, 0], [0, 10.0, 0], [0, 0, 10.0]]
    symbols = ["Cr"] * 4 + ["O"] * 8                      # 104 electrons -> nbnd 62
    c = cost.deck_cost(symbols, cell, "atomic", anchor, band, inputs, max_seconds=165000)
    norm = 1000.0 * 62
    t_iter, t_force = 1e-4 * norm, 2e-4 * norm
    plan = 30 + (40 + 19 * 14) * t_iter + 20 * (t_force + 4)
    p90 = 30 + (80 + 49 * 19) * t_iter + 50 * (t_force + 4)
    assert c["nbnd_rule"] == 62
    assert c["planning_core_h"] == pytest.approx(plan * 128 / 3600)
    assert c["ceiling_core_h"] == pytest.approx(max(3 * plan, p90) * 128 / 3600)
    assert c["memory_printed_estimate_GB"] == pytest.approx(1e-4 * norm)
    assert c["fits_node"] and not c["ceiling_exceeds_deck_max_seconds"]


def _write_relax(tmp, name, fmax_ry, cycles, converged=True, note="IEEE_UNDERFLOW_FLAG IEEE_DENORMAL"):
    deck = f"""&CONTROL
  calculation = 'relax'
/
&SYSTEM
  nat = 18
  nspin = 2
/
ATOMIC_SPECIES
  Cr  51.996  cr.UPF
CELL_PARAMETERS angstrom
  5.0 0.0 0.0
  0.0 5.0 0.0
  0.0 0.0 20.0
ATOMIC_POSITIONS angstrom
""" + "".join(f"  Cr 0.0 0.0 {i}.0 {'0 0 0' if i < 6 else '1 1 1'}\n" for i in range(18))
    rows = "\n".join(f"     atom {i + 1:4d} type  1   force =     0.00000000    0.00000000 {fmax_ry:14.8f}" for i in range(18))
    blocks = []
    for k in range(cycles):
        blocks.append(f"!    total energy              =    -100.0 Ry\n     convergence has been achieved in  {30 if k == 0 else 12} iterations\n"
                      f"     Forces acting on atoms (cartesian axes, Ry/au):\n\n{rows}\n\n     Total force = 0.1\n")
    tail = f"     bfgs converged in {cycles:3d} scf cycles and {cycles - 1:3d} bfgs steps\n" if converged else \
        "     The maximum number of steps has been reached.\n"
    out = ("     number of atoms/cell      =           18\n" + "".join(blocks) + tail + "   JOB DONE.\n"
           + f"Note: The following floating-point exceptions are signalling: {note}\n")
    (tmp / f"{name}.in").write_text(deck, encoding="utf-8")
    (tmp / f"{name}.out").write_text(out, encoding="utf-8")


def test_relax_survey_and_band(tmp_path):
    root = tmp_path / "runs"
    (root / "a").mkdir(parents=True)
    (root / "hea").mkdir()
    _write_relax(root / "a", "in_band", 0.06, 10)          # 1.54 eV/A
    _write_relax(root / "a", "in_band2", 0.05, 30)
    _write_relax(root / "a", "low", 0.001, 2)              # outside the band
    _write_relax(root / "a", "stopped", 0.06, 5, converged=False)
    _write_relax(root / "a", "ieee", 0.06, 40, note="IEEE_INVALID_FLAG")    # BFGS-converged, rejected by the scorer
    _write_relax(root / "hea", "excluded_dir", 0.06, 99)
    s = cost.relax_survey(root)
    names = sorted(Path(r["output"]).name for r in s["rows"])
    assert names == ["ieee.out", "in_band.out", "in_band2.out", "low.out", "stopped.out"]
    b = cost.band_statistics(s, 1.5)
    assert b["n_in_band"] == 4 and b["n_bfgs_converged"] == 3 and b["n_basis"] == 2 and b["n_not_bfgs_converged"] == 1
    rejected = b["bfgs_converged_rejected_by_scorer"]
    assert len(rejected) == 1 and "IEEE_INVALID_FLAG" in rejected[0]["severe_failures"]
    assert b["scf_cycles_p50"] == 10 and b["scf_cycles_p90"] == 30 and b["subsequent_iterations_p50"] == 12
    assert b["bfgs_converged_statistics"]["scf_cycles_max"] == 40 and not b["statistics_unchanged_by_scorer_rule"]
    qc = cost.survey_qc(s)
    assert qc["n_rows"] == 5 and qc["n_ieee_invalid"] == 1 and qc["scorer_status_counts"]["CONVERGED"] == 3
    m = cost.survey_manifest(s)
    assert m["n_used"] == 5 and all(len(u["output"]["sha256"]) == 64 and len(u["input"]["sha256"]) == 64 for u in m["used"])
