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


class FairchemSurfaceBackend(AdsorptionBackend):
    """Real backend: CHE-referenced *OH/*O/*OOH adsorption ΔG on an fcc(111) HEA
    slab, energies from a fairchem universal model (UMA, OC20 task).

    Per composition: relax the clean slab, relax each adsorbate configuration, and
    reference to gas-phase H2O/H2 (cached). Heavy deps (ase, fairchem) and the
    model load lazily on first ``predict`` — importing hea_oer stays light and the
    CPU heuristic round-1 needs neither. Requires a GPU and (gated) HF access to
    the model; an alternative ASE ``calculator`` can be injected for testing.
    """

    name = "uma"

    def __init__(self, model: str = "uma-s-1p1", task: str = "oc20", device: str = "cuda",
                 size: tuple[int, int, int] = (3, 3, 4), fmax: float = 0.05,
                 steps: int = 300, seed: int = 0, surface: str = "metal",
                 n_sites: int = 4, calculator=None):
        self.model = model
        self.task = task
        self.device = device
        self.size = size
        self.fmax = fmax
        self.steps = steps
        self.seed = seed
        self.surface = surface  # "metal" fcc(111) | "oxide" rocksalt(100) | "rutile" MO2(110)
        self.n_sites = n_sites  # cus sites sampled per composition (rutile multi-site)
        #: formula -> per-site eta distribution {n_sites, eta_min, eta_mean, eta_std, eta_max}
        self.site_records: dict[str, dict] = {}
        base = "fairchem:custom" if calculator is not None else f"fairchem:{model}"
        self.name = base + ("" if surface == "metal" else f":{surface}")
        self._calc = calculator
        self._gas: tuple[float, float] | None = None

    def _calculator(self):
        if self._calc is None:
            from .relax import make_calculator
            self._calc = make_calculator(self.model, self.task, self.device)
        return self._calc

    def _gas_refs(self) -> tuple[float, float]:
        if self._gas is None:
            from .relax import gas_reference_energies
            self._gas = gas_reference_energies(self._calculator(), self.fmax, self.steps)
        return self._gas

    def predict(self, comp: Composition) -> tuple[float, float, float]:
        if self.surface == "rutile":
            return self._predict_rutile_multisite(comp)
        from .relax import relax
        from .referencing import delta_G
        if self.surface == "oxide":
            from .surfaces_oxide import build_rocksalt100_hea as build_slab
            from .surfaces_oxide import add_oer_adsorbate_oxide as add_ads
        else:
            from .surfaces import build_fcc111_hea as build_slab
            from .surfaces import add_oer_adsorbate as add_ads

        calc = self._calculator()
        slab = build_slab(comp, size=self.size, seed=self.seed)
        e_slab, slab_relaxed = relax(slab, calc, self.fmax, self.steps)
        E_H2O, E_H2 = self._gas_refs()
        dG: dict[str, float] = {}
        for sp in ("OH", "O", "OOH"):
            ads = add_ads(slab_relaxed, sp)
            e_ads, _ = relax(ads, calc, self.fmax, self.steps)
            dG[sp] = delta_G(e_slab, e_ads, sp, E_H2O, E_H2)
        return dG["OH"], dG["O"], dG["OOH"]

    def _predict_rutile_multisite(self, comp: Composition) -> tuple[float, float, float]:
        """Rutile(110): relax the slab, then sample `n_sites` cus sites, compute
        ΔG(*OH/*O/*OOH)→η at each, and return the **best (lowest-η) site's** triple
        (the 'favorable tail' active-site hypothesis). Per-site η spread is stashed
        in `self.site_records[formula]` for the driver to surface.
        """
        from .relax import relax
        from .referencing import delta_G
        from .descriptors import oer_overpotential
        from .surfaces_rutile import build_rutile110_hea, cus_site_xy, add_oer_adsorbate_at

        calc = self._calculator()
        slab = build_rutile110_hea(comp, supercell=(self.size[0], self.size[1]), seed=self.seed)
        sites = cus_site_xy(slab, n_sites=self.n_sites)  # on pristine slab: ideal cus coordination
        e_slab, slab_relaxed = relax(slab, calc, self.fmax, self.steps)
        E_H2O, E_H2 = self._gas_refs()

        per_site: list[tuple[float, tuple[float, float, float]]] = []
        for xy in sites:
            dG: dict[str, float] = {}
            for sp in ("OH", "O", "OOH"):
                ads = add_oer_adsorbate_at(slab_relaxed, sp, xy)
                e_ads, _ = relax(ads, calc, self.fmax, self.steps)
                dG[sp] = delta_G(e_slab, e_ads, sp, E_H2O, E_H2)
            triple = (dG["OH"], dG["O"], dG["OOH"])
            per_site.append((oer_overpotential(*triple).overpotential, triple))

        per_site.sort(key=lambda t: t[0])  # favorable tail = lowest-η cus site first
        etas = np.array([e for e, _ in per_site], dtype=float)
        self.site_records[comp.formula()] = dict(
            n_sites=int(len(etas)), eta_min=float(etas.min()), eta_mean=float(etas.mean()),
            eta_std=float(etas.std()) if len(etas) > 1 else 0.0, eta_max=float(etas.max()),
        )
        return per_site[0][1]


_BACKENDS = {
    "heuristic": HeuristicBackend,
    "uma": FairchemSurfaceBackend,
    "oc22": FairchemSurfaceBackend,  # alias — legacy name used in docs/12
}


def get_backend(name: str = "heuristic", **kwargs) -> AdsorptionBackend:
    """Factory: 'heuristic' (CPU placeholder) or 'uma'/'oc22' (fairchem surface backend)."""
    key = name.lower()
    if key not in _BACKENDS:
        raise ValueError(f"unknown backend {name!r}; choose from {list(_BACKENDS)}")
    return _BACKENDS[key](**kwargs)
