"""Setup-only diagnostic: source-derived QE branch signature and fail-closed launch."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest

from dft import hea_ieee_initialization_probe as probe
from test_hea_ieee_smearing_diagnostic import diagnostic as smearing_case
from test_hea_sensitivity_shell import batch as sensitivity_batch, original_sources
from test_hea_followup_shell import _pin_script
from test_hea_pilot_runner import ROOT, _shell_path, _write


# Minimal structural fixture of the QE 7.5 source branch, not a fabricated
# 'dry-run success' log. run_pwscf/punch/qexsd supply these exact identities.
SETUP_XML = """<qes:espresso xmlns:qes="http://www.quantum-espresso.org/ns/qes/qes-1.0">
<parallel_info><nprocs>128</nprocs><npool>8</npool></parallel_info>
<input><control_variables><calculation>scf</calculation>
<prefix>hc__leader_pull2.10__ortho__fragment</prefix>
<outdir>./tmp_hs__leader_pull2.10__ortho__smearing</outdir>
<nstep>0</nstep><max_seconds>480</max_seconds></control_variables></input>
<output><atomic_structure nat="75"/></output><exit_status>255</exit_status>
</qes:espresso>
"""
SETUP_STDOUT = """     Program PWSCF v.7.5 starts on 11Sep2026
     Writing config-init to output data dir ./tmp_hs__leader_pull2.10__ortho__smearing/hc__leader_pull2.10__ortho__fragment.save/ :
     JOB DONE.
