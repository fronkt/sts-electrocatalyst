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
CONFIRMED_FREEZE = b"# S8 stage-1 melt freeze\n\nStatus: **frozen 2026-10-15** by the entrant.\n"


def committed(path):
    return subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"HEAD:{path}"]).returncode == 0


def filled(monkeypatch, freeze=CONFIRMED_FREEZE):
    """The entrant's values filled in and the freeze text confirmed, as they will be at deposit time."""
    monkeypatch.setattr(zd, "CONFIRMED", "2026-10-15")
    monkeypatch.setattr(zd, "FIRST_INGOT", "before the first ingot")
    monkeypatch.setattr(zd, "FILESET", [(p, n.replace("PENDING_CONFIRMATION_DATE", "2026-10-15"))
                                        for p, n in zd.FILESET])
    real = zd.blob
    monkeypatch.setattr(zd, "blob", lambda path, commit: freeze if path == zd.FREEZE else real(path, commit))


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


def test_the_metadata_keeps_the_published_stem_and_adds_one_dated_paragraph(monkeypatch):
    filled(monkeypatch)
    meta = zd.metadata(zd.head())["metadata"]
    assert meta["title"].startswith("Pre-registration record, DFT error-budget campaign (sts-electrocatalyst): "
                                    "Week-1 factorial, Hessian test, U gate — ")
    assert (meta["version"], meta["access_right"]) == ("A1-A13-plus-A10-plus-S8", "restricted")
    assert meta["description"].count("<p>New version, ") == 4
    s8 = meta["description"].split("<p>New version, ")[-1]
    assert s8.startswith("2026-10-15: the S8 stage-1 melt freeze") and "before the first ingot" in s8
    assert "K1 decides between arms A and B and K2 is shared by them" in s8
    assert "selection threshold was set after its screen was run" in s8
    assert zd.manifest_path(zd.head()) in s8 and zd.head()[:7] in s8


def test_a_settled_deposit_has_nothing_pending(monkeypatch):
    filled(monkeypatch)
    assert zd.pending() == []


@pytest.mark.parametrize("attribute, value, reason", [
    ("FIRST_INGOT", "PENDING_FIRST_INGOT", "PENDING_FIRST_INGOT"),
    ("CONFIRMED", "15 Oct 2026", "not a YYYY-MM-DD date"),
    ("freeze", b"Status: **proposed, not frozen, not deposited.**\n", "proposed, not frozen"),
    ("freeze", b"Scope line [CONFIRM wording]: S8 is a declared exploratory validation set.\n", "[CONFIRM"),
])
def test_nothing_is_written_until_the_deposit_is_settled(monkeypatch, attribute, value, reason):
    monkeypatch.setattr(zd, "api", lambda *a, **k: pytest.fail("contacted Zenodo"))
    monkeypatch.setattr(zd, "cmd_manifest", lambda *a: pytest.fail("wrote a manifest"))
    filled(monkeypatch, value if attribute == "freeze" else CONFIRMED_FREEZE)
    if attribute != "freeze":
        monkeypatch.setattr(zd, attribute, value)
    assert any(reason in r for r in zd.pending())
    for step in ("--manifest", "--create", "--upload", "--publish"):
        with pytest.raises(SystemExit, match="not ready"):
            zd.main([step])
