"""Adversarial QE parser tests independent of archived census verdicts."""
from pathlib import Path

import pytest

from silentgate.readers.qe import read_deck, read_energies, read_force_blocks, read_header, read_qe


def force(atom, x="0.00000000", y="-0.00000000", z="0.25"):
    return f" atom {atom} type 1 force = {x} {y} {z}\n"


def deck(path, ads=True, units="angstrom", flags="1 1 1", cell=""):
    count = 2 if ads else 1
    atoms = "Cr 0 0 1 0 0 0\n"
    if ads:
        atoms += f"O 0 0 3 {flags}\n"
    path.write_text(
        f"&SYSTEM\n nat={count}, nspin=2, tot_magnetization=1.5\n/\n"
        "&CONTROL\nforc_conv_thr=2.0d-3\n/\n"
        f"ATOMIC_POSITIONS {units}\n{atoms}"
        f"{cell}HUBBARD (atomic)\nU Cr-3d 3.7\n", encoding="utf-8")
    return path


def pair(tmp_path, output):
    deck(tmp_path / "slab.in", ads=False)
    deck(tmp_path / "arbitrary-name.in")
    path = tmp_path / "arbitrary-name.out"
    path.write_bytes(output.encode())
    return path


def test_contribution_blocks_do_not_become_steps():
    text = "Forces acting on atoms (cartesian axes, Ry/au):\n" + force(1)
    for title in (
        "The non-local contrib. to forces", "The ionic contribution to forces",
        "The local contribution to forces", "The core correction contribution to forces",
        "The Hubbard contrib. to forces", "The SCF correction term to forces",
    ):
        text += title + "\n" + force(1, x="1.0", y="1.0")
    text += "Total force = 0.1\n"
    steps, _, issues = read_force_blocks(text)
    assert steps == [{1: [0.0, -0.0, 0.25]}]
    assert issues == []


def test_every_step_is_retained_and_signed_zero_is_numeric():
    text = "Forces acting on atoms:\n" + force(1) + "Total force = 0.1\n"
    text += "Forces acting on atoms:\n" + force(1, x="2d-8") + "Total force = 0.1\n"
    steps, _, issues = read_force_blocks(text.replace("\n", "\r\n"))
    assert len(steps) == 2
    assert steps[0][1][:2] == [0.0, 0.0]
    assert steps[1][1][0] == 2e-8
    assert not issues


def test_headerless_truncated_block_scores_only_surviving_adsorbate(tmp_path):
    path = pair(tmp_path, "2 Sym. Ops. (no inversion) found\n\x00\n" + force(2) + "Total force = 0.1\n")
    result = read_qe(path)
    assert result["adsorbate_indices"] == [2]
    assert result["n_if_pos_excluded"] == 1
    assert result["force_steps"] == [{2: [0.0, -0.0, 0.25]}]
    assert not result["force_issues"]
    assert not result["unidentified"]
    assert result["nul_bytes"] == 1
    path.write_text("\x00\n" + force(1) + "Total force = 0.1\n")
    assert "missing adsorbate" in " ".join(read_qe(path)["force_issues"])


def test_orphan_rows_need_total_force_delimiter():
    _, _, issues = read_force_blocks(force(2))
    assert "lacks Total force delimiter" in " ".join(issues)


@pytest.mark.parametrize("token", ["nan", "inf", "1e999", "1e-999", "***"])
def test_invalid_or_underflow_force_is_never_replaced_by_zero(token):
    steps, _, issues = read_force_blocks(
        "Forces acting on atoms:\n" + force(1, x=token) + "Total force = 0.1\n")
    assert issues
    assert not any(1 in step for step in steps)


def test_duplicate_rows_are_reported():
    _, _, issues = read_force_blocks("Forces acting on atoms:\n" + force(1) + force(1) + "Total force = 0.1\n")
    assert "duplicate atom" in " ".join(issues)


@pytest.mark.parametrize("header,count,form", [
    ("4 Sym. Ops. (no inversion) found", 4, "count-first"),
    ("16 Sym. Ops., with inversion, found ( 8 have fractional translation)", 16, "count-first"),
    ("Sym. Ops., with inversion, found 4 symmetry operations", 4, "count-last"),
    ("No symmetry found", 1, "no-symmetry"),
])
def test_header_grammars(header, count, form):
    result = read_header(header)
    assert result["n_symops"] == count
    assert result["header_form"].startswith(form)


def test_conflicting_header_witness_is_not_collapsed():
    result = read_header("4 Sym. Ops. (no inversion) found\nNo symmetry found")
    assert result["symmetry_conflict"]
    assert result["n_symops"] is None
    assert len(result["symmetry_headers"]) == 2


def test_crystal_cell_after_atoms_and_metadata(tmp_path):
    path = deck(tmp_path / "deck.in", units="crystal", cell="CELL_PARAMETERS angstrom\n1 0 0\n0 1 0\n0 0 2\n")
    result = read_deck(path)
    assert not result["issues"]
    assert result["atoms"][1]["position"] == [0.0, 0.0, 6.0]
    assert result["forc_conv_thr"] == 0.002
    assert result["nspin"] == 2
    assert result["tot_magnetization"] == 1.5
    assert result["U"] == {"Cr-3d": 3.7}


@pytest.mark.parametrize("kwargs", [{"units": "crystal"}, {"units": "crystal_sg"}, {"flags": "1 1"}])
def test_unsupported_or_incomplete_deck_is_explicit(tmp_path, kwargs):
    result = read_deck(deck(tmp_path / "deck.in", **kwargs))
    assert result["issues"]


def test_converged_energy_reader_ignores_iteration_decoys(tmp_path):
    path = tmp_path / "energies.out"
    path.write_text(" iteration # ***\n total energy = -8.0 Ry\n"
                    "! total energy = -10.0 Ry\n total energy = -9.0 Ry\n"
                    "! total energy = -11d0 Ry\n convergence NOT achieved\n")
    assert read_energies(path) == [-10.0, -11.0]


def test_companion_lookup_does_not_guess_alternate_decks(tmp_path):
    deck(tmp_path / "slab.in", ads=False)
    deck(tmp_path / "unknown.run.in")
    path = tmp_path / "unknown.out"
    path.write_text("Forces acting on atoms:\n" + force(1) + force(2) + "Total force = 0.1\n")
    assert read_qe(path)["unidentified"]
    assert not read_qe(path, deck_path=tmp_path / "unknown.run.in")["unidentified"]


def test_bare_u_nat_disagreement_is_unidentified(tmp_path):
    path = pair(tmp_path, "Forces acting on atoms:\n" + force(1) + force(2) + "Total force = 0.1\n")
    deck(tmp_path / "slab__u1.in")
    result = read_qe(path)
    assert result["unidentified"]
    assert "inconsistent same-metal bare nat" in " ".join(result["issues"])
