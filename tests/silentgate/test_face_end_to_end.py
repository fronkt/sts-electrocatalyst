"""End-to-end proof that the A9.2 status face scores the registered gates right.

The core does not exist yet, so these drive the face with a test double
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
import shutil
import sys

import pytest

from conftest import CI, HERE, ROOT, run_py

FAKE = os.path.join(HERE, "fixtures", "fake_census.py")


def _invocation(tmp_path):
    """A filled-in invocation config pointing at the test double."""
    src = os.path.join(CI, "silentgate-invocation.toml")
    with open(src, "r", encoding="utf-8") as fh:
        text = fh.read()
    # Forward slashes and explicit quotes: shlex.split (POSIX mode, which is what
    # run_controls.py uses) eats backslashes, and Windows paths are full of them.
    # A TOML literal string ('...') keeps the embedded double quotes intact.
    cmd = '"%s" "%s" --paths-from {paths_file}' % (
        sys.executable.replace("\\", "/"), FAKE.replace("\\", "/"))
    # Fail loudly rather than silently inheriting the entrant's real command:
    # once he fills silentgate-invocation.toml this replace stops matching, and a
    # quiet miss would have these tests driving his actual core instead of the
    # double. Then they would be testing the core, which is not their job.
    assert 'census_cmd = ""' in text, (
        "silentgate-invocation.toml no longer has a blank census_cmd -- update "
        "this helper to build its own config from scratch rather than patching "
        "the real one, or these tests will silently run the entrant's core"
    )
    text = text.replace('census_cmd = ""', "census_cmd = '%s'" % cmd)
    unmapped = 0
    for key, ptr in (
        ("runs_array", "/runs"), ("path", "/path"), ("n_symops", "/n_symops"),
        ("nosym_in_deck", "/nosym_in_deck"),
        ("locked_two_witness", "/locked_two_witness"),
        ("locked_force_only", "/locked_force_only"),
        ("locked_axes", "/locked_axes"), ("n_adsorbate", "/n_adsorbate"),
        ("unidentified", "/unidentified"),
        ("n_if_pos_excluded", "/n_if_pos_excluded"),
        ("header_form", "/header_form"),
    ):
        if '%s = ""' % key not in text:
            unmapped += 1
            continue
        text = text.replace('%s = ""' % key, '%s = "%s"' % (key, ptr), 1)
    assert unmapped == 0, (
        "%d [schema] keys were already filled in the real invocation file; this "
        "helper must build its own config instead of patching it" % unmapped
    )
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


def test_every_gate_but_the_missing_core_can_be_satisfied(tmp_path):
    """The proof that this gate is passable at all.

    A gate that can never go green is as broken as one that always does, and
    "it is red because the core is missing" would hide a bug that keeps it red
    forever. So: drive every control to its registered passing value and check
    that the ONLY row still red is `core_present` -- which no test double can or
    should satisfy, because satisfying it would mean writing files under
    silentgate/, and that is the one thing AI may not do (docs/43:1840).
    """
    proc, face, g = _run_face(tmp_path, "all_pass")
    blocked = [k for k, gate in g.items() if gate["verdict"] is not True]
    assert blocked == ["core_present"], (
        "expected the absent core to be the only blocker; also red: %r\n%s"
        % ([k for k in blocked if k != "core_present"], proc.stdout)
    )
    assert g["positive_9_9"]["detail"] == "two-witness 9/9, force-only 9/9"
    assert g["negative_qe_0_11"]["detail"].startswith("force-only LOCKED 0/11")
    assert g["partition_20_20"]["detail"].startswith("20/20 partition")
    assert g["tag_agreement_20_20"]["detail"].startswith("20/20 agree")
    assert g["two_witness_n_n"]["detail"] == "96/96 agree"
    assert g["negative_oc20"]["verdict"] is True
    assert face["green"] is False and proc.returncode != 0


def test_an_empty_package_directory_is_not_a_core(tmp_path):
    """`core_present` names the five module paths, not just the directory.

    An empty silentgate/ would otherwise read PRESENT, and the face would then
    claim an instrument that does not exist. The directory is created empty and
    removed here; no file is ever written under it.
    """
    d = os.path.join(ROOT, "silentgate")
    if os.path.exists(d):
        pytest.skip("silentgate/ already exists; the entrant has started the core")
    os.mkdir(d)
    try:
        proc, face, g = _run_face(tmp_path, "all_pass")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    assert g["core_present"]["verdict"] is False
    for name in ("readers", "census.py", "classify.py", "direction.py", "cli.py"):
        assert "silentgate/" + name in g["core_present"]["detail"]


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
