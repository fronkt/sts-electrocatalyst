"""Current authorship authorization must fail closed independently of scientific controls."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / ".github" / "ci" / "check_core_authorship.py"
spec = importlib.util.spec_from_file_location("core_authorship_check", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


@pytest.fixture
def authorized_root(tmp_path):
    (tmp_path / ".github" / "ci").mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    core = tmp_path / "silentgate"
    (core / "readers").mkdir(parents=True)
    names = ["silentgate/" + name for name in checker.CORE_FILES]
    names += ["silentgate/readers/pwx.py", "silentgate/readers/oc20.py"]
    for name in names:
        (tmp_path / name).write_text("# fixture\n", encoding="utf-8")
    authorization = tmp_path / "docs" / "authorization.md"
    authorization.write_text("User authorization: implement the core.\n", encoding="utf-8")
    (tmp_path / "docs" / "provenance.md").write_text(
        "\n".join("- `%s` AI-authored" % name for name in names), encoding="utf-8")
    policy = {"schema": "silentgate-authorship-v1", "mode": "ai-assisted-authorized",
              "authorization": "docs/authorization.md",
              "authorization_sha256": hashlib.sha256(authorization.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
              "provenance": "docs/provenance.md"}
    (tmp_path / checker.POLICY).write_text(json.dumps(policy), encoding="utf-8")
    return tmp_path


def test_authorization_and_explicit_disclosure_pass(authorized_root):
    result = checker.check(authorized_root)
    assert result["status"] == "PASS"
    assert len(result["core_paths"]) == 6
    assert "disjointness assertion is not satisfied" in result["detail"]


@pytest.mark.parametrize("missing", [checker.POLICY, "docs/authorization.md", "docs/provenance.md"])
def test_missing_policy_or_evidence_fails(authorized_root, missing):
    (authorized_root / missing).unlink()
    assert checker.check(authorized_root)["status"] == "FAIL"


def test_changed_authorization_fails(authorized_root):
    (authorized_root / "docs/authorization.md").write_text("changed", encoding="utf-8")
    assert "SHA256 mismatch" in checker.check(authorized_root)["reason"]


def test_directory_or_glob_is_not_explicit_disclosure(authorized_root):
    (authorized_root / "docs/provenance.md").write_text("silentgate/* silentgate/readers/", encoding="utf-8")
    result = checker.check(authorized_root)
    assert result["status"] == "FAIL"
    assert len(result["undisclosed"]) == 6


def test_new_reader_requires_new_disclosure(authorized_root):
    (authorized_root / "silentgate/readers/new.py").write_text("# new reader\n", encoding="utf-8")
    assert checker.check(authorized_root)["undisclosed"] == ["silentgate/readers/new.py"]


def test_incomplete_core_fails_even_if_logged(authorized_root):
    (authorized_root / "silentgate/cli.py").unlink()
    assert "core incomplete" in checker.check(authorized_root)["reason"]


def test_unknown_policy_mode_fails(authorized_root):
    path = authorized_root / checker.POLICY
    policy = json.loads(path.read_text(encoding="utf-8"))
    policy["mode"] = "allow-everything"
    path.write_text(json.dumps(policy), encoding="utf-8")
    assert checker.check(authorized_root)["status"] == "FAIL"


def test_authorization_cannot_escape_repository(authorized_root):
    path = authorized_root / checker.POLICY
    policy = json.loads(path.read_text(encoding="utf-8"))
    policy["authorization"] = "../outside.md"
    path.write_text(json.dumps(policy), encoding="utf-8")
    assert "within the repository" in checker.check(authorized_root)["reason"]


@pytest.mark.parametrize("current_status", ["PASS", "FAIL"])
def test_current_policy_preserves_failed_legacy_assertion(tmp_path, monkeypatch, current_status):
    import sys
    from types import SimpleNamespace

    control_spec = importlib.util.spec_from_file_location("authorship_control_face", SCRIPT.with_name("run_controls.py"))
    controls = importlib.util.module_from_spec(control_spec)
    control_spec.loader.exec_module(controls)
    invocation = tmp_path / "invocation.toml"
    invocation.write_text('[cli]\ncensus_cmd = ""\n[schema]\n', encoding="utf-8")
    legacy = {"status": "FAIL", "violations": [{"path": "silentgate/census.py"}],
              "reason": "core path disclosed in log"}
    legacy_path = tmp_path / "legacy.json"
    legacy_path.write_text(json.dumps(legacy), encoding="utf-8")
    current_path = tmp_path / "current.json"
    current_path.write_text(json.dumps({
        "status": current_status, "mode": "ai-assisted-authorized",
        "core_paths": ["silentgate/census.py"], "undisclosed": [],
        "detail": "current policy check",
    }), encoding="utf-8")
    output = tmp_path / "face.json"
    monkeypatch.setattr(controls.subprocess, "run", lambda *a, **k: SimpleNamespace(stdout="test-commit", returncode=0))
    monkeypatch.setattr(sys, "argv", ["run_controls.py", "--invocation", str(invocation),
                        "--disjoint-json", str(legacy_path), "--authorship-json", str(current_path),
                        "--out-json", str(output)])
    controls.main()
    face = json.loads(output.read_text(encoding="utf-8"))
    assert face["legacy_disjointness"]["verdict"] is False
    assert face["legacy_disjointness_evidence"] == legacy
    gate = next(row for row in face["gates"] if row["key"] == "disjointness")
    assert gate["verdict"] is (current_status == "PASS")
    assert "current core authorship" in gate["title"]
    assert face["green"] is False  # No scientific measurement was supplied.


def test_authorization_hash_is_stable_across_line_endings(authorized_root):
    path = authorized_root / "docs/authorization.md"
    lf = path.read_bytes().replace(b"\r\n", b"\n")
    path.write_bytes(lf)
    assert checker.check(authorized_root)["status"] == "PASS"
    path.write_bytes(lf.replace(b"\n", b"\r\n"))
    assert checker.check(authorized_root)["status"] == "PASS"
