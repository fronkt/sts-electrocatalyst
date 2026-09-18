"""Relaxation readout on synthetic pw.x outputs: scorer acceptance, readout checks, basins and site outcomes."""
import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "s2" / "lowtail_dft"))

import lt_readout as ro  # noqa: E402

CELL = [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 20.0]]
# slab: 0 Mn fixed, 1 axial O below the site, 2 site Cr, 3 lateral O; appended O = 4
SYMBOLS_SLAB = ["Mn", "O", "Cr", "O"]
CLEAN = [[2.0, 2.0, 5.0], [5.0, 5.0, 6.2], [5.0, 5.0, 8.0], [7.0, 5.0, 8.0]]
TH = dict(lift_min_A=0.5, axial_break_A=2.1758, desorbed_min_A=3.0, magnetization_flag_muB=0.5, energy_order_margin_eV=0.48)
FORC = 2.0e-3
LIMITS = dict(stop_when_iteration_begins=127, max_scf_iterations=126, leg_wall_ceiling_s=20000, electron_maxstep=300)
EXIT_NOTE_BENIGN = "Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_DENORMAL"


def deck_text(symbols, positions):
    rows = "".join(f"  {s}  {p[0]!r}  {p[1]!r}  {p[2]!r}  {'0 0 0' if i == 0 else '1 1 1'}\n"
                   for i, (s, p) in enumerate(zip(symbols, positions)))
    return ("&CONTROL\n  calculation = 'relax'\n  forc_conv_thr = 2.0d-3\n/\n&SYSTEM\n  ibrav = 0\n"
            f"  nat = {len(symbols)}\n  ntyp = 3\n/\n&ELECTRONS\n/\n&IONS\n  ion_dynamics = 'bfgs'\n/\n"
            "ATOMIC_SPECIES\n  Cr  51.996  cr.UPF\n  Mn  54.938  mn.UPF\n  O  15.999  o.UPF\n"
            "CELL_PARAMETERS angstrom\n  10.0  0.0  0.0\n  0.0  10.0  0.0\n  0.0  0.0  20.0\n"
            "ATOMIC_POSITIONS angstrom\n" + rows + "K_POINTS automatic\n  1 1 1 0 0 0\n")


def output_text(symbols, final, energy=-500.0, mag=3.0, force_z=0.0005, *, bfgs=True, job_done=True, extra="",
                final_block=True, wall="11.00s", iterations=(30, 12), exit_note=EXIT_NOTE_BENIGN):
    n = len(symbols)
    its = ["\n".join(f"     iteration # {k:3d}     ecut=    80.00 Ry     beta= 0.30" for k in range(1, m + 1)) for m in iterations]
    rows = "\n".join(f"     atom {i + 1:4d} type  1   force =     0.00000000    0.00000000 {force_z:14.8f}" for i in range(n))
    parts = [f"     number of atoms/cell      =  {n:11d}",
             f"     total magnetization       =  {mag:8.2f} Bohr mag/cell",
             "     absolute magnetization    =     5.00 Bohr mag/cell", its[0],
             f"!    total energy              =  {energy - 0.1:.8f} Ry",
             f"     convergence has been achieved in  {iterations[0]} iterations",
             "     Forces acting on atoms (cartesian axes, Ry/au):", "", rows.replace(f"{force_z:14.8f}", f"{0.05:14.8f}"), "",
             "     Total force =     0.1", its[1],
             f"!    total energy              =  {energy:.8f} Ry",
             f"     convergence has been achieved in  {iterations[1]} iterations",
             "     Forces acting on atoms (cartesian axes, Ry/au):", "", rows, "",
             "     Total force =     0.001"]
    if bfgs:
        parts += ["     bfgs converged in   2 scf cycles and   1 bfgs steps", "     End of BFGS Geometry Optimization",
                  f"     Final energy             =  {energy:.10f} Ry"]
    if final_block:
        parts += ["Begin final coordinates", "", "ATOMIC_POSITIONS (angstrom)"]
        parts += [f"{s}  {p[0]:.10f}  {p[1]:.10f}  {p[2]:.10f}" + ("    0   0   0" if i == 0 else "") for i, (s, p) in enumerate(zip(symbols, final))]
        parts += ["End final coordinates"]
    parts += [f"     PWSCF        :     10.00s CPU     {wall} WALL", extra]
    if job_done:
        parts.append("   JOB DONE.")
    if exit_note:
        parts += [exit_note] * 3
    return "\n".join(parts) + "\n"


