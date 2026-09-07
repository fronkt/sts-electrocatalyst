"""Rank-resolution statistics: synthetic data with known answers, plus the two
retained 2026-09-06 chains as a one-decoration fixture (the library must report
'insufficient decorations' and the CLI must exit 3)."""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
from scipy.special import ndtr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hea_oer import rank_resolution as rr  # noqa: E402

BANK = ROOT / "results/cr_site_chains_2026-09-06"
CLI = ROOT / "src/scripts/rank_resolution_readout.py"
PY = sys.executable
BOX = ROOT / "results/ranking_adequacy_2026-09-06/inputs/r4_screen_box.json"


# --------------------------------------------------------------------------- helpers
def synthetic_rows(mus, sigma, n_dec, n_sites, rng, between_sd=0.0):
    """Sites eta ~ N(mu_k + decoration effect, sigma^2) for composition k."""
    rows = []
    for k, mu in enumerate(mus):
        for seed in range(n_dec):
            shift = rng.normal(0.0, between_sd) if between_sd > 0 else 0.0
            for s in range(n_sites):
                rows.append({"formula": f"C{k}", "seed": seed, "site_index": s,
                             "eta": float(mu + shift + rng.normal(0.0, sigma)), "admitted": True})
    return rows


@pytest.fixture(scope="module")
def chains():
    return [json.loads((BANK / f"{arm}_result.json").read_text(encoding="utf-8")) for arm in ("equiatomic", "leader")]


def synthetic_payload(chains, mus, n_dec=3, n_sites=4, sigma=0.05, rng_seed=0, model=None, formulas=None):
    """Full screen-diagnostic-v1 payloads whose decoration slabs are the retained
    equiatomic slab with its cations re-shuffled per seed, so the environment
    path is exercised end to end.  ``model`` adds a manifest block."""
    rng = np.random.default_rng(rng_seed)
    base_row = chains[0]["results"][0]["row"]
    slab = base_row["decoration_records"][0]["relaxed_slab"]
    site_xy = base_row["per_site_records"][0]["site_xy_A"]
    payloads = []
    for k, mu in enumerate(mus):
        formula = formulas[k] if formulas else f"S{k}"
        decs, sites = [], []
        for seed in range(n_dec):
            sl = copy.deepcopy(slab)
            metals = [i for i, s in enumerate(sl["symbols"]) if s != "O"]
            perm = rng.permutation(len(metals))
            syms = [sl["symbols"][metals[j]] for j in perm]
            for i, sym in zip(metals, syms):
                sl["symbols"][i] = sym
            decs.append({"seed": seed, "n_cations": len(metals), "relaxed_slab": sl})
            for s in range(n_sites):
                eta = float(mu + rng.normal(0.0, sigma))
                oh = 1.6 + rng.normal(0.0, 0.05)
                sites.append({"seed": seed, "site_index": s, "site_xy_A": site_xy, "dG_OH": oh, "dG_O": oh + 1.23 + eta,
                              "dG_OOH": oh + 3.2, "eta": eta, "pls": 2,
                              "bonds": {"seed": seed, "site_metal": sl["symbols"][16]},
                              "initial_binding_metal_index": 16, "initial_binding_metal": sl["symbols"][16],
                              "desorbed": []})
        payload = {"schema": "screen-diagnostic-v1", "status": "complete",
                   "results": [{"formula": formula, "status": "evaluated",
                                "row": {"formula": formula, "elements": ["Fe", "Co", "Ni", "Cr"],
                                        "fractions": [0.25] * 4, "n_sites": n_dec * n_sites, "n_decorations": n_dec,
                                        "per_site_records": sites, "decoration_records": decs}}]}
        if model is not None:
            payload["manifest"] = {"model": {"filename": model, "sha256_bytes": hashlib.sha256(model.encode()).hexdigest()}}
        payloads.append(payload)
    return payloads


def run_cli(*extra, cwd=ROOT):
    return subprocess.run([PY, str(CLI), *map(str, extra)], capture_output=True, text=True, cwd=str(cwd))


# --------------------------------------------------------------------------- (f) samplers and power
def test_normal_maximum_sampler_matches_brute_force():
    rng = np.random.default_rng(1)
    mins = -rr.normal_maximum_from_uniform(rng.random(400000), 4)
    brute = np.random.default_rng(2).normal(size=(400000, 4)).min(axis=1)
    assert abs(mins.mean() - (-1.029375)) < 0.01      # E[min of 4 N(0,1)] = -1.02938
    assert abs(mins.mean() - brute.mean()) < 0.01
    assert abs(mins.std() - brute.std()) < 0.01
    huge = rr.normal_maximum_from_uniform(np.array([0.5]), 1e200)
    assert np.isfinite(huge).all() and huge[0] > 30.0   # sqrt(2 ln 1e200) ~ 30.3


