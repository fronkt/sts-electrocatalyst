"""Separate checked copies, never changes scientific criteria or frozen reads."""
import json
import pathlib
import sys

HERE=pathlib.Path(__file__).resolve().parent
FT=HERE.parent
sys.path.insert(0,str(FT))
from ft_screen import check
from reconcile import verified
from verify_evidence_recovery import row_errors
from prepare_sources import retain,jsonbytes,sha

def main(report_name='transcription_repairs_checked.json'):
    specs=json.loads((HERE/'transcription_repairs.json').read_text(encoding='utf-8'))
    reports=[]
    for item in specs['records']:
        inp=json.loads((HERE/item['input']).read_text(encoding='utf-8'))
        old=json.loads((HERE/item['original']).read_text(encoding='utf-8'))
        row=json.loads(json.dumps(old))
        for key,value in item['patches'].items():
            parts=key.split('.')
            if len(parts)==2:
                assert parts[0] in ['E'+str(n) for n in range(1,7)] and parts[1] in ('excerpt','where')
                row[parts[0]][parts[1]]=value
            else:
                assert key=='note'
                row[key]=value
        assert all(row['E'+str(n)]['v']==old['E'+str(n)]['v'] for n in range(1,7))
        assert all(row[k]==old[k] for k in ('disposition','exclude_criterion','form','eta_form','eta_derivation','eta_note','secondary','provenance','screen_id','doi','text_ok'))
        text=(FT/inp['text']).read_text(encoding='utf-8')+'\n'+(FT/inp['si_text']).read_text(encoding='utf-8')
        errors=row_errors(row,text,inp['si_complete'])
        assert not errors,(item['original'],errors)
        assert verified(row,text)
        target=HERE/item['checked']
        retain(target,(json.dumps(row,ensure_ascii=False)+'\n').encode('utf-8'))
        checked_in=HERE/item['checked'].replace('.out.','.in.')
        retain(checked_in,(HERE/item['input']).read_bytes())
        assert not check(checked_in,target)
        reports.append(dict(item,original_sha256=sha(HERE/item['original']),checked_sha256=sha(target),new_source_assessment=False))
    retain(HERE/report_name,jsonbytes({'records':reports,'errors':[]}))
    print('Separate checked transcripts:',len(reports))

if __name__=='__main__':
    main()
