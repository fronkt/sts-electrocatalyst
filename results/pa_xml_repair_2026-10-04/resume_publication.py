"""Carry forward additive SI commits without altering the reviewed repair."""
import hashlib,json
from pathlib import Path
phase=Path(__file__).resolve().parent
previous=json.loads((phase/'publication.json').read_text())
assert not previous['successful'] and not previous.get('commit')
assert previous['before']['errors']==[] and len(previous['commands'])==1
assert previous['commands'][0]['args'][-2:]==['rev-parse','HEAD']
source=(phase/'publish_repair.py').read_bytes()
assert hashlib.sha256(source).hexdigest()=='37cc2726fa94948611894119c2f3f9eea73c2ff5cb3b54992d01a43476fdfdd2'
program=source.decode('utf-8')
assert program.count("TARGET=PHASE/'publication.json'")==1
program=program.replace("TARGET=PHASE/'publication.json'","TARGET=PHASE/'publication_checked.json'")
old=" assert git('rev-parse','HEAD')=='cbf7c7d81dc42b05bf81ca952d57dda8bafaa2a5'"
assert program.count(old)==1
new=""" parent=git('rev-parse','HEAD');REPORT['publication_parent']=parent
 git('merge-base','--is-ancestor','cbf7c7d81dc42b05bf81ca952d57dda8bafaa2a5',parent)
 additions=git('diff','--name-status','cbf7c7d81dc42b05bf81ca952d57dda8bafaa2a5',parent).splitlines()
 assert all(line.startswith('A\\tresults/s2_2026-09-25/full_text/si_read_round_2026-10-04/') for line in additions),'non-additive concurrent work needs new inspection'
 additional_paths=[line.split('\\t',1)[1] for line in additions]
 REPORT['concurrent_addition_pins']={rel:sha(ROOT/rel) for rel in additional_paths}
 assert git('rev-parse','HEAD')==parent,'parent moved during inspection'"""
program=program.replace(old,new)
assert program.count("phase_files=['.gitattributes'")==1
program=program.replace("phase_files=['.gitattributes'","phase_files=['publication.json','resume_publication.py','git_inspection_checked.json','.gitattributes'")
needle=" REPORT['successful']=True";assert program.count(needle)==1
program=program.replace(needle," for rel,pin in REPORT['concurrent_addition_pins'].items():assert sha(ROOT/rel)==pin,'concurrent SI addition drift: '+rel\n"+needle)
exec(compile(program,str(phase/'publish_repair.py'),'exec'),{'__file__':str(phase/'publish_repair.py'),'__name__':'__main__'})
