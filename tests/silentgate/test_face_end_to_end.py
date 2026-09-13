"""End-to-end proof that the A9.2 status face scores the registered gates right.

These drive the face with a test double
(fixtures/fake_census.py) that emits canned JSON. That is enough to answer the
two questions that actually matter about a gate:

  1. CAN it go green?  A gate that can never pass is as broken as one that always
     does, and "it is red because the core is missing" would hide a bug that keeps
     it red forever. `test_the_face_goes_green_...` is the proof it can.
  2. Does it go red for each registered failure, one at a time? One test per
     registered threshold, each failing exactly the gate it should and leaving
     the others alone.

The double parses nothing -- it looks paths up in .github/ci/populations.txt and
emits the scenario's answer. See its docstring.

AUTHORSHIP: written by AI as "tests and fixtures" under the A9.1 :1840 permitted
list.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

from conftest import CI, HERE, ROOT, run_py

FAKE = os.path.join(HERE, "fixtures", "fake_census.py")


def _invocation(tmp_path):
    """A filled-in invocation config pointing at the test double."""
    # Build an isolated config: the production invocation now drives the real core.
    cmd = '"%s" "%s" --paths-from {paths_file}' % (
        sys.executable.replace("\\", "/"), FAKE.replace("\\", "/"))
    keys = (
        "runs_array", "path", "n_symops", "nosym_in_deck",
        "locked_two_witness", "locked_force_only", "locked_axes",
        "n_adsorbate", "unidentified", "n_if_pos_excluded", "header_form",
    )
    text = "[cli]\ncensus_cmd = '%s'\n\n[schema]\n" % cmd
    text += "\n".join('%s = "/%s"' % (key, "runs" if key == "runs_array" else key)
                      for key in keys) + "\n"
    dst = tmp_path / "invocation.toml"
    dst.write_text(text, encoding="utf-8")
    return str(dst)


def _green_oc20(tmp_path):
    p = tmp_path / "oc20.json"
    p.write_text(json.dumps({
        "status": "MEASURED", "detail": "test double",
        "n_relaxations": 500, "n_locked": 0, "locked_rate_percent": 0.0, "green": True,
    }), encoding="utf-8")
    return str(p)


def _passing_log(tmp_path):
    p = tmp_path / "ai-use-log.md"
    p.write_text(
        "# AI-use log\n"
        "- `.github/workflows/s1-controls.yml` -- the CI workflow\n"
        "- `tests/silentgate/` -- tests and fixtures\n"
        "- `pyproject.toml` -- metadata, version, entry-point\n",
        encoding="utf-8")
    dj = tmp_path / "disjoint.json"
    proc = run_py("check_disjoint.py", "--log", str(p), "--json", str(dj))
    assert proc.returncode == 0, proc.stdout
    return str(dj)


def _run_face(tmp_path, scenario, **kw):
    out = tmp_path / "face.json"
    proc = run_py(
        "run_controls.py",
        "--invocation", kw.get("invocation") or _invocation(tmp_path),
        "--disjoint-json", kw.get("disjoint") or _passing_log(tmp_path),
        "--oc20-json", kw.get("oc20") or _green_oc20(tmp_path),
        "--out-json", str(out),
        env={"FAKE_SCENARIO": scenario},
    )
    face = json.loads(out.read_text(encoding="utf-8"))
    return proc, face, {g["key"]: g for g in face["gates"]}


def test_the_face_goes_green_when_every_gate_is_satisfied(tmp_path):
    """A complete core plus passing doubles proves the face is passable."""
    proc, face, g = _run_face(tmp_path, "all_pass")
    assert all(gate["verdict"] is True for gate in g.values()), proc.stdout
    assert g["positive_9_9"]["detail"] == "two-witness 9/9, force-only 9/9"
    assert g["negative_qe_0_11"]["detail"].startswith("force-only LOCKED 0/11")
    assert g["partition_20_20"]["detail"].startswith("20/20 partition")
    assert g["tag_agreement_20_20"]["detail"].startswith("20/20 agree")
    assert g["two_witness_n_n"]["detail"] == "96/96 agree"
    assert g["negative_oc20"]["verdict"] is True
    assert face["green"] is True and proc.returncode == 0


@pytest.mark.parametrize("create_directory", [False, True], ids=["absent", "empty"])
def test_an_absent_or_empty_package_is_not_a_core(tmp_path, monkeypatch, create_directory):
    """Exercise missing-core states in a temporary root, never mutate the real core."""
    import importlib.util
    import json

    spec = importlib.util.spec_from_file_location("isolated_control_face", os.path.join(CI, "run_controls.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = tmp_path / "repo"
    root.mkdir()
    if create_directory:
        (root / "silentgate").mkdir()
    monkeypatch.setattr(module, "ROOT", str(root))
    monkeypatch.setattr(sys, "argv", [
        "run_controls.py", "--invocation", _invocation(tmp_path),
        "--disjoint-json", _passing_log(tmp_path),
        "--oc20-json", _green_oc20(tmp_path),
        "--out-json", str(tmp_path / "isolated-face.json"),
    ])
    # The double has its own repository location; cwd does not supply its corpus.
    monkeypatch.setenv("FAKE_SCENARIO", "all_pass")
    assert module.main() != 0
    face = json.loads((tmp_path / "isolated-face.json").read_text(encoding="utf-8"))
    gate = next(g for g in face["gates"] if g["key"] == "core_present")
    assert gate["verdict"] is False
    assert face["green"] is False
    for name in ("readers", "census.py", "classify.py", "direction.py", "cli.py"):
        assert "silentgate/" + name in gate["detail"]


def test_a_null_verdict_is_not_measured_never_zero_of_eleven(tmp_path):
    """The fail-open this hardening exists for.

    A census that answers `null` everywhere would, under a naive `is True` count,
    report "force-only LOCKED 0/11" and pass the QE negative control on no
    evidence at all.
    """
    proc, face, g = _run_face(tmp_path, "null_verdicts")
    assert face["green"] is False
    assert g["negative_qe_0_11"]["status"] == "NOT MEASURED"
    assert g["negative_qe_0_11"]["verdict"] is not True
    assert "null" in g["negative_qe_0_11"]["detail"]
    assert g["positive_9_9"]["status"] == "NOT MEASURED"


def test_one_locked_run_fails_the_qe_negative_control(tmp_path):
    """0 of the 11, force-only (docs/43:1858). One is a failure, not a caveat."""
    proc, face, g = _run_face(tmp_path, "one_locked_in_eleven")
    assert face["green"] is False
    assert g["negative_qe_0_11"]["status"] == "MEASURED"
    assert g["negative_qe_0_11"]["verdict"] is False
    assert "1/11" in g["negative_qe_0_11"]["detail"]


def test_a_misplaced_deck_fails_the_partition(tmp_path):
    """The 20-for-20 partition by the deck's nosym line (docs/43:1864)."""
    proc, face, g = _run_face(tmp_path, "partition_broken")
    assert face["green"] is False
    assert g["partition_20_20"]["verdict"] is False
    assert "19/20" in g["partition_20_20"]["detail"]


