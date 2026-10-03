"""Retain initial hidden-desktop failures and successes without publisher payloads."""
import json
import pathlib
from prepare_sources import retain,jsonbytes,sha

HERE=pathlib.Path(__file__).resolve().parent
BACKGROUND=pathlib.Path('C:/Users/frank/AppData/Local/Temp/sts-background-2026-09-06')

def main(index_name='intake_execution_receipts.json'):
    receipts=[]
    for source in sorted(BACKGROUND.glob('five_si_*.status.json')):
        status=json.loads(source.read_text(encoding='utf-8'))
        log=source.with_name(source.name.replace('.status.json','.log'))
        text=log.read_text(encoding='utf-8')
        assert status['desktop_requested']=='Codex_STS_Background'
        assert text.startswith('Verified background desktop: Codex_STS_Background')
        retain(HERE/'local_execution_receipts'/source.name,source.read_bytes())
        retain(HERE/'local_execution_receipts'/log.name,log.read_bytes())
        receipts.append({'status':source.name,'status_sha256':sha(source),'exit_code':status['exit_code'],'verified_desktop':'Codex_STS_Background','log':log.name,'log_sha256':sha(log),'failure_tail':text[-1300:] if status['exit_code'] else None})
    retain(HERE/index_name,jsonbytes({'scope':'Local intake/verification receipts; raw receipts stay local','receipts':receipts,'new_paid_external_api_calls':0}))
    print('Local isolation/failure receipts:',len(receipts))

if __name__=='__main__':
    main()
