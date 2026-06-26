"""Adsorption-energy backends: ΔG(*OH), ΔG(*O), ΔG(*OOH) for a composition.

Two implementations behind one interface:

* ``HeuristicBackend``  — a TRANSPARENT PLACEHOLDER for ranking only. It is NOT
  DFT and must not be reported as physical adsorption energies. It maps a
  composition-weighted oxophilicity proxy to ΔG(*OH), applies the universal
  *OOH/*OH scaling, and lets compositional *disorder* nudge the activity
  descriptor toward the volcano apex — encoding (in a deliberately simple way)
  the hypothesis that high-entropy disorder partially breaks OER scaling
  relations. Outputs are bounded and deterministic so the round-1 pipeline runs
  and is unit-testable on CPU.

* ``OC22FairchemBackend`` — the real backend (stub). Predicts ΔG(*OH/*O/*OOH) on
  reconstructed (oxy)hydroxide/oxide surfaces with a pretrained Open Catalyst
  2022 GNN (EquiformerV2 / GemNet-OC) via ``fairchem``. Needs a GPU; intended to
  run on Vast.ai. See src/README.md for the swap instructions.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from .composition import Composition
from .data import OXOPHILICITY_KJ_PER_O
from .descriptors import OOH_OH_SCALING, OPTIMAL_DESCRIPTOR


class AdsorptionBackend(ABC):
    name: str = "abstract"

    @abstractmethod
    def predict(self, comp: Composition) -> tuple[float, float, float]:
        """Return (ΔG_OH, ΔG_O, ΔG_OOH) in eV for a composition."""

    def predict_many(self, comps) -> np.ndarray:
        """Vectorized helper: (N, 3) array of (ΔG_OH, ΔG_O, ΔG_OOH)."""
        return np.array([self.predict(c) for c in comps], dtype=float)


class HeuristicBackend(AdsorptionBackend):
    """Transparent oxophilicity-based PLACEHOLDER prior (not DFT)."""

    name = "heuristic"

    # --- calibration constants (documented; tuned to plausible 3d-oxide ranges) ---
    OX_REF = -270.0      # kJ/mol O, mid-3d reference oxophilicity
    G0 = 1.3             # ΔG_OH (eV) at the reference oxophilicity
    G1 = 0.008           # eV per (kJ/mol O): more oxophilic -> stronger OH binding
    DG_OH_BOUNDS = (0.2, 2.6)
    BG0, BG1 = 0.9, 0.55  # base scaling line for ΔG_O - ΔG_OH vs ΔG_OH
    DISORDER_REF = 120.0  # kJ/mol O normalizer for the oxophilicity spread
    DISORDER_GAIN = 0.5   # max fractional pull of the descriptor toward the apex
    DISORDER_CAP = 0.6

    def predict(self, comp: Composition) -> tuple[float, float, float]:
        x = np.array(comp.fractions)
        ox = np.array([OXOPHILICITY_KJ_PER_O[el] for el in comp.elements])
        ox_bar = float(np.sum(x * ox))
        spread = float(np.sqrt(np.sum(x * (ox - ox_bar) ** 2)))

        # 1) oxophilicity -> ΔG(*OH) (volcano position)
        dG_OH = self.G0 + self.G1 * (ox_bar - self.OX_REF)
        lo, hi = self.DG_OH_BOUNDS
        dG_OH = float(np.clip(dG_OH, lo, hi))

        # 2) parent scaling line for the descriptor ΔG(*O) - ΔG(*OH)
        base_gap = self.BG0 + self.BG1 * dG_OH

        # 3) high-entropy disorder pulls the descriptor toward the apex (1.6 eV)
        disorder = min(self.DISORDER_CAP, self.DISORDER_GAIN * spread / self.DISORDER_REF)
        gap = OPTIMAL_DESCRIPTOR + (base_gap - OPTIMAL_DESCRIPTOR) * (1.0 - disorder)

        dG_O = dG_OH + gap
        dG_OOH = dG_OH + OOH_OH_SCALING   # universal scaling (real)
        return dG_OH, dG_O, dG_OOH


class OC22FairchemBackend(AdsorptionBackend):
    """Real OC22 GNN backend (stub — requires fairchem + GPU)."""

    name = "oc22"

    def __init__(self, checkpoint: str | None = None):
        self.checkpoint = checkpoint

    def predict(self, comp: Composition) -> tuple[float, float, float]:
        raise NotImplementedError(
            "OC22FairchemBackend is a stub. To enable on a GPU box:\n"
            "  1) pip install fairchem-core\n"
            "  2) download an OC22 checkpoint (EquiformerV2 / GemNet-OC)\n"
            "  3) build (oxy)hydroxide/oxide surface slabs for the composition "
            "(pymatgen/ASE), place *OH/*O/*OOH adsorbates, relax with the GNN, "
            "and convert binding energies to ΔG with the standard gas-phase "
            "references. Then return (ΔG_OH, ΔG_O, ΔG_OOH).\n"
            "See src/README.md."
        )


_BACKENDS = {"heuristic": HeuristicBackend, "oc22": OC22FairchemBackend}


def get_backend(name: str = "heuristic", **kwargs) -> AdsorptionBackend:
    """Factory: 'heuristic' (default, CPU) or 'oc22' (GPU stub)."""
    key = name.lower()
    if key not in _BACKENDS:
        raise ValueError(f"unknown backend {name!r}; choose from {list(_BACKENDS)}")
    return _BACKENDS[key](**kwargs)
