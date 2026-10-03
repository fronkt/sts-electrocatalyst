"""Retain local execution receipts, including corrected initial failures."""
import hashlib
import json
from pathlib import Path

PHASE = Path(__file__).resolve().parent
BG = Path('C:/Users/frank/AppData/Local/Temp/sts-background-2026-09-06')
JOBS = [
    ('pa-integration-baseline-2026-10-03', 1, 'Initial nested-code newline syntax error; no baseline mutation'),
    ('pa-integration-baseline-checked-2026-10-03', 0, 'Corrected clean checkpoint and whole tracked/unrelated byte pins'),
    ('pa-extraction-check-2026-10-03', 1, 'Initial global Word-table-count assumption refused extraction'),
    ('pa-extraction-check-v2-2026-10-03', 0, 'Unique source-header selection and exact literal site transcription'),
    ('pa-package-verify-2026-10-03', 1, 'Initial fixture helper argument mismatch; immutable failure receipt retained'),
    ('pa-package-verify-v2-2026-10-03', 0, 'Fresh corrected offline regressions, science and whole-byte preservation'),
]


def main():
    receipts = []
    for name, expected, note in JOBS:
        files = {kind:BG/(name+suffix) for kind,suffix in
                 [('config','.json'),('log','.log'),('status','.status.json')]}
        status = json.loads(files['status'].read_text(encoding='utf-8'))
        log = files['log'].read_text(encoding='utf-8')
        if status['exit_code']!=expected or status['desktop_requested']!='Codex_STS_Background' or not log.startswith('Verified background desktop: Codex_STS_Background'):
            raise ValueError('execution receipt differs from reviewed outcome: '+name)
        receipts.append({'job':name,'status':status,'note':note,
                         'files':{k:{'path':str(p),'bytes':p.stat().st_size,
                                     'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                                  for k,p in files.items()},
                         'failure_tail':log.splitlines()[-30:] if expected else []})
    report = {'verified_background_desktop':True,'local_jobs':receipts,
              'new_qe_or_slurm_jobs':0,'new_paid_external_api_calls':0,
              'all_initial_failures_preserved':True}
    (PHASE/'execution_receipts.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    main()
