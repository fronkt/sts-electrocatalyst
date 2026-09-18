"""Cost of the low-tail relaxation decks from measured HEA SCF costs and banked relaxation statistics.

Measured anchors (no model extrapolation from small cells):
  * per-SCF-iteration wall, force wall, init wall and per-SCF remainder from every ACCEPTED banked
    HEA single point at the settings of record (80/640 Ry, MV 0.01 Ry), per projector, normalised
    by cell volume x Kohn-Sham states (the FFT-dominated scaling that reproduced the banked HEA
    anchor, runs/hea/COST_MODEL.md section 2 model B);
  * first-SCF iteration counts of those from-scratch HEA SCFs (median planning, p90 ceiling);
  * memory: printed 'Estimated total dynamical RAM' and scheduler MaxRSS of the accepted winner
    tasks (results/hea_continuation_2026-09-11/collection_verified/memory.json), normalised the same way.
Expected ionic steps come from the survey of banked nspin = 2 slab relaxations outside runs/hea,
restricted to starts whose initial free-atom force maximum lies within a factor two of the DFT
force maximum measured at the corresponding MACE endpoint in (a). Step statistics use only band
members that are BFGS-converged AND CONVERGED under the existing HEA scorer
(src/dft/hea_panel_readout.py parse_out(allow_relax=True): no severe numerical exception such as
IEEE_INVALID, exactly one JOB DONE), the rule the relaxation readout applies to the decks; the
BFGS-converged members that the scorer rejects are listed by name with their flags. Every surveyed
and excluded output (and its input) is hashed in the survey manifest.

planning wall = t_init + [I_first + (S - 1) I_sub] t_iter + S (t_force + t_rest)
ceiling      = max(3 x planning [COST_MODEL.md ceiling factor], the same formula at p90 S, I_first, I_sub)
core-h       = wall x ranks / 3600
"""
from __future__ import annotations

import argparse
import math
import re
import statistics
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lt_qe as qe  # noqa: E402
import lt_sources as src  # noqa: E402
from lt_common import ROOT, evidence, read_json, rel, sha256_file, write_json  # noqa: E402

import lt_readout  # noqa: E402  (scorer_parse_out: the HEA scorer with every pw.x wall-token format)

COST_MODEL = ROOT / "runs/hea/COST_MODEL.md"
MEMORY = ROOT / "results/hea_continuation_2026-09-11/collection_verified/memory.json"
WINNER_SPEC = ROOT / "results/hea_winner_2026-09-10/launch_spec.json"


def nearest_rank(values, q: float):
    """Nearest-rank percentile (the convention of runs/hea/COST_MODEL.md section 1b)."""
    xs = sorted(values)
    if not xs:
        return None
    k = max(1, math.ceil(q / 100.0 * len(xs)))
    return xs[k - 1]


def fortran_nint(x: float) -> int:
    return int(math.floor(x + 0.5)) if x >= 0 else -int(math.floor(-x + 0.5))


def nbnd_rule(nelec: float) -> int:
    """pw.x default for these decks, as stated and checked in runs/hea/COST_MODEL.md section 2."""
    return fortran_nint(1.2 * fortran_nint(nelec / 2.0))


def cost_model_inputs(path: Path = COST_MODEL) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    head = lines.index("| species | valence | source |")
    valence = {}
    for line in lines[head + 2:]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        valence[cells[0]] = float(cells[1])
    ceiling = re.search(r"^\| ceiling factor \| (\d+)x planning \|", text, re.M)
    node = re.search(r"^\| node memory \| ([\d.]+) GB \|", text, re.M)
    ranks = re.search(r"^\| ranks per job \| (\d+) \|", text, re.M)
    return dict(valence=valence, ceiling_factor=float(ceiling.group(1)), node_memory_GB=float(node.group(1)),
                ranks=int(ranks.group(1)))


def cell_volume_A3(cell) -> float:
    return float(abs(np.linalg.det(np.asarray(cell, dtype=float))))


