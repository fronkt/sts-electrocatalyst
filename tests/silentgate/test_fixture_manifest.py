"""Tripwires on the corpus the S1 controls are scored against.

These do not test `silentgate` -- they test that the archive still is what the
fixture manifest says it is. If one of them fails, a tracked output was added,
rewritten, corrupted or normalised, and every fixture claim downstream of it is
suspect. That matters because the positive control is defined by FILE
(docs/43:1864) and the two-witness agreement is defined against
docs/figs/symops_audit.csv "at the commit CI runs against".

Every check here is structural: a hash, a byte count, a marker line, a block
count. None of them censuses a force. Deriving a per-atom / per-axis / per-step
expectation would mean writing a reader, and the readers are core, "written and
committed only by the entrant" (:1840).

AUTHORSHIP: written by AI as "tests and fixtures" under the A9.1 :1840 permitted
list.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess

import pytest

from conftest import ROOT, read_lf

CONTRIB = re.compile(
    rb"^\s*The .{0,40}(?:contrib\.|contribution|correction term)\s+to forces\s*$", re.M)
FHDR = re.compile(rb"^\s*Forces acting on atoms", re.M)
FLINE = re.compile(rb"^\s*atom\s+\d+\s+type\s+\d+\s+force\s*=", re.M)
NAT = re.compile(rb"number of atoms/cell\s*=\s*(\d+)")
SYM = re.compile(rb"^.*?(\d+)\s+Sym\.\s*Ops\..*$", re.M)


def _ids(manifest):
    return [f["path"] for f in manifest["fixture"]]


def _fixture(manifest, path):
    for f in manifest["fixture"]:
        if f["path"] == path:
            return f
    raise KeyError(path)


@pytest.fixture(scope="session")
def fixture_paths(manifest):
    return _ids(manifest)


def test_every_fixture_is_tracked(manifest):
    tracked = set(
        subprocess.run(["git", "ls-files"], capture_output=True, text=True, cwd=ROOT)
        .stdout.split("\n")
    )
    for f in manifest["fixture"]:
        assert f["path"] in tracked, (
            "%s is not tracked; a fixture must be a committed file, not a local "
            "artefact" % f["path"]
        )


def test_fixture_content_is_unchanged(manifest):
    """LF-normalised sha256, so the check holds on Windows and on Linux CI alike."""
    drift = []
    for f in manifest["fixture"]:
        p = os.path.join(ROOT, f["path"])
        if not os.path.exists(p):
            drift.append("%s: MISSING" % f["path"])
            continue
        lf = read_lf(p)
        got = hashlib.sha256(lf).hexdigest()
        if got != f["sha256_lf"]:
            drift.append("%s: sha256_lf %s != %s" % (f["path"], got, f["sha256_lf"]))
        elif len(lf) != f["bytes_lf"]:
            drift.append("%s: bytes_lf %d != %d" % (f["path"], len(lf), f["bytes_lf"]))
    assert not drift, "fixture content drifted:\n" + "\n".join(drift)


def test_fixture_structure_is_unchanged(manifest):
    """The marker lines and block counts each fixture was chosen for."""
    drift = []
    for f in manifest["fixture"]:
        s = f["structure"]
        b = read_lf(os.path.join(ROOT, f["path"]))
        checks = {
            "pwscf_banner": (b"Program PWSCF" in b),
            "no_symmetry_found": (b"No symmetry found" in b),
            "n_force_block_headers": len(FHDR.findall(b)),
            "n_contribution_block_headers": len(CONTRIB.findall(b)),
            "n_force_lines": len(FLINE.findall(b)),
            "nul_bytes": b.count(b"\x00"),
            "negative_zero_tokens": b.count(b"-0.00000000"),
            "job_done": (b"JOB DONE" in b),
            "mpi_abort": (b"MPI_ABORT" in b),
        }
        m = NAT.search(b)
        checks["n_atoms_cell"] = int(m.group(1)) if m else 0
        sm = SYM.search(b)
        checks["symmetry_header"] = sm.group(0).decode("utf8", "replace").strip() if sm else ""
        for key, got in checks.items():
            if s[key] != got:
                drift.append("%s: %s %r != %r" % (f["path"], key, got, s[key]))
    assert not drift, "fixture structure drifted:\n" + "\n".join(drift)


def test_the_corpus_never_shrinks(manifest, corpus_scan):
    """The corpus may GROW -- S3 is live and adds outputs -- but must not shrink.

    This deliberately does not freeze the count. A tripwire that fires on every
    legitimate new run is a tripwire that gets ignored, and being ignored is the
    only way a gate fails. What is genuinely alarming is a tracked output
    DISAPPEARING, because the positive control is defined by file (docs/43:1864)
    and the n/n agreement is defined against the CSV at the commit CI runs
    against. Growth is reported, not punished.
    """
    c = manifest["corpus"]
    now = len(corpus_scan)
    was = c["tracked_out_files"]
    assert now >= was, (
        "tracked .out count FELL %d -> %d. Outputs do not vanish on their own; "
        "the positive control is enumerated by file and something it names may "
        "be gone." % (was, now)
    )
    if now > was:
        print("corpus grew %d -> %d tracked .out files since the manifest was "
              "generated (expected while S3 runs)" % (was, now))
    for f in (
        "runs/Cr_slab/s0_O.out", "runs/Ir_anchor/s0_O.out", "runs/Ru_anchor/s0_O.out",
        "runs/Co_slab/s0_O.out", "runs/Cu_slab/s0_OOH.out", "runs/Ni_slab/s0_O.out",
    ):
        assert f in corpus_scan, "a production control file left the corpus: %s" % f


def test_no_unrecognised_symmetry_header_form_has_appeared(manifest, corpus_scan):
    """A NEW header form is a real risk to the reader, so this one does fail.

    Growth in the counts of the four known forms is fine and expected. A fifth
    form appearing means pw.x printed something the header regex has never seen,
    and A9.1 :1836 registers that the reader "accepts both forms by regex and
    logs the form encountered per file" -- an unlogged fifth form is exactly the
    silent failure that rule exists to prevent.
    """
    known = set(manifest["corpus"]["header_forms"])
    seen = {}
    for f, v in corpus_scan.items():
        if v["header_form"]:
            seen.setdefault(v["header_form"], []).append(f)
    new = {k: v[:3] for k, v in seen.items() if k not in known}
    assert not new, (
        "an unrecognised pw.x symmetry-header form appeared: %r\n"
        "Check that silentgate's header reader handles it, then regenerate the "
        "manifest with tests/silentgate/fixtures/regenerate_manifest.py." % new
    )
    missing = [k for k in known if k not in seen]
    assert not missing, "a known header form vanished from the corpus: %r" % missing


def test_the_four_header_forms_are_still_present(manifest, corpus_scan):
    """A9.1 :1836 registers that the header reader "accepts both forms by regex
    and logs the form encountered per file".

    Measured 2026-08-27: this repo's corpus contains FOUR distinct count-first
    forms and ZERO instances of the count-LAST form shown in symops_audit.py's
    own docstring. A regex anchored on "(no inversion)" misses 32 of the 173
    files that carry a header. These counts are the tripwire; the reader itself
    is core and is tested by golden file once it exists.
    """
    want = manifest["corpus"]["header_forms"]
    got = {}
    for v in corpus_scan.values():
        if v["header_form"]:
            got[v["header_form"]] = got.get(v["header_form"], 0) + 1
    assert len(want) == 4
    shrunk = {k: (want[k], got.get(k, 0)) for k in want if got.get(k, 0) < want[k]}
    assert not shrunk, (
        "a header form lost files (was, now): %r -- outputs do not un-print a "
        "header, so something was removed or rewritten" % shrunk
    )


def test_the_count_last_header_form_is_absent_in_house(manifest):
    """The form symops_audit.py's docstring shows does not occur here.

    Docstring form: "Sym. Ops., with inversion, found          4 symmetry operations"
    -- count LAST. Zero in-house files use it. A9.7's act-2 dated line
    (2026-08-23, the first parse) looked for it in the Xu deposit too and records
    that all four validated RuO2 files "are the count-first form; the older
    docstring form was not encountered". So the registered both-forms rule stands
    but has been exercised against no real count-last data anywhere; P-XU's six
    blind metals are still unread and cannot rule it out. Recorded so "accepts
    both forms" is never mistaken for "tested on both forms".
    """
    for key in manifest["corpus"]["header_forms"]:
        assert key.startswith("N Sym. Ops."), (
            "a count-last header form appeared in-house: %r -- the reader's "
            "both-forms requirement can now be tested against real data" % key
        )


def test_the_force_decomposition_family_is_unchanged(manifest, corpus_scan):
    """One real force block, six contribution blocks, identical line format.

    A detector that regex-scrapes `atom N type M force =` without delimiting
    blocks reads 7x the ionic steps on each of these and mixes partial forces
    into the census. `src/dft/symops_audit.py`'s FORCE_BLOCK finditer does
    exactly that; v0.1 must not inherit it.
    """
    want = set(manifest["corpus"]["force_decomposition_files"]["paths"])
    got = {f for f, v in corpus_scan.items() if v["has_decomposition"]}
    gone = want - got
    assert not gone, "a force-decomposition fixture left the corpus: %r" % sorted(gone)
    new = got - want
    if new:
        # Informational, not a failure: another high-verbosity run is a legitimate
        # thing to add. It IS worth seeing, because each new one is another file a
        # block-blind detector would mis-parse by 7x.
        print("new force-decomposition outputs since the manifest was generated "
              "(each is another 7x mis-parse risk): %r" % sorted(new))
    for f in sorted(want):
        b = read_lf(os.path.join(ROOT, f))
        nat = int(NAT.search(b).group(1))
        assert len(FHDR.findall(b)) == 1
        assert len(CONTRIB.findall(b)) == 6
        assert len(FLINE.findall(b)) == 7 * nat, (
            "%s: %d force lines for nat=%d -- the 7x split is the whole point of "
            "this fixture" % (f, len(FLINE.findall(b)), nat)
        )


def test_the_nul_spliced_fixture_still_has_its_header_destroyed(manifest):
    """runs/probe/Cr/s0_OOH__base.out: MPI abort text written into the output.

    The `Forces acting on atoms` header is gone and the block starts partway
    through the atom list. Whether such a block is scorable is an OPEN entrant
    decision -- three archived LOCKED rows rest on blocks missing their first
    atoms. See test_open_questions.py.
    """
    f = _fixture(manifest, "runs/probe/Cr/s0_OOH__base.out")
    b = read_lf(os.path.join(ROOT, f["path"]))
    assert b.count(b"\x00") == 1, "the NUL splice is what makes this fixture"
    assert len(FHDR.findall(b)) == 0, "the force-block header must still be destroyed"
    assert len(FLINE.findall(b)) == 10
    assert int(NAT.search(b).group(1)) == 21
    first = int(re.search(rb"^\s*atom\s+(\d+)\s+type", b, re.M).group(1))
    assert first == 12, "the surviving block still starts at atom 12 of 21"


def test_grep_would_skip_the_nul_spliced_files():
    """A NUL byte makes grep treat the file as binary and skip it silently.

    Recorded because it is how this family stayed invisible: any harness that
    shells out to grep to find candidate outputs will under-count, and will do
    so without saying anything.
    """
    p = os.path.join(ROOT, "runs", "probe", "Cr", "s0_OOH__base.out")
    with open(p, "rb") as fh:
        assert b"\x00" in fh.read()


def test_the_two_unclassifiable_rows_are_the_registered_pair():
    """:1864 names 96 of 98 classifiable adsorbate rows at 137010b.

    The two without a force block are runs/Cu_slab/s0_OH.out and
    runs/probe/Ru_spin/s0_OH__spin0.5.out. The CSV is the enumeration source for
    the n/n agreement gate, so if its shape moves, n moves with it.
    """
    import csv
    path = os.path.join(ROOT, "docs", "figs", "symops_audit.csv")
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    ads = [r for r in rows if (r["n_adsorbate"] or "").strip() and int(r["n_adsorbate"]) > 0]
    uncl = [r["path"] for r in ads if not (r["max_fy_adsorbate"] or "").strip()]
    assert len(rows) == 156
    assert len(ads) == 98
    assert sorted(uncl) == sorted(["Cu_slab/s0_OH.out", "probe/Ru_spin/s0_OH__spin0.5.out"])
    assert len(ads) - len(uncl) == 96


def test_the_csv_predates_most_of_the_corpus(corpus_scan):
    """:1864: "UNKNOWN in the repo until symops_audit.csv is regenerated at HEAD."

    The oracle covers 156 rows; the tracked corpus is far larger. The n/n gate is
    defined against the CSV "at the commit CI runs against", so regenerating it
    changes n deliberately -- this test records the gap rather than hiding it.
    """
    import csv
    path = os.path.join(ROOT, "docs", "figs", "symops_audit.csv")
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    tracked = list(corpus_scan)
    covered = {"runs/" + r["path"].replace("\\", "/") for r in rows}
    uncovered = [f for f in tracked if f not in covered]
    assert len(rows) == 156, "the CSV was regenerated; the n/n gate's n moved with it"
    # Recorded, not targeted: most of the tracked corpus postdates the Aug-9 CSV,
    # including every force-only false positive the 2026-08-27 survey found. If
    # the CSV is regenerated at HEAD this test is the one that says so.
    assert len(uncovered) >= 300, (
        "only %d tracked outputs are outside the CSV; it was regenerated, and "
        "the n/n agreement gate is now scored over a different n" % len(uncovered)
    )
