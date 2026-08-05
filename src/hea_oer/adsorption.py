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
from .data import M_O_DESORBED_MIN, OXOPHILICITY_KJ_PER_O
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
                 n_sites: int = 4, calculator=None, seeds: tuple[int, ...] | None = None):
        self.model = model
        self.task = task
        self.device = device
        self.size = size
        self.fmax = fmax
        self.steps = steps
        self.seed = seed
        #: Decorations to pool cus sites over. A 2x2 rutile(110) slab exposes only 4
        #: cus sites, and which elements land on them is an accident of one seeded
        #: shuffle: for Fe32Ni17Co34Mn18 seed 0 puts *only* Co and Fe there, so Ni and
        #: Mn -- 34 at.% of the alloy between them -- never appear at an active site.
        #: Estimating a favourable TAIL from that is the wrong instrument for the very
        #: hypothesis the multi-site sampling exists to test, so the default pools
        #: several independent decorations. `seed` alone reproduces the old behaviour.
        self.seeds = tuple(seeds) if seeds is not None else (seed,)
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

        Each adsorbate state is relaxed from **several starts** (builder placement +
        rigid pull-ins) and the lowest-energy result wins — see
        `surfaces_rutile.adsorbate_starts` for why single-start is not an option here.
        The winning M–O distances are recorded so a desorbed "minimum" cannot enter
        the melt list silently, which is exactly how four wrong structures survived
        into the DFT tier.
        """
        from .relax import relax
        from .referencing import delta_G
        from .descriptors import oer_overpotential
        from .surfaces_rutile import (
            add_oer_adsorbate_at, adsorbate_starts, binding_metal_index,
            build_rutile110_hea, cus_site_xy, m_o_distance,
        )

        calc = self._calculator()
        E_H2O, E_H2 = self._gas_refs()

        per_site: list[tuple[float, tuple[float, float, float]]] = []
        bonds: list[dict] = []
        for seed in self.seeds:
            slab = build_rutile110_hea(comp, supercell=(self.size[0], self.size[1]),
                                       seed=seed)
            sites = cus_site_xy(slab, n_sites=self.n_sites)  # pristine slab: ideal cus coordination
            e_slab, slab_relaxed = relax(slab, calc, self.fmax, self.steps)
            n_slab = len(slab_relaxed)
            for xy in sites:
                dG: dict[str, float] = {}
                bond: dict[str, float] = {"seed": seed}
                for sp in ("OH", "O", "OOH"):
                    best_e, best_atoms, best_tag = None, None, ""
                    for tag, start in adsorbate_starts(slab_relaxed, sp, xy):
                        e_ads, relaxed = relax(start, calc, self.fmax, self.steps)
                        if best_e is None or e_ads < best_e:
                            best_e, best_atoms, best_tag = e_ads, relaxed, tag
                    dG[sp] = delta_G(e_slab, best_e, sp, E_H2O, E_H2)
                    bond[sp] = m_o_distance(best_atoms, n_slab)
                    bond[sp + "_start"] = best_tag
                bond["site_metal"] = slab_relaxed[
                    binding_metal_index(add_oer_adsorbate_at(slab_relaxed, "O", xy), n_slab)
                ].symbol
                triple = (dG["OH"], dG["O"], dG["OOH"])
                per_site.append((oer_overpotential(*triple).overpotential, triple))
                bonds.append(bond)

        order = np.argsort([e for e, _ in per_site])  # favorable tail = lowest-η first
        per_site = [per_site[i] for i in order]
        bonds = [bonds[i] for i in order]
        etas = np.array([e for e, _ in per_site], dtype=float)
        self.site_records[comp.formula()] = dict(
            n_sites=int(len(etas)), n_decorations=len(self.seeds),
            eta_min=float(etas.min()), eta_mean=float(etas.mean()),
            eta_std=float(etas.std()) if len(etas) > 1 else 0.0, eta_max=float(etas.max()),
            site_metals=sorted({b["site_metal"] for b in bonds}),
            bonds=bonds[0], all_bonds=bonds,
            # the winning site's chemistry, so the screen can refuse to rank a
            # composition whose "best" state never actually adsorbed
            desorbed=[sp for sp in ("OH", "O", "OOH")
                      if bonds[0][sp] >= M_O_DESORBED_MIN],
        )
        return per_site[0][1]


class MACESurfaceBackend(FairchemSurfaceBackend):
    """The screening backend of record: identical geometry/CHE machinery, MACE energies.

    R0 established that **no** out-of-box UMA head ranks rutile MO2(110) OER (best
    oc25 rho = +0.400, p = 0.52; docs/29 s8), which voids the UMA-derived melt set in
    docs/15 s1. R3 then found that MACE-MPA-0 does, un-fine-tuned and free
    (rho = +0.857, exact p = 0.0238, eta MAE 0.172 V at n = 7; docs/35 s1). This
    backend is that result made usable for screening.

    Two standing caveats, both load-bearing when reading a shortlist it produces:

    * **Rank, not value.** The pre-registered out-of-sample test in docs/34 came back
      1 hit / 1 miss -- eta(Co) was wrong by +0.339 V, 2.3x the validated bar. Use the
      ordering; do not quote a candidate's absolute eta as a prediction.
    * **A calibration tier, not an electrode.** docs/31: of the six rutile MO2
      endmembers only beta-MnO2 is a real ambient phase with any aqueous window, and
      what actually gets melted is an fcc metal that reconstructs to an (oxy)hydroxide
      under OER. Activity from here must be gated on stability before it means
      anything (docs/31 s8.3).
    """

    def __init__(self, model: str = "medium-mpa-0", device: str = "cpu",
                 dtype: str = "float64", surface: str = "rutile", **kwargs):
        kwargs.pop("task", None)  # MACE has no task head; silently accepting one would lie
        super().__init__(model=model, device=device, surface=surface, **kwargs)
        self.dtype = dtype
        self.name = f"mace:{model}" + ("" if surface == "metal" else f":{surface}")

    def _calculator(self):
        if self._calc is None:
            from .relax import make_mace_calculator
            self._calc = make_mace_calculator(self.model, self.device, self.dtype)
        return self._calc


_BACKENDS = {
    "heuristic": HeuristicBackend,
    "uma": FairchemSurfaceBackend,
    "oc22": FairchemSurfaceBackend,  # alias — legacy name used in docs/12
    "mace": MACESurfaceBackend,
}


def get_backend(name: str = "heuristic", **kwargs) -> AdsorptionBackend:
    """Factory: 'heuristic' (CPU placeholder) or 'uma'/'oc22' (fairchem surface backend)."""
    key = name.lower()
    if key not in _BACKENDS:
        raise ValueError(f"unknown backend {name!r}; choose from {list(_BACKENDS)}")
    return _BACKENDS[key](**kwargs)
