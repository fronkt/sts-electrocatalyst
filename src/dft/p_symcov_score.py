# P-SYMCOV scoring over runs/s3/readout/s3_readout_2026-08-24.json
# Registered rules applied (quoted in the artifacts):
#   docs/43:1532-1533  wording rule (coverage attached in the same sentence)
#   docs/43:1539-1541  satisfaction: per metal, symmetry effect at both coverages or GAP;
#                      single-coverage metal never averaged into any symmetry statistic
#   docs/43:1546-1554  claim-scope branch; "most" = >= 5 of the 8 metals with both cells measured
#   docs/43:1566-1571  A8.3 magnetic CONFOUND: |dM| > 0.05 uB -> CONFOUNDED, excluded from
#                      contrast statistics and reported separately (precedent docs/43:306-310)
#   docs/55 R3         Cr *OOH 2x1v mir energy of record = escape minimum (quote min-to-min)
# Convention check: Delta_sym = E(off) - E(mir); reproduces docs/54:245's printed signs
# (+0.2475 eV at 1x1, +0.0130 eV at 2x1v for Ru *OH) and docs/54:152's 1.188 eV magnitude
# against the saddle. Nothing else is assumed.
import json, os

RY2MEV = 13605.693
ROOT = r"C:\Users\frank\sts-electrocatalyst"
readout_path = os.path.join(ROOT, "runs", "s3", "readout", "s3_readout_2026-08-24.json")
d = json.load(open(readout_path, encoding="utf-8"))
cells = {c["cell"]: c for c in d["cells"]}

METALS = ["Cr", "Mn", "Fe", "Co", "Ni", "Ru", "Ir", "Ti"]  # the 8 S3 systems, docs/54:23-25
STATES = ["O", "OH", "OOH"]
COVS = ["1x1", "2x1v"]

# docs/55 R2 array-20123293 membership (round 3), quoted from the state of record:
R2_ROWS = {
    "Co|ref|2x1v|-", "Co|OH|1x1|off", "Co|O|2x1v|mir", "Co|OH|2x1v|mir", "Co|OOH|2x1v|mir",
    "Co|OH|2x1v|off", "Co|OOH|2x1v|off", "Ni|OOH|2x1v|mir", "Ni|OOH|2x1v|off",
}
# g1 children in the array: Co s0_O__1x1_off__g1, Ni s0_OH__2x1v_off__g1 (verify parents)
G1_IN_ARRAY_PARENTS = {"Co|O|1x1|off", "Ni|OH|2x1v|off"}
# docs/55 R1 __basin re-relaxations in the same array:
R1_ROWS = {"Fe|OOH|1x1|off", "Mn|OOH|2x1v|off"}

def get(metal, state, cov, arm):
    return cells.get(f"{metal}|{state}|{cov}|{arm}")

def member_summary(c):
    if c is None:
        return {"status": "ABSENT", "note": "no cell of this name exists in the readout"}
    out = {
        "status": c["status"],
        "file": c.get("energy_of_record_file"),
        "energy_ry": c.get("energy_of_record_ry"),
        "M_uB": c.get("total_magnetization_bohr"),
    }
    if c.get("parent_quoted"):
        out["parent_quoted"] = c["parent_quoted"]
    if c.get("child_quoted"):
        out["child_quoted"] = c["child_quoted"]
    if c.get("notes"):
        out["notes"] = c["notes"]
    return out

