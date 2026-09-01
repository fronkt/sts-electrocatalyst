"""Tests for src/dft/a0spin_census.py (the a7_3_spin equalised sensitivity census
readout; docs/43 AMENDMENT 11 A11.R1 [A11.6 SEEDS+SELECTION] + Rider 2, A11.R3
[CR/MN/FE SEED SEARCH]; docs/61 SSA11.6/SSA11.7; docs/66 SS2 rows 3-7/12).

Two evidence classes:

  BANKED (runs/a0/spin + runs/a0/main, read-only):
    B1  the 8 Stage-0 P11-reproduction rungs (Ru/Ir x 4 states) reproduce their
        banked selection: floor deltas match docs/62 SS4 to <= 0.005 meV and the
        Ir slab seed-0.50 rung is REJECTED by the variational floor (+0.583 meV)
    B2  cell-level integration on the same 8 rungs: candidate verdicts + the
        never-select-a-rejected-row invariant
    B3  the two Ti null controls reproduce docs/62 SS5 (slab CONTROL-PASS,
        s0_OOH CONTROL-BREAKS)
    B4  the (Ti, s0_OOH, u900) pool contains the banked null-seed row
        -1298.17043625 Ry (A11.R1 Rider 2) on the real tree
    B5  Cr/Mn/Fe incumbents are the banked FM rows and the A11.R3 coverage
        convention (banked seed == grid member covers the cell) is applied
    B6  full main() run: exit clean, JSON written only to the given path,
        byte-identical on a double run, runs/ + docs/figs untouched, Ti rows
        PENDING-CONFIRMATION while docs/59 SS5 lacks the dated CONFIRMED line
    B7  refusal paths: --help / extra args / paths under runs/ or docs/ /
        existing output -- all refuse and write nothing

  SYNTHETIC (fixtures under the scratchpad or tmp_path; never under the repo):
    S1  gate detectors: GRANTED literal, placeholder-dated CONFIRMED template is
        NOT a confirmation, fully dated line IS
    S2  a <= 1 meV tie selects the smaller |seed| even against a strictly lower
        energy
    S3  floor equality (dE == 0) PASSES -- the candidate is admitted
    S4  floor +0.1 meV is REJECTED and the rejection is recorded
    S5  the Ti fifth candidate (Rider 2 null row) is present in the pool and can
        win the selection at seed 0.0
    S6  an unconverged .out is refused: recorded UNCONVERGED, excluded from the
        pool, never the winner
    S7  a literal 0.0 seed is separately fatal outside the two whitelisted null
        controls (both spellings: a stray __sp2null stem, and an all-zero seed
        block on a grid stem)

Tests read runs/ and docs/ but NEVER write, modify, or delete anything there.
All writes go to the scratchpad fixture root (or tmp_path as fallback).
"""
import io
import json
import os
import shutil
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dft import a0spin_census as ac  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUNS = os.path.join(REPO, "runs")
FIGS = os.path.join(REPO, "docs", "figs")

#: synthetic fixtures live in the session scratchpad when one exists (never the
#: repo); tmp_path is the fallback so the suite stays runnable anywhere.
_SCRATCH = os.environ.get("CLAUDE_SCRATCHPAD_DIR") or os.path.join(
    os.environ.get("TEMP", ""), "claude",
    "C--Users-frank", "f6c183bd-0475-4096-8861-eaa7ede9ebef", "scratchpad")

RY = ac.RY_EV  # eV per Ry, from qe_qc via the module under test


@pytest.fixture(autouse=True)
def _fresh_read_log():
    """The module logs md5s of every banked read (CEN-a); isolate per test."""
    ac.READ_LOG.clear()
    yield
    ac.READ_LOG.clear()


@pytest.fixture
def fixdir(tmp_path, request):
    """Per-test synthetic-fixture root: scratchpad if present, else tmp_path."""
    if os.path.isdir(_SCRATCH):
        d = os.path.join(_SCRATCH, "a0spin_census_fixtures", request.node.name)
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)
        return d
    return str(tmp_path)


# ---------------------------------------------------------------------------
# synthetic deck / output factories
# ---------------------------------------------------------------------------

