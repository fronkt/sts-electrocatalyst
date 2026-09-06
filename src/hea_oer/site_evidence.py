"""Site-level diagnostics for retained screening evidence.

Eligibility here is numerical/chemical record completeness, not a validated catalyst
ranking. Finite shared OH/O/OOH corrections are explicit scenarios only. They are applied
to every observed site before selecting a minimum; no continuous-box claim follows.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
from numbers import Real

STATES = ("OH", "O", "OOH")
TOL_EV = 1e-9
ENERGY_TOL_EV = 1e-7
TOTAL_EV = 4.92
EQUILIBRIUM_V = 1.23


def _finite(value, where):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError(f"{where}: finite real number required")
    return float(value)


def _integer(value, where, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{where}: integer >= {minimum} required")
    return value


def _steps(site, correction=None):
    values = [_finite(site["dG_" + state], "dG_" + state) for state in STATES]
    if correction is not None:
        values = [value + correction[state] for state, value in zip(STATES, values)]
    oh, oxygen, ooh = values
    steps = [oh, oxygen - oh, ooh - oxygen, TOTAL_EV - ooh]
    if not all(math.isfinite(value) for value in [*values, *steps]):
        raise ValueError("corrected energies exceed finite floating-point range")
    return steps


def _site_id(site):
    seed = _integer(site["seed"], "site seed")
    index = _integer(site["site_index"], "site index")
    return f"seed={seed}/site={index}"


def _force_quality(record, context):
    failures, unknowns = [], []
    if record is None:
        return [], [context + ": record missing"]
    if not isinstance(record, Mapping):
        return [context + ": malformed structure record"], []
    converged = record.get("converged_by_force")
    if converged is False:
        failures.append(context + ": force convergence failed")
    elif converged is not True and converged is not None:
        failures.append(context + ": malformed convergence flag")
    elif converged is None:
        unknowns.append(context + ": force convergence unknown")
    measured = record.get("max_constrained_force_eV_A")
    target = record.get("fmax_target_eV_A")
    for value, name, positive in ((measured, "maximum force", False),
                                  (target, "force target", True)):
        if value is None:
            unknowns.append(context + ": " + name + " missing")
        elif (isinstance(value, bool) or not isinstance(value, Real)
              or not math.isfinite(value) or value < 0 or (positive and value == 0)):
            failures.append(context + ": invalid " + name)
    if not failures and measured is not None and target is not None and measured >= target:
        failures.append(context + ": measured force does not meet target")
    energy = record.get("energy_eV")
    if energy is None:
        unknowns.append(context + ": absolute energy missing")
    elif isinstance(energy, bool) or not isinstance(energy, Real) or not math.isfinite(energy):
        failures.append(context + ": invalid absolute energy")
    if record.get("other_constraint_types"):
        unknowns.append(context + ": unsupported constraint types need review")
    return failures, unknowns


def _energy_consistency(site, structures, bare, gas_records):
    failures, unknowns = [], []
    records = {"slab": bare, **{state: structures.get(state) for state in STATES},
               **{gas: gas_records.get(gas) for gas in ("H2O", "H2")}}
    energies = {}
    for name, record in records.items():
        if isinstance(record, Mapping):
            value = record.get("energy_eV")
            if (isinstance(value, Real) and not isinstance(value, bool)
                    and math.isfinite(value)):
                energies[name] = float(value)
    aliases = site.get("energies_eV")
    if aliases is not None:
        if not isinstance(aliases, Mapping):
            failures.append("malformed energies_eV")
        else:
            for name in records:
                if aliases.get(name) is None:
                    unknowns.append(name + ": raw energy alias missing")
                    continue
                try:
                    value = _finite(aliases[name], name + " raw energy")
                except ValueError:
                    failures.append(name + ": invalid raw energy alias")
                    continue
                if name in energies and abs(value - energies[name]) > ENERGY_TOL_EV:
                    failures.append(name + ": raw energy alias disagrees with structure record")
    if len(energies) == len(records):
        h2o, h2 = energies["H2O"], energies["H2"]
        references = {"OH": h2o - .5 * h2, "O": h2o - h2, "OOH": 2 * h2o - 1.5 * h2}
        offsets = {"OH": .35, "O": .05, "OOH": .40}
        for state in STATES:
            derived = energies[state] - energies["slab"] - references[state] + offsets[state]
            if not math.isfinite(derived) or abs(derived - site["dG_" + state]) > ENERGY_TOL_EV:
                failures.append(state + ": adsorption free energy disagrees with absolute energies")
    return failures, unknowns


def _attempt_summary(site):
    records = site.get("start_records")
    if not isinstance(records, Mapping):
        return dict(available=False, reason="Attempt-level records absent or malformed.",
                    interpretation="Selected-chain eligibility does not certify an exhaustive basin search.")
    counts = {"eligible": 0, "failed": 0, "unknown": 0}
    per_state, missing_states = {}, []
    for state in STATES:
        attempts = records.get(state)
        if not isinstance(attempts, list) or not attempts:
            missing_states.append(state)
            per_state[state] = None
            continue
        statuses = []
        for attempt in attempts:
            failures, unknowns = _force_quality(attempt, state + " attempted start")
            status = "failed" if failures else "unknown" if unknowns else "eligible"
            counts[status] += 1
            distance = attempt.get("bond_length_A") if isinstance(attempt, Mapping) else None
            distance_known = (isinstance(distance, Real) and not isinstance(distance, bool)
                              and math.isfinite(distance) and distance > 0)
            statuses.append(dict(
                start=attempt.get("start") if isinstance(attempt, Mapping)
                and isinstance(attempt.get("start"), str) else None,
                numerical_status=status,
                desorption_distance_flag=bool(distance >= 3) if distance_known else None,
            ))
        per_state[state] = statuses
    return dict(available=True, numerical_status_counts=counts,
                missing_states=missing_states, by_state=per_state,
                interpretation="Descriptive attempted-start coverage. A failed nonwinning start may hide a lower basin; selected-chain eligibility is unchanged and does not certify a global minimum.")


def _binding_identity(site):
    initial = site.get("initial_binding_metal_index")
    valid_index = lambda value: isinstance(value, int) and not isinstance(value, bool) and value >= 0
    if not valid_index(initial):
        initial = None
    structures = site.get("relaxed_states", {})
    if not isinstance(structures, Mapping):
        structures = {}
    final = {}
    for state in STATES:
        record = structures.get(state)
        if not isinstance(record, Mapping):
            record = {}
        index = record.get("final_binding_metal_index")
        final[state] = dict(index=index if valid_index(index) else None,
                            metal=record.get("final_binding_metal")
                            if isinstance(record.get("final_binding_metal"), str) else None)
    indices = [record["index"] for record in final.values() if record["index"] is not None]
    cross_state = True if len(set(indices)) > 1 else False if len(indices) == 3 else None
    migrated = [state for state, record in final.items()
                if initial is not None and record["index"] is not None and record["index"] != initial]
    if cross_state is True:
        status = "different_final_binding_partners"
    elif initial is None or len(indices) < 3:
        status = "unknown"
    elif migrated:
        status = "all_states_migrated_from_initial_site"
    else:
        status = "same_binding_index_for_all_states"
    return dict(status=status, initial_index=initial,
                initial_metal=site.get("initial_binding_metal")
                if isinstance(site.get("initial_binding_metal"), str) else None,
                final_by_state=final, cross_state_final_indices_differ=cross_state,
                migrated_states=migrated,
                interpretation="Binding-partner diagnostic only. Migration does not by itself invalidate energies; a local single-site mechanism remains unverified.")


def _quality(site, decoration, gas_records):
    failures, unknowns = [], []
    structures = site.get("relaxed_states", {})
    if not isinstance(structures, Mapping):
        failures.append("malformed relaxed_states")
        structures = {}
    for state in STATES:
        bad, absent = _force_quality(structures.get(state), state)
        failures.extend(bad)
        unknowns.extend(absent)
    bare = None if decoration is None else decoration.get("relaxed_slab")
    if isinstance(bare, Mapping) and "energy_eV" not in bare and decoration.get("energy_eV") is not None:
        bare = dict(bare, energy_eV=decoration["energy_eV"])
    bad, absent = _force_quality(bare, "clean slab")
    failures.extend(bad)
    unknowns.extend(absent)
    if gas_records is None:
        gas_records = {}
    if not isinstance(gas_records, Mapping):
        failures.append("malformed gas_reference_records")
        gas_records = {}
    for gas in ("H2O", "H2"):
        bad, absent = _force_quality(gas_records.get(gas), gas)
        failures.extend(bad)
        unknowns.extend(absent)
    bad, absent = _energy_consistency(site, structures, bare, gas_records)
    failures.extend(bad)
    unknowns.extend(absent)
    desorbed = site.get("desorbed")
    if desorbed is None:
        unknowns.append("desorption flags missing")
    elif not isinstance(desorbed, list) or any(state not in STATES for state in desorbed):
        failures.append("malformed desorption flags")
    elif desorbed:
        failures.append("selected adsorbate state desorbed: " + ", ".join(desorbed))
    bonds = site.get("bonds", {})
    if not isinstance(bonds, Mapping):
        failures.append("malformed bond record")
        bonds = {}
    for state in STATES:
        distance = bonds.get(state)
        if distance is None:
            unknowns.append(state + ": M-O distance missing")
        elif (isinstance(distance, bool) or not isinstance(distance, Real)
              or not math.isfinite(distance) or distance <= 0):
            failures.append(state + ": invalid M-O distance")
        elif distance >= 3.0:
            failures.append(state + ": M-O distance reaches desorption cut")
    status = "failed" if failures else "unknown" if unknowns else "eligible"
    return dict(status=status, failures=failures, unknowns=unknowns)


def _minimum(values):
    if not values:
        return None
    minimum = min(values.values())
    return dict(minimum_eta_V=minimum,
                winners=[name for name, value in values.items() if value <= minimum + TOL_EV])


def _leave_out(values, site_seeds, all_seeds):
    result = {}
    for seed in all_seeds:
        remaining = {name: eta for name, eta in values.items() if site_seeds[name] != seed}
        result[str(seed)] = _minimum(remaining)
    return result


def analyze_site_evidence(row, corrections):
    """Analyze a retained screen row without replacing its legacy winner.

    Requires an explicit correction sequence with exactly label/OH/O/OOH per item.
    An empty sequence requests baseline-only analysis.
    A label identifies a scenario, not a calibrated interval. Ties within 1e-9 V
    are retained. Duplicate identities or inconsistent CHE values raise ValueError.
    Incomplete declared sampling coverage is disclosed and suppresses the secondary
    eligible-only minimum; all observed-site arithmetic remains a labeled diagnostic.

    Eligibility requires complete clean/adsorbate/gas force and energy records and
    no desorption flag. Unknown gas QC remains unknown. This does not validate the
    imposed surface, mechanism, binding-site identity, or physical model accuracy.
    """
    if not isinstance(row, Mapping):
        raise ValueError("row must be a mapping")
    if row.get("formula") is not None and not isinstance(row["formula"], str):
        raise ValueError("formula must be a string if supplied")
    records = row.get("per_site_records")
    decorations = row.get("decoration_records")
    if not isinstance(records, list) or not records:
        raise ValueError("nonempty per_site_records required")
    if not isinstance(decorations, list) or not decorations:
        raise ValueError("nonempty decoration_records required")
    declared_sites = _integer(row.get("n_sites"), "n_sites", 1)
    declared_decorations = _integer(row.get("n_decorations"), "n_decorations", 1)
    legacy_eta = _finite(row.get("eta"), "legacy eta")
    if not isinstance(corrections, Sequence) or isinstance(corrections, (str, bytes)):
        raise ValueError("explicit correction sequence required")
    scenarios, labels = [], set()
    for correction in corrections:
        if not isinstance(correction, Mapping) or set(correction) != {"label", *STATES}:
            raise ValueError("each correction requires exactly label, OH, O, OOH")
        label = correction["label"]
        if not isinstance(label, str) or not label.strip() or label in labels:
            raise ValueError("correction labels must be nonempty and distinct")
        labels.add(label)
        scenarios.append(dict(label=label, **{state: _finite(correction[state], label + "." + state)
                                             for state in STATES}))
    by_seed = {}
    for decoration in decorations:
        if not isinstance(decoration, Mapping):
            raise ValueError("each decoration must be a mapping")
        seed = _integer(decoration.get("seed"), "decoration seed")
        if seed in by_seed:
            raise ValueError("duplicate decoration seed")
        by_seed[seed] = decoration
    sites, site_seeds, baseline_values = {}, {}, {}
    for site in records:
        if not isinstance(site, Mapping):
            raise ValueError("each site must be a mapping")
        name = _site_id(site)
        if name in sites:
            raise ValueError("duplicate site identity: " + name)
        steps = _steps(site)
        eta = max(steps) - EQUILIBRIUM_V
        if abs(eta - _finite(site.get("eta"), name + " eta")) > TOL_EV:
            raise ValueError(name + ": reported eta disagrees with CHE")
        pls = _integer(site.get("pls"), name + " pls", 1)
        if pls > 4 or abs(steps[pls - 1] - max(steps)) > TOL_EV:
            raise ValueError(name + ": reported PLS disagrees with CHE")
        sites[name], site_seeds[name], baseline_values[name] = site, site["seed"], eta
    sites = dict(sorted(sites.items(), key=lambda item: (item[1]["seed"], item[1]["site_index"])))
    site_seeds = {name: site_seeds[name] for name in sites}
    baseline_values = {name: baseline_values[name] for name in sites}
    observed_seeds = sorted(set(site_seeds.values()))
    issues = []
    if len(sites) != declared_sites:
        issues.append("site count differs from declared sampling")
    if len(by_seed) != declared_decorations:
        issues.append("decoration count differs from declared sampling")
    if set(observed_seeds) != set(by_seed):
        issues.append("site and decoration seed rosters differ")
    expected_per_seed = declared_sites // declared_decorations if declared_sites % declared_decorations == 0 else None
    if expected_per_seed is None:
        issues.append("declared total is not balanced across decorations")
    else:
        for seed in by_seed:
            indices = {site["site_index"] for site in sites.values() if site["seed"] == seed}
            if indices != set(range(expected_per_seed)):
                issues.append(f"seed {seed}: site indices do not cover declared balanced sampling")
    coverage = dict(complete=not issues, declared_n_sites=declared_sites,
                    observed_n_sites=len(sites), declared_n_decorations=declared_decorations,
                    observed_n_decorations=len(by_seed), expected_sites_per_decoration=expected_per_seed,
                    issues=issues,
                    interpretation="Counts and indices only; a frozen run manifest must identify the intended seeds.")
    baseline = _minimum(baseline_values)
    if coverage["complete"] and abs(baseline["minimum_eta_V"] - legacy_eta) > TOL_EV:
        raise ValueError("legacy eta disagrees with complete observed-site minimum")
    original_winners = [name for name, eta in baseline_values.items() if abs(eta - legacy_eta) <= TOL_EV]
    quality = {name: _quality(site, by_seed.get(site["seed"]), row.get("gas_reference_records"))
               for name, site in sites.items()}
    counts = {status: sum(item["status"] == status for item in quality.values())
              for status in ("eligible", "failed", "unknown")}
    eligible = {name for name, item in quality.items() if item["status"] == "eligible"}
    seeds = sorted(set(by_seed) | set(observed_seeds))

    def scenario_report(label, correction):
        values, details = {}, []
        for name, site in sites.items():
            steps = _steps(site, correction)
            eta = max(steps) - EQUILIBRIUM_V
            values[name] = eta
            details.append(dict(site_id=name, seed=site["seed"], site_index=site["site_index"],
                                eta_V=eta, che_steps_eV=steps,
                                potential_limiting_steps=[i + 1 for i, step in enumerate(steps)
                                                          if step >= max(steps) - TOL_EV]))
        all_minimum = _minimum(values)
        eligible_values = {name: eta for name, eta in values.items() if name in eligible}
        secondary = _minimum(eligible_values) if coverage["complete"] else None
        overlap = sorted(set(original_winners) & set(all_minimum["winners"]))
        return dict(
            label=label, correction_eV=correction, site_values=details,
            all_observed_sites=all_minimum,
            legacy_winners_remaining=overlap,
            all_legacy_winners_lost=(not overlap) if original_winners and coverage["complete"] else None,
            legacy_winner_gap_V=(max(0.0, min(values[name] for name in original_winners) -
                                      all_minimum["minimum_eta_V"]) if original_winners else None),
            leave_one_decoration_out_all_observed=_leave_out(values, site_seeds, seeds),
            eligible_only_secondary=dict(
                result=secondary, eligible_sites=len(eligible_values),
                declared_sites=declared_sites, sampling_coverage_complete=coverage["complete"],
                all_declared_sites_eligible=coverage["complete"] and len(eligible_values) == declared_sites,
                leave_one_decoration_out=(_leave_out(eligible_values, site_seeds, seeds)
                                           if coverage["complete"] else None),
                interpretation="Secondary minimum on eligible observed sites only; never a replacement candidate ranking."),
        )

    zero = {state: 0.0 for state in STATES}
    return dict(
        schema_version=1, formula=row.get("formula"), tie_tolerance_V=TOL_EV,
        energy_consistency_tolerance_eV=ENERGY_TOL_EV,
        analysis="explicit_site_correction_scenarios", continuous_certificate=False,
        confidence_interval=False, performance_certification=False,
        coverage=coverage, quality_counts=counts,
        sites=[dict(site_id=name, seed=sites[name]["seed"], site_index=sites[name]["site_index"],
                    binding_identity=_binding_identity(sites[name]),
                    attempted_starts=_attempt_summary(sites[name]),
                    **quality[name]) for name in sites],
        legacy=dict(reported_eta_V=legacy_eta, recovered_winners=original_winners,
                    preserved=True, interpretation="Original all-site minimum is retained regardless of quality status."),
        baseline=scenario_report("baseline", zero),
        scenarios=[scenario_report(item["label"], {state: item[state] for state in STATES})
                   for item in scenarios],
        interpretation=("Corrections are shared across every site within each explicit scenario. "
                        "Recomputed winning motifs, rejected/unknown records and incomplete coverage "
                        "remain visible. No scenario frequency is a probability."),
    )
