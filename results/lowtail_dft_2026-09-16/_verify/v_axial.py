import json, os, numpy as np, hashlib
os.chdir(r"C:\Users\frank\sts-electrocatalyst")
S=[("results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json",1,0),
   ("results/site_census_2026-09-06/results/mpa0__Fe25Co25Ni25Cr25_result.json",2,0),
   ("results/site_census_2026-09-06/results/mpa0_ext__Cu26Ni9Cr31Co33__s03-05_result.json",5,2),
   ("results/site_census_2026-09-06/results/mpa0_ext__Cu8Cr23Mn35Co34__s18-20_result.json",20,2)]
def mic(v,c):
    L=np.diag(np.array(c)); return v-L*np.round(v/L)
rows=[]
for p,seed,site in S:
    d=json.load(open(p)); rw=[r for r in d['results'] if r['status']=='evaluated'][0]['row']
    ps=[x for x in rw['per_site_records'] if x['seed']==seed and x['site_index']==site][0]
    sl=[x for x in rw['decoration_records'] if x['seed']==seed][0]['relaxed_slab']
    m=ps['initial_binding_metal_index']; c=np.array(sl['positions_A']); cell=sl['cell_A']
    O=np.array(ps['relaxed_states']['O']['positions_A'])
    # axial: nearest O below the site metal in clean slab
    best=None
    for j,s in enumerate(sl['symbols']):
        if s!='O': continue
        v=mic(c[j]-c[m],cell); dd=np.linalg.norm(v)
        if v[2]<-1.0 and (best is None or dd<best[1]): best=(j,dd)
    ax=best[0]
    rows.append(dict(p=p,metal=sl['symbols'][m],m=m,ax=ax,clean=best[1],O=float(np.linalg.norm(mic(O[ax]-O[m],cell))),lift=float(mic(O[m]-c[m],cell)[2]),sha=hashlib.sha256(open(p,'rb').read()).hexdigest()[:12]))
for r in rows: print(r)
cm=max(r['clean'] for r in rows); om=min(r['O'] for r in rows); print('mid', (cm+om)/2, cm, om)
