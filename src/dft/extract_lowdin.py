#!/usr/bin/env python3
"""Committed Lowdin extractor + validator (docs/61 SA11.8 item 4 / decision item 12).

Reproduces, byte-for-byte, the recipe behind every banked `runs/**/<job>.lowdin.txt`
(265 precedents at build time):

    line 1:   `# Lowdin section of <job>.projwfc.out (full projwfc output retained
              on Anvil beside the deck)`
    line 2..EOF: a VERBATIM byte-for-byte copy of the raw projwfc stdout from the
              start of its column-0 `Lowdin Charges: ` line through EOF -- including
              the Spilling Parameter, the PROJWFC timing line, the JOB DONE banner,
              and the trailing per-rank IEEE_UNDERFLOW/IEEE_DENORMAL Note lines
              (stderr is merged into stdout by `> "$pout" 2>&1`, anvil/46_a0.slurm).

i.e. functionally:
    { echo "# Lowdin section of ${job}.projwfc.out (full projwfc output retained on Anvil beside the deck)";
      sed -n '/^Lowdin Charges:/,$p' ${job}.projwfc.out; } > ${job}.lowdin.txt

The extractor is SHAPE-AGNOSTIC (verbatim copy); only the validator is shape-aware.
Both banked shapes exist: nspin=1 (3 rows/atom, repeated `total charge`) and nspin=2
(8 rows/atom: summary + 3x spin up + 3x spin down + polarization). The nspin=2
artifact format is fixed by 169 banked precedents -- nothing here invents a format.

Byte handling is mandatory: the raw file is read in binary, the tail is copied with
no decode/re-encode, output is written in binary ('wb'); text mode is never used
(CRLF translation on Windows would corrupt the artifact).

Evidence-safety rail: an existing target is REFUSED (exit 3) and NO overwrite flag
exists at all -- re-extraction over a banked file must be impossible from this tool.
Output is written to a temp file in the target's directory, fully validated, then
atomically os.replace()d into place; a half-written or invalid artifact is never
left beside a deck.

PROPOSED conventions (entrant may amend; nothing here is an election):
  * TOL = 5e-4 absolute. All values print at 4 dp, so a k-term sum accumulates a
    worst-case (k+1)*5e-5 rounding error; the largest k here is 5 (d suborbitals)
    -> 3e-4. Measured example of a real 1e-4 discrepancy: Ru sp2m050 Atom #1
    su+sd = 2.3812 vs s = 2.3813. This is an engineering rounding bound, not a
    scientific threshold, but it is still a number the entrant may tighten.
  * Header wording is kept byte-identical to the 265 banked precedents, including
    "retained on Anvil beside the deck", even for in-repo raws (it stays literally
    true for Anvil-side extraction, and the banked precedents fix the template).
    Changing the wording is an entrant convention election -- flagged, not decided.

EXPLICIT NON-CHECK: Lowdin totals need NOT equal pw.x totmag/absmag or nelec --
Lowdin projection loses the spilled charge (Spilling Parameter 0.0033-0.0043 in
this campaign, ~0.5 e on a ~150 e cell). Any comparison against pw.x quantities is
a sanity band for the human log, not an equality check, and this tool performs no
such comparison; --report merely prints the sum of total charges and (nspin=2) the
sum of per-atom polarizations so a human can eyeball them against the SCF output.
NOTHING derived is ever written into a .lowdin.txt; the artifact is the verbatim
QE text and nothing else. Derived per-atom up+down / up-down values appear only in
the --report stream, explicitly headed `DERIVED (not part of the artifact)`.

CLI:
  EXTRACT (default):
    python src/dft/extract_lowdin.py RAW.projwfc.out [RAW2.projwfc.out ...]
        [--out FILE]     single input only; explicit target (scratch/testing)
        [--out-dir DIR]  write <job>.lowdin.txt into DIR instead of beside input
        [--stdout]       single input only; print artifact bytes, write nothing
  CHECK:
    python src/dft/extract_lowdin.py --check FILE.lowdin.txt [FILE2 ...] [--report]

Exit codes:
  0  success (all inputs)
  1  no Lowdin block / ambiguous (>=2 blocks) / CR byte in tail / --check failure
  2  truncated or failed projwfc (no JOB DONE after the Lowdin block; mirrors the
     anvil/46_a0.slurm JOB DONE gate)
  3  target already exists (refused; no overwrite flag exists)
  4  input filename does not end in `.projwfc.out` (header template requires it)
  5  extraction produced bytes that fail the validator (temp deleted, no artifact)
  64 CLI usage error

Stdlib only; runs on the Anvil login node (python3) and locally (Python 3.12).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile

# ---------------------------------------------------------------------------
# Constants (formats fixed by the 265 banked precedents)
# ---------------------------------------------------------------------------

# PROPOSED tolerance -- see module docstring for the (k+1)*5e-5 derivation.
TOL = 5e-4

RAW_SUFFIX = ".projwfc.out"
ART_SUFFIX = ".lowdin.txt"

HEADER_TEMPLATE = (
    "# Lowdin section of {job}.projwfc.out "
    "(full projwfc output retained on Anvil beside the deck)"
)
HEADER_RE = re.compile(
    r"^# Lowdin section of (?P<job>.+)\.projwfc\.out "
    r"\(full projwfc output retained on Anvil beside the deck\)$"
)

LOWDIN_MARK = b"Lowdin Charges"          # line-start needle for block counting
LOWDIN_LINE = "Lowdin Charges: "         # line 2 of every artifact, exactly

ATOM_RE = re.compile(r"^     Atom #( *\d+): total charge =( *-?\d+\.\d+), (.*)$")
UP_RE = re.compile(r"^ {17}spin up +=( *-?\d+\.\d+), (.*)$")
DOWN_RE = re.compile(r"^ {17}spin down +=( *-?\d+\.\d+), (.*)$")
POL_RE = re.compile(r"^ {17}polarization +=( *-?\d+\.\d+), (.*)$")
# Conditional block-level total polarization: QE PROJWFC v.7.5 prints NO such row
# (verified: the last atom's polarization row is immediately followed by Spilling
# Parameter), so this pattern is dormant on all current data. Implemented as a
# conditional check, never required.
BLOCKPOL_RE = re.compile(r"^\s*[Tt]otal polarization\s*[=:]\s*(-?\d+\.\d+)")

SPILL_RE = re.compile(r"^     Spilling Parameter:\s+([0-9.]+)$")
PROJWFC_RE = re.compile(r"^     PROJWFC\s+:.*WALL\s*$")
TERM_RE = re.compile(r"^   This run was terminated on:")
BANNER = "=" + "-" * 78 + "="
JOB_DONE_LINE = "   JOB DONE."
NOTE_PREFIX = "Note: The following floating-point exceptions are signalling:"

KV_RE = re.compile(r"^([A-Za-z0-9^_\-]+?) *= *(-?\d+\.\d+)$")

# Channels seen in this campaign are s/p/d only (no banked file has an f channel);
# the parser must not hard-fail on one, but the validator WARNS.
KNOWN_CHANNELS = ("s", "p", "d")
EXPECTED_SUBS = {
    "s": [],
    "p": ["pz", "px", "py"],
    "d": ["dz2", "dxz", "dyz", "dx2-y2", "dxy"],
}


class Result:
    """Outcome of validating one artifact's bytes."""

    def __init__(self):
        self.failures = []   # list of str, each "line N: <what failed>"
        self.warnings = []   # list of str
        self.info = {"nspin_shape": None, "atoms": 0, "spilling": None, "notes": 0}
        self.atoms = []      # parsed per-atom records (floats), for --report/tests

    @property
    def ok(self):
        return not self.failures

    def fail(self, lineno, msg):
        self.failures.append("line %d: %s" % (lineno, msg))

    def warn(self, lineno, msg):
        self.warnings.append("line %d: %s" % (lineno, msg))


