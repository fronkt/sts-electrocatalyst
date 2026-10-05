"""Zero-SU audit of every XML tag, attribute and literal string the adapter and controller require,
for every arm type of the trial, against the real QE 7.5 output available locally.

Reads only.  Writes audit_real_outputs.json and audit_table.md into this directory (refuses to
overwrite).  Never imports the frozen adapter except to report what it does with the same files.

Real corpora (all QE 7.5):
  CONTROL   control call of job 21034683: deck, stdout, stderr, XML, .bfgs (72 atoms, Hubbard, 128 MPI)
  SCF19     19 calculation='scf' Hubbard XML + deck + log (runs/a0/pproj6)
  FRESH21   21 September 72-atom 128-rank fresh SCF logs (15 converged, 6 stalled and stopped)
  SEG21     21 September 72-atom 128-rank from-scratch single-step relax logs
  TINY      four arms of the one-process H2 restart probe (clean stop, continuous, resumed, scratch)
"""
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "src/dft"))
sys.path.insert(0, str(ROOT / "tests"))
import pa_catalyst_retest as controller  # noqa: E402
FROZEN_COPY = ROOT / "results/pa_catalyst_trial_readout_2026-10-04/dryrun/scratch/pa_qe_adapter_FROZEN_COPY.py"
FROZEN_SHA256 = "255464215aa898d0c9d34317a1be9b16fb27ba6d35108e0ca78215331a628879"  # launch_spec.json pin
assert hashlib.sha256(FROZEN_COPY.read_bytes()).hexdigest() == FROZEN_SHA256, "retained frozen copy differs from its pin"
_frozen_spec = importlib.util.spec_from_file_location("frozen_pa_qe_adapter", FROZEN_COPY)
frozen = importlib.util.module_from_spec(_frozen_spec)  # byte-identical copy of the adapter that ran in job 21034683
_frozen_spec.loader.exec_module(frozen)
import pa_qe_adapter_v2 as adapter  # noqa: E402
import qe75_real_fixtures as real_files  # noqa: E402

QE_SOURCE = ROOT / "results/pa_catalyst_trial_2026-10-03/qe_source"
MIRROR = ROOT / "results/pa_catalyst_trial_readout_2026-10-04/mirror/trial_results"
SEPT = ROOT / "results/lowtail_low_state_restart_2026-09-22/checked2/outputs/Cu8Cr23Mn35Co34__s20_site2/segments"
PPROJ6 = ROOT / "runs/a0/pproj6"
TINY = ROOT / "results/s2_2026-09-25/full_text/sequential_2026-10-03/pa_tiny_raw/tiny_results"
REAL_UPF_READS, REAL_PARALLEL = adapter._raw_upf_reads, adapter._raw_parallel


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tag(node):
    return node.tag.rsplit("}", 1)[-1]


# --------------------------------------------------------------------------- corpora
def pproj6_pairs():
    pairs = []
    for xml in sorted(PPROJ6.rglob("data-file-schema.xml")):
        case, element = xml.parent.name[:-5], xml.parts[-4]
        pairs.append({"id": element + "/" + case, "xml": xml, "deck": PPROJ6 / element / (case + ".in"),
                      "log": PPROJ6 / element / (case + ".out")})
    return pairs


def control_arm():
    c = MIRROR / "control"
    return {"deck": c / "input.in", "stdout": c / "stdout.log", "stderr": c / "stderr.log",
            "xml": c / "outdir/slab_c5low__pa_boundary.save/data-file-schema.xml",
            "bfgs": c / "outdir/slab_c5low__pa_boundary.bfgs", "receipt": c / "process_receipt.json",
            "upfs": MIRROR / "common_pseudo"}


def tiny_arms():
    return {name: {"deck": TINY / name / "input.in", "stdout": TINY / name / "stdout.log",
                   "stderr": TINY / name / "stderr.log", "receipt": TINY / name / "receipt.json",
                   "xml": TINY / name / "scratch/h2_probe.save/data-file-schema.xml"}
            for name in ("candidate-stop", "continuous", "resumed", "negative-fresh")}


