"""Prepare pre-DFT benchmark rows from a frozen HEA geometry snapshot.

No DFT labels or ensemble spreads are imputed. These rows are not a new ranking.
Only OH/O/OOH slots enter this adsorbate diagnostic; slab references stay in the
geometry snapshot. Geometry is a predictor, never the benchmark truth label.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from dft.hea_validation_plan import identity, read_json, validate_plan, write_new
from hea_oer.site_integrity import classify_state, DEFAULT_THRESHOLDS
from hea_oer.failure_benchmark import validate, evaluate
from dataclasses import asdict

SPLITS = {'discovery': 'discovery', 'targeted_audit': 'audit', 'heldout_dft_labels': 'heldout'}


def prepare(plan: dict, snapshot: dict) -> tuple[dict, dict]:
    validate_plan(plan)
    if snapshot.get('schema') != 'hea-dft-validation-geometries-v1' or snapshot.get('plan_id') != plan['plan_id']:
        raise ValueError('snapshot does not belong to this plan')
    if snapshot.get('snapshot_id') != identity({k: v for k, v in snapshot.items() if k != 'snapshot_id'}):
        raise ValueError('snapshot identity mismatch')
    expected = {slot['slot_id']: slot for slot in plan['slots']}
    if len(snapshot['slots']) != len(expected) or {s['slot_id'] for s in snapshot['slots']} != set(expected):
        raise ValueError('snapshot changed slot denominator')
    cases, evidence = [], []
    for slot in snapshot['slots']:
        original = expected[slot['slot_id']]
        if any(slot[k] != original[k] for k in ('formula', 'split', 'arm', 'selector')):
            raise ValueError('snapshot changed selected identity')
        initial = slot.get('initial_binding_metal_index')
        clean_state = slot['states']['slab']
        clean = clean_state.get('geometry') if clean_state['status'] == 'ready' else None
        if clean is not None and clean_state.get('geometry_sha256') != identity(clean):
            raise ValueError('clean-slab geometry content hash mismatch')
        for species in ('OH', 'O', 'OOH'):
            case_id = slot['slot_id'] + '__' + species
            state = slot['states'][species]
            features = dict(converged=None, geometry_status=None, ensemble_spread_ev=None)
            classification = None
            if state['status'] == 'ready':
                geometry = state['geometry']
                if state['geometry_sha256'] != identity(geometry):
                    raise ValueError('geometry content hash mismatch')
                converged = state.get('converged_by_force')
                if converged is not None and type(converged) is not bool:
                    raise ValueError('converged_by_force must be boolean or null')
                features['converged'] = converged
                record = dict(geometry, converged_by_force=converged, energy_eV=state.get('energy_eV'))
                classification = classify_state(species, record, initial, clean)
                if classification['category'] != 'NORMAL':
                    features['geometry_status'] = 'changed'
                elif initial is None or clean is None or classification['bond_tier'] == 'weak':
                    features['geometry_status'] = 'ambiguous'
                else:
                    features['geometry_status'] = 'intact'
            cases.append(dict(case_id=case_id, composition_id=slot['formula'], group_id=slot['formula'],
                split=SPLITS[slot['split']], features=features, truth=None, ranking=None))
            evidence.append(dict(case_id=case_id, state=species, status=state['status'],
                geometry_sha256=state.get('geometry_sha256'), classification=classification))
    payload = dict(schema='screen-failure-benchmark-v1', protocol_id=plan['plan_id'],
        truth_criterion_id='paired-state-reference-error-0p10eV-v1', ranking_tolerance_ev=0.05, cases=cases)
    validate(payload)
    return payload, dict(schema='screen-failure-feature-evidence-v1', plan_id=plan['plan_id'],
        snapshot_id=snapshot['snapshot_id'], thresholds=asdict(DEFAULT_THRESHOLDS), cases=evidence,
        notes=['Every DFT truth remains null until independent reference checks pass.',
               'Ensemble spread remains null; one available model is not zero disagreement.',
               'Geometry flags are predictors, not proof of an incorrect state or pathway.',
               'ranking_tolerance_ev is reserved for future comparable reaction-energy pairs; no ranking values here.'])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan', type=Path, required=True)
    ap.add_argument('--snapshot', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    args = ap.parse_args(argv)
    payload, evidence = prepare(read_json(args.plan), read_json(args.snapshot))
    report = evaluate(payload)
    targets = {args.out_dir / 'benchmark_input.json': payload,
               args.out_dir / 'feature_evidence.json': evidence,
               args.out_dir / 'benchmark_pending_report.json': report}
    if any(path.exists() for path in targets):
        raise ValueError('refusing to overwrite benchmark snapshot')
    for path, content in targets.items():
        write_new(path, content)
    print(json.dumps(dict(status=report['status'], n_cases=len(payload['cases']),
        n_geometry_features=sum(c['features']['geometry_status'] is not None for c in payload['cases']))))
    return 3 if report['status'] == 'PENDING' else 0


if __name__ == '__main__':
    raise SystemExit(main())