# ---------------------------------------------------------------------------
# Field-level parsing helpers
# ---------------------------------------------------------------------------

def _parse_fields(rest, lineno, res):
    """Parse the `k = v, k= v, ` remainder of a data line into [(key, float)].

    Every data line ends with `, ` (comma-space) before the newline; fields are
    `, `-separated; channel keys use ` = `, suborbital keys `=` with no space
    before it -- both parsed by one generic pattern. Returns None on failure.
    """
    if not rest.endswith(", "):
        res.fail(lineno, "data line does not end with ', ': %r" % rest[-20:])
        return None
    items = []
    for tok in rest[:-2].split(", "):
        m = KV_RE.match(tok)
        if m is None:
            res.fail(lineno, "unparseable field %r" % tok)
            return None
        items.append((m.group(1), float(m.group(2))))
    if not items:
        res.fail(lineno, "data line carries no key=value fields")
        return None
    return items


def _check_suborbitals(channel, value, subs, lineno, res, where):
    """Check suborbital naming/order and sum(subs) == channel value (TOL)."""
    names = [k for k, _ in subs]
    if channel in EXPECTED_SUBS:
        if names != EXPECTED_SUBS[channel]:
            res.fail(lineno, "%s: channel %s suborbitals %r != expected %r"
                     % (where, channel, names, EXPECTED_SUBS[channel]))
            return
    elif names:
        res.warn(lineno, "%s: unexpected channel %r with suborbitals %r "
                         "(no banked file has one)" % (where, channel, names))
    if subs:
        total = sum(v for _, v in subs)
        if abs(total - value) > TOL:
            res.fail(lineno, "%s: sum of %s suborbitals %.4f != %s = %.4f "
                             "(tol %g)" % (where, channel, total, channel,
                                           value, TOL))


