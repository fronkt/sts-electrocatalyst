"""Protocol identity, exact composition, and failure/resume tests without model loading."""
import copy
import json

import pytest

from scripts import screen_diagnostic as diagnostic


@pytest.fixture
def setup(tmp_path, monkeypatch):
    source = tmp_path / "source.json"
    source.write_text(json.dumps({"status": "complete", "model": "legacy-label", "rows": [
        {"formula": "Fe33Ni67", "elements": ["Fe", "Ni"], "fractions": [.3344, .6656]},
        {"formula": "Co40Ni60", "elements": ["Co", "Ni"], "fractions": [.4, .6]},
    ]}))
    model = tmp_path / "model"
    model.write_bytes(b"test-checkpoint")
    # Toy records test orchestration, not the independent evidence analyzer.
    import hea_oer.site_evidence
    monkeypatch.setattr(hea_oer.site_evidence, "analyze_site_evidence",
                        lambda row, corrections: {"toy_readout": True})
    return source, model, tmp_path / "result.json"


def manifest(setup, **kwargs):
    source, model, _ = setup
    return diagnostic.prepare(source, ["Fe33Ni67", "Co40Ni60"], model, **kwargs)


class Backend:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.site_records = {}
        self.seen = []

    def predict(self, comp):
        self.seen.append(comp)
        self.site_records[comp.formula()] = {"n_sites": self.kwargs["n_sites"] * len(self.kwargs["seeds"]), "desorbed": [],
            "per_site_records": [{"seed": s, "site_index": i}
                                 for s in self.kwargs["seeds"] for i in range(self.kwargs["n_sites"])]}
        return 1.4, 2.8, 4.2


def test_manifest_preserves_exact_fractions_and_weights(setup):
    m = manifest(setup)
    assert m["candidates"][0]["fractions"] == [.3344, .6656]
    assert m["model"]["historical_weight_identity_established"] is False
    assert m["work_estimate"]["adsorbate_relaxations_upper"] == 216
    assert m["work_estimate"]["clean_slab_relaxations"] == 6
    assert m["work_estimate"]["wall_time_estimate_seconds"] is None
    diagnostic.validate_manifest(json.loads(json.dumps(m)))


@pytest.mark.parametrize("kwargs", [{"seeds": ()}, {"seeds": (0, 0)}, {"seeds": (-1,)},
                                     {"seeds": (True,)}, {"n_sites": 0}, {"n_sites": 5},
                                     {"steps": 0}, {"fmax": float("nan")},
                                     {"fmax": -1}, {"mode": "validation"}])
def test_refuses_invalid_protocol(setup, kwargs):
    with pytest.raises(ValueError):
        manifest(setup, **kwargs)


def test_refuses_unknown_duplicate_and_noncomplete_sources(setup):
    source, model, _ = setup
    for formulas in (["absent"], ["Fe33Ni67", "Fe33Ni67"], []):
        with pytest.raises(ValueError):
            diagnostic.prepare(source, formulas, model)
    payload = json.loads(source.read_text())
    payload["status"] = "running"
    source.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="complete"):
        manifest(setup)


def test_refuses_unormalized_negative_and_duplicate_composition(setup):
    source, model, _ = setup
    original = json.loads(source.read_text())
    for fractions in ([.3, .6], [-.1, 1.1], [0, 1]):
        data = copy.deepcopy(original)
        data["rows"][0]["fractions"] = fractions
        source.write_text(json.dumps(data))
        with pytest.raises(ValueError):
            manifest(setup)
    data = copy.deepcopy(original)
    data["rows"][1].update(elements=["Ni", "Fe"], fractions=[.6656, .3344])
    source.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="duplicate"):
        manifest(setup)


def test_partial_resume_exact_inputs_and_no_rerun(setup):
    source, model, out = setup
    m = manifest(setup)
    instances = []
    def factory(**kw):
        backend = Backend(**kw); instances.append(backend); return backend
    first = diagnostic.run(m, model, out, max_candidates=1, backend_factory=factory)
    assert first["status"] == "partial"
    assert instances[0].seen[0].fractions == (.3344, .6656)
    assert instances[0].kwargs["seeds"] == (0, 1, 2)
    finished = diagnostic.run(m, model, out, resume=True, backend_factory=factory)
    assert finished["status"] == "complete"
    assert [len(x.seen) for x in instances] == [1, 1]
    assert finished["results"][0] == first["results"][0]
    assert diagnostic.run(m, model, out, resume=True, backend_factory=factory) == finished
    assert len(instances) == 2
    assert not out.with_name(out.name + ".lock").exists()


def test_failures_retained_in_denominator_and_not_retried(setup):
    _, model, out = setup
    m = manifest(setup)
    class Broken(Backend):
        def predict(self, comp):
            raise RuntimeError("model failed")
    result = diagnostic.run(m, model, out, backend_factory=Broken)
    assert result["status"] == "complete_with_errors"
    assert len(result["results"]) == 2
    assert all(r["status"] == "error" for r in result["results"])
    assert diagnostic.run(m, model, out, resume=True, backend_factory=Backend) == result
    assert not result["claims"]["ranking_validated"]


