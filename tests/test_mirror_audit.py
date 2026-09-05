"""Pins the two md5sum dialects and the classification of src/dft/mirror_audit.py.

The 2026-09-05 audit first reported "Ni local: 0" because the local listing came
from Git for Windows' md5sum (`<hash> *./<path>`, one space) and the parser split
on two. Every local file was silently dropped and the whole tree read as
anvil-only. That is the one failure mode a mirror audit must not have.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "dft"))

import mirror_audit as ma  # noqa: E402

LINUX = (
    "0123456789abcdef0123456789abcdef  runs/s3/Ni/s0_OH__2x1v_off.replay.out\n"
    "fedcba9876543210fedcba9876543210  runs/s3/Ni/s0_OH__2x1v_off.in\n"
    "11111111111111111111111111111111  runs/a0/main/Cr/slab__u000.projwfc.out\n"
)
WINDOWS = (
    "fedcba9876543210fedcba9876543210 *./s3/Ni/s0_OH__2x1v_off.in\n"
    "22222222222222222222222222222222 *./s3/Ni/local_note.txt\n"
)


def test_both_md5sum_dialects_parse_to_the_same_keys():
    r = ma.parse_listing(LINUX)
    l = ma.parse_listing(WINDOWS)
    assert "s3/Ni/s0_OH__2x1v_off.in" in r and "s3/Ni/s0_OH__2x1v_off.in" in l
    assert r["s3/Ni/s0_OH__2x1v_off.in"] == l["s3/Ni/s0_OH__2x1v_off.in"]


def test_classification_names_the_anvil_only_output_and_not_the_projwfc():
    same, ronly, lonly, differ = ma.classify(ma.parse_listing(LINUX), ma.parse_listing(WINDOWS))
    assert same == ["s3/Ni/s0_OH__2x1v_off.in"]
    assert "s3/Ni/s0_OH__2x1v_off.replay.out" in ronly
    assert lonly == ["s3/Ni/local_note.txt"]
    assert differ == []
    pw = [k for k in ronly if ma.is_pw_output(k) and not ma.is_by_design(k)]
    assert pw == ["s3/Ni/s0_OH__2x1v_off.replay.out"], "projwfc.out is out of git by design"


def test_a_differing_hash_is_reported_not_averaged():
    a = ma.parse_listing("aaaa  runs/x/y.out\n")
    b = ma.parse_listing("bbbb *./x/y.out\n")
    assert ma.classify(a, b)[3] == ["x/y.out"]


def test_offline_run_exits_nonzero_when_an_output_is_unmirrored(tmp_path, capsys):
    rl = tmp_path / "r.txt"
    ll = tmp_path / "l.txt"
    rl.write_text(LINUX, encoding="utf-8")
    ll.write_text(WINDOWS, encoding="utf-8")
    rc = ma.main(["--remote-list", str(rl), "--local-list", str(ll),
                  "--save-dir", str(tmp_path / "out")])
    out = capsys.readouterr().out
    assert rc == 1
    assert "s0_OH__2x1v_off.replay.out" in out
    assert (tmp_path / "out" / "mirror_anvil_only.txt").exists()
