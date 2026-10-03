"""Immutable-output QC for job21024848; no process or computation launch."""
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

PHASE=Path(__file__).resolve().parent
RAW=PHASE/'pa_tiny_raw/tiny_results'
QE_SHA='1d66c7856f5d6b3cd9c66b8578e01512b16bbe907b4360e54234890712ccd6a1'
UPF_SHA='27f8a7e87851d59a2698237d6ab4578d62950640f4f175781b015a0ce731f962'
UPF='H.pbe-rrkjus_psl.1.0.0.UPF'
TOLERANCES={'energy_Ry':1e-6,'position_bohr':1e-5,'force_Ry_per_bohr':1e-5}

def tag(node):return node.tag.rsplit('}',1)[-1]

def one(node,name):
    values=[v for v in node if tag(v)==name]
    assert len(values)==1,(tag(node),name,len(values))
    return values[0]

def numbers(text):
    values=[float(v.replace('D','e').replace('d','e')) for v in text.split()]
    assert values and all(math.isfinite(v) for v in values),'nonfinite or empty values'
    return values

def positions(node):
    structure=one(node,'atomic_structure')
    assert structure.attrib.get('nat')=='2'
    atoms=list(one(structure,'atomic_positions'))
    assert [(a.attrib['name'],a.attrib['index']) for a in atoms]==[('H','1'),('H','2')]
    coords=[numbers(a.text or '') for a in atoms]
    assert all(len(v)==3 for v in coords)
    cell=[numbers(v.text or '') for v in one(structure,'cell')]
    assert cell==[[20.,0.,0.],[0.,20.,0.],[0.,0.,20.]]
    return coords

def evaluated(node):
    coords=positions(node)
    energy=numbers(one(one(node,'total_energy'),'etot').text or '')
    assert len(energy)==1
    force_node=one(node,'forces')
    assert numbers(force_node.attrib['dims'])==[3.,2.]
    forces=numbers(force_node.text or '')
    assert len(forces)==6
    return {'atoms':['H','H'],'positions_bohr':coords,'energy_Ry':2*energy[0],
            'forces_Ry_per_bohr':[[2*v for v in forces[i:i+3]] for i in range(0,6,3)]}

def parse(arm):
    root=ET.parse(RAW/arm/'scratch/h2_probe.save/data-file-schema.xml').getroot()
    assert root.attrib['Units']=='Hartree atomic units'
    parallel={tag(n):int(n.text) for n in one(root,'parallel_info')}
    assert parallel=={'nprocs':1,'nthreads':1,'ntasks':1,'nbgrp':1,'npool':1,'ndiag':1}
    assert one(one(root,'general_info'),'creator').attrib['VERSION']=='7.5'
    steps=[]
    for node in root:
        if tag(node)=='step':
            assert one(one(node,'scf_conv'),'convergence_achieved').text=='true'
            steps.append(evaluated(node))
    status=int(one(root,'exit_status').text)
    output=one(root,'output')
    return {'steps':steps,'parallel':parallel,'status':status,
            'proposal':positions(output),'endpoint':evaluated(output) if status==0 else None}

def differences(first,second):
    assert first['atoms']==second['atoms']
    return {'energy_Ry':abs(first['energy_Ry']-second['energy_Ry']),
        'position_bohr':max(abs(a-b) for p,q in zip(first['positions_bohr'],second['positions_bohr']) for a,b in zip(p,q)),
        'force_Ry_per_bohr':max(abs(a-b) for p,q in zip(first['forces_Ry_per_bohr'],second['forces_Ry_per_bohr']) for a,b in zip(p,q))}

