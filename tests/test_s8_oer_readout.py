"""Offline checks for the S8 electrode readout (src/echem/s8_oer_readout.py): endpoints recovered from synthetic
campaigns (src/echem/s8_oer_synthetic.py) and hand-built curves, the refusals on bad input, the lock-rule
completeness logic, the K1/K2/IrO2 classes, the blinded mode, and the frozen predictions against the freeze document.
No bench file is needed. The synthetic generator shares the readout's iR export convention, so these tests cannot
check that convention; the bench check recorded with --ir-hw-verified does."""
import csv
import json
import math
import re
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/echem"))
import s8_oer_readout as ro  # noqa: E402
import s8_oer_synthetic as syn  # noqa: E402

FREEZE = ROOT / "docs/research/s8-stage1-freeze-proposal-2026-10-07.md"
LOCK = "2026-10-31"
VERIFIED = "synthetic: the generator exports Ewe without the live share"
I10 = 10e-3 * math.pi * 0.25 ** 2          # A at 10 mA cm-2 on a 5.00 mm disk


@pytest.fixture(scope="module")
def campaign(tmp_path_factory):
    d = tmp_path_factory.mktemp("s8syn")
    return d, syn.make_campaign(str(d))


def readout(manifest, lock=LOCK, key=True, campaign_dir=None, verified=VERIFIED):
    d = campaign_dir or Path(manifest).parent
    return ro._clean(ro.readout(str(manifest), lock, str(d / "key.csv") if key else None, verified))


@pytest.fixture(scope="module")
def keyed(campaign):
    d, truth = campaign
    return readout(d / "manifest.csv"), truth


