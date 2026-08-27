"""Shared fixtures for the `silentgate` S1 suite.

AUTHORSHIP: written by AI as "tests and fixtures" under the A9.1 :1840 permitted
list. Nothing in this directory parses a pw.x output. The readers, the census,
the classifier, the direction map and the CLI are core, "written and committed
only by the entrant" (docs/43:1840), and this suite exercises them from outside.
"""
from __future__ import annotations

import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CI = os.path.join(ROOT, ".github", "ci")
MANIFEST = os.path.join(HERE, "fixtures", "manifest.toml")

# The five-entry core path list, docs/43:1840. Restated here so the suite can
# check that .github/ci/core_paths.txt has not drifted from the registered text.
REGISTERED_CORE_PATHS = (
    "silentgate/readers/*",
    "silentgate/census.py",
    "silentgate/classify.py",
    "silentgate/direction.py",
    "silentgate/cli.py",
)

CORE_ABSENT_REASON = (
    "silentgate/ does not exist yet. The core is entrant-written and "
    "entrant-committed (docs/43:1840); this test scores the core, so it cannot "
    "run until the core is committed. The GATE for that state is the control "
    "face, which reports NOT GREEN -- see test_face_fails_closed."
)


def _load_toml(path):
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
        import tomli as tomllib  # type: ignore
    with open(path, "rb") as fh:
        return tomllib.load(fh)


@pytest.fixture(scope="session")
def repo_root():
    return ROOT


@pytest.fixture(scope="session")
def ci_dir():
    return CI


@pytest.fixture(scope="session")
def manifest():
    return _load_toml(MANIFEST)


@pytest.fixture(scope="session")
def invocation():
    return _load_toml(os.path.join(CI, "silentgate-invocation.toml"))


@pytest.fixture(scope="session")
def core_present():
    return os.path.isdir(os.path.join(ROOT, "silentgate"))


@pytest.fixture
def requires_core(core_present):
    if not core_present:
        pytest.skip(CORE_ABSENT_REASON)


@pytest.fixture(scope="session")
def corpus_scan():
    """One pass over every tracked runs/*.out, yielding only small derived facts.

    Session-scoped on purpose: three tripwires need the same sweep, the corpus is
    375 MB on disk, and CI runs this on every commit. Nothing here censuses a
    force -- it records which marker lines a file carries.
    """
    import re

    SYM = re.compile(rb"^.*?(\d+)\s+Sym\.\s*Ops\..*$", re.M)
    CONTRIB = re.compile(
        rb"^\s*The .{0,40}(?:contrib\.|contribution|correction term)\s+to forces\s*$", re.M)

    files = [
        f for f in subprocess.run(
            ["git", "ls-files", "runs/"], capture_output=True, text=True, cwd=ROOT
        ).stdout.split("\n") if f.endswith(".out")
    ]
    scan = {}
    for f in files:
        b = read_lf(os.path.join(ROOT, f))
        m = SYM.search(b)
        scan[f] = {
            "header_form": (
                re.sub(r"\d+", "N", m.group(0).decode("utf8", "replace").strip())
                if m else None
            ),
            "no_symmetry_found": b"No symmetry found" in b,
            "has_decomposition": bool(CONTRIB.search(b)),
        }
    return scan


def read_lf(path):
    """Bytes with CRLF normalised to LF.

    *.out carries no .gitattributes rule and core.autocrlf=true on the entrant's
    machine, so the same tracked blob is CRLF in the Windows working tree and LF
    on Linux CI. Every content check in this suite normalises first.
    """
    with open(path, "rb") as fh:
        return fh.read().replace(b"\r\n", b"\n")


def run_py(script, *args, env=None):
    """Run one of the .github/ci scripts and return the CompletedProcess."""
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(
        [sys.executable, os.path.join(CI, script), *args],
        capture_output=True, text=True, cwd=ROOT, env=e,
    )