def _channels_only(items, lineno, res, where):
    """Assert a row's fields are bare channels (no suborbital names)."""
    sub_names = {n for subs in EXPECTED_SUBS.values() for n in subs}
    for k, _ in items:
        if k in sub_names:
            res.fail(lineno, "%s: suborbital %r not allowed on this row" % (where, k))
    return [k for k, _ in items]


# ---------------------------------------------------------------------------
# Atom-region parsing (shape-aware)
# ---------------------------------------------------------------------------

def _parse_region(lines, start, spill_idx, res):
    """Classify and group the atom rows lines[start:spill_idx] (0-based)."""
    rows = []  # (lineno_1based, kind, raw_val_str, items)
    block_pol = None
    for i in range(start, spill_idx):
        line = lines[i]
        lineno = i + 1
        for kind, rx in (("ATOM", ATOM_RE), ("UP", UP_RE),
                         ("DOWN", DOWN_RE), ("POL", POL_RE)):
            m = rx.match(line)
            if m:
                break
        else:
            m2 = BLOCKPOL_RE.match(line)
            if m2:
                block_pol = (lineno, float(m2.group(1)))
                continue
            res.fail(lineno, "unexpected line in Lowdin atom region: %r" % line[:60])
            return None, None, block_pol
        if kind == "ATOM":
            idx_str, val_str, rest = m.group(1), m.group(2), m.group(3)
            items = _parse_fields(rest, lineno, res)
            if items is None:
                return None, None, block_pol
            rows.append((lineno, kind, int(idx_str), val_str, items))
        else:
            val_str, rest = m.group(1), m.group(2)
            items = _parse_fields(rest, lineno, res)
            if items is None:
                return None, None, block_pol
            rows.append((lineno, kind, None, val_str, items))

    nspin2 = any(r[1] in ("UP", "DOWN", "POL") for r in rows)
    res.info["nspin_shape"] = 2 if nspin2 else 1

    # Group rows into atoms.
    groups = []  # list of list-of-rows
    for row in rows:
        if row[1] == "ATOM":
            if nspin2:
                groups.append([row])
            else:
                if groups and groups[-1][0][2] == row[2]:
                    groups[-1].append(row)
                else:
                    groups.append([row])
        else:
            if not groups:
                res.fail(row[0], "spin row before any Atom row")
                return None, None, block_pol
            groups[-1].append(row)
    return groups, nspin2, block_pol


def _validate_atoms(groups, nspin2, res):
    """Per-atom internal-consistency checks; fills res.atoms."""
    indices = []
    for g in groups:
        head = g[0]
        lineno0, _, idx, tot_str, head_items = head
        indices.append(idx)
        if nspin2:
            _validate_atom_nspin2(g, res)
        else:
            _validate_atom_nspin1(g, res)
    n = len(groups)
    if n < 1:
        res.fail(4, "no atoms parsed (N >= 1 required)")
    elif indices != list(range(1, n + 1)):
        res.fail(groups[0][0][0], "atom indices not contiguous 1..%d: %r"
                 % (n, indices[:12]))
    res.info["atoms"] = n


