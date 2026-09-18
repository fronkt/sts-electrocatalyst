"""Run exact P-DIVANIS analysis and independent verification.

From the repository root: PYTHONPATH=src python -m s2.divanis.run --out-dir results/s2_2026-09-18/divanis
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

from .curve import analyze, row_at, serializable
from .independent import verify
from .source import DEFAULT_SELECTION, REPO, load_population


def _format(q) -> str:
    return f"{float(q):.8g}" if isinstance(q, Fraction) else str(q)


def render_report(result: dict, rows) -> str:
    analysis = result["analysis"]
    iv = analysis["invariance"]
    lines = ["# P-DIVANIS exact correction-sensitivity readout", "",
             "This is an external-table arithmetic reconstruction, not a prediction of electrode performance. "
             "The primary result covers the full delta interval [0, 0.10] eV; no single correction value is elected.", "",
             f"The scored count ranges from **{iv['count_min']} to {iv['count_max']} of 38**. "
             f"Curve outcome(s): **{'; '.join(iv['curve_verdicts'])}**. "
             f"Count invariant: {iv['count_invariant']}; selected membership invariant: {iv['membership_invariant']}; "
             f"verdict invariant: {iv['verdict_invariant']}.", "",
             "Population: Man 26, Mom 11, Frydendal 1, across three articles. The historical 24-article label "
             "belongs to the entire ESI. Repeated material rows and the unlegended b suffix are retained. "
             "The lexical selection does not independently establish phase identity or stability.", "",
             "Corrections to the source adsorption-energy columns are OH +0.35 eV, O +0.05 eV, and "
             "OOH +(0.35 + delta) eV. The imposed cycle total is 4.92 eV. At each row's own scaling intercept c, "
             "the exact floor is max(c, 4.92-c)/2 - 1.23 V. Numerator requires eta <0.60 V and excess above "
             "that floor <=0.050 eV; denominator remains 38. Counts >=10 are HELD, <=3 FALSIFIED, and 4–9 "
             "SCORED — MIDDLE BAND / NOT MET.", "",
             "All source decimals, intersections and inequalities use rational arithmetic. The partition includes "
             "active CHE-step and floor-branch crossings, both predicate roots and fourth-step zero crossings. "
             "Boundary points are evaluated separately from open intervals; ties remain explicit. Decimal "
             "coordinates below are display values; exact fractions and all row values are in readout.json.", "",
             "| Delta region (eV) | Selected /38 | Man /26 | Mom /11 | Frydendal /1 | Curve outcome | Negative fourth steps |",
             "|---|---:|---:|---:|---:|---|---:|"]
    for cell in analysis["cells"]:
        reg = f"{{{_format(cell['delta'])}}}" if cell["kind"] == "point" else \
            f"({_format(cell['left'])}, {_format(cell['right'])})"
        agg = cell["aggregate"]
        nums = [agg["per_article"][str(a)]["count"] for a in (1, 7, 9)]
        lines.append(f"| {reg} | {agg['count']} | {nums[0]} | {nums[1]} | {nums[2]} | "
                     f"{agg['verdict']} | {len(agg['negative_dg4_row_ids'])} |")
    negative_ids = sorted({rid for c in analysis["cells"] for rid in c["aggregate"]["negative_dg4_row_ids"]})
    lookup = {row.row_id: row for row in rows}
    lines += ["", "## Negative fourth-step free energies", "",
              "These rows are retained in the denominator. A downhill fourth step under the imposed CHE cycle "
              "does not establish a physically impossible material or an incorrect paper. Their exact interval "
              "memberships, including equality cases, are in the JSON.", "",
              "| Source row | Article | Structure token | DeltaG4 at delta=0 (eV) | DeltaG4 at delta=0.10 (eV) |",
              "|---|---:|---|---:|---:|"]
    for rid in negative_ids:
        row = lookup[rid]
        vals = [row_at(row, d)["steps"][3] for d in (Fraction(0), Fraction("0.10"))]
        lines.append(f"| {rid} | {row.article_id} | {row.structure_token} | {_format(vals[0])} | {_format(vals[1])} |")
    guard = next(row for row in rows if row.source_line == 152)
    rec = row_at(guard, Fraction("0.05"))
    lines += ["", "## Historical arithmetic guard", "",
              f"At delta=0.05 solely to reproduce the registered source-row guard, {guard.row_id} reconstructs "
              f"eta={_format(rec['eta'])} V and DeltaG4={_format(rec['steps'][3])} eV. This external-table "
              "check neither selects a correction convention nor makes a Cr electrode-performance claim. "
              "The high-coverage attribution is external to the ESI row label.", "",
              "## Verification", "",
              f"Source SHA-256: `{result['inputs']['source_sha256']}`. Selection re-derived from raw text: 38/38 "
              "identities match. The independent raw-source verifier uses a separate parser and the "
              "absolute-value floor formula, and checks an over-partition containing even inactive branch roots.", "",
              f"Independent verification passed: {result['independent_verification']['passed']}; "
              f"{result['independent_verification']['exact_row_sample_comparisons']} exact row/sample comparisons "
              f"and {result['independent_verification']['independent_point_and_open_interval_probes']} independently "
              "constructed point/open-interval probes. Input/code hashes, all roots, active-step ties, negative-step "
              "sets and per-row threshold decisions are included in readout.json.", ""]
    return "\n".join(lines)


def run(selection_path: Path = DEFAULT_SELECTION, source_path: Path | None = None) -> tuple[dict, str]:
    rows, evidence = load_population(selection_path, source_path)
    analysis = analyze(rows)
    verification = verify(analysis, Path(evidence["source_path"]))
    codes = {str(p.relative_to(REPO)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(Path(__file__).parent.glob("*.py"))}
    result = dict(schema="divanis-exact-curve-v1", generated_utc=datetime.now(timezone.utc).isoformat(),
                  inputs=evidence, code_sha256=codes,
                  source_rows=[dict(row_id=r.row_id, source_line=r.source_line, article_id=r.article_id,
                                    structure_token=r.structure_token, energy_tokens=r.energy_tokens,
                                    source_row=r.source_row) for r in rows],
                  analysis=analysis, independent_verification=verification)
    return result, render_report(result, rows)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    result, report = run(args.selection, args.source)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    # Existing scientific results are never overwritten by a repeat invocation.
    targets = [args.out_dir / "readout.json", args.out_dir / "readout.md"]
    if any(p.exists() for p in targets):
        raise FileExistsError("readout already exists; use a new dated verification directory")
    targets[0].write_text(json.dumps(serializable(result), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    targets[1].write_text(report, encoding="utf-8")
    print(json.dumps(serializable(result["analysis"]["invariance"]), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
