"""P-BUILDER execution script: tested on the non-blind rutile(110) arm only.

The boundary rule is exercised in throwaway git repositories under pytest's tmp_path, with the
user's git configuration isolated; the project repository is only read.
"""
import json
import shutil
import subprocess
from types import SimpleNamespace

import pytest

from s2.p_builder import run_census as rc
from s2.p_builder.registered import CODE_DIR, PRESTATE_DIR


@pytest.fixture(scope="module")
def rutile():
    return rc.run(["rutile110"])["families"]["rutile110"]


def test_rutile_reproduces_disclosed_arm(rutile):
    assert rutile["reproduces_disclosure"] is True
    assert rutile["disclosure_2026_08_15"]["docs43_line"] == 1902
    c = rutile["census"]
    assert (c["O"]["retained"], c["OH"]["retained"], c["OOH"]["retained"]) == (9, 9, 0)
    assert (c["O"]["n_space_group_P1"], c["OOH"]["n_space_group_P1"]) == (1, 10)
    assert rutile["verdicts"] == {"O": "HELD", "OH": "HELD"}
    assert rutile["construction_checks"]["void_reasons"] == []
    assert rutile["reproduction"]["reproducible"]


def test_rutile_pooled_rate_is_reported_without_verdict(rutile):
    p = rutile["pooled_all_adsorbates"]
    assert (p["retained"], p["n_configurations"], p["verdict"]) == (18, 30, None)


def test_rutile_matches_committed_rerun(rutile):
    saved = json.loads((PRESTATE_DIR / "rutile_nonblind_rerun.json").read_text(encoding="utf-8"))
    s = saved["families"]["rutile110"]
    for ads in ("O", "OH", "OOH"):
        assert s["census"][ads]["retained"] == rutile["census"][ads]["retained"]
        assert [x["space_group"] for x in s["census"][ads]["configurations"]] == \
            [x["space_group"] for x in rutile["census"][ads]["configurations"]]
    assert saved["manifest_check"]["mismatches"] == {} and saved["manifest_check"]["n_code_files"] >= 10
    assert saved["manifest_check"]["verified_set_sha256"] == rc.verify_manifest(PRESTATE_DIR)["verified_set_sha256"]


@pytest.mark.parametrize("fam", ["perovskite001", "spinel001", "fcc111"])
def test_blind_family_refused_without_flag(fam, monkeypatch):
    monkeypatch.setattr(rc, "census_family", lambda *a, **k: pytest.fail("census ran on a blind family"))
    with pytest.raises(rc.BoundaryError):
        rc.run([fam])


def test_blind_family_refused_without_boundary(monkeypatch):
    monkeypatch.setattr(rc, "census_family", lambda *a, **k: pytest.fail("census ran on a blind family"))
    with pytest.raises(rc.BoundaryError):
        rc.run(["rutile110", "fcc111"], allow_blind=True,
               boundary_fn=lambda p: dict(ok=False, problems=["untracked"], boundary_commit=None, head=""))


def test_boundary_in_project_repo_is_reported_consistently():
    st = rc.boundary_status(PRESTATE_DIR)
    assert isinstance(st["ok"], bool) and st["n_paths"] == len(rc.boundary_paths(PRESTATE_DIR))
    if not st["ok"]:
        assert st["problems"]


def test_boundary_paths_cover_code_and_prestate():
    rels = {p.name for p in rc.boundary_paths(PRESTATE_DIR)}
    assert {"census.py", "decision.py", "registered.py", "run_census.py", "p-builder.md", "decision.json",
            "denominators.json", "manifest.json", "fcc111.json", "spinel001__OOH.json"} <= rels


def test_cli_refuses_blind_and_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(rc, "census_family", lambda *a, **k: pytest.fail("census ran on a blind family"))
    out = tmp_path / "x.json"
    assert rc.main(["--families", "spinel001", "--out", str(out)]) == 3
    assert not out.exists()


def test_manifest_mismatch_detected(tmp_path):
    dst = tmp_path / "prestate"
    shutil.copytree(PRESTATE_DIR, dst)
    f = dst / "configs" / "rutile110__O.json"
    f.write_text(f.read_text(encoding="utf-8").replace('"bridge"', '"hollow"', 1), encoding="utf-8")
    with pytest.raises(RuntimeError):
        rc.run(["rutile110"], prestate=dst)


def test_unlisted_census_input_detected(tmp_path):
    dst = tmp_path / "prestate"
    shutil.copytree(PRESTATE_DIR, dst)
    (dst / "configs" / "extra.json").write_text("[]\n", encoding="utf-8")
    chk = rc.verify_manifest(dst)
    assert chk["mismatches"] == {"prestate/configs/extra.json": "not in manifest"}