def _validate_atom_nspin1(g, res):
    """nspin=1 atom: rows repeat `total charge`; one channel (+subs) per row."""
    lineno0, _, idx, tot_str, _ = g[0]
    where = "atom %d" % idx
    channels = []  # (name, value, subs)
    for lineno, kind, ridx, val_str, items in g:
        if kind != "ATOM":
            res.fail(lineno, "%s: spin row in an nspin=1-shaped file" % where)
            return
        if val_str != tot_str:
            res.fail(lineno, "%s: repeated 'total charge' string %r != %r "
                             "(must be byte-identical)" % (where, val_str, tot_str))
        ch, chval = items[0]
        subs = items[1:]
        if ch in [c[0] for c in channels]:
            res.fail(lineno, "%s: duplicate channel %r" % (where, ch))
        _check_suborbitals(ch, chval, subs, lineno, res, where)
        channels.append((ch, chval, subs))
    names = [c[0] for c in channels]
    if names != list(KNOWN_CHANNELS):
        res.warn(lineno0, "%s: channel sequence %r != %r"
                 % (where, names, list(KNOWN_CHANNELS)))
    total = float(tot_str)
    chsum = sum(c[1] for c in channels)
    if abs(chsum - total) > TOL:
        res.fail(lineno0, "%s: s+p+d... = %.4f != total charge %.4f (tol %g)"
                 % (where, chsum, total, TOL))
    res.atoms.append({
        "index": idx, "total": total,
        "channels": [(c[0], c[1]) for c in channels],
        "suborbitals": {c[0]: list(c[2]) for c in channels},
    })


def _validate_atom_nspin2(g, res):
    """nspin=2 atom: summary + k spin-up + k spin-down + 1 polarization row."""
    lineno0, _, idx, tot_str, summary_items = g[0]
    where = "atom %d" % idx
    summary_ch = _channels_only(summary_items, lineno0, res, where + " summary")
    ups, downs, pols = [], [], []
    phase = "UP"
    order = {"UP": 0, "DOWN": 1, "POL": 2}
    seen_phase = 0
    for lineno, kind, ridx, val_str, items in g[1:]:
        if kind == "ATOM":  # unreachable by grouping; defensive
            res.fail(lineno, "%s: unexpected Atom row inside atom block" % where)
            return
        if order[kind] < seen_phase:
            res.fail(lineno, "%s: %s row out of order (expected all spin up, "
                             "then all spin down, then polarization)"
                     % (where, kind.lower()))
            return
        seen_phase = order[kind]
        {"UP": ups, "DOWN": downs, "POL": pols}[kind].append(
            (lineno, val_str, items))
    if not ups or not downs or not pols:
        res.fail(lineno0, "%s: incomplete row set (%d spin up, %d spin down, "
                          "%d polarization; need k, k, 1)"
                 % (where, len(ups), len(downs), len(pols)))
        return
    if len(pols) != 1:
        res.fail(pols[1][0], "%s: %d polarization rows (need exactly 1)"
                 % (where, len(pols)))
        return
    if len(ups) != len(downs):
        res.fail(lineno0, "%s: %d spin-up rows != %d spin-down rows"
                 % (where, len(ups), len(downs)))
        return

    # Byte-identity of the repeated totals.
    u_str = ups[0][1]
    for lineno, val_str, _ in ups[1:]:
        if val_str != u_str:
            res.fail(lineno, "%s: repeated 'spin up' string %r != %r "
                             "(must be byte-identical)" % (where, val_str, u_str))
    w_str = downs[0][1]
    for lineno, val_str, _ in downs[1:]:
        if val_str != w_str:
            res.fail(lineno, "%s: repeated 'spin down' string %r != %r "
                             "(must be byte-identical)" % (where, val_str, w_str))

    def spin_channels(rows, label):
        out = []
        for lineno, _, items in rows:
            ch, chval = items[0]
            subs = items[1:]
            _check_suborbitals(ch, chval, subs, lineno, res,
                               "%s %s" % (where, label))
            out.append((ch, chval, subs))
        names = [c[0] for c in out]
        if names != summary_ch:
            res.fail(rows[0][0], "%s: %s channel sequence %r != summary %r"
                     % (where, label, names, summary_ch))
        return out

    up_ch = spin_channels(ups, "spin up")
    down_ch = spin_channels(downs, "spin down")

    pol_lineno, z_str, pol_items = pols[0]
    pol_ch_names = _channels_only(pol_items, pol_lineno, res,
                                  where + " polarization")
    if pol_ch_names != summary_ch:
        res.fail(pol_lineno, "%s: polarization channel sequence %r != summary %r"
                 % (where, pol_ch_names, summary_ch))

    total, u, w, z = float(tot_str), float(u_str), float(w_str), float(z_str)
    if [k for k, _ in summary_items] != list(KNOWN_CHANNELS):
        res.warn(lineno0, "%s: channel sequence %r != %r"
                 % (where, summary_ch, list(KNOWN_CHANNELS)))

    # (a) summary channels sum to total charge
    ssum = sum(v for _, v in summary_items)
    if abs(ssum - total) > TOL:
        res.fail(lineno0, "%s: summary s+p+d... = %.4f != total charge %.4f "
                          "(tol %g)" % (where, ssum, total, TOL))
    # (b) per-spin channel sums
    usum = sum(c[1] for c in up_ch)
    if abs(usum - u) > TOL:
        res.fail(ups[0][0], "%s: spin-up channel sum %.4f != spin up total %.4f "
                            "(tol %g)" % (where, usum, u, TOL))
    wsum = sum(c[1] for c in down_ch)
    if abs(wsum - w) > TOL:
        res.fail(downs[0][0], "%s: spin-down channel sum %.4f != spin down "
                              "total %.4f (tol %g)" % (where, wsum, w, TOL))
    # (c) suborbital sums already checked inside spin_channels
    # (d) U + W == T
    if abs(u + w - total) > TOL:
        res.fail(lineno0, "%s: spin up %.4f + spin down %.4f = %.4f != total "
                          "charge %.4f (tol %g)" % (where, u, w, u + w, total, TOL))
    # (e) polarization identities
    if abs(z - (u - w)) > TOL:
        res.fail(pol_lineno, "%s: polarization %.4f != up-down %.4f (tol %g)"
                 % (where, z, u - w, TOL))
    up_map = {c[0]: c[1] for c in up_ch}
    down_map = {c[0]: c[1] for c in down_ch}
    zsum = 0.0
    for ch, zval in pol_items:
        zsum += zval
        if ch in up_map and ch in down_map:
            diff = up_map[ch] - down_map[ch]
            if abs(zval - diff) > TOL:
                res.fail(pol_lineno, "%s: polarization %s = %.4f != up-down "
                                     "%.4f (tol %g)" % (where, ch, zval, diff, TOL))
    if abs(zsum - z) > TOL:
        res.fail(pol_lineno, "%s: sum of channel polarizations %.4f != "
                             "polarization total %.4f (tol %g)"
                 % (where, zsum, z, TOL))

    res.atoms.append({
        "index": idx, "total": total,
        "summary": [(k, v) for k, v in summary_items],
        "up_total": u, "up": [(c[0], c[1], list(c[2])) for c in up_ch],
        "down_total": w, "down": [(c[0], c[1], list(c[2])) for c in down_ch],
        "pol_total": z, "pol": [(k, v) for k, v in pol_items],
    })