def test_normal_quantile_sampler_matches_numpy_percentile():
    rng = np.random.default_rng(21)
    n = 200000
    for N, p in ((12, 0.1), (12, 0.5), (13, 0.5), (4, 0.1), (400, 0.1), (16, 0.1)):
        s = rr.normal_quantile_from_uniform(rng.random(n), rng.random(n), N, p)
        b = np.percentile(rng.normal(size=(n, N)), 100 * p, axis=1)
        assert abs(s.mean() - b.mean()) < 0.01, (N, p)
        assert abs(s.std() - b.std()) < 0.01, (N, p)
    # p = 0 is the minimum, and the rule sampler agrees with the maximum-by-symmetry path
    u = rng.random(n)
    assert np.allclose(rr.normal_quantile_from_uniform(u, u, 7, 0.0), -rr.normal_maximum_from_uniform(1.0 - u, 7), atol=1e-9)
    # large N stays finite and reaches the asymptotic sd for the 10th percentile
    s = rr.normal_quantile_from_uniform(rng.random(20000), rng.random(20000), 40000, 0.1)
    assert np.isfinite(s).all()
    assert abs(s.std() - math.sqrt(rr.QUANTILE_VARIANCE_FACTOR["p10"] / 40000)) < 0.001


def test_decorations_needed_mean_matches_repeated_experiments():
    sigma, gap, n = 0.1, 0.05, 4
    res = rr.decorations_needed(sigma, gap, n, "mean", 0.95)
    z = 1.6448536269514722
    assert res["n_sites_needed"] == math.ceil(2 * sigma ** 2 * (z / gap) ** 2 - 1e-12)   # 22 sites
    assert res["decorations_needed"] == math.ceil(res["n_sites_needed"] / n)              # 6 decorations
    assert res["decorations_needed_bracket"] == [6, 6] and not res["order_reverses_at_depth"]
    D = res["decorations_needed"]
    rng = np.random.default_rng(3)
    for d, want in ((D, True), (D - 1, False)):
        N = d * n
        a = rng.normal(0.0, sigma, size=(60000, N)).mean(axis=1)
        b = rng.normal(gap, sigma, size=(60000, N)).mean(axis=1)
        p_sim = float(np.mean(a < b))
        p_an = float(ndtr(gap / math.sqrt(2 * sigma ** 2 / N)))
        assert abs(p_sim - p_an) < 0.01
        assert (p_an >= 0.95) is want


def test_decorations_needed_min_matches_brute_force_simulation():
    sigma, gap, n = 0.1, 0.15, 4
    res = rr.decorations_needed(sigma, gap, n, "min", 0.95, n_sim=40000)
    D = res["decorations_needed"]
    assert D is not None and 1 <= D <= 50
    assert res["achieved_prob"] >= 0.95
    lo, hi = res["decorations_needed_bracket"]
    assert lo <= D <= hi
    rng = np.random.default_rng(4)
    for d in (D, max(1, D - 1)):
        N = d * n
        a = rng.normal(0.0, sigma, size=(60000, N)).min(axis=1)
        b = rng.normal(gap, sigma, size=(60000, N)).min(axis=1)
        p_brute = float(np.mean(a < b))
        p_lib = rr.order_probability("min", gap, sigma, sigma, N, n_sim=60000, rng=np.random.default_rng(5))["p_order_simulated"]
        assert abs(p_brute - p_lib) < 0.012
    if D > 1:
        N = (D - 1) * n
        p_prev = rr.order_probability("min", gap, sigma, sigma, N, n_sim=60000, rng=np.random.default_rng(6))["p_order_simulated"]
        assert p_prev < 0.95 + 0.006


def test_min_rule_saturates_and_flags_spread_decided_order():
    # 13 mV gap, site sigma ~0.32 V: the minimum cannot resolve it at any depth on the grid
    res = rr.decorations_needed((0.3241490799729384, 0.3285840051032546), 0.01306048799396554, 4, "min", 0.95,
                                n_sim=5000, max_decorations=2000)
    assert res["decorations_needed"] is None and res["saturated"]
    assert res["log10_n_sites_asymptotic"] > 100 and res["decorations_needed_closed_form"] is None
    assert len(res["scan"]) > 5 and res["scan"][-1]["decorations"] == 2000
    # wider-but-worse composition wins at depth: probability falls below 1/2 and the flag is set
    # even though no D was found (the banked pair 5 case)
    assert res["prob_at_max_decorations"] < 0.5 and res["order_reverses_at_depth"]
    pair5 = rr.decorations_needed((0.13523748906747102, 0.18412911957317757), 0.03988526123725933, 4, "min", 0.95,
                                  n_sim=5000, max_decorations=2000)
    assert pair5["saturated"] and pair5["order_reverses_at_depth"] and pair5["prob_at_max_decorations"] < 0.1
    # equal spreads: monotone under common random numbers, no reversal flag
    same = rr.decorations_needed(0.1, 0.02, 4, "min", 0.95, n_sim=5000, max_decorations=500)
    assert same["equal_spreads"] and not same["order_reverses_at_depth"]