_SPECIES = {
    "Ru": ["  H  1.008  H.pbe-rrkjus_psl.1.0.0.UPF",
           "  Ru  101.070  Ru_ONCV_PBE-1.0.oncvpsp.upf",
           "  O  15.999  O.pbe-n-kjpaw_psl.0.1.UPF"],
    "Ti": ["  H  1.008  H.pbe-rrkjus_psl.1.0.0.UPF",
           "  Ti  47.867  ti_pbe_v1.4.uspp.F.UPF",
           "  O  15.999  O.pbe-n-kjpaw_psl.0.1.UPF"],
}
_MIDX = {"Ru": 2, "Ti": 2}   # the metal's 1-based ATOMIC_SPECIES index above


def _deck(metal, seed=None, null=False):
    """Minimal pw.x input the readout's deck anatomy accepts. seed=None with
    null=False -> the banked nspin = 1 incumbent shape (no spin keys at all)."""
    body = ["&CONTROL", "  calculation = 'scf'", "/", "&SYSTEM", "  ntyp = 3",
            "  nat = 4"]
    if null or seed is not None:
        body.append("  nspin = 2")
        for i in (1, 2, 3):
            v = "%.2f" % seed if (not null and i == _MIDX[metal]) else "0.0"
            body.append("  starting_magnetization(%d) = %s" % (i, v))
    body += ["/", "&ELECTRONS", "  conv_thr = 1.0d-6", "/", "ATOMIC_SPECIES"]
    body += _SPECIES[metal]
    body += ["K_POINTS automatic", "  4 4 1 0 0 0", ""]
    return "\n".join(body)


def _out(e=None, totmag=None, absmag=None, converged=True):
    """Minimal pw.x output the gate-(h) recipe parses. All fixtures share one
    electron count / Sym. Ops. line / k-count so guards 1 + CEN-h compare
    equal between candidate and incumbent."""
    L = ["     Program PWSCF v.7.5 starts on synthetic fixture",
         "     number of electrons       =       175.00",
         "      2 Sym. Ops. (no inversion) found ( 1 have fractional translation)",
         "     number of k points=    15  Marzari-Vanderbilt smearing, width (Ry)=  0.0100"]
    if totmag is not None:
        L += ["     total magnetization       =     %.2f Bohr mag/cell" % totmag,
              "     absolute magnetization    =     %.2f Bohr mag/cell"
              % (totmag if absmag is None else absmag)]
    if converged:
        L += ["     convergence has been achieved in  25 iterations",
              "!    total energy              =  %.8f Ry" % e]
    else:
        L += ["     convergence NOT achieved after 200 iterations: stopping"]
    L += ["     JOB DONE.", ""]
    return "\n".join(L)


def _w(path, txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt)


def _mk_cell(root, metal, state, utok, inc_e, cands, monkeypatch):
    """Build a synthetic main/ + spin/ pair for one cell and point the module
    at it. cands: list of (token, energy | 'UNCONVERGED', totmag)."""
    main = os.path.join(root, "main")
    spin = os.path.join(root, "spin")
    _w(os.path.join(main, metal, "%s__%s.in" % (state, utok)), _deck(metal))
    _w(os.path.join(main, metal, "%s__%s.out" % (state, utok)), _out(inc_e))
    for token, e, tm in cands:
        stem = "%s__%s__%s" % (state, utok, token)
        null = token == "sp2null"
        seed = None if null else int(token[4:]) / 100.0
        _w(os.path.join(spin, metal, stem + ".in"),
           _deck(metal, seed=seed, null=null))
        if e == "UNCONVERGED":
            _w(os.path.join(spin, metal, stem + ".out"), _out(converged=False))
        elif e is not None:
            _w(os.path.join(spin, metal, stem + ".out"), _out(e, totmag=tm))
    monkeypatch.setattr(ac, "MAIN", main)
    monkeypatch.setattr(ac, "SPIN", spin)


def _cand(cell, token):
    return next(c for c in cell["candidates"] if c["stem"].endswith(token))


# ---------------------------------------------------------------------------
# B1/B2 -- the banked Stage-0 rungs reproduce their banked selection
# ---------------------------------------------------------------------------

