"""Fresh offline schema regression, raw replay and historical preservation."""
import copy,hashlib,importlib.util,json,subprocess,sys,unittest,urllib.request
from pathlib import Path
PHASE=Path(__file__).resolve().parent;ROOT=PHASE.parents[1]
FT=ROOT/'results/s2_2026-09-25/full_text'
EDITABLE={'src/dft/pa_qe_adapter.py','tests/test_pa_qe_adapter.py','tasks/todo.md'}
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def preserve():
 baseline=json.loads((PHASE/'baseline.json').read_text())
 checked=0
 for row in baseline['tracked_pins']+baseline['unrelated_pins']:
  if row['path'] in EDITABLE:continue
  p=ROOT/row['path'];assert p.is_file() and p.stat().st_size==row['bytes'] and digest(p)==row['sha256'],'unrelated/historical drift: '+row['path']
  checked+=1
 return {'unchanged_historical_files':len(baseline['tracked_pins'])-len(EDITABLE),'unchanged_unrelated_files':len(baseline['unrelated_pins']),'checked_files':checked,'errors':[]}
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def run(args,timeout=400):
 p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout,creationflags=0x08000000)
 return {'args':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def main(label):
 assert label in {'initial','checked'}
 target=PHASE/('verification_'+label+'.json');assert not target.exists()
 r={'successful':False,'scope':'OFFLINE_XML_REPAIR_ONLY','new_jobs_submitted':0,'qe_executed':False,'complete_trial_pass':False,'production_accepted':False,'label':label}
 try:
  r['before']=preserve()
  files=['src/dft/pa_qe_adapter.py','tests/test_pa_qe_adapter.py','tests/test_pa_qe_schema_repair.py','src/dft/pa_catalyst_trial.py','results/pa_xml_repair_2026-10-04/replay_control.py']
  r['code_pins']={p:digest(ROOT/p) for p in files}
  def offline(*a,**k):raise RuntimeError('verification refuses URL requests')
  urllib.request.urlopen=offline;sys.path.insert(0,str(FT))
  suite=unittest.TestSuite()
  for directory in [FT,FT/'download_si_review_2026-10-02',FT/'download_si_review_2026-10-03',ROOT/'results/pa_integration_2026-10-03']:
   suite.addTests(unittest.TestLoader().discover(str(directory),pattern='test_*.py'))
  result=unittest.TextTestRunner(verbosity=1).run(suite)
  r['evidence_tests']={'tests_run':result.testsRun,'successful':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors)}
  tests=['tests/test_pa_qe_adapter.py','tests/test_pa_qe_schema_repair.py','tests/test_pa_catalyst_trial.py','tests/test_pa_catalyst_watch.py','tests/test_pa_checked_contract.py','tests/test_pa_restart_diagnostic.py','tests/test_pa_tiny_restart_probe.py','tests/test_pa_tiny_raw_readout.py','tests/test_pa_tiny_readonly_watch.py','tests/test_research_batch_checked.py','tests/test_research_batch_seeded.py','tests/test_lowtail_batch_launch.py','results/pa_catalyst_trial_readout_prep_2026-10-04/test_readout_trial.py']
  # Historical readout citations intentionally refer to the frozen launch code,
  # not this repaired source path. Verify that exact test separately on the
  # byte-identical retained launch snapshot instead of altering its line counts.
  readout=load('repair_frozen_readout_'+label,ROOT/'results/pa_catalyst_trial_readout_prep_2026-10-04/readout_trial.py')
  criteria=copy.deepcopy(readout.CRITERIA)
  for criterion in criteria.values():
   for cite in criterion['cites']:
    if cite['file']=='src/dft/pa_qe_adapter.py':cite['file']='results/pa_xml_repair_2026-10-04/launch_adapter_original.py'
  citations=readout.check_citations(ROOT,criteria)
  assert citations and all(x['status']=='EXACT' for x in citations),citations
  assert all(x['cites'] for x in readout.CRITERIA.values())
  assert all(x['kind'] in (readout.KIND_STATED,readout.KIND_FROZEN) for x in readout.CRITERIA.values())
  assert digest(PHASE/'launch_adapter_original.py')=='255464215aa898d0c9d34317a1be9b16fb27ba6d35108e0ca78215331a628879'
  r['frozen_readout_citation_test']={'passed':True,'launch_adapter_sha256':digest(PHASE/'launch_adapter_original.py'),'citations':citations,'current_repaired_path_deliberately_not_substituted_for_launch_source':True}
  controller=load('repair_unchanged_controller_'+label,ROOT/'src/dft/pa_catalyst_trial.py')
  lines=(ROOT/readout.CTRL).read_text(encoding='utf-8').splitlines()
  for name,registered in readout.REGISTERED.items():
   window=' '.join(lines[registered['site']-1:registered['site']+1])
   assert 'self.execute("%s", kind="%s"' % (name,registered['kind']) in window,name
   assert 'expected_cycles=%s' % registered['expected_cycles'] in window,name
   assert 'expected_steps=%d' % registered['expected_steps'] in window,name
  assert readout.PREFIX==controller.PREFIX and readout.LOG_XML_ENERGY_TOL_RY==5.1e-8
  assert '5.1e-8' in (PHASE/'launch_adapter_original.py').read_text(encoding='utf-8').splitlines()[844]
  r['frozen_registered_call_table_test']={'passed':True,'controller_unchanged':True,'adapter_literal_line845_checked_on_exact_launch_snapshot':True,'launch_adapter_sha256':digest(PHASE/'launch_adapter_original.py')}
  r['compute_and_readout_tests']=run([sys.executable,'-B','-m','pytest','-q','-p','no:cacheprovider','--deselect=results/pa_catalyst_trial_readout_prep_2026-10-04/test_readout_trial.py::test_every_citation_resolves_exactly_in_the_pinned_files','--deselect=results/pa_catalyst_trial_readout_prep_2026-10-04/test_readout_trial.py::test_registered_call_table_matches_controller_source',*tests])
  print(r['compute_and_readout_tests']['stdout'],flush=True)
  assert result.wasSuccessful() and r['compute_and_readout_tests']['returncode']==0,'fresh regression failed'
  r['raw_replay']=run([sys.executable,'-B',str(PHASE/'replay_control.py'),label]);print(r['raw_replay']['stdout'],flush=True)
  assert r['raw_replay']['returncode']==0,'actual raw replay failed'
  scientific=load('schema_repair_scientific_'+label,FT/'verify_evidence_recovery.py')
  output=PHASE/('scientific_'+label);output.mkdir(exist_ok=False)
  evidence=scientific.main(baseline_dir=FT/'download_si_review_2026-10-03/code_validation_checked',output_dir=output)
  rounds=load('schema_repair_rounds_'+label,FT/'verify_si_round.py');rounds.AUDIT=output/'si_round_verification.json';rounds.main(require_audits=True)
  r['scientific_verifiers_pass']=True;r['registered_recovery_reads']=evidence['independent_reads']
  assert r['code_pins']=={p:digest(ROOT/p) for p in files},'code changed during verification'
  r['after']=preserve();r['successful']=True
 except BaseException as exc:r['error']=repr(exc);raise
 finally:target.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in r.items() if k not in {'compute_and_readout_tests','raw_replay','code_pins'}},indent=2),flush=True)
if __name__=='__main__':main(sys.argv[1])
