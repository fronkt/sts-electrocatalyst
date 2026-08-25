#!/usr/bin/env python3
"""s3_readout.py — deterministic S3 readout parser (state of record 2026-08-24).

Disclosed AI-drafted infrastructure. Parses every final .out under runs/s3/*/
plus every external energy-of-record file named in docs/54 (the row->file
authority), applies the state-of-record status rules VERBATIM (docs/52 C9,
docs/55 R1/R2/R3, docs/54 substitutions), and emits
runs/s3/readout/s3_readout_2026-08-24.json.

Rules applied (each cited in the emitted rows/cells):
  - docs/52 C9: GATE-1 AGREE rows quote the CHILD as energy of record.
  - docs/43:1589-1592: a __g1 child > 1 meV above its parent is refused
    (used only to CLASSIFY; refusals not covered by docs/55 are FLAGGED,
    never resolved).
  - docs/55 R1: Fe s0_OOH__1x1_off and Mn s0_OOH__2x1v_off are
    PENDING-RERELAX — quote parent AND child, bank neither as final.
  - docs/55 R2: 11 rung-(iii) rows are PENDING-RETRY (array 20123293);
    their NOT_CONVERGED records are now *.out.attemptN.
  - docs/55 R3: Cr *OOH 2x1v mir energy of record = the escape minimum
    -3188.71606 Ry (runs/s3/Cr/s0_OOH__2x1v_escape.out); the mirror value
    -3188.70497 is a SADDLE diagnostic, not a state.
  - docs/54:140-265, :400-405: external energy-of-record rows and the
    basin-substitution banking rule.
  - docs/54:206, :226: Co/Ni *OOH 1x1 mir are by-record GAP rows.

No existing file is modified. Takes no arguments; stdlib only; output is
byte-identical on re-run.
"""

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
S3_DIR = REPO / "runs" / "s3"
OUT_DIR = S3_DIR / "readout"
OUT_JSON = OUT_DIR / "s3_readout_2026-08-24.json"

RY_TO_MEV = 13605.693

S3_METALS = ["Co", "Cr", "Fe", "Mn", "Ni", "Ti"]

# Skip patterns for files under runs/s3/*/ (task spec).
SKIP_RE = re.compile(
    r"(\.attempt\d+$)|(\.replay\.out$)|(\.fromparent\.out$)|(__hess_)"
)

# ---------------------------------------------------------------------------
# docs/55 R1 — PENDING-RERELAX (quote parent AND child, bank neither)
R1_ROWS = {
    ("Fe", "s0_OOH__1x1_off"),
    ("Mn", "s0_OOH__2x1v_off"),
}
R1_CITE = ("docs/55 R1: children found deeper electronic states "
           "(-384.30/-20.62 meV); __basin re-relaxations in flight "
           "(array 20123293) — quote parent AND child, bank neither as final")

# docs/55 R2 — PENDING-RETRY (canonical .out renamed to *.out.attemptN)
R2_ROWS = {
    ("Co", "ref__2x1v"),
    ("Co", "s0_OH__1x1_off"),
    ("Co", "s0_O__2x1v_mir"),
    ("Co", "s0_OH__2x1v_mir"),
    ("Co", "s0_OOH__2x1v_mir"),
    ("Co", "s0_OH__2x1v_off"),
    ("Co", "s0_OOH__2x1v_off"),
    ("Ni", "s0_OOH__2x1v_mir"),
    ("Ni", "s0_OOH__2x1v_off"),
    ("Co", "s0_O__1x1_off__g1"),
    ("Ni", "s0_OH__2x1v_off__g1"),
}
R2_CITE = ("docs/55 R2: PENDING-RETRY in array 20123293; rung-(iii) "
           "NOT_CONVERGED records are now *.out.attemptN")

# GATE-1 census UNVERIFIED parents (children are in the R2 set)
UNVERIFIED_PARENTS = {
    ("Co", "s0_O__1x1_off"),
    ("Ni", "s0_OH__2x1v_off"),
}
UNVERIFIED_CITE = ("GATE-1 census 2026-08-24: parent UNVERIFIED — its __g1 "
                   "child is PENDING-RETRY per docs/55 R2")

R3_CITE = ("docs/55 R3: Cr *OOH 2x1v mir energy of record = the escape "
           "minimum -3188.71606 Ry (runs/s3/Cr/s0_OOH__2x1v_escape.out); "
           "the mirror value -3188.70497 is a SADDLE diagnostic, not a state")

C9_CITE = ("docs/52 C9: GATE-1 AGREE rows quote the CHILD as the energy "
           "of record")

REFUSE_CITE = ("docs/43:1589-1592: a __g1 child > 1 meV above its parent is "
               "refused and re-run from the parent's converged density; "
               "second failure records the pair MULTISTABLE")

# By-record GAP cells (docs/54:206, :226)
GAP_CELLS = [
    {"metal": "Co", "state": "OOH", "coverage": "1x1", "arm": "mir",
     "rule": ("docs/54:206: absent by record — failed 4x in earlier waves, "
              "dropped (docs/43:1864, :1596); GAP row, never interpolated")},
    {"metal": "Ni", "state": "OOH", "coverage": "1x1", "arm": "mir",
     "rule": ("docs/54:226: absent by record — failed 5x, dropped "
              "(docs/43:1864, :1596); GAP row, never interpolated")},
]

# basin_g1 children inside runs/s3 whose parents are EXTERNAL basin rows
BASIN_G1_PARENTS = {
    ("Cr", "s0_OOH__basin_g1"): "runs/probe/Cr_basin/s0_OOH.out",
    ("Co", "s0_OH__basin_g1"): "runs/probe/Co_basin/s0_OH.out",
    ("Ni", "s0_OH__basin_g1"): "runs/probe/Ni_basin/s0_OH.out",
}
BASIN_G1_CELL = {
    ("Cr", "s0_OOH__basin_g1"): ("Cr", "OOH", "1x1", "mir"),
    ("Co", "s0_OH__basin_g1"): ("Co", "OH", "1x1", "mir"),
    ("Ni", "s0_OH__basin_g1"): ("Ni", "OH", "1x1", "mir"),
}