def test_b1_stage0_eight_rows_reproduce_banked():
    rows = ac.stage0_controls()
    assert len(rows) == 8
    for (m, st), lit in ac.S0_FLOOR_MEV.items():
        r = rows["%s/%s" % (m, st)]
        assert r["p11_reproduction"].startswith("PASS")
        assert abs(r["dE_vs_nspin1_meV"] - lit) <= 0.005
        if lit > 0.0:
            assert "REJECT" in r["floor"]
        else:
            assert r["floor"].startswith("PASS")
    # the one positive delta is the Ir slab, and it is refused by the floor
    assert "REJECT" in rows["Ir/slab"]["floor"]
    assert abs(rows["Ir/slab"]["dE_vs_nspin1_meV"] - 0.583) <= 0.005


def test_b2_stage0_cells_and_ir_slab_rejection():
    for (m, st), lit in sorted(ac.S0_FLOOR_MEV.items()):
        cell = ac.build_cell(m, st, "u000")
        c = _cand(cell, "sp2m050")
        assert abs(c["dE_vs_incumbent_meV"] - lit) <= 0.005
        if (m, st) == ("Ir", "slab"):
            # docs/62 SS4: REJECT (+0.583 meV) -- refused by the floor,
            # recorded with its energy, and NEVER selectable
            assert c["status"].startswith("REJECT-FLOOR")
            assert "energy_ry" in c
        else:
            assert c["status"] == "ADMITTED"
        assert cell["selection"]["winner"] != c["stem"] or \
            not c["status"].startswith("REJECT-FLOOR")
    ir = ac.build_cell("Ir", "slab", "u000")
    assert ir["selection"]["winner"] != "slab__u000__sp2m050"
    assert ir["incumbent"]["kind"] == "banked nspin = 1 row"
    assert ir["incumbent"]["seed"] == 0.0


def test_b3_null_controls_reproduce_docs62():
    rows = ac.null_controls(confirmed=False)
    assert rows["slab__u900__sp2null"]["verdict"].startswith("CONTROL-PASS")
    assert rows["s0_OOH__u900__sp2null"]["verdict"].startswith("CONTROL-BREAKS")
    # unconfirmed -> numeric values withheld from the report body
    for r in rows.values():
        assert "energy_ry" not in r and "values" in r


def test_b4_rider2_row_in_the_real_pool():
    cell = ac.build_cell("Ti", "s0_OOH", "u900")
    rider = [c for c in cell["candidates"] if "Rider 2" in c["kind"]]
    assert len(rider) == 1
    assert rider[0]["status"] == "ADMITTED"
    assert rider[0]["energy_ry"] == ac.RIDER2_E_RY
    assert abs(rider[0]["dE_vs_incumbent_meV"] - (-153.072)) <= 0.005


def test_b5_cmf_incumbents_and_coverage():
    expect = {("Cr", "s0_OH"): (0.6, ["0.10", "0.30", "0.50"], False),
              ("Mn", "s0_OH"): (0.5, ["0.10", "0.30"], True),
              ("Fe", "s0_OH"): (0.5, ["0.10", "0.30"], True),
              ("Fe", "s0_OOH"): (0.1, ["0.30", "0.50"], True)}
    for (m, st), (seed, req, cov) in expect.items():
        cell = ac.build_cell(m, st, "u000")
        assert cell["incumbent"]["kind"] == \
            "banked FM row (incumbent candidate)"
        assert abs(cell["incumbent"]["seed"] - seed) < 1e-9
        assert cell["required_seeds"] == req
        assert cell["covered_by_incumbent"] is cov


# ---------------------------------------------------------------------------
# B6 -- full readout: clean run, determinism, read-only over the banked trees
# ---------------------------------------------------------------------------

def _tree_sig(root):
    sig = []
    for r, _, fs in os.walk(root):
        for f in sorted(fs):
            p = os.path.join(r, f)
            st = os.stat(p)
            sig.append((p, st.st_size, st.st_mtime_ns))
    return sorted(sig)


