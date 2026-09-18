"""Independent raw-output recomputation of P-XU numerators and U spans.

No silentgate or primary adapter functions are imported. Paths come from the
pinned mirror tree; force rows and decimal energies are reparsed independently.
"""
from __future__ import annotations
import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?"


def val(s):
    n = Decimal(s.replace("D", "E").replace("d", "e"))
    if not n.is_finite():
        raise ValueError("nonfinite independent decimal")
    return n


def input_info(text):
    nat = int(re.search(r"\bnat\s*=\s*(\d+)", text, re.I)[1])
    kind = re.search(r"\bcalculation\s*=\s*['\"]([^'\"]+)", text, re.I)
    units = re.search(r"ATOMIC_POSITIONS\s*[({]?\s*(\w+)", text, re.I)[1].lower()
    body = re.split(r"ATOMIC_POSITIONS[^\n]*\n", text, flags=re.I)[1]
    atoms = []
    for line in body.splitlines()[:nat]:
        fields = line.split()
        atoms.append((re.sub(r"\d+$", "", fields[0]), [val(x) for x in fields[1:4]],
                      [int(x) for x in fields[4:7]] or [1,1,1]))
    if units == "crystal":
        cell = re.split(r"CELL_PARAMETERS[^\n]*\n", text, flags=re.I)[1]
        matrix = [[val(x) for x in line.split()] for line in cell.splitlines()[:3]]
        atoms = [(symbol,[sum(p[j]*matrix[j][k] for j in range(3)) for k in range(3)],mask) for symbol,p,mask in atoms]
    return dict(nat=nat, atoms=atoms, calculation=kind[1] if kind else None)


def forces(text):
    blocks, current, mode = [], None, "outside"
    errors = []
    def close():
        nonlocal current
        if current is not None:
            blocks.append(current)
            current = None
    for line in text.replace("\x00", "\n").splitlines():
        if "Forces acting on atoms" in line:
            close(); current = {}; mode = "total"; continue
        if re.search(r"(?:contrib\.|contribution|SCF correction term).*forces", line, re.I):
            close(); mode = "contribution"; continue
        if re.match(r"\s*Total force\s*=",line,re.I):
            close(); mode = "outside"; continue
        row = re.fullmatch(r"\s*atom\s+(\d+)\s+type\s+\d+\s+force\s*=\s*("+NUMBER+r")\s+("+NUMBER+r")\s+("+NUMBER+r")\s*",line,re.I)
        if row and mode != "contribution":
            if current is None:
                current = {}; mode = "total"
            index = int(row[1])
            if index in current:
                errors.append("duplicate force row")
            current[index] = [val(x) for x in row.groups()[1:]]
        elif re.match(r"\s*atom\s+\d+\s+type\s+\d+\s+force\s*=",line) and mode != "contribution":
            errors.append("malformed force row")
        elif line.strip() and current:
            close(); mode = "outside"
    close()
    return blocks, errors


def independently_usable(text, kind):
    tokens = re.findall(r"(?im)^\s*!\s+total energy\s*=\s*("+NUMBER+r")\s+Ry\b", text)
    energies = [val(x) for x in tokens]
    scfs = re.findall(r"convergence has been achieved in\s+(\d+)\s+iterations",text)
    bfgs = re.findall(r"bfgs converged in\s+(\d+)\s+scf cycles and\s+(\d+)\s+bfgs steps",text,re.I)
    failed = bool(re.search(r"convergence NOT achieved|Maximum (?:CPU|wall) time exceeded|maximum number of steps has been reached|Error in routine|MPI_ABORT|SIGSEGV|SIGFPE|IEEE_(?:INVALID|OVERFLOW|DIVIDE_BY_ZERO)(?:_FLAG)?|Program stopped by user request",text,re.I))
    usable = not failed and text.count("JOB DONE")==1 and bool(energies) and len(energies)==len(scfs)
    if kind == "relax":
        usable = usable and len(bfgs)==1 and int(bfgs[0][0])==len(energies)
    else:
        usable = usable and kind=="scf" and len(energies)==1
    return energies[-1] if usable else None


def rate_status(n, missing, total):
    if total and Decimal(n)/total >= Decimal("0.90"):
        return "HELD"
    if total and Decimal(n+missing)/total < Decimal("0.75"):
        return "FALSIFIED"
    if missing or not total:
        return "INCOMPLETE EVIDENCE"
    return "SCORED — MIDDLE BAND / NOT MET"


