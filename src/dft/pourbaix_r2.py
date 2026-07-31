#!/usr/bin/env python3
"""R2 - the aqueous-stability gate for the rutile-MO2 OER endmember tier.

WHY THIS EXISTS
---------------
docs/26 and docs/29 report an OER overpotential for a rutile (110) slab of every
3d endmember we could converge. An overpotential is a property of an *electrode*.
Before any of those numbers can be read as a screening result, one prior question
has to be answered for each endmember: **does the rutile MO2 polymorph exist as an
ambient bulk phase at all, and does it survive water at OER potentials?**

This module answers that in two stages, deliberately in this order:

  Stage 1 - PHASE EXISTENCE (`gate`). Purely structural, no energetics. For each
    of MnO2/CrO2/FeO2/CoO2/NiO2/CuO2 plus the RuO2/IrO2 anchors, ask Materials
    Project whether a P4_2/mnm (rutile, #136) entry exists, whether it carries
    ICSD provenance (i.e. somebody made it and diffracted it), and how far above
    the convex hull it sits. This decides most of the set *before* any Pourbaix
    energy is computed.

  Stage 2 - AQUEOUS STABILITY (`window`, `anchors`). Only for phases that pass
    stage 1. The Pourbaix construction of Persson 2012 (10.1103/PhysRevB.85.235438)
    /Wang 2020 (10.1038/s41524-020-00430-3), the same one behind the MP Pourbaix app.

INTEGRITY RULE ENFORCED IN CODE
-------------------------------
A Pourbaix decomposition energy printed next to a phase that does not exist is
fabrication, not a result. `dg_pbx_for` therefore refuses to return a number for
any endmember whose stage-1 verdict is ABSENT, and the two energy paths are kept
on separate, separately-labelled axes throughout:

  * "experimental"  - hand-entered literature Delta_Gf (298 K), Mn only. pymatgen's
                      pourbaix_diagram ships no bundled thermodynamic data, so this
                      path runs fully offline and is what the textbook beta-MnO2
                      diagram is built from.
  * "MP PBE+U"      - Materials Project GGA/GGA+U solids + experimental aqueous ions.

They are never averaged, never plotted on one axis, and every reported window
carries its dissolved-ion concentration (MP convention 1e-6 M; a Nernstian window
edge moves ~59 mV per decade of concentration, so a window quoted without its
concentration means nothing).

Usage
-----
    PYTHONPATH=src python src/dft/pourbaix_r2.py selftest        # offline, no key
    PYTHONPATH=src python src/dft/pourbaix_r2.py window          # offline, no key
    PYTHONPATH=src python src/dft/pourbaix_r2.py gate            # needs MP key
    PYTHONPATH=src python src/dft/pourbaix_r2.py anchors         # needs MP key
    PYTHONPATH=src python src/dft/pourbaix_r2.py run             # everything + JSON + PNG

`gate`/`anchors`/`run` cache every Materials Project response in
`results/r2_mp_cache.json`, so a second run (and the figure) needs no network.
Pass `--refresh` to re-query. Exit status of `run` is 1 if any endmember's
verified verdict contradicts what docs/28 s3 asserted (that is a finding, not a
crash - it is meant to be noisy).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
import warnings

import numpy as np

from pymatgen.analysis.pourbaix_diagram import IonEntry, PourbaixDiagram, PourbaixEntry
from pymatgen.core.ion import Ion
from pymatgen.entries.computed_entries import ComputedEntry

# ---------------------------------------------------------------------------
# constants and conventions
# ---------------------------------------------------------------------------

# 1 eV per particle = 96.485 kJ/mol (Faraday constant / 1000).
KJMOL_PER_EV = 96.485
# Nernst prefactor at 298.15 K, 2.303 RT/F, in V per pH unit / per decade.
PREFAC_V = 0.0591
# Reversible OER potential, pH-independent on the RHE scale.
OER_EQUILIBRIUM_V_RHE = 1.229
# Representative overpotential at which an OER electrode is actually operated.
OER_OPERATING_ETA_V = 0.30
# MP's dissolved-ion convention. EVERY window in this module is quoted at this
# concentration; changing it moves Nernstian edges by ~59 mV per decade.
DEFAULT_CONC_M = 1e-6

RUTILE_SPACEGROUP = "P4_2/mnm"
RUTILE_SPACEGROUP_NUMBER = 136

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_CACHE = os.path.join(REPO, "results", "r2_mp_cache.json")
DEFAULT_JSON = os.path.join(REPO, "results", "r2_stability.json")
DEFAULT_FIG = os.path.join(REPO, "docs", "figs", "pourbaix_mno2.png")

# ---------------------------------------------------------------------------
# what docs/28 s3 asserted, so the script can grade itself against it
# ---------------------------------------------------------------------------

# Six endmembers of the rutile tier plus the two literature anchors. `asserted`
# is docs/28 s3's claim verbatim in machine-readable form; `expect_rutile` is what
# that claim implies for stage 1 so a contradiction can be detected automatically.
ENDMEMBERS = {
    "MnO2": dict(metal="Mn", asserted="rutile ambient phase (pyrolusite)", expect_rutile=True),
    "CrO2": dict(metal="Cr", asserted="metastable, CVD-only, decomposes to Cr2O3", expect_rutile=True),
    "FeO2": dict(metal="Fe", asserted="no ambient phase; pyrite-type only above ~74 GPa", expect_rutile=False),
    "CoO2": dict(metal="Co", asserted="layered (delithiated LiCoO2), not rutile", expect_rutile=False),
    "NiO2": dict(metal="Ni", asserted="layered (delithiated LiNiO2), not rutile", expect_rutile=False),
    "CuO2": dict(metal="Cu", asserted="does not exist as bulk (Cu(IV) unfavourable)", expect_rutile=False),
    "RuO2": dict(metal="Ru", asserted="anchor: rutile ambient phase", expect_rutile=True),
    "IrO2": dict(metal="Ir", asserted="anchor: rutile ambient phase", expect_rutile=True),
}

# ---------------------------------------------------------------------------
# Stage 2a - hand-entered experimental thermochemistry (offline path)
# ---------------------------------------------------------------------------

# Standard Gibbs energies of formation at 298.15 K, 1 bar, kJ/mol, from the NBS
# tables (Wagman et al., J. Phys. Chem. Ref. Data 11, Suppl. 2, 1982) as
# reproduced in the CRC Handbook and in Pourbaix's Atlas (1974) chapter on Mn.
#
# These are the numbers the textbook beta-MnO2 Pourbaix diagram is built from.
# They are NOT DFT and must never be mixed onto an axis with the MP PBE+U path.
#
# Deliberate omission: no Mn(III) oxyhydroxide (manganite, gamma-MnOOH). Its
# tabulated Delta_Gf varies by tens of kJ/mol across compilations and the value
# would set the *lower* MnO2 edge; the OER-relevant *upper* edge is fixed by the
# MnO4(2-)/MnO4(-) couples and is untouched by the omission. Flagged in the
# writeup rather than guessed at.
MN_GF_KJMOL = [
    # (formula, phase, Delta_Gf kJ/mol, note)
    ("Mn", "solid", 0.0, "element reference state, alpha-Mn"),
    ("MnO", "solid", -362.9, "manganosite"),
    ("Mn3O4", "solid", -1283.2, "hausmannite"),
    ("Mn2O3", "solid", -881.1, "bixbyite"),
    ("MnO2", "solid", -465.14, "PYROLUSITE = beta-MnO2, the rutile polymorph"),
    ("Mn(OH)2", "solid", -615.0, "pyrochroite"),
    ("Mn[+2]", "ion", -228.1, "aquo Mn(II)"),
    ("Mn[+3]", "ion", -82.0, "aquo Mn(III), strongly disproportionating"),
    ("HMnO2[-1]", "ion", -505.8, "hypomanganite, alkaline Mn(II)"),
    ("MnO4[-2]", "ion", -500.7, "manganate, Mn(VI)"),
    ("MnO4[-1]", "ion", -447.2, "permanganate, Mn(VII)"),
]
MN_GF_SOURCE = ("Wagman et al., NBS tables, J. Phys. Chem. Ref. Data 11 Suppl. 2 (1982); "
                "cross-checked against Pourbaix, Atlas of Electrochemical Equilibria (1974)")


def literature_mn_entries(conc_M: float = DEFAULT_CONC_M) -> list[PourbaixEntry]:
    """Build PourbaixEntry objects for Mn from the hand-entered table above.

    pymatgen's PourbaixEntry expects the wrapped entry's energy to be a *formation*
    energy referenced to the elements (it then re-references O and H to H2O and to
    the H+/e- couple internally), which is exactly what Delta_Gf is. So the
    conversion is a unit change and nothing else.
    """
    entries: list[PourbaixEntry] = []
    for formula, phase, gf_kj, note in MN_GF_KJMOL:
        gf_ev = gf_kj / KJMOL_PER_EV
        if phase == "solid":
            entries.append(PourbaixEntry(ComputedEntry(formula, gf_ev), entry_id=f"lit-{formula}"))
        else:
            ion = Ion.from_formula(formula)
            entries.append(PourbaixEntry(IonEntry(ion, gf_ev), entry_id=f"lit-{formula}",
                                         concentration=conc_M))
        entries[-1].lit_note = note  # type: ignore[attr-defined]
    return entries


def literature_mn_diagram(conc_M: float = DEFAULT_CONC_M) -> PourbaixDiagram:
    """The classical experimental Mn-H2O diagram.

    `filter_solids=False` on purpose: the solid list is hand-picked and every
    member of it is an experimentally established phase. MP's filter exists to
    throw out DFT-overstabilised oxides, which cannot happen here.
    """
    return PourbaixDiagram(literature_mn_entries(conc_M), conc_dict={"Mn": conc_M},
                           filter_solids=False)


# ---------------------------------------------------------------------------
# window / potential-scale helpers
# ---------------------------------------------------------------------------

def she_to_rhe(v_she: float | np.ndarray, pH: float | np.ndarray):
    """V vs RHE = V vs SHE + 0.0591 * pH. The OER equilibrium is flat on this scale."""
    return np.asarray(v_she) + PREFAC_V * np.asarray(pH)


def rhe_to_she(v_rhe: float | np.ndarray, pH: float | np.ndarray):
    return np.asarray(v_rhe) - PREFAC_V * np.asarray(pH)


def stability_window(pbx: PourbaixDiagram, entry: PourbaixEntry, pH: float,
                     v_lo: float = -1.2, v_hi: float = 2.6, step: float = 5e-4,
                     tol: float = 1e-4) -> dict:
    """Contiguous V range (vs SHE) at fixed pH where `entry` is the Pourbaix-stable phase.

    Defined as {V : dG_pbx(entry, pH, V) <= tol}. `tol` is 0.1 meV/atom: this is a
    membership test on the hull, not a metastability tolerance, so it must stay
    far below any physically meaningful energy.

    Returns lower/upper edges plus the phases that bound them, or `stable=False`
    with the minimum dG_pbx attained if the entry is nowhere on the hull. That
    "nowhere stable" outcome is a real result and is reported as such, never as a
    silently empty window.
    """
    grid = np.arange(v_lo, v_hi + step, step)
    # get_decomposition_energy broadcasts over V, so the whole scan is one call.
    dg = np.asarray(pbx.get_decomposition_energy(entry, np.full_like(grid, pH), grid),
                    dtype=float)
    on = dg <= tol
    if not on.any():
        return dict(pH=pH, stable=False, min_dg_pbx_eV_per_atom=float(dg.min()),
                    v_at_min_V_she=float(grid[int(dg.argmin())]))

    # Longest contiguous True run; a Pourbaix domain for a single solid is convex
    # in V at fixed pH, so there should only be one, but do not assume it.
    idx = np.flatnonzero(on)
    splits = np.split(idx, np.flatnonzero(np.diff(idx) != 1) + 1)
    run = max(splits, key=len)
    lo_i, hi_i = int(run[0]), int(run[-1])

    def _bisect(a: float, b: float) -> float:
        """Refine an edge between an off-hull V=a and an on-hull V=b to ~1e-6 V."""
        for _ in range(25):
            m = 0.5 * (a + b)
            if float(pbx.get_decomposition_energy(entry, pH, m)) <= tol:
                b = m
            else:
                a = m
        return b

    lo = float(grid[lo_i]) if lo_i == 0 else _bisect(float(grid[lo_i - 1]), float(grid[lo_i]))
    hi = float(grid[hi_i]) if hi_i == len(grid) - 1 else _bisect(float(grid[hi_i + 1]), float(grid[hi_i]))

    below = pbx.get_stable_entry(pH, lo - 0.02)
    above = pbx.get_stable_entry(pH, hi + 0.02)
    return dict(
        pH=pH, stable=True,
        lower_V_she=round(lo, 4), upper_V_she=round(hi, 4),
        lower_V_rhe=round(float(she_to_rhe(lo, pH)), 4),
        upper_V_rhe=round(float(she_to_rhe(hi, pH)), 4),
        width_V=round(hi - lo, 4),
        reduces_to=below.name, oxidises_to=above.name,
        upper_edge_minus_oer_V=round(float(she_to_rhe(hi, pH)) - OER_EQUILIBRIUM_V_RHE, 4),
    )


def composition_domain(pbx: PourbaixDiagram, formula: str, pH_list: list[float]) -> dict | None:
    """Window of whichever solid of this composition actually sits on the Pourbaix hull.

    Needed because MP's diagram is built from the *lowest-energy* polymorph of each
    composition, which for MnO2 is not pyrolusite. Comparing that domain against
    the experimental beta-MnO2 diagram is the only like-for-like MP-vs-experiment
    comparison available, and it has to be labelled as such: it is a window for
    "some MnO2 solid", not for the rutile one.
    """
    from pymatgen.core.composition import Composition

    target = Composition(formula).reduced_formula
    cands = [e for e in pbx.stable_entries
             if e.phase_type == "Solid" and e.entry.composition.reduced_formula == target]
    if not cands:
        return None
    entry = cands[0]
    return dict(entry_id=_mpid(entry.entry_id),
                caveat="MP's lowest-energy polymorph of this composition, not necessarily rutile",
                windows=[stability_window(pbx, entry, ph) for ph in pH_list])


def dg_pbx_for(pbx: PourbaixDiagram, entry: PourbaixEntry, pH: float, v_rhe: float) -> float:
    """dG_pbx in eV/atom at (pH, V vs RHE). Caller must have cleared the phase gate."""
    return float(pbx.get_decomposition_energy(entry, pH, float(rhe_to_she(v_rhe, pH))))


# ---------------------------------------------------------------------------
# Materials Project access
# ---------------------------------------------------------------------------

def _normalise_potcar_spec(entries):
    """Work around an mp-api 0.46 / pymatgen 2026.4 interface break.

    mp-api now hands back `parameters['potcar_spec']` as a list of pydantic
    `PotcarSpec` models, while pymatgen's `PotcarCorrection.get_correction` still
    calls `.get('titel')` on each element. Without this the whole MP Pourbaix path
    dies with `'PotcarSpec' object has no attribute 'get'`. Converting the models
    back to plain dicts changes no numbers; it only restores the expected type.
    """
    for e in entries:
        spec = getattr(e, "parameters", {}).get("potcar_spec")
        if spec:
            e.parameters["potcar_spec"] = [
                p if isinstance(p, dict) else (p.model_dump() if hasattr(p, "model_dump") else dict(p))
                for p in spec
            ]
    return entries


def _mpid(raw) -> str:
    """MP thermo entries carry entry_id as {'identifier': ..., 'suffix': ...}."""
    if isinstance(raw, dict):
        return str(raw.get("identifier", raw))
    return str(raw)


def _open_mprester():
    from mp_api.client import MPRester  # imported lazily: heavy, and offline paths must not need it
    mpr = MPRester()
    original = mpr.get_entries_in_chemsys
    mpr.get_entries_in_chemsys = lambda *a, **k: _normalise_potcar_spec(original(*a, **k))
    return mpr


def fetch_mp(cache_path: str, refresh: bool = False) -> dict:
    """Polymorph census + Pourbaix entry sets for every element in the tier.

    Everything is cached to disk so that `figure`/`run` and any re-analysis work
    with no network and no key. Cache is keyed by formula/element, so a partial
    cache is topped up rather than rebuilt.
    """
    cache: dict = {"polymorphs": {}, "pourbaix": {}, "material_alias": {}}
    if os.path.exists(cache_path) and not refresh:
        with open(cache_path) as fh:
            cache.update(json.load(fh))

    want_formulas = [f for f in ENDMEMBERS if f not in cache["polymorphs"]]
    want_elements = [d["metal"] for d in ENDMEMBERS.values() if d["metal"] not in cache["pourbaix"]]
    if not want_formulas and not want_elements:
        return cache

    def _flush() -> None:
        """Checkpoint after every element: `get_pourbaix_entries` is minutes long
        per element, and losing eight of them to one dropped connection is not a
        cost worth paying twice."""
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w") as fh:
            json.dump(cache, fh, indent=1)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with _open_mprester() as mpr:
            for formula in want_formulas:
                docs = mpr.materials.summary.search(
                    formula=formula,
                    fields=["material_id", "formula_pretty", "symmetry", "energy_above_hull",
                            "formation_energy_per_atom", "is_stable", "theoretical",
                            "database_IDs", "nsites", "total_magnetization"])
                rows = [dict(
                    material_id=str(d.material_id),
                    spacegroup=d.symmetry.symbol,
                    spacegroup_number=d.symmetry.number,
                    e_above_hull_eV_per_atom=(None if d.energy_above_hull is None
                                              else round(d.energy_above_hull, 4)),
                    e_form_eV_per_atom=(None if d.formation_energy_per_atom is None
                                        else round(d.formation_energy_per_atom, 4)),
                    is_stable=bool(d.is_stable),
                    theoretical=bool(d.theoretical),
                    nsites=d.nsites,
                    icsd=list((d.database_IDs or {}).get("icsd", []))[:6],
                    total_magnetization=(None if d.total_magnetization is None
                                         else round(d.total_magnetization, 3)),
                ) for d in docs]
                rows.sort(key=lambda r: (r["e_above_hull_eV_per_atom"]
                                         if r["e_above_hull_eV_per_atom"] is not None else 99))
                cache["polymorphs"][formula] = rows

                # MP's thermo endpoint returns obfuscated entry ids, so resolve the
                # rutile material_id -> entry_id mapping here while we have the key.
                rutile = next((r for r in rows if r["spacegroup_number"] == RUTILE_SPACEGROUP_NUMBER), None)
                if rutile is not None:
                    ents = mpr.get_entry_by_material_id(rutile["material_id"])
                    ids = {_mpid(e.entry_id) for e in (ents if isinstance(ents, list) else [ents])}
                    cache["material_alias"][rutile["material_id"]] = sorted(ids)
                _flush()

            for el in want_elements:
                pbx_entries = mpr.get_pourbaix_entries([el])
                cache["pourbaix"][el] = [e.as_dict() for e in pbx_entries]
                _flush()

    _flush()
    return cache


def pourbaix_from_cache(cache: dict, element: str, conc_M: float = DEFAULT_CONC_M) -> PourbaixDiagram:
    entries = [PourbaixEntry.from_dict(d) for d in cache["pourbaix"][element]]
    return PourbaixDiagram(entries, conc_dict={element: conc_M})


def entry_aliases(cache: dict, material_id: str) -> set[str]:
    """MP's thermo endpoint obfuscates entry ids, so mp-510408 arrives as e.g.
    mp-aaabdbbc. `fetch_mp` resolves the mapping while the key is in hand."""
    aliases = set(cache.get("material_alias", {}).get(material_id, []))
    aliases.add(material_id)
    return aliases


def find_cached_entry(cache: dict, element: str, material_id: str) -> PourbaixEntry | None:
    """The PourbaixEntry for one specific MP material_id, via the alias table."""
    aliases = entry_aliases(cache, material_id)
    for d in cache["pourbaix"][element]:
        if _mpid(d.get("entry_id")) in aliases:
            return PourbaixEntry.from_dict(d)
    return None


# ---------------------------------------------------------------------------
# Stage 1 - the phase-existence gate
# ---------------------------------------------------------------------------

# MP's convex hull is a 0 K, 0 atm PBE(+U) statement. It is excellent evidence
# about *structures* and poor evidence about *thermal* metastability, and for a
# few of these systems it is known to be wrong about polymorph ordering. Each
# note below is a curated literature qualifier that travels with the MP verdict
# instead of quietly overwriting it; `curated` is the call a human stands behind,
# `unverified` lists what could not be substantiated from here.
LITERATURE_NOTES = {
    "MnO2": dict(
        curated="AMBIENT_PHASE",
        note=("beta-MnO2 (pyrolusite) is the thermodynamically stable ambient MnO2 polymorph "
              "and a common ore mineral (Post, PNAS 1999, 10.1073/pnas.96.7.3447). MP's "
              "GGA+U hull places it 46 meV/atom above a C2/m polymorph (mp-644514); that "
              "inversion is a documented PBE+U failure for MnO2 polymorph energetics which "
              "SCAN repairs (Kitchaev et al., PRB 93, 045132, 10.1103/PhysRevB.93.045132). "
              "The MP verdict METASTABLE_PHASE here is a statement about the functional, "
              "not about pyrolusite."),
        unverified=[]),
    "CrO2": dict(
        curated="METASTABLE_PHASE",
        note=("rutile CrO2 is a real, once mass-produced bulk material (magnetic recording "
              "media) - Chamberland, Crit. Rev. Solid State Mater. Sci. 1977, "
              "10.1080/10408437708243431; Coey & Venkatesan, J. Appl. Phys. 2002, "
              "10.1063/1.1447879 - and MP's 0 K GGA+U hull calls it STABLE (E_hull = 0, "
              "and it is the ground-state CrO2 polymorph). It is nonetheless thermally "
              "metastable with respect to Cr2O3 + O2 and needs elevated oxygen pressure to "
              "make, which the 0 K hull cannot see. Its FM half-metal moment (4 muB per "
              "2 f.u. = 2 muB/Cr) is reproduced by MP."),
        unverified=["docs/28's 'CVD-only' is too narrow: hydrothermal and high-pressure "
                    "routes are also standard; not re-verified here"]),
    "FeO2": dict(
        curated="HYPOTHETICAL",
        note=("no FeO2 polymorph in MP is within 0.14 eV/atom of the Fe-O hull, and the "
              "rutile entry mp-850222 is theory-only (no ICSD). The pyrite-type FeO2 that "
              "docs/28 refers to is a deep-lower-mantle high-pressure phase (Hu et al., "
              "Nature 534, 241, 2016, 10.1038/nature18018); MP contains no Pa-3 FeO2 entry "
              "at all, so that phase is not even in the database this gate queries."),
        unverified=["the specific '~74 GPa' threshold in docs/28 s3 was NOT verified here - "
                    "the Hu 2016 abstract could not be read without a full-text pull. Treat "
                    "the number as unsourced; the qualitative megabar-regime claim stands"]),
    "CoO2": dict(
        curated="ABSENT",
        note=("MP holds 37 CoO2 polymorphs and none is rutile. The experimentally real CoO2 "
              "is the layered CdI2-type R-3m phase obtained by fully delithiating LiCoO2 "
              "(mp-550206, ICSD-backed, 7 meV/atom above the hull; Amatucci, Tarascon & "
              "Klein, J. Electrochem. Soc. 143, 1114, 1996, 10.1149/1.1836594)."),
        unverified=[]),
    "NiO2": dict(
        curated="ABSENT",
        note=("MP holds 15 NiO2 polymorphs and none is rutile; every one of them, including "
              "the ICSD-backed layered R-3m phases from delithiated LiNiO2 (mp-35925, "
              "mp-25210), sits >= 0.127 eV/atom above the Ni-O hull, i.e. the NiO2 "
              "stoichiometry itself is unstable to NiO + O2 at 0 K in MP."),
        unverified=[]),
    "CuO2": dict(
        curated="ABSENT",
        note=("MP holds 8 CuO2 polymorphs, none rutile, none closer than 0.18 eV/atom to the "
              "Cu-O hull. Consistent with docs/28: there is no bulk Cu(IV) dioxide."),
        unverified=["the four ICSD-tagged CuO2 entries (mp-1181499 Cmcm/icsd-15455, "
                    "mp-601195, mp-600604 Fmmm, mp-705439 Pmmm) were NOT traced back to their "
                    "ICSD records; they are most likely CuO2 sub-lattices of cuprates or "
                    "peroxide/high-pressure assignments rather than bulk CuO2, but that was "
                    "not confirmed and no claim rests on it"]),
    "RuO2": dict(curated="AMBIENT_PHASE", note="rutile RuO2 is the ground state and ICSD-backed.",
                 unverified=[]),
    "IrO2": dict(curated="AMBIENT_PHASE", note="rutile IrO2 is the ground state and ICSD-backed.",
                 unverified=[]),
}


def phase_gate(cache: dict) -> dict:
    """Per-endmember verdict on whether the RUTILE polymorph is an ambient bulk phase.

    Three MP observables carry the automated decision, in order of weight:
      1. Is there a P4_2/mnm entry for this MO2 at all? MP runs structure
         substitution across every prototype it holds, so the *absence* of a
         rutile entry after that sweep is strong evidence nobody has one.
      2. Does it carry ICSD ids (`theoretical == False`)? That means a measured
         diffraction pattern exists - the only direct evidence of existence here.
      3. energy_above_hull, which separates "on the hull" from "off it".

    Verdicts (`mp_verdict`, machine-derived):
      AMBIENT_PHASE      rutile entry, ICSD-backed, within 30 meV/atom of the hull
      METASTABLE_PHASE   rutile entry, ICSD-backed, further off the hull
      HYPOTHETICAL       rutile entry exists but is theory-only (no ICSD)
      ABSENT             MP has no rutile entry for this composition

    `curated_verdict` is the human call from LITERATURE_NOTES, kept as a separate
    field so that where DFT and experiment disagree - and for MnO2 they do - the
    disagreement is visible instead of averaged away. `realisable_electrode` uses
    the curated verdict, because that is the one about the physical world.
    """
    out: dict = {}
    for formula, meta in ENDMEMBERS.items():
        rows = cache["polymorphs"].get(formula, [])
        rutile = next((r for r in rows if r["spacegroup_number"] == RUTILE_SPACEGROUP_NUMBER), None)
        icsd_backed = [r for r in rows if not r["theoretical"]]
        ground = rows[0] if rows else None
        lit = LITERATURE_NOTES.get(formula, dict(curated=None, note="", unverified=[]))

        evidence: list[str] = []
        flags: list[str] = []
        if rutile is None:
            mp_verdict = "ABSENT"
            evidence.append(f"MP has {len(rows)} {formula} polymorph(s) and none in "
                            f"{RUTILE_SPACEGROUP} (#{RUTILE_SPACEGROUP_NUMBER})")
        else:
            evidence.append(
                f"MP {rutile['material_id']} {RUTILE_SPACEGROUP}, "
                f"E_hull = {rutile['e_above_hull_eV_per_atom']} eV/atom, "
                f"theoretical = {rutile['theoretical']}, ICSD = {rutile['icsd'] or 'none'}")
            if rutile["theoretical"]:
                mp_verdict = "HYPOTHETICAL"
            elif rutile["e_above_hull_eV_per_atom"] is not None and rutile["e_above_hull_eV_per_atom"] > 0.03:
                mp_verdict = "METASTABLE_PHASE"
            else:
                mp_verdict = "AMBIENT_PHASE"

        if ground is not None:
            evidence.append(
                f"lowest-energy {formula} polymorph in MP is {ground['material_id']} "
                f"{ground['spacegroup']} at E_hull = {ground['e_above_hull_eV_per_atom']} eV/atom "
                f"(theoretical = {ground['theoretical']}); an E_hull > 0 here means the MO2 "
                f"STOICHIOMETRY is itself unstable, in any structure")
        if icsd_backed:
            evidence.append("ICSD-backed polymorphs: " + ", ".join(
                f"{r['material_id']} {r['spacegroup']} @ {r['e_above_hull_eV_per_atom']} eV/atom"
                for r in icsd_backed[:5]))
        else:
            evidence.append("no ICSD-backed polymorph of this composition in MP at all")

        curated = lit["curated"] or mp_verdict
        if curated != mp_verdict:
            flags.append(f"MP verdict {mp_verdict} overridden to {curated} on literature grounds; "
                         f"see literature_note")
        realisable = curated in ("AMBIENT_PHASE", "METASTABLE_PHASE")
        if realisable != bool(meta["expect_rutile"]):
            flags.append(f"CONTRADICTS docs/28 s3, which asserted: {meta['asserted']}")
        for u in lit["unverified"]:
            flags.append(f"UNVERIFIED: {u}")

        out[formula] = dict(
            metal=meta["metal"], asserted_docs28=meta["asserted"],
            mp_verdict=mp_verdict, curated_verdict=curated,
            literature_note=lit["note"],
            rutile_material_id=(rutile or {}).get("material_id"),
            rutile_e_above_hull_eV_per_atom=(rutile or {}).get("e_above_hull_eV_per_atom"),
            rutile_icsd=(rutile or {}).get("icsd", []),
            rutile_is_theoretical=(rutile or {}).get("theoretical"),
            composition_min_e_above_hull_eV_per_atom=(ground or {}).get("e_above_hull_eV_per_atom"),
            n_polymorphs_in_mp=len(rows),
            realisable_electrode=realisable,
            evidence=evidence, flags=flags,
        )
    return out


# ---------------------------------------------------------------------------
# Stage 2b - MP Pourbaix for the phases that cleared the gate
# ---------------------------------------------------------------------------

# The (pH, V vs RHE) grid at which dG_pbx is quoted. 1.229 V is the OER
# equilibrium; +0.30 V is a representative operating overpotential.
OER_CONDITIONS = [
    (0.0, OER_EQUILIBRIUM_V_RHE), (0.0, OER_EQUILIBRIUM_V_RHE + OER_OPERATING_ETA_V),
    (14.0, OER_EQUILIBRIUM_V_RHE), (14.0, OER_EQUILIBRIUM_V_RHE + OER_OPERATING_ETA_V),
]
WINDOW_PH = [0.0, 7.0, 13.0, 14.0]


def mp_anchors(cache: dict, gate: dict, conc_M: float = DEFAULT_CONC_M) -> dict:
    """dG_pbx and aqueous windows on the MP PBE+U axis, gated by stage 1.

    Reported for every endmember whose rutile polymorph cleared the gate
    (AMBIENT_PHASE or METASTABLE_PHASE). HYPOTHETICAL rutiles go into a separate
    `hypothetical_structures` block that is explicitly labelled; ABSENT ones get
    no number at all, only a refusal record.
    """
    result: dict = {
        "convention": ("MP PBE+U (GGA/GGA+U, MP2020 corrections) solids + experimental "
                       "aqueous ions, Persson 2012 scheme; dG_pbx in eV/atom"),
        "dissolved_ion_concentration_M": conc_M,
        "potential_scale": "V vs RHE (converted internally to SHE via V_SHE = V_RHE - 0.0591*pH)",
        "gated": {}, "hypothetical_structures": {}, "refused": {}, "stable_phase_at_oer": {},
    }
    for formula, g in gate.items():
        element = g["metal"]
        if element not in cache["pourbaix"]:
            continue
        pbx = pourbaix_from_cache(cache, element, conc_M)

        # What the metal's aqueous chemistry actually settles on under OER - this
        # is legitimate for every element, existing rutile or not, and it is the
        # quantitative form of the "the real surface is an oxyhydroxide" thesis.
        result["stable_phase_at_oer"][element] = {
            f"pH{ph:g}_{v:.2f}VRHE": pbx.get_stable_entry(ph, float(rhe_to_she(v, ph))).name
            for ph, v in OER_CONDITIONS
        }

        mid = g["rutile_material_id"]
        entry = find_cached_entry(cache, element, mid) if mid else None
        if entry is None:
            if g["curated_verdict"] == "ABSENT":
                result["refused"][formula] = (
                    "no rutile polymorph exists (stage-1 verdict ABSENT); a dG_pbx "
                    "for it would be a number about a phase that does not exist")
            else:
                result["refused"][formula] = (
                    f"rutile {mid} is not resolvable in the cached MP Pourbaix entry set "
                    "(entry-id alias missing); refusing to substitute another polymorph")
            continue

        block = dict(
            material_id=mid, spacegroup=RUTILE_SPACEGROUP, verdict=g["curated_verdict"],
            dg_pbx_eV_per_atom={f"pH{ph:g}_{v:.2f}VRHE": round(dg_pbx_for(pbx, entry, ph, v), 4)
                                for ph, v in OER_CONDITIONS},
            windows=[stability_window(pbx, entry, ph) for ph in WINDOW_PH],
            mp_hull_polymorph=composition_domain(pbx, formula, WINDOW_PH),
        )
        if block["mp_hull_polymorph"]:
            block["mp_hull_polymorph"]["is_the_rutile_entry"] = (
                block["mp_hull_polymorph"]["entry_id"] in entry_aliases(cache, mid))
        if g["curated_verdict"] == "HYPOTHETICAL":
            block["label"] = ("MP PBE+U, HYPOTHETICAL STRUCTURE, NOT AN AMBIENT PHASE - "
                              "reported only to show the magnitude, not as a property of a material")
            result["hypothetical_structures"][formula] = block
        else:
            result["gated"][formula] = block
    return result


# ---------------------------------------------------------------------------
# Stage 2a results - beta-MnO2 on the experimental axis
# ---------------------------------------------------------------------------

def beta_mno2_report(conc_M: float = DEFAULT_CONC_M) -> dict:
    """The one physically real endmember, on the hand-entered experimental axis."""
    pbx = literature_mn_diagram(conc_M)
    mno2 = next(e for e in literature_mn_entries(conc_M)
                if e.phase_type == "Solid" and e.entry.composition.reduced_formula == "MnO2")
    windows = [stability_window(pbx, mno2, ph) for ph in WINDOW_PH]
    operating = OER_EQUILIBRIUM_V_RHE + OER_OPERATING_ETA_V
    for w in windows:
        if not w.get("stable"):
            continue
        w["oer_equilibrium_inside_window"] = bool(
            w["lower_V_rhe"] <= OER_EQUILIBRIUM_V_RHE <= w["upper_V_rhe"])
        w["operating_1p53VRHE_inside_window"] = bool(
            w["lower_V_rhe"] <= operating <= w["upper_V_rhe"])
        # The headline quantity: how much overpotential the phase survives before
        # its upper edge is crossed. Negative means it is already gone at 1.229 V.
        w["max_eta_before_upper_edge_V"] = round(w["upper_V_rhe"] - OER_EQUILIBRIUM_V_RHE, 4)
    return dict(
        phase="beta-MnO2 (pyrolusite, rutile P4_2/mnm)",
        axis="experimental Delta_Gf (298 K), hand-entered - NOT DFT",
        source=MN_GF_SOURCE,
        dissolved_ion_concentration_M=conc_M,
        concentration_sensitivity="Nernstian edges move ~59 mV per decade of dissolved-ion activity",
        solids_included=[f for f, p, _, _ in MN_GF_KJMOL if p == "solid"],
        ions_included=[f for f, p, _, _ in MN_GF_KJMOL if p == "ion"],
        known_omission="no Mn(III) oxyhydroxide (gamma-MnOOH); affects the lower edge only",
        oer_equilibrium_V_rhe=OER_EQUILIBRIUM_V_RHE,
        windows=windows,
    )


# ---------------------------------------------------------------------------
# validation - analytic Nernst lines the diagram must reproduce
# ---------------------------------------------------------------------------

def analytic_checks(conc_M: float = DEFAULT_CONC_M) -> list[dict]:
    """Two boundaries derived by hand from the same Delta_Gf table.

    If pymatgen's halfspace construction and the hand algebra disagree, one of
    them is wrong; agreement to <1 mV is the cheapest available proof that the
    hand-entered table has been wired in correctly (right sign, right units,
    right H2O reference, right concentration term).

      (1) MnO2 + 4H+ + 2e- -> Mn(2+) + 2H2O
      (2) MnO4(-) + 4H+ + 3e- -> MnO2 + 2H2O
    """
    gf = {f: g / KJMOL_PER_EV for f, _, g, _ in MN_GF_KJMOL}
    mu_h2o = -237.18 / KJMOL_PER_EV  # matches pymatgen's MU_H2O = -2.4583 eV
    log_c = np.log10(conc_M)

    # (1) n = 2, consumes 4 H+
    dg1 = (gf["Mn[+2]"] + 2 * mu_h2o) - gf["MnO2"]
    e1_0 = -dg1 / 2.0
    line1 = lambda ph: e1_0 - (PREFAC_V * 4 / 2) * ph - (PREFAC_V / 2) * log_c  # noqa: E731
    # (2) n = 3, consumes 4 H+
    dg2 = (gf["MnO2"] + 2 * mu_h2o) - gf["MnO4[-1]"]
    e2_0 = -dg2 / 3.0
    line2 = lambda ph: e2_0 - (PREFAC_V * 4 / 3) * ph + (PREFAC_V / 3) * log_c  # noqa: E731

    pbx = literature_mn_diagram(conc_M)
    mno2 = next(e for e in literature_mn_entries(conc_M)
                if e.phase_type == "Solid" and e.entry.composition.reduced_formula == "MnO2")
    out = []
    for ph in (0.0, 7.0):
        w = stability_window(pbx, mno2, ph)
        if not w.get("stable"):
            out.append(dict(pH=ph, ok=False, reason="MnO2 not stable at this pH in the diagram"))
            continue
        out.append(dict(
            pH=ph,
            lower_edge_diagram_V_she=w["lower_V_she"],
            lower_edge_analytic_V_she=round(float(line1(ph)), 4),
            lower_edge_residual_mV=round(1000 * (w["lower_V_she"] - float(line1(ph))), 3),
            upper_edge_diagram_V_she=w["upper_V_she"],
            upper_edge_analytic_V_she=round(float(line2(ph)), 4),
            upper_edge_residual_mV=round(1000 * (w["upper_V_she"] - float(line2(ph))), 3),
        ))
    return out


# ---------------------------------------------------------------------------
# figure
# ---------------------------------------------------------------------------

def _domain_map(pbx: PourbaixDiagram, ph_grid: np.ndarray, v_grid: np.ndarray,
                rhe: bool = False):
    """argmin over the stable Pourbaix planes -> (index map, ordered entry names)."""
    PH, V = np.meshgrid(ph_grid, v_grid)
    v_she = V - PREFAC_V * PH if rhe else V
    stable = list(pbx.stable_entries)
    stack = np.array([e.normalized_energy_at_conditions(PH, v_she) for e in stable])
    return np.argmin(stack, axis=0), [e.name for e in stable]


def make_figure(out_path: str, conc_M: float = DEFAULT_CONC_M) -> str:
    """Two panels of the SAME experimental diagram: SHE (classical) and RHE (catalytic).

    The RHE panel is the one that matters for OER, because on that scale the
    reversible OER potential is a horizontal line at 1.229 V and the eye can read
    off directly whether the oxide's upper edge sits above or below where the
    electrode is actually driven.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    pbx = literature_mn_diagram(conc_M)
    mno2_entry = next(e for e in literature_mn_entries(conc_M)
                      if e.phase_type == "Solid" and e.entry.composition.reduced_formula == "MnO2")
    ph = np.linspace(0, 14, 421)
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.6))

    for ax, rhe in zip(axes, (False, True)):
        v = np.linspace(-1.2, 2.4, 481) if not rhe else np.linspace(-0.6, 2.6, 481)
        idx, names = _domain_map(pbx, ph, v, rhe=rhe)
        used = sorted(set(idx.ravel().tolist()))
        cmap = plt.get_cmap("tab20")
        remap = {u: i for i, u in enumerate(used)}
        img = np.vectorize(remap.get)(idx)
        ax.imshow(img, origin="lower", aspect="auto", interpolation="nearest",
                  extent=(ph[0], ph[-1], v[0], v[-1]),
                  cmap=matplotlib.colors.ListedColormap([cmap(i % 20) for i in range(len(used))]),
                  alpha=0.75, vmin=-0.5, vmax=len(used) - 0.5)
        # outline the beta-MnO2 domain
        mask = np.array([[names[i] == "MnO2(s)" for i in row] for row in idx], dtype=float)
        ax.contour(ph, v, mask, levels=[0.5], colors="k", linewidths=2.0)

        # Water stability lines: HER at 0 V RHE and OER at 1.229 V RHE. On the SHE
        # axis both acquire the -59 mV/pH slope; on the RHE axis both are flat.
        ax.plot(ph, np.zeros_like(ph) if rhe else -PREFAC_V * ph, "k--", lw=0.9, alpha=0.6)
        if not rhe:  # on the RHE panel the OER line is drawn in red below instead
            ax.plot(ph, OER_EQUILIBRIUM_V_RHE - PREFAC_V * ph, "k--", lw=0.9, alpha=0.6)
        if rhe:
            ax.axhline(OER_EQUILIBRIUM_V_RHE, color="crimson", lw=1.7, zorder=5)
            ax.axhline(OER_EQUILIBRIUM_V_RHE + OER_OPERATING_ETA_V, color="crimson",
                       lw=1.0, ls=":", zorder=5)
            ax.text(7.2, OER_EQUILIBRIUM_V_RHE + 0.04,
                    "OER equilibrium 1.229 V; dotted = +0.30 V overpotential",
                    fontsize=8, color="crimson", ha="center", zorder=6,
                    bbox=dict(fc="white", ec="none", alpha=0.75, pad=1.2))
            # Where our own PBE+U slab says this electrode would have to be driven.
            # Same physical quantity (electrode potential), so it belongs on this
            # axis; it is an activity number and carries a +-0.3 V method error.
            u_l = OER_EQUILIBRIUM_V_RHE + 0.892
            ax.axhline(u_l, color="k", lw=1.3, ls="-.", zorder=5)
            ax.text(0.3, u_l + 0.045,
                    "$U_L$ = 2.12 V: limiting potential of our PBE+U\n"
                    r"$\beta$-MnO$_2$(110) slab ($\eta$ = 0.89 V, docs/26)",
                    fontsize=8, color="k", zorder=6)
            # annotate the two windows quoted in the text
            for ph_a, side in ((0.2, +1), (13.6, -1)):
                w = stability_window(pbx, mno2_entry, ph_a)
                if not w.get("stable"):
                    continue
                ax.annotate("", xy=(ph_a, w["upper_V_rhe"]), xytext=(ph_a, w["lower_V_rhe"]),
                            arrowprops=dict(arrowstyle="<->", color="k", lw=1.2))
                ax.text(ph_a + 0.2 * side, 0.5 * (w["lower_V_rhe"] + w["upper_V_rhe"]),
                        f"{w['width_V']:.2f} V", fontsize=8, va="center",
                        ha="left" if side > 0 else "right",
                        bbox=dict(fc="white", ec="none", alpha=0.7, pad=1.0))
            ax.set_ylabel("E (V vs RHE)")
            ax.set_title("(b) same diagram, RHE scale - the OER-relevant view")
        else:
            ax.set_ylabel("E (V vs SHE)")
            ax.set_title("(a) Mn-H$_2$O, experimental $\\Delta G_f$, 298 K")
        ax.set_xlabel("pH")
        ax.set_xlim(0, 14)
        ax.set_ylim(v[0], v[-1])

        handles = [Patch(facecolor=cmap(remap[u] % 20), edgecolor="none", alpha=0.75,
                         label=names[u]) for u in used]
        ax.legend(handles=handles, fontsize=7, loc="lower left", ncol=2, framealpha=0.9)

    fig.suptitle(r"$\beta$-MnO$_2$ (pyrolusite) aqueous stability - "
                 f"dissolved Mn at {conc_M:g} M; heavy outline = MnO$_2$(s) domain\n"
                 "hand-entered experimental $\\Delta G_f$ (NBS 1982) - NOT DFT", fontsize=10.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    return out_path


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def _print_gate(gate: dict) -> int:
    w = max(len(f) for f in gate)
    print(f"{'phase'.ljust(w)}  {'MP verdict':<17} {'curated':<17} {'rutile mp-id':<14} "
          f"{'E_hull (eV/at)':>14}  ICSD")
    contradictions = 0
    for formula, g in gate.items():
        hull = g["rutile_e_above_hull_eV_per_atom"]
        hull_s = "-" if hull is None else f"{hull:.4f}"
        print(f"{formula.ljust(w)}  {g['mp_verdict']:<17} {g['curated_verdict']:<17} "
              f"{str(g['rutile_material_id'] or '-'):<14} {hull_s:>14}  "
              f"{','.join(g['rutile_icsd'][:2]) or '-'}")
        for line in g["evidence"]:
            print(f"{' ' * w}    . {line}")
        if g["literature_note"]:
            print(f"{' ' * w}    L {g['literature_note']}")
        for line in g["flags"]:
            if line.startswith("CONTRADICTS"):
                contradictions += 1
            print(f"{' ' * w}    ! {line}")
    return contradictions


def cmd_gate(args) -> int:
    cache = fetch_mp(args.cache, args.refresh)
    return 1 if _print_gate(phase_gate(cache)) else 0


def cmd_window(args) -> int:
    rep = beta_mno2_report(args.conc)
    print(f"{rep['phase']}\naxis: {rep['axis']}\nsource: {rep['source']}")
    print(f"dissolved Mn concentration: {rep['dissolved_ion_concentration_M']:g} M "
          f"({rep['concentration_sensitivity']})\n")
    print(f"{'pH':>4} {'lower (V RHE)':>14} {'upper (V RHE)':>14} {'width':>7} "
          f"{'reduces to':>12} {'oxidises to':>13} {'max eta (V)':>12}")
    for w in rep["windows"]:
        if not w.get("stable"):
            print(f"{w['pH']:>4.0f}   NOT STABLE at any potential "
                  f"(min dG_pbx {w['min_dg_pbx_eV_per_atom']:.4f} eV/atom)")
            continue
        print(f"{w['pH']:>4.0f} {w['lower_V_rhe']:>14.3f} {w['upper_V_rhe']:>14.3f} "
              f"{w['width_V']:>7.3f} {w['reduces_to']:>12} {w['oxidises_to']:>13} "
              f"{w['max_eta_before_upper_edge_V']:>12.3f}")
    print(f"\nOER equilibrium = {OER_EQUILIBRIUM_V_RHE} V vs RHE at every pH.")
    return 0


def cmd_anchors(args) -> int:
    cache = fetch_mp(args.cache, args.refresh)
    gate = phase_gate(cache)
    res = mp_anchors(cache, gate, args.conc)
    print(f"axis: {res['convention']}\nconcentration: {res['dissolved_ion_concentration_M']:g} M\n")
    for formula, b in res["gated"].items():
        print(f"{formula}  ({b['material_id']}, {b['verdict']})")
        for k, v in b["dg_pbx_eV_per_atom"].items():
            print(f"    dG_pbx {k:>20} = {v:+.4f} eV/atom")
        for w in b["windows"]:
            if w.get("stable"):
                print(f"    window pH {w['pH']:>4.0f}: {w['lower_V_rhe']:.3f} -> "
                      f"{w['upper_V_rhe']:.3f} V RHE  ({w['reduces_to']} | {w['oxidises_to']})")
            else:
                print(f"    window pH {w['pH']:>4.0f}: none "
                      f"(min dG_pbx {w['min_dg_pbx_eV_per_atom']:.4f} eV/atom)")
        cd = b.get("mp_hull_polymorph")
        if cd and not cd.get("is_the_rutile_entry"):
            print(f"    [{formula}(s) hull polymorph {cd['entry_id']} - {cd['caveat']}]")
            for w in cd["windows"]:
                if w.get("stable"):
                    print(f"      window pH {w['pH']:>4.0f}: {w['lower_V_rhe']:.3f} -> "
                          f"{w['upper_V_rhe']:.3f} V RHE  ({w['reduces_to']} | {w['oxidises_to']})")
                else:
                    print(f"      window pH {w['pH']:>4.0f}: none")
    for formula, b in res["hypothetical_structures"].items():
        print(f"\n{formula}  [{b['label']}]")
        for k, v in b["dg_pbx_eV_per_atom"].items():
            print(f"    dG_pbx {k:>20} = {v:+.4f} eV/atom")
    print("\nREFUSED (no number produced):")
    for formula, why in res["refused"].items():
        print(f"    {formula}: {why}")
    print("\nPourbaix-stable phase at OER conditions (what the metal actually becomes):")
    for el, d in res["stable_phase_at_oer"].items():
        print(f"    {el:>3}: " + "  ".join(f"{k}={v}" for k, v in d.items()))
    return 0


def cmd_selftest(args) -> int:
    checks = analytic_checks(args.conc)
    bad = 0
    for c in checks:
        if not c.get("ok", True):
            print(f"pH {c['pH']}: FAIL - {c['reason']}")
            bad += 1
            continue
        print(f"pH {c['pH']:.0f}  lower edge: diagram {c['lower_edge_diagram_V_she']:+.4f} V "
              f"vs analytic {c['lower_edge_analytic_V_she']:+.4f} V "
              f"({c['lower_edge_residual_mV']:+.2f} mV)")
        print(f"pH {c['pH']:.0f}  upper edge: diagram {c['upper_edge_diagram_V_she']:+.4f} V "
              f"vs analytic {c['upper_edge_analytic_V_she']:+.4f} V "
              f"({c['upper_edge_residual_mV']:+.2f} mV)")
        if abs(c["lower_edge_residual_mV"]) > 2.0 or abs(c["upper_edge_residual_mV"]) > 2.0:
            bad += 1
    print("\nOK: hand-entered table reproduces the analytic Nernst lines to <2 mV"
          if not bad else "\nFAIL: diagram and hand algebra disagree")
    return 1 if bad else 0


def cmd_run(args) -> int:
    cache = fetch_mp(args.cache, args.refresh)
    gate = phase_gate(cache)
    contradictions = _print_gate(gate)
    payload = {
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "what_this_is": ("R2 aqueous-stability gate. Stage 1 (phase existence) decides "
                         "membership; stage 2 (Pourbaix) only runs on what stage 1 passes."),
        "integrity_rule": ("no dG_pbx is reported for a phase whose rutile polymorph does not "
                           "exist; experimental and MP PBE+U axes are never mixed"),
        "conventions": {
            "dissolved_ion_concentration_M": args.conc,
            "concentration_note": "all windows shift ~59 mV per decade of concentration",
            "oer_equilibrium_V_rhe": OER_EQUILIBRIUM_V_RHE,
            "rhe_conversion": "V_RHE = V_SHE + 0.0591 * pH (298 K)",
            "rutile_test": f"{RUTILE_SPACEGROUP} (#{RUTILE_SPACEGROUP_NUMBER})",
        },
        "phase_gate": gate,
        "beta_mno2_experimental": beta_mno2_report(args.conc),
        "analytic_validation": analytic_checks(args.conc),
        "mp_pbe_u": mp_anchors(cache, gate, args.conc),
        "mp_polymorph_census": cache["polymorphs"],
    }
    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    with open(args.json, "w") as fh:
        json.dump(payload, fh, indent=1)
    print(f"\n-> {args.json}")
    print(f"-> {make_figure(args.fig, args.conc)}")

    # `results/` is gitignored, so mirror the figure's numbers next to the figure -
    # the same convention parity_r0.py and volcano_r1.py use for committed results.
    sidecar = os.path.splitext(args.fig)[0] + ".json"
    with open(sidecar, "w") as fh:
        json.dump({k: payload[k] for k in
                   ("generated_utc", "conventions", "beta_mno2_experimental",
                    "analytic_validation")}, fh, indent=1)
    print(f"-> {sidecar}")
    if contradictions:
        print(f"\n{contradictions} verdict(s) contradict docs/28 s3 - see the JSON `flags` fields.")
    return 1 if contradictions else 0


def cmd_figure(args) -> int:
    print(f"-> {make_figure(args.fig, args.conc)}")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conc", type=float, default=DEFAULT_CONC_M,
                    help="dissolved-ion concentration in M (default 1e-6, the MP convention)")
    ap.add_argument("--cache", default=DEFAULT_CACHE, help="Materials Project response cache")
    ap.add_argument("--refresh", action="store_true", help="re-query MP instead of using the cache")
    ap.add_argument("--json", default=DEFAULT_JSON)
    ap.add_argument("--fig", default=DEFAULT_FIG)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn, helptext in [
        ("gate", cmd_gate, "stage 1: does the rutile polymorph exist? (needs MP)"),
        ("window", cmd_window, "beta-MnO2 aqueous window, experimental axis (offline)"),
        ("anchors", cmd_anchors, "stage 2: MP dG_pbx for the phases that cleared the gate"),
        ("selftest", cmd_selftest, "validate the hand-entered table against analytic Nernst lines"),
        ("figure", cmd_figure, "write docs/figs/pourbaix_mno2.png (offline)"),
        ("run", cmd_run, "everything; writes results/r2_stability.json + the figure"),
    ]:
        p = sub.add_parser(name, help=helptext)
        p.set_defaults(func=fn)
    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