# ---------------------------------------------------------------------------
# External energy-of-record rows (docs/54, the row->file authority).
# Fields: path, metal, state, coverage, arm, status, rule, expected_E (docs/54
# printed value), parallel (production file quoted alongside, or None),
# flags (registered OPEN questions carried verbatim), cell_member.
E = lambda *a: a  # noqa: E731  (compact row constructor)
EXTERNAL_ROWS = [
    # --- Cr (15) ---
    dict(path="runs/Cr_slab/slab.out", metal="Cr", state="ref",
         coverage="1x1", arm="-", status="BANKED",
         rule="docs/54:140 (BANKED tier_v2 production reuse)",
         expected_E=-1552.21158979, parallel=None, flags=[]),
    dict(path="runs/probe/Cr_cellsym/ref__2x1v.out", metal="Cr", state="ref",
         coverage="2x1v", arm="-", status="BANKED",
         rule="docs/54:141 (BANKED probe reuse, g1 AGREE)",
         expected_E=-3104.42285307, parallel=None, flags=[]),
    dict(path="runs/probe/Cr_cellsym/s0_O__1x1_mir.out", metal="Cr",
         state="O", coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:142 (corner N; production LOCKED value quoted in "
              "parallel, 0.19 meV apart)",
         expected_E=-1593.69696999, parallel="runs/Cr_slab/s0_O.out",
         flags=[]),
    dict(path="runs/probe/Cr_cellsym/s0_O__1x1_off.out", metal="Cr",
         state="O", coverage="1x1", arm="off", status="BANKED",
         rule="docs/54:143 (corner S)", expected_E=-1593.69698646,
         parallel=None, flags=[]),
    dict(path="runs/probe/Cr_cellsym/s0_O__2x1v_mir.out", metal="Cr",
         state="O", coverage="2x1v", arm="mir", status="BANKED",
         rule="docs/54:144 (corner C)", expected_E=-3145.93480354,
         parallel=None, flags=[]),
    dict(path="runs/probe/Cr_cellsym/s0_O__2x1v_off.out", metal="Cr",
         state="O", coverage="2x1v", arm="off", status="BANKED",
         rule="docs/54:145 (corner B; D_cell -0.3616 EXCEEDS)",
         expected_E=-3145.93480189, parallel=None, flags=[]),
    dict(path="runs/probe/Cr_cellsym/s0_OH__1x1_mir.out", metal="Cr",
         state="OH", coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:146 (corner N; production LOCKED value quoted in "
              "parallel)",
         expected_E=-1595.00031719, parallel="runs/Cr_slab/s0_OH.out",
         flags=[]),
    dict(path="runs/probe/Cr_cellsym/s0_OH__1x1_off.out", metal="Cr",
         state="OH", coverage="1x1", arm="off", status="BANKED",
         rule="docs/54:147 (corner S; 1x1 pair CONFOUNDED per "
              "docs/43:1566-1571)",
         expected_E=-1594.98847069, parallel=None,
         flags=["1x1 symmetry pair CONFOUNDED (docs/54:147)"]),
    dict(path="runs/probe/Cr_cellsym/s0_OH__2x1v_mir.out", metal="Cr",
         state="OH", coverage="2x1v", arm="mir", status="BANKED",
         rule="docs/54:148 (corner C; path inferred under ditto, verified "
              "on disk 2026-08-24)",
         expected_E=-3147.21581906, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Cr_cellsym/s0_OH__2x1v_off.out", metal="Cr",
         state="OH", coverage="2x1v", arm="off", status="BANKED",
         rule="docs/54:149 (corner B; D_cell -0.2195 EXCEEDS; path inferred, "
              "verified on disk)",
         expected_E=-3147.21597446, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Cr_basin/s0_OOH.out", metal="Cr",
         state="OOH", coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:150, :400-405 (BASIN SUBSTITUTION banked as "
              "production-seed energy-of-record; production file metastable "
              "+178.58 meV, quoted in parallel)",
         expected_E=-1636.48392834, parallel="runs/Cr_slab/s0_OOH.out",
         flags=["member identity OPEN — which file is the 1x1-mir "
                "production-seed MEMBER is unresolved (docs/54:400-405); "
                "pair CONFOUNDED either way — entrant's call, NOT resolved "
                "here"]),
    dict(path="runs/probe/Cr_cellsym/s0_OOH__1x1_off.out", metal="Cr",
         state="OOH", coverage="1x1", arm="off", status="BANKED",
         rule="docs/54:151 (corner S)", expected_E=-1636.56973955,
         parallel=None, flags=[]),
    dict(path="runs/probe/Cr_cellsym/s0_OOH__2x1v_mir.out", metal="Cr",
         state="OOH", coverage="2x1v", arm="mir", status="DIAGNOSTIC",
         rule=R3_CITE + " — this mirror output is the SADDLE diagnostic; "
              "docs/54:152 entry superseded by docs/55 R3",
         expected_E=-3188.70497020, parallel=None,
         flags=["pair CONFOUNDED (Delta_sym 1.188 eV, docs/54:152)",
                "path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Cr_cellsym/s0_OOH__2x1v_off.out", metal="Cr",
         state="OOH", coverage="2x1v", arm="off", status="BANKED",
         rule="docs/54:153 (corner B; D_cell -0.1559 EXCEEDS; path inferred, "
              "verified on disk)",
         expected_E=-3188.79231810, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Cr_lit3/s0_OOH__1x1_yaw90_magm.out", metal="Cr",
         state="OOH", coverage="1x1", arm="off", status="BANKED",
         rule="docs/54:154 (second-seed basin level, BANKED; NOT the "
              "production-seed corner member)",
         expected_E=-1636.56961270, parallel=None,
         flags=["g1 BASIN_DRIFT +47.77 meV, A8.3 refused-child re-run owed "
                "(docs/54:154)", "second seed — excluded from cells"],
         cell_member=False),
    # --- Mn (4) ---
    dict(path="runs/Mn_slab/slab.out", metal="Mn", state="ref",
         coverage="1x1", arm="-", status="BANKED",
         rule="docs/54:168 (BANKED tier_v2 reuse)",
         expected_E=-1766.35807805, parallel=None, flags=[]),
    dict(path="runs/Mn_slab/s0_O.out", metal="Mn", state="O",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:170, :318 (tier_v2 reuse; __base audit banked in "
              "runs/probe/Mn_audit/; __g1 owed)",
         expected_E=-1807.77357526, parallel=None,
         flags=["nosym ON_PLANE — whether this row stands as a mirror "
                "member is OPEN (docs/54:406-411, section 6 item 5)"]),
    dict(path="runs/Mn_slab/s0_OH.out", metal="Mn", state="OH",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:170, :318 (tier_v2 reuse; __g1 owed)",
         expected_E=-1809.11818344, parallel=None,
         flags=["nosym EXPLORED — mirror-member standing OPEN "
                "(docs/54:406-411, section 6 item 5)"]),
    dict(path="runs/Mn_slab/s0_OOH.out", metal="Mn", state="OOH",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:170, :318 (tier_v2 reuse; __g1 owed). NOTE docs/55 "
              "R1 attaches to Mn s0_OOH__2x1v_off, not this row",
         expected_E=-1850.60679209, parallel=None,
         flags=["nosym EXPLORED — mirror-member standing OPEN "
                "(docs/54:406-411, section 6 item 5)"]),
    # --- Fe (4) ---
    dict(path="runs/Fe_slab/slab.out", metal="Fe", state="ref",
         coverage="1x1", arm="-", status="BANKED",
         rule="docs/54:187 (BANKED tier_v2 reuse)",
         expected_E=-2473.80303205, parallel=None, flags=[]),
    dict(path="runs/Fe_slab/s0_O.out", metal="Fe", state="O",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:189, :318 (tier_v2 reuse; __base audit banked in "
              "runs/probe/Fe_audit/; __g1 owed; path implied, verified on "
              "disk)",
         expected_E=-2515.17456142, parallel=None,
         flags=["nosym ON_PLANE — mirror-member standing OPEN "
                "(docs/54:406-411, section 6 item 5)"]),
    dict(path="runs/Fe_slab/s0_OH.out", metal="Fe", state="OH",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:189, :318 (tier_v2 reuse; __g1 owed; path implied)",
         expected_E=-2516.54646887, parallel=None,
         flags=["nosym EXPLORED — mirror-member standing OPEN "
                "(docs/54:406-411, section 6 item 5)"]),
    dict(path="runs/Fe_slab/s0_OOH.out", metal="Fe", state="OOH",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:189, :318 (tier_v2 reuse; __g1 owed; path implied). "
              "NOTE docs/55 R1 attaches to Fe s0_OOH__1x1_off, not this row",
         expected_E=-2558.05888124, parallel=None,
         flags=["nosym ON_PLANE — mirror-member standing OPEN "
                "(docs/54:406-411, section 6 item 5)"]),
    # --- Co (3) ---
    dict(path="runs/Co_slab/slab.out", metal="Co", state="ref",
         coverage="1x1", arm="-", status="BANKED",
         rule="docs/54:202 (BANKED tier_v2 reuse; clean slab already "
              "drifted +59 meV on fresh-density audit; identical g1 depth "
              "owed)",
         expected_E=-2289.20445721, parallel=None,
         flags=["fresh-density drift +59 meV flagged (docs/54:202)"]),
    dict(path="runs/Co_slab/s0_O.out", metal="Co", state="O",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:204, :318 (tier_v2 reuse; __g1 owed; path implied)",
         expected_E=-2330.66753771, parallel=None,
         flags=["nosym EXPLORED — mirror-member standing OPEN "
                "(docs/54:406-411, section 6 item 5)"]),
    dict(path="runs/probe/Co_basin/s0_OH.out", metal="Co", state="OH",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:205, :318, :400-405 (BASIN SUBSTITUTION banked as "
              "production-seed energy-of-record, -406.51 meV below prod; "
              "production quoted in parallel; __g1 owed on the basin row)",
         expected_E=-2332.00425138, parallel="runs/Co_slab/s0_OH.out",
         flags=[]),
    # --- Ni (3) ---
    dict(path="runs/Ni_slab/slab.out", metal="Ni", state="ref",
         coverage="1x1", arm="-", status="BANKED",
         rule="docs/54:222 (BANKED tier_v2 reuse)",
         expected_E=-2557.25622867, parallel=None, flags=[]),
    dict(path="runs/Ni_slab/s0_O.out", metal="Ni", state="O",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:224, :318 (tier_v2 reuse; __base audit banked in "
              "runs/probe/Ni_audit/; __g1 owed; path implied)",
         expected_E=-2598.63298268, parallel=None,
         flags=["nosym ON_PLANE — mirror-member standing OPEN "
                "(docs/54:406-411, section 6 item 5)"]),
    dict(path="runs/probe/Ni_basin/s0_OH.out", metal="Ni", state="OH",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:225, :318, :400-405 (BASIN SUBSTITUTION banked as "
              "production-seed energy-of-record, -175.85 meV below prod; "
              "production quoted in parallel; __g1 owed on the basin row)",
         expected_E=-2599.99940826, parallel="runs/Ni_slab/s0_OH.out",
         flags=[]),
    # --- Ru (14) ---
    dict(path="runs/Ru_anchor/slab.out", metal="Ru", state="ref",
         coverage="1x1", arm="-", status="BANKED",
         rule="docs/54:238 (BANKED; nspin=1, no M)",
         expected_E=-1630.66772646, parallel=None, flags=[]),
    dict(path="runs/probe/Ru_cellsym/ref__2x1v.out", metal="Ru", state="ref",
         coverage="2x1v", arm="-", status="BANKED",
         rule="docs/54:239 (BANKED)", expected_E=-3261.33545254,
         parallel=None, flags=[]),
    dict(path="runs/Ru_anchor/s0_O.out", metal="Ru", state="O",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:240 (corner N, LOCKED)", expected_E=-1672.25496768,
         parallel=None, flags=[]),
    dict(path="runs/probe/Ru_cellsym/s0_O__1x1_off.out", metal="Ru",
         state="O", coverage="1x1", arm="off", status="BANKED",
         rule="docs/54:241 (corner S)", expected_E=-1672.25490048,
         parallel=None, flags=[]),
    dict(path="runs/probe/Ru_cellsym/s0_O__2x1v_mir.out", metal="Ru",
         state="O", coverage="2x1v", arm="mir", status="BANKED",
         rule="docs/54:242 (corner C; path inferred under ditto, verified "
              "on disk)",
         expected_E=-3302.93178672, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ru_cellsym/s0_O__2x1v_off.out", metal="Ru",
         state="O", coverage="2x1v", arm="off", status="BANKED",
         rule="docs/54:243 (corner B; D_cell -0.1247 EXCEEDS; path "
              "inferred, verified on disk)",
         expected_E=-3302.93178971, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/Ru_anchor/s0_OH.out", metal="Ru", state="OH",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:244 (corner N, LOCKED; path inferred from anchor "
              "context, verified on disk)",
         expected_E=-1673.52913839, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ru_cellsym/s0_OH__1x1_off.out", metal="Ru",
         state="OH", coverage="1x1", arm="off", status="BANKED",
         rule="docs/54:245 (corner S; 1x1 pair SIGN_VIOLATION +0.2475 eV "
              "at 1x1 vs +0.0130 at 2x1v; path inferred, verified on disk)",
         expected_E=-1673.51094446, parallel=None,
         flags=["1x1 pair SIGN_VIOLATION (docs/54:245)",
                "path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ru_cellsym/s0_OH__2x1v_mir.out", metal="Ru",
         state="OH", coverage="2x1v", arm="mir", status="BANKED",
         rule="docs/54:246 (corner C; path inferred, verified on disk)",
         expected_E=-3304.19810638, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ru_cellsym/s0_OH__2x1v_off.out", metal="Ru",
         state="OH", coverage="2x1v", arm="off", status="BANKED",
         rule="docs/54:247 (corner B; D_cell -0.2515 EXCEEDS; path "
              "inferred, verified on disk)",
         expected_E=-3304.19715356, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/Ru_anchor/s0_OOH.out", metal="Ru", state="OOH",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:248 (corner N, LOCKED)", expected_E=-1715.00704045,
         parallel=None, flags=[]),
    dict(path="runs/probe/Ru_orient/s0_OOH__yaw90.out", metal="Ru",
         state="OOH", coverage="1x1", arm="off", status="BANKED",
         rule="docs/54:249 (corner S, the SCORED member; yaw270 NOT "
              "banked)",
         expected_E=-1715.01304629, parallel=None,
         flags=["oosh conformer -1715.02124065 is LOWEST banked; whether "
                "oosh becomes the member is OPEN (docs/54:422-424, section "
                "6 item 10) — entrant's call, NOT resolved here"]),
    dict(path="runs/probe/Ru_cellsym/s0_OOH__2x1v_mir.out", metal="Ru",
         state="OOH", coverage="2x1v", arm="mir", status="BANKED",
         rule="docs/54:250 (corner C; path inferred, verified on disk)",
         expected_E=-3345.67264760, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ru_cellsym/s0_OOH__2x1v_off.out", metal="Ru",
         state="OOH", coverage="2x1v", arm="off", status="BANKED",
         rule="docs/54:251 (corner B; D_cell +0.0018 WITHIN; path inferred, "
              "verified on disk)",
         expected_E=-3345.68064313, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    # --- Ir (14) ---
    dict(path="runs/Ir_anchor/slab.out", metal="Ir", state="ref",
         coverage="1x1", arm="-", status="BANKED",
         rule="docs/54:258 (BANKED)", expected_E=-1589.74822625,
         parallel=None, flags=[]),
    dict(path="runs/probe/Ir_cellsym/ref__2x1v.out", metal="Ir", state="ref",
         coverage="2x1v", arm="-", status="BANKED",
         rule="docs/54:259 (BANKED)", expected_E=-3179.49645246,
         parallel=None, flags=[]),
    dict(path="runs/Ir_anchor/s0_O.out", metal="Ir", state="O",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:260 (corner N, LOCKED; combined mir/off row prints "
              "energies only; path inferred, verified on disk)",
         expected_E=-1631.33923851, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ir_cellsym/s0_O__1x1_off.out", metal="Ir",
         state="O", coverage="1x1", arm="off", status="BANKED",
         rule="docs/54:260 (corner S; path inferred, verified on disk)",
         expected_E=-1631.33917053, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ir_cellsym/s0_O__2x1v_mir.out", metal="Ir",
         state="O", coverage="2x1v", arm="mir", status="BANKED",
         rule="docs/54:261 (corner C; path inferred, verified on disk)",
         expected_E=-3221.09584906, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ir_cellsym/s0_O__2x1v_off.out", metal="Ir",
         state="O", coverage="2x1v", arm="off", status="BANKED",
         rule="docs/54:261 (corner B; D_cell -0.1149 EXCEEDS; path "
              "inferred, verified on disk)",
         expected_E=-3221.09583897, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/Ir_anchor/s0_OH.out", metal="Ir", state="OH",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:262 (corner N; path inferred, verified on disk)",
         expected_E=-1632.64856529, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ir_cellsym/s0_OH__1x1_off.out", metal="Ir",
         state="OH", coverage="1x1", arm="off", status="BANKED",
         rule="docs/54:262 (corner S; path inferred, verified on disk)",
         expected_E=-1632.64814256, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ir_cellsym/s0_OH__2x1v_mir.out", metal="Ir",
         state="OH", coverage="2x1v", arm="mir", status="BANKED",
         rule="docs/54:263 (corner C; path inferred, verified on disk)",
         expected_E=-3222.38878145, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ir_cellsym/s0_OH__2x1v_off.out", metal="Ir",
         state="OH", coverage="2x1v", arm="off", status="BANKED",
         rule="docs/54:263 (corner B; D_cell +0.0661 WITHIN; path "
              "inferred, verified on disk)",
         expected_E=-3222.39151403, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/Ir_anchor/s0_OOH.out", metal="Ir", state="OOH",
         coverage="1x1", arm="mir", status="BANKED",
         rule="docs/54:264 (corner N; N2 fresh replication context, "
              "verifier-corrected citation docs/43:808; path inferred, "
              "verified on disk)",
         expected_E=-1674.09176132, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ir_cellsym/s0_OOH__1x1_off.out", metal="Ir",
         state="OOH", coverage="1x1", arm="off", status="BANKED",
         rule="docs/54:264 (corner S; N2 fresh replication)",
         expected_E=-1674.11268108, parallel=None,
         flags=["Ir_orient yaw90 -1674.11317317 and oosh -1674.11459651 "
                "also banked — oosh-member question OPEN (docs/54:422-424, "
                "section 6 item 10) — entrant's call, NOT resolved here"]),
    dict(path="runs/probe/Ir_cellsym/s0_OOH__2x1v_mir.out", metal="Ir",
         state="OOH", coverage="2x1v", arm="mir", status="BANKED",
         rule="docs/54:265 (corner C; path inferred, verified on disk)",
         expected_E=-3263.87194671, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
    dict(path="runs/probe/Ir_cellsym/s0_OOH__2x1v_off.out", metal="Ir",
         state="OOH", coverage="2x1v", arm="off", status="BANKED",
         rule="docs/54:265 (corner B; interaction INCONCLUSIVE 0.266 eV, "
              "the one non-additive candidate S3 re-tests, docs/43:1520-"
              "1521; path inferred, verified on disk)",
         expected_E=-3263.87330531, parallel=None,
         flags=["path inferred from docs/54 row grammar"]),
]

# ---------------------------------------------------------------------------
ENERGY_RE = re.compile(r"^!\s+total energy\s+=\s+(-?\d+\.\d+)\s+Ry")
MAG_RE = re.compile(r"^\s+total magnetization\s+=\s+(-?\d+\.\d+)\s+Bohr")
KPT_RE = re.compile(r"number of k points\s*=\s*(\d+)")
CALC_RE = re.compile(r"calculation\s*=\s*['\"](\w+)['\"]")


def parse_out(path):
    """Parse one pw.x output file. Returns a dict of raw parse fields."""
    energy = None
    mag = None
    kpts = None
    job_done = False
    not_achieved = False
    try:
        text = path.read_text(errors="replace")
    except OSError as exc:
        return {"parse_error": str(exc)}
    for line in text.splitlines():
        m = ENERGY_RE.match(line)
        if m:
            energy = float(m.group(1))
            continue
        m = MAG_RE.match(line)
        if m:
            mag = float(m.group(1))
            continue
        if kpts is None:
            m = KPT_RE.search(line)
            if m:
                kpts = int(m.group(1))
                continue
        if "JOB DONE" in line:
            job_done = True
        if "convergence NOT achieved" in line:
            not_achieved = True
    # calculation type: prefer the sibling .in deck; fall back to inference
    calc = None
    in_path = path.with_suffix(".in")
    if in_path.exists():
        m = CALC_RE.search(in_path.read_text(errors="replace"))
        if m:
            calc = m.group(1)
    if calc is None:
        calc = "relax" if "Geometry Optimization" in text else "scf"
    return {
        "energy_ry": energy,
        "total_magnetization_bohr": mag,
        "n_kpoints": kpts,
        "converged": bool(job_done and not not_achieved),
        "calculation": calc,
    }


def job_fields(job):
    """metal-dir job name -> (state, coverage, arm, is_g1, parent_job)."""
    is_g1 = False
    parent = None
    base = job
    if base.endswith("__g1"):
        is_g1 = True
        base = base[: -len("__g1")]
        parent = base
    if base.endswith("__basin_g1") or base.endswith("_basin_g1"):
        # handled by caller via BASIN_G1_PARENTS
        pass
    # state
    if base.startswith("ref"):
        state = "ref"
        rest = base[len("ref"):]
    elif base.startswith("s0_OOH"):
        state = "OOH"
        rest = base[len("s0_OOH"):]
    elif base.startswith("s0_OH"):
        state = "OH"
        rest = base[len("s0_OH"):]
    elif base.startswith("s0_O"):
        state = "O"
        rest = base[len("s0_O"):]
    else:
        return None
    rest = rest.lstrip("_")
    coverage = None
    arm = None
    if rest.startswith("1x1"):
        coverage = "1x1"
        rest = rest[3:].lstrip("_")
    elif rest.startswith("2x1v"):
        coverage = "2x1v"
        rest = rest[4:].lstrip("_")
    if rest in ("mir", "off", "base", "k8", "escape"):
        arm = rest
    elif rest == "basin_g1":
        arm = "basin"
        coverage = "1x1"  # basin substitutions are 1x1-mir cells (docs/54)
        is_g1 = True
    elif rest == "":
        arm = "-"
    else:
        arm = rest  # unknown suffix — surfaces as unclassifiable
    return state, coverage, arm, is_g1, parent


def collect_s3_rows():
    rows = []
    findings = []
    for metal in S3_METALS:
        mdir = S3_DIR / metal
        if not mdir.is_dir():
            continue
        outs = sorted(p.name for p in mdir.iterdir()
                      if p.name.endswith(".out") and not SKIP_RE.search(p.name))
        for name in outs:
            job = name[: -len(".out")]
            path = mdir / name
            parsed = parse_out(path)
            jf = job_fields(job)
            if jf is None:
                findings.append(f"UNPARSEABLE job name: runs/s3/{metal}/{name}")
                continue
            state, coverage, arm, is_g1, parent = jf
            row = {
                "source": "runs/s3",
                "file": f"runs/s3/{metal}/{name}",
                "metal": metal,
                "job": job,
                "state": state,
                "coverage": coverage,
                "arm": arm,
                "is_g1_child": is_g1,
                "flags": [],
            }
            row.update(parsed)
            # parent linkage and delta
            if is_g1:
                if (metal, job) in BASIN_G1_PARENTS:
                    parent_path = REPO / BASIN_G1_PARENTS[(metal, job)]
                    row["parent_file"] = BASIN_G1_PARENTS[(metal, job)]
                else:
                    parent_path = mdir / (parent + ".out")
                    row["parent_file"] = f"runs/s3/{metal}/{parent}.out"
                if parent_path.exists():
                    pE = parse_out(parent_path)["energy_ry"]
                    if pE is not None and row.get("energy_ry") is not None:
                        row["g1_delta_vs_parent_mev"] = round(
                            (row["energy_ry"] - pE) * RY_TO_MEV, 3)
                else:
                    row["g1_delta_vs_parent_mev"] = None
                    row["flags"].append("parent output not found on disk")
            rows.append(row)
    return rows, findings


def classify_s3(rows, findings):
    by_job = {(r["metal"], r["job"]): r for r in rows}
    # children first: a parent's status follows its child's GATE-1 outcome
    ordered = ([r for r in rows if r["is_g1_child"]] +
               [r for r in rows if not r["is_g1_child"]])
    for r in ordered:
        key = (r["metal"], r["job"])
        parent_key = (r["metal"], r["job"][: -len("__g1")]) \
            if r["job"].endswith("__g1") else None
        if key in R1_ROWS or parent_key in R1_ROWS:
            r["status"] = "PENDING-RERELAX"
            r["rule"] = R1_CITE
        elif key in R2_ROWS:
            # should not happen: R2 rows have no final .out
            r["status"] = "PENDING-RETRY"
            r["rule"] = R2_CITE
            findings.append(
                f"R2 row unexpectedly has a final .out on disk: {r['file']}")
        elif key in UNVERIFIED_PARENTS:
            r["status"] = "UNVERIFIED"
            r["rule"] = UNVERIFIED_CITE
        elif r["job"] == "s0_OOH__2x1v_escape" and r["metal"] == "Cr":
            r["status"] = "BANKED"
            r["rule"] = R3_CITE
        elif r["is_g1_child"]:
            d = r.get("g1_delta_vs_parent_mev")
            if d is None:
                r["status"] = "UNCLASSIFIED"
                r["rule"] = None
                findings.append(
                    f"g1 child with no computable parent delta: {r['file']}")
            elif d > 1.0:
                r["status"] = "UNCLASSIFIED"
                r["rule"] = None
                r["flags"].append(
                    f"g1 child is {d:+.2f} meV ABOVE its parent — "
                    f"refused-candidate per {REFUSE_CITE}; not covered by "
                    "docs/55 R1/R2 or the 2026-08-24 census (35 AGREE / 0 "
                    "REFUSED / 2 UNVERIFIED) — FLAGGED, not resolved")
                fp = S3_DIR / r["metal"] / (r["job"] + ".fromparent.out")
                fp_note = (" -- a .fromparent re-run record exists on disk "
                           f"(runs/s3/{r['metal']}/{r['job']}"
                           ".fromparent.out, the docs/43:1589-1592 remedy; "
                           "excluded from parsing by task spec)"
                           if fp.exists() else "")
                if fp_note:
                    r["flags"].append(fp_note.strip(" -"))
                findings.append(
                    f"REFUSED-CANDIDATE g1 child ({d:+.2f} meV above "
                    f"parent {r.get('parent_file')}): {r['file']}{fp_note}")
            else:
                r["status"] = "BANKED"
                r["gate1"] = "AGREE"
                r["rule"] = C9_CITE
                if d < -1.0:
                    r["flags"].append(
                        f"child {d:+.2f} meV BELOW parent (deeper "
                        "electronic state) yet not named in docs/55 R1 — "
                        "FLAGGED for the entrant, banked per the GATE-1 "
                        "census AGREE treatment")
                    findings.append(
                        f"DEEPER-STATE g1 child not in docs/55 R1 "
                        f"({d:+.2f} meV): {r['file']}")
        elif r["arm"] in ("k8",):
            r["status"] = "UNCLASSIFIED"
            r["rule"] = None
            r["flags"].append(
                "k-bridge deck (docs/54:41-43 registers the Cr/Mn k-bridge "
                "correction as infrastructure) — no registered STATUS rule "
                "for these rows is quoted in the state of record; FLAGGED")
            findings.append(f"NO-STATUS-RULE (k-bridge deck): {r['file']}")
        elif r["arm"] in ("base",):
            r["status"] = "UNCLASSIFIED"
            r["rule"] = None
            r["flags"].append(
                "__1x1_base deck — not named in docs/54 rows or docs/55 "
                "rulings quoted in the state of record; FLAGGED")
            findings.append(f"NO-STATUS-RULE (__1x1_base deck): {r['file']}")
        else:
            # parent relaxation row: status follows its child
            child = by_job.get((r["metal"], r["job"] + "__g1"))
            if child is not None and child.get("gate1") == "AGREE":
                r["status"] = "BANKED"
                r["gate1"] = "AGREE (parent; child is energy of record)"
                r["rule"] = C9_CITE
            elif child is not None:
                r["status"] = "UNCLASSIFIED"
                r["rule"] = None
                findings.append(
                    f"parent whose g1 child is unclassified: {r['file']}")
            elif (r["metal"], r["job"] + "__g1") in R2_ROWS:
                r["status"] = "UNVERIFIED"
                r["rule"] = UNVERIFIED_CITE
            else:
                r["status"] = "UNCLASSIFIED"
                r["rule"] = None
                findings.append(
                    f"parent with no __g1 child and no covering rule: "
                    f"{r['file']}")
    return rows


def synth_r2_rows(findings):
    rows = []
    for metal, job in sorted(R2_ROWS):
        jf = job_fields(job)
        state, coverage, arm, is_g1, _ = jf
        final = S3_DIR / metal / (job + ".out")
        attempts = sorted(p.name for p in (S3_DIR / metal).iterdir()
                          if re.fullmatch(re.escape(job) +
                                          r"\.out\.attempt\d+", p.name))
        if final.exists():
            continue  # already emitted as a parsed row (finding logged there)
        rows.append({
            "source": "runs/s3",
            "file": None,
            "metal": metal,
            "job": job,
            "state": state,
            "coverage": coverage,
            "arm": arm,
            "is_g1_child": is_g1,
            "status": "PENDING-RETRY",
            "rule": R2_CITE,
            "converged": False,
            "energy_ry": None,
            "total_magnetization_bohr": None,
            "n_kpoints": None,
            "calculation": None,
            "attempt_records": [f"runs/s3/{metal}/{a}" for a in attempts],
            "flags": ["no final .out on disk — canonical records renamed "
                      "to *.out.attemptN per docs/55 R2"],
        })
        if not attempts:
            findings.append(
                f"R2 PENDING-RETRY row with no *.out.attemptN records on "
                f"disk: runs/s3/{metal}/{job}")
    return rows


def collect_external_rows(findings):
    rows = []
    for spec in EXTERNAL_ROWS:
        path = REPO / spec["path"]
        row = {
            "source": "external",
            "file": spec["path"],
            "metal": spec["metal"],
            "job": Path(spec["path"]).stem,
            "state": spec["state"],
            "coverage": spec["coverage"],
            "arm": spec["arm"],
            "is_g1_child": False,
            "status": spec["status"],
            "rule": spec["rule"],
            "docs54_expected_energy_ry": spec["expected_E"],
            "flags": list(spec["flags"]),
            "cell_member": spec.get("cell_member", True),
        }
        if not path.exists():
            row["flags"].append("FILE MISSING ON DISK")
            findings.append(f"EXTERNAL record file missing: {spec['path']}")
            rows.append(row)
            continue
        row.update(parse_out(path))
        e = row.get("energy_ry")
        if e is not None and abs(e - spec["expected_E"]) > 5e-8:
            row["flags"].append(
                f"parsed energy {e:.8f} differs from docs/54 printed value "
                f"{spec['expected_E']:.8f}")
            findings.append(
                f"ENERGY MISMATCH vs docs/54: {spec['path']} parsed "
                f"{e:.8f} vs docs/54 {spec['expected_E']:.8f}")
        if spec["parallel"]:
            ppath = REPO / spec["parallel"]
            pinfo = {"file": spec["parallel"]}
            if ppath.exists():
                pp = parse_out(ppath)
                pinfo["energy_ry"] = pp["energy_ry"]
                pinfo["total_magnetization_bohr"] = \
                    pp["total_magnetization_bohr"]
                pinfo["note"] = ("production output retained and quoted "
                                 "alongside per docs/54 (A8.8 forbids "
                                 "in-place replacement, docs/43:1754-1764)")
            else:
                pinfo["note"] = "FILE MISSING ON DISK"
                findings.append(
                    f"PARALLEL production file missing: {spec['parallel']}")
            row["parallel_production"] = pinfo
        rows.append(row)
    return rows


def build_cells(all_rows, findings):
    """energy_of_record per (metal, state, coverage, arm) cell."""
    cells = {}

    def cell_key(m, s, c, a):
        return f"{m}|{s}|{c}|{a}"

    # index runs/s3 rows
    s3_parents = {}
    s3_children = {}
    for r in all_rows:
        if r["source"] != "runs/s3":
            continue
        if r["is_g1_child"]:
            s3_children[(r["metal"], r["job"])] = r
        else:
            s3_parents[(r["metal"], r["job"])] = r

    # 1) runs/s3 parent rows -> cells
    for (metal, job), r in sorted(s3_parents.items()):
        if r["file"] is None:
            continue  # synthetic PENDING-RETRY rows: handled in step 2
        state, coverage, arm = r["state"], r["coverage"], r["arm"]
        if arm == "escape":
            # docs/55 R3: this row IS the Cr *OOH 2x1v mir energy of record
            key = cell_key(metal, state, coverage, "mir")
            child = s3_children.get((metal, job + "__g1"))
            cells[key] = {
                "cell": key, "metal": metal, "state": state,
                "coverage": coverage, "arm": "mir",
                "status": "BANKED",
                "energy_of_record_file": r["file"],
                "energy_of_record_ry": r["energy_ry"],
                "total_magnetization_bohr": r["total_magnetization_bohr"],
                "rule": R3_CITE,
                "notes": ["mirror saddle carried as DIAGNOSTIC row "
                          "(runs/probe/Cr_cellsym/s0_OOH__2x1v_mir.out)"] +
                         ([f"escape __g1 child AGREE "
                           f"({child['g1_delta_vs_parent_mev']:+.3f} meV); "
                           "docs/55 R3 names the escape minimum FILE as the "
                           "energy of record, so R3 is applied verbatim and "
                           "the child is quoted, not substituted"]
                          if child else []),
            }
            continue
        key = cell_key(metal, state, coverage, arm)
        status = r["status"]
        child = s3_children.get((metal, job + "__g1"))
        cell = {
            "cell": key, "metal": metal, "state": state,
            "coverage": coverage, "arm": arm,
            "status": status, "notes": [],
        }
        if status == "PENDING-RERELAX":
            cell.update({
                "energy_of_record_file": None, "energy_of_record_ry": None,
                "rule": R1_CITE,
                "parent_quoted": {"file": r["file"],
                                  "energy_ry": r["energy_ry"]},
                "child_quoted": ({"file": child["file"],
                                  "energy_ry": child["energy_ry"],
                                  "delta_mev": child.get(
                                      "g1_delta_vs_parent_mev")}
                                 if child else None),
            })
        elif status == "UNVERIFIED":
            cell.update({
                "energy_of_record_file": None, "energy_of_record_ry": None,
                "rule": UNVERIFIED_CITE,
                "parent_quoted": {"file": r["file"],
                                  "energy_ry": r["energy_ry"]},
            })
        elif child is not None and child.get("gate1") == "AGREE":
            cell.update({
                "energy_of_record_file": child["file"],
                "energy_of_record_ry": child["energy_ry"],
                "total_magnetization_bohr":
                    child["total_magnetization_bohr"],
                "rule": C9_CITE,
                "parent_quoted": {"file": r["file"],
                                  "energy_ry": r["energy_ry"]},
            })
        else:
            cell.update({
                "energy_of_record_file": None, "energy_of_record_ry": None,
                "rule": None,
            })
            cell["notes"].append("no rule quoted in the state of record "
                                 "determines this cell — FLAGGED")
            findings.append(f"CELL WITHOUT RULE: {key} (row {r['file']})")
        cells[key] = cell

    # 2) synthetic R2 / external rows -> cells
    for r in all_rows:
        if r["source"] == "runs/s3" and r["file"] is None:
            if r["is_g1_child"]:
                continue  # pending g1 children attach to their parent cells
            key = cell_key(r["metal"], r["state"], r["coverage"], r["arm"])
            if key not in cells:
                cells[key] = {
                    "cell": key, "metal": r["metal"], "state": r["state"],
                    "coverage": r["coverage"], "arm": r["arm"],
                    "status": "PENDING-RETRY",
                    "energy_of_record_file": None,
                    "energy_of_record_ry": None,
                    "rule": R2_CITE, "notes": [],
                }
        elif r["source"] == "external" and r.get("cell_member", True):
            key = cell_key(r["metal"], r["state"], r["coverage"], r["arm"])
            if r["status"] == "DIAGNOSTIC":
                continue  # the Cr saddle: its cell is owned by docs/55 R3
            if key in cells:
                findings.append(
                    f"CELL COLLISION: {key} claimed by both {cells[key].get('energy_of_record_file')} and {r['file']}")
                continue
            cell = {
                "cell": key, "metal": r["metal"], "state": r["state"],
                "coverage": r["coverage"], "arm": r["arm"],
                "status": r["status"],
                "energy_of_record_file": r["file"],
                "energy_of_record_ry": r["energy_ry"],
                "total_magnetization_bohr": r["total_magnetization_bohr"],
                "rule": r["rule"],
                "notes": list(r["flags"]),
            }
            if "parallel_production" in r:
                cell["parallel_production"] = r["parallel_production"]
            # basin rows now have __g1 children inside runs/s3
            for (m, j), pfile in BASIN_G1_PARENTS.items():
                if pfile == r["file"] and m == r["metal"]:
                    child = s3_children.get((m, j))
                    if child is None:
                        continue
                    d = child.get("g1_delta_vs_parent_mev")
                    if child.get("gate1") == "AGREE":
                        cell["energy_of_record_file"] = child["file"]
                        cell["energy_of_record_ry"] = child["energy_ry"]
                        cell["total_magnetization_bohr"] = \
                            child["total_magnetization_bohr"]
                        cell["rule"] = (r["rule"] + " ; " + C9_CITE +
                                        " (basin __g1 child AGREE, "
                                        f"{d:+.3f} meV)")
                        cell["parent_quoted"] = {"file": r["file"],
                                                 "energy_ry": r["energy_ry"]}
                    else:
                        cell["notes"].append(
                            f"basin __g1 child {child['file']} is "
                            f"{d:+.2f} meV vs parent — refused-candidate "
                            f"per {REFUSE_CITE}; energy of record stays "
                            "the docs/54 basin file pending the owed re-run "
                            "— FLAGGED")
            cells[key] = cell

    # 3) by-record GAP cells (docs/54:206, :226)
    for g in GAP_CELLS:
        key = cell_key(g["metal"], g["state"], g["coverage"], g["arm"])
        if key not in cells:
            cells[key] = {
                "cell": key, "metal": g["metal"], "state": g["state"],
                "coverage": g["coverage"], "arm": g["arm"],
                "status": "GAP",
                "energy_of_record_file": None, "energy_of_record_ry": None,
                "rule": g["rule"], "notes": [],
            }
    return [cells[k] for k in sorted(cells)]


def main():
    findings = []
    s3_rows, findings_parse = collect_s3_rows()
    findings.extend(findings_parse)
    s3_rows = classify_s3(s3_rows, findings)
    s3_rows.extend(synth_r2_rows(findings))
    ext_rows = collect_external_rows(findings)
    all_rows = s3_rows + ext_rows
    all_rows.sort(key=lambda r: (r["metal"], r["source"],
                                 r["file"] or f"zz-pending/{r['job']}"))
    cells = build_cells(all_rows, findings)

    # census
    def count(pred):
        return sum(1 for r in all_rows if pred(r))

    status_counts = {}
    for r in all_rows:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
    gate1_agree = count(lambda r: r.get("gate1") == "AGREE")
    counts = {
        "rows_total": len(all_rows),
        "rows_runs_s3": count(lambda r: r["source"] == "runs/s3"),
        "rows_external": count(lambda r: r["source"] == "external"),
        "rows_by_status": dict(sorted(status_counts.items())),
        "gate1_agree_children": gate1_agree,
        "gate1_refused_candidates": count(
            lambda r: any("refused-candidate" in f for f in r["flags"])),
        "gate1_unverified_parents": count(
            lambda r: r["status"] == "UNVERIFIED"),
        "gate1_census_of_record": "35 AGREE / 0 REFUSED / 2 UNVERIFIED "
                                  "(2026-08-24)",
        "cells_total": len(cells),
        "cells_with_energy_of_record": sum(
            1 for c in cells if c["energy_of_record_ry"] is not None),
        "cells_pending_or_gap": sum(
            1 for c in cells if c["energy_of_record_ry"] is None),
        "unconverged_final_outs": count(
            lambda r: r.get("file") and r["source"] == "runs/s3"
            and not r.get("converged")),
        "findings_unclassified": sorted(set(findings)),
    }

    payload = {
        "generated_by": ("src/dft/s3_readout.py — deterministic S3 readout, "
                         "state of record 2026-08-24; disclosed AI-drafted "
                         "infrastructure; rules applied verbatim from "
                         "docs/52 C9, docs/54, docs/55 R1/R2/R3, "
                         "docs/43:1589-1592"),
        "rows": all_rows,
        "cells": cells,
        "counts": counts,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True,
                      ensure_ascii=False) + "\n"
    OUT_JSON.write_text(text, encoding="utf-8", newline="\n")

    # stdout census
    print("S3 READOUT CENSUS (state of record 2026-08-24)")
    print(f"  rows total          : {counts['rows_total']} "
          f"(runs/s3 {counts['rows_runs_s3']}, "
          f"external {counts['rows_external']})")
    for k, v in counts["rows_by_status"].items():
        print(f"    status {k:<16}: {v}")
    print(f"  GATE-1 AGREE children (computed) : {gate1_agree}")
    print(f"  GATE-1 refused-candidates        : "
          f"{counts['gate1_refused_candidates']}")
    print(f"  GATE-1 UNVERIFIED parents        : "
          f"{counts['gate1_unverified_parents']}")
    print(f"  census of record                 : "
          f"{counts['gate1_census_of_record']}")
    print(f"  cells: {counts['cells_total']} total, "
          f"{counts['cells_with_energy_of_record']} with energy of record, "
          f"{counts['cells_pending_or_gap']} pending/gap")
    print(f"  JSON: {OUT_JSON.relative_to(REPO)}")
    if counts["findings_unclassified"]:
        print("  FINDINGS (unclassifiable / flagged rows):")
        for f in counts["findings_unclassified"]:
            print(f"    - {f}")
    else:
        print("  FINDINGS: none")


if __name__ == "__main__":
    main()
