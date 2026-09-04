"""Tests for src/lit/verify_dois.py — the F8 bibliography check.

F8 (`docs/43:1945`) requires the bibliography regenerated from Crossref, and the
published number-one reason projects failed to qualify in 2026 is "Fake
references and/or citations in Research Report". A tool that hunts fabricated
citations has one failure mode worse than missing a bad DOI: reporting a GOOD one
as NOT_FOUND. That reads as a fabricated reference in an audit and is exactly the
error the 2026-08-15 sweep's own critic caught it making, where a permissive
character class swallowed sentence punctuation and manufactured "malformed DOIs".

These tests pin extraction only. Nothing here touches the network: resolution is
covered by the committed report artifact, and a unit test that depends on a
registrar being up is a test that fails for reasons unrelated to this repository.

  E1  parenthesised Elsevier DOIs survive intact (the pre-2000 form)
  E2  prose punctuation and markdown emphasis are stripped
  E3  balanced vs unbalanced parentheses are distinguished
  E4  a DOI is found regardless of surrounding markup
  E5  scanning is idempotent under normalisation
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "lit"))

import verify_dois as vd  # noqa: E402


def _extract(text):
    return [vd.normalise(m.group(1)) for m in vd.DOI_RE.finditer(text)]


# E1 + E3 — the regression that motivated this file.
@pytest.mark.parametrize("text,want", [
    # Pre-2000 Elsevier DOIs contain parentheses. Truncating at "(" reports a
    # whole generation of real citations as fabricated.
    ("Surface Science 10.1016/0039-6028(95)00816-0 reports",
     "10.1016/0039-6028(95)00816-0"),
    ("10.1016/0254-0584(86)90045-6.", "10.1016/0254-0584(86)90045-6"),
    # ...while an unbalanced closer is prose and must go.
    ("see (10.1021/jp047349j)", "10.1021/jp047349j"),
    ("OC20 (10.1021/acscatal.0c04525): slab relaxations",
     "10.1021/acscatal.0c04525"),
])
def test_parentheses_are_kept_when_balanced_and_dropped_when_not(text, want):
    assert want in _extract(text)


# E2 — markdown emphasis around a DOI is markup, not identifier.
@pytest.mark.parametrize("text,want", [
    ("**10.1002/anie.202521856**", "10.1002/anie.202521856"),
    ("`10.1039/d2cp04814k`", "10.1039/d2cp04814k"),
    ("__10.1021/acscatal.6b01907__", "10.1021/acscatal.6b01907"),
    ("~~10.1038/s41524-023-00973-1~~", "10.1038/s41524-023-00973-1"),
    ("10.1103/PhysRevB.65.035406,", "10.1103/physrevb.65.035406"),
    ("cited as 10.5281/zenodo.22304889;", "10.5281/zenodo.22304889"),
])
def test_markup_and_punctuation_are_stripped(text, want):
    assert want in _extract(text)


# Underscore and tilde are LEGAL DOI characters. Only the doubled markdown forms
# are removed, so a single trailing one must survive.
@pytest.mark.parametrize("doi", [
    "10.1234/abc_def",
    "10.1234/abc~def",
])
def test_single_underscore_and_tilde_are_not_stripped(doi):
    assert vd.normalise(doi) == doi


# E4 — the same identifier reaches the same normal form from any surrounding.
def test_normalisation_is_idempotent_and_surrounding_independent():
    forms = ["10.1002/cctc.201000397",
             "**10.1002/cctc.201000397**",
             "(10.1002/cctc.201000397)",
             "10.1002/cctc.201000397.",
             "`10.1002/cctc.201000397`,"]
    # The real pipeline is regex-then-normalise: the regex decides where the DOI
    # STARTS (dropping leading markup) and normalise trims the tail. Calling
    # normalise alone would leave leading characters, which is its contract.
    normal = set()
    for f in forms:
        normal.update(_extract(f))
    assert normal == {"10.1002/cctc.201000397"}
    once = vd.normalise("10.1002/cctc.201000397")
    assert vd.normalise(once) == once


# E5 — a state must never be silently upgraded. An unreachable registrar is
# ERROR, never NOT_FOUND: the difference is "we could not check" versus "this
# citation does not exist", and only one of those belongs in an audit.
def test_error_and_not_found_are_distinct_states():
    src = open(os.path.join(ROOT, "src", "lit", "verify_dois.py"),
               encoding="utf-8").read()
    assert 'state = "NOT_FOUND" if "404" in last_err else "ERROR"' in src, (
        "resolve() must distinguish a 404 from a transport failure; collapsing "
        "them makes an outage look like a fabricated citation"
    )


def test_title_agreement_is_none_without_context():
    """No citing line means the check is inapplicable, not failed."""
    assert vd.title_agreement({"title": "Some Paper Title"}, []) is None
    assert vd.title_agreement({"title": ""}, [("f", 1, "text")]) is None


def test_a_prose_template_is_not_read_as_a_citation(tmp_path):
    """`10.1103/PhysRevB.<vol>.<article>` describes a pattern, not a work.

    The regex stops at the "<", leaving a bare "10.1103/physrevb" that resolves
    nowhere. Reported as NOT_FOUND it reads like a fabricated DOI in an audit,
    which is the one error this tool must not make.
    """
    d = tmp_path / "digest.md"
    d.write_text(
        "APS DOIs quoted as 10.1103/PhysRevB.<vol>.<article> follow a pattern.\n"
        "A real one is 10.1103/PhysRevB.65.035406 here.\n",
        encoding="utf-8")
    found = vd.scan([str(tmp_path)])
    assert "10.1103/physrevb" not in found, "prose template was read as a citation"
    assert "10.1103/physrevb.65.035406" in found, "the real DOI beside it was lost"


def test_the_tools_own_outputs_are_not_rescanned(tmp_path):
    """The report quotes every DOI in the tree; scanning it doubles the census."""
    (tmp_path / "real.md").write_text("cite 10.1021/jp047349j\n", encoding="utf-8")
    (tmp_path / "f8_doi_resolution.json").write_text(
        '{"x": "10.9999/should-not-be-seen"}\n', encoding="utf-8")
    (tmp_path / "2026-09-04-f8-doi-resolution.md").write_text(
        "- `10.8888/also-not-seen`\n", encoding="utf-8")
    (tmp_path / "references.bib").write_text(
        "@article{x, doi = {10.7777/nor-this}}\n", encoding="utf-8")
    found = vd.scan([str(tmp_path)])
    assert "10.1021/jp047349j" in found
    for leaked in ("10.9999/should-not-be-seen", "10.8888/also-not-seen",
                   "10.7777/nor-this"):
        assert leaked not in found, "%s came from this tool's own output" % leaked