def round3(cell_key, c):
    """What round 3 (array 20123293, docs/55 R1/R2) can change for this member."""
    if c is None:
        return "nothing — no deck exists for this cell; not in array 20123293"
    if cell_key in R1_ROWS:
        return ("__basin re-relaxation in flight (docs/55 R1, array 20123293); round 3 delivers "
                "the final off-arm member — until then quote parent AND child, bank neither")
    if cell_key in R2_ROWS:
        return ("rung-(iii) row PENDING-RETRY in array 20123293 (docs/55 R2); a converged round-3 "
                ".out would give this cell an energy of record")
    if cell_key in G1_IN_ARRAY_PARENTS:
        return ("parent UNVERIFIED — its __g1 child is PENDING-RETRY in array 20123293 (docs/55 R2); "
                "a converged AGREE child banks this cell (child quoted per docs/52 C9), a REFUSED "
                "child triggers docs/43:1589-1592")
    if c["status"] == "GAP":
        return ("nothing — GAP by record (docs/54:206/:226), not in array 20123293; reopening it "
                "would be an entrant action outside round 3")
    if c["status"] == "UNCLASSIFIED":
        return ("nothing — cell has no rule in the state of record and is not in array 20123293; "
                "needs an entrant ruling (for Ni *O 1x1 off: refused __g1 child +85.10 meV, remedy "
                "re-run exists only as the spec-excluded .fromparent.out)")
    return None

CONF_CITE = "docs/43:1566-1571"

pairs = []
for metal in METALS:
    for state in STATES:
        for cov in COVS:
            mir = get(metal, state, cov, "mir")
            off = get(metal, state, cov, "off")
            key_m = f"{metal}|{state}|{cov}|mir"
            key_o = f"{metal}|{state}|{cov}|off"
            rec = {
                "metal": metal, "state": "*" + state, "coverage": cov,
                "mir": member_summary(mir), "off": member_summary(off),
                "pair_status": None, "delta_sym_mev": None, "delta_sym_ev": None,
                "delta_M_uB": None, "confound_check": None, "tags": [], "why_unscored": None,
                "round3_impact": [],
            }
            # member-level blockers
            blockers = []
            for arm_key, c in ((key_m, mir), (key_o, off)):
                st = "ABSENT" if c is None else c["status"]
                if st not in ("BANKED",):
                    blockers.append((arm_key, st))
                r3 = round3(arm_key, c)
                if r3 and (c is None or c["status"] != "BANKED"):
                    rec["round3_impact"].append({"member": arm_key, "round3": r3})
            if blockers:
                rec["pair_status"] = "UNSCORED"
                rec["why_unscored"] = "; ".join(
                    f"{k.split('|')[-1]} member is {st}" for k, st in blockers)
                # quote R1 parent+child without banking (docs/55 R1)
                pairs.append(rec)
                continue
            e_m, e_o = mir["energy_of_record_ry"], off["energy_of_record_ry"]
            dmev = (e_o - e_m) * RY2MEV
            rec["delta_sym_mev"] = round(dmev, 2)
            rec["delta_sym_ev"] = round(dmev / 1000.0, 4)
            m_m, m_o = mir.get("total_magnetization_bohr"), off.get("total_magnetization_bohr")
            record_confound = any(
                "CONFOUNDED" in (c.get("rule") or "") or
                any("CONFOUNDED" in n for n in c.get("notes", []))
                for c in (mir, off))
            if m_m is None or m_o is None:
                rec["confound_check"] = ("NOT-APPLICABLE — no converged total magnetisation printed "
                                         "(nspin=1 / d0 row, docs/54:64-66); the registered rule "
                                         f"({CONF_CITE}) presumes a converged moment — open question")
                rec["tags"].append("CONFOUND-CHECK-NA")
            else:
                dM = abs(m_m - m_o)
                rec["delta_M_uB"] = round(dM, 2)
                if dM > 0.05:
                    rec["confound_check"] = (f"CONFOUNDED — |dM| = {dM:.2f} uB > 0.05 uB ({CONF_CITE}); "
                                             "excluded from contrast statistics, reported separately "
                                             "(treatment per docs/43:306-310)")
                    rec["tags"].append("CONFOUNDED")
                else:
                    rec["confound_check"] = f"PASS — |dM| = {dM:.2f} uB <= 0.05 uB ({CONF_CITE})"
            if record_confound and "CONFOUNDED" not in rec["tags"]:
                rec["tags"].append("CONFOUNDED-BY-RECORD")
                rec["confound_check"] += (
                    " ; BUT the state of record marks this pair CONFOUNDED "
                    "(docs/54 marking carried on the cell) — the record marking is carried, the "
                    "readout-member dM discrepancy is flagged for the entrant")
            # mirror-member standing OPEN flags carried from readout notes
            for c in (mir, off):
                for n in c.get("notes", []):
                    if "OPEN" in n and "mirror-member" in n or "stands as a mirror member" in n:
                        rec["tags"].append("MIR-MEMBER-STANDING-OPEN")
                    if "member identity OPEN" in n:
                        rec["tags"].append("MEMBER-IDENTITY-OPEN")
                    if "oosh-member question OPEN" in n:
                        rec["tags"].append("OOSH-MEMBER-OPEN")
                    if "refused-candidate" in n or "REFUSED" in n:
                        rec["tags"].append("MIR-G1-REFUSED-CANDIDATE")
            rec["tags"] = sorted(set(rec["tags"]))
            excl = any(t.startswith("CONFOUNDED") for t in rec["tags"])
            rec["pair_status"] = "SCORED-EXCLUDED" if excl else "SCORED"
            # docs/55 R3 special quote for Cr *OOH 2x1v
            if metal == "Cr" and state == "OOH" and cov == "2x1v":
                rec["tags"].append("R3-ESCAPE-MINIMUM")
                rec["r3_note"] = (
                    "docs/55 R3: mir member = escape minimum runs/s3/Cr/s0_OOH__2x1v_escape.out "
                    "(-3188.71605541 Ry); mir-vs-off gap quoted minimum-to-minimum at 2x1v coverage: "
                    f"{dmev:.2f} meV. The saddle value -3188.70497020 Ry is a DIAGNOSTIC, not a "
                    "state; docs/54:152's CONFOUNDED marking (Delta_sym 1.188 eV) was computed "
                    "against that superseded saddle — whether the min-to-min pair re-enters the "
                    "contrast statistics is not ruled anywhere; readout members have |dM| = 0.00 uB")
            pairs.append(rec)

