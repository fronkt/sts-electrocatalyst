"""Bounded read-only collection for job21024848; never submit or retry QE."""
import hashlib
import json
import pathlib
import subprocess
import tarfile
import time
from datetime import datetime, timezone

PHASE=pathlib.Path.cwd()/'results/s2_2026-09-25/full_text/sequential_2026-10-03'
JOB='21024848'
REMOTE='/anvil/projects/x-che260157/sts_pa_probe_2026-10-03'
SSH=['C:/Program Files/Git/usr/bin/ssh.exe','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
     '-o','ConnectTimeout=12','x-fcai3@anvil.rcac.purdue.edu']
TERMINAL={'COMPLETED','FAILED','CANCELLED','TIMEOUT','OUT_OF_MEMORY','NODE_FAIL','PREEMPTED','BOOT_FAIL','DEADLINE'}

def status(**fields):
    fields.update(observed_utc=datetime.now(timezone.utc).isoformat(),job_id=JOB,
                  readonly=True,automatic_qe_retry=False,collection_retry_limit=3,production_accepted=False)
    (PHASE/'pa_tiny_watch_status.json').write_text(json.dumps(fields,indent=2),encoding='utf-8')
    print(json.dumps(fields),flush=True)

def observe():
    script=r'''import pathlib,subprocess,json
from datetime import datetime,timezone
job='21024848'
root=pathlib.Path('/anvil/projects/x-che260157/sts_pa_probe_2026-10-03')
r={'observed_utc':datetime.now(timezone.utc).isoformat(),'job_id':job,'commands':{},'arms':{}}
for name,args in [('queue',['squeue','-h','-j',job,'-o','%i|%T|%M|%C|%R']),
 ('accounting',['sacct','-n','-P','-j',job,'--format=JobIDRaw,State,ExitCode,ElapsedRaw,AllocCPUS,ReqMem,AllocTRES,CPUTimeRAW']),
 ('job',['scontrol','show','job',job,'-o'])]:
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=20)
 r['commands'][name]={'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
log=root/('probe_'+job+'.log')
r['scheduler_log_tail']=log.read_text(errors='replace')[-3000:] if log.exists() else None
for arm in ['continuous','candidate-stop','negative-fresh','resumed']:
 d=root/'tiny_results'/arm
 r['arms'][arm]={'exists':d.exists()}
 if (d/'receipt.json').exists():r['arms'][arm]['receipt']=json.loads((d/'receipt.json').read_text())
 if (d/'stdout.log').exists():r['arms'][arm]['stdout_tail']=(d/'stdout.log').read_text(errors='replace')[-1200:]
report=root/'tiny_results/report.json'
if report.exists():r['report']=json.loads(report.read_text())
print(json.dumps(r))
'''
    compile(script,'<readonly-observation>','exec')
    p=subprocess.run(SSH+['/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -'],
        input=script,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90,creationflags=0x08000000)
    row={'observed_utc':datetime.now(timezone.utc).isoformat(),'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    with (PHASE/'pa_tiny_observations.jsonl').open('a',encoding='utf-8') as out:out.write(json.dumps(row)+'\n')
    assert p.returncode==0,row
    return json.loads(p.stdout)

def mirror():
    script=r'''import pathlib,hashlib,json
root=pathlib.Path('/anvil/projects/x-che260157/sts_pa_probe_2026-10-03')
files=list((root/'tiny_results').rglob('*'))+[root/'probe_21024848.log']
rows=[]
for p in sorted(files):
 assert not p.is_symlink(),'symlink refused'
 if p.is_file():
  h=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
  rows.append({'path':p.relative_to(root).as_posix(),'size':p.stat().st_size,'sha256':h.hexdigest()})
assert len(rows)<=512 and sum(r['size'] for r in rows)<=536870912,'bounded mirror exceeded'
print(json.dumps(rows))
'''
    p=subprocess.run(SSH+['/apps/spack/anvil/apps/python/3.9.5-gcc-11.2.0-vtey2yv/bin/python3 -'],
        input=script,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90,creationflags=0x08000000)
    assert p.returncode==0,p.stderr
    rows=json.loads(p.stdout)
    destination=PHASE/'pa_tiny_raw'
    archive=PHASE/'pa_tiny_raw.tar'
    assert not destination.exists() and not archive.exists(),'no mirror overwrite'
    names=sorted({r['path'].split('/')[0] for r in rows})
    assert set(names).issubset({'tiny_results','probe_'+JOB+'.log'}) and names
    command='tar -c -C '+REMOTE+' '+' '.join(names)
    with archive.open('xb') as out:
        transfer=subprocess.run(SSH+[command],stdout=out,stderr=subprocess.PIPE,timeout=120,creationflags=0x08000000)
    assert transfer.returncode==0,transfer.stderr.decode('utf-8','replace')
    assert archive.stat().st_size<=537919488,'archive bound exceeded'
    destination.mkdir()
    with tarfile.open(archive,'r:') as tar:
        members=tar.getmembers()
        assert len(members)<=1024
        for member in members:
            parts=pathlib.PurePosixPath(member.name).parts
            assert parts and not member.name.startswith('/') and '..' not in parts
            assert member.isfile() or member.isdir(),'nonregular archive member'
        tar.extractall(destination,filter='data')
    actual={p.relative_to(destination).as_posix():p for p in destination.rglob('*') if p.is_file()}
    assert set(actual)=={r['path'] for r in rows},'mirror file set differs'
    for row in rows:
        local=actual[row['path']]
        assert local.stat().st_size==row['size']
        assert hashlib.sha256(local.read_bytes()).hexdigest()==row['sha256'],'mirror hash differs:'+row['path']
    receipt={'job_id':JOB,'remote_root':REMOTE,'local_root':str(destination),'files':rows,
        'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'inventory_stderr':p.stderr,
        'transfer_stderr':transfer.stderr.decode('utf-8','replace'),'all_pins_match':True,
        'readonly':True,'production_accepted':False,'full_trajectory_review_pending':True}
    (PHASE/'pa_tiny_mirror_receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    return len(rows)

def main():
    deadline=time.monotonic()+86400
    failures=0
    status(state='WATCHING',deadline_seconds=86400,poll_seconds=120)
    while time.monotonic()<deadline:
        try:
            data=observe()
            failures=0
            entries=[line.split('|') for line in data['commands']['accounting']['stdout'].splitlines() if line]
            job=next((row for row in entries if row[0]==JOB),None)
            state=job[1].split()[0].rstrip('+') if job else 'ACCOUNTING_PENDING'
            status(state=state,queue=data['commands']['queue']['stdout'],accounting=data['commands']['accounting'])
            if state in TERMINAL:
                count=mirror()
                status(state='TERMINAL_MIRRORED',scheduler_state=state,files=count,
                       full_trajectory_review_pending=True)
                return
        except BaseException as exc:
            failures+=1
            status(state='COLLECTION_ERROR',error=repr(exc),consecutive_failures=failures)
            if failures>=3:return
        time.sleep(min(120,max(0,deadline-time.monotonic())))
    status(state='WATCH_DEADLINE',full_trajectory_review_pending=True)

if __name__=='__main__':main()