# --------------------------------------------------------------------------- measured HEA SCFs
def measured_hea_scfs() -> list:
    rows = []
    maxrss = winner_maxrss_GiB()
    for e in src.registry()["entries"]:
        if e["status"] != "ACCEPTED":
            continue
        parsed = qe.parse_input(qe.read_text(ROOT / e["input"]))
        p = parsed["params"]
        if not (p["ecutwfc"] == 80.0 and p["ecutrho"] == 640.0 and p["degauss"] == 0.01):
            continue
        text = qe.read_text(ROOT / e["output"])
        scf = qe.parse_scf(text, parsed["nat"])
        if scf["status"] != "VALID_SCF":
            continue
        t, h = scf["timers"], scf["header"]
        norm = cell_volume_A3(parsed["cell"]) * h["nbnd"]
        rest = t["PWSCF_wall_s"] - t["init_run"]["wall_s"] - t["electrons"]["wall_s"] - t["forces"]["wall_s"]
        rows.append(dict(job=e["job"], projector=("ortho" if "ortho" in (parsed["hubbard_card"] or "") else "atomic"),
                         input=evidence(ROOT / e["input"]), output=evidence(ROOT / e["output"]),
                         acceptance_readout=e["readout"],
                         from_scratch=p["startingwfc"] is None and p["startingpot"] is None,
                         record_spin_start=e.get("variant") == "baseline",
                         rest_resolved=t["PWSCF_wall_resolution_s"] is not None and t["PWSCF_wall_resolution_s"] < 1.0,
                         iterations=scf["iterations"], nbnd=h["nbnd"], nelec=h["nelec"], volume_A3=cell_volume_A3(parsed["cell"]),
                         procs=h["procs"], npool=h["npool"], wall_init_s=t["init_run"]["wall_s"],
                         wall_per_iteration_s=t["electrons"]["wall_s"] / scf["iterations"], wall_forces_s=t["forces"]["wall_s"],
                         wall_rest_s=rest, pwscf_wall_s=t["PWSCF_wall_s"], ram_total_GB=h["ram_total_GB"],
                         maxrss_GiB=maxrss.get(e["job"]), nbnd_rule_check=nbnd_rule(h["nelec"]) == h["nbnd"],
                         per_iteration_norm=t["electrons"]["wall_s"] / scf["iterations"] / norm,
                         forces_norm=t["forces"]["wall_s"] / norm, ram_norm=h["ram_total_GB"] / norm,
                         maxrss_norm=(maxrss[e["job"]] / norm if e["job"] in maxrss else None)))
    return rows


def winner_maxrss_GiB() -> dict:
    jobs = [j["job"] for j in read_json(WINNER_SPEC)["jobs"]]
    text = read_json(MEMORY)["out"]
    out = {}
    for line in text.splitlines():
        fields = line.split("|")
        m = re.match(r"^20563386_(\d+)\.batch$", fields[0])
        if m and fields[2].endswith("K"):
            out[jobs[int(m.group(1)) - 1]] = int(fields[2][:-1]) / 1024 ** 2
    return out


# --------------------------------------------------------------------------- relaxation survey
def relax_survey(root: Path = ROOT / "runs") -> dict:
    rows, excluded = [], []
    for out in sorted(root.rglob("*.out")):
        if "hea" in out.relative_to(root).parts[:1] or out.name.endswith(".projwfc.out"):
            continue
        inp = out.with_name(out.name[:-4] + ".in")
        if not inp.exists():
            continue
        text_in = qe.read_text(inp)
        if qe.namelist_value(text_in, "calculation") != "relax":
            continue
        if qe.namelist_value(text_in, "nspin") != 2.0:
            continue
        text = qe.read_text(out)
        nat = qe.header_numbers(text)["nat"]
        if nat is None or nat < 18:
            continue
        hashes = dict(output=evidence(out), input=evidence(inp))
        try:
            parsed = qe.parse_input(text_in)
            if parsed["nat"] != nat:
                raise ValueError("input nat differs from output")
        except ValueError as error:
            excluded.append(dict(output=rel(out), reason=f"input not parseable for the if_pos mask: {error}", files=hashes))
            continue
        relax = qe.parse_relax(text, nat)
        if relax["force_error"] or not relax["force_blocks"]:
            excluded.append(dict(output=rel(out), reason=relax["force_error"] or "no force block", files=hashes,
                                 scf_not_converged=len(relax["scf_failures"])))
            continue
        f0 = qe.free_fmax(relax["force_blocks"][0], parsed["if_pos"])
        converged = relax["bfgs_converged"] and not relax["scf_failures"] and relax["job_done"] >= 1
        qc = lt_readout.scorer_parse_out(out, allow_relax=True)
        rows.append(dict(output=rel(out), files=hashes, nat=nat, n_free_atoms=sum(1 for f in parsed["if_pos"] if any(f)),
                         converged=converged, scorer_status=qc["status"],
                         severe_failures=sorted(set(qc.get("severe_failures") or [])),
                         scf_cycles=relax["bfgs_scf_cycles"], bfgs_steps=relax["bfgs_steps"],
                         first_scf_iterations=relax["scf_iterations"][0] if relax["scf_iterations"] else None,
                         subsequent_iterations_median=(statistics.median(relax["scf_iterations"][1:])
                                                      if len(relax["scf_iterations"]) > 1 else None),
                         initial_free_fmax_eV_A=f0, scf_failures=len(relax["scf_failures"]),
                         max_steps_reached=relax["max_steps_reached"]))
    return dict(rows=rows, excluded=excluded)


