"""The pre-flight for the core commit must refuse the two states that would turn
seven registered skips into seven failures, and must never create silentgate/.

Everything runs against tmp_path. Nothing here changes the repository's own
silentgate/ path.
"""
from __future__ import annotations

import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, ".github", "ci", "preflight_core_commit.py")


def _run(root):
    return subprocess.run([sys.executable, SCRIPT, "--root", str(root), "--no-pytest"],
                          capture_output=True, text=True)


def test_an_empty_silentgate_directory_is_refused_by_name(tmp_path):
    (tmp_path / "silentgate").mkdir()
    proc = _run(tmp_path)
    assert proc.returncode != 0
    assert "EMPTY" in proc.stdout and "conftest.py:69-70" in proc.stdout


def test_a_partial_core_is_refused(tmp_path):
    sg = tmp_path / "silentgate"
    sg.mkdir()
    (sg / "census.py").write_text("x = 1\n", encoding="utf-8")
    proc = _run(tmp_path)
    assert proc.returncode != 0
    assert "core incomplete" in proc.stdout
    assert "readers" in proc.stdout and "cli.py" in proc.stdout


def test_the_preflight_never_creates_silentgate(tmp_path):
    proc = _run(tmp_path)
    assert proc.returncode != 0
    assert not (tmp_path / "silentgate").exists()
    assert "do NOT create it empty" in proc.stdout


def test_a_complete_core_passes_the_presence_check(tmp_path):
    """The same preflight seam accepts a complete instrument and rejects partial ones."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("isolated_preflight", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sg = tmp_path / "silentgate"
    (sg / "readers").mkdir(parents=True)
    (sg / "readers" / "pwx.py").write_text("# test fixture\n", encoding="utf-8")
    for name in ("census.py", "classify.py", "direction.py", "cli.py"):
        (sg / name).write_text("# test fixture\n", encoding="utf-8")
    report = module.Report()
    module.c1_core_present(str(tmp_path), report)
    assert report.ok
    assert report.rows[0][0] == "C1"


def test_missing_core_fails_c1_in_an_isolated_root(tmp_path):
    proc = _run(tmp_path)
    assert proc.returncode != 0
    assert "NOT READY" in proc.stdout
    assert "FAIL  C1" in proc.stdout
    assert not (tmp_path / "silentgate").exists()
