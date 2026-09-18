"""Independent verifier: re-hash every (path, sha256) entry recorded in the track's result JSONs."""
import json, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PREFIX = str(ROOT) + "\\"


def walk(o):
    if isinstance(o, dict):
        if "path" in o and isinstance(o.get("sha256"), str) and len(o["sha256"]) == 64:
            yield o["path"], o["sha256"]
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


out = {}
R = ROOT / "results/lowtail_dft_2026-09-16"
for f in ["zero_compute/input_manifest.json", "relax_survey_manifest.json", "deck_plan.json", "zero_compute/zero_compute_readout.json",
          "scorer_crosscheck.json", "mace_start_check.json", "operating_decisions.json"]:
    d = json.loads((R / f).read_text())
    n, bad, missing = 0, [], []
    for p, h in walk(d):
        s = str(p)
        if s.startswith(PREFIX):
            s = s[len(PREFIX):]
        pp = ROOT / s.replace("\\", "/")
        if not pp.exists():
            missing.append(p)
            continue
        n += 1
        if hashlib.sha256(pp.read_bytes()).hexdigest() != h:
            bad.append(p)
    out[f] = dict(checked=n, bad=bad, missing=missing)
    print(f, "checked", n, "bad", bad[:5], "missing", missing[:5])
d = json.loads((R / "deck_plan.json").read_text())
for p, h in d["manifests"].items():
    print(p, hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h)
print("survey manifest", hashlib.sha256((R / "relax_survey_manifest.json").read_bytes()).hexdigest() == d["cost_inputs"]["survey_manifest"]["sha256"])
z = json.loads((R / "zero_compute/zero_compute_readout.json").read_text())["manifest_sha256"]
print("zero manifest", z == hashlib.sha256((R / "zero_compute/input_manifest.json").read_bytes()).hexdigest())
(Path(__file__).with_name("v2_hashes.json")).write_text(json.dumps(out, indent=1))
