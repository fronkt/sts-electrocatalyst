"""OC20 reader controls at the stored force precision, independent of ASE."""
import lzma
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from silentgate.readers.oc20 import read_oc20


PROPERTIES = "species:S:1:pos:R:3:move_mask:L:1:tags:I:1:forces:R:3"


def frame(rows, properties=PROPERTIES):
    return str(len(rows)) + "\n" + 'Lattice="1 0 0 0 1 0 0 0 1" Properties=' + properties + "\n" + "\n".join(rows) + "\n"


def write(tmp_path, text, compressed=False):
    path = tmp_path / ("sample.extxyz.xz" if compressed else "sample.extxyz")
    if compressed:
        path.write_bytes(lzma.compress(text.encode()))
    else:
        path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize("compressed", [False, True])
def test_mask_tags_one_based_and_all_unconstrained_zero_count(tmp_path, compressed):
    rows = ["Pt 0 0 0 F 0 0 0 0", "Pt 1 1 1 T 1 0 0 1",
            "O 2 2 2 T 2 -0.00000000 0.00000001 1", "H 3 3 3 F 2 0 0 0"]
    second = rows.copy()
    second[2] = "O 2 2 2 T 2 1 0 1"
    result = read_oc20(write(tmp_path, frame(rows) + frame(second), compressed))
    assert result["scorable"] and not result["unidentified"]
    assert result["issues"] == []
    assert result["adsorbate_indices"] == [3]
    assert result["n_if_pos_excluded"] == 2
    assert result["n_adsorbate_excluded"] == 1
    assert result["excluded_adsorbate_indices"] == [4]
    assert set(result["force_steps"][0]) == {2, 3}
    assert result["force_steps"][0][3] == (0.0, 1e-8, 1.0)
    assert result["per_step_exact_zero_count"] == 6
    assert result["per_step_exact_zero_counts"] == [3, 3]
    assert result["n_symops"] is None
    assert result["header_form"] == "force-only"


def test_reordered_properties_and_quoted_header(tmp_path):
    props = '"forces:R:3:tags:I:1:species:S:1:move_mask:L:1:pos:R:3:extra:R:1"'
    text = frame(["0 1 2 2 O T 0 0 0 42"], props)
    result = read_oc20(write(tmp_path, text))
    assert result["scorable"]
    assert result["force_steps"] == [{1: (0.0, 1.0, 2.0)}]


@pytest.mark.parametrize("token", ["nan", "inf", "-inf", "1e-999", "1e999", "oops"])
def test_bad_forces_cannot_be_scored_as_unlocked(tmp_path, token):
    result = read_oc20(write(tmp_path, frame([f"O 0 0 0 T 2 {token} 1 1"])))
    assert not result["scorable"]
    assert result["unidentified"] and result["fatal_issues"]


@pytest.mark.parametrize("tail", ["1\n", "1\nProperties=" + PROPERTIES + "\n", "junk\n"])
def test_truncated_or_garbage_tail_invalidates_complete_prefix(tmp_path, tail):
    prefix = frame(["O 0 0 0 T 2 0 1 1"])
    result = read_oc20(write(tmp_path, prefix + tail))
    assert len(result["force_steps"]) == 1
    assert not result["scorable"]
    assert result["issues"]


@pytest.mark.parametrize("changed", ["O 0 0 0 F 2 0 1 1", "O 0 0 0 T 1 0 1 1", "H 0 0 0 T 2 0 1 1"])
def test_identity_and_constraint_changes_invalidate_trajectory(tmp_path, changed):
    result = read_oc20(write(tmp_path, frame(["O 0 0 0 T 2 0 1 1"]) + frame([changed])))
    assert not result["scorable"]
    assert "changed" in result["issues"][0]


@pytest.mark.parametrize("rows", [["O 0 0 0 T 1 0 1 1"], ["O 0 0 0 F 2 0 1 1"]])
def test_no_eligible_adsorbates_is_unmeasured(tmp_path, rows):
    result = read_oc20(write(tmp_path, frame(rows)))
    assert not result["scorable"]
    assert result["unidentified"]


@pytest.mark.parametrize("props", [PROPERTIES.replace("move_mask:L:1", "move_mask:R:1"), PROPERTIES.replace(":forces:R:3", ""), PROPERTIES + ":tags:I:1"])
def test_missing_or_ambiguous_metadata_fails_closed(tmp_path, props):
    result = read_oc20(write(tmp_path, frame(["O 0 0 0 T 2 0 1 1"], props)))
    assert not result["scorable"]
    assert result["issues"]


def test_corrupt_xz_and_missing_input_are_diagnostic(tmp_path):
    path = tmp_path / "bad.extxyz.xz"
    path.write_bytes(b"not an xz stream")
    assert read_oc20(path)["issues"]
    assert not read_oc20(tmp_path / "missing.extxyz")["scorable"]


def test_empty_input_is_unmeasured(tmp_path):
    result = read_oc20(write(tmp_path, ""))
    assert not result["scorable"]
    assert result["force_steps"] == []