# --------------------------------------------------------------------------- dynamic XML lookup recorder
class Recorder:
    def __init__(self):
        self.rows = {}
        self.original = adapter._one

    def __enter__(self):
        recorder = self

        def traced(node, name):
            found = sum(1 for child in node if tag(child) == name)
            key = (tag(node), name)
            record = recorder.rows.setdefault(key, {"calls": 0, "found_once": 0, "missing_or_repeated": 0})
            record["calls"] += 1
            record["found_once" if found == 1 else "missing_or_repeated"] += 1
            return recorder.original(node, name)
        adapter._one = traced
        return self

    def __exit__(self, *exc):
        adapter._one = self.original


def run_clean_stop_control():
    arm = control_arm()
    expected = adapter.parse_deck(arm["deck"])
    pins = {p.name: digest(p) for p in sorted(arm["upfs"].iterdir())}
    expected["upf_pins"] = pins
    expected["upf_read_path_map"] = {real_files.LOGGED_CONTROL_UPF_DIR + n: str(arm["upfs"] / n) for n in pins}
    receipt = json.loads(arm["receipt"].read_text(encoding="utf-8"))
    with Recorder() as rec:
        result = adapter.read_qe_arm(arm["deck"], arm["stdout"], arm["stderr"], arm["xml"], receipt,
                                     expected_settings=expected, expected_parallel=real_files.CATALYST,
                                     expected_exit="clean_stop", expected_evaluations=3)
    return result, rec.rows


def run_scf_pairs():
    """read_qe_arm(normal_scf) on every real scf pair; header stubbed, UPF reads real when the UPF is on hand."""
    adapter.HUBBARD_PROJECTORS = ("atomic", "ortho-atomic")
    upf_dir = control_arm()["upfs"]
    outcomes, rows = [], {}
    empty = HERE / "_empty_stderr.tmp"
    empty.write_text("", encoding="utf-8")
    try:
        for pair in pproj6_pairs():
            expected = adapter.parse_deck(pair["deck"])
            names = [u["filename"] for u in expected["upfs"]]
            have = all((upf_dir / n).exists() for n in names)
            adapter._raw_upf_reads = REAL_UPF_READS
            if have:
                expected["upf_pins"] = {n: digest(upf_dir / n) for n in names}
                logged = re.findall(r"PseudoPot\.\s*#\s*\d+\s+for\s+\S+\s+read from file:[ \t]*\n?[ \t]*([^\r\n]+)",
                                    pair["log"].read_text(encoding="utf-8"))
                expected["upf_read_path_map"] = {p.strip(): str(upf_dir / Path(p.strip()).name) for p in logged}
            else:
                adapter._raw_upf_reads = lambda *a, **k: []
            adapter._raw_parallel = lambda *a, **k: {"stubbed": True}
            root = ET.parse(str(pair["xml"])).getroot()
            parallel = {tag(n): int(n.text) for n in root.find("parallel_info")}
            outcome = {"id": pair["id"], "real_upf_reads": have}
            try:
                with Recorder() as rec:
                    arm = adapter.read_qe_arm(pair["deck"], pair["log"], empty, pair["xml"],
                                              {"returncode": 0, "timed_out": False}, expected_settings=expected,
                                              expected_parallel=parallel, expected_exit="normal_scf", expected_evaluations=1)
                outcome.update(result="ACCEPTED", energy_Ry=arm["evaluations"][0]["energy_Ry"])
                for key, value in rec.rows.items():
                    merged = rows.setdefault(key, {"calls": 0, "found_once": 0, "missing_or_repeated": 0})
                    for field in merged:
                        merged[field] += value[field]
            except Exception as error:  # noqa: BLE001
                outcome.update(result="REFUSED", error=repr(error))
            outcomes.append(outcome)
    finally:
        adapter._raw_upf_reads, adapter._raw_parallel = REAL_UPF_READS, REAL_PARALLEL
        adapter.HUBBARD_PROJECTORS = ("atomic",)
        empty.unlink()
    return outcomes, rows


