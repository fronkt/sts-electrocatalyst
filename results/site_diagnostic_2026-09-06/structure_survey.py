# Run from repository root. This contains no model evaluation.
import sys, json, argparse
from pathlib import Path
sys.path.insert(0, 'src')
from hea_oer.composition import Composition
from hea_oer.surfaces_rutile import build_rutile110_hea, cus_site_xy, add_oer_adsorbate_at, binding_metal_index
source=Path('results/ranking_adequacy_2026-09-06/inputs/r4_screen_box.json')
from scripts.screen_diagnostic import sha256_file
rows=json.loads(source.read_text())['rows']
records=[]
for row in rows:
 comp=Composition(tuple(row['elements']),tuple(row['fractions']))
 record={'formula':row['formula'],'target_fractions':comp.as_dict(),'decorations':[]}
 for seed in (0,1,2):
  slab=build_rutile110_hea(comp,seed=seed)
  counts={el:slab.get_chemical_symbols().count(el) for el in comp.elements}
  n=sum(counts.values()); realized={el:v/n for el,v in counts.items()}
  sites=[]
  for i,xy in enumerate(cus_site_xy(slab,n_sites=4)):
   idx=binding_metal_index(add_oer_adsorbate_at(slab,'O',xy),len(slab))
   sites.append({'site_index':i,'binding_metal_index':idx,'metal':slab[idx].symbol,'xy_A':list(xy)})
  record['decorations'].append({'seed':seed,'n_atoms':len(slab),'n_cations':n,'cation_counts':counts,'cation_fractions':realized,'sites':sites,'max_fraction_error':max(abs(realized[e]-comp.as_dict()[e]) for e in realized)})
 records.append(record)
 print(row['formula'],counts, [s['metal'] for d in record['decorations'] for s in d['sites']], flush=True)
parser=argparse.ArgumentParser(description='Inspect pristine finite-cell composition and cus-site coverage without a calculator.')
parser.add_argument('--out', type=Path, default=Path('results/site_diagnostic_2026-09-06/structure_survey.json'))
out=parser.parse_args().out;out.parent.mkdir(parents=True,exist_ok=True)
payload={'kind':'pristine_geometry_survey_no_model_evaluation','source_sha256_lf':sha256_file(source,normalize_lf=True),'implementation_sha256_lf':{p:sha256_file(p,normalize_lf=True) for p in ['src/hea_oer/surfaces_rutile.py','src/hea_oer/surfaces.py','src/hea_oer/composition.py']},'records':records}
with out.open('x', encoding='utf-8', newline='\n') as handle:
 handle.write(json.dumps(payload,indent=2,allow_nan=False)+'\n')
