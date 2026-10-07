"""Offline checks for the S8 arm-C fixed-geometry DFT+U package; never launch QE/Slurm."""
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import arm_c_build as build  # noqa: E402
import arm_c_readout as readout  # noqa: E402
import hea_deck as hd  # noqa: E402
import research_batch as rb  # noqa: E402

PACKAGE = ROOT / "results/arm_c_2026-10-07"
SPEC = json.loads((PACKAGE / "launch_spec.json").read_text(encoding="utf-8"))
PLAN = json.loads((PACKAGE / "site_plan.json").read_text(encoding="utf-8"))
SLURM = ROOT / "anvil/94_arm_c_batch.slurm"
ARM_B_P10 = {"Cu8Cr23Mn35Co34": 0.384, "Ni31Cr29Cu5Mn35": 0.473, "Fe25Co25Ni25Cr25": 0.554,
             "Cu26Ni9Cr31Co33": 0.502, "Cu22Fe30Co32Mn15": 0.831, "Ni34Fe6Cu29Co31": 0.739}


@pytest.fixture(scope="module")
def built():
    return build.build()


# ---------------------------------------------------------------- scope and selection
def test_build_reproduces_every_committed_file_byte_for_byte(built):
    assert len(built) == 70
    for relative, data in built.items():
        assert (ROOT / relative).read_bytes() == data, relative
        assert b"\r" not in data


def test_sites_are_the_approved_sixteen_with_arm_b_weights_and_p10():
    sites = build.selection()
    assert len(sites) == 16
    for formula, pairs in build.APPROVED_SUPPORTS.items():
        own = [s for s in sites if s["formula"] == formula]
        lo = [s for s in own if "support_lo" in s["roles"]]
        hi = [s for s in own if "support_hi" in s["roles"]]
        assert (lo[0]["seed"], lo[0]["site_index"], lo[0]["roles"]["support_lo"]["weight"]) == pairs[0]
        assert (hi[0]["seed"], hi[0]["site_index"], hi[0]["roles"]["support_hi"]["weight"]) == pairs[1]
        p10 = lo[0]["roles"]["support_lo"]["p10_V"]
        assert abs(p10 - ARM_B_P10[formula]) < 5e-4
        w_lo = readout.eval_fraction(pairs[0][2])
        w_hi = readout.eval_fraction(pairs[1][2])
        assert abs(w_lo + w_hi - 1) < 1e-12
        assert abs(w_lo * lo[0]["eta_mlip_V"] + w_hi * hi[0]["eta_mlip_V"] - p10) < 1e-12
    best = {(s["formula"], s["seed"], s["site_index"]) for s in sites if "best" in s["roles"]}
    assert best == {(f, *v) for f, v in build.APPROVED_BEST.items()}
    assert not any(s["formula"] == "Ni34Fe6Cu29Co31" and "best" in s["roles"] for s in sites)


def test_selection_refuses_a_census_that_no_longer_gives_the_approved_sites(monkeypatch):
    monkeypatch.setitem(build.APPROVED_SUPPORTS, "Cu8Cr23Mn35Co34", ((16, 2, "1/2"), (20, 2, "1/2")))
    with pytest.raises(ValueError, match="differ from the approved"):
        build.selection()