def test_a_tag_disagreement_is_printed_and_fails(tmp_path):
    """:1834 -- "must reproduce the tag counts 20/20 ... printed by CI"."""
    proc, face, g = _run_face(tmp_path, "tag_mismatch")
    assert face["green"] is False
    assert g["tag_agreement_20_20"]["verdict"] is False
    assert "19/20" in g["tag_agreement_20_20"]["detail"]


def test_a_two_witness_disagreement_fails_the_n_n_gate(tmp_path):
    """:1864 -- agreement on EVERY classifiable adsorbate row, n/n printed."""
    proc, face, g = _run_face(tmp_path, "disagreement")
    assert face["green"] is False
    assert g["two_witness_n_n"]["verdict"] is False
    assert g["two_witness_n_n"]["detail"] == "95/96 agree"


def test_an_empty_census_is_not_measured(tmp_path):
    """A census that returns nothing must not read as "nothing was locked"."""
    proc, face, g = _run_face(tmp_path, "empty")
    assert face["green"] is False
    for key in ("positive_9_9", "negative_qe_0_11", "partition_20_20",
                "tag_agreement_20_20", "two_witness_n_n"):
        assert g[key]["status"] == "NOT MEASURED", key
        assert g[key]["verdict"] is not True, key


def test_a_missing_ai_use_log_keeps_the_face_red_even_when_controls_pass(tmp_path):
    """The disjointness assertion is a gate row, not a footnote (:1840)."""
    dj = tmp_path / "disjoint.json"
    proc = run_py("check_disjoint.py", "--log", str(tmp_path / "nope.md"), "--json", str(dj))
    assert proc.returncode != 0
    proc, face, g = _run_face(tmp_path, "all_pass", disjoint=str(dj))
    assert face["green"] is False
    assert g["disjointness"]["verdict"] is False
    assert g["positive_9_9"]["verdict"] is True, "the controls themselves still passed"


def test_a_missing_oc20_verdict_keeps_the_face_red_when_all_else_passes(tmp_path):
    """"a commit on which the OC20 job did not execute is not green" (:1868)."""
    proc, face, g = _run_face(tmp_path, "all_pass", oc20=str(tmp_path / "absent.json"))
    assert face["green"] is False
    assert g["negative_oc20"]["status"] == "NOT MEASURED"
    assert g["positive_9_9"]["verdict"] is True


def test_a_nonzero_oc20_rate_fails_the_face(tmp_path):
    """"exactly 0.00 % of the 500" (:1856). 0.2 % is a failure, not a caveat."""
    oc = tmp_path / "oc20.json"
    oc.write_text(json.dumps({
        "status": "MEASURED", "detail": "one locked",
        "n_relaxations": 500, "n_locked": 1, "locked_rate_percent": 0.2, "green": False,
    }), encoding="utf-8")
    proc, face, g = _run_face(tmp_path, "all_pass", oc20=str(oc))
    assert face["green"] is False
    assert g["negative_oc20"]["status"] == "MEASURED"
    assert g["negative_oc20"]["verdict"] is False
