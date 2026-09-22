"""The sibling launcher: identical behaviour to the diagnostic launcher plus the day-form time limit."""
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/dft"))
import lowtail_batch_launch as launch
import lowtail_slab_scf_diag_launch as original


def test_time_limit_field_matches_scontrol_below_and_beyond_one_day():
    assert launch.time_limit_field(150) == "02:30:00"
    assert launch.time_limit_field(780) == "13:00:00"
    assert launch.time_limit_field(1440) == "1-00:00:00"
    assert launch.time_limit_field(4320) == "3-00:00:00"
    assert launch.time_limit_field(2160) == "1-12:00:00"


def test_sibling_pins_itself_and_leaves_the_original_untouched():
    assert launch.LOCAL_SOURCES[0] == "src/dft/lowtail_batch_launch.py"
    assert original.LOCAL_SOURCES[0] == "src/dft/lowtail_slab_scf_diag_launch.py"
    own = hashlib.sha256((ROOT / launch.LOCAL_SOURCES[0]).read_bytes()).hexdigest()
    assert launch.LOADED_SHA256 == own


def test_array_task_field_is_shared_behaviour():
    assert launch.array_task_field(1, 1) == original.array_task_field(1, 1) == "1%1"
    assert launch.array_task_field(2, 2) == original.array_task_field(2, 2) == "1-2%2"
