"""The pre-flight for the core commit must refuse the two states that would turn
seven registered skips into seven failures, and must never create silentgate/.

Everything runs against tmp_path. Nothing here touches the repository's own
silentgate/ path, which does not exist and must not be created by a test.
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


def test_the_repository_itself_is_not_ready_and_says_why():
    """Against the real tree: the core is absent (entrant-only), so NOT READY --
    and C1 must be the reason, never a crash in a later check."""
    proc = _run(ROOT)
    assert proc.returncode != 0
    assert "NOT READY" in proc.stdout
    assert "FAIL  C1" in proc.stdout
    assert not os.path.isdir(os.path.join(ROOT, "silentgate"))