# coverage-dependence quantity per (metal, state): DD = Delta_sym(1x1) - Delta_sym(2x1v)
# (docs/43:1546-1547; classifier cut for "large" is NOT registered — values only, no verdicts)
by_ms = {}
for p in pairs:
    by_ms.setdefault((p["metal"], p["state"]), {})[p["coverage"]] = p
dd_rows = []
for (metal, state), cc in by_ms.items():
    p1, p2 = cc.get("1x1"), cc.get("2x1v")
    row = {"metal": metal, "state": state}
    ok1 = p1 and p1["pair_status"] == "SCORED"
    ok2 = p2 and p2["pair_status"] == "SCORED"
    if ok1 and ok2:
        dd = p1["delta_sym_mev"] - p2["delta_sym_mev"]
        row["dd_mev"] = round(dd, 2)
        row["abs_dd_ev"] = round(abs(dd) / 1000.0, 4)
        row["enters_pooled_statistics"] = True
        row["tags"] = sorted(set(p1["tags"]) | set(p2["tags"]))
    else:
        row["dd_mev"] = None
        row["enters_pooled_statistics"] = False
        why = []
        for cov, p, ok in (("1x1", p1, ok1), ("2x1v", p2, ok2)):
            if not ok:
                why.append(f"{cov}: " + (p["why_unscored"] or "pair CONFOUNDED — excluded (docs/43:1566-1569)"
                           if p else "no pair"))
        row["why_excluded"] = "; ".join(why)
    dd_rows.append(row)
dd_rows.sort(key=lambda r: (METALS.index(r["metal"]), STATES.index(r["state"].lstrip("*"))))

