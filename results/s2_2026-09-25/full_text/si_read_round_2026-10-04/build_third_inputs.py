"""Build visual-completion third-read inputs for the 2026-10-04 SI round.

Each third-read line = the pass-1 input line + `why` + the two pass rows
(`pass1`, `pass2`) + `main_visual_root` (main-text page renders that neither
pass had). Write-once: refuses to overwrite an existing output.
"""
import glob
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
FULL = os.path.dirname(ROOT)
CRIT = ("E1", "E2", "E3", "E4", "E5", "E6")


def rows(pattern):
    out = {}
    for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                out[row["screen_id"]] = row
    return out


def why(sid, p1, p2):
    reasons = []
    if p1["disposition"] != p2["disposition"]:
        reasons.append("Pass disagreement on disposition: pass1 {} vs pass2 {}.".format(
            p1["disposition"], p2["disposition"]))
    diffs = [k for k in CRIT if p1[k]["v"] != p2[k]["v"]]
    if diffs:
        reasons.append("Pass disagreement on " + ", ".join(
            "{} ({} vs {})".format(k, p1[k]["v"], p2[k]["v"]) for k in diffs) + ".")
    reasons.append(
        "Visual completion: neither pass had main-text page images (both passes judged "
        "main-text figures from captions/text only). main_visual_root now holds every "
        "main-text page. Inspect the main-text figures and tables that bear on any "
        "criterion, especially any UNCLEAR criterion and any E6 NO, and judge the paper "
        "again from the full evidence.")
    return " ".join(reasons)


def main():
    third = os.path.join(ROOT, "third", "batches")
    os.makedirs(third, exist_ok=True)
    p1_rows = rows("pass_1/batches/*.out.jsonl")
    p2_rows = rows("pass_2/batches/*.out.jsonl")
    made = []
    for inp in sorted(glob.glob(os.path.join(ROOT, "pass_1", "batches", "SI1_*.in.jsonl"))):
        batch = os.path.basename(inp)[len("SI1_"):-len(".in.jsonl")]
        dest = os.path.join(third, "T3_{}.in.jsonl".format(batch))
        if os.path.exists(dest):
            raise SystemExit("refusing to overwrite " + dest)
        lines = []
        with open(inp, encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                sid = row["screen_id"]
                mv = os.path.join("si_read_round_2026-10-04", "main_visual", sid)
                if not os.path.isdir(os.path.join(FULL, mv)):
                    raise SystemExit("missing main_visual for " + sid)
                row["why"] = why(sid, p1_rows[sid], p2_rows[sid])
                row["pass1"] = p1_rows[sid]
                row["pass2"] = p2_rows[sid]
                row["main_visual_root"] = mv.replace(os.sep, "/")
                lines.append(json.dumps(row, ensure_ascii=False))
        with open(dest, "x", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")
        made.append((dest, len(lines), hashlib.sha256(open(dest, "rb").read()).hexdigest()))
    for dest, n, sha in made:
        print(os.path.relpath(dest, FULL), n, sha[:16])


if __name__ == "__main__":
    main()
