"""The tripwire on the tripwire: prove the S1 gate cannot pass by accident.

A9.2 is registered as a GATE, not a caveat (docs/43:1848): "P-CTRL therefore
voids rather than caveats. Any drift voids the corresponding numbers rather than
caveating them." A gate that can go green while its instrument does not exist,
or while nobody is keeping the AI-use log, is worse than no gate: it converts an
unchecked claim into a checked-looking one.

So these tests do not check that the controls PASS -- they cannot, the core is
not written. They check that the machinery FAILS CLOSED in every state where a
number would otherwise be produced without evidence behind it.

They must keep passing after the core is written. If one of them starts failing
because the gate started tolerating a missing input, that is the regression.
"""
from __future__ import annotations

import json
import os

import pytest

from conftest import CI, REGISTERED_CORE_PATHS, ROOT, run_py


def test_core_path_list_matches_the_registered_text():
    """.github/ci/core_paths.txt is the machine-readable form of docs/43:1840.

    Registered, verbatim: "the core is the named module set silentgate/readers/*
    (pw.x force/header/energy/deck readers, the OC20 trajectory reader),
    silentgate/census.py, silentgate/classify.py, silentgate/direction.py and
    silentgate/cli.py -- written and committed only by the entrant."
    """
    path = os.path.join(CI, "core_paths.txt")
    with open(path, "r", encoding="utf-8") as fh:
        pats = [l.strip() for l in fh if l.strip() and not l.strip().startswith("#")]
    assert tuple(pats) == REGISTERED_CORE_PATHS, (
        "core_paths.txt has drifted from the registered five-entry module set"
    )


def test_core_path_list_is_not_a_whole_package_glob():
    """It must NOT be silentgate/** -- that would self-fail on a permitted act.

    A9.1 :1828 requires any legacy detector the entrant lifts to go into
    `silentgate/legacy/` "lifted as-is with its existing authorship recorded in
    the AI-use log". A legally-lifted legacy file therefore appears in the log by
    design. Globbing the whole package here would make the disjointness
    assertion fail on that permitted act, and the registered phrase is "named
    module set", not "the package".
    """
    path = os.path.join(CI, "core_paths.txt")
    with open(path, "r", encoding="utf-8") as fh:
        pats = [l.strip() for l in fh if l.strip() and not l.strip().startswith("#")]
    for bad in ("silentgate/**", "silentgate/*", "silentgate"):
        assert bad not in pats
    assert not any(p.startswith("silentgate/legacy") for p in pats)


def test_disjointness_fails_when_the_log_is_missing(tmp_path):
    """An absent AI-use log leaves the log's file list UNDEFINED, not empty."""
    proc = run_py(
        "check_disjoint.py",
        "--log", str(tmp_path / "there-is-no-such-log.md"),
        "--json", str(tmp_path / "out.json"),
    )
    assert proc.returncode != 0, "a missing AI-use log must fail, never pass vacuously"
    assert "FAIL" in proc.stdout
    result = json.loads((tmp_path / "out.json").read_text(encoding="utf-8"))
    assert result["status"] == "FAIL"


def test_disjointness_catches_a_core_path_in_the_log(tmp_path):
    log = tmp_path / "ai-use-log.md"
    log.write_text(
        "# AI-use log\n"
        "\n"
        "| file | what AI produced |\n"
        "|---|---|\n"
        "| `.github/workflows/s1-controls.yml` | the CI workflow |\n"
        "| `silentgate/census.py` | ...this must trip the assertion |\n",
        encoding="utf-8",
    )
    proc = run_py("check_disjoint.py", "--log", str(log), "--json", str(tmp_path / "o.json"))
    assert proc.returncode != 0
    result = json.loads((tmp_path / "o.json").read_text(encoding="utf-8"))
    assert result["status"] == "FAIL"
    hits = {v["path"] for v in result["violations"]}
    assert "silentgate/census.py" in hits