def _step_stats(rows: list) -> dict:
    sub = [r["subsequent_iterations_median"] for r in rows if r["subsequent_iterations_median"] is not None]
    cycles = [r["scf_cycles"] for r in rows]
    return dict(scf_cycles_p50=nearest_rank(cycles, 50), scf_cycles_p90=nearest_rank(cycles, 90), scf_cycles_max=max(cycles) if cycles else None,
                subsequent_iterations_p50=nearest_rank(sub, 50), subsequent_iterations_p90=nearest_rank(sub, 90),
                max_n_free_atoms=max((r["n_free_atoms"] for r in rows), default=None))


def band_statistics(survey: dict, f_ref: float) -> dict:
    """Step statistics over the band members that are BFGS-converged and CONVERGED under the HEA scorer."""
    lo, hi = f_ref / 2.0, f_ref * 2.0
    band = [r for r in survey["rows"] if r["initial_free_fmax_eV_A"] is not None and lo <= r["initial_free_fmax_eV_A"] <= hi]
    bfgs = [r for r in band if r["converged"] and r["scf_cycles"]]
    basis = [r for r in bfgs if r["scorer_status"] == "CONVERGED"]
    stats = _step_stats(basis)
    bfgs_stats = _step_stats(bfgs)
    return dict(f_ref_eV_A=f_ref, band_eV_A=[lo, hi], n_in_band=len(band), n_bfgs_converged=len(bfgs), n_basis=len(basis),
                basis_rule="BFGS-converged and src/dft/hea_panel_readout.py parse_out(allow_relax=True) status CONVERGED",
                n_not_bfgs_converged=len(band) - len(bfgs), not_bfgs_converged=[r["output"] for r in band if r not in bfgs],
                bfgs_converged_rejected_by_scorer=[dict(output=r["output"], scorer_status=r["scorer_status"],
                                                        severe_failures=r["severe_failures"]) for r in bfgs if r not in basis],
                statistics_unchanged_by_scorer_rule=bool(stats == bfgs_stats), bfgs_converged_statistics=bfgs_stats, **stats)


def survey_qc(survey: dict) -> dict:
    """Scorer outcomes over every surveyed relaxation (the rejection-risk record for relax legs)."""
    rows = survey["rows"]
    statuses = sorted({r["scorer_status"] for r in rows})
    ieee = [r["output"] for r in rows if any("IEEE_INVALID" in s.upper() for s in r["severe_failures"])]
    return dict(n_rows=len(rows), scorer_status_counts={s: sum(r["scorer_status"] == s for r in rows) for s in statuses},
                n_bfgs_converged=sum(bool(r["converged"]) for r in rows),
                n_bfgs_converged_scorer_rejected=sum(bool(r["converged"]) and r["scorer_status"] != "CONVERGED" for r in rows),
                n_ieee_invalid=len(ieee), ieee_invalid_outputs=ieee)


def survey_manifest(survey: dict) -> dict:
    """sha256 of every output (and input) the relaxation survey read, used or excluded."""
    return dict(schema="lowtail-relax-survey-manifest-v1", root="runs (runs/hea excluded)",
                used=[dict(output=r["files"]["output"], input=r["files"]["input"]) for r in survey["rows"]],
                excluded=[dict(output=e["files"]["output"], input=e["files"]["input"], reason=e["reason"]) for e in survey["excluded"]],
                n_used=len(survey["rows"]), n_excluded=len(survey["excluded"]),
                scorer=evidence(ROOT / "src/dft/hea_panel_readout.py"))