def test_quantile_rules_exact_simulation_and_closed_form_reference():
    for rule in ("median", "p10"):
        # large N, equal spreads: the exact simulation agrees with the large-sample closed form
        out = rr.order_probability(rule, 0.05, 0.1, 0.1, 400, n_sim=20000, rng=np.random.default_rng(7))
        assert abs(out["p_order_analytic"] - out["p_order_simulated"]) < 0.02
        need = rr.decorations_needed(0.1, 0.05, 4, rule, 0.95)
        assert need["decorations_needed"] is not None
        lo, hi = need["decorations_needed_bracket"]
        assert lo <= need["decorations_needed"] <= hi
        assert need["decorations_needed"] >= rr.decorations_needed(0.1, 0.05, 4, "mean", 0.95)["decorations_needed"]
        assert abs(need["decorations_needed"] - need["decorations_needed_closed_form"]) <= max(3, 0.1 * need["decorations_needed_closed_form"])
    # 12 sites, unequal spreads (banked pair 5): p10 is near-extreme and the closed form is wrong in kind,
    # the exact curve falls with depth like the minimum
    sa, sb, gap = 0.13523748906747102, 0.18412911957317757, 0.03988526123725933
    at12 = rr.order_probability("p10", gap, sa, sb, 12, n_sim=100000, rng=np.random.default_rng(8))
    assert at12["p_order_simulated"] < 0.5 < at12["p_order_analytic"]
    brute = np.random.default_rng(9)
    A = np.percentile(brute.normal(0.0, sa, size=(100000, 12)), 10, axis=1)
    Bq = np.percentile(brute.normal(gap, sb, size=(100000, 12)), 10, axis=1)
    assert abs(float(np.mean(A < Bq)) - at12["p_order_simulated"]) < 0.01
    p10 = rr.decorations_needed((sa, sb), gap, 4, "p10", 0.95, n_sim=5000, max_decorations=2000)
    assert p10["saturated"] and p10["order_reverses_at_depth"]


def test_decorations_needed_rejects_non_positive_gap():
    with pytest.raises(ValueError):
        rr.decorations_needed(0.1, 0.0, 4, "mean")
    with pytest.raises(ValueError):
        rr.decorations_needed(0.1, 0.1, 4, "max")


# --------------------------------------------------------------------------- (b)-(e) bootstrap
def test_bootstrap_order_probability_matches_normal_theory_for_mean():
    rng = np.random.default_rng(10)
    rows = synthetic_rows([0.0, 0.03], 0.1, n_dec=40, n_sites=4, rng=rng)
    stats = rr.composition_statistic(rows, "mean")
    boot = rr.cluster_bootstrap(rows, 20000, 0, "mean")
    gaps = rr.adjacent_gap_resolvability(boot, ["C0", "C1"], point=stats)
    obs_gap = stats["C1"] - stats["C0"]
    N = 160
    v = [np.var([r["eta"] for r in rows if r["formula"] == f]) for f in ("C0", "C1")]
    p_theory = float(ndtr(obs_gap / math.sqrt(v[0] / N + v[1] / N)))
    assert abs(gaps[0]["p_order_preserved"] - p_theory) < 0.03
    assert abs(gaps[0]["gap_point_V"] - obs_gap) < 1e-12
    lo, hi = gaps[0]["gap_interval_V"]
    assert lo < obs_gap < hi


def test_bootstrap_keeps_decorations_together_under_min():
    rng = np.random.default_rng(11)
    rows = synthetic_rows([0.5], 0.05, n_dec=5, n_sites=4, rng=rng)
    seed_min = {}
    for r in rows:
        seed_min[r["seed"]] = min(seed_min.get(r["seed"], np.inf), r["eta"])
    boot = rr.cluster_bootstrap(rows, 3000, 1, "min")["C0"]
    # min over a union of whole decorations is a min over per-decoration minima
    assert set(np.round(boot, 12)).issubset(set(np.round(list(seed_min.values()), 12)))
    assert len(set(boot)) <= 5
    assert rr.bootstrap_support(3) == 10 and rr.bootstrap_support(5) == 126


def test_bootstrap_refuses_single_decoration():
    rng = np.random.default_rng(12)
    rows = synthetic_rows([0.0, 0.1], 0.1, n_dec=1, n_sites=4, rng=rng)
    assert rr.check_decorations(rows) == [("C0", 1), ("C1", 1)]
    with pytest.raises(rr.InsufficientDecorationsError, match="insufficient decorations"):
        rr.cluster_bootstrap(rows, 100, 0, "mean")


def test_statistics_and_admission():
    rows = [{"formula": "A", "seed": 0, "site_index": i, "eta": v, "admitted": True} for i, v in enumerate([0.3, 0.5, 0.7, 0.9])]
    rows += [{"formula": "A", "seed": 1, "site_index": i, "eta": v, "admitted": (i != 0)} for i, v in enumerate([0.1, 0.6, 0.8, 1.0])]
    assert rr.composition_statistic(rows, "min")["A"] == 0.3            # 0.1 not admitted
    assert abs(rr.composition_statistic(rows, "mean")["A"] - np.mean([0.3, 0.5, 0.7, 0.9, 0.6, 0.8, 1.0])) < 1e-12
    assert abs(rr.composition_statistic(rows, "median")["A"] - 0.7) < 1e-12
    assert abs(rr.composition_statistic(rows, "p10")["A"] - np.percentile([0.3, 0.5, 0.7, 0.9, 0.6, 0.8, 1.0], 10)) < 1e-12
    census = rr.decoration_census(rows)["A"]
    assert census["n_decorations"] == 2 and census["n_admitted"] == 7 and census["usable_seeds"] == [0, 1]