def test_analyzer_failure_retains_raw_row(setup, monkeypatch):
    _, model, out = setup
    import hea_oer.site_evidence
    def broken(*args, **kwargs):
        raise ValueError("invalid site evidence")
    monkeypatch.setattr(hea_oer.site_evidence, "analyze_site_evidence", broken)
    result = diagnostic.run(manifest(setup), model, out, backend_factory=Backend)
    assert result["results"][0]["status"] == "error"
    assert result["results"][0]["row"]["eta"] == pytest.approx(.17)


def test_identity_environment_and_existing_output_guards(setup):
    _, model, out = setup
    m = manifest(setup)
    tampered = copy.deepcopy(m); tampered["protocol"]["steps"] = 2
    with pytest.raises(ValueError, match="identity"):
        diagnostic.run(tampered, model, out, backend_factory=Backend)
    diagnostic.run(m, model, out, max_candidates=1, backend_factory=Backend)
    with pytest.raises(FileExistsError):
        diagnostic.run(m, model, out, backend_factory=Backend)
    with pytest.raises(ValueError, match="environment"):
        diagnostic.run(m, model, out, resume=True, threads=3, backend_factory=Backend)
    model.write_bytes(b"different-checkpoint")
    with pytest.raises(ValueError, match="model bytes"):
        diagnostic.run(m, model, out, resume=True, backend_factory=Backend)


def test_resume_detects_modified_results(setup):
    _, model, out = setup
    m = manifest(setup)
    diagnostic.run(m, model, out, max_candidates=1, backend_factory=Backend)
    payload = json.loads(out.read_text()); payload["results"][0]["status"] = "changed"
    out.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="result identity"):
        diagnostic.run(m, model, out, resume=True, backend_factory=Backend)


def test_implementation_drift_missing_hash_and_lock(setup, monkeypatch):
    _, model, out = setup
    m = manifest(setup)
    bad = copy.deepcopy(m); bad["implementation_sha256_lf"].pop(next(iter(bad["implementation_sha256_lf"])))
    bad["manifest_id"] = diagnostic.identity({k:v for k,v in bad.items() if k != "manifest_id"})
    with pytest.raises(ValueError, match="incomplete implementation"):
        diagnostic.run(bad, model, out, backend_factory=Backend)
    lock = out.with_name(out.name + ".lock"); lock.write_text("other-worker")
    with pytest.raises(FileExistsError):
        diagnostic.run(m, model, out, backend_factory=Backend)
    assert lock.read_text() == "other-worker"


def test_no_silent_overwrite_and_lf_hash(tmp_path):
    path = tmp_path / "out.json"
    diagnostic.write_json_new(path, {"a": 1})
    with pytest.raises(FileExistsError):
        diagnostic.write_json_new(path, {"a": 2})
    assert json.loads(path.read_text()) == {"a": 1}
    a, b = tmp_path / "a", tmp_path / "b"
    a.write_bytes(b"one\r\ntwo\r\n"); b.write_bytes(b"one\ntwo\n")
    assert diagnostic.sha256_file(a, normalize_lf=True) == diagnostic.sha256_file(b, normalize_lf=True)
    assert diagnostic.sha256_file(a) != diagnostic.sha256_file(b)


@pytest.mark.parametrize("status", ["evaluated", "error"])
def test_resume_final_checkpoint_repairs_running_status(setup, status):
    _, model, out = setup
    m = manifest(setup)
    diagnostic.run(m, model, out, backend_factory=Backend)
    payload = json.loads(out.read_text())
    payload["status"] = "running"
    payload["results"][-1]["status"] = status
    payload["results_sha256"] = diagnostic.identity(payload["results"])
    out.write_text(json.dumps(payload))
    result = diagnostic.run(m, model, out, resume=True, backend_factory=Backend)
    expected = "complete" if status == "evaluated" else "complete_with_errors"
    assert result["status"] == expected
    assert json.loads(out.read_text())["status"] == expected


def test_incomplete_actual_sampling_retains_error_evidence(setup):
    _, model, out = setup
    class Missing(Backend):
        def predict(self, comp):
            result = super().predict(comp)
            self.site_records[comp.formula()]["per_site_records"].pop()
            return result
    result = diagnostic.run(manifest(setup), model, out, backend_factory=Missing)
    assert result["results"][0]["status"] == "error"
    assert result["results"][0]["row"]["sampling_check"]["complete"] is False
    assert "coverage" in result["results"][0]["error"]["message"]


def test_exception_preserves_finite_partial_evidence(setup):
    _, model, out = setup
    class Partial(Backend):
        def predict(self, comp):
            self.partial_site_records = {comp.formula(): {"completed_sites": 1}}
            raise ValueError("later site failed")
    result = diagnostic.run(manifest(setup), model, out, backend_factory=Partial)
    assert result["results"][0]["partial_evidence"] == {"completed_sites": 1}