# per-metal coverage status (satisfaction table, docs/43:1539-1541)
per_metal = []
for metal in METALS:
    entry = {"metal": metal}
    for cov in COVS:
        scored, excluded, pending, gap = [], [], [], []
        for state in STATES:
            p = by_ms[(metal, "*" + state)].get(cov)
            if p is None:
                gap.append("*" + state)
            elif p["pair_status"] == "SCORED":
                scored.append("*" + state)
            elif p["pair_status"] == "SCORED-EXCLUDED":
                excluded.append("*" + state)
            else:
                mir_abs = p["mir"]["status"] in ("GAP", "ABSENT", "UNCLASSIFIED")
                off_abs = p["off"]["status"] in ("GAP", "ABSENT", "UNCLASSIFIED")
                (gap if (mir_abs or off_abs) and not any(
                    r["member"].split("|")[0:1] for r in p["round3_impact"]
                    if "array 20123293" in r["round3"] and "PENDING" in r["round3"].upper()
                ) else pending).append("*" + state)
        entry[cov] = {"scored": scored, "excluded_confounded": excluded,
                      "pending_or_unverified": pending, "gap_absent_or_unclassified": gap}
    sc1 = bool(entry["1x1"]["scored"])
    sc2 = bool(entry["2x1v"]["scored"])
    entry["both_coverages_scored_now_any_state_reading"] = sc1 and sc2
    entry["single_or_zero_coverage_now"] = not (sc1 and sc2)
    per_metal.append(entry)

both_now = [e["metal"] for e in per_metal if e["both_coverages_scored_now_any_state_reading"]]