def variant(campaign, tmp_path, edit):
    """Copy the synthetic manifest beside the original files with edit(rows) applied; return its path."""
    d, _ = campaign
    lines = (d / "manifest.csv").read_text(encoding="utf-8").splitlines()
    rows = list(csv.DictReader(lines[1:]))
    rows = edit(rows) or rows
    out = d / f"manifest_{tmp_path.name}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        f.write(lines[0] + "\n")
        w = csv.DictWriter(f, fieldnames=ro.MANIFEST_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return out


def row(rows, run_id):
    return next(r for r in rows if r["run_id"] == run_id)


def curve_from(cols, **extra):
    c = {"t": cols["time/s"], "E": cols["Ewe/V"], "I": cols["I/mA"] / 1e3, "cycle": None, "control": None,
         "ns": None, "rows_dropped": 0}
    c.update(extra)
    return c


def run_for(day, R_u, cycle=None):
    return {"offset": syn.OFFSETS[day], "R_u": R_u, "ir_hw": syn.IR_HW[day], "area": ro.AREA_CM2, "cycle": cycle}


# ------------------------------------------------------------------------------------------------ endpoints
def test_area_is_the_5mm_disk_face():
    assert ro.AREA_CM2 == pytest.approx(0.19635, abs=1e-5)


def test_eta10_recovers_truth_with_the_registered_10pct_residual(keyed):
    res, truth = keyed
    for disk, eta in truth["disks"].items():
        expected = eta + (1 - ro.IR_TOTAL) * I10 * truth["R_u"][disk]
        assert res["disks"][disk]["eta_10_V"] == pytest.approx(expected, abs=3e-4), disk


def test_tafel_cdl_and_drift_recover_truth(keyed):
    res, truth = keyed
    for disk, d in res["disks"].items():
        p = syn.TRUTH[truth["key"][disk[0]]]
        assert d["tafel_mV_dec"] == pytest.approx(p["b"] * 1e3, abs=1.0), disk
        assert d["roughness_factor"] == pytest.approx(p["cdl"] / (ro.CS_F_CM2 * ro.AREA_CM2), rel=0.02), disk
        if disk.endswith("1"):
            assert d["drift_mV_h"] == pytest.approx(syn.DRIFT_TRUE_MV_H, abs=0.05), disk


def test_reader_handles_the_three_export_styles(campaign):
    d, _ = campaign
    raw = (d / "files/d2_A2_lsv.mpt").read_bytes().decode("latin-1")
    assert "<I>/mA" in raw and "\t0,0" in raw                  # EC-Lab sweep header, comma decimals
    for name in ("d1_A1_lsv.mpt", "d2_A2_lsv.mpt", "d3_A3_lsv.csv"):
        c = ro.read_curve(d / "files" / name)
        assert np.isfinite(c["E"]).all() and c["rows_dropped"] == 0
        assert 1e-3 < c["I"].max() < 0.01                       # A, not mA: 30 mA cm-2 on 0.196 cm2 is 5.9 mA


def test_empty_cells_are_dropped_and_counted_and_many_refused(campaign, tmp_path):
    d, _ = campaign
    lines = (d / "files/d1_B1_lsv.mpt").read_text(encoding="latin-1").splitlines()
    cells = lines[500].split("\t")
    cells[3] = ""
    one = tmp_path / "one.mpt"
    one.write_text("\n".join(lines[:500] + ["\t".join(cells)] + lines[501:]), encoding="latin-1")
    c = ro.read_curve(one)
    assert c["rows_dropped"] == 1 and np.isfinite(c["I"]).all()
    for col in (3, 4):                                         # the current, then the optional cycle column
        blanked = [x.split("\t") for x in lines[4:]]
        for k, cells in enumerate(blanked):
            if k % 10 == 0:
                cells[col] = ""
        many = tmp_path / f"many{col}.mpt"
        many.write_text("\n".join(lines[:4] + ["\t".join(c) for c in blanked]), encoding="latin-1")
        with pytest.raises(ro.InputError):
            ro.read_curve(many)


def test_instrument_ir_share_is_not_applied_twice():
    rng = np.random.default_rng(1)
    p, eta10, R_u = syn.TRUTH["Cu8"], 0.400, 6.0
    etas = [ro.lsv_endpoints(curve_from(syn.lsv(p, eta10, day, R_u, rng)), run_for(day, R_u))["eta_10_V"]
            for day in (0, 2)]                                   # instrument share 0 and 0.85
    expected = eta10 + (1 - ro.IR_TOTAL) * I10 * R_u
    assert etas == pytest.approx([expected, expected], abs=2e-4)


def test_last_crossing_ignores_a_redox_peak_above_the_target():
    rng = np.random.default_rng(2)
    p = dict(syn.TRUTH["Ni31"], peak=1.5)                       # the peak crosses 1 mA cm-2 before OER does
    out = ro.lsv_endpoints(curve_from(syn.lsv(p, 0.36, 0, 0.0, rng)), run_for(0, 0.0))
    assert out["eta_1_V"] == pytest.approx(0.36 - p["b"], abs=5e-4)
    assert out["eta_1_first_V"] == pytest.approx(syn.PEAK_E - ro.E_EQ, abs=0.02)
    assert out["redox_flag_1"] and not out["redox_flag_10"]


def test_target_not_reached_or_not_sustained_gives_no_eta():
    E = np.linspace(1.3, 1.7, 401)
    run = {"offset": 0.0, "R_u": 0.0, "ir_hw": 0.0, "area": ro.AREA_CM2, "cycle": None}

    def endpoints(j):
        return ro.lsv_endpoints({"t": np.arange(len(E)), "E": E, "I": j * ro.AREA_CM2 / 1e3, "cycle": None,
                                 "control": None, "ns": None, "rows_dropped": 0}, run)
    short = endpoints(np.linspace(0, 5, len(E)))
    assert short["eta_10_V"] is None and short["eta_1_V"] is not None
    falls_back = endpoints(np.concatenate([np.linspace(0, 12, 300), np.linspace(12, 8, 101)]))
    assert falls_back["eta_10_V"] is None and falls_back["eta_10_first_V"] is not None


def test_sweep_selection_refuses_ambiguous_files():
    rng = np.random.default_rng(3)
    one = syn.lsv(syn.TRUTH["Cu8"], 0.40, 0, 4.0, rng)
    two = {k: np.concatenate([v, v[::-1], v]) for k, v in one.items()}   # up, down, up: two anodic sweeps
    with pytest.raises(ro.InputError):
        ro.lsv_endpoints(curve_from(two), run_for(0, 4.0))
    with pytest.raises(ro.InputError):                                    # a cycle asked of a file without cycles
        ro.lsv_endpoints(curve_from(one), run_for(0, 4.0, cycle=2))
    cyc = np.concatenate([np.ones(len(one["Ewe/V"]) * 2, int), 2 * np.ones(len(one["Ewe/V"]), int)])
    shifted = dict(two, **{"I/mA": np.concatenate([one["I/mA"], one["I/mA"][::-1], one["I/mA"]])})
    picked = ro.lsv_endpoints(curve_from(shifted, cycle=cyc), run_for(0, 4.0, cycle=2))
    assert picked["eta_10_V"] == pytest.approx(0.40 + 0.1 * I10 * 4.0, abs=3e-4)
    with pytest.raises(ro.InputError):                                    # linked techniques
        ro.lsv_endpoints(curve_from(one, ns=np.arange(len(one["Ewe/V"])) % 2), run_for(0, 4.0))
    with pytest.raises(ro.InputError):                                    # cathodic-positive export
        ro.lsv_endpoints(curve_from(dict(one, **{"I/mA": -one["I/mA"]})), run_for(0, 0.0))


def test_cdl_midpoint_outside_a_branch_gives_no_point():
    E = np.concatenate([np.linspace(0.95, 1.05, 100), np.linspace(1.05, 1.02, 30)])
    I = np.concatenate([np.full(100, 1e-6), np.full(30, -1e-6)])
    out = ro.cdl_point({"t": np.arange(len(E)), "E": E, "I": I, "cycle": None, "control": None, "ns": None},
                       {"cycle": None})
    assert out["cdl_half_delta_I_A"] is None and "central band" in out["cdl_note"]


# ------------------------------------------------------------------------------------------------ judging
def test_end_to_end_classes_and_criterion(keyed):
    res, _ = keyed
    json.dumps(res, allow_nan=False)
    assert res["synthetic"] is True and res["blinded"] is False and res["lock_is_registered"] is False
    assert res["criterion"]["pooled_over"] == list(ro.K_SET) and res["criterion"]["df"] == 10
    assert res["criterion"]["pooled_sd_V"] == pytest.approx(syn.DISK_SD, abs=3e-4)
    assert all(g["complete"] for g in res["alloys"].values())
    # invented truth: Cu8 0.400 sits between Ni31 0.360 and Fe25 0.450; Cu22 0.490 is last by > 0.024 V
    assert res["k1"] == {"class": "mixed_or_unresolved", "Cu8_vs": {"Ni31": "higher", "Fe25": "lower"}}
    assert res["k2"]["class"] == "supported"
    assert res["alloys"]["Ni31"]["iro2"]["class"] == "lower"
    assert res["alloys"]["Cu8"]["iro2"]["class"] == "not_distinguishable"
    assert res["alloys"]["Cu22"]["iro2"]["class"] == "higher"
    assert len(res["iro2_runs"]) == 3
    ex = res["exploratory"]
    assert ex["measured_order"] == ["Ni31", "Cu26", "Cu8", "Ni34", "Fe25", "Cu22"]
    assert ex["leader_distinguishable"] is False
    assert {k: v["n"] for k, v in ex["spearman"].items()} == {"A": 6, "B": 6, "C": 4, "C_ext": 5}


def test_ni34_spread_does_not_move_the_threshold(campaign, tmp_path):
    """Freeze §2: Ni34 changes no primary test. Swapping two Ni34 (code E) disk files changes nothing judged."""
    def edit(rows):
        row(rows, "d1_E1_lsv")["file"], row(rows, "d3_E3_lsv")["file"] = "files/d3_E3_lsv.csv", "files/d1_E1_lsv.mpt"
    base, swapped = readout(campaign[0] / "manifest.csv"), readout(variant(campaign, tmp_path, edit))
    assert swapped["criterion"]["threshold_V"] == base["criterion"]["threshold_V"]
    assert (swapped["k1"], swapped["k2"]) == (base["k1"], base["k2"])


def test_blinded_readout_has_no_identity_dependent_result(campaign):
    d, _ = campaign
    res = readout(d / "manifest.csv", key=False)
    assert res["blinded"] and res["k1"] is None and res["k2"] is None and res["exploratory"] is None
    assert "alloys" not in res and sorted(res["codes"]) == list("ABCDEF")
    assert all(g["complete"] and g["iro2"]["class"] for g in res["codes"].values())
    assert res["criterion"]["df"] == 12 and "provisional" in res["criterion"]["note"]


def test_lock_date_is_inclusive_and_excludes_later_days(campaign):
    d, _ = campaign
    res = readout(d / "manifest.csv", lock=syn.DAYS[1])
    assert all(g["n"] == 2 and not g["complete"] for g in res["alloys"].values())
    used_days = {r["day"] for r in res["runs"] if r["used"]}
    assert used_days == set(syn.DAYS[:2])
    assert res["criterion"]["threshold_V"] is None
    assert res["k1"]["class"] == res["k2"]["class"] == "not_evaluated" and res["exploratory"] is None


def test_day_without_iro2_does_not_count(campaign, tmp_path):
    def edit(rows):
        row(rows, "d3_IrO2_lsv")["status"] = "failed: reference electrode"
    res = readout(variant(campaign, tmp_path, edit), campaign_dir=campaign[0])
    assert res["days"][syn.DAYS[2]]["counted"] is False
    assert all(g["n"] == 2 and not g["complete"] for g in res["alloys"].values())


def test_incomplete_alloy_blocks_what_involves_it_and_its_numbers_stay_out(campaign, tmp_path):
    def edit(rows):
        row(rows, "d1_A1_lsv")["status"] = "failed: disk cracked"
    res = readout(variant(campaign, tmp_path, edit), campaign_dir=campaign[0])
    cu8 = res["alloys"]["Cu8"]
    assert not cu8["complete"] and cu8["n"] == 2
    assert cu8["eta_10_mean_V"] is None and cu8["eta_10_V"] is None and "iro2" not in cu8
    assert cu8["kept_not_reported"]["eta_10_mean_V"] is not None
    assert res["criterion"]["pooled_over"] == ["Ni31", "Fe25", "Cu26", "Cu22"] and res["criterion"]["df"] == 8
    assert res["k1"]["class"] == res["k2"]["class"] == "not_evaluated"
    assert res["alloys"]["Ni31"]["iro2"]["class"] == "lower"
    ex = res["exploratory"]
    assert "measured_order" not in ex
    assert ex["spearman"]["A"]["rho"] is None and ex["spearman"]["A"]["missing"] == ["Cu8"]
    assert ex["spearman"]["C"]["rho"] is not None and ex["spearman"]["C_ext"]["rho"] is not None


def test_a_spare_replaces_a_failed_disk(campaign, tmp_path):
    def edit(rows):
        row(rows, "d1_A1_lsv")["status"] = "failed: disk cracked"
        i = rows.index(row(rows, "d1_A1_lsv"))
        rows.insert(i + 1, dict(rows[i], run_id="d1_AS_lsv", sample="AS", status="ok", notes="spare for A1"))
    res = readout(variant(campaign, tmp_path, edit), campaign_dir=campaign[0])
    assert res["alloys"]["Cu8"]["complete"] and sorted(res["alloys"]["Cu8"]["disks"]) == ["A2", "A3", "AS"]


def test_primary_sweep_follows_days_not_row_order(campaign, tmp_path):
    def edit(rows):
        late = dict(row(rows, "d2_F2_lsv"), run_id="d2_A1_lsv_late", sample="A1")
        return [late] + [r for r in rows if r["day"] == syn.DAYS[1]] + \
            [r for r in rows if r["day"] != syn.DAYS[1]]
    res = readout(variant(campaign, tmp_path, edit), campaign_dir=campaign[0])
    base = readout(campaign[0] / "manifest.csv")
    assert res["disks"]["A1"]["primary_run"] == "d1_A1_lsv"
    assert res["disks"]["A1"]["repeat_runs"] == ["d2_A1_lsv_late"]
    assert res["disks"]["A1"]["eta_10_V"] == base["disks"]["A1"]["eta_10_V"]


def test_live_compensation_needs_a_recorded_check(campaign):
    with pytest.raises(ro.InputError, match="ir-hw-verified"):
        readout(campaign[0] / "manifest.csv", verified=None)
    readout(campaign[0] / "manifest.csv", lock=syn.DAYS[1], verified=None)   # days 1-2 had no live share


def test_classifiers_and_finite_inputs():
    t = 0.25                                                       # exact in binary, so the boundary is tested
    assert ro.compare(0.5, 0.75, t) == "not_distinguishable"
    assert ro.compare(0.5, 0.75 + 2 ** -10, t) == "lower" and ro.compare(0.75 + 2 ** -10, 0.5, t) == "higher"
    for bad in (math.nan, None):
        with pytest.raises(ro.InputError):
            ro.compare(0.5, bad, t)
    with pytest.raises(ro.InputError):
        ro.pooled_sd([[0.4, math.nan, 0.41]])
    base = {"Ni31": 0.45, "Fe25": 0.46}
    assert ro.classify_k1(dict(base, Cu8=0.40), 0.02)["class"] == "B-consistent"
    assert ro.classify_k1(dict(base, Cu8=0.50), 0.02)["class"] == "A-consistent"
    assert ro.classify_k1(dict(base, Cu8=0.44), 0.02)["class"] == "mixed_or_unresolved"
    k = {"Cu8": 0.40, "Ni31": 0.41, "Fe25": 0.42, "Cu26": 0.43}
    assert ro.classify_k2(dict(k, Cu22=0.50), 0.02)["class"] == "supported"
    assert ro.classify_k2(dict(k, Cu22=0.44), 0.02)["class"] == "unresolved"
    assert ro.classify_k2(dict(k, Cu22=0.38), 0.02)["class"] == "contradicted"


def test_pooled_sd():
    sd, df = ro.pooled_sd([[1.0, 2.0, 3.0], [2.0, 4.0, 6.0], [5.0]])
    assert df == 4 and sd == pytest.approx(np.sqrt((2 * 1.0 + 2 * 4.0) / 4))


# ------------------------------------------------------------------------------------------------ inputs
def test_predictions_match_the_freeze_document():
    text = FREEZE.read_text(encoding="utf-8")
    short = {full: re.match(r"[A-Z][a-z]?\d+", full).group(0) for full in re.findall(
        r"^\| ((?:Cu|Ni|Fe)\d+\w*?) \|", text, re.M)}
    ab = re.findall(r"^\| (\w+) \| \**([\d.]+)\** \| \**([\d.]+)\** \[([\d.]+), ([\d.]+)\]", text, re.M)
    assert len(ab) == 6
    for full, a, b, lo, hi in ab:
        s = short[full]
        assert ro.PREDICTIONS["A"][s] == float(a) and ro.PREDICTIONS["B"][s] == float(b)
        assert ro.B_INTERVAL[s] == (float(lo), float(hi))
    c_part = text.split("**Arm C (final")[1].split("**Arm C extension")[0]
    ext_part = text.split("**Arm C extension")[1].split("Predicted orders")[0]
    for part, arm in ((c_part, "C"), (ext_part, "C_ext")):
        rows = {short[f]: float(v) for f, v in re.findall(r"^\| (\w+) \| ([\d.]+) \|", part, re.M)}
        assert rows == ro.PREDICTIONS[arm], arm


def test_key_reader_accepts_the_bench_format_and_refuses_a_bad_map(tmp_path):
    good = tmp_path / "key.csv"
    good.write_text("seed,x\ncode,alloy,composition_at_pct,contains_Cr\n"
                    + "".join(f"{c},{a},x,True\n" for c, a in zip("FEDCBA", ro.ALLOYS)), encoding="utf-8")
    assert ro.read_key(good)["F"] == "Cu8"
    bad = tmp_path / "bad.csv"
    bad.write_text("code,alloy\n" + "".join(f"{c},Cu8\n" for c in "ABCDEF"), encoding="utf-8")
    with pytest.raises(ro.InputError):
        ro.read_key(bad)


def test_ph_formula_and_day_normalization(campaign, tmp_path):
    def edit(rows):
        for r in rows:
            r["rhe_offset_V"], r["pH"] = "", "14"
        row(rows, "d1_A1_lsv")["day"] = syn.DAYS[0].replace("-", "")
        row(rows, "d1_A2_lsv" if any(r["run_id"] == "d1_A2_lsv" for r in rows) else "d1_B1_lsv")["status"] = "OK"
    recs, _ = ro.read_manifest(variant(campaign, tmp_path, edit))
    lsv = [r for r in recs if r["technique"] == "lsv"]
    assert all(r["offset_source"] == "pH formula" and r["offset"] == pytest.approx(0.098 + 0.059 * 14) for r in lsv)
    assert next(r for r in recs if r["run_id"] == "d1_A1_lsv")["day"] == syn.DAYS[0]
    assert next(r for r in recs if r["run_id"] == "d1_B1_lsv")["ok"] is True


@pytest.mark.parametrize("run_id,field,value", [
    ("d1_A1_lsv", "sample", "G1"), ("d1_A1_lsv", "ir_hw_pct", "95"), ("d1_A1_lsv", "ir_hw_pct", ""),
    ("d1_A1_lsv", "technique", "chrono"), ("d1_A1_lsv", "status", ""), ("d1_A1_lsv", "day", "Oct 26"),
    ("d1_IrO2_lsv", "area_cm2", ""), ("d1_A1_lsv", "rhe_offset_V", "-0.9260"), ("d1_A1_lsv", "rhe_offset_V", "0.9300"),
    ("d1_A1_lsv", "file", "")])
def test_manifest_refusals(campaign, tmp_path, run_id, field, value):
    def edit(rows):
        row(rows, run_id)[field] = value
    with pytest.raises(ro.InputError):
        ro.read_manifest(variant(campaign, tmp_path, edit))


def test_missing_offset_refused(campaign, tmp_path):
    def edit(rows):
        row(rows, "d1_A1_lsv")["rhe_offset_V"] = ""
    with pytest.raises(ro.InputError):
        ro.read_manifest(variant(campaign, tmp_path, edit))
