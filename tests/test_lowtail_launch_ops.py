"""Actual Slurm pending-node ranges must remain exactly one node."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/dft"))
import lowtail_launch_ops as ops


def held(nodes="1-1", extra=""):
    return ("JobState=PENDING Reason=JobHeldUser NumCPUs=128 NumTasks=128 NumNodes=" + nodes +
            " Requeue=0 Account=che260157 ArrayTaskId=1-9%1 MinMemoryNode=237G Partition=shared" +
            " WorkDir=" + ops.REMOTE + " ArrayJobId=20813525 TimeLimit=16:45:00 ExcNodeList=a024" +
            " Command=" + ops.REMOTE + "/" + ops.SCRIPT + extra)


@pytest.mark.parametrize("nodes", ["1", "1-1"])
def test_exact_one_node_formats(monkeypatch, nodes):
    monkeypatch.setattr(ops, "command", lambda *a, **k: {"stdout": held(nodes)})
    ops.inspect_held(None, "20813525", {"wall_minutes": 1005, "exclusions": "a024"})


@pytest.mark.parametrize("override", [" NumNodes=1-2", " NumNodes=2", " NumCPUs=256",
                                    " NumTasks=64", " Partition=debug", " WorkDir=/tmp",
                                    " ArrayJobId=123", " Reason=Priority", " TimeLimit=48:00:00"])
def test_resource_mismatch_remains_held(monkeypatch, override):
    monkeypatch.setattr(ops, "command", lambda *a, **k: {"stdout": held(extra=override)})
    with pytest.raises(ValueError):
        ops.inspect_held(None, "20813525", {"wall_minutes": 1005, "exclusions": "a024"})