artifact = {
    "artifact": "P-SYMCOV score over the S3 readout",
    "date": "2026-08-24",
    "input": "runs/s3/readout/s3_readout_2026-08-24.json",
    "script": "session scratchpad p_symcov_score.py (disclosed AI infrastructure)",
    "convention": ("Delta_sym = E(off) - E(mir) per (metal, state, coverage), energies of record "
                   "from the readout (GATE-1 AGREE rows quote the child, docs/52 C9); meV = Ry x "
                   "13605.693. Sign convention verified against docs/54:245 (+0.2475 eV at 1x1, "
                   "+0.0130 eV at 2x1v for Ru *OH) and docs/54:152 (1.188 eV vs the saddle)."),
    "wording_rule": ("docs/43:1532-1533: no statement of the symmetry-trap magnitude appears in "
                     "this artifact without the coverage at which it was measured attached in the "
                     "same sentence/row — every magnitude below is coverage-indexed."),
    "registered_rules_applied": [
        "docs/43:1539-1541 (THRESHOLD adopted 2026-08-23): P-SYMCOV satisfied when, for every metal in S3, the symmetry effect is reported at both coverages, or the missing cell is reported as a gap; a metal with only one coverage is not averaged into any symmetry statistic.",
        "docs/43:1546-1554: claim-scope branch; 'most' = >= 5 of the 8 metals with both cells measured; a metal with one cell is a gap. Coverage-DEPENDENT = |DeltaDeltaE(1x1) - DeltaDeltaE(2x1v)| large (NO numeric cut registered); coverage-INDEPENDENT = agreement 'within the basin CONFOUND tolerance' (registered tolerance is 0.05 uB, a magnetisation) — neither branch is decidable by this script; values are reported, the sentence is the entrant's (docs/43:1554-1556).",
        "docs/43:1566-1571: pair members differing > 0.05 uB in converged total magnetisation -> CONFOUNDED, excluded from contrast statistics, reported separately (treatment per the geometry precedent docs/43:306-310).",
        "docs/55 R3: Cr *OOH 2x1v mir energy of record = escape minimum -3188.71606 Ry (runs/s3/Cr/s0_OOH__2x1v_escape.out); saddle -3188.70497 is a diagnostic, not a state.",
        "docs/55 R1: Fe s0_OOH__1x1_off and Mn s0_OOH__2x1v_off PENDING-RERELAX — quote parent AND child, bank neither.",
        "docs/55 R2: 11 rung-(iii) rows PENDING-RETRY in array 20123293.",
        "docs/54:23-25: the 8 S3 systems = tier_v2 seven + TiO2 (denominator of the >= 5-of-8 count).",
        "docs/54:37-40: symmetry pairs are mir-vs-off contrasts at each coverage.",
    ],
    "pairs": pairs,
    "coverage_dependence_DD": {
        "definition": ("DD = Delta_sym(1x1) - Delta_sym(2x1v) per (metal, state); |DD| is the "
                       "quantity the docs/43:1546-1547 classifier compares (equal in magnitude to "
                       "block 1A's I, docs/43:169, opposite sign). Values only — the registered "
                       "classifier has no numeric cut for 'large', and the per-metal aggregation "
                       "of states is not registered; no verdict is emitted."),
        "rows": dd_rows,
    },
    "per_metal_coverage_table": per_metal,
    "satisfaction": {
        "rule": "docs/43:1539-1541",
        "statement": ("Under the reading that a PENDING/UNVERIFIED/ABSENT cell 'reported as a gap' "
                      "discharges the reporting condition, this artifact reports every one of the 8 "
                      "metals at both coverages (symmetry effect or explicit gap), so the reporting "
                      "condition is discharged BY THIS REPORT as of 2026-08-24. Whether a PENDING "
                      "cell counts as 'a gap' for final-report purposes is not registered — open."),
        "single_coverage_exclusion": ("Metals with a scored (non-excluded) symmetry pair at both "
                                      "coverages right now, any-state reading: "
                                      + ", ".join(both_now) +
                                      f" ({len(both_now)} of 8). All other metals are, today, "
                                      "single- or zero-coverage and enter no pooled symmetry "
                                      "statistic (docs/43:1540-1541)."),
    },
    "claim_scope_branch": {
        "rule": "docs/43:1546-1554",
        "resolution": ("NOT RESOLVED HERE. The >= 5-of-8 count requires (a) a per-metal symmetry "
                       "effect whose aggregation over states is unregistered, (b) a numeric cut for "
                       "'large' that is unregistered, and (c) rulings on the tier_v2 1x1 mirror-member "
                       "standing (docs/54:406-411) and on confounded-pair coverage status. "
                       "The facts needed for the entrant's sentence are in "
                       "coverage_dependence_DD.rows and per_metal_coverage_table."),
        "metals_with_both_coverages_scored_now_any_state_reading": both_now,
    },
    "open_questions_registered_elsewhere": [
        "Per-metal aggregation of the per-state symmetry effect is unregistered (which state(s) carry the metal's 'symmetry effect' for the >= 5-of-8 count).",
        "The coverage-DEPENDENT cut ('large') has no registered numeric value; the coverage-INDEPENDENT tolerance cited is 0.05 uB, a magnetisation, applied to an energy comparison (spec-flagged).",
        "Mn/Fe/Co/Ni tier_v2 1x1 mirror reuse rows are nosym ON_PLANE/EXPLORED — 'neither registered arm' (docs/54:406-411); if they do not stand as mirror members, every 1x1 pair tagged MIR-MEMBER-STANDING-OPEN becomes a gap.",
        "Whether a CONFOUNDED pair counts as 'measured' for a metal's coverage status is unregistered.",
        "Ru/Ir (nspin=1) and Ti (d0) print no total magnetisation; whether the 0.05 uB confound check is trivially passed or inapplicable is unregistered (spec-flagged).",
        "Cr *OH 1x1: the state of record (docs/54:147) marks the pair CONFOUNDED while both readout members print M = 11.00 uB (|dM| = 0.00) — the record marking is carried; the discrepancy is for the entrant.",
        "Cr *OOH 1x1: docs/54:150/:400-405 'pair CONFOUNDED either way', member identity OPEN (production M 11.80 vs basin M 11.00); carried as CONFOUNDED.",
        "Cr *OOH 2x1v: docs/54:152's CONFOUNDED marking was computed against the superseded saddle; on the docs/55 R3 escape-minimum members |dM| = 0.00 uB — whether the min-to-min pair re-enters contrast statistics is unruled.",
        "Which member's M enters the 0.05 uB comparison where the __g1 child is the energy of record (spec-flagged); this script used the readout's energy-of-record M per cell.",
        "Ni *O 1x1 off is UNCLASSIFIED (refused __g1 child +85.10 meV; remedy re-run exists only as the spec-excluded .fromparent.out) and is NOT in array 20123293 — round 3 cannot deliver this cell.",
    ],
}

