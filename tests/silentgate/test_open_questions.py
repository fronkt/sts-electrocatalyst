"""The open registered decisions, mechanised as a checklist.

Seven questions in spec_rulings.toml are left open by the registered text. Each is
the entrant's to answer, by a dated line in docs/43. None can be answered here,
and this suite does not answer them -- it refuses to let them be forgotten.

Sequencing: while `silentgate/` does not exist these SKIP, because a question
about how to score the core cannot bind before the core is written. The moment
the core is committed they become failures until each ruling is recorded. Two of
them (the OC20 transport and the AI-use log path) additionally block the control
face today, and the face is where that red is carried.

AUTHORSHIP: written by AI as "tests and fixtures" under the A9.1 :1840 permitted
list. Every question is transcribed from the registered text; every answer is
blank on purpose.
"""
from __future__ import annotations

import os

import pytest

from conftest import HERE, ROOT, _load_toml

RULINGS = os.path.join(HERE, "spec_rulings.toml")
_DOC = _load_toml(RULINGS)
QUESTIONS = _DOC["question"]
IDS = [q["id"] for q in QUESTIONS]


def test_the_register_is_complete():
    """Every question carries its citation, its stake and its options."""
    assert len(QUESTIONS) == 7
    for q in QUESTIONS:
        assert q["registered_at"], q["id"]
        assert q["why"].strip(), q["id"]
        assert q["decides"].strip(), q["id"]
        assert "ruling" in q and "dated_line" in q, q["id"]


def test_no_question_was_answered_by_an_assistant():
    """A ruling without a dated line is not a ruling.

    A registered parameter is elected by the entrant in docs/43. If `ruling` is
    filled but `dated_line` is empty, something wrote an answer here that has no
    authority behind it -- which is exactly the failure this register exists to
    prevent.
    """
    orphans = [q["id"] for q in QUESTIONS if q["ruling"].strip() and not q["dated_line"].strip()]
    assert not orphans, (
        "ruling recorded with no dated line for: %s -- a registered parameter is "
        "elected by a dated line in docs/43, not by editing this file" % ", ".join(orphans)
    )


def test_a_recorded_ruling_is_one_of_the_registered_options():
    bad = []
    for q in QUESTIONS:
        r = q["ruling"].strip()
        if r and q["options"] and r not in q["options"]:
            bad.append("%s: %r not in %r" % (q["id"], r, q["options"]))
    assert not bad, "\n".join(bad)


def test_a_recorded_dated_line_points_at_real_text():
    """`dated_line` must cite a file that exists, so the ruling is findable."""
    bad = []
    for q in QUESTIONS:
        cite = q["dated_line"].strip()
        if not cite:
            continue
        path = cite.split(":")[0].strip()
        if not os.path.exists(os.path.join(ROOT, path)):
            bad.append("%s cites %r, which does not exist" % (q["id"], path))
    assert not bad, "\n".join(bad)


def test_every_named_fixture_exists():
    missing = [
        "%s -> %s" % (q["id"], q["fixture"])
        for q in QUESTIONS
        if q["fixture"] and not os.path.exists(os.path.join(ROOT, q["fixture"]))
    ]
    assert not missing, "\n".join(missing)


@pytest.mark.parametrize("q", QUESTIONS, ids=IDS)
def test_question_is_answered_before_the_core_is_scored(q, requires_core):
    """Once `silentgate/` exists, every open question must carry a ruling."""
    assert q["ruling"].strip(), (
        "OPEN REGISTERED DECISION, unanswered: %s\n\n"
        "  %s\n\n"
        "  registered at: %s\n"
        "  options:       %s\n"
        "  fixture:       %s\n"
        "%s\n"
        "  Answer it with a dated line in docs/43, then record the ruling and the\n"
        "  citation in tests/silentgate/spec_rulings.toml. This test is a reminder,\n"
        "  not an authority: it cannot and must not choose for you."
        % (q["id"], q["question"], q["registered_at"],
           ", ".join(q["options"]) or "(free text)", q["fixture"] or "(none)",
           q["decides"].rstrip())
    )
    assert q["dated_line"].strip(), (
        "%s has a ruling but no dated line to cite" % q["id"]
    )


def test_the_fixtures_own_citation_example_is_valid():
    """The header tells the entrant how to write `dated_line`. Check its example.

    Regression, 2026-09-04. The example read `docs/43:1975` -- and
    test_a_recorded_dated_line_points_at_real_text does cite.split(":")[0] then
    os.path.exists, so the abbreviation "docs/43" resolves to a path that is not
    on disk. Following the file's own instruction broke the suite. Nothing may
    document a citation form that the citation test rejects.
    """
    import re

    with open(RULINGS, encoding="utf-8") as fh:
        header = fh.read().split("[[question]]")[0]
    examples = re.findall(r'"([^"]*:[0-9]+[^"]*)"', header)
    assert examples, "the header no longer shows a dated_line example to check"
    bad = []
    for ex in examples:
        path = ex.split(":")[0].strip()
        if not os.path.exists(os.path.join(ROOT, path)):
            bad.append("%r -> path %r does not exist" % (ex, path))
    assert not bad, (
        "the fixture header documents a citation form its own test rejects:\n  "
        + "\n  ".join(bad)
        + "\n\nUse the full filename, e.g. docs/43-prereg-week1-factorial.md:4106"
    )


def test_every_registered_option_is_lowercase_hyphenated():
    """The `ruling` field is matched VERBATIM against these strings.

    docs/82 drafts each signature in prose caps ("ALL", "CORRECTION FILED").
    That prose belongs in the docs/43 dated line; this field takes the option
    token. Pinning the option vocabulary makes a pasted signature fail loudly
    rather than cryptically.
    """
    bad = []
    for q in QUESTIONS:
        for opt in q["options"]:
            if opt != opt.lower() or " " in opt:
                bad.append("%s: %r" % (q["id"], opt))
    assert not bad, "options must be lowercase and hyphenated: %s" % ", ".join(bad)


@pytest.mark.parametrize("q", QUESTIONS, ids=IDS)
def test_a_case_variant_ruling_is_named_as_such(q):
    """Diagnose the paste-from-docs/82 failure instead of merely rejecting it.

    docs/82 row 5 is the worst case: it signs "CORRECTION FILED", which is not in
    that question's options at all, while the option is "file-the-correction".
    """
    r = q["ruling"].strip()
    if not r or not q["options"] or r in q["options"]:
        return
    near = [o for o in q["options"] if o.lower() == r.lower().replace(" ", "-")]
    assert not near, (
        "%s: ruling %r is the right decision in the wrong form -- write %r.\n"
        "The prose signature belongs in the docs/43 dated line, not in this field."
        % (q["id"], r, near[0])
    )