def frozen_on_real():
    """What the frozen adapter does with the real control and with each real scf deck/XML."""
    arm = control_arm()
    deck = frozen.parse_deck(arm["deck"])
    root = ET.parse(str(arm["xml"])).getroot()
    out = {}
    try:
        frozen._check_xml_input(root, deck)
        out["control_xml_input"] = "ACCEPTED"
    except Exception as error:  # noqa: BLE001
        out["control_xml_input"] = "REFUSED: " + str(error)
    refused = 0
    for pair in pproj6_pairs():
        try:
            frozen.parse_deck(pair["deck"])
        except Exception:  # noqa: BLE001
            refused += 1
    out["scf_decks_refused_by_frozen_parse_deck"] = "%d of %d (ortho-atomic projector outside the registered scope)" % (
        refused, len(pproj6_pairs()))
    return out


# --------------------------------------------------------------------------- log literal audit
def count(pattern, text, flags=re.M):
    return len(re.findall(pattern, text, flags))


LOG_ITEMS = [
    # name, regex, expectation per corpus kind, role
    ("QE banner", r"Program PWSCF v\.([0-9.]+) starts", "exactly1", "read_qe_arm banner == ['7.5'] (ADP read_qe_arm)"),
    ("clean shutdown", r"JOB DONE\.", "exactly1", "read_qe_arm requires JOB DONE."),
    ("MPI processes", r"^[ \t]*Number of MPI processes:[ \t]*(\d+)[ \t]*\r?$", "exactly1", "_raw_parallel mpi_processes"),
    ("threads per MPI", r"^[ \t]*Threads/MPI process:[ \t]*(\d+)[ \t]*\r?$", "exactly1", "_raw_parallel threads_per_mpi"),
    ("processor cores", r"^[ \t]*Parallel version \(MPI & OpenMP\), running on[ \t]*(\d+)[ \t]+processor cores[ \t]*\r?$", "exactly1", "_raw_parallel processor_cores"),
    ("k-point pools", r"^[ \t]*K-points division:[ \t]*npool[ \t]*=[ \t]*(\d+)[ \t]*\r?$", "exactly1", "_raw_parallel kpoint_pools"),
    ("proc/nbgrp/npool/nimage", r"^[ \t]*R & G space division:[ \t]*proc/nbgrp/npool/nimage[ \t]*=[ \t]*(\d+)[ \t]*\r?$", "exactly1", "_raw_parallel band-group"),
    ("ELPA sub-group", r"^[ \t]*ELPA distributed-memory algorithm \(size of sub-group:[ \t]*(\d+)[ \t]*\*[ \t]*(\d+)[ \t]+procs\)[ \t]*\r?$", "exactly1", "_raw_parallel elpa_subgroup (128-rank only)"),
    ("first SCF threshold", r"convergence threshold\s*=\s*([+-]?\d+(?:\.\d*)?(?:[eEdD][+-]?\d+)?)", "atleast1", "read_qe_arm thresholds[0]"),
    ("pseudopotential read", r"PseudoPot\.\s*#\s*(\d+)\s+for\s+(\S+)\s+read from file:[ \t]*\n?[ \t]*([^\r\n]+)", "five", "_raw_upf_reads"),
    ("pseudopotential MD5", r"MD5 check sum:\s*([a-f0-9]{32})", "five", "_raw_upf_reads"),
    ("converged SCF energy", r"(?m)^\s*!\s+total energy\s*=\s*([+-]?\d+(?:\.\d*)?(?:[eEdD][+-]?\d+)?)\s+Ry\s*$", "atleast1", "log/XML energy binding"),
    ("force block header", r"Forces acting on atoms \(cartesian axes, Ry/au\):", "atleast1", "log/XML force binding"),
    ("force row", r"(?m)^\s*atom\s+(\d+)\s+type\s+(\d+)\s+force\s*=", "atleast1", "log/XML force binding rows"),
    ("SCF-cycle counter", r"(?m)^[ \t]*number of scf cycles[ \t]*=[ \t]*(\d+)[ \t]*$", "relax", "controller SCF_CYCLE; adapter scf_counts"),
    ("BFGS-step counter", r"number of bfgs steps\s*=\s*(\d+)", "relax", "adapter optimizer_counts"),
    ("proposal geometry", r"(?mi)^\s*ATOMIC_POSITIONS\s*\((bohr|angstrom)\)\s*\n", "relax", "adapter logged proposals"),
    ("user stop", r"Program stopped by user request", "stop", "adapter STOP (clean_stop only)"),
    ("optimizer reset at startup", r"\.bfgs deleted, as requested", "scratch", "adapter startup_history_deleted / negative control"),
]
FAILURE_ADAPTER = re.compile(frozen.FAILURE.pattern, re.I)
FAILURE_CONTROLLER = controller.FAILURE
SCF_ITERATION = controller.SCF_ITERATION


