"""Reproduce the two hypothesis-driven Cr-site chains with separate manifests."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time

os.environ.setdefault("TORCHINDUCTOR_CACHE_DIR", str(Path(tempfile.gettempdir()) / "sts-torch-cache"))
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from scripts.screen_diagnostic import prepare, run, write_json_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-file", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--arm", choices=("equiatomic", "leader"), required=True)
    args = parser.parse_args()
    formula, seed = {"equiatomic": ("Fe25Co25Ni25Cr25", 2),
                     "leader": ("Ni31Cr29Cu5Mn35", 0)}[args.arm]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest = prepare(ROOT / "results/r4_screen_box.json", [formula], args.model_file,
                       seeds=(seed,), n_sites=1, fmax=0.05, steps=300)
    write_json_new(args.out_dir / (args.arm + "_manifest.json"), manifest)
    started = time.monotonic()
    result = run(manifest, args.model_file, args.out_dir / (args.arm + "_result.json"), threads=2)
    print(json.dumps({"arm": args.arm, "end_to_end_seconds": time.monotonic() - started,
                      "status": result["status"]}), flush=True)
    return 1 if result["status"] == "complete_with_errors" else 0


if __name__ == "__main__":
    raise SystemExit(main())
