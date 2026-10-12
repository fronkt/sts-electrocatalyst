"""Offline checks of src/dft/zenodo_deposit.py as set up for the S8 freeze deposit; never contacts Zenodo."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import zenodo_deposit as zd  # noqa: E402

A10_MANIFEST = ROOT / "docs/deposits/2026-09-21-A10.manifest.txt"
S8_FILES = [
    "docs/research/s8-stage1-freeze-proposal-2026-10-07.md",
    "docs/95-census-2-3-readout-2026-09-13.md",
    "results/s8_ranking_statistic_2026-09-19/ranking_statistics.md",
    "docs/research/s8-arm-c-dft-design-2026-10-07.md",
    "results/arm_c_2026-10-07_rerun/readout.json",
    "docs/research/s8-arm-c-extension-2026-10-08.md",
    "results/arm_c_ext_r6_2026-10-11/readout.json",
    "docs/research/s8-melt-plan-2026-10-07.md",
    "docs/research/s8-weigh-sheet-2026-10-08.md",
]
MELT_PLAN = "docs/research/s8-melt-plan-2026-10-07.md"


def committed(path):
    return subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"HEAD:{path}"]).returncode == 0


def test_every_file_is_committed_and_carries_a_unique_name():
    paths, names = zip(*zd.FILESET)
    assert all(committed(p) for p in paths)
    assert len(set(paths)) == len(paths) and len(set(names)) == len(names)


def test_the_a10_fileset_is_carried_forward_and_the_s8_files_follow_it():
    a10 = [line.split()[-1] for line in A10_MANIFEST.read_text(encoding="utf-8").splitlines()
           if line and not line.startswith("#")]
    paths = [p for p, _ in zd.FILESET]
    assert paths == a10 + S8_FILES  # a new version replaces the whole fileset
    assert zd.FREEZE == S8_FILES[0]


def test_the_committed_deposit_is_settled():
    # the entrant confirmed the freeze as written on 2026-10-12, after three buttons were melted
    assert zd.pending() == []
    assert dict(zd.FILESET)[zd.FREEZE] == "s8-stage1-freeze-as-confirmed-2026-10-12.md"


def test_the_metadata_keeps_the_published_stem_and_adds_one_dated_paragraph():
    meta = zd.metadata(zd.head())["metadata"]
    assert meta["title"].startswith("Pre-registration record, DFT error-budget campaign (sts-electrocatalyst): "
                                    "Week-1 factorial, Hessian test, U gate — ")
    assert meta["title"].endswith("the S8 stage-1 melt freeze (confirmed 2026-10-12)")
    assert (meta["version"], meta["access_right"]) == ("A1-A13-plus-A10-plus-S8", "restricted")
    assert meta["description"].count("<p>New version, ") == 4
    s8 = meta["description"].split("<p>New version, ")[-1]
    assert s8.startswith("2026-10-12: the S8 stage-1 melt freeze, confirmed by the entrant on 2026-10-12 and "
                         "deposited after three of its six buttons")
    assert "on 2026-10-09 and 2026-10-12, with nothing yet measured on them, and before any OER measurement" in s8
    assert "the deposit follows the first ingot" in s8 and "(freeze section 1b)" in s8
    assert "K1 decides between arms A and B and K2 is shared by them" in s8
    assert "selection threshold was set after its screen was run" in s8
    assert zd.manifest_path(zd.head()) in s8 and zd.head()[:7] in s8


@pytest.mark.parametrize("attribute, value, reason", [
    ("FIRST_INGOT", "PENDING_FIRST_INGOT", "PENDING_FIRST_INGOT"),
    ("CONFIRMED", "15 Oct 2026", "not a YYYY-MM-DD date"),
    (zd.FREEZE, b"Status: **proposed, not frozen, not deposited.**\n", "proposed, not frozen"),
    (zd.FREEZE, b"Scope line [CONFIRM wording]: S8 is a declared exploratory validation set.\n", "[CONFIRM"),
    (MELT_PLAN, b"Each button is 200 g with 4% extra Mn [CONFIRM the over-charge with FWM].\n", "[CONFIRM"),
])
def test_nothing_is_written_until_the_deposit_is_settled(monkeypatch, attribute, value, reason):
    monkeypatch.setattr(zd, "api", lambda *a, **k: pytest.fail("contacted Zenodo"))
    monkeypatch.setattr(zd, "cmd_manifest", lambda *a: pytest.fail("wrote a manifest"))
    if "/" in attribute:  # a deposited file's committed text
        real = zd.blob
        monkeypatch.setattr(zd, "blob", lambda path, commit: value if path == attribute else real(path, commit))
    else:
        monkeypatch.setattr(zd, attribute, value)
    assert any(reason in r for r in zd.pending())
    for step in ("--manifest", "--create", "--upload", "--publish"):
        with pytest.raises(SystemExit, match="not ready"):
            zd.main([step])


def test_no_manifest_is_written_unless_docs43_names_it(monkeypatch, tmp_path):
    real = zd.blob
    monkeypatch.setattr(zd, "blob", lambda path, commit: b"no addendum" if path == zd.DOCS43 else real(path, commit))
    monkeypatch.setattr(zd, "manifest_path", lambda commit: str(tmp_path / "manifest.txt"))  # never the repo's
    with pytest.raises(SystemExit, match="does not name the manifest"):
        zd.cmd_manifest(zd.head())
    assert not (tmp_path / "manifest.txt").exists()


@pytest.mark.parametrize("status, blocks", [
    (b" M .gitignore\n", False),  # another session's edit, outside the deposit
    (b" M docs/45-error-ledger.md\n", True),
    (b" M docs/deposits/.draft_state.json\n", True),
])
def test_only_a_modified_deposited_file_blocks_the_deposit(monkeypatch, status, blocks):
    real = zd.git
    monkeypatch.setattr(zd, "git", lambda *args: status if args[0] == "status" else real(*args))
    if blocks:
        with pytest.raises(SystemExit, match="deposited files are modified"):
            zd.check_clean()
    else:
        zd.check_clean()