def audit_logs():
    corpora = {}
    control = control_arm()
    corpora["CONTROL stdout (relax, clean stop)"] = [(control["stdout"], control["stderr"])]
    corpora["SEG21 (from-scratch relax, one step)"] = [(p, None) for p in sorted(SEPT.glob("slab_c5low__checked.seg*.out"))]
    fresh = sorted(SEPT.glob("slab_c5low__checked.fresh*.out"))
    corpora["FRESH21 (scf, 72 atoms)"] = [(p, None) for p in fresh]
    corpora["SCF19 pproj6 logs (scf)"] = [(pair["log"], None) for pair in pproj6_pairs()]
    arms = tiny_arms()
    corpora["TINY resumed (restart_mode='restart')"] = [(arms["resumed"]["stdout"], arms["resumed"]["stderr"])]
    corpora["TINY scratch negative"] = [(arms["negative-fresh"]["stdout"], arms["negative-fresh"]["stderr"])]
    corpora["TINY clean stop"] = [(arms["candidate-stop"]["stdout"], arms["candidate-stop"]["stderr"])]
    table = []
    for name, pattern, expect, role in LOG_ITEMS:
        for corpus, files in corpora.items():
            counts = []
            for path, err in files:
                text = path.read_text(encoding="utf-8", errors="replace")
                counts.append(count(pattern, text) if not pattern.startswith("(?m)") else len(re.findall(pattern, text)))
            table.append({"item": name, "role": role, "corpus": corpus, "files": len(files),
                          "match_counts_min_max": [min(counts), max(counts)]})
    failures = []
    for corpus, files in corpora.items():
        hits_adapter = hits_controller = hits_time = 0
        stalled = 0
        for path, err in files:
            text = path.read_text(encoding="utf-8", errors="replace") + ("\n" + err.read_text(encoding="utf-8", errors="replace") if err else "")
            hits_adapter += bool(FAILURE_ADAPTER.search(text))
            hits_controller += bool(FAILURE_CONTROLLER.search(text))
            hits_time += bool(controller.TIME_FAILURE.search(text))
            stalled += any(int(m.group(1)) >= 127 for m in SCF_ITERATION.finditer(text))
        failures.append({"corpus": corpus, "files": len(files), "adapter_FAILURE_hits": hits_adapter,
                         "controller_FAILURE_hits": hits_controller, "controller_TIME_FAILURE_hits": hits_time,
                         "controller_HEA4_iteration_127_hits": stalled})
    return table, failures


# --------------------------------------------------------------------------- canonicalization map with the cited source text
def canonical_map():
    rows = []
    for key, rule in adapter.QE75_XML_CANONICAL.items():
        row = {"deck_or_xml_key": key, "kind": rule["kind"], "source": rule["source"]}
        if rule["kind"] == "map":
            row["map"] = rule["map"]
        file_part = rule["source"].split(" ")[0]
        name, _, span = file_part.partition(":")
        cached = QE_SOURCE / name
        if cached.is_file() and span:
            first, _, last = span.partition("-")
            lines = cached.read_text(encoding="utf-8").splitlines()
            row["cited_source_sha256"] = digest(cached)
            row["cited_text"] = lines[int(first) - 1:int(last or first)]
        rows.append(row)
    return rows