def test_disjointness_catches_a_reader_under_the_glob(tmp_path):
    """silentgate/readers/* must match at any depth, and the bare directory too."""
    log = tmp_path / "ai_use.md"
    log.write_text(
        "- silentgate/readers/pwx_forces.py -- drafted\n"
        "- silentgate/readers/oc20/traj.py -- drafted\n"
        "- silentgate/readers -- the package directory\n",
        encoding="utf-8",
    )
    proc = run_py("check_disjoint.py", "--log", str(log), "--json", str(tmp_path / "o.json"))
    assert proc.returncode != 0
    result = json.loads((tmp_path / "o.json").read_text(encoding="utf-8"))
    hits = {v["path"] for v in result["violations"]}
    assert "silentgate/readers/pwx_forces.py" in hits
    assert "silentgate/readers/oc20/traj.py" in hits, "the glob must match at any depth"
    assert "silentgate/readers" in hits, "logging the bare directory must trip it too"


def test_disjointness_passes_on_a_clean_log(tmp_path):
    """The permitted list, logged. Tests, fixtures, the workflow, pyproject."""
    log = tmp_path / "ai-use-log.md"
    log.write_text(
        "# AI-use log\n"
        "- `.github/workflows/s1-controls.yml` -- the CI workflow\n"
        "- `.github/ci/check_disjoint.py` -- CI helper\n"
        "- `tests/silentgate/test_gate_fails_closed.py` -- tests\n"
        "- `tests/silentgate/fixtures/manifest.toml` -- fixtures\n"
        "- `pyproject.toml` -- metadata, version, entry-point only\n"
        "- `silentgate_notes.md` -- a filename that merely starts with the word\n",
        encoding="utf-8",
    )
    proc = run_py("check_disjoint.py", "--log", str(log), "--json", str(tmp_path / "o.json"))
    assert proc.returncode == 0, proc.stdout
    result = json.loads((tmp_path / "o.json").read_text(encoding="utf-8"))
    assert result["status"] == "PASS"
    assert result["violations"] == []


def test_disjointness_is_not_fooled_by_prose_around_the_path(tmp_path):
    """The log's format is unregistered, so extraction must be format-agnostic."""
    log = tmp_path / "ai-use-log.md"
    log.write_text(
        "On 2026-08-27 an assistant drafted (silentgate/direction.py), which it\n"
        "should not have done.\n",
        encoding="utf-8",
    )
    proc = run_py("check_disjoint.py", "--log", str(log), "--json", str(tmp_path / "o.json"))
    assert proc.returncode != 0, "surrounding punctuation must not hide a core path"
    result = json.loads((tmp_path / "o.json").read_text(encoding="utf-8"))
    assert any(v["path"] == "silentgate/direction.py" for v in result["violations"])


def test_control_face_is_not_green_while_the_core_is_absent(tmp_path):
    """The gate itself. NOT GREEN, and it says which of the two reasons applies.

    Guarded: once the entrant commits the core this test has nothing to assert,
    and without the guard the project's success would read as a harness
    regression. The unconditional half -- that every registered gate is on the
    face and none was quietly dropped -- runs either way.
    """
    out = tmp_path / "face.json"
    proc = run_py("run_controls.py", "--out-json", str(out))
    face = json.loads(out.read_text(encoding="utf-8"))
    gates = {g["key"]: g for g in face["gates"]}
    # unconditional: every registered gate is on the face, none quietly dropped
    for key in (
        "core_present", "disjointness", "positive_9_9", "negative_qe_0_11",
        "partition_20_20", "two_witness_n_n", "tag_agreement_20_20", "negative_oc20",
    ):
        assert key in gates, "gate %s vanished from the face" % key
    assert face["commit"] and face["commit"] != "UNKNOWN"

    if os.path.isdir(os.path.join(ROOT, "silentgate")):
        pytest.skip("the entrant has committed the core; this test asserts its absence")
    assert proc.returncode != 0, "the face must not go green without the controls"
    assert "NOT GREEN" in proc.stdout
    assert face["green"] is False
    assert gates["core_present"]["verdict"] is False


def test_oc20_is_not_measured_until_the_entrant_elects_a_mechanism(tmp_path):
    """:1868 leaves the transport open; CI must not default it."""
    out = tmp_path / "oc20.json"
    proc = run_py("run_oc20.py", "--out-json", str(out), env={"S1_OC20_MECHANISM": ""})
    assert proc.returncode != 0
    rec = json.loads(out.read_text(encoding="utf-8"))
    assert rec["status"] == "NOT MEASURED"
    assert "entrant's call" in rec["detail"]


