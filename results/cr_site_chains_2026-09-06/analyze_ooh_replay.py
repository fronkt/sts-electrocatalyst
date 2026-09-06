"""Inspect all replayed OOH endpoints without assigning intact-OOH CHE corrections."""
from copy import deepcopy
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from ase import Atoms
from ase.constraints import FixAtoms
from ase.io import read, write
from ase.geometry import find_mic
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from scripts.screen_diagnostic import identity,sha256_file
from hea_oer.adsorbate_geometry import analyze_adsorbate_geometry


def analyze(folder, out):
    if out.exists():
        raise FileExistsError(out)
    results = {}
    pending_exports = []
    for arm in ('equiatomic','leader'):
        original_path = folder/(arm+'_result.json')
        original = json.loads(original_path.read_text(encoding='utf-8'))
        replay_path = folder/(arm+'_ooh_replay.json')
        replay = json.loads(replay_path.read_text(encoding='utf-8'))
        if replay['status'] != 'complete' or replay['attempts_sha256'] != identity(replay['attempts']):
            raise ValueError('incomplete or altered replay')
        if replay['source_result_sha256_lf'] != sha256_file(original_path,normalize_lf=True):
            raise ValueError('original result identity mismatch')
        if original['results_sha256'] != identity(original['results']) or replay['manifest_id'] != original['manifest_id']:
            raise ValueError('source result or manifest mismatch')
        if replay['model'] != original['manifest']['model'] or replay['environment'] != original['environment']:
            raise ValueError('replay model or environment mismatch')
        if {a['start'] for a in replay['attempts']} != {'builder','pull1.70','pull2.10'} or len(replay['attempts']) != 3:
            raise ValueError('OOH start coverage mismatch')
        executed_candidates = [folder/'recover_ooh_starts.py',folder/'recover_ooh_starts_recorded.py']
        executed_matches = [p.name for p in executed_candidates if p.is_file() and sha256_file(p,normalize_lf=True)==replay['script_sha256_lf']]
        if not executed_matches:
            raise ValueError('executed recovery script identity unavailable')
        row = original['results'][0]['row']
        site = row['per_site_records'][0]
        originals = {a['start']:a for a in site['start_records']['OOH']}
        baseline = min(a['energy_eV'] for a in originals.values())
        entries = []
        for attempt in replay['attempts']:
            name, geometry = attempt['start'],attempt['geometry']
            difference = attempt['energy_eV']-originals[name]['energy_eV']
            if abs(difference)>1e-8 or difference != attempt['replay_minus_original_eV'] or geometry['energy_eV'] != attempt['energy_eV']:
                raise ValueError('replay failed numerical energy match')
            copied = deepcopy(row)
            copied['per_site_records'][0]['relaxed_states']['OOH'] = geometry
            diagnostic = analyze_adsorbate_geometry(copied)['sites'][0]['states']['OOH']
            if diagnostic['geometry_status'] != 'observed':
                raise ValueError('replayed OOH coordinates cannot be inspected')
            entry = dict(start=name,energy_eV=attempt['energy_eV'],above_original_selected_eV=attempt['energy_eV']-baseline,
                         replay_minus_original_eV=difference,seconds=attempt['seconds'],geometry_diagnostic=diagnostic)
            entries.append(entry)
            if name == site['bonds']['OOH_start']:
                old = site['relaxed_states']['OOH']
                _, distances = find_mic(np.asarray(geometry['positions_A'])-np.asarray(old['positions_A']),geometry['cell_A'],pbc=geometry['pbc'])
                entry['selected_original_max_MIC_displacement_A'] = float(max(distances))
                if max(distances)>1e-6:
                    raise ValueError('selected endpoint geometry did not reproduce')
            pending_exports.append((arm,name,geometry,entry))
        results[arm] = dict(source_replay_sha256_lf=sha256_file(replay_path,normalize_lf=True),attempts=entries,seconds=replay['seconds'],executed_recovery_sha256_lf=replay['script_sha256_lf'],executed_recovery_files=executed_matches,environment_metadata_scope=replay.get('environment_scope','copied_from_initial_chain_not_runtime_measured'))
    out.mkdir(parents=True)
    for arm,name,record,entry in pending_exports:
        if record['other_constraint_types']:
            raise ValueError('unsupported constraints')
        atoms = Atoms(record['symbols'],positions=record['positions_A'],cell=record['cell_A'],pbc=record['pbc'])
        if record['fixed_atom_indices']:
            atoms.set_constraint(FixAtoms(indices=record['fixed_atom_indices']))
        target = out/(arm+'_'+name+'.extxyz')
        write(target,atoms,format='extxyz')
        recovered = read(target,format='extxyz')
        if recovered.get_chemical_symbols()!=atoms.get_chemical_symbols() or not np.array_equal(recovered.pbc,atoms.pbc) or not np.allclose(recovered.cell,atoms.cell,rtol=0,atol=1e-10) or not np.allclose(recovered.positions,atoms.positions,rtol=0,atol=6e-9):
            raise ValueError('coordinate roundtrip mismatch')
        if sorted(i for c in recovered.constraints for i in c.get_indices()) != record['fixed_atom_indices']:
            raise ValueError('constraint roundtrip mismatch')
        entry['coordinate_export'] = dict(file=target.name,sha256_lf=sha256_file(target,normalize_lf=True),roundtrip_verified=True)
    report = dict(schema='ooh-replay-readout-v1',arms=results,claims=dict(DFT_validation=False,kinetic_barrier=False,gas_production=False),
                  interpretation='All six OOH-start endpoints retain coordinates. Relative energies are model electronic endpoint energies at identical atom inventory within each arm; no intact-OOH thermochemical correction is assigned to alternative branches.',
                  source_hashes={p.name:sha256_file(p,normalize_lf=True) for p in (Path(__file__).resolve(),ROOT/'src/hea_oer/adsorbate_geometry.py',folder/'recover_ooh_starts.py')})
    (out/'readout.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',type=Path,required=True)
    parser.add_argument('--out-dir',type=Path,required=True)
    args=parser.parse_args()
    result=analyze(args.input_dir,args.out_dir)
    print(json.dumps({k:[{'start':a['start'],'relative_eV':a['above_original_selected_eV'],'distances':a['geometry_diagnostic']['distances_A']} for a in v['attempts']] for k,v in result['arms'].items()},indent=2))
