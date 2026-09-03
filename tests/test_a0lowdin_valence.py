"""Tests for src/dft/a0lowdin_valence.py (docs/43 A11.R7, registered 2026-09-03).

The registration makes five self-checks FATAL and fixes the scope rule, the active-site
rule and the statistics before any number was read.  These tests pin exactly those:

  T1  the nspin=1 and nspin=2 Lowdin shapes both parse, on REAL banked artifacts,
      and the parser's d-channel agrees with an independently written extraction;
  T2  self-check 2 (total == s+p+d) is fatal on a corrupted total;
  T3  self-check 3 (up_d + dn_d == total d) is fatal on a corrupted spin row;
  T4  the scope rule admits exactly ^u\\d{3}$ and names every exclusion;
  T5  the active-site rule returns a metal atom, the same index for all four states;
  T6  spearman/perm_p are correct on hand-checkable inputs;
  T7  the banked readout cross-check: span_U(c_M)/2 reproduces a0main_readout.json's
      span_over_2_V on all six metals (the response side's independent witness);
  T8  A11.R7's binding clause is present in the emitted JSON.

Tests read runs/ and docs/figs/ but NEVER write, modify or delete anything there.
All writes go to tmp_path.
"""
import importlib.util
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOD_PATH = os.path.join(ROOT, "src", "dft", "a0lowdin_valence.py")


