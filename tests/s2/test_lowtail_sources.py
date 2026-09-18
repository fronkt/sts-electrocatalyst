"""Acceptance registry and census extraction of the low-tail track (real banked files)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "s2" / "lowtail_dft"))

import lt_common  # noqa: E402
import lt_decisions  # noqa: E402
import lt_sources as src  # noqa: E402


def test_every_banked_output_is_classified_once_with_its_readout_status():
    reg = src.registry()
    outs = sorted(p for p in (ROOT / "runs/hea").rglob("*.out") if not p.name.endswith(".projwfc.out"))
    assert len(reg["entries"]) + len(reg["unidentified"]) == len(outs)
    assert reg["unidentified"] == []
    jobs = [e["job"] for e in reg["entries"]]
    assert len(jobs) == len(set(jobs))
    by = {e["job"]: e for e in reg["entries"]}
    # Known dispositions of record.
    assert by["hn__leader_builder__atomic__tight"]["status"] == "REJECTED"
    assert by["hs__leader_pull2.10__ortho__smearing"]["status"] == "REJECTED"
    assert by["hd__leader_builder__atomic__ieee_repro"]["status"] == "ACCEPTED"
    assert by["hi__leader_pull2.10__ortho__smearing_init"]["status"] == "NO_SCF"
    assert by["hc__leader_pull2.10__ortho__baseline"]["status"] == "REJECTED"
    for e in reg["entries"]:
        if e["status"] == "ACCEPTED":
            assert e["recorded_output_sha256"] == e["output_sha256"], e["job"]
            assert e["input"] is not None


def test_census_site_refuses_ambiguous_records(tmp_path):
    doc = json.loads((ROOT / "results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json").read_text(encoding="utf-8"))
    row = doc["results"][0]["row"]
    row["per_site_records"].append(dict(row["per_site_records"][4]))
    path = tmp_path / "dup.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(ValueError):
        src.census_site(path, 1, 0)
    doc["status"] = "incomplete"
    path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(ValueError):
        src.census_site(path, 0, 0)


def test_final_batch_counts_physical_outputs_and_retains_aliases():
    rows = src.final_entries()
    assert len(rows) == 22
    assert sum(e["status"] == "ACCEPTED" for e in rows) == 15
    assert sum(e["status"] == "KILLED" for e in rows) == 5
    assert sum(e["status"] == "REJECTED" for e in rows) == 2
    assert len({e["output"] for e in rows}) == 22
    assert sum(len(e["readout_aliases"]) for e in rows) == 4
    by_job = {e["job"]: e for e in rows}
    assert by_job["pilot_retained/Fe25Co25Ni25Cr25__s2_site0/O__atomic"]["status"] == "ACCEPTED"
    assert by_job["pilot_retained/Fe25Co25Ni25Cr25__s2_site0/O__ortho"]["status"] == "KILLED"
    assert by_job["pilot_retained/Ni31Cr29Cu5Mn35__s0_site0/O__atomic"]["status"] == "ACCEPTED"
    assert by_job["pilot_retained/Ni31Cr29Cu5Mn35__s0_site0/O__ortho"]["status"] == "ACCEPTED"
    for e in rows:
        assert len(e["output_sha256"]) == 64
        assert e["qc"]["sha256"] == lt_common.sha256_file(ROOT / e["qc"]["path"])


def test_operating_decisions_file_reproduces_from_sources():
    stored = lt_common.read_json(ROOT / "results/lowtail_dft_2026-09-16/operating_decisions.json")
    fresh = lt_decisions.build()
    assert stored["thresholds"] == fresh["thresholds"]
    th = fresh["thresholds"]
    assert th["lift_min_A"] == 0.5 and th["desorbed_min_A"] == 3.0 and th["magnetization_flag_muB"] == 0.5
    ax = fresh["axial_minima"]
    assert ax["clean_max_A"] < th["axial_break_A"] < ax["O_state_min_A"]
    assert len(ax["rows"]) == 4 and all(r["site_lift_z_A"] > th["lift_min_A"] for r in ax["rows"])


def test_axial_oxygen_agrees_with_the_endpoint_audit():
    audit = json.loads((ROOT / "results/site_census_2026-09-06/chemistry_2026-09-13/endpoint_audit.json").read_text(encoding="utf-8"))
    rows = {(r["formula"], r["seed"], r["site"]): r for r in lt_decisions.axial_minima()["rows"]}
    compared = 0
    for s in audit["sites"]:
        key = (s["formula"], s["seed"], s["site_index"])
        if s["tag"] == "mpa0" and key in rows:
            neighbors = s["geometry"]["O"]["binding_metal_lattice_O_neighbors"]
            grown = max(neighbors, key=lambda n: n["O_state_A"] - n["clean_A"])
            assert grown["index"] == rows[key]["axial_O_index"]
            assert grown["clean_A"] == pytest.approx(rows[key]["clean_A"], abs=1e-12)
            assert grown["O_state_A"] == pytest.approx(rows[key]["O_state_A"], abs=1e-12)
            compared += 1
    assert compared == 4
