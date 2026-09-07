"""CHE bookkeeping for explicitly specified OER cycles, including chemical steps.

All cumulative free energies must use ONE clean-surface/H2O/H2 reference,
including appropriate entropy/solvation terms for detached species. No energy or
vibrational correction is imputed from a geometry label. This is thermodynamics,
not a kinetic mechanism or a surface-stability calculation.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path


def evaluate_cycle(document: dict, potential_rhe: float = 0.0) -> dict:
    if isinstance(potential_rhe, bool) or not isinstance(potential_rhe, (int, float)) or not math.isfinite(potential_rhe):
        raise ValueError("finite RHE potential required")
    if document.get("schema") != "oer-pathway-audit-v1":
        raise ValueError("unsupported pathway schema")
    if not isinstance(document.get("reference_id"), str) or not document["reference_id"].strip():
        raise ValueError("explicit common reference identity required")
    states = document.get("states", [])
    if not isinstance(states, list) or len(states) < 3 or not all(isinstance(s, dict) and isinstance(s.get('id'), str) for s in states):
        raise ValueError("ordered state dictionaries with string ids required")
    if len({s['id'] for s in states}) != len(states):
        raise ValueError("at least three unique ordered states required")
    for state in states:
        for key in ('delta_O', 'delta_H'):
            if type(state.get(key)) is not int:
                raise ValueError("integer atom inventories required, including released O2")
        if not isinstance(state.get('id'), str) or not state['id']:
            raise ValueError("nonempty state id required")
        if state.get('reference_id') != document['reference_id']:
            raise ValueError("mixed surface/calculator/reference identities")
        g = state.get('G0_eV')
        if g is not None and (isinstance(g, bool) or not isinstance(g, (int, float)) or not math.isfinite(g)):
            raise ValueError("energies must be finite or explicitly null")
        if g is not None and not state.get('energy_evidence'):
            raise ValueError("measured energy needs an evidence reference")
    if (states[0]['delta_O'], states[0]['delta_H']) != (0, 0) or states[0].get('G0_eV') != 0.0:
        raise ValueError("cycle must begin at the zero-reference clean surface")
    if (states[-1]['delta_O'], states[-1]['delta_H']) != (2, 0) or states[-1].get('surface_regenerated') is not True:
        raise ValueError("cycle must release O2 and regenerate the original surface")
    # 4.92 eV is the inherited CHE total at standard conditions, not a DFT O2 energy.
    if states[-1].get('G0_eV') != 4.92:
        raise ValueError("standard CHE terminal free energy must be 4.92 eV")
    steps = []
    pending = []
    chemical_uphill = []
    pcet_limits = []
    for a, b in zip(states, states[1:]):
        # H2O is the only O-bearing reactant reservoir. H+ + e- are paired;
        # inventory delta_H + electron/proton release must equal 2*water.
        water = b['delta_O'] - a['delta_O']
        ne = 2 * water - (b['delta_H'] - a['delta_H'])
        if water < 0 or ne not in (0, 1):
            raise ValueError("only forward zero/one-electron steps with water uptake supported")
        step = dict(source=a['id'], target=b['id'], water_consumed=water,
                    proton_electron_pairs_released=ne, delta_G0_eV=None, delta_G_eV=None)
        if a.get('G0_eV') is None or b.get('G0_eV') is None:
            pending.append([a['id'], b['id']])
        else:
            dg = b['G0_eV'] - a['G0_eV']
            step.update(delta_G0_eV=dg, delta_G_eV=dg - ne * potential_rhe)
            if ne:
                pcet_limits.append(dg)
            elif dg > 0:
                chemical_uphill.append([a['id'], b['id']])
        steps.append(step)
    if sum(s['water_consumed'] for s in steps) != 2 or sum(s['proton_electron_pairs_released'] for s in steps) != 4:
        raise ValueError("cycle must consume 2 H2O and release 4 proton/electron pairs")
    status = 'PENDING' if pending else 'CHEMICAL_STEP_UPHILL' if chemical_uphill else 'COMPLETE'
    limit = max(pcet_limits) if status == 'COMPLETE' else None
    return dict(schema='oer-pathway-readout-v1', reference_id=document['reference_id'],
                status=status, potential_RHE_V=potential_rhe, steps=steps,
                missing_energy_steps=pending, uphill_potential_independent_steps=chemical_uphill,
                limiting_potential_V=limit, overpotential_V=limit - 1.23 if limit is not None else None,
                interpretation='specified-cycle CHE thermodynamics; no kinetic or active-phase validation')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--json', type=Path, required=True)
    ap.add_argument('--potential-rhe', type=float, default=0.0)
    args = ap.parse_args()
    result = evaluate_cycle(json.loads(args.input.read_text(encoding='utf-8')), args.potential_rhe)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(result['status'])
    return 3 if result['status'] == 'PENDING' else 0


if __name__ == '__main__':
    raise SystemExit(main())