# ---------------------------------------------------------------------------
# Whole-artifact validation
# ---------------------------------------------------------------------------

def validate_artifact_bytes(data, expected_job=None):
    """Full structural + internal-consistency validation of artifact bytes.

    `expected_job`: when the artifact's filename is `<stem>.lowdin.txt`, pass
    <stem> -- the header's <job> must equal it. Pass None to accept any job.
    """
    res = Result()
    if b"\r" in data:
        res.fail(1, "CR byte present (banked evidence is pure LF)")
        return res
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError as e:
        res.fail(1, "non-ASCII byte: %s" % e)
        return res
    if not text.endswith("\n"):
        res.fail(1, "no trailing newline")
        return res
    lines = text.split("\n")[:-1]
    if len(lines) < 12:
        res.fail(1, "file too short to be a Lowdin artifact (%d lines)"
                 % len(lines))
        return res

    # L1 header
    m = HEADER_RE.match(lines[0])
    if m is None:
        res.fail(1, "header line does not match the banked template: %r"
                 % lines[0][:80])
    elif expected_job is not None and m.group("job") != expected_job:
        res.fail(1, "header job %r != expected %r"
                 % (m.group("job"), expected_job))
    # L2 / L3
    if lines[1] != LOWDIN_LINE:
        res.fail(2, "line 2 != %r (exact, incl. trailing space)" % LOWDIN_LINE)
    if lines[2] != "":
        res.fail(3, "line 3 is not empty")
    # global uniqueness
    lowdin_lines = [i for i, l in enumerate(lines)
                    if l.startswith("Lowdin Charges")]
    if lowdin_lines != [1]:
        res.fail(1, "expected exactly one 'Lowdin Charges' line at line 2; "
                    "found at lines %r" % [i + 1 for i in lowdin_lines])
    jd = [i for i, l in enumerate(lines) if "JOB DONE" in l]
    if len(jd) != 1:
        res.fail(1, "expected exactly one 'JOB DONE' line; found %d" % len(jd))
    spills = [i for i, l in enumerate(lines) if SPILL_RE.match(l)]
    if len(spills) != 1:
        res.fail(1, "expected exactly one Spilling Parameter line; found %d"
                 % len(spills))
        return res
    spill_idx = spills[0]
    sm = SPILL_RE.match(lines[spill_idx])
    spill_str = sm.group(1)
    try:
        spill_val = float(spill_str)
    except ValueError:
        res.fail(spill_idx + 1, "unparseable Spilling Parameter %r" % spill_str)
        spill_val = None
    if spill_val is not None and not (0.0 <= spill_val < 1.0):
        res.fail(spill_idx + 1, "Spilling Parameter %s outside [0, 1)" % spill_str)
    res.info["spilling"] = spill_str

    # Atom region
    groups, nspin2, block_pol = _parse_region(lines, 3, spill_idx, res)
    if groups is not None:
        _validate_atoms(groups, nspin2, res)
        if block_pol is not None and res.info["nspin_shape"] == 2:
            # Conditional check, dormant on all current data (QE 7.5 prints no
            # block-total polarization row).
            polsum = sum(a["pol_total"] for a in res.atoms)
            if abs(polsum - block_pol[1]) > TOL:
                res.fail(block_pol[0], "block total polarization %.4f != sum of "
                                       "per-atom polarizations %.4f (tol %g)"
                         % (block_pol[1], polsum, TOL))

    # Frame tail after Spilling Parameter
    t = spill_idx
    def expect(offset, ok, desc):
        i = t + offset
        if i >= len(lines):
            res.fail(len(lines), "file ends before %s" % desc)
            return False
        if not ok(lines[i]):
            res.fail(i + 1, "expected %s, got: %r" % (desc, lines[i][:60]))
        return True

    frame = (
        (1, lambda l: l == "", "blank line after Spilling Parameter"),
        (2, lambda l: PROJWFC_RE.match(l) is not None, "PROJWFC timing line"),
        (3, lambda l: l == "", "blank line"),
        (4, lambda l: l == "", "blank line"),
        (5, lambda l: TERM_RE.match(l) is not None,
         "'This run was terminated on:' line"),
        (6, lambda l: l == "", "blank line"),
        (7, lambda l: l == BANNER, "banner line"),
        (8, lambda l: l == JOB_DONE_LINE, "'   JOB DONE.' line"),
        (9, lambda l: l == BANNER, "banner line"),
    )
    for offset, ok, desc in frame:
        if not expect(offset, ok, desc):
            return res
    notes = 0
    for i in range(t + 10, len(lines)):
        if not lines[i].startswith(NOTE_PREFIX):
            res.fail(i + 1, "expected IEEE Note line or EOF, got: %r"
                     % lines[i][:60])
            return res
        notes += 1
    res.info["notes"] = notes
    return res