def test_single_model_check_and_kendall_tau():
    rows = [{"formula": "A", "seed": 0, "site_index": 0, "eta": 0.1, "model_filename": "m1", "model_sha256": "x"},
            {"formula": "A", "seed": 0, "site_index": 1, "eta": 0.2, "model_filename": "m1", "model_sha256": "x"}]
    assert rr.check_single_model(rows)["models"] == [("m1", "x")]
    mixed = rows + [{"formula": "A", "seed": 0, "site_index": 0, "eta": 0.3, "model_filename": "m2", "model_sha256": "y"}]
    with pytest.raises(rr.MixedModelError, match="within a decoration"):
        rr.check_single_model(mixed)
    across = rows + [{"formula": "B", "seed": 0, "site_index": 0, "eta": 0.3, "model_filename": "m2", "model_sha256": "y"}]
    with pytest.raises(rr.MixedModelError, match="across the table"):
        rr.check_single_model(across)
    assert rr.kendall_tau_a(["a", "b", "c"], ["a", "b", "c"]) == 1.0
    assert rr.kendall_tau_a(["c", "b", "a"], ["a", "b", "c"]) == -1.0
    assert abs(rr.kendall_tau_a(["b", "a", "c"], ["a", "b", "c"]) - 1 / 3) < 1e-12


def test_rank_matrix_is_doubly_stochastic_and_pairwise_antisymmetric():
    rng = np.random.default_rng(13)
    rows = synthetic_rows([0.0, 0.02, 0.5], 0.1, n_dec=10, n_sites=4, rng=rng)
    boot = rr.cluster_bootstrap(rows, 5000, 2, "mean")
    rm = rr.rank_probability_matrix(boot)
    assert np.allclose(rm["rank_matrix"].sum(axis=1), 1.0)
    assert np.allclose(rm["rank_matrix"].sum(axis=0), 1.0)
    pw = rm["pairwise"]
    assert np.allclose(pw + pw.T, 1.0)
    assert rm["rank_matrix"][2, 2] > 0.99                     # C2 is far worse: always last
    assert pw[0, 2] > 0.99 and 0.3 < pw[0, 1] < 0.95
    gaps = rr.adjacent_gap_resolvability(boot, ["C0", "C1", "C2"])
    assert gaps[1]["p_order_preserved"] > 0.99 and gaps[1]["gap_interval_V"][0] > 0
    # identical compositions: P(order) is not a fixed number (it is uniform over draws);
    # it must track Phi(observed gap / se) for the draw in hand
    same_rows = synthetic_rows([0.0, 0.0], 0.1, 30, 4, np.random.default_rng(14))
    same = rr.cluster_bootstrap(same_rows, 5000, 0, "mean")
    same_stats = rr.composition_statistic(same_rows, "mean")
    p_same = rr.adjacent_gap_resolvability(same, ["C0", "C1"])[0]["p_order_preserved"]
    v = [np.var([r["eta"] for r in same_rows if r["formula"] == f]) for f in ("C0", "C1")]
    p_theory = float(ndtr((same_stats["C1"] - same_stats["C0"]) / math.sqrt((v[0] + v[1]) / 120)))
    assert abs(p_same - p_theory) < 0.03


# --------------------------------------------------------------------------- (h) variance components
def test_variance_components_recover_planted_icc():
    rng = np.random.default_rng(15)
    rows = synthetic_rows([0.0], 0.1, n_dec=300, n_sites=4, rng=rng, between_sd=0.2)
    vc = rr.variance_components(rows)["C0"]
    assert vc["status"] == "ok"
    assert abs(vc["within_sd"] - 0.1) < 0.02
    assert abs(vc["between_sd"] - 0.2) < 0.04
    assert abs(vc["icc"] - 0.8) < 0.08
    flat = rr.variance_components(synthetic_rows([0.0], 0.1, 300, 4, np.random.default_rng(16)))["C0"]
    assert flat["icc"] < 0.05


# --------------------------------------------------------------------------- (g) ridge
def test_ridge_recovers_planted_coefficients_and_loo_identity():
    rng = np.random.default_rng(17)
    n, p = 200, 6
    X = rng.integers(0, 5, size=(n, p)).astype(float)
    beta = np.array([0.05, -0.03, 0.02, 0.0, 0.04, -0.01])
    y = 0.4 + X @ beta + rng.normal(0.0, 0.01, size=n)
    rows = [{"eta": float(v)} for v in y]
    fit = rr.ridge_model(rows, X, alpha=1e-6, feature_names=[f"n{k}" for k in range(p)])
    assert fit["status"] == "ok" and fit["meaningful"]
    assert np.allclose([fit["coefficients"][f"n{k}"] for k in range(p)], beta, atol=0.006)
    assert abs(fit["intercept"] - 0.4) < 0.02
    assert fit["r2_loo"] > 0.95 and 0.007 < fit["sigma_loo"] < 0.015
    # leave-one-out shortcut equals brute-force refits (alpha = 1, n = 40)
    Xs, ys = X[:40], y[:40]
    fit2 = rr.ridge_model([{"eta": float(v)} for v in ys], Xs, alpha=1.0)
    loo = []
    for i in range(40):
        m = np.ones(40, bool); m[i] = False
        f = rr.ridge_model([{"eta": float(v)} for v in ys[m]], Xs[m], alpha=1.0)
        pred = f["intercept"] + Xs[i] @ np.array(list(f["coefficients"].values()))
        loo.append(ys[i] - pred)
    assert abs(math.sqrt(np.mean(np.square(loo))) - fit2["sigma_loo"]) < 1e-9


