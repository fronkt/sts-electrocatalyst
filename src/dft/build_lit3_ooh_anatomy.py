#!/usr/bin/env python3
"""LIT-3 compute decks: the *OOH anatomy, parts (b) and (c) (docs/43 A5.3 = D4).

THE PRE-REGISTRATION IS docs/43 A5.3, NOT THIS FILE
---------------------------------------------------
Part (a) -- the zero-DFT O-O fingerprint classification -- is NOT here; it is
`src/dft/lit3_ooh_fingerprints.py` and runs today with no compute. This file
emits the two registered compute arms:

  (b) the *OO-H spot check, uniform across Cr, Ir, Ru (P6/P19: never Cr
      alone): one *OO-H initialization -- superoxo O-O + H on bridging O --
      per metal, "+/- spin starts", standing protocol, GATE-1 children for Cr.
  (c) the Cr conformer x spin factorial including one nspin=1 control (the
      Gauthier diagnostic for the 175 meV metastable-magnetic *OOH state,
      docs/41 s6f).

Registered constraint, carried into the manifest: outputs of (b) and (c) are
mechanism-caveat columns or uniformly-applied tier_v3 inputs -- never a
Cr-specific rescue (P6). The docs/43 s2 registered Cr prediction (the *OOH
symmetry correction changes eta(Cr) by exactly zero) is untouched.

Geometry construction, stated numerically
-----------------------------------------
*OO-H (b): start from the relaxed production *OOH geometry (Cr redirected to
runs/probe/Cr_basin/s0_OOH.out, the corrected basin -- docs/41 s6f, same
redirect as build_cellsym_pilot). The binding O stays put (the M-O bond is
untouched, P10's reasoning); the outer O is yawed 90 deg about the vertical
axis through the binding O and rescaled to O-O = 1.31 A, the midpoint of the
registered superoxo band 1.30-1.32 A; the H is detached and placed on the
slab's bridging O (the highest-z O of the slab half, +1.15 A above every
other top-layer O in the production geometries) at O-H = 0.98 A with a
+0.35 A y-component so the bridge row's own mirror is also physically broken.

Conformers (c): the P10 yaw operation, deg in {90, 270} -- exactly the
orientation set the campaign already measured on Ir/Ru (runs/probe/
{Ir,Ru}_orient) -- applied to the corrected-basin Cr *OOH. The mirror (yaw0)
conformer is NOT re-run: it is on disk twice (production relaxation =
metastable magnetic solution; basin restart = corrected solution) and A5.2's
reuse rule applies. yaw90 x production-spin is the pending block-1A row
probe/Cr_cellsym/s0_OOH__1x1_off and is likewise declared REUSE, not re-run.

INTERPRETIVE CHOICES the registered text under-determines (echoed in
lit3_manifest.json `registered_ambiguities`; decks are NOT-DEPLOYED and the
+/- reading needs Frank's sign-off before launch):
  1. "+/- spin starts": a global sign flip of every starting_magnetization is
     EXACTLY degenerate in a collinear calculation (time reversal), so +/-
     cannot mean flipping the whole start. It is implemented as the sign of
     the O-channel seed relative to the metal sublattice --
       magp: the production start (Cr 0.6, O 0.0)
       magm: Cr 0.6 with starting_magnetization(O) = -0.5, seeding the
             adsorbate/O sublattice antiparallel to Cr (the physically
             distinct alignment Gauthier 2017 p.4 says matters for *OOH)
     -- because a per-adsorbate-atom seed would need a fourth species and
     change ntyp, a larger protocol deviation. Ru and Ir run nspin = 1 in
     production; a "spin start" does not exist at nspin = 1, so they get ONE
     deck each at the standing protocol, which also keeps their *OO-H energy
     comparable to their existing nspin = 1 *OOH rows. The uniformity
     requirement (P6/P19) is read as "the *OO-H search runs on all three
     metals", not "all three metals get a spin axis they do not have".
  2. The conformer axis is {yaw90, yaw270} (P10's registered operation, the
     set already measured on Ir/Ru); no other conformer generator is
     registered anywhere in this campaign.
  3. The single nspin=1 control sits at yaw90, the same conformer as the
     pending 1A off-plane row, so the ns2/ns1 comparison is at a matched
     conformer. (One control cannot measure a conformer GAP at nspin=1; the
     registered text says "one nspin=1 control" and gets exactly one.)
  4. Ionic-step allowances: conformer rows use the measured production step
     count x 1.0 (the yaw'd off-plane rows on record came in at 0.34-0.90x of
     their mirror row -- build_cellsym_pilot); *OO-H rows use x 1.5, ASSUMED,
     because moving H to a new bonding site is not the measured restart class.

Usage
-----
  PYTHONPATH=src python src/dft/build_lit3_ooh_anatomy.py
  PYTHONPATH=src python src/dft/build_lit3_ooh_anatomy.py --dry-run
  PYTHONPATH=src python src/dft/build_lit3_ooh_anatomy.py --gate1   # wave 2

NOTHING IS DEPLOYED BY THIS SCRIPT. The manifests carry NOT-DEPLOYED headers;
docs/43 A5.7 gates the launch on the 1A manifest being drained.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_decks import (parse_input_deck, parse_final_coordinates,  # noqa: E402
                         relax_final_energy_ev, write_probe, parse_variant)
from build_cellsym_pilot import (  # noqa: E402
    DOC43, yaw_fragment, cus_metal, load, final_magnetisation,
    est_hours_np4, est_bracket_np4, SCF_STEP_EQUIV,
    MAX_SECONDS_SAFETY, MAX_SECONDS_FLOOR, RANK_SPEEDUP_NP20,
    LONG_JOB_NP4_HOURS)
from lit_deckgen import (  # noqa: E402
    prereg_check, guard_deck, insert_max_seconds, write_deck, write_text,
    nk_for, species_index, bridging_O_index, out_status, ceil_steps,
    NP_LONG, NCONC_LONG)

# --------------------------------------------------------------------------
# PREREG -- pointers, not copies (build_cellsym_pilot round-2 finding N1).
# --------------------------------------------------------------------------
PREREG = {
    "oosh_initialization": (
        True, "A5.3(b)",
        "(superoxo O–O + H on bridging O) per metal, ± spin starts"),
    "uniform_across_metals": (
        ("Cr", "Ir", "Ru"), "A5.3(b)",
        "uniform across Cr, Ir, Ru** (P6/P19: never Cr alone)"),
    "inico_stabilization_ruo2_eV": (
        0.46, "A5.3(b)",
        "Inico's measured stabilizations, per oxide: 0.46 eV"),
    "cr_factorial": (
        True, "A5.3(c)",
        "**Cr conformer × spin factorial** including one nspin=1 control"),
    "superoxo_band_A": (
        (1.30, 1.32), "A5.3(a)", "vs superoxo *OO-H ~1.30–1.32 Å"),
    "never_cr_rescue": (
        True, "A5.3", "never a Cr-specific rescue (P6)"),
    "offplane_min_dy_A": (
        0.30, "s2-A.1", "y-translation of ≥ 0.30 Å"),
    "gate1_children_cr": (
        True, "A5.7", "Every new Cr relaxation gets its GATE-1 child"),
    "not_deployed_gate": (
        True, "A5.7",
        "manifest on a box is drained, or on a separately provisioned box"),
}

#: production sources; identical to build_cellsym_pilot.METALS including the
#: Cr *OOH basin redirect (docs/41 s6f).
METALS = {
    "Cr": dict(rundir="runs/Cr_slab", n_slab=18,
               basin_out={"s0_OOH": os.path.join("runs", "probe", "Cr_basin",
                                                 "s0_OOH.out")},
               kmesh_1x1=("9", "4", "1"), nkp_nosym=36, magnetic=True),
    "Ir": dict(rundir="runs/Ir_anchor", n_slab=18, basin_out={},
               kmesh_1x1=("8", "4", "1"), nkp_nosym=32, magnetic=False),
    "Ru": dict(rundir="runs/Ru_anchor", n_slab=18, basin_out={},
               kmesh_1x1=("8", "4", "1"), nkp_nosym=32, magnetic=False),
}

OO_SUPEROXO_A = 1.31          # midpoint of the registered band 1.30-1.32 A
H_BR_OFFSET_A = (0.0, 0.35, 0.92)   # |v| = 0.984 A ~ O-H; y-tilt breaks the
                                    # bridge row's own mirror physically
OOSH_STEP_MULT = 1.5          # ASSUMED (new H bonding site), bracket below
OOSH_STEP_MULT_BRACKET = (1.0, 2.0)
CONFORMER_STEP_MULT = 1.0     # MEASURED class: yaw'd rows 0.34-0.90x mirror
YAWS = (90.0, 270.0)          # P10's operation; the set measured on Ir/Ru
O_SEED_MINUS = -0.5           # magm O-channel seed (see module docstring)


def make_oosh(pos, n_slab, job):
    """Superoxo *OO + H-on-bridging-O start from a relaxed *OOH geometry."""
    slab, ads = pos[:n_slab], pos[n_slab:]
    if [q[0] for q in ads] != ["O", "O", "H"]:
        raise SystemExit(f"refusing to build {job}: adsorbate is "
                         f"{[q[0] for q in ads]}, expected [O, O, H]")
    ob, oo = ads[0], ads[1]
    frag = yaw_fragment([ob, oo], 90.0)
    v = (frag[1][1] - ob[1], frag[1][2] - ob[2], frag[1][3] - ob[3])
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if n < 1e-6:
        raise SystemExit(f"refusing to build {job}: degenerate O-O vector")
    oo2 = ("O", ob[1] + OO_SUPEROXO_A * v[0] / n,
           ob[2] + OO_SUPEROXO_A * v[1] / n,
           ob[3] + OO_SUPEROXO_A * v[2] / n)
    ib = bridging_O_index(slab, n_slab)
    obr = slab[ib]
    hn = ("H", obr[1] + H_BR_OFFSET_A[0], obr[2] + H_BR_OFFSET_A[1],
          obr[3] + H_BR_OFFSET_A[2])
    return list(slab) + [ob, oo2, hn], ib


def build(a):
    verified = prereg_check(PREREG, "LIT-3 (b)/(c)")
    outroot = a.out
    jobs, reuse_rows = [], []

    for M, cfg in METALS.items():
        rd, n_slab = cfg["rundir"], cfg["n_slab"]
        outdir = os.path.join(outroot, f"{M}_lit3")
        src = load(rd, "s0_OOH", cfg["basin_out"].get("s0_OOH"))
        src_slab = load(rd, "slab")
        pos = src["pos"]
        ads = pos[n_slab:]
        cus = cus_metal(src_slab["pos"], ads)
        y_mirror = cus[2]
        mask = src_slab["deck"]["flags"][:n_slab]

        def emit(name, positions, variant, steps, steps_basis, note,
                 nspin_override=None, mags_override=None):
            d = dict(parse_input_deck(os.path.join(rd, "s0_OOH.in")))
            d["flags"] = list(mask) + ["1 1 1"] * (len(positions) - n_slab)
            d["nosym"] = True
            d["kpts"] = ("automatic", list(cfg["kmesh_1x1"]) + ["0", "0", "0"])
            allowed = {"mixing_mode"}
            expected_mags = None
            if mags_override is not None:
                d["mags"] = dict(mags_override)
                expected_mags = dict(mags_override)
            if nspin_override is not None:
                d["nspin"] = nspin_override
                allowed |= {"nspin"}
                if nspin_override == 1:
                    d["mags"] = {}
                    expected_mags = {}
            text, _ = write_probe(d, positions, parse_variant("base"), name,
                                  a.pseudo_dir, a.scratch,
                                  calculation="relax")
            nkp = cfg["nkp_nosym"]
            magnetic = d["nspin"] == 2
            h4 = est_hours_np4(nkp, steps, magnetic, False)
            lo4, hi4 = est_bracket_np4(nkp, steps, magnetic, False)
            h_run = h4 / RANK_SPEEDUP_NP20
            ms = max(MAX_SECONDS_FLOOR,
                     int(round(MAX_SECONDS_SAFETY * h_run * 3600)))
            text = insert_max_seconds(text, ms)
            meta = guard_deck(text, os.path.join(rd, "s0_OOH.in"), name, dict(
                allowed=allowed, expected_mags=expected_mags, cell_mult=1.0,
                kmesh=cfg["kmesh_1x1"], nat=len(positions),
                flags=d["flags"],
                dy_checks=[(i, y_mirror)
                           for i in range(n_slab, len(positions))],
                require_offplane=True, max_seconds=ms))
            md5 = write_deck(outdir, name, text, a.dry_run)
            # manifest split, build_cellsym_pilot rule: Cr relaxations and any
            # job over LONG_JOB_NP4_HOURS at NP=4 run one-at-a-time at NP=20.
            long_job = h4 > LONG_JOB_NP4_HOURS
            manifest = "B" if (long_job or M == "Cr") else "A"
            np_run = NP_LONG if manifest == "B" else 4
            nk = nk_for(nkp, np_run)
            h_at = h_run if manifest == "B" else h4
            jobs.append(dict(
                metal=M, job=name, deck_source="s0_OOH", variant=variant,
                calculation="relax", sym="off",
                kmesh=" ".join(cfg["kmesh_1x1"]), n_kpt_est=nkp, nk=nk,
                manifest=manifest, np_run=np_run, steps_est=steps,
                steps_basis=steps_basis, est_hours_np4=round(h4, 1),
                est_hours_at_np=round(h_at, 1),
                est_hours_bracket_np4=[round(lo4, 1), round(hi4, 1)],
                max_seconds=ms, nspin=d["nspin"],
                geometry_source=src["geom_src"].replace("\\", "/"),
                note=note, md5=md5, **meta))
            print(f"  {M} {name}: nspin={d['nspin']}, ~{h_at:.1f} h at "
                  f"NP={np_run}")

        # ---- (b) the *OO-H spot check, all three metals ---------------------
        oosh_pos, ib = make_oosh(pos, n_slab, f"{M} oosh")
        oosh_steps = ceil_steps(src["steps_1x1"], OOSH_STEP_MULT)
        oosh_basis = dict(
            measured_1x1_steps=src["steps_1x1"],
            source=src["steps_src"].replace("\\", "/"),
            multiplier=OOSH_STEP_MULT, bracket=list(OOSH_STEP_MULT_BRACKET),
            basis="measured production s0_OOH ionic steps x OOSH_STEP_MULT "
                  "(ASSUMED: H moved to a new bonding site is not the "
                  "measured restart class)")
        oosh_note = (f"A5.3(b): superoxo O-O = {OO_SUPEROXO_A} A (registered "
                     f"band midpoint), H on the bridging O (slab atom {ib}) "
                     f"at 0.98 A with +{H_BR_OFFSET_A[1]} A y-tilt; O-O "
                     "fragment yawed 90 deg off the mirror")
        if cfg["magnetic"]:
            d0 = parse_input_deck(os.path.join(rd, "s0_OOH.in"))
            io = species_index(d0, "O")
            mags_m = dict(d0["mags"])
            mags_m[io] = O_SEED_MINUS
            emit("oosh__1x1_off_magp", oosh_pos, "oosh/magp", oosh_steps,
                 oosh_basis, oosh_note + "; PLUS spin start (production "
                 "starting_magnetization)")
            emit("oosh__1x1_off_magm", oosh_pos, "oosh/magm", oosh_steps,
                 oosh_basis, oosh_note + f"; MINUS spin start "
                 f"(starting_magnetization(O) = {O_SEED_MINUS}, O channel "
                 "seeded antiparallel to Cr -- see module docstring, "
                 "interpretive choice 1)", mags_override=mags_m)
        else:
            emit("oosh__1x1_off", oosh_pos, "oosh", oosh_steps, oosh_basis,
                 oosh_note + "; nspin=1 standing protocol -- a spin start "
                 "does not exist at nspin=1 (interpretive choice 1), and "
                 "nspin=1 keeps this row comparable to the existing *OOH")

        # ---- (c) the Cr conformer x spin factorial --------------------------
        if M == "Cr":
            d0 = parse_input_deck(os.path.join(rd, "s0_OOH.in"))
            io = species_index(d0, "O")
            mags_m = dict(d0["mags"])
            mags_m[io] = O_SEED_MINUS
            conf_steps = ceil_steps(src["steps_1x1"], CONFORMER_STEP_MULT)
            conf_basis = dict(
                measured_1x1_steps=src["steps_1x1"],
                source=src["steps_src"].replace("\\", "/"),
                multiplier=CONFORMER_STEP_MULT,
                basis="measured production s0_OOH ionic steps x 1.0; the "
                      "yaw'd off-plane rows on record came in at 0.34-0.90x "
                      "of their mirror row (build_cellsym_pilot), so 1.0x is "
                      "already the conservative side")
            for deg in YAWS:
                newpos = pos[:n_slab] + yaw_fragment(ads, deg)
                tag = f"yaw{int(deg)}"
                cells = [("magp", None, None,
                          "production starting_magnetization"),
                         ("magm", None, mags_m,
                          f"starting_magnetization(O) = {O_SEED_MINUS} "
                          "(interpretive choice 1)")]
                for sname, ns, mg, snote in cells:
                    name = f"s0_OOH__1x1_{tag}_{sname}"
                    if deg == 90.0 and sname == "magp":
                        # A5.2 reuse rule: this cell IS the pending block-1A
                        # row probe/Cr_cellsym/s0_OOH__1x1_off (same emitter,
                        # same start, same spin) -- reused, not re-run.
                        p = os.path.join(outroot, "Cr_cellsym",
                                         "s0_OOH__1x1_off.out")
                        reuse_rows.append(dict(
                            metal="Cr", cell="conformer yaw90 x magp",
                            job="probe/Cr_cellsym/s0_OOH__1x1_off",
                            status=out_status(p, "relax"),
                            gate1_required=True,
                            note="block-1A row, declared REUSE (A5.2 rule); "
                                 "its GATE-1 child is a 1A wave-2 "
                                 "obligation"))
                        continue
                    emit(name, newpos, f"conformer {tag}/{sname}", conf_steps,
                         conf_basis,
                         f"A5.3(c) factorial cell: conformer = P10 yaw "
                         f"{int(deg)} deg of the corrected-basin *OOH; spin "
                         f"start = {snote}", nspin_override=ns,
                         mags_override=mg)
            # the single registered nspin=1 control, at the yaw90 conformer
            newpos = pos[:n_slab] + yaw_fragment(ads, 90.0)
            emit("s0_OOH__1x1_yaw90_ns1", newpos, "conformer yaw90/ns1",
                 conf_steps, conf_basis,
                 "A5.3(c): the ONE registered nspin=1 control (Gauthier "
                 "diagnostic -- without spin polarization the conformer/"
                 "basin structure should collapse). Hubbard U stays on: only "
                 "the spin axis moves. Placed at yaw90, matched to the "
                 "pending 1A off row (interpretive choice 3)",
                 nspin_override=1)
            # the mirror (yaw0) conformer: on disk twice, reused not re-run
            reuse_rows.append(dict(
                metal="Cr", cell="conformer yaw0 (mirror) x production spin",
                job="runs/Cr_slab/s0_OOH",
                status=out_status(os.path.join("runs", "Cr_slab",
                                               "s0_OOH.out"), "relax"),
                gate1_required=False,
                note="production relaxation -- the METASTABLE magnetic "
                     "solution, 175 meV high (docs/41 s6f); enters the "
                     "factorial as the documented trap, never as an energy "
                     "of record"))
            reuse_rows.append(dict(
                metal="Cr", cell="conformer yaw0 (mirror) x production spin",
                job="runs/probe/Cr_basin/s0_OOH",
                status=out_status(os.path.join("runs", "probe", "Cr_basin",
                                               "s0_OOH.out"), "relax"),
                gate1_required=False,
                note="basin restart, the corrected (tier_v2) mirror value; "
                     "prevalidated (docs/41 s6f: step-1 energy reproduced "
                     "the audit SCF to 8.7e-4 meV)"))

    # ---- manifests ----------------------------------------------------------
    jobs.sort(key=lambda j: (j["manifest"], -j["est_hours_at_np"]))
    man = {"A": [j for j in jobs if j["manifest"] == "A"],
           "B": [j for j in jobs if j["manifest"] == "B"]}
    common_head = [
        "# NOT-DEPLOYED -- prepared decks only, nothing queued, nothing",
        "# launched. docs/43 A5.7: LIT decks queue only after the 1A manifest",
        "# on a box is drained, or on a separately provisioned box. Launch",
        "# authority: Frank -- and the +/- spin-start interpretation",
        "# (lit3_manifest.json `registered_ambiguities`) needs his sign-off.",
    ]
    manifests_meta = {}
    for key, np_run, nconc, fname in (
            ("A", 4, 5, "m_lit3_a_np4.txt"),
            ("B", NP_LONG, NCONC_LONG, "m_lit3_np20.txt")):
        rows = man[key]
        if not rows:
            continue
        lines = common_head + [
            f"# LIT-3 (b)/(c) manifest {key} (docs/43 A5.3 = D4)",
            f"# NP={np_run} NCONC={nconc}",
            f"#   bash queue_r1.sh {fname} {np_run} {nconc}",
            "# NP is an exact multiple of every nk below. Longest first.",
        ] + [f"probe/{j['metal']}_lit3 {j['job']} .in {j['nk']}"
             for j in rows]
        write_text(os.path.join(outroot, fname), "\n".join(lines) + "\n",
                   a.dry_run)
        manifests_meta[key] = dict(
            file=fname, np=np_run, nconc=nconc, n_jobs=len(rows),
            command=f"bash queue_r1.sh {fname} {np_run} {nconc}",
            sum_hours=round(sum(j["est_hours_at_np"] for j in rows), 1),
            longest_job_hours=max(j["est_hours_at_np"] for j in rows))

    manifest = dict(
        block="LIT-3 (b)+(c) -- *OO-H spot check and Cr conformer x spin "
              "factorial (docs/43 A5.3 = D4)",
        status="NOT_DEPLOYED",
        prereg=dict(document=DOC43, section="AMENDMENT 5, A5.3 (+ A5.7)",
                    rule="docs/43 is the only pre-registration. Where this "
                         "manifest and docs/43 disagree, docs/43 wins.",
                    anchors_verified=verified),
        registered_constraint="outputs are mechanism-caveat columns or "
                              "uniformly-applied tier_v3 inputs -- never a "
                              "Cr-specific rescue (P6); the docs/43 s2 "
                              "registered Cr prediction is untouched",
        inico_reference_stabilizations_eV=dict(
            TiO2_vacuum=0.46, RuO2_vacuum=0.19,
            IrO2_one_water_bilayer="0.13-0.15",
            note="per-oxide, NEVER a blanket band (sweep verifier fix, memo "
                 "s9 LIT-3 row)"),
        registered_ambiguities=[
            "'+/- spin starts' is under-determined: a global sign flip is "
            "exactly degenerate (collinear time reversal). Implemented as "
            "the O-channel seed sign (magp = production; magm = "
            "starting_magnetization(O) = -0.5, antiparallel to Cr). Ru/Ir "
            "run nspin=1 in production, where a spin start does not exist: "
            "one deck each. NEEDS FRANK'S SIGN-OFF BEFORE LAUNCH.",
            "conformer axis = {yaw90, yaw270} (P10's registered operation); "
            "the mirror conformer enters by reuse (production metastable + "
            "basin corrected), and yaw90 x magp is the pending 1A row "
            "probe/Cr_cellsym/s0_OOH__1x1_off, reused not re-run.",
            "the single nspin=1 control is placed at yaw90, matched to the "
            "1A off row's conformer.",
            "step allowances: conformers x1.0 (measured class), *OO-H x1.5 "
            "(ASSUMED, bracket 1.0-2.0)."],
        reused_rows=reuse_rows,
        manifests=manifests_meta,
        jobs=jobs)
    write_text(os.path.join(outroot, "lit3_manifest.json"),
               json.dumps(manifest, indent=2) + "\n", a.dry_run)
    n_cr = sum(1 for j in jobs if j["metal"] == "Cr")
    print(f"{len(jobs)} new LIT-3 decks ({n_cr} Cr -- each owed a GATE-1 "
          f"child via --gate1 -- {len(jobs) - n_cr} Ir/Ru) + "
          f"{len(reuse_rows)} declared reuse rows -> {outroot} [NOT DEPLOYED]"
          + ("  (dry run)" if a.dry_run else ""))
    return 0


def cmd_gate1(a):
    """Wave 2 (docs/43 A5.7): one fresh-density fixed-geometry SCF per
    converged Cr LIT-3 relaxation, at its own final coordinates, spin
    treatment, k-mesh and cell. Refuses if any parent is not scoreable."""
    man_path = os.path.join(a.out, "lit3_manifest.json")
    if not os.path.exists(man_path):
        raise SystemExit(f"refusing: {man_path} not found; build LIT-3 first")
    man = json.load(open(man_path, encoding="utf-8"))
    targets = [j for j in man["jobs"]
               if j["metal"] == "Cr" and j["calculation"] == "relax"]
    if not targets:
        raise SystemExit("refusing: no Cr relaxations in the LIT-3 manifest")

    cfg = METALS["Cr"]
    rd = cfg["rundir"]
    outdir = os.path.join(a.out, "Cr_lit3")
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
        # the child mirrors the PARENT'S emitted deck (N3): spin treatment,
        # starting magnetization, mesh and flags are re-read from its bytes.
        pd = parse_input_deck(os.path.join(outdir, j["job"] + ".in"))
        if not re.search(r"^\s*nosym\s*=\s*\.true\.", pd["raw"], re.M | re.I):
            raise SystemExit(f"refusing {name}: parent deck lacks nosym (N3)")
        d = dict(parse_input_deck(os.path.join(rd, "s0_OOH.in")))
        d["flags"] = pd["flags"]
        d["nosym"] = True
        d["kpts"] = pd["kpts"]
        d["nspin"] = pd["nspin"]
        d["mags"] = dict(pd["mags"])
        allowed = {"mixing_mode", "calculation"}
        if pd["nspin"] != d0_nspin(rd):
            allowed |= {"nspin"}
        text, _ = write_probe(d, pos, parse_variant("base"), name,
                              a.pseudo_dir, a.scratch, calculation="scf")
        magnetic = pd["nspin"] == 2
        h4 = est_hours_np4(j["n_kpt_est"], SCF_STEP_EQUIV, magnetic, False)
        h_run = h4 / RANK_SPEEDUP_NP20
        ms = max(MAX_SECONDS_FLOOR,
                 int(round(MAX_SECONDS_SAFETY * h_run * 3600)))
        text = insert_max_seconds(text, ms)
        guard_deck(text, os.path.join(rd, "s0_OOH.in"), name, dict(
            allowed=allowed, expected_mags=dict(pd["mags"]), cell_mult=1.0,
            kmesh=tuple(pd["kpts"][1][:3]), nat=j["nat"], flags=pd["flags"],
            dy_checks=[], require_offplane=False, max_seconds=ms))
        md5 = write_deck(outdir, name, text, a.dry_run)
        tot, ab = final_magnetisation(op)
        rows.append(dict(job=name, parent=j["job"], variant=j["variant"],
                         nk=j["nk"], max_seconds=ms,
                         est_hours_at_np20=round(h_run, 1),
                         parent_final_energy_ev=relax_final_energy_ev(op),
                         parent_total_magnetization=tot,
                         parent_absolute_magnetization=ab, md5=md5))
        lines.append(f"probe/Cr_lit3 {name} .in {j['nk']}")

    if not_ready:
        raise SystemExit("refusing to emit any LIT-3 GATE-1 deck; "
                         f"{len(not_ready)} of {len(targets)} Cr relaxations "
                         "are not scoreable yet:\n  " + "\n  ".join(not_ready))

    head = ["# NOT-DEPLOYED -- LIT-3 GATE-1 children (docs/43 A5.7 /",
            "# s2-A.3(b), tolerance 5 meV). One fresh-density fixed-geometry",
            "# SCF per converged Cr LIT-3 relaxation, at the parent's own",
            "# spin treatment.",
            f"# NP={NP_LONG} NCONC={NCONC_LONG}",
            f"#   bash queue_r1.sh m_lit3_gate1.txt {NP_LONG} {NCONC_LONG}"]
    write_text(os.path.join(a.out, "m_lit3_gate1.txt"),
               "\n".join(head + lines) + "\n", a.dry_run)
    write_text(os.path.join(a.out, "lit3_gate1_manifest.json"),
               json.dumps(dict(prereg=f"{DOC43} A5.7 / s2-A.3(b)",
                               status="NOT_DEPLOYED", jobs=rows), indent=2)
               + "\n", a.dry_run)
    print(f"{len(rows)} LIT-3 GATE-1 SCFs -> {outdir} [NOT DEPLOYED]")
    return 0


def d0_nspin(rd):
    return parse_input_deck(os.path.join(rd, "s0_OOH.in"))["nspin"]


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
                         "LIT-3 relaxations")
    a = ap.parse_args()
    return cmd_gate1(a) if a.gate1 else build(a)


if __name__ == "__main__":
    sys.exit(main())
