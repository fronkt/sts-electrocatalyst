"""SCF progress distinguishes electronic updates from shutdown bookkeeping."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import qe_relax_trace


def parse(tmp_path, text):
    path = tmp_path / "pw.out"
    path.write_text(text, encoding="utf-8")
    return qe_relax_trace.trace(path)


def test_exit_request_does_not_count_shutdown_or_unfinished_iteration(tmp_path):
    body = ["Self-consistent Calculation"]
    for iteration in range(1, 127):
        body += [f"     iteration # {iteration} ecut= 80.00 Ry beta= 0.30",
                 "     estimated scf accuracy < 0.00000043 Ry"]
    body += ["     iteration #127 ecut= 80.00 Ry beta= 0.30",
             "     Program stopped by user request",
             "     Calculation stopped in scf loop at iteration #   126",
             "     JOB DONE."]
    record = parse(tmp_path, "\n".join(body))
    cycle = record["cycles"][0]
    assert cycle["n_iter"] == 126
    assert cycle["n_iter_started"] == 127
    assert cycle["last_iteration_started"] == 127
    assert cycle["last_iteration_completed"] == 126
    assert cycle["iteration_records"][-1] == {"iteration": 127, "accuracy_Ry": None}
    assert cycle["converged_in"] is None
    assert not record["bfgs_converged"]


def test_threshold_crossing_keeps_iteration_identity_when_residual_missing(tmp_path):
    record = parse(tmp_path, """Self-consistent Calculation
     iteration # 39 ecut= 80.00 Ry beta= 0.30
     estimated scf accuracy < 0.00000090 Ry
     iteration # 40 ecut= 80.00 Ry beta= 0.30
     iteration # 41 ecut= 80.00 Ry beta= 0.30
     estimated scf accuracy < 0.00000008 Ry
     Calculation stopped in scf loop at iteration # 41
""")
    cycle = record["cycles"][0]
    assert cycle["n_iter"] == 2
    assert cycle["n_iter_started"] == 3
    assert cycle["first_iter_below"]["1e-07"] == 41
    assert cycle["acc_after_iter40_min_Ry"] == 8e-8
    assert cycle["acc_after_iter40_max_Ry"] == 8e-8


def test_completed_cycles_remain_separate_and_table_labels_counts(tmp_path):
    record = parse(tmp_path, """Self-consistent Calculation
     iteration # 1 ecut= 80.00 Ry beta= 0.30
     estimated scf accuracy < 0.00000090 Ry
     convergence has been achieved in 1 iterations
     new conv_thr = 0.0000000808 Ry
Self-consistent Calculation
     iteration # 1 ecut= 80.00 Ry beta= 0.30
     estimated scf accuracy < 0.00000007 Ry
     convergence has been achieved in 1 iterations
""")
    assert [cycle["n_iter"] for cycle in record["cycles"]] == [1, 1]
    assert [cycle["n_iter_started"] for cycle in record["cycles"]] == [1, 1]
    assert record["cycles"][0]["new_conv_thr_after_Ry"] == 8.08e-8
    rendered = qe_relax_trace.table(record)
    assert "nfin" in rendered and "nbeg" in rendered
