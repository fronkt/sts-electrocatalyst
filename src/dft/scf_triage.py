#!/usr/bin/env python
"""SCF failure triage against the EFFECTIVE conv_thr (2026-08-25).

Round 3 was triaged by eye as "6 creepers at the 500-iteration ceiling" and the
registered remedy proposed was electron_maxstep 500 -> 1000-1500. This tool was
written to size that bump and instead refuted it.

The reason a hand triage goes wrong here: QE does NOT hold a `relax` run to the
conv_thr in the deck. With `upscale` unset (default 100) it TIGHTENS conv_thr as
the forces converge, down to a floor of conv_thr/upscale = 1e-8, printing

    new conv_thr            =       0.0000002791 Ry

at the end of each BFGS step. So "convergence NOT achieved" at 3.2e-7 with a
deck saying conv_thr = 1.0d-6 is not a contradiction -- the run was being held
to 2.79e-7 by then. `upscale` appears in ZERO decks in this repo, which makes it
an unregistered parameter that has governed every relax the project has run.

Classification is on PROGRESS RATE, not on flatness -- these runs jitter by
15-30% between iterations while making no progress at all, so a flatness test
misreads them. The decision-relevant question is only ever "would another 500
iterations have helped?", which is answered by how much the RUNNING MINIMUM
improved over the last stretch:

  UNREG_THR  min accuracy went below the deck's REGISTERED conv_thr but not
             below the upscale-tightened one -> the run met the threshold the
             project registered and was refused by a parameter it never set.
             Remedy: set `upscale`. More iterations are irrelevant.
  BRANCH     magnetization unstable over the tail (dM60) or the run never even
             reached 1e-3 -> electronic branch problem, A8.3 density retention.
  STALLED    running min improved < 2x over the last 150 iterations with stable
             magnetization -> self-consistency floor. The Broyden history is
             saturated; a RESTART FROM DENSITY with a fresh mixing space is the
             registered remedy (A8.4 rung (i)). More iterations buy nothing.
  SLOW       running min still improving > 2x per 150 iterations -> genuine
             creep. This is the ONLY class a maxstep increase can fix.

Usage:  python src/dft/scf_triage.py runs/s3/Co/s0_OH__2x1v_off.out ...
        python src/dft/scf_triage.py --all runs/s3
"""
import re, sys, pathlib, glob

ACC  = re.compile(r"estimated scf accuracy\s+<\s+([0-9.Ee+-]+)\s+Ry")
NEW  = re.compile(r"new conv_thr\s+=\s+([0-9.Ee+-]+)")
INIT = re.compile(r"scf convergence threshold\s+=\s+([0-9.Ee+-]+)")
MAG  = re.compile(r"total magnetization\s+=\s+([0-9.+-]+)\s+Bohr")


def blocks(txt):
    """Yield (index, body, effective_conv_thr) per SCF block, tracking the
    threshold QE actually enforced -- it is reset by `new conv_thr` at the end
    of each BFGS step, so block N runs under the value printed in block N-1."""
    m = INIT.search(txt)
    thr = float(m.group(1)) if m else None
    parts = re.split(r"(Self-consistent Calculation)", txt)
    i = 0
    for j, p in enumerate(parts):
        if p != "Self-consistent Calculation":
            continue
        i += 1
        body = parts[j + 1] if j + 1 < len(parts) else ""
        yield i, body, thr
        nc = NEW.findall(body)
        if nc:
            thr = float(nc[-1])


def classify(acc, mag, thr, nominal):
    """Return (kind, min, at, last). See module docstring for the taxonomy."""
    mn, last = min(acc), acc[-1]
    at = acc.index(mn) + 1
    dm = (max(mag[-60:]) - min(mag[-60:])) if len(mag) >= 60 else 0.0

    # Met the registered threshold; refused only by the tightened one.
    if nominal is not None and mn < nominal and (thr is None or mn >= thr):
        return "UNREG_THR", mn, at, last
    # Never got within three decades of anything, or magnetically unstable.
    if mn > 1e-3 or dm >= 0.5:
        return "BRANCH", mn, at, last
    # Progress rate of the RUNNING minimum over the last 150 iterations.
    if len(acc) > 200:
        before = min(acc[:-150])
        gain = before / mn if mn > 0 else float("inf")
        return ("SLOW" if gain > 2.0 else "STALLED"), mn, at, last
    return "STALLED", mn, at, last


def triage(path):
    txt = pathlib.Path(path).read_text(errors="ignore")
    m = INIT.search(txt)
    nominal = float(m.group(1)) if m else None
    out = []
    for i, body, thr in blocks(txt):
        if "convergence NOT achieved" not in body:
            continue
        acc = [float(x) for x in ACC.findall(body)]
        if not acc:
            continue
        mag = [float(x) for x in MAG.findall(body)]
        kind, mn, at, last = classify(acc, mag, thr, nominal)
        mspan = (max(mag[-60:]) - min(mag[-60:])) if len(mag) >= 60 else float("nan")
        out.append(dict(path=str(path), blk=i, thr=thr, n=len(acc), min=mn,
                        at=at, last=last, kind=kind, mspan=mspan))
    return out


def main(argv):
    if argv and argv[0] == "--all":
        root = argv[1] if len(argv) > 1 else "runs/s3"
        files = sorted(glob.glob(f"{root}/*/*.out"))
    else:
        files = argv
    rows = [r for f in files for r in triage(f)]
    if not rows:
        print("no non-convergent SCF blocks found")
        return 0
    print(f"{'deck':40s} {'blk':>3s} {'eff_thr':>9s} {'min_acc':>9s} {'@it':>4s} "
          f"{'last':>9s} {'n':>4s} {'dM60':>6s}  class")
    for r in rows:
        name = r["path"].replace("\\", "/").replace("runs/s3/", "")
        print(f"{name:40s} {r['blk']:3d} {r['thr']:9.2e} {r['min']:9.2e} {r['at']:4d} "
              f"{r['last']:9.2e} {r['n']:4d} {r['mspan']:6.2f}  {r['kind']}")
    print()
    for k in ("SLOW", "STALLED", "BRANCH", "UNREG_THR"):
        n = sum(1 for r in rows if r["kind"] == k)
        if n:
            print(f"  {k:9s} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
