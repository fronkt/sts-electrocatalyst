"""Exact boundary behavior, scaling-floor identities and frozen source integrity."""
import copy
import json
from fractions import Fraction as Q

import pytest

from s2.divanis.curve import (analyze, classify_count, partition_events, row_at,
                              serializable)
from s2.divanis.independent import verify
from s2.divanis.source import DEFAULT_SELECTION, REPO, Row, load_population, parse_rows


def row(oh, oxygen, ooh, name="toy"):
    tokens = (oh, oxygen, ooh, "4.92")
    return Row(name, 1, 1, "RuO2", tuple(Q(x) for x in tokens), tokens,
               "1 RuO2 " + " ".join(tokens))


def test_eta_threshold_is_strict_and_margin_threshold_is_inclusive():
    # At delta=.05, eta=.60 exactly while the margin still qualifies.
    strict = row("0", "2.08", "3.56")
    at = row_at(strict, Q("0.05"))
    assert at["eta"] == Q("0.60") and at["margin_within"]
    assert not at["eta_below"] and not at["selected"]
    assert row_at(strict, Q("0.049"))["selected"]
    inclusive = row("0", "2.10", "3.40")
    at = row_at(inclusive, Q("0.10"))
    assert at["margin"] == Q("0.050") and at["selected"]
    assert not row_at(inclusive, Q("0.099"))["selected"]


def test_both_predicate_boundary_events_are_retained_at_endpoints():
    strict = row("0", "2.08", "3.56")
    events = partition_events([strict])
    assert any(r["kind"] == "eta_equals_0.60" for r in events[Q("0.05")])
    inclusive = row("0", "2.10", "3.40")
    events = partition_events([inclusive])
    assert any(r["kind"] == "margin_equals_0.050" for r in events[Q("0.10")])


def test_che_crossing_preserves_ties_and_two_sides():
    r = row("1", "1.99", "3.08")
    assert row_at(r, Q("0.049"))["active_steps"] == (4,)
    assert row_at(r, Q("0.05"))["active_steps"] == (3, 4)
    assert row_at(r, Q("0.051"))["active_steps"] == (3,)
    events = partition_events([r])
    assert any(e["kind"] == "CHE_active_step_crossing" for e in events[Q("0.05")])


def test_exact_floor_handles_both_scaling_branches():
    r = row("0", "1", "2.41")
    assert row_at(r, Q("0.05"))["floor"] == 0
    assert row_at(r, Q("0.05"))["active_floor_branches"] == (0, 1)
    assert row_at(r, Q("0.025"))["floor"] == row_at(r, Q("0.075"))["floor"] == Q("0.0125")
    assert any(e["kind"] == "scaling_floor_branch_crossing"
               for e in partition_events([r])[Q("0.05")])


def test_negative_fourth_step_is_strict_and_does_not_remove_row():
    r = row("1", "2", "4.52")
    assert row_at(r, Q("0.05"))["steps"][3] == 0
    assert not row_at(r, Q("0.05"))["negative_dg4"]
    assert row_at(r, Q("0.051"))["negative_dg4"]
    result = analyze([r])
    assert all(c["aggregate"]["denominator"] == 1 for c in result["cells"])
    assert not result["invariance"]["negative_dg4_membership_invariant"]


def test_partition_covers_every_endpoint_and_open_interval():
    r = row("0", "2.08", "3.56")
    result = analyze([r])
    cells = result["cells"]
    assert cells[0]["kind"] == cells[-1]["kind"] == "point"
    assert cells[0]["delta"] == 0 and cells[-1]["delta"] == Q("0.10")
    state = ("active_steps", "eta_below", "margin_within", "selected", "negative_dg4")
    for cell in cells:
        if cell["kind"] == "open_interval":
            left, right = cell["left"], cell["right"]
            for sample in ((3 * left + right) / 4, (left + 3 * right) / 4):
                check = row_at(r, sample)
                assert all(check[k] == cell["rows"][0][k] for k in state)
    with pytest.raises(ValueError):
        analyze([r, r])


@pytest.mark.parametrize("n,expected", [(0, "FALSIFIED"), (3, "FALSIFIED"),
                                        (4, "SCORED — MIDDLE BAND / NOT MET"),
                                        (9, "SCORED — MIDDLE BAND / NOT MET"), (10, "HELD"), (38, "HELD")])
def test_registered_count_bands(n, expected):
    assert classify_count(n) == expected


def test_parser_does_not_whitelist_articles_or_deduplicate():
    text = "99 CoO2b 1.1 2 3 4.92\n99 CoO2b 1.1 2 3 4.92\n1 FeO2/other 1 2 3 4.92\n"
    found = parse_rows(text, 1, 3)
    assert len(found) == 2 and [r.source_line for r in found] == [1, 2]
    assert all(r.article_id == 99 and r.structure_token == "CoO2b" for r in found)


def test_frozen_selection_matches_raw_source_and_registered_guard():
    rows, ev = load_population()
    assert len(rows) == 38 and ev["article_denominators"] == {"1": 26, "7": 11, "9": 1}
    r = next(r for r in rows if r.source_line == 152)
    result = row_at(r, Q("0.05"))
    assert result["eta"] == Q("1.96") and result["steps"][3] == Q("-0.46")
    assert result["active_steps"] == (3,)


def test_source_or_selection_changes_refused(tmp_path):
    manifest = json.loads(DEFAULT_SELECTION.read_text(encoding="utf-8"))
    source = tmp_path / "source.txt"
    source.write_bytes((REPO / manifest["source"]["path"]).read_bytes() + b"\n")
    with pytest.raises(ValueError, match="source hash"):
        load_population(source_path=source)
    manifest["rows"][0]["structure_token"] = "CuO2"
    selection = tmp_path / "selection.json"
    selection.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="identity mismatch"):
        load_population(selection)


def test_independent_raw_verification_and_corruption_detection():
    rows, ev = load_population()
    result = analyze(rows)
    verified = verify(result, ev["source_path"])
    assert verified["passed"] and verified["raw_rows"] == 38
    assert verified["independent_candidate_breakpoints"] >= len(result["breakpoints"])
    broken = copy.deepcopy(result)
    broken["cells"][0]["rows"][0]["eta"] += Q("0.01")
    with pytest.raises(AssertionError, match="arithmetic mismatch"):
        verify(broken, ev["source_path"])


def test_fraction_serialization_preserves_exact_values():
    assert serializable({"delta": Q(1, 30)}) == {"delta": {"exact": "1/30", "display": float(Q(1, 30))}}