def test_ridge_degrades_gracefully_on_small_censuses():
    rng = np.random.default_rng(18)
    X = rng.integers(0, 5, size=(5, 12)).astype(float)
    rows = [{"eta": float(v)} for v in rng.normal(size=5)]
    under = rr.ridge_model(rows, X)
    assert under["status"] == "underdetermined" and under["coefficients"] is None and not under["meaningful"]
    X = rng.integers(0, 5, size=(20, 6)).astype(float)
    rows = [{"eta": float(v)} for v in rng.normal(size=20)]
    small = rr.ridge_model(rows, X)
    assert small["status"] == "insufficient_sites" and small["coefficients"] is not None and not small["meaningful"]


# --------------------------------------------------------------------------- real fixture: the two retained chains
def test_two_chains_load_and_report_insufficient_decorations(chains):
    rows = rr.load_site_table(chains)
    assert [(r["formula"], r["seed"], r["site_index"], r["site_metal"]) for r in rows] == [
        ("Fe25Co25Ni25Cr25", 2, 0, "Cr"), ("Ni31Cr29Cu5Mn35", 0, 0, "Cr")]
    assert rows[0]["desorbed"] == [] and rows[1]["desorbed"] == ["OOH"] and rows[1]["desorbed_any"]
    assert rows[0]["evidence_status"] == "eligible" and rows[1]["evidence_status"] == "failed"
    assert rows[0]["eta"] == 0.4530565522419163 and rows[1]["eta"] == 0.9780789066094675
    assert rows[0]["eta_cus"] == rows[0]["eta"]
    assert rows[1]["final_binding_metals"]["OOH"] == "Ni"
    assert all(r["converged"] for r in rows)
    assert all(r["model_filename"] == "macempa0mediummodel" for r in rows)
    assert rr.check_single_model(rows)["models"] == [("macempa0mediummodel", "75428afe3a1d7d8062e19bcaabd5c433623cabf308242ec9fb493e38604fb638")]
    assert rr.check_decorations(rows) == [("Fe25Co25Ni25Cr25", 1), ("Ni31Cr29Cu5Mn35", 1)]
    with pytest.raises(rr.InsufficientDecorationsError, match="insufficient decorations"):
        rr.cluster_bootstrap(rows, 100, 0, "min")
    vc = rr.variance_components(rows)
    assert all(v["status"] == "insufficient decorations" for v in vc.values())
    eligible = rr.load_site_table(chains, admitted=lambda r: r["evidence_status"] == "eligible")
    assert [r["admitted"] for r in eligible] == [True, False]
    assert math.isnan(rr.composition_statistic(eligible, "min")["Ni31Cr29Cu5Mn35"])
    # the annotate hook runs before admission and may add keys
    tagged = rr.load_site_table(chains, admitted=lambda r: r["tag"] == "keep",
                                annotate=lambda rec, site, row: rec.__setitem__("tag", "keep" if site["seed"] == 2 else "drop"))
    assert [r["admitted"] for r in tagged] == [True, False]


def test_two_chains_local_environments_and_ridge_degrade(chains):
    rows = rr.load_site_table(chains)
    envs = []
    for payload, r in zip(chains, rows):
        row = payload["results"][0]["row"]
        env = rr.local_environment_features(row["decoration_records"][0]["relaxed_slab"], r["site_xy_A"], 3.8)
        assert env["center_index"] == 16 and env["center_metal"] == "Cr"
        assert env["center_offset_A"] < 0.1
        assert env["n_neighbours"] == 8 and sum(env["counts"].values()) == 8
        assert 2.8 < env["distances_A"][0] < 3.1 and env["distances_A"][-1] < 3.8
        envs.append(env)
    assert envs[0]["counts"] == {"Co": 4, "Cr": 0, "Fe": 4, "Ni": 0}
    assert envs[1]["counts"] == {"Cr": 3, "Cu": 1, "Mn": 0, "Ni": 4}
    explicit = rr.local_environment_features(chains[1]["results"][0]["row"]["decoration_records"][0]["relaxed_slab"],
                                             rows[1]["site_xy_A"], 3.8, center_index=16)
    assert explicit["counts"] == envs[1]["counts"]
    X, names = rr.feature_matrix(rows, envs)
    assert X.shape == (2, 12) and X[0, names.index("center_Cr")] == 1.0 and X[0, names.index("n_Co")] == 4
    fit = rr.ridge_model(rows, X, feature_names=names)
    assert fit["status"] == "underdetermined" and fit["coefficients"] is None
    assert "30" in fit["message"]