def test_b6_main_run_readonly_and_deterministic(fixdir, capsys):
    before = _tree_sig(RUNS) + _tree_sig(FIGS)
    p1 = os.path.join(fixdir, "census_run1.json")
    p2 = os.path.join(fixdir, "census_run2.json")
    r1 = ac.main([p1])
    ac.READ_LOG.clear()
    r2 = ac.main([p2])
    assert _tree_sig(RUNS) + _tree_sig(FIGS) == before, \
        "the readout touched runs/ or docs/figs"
    with open(p1, "rb") as a, open(p2, "rb") as b:
        assert a.read() == b.read(), "double run is not byte-identical"

    assert r1["gates"]["licence_granted"] is True
    body = r1["a7_3_spin"]
    assert body["sensitivity_only"] is True
    assert body["as_built_headline"]["status"] == "NOT MET"
    assert body["as_built_headline"]["over"] == ["Cr", "Fe", "Mn"]
    assert set(r1["assertions"].values()) == {"PASS"}
    ti = body["per_metal"]["Ti"]
    if r1["gates"]["confirmed"]:
        assert ti["equalised"] != "PENDING-CONFIRMATION"
    else:
        # the current tree state: docs/59 SS5 has no dated CONFIRMED line, so
        # Ti rows appear PENDING-CONFIRMATION and are never scored
        assert ti["equalised"] == "PENDING-CONFIRMATION"
        assert "Ti" not in body["cells"]
    out = capsys.readouterr().out
    assert "READOUT OK" in out


def test_b7_refusals_write_nothing(fixdir):
    for bad in (["--help"], ["-x"], ["a.json", "b.json"],
                [os.path.join(RUNS, "a0", "nope.json")],
                [os.path.join(REPO, "docs", "figs", "nope.json")]):
        with pytest.raises(SystemExit):
            ac.main(bad)
    assert not os.path.exists(os.path.join(RUNS, "a0", "nope.json"))
    assert not os.path.exists(os.path.join(REPO, "docs", "figs", "nope.json"))
    exists = os.path.join(fixdir, "already_there.json")
    _w(exists, "{}\n")
    with pytest.raises(SystemExit):
        ac.main([exists])
    with open(exists) as fh:
        assert fh.read() == "{}\n", "existing output was overwritten"


# ---------------------------------------------------------------------------
# S1 -- the docs/59 gate detectors
# ---------------------------------------------------------------------------

def test_s1_gate_detectors():
    grant = ac.GRANT_LIT + " — EXECUTED UNDER DIRECTIVE]"
    g = ac.gates_from_text("preamble\n" + grant + "\n")
    assert g["licence_granted"] and not g["confirmed"]
    # the reserved SS5 template carries a placeholder date: NOT a confirmation
    tmpl = "[§3c CONFIRMED 2026-__-__ — read docs/66 §2]"
    g = ac.gates_from_text(grant + "\n" + tmpl + "\n")
    assert g["licence_granted"] and not g["confirmed"]
    # a fully dated line IS
    done = "[§3c CONFIRMED 2026-09-01 — the grant stands]"
    g = ac.gates_from_text(grant + "\n" + done + "\n")
    assert g["licence_granted"] and g["confirmed"]
    assert not ac.gates_from_text("no lines here")["licence_granted"]
    # and the real docs/59 is internally consistent with GRANTED
    with io.open(ac.DOCS59, encoding="utf-8") as fh:
        assert ac.gates_from_text(fh.read())["licence_granted"]


# ---------------------------------------------------------------------------
# S2/S3/S4 -- selection rule and variational floor on synthetic cells
# ---------------------------------------------------------------------------

def test_s2_tie_within_1mev_picks_smaller_seed(fixdir, monkeypatch):
    # m030 is the raw minimum; m010 sits 4e-5 Ry (= 0.544 meV) above it,
    # inside the 1 meV tie window -> the registered tie-break selects m010.
    _mk_cell(fixdir, "Ru", "s0_OH", "u000", -100.00000000,
             [("sp2m010", -100.00996000, 0.5),
              ("sp2m030", -100.01000000, 1.5),
              ("sp2m050", -100.00500000, 2.5)], monkeypatch)
    cell = ac.build_cell("Ru", "s0_OH", "u000")
    sel = cell["selection"]
    assert sel["status"] == "FINAL"
    assert sel["winner"] == "s0_OH__u000__sp2m010"
    assert sel["seed"] == 0.10
    assert sel["tie_break_applied"] is True
    assert sel["energy_ry"] == -100.00996000     # the winner's own row travels
    assert sel["totmag"] == 0.5


