"""Serialize explicit human-reviewed row choices; never infer scientific verdicts."""
import json
import pathlib
import sys

HERE=pathlib.Path(__file__).resolve().parent
FT=HERE.parent
sys.path.insert(0,str(FT))
from recovery_state import validate_fields
from verify_evidence_recovery import row_errors
from reconcile import verified
from prepare_sources import retain,jsonbytes

def one(path):
    lines=path.read_text(encoding='utf-8').splitlines()
    assert len(lines)==1
    return json.loads(lines[0])

def main():
    spec=json.loads((HERE/'adjudication_spec.json').read_text(encoding='utf-8'))
    entries=[]
    for choice in spec['records']:
        row=one(HERE/choice['chosen'])
        assert row['screen_id']==choice['screen_id']
        if 'note' in choice:row['note']=choice['note']
        source=one(HERE/choice['chosen'].replace('.out.','.in.'))
        text=(FT/source['text']).read_text(encoding='utf-8')+'\n'+(FT/source['si_text']).read_text(encoding='utf-8')
        errors=row_errors(row,text,True)
        assert not errors,(row['screen_id'],errors)
        assert verified(row,text)
        reads=[one(HERE/name) for name in choice['independent_reads']]
        entry={'row':row,'reason':choice['reason'],'review':choice['review'],
               'independent_reads':[(HERE/name).relative_to(FT).as_posix() for name in choice['independent_reads']],
               'source_metadata':(HERE/(row['screen_id'].lower()+'_source_metadata.json')).relative_to(FT).as_posix(),
               'source':'manual priority SI 2026-10-03: independent reads reviewed','si_complete':True,
               'field_decisions':choice['field_decisions']}
        assert not validate_fields(entry,reads),(row['screen_id'],validate_fields(entry,reads))
        entries.append(entry)
    retain(HERE/'reviewed_decisions.json',jsonbytes({'date':spec['date'],'scope':spec['scope'],'records':entries}))
    print('Explicit reviewed recovery rows retained:',len(entries))

if __name__=='__main__':
    main()
