"""End-to-end round-1 pipeline: shape, determinism, value sanity."""
import numpy as np

from hea_oer import run_round1
from hea_oer.active_learning import propose_round2
from hea_oer.composition import sample_compositions

EXPECTED_COLS = {"rank", "formula", "eta_V", "descriptor", "formability",
                 "single_phase", "abundance", "score", "pareto", "backend"}


def test_round1_shape_and_columns():
    res = run_round1(n_samples=300, top_k=4, seed=0)
    assert len(res.shortlist) == 4
    assert EXPECTED_COLS.issubset(set(res.table.columns))
    assert res.table["backend"].eq("heuristic").all()


def test_round1_values_sane():
    res = run_round1(n_samples=300, top_k=4, seed=0)
    assert np.isfinite(res.table["eta_V"]).all()
    assert res.table["formability"].between(0.0, 1.0).all()
    # shortlist must be single-phase formable and earth-abundant-leaning
    assert res.shortlist["formable"].all()


def test_round1_is_deterministic():
    a = run_round1(n_samples=300, top_k=4, seed=0)
    b = run_round1(n_samples=300, top_k=4, seed=0)
    assert a.shortlist["formula"].tolist() == b.shortlist["formula"].tolist()


def test_round2_active_learning_runs():
    res = run_round1(n_samples=300, top_k=6, seed=1)
    # synthesize "measured" overpotentials = model η + noise (scaffold exercise)
    rng = np.random.default_rng(0)
    measured = [
        (row["_comp"], float(row["eta_V"] + rng.normal(0, 0.02)))
        for _, row in res.shortlist.iterrows()
    ]
    candidates = sample_compositions(n_samples=200, seed=2)
    proposals = propose_round2(measured, candidates, n_propose=2, seed=0)
    assert len(proposals) == 2
    for comp, mu, sigma, ei in proposals:
        assert np.isfinite(mu) and sigma >= 0.0