def test_s3_floor_equality_passes(fixdir, monkeypatch):
    # 'must be <= 0' with EQUALITY PASSING: dE == 0 is admitted, not rejected
    _mk_cell(fixdir, "Ru", "s0_OH", "u000", -100.00000000,
             [("sp2m010", -100.00000000, 0.3),
              ("sp2m030", -100.00100000, 1.5),
              ("sp2m050", -100.00200000, 2.5)], monkeypatch)
    cell = ac.build_cell("Ru", "s0_OH", "u000")
    eq = _cand(cell, "sp2m010")
    assert eq["status"] == "ADMITTED"
    assert eq["dE_vs_incumbent_meV"] == 0.0
    assert cell["selection"]["winner"] == "s0_OH__u000__sp2m050"


def test_s4_floor_plus_point1_mev_rejected(fixdir, monkeypatch):
    # +0.1 meV above the incumbent: a search failure, rejected, not banked --
    # and the rejection is recorded with its energy and delta
    _mk_cell(fixdir, "Ru", "s0_OH", "u000", -100.00000000,
             [("sp2m010", -99.99999265, 0.3),
              ("sp2m030", -100.00100000, 1.5),
              ("sp2m050", -100.00200000, 2.5)], monkeypatch)
    cell = ac.build_cell("Ru", "s0_OH", "u000")
    rej = _cand(cell, "sp2m010")
    assert rej["status"].startswith("REJECT-FLOOR")
    assert abs(rej["dE_vs_incumbent_meV"] - 0.1) < 0.01
    assert "energy_ry" in rej                    # recorded, never banked
    sel = cell["selection"]
    assert sel["winner"] == "s0_OH__u000__sp2m050"
    assert sel["status"] == "FINAL"


def test_s4b_all_rejected_resolves_to_incumbent(fixdir, monkeypatch):
    # every seed above the floor -> the row EXISTS and equals the banked
    # nspin = 1 row: EQUALISED-BY-SELECTION(nspin=1) with the rejection record
    _mk_cell(fixdir, "Ru", "s0_OH", "u000", -100.00000000,
             [("sp2m010", -99.99999265, 0.3),
              ("sp2m030", -99.99990000, 1.5),
              ("sp2m050", -99.99980000, 2.5)], monkeypatch)
    cell = ac.build_cell("Ru", "s0_OH", "u000")
    assert all(c["status"].startswith("REJECT-FLOOR")
               for c in cell["candidates"])
    sel = cell["selection"]
    assert sel["winner"] == "incumbent"
    assert sel["resolution"] == "EQUALISED-BY-SELECTION(nspin=1)"
    assert sel["energy_ry"] == -100.00000000


# ---------------------------------------------------------------------------
# S5 -- the Ti fifth candidate (Rider 2) in a synthetic full-grid pool
# ---------------------------------------------------------------------------

def test_s5_ti_fifth_candidate_in_pool(fixdir, monkeypatch):
    _mk_cell(fixdir, "Ti", "s0_OOH", "u900", -1298.15918570,
             [("sp2m010", -1298.16000000, 1.0),
              ("sp2m030", -1298.16500000, 1.1),
              ("sp2m050", -1298.16800000, 1.2),
              ("sp2null", ac.RIDER2_E_RY, 1.04)], monkeypatch)
    cell = ac.build_cell("Ti", "s0_OOH", "u900")
    assert len(cell["candidates"]) == 4          # three seeds + the named row
    rider = [c for c in cell["candidates"] if "Rider 2" in c["kind"]][0]
    assert rider["status"] == "ADMITTED"
    sel = cell["selection"]
    assert sel["status"] == "FINAL"
    assert sel["winner"] == "s0_OOH__u900__sp2null"
    assert sel["seed"] == 0.0
    assert sel["energy_ry"] == ac.RIDER2_E_RY


