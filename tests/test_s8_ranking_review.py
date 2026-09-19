"""Independent ranking review: meaningful quantile, tie, and empty edge cases."""
import pytest

from scripts.s8_ranking_review import empty_probability, quantile_support, tie_ranks


def sites(values):
    return [{"eta_V": float(value), "seed": i // 4, "site_index": i % 4}
            for i, value in enumerate(values)]


def test_p10_120_is_interpolated_not_twelfth_order_statistic():
    result = quantile_support(sites(range(120)))
    assert result["value_V"] == pytest.approx(11.9)
    assert (result["lower_order_1based"], result["upper_order_1based"]) == (12, 13)
    assert result["weight_upper"] == pytest.approx(0.9)


def test_sparse_p10_and_tied_support_keep_site_identities():
    result = quantile_support(sites([0.4, 0.4, 0.4, 0.9]))
    assert result["value_V"] == pytest.approx(0.4)
    assert len(result["sites_at_lower_value"]) == 3
    assert len(result["sites_at_upper_value"]) == 3
    assert quantile_support(sites([0.7]))["value_V"] == pytest.approx(0.7)


def test_empty_quantile_and_missing_competitor_are_explicit():
    assert quantile_support([])["value_V"] is None
    result = tie_ranks({"A": None, "B": 0.4})
    assert result["n_requested"] == 2 and result["n_defined"] == 1
    assert not result["all_compositions_defined"]
    assert result["undefined_compositions"] == ["A"]
    assert result["ranks"]["A"]["rank_best"] is None


def test_ties_do_not_privilege_alphabetical_order():
    values = {"Z": 0.0, "A": 0.0, "C": 1 / 6}
    result = tie_ranks(values, lower_is_better=False)
    assert result["ranks"]["Z"] == result["ranks"]["A"]
    assert result["ranks"]["Z"] == {"rank_best": 2, "rank_worst": 3, "tie_size": 2}
    assert result == tie_ranks(dict(reversed(list(values.items()))), lower_is_better=False)
    assert result["raw_ties"][0]["members"] == ["A", "Z"]


def test_all_undefined_and_all_tied_are_not_winners():
    missing = tie_ranks({"A": None, "B": None})
    assert missing["n_defined"] == 0
    tied = tie_ranks({"A": 0.0, "B": 0.0, "C": 0.0})
    assert {r["rank_worst"] for r in tied["ranks"].values()} == {3}


def test_empty_cluster_probability_boundaries():
    assert empty_probability(0, 30) == 1
    assert empty_probability(30, 30) == 0
    assert empty_probability(3, 30) == pytest.approx(0.9 ** 30)
    with pytest.raises(ValueError):
        empty_probability(31, 30)