def _load():
    spec = importlib.util.spec_from_file_location("a0lowdin_valence", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = _load()

NSPIN1 = os.path.join(ROOT, "runs", "a0", "main", "Ru", "slab__u000.lowdin.txt")
NSPIN2 = os.path.join(ROOT, "runs", "a0", "main", "Cr", "slab__u000.lowdin.txt")


def _independent_d(path, atom):
    """Independently extract the d charge for `atom` -- deliberately NOT the module's
    parser, so T1 compares two readings of the same bytes."""
    want = re.compile(r"^\s*Atom #\s*%d:\s*total charge" % atom)
    for line in open(path, encoding="utf-8", errors="replace"):
        if want.match(line):
            hit = re.search(r"\bd\s*=\s*([-\d.]+)", line)
            if hit:
                return float(hit.group(1))
    raise AssertionError("no d row for atom %d in %s" % (atom, path))


# ------------------------------------------------------------------------ T1 --

@pytest.mark.parametrize("path", [NSPIN1, NSPIN2])
def test_t1_both_shapes_parse_and_agree(path):
    if not os.path.exists(path):
        pytest.skip("banked artifact absent: %s" % path)
    atoms = M.parse_lowdin(path)
    assert len(atoms) >= 18, "expected a full slab census"
    M.check_atoms(path, atoms)
    for idx in (1, 5):
        assert M.d_charge(atoms, idx) == pytest.approx(
            _independent_d(path, idx), abs=1e-9)


def test_t1b_nspin_flag_is_read_from_the_file_not_assumed():
    if not (os.path.exists(NSPIN1) and os.path.exists(NSPIN2)):
        pytest.skip("banked artifacts absent")
    assert M.parse_lowdin(NSPIN1)[5]["nspin2"] is False
    assert M.parse_lowdin(NSPIN2)[5]["nspin2"] is True


# ------------------------------------------------------------------- T2, T3 --

def test_t2_corrupted_total_is_fatal(tmp_path):
    if not os.path.exists(NSPIN1):
        pytest.skip("banked artifact absent")
    lines = open(NSPIN1, encoding="utf-8").read().splitlines(True)
    for i, ln in enumerate(lines):
        m = re.match(r"^(\s*Atom #\s*\d+:\s*total charge =\s*)([-\d.]+)(,.*)$", ln)
        if m:
            lines[i] = "%s%.4f%s\n" % (m.group(1), float(m.group(2)) + 85.0,
                                       m.group(3).rstrip("\n"))
            break
    else:
        pytest.skip("no atom row found to corrupt")
    bad = "".join(lines)
    p = tmp_path / "bad.lowdin.txt"
    p.write_text(bad, encoding="utf-8")
    with pytest.raises(M.Fatal) as e:
        M.check_atoms(str(p), M.parse_lowdin(str(p)))
    assert "CHECK 2 FAILED" in str(e.value) or "two different total charges" in str(e.value)


def test_t3_corrupted_spin_channel_is_fatal(tmp_path):
    if not os.path.exists(NSPIN2):
        pytest.skip("banked artifact absent")
    lines = open(NSPIN2, encoding="utf-8").read().splitlines(True)
    for i, ln in enumerate(lines):
        m = re.match(r"^(\s*spin up\s*=\s*[-\d.]+,\s*d\s*=\s*)([-\d.]+)(.*)$", ln)
        if m:
            lines[i] = "%s%.4f%s\n" % (m.group(1), float(m.group(2)) + 5.0,
                                       m.group(3).rstrip("\n"))
            break
    else:
        pytest.skip("no spin-up d row found to corrupt")
    p = tmp_path / "bad2.lowdin.txt"
    p.write_text("".join(lines), encoding="utf-8")
    with pytest.raises(M.Fatal) as e:
        M.check_atoms(str(p), M.parse_lowdin(str(p)))
    assert "CHECK 3 FAILED" in str(e.value)


# ------------------------------------------------------------------------ T4 --

def test_t4_scope_rule_is_exactly_three_digit_u_tokens():
    ok = ["u000", "u150", "u900", "u673"]
    bad = ["pilot530_m010", "u300__r1", "u450__r2b", "base", "u0.0", "u12", "u1234"]
    for t in ok:
        assert M.UTOK_RE.match(t), t
    for t in bad:
        assert not M.UTOK_RE.match(t), t


def test_t4b_every_exclusion_is_named_in_the_banked_census():
    j = os.path.join(ROOT, "docs", "figs", "a0lowdin_valence.json")
    if not os.path.exists(j):
        pytest.skip("readout not yet generated")
    out = json.load(open(j, encoding="utf-8"))
    for row in out["census"]["excluded"]:
        assert len(row) == 3 and row[2], "an exclusion carries no reason: %r" % (row,)


# ------------------------------------------------------------------------ T5 --

def test_t5_active_site_is_a_metal_and_stable_across_states():
    for metal in M.METALS:
        mdir = os.path.join(ROOT, "runs", "a0", "main", metal)
        if not os.path.isdir(mdir):
            pytest.skip("A0 grid absent")
        idx, dist, n_slab = M.active_site(metal, mdir)
        assert 1 <= idx <= n_slab, "%s: site %d outside the slab" % (metal, idx)
        assert 1.5 < dist < 2.6, "%s: M-O distance %.3f A is not a bond" % (metal, dist)
        # the same index must exist in every state's artifact
        for state in M.STATES:
            p = os.path.join(mdir, "%s__%s.lowdin.txt" % (state, M.BASE_UTOK))
            if os.path.exists(p):
                assert idx in M.parse_lowdin(p), "%s %s missing atom %d" % (
                    metal, state, idx)


# ------------------------------------------------------------------------ T6 --

def test_t6_spearman_and_permutation_p():
    assert M.spearman([1, 2, 3, 4], [1, 2, 3, 4]) == pytest.approx(1.0)
    assert M.spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    # ties get average ranks
    assert M.spearman([1, 1, 2, 2], [1, 1, 2, 2]) == pytest.approx(1.0)
    rho, p, how = M.perm_p([1, 2, 3, 4], [1, 2, 3, 4])
    assert rho == pytest.approx(1.0)
    assert "exact" in how
    assert p == pytest.approx(2.0 / 24.0)   # only the identity and its reverse hit |1|


# ------------------------------------------------------------------------ T7 --

def test_t7_response_reproduces_the_banked_a7_3_spans():
    j = os.path.join(ROOT, "docs", "figs", "a0lowdin_valence.json")
    b = os.path.join(ROOT, "docs", "figs", "a0main_readout.json")
    if not (os.path.exists(j) and os.path.exists(b)):
        pytest.skip("readouts absent")
    out = json.load(open(j, encoding="utf-8"))
    bank = json.load(open(b, encoding="utf-8"))
    for metal, v in out["per_metal"].items():
        assert v["span_cM"] / 2.0 == pytest.approx(
            bank["a7_3"]["per_metal"][metal]["span_over_2_V"], abs=1e-12), metal


# ------------------------------------------------------------------------ T8 --

def test_t8_binding_clause_present():
    j = os.path.join(ROOT, "docs", "figs", "a0lowdin_valence.json")
    if not os.path.exists(j):
        pytest.skip("readout not yet generated")
    out = json.load(open(j, encoding="utf-8"))
    assert "moves no banked verdict" in out["binding"]
    assert "NOT MET at 3 of 6" in out["binding"]
    assert out["r7_p2"]["verdict"].startswith("REPORTED, NEVER SCORED")
    assert "POST-HOC" in out["POST_HOC_all_six"]["status"]
