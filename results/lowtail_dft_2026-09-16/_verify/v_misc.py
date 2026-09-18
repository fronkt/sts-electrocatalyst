import json, os, re, glob, numpy as np
os.chdir(r"C:\Users\frank\sts-electrocatalyst")
Z=json.load(open("results/lowtail_dft_2026-09-16/_verify/v_zero.json"))
FC=Z["consts"]["F_CONV"]
worst=0
for q in sorted(glob.glob("runs/hea/winner_2026-09-10/*.qc.json")):
    d=json.load(open(q))
    stored=np.array([a["force_ev_A"] for a in d["scf"]["per_atom"]])
    out=q.replace(".qc.json",".out")
    L=open(out,encoding="utf-8",errors="replace").read().splitlines()
    h=[i for i,l in enumerate(L) if "Forces acting on atoms" in l][0]
    F=[]
    for l in L[h+1:]:
        m=re.match(r"^\s*atom\s+\d+\s+type\s+\d+\s+force\s*=\s*(\S+)\s+(\S+)\s+(\S+)",l)
        if m: F.append([float(m.group(k)) for k in (1,2,3)])
        if len(F)==len(stored): break
    F=np.array(F)
    # conversion used by stored audit
    ratio=np.median((stored[np.abs(F)>1e-3]/F[np.abs(F)>1e-3]))
    diff=np.max(np.abs(stored-F*25.71104309541616))
    diff2=np.max(np.abs(stored-F*FC))
    worst=max(worst,diff)
    print(os.path.basename(q)[-18:], len(stored), 'ratio %.12f'%ratio, 'maxdiff(audit const) %.2e'%diff, 'maxdiff(CODATA) %.2e'%diff2, 'sha_out', d['output'].get('sha256_bytes','')[:10])
# desorbed seed-0 OOH endpoints: nearest metal to O72
rep={a["start"]:a for a in json.load(open("results/cr_site_chains_2026-09-06/leader_ooh_replay.json"))["attempts"]}
cen=json.load(open("results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json"))
row=cen["results"][0]["row"]; s0=[x for x in row["per_site_records"] if x["seed"]==0 and x["site_index"]==0][0]
for k in ("builder","pull2.10"):
    g=rep[k]["geometry"]; P=np.array(g["positions_A"]); c=g["cell_A"]
    mets=[j for j,s in enumerate(g["symbols"]) if s not in ("O","H")]
    ds=sorted((np.linalg.norm((P[72]-P[j])-np.diag(c)*np.round((P[72]-P[j])/np.diag(c))),j,g["symbols"][j]) for j in mets)
    print(k, 'O72 nearest metal', ds[0], 'Cr16 dist %.3f'%[x for x in ds if x[1]==16][0][0], 'nat', len(P))
    cs={r["start"]:r["energy_eV"] for r in s0["start_records"]["OOH"]}
    print('  replay-census start dE', rep[k]["energy_eV"]-cs[k])
