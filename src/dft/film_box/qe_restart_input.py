#!/usr/bin/env python3
"""Write a pw.x relax input that restarts from the last geometry printed in an output.

  python3 qe_restart_input.py IN.in OUT.out NEW.in NEW_PREFIX [--conv-thr 5.0d-6]

Copies IN.in, replaces its ATOMIC_POSITIONS block with the last block in OUT.out (fixed atoms
keep 0 0 0, free atoms get 1 1 1), sets prefix and, optionally, conv_thr. Stdlib only, so it
runs on the box.
"""
import re
import sys


def last_positions(out_text, nat):
    starts = [m.end() for m in re.finditer(r"ATOMIC_POSITIONS \(angstrom\)\n", out_text)]
    if not starts:
        raise SystemExit("no ATOMIC_POSITIONS block in the output")
    rows = out_text[starts[-1]:].split("\n")[:nat]
    out = []
    for r in rows:
        t = r.split()
        if len(t) not in (4, 7):
            raise SystemExit(f"unexpected position line: {r!r}")
        flags = " ".join(t[4:7]) if len(t) == 7 else "1 1 1"
        out.append(f"  {t[0]}  {float(t[1]):.8f}  {float(t[2]):.8f}  {float(t[3]):.8f}  {flags}")
    return out


def main():
    args = sys.argv[1:]
    conv = None
    if "--conv-thr" in args:
        i = args.index("--conv-thr"); conv = args[i + 1]; del args[i:i + 2]
    src_in, src_out, dst_in, prefix = args
    text = open(src_in).read()
    nat = int(re.search(r"nat\s*=\s*(\d+)", text).group(1))
    pos = last_positions(open(src_out, errors="replace").read(), nat)
    head, tail = text.split("ATOMIC_POSITIONS angstrom\n", 1)
    tail_lines = tail.split("\n")
    text = head + "ATOMIC_POSITIONS angstrom\n" + "\n".join(pos) + "\n" + "\n".join(tail_lines[nat:])
    text = re.sub(r"prefix = '[^']*'", f"prefix = '{prefix}'", text, count=1)
    if conv:
        text, n = re.subn(r"(?m)^(\s*)conv_thr = \S+", r"\g<1>conv_thr = " + conv, text, count=1)
        if n != 1:
            raise SystemExit("no conv_thr line at the start of a line")
    open(dst_in, "w", newline="\n").write(text)
    print(f"{dst_in}: {nat} atoms from the last block of {src_out}; prefix {prefix}; conv_thr {conv or 'unchanged'}")


if __name__ == "__main__":
    main()