# --------------------------------------------------------------------------- latent hazards, cross-arm identity
DRYRUN_PATCHED = ROOT / "results/pa_catalyst_trial_readout_2026-10-04/dryrun/scratch/pa_qe_adapter.py"
VARIANTS = [("diagonalization = 'david'", "ELECTRONS", "QE writes davidson"), ("disk_io = 'default'", "CONTROL", "QE writes low"),
            ("verbosity = 'default'", "CONTROL", "QE writes low"), ("input_dft = 'pbe'", "SYSTEM", "QE writes PBE"),
            ("diagonalization = 'cg'", "ELECTRONS", "real XML says davidson: must be refused"),
            ("mixing_mode = 'plain'", "ELECTRONS", "real XML says local-TF: must be refused")]


def with_assignment(text, namelist, line):
    key = line.split("=", 1)[0].strip()
    existing = re.compile(r"(?m)^[ \t]*" + re.escape(key) + r"[ \t]*=.*$")
    if existing.search(text):
        return existing.sub("  " + line, text, count=1)
    marker = "&" + namelist + "\n"
    return text.replace(marker, marker + "  " + line + "\n", 1)


def latent_hazards():
    """Deck strings QE rewrites.  The 'frozen + dry-run one-line patch' column isolates the literal-compare
    hazard from the lda_plus_u refusal that masks it in the frozen adapter."""
    spec = importlib.util.spec_from_file_location("dryrun_patched_adapter", DRYRUN_PATCHED)
    patched = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(patched)
    arm = control_arm()
    text = arm["deck"].read_text(encoding="utf-8")
    root = ET.parse(str(arm["xml"])).getroot()
    rows = []
    with tempfile.TemporaryDirectory() as scratch:
        for line, namelist, note in VARIANTS:
            path = Path(scratch) / "variant.in"
            path.write_text(with_assignment(text, namelist, line), encoding="utf-8", newline="\n")
            row = {"deck_assignment": line, "expectation": note}
            for label, module in (("frozen_with_dryrun_patch", patched), ("v2", adapter)):
                try:
                    module._check_xml_input(root, module.parse_deck(path))
                    row[label] = "ACCEPTED"
                except Exception as error:  # noqa: BLE001
                    row[label] = "REFUSED: " + str(error)
            rows.append(row)
    return rows


def xml_input_identity_evidence():
    """Cross-arm identity premise on real files: restart/from_scratch arms share one XML identity, and the
    <input> of a real relax (catalyst control) and a real scf differ only in declared operational fields."""
    out = {}
    identities = {}
    for name, arm in tiny_arms().items():
        deck = adapter.parse_deck(arm["deck"])
        root = ET.parse(str(arm["xml"])).getroot()
        identities[name] = {"restart_mode": deck["operations"]["restart_mode"], "xml_identity": adapter._check_xml_input(root, deck)}
    out["tiny_h2_arms"] = identities
    out["tiny_h2_all_equal"] = len({v["xml_identity"] for v in identities.values()}) == 1

    def leaves(path):
        node = ET.parse(str(path)).getroot().find("input")
        found = {}

        def walk(item, prefix):
            here = prefix + "/" + tag(item)
            kids = list(item)
            if not kids:
                found[here] = (" ".join((item.text or "").split()), tuple(sorted(item.attrib.items())))
            for kid in kids:
                walk(kid, here)
        for kid in node:
            if tag(kid) != "atomic_structure":
                walk(kid, "")
        return found
    relax = leaves(control_arm()["xml"])
    scf = leaves(PPROJ6 / "Mn/dens/slab__u750_ortho.save/data-file-schema.xml")
    differing = sorted(k for k in relax if k in scf and relax[k] != scf[k])
    only_one_side = sorted(set(relax) ^ set(scf))
    out["relax_control_vs_scf_Mn_slab_differing_input_fields"] = differing
    out["relax_control_vs_scf_Mn_slab_fields_on_one_side_only"] = only_one_side
    out["declared_operational_exclusions"] = ["title", "calculation", "restart_mode", "prefix", "pseudo_dir", "outdir", "wfcdir",
                                              "max_seconds", "nstep", "max_xml_steps", "print_every"]
    return out