def test_cli_exits_3_on_the_one_decoration_fixture(tmp_path):
    out = tmp_path / "readout" / "rank_resolution.json"
    proc = run_cli("--results", BANK, "--stems", "*", "--B", "200", "--out", out)
    assert proc.returncode == 3, proc.stderr
    assert "insufficient decorations" in proc.stdout
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "insufficient_decorations"
    assert "bootstrap_intervals" not in data and "rank_probability" not in data
    assert data["statistics"]["min"]["Fe25Co25Ni25Cr25"] == 0.4530565522419163
    assert data["banked_order"][:2] == ["Ni31Cr29Cu5Mn35", "Fe25Co25Ni25Cr25"]
    assert data["model"]["filename"] == "macempa0mediummodel"
    assert data["coverage"]["unverified"] is True and data["coverage"]["expected"] == []
    # T2 reproduction against the banked eta at the docs/91 bar
    rep = data["reproduction"]
    assert rep["Fe25Co25Ni25Cr25"]["verdict"] == "REPRODUCED"
    assert rep["Fe25Co25Ni25Cr25"]["abs_difference_V"] == abs(0.4530565522419163 - 0.4530565517906915)
    assert rep["Ni31Cr29Cu5Mn35"]["verdict"] == "NOT REPRODUCED"      # seed-0 site, not the banked seed-1 winner
    assert rep["Ni31Cr29Cu5Mn35"]["abs_difference_V"] == abs(0.9780789066094675 - 0.43999606379672596)
    assert rep["Ni31Cr29Cu5Mn35"]["seeds"] == [0, 1, 2] and rep["Ni31Cr29Cu5Mn35"]["n_sites"] == 1
    assert "NOT REPRODUCED" in proc.stdout and "abs(census min - banked)" in proc.stdout
    assert data["census_orders"]["min"]["kendall_tau_a_vs_banked"] == -1.0
    assert data["ridge"]["fits"]["eta"]["status"] == "underdetermined"
    # T7: each rule on its own banked gap, and the hypothetical min-gap block
    pair = data["banked_reference"]["pairs"][0]
    assert pair["gap_min_V"] == 0.4530565517906915 - 0.43999606379672596
    assert pair["gap_mean_V"] == 1.046721011508203 - 0.9103271635814684
    assert pair["own_gap"]["mean"]["decorations_needed"] == 8 and pair["own_gap"]["mean"]["gap_source"] == "banked eta_mean"
    assert pair["own_gap"]["median"]["decorations_needed"] is None and "no box estimate" in pair["own_gap"]["median"]["message"]
    assert pair["own_gap"]["min"]["saturated"] and pair["own_gap"]["min"]["order_reverses_at_depth"]
    assert pair["hypothetical_min_gap"]["mean"]["decorations_needed"] == 845
    assert "saturated: P(10000)" in proc.stdout and "no box estimate" in proc.stdout
    assert b"\r" not in out.read_bytes()


def test_cli_classifier_policies_on_the_fixture(tmp_path):
    pytest.importorskip("hea_oer.site_integrity")
    for policy, want in (("intact", [False, False]), ("adsorbate-intact", [True, False]), ("two-pathway", [True, False])):
        out = tmp_path / f"{policy}.json"
        proc = run_cli("--results", BANK, "--stems", "*", "--B", "50", "--admit", policy, "--out", out)
        assert proc.returncode == 3, proc.stderr
        data = json.loads(out.read_text(encoding="utf-8"))
        assert [r["admitted"] for r in data["site_rows"]] == want, policy
        assert data["site_rows"][1]["state_categories"]["OOH"] == "DESORPTION"
        assert data["site_rows"][0]["pathway"] == "cus" and data["site_rows"][1]["pathway"] == "undefined"
        assert data["settings"]["admit_definition"]
        # the eta is never replaced by a policy
        assert data["site_rows"][0]["eta"] == 0.4530565522419163


def test_cli_full_readout_on_synthetic_census(tmp_path, chains):
    payloads = synthetic_payload(chains, [0.40, 0.42, 0.70], n_dec=3, n_sites=4)
    src = tmp_path / "census"
    src.mkdir()
    for k, pl in enumerate(payloads):
        (src / f"S{k}_result.json").write_text(json.dumps(pl), encoding="utf-8")
    (src / "note.json").write_text("{}", encoding="utf-8")
    out = tmp_path / "readout.json"
    proc = run_cli("--results", src, "--stems", "*", "--B", "2000", "--seed", "1", "--box", tmp_path / "absent.json", "--out", out)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "complete" and data["n_site_rows"] == 36
    assert data["banked_order"] == ["S0", "S1", "S2"]
    assert len(data["inputs"]["skipped"]) == 1
    for rule in rr.RULES:
        assert set(data["bootstrap_intervals"][rule]) == {"S0", "S1", "S2"}
        assert len(data["adjacent_gaps"][rule]) == 2
        assert all(len(row) == 3 for row in data["rank_probability"][rule]["rank_matrix"])
        assert all(g["verdict"] in ("RESOLVED", "UNRESOLVED", "INVERTED", "RESOLVED / SPREAD-DECIDED", "UNRESOLVED / SPREAD-DECIDED")
                   for g in data["adjacent_gaps"][rule])
    far = data["adjacent_gaps"]["mean"][1]
    assert far["resolved"] and far["p_order_preserved"] > 0.99 and far["verdict"] == "RESOLVED"
    assert far["decorations_needed"]["decorations_needed"] == 1
    assert data["rank_probability"]["mean"]["stable"]["S2"]["stable"] and data["rank_probability"]["mean"]["stable"]["S2"]["banked_rank"] == 3
    assert data["resolved_boundaries"]["mean"] >= 1 and data["n_boundaries"] == 2
    assert data["census_orders"]["mean"]["kendall_tau_a_vs_banked"] == 1.0
    assert all(v["verdict"] == "-" for v in data["reproduction"].values())      # no box: no reproduction check
    assert data["ridge"]["fits"]["eta"]["status"] == "ok" and data["ridge"]["n_sites_with_environment"] == 36
    assert all(v["status"] == "ok" for v in data["variance_components"].values())
    assert "## T3 Rank-probability matrix (min rule" in proc.stdout and "STABLE" in proc.stdout
    assert b"\r" not in out.read_bytes()
    # an inverted pair under the mean is labelled INVERTED, not resolved
    inv = synthetic_payload(chains, [0.40, 0.42], n_dec=3, n_sites=4, rng_seed=3)
    inv[0]["results"][0]["row"]["per_site_records"][0]["eta"] = 0.10          # S0 keeps the min, S1 has the lower mean
    for s in inv[1]["results"][0]["row"]["per_site_records"]:
        s["eta"] -= 0.20
    src2 = tmp_path / "census_inv"
    src2.mkdir()
    for k, pl in enumerate(inv):
        (src2 / f"S{k}_result.json").write_text(json.dumps(pl), encoding="utf-8")
    proc = run_cli("--results", src2, "--stems", "*", "--B", "500", "--box", tmp_path / "absent.json", "--out", tmp_path / "inv.json")
    assert proc.returncode == 0, proc.stderr
    inv_data = json.loads((tmp_path / "inv.json").read_text(encoding="utf-8"))
    assert inv_data["banked_order"] == ["S0", "S1"]
    g = inv_data["adjacent_gaps"]["mean"][0]
    assert g["gap_point_V"] < 0 and g["verdict"] == "INVERTED" and g["inverted"] and not g["resolved"]
    assert inv_data["inverted_boundaries"]["mean"] == 1 and "INVERTED" in proc.stdout


