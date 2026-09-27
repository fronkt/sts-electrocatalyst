"""Stamps rows written by in-session agents with "_screener", the field api_screen.py puts on API rows.

  python agent_stamp.py --model claude-sonnet-5 pass_1/batches/P1_0348.out.jsonl [...]

Adds _screener = {method: "agent", model, at} to every row that has none; "at" is the output file's
modification time (UTC), the moment the agent finished writing it.  current_state.py and v5_read.py date
a row by _screener.at (instruction v4 from 2026-09-27 07:50Z, v5 from 10:34:50Z); agent rows written
before the 2026-09-26 route change carry no stamp and are all v3 reads.  Rows are otherwise unchanged.
A file that fails ft_screen.check is left alone.
"""
import argparse
import datetime as dt
import json
import pathlib

from ft_screen import check


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("out", nargs="+")
    a = p.parse_args()
    for o in map(pathlib.Path, a.out):
        probs = check(o.with_name(o.name.replace(".out.", ".in.")), o)
        if probs:
            print(o.name, "NOT stamped:", probs)
            continue
        at = dt.datetime.fromtimestamp(o.stat().st_mtime, dt.timezone.utc).isoformat()
        rows = [json.loads(l) for l in open(o, encoding="utf-8") if l.strip()]
        n = 0
        for r in rows:
            if "_screener" not in r:
                r["_screener"] = dict(method="agent", model=a.model, at=at)
                n += 1
        o.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8", newline="\n")
        print(o.name, n, "rows stamped", at)


if __name__ == "__main__":
    main()