def test_code_change_detected(tmp_path):
    code = tmp_path / "code"
    shutil.copytree(CODE_DIR, code, ignore=shutil.ignore_patterns("__pycache__"))
    p = code / "decision.py"
    p.write_text(p.read_text(encoding="utf-8").replace('"spinel001": 8,', '"spinel001": 7,'), encoding="utf-8")
    chk = rc.verify_manifest(PRESTATE_DIR, code_dir=code)
    assert chk["mismatches"] == {"code/decision.py": "sha256 mismatch"}
    (code / "extra.py").write_text("x = 1\n", encoding="utf-8")
    assert rc.verify_manifest(PRESTATE_DIR, code_dir=code)["mismatches"]["code/extra.py"] == "not in manifest"
    with pytest.raises(RuntimeError):
        rc.run(["rutile110"], code_dir=code)


def test_crlf_checkout_is_accepted_and_listed(tmp_path):
    dst = tmp_path / "prestate"
    shutil.copytree(PRESTATE_DIR, dst)
    f = dst / "decision.json"
    f.write_bytes(f.read_bytes().replace(b"\n", b"\r\n"))
    chk = rc.verify_manifest(dst)
    assert chk["mismatches"] == {} and chk["matched_after_crlf_normalisation"] == ["prestate/decision.json"]


def test_decision_doc_hash_checked_for_blind_runs():
    chk = rc.verify_manifest(PRESTATE_DIR, include_doc=True)
    assert chk["decision_doc_checked"] and chk["mismatches"] == {}


def test_disclosure_parser():
    d = rc.read_rutile_disclosure()
    assert (d["sg"], d["ops"], d["k"], d["n"], d["p1"], d["ooh_p1"]) == ("Pmm2", 4, 9, 10, 1, 10)


# ------------------------------------------------------------------ boundary rule, throwaway repos

def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


@pytest.fixture
def mini(tmp_path, monkeypatch):
    cfg = tmp_path / "isolated.gitconfig"
    cfg.write_text("", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(cfg))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for k in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(k, "test")
    for k in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(k, "test@example.invalid")
    repo = tmp_path / "repo"
    pre, code, doc = repo / "results" / "pre", repo / "src" / "pkg", repo / "docs" / "decision.md"
    files = {doc: "decision\n", pre / "manifest.json": "{}\n", pre / "decision.json": '{"k": 8}\n',
             pre / "denominators.json": "{}\n", pre / "slabs" / "a.json": "1\n", pre / "configs" / "a__O.json": "2\n",
             pre / "structures" / "a.cif": "3\n", code / "census.py": "x = 1\n"}
    for p, t in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(t, encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)

    def commit(*paths, msg="c"):
        _git(repo, "add", "--", *[p.relative_to(repo).as_posix() for p in paths])
        _git(repo, "commit", "-q", "-m", msg)
        return _git(repo, "rev-parse", "HEAD")

    return SimpleNamespace(repo=repo, pre=pre, code=code, doc=doc, files=list(files), commit=commit,
                           status=lambda: rc.boundary_status(prestate=pre, repo=repo, code_dir=code, doc=doc))


def test_boundary_refuses_untracked(mini):
    st = mini.status()
    assert not st["ok"] and any(p.startswith("no HEAD") or p.startswith("untracked") for p in st["problems"])


def test_boundary_single_commit(mini):
    c = mini.commit(*mini.files)
    st = mini.status()
    assert st["ok"] and st["boundary_commit"] == c and st["problems"] == [] and st["n_paths"] == 8


def test_boundary_is_the_commit_completing_the_set(mini):
    mini.commit(mini.doc)
    c2 = mini.commit(*[p for p in mini.files if p != mini.doc])
    st = mini.status()
    assert st["ok"] and st["boundary_commit"] == c2


@pytest.mark.parametrize("target", ["decision.json", "census.py", "decision.md"])
def test_boundary_refuses_committed_change_after_boundary(mini, target):
    c = mini.commit(*mini.files)
    p = [f for f in mini.files if f.name == target][0]
    p.write_text(p.read_text(encoding="utf-8") + "edited\n", encoding="utf-8")
    mini.commit(p)
    st = mini.status()
    assert not st["ok"] and st["boundary_commit"] == c
    assert st["problems"] == [f"changed after boundary commit: {p.relative_to(mini.repo).as_posix()}"]


def test_boundary_refuses_uncommitted_change(mini):
    mini.commit(*mini.files)
    p = mini.pre / "decision.json"
    p.write_text('{"k": 7}\n', encoding="utf-8")
    st = mini.status()
    assert not st["ok"] and st["problems"] == ["uncommitted change: results/pre/decision.json"]


def test_boundary_refuses_new_untracked_census_input(mini):
    mini.commit(*mini.files)
    (mini.pre / "configs" / "b__O.json").write_text("9\n", encoding="utf-8")
    st = mini.status()
    assert not st["ok"] and st["problems"] == ["untracked: results/pre/configs/b__O.json"]