# ---------------------------------------------------------------- decks
def test_every_production_deck_is_the_census_structure_under_the_production_recipe():
    for site in PLAN["sites"]:
        geometries = build.census_geometries(site)["geometries"]
        for state in build.STATES:
            path = ROOT / site["states"][state]["deck"]
            text = path.read_text(encoding="utf-8")
            parsed = hd.parse_deck(text)
            geometry = geometries[state]
            assert parsed["symbols"] == geometry["symbols"]
            assert parsed["positions"] == [[float(x) for x in p] for p in geometry["positions_A"]]
            assert parsed["cell"] == [[float(x) for x in r] for r in geometry["cell_A"]]
            assert parsed["mesh"] == (4, 2, 1) and parsed["hubbard_card"] == "HUBBARD (atomic)"
            for line in ("  calculation = 'scf'", "  conv_thr = 1.0d-6", "  mixing_mode = 'local-TF'",
                         "  mixing_beta = 0.3", "  degauss = 0.01", "  nspin = 2", "  ecutwfc = 80.0"):
                assert line in text.split("\n")
            assert re.findall(r"(?m)^\s*prefix\s*=\s*'([^']+)'", text) == [state + "__atomic"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == site["states"][state]["deck_sha256"]


def test_probe_decks_change_exactly_one_registered_thing():
    site = next(s for s in PLAN["sites"] if (s["formula"], s["seed"], s["site_index"]) == build.PROBE_SOURCE)
    base = (ROOT / site["states"]["slab"]["deck"]).read_text(encoding="utf-8").split("\n")
    probe_dir = ROOT / "runs/hea/arm_c_2026-10-07/probe__Fe25Co25Ni25Cr25__s2_site0"
    expected = {"ndim16": ["+   mixing_ndim = 16"]}
    assert [v for v, _ in build.PROBE_VARIANTS] == ["ndim16", "hs"]
    assert not (probe_dir / "slab__atomic_cg.in").exists()
    for variant in ("ndim16", "hs"):
        lines = (probe_dir / ("slab__atomic_" + variant + ".in")).read_text(encoding="utf-8").split("\n")
        changed = [d for d in difflib.ndiff(base, lines) if d[:2] in ("- ", "+ ")]
        prefix = [d for d in changed if "prefix" in d]
        rest = [d for d in changed if "prefix" not in d]
        assert prefix == ["-   prefix = 'slab__atomic'", "+   prefix = 'slab__atomic_" + variant + "'"]
        if variant in expected:
            assert rest == expected[variant]
        else:
            assert rest and all("starting_magnetization" in d for d in rest)
            assert all(d.endswith("= 1.0") for d in rest if d.startswith("+"))


# ---------------------------------------------------------------- spec, manifests, runner, Slurm
def test_spec_pins_and_shape():
    assert SPEC["schema"] == "research-batch-2026-09-16" and SPEC["np"] == 128
    for relative, digest in SPEC["files"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, relative
    main, probe = SPEC["stages"]["arm_c_main"], SPEC["stages"]["arm_c_probe"]
    assert len(main["jobs"]) == 64 and len(probe["jobs"]) == 2
    for job in main["jobs"] + probe["jobs"]:
        assert (job["nk"], job["scf_seconds"], job["projection_seconds"], job["max_iterations"]) == (8, 8100, 600, 126)
    assert main["wall_minutes"] == probe["wall_minutes"] == 150
    launch = (64 + 2) * 150 * 128 // 60
    assert SPEC["allocation"]["this_launch_ceiling_cpu_su"] == launch == 21120
    assert SPEC["qe_binaries_sha256"] == build.QE_BINARIES
    assert launch + SPEC["allocation"]["reserved_for_rerun_round_cpu_su"] <= SPEC["allocation"]["approved_campaign_ceiling_cpu_su"] == 23680
    assert set(SPEC["pseudo_md5"]) == {hd.ELEMENTS[e]["pseudo"] for e in ("Co", "Cr", "Cu", "Fe", "Mn", "Ni", "O", "H")}


def test_unchanged_runner_accepts_both_stages():
    for stage in ("arm_c_main", "arm_c_probe"):
        group = rb.validate(SPEC, ROOT, stage)
        assert group["kind"] == "hea"
        text = (ROOT / group["manifest"]).read_text(encoding="utf-8")
        assert "# NP=128 NCONC=1" in text and "NOT LICENSED" not in text.upper()


def test_slurm_script_pins_the_spec_and_runner():
    text = SLURM.read_text(encoding="utf-8")
    assert "\r" not in text
    pins = re.findall(r'check_hash "\$(\w+)" ([0-9a-f]{64})', text)
    assert dict(pins) == {"SPEC": hashlib.sha256((PACKAGE / "launch_spec.json").read_bytes()).hexdigest(),
                          "RUNNER": hashlib.sha256((ROOT / "src/dft/research_batch.py").read_bytes()).hexdigest()}
    assert "case \"${STAGE:-}\" in arm_c_main|arm_c_probe)" in text
    assert "#SBATCH --partition=wholenode" in text and "#SBATCH --no-requeue" in text
    bash = shutil.which("bash")
    if bash:
        assert subprocess.run([bash, "-n", str(SLURM)]).returncode == 0


# ---------------------------------------------------------------- readout rules
def fake_site(formula, seed, index, roles, eta=None):
    return {"formula": formula, "seed": seed, "site_index": index, "roles": roles,
            "complete": eta is not None, "eta_dft_V": eta, "eta_mlip_V": 0.5}


def roles_for(formula):
    return {s["seed"]: s["roles"] for s in PLAN["sites"] if s["formula"] == formula}


def all_sites(etas):
    sites = []
    for s in PLAN["sites"]:
        sites.append(fake_site(s["formula"], s["seed"], s["site_index"], s["roles"], etas.get((s["formula"], s["seed"]))))
    return sites


def test_alloy_value_is_the_arm_b_weighted_mean_with_single_site_fallback():
    etas = {(s["formula"], s["seed"]): 0.4 + 0.01 * i for i, s in enumerate(PLAN["sites"])}
    values = readout.alloy_values(all_sites(etas))
    cu8 = values["Cu8Cr23Mn35Co34"]
    assert cu8["status"] == "TWO_SITE"
    assert abs(cu8["C_V"] - (0.5 * etas[("Cu8Cr23Mn35Co34", 16)] + 0.5 * etas[("Cu8Cr23Mn35Co34", 26)])) < 1e-12
    ni31 = values["Ni31Cr29Cu5Mn35"]
    assert abs(ni31["C_V"] - (0.3 * etas[("Ni31Cr29Cu5Mn35", 1)] + 0.7 * etas[("Ni31Cr29Cu5Mn35", 10)])) < 1e-12
    del etas[("Fe25Co25Ni25Cr25", 25)]
    values = readout.alloy_values(all_sites(etas))
    assert values["Fe25Co25Ni25Cr25"]["status"] == "SINGLE_SITE"
    assert values["Fe25Co25Ni25Cr25"]["C_V"] == etas[("Fe25Co25Ni25Cr25", 13)]
    del etas[("Fe25Co25Ni25Cr25", 13)]
    values = readout.alloy_values(all_sites(etas))
    assert values["Fe25Co25Ni25Cr25"]["status"] == "NO_VALUE" and values["Fe25Co25Ni25Cr25"]["C_V"] is None
    assert readout.predictions(values)["K1"] == "NOT_EVALUABLE_UNDER_ARM_C"


def test_k1_k2_and_ni34_nomination():
    def values(c):
        return {f: {"C_V": v} for f, v in c.items()}
    base = {"Cu8Cr23Mn35Co34": 0.40, "Ni31Cr29Cu5Mn35": 0.50, "Fe25Co25Ni25Cr25": 0.55,
            "Cu26Ni9Cr31Co33": 0.52, "Cu22Fe30Co32Mn15": 0.90, "Ni34Fe6Cu29Co31": 0.80}
    out = readout.predictions(values(base))
    assert out["K1"] == "CU8_MORE_ACTIVE_THAN_NI31_AND_FE25" and out["K2"] == "CU22_LAST"
    assert out["ni34_batch_2"] == "NOT_NOMINATED"
    out = readout.predictions(values(dict(base, **{"Cu8Cr23Mn35Co34": 0.60, "Ni34Fe6Cu29Co31": 0.45})))
    assert out["K1"] == "CU8_LESS_ACTIVE_THAN_NI31_AND_FE25" and out["ni34_batch_2"] == "NOMINATED"
    out = readout.predictions(values(dict(base, **{"Cu8Cr23Mn35Co34": 0.52, "Cu22Fe30Co32Mn15": 0.30})))
    assert out["K1"] == "MIXED" and out["K2"] == "CU22_NOT_LAST"


def write_fake(run_dir, job, energy_Ry=None, status="COMPLETE", reason=None, note=None, killed=False):
    run_dir.mkdir(parents=True, exist_ok=True)
    lines = ["     running on   128 processor cores"]
    if energy_Ry is not None:
        lines += ["     convergence has been achieved in  40 iterations",
                  f"!    total energy              =   {energy_Ry:.8f} Ry"]
    if note:
        lines.append(note)
    lines.append("   JOB DONE.")
    (run_dir / (job + ".out")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    receipt = {"status": status, "reason": reason}
    if status == "COMPLETE":
        receipt["scf"] = {"energy_Ry": energy_Ry, "iterations": 40}
    (run_dir / (job + ".qc.json")).write_text(json.dumps(receipt), encoding="utf-8")
    if killed:
        (run_dir / (job + ".KILLED")).write_text("SCF iteration ceiling\n", encoding="utf-8")


def test_acceptance_needs_receipt_and_parser_and_classifies_failures(tmp_path):
    write_fake(tmp_path, "ok", -7551.5)
    assert readout.accepted(tmp_path, "ok")["accepted"] is True
    write_fake(tmp_path, "ieee", None, status="REJECTED", reason="numerical failure marker",
               note="Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG")
    row = readout.accepted(tmp_path, "ieee")
    assert not row["accepted"] and readout.failure_class(row) == "IEEE"
    write_fake(tmp_path, "stall", None, status="REJECTED", reason="SCF iteration ceiling", killed=True)
    row = readout.accepted(tmp_path, "stall")
    assert not row["accepted"] and readout.failure_class(row) == "CEILING"
    write_fake(tmp_path, "odd", -7551.5, status="REJECTED", reason="projection failed or exceeded bound")
    row = readout.accepted(tmp_path, "odd")
    assert not row["accepted"] and readout.failure_class(row) == "OTHER"


def test_a_ceiling_stop_with_an_ieee_note_is_a_ceiling_stop_and_projection_ieee_counts(tmp_path):
    write_fake(tmp_path, "both", None, status="REJECTED", reason="SCF iteration ceiling", killed=True,
               note="Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG")
    assert readout.failure_class(readout.accepted(tmp_path, "both")) == "CEILING"
    write_fake(tmp_path, "proj", -7551.5, status="REJECTED", reason="projection failed or exceeded bound")
    (tmp_path / "proj.projwfc.out").write_text(
        "Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG\n", encoding="utf-8")
    assert readout.failure_class(readout.accepted(tmp_path, "proj")) == "IEEE"


def failing(formula, seed, roles, failures, order_dir=None):
    return {"formula": formula, "seed": seed, "site_index": 0, "roles": roles, "complete": not failures,
            "original_failures": failures, "dir": order_dir or f"hea/arm_c_2026-10-07/{formula}__s{seed}_site0"}


def test_rerun_selection_follows_the_registered_order_all_or_nothing():
    support = {"support_lo": {"weight": "1/2"}}
    best = {"best": {}}
    sites = [
        failing("Cu22Fe30Co32Mn15", 6, support, {"OH": "IEEE"}),
        failing("Cu8Cr23Mn35Co34", 16, support, {"slab": "CEILING", "OH": "IEEE", "O": "IEEE"}),
        failing("Fe25Co25Ni25Cr25", 13, support, {"slab": "CEILING"}),
        failing("Ni31Cr29Cu5Mn35", 10, support, {"OOH": "OTHER"}),
        failing("Cu8Cr23Mn35Co34", 20, best, {"OH": "IEEE"}),
        failing("Ni34Fe6Cu29Co31", 22, support, {"O": "IEEE", "OOH": "IEEE"}),
    ]
    chosen = readout.rerun_selection(sites, "ndim16", slots=6)
    picked = [(c["site_dir"].rsplit("/", 1)[-1], c["state"], c["recipe"], c["job"]) for c in chosen]
    assert picked == [
        ("Fe25Co25Ni25Cr25__s13_site0", "slab", "ndim16", "slab__atomic_ndim16"),   # tier 1, one failure
        ("Cu8Cr23Mn35Co34__s16_site0", "slab", "ndim16", "slab__atomic_ndim16"),    # tier 1, three failures
        ("Cu8Cr23Mn35Co34__s16_site0", "OH", "production", "OH__atomic"),
        ("Cu8Cr23Mn35Co34__s16_site0", "O", "production", "O__atomic"),
        ("Cu22Fe30Co32Mn15__s6_site0", "OH", "production", "OH__atomic"),           # tier 2
        # Ni34 (tier 3) needs two slots and only one is left; the tier-4 best site fits
        ("Cu8Cr23Mn35Co34__s20_site0", "OH", "production", "OH__atomic"),
    ]
    assert all(c["dir"].startswith(readout.RERUN_ROOT + "/") for c in chosen)
    # Without a probe recipe, ceiling stops are not repairable.
    no_recipe = readout.rerun_selection(sites, None, slots=6)
    assert [(c["site_dir"].rsplit("/", 1)[-1], c["state"]) for c in no_recipe] == [
        ("Cu22Fe30Co32Mn15__s6_site0", "OH"), ("Ni34Fe6Cu29Co31__s22_site0", "O"),
        ("Ni34Fe6Cu29Co31__s22_site0", "OOH"), ("Cu8Cr23Mn35Co34__s20_site0", "OH")]


def test_variant_transform_applies_to_any_production_deck():
    site = next(s for s in PLAN["sites"] if s["formula"] == "Cu22Fe30Co32Mn15")
    text = (ROOT / site["states"]["OH"]["deck"]).read_text(encoding="utf-8")
    for variant in ("ndim16", "hs"):
        out = build.variant_deck(text, variant, "OH__atomic_" + variant)
        changed = [d for d in difflib.ndiff(text.split("\n"), out.split("\n")) if d[:2] in ("- ", "+ ")]
        rest = [d for d in changed if "prefix" not in d]
        assert "+   prefix = 'OH__atomic_" + variant + "'" in changed
        assert rest == ["+   mixing_ndim = 16"] if variant == "ndim16" else all("starting_magnetization" in d for d in rest)
    with pytest.raises(ValueError):
        build.variant_deck(text, "cg", "OH__atomic_cg")


def test_quota_parser_reads_the_project_row():
    sys.path.insert(0, str(PACKAGE))
    import importlib.util
    spec = importlib.util.spec_from_file_location("arm_c_launch_ops", PACKAGE / "launch_ops.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    text = ("Type       Location             Size    Limit    Use   Files   Limit    Use\n"
            "home       x-fcai3            54.9MB   25.0GB   0.2%      -       -      -\n"
            "projects   x-che260157         2.5TB    5.0TB  51.0%   90.3K    1.0M   8.6%\n")
    assert abs(module.project_free_tb(text) - 2.5) < 1e-9
    assert module.project_free_tb("projects x-che260157 n/a n/a\n") is None
    assert module.ARRAYS["arm_c_probe"] == {"array": "1-2%2", "tasks": 2, "throttle": "2", "name": "arm-c-probe"}