def validate_artifact_file(path):
    """Validate an on-disk artifact; job-vs-stem enforced for *.lowdin.txt names."""
    name = os.path.basename(path)
    expected_job = name[:-len(ART_SUFFIX)] if name.endswith(ART_SUFFIX) else None
    with open(path, "rb") as fh:
        data = fh.read()
    return validate_artifact_bytes(data, expected_job=expected_job)


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def build_artifact_bytes(raw_path):
    """Return (job, artifact_bytes) or raise ExtractError with an exit code."""
    name = os.path.basename(raw_path)
    if not name.endswith(RAW_SUFFIX):
        raise ExtractError(4, "%s: input does not end in %s (the header "
                              "template requires that suffix)"
                          % (raw_path, RAW_SUFFIX))
    job = name[:-len(RAW_SUFFIX)]
    with open(raw_path, "rb") as fh:
        data = fh.read()
    starts = []
    pos = 0
    while True:
        i = data.find(LOWDIN_MARK, pos)
        if i < 0:
            break
        if i == 0 or data[i - 1:i] == b"\n":
            starts.append(i)
        pos = i + 1
    if len(starts) == 0:
        raise ExtractError(1, "%s: no Lowdin block ('%s' at start of line)"
                          % (raw_path, LOWDIN_MARK.decode()))
    if len(starts) >= 2:
        raise ExtractError(1, "%s: ambiguous -- %d Lowdin blocks"
                          % (raw_path, len(starts)))
    tail = data[starts[0]:]
    if b"JOB DONE" not in tail:
        raise ExtractError(2, "%s: truncated/failed projwfc (no JOB DONE after "
                              "the Lowdin block)" % raw_path)
    if b"\r" in tail:
        raise ExtractError(1, "%s: CR byte in Lowdin tail (banked evidence is "
                              "pure LF)" % raw_path)
    header = HEADER_TEMPLATE.format(job=job).encode("ascii")
    return job, header + b"\n" + tail


