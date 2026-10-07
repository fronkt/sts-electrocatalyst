"""Write the dated O1 launch spec (offline; LF bytes).

Derived from the launched re-test spec (results/pa_catalyst_retest_2026-10-04/launch_spec.json):
the same executables, pseudopotentials, seed, shape, negative control and real-control replay;
every file that lived under the re-test parent moves to the O1 parent; the dependency pins are
the O1 sibling controller and adapter, the unchanged contract and the O1 Slurm script.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "results/pa_catalyst_o1_2026-10-07"
OLD_PARENT = "/anvil/projects/x-che260157/sts_pa_catalyst_retest_2026-10-04"
PARENT = "/anvil/projects/x-che260157/sts_pa_catalyst_o1_2026-10-07"
RETEST = json.loads((ROOT / "results/pa_catalyst_retest_2026-10-04/launch_spec.json").read_text(encoding="utf-8"))
REVIEW = "results/pa_catalyst_o1_2026-10-07/source_xml_input_review.md"
DEPENDENCIES = ["src/dft/pa_catalyst_o1.py", "src/dft/pa_qe_adapter_o1.py", "src/dft/pa_checked_contract.py",
                "anvil/93_pa_catalyst_o1.slurm"]


def sha(path: Path, text: bool = True) -> str:
    data = path.read_bytes()
    if text and b"\r" in data:
        raise SystemExit(f"{path} is not LF")
    return hashlib.sha256(data).hexdigest()


def moved(path: str) -> str:
    if not path.startswith(OLD_PARENT + "/"):
        raise SystemExit("not under the re-test parent: " + path)
    return PARENT + path[len(OLD_PARENT):]


replay = copy.deepcopy(RETEST["preflight_replay"])
replay["root"] = moved(replay["root"])
fixtures = ROOT / "tests/fixtures/qe75_real"
for entry in replay["files"]:
    if sha(fixtures / entry["path"], text=False) != entry["sha256"]:
        raise SystemExit("replay fixture differs from the re-test pin: " + entry["path"])
source_deck = {"path": moved(RETEST["source_deck"]["path"]), "sha256": RETEST["source_deck"]["sha256"]}
if sha(ROOT / RETEST["source_deck"]["path"][len(OLD_PARENT) + 1:]) != source_deck["sha256"]:
    raise SystemExit("repo source deck differs from the re-test pin")
review = ROOT / REVIEW
if sha(review) != RETEST["source_review"]["sha256"]:
    raise SystemExit("source review differs from the re-test pin")
spec = {
    "schema": "pa-catalyst-o1-v1",
    "date": "2026-10-07",
    "target": RETEST["target"],
    "predecessor": {"slurm_job": "21075231", "slurm_state": "FAILED 3:0", "scientific_status": "INCONCLUSIVE",
                    "charged_cpu_su": 353.92, "spec_sha256": "4c2384c6375f1c7892d33d8f6c37478243f41af3da9dd0f9ec507bcd8423e435",
                    "cause": "registered continuity force gate (1e-5 Ry/bohr) below the SCF force precision at conv_thr 1e-6",
                    "readout": "docs/research/pa-fixed-geometry-diagnostic-readout-2026-10-06.md"},
    "decision_ref": "docs/research/pa-catalyst-o1-2026-10-07.md (decision of record, Frank, 2026-10-07: \"Ok do O1.\")",
    "source_deck": source_deck,
    "pw_x": RETEST["pw_x"],
    "mpirun": RETEST["mpirun"],
    "upfs": RETEST["upfs"],
    "dependencies": [{"path": PARENT + "/" + rel, "sha256": sha(ROOT / rel)} for rel in DEPENDENCIES],
    "source_review": {"path": PARENT + "/" + REVIEW, "sha256": sha(review)},
    "preflight_replay": replay,
    "initial_seed": RETEST["initial_seed"],
    "trial_parent": PARENT,
    "trial_root": PARENT + "/trial_results",
    "allocation": dict(RETEST["allocation"], time_limit_seconds=28800, max_cpu_su=1024),
    "caps": dict(RETEST["caps"], aggregate_seconds=28800),
    "parallel_shape": RETEST["parallel_shape"],
    "optional_negative_control": True,
    "estimated_cpu_su": [350, 550],
    "estimate_basis": "job 21075231 measured 353.92 SU for control, candidate, fresh and resumed calls (9,954 s); the registered negative-control call (three evaluations from the copied checkpoint) adds about 100 SU",
    "production_accepted": False,
}
assert RETEST["optional_negative_control"] is True
out = HERE / "launch_spec.json"
out.write_bytes((json.dumps(spec, indent=2) + "\n").encode("utf-8"))
print(sha(out))
