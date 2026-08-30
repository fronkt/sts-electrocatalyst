"""probe_decks must parse the gate-(h) AFM sublattice decks.

docs/51:25 recorded, as the reason nothing could be launched for the S0 gate-(h)
family, that "`probe_decks.py` cannot parse the Ru1/Ru2 species". The cause was
`_ELEMENT_RE = ^[A-Z][a-z]?$` applied to ATOMIC_POSITIONS lines: the registered AFM
idiom (docs/43:1391) splits the metal into two species LABELS `Ru1`/`Ru2` with
identical mass and pseudo and opposite starting_magnetization, and neither label is
an element symbol. Every position line was skipped and the deck parsed to ZERO atoms
-- silently, with no exception and no warning, which is the failure mode this test
exists to make loud.

These four decks are the banked gate-(h) SCFs (commit 946c3aa, 4/4 ADOPT_AFM), so the
test runs against real registered artifacts rather than a fixture.
"""
import os
import re

import pytest

from dft.probe_decks import parse_input_deck

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AFM_DIR = os.path.join(HERE, "runs", "s0", "h_afm_anchor")

# (deck, declared nat, declared ntyp, species labels in ATOMIC_SPECIES order)
DECKS = [
    ("ref__2x1v__afm.in", 36, 3, ["Ru1", "Ru2", "O"]),
    ("s0_O__2x1v_off__afm.in", 37, 3, ["Ru1", "Ru2", "O"]),
    ("s0_OH__2x1v_off__afm.in", 38, 4, ["H", "Ru1", "Ru2", "O"]),
    ("s0_OOH__2x1v_off__afm.in", 39, 4, ["H", "Ru1", "Ru2", "O"]),
]

pytestmark = pytest.mark.skipif(
    not os.path.isdir(AFM_DIR), reason="gate-(h) AFM decks not present"
)


@pytest.mark.parametrize("deck,nat,ntyp,labels", DECKS)
def test_afm_deck_parses_every_atom(deck, nat, ntyp, labels):
    path = os.path.join(AFM_DIR, deck)
    parsed = parse_input_deck(path)

    # The regression itself: zero atoms was the old behaviour.
    assert len(parsed["positions"]) > 0, f"{deck} parsed to zero atoms"
    assert len(parsed["positions"]) == nat, (
        f"{deck}: parsed {len(parsed['positions'])} atoms, deck declares nat = {nat}"
    )
    assert len(parsed["flags"]) == nat

    # nat and ntyp are cross-checked against the deck's own &SYSTEM namelist rather
    # than against this table alone, so an edited deck cannot pass on stale constants.
    txt = open(path).read()
    assert int(re.search(r"^\s*nat\s*=\s*(\d+)", txt, re.M).group(1)) == nat
    assert int(re.search(r"^\s*ntyp\s*=\s*(\d+)", txt, re.M).group(1)) == ntyp

    assert [s[0] for s in parsed["species"]] == labels
    # Every position label must be one the deck declares -- the property the old
    # regex could not express.
    assert {p[0] for p in parsed["positions"]} <= set(labels)


@pytest.mark.parametrize("deck,nat,ntyp,labels", DECKS)
def test_afm_sublattices_are_antiparallel_and_on_the_metal(deck, nat, ntyp, labels):
    """The two Ru labels carry opposite seeds; H and O are explicitly zero.

    This is the gate-(h) recipe's defining property, and it is index-sensitive: the
    metal sits at species index 1/2 on the ntyp = 3 decks but 2/3 on the ntyp = 4
    decks, because H sorts first. A per-deck constant would seed H or O -- the same
    state-dependent-index trap build_a0spin.py assertion A1 exists to catch.
    """
    parsed = parse_input_deck(os.path.join(AFM_DIR, deck))
    idx = {label: i + 1 for i, (label, _m, _p) in enumerate(parsed["species"])}
    mags = parsed["mags"]

    assert mags[idx["Ru1"]] == pytest.approx(0.5)
    assert mags[idx["Ru2"]] == pytest.approx(-0.5)
    assert mags[idx["Ru1"]] == pytest.approx(-mags[idx["Ru2"]])
    for label in labels:
        if label not in ("Ru1", "Ru2"):
            assert mags[idx[label]] == pytest.approx(0.0), (
                f"{deck}: non-metal species {label} carries a nonzero seed"
            )

    # Identical pseudo and identical mass -- the two labels are one element.
    by_label = {s[0]: s for s in parsed["species"]}
    assert by_label["Ru1"][1] == by_label["Ru2"][1]
    assert by_label["Ru1"][2] == by_label["Ru2"][2]

    # Ru carries no U anywhere in this family (protocol.md section 2).
    assert parsed["hubbard"] == []
    assert parsed["nspin"] == 2