out_json = os.path.join(ROOT, "runs", "s3", "readout", "p_symcov_2026-08-24.json")
with open(out_json, "w", encoding="utf-8", newline="\n") as f:
    json.dump(artifact, f, indent=1, sort_keys=True)
    f.write("\n")

# ---------- markdown ----------
def fmt(v, unit=""):
    return "—" if v is None else f"{v:+.2f}{unit}"

lines = []
A = lines.append
A("# P-SYMCOV score — S3 readout, 2026-08-24")
A("")
A("Input: `runs/s3/readout/s3_readout_2026-08-24.json`. Convention: Delta_sym = E(off) − E(mir) "
  "per (metal, state, coverage) from the energies of record (GATE-1 AGREE rows quote the child, "
  "docs/52 C9); meV = Ry × 13605.693. Sign verified against docs/54:245 and docs/54:152.")
A("")
A("Wording rule (docs/43:1532-1533): every symmetry-effect magnitude below is stated with the "
  "coverage at which it was measured in the same row or sentence.")
A("")
A("## Registered rules applied")
A("")
A("- **Satisfaction** (docs/43:1539-1541, THRESHOLD adopted 2026-08-23): per metal, the symmetry "
  "effect reported at both coverages or the missing cell reported as a gap; a metal with only one "
  "coverage is not averaged into any symmetry statistic.")
A("- **Claim-scope branch** (docs/43:1546-1554): 'most' = ≥ 5 of the 8 metals with both cells "
  "measured; coverage-DEPENDENT = |ΔΔE(1x1) − ΔΔE(2x1v)| large (no numeric cut registered); "
  "coverage-INDEPENDENT = agreement within the basin CONFOUND tolerance (registered as 0.05 uB, a "
  "magnetisation). Neither branch is decided here; the sentence is the entrant's (docs/43:1554-1556).")
A("- **CONFOUND** (docs/43:1566-1571): pair members differing > 0.05 uB in converged total "
  "magnetisation → CONFOUNDED, excluded from contrast statistics, reported separately "
  "(treatment per docs/43:306-310).")
A("- **docs/55 R1/R2/R3**: R1 rows quote parent AND child, bank neither; R2 rows are PENDING-RETRY "
  "in array 20123293 (round 3); R3 fixes the Cr *OOH 2x1v mir record at the escape minimum, saddle "
  "kept as diagnostic.")
A("- The 8 S3 systems (denominator): tier_v2 seven + TiO2 (docs/54:23-25); symmetry pairs are "
  "mir-vs-off contrasts at each coverage (docs/54:37-40).")
A("")
A("## Symmetry effect Delta_sym = E(off) − E(mir), by metal, state, coverage (meV)")
A("")
A("| Metal | State | Δ_sym @1x1 (meV) | 1x1 tag | Δ_sym @2x1v (meV) | 2x1v tag | ΔΔ = 1x1 − 2x1v (meV) |")
A("|---|---|---|---|---|---|---|")
def tagstr(p):
    if p is None:
        return "ABSENT"
    if p["pair_status"] == "UNSCORED":
        return "UNSCORED: " + p["why_unscored"]
    t = ",".join(p["tags"]) if p["tags"] else "clean"
    return ("EXCLUDED " if p["pair_status"] == "SCORED-EXCLUDED" else "") + t
