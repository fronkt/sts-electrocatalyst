#!/usr/bin/env python3
"""A8.1 cell x symmetry non-additivity bins over the S3 crossed factorial.

Registered quantity (docs/43:1523-1525, DEPOSITED, adopted as proposed 2026-08-23):
    "a cell x symmetry interaction term is reported NON-ADDITIVE where
     |E(both) - E(cell) - E(sym) + E(neither)| exceeds 0.10 eV"
Corner mapping (docs/54:37-40, infrastructure, not registration):
    N = E(neither) = 1x1 mir ; S = E(sym) = 1x1 off ;
    C = E(cell)   = 2x1v mir ; B = E(both) = 2x1v off ; bares (ref) are not corners.
"At fixed basin" gloss: docs/54:20-21 (infrastructure).
Conversion: Ry -> eV x 13.605693 (project convention; meV = (E1-E2)*13605.693).
Parallel still-deposited ladder on the same algebraic quantity I (docs/43:169-176,
inherited verbatim by A6.2 at docs/43:1216-1220):
    |I| < 0.05 eV additive / 0.05-0.30 eV inconclusive / >= 0.30 eV not separable.
Whether A8.1 supersedes or coexists with that ladder is NOT registered -> both reported.
Magnetic CONFOUND check (docs/43:1566-1571, DEPOSITED): pair members differing
> 0.05 uB in converged TOTAL magnetisation are CONFOUNDED. Applied here to the
same-coverage symmetry edges (N-S, C-B) only, as docs/54:55-58, :147, :152 do;
cross-coverage edges compare cells with different atom counts and no registered
normalisation exists -> not evaluated, flagged.
PENDING rows (docs/55 R1, binding): Fe s0_OOH__1x1_off and Mn s0_OOH__2x1v_off
must be quoted parent AND child, neither banked -> both readings computed, row
tagged PENDING-RERELAX.

Inputs: runs/s3/readout/s3_readout_2026-08-24.json ONLY (plus docs-quoted constants
for informational alternate members named in that readout's notes / docs/54 rows).
Outputs (NEW files): runs/s3/readout/nonadditivity_2026-08-24.json / .md
No existing file is modified.
"""
import json, os, hashlib
from datetime import date

RY_TO_EV = 13.605693
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
READOUT = os.path.normpath(os.path.join(ROOT, "runs", "s3", "readout", "s3_readout_2026-08-24.json"))
OUT_JSON = os.path.normpath(os.path.join(ROOT, "runs", "s3", "readout", "nonadditivity_2026-08-24.json"))
OUT_MD = os.path.normpath(os.path.join(ROOT, "runs", "s3", "readout", "nonadditivity_2026-08-24.md"))

METALS = ["Cr", "Mn", "Fe", "Co", "Ni", "Ru", "Ir", "Ti"]
STATES = ["O", "OH", "OOH"]
CORNERS = {"N": ("1x1", "mir"), "S": ("1x1", "off"), "C": ("2x1v", "mir"), "B": ("2x1v", "off")}

# Informational alternate members named in the readout notes / docs/54 rows quoted in
# the state of record. NEVER binned; OPEN member questions are the entrant's call.
ALT_MEMBERS = {
    ("Cr", "OOH", "N"): {
        "energy_ry": -1636.47080322, "m": 11.8,
        "label": "ALT member: production runs/Cr_slab/s0_OOH.out (member identity OPEN, docs/54:150, :400-405)",
    },
    ("Ru", "OOH", "S"): {
        "energy_ry": -1715.02124065, "m": None,
        "label": "ALT member: oosh conformer, lowest banked (oosh-member question OPEN, docs/54:249, :422-424)",
    },
    ("Ir", "OOH", "S"): {
        "energy_ry": -1674.11459651, "m": None,
        "label": "ALT member: oosh conformer (oosh-member question OPEN, docs/54:264, :422-424)",
    },
}


def bin_a81(abs_ev):
    # docs/43:1523-1525 names only the NON-ADDITIVE side (>0.10 eV); the <=0.10 eV
    # outcome has NO deposited label -> reported as such, flagged.
    return "NON-ADDITIVE" if abs_ev > 0.10 else "<=0.10 eV (no deposited label)"