class ExtractError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code
        self.msg = msg


def extract_one(raw_path, out=None, out_dir=None, to_stdout=False):
    """Extract one raw file. Returns (exit_code, info_or_None)."""
    try:
        job, artifact = build_artifact_bytes(raw_path)
    except ExtractError as e:
        print("ERROR: %s" % e.msg, file=sys.stderr)
        return e.code, None

    res = validate_artifact_bytes(artifact, expected_job=job)
    if not res.ok:
        print("ERROR: %s: extracted bytes fail validation:" % raw_path,
              file=sys.stderr)
        for f in res.failures:
            print("  %s" % f, file=sys.stderr)
        return 5, None
    for w in res.warnings:
        print("WARNING: %s: %s" % (raw_path, w), file=sys.stderr)

    if to_stdout:
        sys.stdout.buffer.write(artifact)
        sys.stdout.buffer.flush()
        return 0, res.info

    if out is not None:
        target = out
    elif out_dir is not None:
        target = os.path.join(out_dir, job + ART_SUFFIX)
    else:
        target = os.path.join(os.path.dirname(raw_path) or ".", job + ART_SUFFIX)

    # Evidence-safety rail: refuse an existing target; no overwrite flag exists.
    if os.path.exists(target):
        print("ERROR: %s: target exists, refusing to overwrite (no overwrite "
              "flag exists; this is the evidence-safety rail)" % target,
              file=sys.stderr)
        return 3, None

    tdir = os.path.dirname(target) or "."
    fd, tmp = tempfile.mkstemp(prefix=".%s." % os.path.basename(target),
                               suffix=".tmp", dir=tdir)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(artifact)
        with open(tmp, "rb") as fh:
            written = fh.read()
        wres = validate_artifact_bytes(written, expected_job=job)
        if written != artifact or not wres.ok:
            print("ERROR: %s: temp file failed post-write validation"
                  % raw_path, file=sys.stderr)
            for f in wres.failures:
                print("  %s" % f, file=sys.stderr)
            return 5, None
        if os.path.exists(target):  # re-check before the atomic move
            print("ERROR: %s: target appeared during extraction, refusing"
                  % target, file=sys.stderr)
            return 3, None
        os.replace(tmp, target)
        tmp = None
    finally:
        if tmp is not None and os.path.exists(tmp):
            os.unlink(tmp)

    print("EXTRACTED %s nspin_shape=%d atoms=%d spilling=%s notes=%d"
          % (target, res.info["nspin_shape"], res.info["atoms"],
             res.info["spilling"], res.info["notes"]))
    return 0, res.info


# ---------------------------------------------------------------------------
# Check mode
# ---------------------------------------------------------------------------