def verify(primary, corpus):
    tree = ROOT / "docs/research/2026-08-15-sampling/xu_tree.json"
    if hashlib.sha256(tree.read_bytes()).hexdigest() != "d20af9dbfbbbdc05714b352ac15b176e75b4096f5bff475159395187c957e8b9":
        raise ValueError("independent tree identity mismatch")
    manifest = json.loads(tree.read_text())
    selected = sorted(r["path"] for r in manifest["tree"] if r["type"]=="blob" and "/Eads-" in r["path"] and r["path"].endswith("/pwscf.out"))
    if len(selected)!=810 or set(selected)!={r["output"] for r in primary["rows"]}:
        raise ValueError("independent population mismatch")
    known = {r["output"]:r for r in primary["rows"]}
    metadata = {}
    for name in selected:
        metadata[name] = input_info((corpus / name).with_suffix(".in").read_text())
    differences, raw = [], []
    def compare(label, observed, expected):
        if observed != expected:
            differences.append(dict(check=label, independent=observed, primary=expected))
    # Original Git blob hashes are independent of the primary result's SHA-256 list.
    blob_map = {r["path"]:r for r in manifest["tree"] if r["type"]=="blob"}
    for name in selected:
        for file in (name, name[:-3]+"in"):
            data=(corpus/file).read_bytes()
            blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
            if blob!=blob_map[file]["sha"] or len(data)!=blob_map[file]["size"]:
                raise ValueError("independent corpus mismatch: "+file)
        text=(corpus/name).read_text(errors="replace")
        _,metal,layer,job,_=name.split("/")
        layer=int(re.search(r"\d+",layer)[0])
        state=job.split("-")[0]
        u=job.split("-U-")[1] if "-U-" in job else None
        deck=metadata[name]
        bares=[v for k,v in metadata.items() if k.startswith(f"supporting-data/{metal}/Eads-{layer}-layers/bare")]
        counts={b["nat"] for b in bares}
        unidentified=len(counts)!=1
        bare_nat=next(iter(counts)) if len(counts)==1 else None
        if bare_nat is not None:
            ads=list(range(bare_nat+1,deck["nat"]+1))
            top=max(p[2] for s,p,m in deck["atoms"] if s not in ("O","H"))
            unidentified=any(deck["atoms"][i-1][0] not in ("O","H") or deck["atoms"][i-1][1][2]<=top for i in ads)
            unidentified=unidentified or any([s for s,p,m in b["atoms"]]!=[s for s,p,m in deck["atoms"][:bare_nat]] for b in bares)
        else:
            ads=[]
        eligible=[i for i in ads if 0 not in deck["atoms"][i-1][2]]
        blocks, errors=forces(text)
        scorable=bool(eligible) and bool(blocks) and not errors and not unidentified and all(all(i in b for i in ads) for b in blocks)
        final=[a for k,a in enumerate(("x","y")) if all(blocks[-1][i][k]==0 for i in eligible)] if scorable else None
        every=[a for k,a in enumerate(("x","y")) if all(b[i][k]==0 for b in blocks for i in eligible)] if scorable else None
        sym=[]
        for line in text.splitlines():
            m=re.search(r"\b(\d+)\s+Sym\.\s*Ops\..*found",line,re.I)
            if not m:
                m=re.search(r"Sym\.\s*Ops\..*found\s+(\d+)",line,re.I)
            if m: sym.append(int(m[1]))
            elif "No symmetry found" in line: sym.append(1)
        header=sym[0] if sym and len(set(sym))==1 else None
        energy=independently_usable(text,deck["calculation"])
        p=known[name]
        for key,actual,expected in (("header",header,p["header"]["n_symops"]),("unidentified",unidentified,p["unidentified"]),
            ("eligible",eligible,p["force"]["eligible_adsorbate_indices"]),("force_blocks",len(blocks),p["force"]["n_force_steps"]),
            ("final_axes",final,p["force"]["final_all_atom_zero_lateral_axes"]),("all_step_axes",every,p["force"]["every_step_all_atom_zero_lateral_axes"]),
            ("energy_usable",energy is not None,p["energy"]["usable"])):
            compare(name+":"+key,actual,expected)
        if energy is not None: compare(name+":energy",str(energy),p["energy"]["final_energy_Ry"])
        raw.append(dict(path=name,metal=metal,layer=layer,job=job,state=state,u=u,header=header,unidentified=unidentified,blocks=len(blocks),final=final,every=every,energy=energy))
    headers=sum(r["header"] is not None and r["header"]>1 for r in raw)
    hu=sum(r["header"] is None for r in raw)
    ads=[r for r in raw if r["state"]!="bare"]
    eligible=[r for r in ads if not r["unidentified"] and r["blocks"]]
    fn=sum(bool(r["final"]) for r in eligible)
    fu=sum(r["final"] is None for r in eligible)
    direction=[]
    for metal in sorted({r["metal"] for r in raw}):
        pair=[next(r for r in raw if r["metal"]==metal and r["layer"]==4 and r["job"]==s+"-relax") for s in ("OH","OOH")]
        axes=[r["every"] for r in pair]
        direction.append(None if any(a is None for a in axes) else all(len(a)==1 for a in axes) and axes[0]!=axes[1])
    dn=sum(x is True for x in direction); du=sum(x is None for x in direction)
    compare("header numerator",headers,primary["P_XU"]["header"]["successes"])
    compare("force numerator",fn,primary["P_XU"]["final_force"]["successes"])
    compare("force unknown",fu,primary["P_XU"]["final_force"]["unknown"])
    compare("force denominator",len(eligible),primary["P_XU"]["final_force"]["denominator"])
    compare("named pair numerator",dn,primary["P_XU"]["named_pair_direction"]["successes"])
    ds="HELD" if dn>=8 else "FALSIFIED" if dn+du<=4 else "INCOMPLETE EVIDENCE" if du else "SCORED — MIDDLE BAND / NOT MET"
    statuses=[rate_status(headers,hu,810),rate_status(fn,fu,len(eligible)),ds]
    verdict="FALSIFIED" if "FALSIFIED" in statuses else "HELD" if set(statuses)=={"HELD"} else "INCOMPLETE EVIDENCE" if "INCOMPLETE EVIDENCE" in statuses else "SCORED — MIDDLE BAND / NOT MET"
    compare("combined P-XU",verdict,primary["P_XU"]["outcome"])
    spans=[]
    for metal in sorted({r["metal"] for r in raw}):
        pm=next(m for m in primary["P_XU_SPAN"]["metals"] if m["metal"]==metal)
        result={"metal":metal}
        for quantity,left in (("cM_electronic_eV","OOH"),("dG2_electronic_eV","O")):
            values=[]
            for u in sorted({r["u"] for r in raw if r["u"] is not None},key=Decimal):
                a=next(r for r in raw if r["metal"]==metal and r["u"]==u and r["state"]==left)
                b=next(r for r in raw if r["metal"]==metal and r["u"]==u and r["state"]=="OH")
                if a["energy"] is not None and b["energy"] is not None:
                    values.append((a["energy"]-b["energy"])*Decimal("13.605693122"))
            span=max(values)-min(values) if values else None
            pp=pm["spans"][quantity]
            compare(metal+":"+quantity+":pairs",len(values),pp["paired_usable_rungs"])
            compare(metal+":"+quantity+":range",str(span) if span is not None else None,pp["observed_range_lower_bound_eV"])
            result[quantity]=dict(pairs=len(values),range_eV=str(span) if span is not None else None)
        spans.append(result)
    n=sum(s["cM_electronic_eV"]["pairs"]==17 and Decimal(s["cM_electronic_eV"]["range_eV"])>Decimal(".20") for s in spans)
    missing=sum(s["cM_electronic_eV"]["pairs"]!=17 for s in spans)
    sv="HELD" if n>=5 else "FALSIFIED" if n+missing<3 else "INCOMPLETE EVIDENCE" if missing else "SCORED — MIDDLE BAND / NOT MET"
    compare("span verdict",sv,primary["P_XU_SPAN"]["outcome"])
    compare("full-ladder exceeding count",n,primary["P_XU_SPAN"]["full_ladder_exceeding_count"])
    return dict(schema="xu-independent-verification-v1",status="PASS" if not differences else "FAIL",
                outputs_reparsed=len(raw),inputs_reparsed=len(metadata),differences=differences,
                header_successes=headers,force_successes=fn,force_unknown=fu,force_denominator=len(eligible),
                direction_successes=dn,direction_unknown=du,P_XU=verdict,P_XU_SPAN=sv,spans=spans)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--primary",required=True,type=Path)
    p.add_argument("--corpus",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args(argv)
    if a.corpus.resolve() in a.out.resolve().parents:
        p.error("write verification outside corpus")
    result=verify(json.loads(a.primary.read_text(encoding="utf-8")),a.corpus)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","outputs_reparsed","P_XU","P_XU_SPAN")}),flush=True)
    return 0 if result["status"]=="PASS" else 2


if __name__=="__main__":
    raise SystemExit(main())
