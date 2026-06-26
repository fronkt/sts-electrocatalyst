"""hea_oer — ML round-1 selector for high-entropy-alloy OER electrocatalysts.

Pipeline (see STS2027/docs/12 §3):
    enumerate compositions
      -> empirical phase-stability filter   (phase_stability.py)
      -> adsorption energies                (adsorption.py: heuristic | OC22)
      -> OER theoretical overpotential       (descriptors.py)
      -> multi-objective ranking             (objective.py)
      -> shortlist to melt                   (pipeline.py)

Round-2 active learning conditions on measured overpotentials (active_learning.py).

The heuristic adsorption backend is an explicit PLACEHOLDER for ranking only;
swap in OC22FairchemBackend on a GPU box for physical predictions.
"""

from .composition import Composition, sample_compositions
from .phase_stability import phase_stability, formability_score
from .descriptors import oer_overpotential, descriptor_from_dG_OH
from .adsorption import HeuristicBackend, get_backend
from .pipeline import run_round1

__all__ = [
    "Composition",
    "sample_compositions",
    "phase_stability",
    "formability_score",
    "oer_overpotential",
    "descriptor_from_dG_OH",
    "HeuristicBackend",
    "get_backend",
    "run_round1",
]
