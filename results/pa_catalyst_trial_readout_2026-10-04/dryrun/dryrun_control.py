"""Zero-SU offline dry-run of the controller's control-call validation on the real mirrored control output.

Read-only: imports adapters only from this scratch folder (the frozen copy and the single-line-patched
copy), reads only the local mirror and the frozen controller constants; writes nothing except the new
JSON receipt it is asked to create.  No Anvil access, no QE, no submission.

Usage: python -B dryrun_control.py OUT.json
"""
import copy
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SCRATCH = HERE / "scratch"
REPO = HERE.parents[2]
MIRROR = HERE.parent / "mirror" / "trial_results"
ARM = MIRROR / "control"
SPEC = json.loads((REPO / "results/pa_catalyst_trial_2026-10-03/launch_spec.json").read_text(encoding="utf-8"))
SOURCE_DECK = REPO / "runs/hea/lowtail_low_state_restart_2026-09-22/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in"

sys.path.insert(0, str(SCRATCH))          # pa_checked_contract.py for the bare import in the adapter
sys.path.append(str(REPO / "src" / "dft"))  # frozen controller module, constants only


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, str(SCRATCH / filename))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


frozen = load("pa_qe_adapter_frozen_copy", "pa_qe_adapter_FROZEN_COPY.py")
patched = load("pa_qe_adapter_patched", "pa_qe_adapter.py")
import pa_catalyst_trial as controller  # noqa: E402  (constants SHAPE, PREFIX only)

PREFIX = controller.PREFIX
XML = ARM / "outdir" / (PREFIX + ".save") / "data-file-schema.xml"


def tracing(adapter):
    """Record every XML lookup the adapter makes through _one (behaviour unchanged)."""
    log = []
    original = adapter._one

    def traced(node, name):
        values = [v for v in node if adapter._tag(v) == name]
        log.append({"parent": adapter._tag(node), "wanted": name, "found": len(values)})
        return original(node, name)
    adapter._one = traced
    return log, lambda: setattr(adapter, "_one", original)


def expected_for(adapter):
    expected = adapter.parse_deck(SOURCE_DECK, SPEC["source_deck"]["sha256"])
    expected["upf_pins"] = {Path(p["path"]).name: p["sha256"] for p in SPEC["upfs"]}
    text = (ARM / "stdout.log").read_text(encoding="utf-8", errors="replace")
    mapping = {}
    for match in re.finditer(r"PseudoPot\.\s*#\s*\d+\s+for\s+\S+\s+read from file:[ \t]*\n?[ \t]*([^\r\n]+)", text):
        logged = match.group(1).strip()
        mapping[logged] = str(MIRROR / "common_pseudo" / Path(logged).name)
    expected["upf_read_path_map"] = mapping
    return expected


