"""Replay evidence must match energies, retained selected coordinates and executed code."""
import importlib.util
import json
from pathlib import Path
import shutil
import pytest
ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'results/cr_site_chains_2026-09-06'

@pytest.fixture
def module():
    spec=importlib.util.spec_from_file_location('ooh_replay_readout',BANK/'analyze_ooh_replay.py')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_relative_input_path_and_all_six_endpoints(module,tmp_path,monkeypatch):
    monkeypatch.chdir(ROOT)
    output=module.analyze(Path('results/cr_site_chains_2026-09-06'),tmp_path/'readout')
    assert all(v is False for v in output['claims'].values())
    entries=[a for arm in output['arms'].values() for a in arm['attempts']]
    assert len(entries)==6
    assert max(abs(a['replay_minus_original_eV']) for a in entries)<2e-13
    selected=[a for a in entries if 'selected_original_max_MIC_displacement_A' in a]
    assert len(selected)==2
    assert all(a['selected_original_max_MIC_displacement_A']==0 for a in selected)
    assert all(a['coordinate_export']['roundtrip_verified'] for a in entries)
    assert all(arm['environment_metadata_scope']=='copied_from_initial_chain_not_runtime_measured' for arm in output['arms'].values())


@pytest.mark.parametrize('mutation,match',[('geometry','selected endpoint geometry did not reproduce'),('script','executed recovery script identity unavailable')])
def test_resealed_replay_corruption_is_rejected(module,tmp_path,mutation,match):
    folder=tmp_path/'input'
    folder.mkdir()
    for name in ['equiatomic_result.json','leader_result.json','equiatomic_ooh_replay.json','leader_ooh_replay.json','recover_ooh_starts.py','recover_ooh_starts_recorded.py']:
        shutil.copyfile(BANK/name,folder/name)
    target=folder/'equiatomic_ooh_replay.json'
    data=json.loads(target.read_text())
    if mutation=='geometry':
        data['attempts'][2]['geometry']['positions_A'][-1][0]+=.01
        data['attempts_sha256']=module.identity(data['attempts'])
    else:
        data['script_sha256_lf']='0'*64
    target.write_text(json.dumps(data))
    out=tmp_path/'out'
    with pytest.raises(ValueError,match=match):
        module.analyze(folder,out)
    assert not out.exists()