def recon_positions(lift=0.8, axial_up=0.0):
    p = [list(x) for x in CLEAN]
    p[2][2] += lift
    p[1][2] += axial_up
    return p + [[5.0, 5.0, p[2][2] + 1.59]]


def unrecon_positions():
    p = [list(x) for x in CLEAN]
    p[2][2] += 0.1
    return p + [[5.0, 5.0, p[2][2] + 1.62]]


def make_case(tmp_path, outputs):
    """outputs: {state: text or None}; returns (plan, runs_root, deck_root)."""
    deck_root, runs_root = tmp_path / "repo", tmp_path / "runs"
    decks = []
    starts = dict(slab=(SYMBOLS_SLAB, CLEAN), O_recon=(SYMBOLS_SLAB + ["O"], recon_positions()),
                  O_unrecon=(SYMBOLS_SLAB + ["O"], [list(x) for x in CLEAN] + [[5.0, 5.0, 9.635]]))
    for state, (symbols, positions) in starts.items():
        rel_path = f"decks/site/{state}__atomic.in"
        (deck_root / "decks/site").mkdir(parents=True, exist_ok=True)
        (deck_root / rel_path).write_text(deck_text(symbols, positions), encoding="utf-8")
        decks.append(dict(site="site", state=state, projector="atomic", job=f"{state}__atomic", path=rel_path,
                          manifest_dir="hea/site", forc_conv_thr_Ry_bohr=FORC, supervisor_limits=LIMITS))
        text = outputs.get(state)
        if text is not None:
            (runs_root / "hea/site").mkdir(parents=True, exist_ok=True)
            if isinstance(text, tuple):
                (runs_root / "hea/site" / f"{state}__atomic{text[0]}").write_text(text[1], encoding="utf-8")
            else:
                (runs_root / "hea/site" / f"{state}__atomic.out").write_text(text, encoding="utf-8")
    plan = dict(sites=[dict(tag="site", site_index=2, n_slab=4, axial_O_index=1, cell_A=CELL, clean_positions_A=CLEAN)], decks=decks)
    return plan, runs_root, deck_root


def run(tmp_path, outputs, th=TH):
    plan, runs_root, deck_root = make_case(tmp_path, outputs)
    return ro.readout(plan, dict(thresholds=th), runs_root, deck_root)


def good(state, **kw):
    symbols = SYMBOLS_SLAB + ([] if state == "slab" else ["O"])
    final = dict(slab=CLEAN, O_recon=recon_positions(), O_unrecon=unrecon_positions())[state]
    return output_text(symbols, kw.pop("final", final), **kw)


def outcome(result):
    return result["sites"][0]["outcome"]


def test_both_starts_reconstructed(tmp_path):
    r = run(tmp_path, dict(slab=good("slab"), O_recon=good("O_recon"), O_unrecon=good("O_unrecon", final=recon_positions(0.75))))
    assert r["leg_counts"] == {"ACCEPTED": 3} and r["pending"] == []
    assert r["sites"][0]["reference"] == "DFT_RELAXED_SLAB"
    assert outcome(r)["outcome"] == "RECONSTRUCTION_SUPPORTED"


def test_both_starts_unreconstructed(tmp_path):
    r = run(tmp_path, dict(slab=good("slab"), O_recon=good("O_recon", final=unrecon_positions()), O_unrecon=good("O_unrecon")))
    assert outcome(r)["outcome"] == "RECONSTRUCTION_NOT_SUPPORTED"


@pytest.mark.parametrize("e_recon, e_unrecon, order", [(-500.1, -500.0, "LIFTED_LOWER"), (-500.0, -500.1, "UNLIFTED_LOWER"),
                                                        (-500.0, -500.02, "ORDER_WITHIN_SPIN_START_SPREAD")])
