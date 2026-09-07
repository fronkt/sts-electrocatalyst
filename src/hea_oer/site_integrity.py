"""Site-integrity classification of retained screen-diagnostic-v1 site records.

Every relaxed adsorbate state (OH, O, OOH) in a ``per_site_records`` entry is classified
on pre-stated geometric criteria (docs/91 readout (b)): a metal-oxygen bond tier taken from
the adsorbate oxygen nearest a metal, the O-O class and the hydrogen location for OOH, and
one anomaly category after the AdsorbML / CatBench taxonomies (NORMAL, MIGRATION,
DISSOCIATION, DESORPTION, RECONSTRUCTION). Distances are periodic minimum-image distances
computed with ase. Force convergence of the state is carried into INTACT.

The module also carries the pathway bookkeeping of docs/91 readout (c). Both pathways are
four electrochemical steps under the computational hydrogen electrode with the O2 release
booked as 4.92 eV minus the third state's free energy:

    cus     * -> *OH -> *O -> *OOH      -> O2(g)     step 4 = 4.92 - dG(*OOH)
    bridge  * -> *OH -> *O -> *O2 + H_b -> O2(g)     step 4 = 4.92 - dG(*O2 + H_b)

(Svane and Rossmeisl, Angew. Chem. Int. Ed. 61 (2022) e202201146: the proton of *OH or
*OOH moves to a neighbouring bridging oxygen, giving *O + H_b and *O2 + H_b). The retained
"OOH" energy of an H-TRANSFERRED site IS E(*O2 + H_b), and the retained "OH" energy of an
H-TRANSFERRED OH state IS E(*O + H_b), each with the screen's OOH / OH ZPE-TS correction;
the four-step arithmetic is therefore the same for both pathways and only the label
changes. No *O2 intermediate enters the pathway energetics: referencing a bare *O2 fragment
through the H2O/H2 cycle would re-import the model's O2-molecule error that the
4.92 eV convention removes (hea_oer.referencing). A CENSUS-1b *O2 record, when supplied
together with the same model's O2 gas energy, is booked only as a fragment-binding
diagnostic (``o2_fragment_diagnostic``).

Nothing here changes eligibility, ranking or any banked value; the sealed modules are not
imported, so drift in their hashes cannot reach this file.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
import math
from numbers import Real

import numpy as np
from ase import Atoms

STATES = ("OH", "O", "OOH")
#: Appended-atom order of the retained adsorbate states (surfaces_rutile builder,
#: mol_index = 0 -> the O placed on the metal first; docs/site-evidence-continuation-2026-09-06.md:29).
#: The names are positional (build order); binding is decided by distance, not by position.
APPENDED = {"OH": ("proximal_O", "H"), "O": ("proximal_O",), "OOH": ("proximal_O", "distal_O", "H")}
ADSORBATE_O = {"OH": ("proximal_O",), "O": ("proximal_O",), "OOH": ("proximal_O", "distal_O")}
METALS = frozenset({"Al", "Ti", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Ru", "Ir"})

#: CHE constants, identical to hea_oer.descriptors / hea_oer.site_evidence.
TOTAL_EV = 4.92
EQUILIBRIUM_V = 1.23
#: ZPE - TS corrections of the screen (hea_oer.referencing, Man et al. 2011).
ZPE_TS = {"OH": 0.35, "O": 0.05, "OOH": 0.40}
#: Proposed correction for a bare *O2 fragment in the binding diagnostic (docs/91 (c)).
ZPE_TS_O2_DEFAULT = 0.05

CATEGORIES = ("NORMAL", "MIGRATION", "DISSOCIATION", "DESORPTION", "RECONSTRUCTION")
O_O_CLASSES = ("O2_LIKE", "SUPEROXO_LIKE", "OOH_LIKE", "OO_CLEAVED")
PATHWAYS = ("cus", "bridge", "undefined")


def _finite(value):
    return isinstance(value, Real) and not isinstance(value, (bool, np.bool_)) and math.isfinite(value)


@dataclass(frozen=True)
class IntegrityThresholds:
    """Geometric criteria (angstrom). Inherited: the M-O tiers. Proposed (docs/91 (b) slots):
    the O-O bands, the O-H bond window and the per-atom reconstruction displacement."""
    #: M-O tiers: bound < 2.20, weak [2.20, 3.00), desorbed >= 3.00 (docs/33:317-322;
    #: hea_oer.data.M_O_DESORBED_MIN = 3.00). Inherited.
    bound_max_A: float = 2.20
    desorbed_min_A: float = 3.00
    #: O-O bands for OOH: O2_LIKE <= 1.28; SUPEROXO_LIKE (1.28, 1.36]; OOH_LIKE (1.36, 1.60];
    #: OO_CLEAVED > 1.60. Proposed.
    o2_like_max_A: float = 1.28
    superoxo_like_max_A: float = 1.36
    ooh_like_max_A: float = 1.60
    #: H counts as bonded to an oxygen when within this distance of it. Proposed.
    h_bond_max_A: float = 1.15
    #: Largest single free-slab-atom minimum-image displacement from the relaxed clean slab
    #: above which the state is RECONSTRUCTION (CatBench's 0.5 A per-atom displacement
    #: threshold; RMS is reported beside it and decides nothing). Proposed.
    reconstruction_max_A: float = 0.50
    #: Two candidate nearest metals closer than this are reported as a tie, not a migration.
    tie_tolerance_A: float = 1e-6

    def __post_init__(self):
        for name, value in asdict(self).items():
            if not _finite(value) or value <= 0:
                raise ValueError(name + " must be finite and positive")
        if not self.bound_max_A < self.desorbed_min_A:
            raise ValueError("bound_max_A must be below desorbed_min_A")
        if not self.o2_like_max_A < self.superoxo_like_max_A < self.ooh_like_max_A:
            raise ValueError("O-O windows must be ordered")


DEFAULT_THRESHOLDS = IntegrityThresholds()


def atoms_from_record(record) -> Atoms:
    """Rebuild an ase Atoms object from a retained structure record (symbols, positions_A, cell_A, pbc)."""
    if not isinstance(record, Mapping):
        raise ValueError("structure record must be a mapping")
    missing = [k for k in ("symbols", "positions_A", "cell_A", "pbc") if record.get(k) is None]
    if missing:
        raise ValueError("retained geometry missing: " + ", ".join(missing))
    symbols = list(record["symbols"])
    positions = np.asarray(record["positions_A"], dtype=float)
    cell = np.asarray(record["cell_A"], dtype=float)
    pbc = [bool(x) for x in record["pbc"]]
    if positions.shape != (len(symbols), 3) or cell.shape != (3, 3):
        raise ValueError("positions_A / cell_A have the wrong shape")
    if not np.isfinite(positions).all() or not np.isfinite(cell).all():
        raise ValueError("nonfinite coordinates")
    return Atoms(symbols=symbols, positions=positions, cell=cell, pbc=pbc)


def _nearest(atoms, source, candidates, tie):
    """Nearest candidate index to `source` by minimum-image distance, with tie detection."""
    if not candidates:
        return None, None, []
    d = np.asarray(atoms.get_distances(source, candidates, mic=True), dtype=float)
    order = np.argsort(d, kind="stable")
    best = float(d[order[0]])
    tied = [int(candidates[i]) for i in order if d[i] <= best + tie]
    return int(candidates[order[0]]), best, tied


def bond_tier(m_o_A, thresholds=DEFAULT_THRESHOLDS):
    if not _finite(m_o_A) or m_o_A <= 0:
        raise ValueError("M-O distance must be finite and positive")
    if m_o_A < thresholds.bound_max_A:
        return "bound"
    if m_o_A < thresholds.desorbed_min_A:
        return "weak"
    return "desorbed"


def o_o_class(o_o_A, thresholds=DEFAULT_THRESHOLDS):
    if not _finite(o_o_A) or o_o_A <= 0:
        raise ValueError("O-O distance must be finite and positive")
    if o_o_A <= thresholds.o2_like_max_A:
        return "O2_LIKE"
    if o_o_A <= thresholds.superoxo_like_max_A:
        return "SUPEROXO_LIKE"
    if o_o_A <= thresholds.ooh_like_max_A:
        return "OOH_LIKE"
    return "OO_CLEAVED"


def slab_displacement(state_atoms, clean_atoms, n_slab, fixed_indices):
    """Per-atom minimum-image displacement of the slab atoms from the relaxed clean slab:
    RMS and maximum over the free atoms, maximum over the fixed atoms."""
    if len(clean_atoms) != n_slab:
        raise ValueError("clean slab atom count differs from the adsorbate state's slab")
    if list(clean_atoms.get_chemical_symbols()) != list(state_atoms.get_chemical_symbols())[:n_slab]:
        raise ValueError("clean slab symbols differ from the adsorbate state's slab")
    fixed = set(int(i) for i in fixed_indices)
    free = [i for i in range(n_slab) if i not in fixed]
    delta = state_atoms.positions[:n_slab] - clean_atoms.positions
    # Minimum-image convention in the state's cell (cells are identical by construction).
    from ase.geometry import find_mic
    mic, lengths = find_mic(delta, state_atoms.cell, state_atoms.pbc)
    lengths = np.asarray(lengths, dtype=float)
    fixed_max = float(lengths[sorted(fixed)].max()) if fixed else 0.0
    free_lengths = lengths[free] if free else np.zeros(0)
    rms = float(np.sqrt(np.mean(free_lengths ** 2))) if len(free_lengths) else 0.0
    free_max_index = int(np.asarray(free)[int(np.argmax(free_lengths))]) if len(free_lengths) else None
    return dict(free_atom_rms_A=rms,
                free_atom_max_A=float(free_lengths.max()) if len(free_lengths) else 0.0,
                free_atom_max_index=free_max_index,
                fixed_atom_max_A=fixed_max, n_free=len(free), n_fixed=len(fixed))


def classify_state(species, state_record, initial_metal_index, clean_slab_record=None,
                   thresholds=DEFAULT_THRESHOLDS):
    """Classify one relaxed adsorbate state. Returns a JSON-serialisable dict.

    `initial_metal_index` is the cus metal the site was enumerated on
    (per_site_records[].initial_binding_metal_index); `clean_slab_record` is the matching
    decoration's relaxed clean slab (decoration_records[].relaxed_slab). Without it the
    RECONSTRUCTION test is reported as unknown (None) and cannot fire.

    The M-O tier is taken from whichever adsorbate oxygen lies nearest a metal (both
    distances are reported under `m_o_by_O_A`), so a flipped OOH whose H-bearing oxygen
    binds the metal is tiered on that oxygen and not on the build-order "proximal" atom.
    """
    if species not in STATES:
        raise ValueError("unknown species: " + str(species))
    atoms = atoms_from_record(state_record)
    n_ads = len(APPENDED[species])
    n_slab = len(atoms) - n_ads
    if n_slab <= 0:
        raise ValueError("state has fewer atoms than its adsorbate")
    symbols = atoms.get_chemical_symbols()
    expected = [{"proximal_O": "O", "distal_O": "O", "H": "H"}[name] for name in APPENDED[species]]
    if symbols[n_slab:] != expected:
        raise ValueError(f"{species}: appended atoms are {symbols[n_slab:]}, expected {expected}")
    idx = {name: n_slab + k for k, name in enumerate(APPENDED[species])}
    metals = [i for i in range(n_slab) if symbols[i] in METALS]
    slab_o = [i for i in range(n_slab) if symbols[i] == "O"]
    if not metals or not slab_o:
        raise ValueError("slab lacks metal or oxygen atoms")
    tie = thresholds.tie_tolerance_A

    # Metal contact of every adsorbate oxygen; the binding oxygen is the nearer one.
    contacts = {}
    for name in ADSORBATE_O[species]:
        m_index, m_o, m_tied = _nearest(atoms, idx[name], metals, tie)
        contacts[name] = dict(metal_index=m_index, metal=symbols[m_index], distance_A=m_o, tied_indices=m_tied)
    binding_O = min(contacts, key=lambda name: contacts[name]["distance_A"])
    binding = contacts[binding_O]
    m_o = binding["distance_A"]
    out = dict(
        species=species, n_slab_atoms=n_slab, adsorbate_indices=idx,
        binding_O=binding_O, binding_O_index=idx[binding_O],
        m_o_by_O_A={name: c["distance_A"] for name, c in contacts.items()},
        nearest_metal_by_O={name: c["metal_index"] for name, c in contacts.items()},
        binding_metal_index=binding["metal_index"], binding_metal=binding["metal"],
        binding_metal_tied_indices=binding["tied_indices"], m_o_A=m_o,
        bond_tier=bond_tier(m_o, thresholds),
        initial_metal_index=int(initial_metal_index) if initial_metal_index is not None else None,
        initial_metal=symbols[int(initial_metal_index)] if initial_metal_index is not None else None,
    )
    out["migration"] = (None if initial_metal_index is None else
                        bool(int(initial_metal_index) not in binding["tied_indices"]))

    # Hydrogen location and O-O class.
    out["o_o_A"] = None
    out["o_o_class"] = None
    out["h_location"] = None
    out["h_carrier"] = None
    out["h_to_carrier_O_A"] = None
    out["h_nearest_slab_O_index"] = None
    out["h_nearest_slab_O_A"] = None
    dissociation = False
    if species == "OOH":
        out["o_o_A"] = float(atoms.get_distance(idx["proximal_O"], idx["distal_O"], mic=True))
        out["o_o_class"] = o_o_class(out["o_o_A"], thresholds)
        if out["o_o_class"] == "OO_CLEAVED":
            dissociation = True
    if "H" in idx:
        h = idx["H"]
        # Nearest adsorbate oxygen to the H (for OH there is one).
        h_to_O = {name: float(atoms.get_distance(h, idx[name], mic=True)) for name in ADSORBATE_O[species]}
        carrier = min(h_to_O, key=h_to_O.__getitem__)
        d_carrier = h_to_O[carrier]
        s_index, s_dist, _ = _nearest(atoms, h, slab_o, tie)
        out["h_nearest_slab_O_index"] = s_index
        out["h_nearest_slab_O_A"] = s_dist
        if d_carrier <= thresholds.h_bond_max_A:
            out["h_location"] = "ON_ADSORBATE"
            out["h_to_carrier_O_A"] = d_carrier
            if species == "OOH":
                out["h_carrier"] = "binding_O" if carrier == binding_O else "terminal_O"
            else:
                out["h_carrier"] = "binding_O"
        elif s_dist is not None and s_dist <= thresholds.h_bond_max_A:
            out["h_location"] = "H_TRANSFERRED"
            out["h_carrier"] = "slab_O"
            out["h_to_carrier_O_A"] = s_dist
            dissociation = True
        else:
            out["h_location"] = "H_FREE"
            out["h_to_carrier_O_A"] = d_carrier
            dissociation = True
    out["dissociation"] = dissociation

    # Reconstruction against the relaxed clean slab of the same decoration.
    out["slab_displacement"] = None
    out["reconstruction"] = None
    if clean_slab_record is not None:
        clean = atoms_from_record(clean_slab_record)
        fixed = state_record.get("fixed_atom_indices") or clean_slab_record.get("fixed_atom_indices") or []
        disp = slab_displacement(atoms, clean, n_slab, fixed)
        out["slab_displacement"] = disp
        out["reconstruction"] = bool(disp["free_atom_max_A"] > thresholds.reconstruction_max_A)

    out["category"] = primary_category(out)
    out["converged_by_force"] = state_record.get("converged_by_force")
    out["energy_eV"] = state_record.get("energy_eV")
    converged = out["converged_by_force"] is True
    # INTACT: category NORMAL (so not desorbed; weak counts) and force-converged.
    out["intact"] = bool(out["category"] == "NORMAL" and converged)
    # Adsorbate-only integrity: the reconstruction flag is ignored (reported beside).
    out["adsorbate_intact"] = bool(out["bond_tier"] != "desorbed" and not dissociation
                                   and not out["migration"] and converged)
    # Pathway state label for the CHE bookkeeping of readout (c).
    out["pathway_state"] = pathway_state(out)
    return out


def pathway_state(flags):
    """The intermediate a relaxed state stands for in the four-step bookkeeping:
    OH -> '*OH' or '*O+H_b'; O -> '*O'; OOH -> '*OOH', '*O2+H_b' or 'undefined'."""
    species = flags["species"]
    if species == "O":
        return "*O"
    if flags["bond_tier"] == "desorbed" or flags["h_location"] == "H_FREE" or flags.get("o_o_class") == "OO_CLEAVED":
        return "undefined"
    if species == "OH":
        return "*O+H_b" if flags["h_location"] == "H_TRANSFERRED" else "*OH"
    return "*O2+H_b" if flags["h_location"] == "H_TRANSFERRED" else "*OOH"


def primary_category(flags):
    """One category per state, in fixed priority: DESORPTION > DISSOCIATION > MIGRATION >
    RECONSTRUCTION > NORMAL. All flags stay in the record; the category is a label."""
    if flags["bond_tier"] == "desorbed":
        return "DESORPTION"
    if flags.get("dissociation"):
        return "DISSOCIATION"
    if flags.get("migration"):
        return "MIGRATION"
    if flags.get("reconstruction"):
        return "RECONSTRUCTION"
    return "NORMAL"


def site_pathway(states):
    """'cus' when the OOH state is *OOH, 'bridge' when it is *O2+H_b, else 'undefined'
    (missing state, desorbed fragment, free H or cleaved O-O)."""
    ooh = states.get("OOH")
    if ooh is None:
        return "undefined"
    return {"*OOH": "cus", "*O2+H_b": "bridge"}.get(ooh["pathway_state"], "undefined")


def classify_site(site, decoration_records=None, thresholds=DEFAULT_THRESHOLDS):
    """Classify the three relaxed states of one per_site_records entry.

    `decoration_records` (the row's list) supplies the relaxed clean slab of the site's seed.
    """
    seed = site["seed"]
    clean = None
    for record in decoration_records or []:
        if record.get("seed") == seed:
            clean = record.get("relaxed_slab")
            if clean is not None and "energy_eV" not in clean and record.get("energy_eV") is not None:
                clean = dict(clean, energy_eV=record["energy_eV"])
            break
    initial = site.get("initial_binding_metal_index")
    states = {}
    for species in STATES:
        record = (site.get("relaxed_states") or {}).get(species)
        if record is None:
            states[species] = None
            continue
        states[species] = classify_state(species, record, initial, clean, thresholds)
    present = [s for s in states.values() if s is not None]
    complete = len(present) == 3
    return dict(
        seed=seed, site_index=site.get("site_index"), site_xy_A=site.get("site_xy_A"),
        initial_binding_metal_index=initial, initial_binding_metal=site.get("initial_binding_metal"),
        eta_V=site.get("eta"), pls=site.get("pls"),
        dG_OH=site.get("dG_OH"), dG_O=site.get("dG_O"), dG_OOH=site.get("dG_OOH"),
        states=states,
        all_states_intact=bool(complete and all(s["intact"] for s in present)),
        all_states_adsorbate_intact=bool(complete and all(s["adsorbate_intact"] for s in present)),
        n_unconverged_states=sum(1 for s in present if s["converged_by_force"] is not True) + (3 - len(present)),
        n_weak_states=sum(1 for s in present if s["bond_tier"] == "weak"),
        n_reconstructed_states=sum(1 for s in present if s["reconstruction"]),
        categories={species: (None if s is None else s["category"]) for species, s in states.items()},
        pathway_states={species: (None if s is None else s["pathway_state"]) for species, s in states.items()},
        pathway=site_pathway(states),
        ooh_h_transferred=bool(states["OOH"] is not None and states["OOH"]["h_location"] == "H_TRANSFERRED"),
        thresholds=asdict(thresholds),
    )


def classify_row(row, thresholds=DEFAULT_THRESHOLDS):
    """Classify every site of a screen-diagnostic-v1 result row (results[].row)."""
    sites = [classify_site(site, row.get("decoration_records"), thresholds)
             for site in row.get("per_site_records", [])]
    return dict(formula=row.get("formula"), n_sites=len(sites), sites=sites,
                n_all_states_intact=sum(1 for s in sites if s["all_states_intact"]),
                n_all_states_adsorbate_intact=sum(1 for s in sites if s["all_states_adsorbate_intact"]),
                n_unconverged_sites=sum(1 for s in sites if s["n_unconverged_states"]),
                n_bridge_sites=sum(1 for s in sites if s["pathway"] == "bridge"),
                n_undefined_pathway_sites=sum(1 for s in sites if s["pathway"] == "undefined"),
                thresholds=asdict(thresholds))


# ----------------------------------------------------------------------------------------
# Pathway CHE bookkeeping (docs/91 readout (c)).
# ----------------------------------------------------------------------------------------

def four_step_pathway(dG_1, dG_2, dG_3):
    """Four-step CHE on three referenced state free energies: steps
    [dG_1, dG_2 - dG_1, dG_3 - dG_2, 4.92 - dG_3]; returns (steps_eV, eta_V, pls)."""
    steps = [dG_1, dG_2 - dG_1, dG_3 - dG_2, TOTAL_EV - dG_3]
    if not all(_finite(s) for s in steps):
        raise ValueError("nonfinite step energies")
    top = max(steps)
    return steps, top - EQUILIBRIUM_V, steps.index(top) + 1


def cus_pathway(dG_OH, dG_O, dG_OOH):
    """Conventional pathway * -> *OH -> *O -> *OOH -> O2(g)."""
    return four_step_pathway(dG_OH, dG_O, dG_OOH)


def bridge_pathway(dG_1, dG_O, dG_O2Hb):
    """Bridge pathway after Svane and Rossmeisl 2022: * -> (*OH or *O+H_b) -> *O -> *O2+H_b
    -> O2(g), the fourth step *O2 + H_b -> O2(g) + * + H+ + e- booked as 4.92 - dG(*O2+H_b).
    Returns dict(steps_eV, eta_V, pls, states)."""
    steps, eta, pls = four_step_pathway(dG_1, dG_O, dG_O2Hb)
    return dict(steps_eV=steps, eta_V=eta, pls=pls, states=["state1", "*O", "*O2+H_b", "O2(g)"])


def o2_fragment_diagnostic(o2_record, energies, dG_O2Hb, zpe_ts_O2=ZPE_TS_O2_DEFAULT):
    """Fragment-binding diagnostic from a CENSUS-1b *O2 record (H removed from *O2+H_b and
    re-relaxed) and the SAME model's relaxed O2 gas energy; it enters no pathway rule.

    o2_record: {"energy_eV": E(*O2), "E_O2_gas_eV": E(O2, model), "converged_by_force": bool}
    energies: the site's energies_eV (needs "slab").
    Returns dG_ads_O2_eV = E(*O2) - E_slab - E_O2 + zpe_ts_O2 (negative = bound), the
    reference-cancelled alternative booking dG(*O2) = 4.92 + dG_ads_O2 with its H_b
    deprotonation step dG(*O2) - dG(*O2+H_b) and release -dG_ads_O2, all labelled diagnostic.
    """
    if o2_record.get("converged_by_force") is not True:
        return dict(status="unconverged_O2_record")
    for key in ("energy_eV", "E_O2_gas_eV"):
        if not _finite(o2_record.get(key)):
            raise ValueError("O2 record lacks finite " + key)
    if not _finite(energies.get("slab")):
        raise ValueError("site energies_eV lacks slab")
    if not _finite(zpe_ts_O2) or not _finite(dG_O2Hb):
        raise ValueError("nonfinite energy")
    dG_ads = o2_record["energy_eV"] - energies["slab"] - o2_record["E_O2_gas_eV"] + zpe_ts_O2
    dG_O2 = TOTAL_EV + dG_ads
    return dict(status="computed", dG_ads_O2_eV=dG_ads, zpe_ts_O2_eV=zpe_ts_O2,
                dG_O2_reference_cancelled_eV=dG_O2, hb_deprotonation_step_eV=dG_O2 - dG_O2Hb,
                o2_release_eV=-dG_ads, role="diagnostic; enters no ranking rule")


def two_pathway_site(site, classification=None, o2_record=None, zpe_ts_O2=ZPE_TS_O2_DEFAULT):
    """Per-site pathway readout on the retained dG_OH, dG_O, dG_OOH.

    The four-step eta is the same arithmetic under both labels (the retained third-state
    energy is E(*OOH) or E(*O2 + H_b) as the geometry says); `pathway` comes from the
    classification ('cus', 'bridge' or 'undefined'; 'cus' when no classification is given).
    An `o2_record` adds the fragment-binding diagnostic and changes no eta.
    Returns dict(pathway, steps_eV, eta_V, pls, states, o2_fragment).
    """
    steps, eta, pls = four_step_pathway(site["dG_OH"], site["dG_O"], site["dG_OOH"])
    pathway = "cus" if classification is None else classification["pathway"]
    if classification is None:
        states = ["*OH", "*O", "*OOH"]
    else:
        ps = classification["pathway_states"]
        states = [ps.get("OH"), ps.get("O"), ps.get("OOH")]
    out = dict(pathway=pathway, steps_eV=steps, eta_V=eta, pls=pls, states=states, o2_fragment=None)
    if o2_record is not None:
        out["o2_fragment"] = o2_fragment_diagnostic(o2_record, site.get("energies_eV") or {},
                                                    site["dG_OOH"], zpe_ts_O2)
    return out


def ranking_rules(rows_by_formula, classifications, o2_records=None, zpe_ts_O2=ZPE_TS_O2_DEFAULT):
    """Composition-level eta under the pre-stated rules of docs/91 readout (c), each a
    minimum over the sites supplied (the ranking site set is the caller's; docs/91 fixes it
    to the twelve CENSUS-1 sites).

    rows_by_formula: {formula: screen-diagnostic-v1 row}; classifications: {formula:
    classify_row(row)}; o2_records: {formula: {(seed, site_index): record}} or None
    (diagnostic only). Returns per formula: banked (min over all sites, the screen's own
    aggregation), intact_only, adsorbate_intact_only, two_pathway (min over sites whose
    pathway is cus or bridge), the counts, and the O2-fragment diagnostics.
    """
    out = {}
    for formula, row in rows_by_formula.items():
        sites = row.get("per_site_records", [])
        cls = classifications[formula]["sites"]
        if len(cls) != len(sites):
            raise ValueError("classification / site count mismatch for " + formula)
        etas = [s["eta"] for s in sites]
        intact = [s["eta"] for s, c in zip(sites, cls) if c["all_states_intact"]]
        ads_intact = [s["eta"] for s, c in zip(sites, cls) if c["all_states_adsorbate_intact"]]
        two, diagnostics = [], {}
        for s, c in zip(sites, cls):
            record = None
            if o2_records and formula in o2_records:
                record = o2_records[formula].get((s["seed"], s["site_index"]))
            per = two_pathway_site(s, c, record, zpe_ts_O2)
            if per["pathway"] in ("cus", "bridge"):
                # The retained site eta IS the four-step value on the retained dG; it is
                # used as retained so that no number is re-rounded.
                two.append(s["eta"])
            if per["o2_fragment"] is not None:
                diagnostics[f"{s['seed']}/{s['site_index']}"] = per["o2_fragment"]
        out[formula] = dict(
            banked=min(etas) if etas else None,
            intact_only=min(intact) if intact else None,
            adsorbate_intact_only=min(ads_intact) if ads_intact else None,
            two_pathway=min(two) if two else None,
            n_sites=len(etas), n_intact_sites=len(intact), n_adsorbate_intact_sites=len(ads_intact),
            n_pathway_defined_sites=len(two),
            n_bridge_sites=sum(1 for c in cls if c["pathway"] == "bridge"),
            n_undefined_pathway_sites=sum(1 for c in cls if c["pathway"] == "undefined"),
            n_unconverged_sites=sum(1 for c in cls if c["n_unconverged_states"]),
            n_weak_sites=sum(1 for c in cls if c["n_weak_states"]),
            n_reconstructed_sites=sum(1 for c in cls if c["n_reconstructed_states"]),
            o2_fragment_diagnostics=diagnostics,
        )
    return out


RULES = ("banked", "intact_only", "adsorbate_intact_only", "two_pathway")


def kendall_tau(order_a, order_b):
    """Kendall tau-a between two total orders given as lists of the same labels."""
    if sorted(order_a) != sorted(order_b) or len(set(order_a)) != len(order_a):
        raise ValueError("orders must be permutations of one another")
    rank_b = {label: k for k, label in enumerate(order_b)}
    n = len(order_a)
    concordant = discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            sign = rank_b[order_a[i]] - rank_b[order_a[j]]
            if sign < 0:
                concordant += 1
            elif sign > 0:
                discordant += 1
    pairs = n * (n - 1) / 2
    return (concordant - discordant) / pairs if pairs else float("nan")


# ----------------------------------------------------------------------------------------
# Site-eta distribution statistics (docs/91 readout (f)).
# ----------------------------------------------------------------------------------------

def eta_statistics(values):
    """n, mean, sample standard deviation (ddof = 1; None when n < 2), median, 10th
    percentile (numpy linear interpolation), minimum and maximum of a list of site eta."""
    x = np.asarray([v for v in values if _finite(v)], dtype=float)
    n = int(len(x))
    if n == 0:
        return dict(n=0, mean=None, std=None, median=None, p10=None, min=None, max=None)
    return dict(n=n, mean=float(x.mean()), std=float(x.std(ddof=1)) if n > 1 else None,
                median=float(np.median(x)), p10=float(np.percentile(x, 10)),
                min=float(x.min()), max=float(x.max()))


def expected_minimum_curve(values, ks=(1, 2, 3, 4, 6, 12, 24, 48, 96, 120)):
    """Exact expected minimum of k draws WITHOUT replacement from the empirical site set:
    E[min_k] = sum_i x_(i) C(n-i, k-1) / C(n, k) over the ascending order statistics
    x_(1..n) (1-based i). Returned for every k in `ks` with k <= n."""
    x = np.sort(np.asarray([v for v in values if _finite(v)], dtype=float))
    n = len(x)
    out = []
    for k in ks:
        if k < 1 or k > n:
            continue
        denom = math.comb(n, k)
        expect = sum(float(x[i - 1]) * math.comb(n - i, k - 1) for i in range(1, n + 1)) / denom
        out.append(dict(k=int(k), expected_min=expect))
    return out