for (metal, state) in [(m, "*" + s) for m in METALS for s in STATES]:
    cc = by_ms[(metal, state)]
    p1, p2 = cc.get("1x1"), cc.get("2x1v")
    ddrow = next(r for r in dd_rows if r["metal"] == metal and r["state"] == state)
    A(f"| {metal} | {state} | "
      f"{fmt(p1['delta_sym_mev']) if p1 else '—'} | {tagstr(p1)} | "
      f"{fmt(p2['delta_sym_mev']) if p2 else '—'} | {tagstr(p2)} | "
      f"{fmt(ddrow['dd_mev'])} |")
A("")
A("ΔΔ is quoted only where BOTH pairs are SCORED and non-excluded; |ΔΔ| is the docs/43:1546-1547 "
  "classifier quantity (equal in magnitude, opposite in sign, to block 1A's I, docs/43:169). "
  "No 'large' verdicts are emitted — no numeric cut is registered.")
A("")
A("## Confounded pairs — reported separately, excluded from every contrast statistic "
  "(docs/43:1566-1571; treatment per docs/43:306-310)")
A("")
A("| Pair (metal, state, coverage) | Δ_sym at that coverage (meV) | abs ΔM (uB) | Basis |")
A("|---|---|---|---|")
for p in pairs:
    if p["pair_status"] == "SCORED-EXCLUDED":
        basis = ("record marking (docs/54) — readout members agree in M; discrepancy flagged"
                 if "CONFOUNDED-BY-RECORD" in p["tags"] else
                 f"measured abs dM > 0.05 uB ({CONF_CITE})")
        A(f"| {p['metal']} {p['state']} @{p['coverage']} | {fmt(p['delta_sym_mev'])} | "
          f"{('%.2f' % p['delta_M_uB']) if p['delta_M_uB'] is not None else '0.00 (record says CONFOUNDED)'} | {basis} |")
A("")
A("## Cr *OOH at 2x1v — docs/55 R3, quoted minimum-to-minimum")
A("")
crp = by_ms[("Cr", "*OOH")]["2x1v"]
A(f"At 2x1v coverage, the Cr *OOH mir-vs-off gap quoted minimum-to-minimum is "
  f"{crp['delta_sym_mev']:+.2f} meV ({crp['delta_sym_ev']:+.4f} eV): "
  "E(off) = −3188.79231810 Ry (runs/probe/Cr_cellsym/s0_OOH__2x1v_off.out) minus the escape "
  "minimum E(mir) = −3188.71605541 Ry (runs/s3/Cr/s0_OOH__2x1v_escape.out, docs/55 R3). The "
  "mirror saddle −3188.70497020 Ry is a DIAGNOSTIC, not a state (docs/55 R3); docs/54:152's "
  "CONFOUNDED marking (Δ_sym 1.188 eV at 2x1v) was computed against that superseded saddle. On "
  "the R3 members |ΔM| = 0.00 uB; whether the min-to-min pair re-enters the contrast statistics "
  "is not ruled anywhere — entrant's call.")
A("")
A("## Per-metal coverage status (satisfaction table, docs/43:1539-1541)")
A("")
A("| Metal | 1x1 | 2x1v | Both coverages scored now (any-state reading) |")
A("|---|---|---|---|")
def covstr(e, cov):
    c = e[cov]
    bits = []
    if c["scored"]: bits.append("scored: " + " ".join(c["scored"]))
    if c["excluded_confounded"]: bits.append("confounded: " + " ".join(c["excluded_confounded"]))
    if c["pending_or_unverified"]: bits.append("pending: " + " ".join(c["pending_or_unverified"]))
    if c["gap_absent_or_unclassified"]: bits.append("gap/absent/unclassified: " + " ".join(c["gap_absent_or_unclassified"]))
    return "; ".join(bits) if bits else "—"
for e in per_metal:
    A(f"| {e['metal']} | {covstr(e,'1x1')} | {covstr(e,'2x1v')} | "
      f"{'YES' if e['both_coverages_scored_now_any_state_reading'] else 'no'} |")