def test_two_local_basins_energy_order(tmp_path, e_recon, e_unrecon, order):
    r = run(tmp_path, dict(slab=good("slab"), O_recon=good("O_recon", energy=e_recon), O_unrecon=good("O_unrecon", energy=e_unrecon)))
    o = outcome(r)
    assert o["outcome"] == "TWO_LOCAL_BASINS" and o["energy_order"] == order
    assert o["E_recon_minus_E_unrecon_eV"] == pytest.approx((e_recon - e_unrecon) * 13.605693122)


def test_crossed_and_magnetization_flag(tmp_path):
    r = run(tmp_path, dict(slab=good("slab"), O_recon=good("O_recon", final=unrecon_positions(), mag=3.0),
                           O_unrecon=good("O_unrecon", final=recon_positions(), mag=1.0)))
    o = outcome(r)
    assert o["outcome"] == "BASINS_CROSSED" and "MAGNETIZATION_DIFFERS" in o["flags"]


def test_mixed_and_off_site_are_undecided(tmp_path):
    mixed = recon_positions(lift=0.8, axial_up=0.9)                  # lifted but axial O followed
    off = unrecon_positions()
    off[4] = [2.0, 2.0, 8.0]                                           # O migrated next to Mn
    r = run(tmp_path, dict(slab=good("slab"), O_recon=good("O_recon", final=mixed), O_unrecon=good("O_unrecon", final=off)))
    legs = r["sites"][0]["legs"]
    assert legs["O_recon"]["assignment"]["basin"] == "MIXED_UNASSIGNED"
    assert legs["O_unrecon"]["assignment"]["basin"] == "O_OFF_SITE"
    assert outcome(r)["outcome"] == "UNDECIDED"


def test_slab_not_accepted_uses_flagged_mace_reference(tmp_path):
    r = run(tmp_path, dict(slab=good("slab", job_done=False), O_recon=good("O_recon"), O_unrecon=good("O_unrecon")))
    s = r["sites"][0]
    assert s["slab_status"] == "PENDING" and s["reference"] == "REFERENCE_MACE_SLAB"
    assert s["outcome"]["outcome"] == "TWO_LOCAL_BASINS"
    assert r["pending"] == ["site/slab__atomic"]


@pytest.mark.parametrize("text, status", [
    (None, "PENDING"),
    (good("O_recon", job_done=False), "PENDING"),
    (good("O_recon", extra="     convergence NOT achieved after 300 iterations: stopping"), "NOT CONVERGED"),
    (good("O_recon", extra="     The maximum number of steps has been reached."), "NOT CONVERGED"),
    (good("O_recon", extra="Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG"), "REJECTED"),
    (good("O_recon", exit_note="Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG IEEE_DENORMAL"), "REJECTED"),
    (good("O_recon", extra="Program received signal SIGFPE: Floating-point exception - erroneous arithmetic operation."), "REJECTED"),
    (good("O_recon", iterations=(127, 12)), "KILL_RULE_EXCEEDED"),
    (good("O_recon", wall="5h34m"), "KILL_RULE_EXCEEDED"),
    (good("O_recon", bfgs=False), "REJECTED"),
    (good("O_recon", final_block=False), "REJECTED_BY_READOUT"),
    (good("O_recon", force_z=0.01), "REJECTED_BY_READOUT"),
    (good("O_recon", final=[[2.5, 2.0, 5.0]] + recon_positions()[1:]), "REJECTED_BY_READOUT"),
])
def test_leg_acceptance(tmp_path, text, status):
    r = run(tmp_path, dict(slab=good("slab"), O_recon=text, O_unrecon=good("O_unrecon")))
    leg = next(l for l in r["legs"] if l["state"] == "O_recon")
    assert leg["status"] == status
    assert outcome(r)["outcome"] == "UNDECIDED"


def test_benign_exit_note_and_hour_wall_tokens_are_accepted(tmp_path):
    r = run(tmp_path, dict(slab=good("slab", wall="1h 5m"), O_recon=good("O_recon", wall="5h33m"), O_unrecon=good("O_unrecon", wall="3h 2m")))
    assert r["leg_counts"] == {"ACCEPTED": 3}
    leg = next(l for l in r["legs"] if l["state"] == "O_recon")
    assert leg["scorer"]["status_unmodified"] == "CONVERGED" and leg["scorer"]["exit_note_lines"] == 3
    assert leg["scorer"]["severe_failures"] == [] and leg["scorer"]["wall_s"] == 5 * 3600 + 33 * 60
    assert leg["kill_rule"] == dict(max_iteration_seen=30, wall_s=19980.0, leg_wall_ceiling_s=20000, exceeded=False, reasons=[])


