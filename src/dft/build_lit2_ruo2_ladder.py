#!/usr/bin/env python3
"""LIT-2 trimmed core: the termination check (docs/43 AMENDMENT 5, A5.2 = D2).

THE PRE-REGISTRATION IS docs/43 A5.2, NOT THIS FILE
---------------------------------------------------
This file implements the registered trimmed scope -- "the RuO2 benchmark plus
the Cr O-covered-preference check only" -- and deliberately does not restate
it. The full Ru/Ir/Cr termination campaign and the U-flip extension are D3,
deferred, and NOTHING here builds them. Where this file and docs/43 disagree,
docs/43 wins and this file is the thing that changes.

The design, in one line: static CHE surface Pourbaix in the existing 2x1 cells
over the terminations representable at that size -- clean / 1 ML *O_cus /
mixed 1:1 *OH-*O / 1 ML *OH (plus an O-depleted variant for Cr) -- with
block-1A outputs REUSED, NOT RE-RUN, wherever they already are these states.

What is reused (A5.2, verbatim rule) and what is new
----------------------------------------------------
Reused per metal (declared row by row in lit2_manifest.json, with on-disk
status read at build time):

  clean          probe/{M}_cellsym/ref__2x1v          (2x1 clean slab)
  1 ML *O_cus    probe/{M}_cellsym/s0_O__2x1o_{mir,off}   working *O + spectator
                 *O = every cus site O-covered ("the 2x1 neighbour-*O arm with
                 working *O is 1 ML *O_cus", A5.2)
  mixed 1:1      probe/{M}_cellsym/s0_OH__2x1o_{mir,off}  working *OH +
                 spectator *O ("working *OH with *O spectator is the mixed
                 rung", A5.2)

Genuinely new relaxations emitted here (3 total; each Cr one gets a __g1
GATE-1 child via --gate1 once converged, A5.7):

  cov_2OH__2x1_off    Ru + Cr   1 ML *OH: both cus sites carry the relaxed
                                production *OH, assembled half-and-half like
                                build_cellsym_pilot (each half gets the s0_OH
                                substrate). Off-plane start: the first-half OH
                                is yawed +90 deg, the second-half OH -90 deg
                                (yaw270), so both fragments break the mirror
                                and the two sites are not artificially
                                equivalent by translation.
  cov_Ovac__2x1_off   Cr only   the O-depleted variant: the 2x1 clean slab
                                with ONE of its two bridging O removed (the
                                minimal O depletion representable at 2x1). The
                                REMAINING bridging O is kicked +0.35 A in y --
                                the vacancy alone leaves the y-mirror intact,
                                and nosym on an exactly symmetric input does
                                nothing (lessons.md 2026-08-09); 0.35 A is the
                                s2-A.2 spectator-kick magnitude.

INTERPRETIVE CHOICES the registered text under-determines (also echoed in
lit2_manifest.json `registered_ambiguities`, and reported to Frank before any
launch):
  1. A5.2's cost line says "~12 relaxations", but its reuse rule leaves only
     the three states above genuinely new. The reuse rule is the registered
     text; the parenthetical is a cost estimate. 3 decks are emitted.
  2. "O-depleted variant" does not say which O or how many: one bridging O of
     the 2x1 cell (1/2 of the bridging row) was chosen as the minimal
     depletion; in-plane surface O removal would break the coordination shell
     of a 6-fold metal instead and is not what Cao's oxygen-environment
     finding is about.
  3. New terminations get the off-plane arm only (A5.2 lists "off-plane
     starts, nosym/noinv"); no mirror partner is registered, because LIT-2
     scores a Pourbaix ladder, not a dE_sym pair.
  4. probe/{M}_cellsym/ref__2x1o (working cus BARE + spectator *O = 1/2 ML O)
     is on disk for free and is recorded as CONTEXT in the manifest, but it is
     NOT one of the registered rungs and must not enter the scored ladder
     without its own amendment.

The readout (not built here; registered in A5.2): the coarsened-Qiu two-sided
RuO2 benchmark -- PASS iff the ordering with falling potential is full-O ->
mixed -> full-*OH AND both transition potentials fall within +/-0.25 V of
Qiu's AIMD brackets (~1.50 V / ~1.24 V) -- and the Cr decision rule: O-covered
preferred by > 0.1 eV per site at U = 1.23 V + eta(Cr) => every
clean-termination Cr energetics row carries a conditional-on-termination flag.
The flag qualifies; it does not retract.

Usage
-----
  PYTHONPATH=src python src/dft/build_lit2_ruo2_ladder.py
  PYTHONPATH=src python src/dft/build_lit2_ruo2_ladder.py --dry-run
  PYTHONPATH=src python src/dft/build_lit2_ruo2_ladder.py --gate1   # wave 2,
      # after the Cr relaxations return; refuses on unconverged parents

NOTHING IS DEPLOYED BY THIS SCRIPT. The manifests it writes carry NOT-DEPLOYED
headers; docs/43 A5.7 gates the launch on the 1A manifest being drained.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_decks import (parse_input_deck, parse_final_coordinates,  # noqa: E402
                         relax_final_energy_ev, write_probe, parse_variant)
from build_cellsym_pilot import (  # noqa: E402
    DOC43, shift_x, yaw_fragment, kick_y, cus_metal, load,
    final_magnetisation, est_hours_np4, est_bracket_np4,
    STEP_MULT_2X1, STEP_MULT_2X1_BRACKET, SCF_STEP_EQUIV,
    MAX_SECONDS_SAFETY, MAX_SECONDS_FLOOR, RANK_SPEEDUP_NP20,
    SPECTATOR_KICK_A)
from lit_deckgen import (  # noqa: E402
    prereg_check, guard_deck, insert_max_seconds, write_deck, write_text,
    nk_for, bridging_O_index, out_status, ceil_steps, NP_LONG, NCONC_LONG)

# --------------------------------------------------------------------------
# PREREG -- pointers, not copies (build_cellsym_pilot round-2 finding N1).
# Each entry: (value, docs/43 clause, literal substring still present there).
# --------------------------------------------------------------------------
PREREG = {
    "registered_scope_trimmed": (
        True, "A5.2",
        "benchmark plus the Cr O-covered-preference check only"),
    "terminations_2x1": (
        ("clean", "O_full", "mixed_OH_O", "OH_full"), "A5.2",
        "clean / 1 ML *O_cus / mixed 1:1 *OH–*O / 1 ML *OH"),
    "cr_o_depleted_variant": (
        True, "A5.2", "(plus an O-depleted variant for Cr)"),
    "reuse_rule": (
        True, "A5.2", "Block-1A outputs are **reused, not re-run**"),
    "qiu_tolerance_V": (
        0.25, "A5.2", "within **±0.25 V** of Qiu's AIMD brackets"),
    "qiu_brackets_V": (
        (1.50, 1.24), "A5.2", "Qiu's AIMD brackets (~1.50 V and ~1.24 V"),
    "qiu_ordering": (
        True, "A5.2", "full-O → mixed → full-*OH"),
    "cr_flag_threshold_eV_per_site": (
        0.1, "A5.2",
        "prefers an O-covered termination by > 0.1 eV per site at U = 1.23 V"),
    "offplane_min_dy_A": (
        0.30, "s2-A.1", "y-translation of ≥ 0.30 Å"),
    "gate1_children_cr": (
        True, "A5.7", "Every new Cr relaxation gets its GATE-1 child"),
    "not_deployed_gate": (
        True, "A5.7",
        "manifest on a box is drained, or on a separately provisioned box"),
}

#: production sources, identical to build_cellsym_pilot.METALS for Ru/Cr. Ir is
#: DELIBERATELY absent: the trimmed core is RuO2 benchmark + Cr check; the full
#: per-metal campaign is D3, deferred.
METALS = {
    "Ru": dict(rundir="runs/Ru_anchor", n_slab=18,
               kmesh_1x1=("8", "4", "1"), magnetic=False),
    "Cr": dict(rundir="runs/Cr_slab", n_slab=18,
               kmesh_1x1=("9", "4", "1"), magnetic=True),
}
KMESH_2X1 = ("4", "4", "1")   # the block-1A 2x1 mesh; every reused rung ran it
NKP_2X1_NOSYM = 16            # 4x4 grid, no symmetry reduction under nosym

#: y-kick of the surviving bridging O in cov_Ovac. Same magnitude as the
#: s2-A.2 spectator kick; the vacancy leaves the y-mirror intact (the bridging
#: row maps onto itself), so without a physical displacement the off-plane arm
#: would not be performed.
OVAC_KICK_A = SPECTATOR_KICK_A

#: ionic-step allowance for the vacancy job. ASSUMED, labelled: the spliced
#: 2x1 multiplier (1.5x, measured-floor reasoning in build_cellsym_pilot)
#: assumes both halves start at relaxed geometries; removing an atom adds a
#: genuinely new local rearrangement on top, so the allowance is doubled.
OVAC_STEP_MULT = 2.0
OVAC_STEP_MULT_BRACKET = (1.5, 3.0)


def build(a):
    verified = prereg_check(PREREG, "LIT-2")
    outroot = a.out
    jobs, reuse_rows, geometry = [], [], []

    for M, cfg in METALS.items():
        rd, n_slab = cfg["rundir"], cfg["n_slab"]
        magnetic = cfg["magnetic"]
        outdir = os.path.join(outroot, f"{M}_lit2")

        src_slab = load(rd, "slab")
        src_oh = load(rd, "s0_OH")
        slab_clean = src_slab["pos"]
        slab_oh, ads_oh = src_oh["pos"][:n_slab], src_oh["pos"][n_slab:]
        if [q[0] for q in ads_oh] != ["O", "H"]:
            raise SystemExit(f"refusing to build {M}: s0_OH adsorbate is "
                             f"{[q[0] for q in ads_oh]}, expected [O, H]")
        cus = cus_metal(slab_clean, ads_oh)
        y_mirror = cus[2]
        a1 = src_slab["deck"]["cell"][0][0]
        mask = src_slab["deck"]["flags"][:n_slab]

        def emit(name, deck_src_job, positions, flags, sym_note, steps,
                 steps_basis, dy_checks, cell_mult=2.0, note=""):
            d = dict(parse_input_deck(os.path.join(rd, deck_src_job + ".in")))
            d["flags"] = list(flags)
            d["nosym"] = True
            d["cell"] = [[d["cell"][0][0] * cell_mult, 0.0, 0.0],
                         list(d["cell"][1]), list(d["cell"][2])]
            d["kpts"] = ("automatic", list(KMESH_2X1) + ["0", "0", "0"])
            text, _ = write_probe(d, positions, parse_variant("base"), name,
                                  a.pseudo_dir, a.scratch, calculation="relax")
            nkp = NKP_2X1_NOSYM
            h4 = est_hours_np4(nkp, steps, magnetic, True)
            lo4, hi4 = est_bracket_np4(nkp, steps, magnetic, True)
            h_run = h4 / RANK_SPEEDUP_NP20
            ms = max(MAX_SECONDS_FLOOR,
                     int(round(MAX_SECONDS_SAFETY * h_run * 3600)))
            text = insert_max_seconds(text, ms)
            meta = guard_deck(text, os.path.join(rd, deck_src_job + ".in"),
                              name, dict(
                allowed={"mixing_mode"},   # the emitter's known, declared
                # deviation: Cr production ADSLAB decks carry no mixing_mode,
                # write_probe hardcodes local-TF (build_cellsym_pilot module
                # docstring, "Known, INTENDED deviation")
                expected_mags=None, cell_mult=cell_mult, kmesh=KMESH_2X1,
                nat=len(positions), flags=flags, dy_checks=dy_checks,
                require_offplane=True, max_seconds=ms))
            md5 = write_deck(outdir, name, text, a.dry_run)
            nk = nk_for(nkp, NP_LONG)
            jobs.append(dict(
                metal=M, job=name, deck_source=deck_src_job,
                termination=sym_note, calculation="relax", sym="off",
                kmesh=" ".join(KMESH_2X1), n_kpt_est=nkp, nk=nk,
                np_run=NP_LONG, steps_est=steps, steps_basis=steps_basis,
                est_hours_np4=round(h4, 1), est_hours_at_np20=round(h_run, 1),
                est_hours_bracket_np4=[round(lo4, 1), round(hi4, 1)],
                max_seconds=ms, nspin=d["nspin"], note=note, md5=md5, **meta))
            print(f"  {M} {name}: {len(positions)} atoms, ~{h_run:.1f} h at "
                  f"NP={NP_LONG}")

        # ---- 1 ML *OH: both cus sites carry the relaxed production *OH ----
        oh_a = yaw_fragment(ads_oh, 90.0)
        oh_b = shift_x(yaw_fragment(ads_oh, 270.0), a1)
        pos = slab_oh + shift_x(slab_oh, a1) + oh_a + oh_b
        flags = list(mask) * 2 + ["1 1 1"] * 4
        n2 = 2 * n_slab
        steps = ceil_steps(src_oh["steps_1x1"], STEP_MULT_2X1)
        emit("cov_2OH__2x1_off", "s0_OH", pos, flags, "OH_full (1 ML *OH_cus)",
             steps,
             dict(measured_1x1_steps=src_oh["steps_1x1"],
                  source=src_oh["steps_src"].replace("\\", "/"),
                  multiplier=STEP_MULT_2X1,
                  bracket=list(STEP_MULT_2X1_BRACKET),
                  basis="measured s0_OH 1x1 ionic steps x STEP_MULT_2X1 "
                        "(assumed, build_cellsym_pilot module docstring)"),
             dy_checks=[(n2, y_mirror), (n2 + 1, y_mirror),
                        (n2 + 2, y_mirror), (n2 + 3, y_mirror)],
             note="both halves carry the s0_OH relaxed substrate + its *OH; "
                  "first-half OH yawed +90, second-half -90 (off-plane start "
                  "on BOTH fragments)")

        # ---- O-depleted variant, Cr only (A5.2 parenthetical) --------------
        if M == "Cr":
            ib = bridging_O_index(slab_clean, n_slab)
            half1 = list(slab_clean)
            kicked = kick_y([half1[ib]], OVAC_KICK_A)[0]
            unkicked_y = half1[ib][2]
            half1[ib] = kicked
            half2 = [q for i, q in enumerate(shift_x(slab_clean, a1))
                     if i != ib]
            pos = half1 + half2
            flags = list(mask) + [f for i, f in enumerate(mask) if i != ib]
            if mask[ib] != "1 1 1":
                raise SystemExit("refusing to build cov_Ovac: the bridging O "
                                 "is a constrained atom; removing it would "
                                 "change the frozen layers")
            steps = ceil_steps(src_slab["steps_1x1"], OVAC_STEP_MULT)
            emit("cov_Ovac__2x1_off", "slab", pos, flags,
                 "O_depleted (2x1 clean minus one bridging O)", steps,
                 dict(measured_1x1_steps=src_slab["steps_1x1"],
                      source=src_slab["steps_src"].replace("\\", "/"),
                      multiplier=OVAC_STEP_MULT,
                      bracket=list(OVAC_STEP_MULT_BRACKET),
                      basis="measured clean-slab 1x1 ionic steps x "
                            "OVAC_STEP_MULT (ASSUMED: vacancy adds a new "
                            "local rearrangement on top of the splice)"),
                 dy_checks=[(ib, unkicked_y)],
                 note=f"one of the two bridging O removed (atom {ib} of the "
                      f"second half); the surviving bridging O (atom {ib}) "
                      f"kicked +{OVAC_KICK_A} A in y so the off-plane arm is "
                      "performed, not just flagged")

        # ---- the reused block-1A rungs, status read from disk --------------
        cs = os.path.join(outroot, f"{M}_cellsym")
        for rung, jobname, calc in (
                ("clean", "ref__2x1v", "relax"),
                ("O_full", "s0_O__2x1o_mir", "relax"),
                ("O_full", "s0_O__2x1o_off", "relax"),
                ("mixed_OH_O", "s0_OH__2x1o_mir", "relax"),
                ("mixed_OH_O", "s0_OH__2x1o_off", "relax")):
            p = os.path.join(cs, jobname + ".out")
            reuse_rows.append(dict(
                metal=M, rung=rung, job=f"probe/{M}_cellsym/{jobname}",
                status=out_status(p, calc),
                gate1_required=(M == "Cr"),
                gate1_note=("block-1A wave-2 obligation (s2-A.3(b)/amendment "
                            "4 s2); LIT-2 scores GATE-1-passed Cr energies "
                            "only" if M == "Cr" else "")))
        reuse_rows.append(dict(
            metal=M, rung="CONTEXT-ONLY (1/2 ML O; not a registered rung)",
            job=f"probe/{M}_cellsym/ref__2x1o",
            status=out_status(os.path.join(cs, "ref__2x1o.out"), "relax"),
            gate1_required=False,
            gate1_note="present on disk for free; entering the scored ladder "
                       "would need its own amendment"))

        geometry.append(dict(metal=M, a1=a1, y_mirror=round(y_mirror, 6),
                             kmesh_2x1=" ".join(KMESH_2X1),
                             gas_references=[f"{rd}/H2O.out", f"{rd}/H2.out"]))

    # ---- manifests ----------------------------------------------------------
    jobs.sort(key=lambda j: -j["est_hours_at_np20"])
    man_lines = [
        "# NOT-DEPLOYED -- prepared decks only, nothing queued, nothing",
        "# launched. docs/43 A5.7: LIT decks queue only after the 1A manifest",
        "# on a box is drained, or on a separately provisioned box. Launch",
        "# authority: Frank.",
        "# LIT-2 trimmed core (docs/43 A5.2 = D2): 3 new termination",
        "# relaxations; every other rung of the ladder is a REUSED block-1A",
        "# output (lit2_manifest.json `reused_rungs`).",
        f"# NP={NP_LONG} NCONC={NCONC_LONG}",
        f"#   bash queue_r1.sh m_lit2_np20.txt {NP_LONG} {NCONC_LONG}",
        "# NP is an exact multiple of every nk below; NP x NCONC <= 23 usable",
        "# cores. Longest first.",
    ]
    man_lines += [f"probe/{j['metal']}_lit2 {j['job']} .in {j['nk']}"
                  for j in jobs]
    write_text(os.path.join(outroot, "m_lit2_np20.txt"),
               "\n".join(man_lines) + "\n", a.dry_run)

    manifest = dict(
        block="LIT-2 trimmed core -- termination check (docs/43 A5.2 = D2)",
        status="NOT_DEPLOYED",
        prereg=dict(document=DOC43, section="AMENDMENT 5, A5.2 (+ A5.7)",
                    rule="docs/43 is the only pre-registration. Where this "
                         "manifest and docs/43 disagree, docs/43 wins.",
                    anchors_verified=verified),
        design="static CHE surface Pourbaix in the existing 2x1 cells; "
               "registered rungs clean / 1 ML *O_cus / mixed 1:1 *OH-*O / "
               "1 ML *OH (+ O-depleted for Cr); block-1A outputs reused, "
               "not re-run",
        benchmark=dict(
            what="coarsened-Qiu RuO2 coverage ladder, two-sided, registered "
                 "before any job runs",
            pass_rule="(i) ordering with falling potential is full-O -> "
                      "mixed -> full-*OH AND (ii) both transition potentials "
                      "within +/-0.25 V of Qiu's AIMD brackets ~1.50 V and "
                      "~1.24 V",
            on_pass="Cr column reported as validated-by-proxy",
            on_fail="Cr column still reported, labelled vacuum-CHE-only, "
                    "with the measured RuO2 discrepancy attached as its "
                    "systematic error",
            gate_on_1a_results="none -- neither outcome gates any 1A/1B/1C "
                               "result"),
        cr_decision_rule="if Cr prefers an O-covered termination by > 0.1 eV "
                         "per site at U = 1.23 V + eta(Cr), every "
                         "clean-termination Cr energetics row carries a "
                         "conditional-on-termination flag (qualifies, does "
                         "not retract)",
        registered_ambiguities=[
            "A5.2's cost parenthetical says ~12 relaxations; the registered "
            "reuse rule leaves 3 genuinely new. The reuse rule was followed.",
            "'O-depleted variant' does not name the O: one bridging O of the "
            "2x1 cell was removed (minimal depletion representable at 2x1); "
            "the surviving bridging O carries the off-plane kick.",
            "new terminations are emitted off-plane only (A5.2 lists "
            "off-plane starts + nosym/noinv; no mirror partner registered).",
            "ref__2x1o (1/2 ML O) is on disk but is NOT a registered rung; "
            "recorded as context only."],
        reused_rungs=reuse_rows,
        geometry=geometry,
        manifests=dict(long=dict(
            file="m_lit2_np20.txt", np=NP_LONG, nconc=NCONC_LONG,
            n_jobs=len(jobs),
            command=f"bash queue_r1.sh m_lit2_np20.txt {NP_LONG} {NCONC_LONG}",
            sum_hours=round(sum(j["est_hours_at_np20"] for j in jobs), 1),
            longest_job_hours=max(j["est_hours_at_np20"] for j in jobs))),
        jobs=jobs)
    write_text(os.path.join(outroot, "lit2_manifest.json"),
               json.dumps(manifest, indent=2) + "\n", a.dry_run)
    print(f"{len(jobs)} new LIT-2 decks ({sum(1 for j in jobs if j['metal']=='Cr')} Cr, "
          f"{sum(1 for j in jobs if j['metal']=='Ru')} Ru) + "
          f"{len(reuse_rows)} declared reuse rows -> {outroot} [NOT DEPLOYED]"
          + ("  (dry run)" if a.dry_run else ""))
    return 0


def cmd_gate1(a):
    """Wave 2 (docs/43 A5.7: every new Cr relaxation gets its GATE-1 child).

    One fresh-density fixed-geometry SCF per converged Cr LIT-2 relaxation, at
    its own final coordinates, symmetry treatment, k-mesh and cell. Refuses --
    for every target at once -- if any parent is not scoreable yet."""
    man_path = os.path.join(a.out, "lit2_manifest.json")
    if not os.path.exists(man_path):
        raise SystemExit(f"refusing: {man_path} not found; build LIT-2 first")
    man = json.load(open(man_path, encoding="utf-8"))
    targets = [j for j in man["jobs"]
               if j["metal"] == "Cr" and j["calculation"] == "relax"]
    if not targets:
        raise SystemExit("refusing: no Cr relaxations in the LIT-2 manifest")

    outdir = os.path.join(a.out, "Cr_lit2")
    rd = METALS["Cr"]["rundir"]
    not_ready, rows, lines = [], [], []
    for j in targets:
        op = os.path.join(outdir, j["job"] + ".out")
        if not os.path.exists(op):
            not_ready.append(f"{j['job']}: no .out")
            continue
        txt = open(op, errors="replace").read()
        if "bfgs converged" not in txt:
            not_ready.append(f"{j['job']}: no `bfgs converged` (JOB DONE "
                             f"present: {'JOB DONE' in txt})")
            continue
        pos, prov = parse_final_coordinates(op)
        if pos is None or prov != "final" or len(pos) != j["nat"]:
            not_ready.append(f"{j['job']}: geometry provenance {prov!r}")
            continue
        name = j["job"] + "__g1"
        d = dict(parse_input_deck(os.path.join(rd, j["deck_source"] + ".in")))
        d["flags"] = list(re_flags(a.out, j))
        d["nosym"] = True
        d["cell"] = [[d["cell"][0][0] * 2.0, 0.0, 0.0],
                     list(d["cell"][1]), list(d["cell"][2])]
        d["kpts"] = ("automatic", list(KMESH_2X1) + ["0", "0", "0"])
        text, _ = write_probe(d, pos, parse_variant("base"), name,
                              a.pseudo_dir, a.scratch, calculation="scf")
        h4 = est_hours_np4(j["n_kpt_est"], SCF_STEP_EQUIV, True, True)
        h_run = h4 / RANK_SPEEDUP_NP20
        ms = max(MAX_SECONDS_FLOOR, int(round(MAX_SECONDS_SAFETY * h_run * 3600)))
        text = insert_max_seconds(text, ms)
        guard_deck(text, os.path.join(rd, j["deck_source"] + ".in"), name,
                   dict(allowed={"mixing_mode", "calculation"},
                        expected_mags=None, cell_mult=2.0, kmesh=KMESH_2X1,
                        nat=j["nat"], flags=d["flags"], dy_checks=[],
                        require_offplane=False, max_seconds=ms))
        md5 = write_deck(outdir, name, text, a.dry_run)
        tot, ab = final_magnetisation(op)
        rows.append(dict(job=name, parent=j["job"], nk=j["nk"],
                         max_seconds=ms, est_hours_at_np20=round(h_run, 1),
                         parent_final_energy_ev=relax_final_energy_ev(op),
                         parent_total_magnetization=tot,
                         parent_absolute_magnetization=ab, md5=md5))
        lines.append(f"probe/Cr_lit2 {name} .in {j['nk']}")

    if not_ready:
        raise SystemExit("refusing to emit any LIT-2 GATE-1 deck; "
                         f"{len(not_ready)} of {len(targets)} Cr relaxations "
                         "are not scoreable yet:\n  " + "\n  ".join(not_ready))

    head = ["# NOT-DEPLOYED -- LIT-2 GATE-1 children (docs/43 A5.7 / s2-A.3(b),",
            "# tolerance 5 meV). One fresh-density fixed-geometry SCF per",
            "# converged Cr LIT-2 relaxation.",
            f"# NP={NP_LONG} NCONC={NCONC_LONG}",
            f"#   bash queue_r1.sh m_lit2_gate1.txt {NP_LONG} {NCONC_LONG}"]
    write_text(os.path.join(a.out, "m_lit2_gate1.txt"),
               "\n".join(head + lines) + "\n", a.dry_run)
    write_text(os.path.join(a.out, "lit2_gate1_manifest.json"),
               json.dumps(dict(prereg=f"{DOC43} A5.7 / s2-A.3(b)",
                               status="NOT_DEPLOYED", jobs=rows), indent=2)
               + "\n", a.dry_run)
    print(f"{len(rows)} LIT-2 GATE-1 SCFs -> {os.path.join(a.out, 'Cr_lit2')} "
          "[NOT DEPLOYED]")
    return 0


def re_flags(outroot, j):
    """The parent's own emitted flags, re-read from its deck bytes rather than
    re-derived (build_cellsym_pilot N3: a child must run at the parent's own
    treatment, verified against the parent's bytes)."""
    p = os.path.join(outroot, f"{j['metal']}_lit2", j["job"] + ".in")
    d = parse_input_deck(p)
    if not re.search(r"^\s*nosym\s*=\s*\.true\.", d["raw"], re.M | re.I):
        raise SystemExit(f"refusing: parent deck {p} does not carry nosym; a "
                         "GATE-1 child must run at the parent's own symmetry "
                         "treatment (N3)")
    return d["flags"]


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.split("\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join("runs", "probe"))
    ap.add_argument("--pseudo-dir", default="/usr/share/espresso/pseudo")
    ap.add_argument("--scratch", default="./tmp")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--gate1", action="store_true",
                    help="wave 2: emit GATE-1 children for converged Cr "
                         "LIT-2 relaxations")
    a = ap.parse_args()
    return cmd_gate1(a) if a.gate1 else build(a)


if __name__ == "__main__":
    sys.exit(main())
