import json, os, re, numpy as np
os.chdir(r"C:\Users\frank\sts-electrocatalyst")
man=open("runs/m_research_2026-09-16_hea_pilot.txt").read().splitlines()
for tag,path,seed,site in (("Fe25Co25Ni25Cr25__s2_site0","results/site_census_2026-09-06/results/mpa0__Fe25Co25Ni25Cr25_result.json",2,0),("Ni31Cr29Cu5Mn35__s0_site0","results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json",0,0)):
    rw=json.load(open(path))["results"][0]["row"]
    ps=[x for x in rw["per_site_records"] if x["seed"]==seed and x["site_index"]==site][0]
    sl=[x for x in rw["decoration_records"] if x["seed"]==seed][0]["relaxed_slab"]
    O=ps["relaxed_states"]["O"]; m=ps["initial_binding_metal_index"]
    c=np.diag(np.array(O["cell_A"])); v=np.array(O["positions_A"][m])-np.array(sl["positions_A"][m]); v=v-c*np.round(v/c)
    for pj in ("atomic","ortho"):
        L=open(f"runs/hea/pilot_retained/{tag}/O__{pj}.in").read().splitlines()
        ai=[i for i,l in enumerate(L) if l.startswith("ATOMIC_POSITIONS")][0]
        P=[[float(x) for x in L[ai+1+k].split()[1:4]] for k in range(len(O["symbols"]))]
        print(tag,pj,"metal",sl["symbols"][m],m,"lift %.3f"%v[2],"equal",P==O["positions_A"],"in_manifest",f"hea/pilot_retained/{tag} O__{pj} .in 8" in man, "out exists", os.path.exists(f"runs/hea/pilot_retained/{tag}/O__{pj}.out"))