def controller_chain(adapter, label):
    """The control-call acceptance chain of pa_catalyst_trial.py Trial.execute (lines 837-871)."""
    process = json.loads((ARM / "process_receipt.json").read_text(encoding="utf-8"))
    rows = []

    def row(check, source, ok, detail):
        rows.append({"check": check, "source": source, "result": "PASS" if ok else "FAIL", "detail": detail})

    flags = {k: process.get(k) for k in ("timed_out", "within_per_call_cap", "supervisor_error", "capture_error",
                                         "failure_marker_observed", "HEA4_stall_observed", "solver_limit_observed")}
    contract_ok = not (process.get("timed_out") or process.get("within_per_call_cap") is not True
                       or process.get("supervisor_error") or process.get("capture_error")
                       or process.get("failure_marker_observed") or process.get("HEA4_stall_observed")
                       or process.get("solver_limit_observed"))
    row("process contract flags", "pa_catalyst_trial.py:840-844", contract_ok, flags)
    row("registered-evaluated-boundary stop receipt", "pa_catalyst_trial.py:845-846",
        process.get("stop_reason") == "registered-evaluated-boundary", process.get("stop_reason"))
    exit_files = [str(p) for p in MIRROR.rglob("*.EXIT")]
    inventory = json.loads((HERE.parent / "remote_inventory.json").read_text(encoding="utf-8"))["files"]
    remote_exit = [r["path"] for r in inventory if r["path"].endswith(".EXIT")]
    row("no stale EXIT file after shutdown", "pa_catalyst_trial.py:847-849", not exit_files and not remote_exit,
        {"local_EXIT_files": exit_files, "remote_inventory_EXIT_files": remote_exit})
    expected = expected_for(adapter)
    log, restore = tracing(adapter)
    parsed, error = None, None
    try:
        parsed = adapter.read_qe_arm(ARM / "input.in", ARM / "stdout.log", ARM / "stderr.log", XML, process,
                                     expected_settings=expected, expected_parallel=controller.SHAPE,
                                     expected_exit="clean_stop", expected_evaluations=3)
    except Exception as exc:  # fail closed, as the controller does
        error = "%s: %s" % (type(exc).__name__, exc)
    finally:
        restore()
    row("read_qe_arm (raw input/log/XML/process validation, 3 evaluated steps, clean stop)",
        "pa_catalyst_trial.py:850-854 -> pa_qe_adapter.py:761-914", parsed is not None, error or "returned a raw-validated arm")
    summary = None
    if parsed is not None:
        counts_ok = parsed["scf_counts"] == [1, 2, 3]
        row("ordered global SCF counters equal the registered boundary [1,2,3]", "pa_catalyst_trial.py:855-856", counts_ok,
            parsed["scf_counts"])
        try:
            adapter.require_expected_first_threshold(parsed, expected)
            thr_ok, thr_detail = True, {"first_conv_thr_Ry": parsed["first_conv_thr_Ry"], "deck_conv_thr_Ry": expected["conv_thr_Ry"]}
        except Exception as exc:
            thr_ok, thr_detail = False, "%s: %s" % (type(exc).__name__, exc)
        row("first-boundary SCF threshold equals registered 1e-6 Ry (control, candidate, fresh, reseed, negative)",
            "pa_catalyst_trial.py:857-858 -> pa_qe_adapter.py:917-920", thr_ok, thr_detail)
        row("control XML settings identity recorded for later arms", "pa_catalyst_trial.py:859-860",
            bool(parsed.get("xml_settings_identity")), parsed.get("xml_settings_identity"))
        summary = {
            "evaluations": [{"energy_Ry": e["energy_Ry"], "status": e["status"]} for e in parsed["evaluations"]],
            "scf_counts": parsed["scf_counts"], "optimizer_counts": parsed["optimizer_counts"],
            "xml_exit_status": parsed["xml_exit_status"], "first_conv_thr_Ry": parsed["first_conv_thr_Ry"],
            "startup_history_deleted": parsed["startup_history_deleted"],
            "startup_optimizer_initialized": parsed["startup_optimizer_initialized"],
            "restart_fallback": parsed["restart_fallback"], "runtime_parallel": {
                k: parsed["runtime_parallel"][k] for k in ("nprocs", "nthreads", "npool", "diagonalization_algorithm", "elpa_subgroup")},
            "upf_reads": [{"species": u["species"], "sha256": u["sha256"], "md5": u["md5"],
                           "actual_logged_read_path": u["actual_logged_read_path"]} for u in parsed["upf_reads"]],
            "xml_settings_identity": parsed["xml_settings_identity"], "settings_identity": parsed["settings_identity"],
            "evidence_sha256": parsed["evidence_sha256"]}
        # Same source pins the controller re-verifies after a validated call (verify_sources), where checkable locally.
        local = []
        for pin in SPEC["upfs"]:
            name = Path(pin["path"]).name
            local.append({"upf": name, "mirror_sha256_matches_spec_pin": sha256(MIRROR / "common_pseudo" / name) == pin["sha256"]})
        row("common_pseudo UPF copies match the launch-spec pins (checkable part of verify_sources)",
            "pa_catalyst_trial.py:872,714-723", all(x["mirror_sha256_matches_spec_pin"] for x in local), local)
        deps = [{"path": Path(p["path"]).name, "repo_sha256_matches_spec": sha256(REPO / "src" / "dft" / Path(p["path"]).name) == p["sha256"]}
                for p in SPEC["dependencies"] if p["path"].endswith("/src/dft/" + Path(p["path"]).name)]
        row("repo copies of the frozen dependency modules match their launch-spec pins", "pa_catalyst_trial.py:716-717",
            all(d["repo_sha256_matches_spec"] for d in deps), deps)
    return {"label": label, "controller_chain": rows, "adapter_error": error, "summary": summary,
            "xml_lookups": log, "accepted": all(r["result"] == "PASS" for r in rows)}


def main(out):
    result = {"frozen_adapter_sha256": sha256(REPO / "src/dft/pa_qe_adapter.py"),
              "frozen_copy_sha256": sha256(SCRATCH / "pa_qe_adapter_FROZEN_COPY.py"),
              "patched_copy_sha256": sha256(SCRATCH / "pa_qe_adapter.py"),
              "contract_sha256": sha256(SCRATCH / "pa_checked_contract.py"),
              "control_xml_sha256": sha256(XML), "mirror_control_stdout_sha256": sha256(ARM / "stdout.log")}
    assert result["frozen_adapter_sha256"] == result["frozen_copy_sha256"]
    result["baseline_frozen_adapter"] = controller_chain(frozen, "frozen adapter, unpatched")
    result["patched_lda_plus_u_only"] = controller_chain(patched, "scratch copy with only the lda_plus_u requirement removed")
    with open(out, "x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    for key in ("baseline_frozen_adapter", "patched_lda_plus_u_only"):
        block = result[key]
        print("==", block["label"], "ACCEPTED" if block["accepted"] else "NOT ACCEPTED")
        for r in block["controller_chain"]:
            print(" ", r["result"], "|", r["check"], "|", r["source"], "|", str(r["detail"])[:260])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