# ---------------------------------------------------------------------------
# S6 -- an unconverged .out is refused
# ---------------------------------------------------------------------------

def test_s6_unconverged_out_refused(fixdir, monkeypatch):
    _mk_cell(fixdir, "Ru", "s0_OH", "u000", -100.00000000,
             [("sp2m010", "UNCONVERGED", None),
              ("sp2m030", -100.00100000, 1.5),
              ("sp2m050", -100.00200000, 2.5)], monkeypatch)
    cell = ac.build_cell("Ru", "s0_OH", "u000")
    bad = _cand(cell, "sp2m010")
    assert bad["status"] == "UNCONVERGED"
    assert "energy_ry" not in bad                # no energy enters the pool
    sel = cell["selection"]
    assert sel["winner"] == "s0_OH__u000__sp2m050"
    assert sel["status"] == "FINAL"              # a terminal .out, not pending


# ---------------------------------------------------------------------------
# S7 -- a literal 0.0 seed is separately fatal outside the whitelist
# ---------------------------------------------------------------------------

def test_s7_zero_seed_fatal_outside_whitelist(fixdir, monkeypatch):
    # (a) a __sp2null stem anywhere but the two whitelisted controls
    _mk_cell(fixdir, "Ru", "s0_OH", "u000", -100.00000000,
             [("sp2null", -100.00100000, 0.0)], monkeypatch)
    with pytest.raises(SystemExit) as e:
        ac.build_cell("Ru", "s0_OH", "u000")
    assert "whitelisted" in str(e.value)


def test_s7b_all_zero_seed_block_on_grid_stem_fatal(fixdir, monkeypatch):
    # (b) a grid stem whose deck carries an all-zero seed block
    _mk_cell(fixdir, "Ru", "s0_OH", "u000", -100.00000000,
             [("sp2m010", -100.00100000, 0.3)], monkeypatch)
    bad = os.path.join(fixdir, "spin", "Ru", "s0_OH__u000__sp2m010.in")
    _w(bad, _deck("Ru", seed=0.0))               # writes 0.00 on every index
    with pytest.raises(SystemExit) as e:
        ac.build_cell("Ru", "s0_OH", "u000")
    assert "CEN-d" in str(e.value)


def test_s8_sidecar_classes_tolerated_stray_class_fatal(fixdir, monkeypatch):
    # 2026-09-01: the wave-1 drain leaves three sidecar classes beside the
    # evidence -- the A6.5(1) Loewdin artifact, the runner's projwfc.in, and a
    # preserved failed attempt (.out.<tag>_YYYY-MM-DD). CEN-d tolerates them by
    # CLASS and still dies on anything else.
    _mk_cell(fixdir, "Ru", "s0_OH", "u000", -100.00000000,
             [("sp2m010", -100.00100000, 0.3)], monkeypatch)
    d = os.path.join(fixdir, "spin", "Ru")
    for side in ("s0_OH__u000__sp2m010.lowdin.txt",
                 "s0_OH__u000__sp2m010.projwfc.in",
                 "s0_OH__u000__sp2m010.out.a171_2026-08-31"):
        _w(os.path.join(d, side), "sidecar\n")
    found = ac.scan_spin_tree()
    assert found[("Ru", "s0_OH", "u000")] == ["s0_OH__u000__sp2m010"]
    # an attempt file whose tag lacks the date is NOT the registered class
    _w(os.path.join(d, "s0_OH__u000__sp2m010.out.attempt1"), "x\n")
    with pytest.raises(SystemExit) as e:
        ac.scan_spin_tree()
    assert "unregistered file class" in str(e.value)
    os.remove(os.path.join(d, "s0_OH__u000__sp2m010.out.attempt1"))
    # a genuinely unregistered class is fatal
    _w(os.path.join(d, "s0_OH__u000__sp2m010.csv"), "x\n")
    with pytest.raises(SystemExit) as e:
        ac.scan_spin_tree()
    assert "unregistered file class" in str(e.value)