# --------------------------------------------------------------------------- main
def main():
    target_json, target_md = HERE / "audit_real_outputs.json", HERE / "audit_table.md"
    if target_json.exists() or target_md.exists():
        raise SystemExit("audit receipt exists; refusing to overwrite")
    report = {"qe_executed": False, "new_jobs_submitted": 0, "anvil_writes": 0,
              "frozen_adapter_used_for_comparison": {"sha256": FROZEN_SHA256, "path": FROZEN_COPY.relative_to(ROOT).as_posix()},
              "worktree_src_dft_pa_qe_adapter_py_sha256_at_audit": digest(ROOT / "src/dft/pa_qe_adapter.py")}
    result, control_rows = run_clean_stop_control()
    report["control_clean_stop"] = {"result": "ACCEPTED", "evaluations": len(result["evaluations"]),
                                    "scf_counts": result["scf_counts"], "optimizer_counts": result["optimizer_counts"],
                                    "xml_exit_status": result["xml_exit_status"], "first_conv_thr_Ry": result["first_conv_thr_Ry"],
                                    "runtime_parallel": {k: v for k, v in result["runtime_parallel"].items() if k != "matched_lines"}}
    scf_outcomes, scf_rows = run_scf_pairs()
    report["scf_pairs"] = scf_outcomes
    report["xml_lookups_clean_stop_path"] = [{"parent": k[0], "tag": k[1], **v} for k, v in sorted(control_rows.items())]
    report["xml_lookups_fresh_path"] = [{"parent": k[0], "tag": k[1], **v} for k, v in sorted(scf_rows.items())]
    report["frozen_adapter_on_same_files"] = frozen_on_real()
    report["log_table"], report["failure_regex_table"] = audit_logs()
    report["canonical_map"] = canonical_map()
    report["latent_literal_compare_hazards"] = latent_hazards()
    report["xml_identity_evidence"] = xml_input_identity_evidence()
    # attributes the adapter reads, against the (tag, attribute) vocabulary of the real XML
    real_xml = [control_arm()["xml"]] + [p["xml"] for p in pproj6_pairs()] + [a["xml"] for a in tiny_arms().values()]
    tags, attributes = real_files.xml_vocabulary(real_xml)
    wanted = [("espresso", "Units"), ("creator", "NAME"), ("creator", "VERSION"), ("atomic_structure", "nat"),
              ("atom", "name"), ("atom", "index"), ("forces", "rank"), ("forces", "dims"), ("free_positions", "dims"),
              ("species", "name"), ("Hubbard_U", "specie"), ("Hubbard_U", "label"), ("smearing", "degauss"),
              ("dftU", "new_format"), ("monkhorst_pack", "nk1"), ("monkhorst_pack", "nk2"), ("monkhorst_pack", "nk3"),
              ("monkhorst_pack", "k1"), ("monkhorst_pack", "k2"), ("monkhorst_pack", "k3")]
    report["xml_attributes_read"] = [{"tag": t, "attribute": a, "in_real_qe75_xml": (t, a) in attributes} for t, a in wanted]
    report["real_xml_files_in_vocabulary"] = len(real_xml)
    report["tags_the_frozen_fixture_invented"] = {"lda_plus_u": "lda_plus_u" in tags}
    target_json.write_text(json.dumps(report, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({"scf_accepted": sum(o["result"] == "ACCEPTED" for o in scf_outcomes), "scf_total": len(scf_outcomes),
                      "xml_lookups_clean_stop": len(control_rows), "xml_lookups_fresh": len(scf_rows),
                      "frozen": report["frozen_adapter_on_same_files"]}))


if __name__ == "__main__":
    main()
