#!/usr/bin/env python3
"""DIAGNOSTIC ONLY -- estimate the SCF force noise sigma_F of a mirror-symmetric Hessian
pilot from identities the SCF does NOT enforce (the decks run nosym+noinv), so that any
violation is numerical noise and cannot be anharmonicity:

  (a) in-plane (+/-x, +/-z) decks: an atom ON the mirror plane has F_y == 0 exactly; an
      off-plane atom i and its mirror partner sigma(i) have F_y(i) == -F_y(sigma(i)).
  (b) yp/ym pairs: the ym deck is the exact mirror of the yp deck, so
      F_x,z(ym, i) == F_x,z(yp, sigma(i)) and F_y(ym, i) == -F_y(yp, sigma(i)).
      Two independent SCFs -> residual rms = sqrt(2) * sigma_F.

WHY THIS EXISTS (2026-08-23, Cr *OOH 2x1v, runs/probe/Cr_hess + runs/probe_d02/Cr_hess):
hessian_analyze.py estimates sigma_F from the Hessian's asymmetry H - H^T. On this system
the largest asymmetry sits entirely in the (y, xz) block of the adsorbate partial Hessian,
which mirror symmetry fixes at exactly zero: the column (in-plane displacement -> F_y) IS
zero to 1e-8, but the row (y displacement -> in-plane force, a FORWARD difference) carries
an O(delta) anharmonic term. It doubled exactly when delta doubled (1.548e-1 -> 3.098e-1).
That is not force noise, and a floor propagated from it is not a noise floor.

This script changes no gate, no verdict, and no registered number. It prints a measurement.
Whether the registration's "sigma propagated from the measured force noise" (docs/43
s3-A.3) means the asymmetry estimator or this one is the entrant's call, not this file's.

  PYTHONPATH=src python src/dft/hessian_mirror_noise.py runs/probe/Cr_hess [more dirs]
"""
import re, glob, os, math, sys
def forces(path):
    t=open(path,errors="replace").read(); i=t.rfind("Forces acting on atoms")
    out={}
    for n,fx,fy,fz in re.findall(r"atom\s+(\d+)\s+type\s+\d+\s+force =\s+([-0-9.Ee+]+)\s+([-0-9.Ee+]+)\s+([-0-9.Ee+]+)",t[i:]):
        n=int(n)
        if n in out: break
        out[n]=(float(fx),float(fy),float(fz))
    return out
def geom(path):
    t=open(path,errors="replace").read()
    c=re.search(r"CELL_PARAMETERS[^\n]*\n([^\n]+)\n([^\n]+)\n([^\n]+)",t)
    Lx=float(c.group(1).split()[0]); Ly=float(c.group(2).split()[1])
    pos=re.search(r"ATOMIC_POSITIONS[^\n]*\n((?:\s*\S+\s+[-0-9.]+\s+[-0-9.]+\s+[-0-9.]+[^\n]*\n)+)",t).group(1)
    P=[tuple(float(v) for v in l.split()[1:4]) for l in pos.strip().splitlines()]
    return Lx,Ly,P
def mi(d,L): d=d%L; return min(d,L-d)
for root in (sys.argv[1:] or ("runs/probe/Cr_hess",)):
    Lx,Ly,P=geom(os.path.join(root,"s0_OOH__2x1v_mir__hess_ref.in"))
    y0=P[36][1]; n=len(P); sig={}; dmax=0
    for i,(x,y,z) in enumerate(P):
        ym=2*y0-y
        j,d=min(((k,math.hypot(mi(P[k][0]-x,Lx),mi(P[k][1]-ym,Ly),P[k][2]-z)) for k in range(n)),key=lambda t:t[1])
        sig[i+1]=j+1; dmax=max(dmax,d)
    onp=[i for i in sig if sig[i]==i]; bad=[i for i in sig if sig[sig[i]]!=i]
    print(f"{root}: atoms={n} on-plane={len(onp)} pairs={(n-len(onp))//2} involution-violations={len(bad)} worst-match={dmax:.2e} A")
    a_on=[];a_pr=[];b=[];nin=0;npr=0
    for p in sorted(glob.glob(os.path.join(root,"*_hess_a*.out"))):
        m=re.search(r"_hess_a(\d+)([xyz])([pm])\.out$",p)
        if not m or "JOB DONE" not in open(p,errors="replace").read(): continue
        a,ax,sg=m.groups(); F=forces(p)
        if ax in "xz":
            nin+=1
            for i in F:
                if sig[i]==i: a_on.append(F[i][1])
                elif i<sig[i]: a_pr.append(F[i][1]+F[sig[i]][1])
        elif sg=="p":
            q=p.replace("yp.out","ym.out")
            if not os.path.exists(q) or "JOB DONE" not in open(q,errors="replace").read(): continue
            G=forces(q); npr+=1
            for i in F:
                j=sig[i]; b+=[G[i][0]-F[j][0], G[i][2]-F[j][2], G[i][1]+F[j][1]]
    rms=lambda v: math.sqrt(sum(x*x for x in v)/len(v)) if v else float("nan")
    mx=lambda v: max(abs(x) for x in v) if v else float("nan")
    print(f"  (a) {nin} in-plane decks: on-plane F_y N={len(a_on)} rms={rms(a_on):.2e} max={mx(a_on):.2e} | pair sums N={len(a_pr)} rms={rms(a_pr):.2e} max={mx(a_pr):.2e}  Ry/bohr")
    print(f"  (b) {npr} yp/ym pairs:  mirror residuals N={len(b)} rms={rms(b):.2e} max={mx(b):.2e} Ry/bohr -> sigma_F ~ {rms(b)/math.sqrt(2):.2e}")
print("reference: design sigma_F 1e-05; analyzer asymmetry-based 2.99e-05 (d=0.01) / 1.20e-04 (d=0.02); QE force print resolution 1e-08")
