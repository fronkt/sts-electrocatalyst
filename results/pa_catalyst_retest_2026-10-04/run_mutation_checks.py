"""Mutation checks: each reintroduced flaw in pa_qe_adapter_v2 must fail at least one real-file test.

Works in a scratch tree (the worktree is never touched): a mutated copy of src/dft/pa_qe_adapter_v2.py, the
unchanged contract, the real-file tests and the real fixtures, then pytest on test_pa_qe_adapter_v2_real.py.
Writes mutation_checks.json here (refuses to overwrite).
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGET = HERE / "mutation_checks.json"
if TARGET.exists():
    raise SystemExit("mutation_checks.json exists; refusing to overwrite")

ADAPTER = (ROOT / "src/dft/pa_qe_adapter_v2.py").read_text(encoding="utf-8")
MUTATIONS = [
    ("M1 lda_plus_u element required again (the original defect)",
     'value(dftu, "lda_plus_u_kind", 0)', 'value(dftu, "lda_plus_u", True)\n        value(dftu, "lda_plus_u_kind", 0)'),
    ("M2 diagonalization alias not canonicalized", '"map": {"david": "davidson"}', '"map": {}'),
    ("M3 disk_io default not canonicalized", '"disk_io": {"kind": "map", "map": {"default": "low"}', '"disk_io": {"kind": "map", "map": {}'),
    ("M4 verbosity default not canonicalized", '"verbosity": {"kind": "map", "map": {"default": "low"}', '"verbosity": {"kind": "map", "map": {}'),
    ("M5 input_dft case not folded", '"functional": {"kind": "upper"', '"functional": {"kind": "verbatim"'),
    ("M6 unregistered Hubbard content accepted",
     'if unregistered:\n            raise AdapterError("unregistered XML Hubbard content: " + ", ".join(unregistered))',
     'if False:\n            raise AdapterError("unregistered")'),
    ("M7 new_format layout not required",
     'if dftu.attrib.get("new_format") != "true":', 'if False:'),
    ("M8 operational fields not bound to the arm's deck",
     'if operations.get(key) is not None:\n            value(xml_control, key, operations[key])', 'if False:\n            pass'),
    ("M9 production scope widened to the ortho-atomic projector", 'HUBBARD_PROJECTORS = ("atomic",)', 'HUBBARD_PROJECTORS = ("atomic", "ortho-atomic")'),
    ("M10 Hubbard U values not compared", 'if set(actual) != set(expected) or any(abs(actual[key]-expected[key]) > 1e-10 for key in actual):',
     'if False:'),
    ("M11 U projector not compared", 'value(dftu, "U_projection_type", source_hubbard["unit"])', 'pass'),
    ("M12 smearing alias cold accepted as itself", '"mv": {"marzari-vanderbilt", "cold", "m-v", "mv", "Marzari-Vanderbilt", "M-V", "MV"},',
     '"mv": {"marzari-vanderbilt", "m-v", "mv", "Marzari-Vanderbilt", "M-V", "MV"},'),
]


def build(tree, source):
    (tree / "src/dft").mkdir(parents=True)
    (tree / "tests").mkdir()
    (tree / "results/pa_catalyst_trial_2026-10-03").mkdir(parents=True)
    (tree / "src/dft/pa_qe_adapter_v2.py").write_text(source, encoding="utf-8", newline="\n")
    shutil.copy2(ROOT / "src/dft/pa_checked_contract.py", tree / "src/dft/pa_checked_contract.py")
    for name in ("test_pa_qe_adapter_v2_real.py", "qe75_real_fixtures.py"):
        shutil.copy2(ROOT / "tests" / name, tree / "tests" / name)
    shutil.copytree(ROOT / "tests/fixtures", tree / "tests/fixtures")
    shutil.copy2(ROOT / "results/pa_catalyst_trial_2026-10-03/launch_spec.json", tree / "results/pa_catalyst_trial_2026-10-03/launch_spec.json")
    shutil.copytree(ROOT / "results/pa_catalyst_trial_2026-10-03/qe_source", tree / "results/pa_catalyst_trial_2026-10-03/qe_source")
    for receipt in (ROOT / "results/pa_catalyst_trial_2026-10-03").glob("qe_source*retrieval.json"):
        shutil.copy2(receipt, tree / "results/pa_catalyst_trial_2026-10-03" / receipt.name)


def run(tree):
    process = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
                              "tests/test_pa_qe_adapter_v2_real.py"], cwd=tree, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=900)
    failed = [line.split(" ", 1)[1].split(" - ")[0] for line in process.stdout.splitlines() if line.startswith("FAILED ")]
    summary = [line for line in process.stdout.splitlines() if " passed" in line or " failed" in line]
    return process.returncode, failed, summary[-1] if summary else ""


def main():
    import hashlib
    report = {"qe_executed": False, "adapter_sha256": hashlib.sha256(ADAPTER.encode("utf-8")).hexdigest(), "baseline": None, "mutations": []}
    with tempfile.TemporaryDirectory() as scratch:
        tree = Path(scratch) / "baseline"
        build(tree, ADAPTER)
        code, failed, summary = run(tree)
        report["baseline"] = {"returncode": code, "failed": failed, "summary": summary}
        assert code == 0, "the unmutated adapter must pass its real-file tests"
        for label, old, new in MUTATIONS:
            assert ADAPTER.count(old) == 1, label
            tree = Path(scratch) / ("m" + label.split()[0][1:])
            build(tree, ADAPTER.replace(old, new))
            code, failed, summary = run(tree)
            report["mutations"].append({"mutation": label, "caught": code != 0 and len(failed) > 0, "failing_tests": len(failed),
                                        "first_failing_tests": failed[:4], "summary": summary})
    report["all_caught"] = all(row["caught"] for row in report["mutations"])
    TARGET.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    for row in report["mutations"]:
        print(("CAUGHT " if row["caught"] else "MISSED ") + row["mutation"], "->", row["failing_tests"], "failing")
    print("all caught:", report["all_caught"])


if __name__ == "__main__":
    main()
