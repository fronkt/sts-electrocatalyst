"""CENSUS-1b driver: *O2 fragment completion relaxations on the CENSUS-1 results (docs/91:36).

Reads the twelve CENSUS-1 results (results/site_census_2026-09-06/results/mpa0__<formula>_result.json,
queue order of site_census_plan.BOX_TWELVE), selects every site whose OOH endpoint is
*O2 + H_b (hea_oer.o2_fragment.select_sites), and writes

    <out>            {formula: {"seed/site_index": {energy_eV, E_O2_gas_eV, converged_by_force, ...}}}
                     the file site_census_readout.py --o2-records consumes; nothing but formulas
                     at the top level, because load_o2_records treats every top-level key as a
                     formula (site_census_readout.py:326-337)
    <out>'s sibling o2_audit.json
                     the header (the --dated-line text verbatim and where it was found, model
                     file and sha256, input result hashes sha256_lf, implementation hashes,
                     environment, protocol), every selection with its reason, every relaxed
                     geometry, both O2 energies per composition, per-site failures and the
                     timing; checkpointed after every composition.

--dry-run lists the qualifying sites per composition with counts and the planned relaxations
and exits without importing torch or mace and without writing anything.

A run that relaxes is gated (docs/91 section 5, line 90: a CENSUS-1b module needs its own
dated line before it runs): --dated-line must carry the dated form ``CENSUS-1b YYYY-MM-DD:``
with a real date (a blank ``2026-09-__`` slot is refused) and the text must be present
verbatim in --dated-line-source (default docs/43-prereg-week1-factorial.md, opened read-only
and never written); the text is recorded in the audit header and not otherwise interpreted.
The gate cannot establish the line's origin; it establishes that a dated line exists.

The run refuses an output or audit file that exists (--resume continues a checkpointed audit
whose header matches, reusing its checkpointed O2 energies), refuses an --out inside the
census tree other than under results/site_census_2026-09-06/o2_fragment/ (status.json,
manifests/, results/, logs/, readout/ and torch-cache/ are the runner's and the readout's;
docs/91:73 enumerates that tree and the o2_fragment/ directory is this module's addition to
it), takes <out>.lock (a lock whose recorded pid is dead is removed; a live one is refused),
and hashes the model file against every input's manifest.model.sha256_bytes before any
relaxation. fmax, steps and dtype come from each result's embedded manifest protocol. The
O2 cell choice is --o2-cell {slab,box12}, default slab (a reading of docs/91:36, recorded in
the header; hea_oer.o2_fragment module docstring). Every checkpoint write is a temp file
renamed into place with the same retry the census runner uses (a reader holding the JSON
open on Windows raises PermissionError WinError 5 on the rename). A failing fragment
relaxation is recorded per site and the run continues; any other failure marks the audit
header status "failed" with the composition and error text before the process exits, so a
checkpoint is never left reading "running" after the process is gone.

    python src/scripts/site_census_o2_fragment.py --dry-run
    python src/scripts/site_census_o2_fragment.py --dated-line "<text>" [--o2-cell slab] [--threads 2]

Nothing here scores a docs/43 prediction, registers a threshold, moves a banked value or
enters a ranking rule; the output is a fragment-binding diagnostic (CALIBRATION, docs/43:3447-3455).
"""
from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from hea_oer import o2_fragment as fragment  # noqa: E402
from hea_oer import site_integrity as integrity  # noqa: E402
from scripts import site_census_plan as plan  # noqa: E402

AUDIT_SCHEMA = "census-1b-o2-fragment-audit-v1"
OUT_SUBDIR = "o2_fragment"
DEFAULT_OUT = plan.CENSUS_DIR / OUT_SUBDIR / "o2_records.json"
AUDIT_NAME = "o2_audit.json"
DEFAULT_DATED_LINE_SOURCE = ROOT / "docs/43-prereg-week1-factorial.md"
#: The dated form a CENSUS-1b line must carry; a blank slot (2026-09-__) does not match.
DATED_LINE_PATTERN = re.compile(r"CENSUS-1b (\d{4})-(\d{2})-(\d{2}):")
#: Files whose LF hash is recorded in the audit header (identity of what ran).
IMPLEMENTATION = ("src/hea_oer/o2_fragment.py", "src/scripts/site_census_o2_fragment.py",
                  "src/hea_oer/relax.py", "src/hea_oer/site_integrity.py", "src/scripts/site_census_plan.py")