def test_a_missing_oc20_verdict_is_not_green(tmp_path):
    """"a commit on which the OC20 job did not execute is not green" (:1868)."""
    out = tmp_path / "face.json"
    proc = run_py(
        "run_controls.py",
        "--oc20-json", str(tmp_path / "no-such-artifact.json"),
        "--out-json", str(out),
    )
    assert proc.returncode != 0
    face = json.loads(out.read_text(encoding="utf-8"))
    oc = [g for g in face["gates"] if g["key"] == "negative_oc20"][0]
    assert oc["status"] == "NOT MEASURED"
    assert oc["verdict"] is not True


def test_the_populations_are_9_and_11_not_20_nosym_absent():
    """The registered correction of record, encoded so it cannot be re-broken.

    :1862, verbatim: "The 20-nosym-absent population does not exist." The record
    is 20 production adsorbate relaxations in total: 9 nosym-absent (all LOCKED)
    and 11 nosym-present (0 LOCKED). "20-for-20" is the flag->class partition,
    not a LOCKED rate. "A literal >=95 %-of-20 gate would void the campaign's own
    finding on day one."
    """
    path = os.path.join(CI, "populations.txt")
    absent, present = [], []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            kind, p = line.split()
            (absent if kind == "nosym_absent" else present).append(p)
    assert len(absent) == 9, "the nosym-absent population is 9, not 20"
    assert len(present) == 11
    assert len(absent) + len(present) == 20
    for p in absent + present:
        assert os.path.exists(os.path.join(ROOT, p)), (
            "the positive control is enumerated by file (docs/43:1864) and this "
            "one is gone: %s" % p
        )


