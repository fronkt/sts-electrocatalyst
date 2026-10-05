"""Independent terminal raw reconstruction; never runs QE or changes old evidence."""
from pathlib import Path
import datetime,hashlib,json,math,re,xml.etree.ElementTree as ET
ROOT=Path.cwd();OUT=ROOT/'results/pa_catalyst_retest_readout_2026-10-05';RAW=OUT/'raw_mirror'
NAT=72;BOHR_ANG=0.529177210903;RY_EV=13.605693122994
TOL={'energy_Ry':1e-6,'position_bohr':1e-5,'force_Ry_bohr':1e-5}
NUM=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?'
def number(s):return float(s.replace('D','E').replace('d','e'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tag(e):return e.tag.split('}')[-1]
def child(e,name):return next(x for x in e if tag(x)==name)
def find(e,*names):
 for name in names:e=child(e,name)
 return e
def vals(e):return [number(x) for x in (e.text or '').split()]
def matrix(v):assert len(v)==NAT*3;return [v[i:i+3] for i in range(0,len(v),3)]
def delta(a,b,species):
 records=[{'absolute':abs(y-x),'signed_right_minus_left':y-x,'atom':i+1,'species':species[i],'axis':'xyz'[j],'left':x,'right':y} for i,(r,s) in enumerate(zip(a,b)) for j,(x,y) in enumerate(zip(r,s))]
 return max(records,key=lambda x:x['absolute'])
def plainmax(a,b):return max(abs(y-x) for r,s in zip(a,b) for x,y in zip(r,s))
def write(name,data):(OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
manifest=json.loads((OUT/'raw_manifest.json').read_text(encoding='utf-8'))
receipt=json.loads((RAW/'trial_results/trial_receipt.json').read_text(encoding='utf-8'))
original=json.loads((OUT/'terminal_inventory.json').read_text(encoding='utf-8'))['trial_receipt']
assert receipt==original,'fresh inventory differs from mirrored final receipt'
assert receipt['scientific_status']=='INCONCLUSIVE' and receipt['error']=='all three ordered evaluations did not agree'
assert receipt['production_accepted'] is False
pins={x['path']:x for x in manifest['files'] if x['kind']=='file'}
verified={}
def pinned(rel):
 p=RAW/rel;assert p.stat().st_size==pins[rel]['bytes'] and sha(p)==pins[rel]['sha256'],rel
 verified[rel]=pins[rel]['sha256'];return p

def parse_input(rel):
 p=pinned(rel);lines=p.read_text().splitlines();start=next(i for i,s in enumerate(lines) if s.strip().upper().startswith('ATOMIC_POSITIONS'))
 unit=lines[start].lower();assert 'angstrom' in unit or 'bohr' in unit
 scale=BOHR_ANG if 'angstrom' in unit else 1.0
 species=[];positions=[];flags=[]
 for line in lines[start+1:start+1+NAT]:
  tokens=line.split();assert len(tokens)==7
  species.append(tokens[0]);positions.append([number(x)/scale for x in tokens[1:4]]);flags.append([int(x) for x in tokens[4:7]])
 return species,positions,flags

def structure(e):
 a=find(e,'atomic_structure');atoms=list(find(a,'atomic_positions'));assert len(atoms)==NAT
 assert [int(x.attrib['index']) for x in atoms]==list(range(1,NAT+1))
 species=[x.attrib['name'] for x in atoms];positions=[vals(x) for x in atoms];cell=[vals(x) for x in find(a,'cell')]
 assert all(len(x)==3 for x in positions+cell)
 return {'species':species,'positions':positions,'cell':cell}

def scf_log(text,conv):
 starts=list(re.finditer(r'(?m)^\s*Self-consistent Calculation\s*$',text));frames=[]
 for i,m in enumerate(starts):
  end=starts[i+1].start() if i+1<len(starts) else len(text);block=text[m.end():end]
  energy=re.search(r'(?m)^!\s*total energy\s*=\s*('+NUM+r')\s*Ry',block)
  if not energy:continue
  def matches(pattern):return [{'value':number(x.group(1)),'line':text.count('\n',0,m.end()+x.start())+1} for x in re.finditer(pattern,block)]
  thresholds=list(re.finditer(r'new conv_thr\s*=\s*('+NUM+r')\s*Ry',text[:m.start()]))
  active=number(thresholds[-1].group(1)) if thresholds else conv
  eth=matches(r'ethr\s*=\s*('+NUM+r')');residual=matches(r'estimated scf accuracy\s*<\s*('+NUM+r')\s*Ry')
  its=[int(x.group(1)) for x in re.finditer(r'(?m)^\s*iteration #\s*(\d+)',block)]
  total=matches(r'(?m)^\s*total magnetization\s*=\s*('+NUM+r')')
  absolute=matches(r'(?m)^\s*absolute magnetization\s*=\s*('+NUM+r')')
  traces={}
  for t in re.finditer(r'Tr\[ns\(\s*(\d+)\)\]\s*\(up, down, total\)\s*=\s*('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')',block):
   traces[t.group(1)]={'values':[number(t.group(j)) for j in (2,3,4)],'line':text.count('\n',0,m.end()+t.start())+1}
  correction=matches(r'Total SCF correction\s*=\s*('+NUM+r')')
  converged=re.search(r'convergence has been achieved in\s*(\d+)\s*iterations',block)
  assert converged and its==list(range(1,int(converged.group(1))+1))
  frames.append({'line_start':text.count('\n',0,m.start())+1,'energy_line':text.count('\n',0,m.end()+energy.start())+1,'log_energy_Ry':number(energy.group(1)),'iterations':len(its),'first_ethr_Ry':eth[0]['value'],'first_ethr_line':eth[0]['line'],'ethr_sequence':eth,'printed_residuals_Ry':residual,'active_printed_conv_thr_Ry':active,'final_total_magnetization_printed':total[-1]['value'],'final_absolute_magnetization_printed':absolute[-1]['value'],'hubbard_traces_printed':traces,'scf_correction_printed':correction})
 return frames

arms={};mapping={c['name']:c for c in receipt['calls']}
for name in ['control','candidate','fresh','resumed']:
 c=mapping[name];parsed=c['parsed'];xml_rel=parsed['sources']['xml']['path'].replace(manifest['remote_root']+'/','',1)
 xmlpath=pinned(xml_rel);doc=ET.fromstring(xmlpath.read_bytes());steps=[x for x in doc if tag(x)=='step'];out=child(doc,'output')
 frames=steps if name!='fresh' else [out]
 assert len(frames)=={'control':3,'candidate':1,'fresh':1,'resumed':2}[name]
 species,inputpositions,flags=parse_input('trial_results/'+name+'/input.in')
 stdout_rel='trial_results/'+name+'/stdout.log';stdout=pinned(stdout_rel).read_text();inputtext=(RAW/('trial_results/'+name+'/input.in')).read_text()
 conv=number(re.search(r'conv_thr\s*=\s*('+NUM+r')',inputtext,re.I).group(1))
 logs=scf_log(stdout,conv);assert len(logs)==len(frames)
 force_matches=list(re.finditer(r'(?m)^\s*atom\s+(\d+)\s+type\s+\d+\s+force\s*=\s*('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')',stdout))
 assert len(force_matches)==NAT*len(frames)
 evals=[]
 for i,frame in enumerate(frames):
  geom=structure(frame);assert geom['species']==species
  energy=vals(find(frame,'total_energy','etot'))[0]*2
  forces=[[v*2 for v in r] for r in matrix(vals(find(frame,'forces')))]
  grouped=force_matches[i*NAT:(i+1)*NAT];assert [int(x.group(1)) for x in grouped]==list(range(1,NAT+1))
  logforce=[[number(m.group(j+2))*flags[k][j] for j in range(3)] for k,m in enumerate(grouped)]
  assert plainmax(forces,logforce)<=5.1e-9, name+' force stdout/XML mismatch'
  assert abs(energy-logs[i]['log_energy_Ry'])<=5.1e-9
  assert plainmax(forces,parsed['evaluations'][i]['forces_Ry_bohr'])<=1e-14
  assert plainmax(geom['positions'],parsed['evaluations'][i]['geometry']['positions'])<=1e-13
  assert abs(energy-parsed['evaluations'][i]['energy_Ry'])<=1e-11
  scf=find(frame,'scf_conv') if name!='fresh' else find(frame,'convergence_info','scf_conv');assert find(scf,'convergence_achieved').text=='true'
  xmliter=int(find(scf,'n_scf_steps').text);assert xmliter==logs[i]['iterations']
  evals.append({'energy_Ry':energy,'geometry':geom,'forces_Ry_bohr':forces,'xml_scf_error_Ry':vals(find(scf,'scf_error'))[0],'xml_scf_iterations':xmliter,'log':logs[i]})
 assert plainmax(evals[0]['geometry']['positions'],inputpositions)<=1e-7
 cycles=[int(m.group(1)) for m in re.finditer(r'number of scf cycles\s*=\s*(\d+)',stdout)]
 bfgs=[int(m.group(1)) for m in re.finditer(r'number of bfgs steps\s*=\s*(\d+)',stdout)]
 assert cycles==parsed['scf_counts'] and bfgs==parsed['optimizer_counts']
 arms[name]={'xml_source':xml_rel,'stdout_source':stdout_rel,'evaluations':evals,'cycles':cycles,'optimizer_counts':bfgs,'qe_if_pos':flags,'input_conv_thr_Ry':conv}

left=arms['control']['evaluations'];right=arms['candidate']['evaluations']+arms['resumed']['evaluations'];differences=[]
for i,(a,b) in enumerate(zip(left,right),1):
 species=a['geometry']['species'];assert species==b['geometry']['species'] and plainmax(a['geometry']['cell'],b['geometry']['cell'])<1e-7
 rdelta=delta(a['geometry']['positions'],b['geometry']['positions'],species);fdelta=delta(a['forces_Ry_bohr'],b['forces_Ry_bohr'],species)
 metrics={'energy_Ry':abs(b['energy_Ry']-a['energy_Ry']),'position_bohr':rdelta['absolute'],'force_Ry_bohr':fdelta['absolute']}
 assert metrics==receipt['continuity']['ordered_differences'][i-1]
 failures=[k for k,v in metrics.items() if v>TOL[k]]
 differences.append({'evaluation':i,'metrics':metrics,'ratios_to_limits':{k:v/TOL[k] for k,v in metrics.items()},'failed_metrics':failures,'max_position_component':rdelta,'max_force_component':fdelta,'energy_delta_meV':metrics['energy_Ry']*RY_EV*1000,'position_delta_angstrom':rdelta['absolute']*BOHR_ANG,'force_delta_eV_angstrom':fdelta['absolute']*RY_EV/BOHR_ANG})
assert differences[0]['failed_metrics']==[] and differences[1]['failed_metrics']==['force_Ry_bohr']
assert set(differences[2]['failed_metrics'])==set(TOL)

# Independently compare final full candidate/immutable checkpoint hashes with saved copies.
checkpoint_checks=[]
for name in ['candidate','candidate_immutable']:
 prefix='trial_results/'+name+'/outdir/'
 expected=receipt['candidate_checkpoint']['copies']['outdir']['source_before']
 terminal={x['path'][len(prefix):]:(x['bytes'],x['sha256']) for x in manifest['files'] if x['kind']=='file' and x['path'].startswith(prefix)}
 saved={x['path']:(x['size_bytes'],x['sha256']) for x in expected['files']}
 assert terminal==saved,name+' full checkpoint drift'
 directories=sorted(x['path'][len(prefix):] for x in manifest['files'] if x['kind']=='directory' and x['path'].startswith(prefix))
 assert directories==expected['directories']
 body={'directories':directories,'files':[{'path':x,'size_bytes':v[0],'sha256':v[1]} for x,v in sorted(terminal.items())]}
 computed=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest();assert computed==expected['sha256']
 checkpoint_checks.append({'name':name,'file_count':len(terminal),'sha256':computed,'final_terminal_manifest_matches_initial_snapshot':True})
restart_rel='trial_results/candidate_immutable/outdir/slab_c5low__pa_boundary.restart_scf'
restart_header=pinned(restart_rel).read_text().splitlines()[0].split();assert int(restart_header[0])==0
warm=arms['candidate']['evaluations'][0];fresh=arms['fresh']['evaluations'][0]
assert plainmax(warm['geometry']['positions'],fresh['geometry']['positions'])<=1e-7
warm_minus_fresh=(warm['energy_Ry']-fresh['energy_Ry'])*RY_EV*1000
assert abs(warm_minus_fresh-receipt['pre_resume_decision']['warm_minus_fresh_meV'])<1e-8
assert warm_minus_fresh<10 and receipt['pre_resume_decision']['action']=='RESUME_CANDIDATE'
assert receipt['consumption_audit']['raw_consumption_audit']['passed']
result={'schema':'pa-retest-independent-terminal-analysis-v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'job_id':'21075231','launch_commit':manifest['launch_commit'],'launch_spec_sha256':manifest['launch_spec_sha256'],'scientific_status':'INCONCLUSIVE','production_accepted':False,'comparison_tolerances':TOL,'ordered_comparison':differences,'first_failure_evaluation':2,'first_failure_metric':'force_Ry_bohr','arms':arms,'candidate_checkpoint_terminal_checks':checkpoint_checks,'restart_scf_header':{'iter':int(restart_header[0]),'dr2':number(restart_header[1]),'ethr':number(restart_header[2]),'source':restart_rel},'warm_minus_fresh_meV':warm_minus_fresh,'fresh_reseed_triggered':False,'checkpoint_consumption_recorded_pass':True,'negative_control_executed':False,'independent_stdout_xml_rounding_limit':5.1e-9,'source_sha256':verified,'raw_manifest_sha256':sha(OUT/'raw_manifest.json'),'new_solver_calls':0,'causal_effect_of_startup_threshold_is_unproven':True}
write('independent_analysis.json',result)
print(json.dumps({'ordered_comparison':differences,'scf_summary':{k:[{'iterations':e['xml_scf_iterations'],'residual_Ry':e['xml_scf_error_Ry'],'first_ethr_Ry':e['log']['first_ethr_Ry'],'active_printed_conv_thr_Ry':e['log']['active_printed_conv_thr_Ry']} for e in v['evaluations']] for k,v in arms.items()},'checkpoint_checks':checkpoint_checks,'warm_minus_fresh_meV':warm_minus_fresh},indent=2),flush=True)