def main():
    mirror=json.loads((PHASE/'pa_tiny_mirror_receipt.json').read_text(encoding='utf-8'))
    assert mirror['all_pins_match']
    for row in mirror['files']:
        source=PHASE/'pa_tiny_raw'/row['path']
        assert source.stat().st_size==row['size']
        assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
    runs={name:parse(name) for name in ['continuous','candidate-stop','negative-fresh','resumed']}
    flags={}
    for name,run in runs.items():
        log=(RAW/name/'stdout.log').read_text(encoding='utf-8')
        stderr=(RAW/name/'stderr.log').read_text(encoding='utf-8')
        receipt=json.loads((RAW/name/'receipt.json').read_text(encoding='utf-8'))
        assert receipt['returncode']==0 and not receipt['timed_out'] and not stderr
        assert 'Program PWSCF v.7.5 starts' in log and 'JOB DONE.' in log
        upf=RAW/name/UPF
        assert hashlib.sha256(upf.read_bytes()).hexdigest()==UPF_SHA
        md5=hashlib.md5(upf.read_bytes()).hexdigest()
        assert re.findall(r'MD5 check sum:\s*([a-f0-9]+)',log)==[md5]
        read_paths=re.findall(r'PseudoPot\. #\s*1 for H\s+read from file:\s*([^\n]+)',log)
        assert len(read_paths)==1 and read_paths[0].strip().endswith('/'+name+'/'+UPF)
        count_matches=list(re.finditer(r'number of bfgs steps\s*=\s*(\d+)',log))
        counts=[int(v.group(1)) for v in count_matches]
        cycles=[int(v) for v in re.findall(r'number of scf cycles\s*=\s*(\d+)',log)]
        assert counts and cycles
        startup=log[:count_matches[0].start()]
        assert 'restart disabled' not in log.lower()
        assert 'convergence NOT achieved' not in log
        if name=='candidate-stop':
            assert len(run['steps'])==1 and run['status']==255
            assert receipt['move_trigger_observed'] and 'Program stopped by user request' in log
            assert counts[0]==0 and cycles[0]==1
        else:
            assert run['status']==0 and 'bfgs converged in' in log
        if name=='negative-fresh':assert counts[0]==0 and '.bfgs deleted, as requested' in startup
        if name=='resumed':
            assert counts[0]==1 and cycles[0]==2
            assert '.bfgs deleted, as requested' not in startup
            assert not re.search(r'(?m)^\s*BFGS Geometry Optimization\s*$',log)
        flags[name]={'xml_status':run['status'],'evaluated_steps':len(run['steps']),
            'bfgs_counts':counts,'scf_cycles':cycles,'upf_read_path':read_paths[0].strip(),
            'upf_md5':md5,'upf_sha256':UPF_SHA,'normal_final_history_cleanup':'.bfgs deleted, as requested' in log[len(startup):]}
    control=runs['continuous']['steps']
    split=runs['candidate-stop']['steps']+runs['resumed']['steps']
    assert len(control)==len(split) and len(control)>=3
    deltas=[differences(a,b) for a,b in zip(control,split)]
    endpoint=differences(runs['continuous']['endpoint'],runs['resumed']['endpoint'])
    maxima={key:max([d[key] for d in deltas]+[endpoint[key]]) for key in TOLERANCES}
    assert all(maxima[key]<=tol for key,tol in TOLERANCES.items()),maxima
    saved=numbers((RAW/'checkpoint-stopped/h2_probe.bfgs').read_text(encoding='utf-8'))
    assert len(saved)==326 and saved[32:35]==[1.,1.,0.]
    prior=runs['candidate-stop']['steps'][0]
    prior_pos=[v for row in prior['positions_bohr'] for v in row]
    prior_force=[v for row in prior['forces_Ry_per_bohr'] for v in row]
    assert max(abs(20*a-b) for a,b in zip(saved[:6],prior_pos))<1e-10
    assert max(abs(a/20+b) for a,b in zip(saved[16:22],prior_force))<1e-10
    assert abs(saved[35]-prior['energy_Ry'])<1e-10
    proposal=runs['candidate-stop']['proposal']
    first=runs['resumed']['steps'][0]['positions_bohr']
    assert max(abs(a-b) for p,q in zip(proposal,first) for a,b in zip(p,q))<=1e-5
    assert max(abs(a-b) for p,q in zip(proposal,[[0.,0.,0.],[0.,0.,2.]]) for a,b in zip(p,q))>1e-8
    run=json.loads((RAW/'run.json').read_text(encoding='utf-8'))
    assert run['qe_sha256']==QE_SHA and run['pseudo_sha256']==UPF_SHA
    assert run['scheduler_receipt']['allocated_tres']=={'billing':'4','cpu':'4','mem':'6G','node':'1'}
    result={'job_id':'21024848','source_commit':'9cbcab25ff4f462ab9d1a3d0f6ad7a51fcc8c051',
        'scheduler_outcome':'FAILED2:0 due post-run false-positive cleanup gate',
        'raw_files_checked':len(mirror['files']),'units':'QE Hartree AU; energy/force multiplied by2 to Ry units',
        'trajectory_order':'candidate single evaluated step + all7 resumed evaluated steps; no drops',
        'arms':flags,'tolerances':TOLERANCES,'step_differences':deltas,'endpoint_differences':endpoint,
        'max_differences':maxima,'saved_optimizer_counters':[1,1,0],
        'saved_prior_position_gradient_energy_correspondence':True,
        'negative_endpoint_difference':differences(runs['continuous']['endpoint'],runs['negative-fresh']['endpoint']),
        'tiny_plumbing_numeric_gates_pass':True,'independent_review_pending':True,
        'production_accepted':False,'catalyst_fresh_scf_reseed_validation':False,'new_qe_runs':0}
    (PHASE/'pa_tiny_raw_readout.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