# --------------------------------------------------------------------------- per deck
def anchors(measured: list, projector: str) -> dict:
    rows = [r for r in measured if r["projector"] == projector]
    scratch = [r["iterations"] for r in rows if r["from_scratch"] and r["record_spin_start"]]
    return dict(n=len(rows), jobs=[r["job"] for r in rows],
                per_iteration_norm=statistics.median(r["per_iteration_norm"] for r in rows),
                forces_norm=statistics.median(r["forces_norm"] for r in rows),
                init_s=statistics.median(r["wall_init_s"] for r in rows),
                rest_s=statistics.median(r["wall_rest_s"] for r in rows if r["rest_resolved"]),
                n_rest_resolved=sum(1 for r in rows if r["rest_resolved"]),
                ram_norm=statistics.median(r["ram_norm"] for r in rows),
                maxrss_norm=(statistics.median(r["maxrss_norm"] for r in rows if r["maxrss_norm"] is not None)
                             if any(r["maxrss_norm"] is not None for r in rows) else None),
                first_iterations_p50=nearest_rank(scratch, 50), first_iterations_p90=nearest_rank(scratch, 90),
                n_from_scratch_record_start=len(scratch), first_iterations=sorted(scratch), procs=sorted({r["procs"] for r in rows}), npool=sorted({r["npool"] for r in rows}))


def deck_cost(symbols, cell, projector: str, anchor: dict, band: dict, inputs: dict, max_seconds: float) -> dict:
    nelec = sum(inputs["valence"][s] for s in symbols)
    nbnd = nbnd_rule(nelec)
    volume = cell_volume_A3(cell)
    norm = volume * nbnd
    t_iter, t_force = anchor["per_iteration_norm"] * norm, anchor["forces_norm"] * norm
    ranks = inputs["ranks"]

    def wall(steps, first, sub):
        return anchor["init_s"] + (first + (steps - 1) * sub) * t_iter + steps * (t_force + anchor["rest_s"])

    plan_s = wall(band["scf_cycles_p50"], anchor["first_iterations_p50"], band["subsequent_iterations_p50"])
    p90_s = wall(band["scf_cycles_p90"], anchor["first_iterations_p90"], band["subsequent_iterations_p90"])
    ceil_s = max(inputs["ceiling_factor"] * plan_s, p90_s)
    ram = anchor["ram_norm"] * norm
    rss = anchor["maxrss_norm"] * norm if anchor["maxrss_norm"] is not None else None
    return dict(nelec=nelec, nbnd_rule=nbnd, volume_A3=volume, wall_per_iteration_s=t_iter, wall_forces_s=t_force,
                planning_ionic_steps=band["scf_cycles_p50"], ceiling_ionic_steps_p90=band["scf_cycles_p90"],
                planning_wall_s=plan_s, ceiling_wall_s=ceil_s,
                planning_wall_h=plan_s / 3600, ceiling_wall_h=ceil_s / 3600, p90_formula_wall_h=p90_s / 3600,
                planning_core_h=plan_s * ranks / 3600, ceiling_core_h=ceil_s * ranks / 3600, p90_formula_core_h=p90_s * ranks / 3600,
                ceiling_rule="max(ceiling_factor x planning, p90 formula)",
                memory_printed_estimate_GB=ram, memory_maxrss_scaled_GiB=rss, node_memory_GB=inputs["node_memory_GB"],
                fits_node=bool(max(ram, rss or 0) < inputs["node_memory_GB"]),
                ceiling_exceeds_deck_max_seconds=bool(ceil_s > max_seconds), deck_max_seconds=max_seconds)


def evidence_list() -> list:
    return [evidence(COST_MODEL), evidence(MEMORY), evidence(WINNER_SPEC), evidence(src.READOUTS["final"])]


