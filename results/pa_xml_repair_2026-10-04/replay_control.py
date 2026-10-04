"""Replay only retained actual control/tiny evidence; never run a solver."""
import hashlib,importlib.util,json,re,sys
from pathlib import Path
PHASE=Path(__file__).resolve().parent;ROOT=PHASE.parents[1]
MIRROR=ROOT/'results/pa_catalyst_trial_readout_2026-10-04/mirror'
ARM=MIRROR/'trial_results/control';PREFIX='slab_c5low__pa_boundary'
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'src/dft'))
SHAPE={'nprocs':128,'nthreads':1,'ntasks':1,'nbgrp':1,'npool':8,'ndiag':16}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def mirror_pins():
 inventory=json.loads((MIRROR.parent/'remote_inventory.json').read_text())['files']
 by_path={r['path']:r for r in inventory};records=[]
 for p in sorted(MIRROR.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(MIRROR).as_posix();row=by_path[rel]
  assert p.stat().st_size==row['bytes'] if 'bytes' in row else p.stat().st_size==row['size']
  assert sha(p)==row['sha256'],'actual control mirror pin drift: '+rel
  records.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p)})
 assert len(records)==19
 return records
def expected(adapter):
 spec=json.loads((ROOT/'results/pa_catalyst_trial_2026-10-03/launch_spec.json').read_text())
 source=ROOT/'runs/hea/lowtail_low_state_restart_2026-09-22/Cu8Cr23Mn35Co34__s20_site2/slab_c5low__relax.in'
 deck=adapter.parse_deck(source,spec['source_deck']['sha256'])
 deck['upf_pins']={Path(p['path']).name:p['sha256'] for p in spec['upfs']}
 text=(ARM/'stdout.log').read_text(encoding='utf-8',errors='replace')
 deck['upf_read_path_map']={m.group(1).strip():str(MIRROR/'trial_results/common_pseudo'/Path(m.group(1).strip()).name) for m in re.finditer(r'PseudoPot\.\s*#\s*\d+\s+for\s+\S+\s+read from file:[ \t]*\n?[ \t]*([^\r\n]+)',text)}
 return deck
def control(adapter):
 deck=expected(adapter);process=json.loads((ARM/'process_receipt.json').read_text())
 assert not process.get('timed_out') and process['within_per_call_cap'] is True
 assert not any(process.get(k) for k in ['supervisor_error','capture_error','failure_marker_observed','HEA4_stall_observed','solver_limit_observed'])
 assert process['stop_reason']=='registered-evaluated-boundary' and process['stop_observed_cycles']==[1,2,3]
 assert not list(MIRROR.rglob('*.EXIT'))
 parsed=adapter.read_qe_arm(ARM/'input.in',ARM/'stdout.log',ARM/'stderr.log',ARM/'outdir'/ (PREFIX+'.save')/'data-file-schema.xml',process,expected_settings=deck,expected_parallel=SHAPE,expected_exit='clean_stop',expected_evaluations=3)
 assert parsed['scf_counts']==[1,2,3] and len(parsed['evaluations'])==3
 adapter.require_expected_first_threshold(parsed,deck)
 history=adapter.read_bfgs(ARM/'outdir'/(PREFIX+'.bfgs'),nat=72,cell_bohr=parsed['evaluations'][-1]['geometry']['cell'],evaluated=parsed['evaluations'][-1])
 assert (history['scf_count'],history['bfgs_count'],history['gdiis_count'])==(3,3,0)
 return {'arm':parsed,'saved_control_optimizer':history,'settings_and_threshold_bound':True}
def tiny(adapter):
 raw=ROOT/'results/s2_2026-09-25/full_text/sequential_2026-10-03/pa_tiny_raw/tiny_results/candidate-stop'
 deck=adapter.parse_deck(raw/'input.in');p=raw/'H.pbe-rrkjus_psl.1.0.0.UPF'
 deck['upf_pins']={p.name:'27f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962'}
 deck['upf_read_path_map']={'/anvil/projects/x-che260157/sts_pa_probe_2026-10-03/tiny_results/candidate-stop/'+p.name:str(p)}
 process=json.loads((raw/'receipt.json').read_text())
 parsed=adapter.read_qe_arm(raw/'input.in',raw/'stdout.log',raw/'stderr.log',raw/'scratch/h2_probe.save/data-file-schema.xml',process,expected_settings=deck,expected_parallel={'nprocs':1,'nthreads':1,'ntasks':1,'nbgrp':1,'npool':1,'ndiag':1},expected_exit='clean_stop',expected_evaluations=1)
 assert parsed['scf_counts']==[1] and parsed['optimizer_counts']==[0]
 return {'evaluations':len(parsed['evaluations']),'counts':parsed['scf_counts'],'source_pins':parsed['sources']}
def main(label):
 target=PHASE/('raw_replay_'+label+'.json');assert label in {'initial','checked'} and not target.exists()
 r={'successful':False,'scope':'CONTROL_XML_REPAIR_OFFLINE_ONLY','new_jobs_submitted':0,'qe_executed':False,'production_accepted':False,'original_job_id':'21034683','original_scheduler_status':'FAILED3:0','original_trial_status':'INCONCLUSIVE','complete_trial_pass':False,'remaining_arms_executed':False}
 try:
  r['mirror_before']=mirror_pins()
  original=load('repair_launch_original',PHASE/'launch_adapter_original.py')
  assert sha(PHASE/'launch_adapter_original.py')=='255464215aa898d0c9d34317a1be9b16fb27ba6d35108e0ca78215331a628879'
  try:control(original)
  except original.AdapterError as exc:
   assert str(exc)=='one XML lda_plus_u required';r['original_rejection_reproduced']=str(exc)
  else:raise AssertionError('original adapter did not reproduce the historical rejection')
  repaired=load('repair_adapter_current',ROOT/'src/dft/pa_qe_adapter.py')
  r['adapter_sha256']=sha(ROOT/'src/dft/pa_qe_adapter.py')
  r['control_only']=control(repaired);r['tiny_non_hubbard']=tiny(repaired)
  r['mirror_after']=mirror_pins();assert r['mirror_after']==r['mirror_before']
  assert r['adapter_sha256']==sha(ROOT/'src/dft/pa_qe_adapter.py')
  r['successful']=True
 except BaseException as exc:r['error']=repr(exc);raise
 finally:target.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'successful':r['successful'],'control_evaluations':3,'original_rejection_reproduced':r.get('original_rejection_reproduced'),'complete_trial_pass':False,'qe_executed':False},indent=2),flush=True)
if __name__=='__main__':main(sys.argv[1])