def _print_report(path, res):
    print("DERIVED (not part of the artifact) -- %s" % path)
    if res.info["nspin_shape"] == 2:
        for a in res.atoms:
            up = {c: (v, dict(s)) for c, v, s in a["up"]}
            down = {c: (v, dict(s)) for c, v, s in a["down"]}
            chans = [c for c, _ in a["summary"]]
            updown = "  ".join("%s= %8.4f" % (c, up[c][0] + down[c][0])
                               for c in chans)
            print("  Atom %4d: up+down  %s  | total= %9.4f"
                  % (a["index"], updown, a["up_total"] + a["down_total"]))
            for c in chans:
                subs_u, subs_d = up[c][1], down[c][1]
                if subs_u:
                    line = "  ".join("%s= %8.4f" % (k, subs_u[k] + subs_d.get(k, 0.0))
                                     for k in subs_u)
                    print("             up+down %s suborbitals  %s" % (c, line))
            recomputed = "  ".join("%s= %8.4f" % (c, up[c][0] - down[c][0])
                                   for c in chans)
            print("             up-down  %s  | total= %9.4f (recomputed "
                  "polarization)" % (recomputed,
                                     a["up_total"] - a["down_total"]))
        tot = sum(a["total"] for a in res.atoms)
        pol = sum(a["pol_total"] for a in res.atoms)
        print("  block totals: sum(total charge)= %.4f  "
              "sum(polarization)= %.4f" % (tot, pol))
    else:
        for a in res.atoms:
            line = "  ".join("%s= %8.4f" % (c, v) for c, v in a["channels"])
            print("  Atom %4d: %s  | total= %9.4f"
                  % (a["index"], line, a["total"]))
        tot = sum(a["total"] for a in res.atoms)
        print("  block totals: sum(total charge)= %.4f" % tot)
    print("  (sanity band for the human log only -- Lowdin loses the spilled "
          "charge; never compare as an equality against pw.x totals)")


def check_files(paths, report=False):
    """Validate existing artifacts. Returns process exit code."""
    all_ok = True
    for path in paths:
        try:
            res = validate_artifact_file(path)
        except OSError as e:
            print("CHECK FAIL %s: %s" % (path, e))
            all_ok = False
            continue
        if res.ok:
            print("CHECK PASS %s nspin_shape=%s atoms=%d spilling=%s notes=%d"
                  % (path, res.info["nspin_shape"], res.info["atoms"],
                     res.info["spilling"], res.info["notes"]))
        else:
            all_ok = False
            print("CHECK FAIL %s (%d failure%s)"
                  % (path, len(res.failures),
                     "" if len(res.failures) == 1 else "s"))
            for f in res.failures:
                print("  %s: %s" % (path, f))
        for w in res.warnings:
            print("  WARNING %s: %s" % (path, w))
        # Report only for artifacts that PASS: a failing artifact's parsed rows
        # can be internally inconsistent (e.g. a spin-channel sequence that does
        # not match the summary row), so deriving up+down/up-down tables from
        # them is meaningless and previously crashed with a KeyError, aborting
        # the remaining files in a batch.
        if report and res.ok and res.atoms:
            _print_report(path, res)
    return 0 if all_ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="extract_lowdin.py",
        description="Extract the Lowdin section of a projwfc stdout into the "
                    "banked <job>.lowdin.txt artifact format, or --check "
                    "existing artifacts. See module docstring for the format "
                    "spec, validation plan, and exit codes.")
    ap.add_argument("inputs", nargs="+",
                    help="raw *.projwfc.out files (extract mode) or "
                         "*.lowdin.txt artifacts (--check mode)")
    ap.add_argument("--out", metavar="FILE",
                    help="explicit target path (single input only)")
    ap.add_argument("--out-dir", metavar="DIR",
                    help="write <job>.lowdin.txt into DIR instead of beside "
                         "the input")
    ap.add_argument("--stdout", action="store_true",
                    help="print artifact bytes to stdout, write nothing "
                         "(single input only)")
    ap.add_argument("--check", action="store_true",
                    help="validate existing .lowdin.txt artifacts instead of "
                         "extracting")
    ap.add_argument("--report", action="store_true",
                    help="with --check: print per-atom DERIVED tables "
                         "(never written into any artifact)")
    args = ap.parse_args(argv)

    def usage(msg):
        print("ERROR: %s" % msg, file=sys.stderr)
        return 64

    if args.check:
        if args.out or args.out_dir or args.stdout:
            return usage("--check takes no output options")
        return check_files(args.inputs, report=args.report)

    if args.report:
        return usage("--report requires --check")
    if args.out and args.out_dir:
        return usage("--out and --out-dir are mutually exclusive")
    if args.stdout and (args.out or args.out_dir):
        return usage("--stdout writes nothing; drop --out/--out-dir")
    if (args.out or args.stdout) and len(args.inputs) > 1:
        return usage("--out/--stdout accept a single input only")

    code = 0
    for raw in args.inputs:
        rc, _ = extract_one(raw, out=args.out, out_dir=args.out_dir,
                            to_stdout=args.stdout)
        if rc != 0 and code == 0:
            code = rc
    return code


if __name__ == "__main__":
    sys.exit(main())
