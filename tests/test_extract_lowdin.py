"""Tests for src/dft/extract_lowdin.py (docs/61 SA11.8 item 4 / decision item 12).

The extractor reproduces the recipe behind every banked runs/**/<job>.lowdin.txt:
one header line + a verbatim byte-for-byte copy of the raw projwfc stdout from its
`Lowdin Charges: ` line to EOF. These tests pin:

  T1  the validator against the ENTIRE bank (every committed .lowdin.txt passes,
      which pins the format spec to the 265 banked precedents),
  T2  nspin=2 extraction from the 10 committed raws in runs/a0/spin/ -- header,
      byte-identical tail (reference slice computed independently here, not via
      the module under test), validator pass, shape detection, and the Ti sp2null
      null-seed control property (per-atom polarization == 0.0000),
  T3  nspin=1 byte-fidelity round-trip via a synthesized raw (no nspin=1 raw is
      committed anywhere; full outputs live only on Anvil),
  T4  fail-closed behaviour (exit codes 1/2/3/4; existing target untouched),
  T5  validator negatives (corrupted values, missing rows, altered header).

Tests read runs/ but NEVER write, modify, or delete anything under runs/.
All writes go to tmp_path.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dft import extract_lowdin as xl  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUNS = os.path.join(REPO, "runs")
SPIN = os.path.join(RUNS, "a0", "spin")


def _glob_bank():
    hits = []
    for root, _, files in os.walk(RUNS):
        for f in sorted(files):
            if f.endswith(".lowdin.txt"):
                hits.append(os.path.join(root, f))
    return sorted(hits)


def _glob_spin_raws():
    hits = []
    if os.path.isdir(SPIN):
        for root, _, files in os.walk(SPIN):
            for f in sorted(files):
                if f.endswith(".projwfc.out"):
                    hits.append(os.path.join(root, f))
    return sorted(hits)


def _ref_tail(raw_bytes):
    """Independent reference slice: bytes from the line-start 'Lowdin Charges'."""
    if raw_bytes.startswith(b"Lowdin Charges"):
        return raw_bytes
    i = raw_bytes.find(b"\nLowdin Charges")
    assert i >= 0, "fixture has no Lowdin block"
    return raw_bytes[i + 1:]


# ---------------------------------------------------------------------------
# T1 -- bank-wide validator pass
# ---------------------------------------------------------------------------

def test_t1_entire_bank_validates():
    bank = _glob_bank()
    if not bank:
        pytest.skip("no banked .lowdin.txt files in this checkout")
    rc = xl.main(["--check"] + bank)
    assert rc == 0, "banked artifacts failed the validator"


# ---------------------------------------------------------------------------
# T2 -- nspin=2 extraction from the committed spin raws
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", _glob_spin_raws() or [None])
def test_t2_spin_raw_extraction(raw, tmp_path):
    if raw is None:
        pytest.skip("no committed spin raws in this checkout")
    job = os.path.basename(raw)[:-len(".projwfc.out")]
    rc = xl.main([raw, "--out-dir", str(tmp_path)])
    assert rc == 0
    out = tmp_path / (job + ".lowdin.txt")
    data = out.read_bytes()

    # (i) header line
    header, _, tail = data.partition(b"\n")
    expected = ("# Lowdin section of %s.projwfc.out (full projwfc output "
                "retained on Anvil beside the deck)" % job).encode("ascii")
    assert header == expected

    # (ii) tail byte-identical to independently computed reference slice
    with open(raw, "rb") as fh:
        raw_bytes = fh.read()
    assert tail == _ref_tail(raw_bytes)

    # (iii) validator passes, (iv) shape detected == nspin=2
    res = xl.validate_artifact_bytes(data, expected_job=job)
    assert res.ok, res.failures
    assert res.info["nspin_shape"] == 2

    # Null-seed control property, asserted where it actually holds: the bare
    # slab sp2null run converges with spin-up rows byte-identical to spin-down
    # (every per-atom polarization 0.0000). The s0_OOH sp2null run does NOT --
    # *OOH carries an odd electron and the null-seed SCF genuinely converges
    # polarized (measured max |per-atom polarization| = 0.4352 in the committed
    # raw), so no zero assertion is made there.
    if "sp2null" in job and job.startswith("slab"):
        for atom in res.atoms:
            assert abs(atom["pol_total"]) <= xl.TOL, atom
            for _, zval in atom["pol"]:
                assert abs(zval) <= xl.TOL, atom


# ---------------------------------------------------------------------------
# T3 -- nspin=1 byte-fidelity round-trip (synthesized raw)
# ---------------------------------------------------------------------------

def test_t3_nspin1_round_trip(tmp_path):
    banked = os.path.join(RUNS, "a0", "main", "Ru", "s0_O__u000.lowdin.txt")
    if not os.path.exists(banked):
        pytest.skip("banked nspin=1 fixture absent in this checkout")
    with open(banked, "rb") as fh:
        banked_bytes = fh.read()
    _, _, banked_tail = banked_bytes.partition(b"\n")
    fake_raw = tmp_path / "s0_O__u000.projwfc.out"
    fake_raw.write_bytes(b"arbitrary preamble\n     more projwfc lines\n"
                         + banked_tail)
    outdir = tmp_path / "out"
    outdir.mkdir()
    rc = xl.main([str(fake_raw), "--out-dir", str(outdir)])
    assert rc == 0
    got = (outdir / "s0_O__u000.lowdin.txt").read_bytes()
    assert got == banked_bytes  # byte-identical to the banked artifact
    res = xl.validate_artifact_bytes(got, expected_job="s0_O__u000")
    assert res.ok and res.info["nspin_shape"] == 1


# ---------------------------------------------------------------------------
# T4 -- fail-closed extraction
# ---------------------------------------------------------------------------

def _spin_fixture_bytes():
    raws = _glob_spin_raws()
    if not raws:
        pytest.skip("no committed spin raws in this checkout")
    with open(raws[0], "rb") as fh:
        return fh.read()


def test_t4_no_lowdin_block(tmp_path):
    p = tmp_path / "x.projwfc.out"
    p.write_bytes(b"some projwfc output\nwith no block at all\n")
    assert xl.main([str(p)]) == 1


def test_t4_truncated_before_job_done(tmp_path):
    raw = _spin_fixture_bytes()
    cut = raw[:raw.find(b"JOB DONE")]
    p = tmp_path / "x.projwfc.out"
    p.write_bytes(cut)
    assert xl.main([str(p)]) == 2


def test_t4_two_lowdin_blocks(tmp_path):
    raw = _spin_fixture_bytes()
    tail = _ref_tail(raw)
    p = tmp_path / "x.projwfc.out"
    p.write_bytes(b"preamble\n" + tail + tail)
    assert xl.main([str(p)]) == 1


def test_t4_existing_target_untouched(tmp_path):
    raw = _spin_fixture_bytes()
    p = tmp_path / "x.projwfc.out"
    p.write_bytes(raw)
    target = tmp_path / "x.lowdin.txt"
    sentinel = b"pre-existing banked evidence -- must never change\n"
    target.write_bytes(sentinel)
    before = os.stat(target)
    assert xl.main([str(p)]) == 3
    after = os.stat(target)
    assert target.read_bytes() == sentinel
    assert before.st_mtime_ns == after.st_mtime_ns
    assert before.st_size == after.st_size


def test_t4_cr_byte_in_tail(tmp_path):
    raw = _spin_fixture_bytes()
    tail = _ref_tail(raw)
    p = tmp_path / "x.projwfc.out"
    p.write_bytes(b"preamble\n" + tail.replace(b"JOB DONE.", b"JOB DONE.\r", 1))
    assert xl.main([str(p)]) == 1


def test_t4_bad_input_suffix(tmp_path):
    p = tmp_path / "x.out"
    p.write_bytes(_spin_fixture_bytes())
    assert xl.main([str(p)]) == 4


# ---------------------------------------------------------------------------
# T5 -- validator negatives
# ---------------------------------------------------------------------------

def _banked_nspin2_text():
    banked = os.path.join(RUNS, "a0", "main", "Cr", "s0_O__u000.lowdin.txt")
    if not os.path.exists(banked):
        pytest.skip("banked nspin=2 fixture absent in this checkout")
    with open(banked, "rb") as fh:
        return os.path.basename(banked), fh.read().decode("ascii")


def test_t5_corrupted_spin_total(tmp_path, capsys):
    name, text = _banked_nspin2_text()
    # Corrupt atom 1's spin-up totals (all three rows identically) so that
    # U + W != T and the spin-up channel sum != U.
    lines = text.split("\n")
    old = None
    for i, line in enumerate(lines):
        if line.startswith(" " * 17 + "spin up"):
            if old is None:
                old = line
                head = line.split(",")[0]  # '                 spin up      =   U'
                # corrupt the tenths digit (a 1e-4 change would sit inside TOL)
                assert head[-4].isdigit()
                bad = "6" if head[-4] != "6" else "5"
                bad_head = head[:-4] + bad + head[-3:]
            if line.split(",")[0] == head:
                lines[i] = bad_head + line[len(head):]
            else:
                break  # past atom 1's spin-up rows
    p = tmp_path / name
    p.write_bytes("\n".join(lines).encode("ascii"))
    rc = xl.main(["--check", str(p)])
    out = capsys.readouterr().out
    assert rc != 0
    assert "atom 1" in out and "spin up" in out


def test_t5_missing_polarization_row(tmp_path, capsys):
    name, text = _banked_nspin2_text()
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith(" " * 17 + "polarization"):
            del lines[i]
            break
    p = tmp_path / name
    p.write_bytes("\n".join(lines).encode("ascii"))
    rc = xl.main(["--check", str(p)])
    out = capsys.readouterr().out
    assert rc != 0
    assert "atom 1" in out and "incomplete row set" in out


def test_t5_report_on_failing_artifact_no_crash(tmp_path, capsys):
    # Regression: --check --report on a FAILING artifact whose spin-channel
    # sequence mismatches the summary row used to raise an uncaught KeyError
    # inside _print_report, aborting the remaining files in the batch. The
    # DERIVED report must be suppressed for failing artifacts and later files
    # in the same batch must still be checked.
    name, text = _banked_nspin2_text()
    # rename atom 1's first spin-up channel key (first ' s = ' after the first
    # 'spin up' row start) to 'q'
    i = text.index("spin up")
    j = text.index(" s = ", i)
    bad = text[:j] + " q = " + text[j + len(" s = "):]
    p = tmp_path / name
    p.write_bytes(bad.encode("ascii"))
    good = tmp_path / "good"
    good.mkdir()
    banked = os.path.join(RUNS, "a0", "main", "Cr", "s0_O__u000.lowdin.txt")
    with open(banked, "rb") as fh:
        (good / "s0_O__u000.lowdin.txt").write_bytes(fh.read())
    rc = xl.main(["--check", "--report", str(p),
                  str(good / "s0_O__u000.lowdin.txt")])
    out = capsys.readouterr().out
    assert rc == 1
    assert "channel sequence" in out
    # failing artifact: no DERIVED table; passing artifact: still checked,
    # WITH its DERIVED table
    assert out.count("DERIVED (not part of the artifact)") == 1
    assert "CHECK PASS" in out and "s0_O__u000.lowdin.txt" in out


def test_t5_altered_header(tmp_path, capsys):
    name, text = _banked_nspin2_text()
    assert text.startswith("# Lowdin section")
    p = tmp_path / name
    p.write_bytes(("# Lowdon section" + text[16:]).encode("ascii"))
    rc = xl.main(["--check", str(p)])
    out = capsys.readouterr().out
    assert rc != 0
    assert "header line does not match" in out
