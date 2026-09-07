#!/usr/bin/env python3
"""Isolated HEA spin-start and numerical SCF controls; never submits a job.

Usage: python src/dft/build_hea_controls.py [--check]
The four retained branch endpoints are hash-verified by build_hea_panel.
All 48 decks retain their exact geometry, cell, charge, constraints and U values.
--check requires every expected artifact and compares its bytes without writing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hea_deck as hd  # noqa: E402
import build_hea_panel as panel  # noqa: E402
import hea_cost_model as cm  # noqa: E402

REPO = hd.REPO
OUT = REPO / "runs" / "hea" / "controls_2026-09-07"
MANIFEST = REPO / "runs" / "hea" / "m_controls_2026-09-07.txt"
SMOKE_MANIFEST = REPO / "runs" / "hea" / "m_controls_2026-09-07_smoke.txt"
PROJECTORS = ("atomic", "ortho")
STATE_LABELS = ("equiatomic_pull2.10", "equiatomic_builder", "leader_builder", "leader_pull2.10")
NUMERICAL_LABELS = ("leader_builder", "leader_pull2.10")
NTYP_MAX = 10  # runs/a0/cell/ref__2x1v__u715.out:23, Anvil PWSCF v7.5
SPIN_MODES = ("fm", "metal_alternating", "fragment", "metal_alternating_fragment")
# Each numerical perturbation changes exactly one input setting from the baseline.
NUMERICAL = {
    "scf_1e8": ("conv_thr", "1.0d-8"),
    "wfc100": ("ecutwfc", "100.0"),
    "rho800": ("ecutrho", "800.0"),
    "k6x3": ("mesh", (6, 3, 1)),
    "smear005": ("degauss", "0.005"),
}
CONTROL_NK = {"k6x3": 4}  # keep physical mesh; reduce modeled repeated per-pool memory
BASE_SETTINGS = {"conv_thr": "1.0d-6", "ecutwfc": "80.0", "ecutrho": "640.0", "degauss": "0.01"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def species_plan(symbols, n_slab: int, mode: str, free_moment: float | None = None) -> dict:
    """Deterministic same-element splits with explicit original-element mappings.

    metal_alternating assigns +,- in retained atom-index order within selected metals.
    Reserve one O split even without fragment spin, preserving the same metal texture
    across the two metal modes within the banked Anvil binary ntypx=10 limit.
    This is an AFM-like seed, not a claim of crystallographic AFM or net zero moment.
    Fragment O starts use the fractional-polarization convention compatible with QE 7.2.
    The target 1 or 2 muB is only an initial guess, not constrained magnetization.
    """
    if mode not in SPIN_MODES:
        raise hd.BuildError(f"unknown spin mode {mode!r}")
    symbols = list(symbols)
    hd.species_order(symbols)  # refuse unknown elements before relabeling
    if not 0 < n_slab <= len(symbols):
        raise hd.BuildError("invalid slab atom count")
    metal_split = mode.startswith("metal_alternating")
    fragment = "fragment" in mode
    ads_o = [i for i in range(n_slab, len(symbols)) if symbols[i] == "O"]
    if fragment and (free_moment not in (1.0, 2.0) or len(ads_o) != 2):
        raise hd.BuildError("fragment starts require two adsorbate O and a classified 1/2 muB fragment")
    counts = Counter(symbols[:n_slab])
    eligible = sorted(e for e in hd.METALS if counts[e] > 1)
    split_budget = max(0, NTYP_MAX - len(hd.species_order(symbols)) - 1)
    split_elements = eligible[:split_budget] if metal_split else []
    occurrence = Counter()
    atom_labels, label_element, label_mag = [], {}, {}
    for i, element in enumerate(symbols):
        label, mag = element, float(hd.ELEMENTS[element]["mag"])
        if element in split_elements and i < n_slab:
            sign = 1 if occurrence[element] % 2 == 0 else -1
            label = element + ("1" if sign > 0 else "2")
            mag *= sign
            occurrence[element] += 1
        if fragment and element == "O":
            label = "O2" if i in ads_o else "O1"
            # The O UPF of record has six valence electrons. H remains unpolarized.
            mag = free_moment / (6.0 * len(ads_o)) if i in ads_o else 0.0
        atom_labels.append(label)
        label_element[label] = element
        label_mag[label] = mag
    order = []
    for element in hd.species_order(symbols):
        order.extend(sorted(label for label, e in label_element.items() if e == element))
    if len(set(order)) != len(order) or any(not re.fullmatch(r"[A-Z][a-z]?[12]?", label) for label in order):
        raise hd.BuildError("invalid or duplicate QE species labels")
    if len(order) > NTYP_MAX:
        raise hd.BuildError(f"control needs {len(order)} species but target QE supports {NTYP_MAX}")
    return dict(atom_labels=atom_labels, species=order, element=label_element, magnetization=label_mag,
                split_metal_elements=split_elements, unsplit_eligible_metals=[e for e in eligible if e not in split_elements],
                target_qe_ntyp_max=NTYP_MAX,
                fragment_atom_indices=ads_o if fragment else [], mode=mode,
                nominal_fragment_start_muB=free_moment if fragment else None)


def _replace_setting(text: str, key: str, value: str) -> str:
    text, n = re.subn(r"^  " + re.escape(key) + r" = .*$", f"  {key} = {value}", text, flags=re.M)
    if n != 1:
        raise hd.BuildError(f"expected one {key} setting, found {n}")
    return text


def render_control(state: dict, projector: str, variant: str, template=None) -> tuple[str, dict]:
    if variant not in ("baseline", *SPIN_MODES[1:], *NUMERICAL):
        raise hd.BuildError(f"unknown control variant {variant!r}")
    if projector not in PROJECTORS:
        raise hd.BuildError(f"unknown projector {projector!r}")
    label = state["label"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", label):
        raise hd.BuildError("unsafe state label")
    job = f"hc__{label}__{projector}__{variant}"
    g = state["geometry"]
    symbols, positions, cell, fixed = (g[k] for k in ("symbols", "positions_A", "cell_A", "fixed_atom_indices"))
    if len(symbols) != 75 or symbols[72:] != ["O", "O", "H"]:
        raise hd.BuildError("this retained-branch control arm requires 72 slab atoms followed by O O H")
    mode = variant if variant in SPIN_MODES else "fm"
    spin = species_plan(symbols, 72, mode, state["integrity"].get("expected_free_species_moment_muB"))
    # Baseline delegates all template/source invariants to the established writer first.
    original = hd.render_deck(job, symbols, positions, cell, fixed, projector, template)
    nml = original.split("ATOMIC_SPECIES\n", 1)[0]
    nml = _replace_setting(nml, "ntyp", str(len(spin["species"])))
    nml, n = re.subn(r"^  starting_magnetization\(\d+\) = .*\n", "", nml, flags=re.M)
    if n != len(hd.species_order(symbols)):
        raise hd.BuildError("baseline magnetization block is malformed")
    mags = "".join(f"  starting_magnetization({i}) = {spin['magnetization'][s]}\n"
                   for i, s in enumerate(spin["species"], 1))
    nml = nml.replace("  nspin = 2\n", "  nspin = 2\n" + mags)
    settings = dict(BASE_SETTINGS)
    mesh = hd.kgrid_from_cell(cell)
    changes = {}
    if variant in NUMERICAL:
        key, value = NUMERICAL[variant]
        changes[key] = value
        if key == "mesh":
            mesh = value
        else:
            settings[key] = value
            nml = _replace_setting(nml, key, value)
    lines = nml.rstrip("\n").split("\n") + ["ATOMIC_SPECIES"]
    for label in spin["species"]:
        cfg = hd.ELEMENTS[spin["element"][label]]
        lines.append(f"  {label}  {cfg['mass']}  {cfg['pseudo']}")
    lines.append("CELL_PARAMETERS angstrom")
    lines.extend("  " + "  ".join(repr(float(x)) for x in row) for row in cell)
    lines.append("ATOMIC_POSITIONS angstrom")
    for i, (label, pos) in enumerate(zip(spin["atom_labels"], positions)):
        flags = "0 0 0" if i in fixed else "1 1 1"
        lines.append(f"  {label}  " + "  ".join(repr(float(x)) for x in pos) + f"  {flags}")
    lines += ["K_POINTS automatic", "  " + " ".join(map(str, (*mesh, 0, 0, 0))), hd.CARD[projector]]
    for label in spin["species"]:
        u = hd.ELEMENTS[spin["element"][label]]["U"]
        if u > 0:
            lines.append(f"U {label}-3d {u:.4f}")
    text = "\n".join(lines) + "\n"
    verify_control(text, state, spin, mesh, projector, settings)
    if variant == "baseline" and text != original:
        raise hd.BuildError("control baseline differs from established deck apart from its isolated prefix")
    metadata = dict(job=job, state=state["label"], projector=projector, variant=variant,
                    spin=spin, settings={**settings, "mesh": list(mesh)}, changed_settings=changes,
                    nk=CONTROL_NK.get(variant, hd.choose_nk(hd.kpoint_count(mesh))), nat=len(symbols), ntyp=len(spin["species"]))
    metadata["decomposition"] = dict(np=hd.NP, nk=metadata["nk"], ranks_per_pool=hd.NP // metadata["nk"],
                                     baseline_nk=hd.choose_nk(hd.kpoint_count(hd.kgrid_from_cell(cell))),
                                     reason="nk4 limits modeled memory at the denser 6x3 mesh" if variant == "k6x3" else "baseline pool rule")
    if metadata["nk"] <= 0 or hd.NP % metadata["nk"] or metadata["nk"] > hd.kpoint_count(mesh):
        raise hd.BuildError("invalid pool decomposition")
    return text, metadata


def verify_control(text: str, state: dict, spin: dict, mesh, projector: str, settings: dict) -> dict:
    if "\r" in text or not text.endswith("\n"):
        raise hd.BuildError("control deck must have LF lines and a final newline")
    p = hd.parse_deck(text)
    g = state["geometry"]
    if p["symbols"] != spin["atom_labels"] or [spin["element"][s] for s in p["symbols"]] != g["symbols"]:
        raise hd.BuildError("species relabeling changed retained element identity")
    if p["positions"] != g["positions_A"] or p["cell"] != g["cell_A"] or p["fixed"] != sorted(g["fixed_atom_indices"]):
        raise hd.BuildError("control changed retained geometry or constraints")
    if p["species"] != spin["species"] or p["nat"] != len(g["symbols"]) or p["ntyp"] != len(spin["species"]):
        raise hd.BuildError("control atom/species counts are inconsistent")
    want_u = {s: hd.ELEMENTS[spin["element"][s]]["U"] for s in spin["species"] if hd.ELEMENTS[spin["element"][s]]["U"] > 0}
    want_upfs = [hd.ELEMENTS[spin["element"][s]]["pseudo"] for s in spin["species"]]
    want_mag = {i: spin["magnetization"][s] for i, s in enumerate(spin["species"], 1)}
    if p["U"] != want_u or p["upfs"] != want_upfs or p["mag"] != want_mag:
        raise hd.BuildError("split-species U, pseudopotential or spin mapping is wrong")
    if p["mesh"] != tuple(mesh) or p["hubbard_card"] != hd.CARD[projector]:
        raise hd.BuildError("control mesh or projector is wrong")
    pre = hd.preflight_upfs()
    if any(upf not in pre for upf in p["upfs"]):
        raise hd.BuildError("control contains an unverified pseudopotential")
    for key, value in settings.items():
        if text.split("\n").count(f"  {key} = {value}") != 1:
            raise hd.BuildError(f"control setting {key} is wrong")
    for required in ("  calculation = 'scf'", "  tprnfor = .true.", "  nspin = 2", "  nosym = .true.", "  noinv = .true."):
        if text.split("\n").count(required) != 1:
            raise hd.BuildError(f"control lacks unique {required.strip()}")
    if re.search(r"^\s*(tot_charge|tot_magnetization|constrained_magnetization|startingpot|startingwfc|restart_mode)\s*=", text, re.M):
        raise hd.BuildError("control introduced charge, spin constraints or restart settings")
    return p


def estimate_cost(state: dict, row: dict) -> dict:
    """Apply the banked model at actual mesh/pools; explicit cutoff extrapolation.

    Ecut**1.5 counts reciprocal-space basis/grid points. Applying the larger
    wavefunction/density factor to wall is a planning heuristic, not calibration.
    Same-element splitting leaves electrons unchanged; its extra overhead is unknown.
    """
    g = state["geometry"]
    mesh = row["settings"]["mesh"]
    base = cm.per_scf(dict(Counter(g["symbols"])), g["cell_A"], hd.kpoint_count(mesh), row["nk"])
    wfc_factor = (float(row["settings"]["ecutwfc"]) / 80.0) ** 1.5
    rho_factor = (float(row["settings"]["ecutrho"]) / 640.0) ** 1.5
    wall_factor = max(wfc_factor, rho_factor)
    leg = base[row["projector"]]
    plan_wall = leg["plan_wall_s"] * wall_factor
    factors = base["factors"]
    ram = cm.BANKED[cm.REF]["ram_proc_MB"] * max(factors["mem_wfc"] * wfc_factor, factors["mem_dens"] * rho_factor) * hd.NP / 1024.0
    return dict(
        method="hea_cost_model model A with explicit max(Ewfc/80,Erho/640)**1.5 cutoff scaling",
        planning_iters=cm.PLANNING_ITERS, plan_wall_s=plan_wall,
        plan_coreh=leg["plan_coreh"] * wall_factor, model_B_coreh=leg["floor_coreh"] * wall_factor,
        monitoring_wall_trigger_s=cm.CEILING_FACTOR * plan_wall,
        monitoring_coreh_equivalent=cm.CEILING_FACTOR * leg["plan_coreh"] * wall_factor,
        monitoring_iteration_trigger=126, watchdog_implemented=False,
        qe_max_seconds=hd.MAX_SECONDS, qe_electron_maxstep=hd.ELECTRON_MAXSTEP,
        scheduler_wall_limit_s=48 * 3600,
        ram_GB_estimate=ram, ram_GB_3x_scenario=cm.CEILING_FACTOR * ram,
        node_memory_GB=cm.NODE_GB, planning_memory_fits_node=ram <= cm.NODE_GB,
        memory_3x_scenario_fits_node=cm.CEILING_FACTOR * ram <= cm.NODE_GB,
        cutoff_wfc_point_factor=wfc_factor, cutoff_density_point_factor=rho_factor,
        limitations=["HEA spin texture/ntyp overhead and tighter-SCF iteration count are uncalibrated",
                     "3x figures are monitoring thresholds/scenarios, not enforced caps or statistical bounds",
                     "projwfc.x overhead is excluded; smoke measurements must replace model assumptions"],
    )


def baseline_reference(state: dict, projector: str, template=None) -> dict:
    """Hash and verify exact baseline equivalence, excluding only the unique prefix."""
    job = f"{state['label']}__{projector}"
    path = panel.OUT / (job + ".in")
    original = path.read_bytes()
    g = state["geometry"]
    expected = hd.render_deck(job, g["symbols"], g["positions_A"], g["cell_A"], g["fixed_atom_indices"], projector, template)
    if original != expected.encode("utf-8"):
        raise hd.BuildError(f"{path}: original baseline is not the exact retained protocol")
    companion, row = render_control(state, projector, "baseline", template)
    normalize = lambda t: re.sub(r"^  prefix = .*\n", "", t, flags=re.M)
    normalized = normalize(expected)
    if normalize(companion) != normalized:
        raise hd.BuildError("original/companion baseline differ beyond prefix")
    return dict(
        companion_job=row["job"], original_job=job,
        original_deck=path.relative_to(REPO).as_posix(),
        original_output=path.with_suffix(".out").relative_to(REPO).as_posix(),
        original_lowdin=path.with_suffix(".lowdin.txt").relative_to(REPO).as_posix(),
        original_md5=hashlib.md5(original).hexdigest(), original_sha256=sha(original),
        prefix_normalized_sha256=sha(normalized.encode("utf-8")), equivalence="identical except prefix",
        reuse_policy="Run one location only. Prefer a terminal converged original with matching deck hash, JOB DONE, force table and local-moment/occupation records; otherwise select one location before submission. A terminal failed original remains a failed attempt, not permission for a silent companion retry. If companion ran first, reuse it and omit the original equivalent. Preserve actual output paths/hashes; never copy outputs under a new prefix.",
    )


def plan_controls(states: list, template=None) -> list:
    by_label = {s["label"]: s for s in states}
    if len(by_label) != len(states) or set(STATE_LABELS) - set(by_label):
        raise hd.BuildError("missing or duplicate branch states")
    jobs = []
    references = {(label, proj): baseline_reference(by_label[label], proj, template)
                  for label in STATE_LABELS for proj in PROJECTORS}
    for label in STATE_LABELS:
        s = by_label[label]
        variants = ["baseline", "metal_alternating"]
        if s["integrity"].get("expected_free_species_moment_muB") is not None:
            variants += ["fragment", "metal_alternating_fragment"]
        if label in NUMERICAL_LABELS:
            variants += list(NUMERICAL)
        for projector in PROJECTORS:
            for variant in variants:
                text, row = render_control(s, projector, variant, template)
                data = text.encode("utf-8")
                row.update(md5=hashlib.md5(data).hexdigest(), sha256=sha(data), text=text,
                           baseline_job=f"hc__{label}__{projector}__baseline",
                           source_json=(panel.BANK / s["source_json"]).relative_to(REPO).as_posix(),
                           geometry_pointer=s["pointer"], source_json_sha256_lf=hd.sha256_lf(panel.BANK / s["source_json"]),
                           extxyz=s["extxyz"], extxyz_sha256_lf=s["sha"], integrity=s["integrity"])
                row["baseline_reference"] = references[(label, projector)]
                row["cost"] = estimate_cost(s, row)
                jobs.append(row)
    if len(jobs) != 48 or len({r["job"] for r in jobs}) != len(jobs):
        raise hd.BuildError("expected exactly 48 unique control jobs")
    return jobs


def manifest_text(rows: list) -> str:
    lines = [
        "# HEA fixed-geometry spin and numerical controls, 2026-09-07.",
        "# NOT LICENSED FOR SUBMISSION. Isolated exploratory companion arm; no jobs submitted.",
        "# Original branch-panel decks, MACE census and registered verdicts are unchanged.",
        "# All decks explicitly request forces; tprnfor was already enabled in the baseline.",
        "# Numerical decks change one setting at a time at fixed cell and coverage.",
        "# k6x3 additionally uses nk4 (baseline nk8) for memory; decomposition sensitivity",
        "# requires a baseline nk4 confirmation before tight numerical certification.",
        "# Eight baselines equal original branch decks except prefix: RUN ONCE across both arms.",
        "# Resolve/reuse baseline_reference records and omit duplicate jobs before submission.",
        "# Spin seeds are unconstrained initial guesses, not established magnetic ground states.",
        "# Full requests, exact species mappings, source hashes and readout requirements:",
        "# hea/controls_2026-09-07/requests.json",
        "# COST: banked per-SCF model at actual mesh/pools; cutoff point counts scale Ecut**1.5.",
        "# Split-species, tighter-SCF and larger-basis overhead remain uncalibrated; verify smoke first.",
        f"# Planning {sum(r['cost']['plan_coreh'] for r in rows):.1f} core-h; model B {sum(r['cost']['model_B_coreh'] for r in rows):.1f} core-h.",
        f"# Maximum modeled memory {max(r['cost']['ram_GB_estimate'] for r in rows):.1f} GB; compare with 237 GB/node at runtime.",
        "# Proposed monitoring: cancel and record <job>.KILLED if wall > own 3x planning wall",
        "# or iteration count >126 without convergence. No watchdog is implemented here.",
        "# 3x wall/core-hour figures are not hard caps. QE max_seconds=165000/electron_maxstep=300;",
        "# scheduler wall limit 48 h is distinct. Do not expand before measured memory/cost fit.",
        f"# Worst-case 48 h allocation cap: {len(rows) * hd.NP * 48} core-hours; not a forecast.",
        f"# SUBMIT WITH EXCLUDE={hd.EXCLUDE}",
        f"# NP={hd.NP} NCONC=1",
        "# deck hashes: job md5 sha256",
    ]
    for row in rows:
        lines.append(f"# {row['job']} {row['md5']} {row['sha256']}")
    lines += ["# Per-job estimates: job plan_coreh monitor_wall_h memory_GB (not hard caps)"]
    for row in rows:
        c = row["cost"]
        lines.append(f"# {row['job']} {c['plan_coreh']:.3f} {c['monitoring_wall_trigger_s'] / 3600:.3f} {c['ram_GB_estimate']:.3f}")
    lines += ["# Runnable rows: dir job suffix nk"]
    lines.extend(f"hea/controls_2026-09-07 {r['job']} .in {r['nk']}" for r in rows)
    text = "\n".join(lines) + "\n"
    info = hd.check_manifest_text(text)
    if info["n_rows"] != len(rows) or not info["np_directive"]:
        raise hd.BuildError("control manifest row/header mismatch")
    return text


def request_text(rows: list) -> str:
    document = dict(
        schema="hea-controls-v1", status="NOT LICENSED FOR SUBMISSION", dft_executed=False,
        scientific_scope="Fixed retained-geometry branch gaps, force diagnostics, spin-start and numerical sensitivity; not ranking calibration.",
        source_panel_sha256_lf=hd.sha256_lf(panel.PANEL), template_sha256_lf=hd.sha256_lf(hd.TEMPLATE),
        builder_sha256_lf=hd.sha256_lf(Path(__file__)),
        cost_model_sha256_lf=hd.sha256_lf(Path(cm.__file__)),
        target_qe_species_limit=dict(ntypx=NTYP_MAX, evidence="runs/a0/cell/ref__2x1v__u715.out:23"),
        pseudopotential_md5=hd.preflight_upfs(), n_jobs=len(rows),
        smoke_jobs=[r["job"] for r in smoke_rows(rows)],
        smoke_instructions="Two leader baseline atomic endpoints first, NCONC=1; reuse equivalent original terminal outputs if present instead of running twice. Measure cost/memory, final spin/occupations and forces before expansion. No launch authorized by this request file.",
        baseline_run_once_policy="Eight companion baselines are exact prefix-only twins of existing branch-panel inputs. Across both arms, execute each baseline once. Explicitly resolve baseline_reference for each selected job and exclude duplicates from the submitted subset; preserve original output paths/hashes in readouts. Planned full-arm totals include baselines, so subtract reused jobs from incremental cost.",
        pairs=[dict(name="equiatomic", A=STATE_LABELS[0], B=STATE_LABELS[1]),
               dict(name="leader", A=STATE_LABELS[2], B=STATE_LABELS[3])],
        readout_requirements=[
            "Record SCF convergence, JOB DONE, final energy and SCF residual; never use unconverged energies.",
            "Retain forces in Ry/bohr and eV/angstrom, all-atom and unfixed-atom maxima/RMS separately.",
            "Retain total/absolute magnetization, per-atom Lowdin moments and Hubbard occupation matrices.",
            "For detached fragments report O indices 72,73 separately from H74 (H74 is on the slab for transferred states).",
            "Report every attempted spin start and basin; lower energy alone does not establish the magnetic ground state.",
            "Compute paired E(B)-E(A) and its change from baseline only for matched variant/projector and terminal converged legs.",
            "Treat changed local moments/occupations in a numerical variant as mixed electronic-state sensitivity, not pure numerical error.",
            "No eta, kinetic rate-limiting step, spin ground-state, coverage, slab-thickness or vacuum convergence claim follows from this panel.",
            "After one-factor tests, a joint tighter-setting confirmation is required before asserting a combined numerical error bound.",
            "The k6x3 control uses nk4 versus baseline nk8. Match the baseline at nk4 before tight numerical certification, or if decomposition-dependent changes appear; interpret current differences as mesh plus decomposition sensitivity.",
        ],
        deferred=["negative fragment orientation", "additional magnetic textures", "joint cutoff confirmation", "slab/vacuum/dipole/cell and coverage controls"],
        requests=[{k: v for k, v in row.items() if k != "text"} for row in rows],
    )
    return json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + "\n"


def smoke_rows(rows: list) -> list:
    subset = [r for r in rows if r["state"] in NUMERICAL_LABELS and r["projector"] == "atomic" and r["variant"] == "baseline"]
    if len(subset) != 2:
        raise hd.BuildError("smoke subset requires both leader atomic baseline endpoints")
    return subset


def publish(payloads: dict[Path, str], check_only=False) -> None:
    """Preflight the whole set before any write; fail on drift or an incomplete --check."""
    for path, text in payloads.items():
        if "\r" in text:
            raise hd.BuildError(f"{path}: refusing CR bytes")
        if path.exists():
            if path.read_bytes() != text.encode("utf-8"):
                raise hd.BuildError(f"{path}: differs from expected bytes; refusing overwrite")
        elif check_only:
            raise hd.BuildError(f"{path}: missing expected artifact")
    if not check_only:
        for path, text in payloads.items():
            hd.write_lf(path, text)


def build(check_only=False) -> list:
    rows = plan_controls(panel.collect_states(), hd.load_template())
    payloads = {OUT / (r["job"] + ".in"): r["text"] for r in rows}
    payloads[OUT / "requests.json"] = request_text(rows)
    payloads[MANIFEST] = manifest_text(rows)
    payloads[SMOKE_MANIFEST] = manifest_text(smoke_rows(rows))
    publish(payloads, check_only)
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="require and verify every artifact; no writes")
    args = parser.parse_args(argv)
    rows = build(args.check)
    print(f"{'Verified' if args.check else 'Prepared'} {len(rows)} control decks, requests.json and full/smoke manifests; NOT LICENSED, nothing submitted.")
    print(MANIFEST.relative_to(REPO).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
