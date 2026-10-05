"""pa_qe_adapter_v2 against real QE 7.5 output; no process, scheduler or QE execution.

Inputs are the actual control call of Slurm job 21034683 (72-atom Hubbard relax on 128 MPI
ranks), 19 real calculation='scf' Hubbard XML files with their decks and logs, two real
72-atom fresh-SCF logs, and the retained one-process H2 restart arms (tests/fixtures/qe75_real).
Nothing here is a synthetic XML: a validator that requires a tag real QE never writes fails
these tests, which is exactly what the synthetic fixture of the frozen adapter hid.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import types
import xml.etree.ElementTree as ET

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "src/dft"))
sys.path.insert(0, str(HERE))
import pa_qe_adapter_v2 as adapter
import qe75_real_fixtures as real_files
from qe75_real_fixtures import CATALYST, SERIAL, tag

ROOT = real_files.ROOT
SRC = ROOT / "src/dft/pa_qe_adapter_v2.py"
QE_SOURCE = ROOT / "results/pa_catalyst_trial_2026-10-03/qe_source"
REAL_UPF_READS = adapter._raw_upf_reads
REAL_PARALLEL = adapter._raw_parallel
PPROJ6 = sorted(row["fixture"].split("/", 1)[1][:-len(".xml.gz")] for row in real_files.manifest()
                if row["fixture"].startswith("pproj6/") and row["fixture"].endswith(".xml.gz"))


@pytest.fixture(scope="session")
def real(tmp_path_factory):
    return real_files.materialize(tmp_path_factory.mktemp("qe75_real"))


def control_xml(real):
    return ET.parse(str(real / "control/data-file-schema.xml")).getroot()


def control_deck_text(real):
    return (real / "control/input.in").read_text(encoding="utf-8")


def with_line(text, namelist, line):
    """The control deck with one explicit assignment inside a namelist (an existing key is replaced)."""
    marker = "&" + namelist + "\n"
    assert text.count(marker) == 1
    key = line.split("=", 1)[0].strip()
    existing = re.compile(r"(?m)^[ \t]*" + re.escape(key) + r"[ \t]*=.*$")
    if existing.search(text):
        return existing.sub("  " + line, text, count=1)
    return text.replace(marker, marker + "  " + line + "\n")


def input_side(text, old, new):
    """Edit only the <input> copy of a repeated element (QE repeats <dftU> under <output>)."""
    assert text.count(old) == 2, old
    return text.replace(old, new, 1)


def parsed_deck(tmp_path, text, name="variant.in"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return adapter.parse_deck(path)


# ---------------------------------------------------------------- the fixtures themselves

def test_every_fixture_decompresses_to_its_recorded_original(real):
    rows = real_files.manifest()
    assert len(rows) >= 90
    for row in rows:
        data = (real / row["fixture"][:-3]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row["sha256"] and len(data) == row["bytes"]
        source = ROOT / row["source"]
        if source.is_file():  # originals are left in place; when present they must still match
            assert hashlib.sha256(source.read_bytes()).hexdigest() == row["sha256"], row["source"]


def test_real_control_files_are_qe_7_5_and_carry_no_lda_plus_u(real):
    root = control_xml(real)
    assert root.find("general_info/creator").attrib == {"NAME": "PWSCF", "VERSION": "7.5"}
    names = {tag(node) for node in root.iter()}
    assert "lda_plus_u" not in names
    dftu = root.find("input/dft/dftU")
    assert dftu is not None and dftu.attrib == {"new_format": "true"}
    assert {tag(child) for child in dftu} == adapter.DFTU_REGISTERED_CHILDREN
    # The same holds for every real Hubbard file in the corpus (control + 19 scf).
    for path in real_files.real_xml_paths(real):
        text = path.read_text(encoding="utf-8")
        assert "lda_plus_u>" not in text.replace("lda_plus_u_kind>", ""), path.name


# ---------------------------------------------------------------- the control call, end to end

def test_real_control_call_is_accepted_end_to_end(real):
    args, kwargs = real_files.control_call(real, adapter)
    arm = adapter.read_qe_arm(*args, **kwargs)
    assert arm["raw_validated"] is True and arm["production_accepted"] is False
    assert len(arm["evaluations"]) == 3 and arm["scf_counts"] == [1, 2, 3]
    assert arm["optimizer_counts"] == [0, 1, 2] and arm["xml_exit_status"] == 255
    assert arm["first_conv_thr_Ry"] == 1e-6 and arm["parallel"] == CATALYST
    assert arm["runtime_parallel"]["elpa_subgroup"] == [4, 4]
    assert arm["proposal_geometry"] is not None
    assert adapter.require_expected_first_threshold(arm, kwargs["expected_settings"])
    assert len(arm["upf_reads"]) == 5 and all(row["retained_mirror_used"] for row in arm["upf_reads"])
    # Hubbard U: Co 3.32, Cr 3.70, Mn 3.90 eV came back out of the XML in Hartree.
    assert arm["input"]["settings"]["hubbard"]["rows"] == [["U", "Co-3d", "3.3200"], ["U", "Cr-3d", "3.7000"],
                                                           ["U", "Mn-3d", "3.9000"]]
    assert arm["xml_settings_identity"] == "3bd17094" + arm["xml_settings_identity"][8:]


def test_real_control_pins_equal_the_registered_upf_pins(real):
    spec = json.loads((ROOT / "results/pa_catalyst_trial_2026-10-03/launch_spec.json").read_text(encoding="utf-8"))
    registered = {Path(row["path"]).name: row["sha256"] for row in spec["upfs"]}
    pins, _ = real_files.pinned_control_upfs(real)
    assert pins == registered


def test_real_control_saved_optimizer_reads_as_the_third_evaluation(real):
    args, kwargs = real_files.control_call(real, adapter)
    arm = adapter.read_qe_arm(*args, **kwargs)
    last = arm["evaluations"][2]
    saved = adapter.read_bfgs(real / "control/slab_c5low__pa_boundary.bfgs", nat=72,
                              cell_bohr=last["geometry"]["cell"], evaluated=last)
    assert saved["dimension"] == 226 and saved["inactive_tail_max_abs"] == 0
    assert (saved["scf_count"], saved["bfgs_count"], saved["gdiis_count"]) == (3, 3, 0)


def test_real_control_expected_xml_strings_are_the_strings_in_the_real_xml(real, tmp_path):
    root = control_xml(real)
    deck = adapter.parse_deck(real / "control/input.in")
    expected = adapter.expected_xml_strings(deck)
    assert expected == {"calculation": "relax", "restart_mode": "from_scratch", "prefix": "slab_c5low__pa_boundary",
                        "mixing_mode": "local-TF", "ion_dynamics": "bfgs", "occupations": "smearing",
                        "functional": "PBE", "U_projection_type": "atomic"}
    for name, value in expected.items():
        found = [node for node in root.find("input").iter() if tag(node) == name]
        assert len(found) == 1 and (found[0].text or "").strip() == value, name


def test_every_compared_deck_string_has_a_qe_canonicalization_rule():
    for key in ("calculation", "restart_mode", "prefix", "disk_io", "verbosity", "mixing_mode", "diagonalization",
                "ion_dynamics", "occupations", "functional", "U_projection_type", "smearing"):
        assert key in adapter.QE75_XML_CANONICAL and adapter.QE75_XML_CANONICAL[key]["source"]
    with pytest.raises(adapter.AdapterError, match="no QE 7.5 XML canonicalization rule"):
        adapter._xml_canonical("startingwfc", "atomic+random")  # not an XML field: must never be compared silently


# QE writes these XML strings for deck strings that differ from them.  Each variant makes one
# of QE's own defaults explicit, so the real control XML is the XML QE writes for that deck too.
CANONICAL_VARIANTS = [
    ("electrons", "diagonalization = 'david'", "davidson"),
    ("control", "disk_io = 'default'", "low"),
    ("control", "verbosity = 'default'", "low"),
    ("system", "input_dft = 'pbe'", "PBE"),
    ("system", "input_dft = 'PBE'", "PBE"),
]


@pytest.mark.parametrize("namelist,line,xml_value", CANONICAL_VARIANTS)
def test_canonical_deck_strings_pass_against_the_real_control_xml(real, tmp_path, namelist, line, xml_value):
    deck = parsed_deck(tmp_path, with_line(control_deck_text(real), namelist.upper(), line))
    adapter._check_xml_input(control_xml(real), deck)
    assert xml_value in set(adapter.expected_xml_strings(deck).values()) | {"low", "PBE"}


@pytest.mark.parametrize("namelist,line", [
    ("electrons", "diagonalization = 'cg'"), ("electrons", "mixing_mode = 'plain'"),
    ("control", "disk_io = 'high'"), ("control", "verbosity = 'high'"), ("system", "input_dft = 'rpbe'"),
    ("ions", "ion_dynamics = 'damp'"),
])
def test_a_deck_string_that_differs_from_the_real_xml_is_still_refused(real, tmp_path, namelist, line):
    deck = parsed_deck(tmp_path, with_line(control_deck_text(real), namelist.upper(), line))
    with pytest.raises(adapter.AdapterError, match="source setting differs|functional differs"):
        adapter._check_xml_input(control_xml(real), deck)


def test_operational_fields_are_bound_to_the_deck_of_the_arm(real, tmp_path):
    root = control_xml(real)
    for old, new in (("<restart_mode>from_scratch</restart_mode>", "<restart_mode>restart</restart_mode>"),
                     ("<calculation>relax</calculation>", "<calculation>scf</calculation>"),
                     ("<prefix>slab_c5low__pa_boundary</prefix>", "<prefix>other</prefix>"),
                     ("<max_seconds>7080</max_seconds>", "<max_seconds>7000</max_seconds>")):
        text = (real / "control/data-file-schema.xml").read_text(encoding="utf-8")
        assert old in text
        changed = ET.fromstring(text.replace(old, new))
        with pytest.raises(adapter.AdapterError, match="source setting differs"):
            adapter._check_xml_input(changed, adapter.parse_deck(real / "control/input.in"))
    adapter._check_xml_input(root, adapter.parse_deck(real / "control/input.in"))


def test_an_xml_hubbard_element_real_qe_never_writes_is_refused(real):
    text = (real / "control/data-file-schema.xml").read_text(encoding="utf-8")
    old = "<lda_plus_u_kind>0</lda_plus_u_kind>"
    # The layout the frozen adapter's synthetic fixture invented.
    invented = ET.fromstring(input_side(text, old, "<lda_plus_u>true</lda_plus_u>" + old))
    with pytest.raises(adapter.AdapterError, match="unregistered XML Hubbard content: lda_plus_u"):
        adapter._check_xml_input(invented, adapter.parse_deck(real / "control/input.in"))
    extra = ET.fromstring(input_side(text, old, "<Hubbard_J0 specie=\"Co\" label=\"3d\">1.0</Hubbard_J0>" + old))
    with pytest.raises(adapter.AdapterError, match="unregistered XML Hubbard content"):
        adapter._check_xml_input(extra, adapter.parse_deck(real / "control/input.in"))
    old_format = ET.fromstring(input_side(text, '<dftU new_format="true">', "<dftU>"))
    with pytest.raises(adapter.AdapterError, match="new_format"):
        adapter._check_xml_input(old_format, adapter.parse_deck(real / "control/input.in"))


@pytest.mark.parametrize("old,new", [
    ("<Hubbard_U specie=\"Co\" label=\"3d\">1.220077496231744E-001", "<Hubbard_U specie=\"Co\" label=\"3d\">1.30E-001"),
    ("<U_projection_type>atomic</U_projection_type>", "<U_projection_type>ortho-atomic</U_projection_type>"),
    ("<lda_plus_u_kind>0</lda_plus_u_kind>", "<lda_plus_u_kind>1</lda_plus_u_kind>"),
    ("<Hubbard_U specie=\"Cr\" label=\"3d\">", "<Hubbard_U specie=\"Cr\" label=\"4d\">"),
])
def test_real_hubbard_values_cannot_drift_from_the_registered_card(real, old, new):
    text = (real / "control/data-file-schema.xml").read_text(encoding="utf-8")
    with pytest.raises(adapter.AdapterError):
        adapter._check_xml_input(ET.fromstring(input_side(text, old, new)), adapter.parse_deck(real / "control/input.in"))


# ---------------------------------------------------------------- the fresh (calculation='scf') path

def scf_pair(real, stem):
    base = real / "pproj6"
    return base / (stem + ".in"), base / (stem + ".out"), base / (stem + ".xml")


def test_production_scope_still_refuses_the_ortho_atomic_projector(real):
    deck, _, _ = scf_pair(real, PPROJ6[0])
    assert adapter.HUBBARD_PROJECTORS == ("atomic",)
    with pytest.raises(adapter.AdapterError, match="atomic HUBBARD projector"):
        adapter.parse_deck(deck)


@pytest.mark.parametrize("stem", PPROJ6)
def test_real_scf_hubbard_xml_input_matches_its_own_deck(real, monkeypatch, stem):
    monkeypatch.setattr(adapter, "HUBBARD_PROJECTORS", ("atomic", "ortho-atomic"))
    deck_path, _, xml_path = scf_pair(real, stem)
    deck = adapter.parse_deck(deck_path)
    root = ET.parse(str(xml_path)).getroot()
    assert root.find("input/dft/dftU").attrib == {"new_format": "true"}
    assert root.find("input/control_variables/calculation").text == "scf" and deck["operations"]["calculation"] == "scf"
    assert adapter._check_xml_input(root, deck)
    for name, value in adapter.expected_xml_strings(deck).items():
        found = [node for node in root.find("input").iter() if tag(node) == name]
        assert len(found) == 1 and (found[0].text or "").strip() == value, name


@pytest.mark.parametrize("stem", PPROJ6)
def test_real_scf_output_node_is_a_converged_evaluation_with_forces(real, monkeypatch, stem):
    monkeypatch.setattr(adapter, "HUBBARD_PROJECTORS", ("atomic", "ortho-atomic"))
    deck_path, _, xml_path = scf_pair(real, stem)
    deck = adapter.parse_deck(deck_path)
    root = ET.parse(str(xml_path)).getroot()
    output = root.find("output")
    assert root.find("exit_status").text.strip() == "0" and not root.findall("step")
    frame = adapter._xml_evaluation(output, deck, {"path": str(xml_path), "sha256": "0" * 64, "line_start": 1, "line_end": 2})
    assert frame["status"] == "CONVERGED" and len(frame["forces_Ry_bohr"]) == deck["nat"]
    assert adapter._geometry_matches(frame["geometry"], deck["geometry"])


def run_scf(real, stem, monkeypatch, tmp_path):
    """read_qe_arm(normal_scf) on a real pair.  The pproj6 runs used 128 ranks / 4 pools / a serial
    diagonalization, not the registered catalyst layout, so only the runtime-header check is stubbed
    (it is exercised on real catalyst logs separately); real UPF reads are used when the UPF is on hand."""
    monkeypatch.setattr(adapter, "HUBBARD_PROJECTORS", ("atomic", "ortho-atomic"))
    deck_path, log_path, xml_path = scf_pair(real, stem)
    expected = adapter.parse_deck(deck_path)
    names = [row["filename"] for row in expected["upfs"]]
    directory = real / "control/common_pseudo"
    available = all((directory / name).exists() for name in names)
    monkeypatch.setattr(adapter, "_raw_upf_reads", REAL_UPF_READS)
    if available:
        expected["upf_pins"] = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in names}
        logged = re.findall(r"PseudoPot\.\s*#\s*\d+\s+for\s+\S+\s+read from file:[ \t]*\n?[ \t]*([^\r\n]+)",
                            log_path.read_text(encoding="utf-8"))
        expected["upf_read_path_map"] = {path.strip(): str(directory / Path(path.strip()).name) for path in logged}
    else:
        monkeypatch.setattr(adapter, "_raw_upf_reads", lambda *args, **kwargs: [])
    monkeypatch.setattr(adapter, "_raw_parallel", lambda *args, **kwargs: {"stubbed": True})
    root = ET.parse(str(xml_path)).getroot()
    parallel = {tag(node): int(node.text) for node in root.find("parallel_info")}
    stderr = tmp_path / "stderr.log"
    stderr.write_text("", encoding="utf-8")
    arm = adapter.read_qe_arm(deck_path, log_path, stderr, xml_path, {"returncode": 0, "timed_out": False},
                              expected_settings=expected, expected_parallel=parallel,
                              expected_exit="normal_scf", expected_evaluations=1)
    return arm, available


@pytest.mark.parametrize("stem", PPROJ6)
def test_real_scf_call_is_accepted_through_the_fresh_path(real, monkeypatch, tmp_path, stem):
    arm, _ = run_scf(real, stem, monkeypatch, tmp_path)
    assert arm["xml_exit_status"] == 0 and arm["proposal_geometry"] is None
    assert len(arm["evaluations"]) == 1 and arm["optimizer_counts"] == [] and arm["scf_counts"] == []
    assert arm["evaluations"][0]["status"] == "CONVERGED"


def test_four_real_scf_pairs_read_their_consumed_upfs(real, monkeypatch, tmp_path):
    used = []
    for stem in PPROJ6:
        arm, available = run_scf(real, stem, monkeypatch, tmp_path)
        if available:
            used.append(stem)
            assert len(arm["upf_reads"]) == len(arm["input"]["upfs"])
    assert used == ["Cr__s0_O__u750_ortho", "Cr__slab__u750_ortho", "Mn__s0_O__u750_ortho", "Mn__slab__u750_ortho"]


def test_scf_nstep_is_calculation_dependent_and_therefore_excluded_from_the_identity(real, monkeypatch):
    """QE writes its internal nstep (1 for calculation='scf'), not the deck's: it must not enter the
    cross-arm XML identity, and the deck-vs-XML bind must not compare it."""
    monkeypatch.setattr(adapter, "HUBBARD_PROJECTORS", ("atomic", "ortho-atomic"))
    for stem in PPROJ6:
        deck_path, _, xml_path = scf_pair(real, stem)
        root = ET.parse(str(xml_path)).getroot()
        assert root.find("input/control_variables/nstep").text == "1"
        assert adapter.parse_deck(deck_path)["operations"]["nstep"] == 200
    relax = control_xml(real).find("input/control_variables/nstep").text
    assert relax == "30"
    common = adapter._xml_common(control_xml(real).find("input"))
    flat = json.dumps(common)
    assert '"tag": "nstep"' not in flat and '"tag": "calculation"' not in flat


def test_relax_and_scf_xml_inputs_differ_only_in_operational_and_deck_driven_fields(real, monkeypatch):
    """Real relax (catalyst control) versus real scf (Mn slab): fields whose values QE changes with the
    calculation, other than the declared operational ones, would break the fresh-versus-control identity."""
    monkeypatch.setattr(adapter, "HUBBARD_PROJECTORS", ("atomic", "ortho-atomic"))
    def leaves(path):
        node = ET.parse(str(path)).getroot().find("input")
        found = {}
        def walk(item, prefix):
            here = prefix + "/" + tag(item)
            children = list(item)
            if not children:
                found[here] = (" ".join((item.text or "").split()), tuple(sorted(item.attrib.items())))
            for child in children:
                walk(child, here)
        for child in node:
            if tag(child) not in ("atomic_structure",):
                walk(child, "")
        return found
    relax = leaves(real / "control/data-file-schema.xml")
    scf = leaves(scf_pair(real, "Mn__slab__u750_ortho")[2])
    shared = {key for key in relax if key in scf}
    differing = {key for key in shared if relax[key] != scf[key]}
    operational = {"/control_variables/calculation", "/control_variables/max_seconds", "/control_variables/nstep",
                   "/control_variables/outdir", "/control_variables/prefix", "/control_variables/pseudo_dir"}
    deck_driven = {"/electron_control/max_nstep", "/dft/dftU/U_projection_type", "/free_positions",
                   "/k_points_IBZ/monkhorst_pack"}
    assert operational <= differing
    unexplained = {key for key in differing if key not in operational and key not in deck_driven
                   and not key.startswith("/atomic_species") and "/dftU" not in key}
    assert unexplained == set(), sorted(unexplained)


# ---------------------------------------------------------------- real 72-atom fresh logs and the registered shape

@pytest.mark.parametrize("name,converged", [("slab_c5low__checked.fresh3.out", True), ("slab_c5low__checked.fresh10.out", False)])
def test_real_72_atom_fresh_logs_show_the_registered_runtime_layout(real, name, converged):
    text = (real / "fresh_logs" / name).read_text(encoding="utf-8")
    shape = adapter._raw_parallel(text, {"path": name, "sha256": "0" * 64, "line_start": 1, "line_end": 1}, CATALYST)
    assert shape["elpa_subgroup"] == [4, 4] and shape["nprocs"] == 128 and shape["npool"] == 8
    assert re.findall(r"Program PWSCF v\.([0-9.]+) starts", text) == ["7.5"]
    assert "JOB DONE." in text  # a supervisor stop at the stall also ends in a clean QE shutdown
    assert ("Program stopped by user request" in text) is (not converged)
    assert not adapter.FAILURE.search(text)  # the IEEE underflow/denormal notes are not failures
    if converged:
        assert "IEEE_UNDERFLOW_FLAG" in text or "IEEE_DENORMAL" in text
        assert len(re.findall(r"(?m)^\s*!\s+total energy\s*=", text)) == 1
        assert len(re.findall(r"Forces acting on atoms \(cartesian axes, Ry/au\):", text)) == 1
        assert "number of scf cycles" not in text and "number of bfgs steps" not in text
    else:
        assert "convergence has been achieved" not in text


def test_real_serial_shape_is_still_the_only_other_registered_layout(real):
    text = (real / "tiny_h2/candidate-stop/stdout.log").read_text(encoding="utf-8")
    shape = adapter._raw_parallel(text, {"path": "tiny", "sha256": "0" * 64, "line_start": 1, "line_end": 1}, SERIAL)
    assert shape["diagonalization_algorithm"] == "serial"
    with pytest.raises(adapter.AdapterError):
        adapter._raw_parallel(text, {"path": "tiny", "sha256": "0" * 64, "line_start": 1, "line_end": 1}, CATALYST)


# ---------------------------------------------------------------- the retained real restart arms (serial H2)

def test_real_tiny_clean_stop_arm_is_accepted_and_its_saved_optimizer_reads(real):
    directory = real / "tiny_h2/candidate-stop"
    expected = adapter.parse_deck(directory / "input.in")
    pseudo = directory / "H.pbe-rrkjus_psl.1.0.0.UPF"
    expected["upf_pins"] = {pseudo.name: real_files.TINY_UPF_SHA256}
    expected["upf_read_path_map"] = {real_files.LOGGED_TINY_DIR + pseudo.name: str(pseudo)}
    receipt = json.loads((directory / "receipt.json").read_text(encoding="utf-8"))
    arm = adapter.read_qe_arm(directory / "input.in", directory / "stdout.log", directory / "stderr.log",
                              directory / "data-file-schema.xml", receipt, expected_settings=expected,
                              expected_parallel=SERIAL, expected_exit="clean_stop", expected_evaluations=1)
    assert arm["scf_counts"] == [1] and arm["optimizer_counts"] == [0]
    saved = adapter.read_bfgs(directory / "h2_probe.bfgs", nat=2, cell_bohr=arm["evaluations"][0]["geometry"]["cell"],
                              evaluated=arm["evaluations"][0])
    assert (saved["scf_count"], saved["bfgs_count"], saved["gdiis_count"]) == (1, 1, 0)


def test_real_restart_and_from_scratch_arms_share_one_xml_identity(real):
    identities, restart_modes = {}, {}
    for arm in ("candidate-stop", "continuous", "resumed", "negative-fresh"):
        directory = real / "tiny_h2" / arm
        deck = adapter.parse_deck(directory / "input.in")
        root = ET.parse(str(directory / "data-file-schema.xml")).getroot()
        identities[arm] = adapter._check_xml_input(root, deck)
        restart_modes[arm] = adapter.expected_xml_strings(deck)["restart_mode"]
    assert restart_modes["resumed"] == "restart" and restart_modes["continuous"] == "from_scratch"
    assert len(set(identities.values())) == 1


# ---------------------------------------------------------------- the QE75_XML_CANONICAL map against the cached official source

def cached(name):
    path = QE_SOURCE / name
    if not path.is_file():
        pytest.skip("cached official QE 7.5 source is not present in this checkout")
    receipts = sorted((ROOT / "results/pa_catalyst_trial_2026-10-03").glob("qe_source*retrieval.json"))
    pins = {row["path"]: row["sha256"] for receipt in receipts for row in json.loads(receipt.read_text(encoding="utf-8"))["files"]
            if "sha256" in row}
    assert hashlib.sha256(path.read_bytes()).hexdigest() == pins[name], "cached QE source differs from its retrieval receipt"
    return path.read_text(encoding="utf-8").splitlines()


def lines(rows, first, last):
    return "\n".join(rows[first - 1:last])


def test_canonical_map_rules_quote_the_cached_qe_source():
    pw = cached("PW/src/pw_init_qexsd_input.f90")
    assert "TRIM(ip_diagonalization) == 'david'" in lines(pw, 477, 477) and "'davidson'" in lines(pw, 478, 478)
    assert "ELSE" in lines(pw, 479, 479) and "diagonalization = ip_diagonalization" in lines(pw, 480, 480)
    assert "TRIM(input_dft) .NE. \"none\"" in lines(pw, 203, 203) and "capital(dft_name(i:i))" in lines(pw, 206, 206)
    assert "get_dft_short()" in lines(pw, 209, 209)
    assert "ip_hubbard_projectors" in lines(pw, 396, 396) and "ip_lda_plus_u_kind" in lines(pw, 395, 395)
    assert "ip_occupations" in lines(pw, 449, 449)
    inp = cached("Modules/qexsd_input.f90")
    assert "verbosity" in lines(inp, 80, 80) and "\"low\"" in lines(inp, 81, 81)
    assert "disk_io" in lines(inp, 85, 85) and "\"low\"" in lines(inp, 86, 86)
    assert "calculation=TRIM(calculation)" in lines(inp, 92, 92) and "prefix=TRIM(prefix)" in lines(inp, 93, 93)
    params = cached("Modules/input_parameters.f90")
    assert "'bfgs'" in lines(params, 1101, 1103)
    iosys = cached("PW/src/input.f90")
    assert "SELECT CASE( trim( mixing_mode ) )" in lines(iosys, 1163, 1163) and "'plain'" in lines(iosys, 1164, 1164)


def test_canonical_smearing_aliases_equal_the_cached_set_occupations_source():
    rows = cached("PW/src/set_occupations.f90")
    start = next(i for i, row in enumerate(rows) if "FUNCTION schema_smearing" in row and "END" not in row)
    block = "\n".join(rows[start:start + 25])
    from_source = {}
    for names, canonical in re.findall(r"CASE \(([^)]*)\)\s*\n\s*schema_smearing = '(\w+)'", block):
        from_source[canonical] = set(re.findall(r"'([^']+)'", names))
    assert set(from_source) == {"gaussian", "mp", "mv", "fd"}
    for canonical, aliases in from_source.items():
        for alias in aliases:
            assert adapter._schema_smearing(alias) == canonical


def test_dftu_writer_has_no_lda_plus_u_argument_and_registers_only_the_checked_children():
    module = cached("Modules/qes_init_module.f90")
    text = "\n".join(module)
    start = text.index("SUBROUTINE qes_init_dftU(")
    header = text[start:text.index(")", text.index("Hubbard_ns_nc)", start)) + 1]
    arguments = {part.strip() for part in re.sub(r"\s|&", "", header.split("(", 1)[1].rstrip(")")).split(",")}
    assert "lda_plus_u_kind" in arguments and "new_format" in arguments and "lda_plus_u" not in arguments
    assert adapter.DFTU_REGISTERED_CHILDREN <= arguments | {"U_projection_type"}
    copied = cached("Modules/qexsd_copy.f90")
    assert "lda_plus_u = dft_obj%dftU_ispresent" in lines(copied, 403, 403)
    init = cached("Modules/qexsd_init.f90")
    assert 'CALL qes_init (obj, "dftU", .true., lda_plus_u_kind' in lines(init, 510, 510)


# ---------------------------------------------------------------- mutation checks: each reintroduced flaw must fail a real-file test

def mutant(old, new):
    text = SRC.read_text(encoding="utf-8")
    assert text.count(old) == 1, old
    module = types.ModuleType("pa_qe_adapter_v2_mutant")
    module.__file__ = str(SRC)
    module.__package__ = ""  # falsy: the module takes its sibling-import branch
    exec(compile(text.replace(old, new), str(SRC), "exec"), module.__dict__)
    return module


def accepts_real_control(real, module, tmp_path, *, deck_line=None):
    text = control_deck_text(real)
    if deck_line:
        text = with_line(text, deck_line[0], deck_line[1])
    path = tmp_path / "mutation.in"
    path.write_text(text, encoding="utf-8")
    module._check_xml_input(control_xml(real), module.parse_deck(path))


MUTANTS = [
    ("lda_plus_u element required again",
     'value(dftu, "lda_plus_u_kind", 0)', 'value(dftu, "lda_plus_u", True)\n        value(dftu, "lda_plus_u_kind", 0)',
     None, "lda_plus_u"),
    ("diagonalization compared literally", '"map": {"david": "davidson"}', '"map": {}', ("ELECTRONS", "diagonalization = 'david'"), "diagonalization"),
    ("disk_io default compared literally", '"disk_io": {"kind": "map", "map": {"default": "low"}',
     '"disk_io": {"kind": "map", "map": {}', ("CONTROL", "disk_io = 'default'"), "disk_io"),
    ("verbosity default compared literally", '"verbosity": {"kind": "map", "map": {"default": "low"}',
     '"verbosity": {"kind": "map", "map": {}', ("CONTROL", "verbosity = 'default'"), "verbosity"),
    ("functional compared without case folding", '"functional": {"kind": "upper"', '"functional": {"kind": "verbatim"',
     ("SYSTEM", "input_dft = 'pbe'"), "functional"),
]


@pytest.mark.parametrize("label,old,new,deck_line,message", MUTANTS, ids=[row[0] for row in MUTANTS])
def test_reintroduced_flaw_fails_a_real_file_test(real, tmp_path, label, old, new, deck_line, message):
    accepts_real_control(real, adapter, tmp_path, deck_line=deck_line)  # the corrected adapter accepts the real file
    flawed = mutant(old, new)
    with pytest.raises(flawed.AdapterError, match=message):
        accepts_real_control(real, flawed, tmp_path, deck_line=deck_line)


def test_dropping_the_xml_hubbard_whitelist_would_accept_an_element_real_qe_never_writes(real):
    flawed = mutant('if unregistered:\n            raise AdapterError("unregistered XML Hubbard content: " + ", ".join(unregistered))',
                    'if False:\n            raise AdapterError("unregistered")')
    text = (real / "control/data-file-schema.xml").read_text(encoding="utf-8")
    old = "<lda_plus_u_kind>0</lda_plus_u_kind>"
    invented = ET.fromstring(input_side(text, old, "<lda_plus_u>true</lda_plus_u>" + old))
    deck = flawed.parse_deck(real / "control/input.in")
    assert flawed._check_xml_input(invented, deck)  # the flawed copy lets it through ...
    with pytest.raises(adapter.AdapterError, match="unregistered XML Hubbard content"):
        adapter._check_xml_input(invented, adapter.parse_deck(real / "control/input.in"))  # ... the corrected one does not


def test_dropping_the_operational_binds_would_accept_a_restart_xml_for_a_from_scratch_deck(real):
    flawed = mutant('if operations.get(key) is not None:\n            value(xml_control, key, operations[key])',
                    'if False:\n            pass')
    text = (real / "control/data-file-schema.xml").read_text(encoding="utf-8")
    changed = ET.fromstring(text.replace("<restart_mode>from_scratch</restart_mode>", "<restart_mode>restart</restart_mode>"))
    assert flawed._check_xml_input(changed, flawed.parse_deck(real / "control/input.in"))
    with pytest.raises(adapter.AdapterError, match="restart_mode"):
        adapter._check_xml_input(changed, adapter.parse_deck(real / "control/input.in"))