@pytest.mark.parametrize("exit_note, status", [
    (EXIT_NOTE_BENIGN, "CONVERGED"),
    ("Note: The following floating-point exceptions are signalling: IEEE_DENORMAL", "CONVERGED"),
    ("Note: The following floating-point exceptions are signalling: IEEE_UNKNOWN_FLAG", "REJECTED"),
    ("Note: The following floating-point exceptions are signalling: IEEE_UNDERFLOW_FLAG IEEE_UNKNOWN_FLAG", "REJECTED"),
    ("Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG", "REJECTED"),
    ("Note: The following floating-point exceptions are signalling:", "REJECTED"),
])
def test_wrapper_preserves_canonical_notice_handling_and_evidence(tmp_path, exit_note, status):
    out = tmp_path / "x.out"
    raw = good("O_recon", wall="1h 5m", exit_note=exit_note).encode("utf-8")
    out.write_bytes(raw)
    original_wall_parser = ro.scorer._wall_seconds
    canonical = ro.scorer.parse_out(out, allow_relax=True)
    wrapped = ro.scorer_parse_out(out)
    assert canonical["status"] == wrapped["status"] == status
    assert all(wrapped[key] == value for key, value in canonical.items())
    assert out.read_bytes() == raw
    assert ro.scorer._wall_seconds is original_wall_parser


def test_lift_definition_flag(tmp_path):
    lateral = recon_positions(lift=0.3)
    lateral[2][0] += 0.45                              # 3-D displacement 0.54 > 0.5 while the lift is 0.3
    lateral[4] = [lateral[2][0], 5.0, lateral[2][2] + 1.62]
    r = run(tmp_path, dict(slab=good("slab"), O_recon=good("O_recon", final=lateral), O_unrecon=good("O_unrecon")))
    a = r["sites"][0]["legs"]["O_recon"]["assignment"]
    assert a["site_displacement_A"] == pytest.approx((0.3 ** 2 + 0.45 ** 2) ** 0.5)
    assert a["flags"] == ["LIFT_DEFINITIONS_DISAGREE"] and a["basin"] == "UNRECONSTRUCTED"


def test_canonical_scorer_agrees_with_every_registered_banked_hea_readout():
    c = ro.scorer_crosscheck()
    assert c["n_outputs"] > 0 and c["n_corrected_agree_with_readout"] == c["n_outputs"]
    assert c["scorer_input_corrections"] == []
    assert c["scorer_unmodified_counts"] == c["scorer_canonical_counts"] == c["scorer_corrected_counts"]
    assert c["scorer_corrected_counts"]["CONVERGED"] == c["readout_status_counts"]["ACCEPTED"]


def test_killed_sidecar(tmp_path):
    plan, runs_root, deck_root = make_case(tmp_path, dict(slab=good("slab"), O_recon=good("O_recon"), O_unrecon=good("O_unrecon")))
    (runs_root / "hea/site/O_recon__atomic.KILLED").write_text("iteration cap\n", encoding="utf-8")
    r = ro.readout(plan, dict(thresholds=TH), runs_root, deck_root)
    assert next(l for l in r["legs"] if l["state"] == "O_recon")["status"] == "KILLED"


def test_readout_of_the_prepared_plan_is_pending(tmp_path):
    plan = ro.read_json(ro.PLAN)
    decisions = ro.read_json(ro.DECISIONS)
    r = ro.readout(plan, decisions, tmp_path / "empty_runs")
    assert r["leg_counts"] == {"PENDING": 18} and len(r["sites"]) == 6
    assert all(s["outcome"]["outcome"] == "UNDECIDED" for s in r["sites"])


