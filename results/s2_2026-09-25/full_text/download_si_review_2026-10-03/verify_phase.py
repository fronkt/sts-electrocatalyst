"""Exact-scope and source/history check for five new manual SI packages."""
import csv
import hashlib
import json
import pathlib
from collections import Counter

PHASE = pathlib.Path(__file__).resolve().parent
FT = PHASE.parent
REPO = FT.parents[2]
IDS = {'S29636','S29420','S29447','S28435','S24094'}
REBUILDS = {'reconcile/current_state.csv','reconcile/current_state.json','si_checklist.csv','si_checklist.html'}
IMPLEMENTATION = {'recovery_state.py','test_recovery_state.py'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows(path):
    with path.open(encoding='utf-8',newline='') as stream:
        return list(csv.DictReader(stream))

def changed_scope(before, after):
    old, now = {r['screen_id']:r for r in before}, {r['screen_id']:r for r in after}
    errors = []
    if len(after)!=2496 or set(old)!=set(now):
        return [], ['record population changed']
    changed=sorted(sid for sid in old if old[sid]!=now[sid])
    if set(changed)!=IDS:
        errors.append('changes not exactly the five reviewed rows: '+str(changed))
    for sid in old:
        for field in old[sid]:
            if field.startswith(('v3_','v4_')) or field in ('lane','version_primary','v5_final_before_si'):
                if now[sid][field]!=old[sid][field]:
                    errors.append(sid+': historical field changed: '+field)
    return changed,errors

def main():
    baseline=json.loads((PHASE/'baseline.json').read_text(encoding='utf-8'))
    gate=json.loads((PHASE/'source_read_gate.json').read_text(encoding='utf-8'))
    history=json.loads((PHASE/'assessment_history.json').read_text(encoding='utf-8'))
    decisions=json.loads((PHASE/'reviewed_decisions.json').read_text(encoding='utf-8'))['records']
    errors, preserved, implementation=[],0,{}
    for rel,want in baseline['files'].items():
        actual=sha(FT/rel)
        if rel in REBUILDS:
            continue
        if rel in IMPLEMENTATION:
            implementation[rel]={'before':want,'after':actual}
        elif actual!=want:
            errors.append([rel,'historical file changed'])
        else:
            preserved+=1
    for rel,want in baseline['unrelated_untracked_files'].items():
        if sha(REPO/rel)!=want:
            errors.append([rel,'unrelated DFT changed'])
    before_git=json.loads((PHASE/'implementation_before_git.json').read_text(encoding='utf-8'))
    if before_git['git_head']!=baseline['git_head'] or sha(FT/before_git['snapshot'])!=before_git['sha256']:
        errors.append(['test fixture Git-baseline snapshot differs'])
    implementation['test_recovery_state.py']={'before':before_git['sha256'],'after':sha(FT/'test_recovery_state.py'),'before_source':'clean tracked Git checkpoint; supplementary to original scientific-file baseline'}
    for item in history['original_outputs']:
        if sha(PHASE/item['output'])!=item['sha256']:
            errors.append([item['output'],'original assessment changed'])
        if sha(PHASE/item['input'])!=item['input_sha256']:
            errors.append([item['input'],'original assessment input changed'])
    if history['initial_source_assessments']!=10:
        errors.append(['initial independent read count differs from ten'])
    if sum(item['records'] for item in history['original_outputs'])!=history['all_source_assessments']:
        errors.append(['source assessment count differs from frozen batches'])
    by_id={r['row']['screen_id']:r for r in decisions}
    if len(decisions)!=5 or set(by_id)!=IDS or len(gate['records'])!=5 or {r['screen_id'] for r in gate['records']}!=IDS:
        errors.append(['gate/ruling coverage differs from five IDs'])
    for entry in gate['records']:
        sid=entry['screen_id']
        ruling=by_id[sid]
        meta=json.loads((FT/ruling['source_metadata']).read_text(encoding='utf-8'))
        if not(entry['identity_verified'] is True and entry['si_complete_for_read'] is True and
               meta['identity_verified'] is True and meta['si_complete'] is True and ruling['si_complete'] is True):
            errors.append([sid,'identity/completeness gate not verified'])
        if ruling['row']['doi']!=entry['doi'] or meta['doi']!=entry['doi']:
            errors.append([sid,'DOI link differs'])
        if {p['file']:p['sha256'] for p in meta['files']}!={p['file']:p['sha256'] for p in entry['source_pins']}:
            errors.append([sid,'metadata binary pins differ from verified gate'])
        for pin in entry['source_pins']:
            if sha(FT/pin['file'])!=pin['sha256']:
                errors.append([sid,pin['file'],'source changed'])
            original=pathlib.Path(pin['download_path']) if pin.get('download_path') else FT/'files'/(sid+'.pdf')
            if sha(original)!=pin['sha256']:
                errors.append([sid,str(original),'original changed'])
        for field,hashfield in (('main_text','main_sha256'),('si_text','si_sha256')):
            if sha(FT/entry[field])!=entry[hashfield]:
                errors.append([sid,field,'reading copy changed'])
        if meta['text']!=entry['main_text'] or meta['si_text']!=entry['si_text']:
            errors.append([sid,'metadata reading paths differ'])
        if meta['text_sha256']!=entry['main_sha256'] or meta['si_text_sha256']!=entry['si_sha256']:
            errors.append([sid,'metadata reading pins differ from verified gate'])
        pin=entry['source_pins'][1]
        suffix=pathlib.Path(pin['file']).suffix
        if sha(FT/'files_si'/(sid+'_SI1'+suffix))!=pin['sha256']:
            errors.append([sid,'canonical SI cache changed'])
        for name in ruling['independent_reads']:
            inp=json.loads((FT/name.replace('.out.','.in.')).read_text(encoding='utf-8'))
            if inp['text']!=entry['main_text'] or inp['si_text']!=entry['si_text'] or inp['doi']!=entry['doi']:
                errors.append([sid,name,'read/source join differs'])
    current=rows(FT/'reconcile/current_state.csv')
    changed,scope_errors=changed_scope(baseline['records'],current)
    errors.extend(scope_errors)
    checklist=rows(FT/'si_checklist.csv')
    expected=[r for r in baseline['checklist'] if r['screen_id'] not in IDS]
    if checklist!=expected:
        errors.append(['retained checklist content/order changed'])
    forced={'S29721','S10090','S22807','S26024'}
    if not forced<={r['screen_id'] for r in checklist}:
        errors.append(['forced eligible-question IDs missing'])
    if baseline['budget']!={'lifetime_api_cap_usd':50,'conservative_tracked_usd':1.1105254,'new_paid_external_api_calls':0}:
        errors.append(['budget scope differs'])
    report={'starting_head':baseline['git_head'],'records':len(current),'changed_rows':changed,
            'historical_files_preserved':preserved,'implementation_changes':implementation,
            'unrelated_dft_files_preserved':len(baseline['unrelated_untracked_files']),
            'initial_source_assessments':history['initial_source_assessments'],
            'all_source_assessments':history['all_source_assessments'],
            'original_outputs_preserved':len(history['original_outputs']),
            'checklist_records':len(checklist),'checklist_tiers':dict(Counter(r['tier'] for r in checklist)),
            'v5_counts':dict(Counter('collapsed' if r['v5_final'].startswith('collapsed') else r['v5_final'] for r in current)),
            'reviewed_outcomes':{r['screen_id']:r['v5_final'] for r in current if r['screen_id'] in IDS},
            'errors':errors,'budget':baseline['budget']}
    output=PHASE/'scientific_final_checked'/'phase_verification.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    assert not errors,errors
    return report

if __name__=='__main__':
    main()
