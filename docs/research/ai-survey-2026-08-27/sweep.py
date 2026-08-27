import os, re, json, sys
SYMOPS = re.compile(r"^\s*(\d+)\s+Sym\. Ops\.", re.M)
NOSYMH = re.compile(r"^\s*No symmetry found", re.M)
NAT    = re.compile(r"number of atoms/cell\s*=\s*(\d+)")
FLINE  = re.compile(r"^\s*atom\s+(\d+)\s+type\s+\d+\s+force =\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)", re.M)
NOSYMD = re.compile(r"^\s*nosym\s*=\s*\.true\.", re.I|re.M)
TOTE   = re.compile(r"^!\s+total energy", re.M)
RELAX  = re.compile(r"BFGS Geometry Optimization|Geometry Optimization")
Z='0.00000000'
out=[]
for dp,_,fs in os.walk('runs'):
    for fn in sorted(fs):
        if not fn.endswith('.out'): continue
        p=os.path.join(dp,fn)
        raw=open(p,'rb').read()
        t=raw.decode('utf-8',errors='ignore')
        if 'Program PWSCF' not in t: continue
        r={'path':p.replace(os.sep,'/'),'bytes':len(raw),'crlf':raw.count(b'\r\n')}
        ms=SYMOPS.search(t); r['nops']=int(ms.group(1)) if ms else (1 if NOSYMH.search(t) else None)
        r['nosym_hdr']=bool(NOSYMH.search(t))
        mn=NAT.search(t); r['nat']=int(mn.group(1)) if mn else None
        r['scfblk']=len(TOTE.findall(t)); r['calc']='relax' if RELAX.search(t) else 'scf'
        d=p[:-4]+'.in'
        r['nosym_deck']=bool(NOSYMD.search(open(d,errors='ignore').read())) if os.path.exists(d) else None
        S=[];c={}
        for m in FLINE.finditer(t):
            i=int(m.group(1))
            if i==1 and c: S.append(c); c={}
            c[i]=(m.group(2),m.group(3),m.group(4))
        if c:S.append(c)
        r['steps']=len(S)
        r['negzero']=t.count('-0.00000000')
        nads=0
        for tag,n in (('s0_OOH',3),('s0_OH',2),('s0_O',1)):
            if fn.startswith(tag): nads=n; break
        r['nads']=nads
        if S and nads and r['nat']:
            ads=[i for i in range(r['nat']-nads+1, r['nat']+1) if any(i in s for s in S)]
            r['ads']=ads
            if ads:
                for ax,nm in ((0,'x'),(1,'y')):
                    allz=all(all(s[a][ax].lstrip('-')==Z for s in S if a in s) for a in ads)
                    anyz=any(all(s[a][ax].lstrip('-')==Z for s in S if a in s) for a in ads)
                    mx=max(abs(float(s[a][ax])) for a in ads for s in S if a in s)
                    r[f'{nm}_all']=allz; r[f'{nm}_any']=anyz; r[f'max_f{nm}']=mx
        out.append(r)
json.dump(out, open(sys.argv[1],'w'), indent=0)
print(f"scanned {len(out)} pw.x outputs")