@pytest.mark.parametrize("mutate, reason", [
    (lambda t: t.replace("Final energy             =  -500.0000000000", "Final energy             =  -499.0000000000"),
     "Final energy differs"),
    (lambda t: t.replace("     Final energy             =  -500.0000000000 Ry\n", ""), "Final energy"),
    (lambda t: t.replace("bfgs converged in   2 scf cycles", "bfgs converged in   3 scf cycles"), "cycles"),
    (lambda t: t.replace("Begin final coordinates", "Begin final coordinates\nBegin final coordinates"), "exactly one final-coordinate"),
    (lambda t: t.replace("number of atoms/cell      =            5", "number of atoms/cell      =            6"), "printed nat"),
    (lambda t: t.replace("     PWSCF        :     10.00s CPU     11.00s WALL\n", ""), "kill-rule"),
    (lambda t: t.replace("11.00s WALL", "bad WALL"), "malformed scorer evidence"),
    (lambda t: t.replace("End final coordinates", "O 5.0 5.0 20.0\nEnd final coordinates"), "final coordinates"),
])
def test_malformed_completed_relaxation_is_rejected(tmp_path, mutate, reason):
    result = run(tmp_path, dict(slab=good("slab"), O_recon=mutate(good("O_recon")), O_unrecon=good("O_unrecon")))
    leg = next(x for x in result["legs"] if x["state"] == "O_recon")
    assert leg["status"] == "REJECTED_BY_READOUT"
    assert any(reason in r for r in leg["reasons"]), leg["reasons"]
    assert outcome(result)["outcome"] == "UNDECIDED"


def test_changed_frozen_deck_is_rejected(tmp_path):
    plan, runs_root, deck_root = make_case(tmp_path, dict(slab=good("slab"), O_recon=good("O_recon"), O_unrecon=good("O_unrecon")))
    deck = next(x for x in plan["decks"] if x["state"] == "O_recon")
    source = deck_root / deck["path"]
    deck["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    source.write_text(source.read_text(encoding="utf-8").replace("2.0d-3", "2.1d-3"), encoding="utf-8")
    leg = ro.read_leg(deck, runs_root, deck_root)
    assert leg["status"] == "REJECTED_BY_READOUT" and "frozen plan" in leg["reasons"][0]


def test_real_converged_Cr_relaxation_passes_final_evidence_checks():
    source = ROOT / "runs/Cr_slab/s0_O.in"
    deck = dict(site="Cr_slab", state="O_recon", projector="atomic", job="s0_O",
                path="runs/Cr_slab/s0_O.in", manifest_dir="Cr_slab",
                sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                forc_conv_thr_Ry_bohr=FORC, supervisor_limits=LIMITS)
    leg = ro.read_leg(deck, ROOT / "runs")
    assert leg["status"] == "ACCEPTED", leg
    assert leg["bfgs_scf_cycles"] == 12 and leg["bfgs_steps"] == 11
    assert leg["energy_eV"] == pytest.approx(leg["final_energy_eV"], abs=2e-7)



def test_primary_selection_keeps_historical_eighteen_leg_plan(tmp_path):
    plan = ro.read_json(ro.PLAN)
    primary = ro.primary_plan(plan)
    assert len(plan["decks"]) == 18 and len(primary["decks"]) == 9
    result = ro.readout(primary, ro.read_json(ro.DECISIONS), tmp_path / "empty")
    assert result["leg_counts"] == {"PENDING": 9} and len(result["sites"]) == 3


def test_terminal_qc_failure_suppresses_otherwise_usable_energy(tmp_path):
    plan, runs_root, deck_root = make_case(tmp_path, dict(slab=good("slab"), O_recon=good("O_recon"), O_unrecon=good("O_unrecon")))
    failure = {"site/O_recon__atomic": dict(status="QC_EVIDENCE_INVALID", reasons=["QC hash mismatch"])}
    result = ro.readout(plan, dict(thresholds=TH), runs_root, deck_root, terminal_failures=failure)
    leg = next(x for x in result["legs"] if x["state"] == "O_recon")
    assert leg["status"] == "QC_EVIDENCE_INVALID" and leg["numerical_readout_status"] == "ACCEPTED"
    assert "energy_eV" not in leg and outcome(result)["outcome"] == "UNDECIDED"
    failure["site/O_recon__atomic"]["status"] = "ACCEPTED"
    with pytest.raises(ValueError, match="invalid terminal"):
        ro.readout(plan, dict(thresholds=TH), runs_root, deck_root, terminal_failures=failure)