def test_no_ninety_five_percent_gate_anywhere_in_the_harness():
    """The superseded ">=95 % of 20" threshold must not appear as a LIVE rule.

    Comment lines are exempt: the correction of record has to be able to quote
    the wording it supersedes, and .github/ci/populations.txt does exactly that.
    What must never appear is an executable line carrying the threshold.
    """
    import re
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    self_path = os.path.abspath(__file__)
    pat = re.compile(r"0\.95|>=\s*95|95\s*%")
    bad = []
    for base in (os.path.join(root, ".github"), os.path.join(root, "tests", "silentgate")):
        for dirpath, _d, files in os.walk(base):
            for name in files:
                if not name.endswith((".py", ".yml", ".yaml", ".toml", ".txt")):
                    continue
                p = os.path.join(dirpath, name)
                if os.path.abspath(p) == self_path:
                    continue
                with open(p, "r", encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        stripped = line.lstrip()
                        if stripped.startswith("#") or not stripped:
                            continue
                        if pat.search(line):
                            bad.append("%s:%d: %s" % (p, i, line.strip()))
    assert not bad, "a >=95 %% threshold appears as a live rule:\n" + "\n".join(bad)


# ---------------------------------------------------------------------------
# Regression tests for the fail-open paths the 2026-08-27 adversarial audit
# found in this harness. Each one PASSED the assertion before the fix.


def test_a_windows_style_core_path_cannot_evade_the_assertion(tmp_path):
    r"""A backslash core path used to be chopped into harmless fragments.

    TOKEN_RE excluded the backslash, so the one assertion :1840 registers CI must
    perform was evadable by writing the path the way Windows prints it -- and the
    entrant's machine is Windows.
    """
    log = tmp_path / "ai-use-log.md"
    log.write_text(
        r"- silentgate\census.py -- drafted" + "\n"
        r"- silentgate\readers\pwx.py -- drafted" + "\n",
        encoding="utf-8",
    )
    proc = run_py("check_disjoint.py", "--log", str(log), "--json", str(tmp_path / "o.json"))
    assert proc.returncode != 0, "a Windows-form core path must not evade the assertion"
    result = json.loads((tmp_path / "o.json").read_text(encoding="utf-8"))
    hits = {v["path"] for v in result["violations"]}
    assert "silentgate/census.py" in hits
    assert "silentgate/readers/pwx.py" in hits


def test_a_prefixed_core_path_cannot_evade_the_assertion(tmp_path):
    """A pasted diff path or a repo-qualified path must still match."""
    log = tmp_path / "ai-use-log.md"
    log.write_text(
        "- a/silentgate/cli.py -- from a diff\n"
        "- sts-electrocatalyst/silentgate/direction.py -- repo-qualified\n"
        "- ./silentgate/classify.py -- relative\n",
        encoding="utf-8",
    )
    proc = run_py("check_disjoint.py", "--log", str(log), "--json", str(tmp_path / "o.json"))
    assert proc.returncode != 0
    result = json.loads((tmp_path / "o.json").read_text(encoding="utf-8"))
    assert len(result["violations"]) == 3, result["violations"]


def test_an_empty_log_fails_like_a_missing_one(tmp_path):
    """A log that names no file has an EMPTY file list, not a disjoint one.

    :1840 attaches the duty "each logged in the AI-use log as produced". A log
    with no entries has not discharged it, and passing here would be the same
    vacuous pass a missing log is refused for -- reached through the front door.
    """
    log = tmp_path / "ai-use-log.md"
    log.write_text("# AI-use log\n\nNothing recorded yet.\n", encoding="utf-8")
    proc = run_py("check_disjoint.py", "--log", str(log), "--json", str(tmp_path / "o.json"))
    assert proc.returncode != 0, "an empty log must not pass the assertion"
    result = json.loads((tmp_path / "o.json").read_text(encoding="utf-8"))
    assert result["status"] == "FAIL"
    assert "names no files" in result.get("reason", "")


def test_every_log_is_read_not_only_the_first(tmp_path):
    """Whether the log is one file or many is an OPEN registered question.

    Returning the first match would answer it silently, and a core path recorded
    in the second file would sail through the assertion.
    """
    a = tmp_path / "ai-use-log-1.md"
    b = tmp_path / "ai-use-log-2.md"
    a.write_text("- `pyproject.toml` -- metadata only\n", encoding="utf-8")
    b.write_text("- `silentgate/cli.py` -- this must be caught\n", encoding="utf-8")
    proc = run_py(
        "check_disjoint.py", "--log", "%s,%s" % (a, b),
        "--json", str(tmp_path / "o.json"),
    )
    assert proc.returncode != 0, "the second log must be read too"
    result = json.loads((tmp_path / "o.json").read_text(encoding="utf-8"))
    assert len(result["log_paths"]) == 2
    assert any(v["path"] == "silentgate/cli.py" for v in result["violations"])


def test_a_short_population_is_refused_rather_than_scored(tmp_path):
    """Losing the 11 nosym-present lines used to print "0/11 PASS", green, exit 0.

    The denominators were string literals and the population size was never
    checked, so a gate over an empty set read as a passing control -- the exact
    fail-open A9.2 exists to prevent (docs/43:1848).
    """
    pops = tmp_path / "populations.txt"
    with open(os.path.join(CI, "populations.txt"), "r", encoding="utf-8") as fh:
        kept = [l for l in fh if not l.strip().startswith("nosym_present")]
    pops.write_text("".join(kept), encoding="utf-8")
    proc = run_py("run_controls.py", "--populations", str(pops),
                  "--out-json", str(tmp_path / "face.json"))
    assert proc.returncode != 0
    combined = proc.stdout + proc.stderr
    assert "not the registered 11" in combined, combined[:600]


def test_the_ai_survey_is_not_wired_into_the_gate():
    """docs/research/ai-survey-2026-08-27/ is a disclosure, never an oracle.

    It preserves an AI-written force-block reader and its output so the entrant
    can see what was measured before `silentgate` existed. If any part of the
    harness ever read it, an AI census would be scoring a registered control --
    which is precisely what the authorship rule and A9.2 exist to prevent.

    POINTING at the disclosure is encouraged; comments and prose that cite it are
    how a reader finds it. What is banned is a LIVE reference -- an executable
    line that could open, load or score against it.
    """
    import re
    needle = re.compile(r"ai-survey-2026-08-27|sweep\.json|sweep\.py")
    offenders = []
    for base in (os.path.join(ROOT, ".github"), os.path.join(ROOT, "tests", "silentgate")):
        for dirpath, _d, files in os.walk(base):
            if "__pycache__" in dirpath:
                continue
            for name in files:
                if not name.endswith((".py", ".yml", ".yaml")):
                    continue  # .toml/.md/.txt here are data and prose, not code
                p = os.path.join(dirpath, name)
                if os.path.abspath(p) == os.path.abspath(__file__):
                    continue  # this test names it on purpose
                with open(p, "r", encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        stripped = line.lstrip()
                        if stripped.startswith("#") or not stripped:
                            continue
                        if needle.search(line):
                            offenders.append("%s:%d: %s" % (p, i, line.strip()))
    assert not offenders, (
        "the AI survey is referenced by the harness:\n" + "\n".join(offenders)
    )
