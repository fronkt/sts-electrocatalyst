import json, os, re, numpy as np
os.chdir(r"C:\Users\frank\sts-electrocatalyst")
Z=json.load(open("results/lowtail_dft_2026-09-16/_verify/v_zero.json"))
FC=Z["consts"]["F_CONV"]
cen=json.load(open("results/site_census_2026-09-06/results/mpa0__Ni31Cr29Cu5Mn35_result.json"))
row=cen["results"][0]["row"]; s1=[x for x in row["per_site_records"] if x["seed"]==1 and x["site_index"]==0][0]
slab=[x for x in row["decoration_records"] if x["seed"]==1][0]["relaxed_slab"]
masses={"Cr":51.996,"O":15.999}
for st,job in (("O","g_80ebe76a616d61d6fecca57d1cd6c2ef27990771fbc3db9a8cfea6a4bf228e5c"),("slab","g_bd2523d558a6d76f7856eae53f3de623869b6bd1fb927bed3aaea5a06b693ba1")):
    g = s1["relaxed_states"]["O"] if st=="O" else slab
    P=np.array(g["positions_A"]); c=np.diag(np.array(g["cell_A"]))
    for pj in ("atomic","ortho"):
        L=open(f"runs/hea/winner_2026-09-10/{job}__{pj}.out",encoding="utf-8",errors="replace").read().splitlines()
        h=[i for i,l in enumerate(L) if "Forces acting on atoms" in l][0]
        F=[]
        for l in L[h+1:]:
            m=re.match(r"^\s*atom\s+\d+\s+type\s+\d+\s+force\s*=\s*(\S+)\s+(\S+)\s+(\S+)",l)
            if m: F.append([float(m.group(k))*FC for k in (1,2,3)])
            if len(F)==len(P): break
        F=np.array(F)
        v=P[40]-P[16]; v=v-c*np.round(v/c); u=v/np.linalg.norm(v)
        o40_toward_cr=float(-F[40]@u)
        cr_away_from_o40=float(-F[16]@u)
        res=dict(state=st,proj=pj,u_z=round(float(u[2]),3),F_O40_toward_Cr=round(o40_toward_cr,3),F_Cr_away_from_O40=round(cr_away_from_o40,3),
                 axial_stretch=round(float((F[40]-F[16])@u),3))
        if st=="O":
            mCr,mO=masses["Cr"],masses["O"]
            # acceleration of pair centre of mass vs O40 along u (force per mass)
            a_pair=(F[16]+F[72])@u/(mCr+mO); a_O40=F[40]@u/mO
            res.update(pair_force_along_u=round(float((F[16]+F[72])@u),3), relative_accel_O40_minus_pairCOM_along_u_eV_per_A_amu=round(float(a_O40-a_pair),4),
                       F_O72_along_u=round(float(F[72]@u),3))
        print(res)