def test_cli_refuses_mixed_models_in_one_directory(tmp_path, chains):
    a = synthetic_payload(chains, [0.40, 0.45], n_dec=3, n_sites=4, model="macempa0mediummodel")
    b = synthetic_payload(chains, [0.41, 0.44], n_dec=3, n_sites=4, model="maceomat0mediummodel", rng_seed=5)
    src = tmp_path / "results"
    src.mkdir()
    for k, pl in enumerate(a):
        (src / f"mpa0__S{k}_result.json").write_text(json.dumps(pl), encoding="utf-8")
    for k, pl in enumerate(b):
        (src / f"omat0__S{k}_result.json").write_text(json.dumps(pl), encoding="utf-8")
    # the default stem filter keeps only the mpa0 files: one model, readout complete
    proc = run_cli("--results", src, "--B", "200", "--box", tmp_path / "absent.json", "--out", tmp_path / "mpa0.json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads((tmp_path / "mpa0.json").read_text(encoding="utf-8"))
    assert data["model"]["filename"] == "macempa0mediummodel" and data["n_site_rows"] == 24
    assert sum("outside --stems" in s for s in data["inputs"]["skipped"]) == 2
    # asking for every stem mixes two models on the same (formula, seed): refused
    proc = run_cli("--results", src, "--stems", "*", "--B", "200", "--box", tmp_path / "absent.json", "--out", tmp_path / "mixed.json")
    assert proc.returncode == 2 and "mixed models" in proc.stderr
    assert not (tmp_path / "mixed.json").exists()


def test_cli_census_layout_expected_stems_and_manifest_ids(tmp_path, chains):
    """Layout of results/site_census_2026-09-06: manifests/<stem>.json with manifest_id,
    MANIFESTS.sha256 listing every stem, results/<stem>_result.json."""
    census = tmp_path / "site_census"
    (census / "manifests").mkdir(parents=True)
    (census / "results").mkdir()
    stems = ["mpa0__S0", "mpa0__S1", "omat0__S0"]
    lines = []
    for stem in stems:
        manifest = {"manifest_id": hashlib.sha256(stem.encode()).hexdigest(), "model": {"filename": stem.split("__")[0]}}
        text = json.dumps(manifest)
        (census / "manifests" / f"{stem}.json").write_text(text, encoding="utf-8")
        lines.append(f"{hashlib.sha256(text.encode()).hexdigest()}  manifests/{stem}.json")
    (census / "MANIFESTS.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    payloads = synthetic_payload(chains, [0.40, 0.45], n_dec=3, n_sites=4, model="macempa0mediummodel")
    payloads[0]["manifest_id"] = hashlib.sha256(b"mpa0__S0").hexdigest()
    (census / "results" / "mpa0__S0_result.json").write_text(json.dumps(payloads[0]), encoding="utf-8")
    absent = tmp_path / "absent.json"
    # S1 has not landed: refused without --partial, and the missing stem is named
    proc = run_cli("--results", census / "results", "--B", "100", "--box", absent, "--out", tmp_path / "a.json")
    assert proc.returncode == 2 and "mpa0__S1" in proc.stderr and "omat0__S0" not in proc.stderr
    # --partial reads what exists, status partial, missing stems listed in the JSON
    proc = run_cli("--results", census / "results", "--partial", "--B", "100", "--box", absent, "--out", tmp_path / "b.json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads((tmp_path / "b.json").read_text(encoding="utf-8"))
    assert data["status"] == "partial" and data["coverage"]["missing"] == ["mpa0__S1"]
    assert data["coverage"]["expected"] == ["mpa0__S0", "mpa0__S1"] and data["coverage"]["partial"] is True
    assert "MISSING: mpa0__S1" in proc.stdout
    # a result whose manifest_id differs from its manifest is refused; a foreign stem is refused
    payloads[1]["manifest_id"] = "0" * 64
    (census / "results" / "mpa0__S1_result.json").write_text(json.dumps(payloads[1]), encoding="utf-8")
    (census / "results" / "mpa0__S9_result.json").write_text(json.dumps(payloads[1]), encoding="utf-8")
    proc = run_cli("--results", census / "results", "--partial", "--B", "100", "--box", absent, "--out", tmp_path / "c.json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads((tmp_path / "c.json").read_text(encoding="utf-8"))
    reasons = {r["stem"]: r["reason"] for r in data["coverage"]["refused"]}
    assert "manifest_id differs" in reasons["mpa0__S1"] and "absent from MANIFESTS.sha256" in reasons["mpa0__S9"]
    assert data["coverage"]["missing"] == ["mpa0__S1"]
    # with the right manifest_id the census is complete
    payloads[1]["manifest_id"] = hashlib.sha256(b"mpa0__S1").hexdigest()
    (census / "results" / "mpa0__S1_result.json").write_text(json.dumps(payloads[1]), encoding="utf-8")
    proc = run_cli("--results", census / "results", "--B", "100", "--box", absent, "--out", tmp_path / "d.json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads((tmp_path / "d.json").read_text(encoding="utf-8"))
    assert data["status"] == "complete" and data["coverage"]["missing"] == [] and data["n_site_rows"] == 24
    assert str(census / "MANIFESTS.sha256") == data["coverage"]["manifest_hashes"]
    # the reproduction check reads only the banked seeds: an extra-decoration site below the banked
    # minimum does not turn a REPRODUCED composition into NOT REPRODUCED
    box = {"n_sites": 4, "seeds": [0, 1, 2], "rows": [
        {"formula": "S0", "eta": min(s["eta"] for s in payloads[0]["results"][0]["row"]["per_site_records"]), "eta_mean": 0.5, "eta_std": 0.05},
        {"formula": "S1", "eta": 0.2, "eta_mean": 0.6, "eta_std": 0.05}]}
    (tmp_path / "box.json").write_text(json.dumps(box), encoding="utf-8")
    extra = synthetic_payload(chains, [0.40], n_dec=1, n_sites=4, model="macempa0mediummodel", rng_seed=11)
    for s in extra[0]["results"][0]["row"]["per_site_records"]:
        s["seed"] = 7
        s["eta"] = 0.01
    extra[0]["results"][0]["row"]["decoration_records"][0]["seed"] = 7
    (census / "results" / "mpa0_ext__S0__s07-07_result.json").write_text(json.dumps(extra[0]), encoding="utf-8")
    proc = run_cli("--results", census / "results", "--manifest-hashes", tmp_path / "none.sha256", "--manifests", tmp_path / "nomanifests",
                   "--B", "100", "--box", tmp_path / "box.json", "--out", tmp_path / "e.json")
    assert proc.returncode == 0, proc.stderr
    data = json.loads((tmp_path / "e.json").read_text(encoding="utf-8"))
    assert data["census"]["S0"]["n_decorations"] == 4 and data["statistics"]["min"]["S0"] == 0.01
    assert data["reproduction"]["S0"]["verdict"] == "REPRODUCED" and data["reproduction"]["S0"]["n_sites"] == 12
    assert data["reproduction"]["S1"]["verdict"] == "NOT REPRODUCED"


def test_compare_flags_policy_dependent_boundaries(tmp_path):
    sys.path.insert(0, str(CLI.parent))
    import rank_resolution_readout as cli  # noqa: E402

    def readout(policy, verdict_ab, p_ab):
        return {"schema": "rank-resolution-v1", "status": "complete", "settings": {"admit": policy, "rules": ["min", "mean"]},
                "adjacent_gaps": {rule: [{"better": "A", "worse": "B", "verdict": verdict_ab if rule == "mean" else "UNRESOLVED",
                                          "p_order_preserved": p_ab, "gap_point_V": 0.01},
                                         {"better": "B", "worse": "C", "verdict": "RESOLVED", "p_order_preserved": 0.99, "gap_point_V": 0.2}]
                                  for rule in ("min", "mean")}}
    paths = []
    for policy, v, p in (("all", "UNRESOLVED", 0.7), ("intact", "RESOLVED", 0.97), ("two-pathway", "UNRESOLVED / SPREAD-DECIDED", 0.6)):
        path = tmp_path / f"{policy}.json"
        path.write_text(json.dumps(readout(policy, v, p)), encoding="utf-8")
        paths.append(path)
    cmp = cli.compare_readouts(paths, 0.95)
    assert cmp["policies"] == ["all", "intact", "two-pathway"]
    dep = [b for b in cmp["boundaries"] if b["policy_dependent"]]
    assert len(dep) == 1 and dep[0]["rule"] == "mean" and (dep[0]["better"], dep[0]["worse"]) == ("A", "B")
    assert dep[0]["p_order"] == {"all": 0.7, "intact": 0.97, "two-pathway": 0.6}
    assert cmp["n_policy_dependent"] == 1
    proc = run_cli("--compare", *paths, "--out", tmp_path / "cmp.json")
    assert proc.returncode == 0, proc.stderr
    assert "POLICY-DEPENDENT" in proc.stdout and "policy-dependent boundaries: 1 of 4" in proc.stdout
    assert json.loads((tmp_path / "cmp.json").read_text(encoding="utf-8"))["n_policy_dependent"] == 1
