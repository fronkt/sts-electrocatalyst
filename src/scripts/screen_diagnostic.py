"""Explicit-composition MACE diagnostics, separate from selection and validation gates.

prepare freezes exact source fractions, sampling, model bytes and implementation hashes.
run checks those identities before evaluating; checkpoint/resume never silently retries an
error or changes a protocol. A completed diagnostic means execution finished, not QC passed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

IMPLEMENTATION = (
    "src/scripts/screen_diagnostic.py", "src/hea_oer/adsorption.py",
    "src/hea_oer/relax.py", "src/hea_oer/composition.py",
    "src/hea_oer/surfaces_rutile.py", "src/hea_oer/surfaces.py",
    "src/hea_oer/referencing.py", "src/hea_oer/descriptors.py",
    "src/hea_oer/data.py", "src/hea_oer/site_evidence.py",
)
SCHEMA = "screen-diagnostic-v1"


def sha256_file(path, *, normalize_lf=False):
    data = Path(path).read_bytes()
    if normalize_lf:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def positive(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be finite and positive")
    return value


def integer(value, label, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{label} must be an integer in [{low}, {high}]")
    return value


def validate_manifest(manifest):
    if manifest.get("schema") != SCHEMA:
        raise ValueError("unsupported manifest schema")
    supplied = manifest.get("manifest_id")
    if supplied != identity({k: v for k, v in manifest.items() if k != "manifest_id"}):
        raise ValueError("manifest identity mismatch")
    protocol = manifest["protocol"]
    if protocol["mode"] not in ("diagnostic", "feasibility"):
        raise ValueError("unknown diagnostic mode")
    positive(protocol["fmax_eV_A"], "fmax")
    integer(protocol["steps"], "steps", 1, 100000)
    integer(protocol["n_sites"], "n_sites", 1, 4)
    seeds = protocol["seeds"]
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be nonempty and unique")
    for seed in seeds:
        integer(seed, "seed", 0, 2**32 - 1)
    if protocol["supercell"] != [2, 2] or protocol["dtype"] != "float64":
        raise ValueError("this driver fixes a 2x2 rutile surface and float64")
    rows = manifest["candidates"]
    if not rows:
        raise ValueError("no candidates selected")
    ids, formulas, canonical = set(), set(), set()
    for row in rows:
        els, frs = row["elements"], row["fractions"]
        if not els or len(els) != len(frs) or len(set(els)) != len(els):
            raise ValueError("invalid composition elements")
        if not all(isinstance(el, str) and el and el.isalpha() for el in els):
            raise ValueError("invalid element symbol")
        for fraction in frs:
            positive(fraction, "fraction")
        if not math.isclose(sum(frs), 1, rel_tol=0, abs_tol=1e-10):
            raise ValueError("source fractions must sum to one; no renormalization")
        if row["candidate_id"] != identity({"elements": els, "fractions": frs}):
            raise ValueError("candidate identity mismatch")
        key = tuple(sorted(zip(els, frs)))
        if row["candidate_id"] in ids or row["formula"] in formulas or key in canonical:
            raise ValueError("duplicate candidate")
        if not isinstance(row["formula"], str) or not row["formula"]:
            raise ValueError("candidate needs a source label")
        ids.add(row["candidate_id"]); formulas.add(row["formula"]); canonical.add(key)
    return manifest


def prepare(source, formulas, model_file, *, seeds=(0, 1, 2), n_sites=4,
            fmax=.05, steps=300, mode="diagnostic"):
    source, model_file = Path(source), Path(model_file)
    data = json.loads(source.read_text(encoding="utf-8"))
    if data.get("status") != "complete":
        raise ValueError("source screen must be complete")
    if not formulas or len(set(formulas)) != len(formulas):
        raise ValueError("supply a nonempty unique explicit formula list")
    by_label = {}
    for row in data["rows"]:
        label = row["formula"]
        if label in by_label:
            raise ValueError("source contains duplicate labels")
        by_label[label] = row
    candidates = []
    for label in formulas:
        if label not in by_label:
            raise ValueError(f"candidate absent from source: {label}")
        row = by_label[label]
        comp = {"elements": list(row["elements"]), "fractions": list(row["fractions"])}
        candidates.append(dict(formula=label, candidate_id=identity(comp), **comp))
    result = dict(
        schema=SCHEMA,
        purpose="Historical-candidate diagnostic; not held-out evaluation or melt selection",
        source={"filename": source.name, "sha256_lf": sha256_file(source, normalize_lf=True)},
        model={"historical_label": data.get("model"), "filename": model_file.name,
               "sha256_bytes": sha256_file(model_file),
               "historical_weight_identity_established": False},
        implementation_sha256_lf={p: sha256_file(ROOT / p, normalize_lf=True) for p in IMPLEMENTATION},
        protocol={"mode": mode, "seeds": list(seeds), "n_sites": n_sites,
                  "supercell": [2, 2], "fmax_eV_A": fmax, "steps": steps,
                  "dtype": "float64", "surface": "rutile",
                  "aggregation": "legacy minimum retained, no QC replacement",
                  "sampling_role": "fixed diagnostic; no composition generalization"},
        candidates=candidates,
        work_estimate={"clean_slab_relaxations": len(candidates) * len(seeds),
                       "adsorbate_relaxations_upper": len(candidates) * len(seeds) * n_sites * 9,
                       "gas_relaxations_per_process": 2,
                       "wall_time_estimate_seconds": None},
    )
    result["manifest_id"] = identity(result)
    return validate_manifest(result)


def write_json_new(path, payload):
    path = Path(path)
    encoded = json.dumps(payload, indent=2, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(encoded)


def checkpoint(path, payload):
    # An exclusive lock in run() protects this replace across diagnostic workers.
    path = Path(path)
    encoded = json.dumps(payload, indent=2, allow_nan=False) + "\n"
    temp = path.with_name(path.name + ".pending")
    owns_temp = False
    try:
        with temp.open("x", encoding="utf-8", newline="\n") as handle:
            owns_temp = True
            handle.write(encoded)
        os.replace(temp, path)
    finally:
        if owns_temp and temp.exists():
            temp.unlink()


def environment(device):
    packages = {}
    for name in ("mace-torch", "torch", "ase", "numpy", "pymatgen", "scipy", "e3nn"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {"python": platform.python_version(), "platform": platform.platform(),
            "device": device, "packages": packages}


def run(manifest, model_file, out, *, device="cpu", resume=False,
        max_candidates=None, threads=2, backend_factory=None):
    validate_manifest(manifest)
    integer(threads, "threads", 1, 256)
    if max_candidates is not None:
        integer(max_candidates, "max_candidates", 1, len(manifest["candidates"]))
    if device not in ("cpu", "cuda"):
        raise ValueError("device must be cpu or cuda")
    model_file, out = Path(model_file).resolve(), Path(out).resolve()
    protected = {model_file, *(ROOT / p for p in IMPLEMENTATION)}
    if out in protected:
        raise ValueError("output would overwrite a protected input")
    if sha256_file(model_file) != manifest["model"]["sha256_bytes"]:
        raise ValueError("model bytes differ from manifest")
    for rel, expected in manifest["implementation_sha256_lf"].items():
        if rel not in IMPLEMENTATION or sha256_file(ROOT / rel, normalize_lf=True) != expected:
            raise ValueError(f"implementation differs from manifest: {rel}")
    if set(manifest["implementation_sha256_lf"]) != set(IMPLEMENTATION):
        raise ValueError("incomplete implementation identity")
    out.parent.mkdir(parents=True, exist_ok=True)
    lock = out.with_name(out.name + ".lock")
    with lock.open("x", encoding="utf-8") as handle:
        handle.write(str(os.getpid()))
    try:
        runtime = dict(environment(device), threads=threads)
        if out.exists():
            if not resume:
                raise FileExistsError("output exists; use --resume only for the same manifest and environment")
            payload = json.loads(out.read_text(encoding="utf-8"))
            if payload.get("manifest_id") != manifest["manifest_id"] or payload.get("manifest") != manifest:
                raise ValueError("resume manifest mismatch")
            if payload.get("environment") != runtime:
                raise ValueError("resume environment mismatch; use a separate output")
            if payload.get("results_sha256") != identity(payload.get("results", [])):
                raise ValueError("checkpoint result identity mismatch")
            expected_ids = [r["candidate_id"] for r in manifest["candidates"]]
            got_ids = [r["candidate_id"] for r in payload["results"]]
            if got_ids != expected_ids[:len(got_ids)]:
                raise ValueError("checkpoint does not contain a candidate prefix")
        elif resume:
            raise FileNotFoundError("no checkpoint to resume")
        else:
            payload = dict(schema=SCHEMA, manifest_id=manifest["manifest_id"], manifest=manifest,
                           status="pending", environment=runtime, results=[],
                           claims={"held_out_validation": False, "ranking_validated": False,
                                   "melt_selection": False, "force_convergence_implies_chemistry": False})
        def save():
            payload["results_sha256"] = identity(payload["results"])
            checkpoint(out, payload)
        remaining = manifest["candidates"][len(payload["results"]):]
        if not remaining:
            payload["status"] = "complete_with_errors" if any(
                r["status"] == "error" for r in payload["results"]) else "complete"
            save()
            return payload
        if max_candidates is not None:
            remaining = remaining[:max_candidates]
        payload["status"] = "running"
        save()
        backend = None
        from hea_oer.composition import Composition
        from hea_oer.descriptors import oer_overpotential
        from hea_oer.site_evidence import analyze_site_evidence
        for candidate in remaining:
            started = time.monotonic()
            record = {"candidate_id": candidate["candidate_id"], "formula": candidate["formula"]}
            comp = Composition(tuple(candidate["elements"]), tuple(candidate["fractions"]))
            try:
                if backend is None:
                    if backend_factory is None:
                        import torch
                        torch.set_num_threads(threads)
                        from hea_oer.adsorption import get_backend
                        backend_factory = lambda **kw: get_backend("mace", **kw)
                    protocol = manifest["protocol"]
                    backend = backend_factory(model=str(model_file), device=device,
                        dtype=protocol["dtype"], surface="rutile", size=(2, 2, 4),
                        fmax=protocol["fmax_eV_A"], steps=protocol["steps"],
                        n_sites=protocol["n_sites"], seed=protocol["seeds"][0],
                        seeds=tuple(protocol["seeds"]))
                triple = tuple(float(x) for x in backend.predict(comp))
                oer = oer_overpotential(*triple)
                row = dict(backend.site_records[comp.formula()])
                row.update(formula=candidate["formula"], elements=list(comp.elements),
                           fractions=list(comp.fractions), dG_OH=triple[0], dG_O=triple[1],
                           dG_OOH=triple[2], eta=float(oer.overpotential),
                           pls=int(oer.potential_limiting_step))
                protocol = manifest["protocol"]
                observed = [(r["seed"], r["site_index"]) for r in row.get("per_site_records", [])]
                expected = [(s, i) for s in protocol["seeds"] for i in range(protocol["n_sites"])]
                row["sampling_check"] = {"expected_pairs": [list(x) for x in expected],
                                         "observed_pairs": [list(x) for x in observed],
                                         "complete": sorted(observed) == sorted(expected)}
                # Strict JSON check before any success record, including nested geometry.
                identity(row)
                record.update(status="evaluated", row=row)
                if not row["sampling_check"]["complete"]:
                    raise ValueError("actual site coverage differs from manifest")
                record["site_evidence"] = analyze_site_evidence(row, corrections=[])
            except Exception as error:
                # Keep raw evidence if analysis fails. A new manifest/output is required
                # to retry; resume retains this error in the original denominator.
                record.update(status="error", error={"type": type(error).__name__, "message": str(error)})
                if backend is not None:
                    partial = getattr(backend, "partial_site_records", {}).get(comp.formula())
                    if partial is not None:
                        record["partial_evidence"] = partial
                try:
                    identity(record)
                except (ValueError, TypeError):
                    record.pop("row", None)
                    record.pop("partial_evidence", None)
                    record["raw_evidence_not_json_finite"] = True
            record["seconds"] = round(time.monotonic() - started, 6)
            payload["results"].append(record)
            print(json.dumps({k: record[k] for k in ("formula", "status", "seconds")}), flush=True)
            save()
        all_done = len(payload["results"]) == len(manifest["candidates"])
        payload["status"] = ("complete_with_errors" if any(r["status"] == "error" for r in payload["results"])
                             else "complete") if all_done else "partial"
        save()
        return payload
    finally:
        lock.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--formula", action="append", required=True)
    p.add_argument("--model-file", type=Path, required=True)
    p.add_argument("--seeds", default="0,1,2")
    p.add_argument("--n-sites", type=int, default=4)
    p.add_argument("--steps", type=int, default=300)
    p.add_argument("--fmax", type=float, default=.05)
    p.add_argument("--mode", choices=("diagnostic", "feasibility"), default="diagnostic")
    p.add_argument("--out", type=Path, required=True)
    r = commands.add_parser("run")
    r.add_argument("--manifest", type=Path, required=True)
    r.add_argument("--model-file", type=Path, required=True)
    r.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    r.add_argument("--threads", type=int, default=2)
    r.add_argument("--resume", action="store_true")
    r.add_argument("--max-candidates", type=int)
    r.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        result = prepare(args.source, args.formula, args.model_file,
                         seeds=tuple(int(s) for s in args.seeds.split(",")), n_sites=args.n_sites,
                         fmax=args.fmax, steps=args.steps, mode=args.mode)
        write_json_new(args.out, result)
        print(result["manifest_id"])
        return 0
    if args.out.resolve() == args.manifest.resolve():
        raise ValueError("output must not overwrite manifest")
    result = run(json.loads(args.manifest.read_text(encoding="utf-8")), args.model_file,
                 args.out, device=args.device, resume=args.resume,
                 max_candidates=args.max_candidates, threads=args.threads)
    print(result["status"])
    return 1 if result["status"] == "complete_with_errors" else 0


if __name__ == "__main__":
    raise SystemExit(main())
