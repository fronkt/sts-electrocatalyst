"""Unit tests for the multi-element stability metric.

The arithmetic is tested against hand-built assemblages rather than the Materials
Project, so these run offline, need no API key, and fail for exactly one reason: the
soluble-cation bookkeeping is wrong. The MP-backed behaviour is checked separately by
`test_reproduces_docs31_single_element_assignments`, which is skipped without a cache.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "dft"))

from dft.pourbaix_multi import _parts, soluble_fraction  # noqa: E402

CACHE = os.path.join(os.path.dirname(__file__), "..", "results", "r2_mp_cache.json")


@dataclass
class FakeComp:
    """Minimal stand-in for a pymatgen Composition: element -> moles."""
    counts: dict

    def __iter__(self):
        return iter([type("El", (), {"symbol": s})() for s in self.counts])

    def __getitem__(self, el):
        return self.counts[getattr(el, "symbol", el)]

    @property
    def reduced_formula(self):
        return "".join(f"{k}{v:g}" for k, v in self.counts.items())


@dataclass
class FakeEntry:
    composition: FakeComp
    phase_type: str


def entry(counts: dict, phase: str) -> FakeEntry:
    return FakeEntry(FakeComp(counts), phase)


@dataclass
class FakeMulti:
    entry_list: list
    weights: list


ELEMENTS = ["Fe", "Ni", "Co", "Mn"]


def test_all_solid_is_fully_insoluble():
    m = FakeMulti([entry({"Fe": 1.0}, "Solid"), entry({"Ni": 1.0}, "Solid")], [1.0, 1.0])
    assert soluble_fraction(m, ELEMENTS)["soluble_cation_fraction"] == pytest.approx(0.0)


def test_all_ionic_is_fully_soluble():
    m = FakeMulti([entry({"Mn": 1.0}, "Ion"), entry({"Ni": 1.0}, "Ion")], [1.0, 1.0])
    assert soluble_fraction(m, ELEMENTS)["soluble_cation_fraction"] == pytest.approx(1.0)


def test_fraction_is_weighted_by_cation_moles_not_phase_count():
    """Two phases, wildly different amounts. Counting phases would give 0.5; the
    metric must report the fraction of the material, which is 0.1."""
    m = FakeMulti([entry({"Fe": 0.9}, "Solid"), entry({"Mn": 0.1}, "Ion")], [1.0, 1.0])
    assert soluble_fraction(m, ELEMENTS)["soluble_cation_fraction"] == pytest.approx(0.1)


def test_multientry_weights_are_applied():
    m = FakeMulti([entry({"Fe": 1.0}, "Solid"), entry({"Mn": 1.0}, "Ion")], [3.0, 1.0])
    assert soluble_fraction(m, ELEMENTS)["soluble_cation_fraction"] == pytest.approx(0.25)


def test_oxygen_and_hydrogen_do_not_count_as_cations():
    """Fe2O3 must contribute 2 cation moles, not 5. Counting the O would dilute every
    solid and make everything look more stable than it is."""
    m = FakeMulti([entry({"Fe": 2.0, "O": 3.0}, "Solid"),
                   entry({"Mn": 2.0, "O": 4.0}, "Ion")], [1.0, 1.0])
    assert soluble_fraction(m, ELEMENTS)["soluble_cation_fraction"] == pytest.approx(0.5)


def test_plain_entry_is_handled_like_a_single_part():
    e = entry({"Fe": 1.0}, "Solid")
    assert _parts(e) == [(e, 1.0)]
    r = soluble_fraction(entry({"Mn": 1.0}, "Ion"), ELEMENTS)
    assert r["soluble_cation_fraction"] == pytest.approx(1.0)
    assert len(r["phases"]) == 1


def test_phases_are_reported_largest_first():
    m = FakeMulti([entry({"Mn": 0.1}, "Ion"), entry({"Fe": 0.9}, "Solid")], [1.0, 1.0])
    got = [p["cation_moles"] for p in soluble_fraction(m, ELEMENTS)["phases"]]
    assert got == sorted(got, reverse=True)


def test_elements_outside_the_candidate_are_ignored():
    """A hull can return a phase carrying an element the candidate does not contain;
    it must not enter the denominator."""
    m = FakeMulti([entry({"Fe": 1.0}, "Solid"), entry({"Cu": 5.0}, "Ion")], [1.0, 1.0])
    assert soluble_fraction(m, ELEMENTS)["soluble_cation_fraction"] == pytest.approx(0.0)


@pytest.mark.skipif(not os.path.exists(CACHE), reason="needs the R2 MP cache")
def test_reproduces_docs31_single_element_assignments():
    """The quaternary hull must agree with docs/31 s4's per-element table at
    pH 14 / 1.53 V vs RHE: Fe -> Fe2O3(s), Co -> CoOOH(s), Mn -> MnO4-, Ni -> soluble.

    This is the check that the multi-element machinery reproduces the single-element
    result the campaign already published, rather than quietly disagreeing with it.
    """
    pytest.importorskip("pymatgen")
    from dft.pourbaix_multi import assess_composition

    cache = json.load(open(CACHE))
    rec = assess_composition(cache, ["Fe", "Ni", "Co", "Mn"], [0.32, 0.17, 0.34, 0.17])
    op = next(r for r in rec["points"] if r["pH"] == 14.0 and r["V_RHE"] == 1.53)
    phase_of = {}
    for p in op["phases"]:
        for el in ("Fe", "Ni", "Co", "Mn"):
            if p["formula"].startswith(el):
                phase_of[el] = p["phase"]
    assert phase_of.get("Fe") == "solid"
    assert phase_of.get("Co") == "solid"
    assert phase_of.get("Mn") == "ion"
    assert phase_of.get("Ni") == "ion"