def bin_1a(abs_ev):
    # docs/43:171-176 (block 1A section 2 interaction bins, inherited by A6.2 docs/43:1216-1220)
    if abs_ev < 0.05:
        return "additive (<0.05)"
    if abs_ev < 0.30:
        return "inconclusive (0.05-0.30)"
    return "not separable (>=0.30)"


def main():
    with open(READOUT, encoding="utf-8") as f:
        readout = json.load(f)
    sha = hashlib.sha256(open(READOUT, "rb").read()).hexdigest()

    cells = {}
    for c in readout["cells"]:
        cells[(c["metal"], c["state"], c["coverage"], c["arm"])] = c

    rows = []
    for metal in METALS:
        for state in STATES:
            corners = {}
            for k, (cov, arm) in CORNERS.items():
                cell = cells.get((metal, state, cov, arm))
                if cell is None:
                    corners[k] = {"cell": f"{metal}|{state}|{cov}|{arm}", "status": "ABSENT (no such cell in readout)",
                                  "energy_ry": None, "file": None, "m": None, "notes": []}
                else:
                    corners[k] = {"cell": cell["cell"], "status": cell["status"],
                                  "energy_ry": cell.get("energy_of_record_ry"),
                                  "file": cell.get("energy_of_record_file"),
                                  "m": cell.get("total_magnetization_bohr"),
                                  "notes": list(cell.get("notes", [])),
                                  "parent_quoted": cell.get("parent_quoted"),
                                  "child_quoted": cell.get("child_quoted")}

            pending = [k for k, v in corners.items() if v["status"] == "PENDING-RERELAX"]
            missing = [k for k, v in corners.items() if v["energy_ry"] is None and v["status"] != "PENDING-RERELAX"]

            row = {"metal": metal, "state": state, "corners": corners,
                   "readings": [], "tags": [], "confound_edges": {}, "flags": []}

            # --- confound edges (same-coverage symmetry pairs only; docs/43:1566-1571 via docs/54:55-58)
            for edge, (a, b) in {"N-S (1x1 sym pair)": ("N", "S"), "C-B (2x1v sym pair)": ("C", "B")}.items():
                ma, mb = corners[a]["m"], corners[b]["m"]
                if ma is None or mb is None:
                    row["confound_edges"][edge] = {"delta_m_uB": None,
                        "verdict": "NOT EVALUABLE (a member has no M: nspin=1 row or pending cell)"}
                else:
                    dm = round(abs(ma - mb), 4)
                    row["confound_edges"][edge] = {"delta_m_uB": dm,
                        "verdict": "CONFOUNDED (>0.05 uB, docs/43:1566-1571)" if dm > 0.05 else "within 0.05 uB"}
            row["confound_edges"]["cross-coverage edges (N-C, S-B)"] = {"delta_m_uB": None,
                "verdict": "NOT EVALUATED — members have different atom counts; no registered raw-total-M "
                           "normalisation exists (spec ambiguity: A8.3 contrast enumeration unstated)"}

            # carry docs/54 CONFOUNDED designations found in corner rules (notes are echoed separately below)
            for k, v in corners.items():
                rule = str(cells.get((metal, state) + CORNERS[k], {}).get("rule") or "")
                if "CONFOUNDED" in rule:
                    row["flags"].append(f"corner {k}: docs/54 designates its pair CONFOUNDED — {rule.strip()[:200]}")
            if (metal, state) == ("Cr", "OOH"):
                row["flags"].append(
                    "docs/54:152 designated the 2x1v symmetry pair CONFOUNDED (Delta_sym 1.188 eV) with the "
                    "MIRROR SADDLE as member; docs/55 R3 (binding) since made the escape minimum the C-corner "
                    "record, and escape-vs-off DeltaM = 0.0 uB — whether the CONFOUNDED designation carries to "
                    "the post-R3 pair is an entrant call, NOT resolved here")

            # --- corner-standing flags carried from readout notes
            for k, v in corners.items():
                for n in v.get("notes", []):
                    if "OPEN" in n or "member" in n or "refused" in n:
                        row["flags"].append(f"corner {k}: {n}")
            if metal in ("Cr", "Mn"):
                row["flags"].append("Cr/Mn k-bridge (docs/54:41-43, infrastructure): 1x1<->2x1v corner comparisons "
                                    "carry an unapplied k-bridge correction; whether it cancels inside the double "
                                    "difference is an interpretation, not a registration — value computed uncorrected")

            def compute(e_n, e_s, e_c, e_b, label, informational=False):
                i_ry = e_b - e_c - e_s + e_n
                i_ev = i_ry * RY_TO_EV
                return {"label": label, "informational": informational,
                        "I_ry": round(i_ry, 8), "I_ev": round(i_ev, 6), "abs_I_ev": round(abs(i_ev), 6),
                        "a81_bin": bin_a81(abs(i_ev)), "block1A_bin": bin_1a(abs(i_ev))}

            if missing:
                row["tags"].append("NOT COMPUTABLE")
                row["missing_corners"] = {k: corners[k]["status"] for k in missing + pending}
                # informational note when a parent-only value exists on an UNVERIFIED corner
                for k in missing:
                    pq = corners[k].get("parent_quoted")
                    if pq and corners[k]["status"] == "UNVERIFIED":
                        row["flags"].append(f"corner {k} is UNVERIFIED but a parent value exists "
                                            f"({pq['file']} = {pq['energy_ry']} Ry); GATE-1 child pending — "
                                            f"no reading computed (docs/55 R2; not a docs/55-R1 dual-quote row)")
            elif pending:
                row["tags"].append("PENDING-RERELAX (docs/55 R1: quote parent AND child, bank neither)")
                pk = pending[0]
                e = {k: corners[k]["energy_ry"] for k in "NSCB"}
                par = corners[pk]["parent_quoted"]["energy_ry"]
                chi = corners[pk]["child_quoted"]["energy_ry"]
                for val, which, fil in ((par, "parent", corners[pk]["parent_quoted"]["file"]),
                                        (chi, "child", corners[pk]["child_quoted"]["file"])):
                    e2 = dict(e); e2[pk] = val
                    row["readings"].append(compute(e2["N"], e2["S"], e2["C"], e2["B"],
                        f"reading with {pk} = {which} ({fil} = {val} Ry) — docs/55 R1 dual quote, NOT banked"))
            else:
                e = {k: corners[k]["energy_ry"] for k in "NSCB"}
                row["readings"].append(compute(e["N"], e["S"], e["C"], e["B"], "energy-of-record"))
                # informational alternates for OPEN member questions
                for k in "NSCB":
                    alt = ALT_MEMBERS.get((metal, state, k))
                    if alt:
                        e2 = dict(e); e2[k] = alt["energy_ry"]
                        row["readings"].append(compute(e2["N"], e2["S"], e2["C"], e2["B"],
                            alt["label"], informational=True))
                        row["flags"].append(f"corner {k} member question OPEN — informational alternate computed, "
                                            f"never binned; the call is the entrant's")
            rows.append(row)

    # populations over energy-of-record readings only (definitive rows)
    pop = {"NON-ADDITIVE": [], "<=0.10 eV (no deposited label)": []}
    pop1a = {"additive (<0.05)": [], "inconclusive (0.05-0.30)": [], "not separable (>=0.30)": []}
    pend_pop, not_comp = [], []
    for r in rows:
        name = f"{r['metal']} *{r['state']}"
        if "NOT COMPUTABLE" in r["tags"]:
            not_comp.append(name)
        elif any("PENDING" in t for t in r["tags"]):
            bins = sorted({x["a81_bin"] for x in r["readings"]})
            pend_pop.append(f"{name} (both readings: {' / '.join(bins)})")
        else:
            rec = next(x for x in r["readings"] if not x["informational"])
            pop[rec["a81_bin"]].append(f"{name} ({rec['I_ev']:+.4f} eV)")
            pop1a[rec["block1A_bin"]].append(name)

    result = {
        "task": "A8.1 0.10 eV non-additivity bins over the S3 crossed factorial",
        "generated": str(date.today()),
        "input": {"file": os.path.relpath(READOUT, ROOT).replace("\\", "/"), "sha256": sha},
        "conversion_ry_to_ev": RY_TO_EV,
        "registered_rules": {
            "quantity_and_bin": "docs/43-prereg-week1-factorial.md:1523-1525 (DEPOSITED, 'THRESHOLD (adopted as "
                "proposed, 2026-08-23)'): NON-ADDITIVE where |E(both)-E(cell)-E(sym)+E(neither)| exceeds 0.10 eV; "
                "the <=0.10 eV side carries NO deposited label",
            "corner_mapping": "docs/54-s3-deck-matrix-2026-08-23.md:37-40 (INFRASTRUCTURE, not registration): "
                "N=1x1 mir, S=1x1 off, C=2x1v mir, B=2x1v off; bares (ref) are not corners; "
                "'at fixed basin' gloss docs/54:20-21",
            "algebraic_identity": "docs/43:169 — the double difference equals deltaE_sym(2x1v) - deltaE_sym(1x1), "
                "block 1A's I",
            "parallel_1a_ladder": "docs/43:171-176 (DEPOSITED, prior scheme; inherited verbatim by A6.2, "
                "docs/43:1216-1220): <0.05 additive / 0.05-0.30 inconclusive / >=0.30 not separable — "
                "supersession vs coexistence with A8.1 is NOT registered, both reported",
            "confound": "docs/43:1566-1571 (DEPOSITED): pair members differing >0.05 uB total magnetisation are "
                "CONFOUNDED, excluded from contrast statistics, reported separately; applied to same-coverage "
                "symmetry edges per docs/54:55-58; whether a CONFOUNDED pair voids the A8.1 row is UNSTATED",
            "pending_dual_quote": "docs/55 R1 (binding): Fe s0_OOH__1x1_off and Mn s0_OOH__2x1v_off quote parent "
                "AND child, bank neither as final",
            "energy_of_record": "docs/52 C9 (GATE-1 AGREE rows quote the CHILD) + docs/54 row->file matrix + "
                "docs/55 R3 (Cr *OOH 2x1v mir = escape minimum; mirror value is a SADDLE diagnostic)",
        },
        "rows": rows,
        "populations": {
            "a81_bins_definitive_rows": {k: sorted(v) for k, v in pop.items()},
            "block1A_bins_definitive_rows_parallel_reading": {k: sorted(v) for k, v in pop1a.items()},
            "pending_dual_readings": pend_pop,
            "not_computable": not_comp,
        },
    }

    with open(OUT_JSON, "x", encoding="utf-8") as f:  # "x": refuse to overwrite anything
        json.dump(result, f, indent=1, sort_keys=True)

    # ---------------- markdown ----------------
    lines = []
    lines.append("# A8.1 non-additivity bins — S3 crossed factorial (2026-08-24)")
    lines.append("")
    lines.append(f"Input: `{result['input']['file']}` (sha256 `{sha[:16]}...`). "
                 "Machine-readable twin: `nonadditivity_2026-08-24.json`. No existing file modified.")
    lines.append("")
    lines.append("## Registered rules applied (quoted authorities)")
    lines.append("")
    for k, v in result["registered_rules"].items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    lines.append("## Interaction table")
    lines.append("")
    lines.append("I = E(B) − E(C) − E(S) + E(N), Ry → eV ×13.605693. A8.1 bin: NON-ADDITIVE iff |I| > 0.10 eV "
                 "(docs/43:1523-1525). 1A ladder shown in parallel (docs/43:171-176) — coexistence unresolved, "
                 "flagged for entrant.")
    lines.append("")
    lines.append("| Metal | State | Reading | I (Ry) | I (eV) | A8.1 bin | 1A ladder | Row tag |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        name_written = False
        tag = "; ".join(r["tags"]) if r["tags"] else "definitive"
        if not r["readings"]:
            det = ", ".join(f"{k}:{v}" for k, v in r.get("missing_corners", {}).items())
            lines.append(f"| {r['metal']} | *{r['state']} | — | — | — | — | — | NOT COMPUTABLE ({det}) |")
            continue
        for x in r["readings"]:
            label = x["label"]
            if x["informational"]:
                label = "INFORMATIONAL — " + label
            mcol = r["metal"] if not name_written else ""
            scol = ("*" + r["state"]) if not name_written else ""
            lines.append(f"| {mcol} | {scol} "
                         f"| {label} | {x['I_ry']:+.8f} | {x['I_ev']:+.6f} | {x['a81_bin']} | {x['block1A_bin']} | {tag} |")
            name_written = True
    lines.append("")
    lines.append("## Bin populations (energy-of-record readings on definitive rows only)")
    lines.append("")
    lines.append(f"- **A8.1 NON-ADDITIVE (>0.10 eV)**: {len(pop['NON-ADDITIVE'])} — " + "; ".join(sorted(pop["NON-ADDITIVE"])))
    lines.append(f"- **A8.1 <=0.10 eV (no deposited label)**: {len(pop['<=0.10 eV (no deposited label)'])} — "
                 + "; ".join(sorted(pop["<=0.10 eV (no deposited label)"])))
    lines.append(f"- **1A ladder (parallel)**: additive {len(pop1a['additive (<0.05)'])} "
                 f"({', '.join(sorted(pop1a['additive (<0.05)']))}); inconclusive {len(pop1a['inconclusive (0.05-0.30)'])} "
                 f"({', '.join(sorted(pop1a['inconclusive (0.05-0.30)']))}); not separable {len(pop1a['not separable (>=0.30)'])}")
    lines.append(f"- **PENDING dual readings (docs/55 R1, neither banked)**: " + "; ".join(pend_pop))
    lines.append(f"- **Not computable**: {len(not_comp)} — " + ", ".join(not_comp))
    lines.append("")
    lines.append("## Per-row confound edges and flags")
    lines.append("")
    for r in rows:
        interesting = [e for e, v in r["confound_edges"].items() if v["verdict"].startswith("CONFOUNDED")]
        if not (interesting or r["flags"]):
            continue
        lines.append(f"### {r['metal']} *{r['state']}")
        for e, v in r["confound_edges"].items():
            dm = "n/a" if v["delta_m_uB"] is None else f"{v['delta_m_uB']} uB"
            lines.append(f"- edge {e}: ΔM = {dm} — {v['verdict']}")
        for fl in dict.fromkeys(r["flags"]):
            lines.append(f"- FLAG: {fl}")
        lines.append("")
    lines.append("## Standing ambiguities (NOT resolved here — entrant's calls)")
    lines.append("")
    for a in [
        "A8.1 vs the 1A three-bin ladder: supersession or coexistence is not registered; both binnings are printed.",
        "The <=0.10 eV outcome has no deposited label; the column header above is descriptive, not a registered bin name.",
        "E's definition (raw total energy vs per-adsorbate normalisation) is not registered; raw finals used as docs/54:18-21 does (infrastructure).",
        "Whether a CONFOUNDED symmetry edge voids the four-corner interaction row is unstated (A8.3 contrast enumeration).",
        "Cr/Mn k-bridge (docs/54:41-43): correction registered only as infrastructure; applied nowhere here.",
        "Which member's M enters the 0.05 uB comparison when parent and child moments differ is unstated; the readout's per-cell M was used as printed.",
        "Member-identity questions (Cr *OOH 1x1 mir; Ru/Ir *OOH oosh) remain OPEN; informational alternates are computed but never binned.",
    ]:
        lines.append(f"- {a}")
    lines.append("")
    with open(OUT_MD, "x", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("WROTE", OUT_JSON)
    print("WROTE", OUT_MD)
    # console summary
    for r in rows:
        for x in r["readings"]:
            print(f"{r['metal']:2s} {r['state']:3s} {x['I_ev']:+9.4f} eV  {x['a81_bin']:<30s} {x['block1A_bin']:<26s} "
                  f"{'INFO' if x['informational'] else ('PEND' if any('PENDING' in t for t in r['tags']) else 'REC ')}  {x['label'][:70]}")
        if not r["readings"]:
            print(f"{r['metal']:2s} {r['state']:3s}   NOT COMPUTABLE  missing={r.get('missing_corners')}")


if __name__ == "__main__":
    main()