"""


@pytest.fixture
def setup_case(smearing_case):
    case = smearing_case
    staged = case["runs"].parent
    directory = case["runs"] / probe.DIRECTORY
    directory.mkdir()
    pseudo = case["root"] / "live-pseudo"
    pseudo.mkdir()
    source = next(cp for cp in case["inventory"]["checkpoints"] if cp["source_job"] == probe.SOURCE_JOB)
    for entry in source["files"]:
        if entry["path"].lower().endswith(".upf"):
            (pseudo / entry["path"]).write_bytes((case["runs"] / source["dir"] / entry["path"]).read_bytes())
    for rel in (probe.MANIFEST, probe.MANIFEST + ".lines",
                "runs/" + probe.DIRECTORY + "/" + probe.JOB + ".in",
                "src/dft/hea_ieee_initialization_probe.py", "anvil/hea_ieee_initialization_rank.sh"):
        target = staged / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / rel).read_bytes())
    spec = json.loads((ROOT / probe.SPEC).read_text())
    spec["source_spec_sha256"] = hashlib.sha256((staged / probe.SOURCE_SPEC).read_bytes()).hexdigest()
    spec["source_checkpoints_sha256"] = hashlib.sha256((staged / probe.sources.INVENTORY).read_bytes()).hexdigest()
    spec_path = staged / probe.SPEC
    spec_path.parent.mkdir(parents=True)
    spec_path.write_bytes((json.dumps(spec) + "\n").encode("utf-8"))
    xml = case["root"] / "setup.xml"
    stdout = case["root"] / "setup.stdout"
    xml.write_bytes(SETUP_XML.encode("utf-8"))
    original = (case["runs"] / "hea/sensitivity_2026-09-09" / (probe.ORIGINAL_JOB + ".in")).read_text()
    species = original.split("ATOMIC_SPECIES\n", 1)[1].split("CELL_PARAMETERS", 1)[0]
    pp_blocks = []
    for index, line in enumerate(species.strip().splitlines(), 1):
        label, _, filename = line.split()
        element = "O" if label in ("O1", "O2") else label
        md5 = hashlib.md5((pseudo / filename).read_bytes()).hexdigest()
        pp_blocks.append(f"     PseudoPot. # {index} for {element} read from file:\n"
                         f"     {probe.frozen.PSEUDO_DIRECTORY}/{filename}\n     MD5 check sum: {md5}\n")
    # QE's Linux streams are LF bytes. Avoid Windows text-mode translation in
    # both the valid fixture and later corrupted copies of this evidence.
    stdout.write_bytes(SETUP_STDOUT.replace("     JOB DONE.", "\n".join(pp_blocks) + "     JOB DONE.").encode("utf-8"))
    assert b"\r" not in xml.read_bytes() and b"\r" not in stdout.read_bytes()
    pw = case["paths"]["PW"]
    _write(pw, r"""
        #!/bin/bash
        set -eu
        if [ "$MOCK_INVALID_RANK" = "$OMPI_COMM_WORLD_RANK" ]; then
          echo 'Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG' >&2
        fi
        [ "$OMPI_COMM_WORLD_RANK" = 0 ] || exit 0
        [ "$1" = -nk ] && [ "$2" = 8 ] && [ "$3" = -in ] || exit 92
        [ "$(grep -c '^  nstep = 0$' "$4")" = 1 ] || exit 93
        [ "$(grep -c '^  max_seconds = 480$' "$4")" = 1 ] || exit 94
        save=./tmp_hs__leader_pull2.10__ortho__smearing/hc__leader_pull2.10__ortho__fragment.save
        if [ "$MOCK_KEEP_OLD_XML" != yes ]; then cp "$MOCK_SETUP_XML" "$save/data-file-schema.xml"; fi
        if [ "$MOCK_MUTATE_CLONE" = yes ]; then echo 'unexpected density update' > "$save/charge-density.hdf5"; fi
        cat "$MOCK_SETUP_STDOUT"
        exit "$MOCK_SETUP_EXIT"
    """, executable=True)
    paths = dict(case["paths"], SPEC=spec_path, MANIFEST=staged / probe.MANIFEST,
                 GUARD=staged / "src/dft/hea_ieee_initialization_probe.py",
                 WRAPPER=staged / "anvil/hea_ieee_initialization_rank.sh")
    del paths["PROJECTION"]
    for name in ("70_hea_ieee_initialization.slurm", "71_submit_hea_ieee_initialization.sh"):
        script = case["scripts"] / name
        _pin_script(ROOT / "anvil" / name, script, paths)
        # Production has no path override: both shells require the exact original
        # path. Only this independent fixture maps that mount to its temp folder.
        text = script.read_text().replace("= /anvil/projects/x-che260157/pseudo ]",
                                          '= "' + _shell_path(pseudo) + '" ]')
        script.write_bytes(text.encode("utf-8"))
    env = dict(case["env"], MANIFEST=_shell_path(paths["MANIFEST"]),
               PSEUDO_DIR=_shell_path(pseudo),
               MOCK_SETUP_XML=_shell_path(xml), MOCK_SETUP_STDOUT=_shell_path(stdout),
               MOCK_SETUP_EXIT="0", MOCK_INVALID_RANK="none", MOCK_KEEP_OLD_XML="no", MOCK_MUTATE_CLONE="no")
    return dict(case, directory=directory, manifest=paths["MANIFEST"], paths=paths, env=env,
                setup_xml=xml, setup_stdout=stdout, pseudo=pseudo)


def run(case, submit=False, concurrency="1", **overrides):
    script = "71_submit_hea_ieee_initialization.sh" if submit else "70_hea_ieee_initialization.slurm"
    args = [_shell_path(case["scripts"] / script)]
    if submit:
        args += [_shell_path(case["manifest"]), concurrency]
    return subprocess.run([case["executable"], "-c", 'export PATH="$QE_PREFIX/bin:$PATH"; exec bash "$@"',
                           "mock-setup", *args], cwd=case["root"], env=dict(case["env"], **overrides),
                          text=True, capture_output=True, timeout=60,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)


def record(case):
    return json.loads((case["directory"] / (probe.JOB + ".diagnostic.json")).read_text())


def launches(case):
    path = case["root"] / "mpi.log"
    return path.read_text().splitlines() if path.exists() else []


def save(case):
    return case["directory"] / ("tmp_" + probe.ORIGINAL_JOB) / (probe.PREFIX + ".save")


def test_source_derived_signature_is_setup_only():
    assert probe.setup_signature(SETUP_STDOUT, SETUP_XML)["checkpoint_read_claim"] is False
    # Historical source XML is not sufficient: this run must reach exit_status 255.
    with pytest.raises(ValueError, match="exit_status"):
        probe.setup_signature(SETUP_STDOUT, SETUP_XML.replace("<exit_status>255", "<exit_status>0"))


@pytest.mark.parametrize("seconds", ["480", " 4.800000000000000E+002 ", "4.8D+2"])
def test_max_seconds_xml_numeric_serializations(seconds):
    xml = SETUP_XML.replace("<max_seconds>480", "<max_seconds>" + seconds)
    assert probe.setup_signature(SETUP_STDOUT, xml)["nstep"] == 0


@pytest.mark.parametrize("seconds", ["NaN", "Infinity", "480.1", "13200"])
def test_max_seconds_xml_drift_or_nonfinite_refused(seconds):
    with pytest.raises(ValueError, match="max_seconds"):
        probe.setup_signature(SETUP_STDOUT, SETUP_XML.replace("<max_seconds>480", "<max_seconds>" + seconds))


def test_clean_setup_never_accepts_endpoint_or_checkpoint_read(setup_case):
    original = original_sources(setup_case)
    result = run(setup_case)
    assert result.returncode == 0, result.stdout + result.stderr
    result = record(setup_case)
    assert result["diagnostic_status"] == "SETUP_ONLY_CLEAN"
    assert result["new_endpoint_status"] == "DIAGNOSTIC_ONLY"
    assert result["checkpoint_read_claim"] is False
    assert result["prior_flagged_run_reclassified"] is False
    assert result["rank_capture_complete"] is True
    assert len(result["live_pseudopotentials"]["files"]) == 6
    assert len(result["printed_pseudopotentials"]) == 7
    assert [row["element"] for row in result["printed_pseudopotentials"]] == ["Cr", "Cu", "Mn", "Ni", "O", "O", "H"]
    assert len(result["retained_files"]) == 27
    assert len(launches(setup_case)) == 1
    assert original_sources(setup_case) == original
    assert not (setup_case["directory"] / (probe.JOB + ".projwfc.in")).exists()
    assert not (setup_case["directory"] / (probe.JOB + ".qc.json")).exists()
    receipt = json.loads((setup_case["directory"] / (probe.JOB + ".clone_receipt.json")).read_text())
    assert receipt["source_job"] == probe.SOURCE_JOB
    for entry in receipt["files"]:
        if entry["path"] == "data-file-schema.xml":
            continue
        source = setup_case["runs"] / receipt["source"] / entry["path"]
        cloned = save(setup_case) / entry["path"]
        assert source.read_bytes() == cloned.read_bytes()
        assert not source.samefile(cloned)


@pytest.mark.parametrize("rank", ["0", "7"])
def test_ieee_invalid_is_attributed_but_never_reclassified(setup_case, rank):
    result = run(setup_case, MOCK_INVALID_RANK=rank)
    assert result.returncode == 16
    out = record(setup_case)
    assert out["diagnostic_status"] == "SETUP_INVALID_REPRODUCED"
    assert out["invalid_ranks"] == [int(rank)]
    assert out["new_endpoint_status"] == "DIAGNOSTIC_ONLY"
    assert "IEEE_INVALID_FLAG" in (setup_case["directory"] / (probe.JOB + ".out")).read_text()
    assert len(launches(setup_case)) == 1


@pytest.mark.parametrize("extra", ["iteration # 1", "! total energy = -1 Ry", "init_run : 1.0s CPU",
                                    "electrons : 1.0s CPU", "force_hub : 1.0s CPU",
                                    "The initial density is read from file", "Starting wfcs from file"])
def test_nstep_ignored_cannot_pass_diagnostic(extra):
    with pytest.raises(ValueError, match="post-setup/SCF"):
        probe.setup_signature(SETUP_STDOUT + extra + "\n", SETUP_XML)


@pytest.mark.parametrize("tag", ["band_structure", "total_energy", "forces"])
def test_endpoint_xml_cannot_pass_as_setup(tag):
    with pytest.raises(ValueError, match="computed endpoint"):
        probe.setup_signature(SETUP_STDOUT, SETUP_XML.replace("</output>", "<" + tag + "/></output>"))


@pytest.mark.parametrize("variable,value,reason", [
    ("MOCK_KEEP_OLD_XML", "yes", "exit_status"),
    ("MOCK_MUTATE_CLONE", "yes", "clone mutation"),
    ("MOCK_SETUP_EXIT", "255", "nonzero process exit"),
    ("MOCK_MISSING_RANK", "127", "incomplete rank capture")])
def test_incomplete_or_changed_diagnostic_is_failure(setup_case, variable, value, reason):
    result = run(setup_case, **{variable: value})
    assert result.returncode != 0
    out = record(setup_case)
    assert out["diagnostic_status"] == "OTHER_FAILURE"
    assert out["new_endpoint_status"] == "DIAGNOSTIC_ONLY"
    assert any(reason in error for error in out["evidence_errors"])
    assert len(launches(setup_case)) == 1


def test_job_done_without_config_init_is_not_branch_evidence(setup_case):
    setup_case["setup_stdout"].write_bytes(b"Program PWSCF v.7.5 starts\nJOB DONE.\n")
    assert run(setup_case).returncode != 0
    assert record(setup_case)["diagnostic_status"] == "OTHER_FAILURE"


def test_held_submission_is_single_ten_minute_no_requeue(setup_case):
    before = setup_case["manifest"].with_suffix(".txt.lines").read_bytes()
    result = run(setup_case, submit=True)
    assert result.returncode == 0, result.stdout + result.stderr
    args = (setup_case["root"] / "sbatch.log").read_text().splitlines()
    for flag in ("--hold", "--mem=237G", "--time=00:10:00", "--no-requeue", "--array=1-1%1"):
        assert args.count(flag) == 1
    assert args[args.index("-n") + 1] == "128"
    assert "21.333333" in result.stdout
    assert not (setup_case["root"] / "release.log").exists()
    assert setup_case["manifest"].with_suffix(".txt.lines").read_bytes() == before
    assert not launches(setup_case)


@pytest.mark.parametrize("variable", ["SPEC", "GUARD", "PW", "MPI", "WRAPPER", "MANIFEST"])
def test_byte_drift_is_refused_before_clone_or_launch(setup_case, variable):
    path = setup_case["paths"][variable]
    path.write_bytes(path.read_bytes() + b"\n")
    result = run(setup_case)
    assert result.returncode != 0
    assert not save(setup_case).parent.exists()
    assert not launches(setup_case)


def test_source_hash_identity_and_exact_two_control_changes(setup_case):
    ctx = probe.prepare(setup_case["runs"], setup_case["pseudo"])
    runtime = (setup_case["directory"] / (probe.JOB + ".run.in")).read_bytes()
    assert runtime == probe.render(ctx["original"])
    restored = runtime.replace(b"  nstep = 0\n", b"  nstep = 200\n").replace(
        b"  max_seconds = 480\n", b"  max_seconds = 13200\n")
    assert restored == ctx["original"]
    assert len(ctx["checkpoint"]["files"]) == 27
    with pytest.raises(ValueError, match="preexisting"):
        probe.prepare(setup_case["runs"], setup_case["pseudo"])


def test_changed_source_checkpoint_refused(setup_case):
    cp = next(cp for cp in setup_case["inventory"]["checkpoints"] if cp["source_job"] == probe.SOURCE_JOB)
    (setup_case["runs"] / cp["dir"] / "wfcup8.hdf5").write_bytes(b"drift")
    with pytest.raises(ValueError, match="source checkpoint"):
        probe.prepare(setup_case["runs"], setup_case["pseudo"])
    assert not save(setup_case).parent.exists()


@pytest.mark.parametrize("submit", [False, True])
def test_live_pseudopotential_drift_refused_before_clone_or_submission(setup_case, submit):
    original = original_sources(setup_case)
    live = setup_case["pseudo"] / "O.pbe-n-kjpaw_psl.0.1.UPF"
    live.write_bytes(live.read_bytes() + b"live-only corruption\n")
    result = run(setup_case, submit=submit)
    assert result.returncode != 0
    assert "live pseudopotential hash/size mismatch" in result.stdout + result.stderr
    assert not save(setup_case).parent.exists()
    assert not launches(setup_case)
    assert not (setup_case["root"] / "sbatch.log").exists()
    assert original_sources(setup_case) == original


def test_live_pseudopotential_missing_refused_before_clone(setup_case):
    (setup_case["pseudo"] / "O.pbe-n-kjpaw_psl.0.1.UPF").unlink()
    with pytest.raises(ValueError, match="required regular file absent"):
        probe.prepare(setup_case["runs"], setup_case["pseudo"])
    assert not save(setup_case).parent.exists()


def test_live_pseudopotential_changed_during_clone_refuses_runtime_input(setup_case, monkeypatch):
    real = probe.frozen._stream_hash
    changed = False
    def corrupt_live_during_copy(path):
        nonlocal changed
        result = real(path)
        if not changed and probe.DIRECTORY.split("/")[-1] in str(path):
            changed = True
            (setup_case["pseudo"] / "O.pbe-n-kjpaw_psl.0.1.UPF").write_bytes(b"live drift during copy")
        return result
    monkeypatch.setattr(probe.frozen, "_stream_hash", corrupt_live_during_copy)
    with pytest.raises(ValueError, match="live pseudopotential hash/size mismatch"):
        probe.prepare(setup_case["runs"], setup_case["pseudo"])
    assert changed and save(setup_case).is_dir()
    assert not (setup_case["directory"] / (probe.JOB + ".run.in")).exists()


def test_live_pseudopotential_postrun_drift_fails_final_audit(setup_case):
    assert run(setup_case).returncode == 0
    (setup_case["pseudo"] / "O.pbe-n-kjpaw_psl.0.1.UPF").write_bytes(b"live drift after setup")
    (setup_case["directory"] / (probe.JOB + ".diagnostic.json")).unlink()
    result = probe.summarize(setup_case["runs"], 0, setup_case["pseudo"])
    assert result["diagnostic_status"] == "OTHER_FAILURE"
    assert result["new_endpoint_status"] == "DIAGNOSTIC_ONLY"
    assert result["live_pseudopotentials"] is None
    assert any("live pseudopotential hash/size mismatch" in error for error in result["evidence_errors"])


@pytest.mark.parametrize("mutation", ["wrong_md5", "wrong_path", "duplicate_index", "missing_oxygen", "wrong_element"])
def test_printed_pseudopotential_evidence_is_complete_ordered_and_byte_bound(setup_case, mutation):
    path = setup_case["setup_stdout"]
    text = path.read_text()
    if mutation == "wrong_md5":
        live = setup_case["pseudo"] / "O.pbe-n-kjpaw_psl.0.1.UPF"
        text = text.replace(hashlib.md5(live.read_bytes()).hexdigest(), "0" * 32, 1)
    elif mutation == "wrong_path":
        text = text.replace("/anvil/projects/x-che260157/pseudo/", "/unapproved/pseudo/", 1)
    elif mutation == "duplicate_index":
        text = text.replace("PseudoPot. # 6 for O", "PseudoPot. # 5 for O")
    elif mutation == "wrong_element":
        text = text.replace("PseudoPot. # 6 for O", "PseudoPot. # 6 for Ni")
    else:
        start = text.index("     PseudoPot. # 6")
        end = text.index("     PseudoPot. # 7")
        text = text[:start] + text[end:]
    path.write_bytes(text.encode("utf-8"))
    assert b"\r" not in path.read_bytes()
    assert run(setup_case).returncode != 0
    result = record(setup_case)
    assert result["diagnostic_status"] == "OTHER_FAILURE"
    assert result["new_endpoint_status"] == "DIAGNOSTIC_ONLY"
    assert any("printed pseudopotential" in error for error in result["evidence_errors"])


def test_late_raw_stream_change_and_receipt_change_are_rejected(setup_case):
    assert run(setup_case).returncode == 0
    (setup_case["directory"] / (probe.JOB + ".rank_stderr/rank007.stderr")).write_bytes(b"IEEE_INVALID_FLAG\n")
    (setup_case["directory"] / (probe.JOB + ".diagnostic.json")).unlink()
    out = probe.summarize(setup_case["runs"], 0, setup_case["pseudo"])
    assert out["diagnostic_status"] == "OTHER_FAILURE"
    assert out["new_endpoint_status"] == "DIAGNOSTIC_ONLY"
    assert any("differs from raw streams" in error for error in out["evidence_errors"])


def test_no_overwrite_and_no_second_automatic_attempt(setup_case):
    assert run(setup_case).returncode == 0
    before = (setup_case["directory"] / (probe.JOB + ".out")).read_bytes()
    with pytest.raises(FileExistsError):
        probe.assemble(setup_case["runs"])
    assert run(setup_case).returncode != 0
    assert len(launches(setup_case)) == 1
    assert (setup_case["directory"] / (probe.JOB + ".out")).read_bytes() == before


@pytest.mark.parametrize("overrides", [{"NP": "64"}, {"SLURM_ARRAY_TASK_ID": "2"}])
def test_resource_scope_cannot_expand(setup_case, overrides):
    assert run(setup_case, **overrides).returncode != 0
    assert not launches(setup_case)


def test_frozen_repository_byte_pins():
    spec = json.loads((ROOT / probe.SPEC).read_text())
    for key, path in (("manifest_sha256", probe.MANIFEST), ("manifest_lines_sha256", probe.MANIFEST + ".lines"),
                      ("source_spec_sha256", probe.SOURCE_SPEC), ("source_checkpoints_sha256", probe.sources.INVENTORY),
                      ("input_sha256", "runs/" + probe.DIRECTORY + "/" + probe.JOB + ".in")):
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == spec[key]