A("")
A(f"Metals with a scored, non-excluded symmetry pair at both coverages today (any-state reading): "
  f"**{', '.join(both_now)}** ({len(both_now)} of 8). Every other metal is single- or zero-coverage "
  "today and enters no pooled symmetry statistic (docs/43:1540-1541). This count is a reading, not "
  "a ruling: the per-metal aggregation over states is unregistered, the tier_v2 1x1 mirror-member "
  "standing is OPEN (docs/54:406-411), and whether a confounded pair counts as 'measured' is "
  "unregistered — all entrant calls.")
A("")
A("## Unscored / pending cells — why, and what round 3 (array 20123293) can change")
A("")
A("| Pair | Why unscored now | Round-3 effect |")
A("|---|---|---|")
for p in pairs:
    if p["pair_status"] != "UNSCORED":
        continue
    r3 = " / ".join(f"{r['member'].replace(chr(124), chr(183))}: {r['round3']}" for r in p["round3_impact"]) or "—"
    extra = ""
    if f"{p['metal']}|{p['state'].lstrip('*')}|{p['coverage']}|off".replace("*","") in R1_ROWS or \
       (p['metal'], p['state'], p['coverage']) in [("Fe","*OOH","1x1"),("Mn","*OOH","2x1v")]:
        oq = p["off"]
        extra = (f" R1 quote (bank neither): parent {oq['parent_quoted']['energy_ry']} Ry, "
                 f"child {oq['child_quoted']['energy_ry']} Ry "
                 f"({oq['child_quoted']['delta_mev']:+.2f} meV) at {p['coverage']} coverage.")
    A(f"| {p['metal']} {p['state']} @{p['coverage']} | {p['why_unscored']}.{extra} | {r3} |")
A("")
A("Also pending but not a symmetry-pair member: Co ref @2x1v is PENDING-RETRY in array 20123293 "
  "(bares are references, not corners, docs/54:39) — it gates Co adsorption energies, not any "
  "mir-vs-off contrast. Ti has no 1x1 cells at all in the readout: every Ti 1x1 cell is a "
  "structural gap; round 3 contains no Ti decks.")
A("")
A("## Satisfaction (docs/43:1539-1541)")
A("")
A(artifact["satisfaction"]["statement"])
A("")
A("## Claim-scope branch (docs/43:1546-1554)")
A("")
A(artifact["claim_scope_branch"]["resolution"])
A("")
A("## Open questions carried from the registered record (not resolved here)")
A("")
for q in artifact["open_questions_registered_elsewhere"]:
    A(f"- {q}")
A("")
A("Generated 2026-08-24 by disclosed AI infrastructure from the readout JSON only; no existing "
  "file was modified. Machine-readable twin: `runs/s3/readout/p_symcov_2026-08-24.json`.")
A("")

out_md = os.path.join(ROOT, "runs", "s3", "readout", "p_symcov_2026-08-24.md")
with open(out_md, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))

# console summary
print("both-coverage metals (any-state reading):", both_now)
print("\nDD rows:")
for r in dd_rows:
    print(f"  {r['metal']:2s} {r['state']:5s} DD={r['dd_mev']}"
          if r["dd_mev"] is not None else
          f"  {r['metal']:2s} {r['state']:5s} excluded: {r['why_excluded']}")
print("\npair statuses:")
from collections import Counter
print(Counter(p["pair_status"] for p in pairs))
print("confounded pairs:", [(p['metal'], p['state'], p['coverage'], p['delta_sym_mev'], p['delta_M_uB'])
                            for p in pairs if p['pair_status'] == 'SCORED-EXCLUDED'])
print("Cr OOH 2x1v min-to-min:", by_ms[("Cr","*OOH")]["2x1v"]["delta_sym_mev"], "meV")
print("\nwrote:", out_json)
print("wrote:", out_md)
