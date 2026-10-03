"""Bounded offline rebuild after explicit, source-verified scientific rulings."""
import json
import pathlib
import sys
import unittest
import urllib.request
import importlib.util

HERE=pathlib.Path(__file__).resolve().parent
FT=HERE.parent
sys.path.insert(0,str(FT))
from prepare_sources import retain,jsonbytes,sha

class ForbiddenNetwork(BaseException):
    pass

def no_network(*args,**kwargs):
    raise ForbiddenNetwork('This evidence reconciliation is offline')

def main():
    urllib.request.urlopen=no_network
    baseline=json.loads((HERE/'baseline.json').read_text(encoding='utf-8'))
    gate=json.loads((HERE/'source_read_gate.json').read_text(encoding='utf-8'))
    assert len(gate['records'])==5
    from recovery_state import recovery_decisions
    from verify_evidence_recovery import validate_recovery_evidence
    decisions=recovery_decisions()
    assert {r['screen_id'] for r in gate['records']}<=set(decisions)
    errors,hashes,reads=validate_recovery_evidence(decisions)
    assert not errors,errors
    for entry in gate['records']:
        assert entry['identity_verified'] is True and entry['si_complete_for_read'] is True
        source=entry['source_pins'][1]
        original=FT/source['file']
        assert sha(original)==source['sha256']
        suffix=original.suffix
        retain(FT/'files_si'/(entry['screen_id']+'_SI1'+suffix),original.read_bytes())
        retain(FT/'text_si'/(entry['screen_id']+'.txt'),(FT/entry['si_text']).read_bytes())
    output=HERE/'scientific_final_checked'
    output.mkdir(exist_ok=True)
    codebase=HERE/'code_validation_checked'
    codebase.mkdir(exist_ok=True)
    amended=json.loads(json.dumps(baseline))
    before=amended['files']['recovery_state.py']
    after=sha(FT/'recovery_state.py')
    assert before!=after
    amended['files']['recovery_state.py']=after
    before_git=json.loads((HERE/'implementation_before_git.json').read_text(encoding='utf-8'))
    assert before_git['git_head']==baseline['git_head']
    test_before=before_git['sha256']
    test_after=sha(FT/'test_recovery_state.py')
    amended['files']['test_recovery_state.py']=test_after
    retain(codebase/'baseline.json',jsonbytes(amended))
    retain(codebase/'implementation_pins.json',jsonbytes({'changes':[{'file':'recovery_state.py','before':before,'after':after},{'file':'test_recovery_state.py','before':test_before,'after':test_after}],'scope':'One additive priority-SI ruling layer and isolated/additivity regression coverage; original and failed-attempt baselines retained for phase verifier'}))
    import current_state,si_checklist,verify_evidence_recovery,verify_si_round
    rebuilt=('reconcile/current_state.csv','reconcile/current_state.json','si_checklist.csv','si_checklist.html')
    runs=[]
    for _ in range(2):
        current_state.main()
        saved=sys.argv
        try:
            sys.argv=['si_checklist.py','--ids','S29721,S10090,S22807,S26024']
            si_checklist.main()
        finally:
            sys.argv=saved
        runs.append({name:sha(FT/name) for name in rebuilt})
    assert runs[0]==runs[1],runs
    retain(output/'deterministic_rebuild.json',jsonbytes({'runs':runs,'network_disabled':True,'forced_ids':['S29721','S10090','S22807','S26024']}))
    loader=unittest.TestLoader()
    suite=unittest.TestSuite()
    for directory in (FT,FT/'download_si_review_2026-10-02',HERE):
        suite.addTests(loader.discover(str(directory),pattern='test_*.py'))
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    retain(output/'regression.json',jsonbytes({'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful()}))
    assert result.wasSuccessful()
    verify_evidence_recovery.main(baseline_dir=codebase,output_dir=output)
    verify_si_round.AUDIT=output/'si_round_verification.json'
    verify_si_round.main(require_audits=True)
    phase_spec=importlib.util.spec_from_file_location('priority_si_phase_verification',HERE/'verify_phase.py')
    phase_module=importlib.util.module_from_spec(phase_spec)
    phase_spec.loader.exec_module(phase_module)
    assert phase_module.PHASE.resolve()==HERE.resolve()
    phase_module.main()
    print('Offline five-package scientific verification complete')

if __name__=='__main__':
    main()