ROLE = ("CENSUS-1b fragment-binding diagnostic (docs/91:36); enters no ranking rule (docs/91 "
        "readout (c)); scores no docs/43 prediction, registers no threshold, fills no entrant "
        "slot, moves no banked value; reportable only as CALIBRATION under docs/43:3447-3455")
O2_CELL_NOTE = ("o2_cell is a reading of docs/91:36 ('the O2 molecule in the same model and cell'), "
                "not a pre-stated value: 'slab' relaxes O2 once per distinct slab cell (twelve "
                "composition-specific energies); 'box12' uses the project's 12 A gas box; both "
                "energies are recorded in every record and the choice is named in it")
REPLACE_ATTEMPTS = 40
REPLACE_DELAY_SECONDS = 0.25
STILL_ACTIVE = 259


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def sha256_file(path, *, normalize_lf=False):
    data = Path(path).read_bytes()
    if normalize_lf:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def environment(threads):
    packages = {}
    for name in ("mace-torch", "torch", "ase", "numpy", "e3nn", "scipy"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {"python": platform.python_version(), "platform": platform.platform(),
            "device": "cpu", "threads": int(threads), "packages": packages,
            "torchinductor_cache_dir": os.environ.get("TORCHINDUCTOR_CACHE_DIR")}


def replace_with_retry(temp, target, attempts=None, delay=None):
    """os.replace that waits out a reader holding the target open (Windows: a file another
    process has open without FILE_SHARE_DELETE cannot be replaced, PermissionError WinError 5
    or 32); retries attempts x delay seconds (module defaults 40 x 0.25 s), then re-raises
    the last error."""
    attempts = REPLACE_ATTEMPTS if attempts is None else attempts
    delay = REPLACE_DELAY_SECONDS if delay is None else delay
    last = None
    for _ in range(max(1, int(attempts))):
        try:
            os.replace(temp, target)
            return
        except PermissionError as error:
            last = error
            time.sleep(delay)
    raise last


def atomic_write_json(path, payload):
    """Write JSON to <path>.pending and rename it into place. The .pending name belongs to
    the process holding <out>.lock, so a stale one left by a crash between write and rename
    is overwritten, not refused."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, allow_nan=False) + "\n"
    temp = path.with_name(path.name + ".pending")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(encoded)
    replace_with_retry(temp, path)


def pid_alive(pid):
    """True when a process with this pid is running. Windows via kernel32 (os.kill with
    signal 0 would TERMINATE the process there); elsewhere kill 0."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return False
            return code.value == STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def acquire_lock(lock):
    """Take <out>.lock. A lock whose recorded pid is dead is stale and removed (with a
    message); one whose pid is alive, or whose content is not a pid, is refused."""
    lock = Path(lock)
    if lock.exists():
        content = lock.read_text(encoding="utf-8", errors="replace").strip()
        if pid_alive(content):
            raise SystemExit(f"refused: lock {lock} is held by live pid {content}")
        if not content.isdigit():
            raise SystemExit(f"refused: lock {lock} carries no pid ({content!r}); remove it by hand if no run is live")
        print(json.dumps(dict(time=now(), message=f"stale lock removed: {lock} (pid {content} is not running)")),
              flush=True)
        lock.unlink()
    with lock.open("x", encoding="utf-8") as handle:
        handle.write(str(os.getpid()))


def check_out_path(out, census_dir=None):
    """Refuse an output inside the census tree unless it is under <census>/o2_fragment/."""
    census = Path(plan.CENSUS_DIR if census_dir is None else census_dir).resolve()
    allowed = census / OUT_SUBDIR
    if out == census or census in out.parents:
        if not (out.parent == allowed or allowed in out.parents):
            raise SystemExit(f"refused: --out {out} lies inside the census tree {census} outside {allowed}; "
                             "status.json, manifests/, results/, logs/, readout/ and torch-cache/ are not "
                             "this module's to write (docs/91:73)")


def check_dated_line(text, source):
    """The docs/91:90 gate: a dated CENSUS-1b line, present verbatim in `source` (read-only).
    Returns dict(source, found, date). Raises SystemExit with 'refused:' otherwise."""
    text = (text or "").strip()
    if not text:
        raise SystemExit("refused: a relaxation run needs --dated-line \"<text>\" (docs/91 section 5, line 90); "
                         "use --dry-run to list the qualifying sites without relaxing")
    match = DATED_LINE_PATTERN.search(text)
    if match is None:
        raise SystemExit("refused: --dated-line must carry the dated form 'CENSUS-1b YYYY-MM-DD:' with a real "
                         "date (a blank 2026-09-__ slot is not a dated line); got " + repr(text))
    try:
        date = dt.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError as error:
        raise SystemExit(f"refused: --dated-line date is not a calendar date: {error}") from error
    source = Path(source)
    if not source.exists():
        raise SystemExit("refused: --dated-line-source does not exist: " + str(source))
    body = source.read_text(encoding="utf-8", errors="replace")
    if text not in body:
        raise SystemExit(f"refused: the dated line is not present verbatim in {source}; a CENSUS-1b run needs "
                         "its own dated line there first (docs/91:90)")
    return dict(source=str(source.resolve()), found=True, date=date.isoformat())


# ----------------------------------------------------------------------------------------
# Inputs
# ----------------------------------------------------------------------------------------

def collect(results_dir, manifest_dir, formulas):
    """CENSUS-1 results in queue order: {formula: dict(path, sha256_lf, result, row, protocol,
    model, manifest_id, manifest_file_id)} plus the list of missing/unusable ones."""
    results_dir, manifest_dir = Path(results_dir), Path(manifest_dir) if manifest_dir else None
    loaded, missing = {}, []
    for formula in formulas:
        stem = f"mpa0__{formula}"
        if plan.parse_stem(stem)["arm"] != "CENSUS-1":
            raise ValueError("not a CENSUS-1 manifest: " + stem)
        path = results_dir / (stem + "_result.json")
        if not path.exists():
            missing.append(dict(formula=formula, reason="result missing", path=str(path)))
            continue
        result = load_json(path)
        manifest = result.get("manifest") or {}
        if result.get("manifest_id") != manifest.get("manifest_id"):
            missing.append(dict(formula=formula, reason="result manifest_id differs from its embedded manifest"))
            continue
        if result.get("status") != "complete":
            missing.append(dict(formula=formula, reason=f"result status {result.get('status')}"))
            continue
        candidates = result.get("results") or []
        if len(candidates) != 1 or candidates[0].get("status") != "evaluated" or candidates[0].get("formula") != formula:
            missing.append(dict(formula=formula, reason="result does not carry one evaluated candidate for the formula"))
            continue
        manifest_file_id = None
        if manifest_dir is not None:
            manifest_path = manifest_dir / (stem + ".json")
            if manifest_path.exists():
                manifest_file_id = load_json(manifest_path).get("manifest_id")
                if manifest_file_id != result["manifest_id"]:
                    missing.append(dict(formula=formula, reason="manifest file manifest_id differs from the result"))
                    continue
        loaded[formula] = dict(
            path=path, sha256_lf=sha256_file(path, normalize_lf=True), result=result,
            row=candidates[0]["row"], protocol=manifest.get("protocol") or {},
            model=manifest.get("model") or {}, manifest_id=result["manifest_id"],
            manifest_file_id=manifest_file_id, candidate_seconds=candidates[0].get("seconds"))
    return loaded, missing


def selection_table(loaded, thresholds):
    """{formula: dict(n_sites, n_qualifying, keys, reasons={reason: count}, selection)}."""
    table = {}
    for formula, item in loaded.items():
        selection = fragment.select_sites(item["row"], thresholds)
        reasons = {}
        for s in selection:
            if not s["qualifies"]:
                reasons[s["reason_class"]] = reasons.get(s["reason_class"], 0) + 1
        table[formula] = dict(
            n_sites=len(selection), n_qualifying=sum(1 for s in selection if s["qualifies"]),
            keys=[s["key"] for s in selection if s["qualifies"]],
            qualifying=[dict(key=s["key"], initial_metal=s["initial_metal"], eta_V=s["eta_V"],
                             tier=s["ooh"]["bond_tier"], m_o_A=s["ooh"]["m_o_A"], o_o_A=s["ooh"]["o_o_A"],
                             o_o_class=s["ooh"]["o_o_class"], binding_metal=s["ooh"]["binding_metal"],
                             ooh_converged_by_force=s["ooh"]["converged_by_force"])
                        for s in selection if s["qualifies"]],
            reasons=reasons, selection=selection,
            cell_id=_row_cell_id(item["row"]))
    return table


def _row_cell_id(row):
    ids = set()
    for site in row.get("per_site_records", []):
        for state in (site.get("relaxed_states") or {}).values():
            if state and state.get("cell_A") is not None:
                ids.add(fragment.cell_id(state["cell_A"]))
    return sorted(ids)


def print_dry_run(table, missing, model_file, o2_cell, thresholds):
    print("CENSUS-1b dry run: site selection only, no model loaded, nothing written")
    print(f"model file (not hashed in a dry run): {model_file} (exists: {Path(model_file).exists()})")
    print(f"o2_cell: {o2_cell} (a reading of docs/91:36, not pre-stated; both O2 energies are recorded)")
    print(f"qualifying rule: OOH pathway_state '{fragment.QUALIFYING_PATHWAY_STATE}' = docs/91:36 "
          f"'H-TRANSFERRED, fragment bound or weak' (H within {thresholds.h_bond_max_A} A of a slab O, "
          f"M-O < {thresholds.desorbed_min_A} A) read through readout (c) docs/91:63, which adds "
          f"O-O not cleaved (<= {thresholds.ooh_like_max_A} A); the added condition excludes no CENSUS-1 site")
    print(f"{'formula':<20} {'sites':>5} {'qual':>4}  {'not qualifying by class':<44}  "
          "qualifying sites: seed/site enumerated->binding metal, tier, M-O/A, O-O/A, OOH convergence")
    total_sites, total_q, cells = 0, 0, set()
    for formula, entry in table.items():
        total_sites += entry["n_sites"]
        total_q += entry["n_qualifying"]
        cells.update(entry["cell_id"])
        keys = "; ".join(f"{q['key']} {q['initial_metal']}->{q['binding_metal']} {q['tier']} {q['m_o_A']:.4f} "
                         f"{q['o_o_A']:.4f} {'conv' if q['ooh_converged_by_force'] is True else 'UNCONV'}"
                         for q in entry["qualifying"]) or "-"
        classes = ", ".join(f"{cls} {count}" for cls, count in
                            sorted(entry["reasons"].items(), key=lambda kv: (-kv[1], kv[0]))) or "-"
        print(f"{formula:<20} {entry['n_sites']:>5} {entry['n_qualifying']:>4}  {classes:<44}  {keys}")
    for item in missing:
        print(f"{item['formula']:<20} MISSING: {item['reason']}")
    n_o2 = len(cells)
    print(f"total: {len(table)} compositions read, {len(missing)} missing, {total_sites} sites, "
          f"{total_q} qualifying fragment relaxations + {n_o2} slab-cell O2 + 1 box12 O2 = "
          f"{total_q + n_o2 + 1} relaxations (docs/91:36 bound: at most 144 + 1; a composition with no "
          "qualifying site still relaxes O2 in its cell so every composition carries the pair)")
    summary = dict(dry_run=True, compositions=len(table), missing=[m["formula"] for m in missing],
                   sites=total_sites, qualifying_total=total_q, distinct_slab_cells=n_o2,
                   planned_relaxations=total_q + n_o2 + 1,
                   per_formula={f: dict(n_sites=e["n_sites"], n_qualifying=e["n_qualifying"], keys=e["keys"])
                                for f, e in table.items()})
    print(json.dumps(summary))
    return summary


# ----------------------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------------------

def default_calculator_factory(model_file, threads, dtype):
    def factory():
        import torch
        torch.set_num_threads(int(threads))
        from hea_oer.relax import make_mace_calculator
        return make_mace_calculator(str(model_file), "cpu", dtype)
    return factory


def build_header(args, loaded, model_sha, table, thresholds, dated_line_check):
    from dataclasses import asdict
    return dict(
        schema=AUDIT_SCHEMA, role=ROLE, dated_line=args.dated_line, dated_line_check=dated_line_check,
        started=now(), finished=None, status="running", o2_cell=args.o2_cell, o2_cell_note=O2_CELL_NOTE,
        output_note=(f"{OUT_SUBDIR}/ under the census tree is this module's addition to the tree "
                     "enumerated at docs/91:73; the runner's and the readout's directories are refused"),
        model=dict(file=str(Path(args.model_file).resolve()), sha256_bytes=model_sha,
                   manifest_sha256_bytes={f: item["model"].get("sha256_bytes") for f, item in loaded.items()},
                   manifest_filename={f: item["model"].get("filename") for f, item in loaded.items()},
                   filename_matches_manifest={f: Path(args.model_file).name == item["model"].get("filename")
                                              for f, item in loaded.items()}),
        protocol={f: dict(fmax_eV_A=item["protocol"].get("fmax_eV_A"), steps=item["protocol"].get("steps"),
                          dtype=item["protocol"].get("dtype")) for f, item in loaded.items()},
        implementation_sha256_lf={rel: sha256_file(ROOT / rel, normalize_lf=True) for rel in IMPLEMENTATION},
        environment=environment(args.threads),
        thresholds=asdict(thresholds),
        inputs={f: dict(path=str(item["path"]), sha256_lf=item["sha256_lf"], manifest_id=item["manifest_id"],
                        manifest_file_id=item["manifest_file_id"], census_candidate_seconds=item["candidate_seconds"],
                        n_sites=table[f]["n_sites"], n_qualifying=table[f]["n_qualifying"],
                        qualifying_keys=table[f]["keys"]) for f, item in loaded.items()},
        readout_keys=list(fragment.READOUT_KEYS),
        zpe_ts_note="no ZPE-TS enters the readout record; site_integrity.o2_fragment_diagnostic applies the "
                    "Proposed 0.05 eV (docs/91:36, CENSUS-7 slot) through site_census_readout.py --o2-records; "
                    "the audit's fragment blocks carry the diagnostic at "
                    + " / ".join(f"{z:.2f}" for z in fragment.ZPE_TS_REPORTED_EV) + " eV for both O2 cells",
        runs=[],
    )


def records_from_audit(audit):
    return {formula: comp["records"] for formula, comp in audit["compositions"].items()}


def check_resume(audit, header, loaded):
    if audit.get("schema") != AUDIT_SCHEMA:
        raise ValueError("resume: audit schema differs")
    old = audit["header"]
    for key in ("dated_line", "o2_cell"):
        if old.get(key) != header.get(key):
            raise ValueError(f"resume: {key} differs from the checkpointed audit")
    if old["model"]["sha256_bytes"] != header["model"]["sha256_bytes"]:
        raise ValueError("resume: model bytes differ from the checkpointed audit")
    if old["environment"] != header["environment"]:
        raise ValueError("resume: environment differs from the checkpointed audit; use a separate output")
    if old["implementation_sha256_lf"] != header["implementation_sha256_lf"]:
        raise ValueError("resume: implementation differs from the checkpointed audit")
    for formula in audit["compositions"]:
        if formula not in loaded:
            raise ValueError(f"resume: checkpointed composition {formula} is not among the inputs")
        if old["inputs"][formula]["sha256_lf"] != loaded[formula]["sha256_lf"]:
            raise ValueError(f"resume: input result for {formula} differs from the checkpointed audit")


def run(args, calculator_factory=None):
    thresholds = integrity.DEFAULT_THRESHOLDS
    formulas = list(args.formula) if args.formula else list(plan.BOX_TWELVE)
    for formula in formulas:
        if formula not in plan.BOX_TWELVE:
            raise SystemExit("formula outside the CENSUS-1 box: " + formula)
    loaded, missing = collect(args.results_dir, args.manifest_dir, formulas)
    table = selection_table(loaded, thresholds)
    if args.dry_run:
        print_dry_run(table, missing, args.model_file, args.o2_cell, thresholds)
        return 0
    dated_line_check = check_dated_line(args.dated_line, args.dated_line_source)
    if missing and not args.partial:
        names = ", ".join(f"{m['formula']} ({m['reason']})" for m in missing)
        raise SystemExit("refused: CENSUS-1 incomplete; rerun with --partial to run on what exists: " + names)
    if not loaded:
        raise SystemExit("refused: no CENSUS-1 result to run on")
    out = Path(args.out).resolve()
    audit_path = out.with_name(AUDIT_NAME)
    if out.suffix != ".json" or audit_path == out:
        raise SystemExit("refused: --out must be a .json path")
    check_out_path(out)
    if (out.exists() or audit_path.exists()) and not args.resume:
        raise SystemExit(f"refused: output exists ({out} / {audit_path}); no overwrite; --resume continues a checkpoint")
    if args.resume and not audit_path.exists():
        raise SystemExit("refused: --resume without a checkpointed audit at " + str(audit_path))
    model_file = Path(args.model_file)
    if not model_file.exists():
        raise SystemExit("refused: model file missing: " + str(model_file))
    model_sha = sha256_file(model_file)
    for formula, item in loaded.items():
        expected = item["model"].get("sha256_bytes")
        if expected != model_sha:
            raise SystemExit(f"refused: model bytes {model_sha} differ from the manifest of {formula} ({expected})")
    dtypes = {item["protocol"].get("dtype") for item in loaded.values()}
    if len(dtypes) != 1:
        raise SystemExit("refused: inputs disagree on dtype: " + ", ".join(map(str, dtypes)))
    dtype = dtypes.pop() or fragment.DEFAULT_DTYPE
    # The same inductor cache the census runner pins for its workers (site_census_runner.child_env),
    # recorded in the environment block; set before the header so a resume compares like with like.
    os.environ.setdefault("TORCHINDUCTOR_CACHE_DIR", str(plan.CENSUS_DIR / "torch-cache"))
    header = build_header(args, loaded, model_sha, table, thresholds, dated_line_check)

    out.parent.mkdir(parents=True, exist_ok=True)
    lock = out.with_name(out.name + ".lock")
    acquire_lock(lock)
    try:
        if args.resume:
            audit = load_json(audit_path)
            try:
                check_resume(audit, header, loaded)
            except ValueError as error:
                raise SystemExit("refused: " + str(error)) from error
            remaining = [f for f in loaded if f not in audit["compositions"]]
            if not remaining:
                print(json.dumps(dict(status=audit["header"].get("status"), message="nothing left to do",
                                      compositions=len(audit["compositions"]), out=str(out), audit=str(audit_path))))
                return 0
            audit["header"].update(status="running", resumed=(audit["header"].get("resumed") or []) + [now()])
            audit["header"].setdefault("runs", [])
        else:
            audit = dict(schema=AUDIT_SCHEMA, header=header, compositions={})
        completed = set(audit["compositions"])
        o2_cache = fragment.o2_cache_from_audits(audit["compositions"].values())
        current = {"formula": None}
        this_run = dict(started=now(), finished=None, wall_seconds=None,
                        compositions=[f for f in loaded if f not in completed],
                        o2_cells_from_checkpoint=sorted(o2_cache))

        def save():
            atomic_write_json(audit_path, audit)
            atomic_write_json(out, records_from_audit(audit))

        def log(message):
            print(json.dumps(dict(time=now(), message=message)), flush=True)

        def on_composition_start(formula):
            current["formula"] = formula

        def on_composition(formula, result):
            current["formula"] = None
            audit["compositions"][formula] = dict(
                finished=now(), records=result["records"], input_sha256_lf=loaded[formula]["sha256_lf"],
                **result["audit"])
            save()
            frag = result["audit"]["fragments"]
            print(json.dumps(dict(formula=formula, n_qualifying=result["audit"]["n_qualifying"],
                                  n_relaxed=sum(1 for r in frag.values() if r.get("status") == "relaxed"),
                                  n_failed=result["audit"]["n_failed"],
                                  n_converged=sum(1 for r in result["records"].values()
                                                  if r["converged_by_force"] is True),
                                  seconds=result["audit"]["seconds"])), flush=True)

        def finish(status, **extra):
            this_run.update(finished=now(), wall_seconds=round(time.monotonic() - started, 6))
            audit["header"]["runs"].append(this_run)
            audit["header"].update(status=status, finished=now(),
                                   wall_seconds=round(sum(r["wall_seconds"] or 0 for r in audit["header"]["runs"]), 6),
                                   missing=missing, **extra)
            save()

        started = time.monotonic()
        save()
        factory = calculator_factory or default_calculator_factory(model_file, args.threads, dtype)
        try:
            fragment.run_census({f: item["row"] for f, item in loaded.items()}, factory,
                                protocol_by_formula={f: item["protocol"] for f, item in loaded.items()},
                                o2_cell=args.o2_cell, thresholds=thresholds, completed=completed,
                                on_composition=on_composition, on_composition_start=on_composition_start,
                                o2_cache=o2_cache, log=log)
        except KeyboardInterrupt:
            finish("interrupted", failure=dict(formula=current["formula"], error="KeyboardInterrupt", time=now()))
            raise
        except Exception as error:  # noqa: BLE001 - the checkpoint must record why the process is gone
            finish("failed", failure=dict(formula=current["formula"], error=f"{type(error).__name__}: {error}",
                                          time=now()))
            raise SystemExit(f"failed: {type(error).__name__}: {error} (composition {current['formula']}; "
                             f"audit header status 'failed' written to {audit_path})") from error
        finish("complete")
    finally:
        lock.unlink()
    n = sum(len(c["records"]) for c in audit["compositions"].values())
    n_failed = sum(c.get("n_failed", 0) for c in audit["compositions"].values())
    print(json.dumps(dict(status="complete", compositions=len(audit["compositions"]), records=n,
                          failed_sites=n_failed, out=str(out), audit=str(audit_path))))
    return 0


def main(argv=None, calculator_factory=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results-dir", type=Path, default=plan.RESULT_DIR)
    parser.add_argument("--manifest-dir", type=Path, default=plan.MANIFEST_DIR,
                        help="manifest files whose manifest_id is cross-checked when present")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help=f"records JSON for site_census_readout.py --o2-records; {AUDIT_NAME} is written beside it")
    parser.add_argument("--dry-run", action="store_true", help="list qualifying sites and exit; no model, no output")
    parser.add_argument("--model-file", type=Path, default=plan.model_path("mpa0"),
                        help="checkpoint; its sha256 must equal every input manifest's model.sha256_bytes")
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--dated-line", default=None,
                        help="required for any run that relaxes: the dated form 'CENSUS-1b YYYY-MM-DD: ...', "
                             "present verbatim in --dated-line-source; recorded verbatim in the audit header")
    parser.add_argument("--dated-line-source", type=Path, default=DEFAULT_DATED_LINE_SOURCE,
                        help="file the dated line must be present in (opened read-only, never written)")
    parser.add_argument("--o2-cell", choices=fragment.O2_CELL_CHOICES, default="slab",
                        help="which O2 energy feeds E_O2_gas_eV; the other is recorded beside it")
    parser.add_argument("--formula", action="append", default=None, help="restrict to a composition (repeatable)")
    parser.add_argument("--partial", action="store_true", help="run on the CENSUS-1 results that exist")
    parser.add_argument("--resume", action="store_true", help="continue a checkpointed audit with the same header")
    args = parser.parse_args(argv)
    if args.threads < 1:
        parser.error("--threads must be positive")
    return run(args, calculator_factory)


if __name__ == "__main__":
    raise SystemExit(main())
