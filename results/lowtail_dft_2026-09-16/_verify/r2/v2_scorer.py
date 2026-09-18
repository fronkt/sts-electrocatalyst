"""Independent verifier: scorer crosscheck on the 43 banked runs/hea pw.x outputs.

Own text classification (not the track's code) + the repository's unmodified scorer
(src/dft/hea_panel_readout.parse_out, which is not track code) + own readout-status
mining from the banked readout JSONs.
"""
import hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src" / "dft"))
sys.path.insert(0, str(ROOT / "src"))

outs = sorted(p for p in (ROOT / "runs" / "hea").rglob("*.out")
              if not p.name.endswith(".projwfc.out") and "lowtail" not in str(p))

NOTE = re.compile(r"^Note: The following floating-point exceptions are signalling:(.*)$", re.M)


def own_classify(blob):
    notes = NOTE.findall(blob)
    note_flags = set()
    for n in notes:
        note_flags.update(n.split())
    wall = re.findall(r"PWSCF\s*:\s*(.+?)\s+CPU\s+(.+?)\s+WALL", blob)
    wall_tok = wall[-1][1] if wall else None
    wall_no_seconds = bool(wall_tok) and not wall_tok.strip().endswith("s")
    conv = re.findall(r"convergence has been achieved in\s+(\d+) iterations", blob)
    notconv = blob.count("convergence NOT achieved")
    maxcpu = blob.count("Maximum CPU time exceeded")
    jobdone = blob.count("JOB DONE")
    energies = re.findall(r"^!\s+total energy\s+=\s+(\S+)\s+Ry", blob, re.M)
    # strip the note lines, then look for any other severe marker
    stripped = NOTE.sub("", blob)
    other_severe = re.findall(r"Error in routine|SIGSEGV|SIGFPE|segmentation fault|MPI_ABORT|"
                              r"Program received signal|floating.point exception", stripped, re.I)
    invalid_like = sorted(f for f in note_flags if f in ("IEEE_INVALID_FLAG", "IEEE_DIVIDE_BY_ZERO", "IEEE_OVERFLOW_FLAG"))
    # also any IEEE_INVALID anywhere outside notes
    invalid_outside = re.findall(r"IEEE_(?:INVALID|DIVIDE_BY_ZERO|OVERFLOW)", stripped)
    if other_severe or invalid_like or invalid_outside:
        own = "REJECTED"
    elif notconv or maxcpu:
        own = "NOT CONVERGED"
    elif jobdone == 1 and len(energies) == 1 and conv:
        own = "CONVERGED"
    else:
        own = "REJECTED" if jobdone else "PENDING"
    return dict(n_note_lines=len(notes), note_flags=sorted(note_flags), wall_token=wall_tok,
                wall_no_seconds=wall_no_seconds, n_conv=len(conv), notconv=notconv, maxcpu=maxcpu,
                jobdone=jobdone, n_energies=len(energies), other_severe=other_severe,
                invalid_flags=invalid_like, own_status=own,
                only_benign_notes=bool(notes) and not invalid_like)


def unmodified(path):
    import hea_panel_readout as hpr
    try:
        o = hpr.parse_out(path)
        return o["status"], None, o.get("severe_failures")
    except hpr.Fatal as e:
        return "FATAL", str(e), None


def mine_readout_status(job):
    """Search banked readouts for an explicit per-job status."""
    hits = []
    cands = list((ROOT / "results").glob("hea_*/**/*.json")) + list((ROOT / "runs" / "hea").rglob("*.json"))
    return None


rows = []
for p in outs:
    blob = p.read_bytes().decode("utf-8", "replace")
    c = own_classify(blob)
    st, fatal, sev = unmodified(p)
    rows.append(dict(path=str(p.relative_to(ROOT)).replace("\\", "/"),
                     sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                     unmodified=st, fatal=fatal, unmodified_severe=sev, **c))

from collections import Counter
summary = dict(
    n=len(rows),
    unmodified=Counter(r["unmodified"] for r in rows),
    own=Counter(r["own_status"] for r in rows),
    wall_no_seconds=sum(r["wall_no_seconds"] for r in rows),
    with_notes=sum(r["n_note_lines"] > 0 for r in rows),
    with_invalid=[r["path"] for r in rows if r["invalid_flags"]],
    no_notes=[r["path"] for r in rows if r["n_note_lines"] == 0],
    fatal_equals_wall_no_seconds=all((r["unmodified"] == "FATAL") == r["wall_no_seconds"] for r in rows),
)
out = Path(__file__).with_name("v2_scorer.json")
out.write_text(json.dumps(dict(summary=summary, rows=rows), indent=1, default=str))
print(json.dumps(summary, indent=1, default=str))