def refresh(zero_compute: Path, prepared_plan: Path, out: Path) -> dict:
    """Reprice prepared decks with final accepted SCFs without changing their bytes or limits."""
    zc, prepared = read_json(zero_compute), read_json(prepared_plan)
    measured = measured_hea_scfs()
    survey = relax_survey()
    inputs = cost_model_inputs()
    anchors_by_projector = {p: anchors(measured, p) for p in ("atomic", "ortho")}
    references = {}
    for row in zc["realizations"]:
        if row["variant"] == "baseline" and row["record_settings"]:
            references.setdefault((row["geometry"], row["projector"]), []).append(row)
    rows = []
    for deck in prepared["decks"]:
        path = ROOT / deck["path"]
        if sha256_file(path) != deck["sha256"]:
            raise ValueError(f"{deck['path']}: prepared deck bytes changed")
        parsed = qe.parse_input(qe.read_text(path))
        state = "slab" if deck["state"] == "slab" else "O"
        chain = "equiatomic" if deck["site"] == "Fe25Co25Ni25Cr25__s2_site0" else "winner"
        key = (f"{chain}_{state}", deck["projector"])
        direct = deck["site"] in ("Fe25Co25Ni25Cr25__s2_site0", "Ni31Cr29Cu5Mn35__s1_site0")
        if key not in references:
            key = (f"winner_{state}", deck["projector"])
            direct = False
        refs = references[key]
        # Use the largest measured baseline force if this geometry has multiple realizations.
        f_ref = max(r["DFT"]["fmax_free_eV_A"] for r in refs)
        band = band_statistics(survey, f_ref)
        fresh = deck_cost(parsed["elements"], parsed["cell"], deck["projector"],
                          anchors_by_projector[deck["projector"]], band, inputs, parsed["params"]["max_seconds"])
        rows.append(dict(path=deck["path"], site=deck["site"], state=deck["state"], projector=deck["projector"],
                         role=deck["role"], sha256=deck["sha256"], prepared_cost=deck["cost"], cost=fresh,
                         force_reference=dict(geometry=key[0], projector=key[1], jobs=[r["job"] for r in refs],
                                              fmax_eV_A=f_ref, same_site=direct,
                                              note=("O reconstructed endpoint proxies the unreconstructed start"
                                                    if deck["state"] == "O_unrecon" else "same state")),
                         band=band, original_supervisor_limits=deck["supervisor_limits"],
                         revised_ceiling_exceeds_original_limit=bool(
                             fresh["ceiling_wall_s"] > deck["supervisor_limits"]["leg_wall_ceiling_s"])))
    totals = {}
    for role in ("primary", "paired projector control"):
        selected = [r for r in rows if r["role"] == role]
        totals[role] = dict(n_decks=len(selected), planning_core_h=sum(r["cost"]["planning_core_h"] for r in selected),
                            ceiling_core_h=sum(r["cost"]["ceiling_core_h"] for r in selected),
                            all_fit_node=all(r["cost"]["fits_node"] for r in selected),
                            any_ceiling_exceeds_deck_max_seconds=any(r["cost"]["ceiling_exceeds_deck_max_seconds"] for r in selected),
                            any_revised_ceiling_exceeds_original_limit=any(r["revised_ceiling_exceeds_original_limit"] for r in selected))
    report = dict(schema="lowtail-cost-refresh-v1", status="COST_REVIEW_ONLY_NO_DECK_OR_LIMIT_MUTATION",
                  inputs=[evidence(zero_compute), evidence(prepared_plan)] + evidence_list(),
                  anchors=anchors_by_projector, measured_accepted_scfs=measured,
                  survey_qc=survey_qc(survey), survey_manifest=survey_manifest(survey), decks=rows, totals=totals,
                  limitations=["Planning and ceiling costs are empirical estimates, not guarantees of convergence.",
                               "Cu8 has no DFT endpoint force: the Ni31 seed-1 endpoint remains its explicit proxy.",
                               "A missing same-site/projector force uses the Ni31 seed-1 proxy; O_unrecon uses O_recon force bands.",
                               "Original deck bytes and supervisor limits are preserved; any revised ceiling above the old limit is reported."])
    write_json(out, report)
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Refresh low-tail cost evidence without mutating prepared decks")
    ap.add_argument("--zero-compute", type=Path, required=True)
    ap.add_argument("--prepared-plan", type=Path, default=ROOT / "results/lowtail_dft_2026-09-16/deck_plan.json")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    result = refresh(args.zero_compute, args.prepared_plan, args.out)
    for role, totals in result["totals"].items():
        print(f"{role}: {totals['planning_core_h']:.1f} planning / {totals['ceiling_core_h']:.1f} ceiling core-h")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
