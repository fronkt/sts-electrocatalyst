"""Negative controls retain ANY-atom rejection while run-level scoring uses ALL."""
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

CI = Path(__file__).resolve().parents[2] / ".github" / "ci"


def load(name):
    spec = importlib.util.spec_from_file_location("quantifier_" + name, CI / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("any_verdict, status, verdict", [
    (True, "MEASURED", False), (None, "NOT MEASURED", None),
])
def test_qe_any_atom_rejects_despite_false_all_atoms(any_verdict, status, verdict):
    module = load("run_controls")
    keys = ("positive_9_9", "negative_qe_0_11", "partition_20_20", "tag_agreement_20_20", "two_witness_n_n")
    gates = {key: module.Gate(key, key, "test") for key in keys}
    absent = ["runs/positive%d/s0_O.out" % i for i in range(9)]
    present = ["runs/negative%d/s0_O.out" % i for i in range(11)]
    rows = {path: {"locked_force_only": path in absent,
                   "locked_two_witness": path in absent,
                   "locked_any_atom_force_only": path in absent,
                   "nosym_in_deck": path in present, "n_adsorbate": 1}
            for path in absent + present}
    rows[present[0]]["locked_any_atom_force_only"] = any_verdict
    schema = {key: "/" + key for key in next(iter(rows.values()))}
    csv_rows = [{"path": path.removeprefix("runs/")} for path in absent + present]
    module.evaluate(gates, schema, rows, {"nosym_absent": absent, "nosym_present": present}, csv_rows)
    negative = gates["negative_qe_0_11"]
    assert negative.status == status
    assert negative.verdict is verdict
    assert "ANY adsorbate atom" in negative.detail
    assert gates["positive_9_9"].green
    assert gates["two_witness_n_n"].green


@pytest.mark.parametrize("any_verdict, status", [(True, "MEASURED"), (None, "NOT MEASURED")])
def test_oc20_any_atom_rejects_despite_false_all_atoms(tmp_path, monkeypatch, any_verdict, status):
    module = load("run_oc20")
    names = ["random%d.extxyz.xz" % i for i in range(500)]
    records = [{"path": name, "locked_force_only": False,
                "locked_any_atom_force_only": False, "per_step_exact_zero_count": 0}
               for name in names]
    records[0]["locked_any_atom_force_only"] = any_verdict
    config = {"cli": {"oc20_cmd": "fake --sample {sample_dir}"},
              "schema": {"runs_array": "/runs", "path": "/path",
                         "locked_force_only": "/locked_force_only",
                         "locked_any_atom_force_only": "/locked_any_atom_force_only",
                         "per_step_exact_zero_count": "/per_step_exact_zero_count"}}
    monkeypatch.setenv("S1_OC20_MECHANISM", "self-hosted")
    monkeypatch.setenv("S1_OC20_SAMPLE_DIR", str(tmp_path))
    monkeypatch.setattr(module, "read_sums", lambda path: {name: "hash" for name in names})
    monkeypatch.setattr(module, "verify_sample", lambda directory, want: ([], []))
    monkeypatch.setattr(module, "load_toml", lambda path: config)
    monkeypatch.setattr(module.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(
        returncode=0, stdout=json.dumps({"runs": records}), stderr=""))
    output = tmp_path / "oc20.json"
    monkeypatch.setattr(sys, "argv", ["run_oc20.py", "--out-json", str(output)])
    assert module.main() != 0
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["status"] == status
    assert "ANY adsorbate atom" in result["detail"]
    if any_verdict is True:
        assert result["n_locked"] == 1
        assert result["locked_rate_percent"] == 0.2
        assert result["green"] is False
