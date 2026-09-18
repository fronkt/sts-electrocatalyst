"""Structure-type assignments for PbO2, OsO2, SnO2, GeO2 and PtO2.

Evidence layers, all cached before they are read:

1. COD (Crystallography Open Database) -- every entry returned for the formula;
   each CIF is parsed and its space group and Wyckoff sites are recomputed with
   spglib (symprec 0.01 A), independent of the header the CIF declares. A
   prototype is assigned by explicit (space group, cation site, anion site)
   rules (``PROTOTYPES``); anything else is reported as its space group only.
2. Materials Project -- the summary documents for the formula (space group,
   energy above hull, ICSD cross-references) and, where a claim names one, the
   robocrystallographer description.

Claims live in ``data/structure_claims.json`` with the file, line and a verbatim
fragment; the fragment is re-found in the file before a claim is evaluated. Each
claim is split into the sub-claims its sentence makes, and each sub-claim gets the
registered binary verdict (docs/43 :1945): CLEARED only when every evidence test
passes, EXCLUDED otherwise.
"""
from __future__ import annotations

import json
import os
import re
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

from .common import Fetcher, cache_key, read_lines, rel, REPO

COD_SEARCH = "https://www.crystallography.net/cod/result?"
COD_CIF = "https://www.crystallography.net/cod/{id}.cif"
MP_SUMMARY = "https://api.materialsproject.org/materials/summary/?"
MP_ROBOCRYS = "https://api.materialsproject.org/materials/robocrys/?"

FORMULAS = {"PbO2": ("O2 Pb", "Pb"), "OsO2": ("O2 Os", "Os"), "SnO2": ("O2 Sn", "Sn"),
            "GeO2": ("Ge O2", "Ge"), "PtO2": ("O2 Pt", "Pt")}
# formulas read only to test a sub-claim about a mineral label (not part of the five)
REFERENCE_FORMULAS = {"CaCl2": ("Ca Cl2", "Ca", "Cl")}

CLEARED, EXCLUDED = "CLEARED", "EXCLUDED"      # docs/43 :1945 "each cleared or excluded"

# (space-group numbers, cation Wyckoff letters, anion Wyckoff letters) -> prototype
PROTOTYPES = [
    ("rutile", {136}, {"a"}, {"f"}),
    ("CaCl2", {58}, {"a"}, {"g"}),
    ("alpha-PbO2", {60}, {"c"}, {"d"}),
    ("CdI2", {164}, {"a"}, {"d"}),
    ("alpha-quartz", {152, 154}, {"a", "b"}, {"c"}),
    ("fluorite", {225}, {"a"}, {"c"}),
    ("pyrite", {205}, {"a"}, {"c"}),
]

AMBIENT_MAX_KPA = 1000.0   # COD pressures are in kPa; <= 1 MPa counts as ambient
SYMPREC = 0.01             # Angstrom, spglib tolerance for the recomputed space group


def classify(sg_number: int, cation_wyckoffs: set, anion_wyckoffs: set) -> str:
    for name, sgs, cat, an in PROTOTYPES:
        if sg_number in sgs and cation_wyckoffs and cation_wyckoffs <= cat and \
                anion_wyckoffs and anion_wyckoffs <= an:
            return name
    return f"sg{sg_number}"


def analyse_cif(cif_text: str, cation: str, anion: str = "O") -> dict:
    """Recompute space group and prototype from CIF coordinates."""
    import warnings

    from pymatgen.io.cif import CifParser
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        parser = CifParser.from_str(cif_text, occupancy_tolerance=1.05)
        try:
            structs = parser.parse_structures(primitive=False)
        except AttributeError:  # older pymatgen
            structs = parser.get_structures(primitive=False)
    if not structs:
        raise ValueError("no structure parsed")
    s = structs[0]
    comp = s.composition.reduced_composition
    elements = sorted(str(e) for e in comp.elements)
    sga = SpacegroupAnalyzer(s, symprec=SYMPREC, angle_tolerance=5)
    ds = sga.get_symmetry_dataset()
    wyck = ds.wyckoffs if hasattr(ds, "wyckoffs") else ds["wyckoffs"]
    number = ds.number if hasattr(ds, "number") else ds["number"]
    symbol = ds.international if hasattr(ds, "international") else ds["international"]
    by_el = defaultdict(set)
    for site, w in zip(s, wyck):
        for sp in site.species:
            by_el[str(sp.element if hasattr(sp, "element") else sp)].add(w)
    cat = by_el.get(cation, set())
    an = by_el.get(anion, set())
    ratio = comp.get(cation, 0) and comp.get(anion, 0) / comp.get(cation, 1)
    return {"sg_number_computed": int(number), "sg_symbol_computed": symbol,
            "cation_wyckoff": sorted(cat), "anion_wyckoff": sorted(an),
            "elements": elements, "anion": anion, "anion_per_cation": round(float(ratio), 4),
            "n_sites_cell": len(s), "prototype": classify(int(number), cat, an)}


HIGH_P_TITLE = ("high pressure", "high-pressure", "ab initio", "high oxygen pressure")


def ambient_status(pressure_kpa, title) -> dict:
    """Ambient if COD records a pressure <= AMBIENT_MAX_KPA; if no pressure is recorded,
    ambient unless the source title names high pressure or an ab initio calculation."""
    if pressure_kpa is not None:
        return {"ambient_pressure": pressure_kpa <= AMBIENT_MAX_KPA, "ambient_basis": "recorded pressure"}
    t = (title or "").lower()
    hit = next((k for k in HIGH_P_TITLE if k in t), None)
    return {"ambient_pressure": hit is None,
            "ambient_basis": f"no pressure recorded; title contains '{hit}'" if hit
            else "no pressure recorded; title silent"}


def _pressure(row: dict):
    vals = [row.get("cellpressure"), row.get("diffrpressure")]
    vals = [float(v) for v in vals if v not in (None, "")]
    return max(vals) if vals else None


def cod_census(fetcher: Fetcher, formula: str) -> dict:
    if formula in FORMULAS:
        (query, cation), anion = FORMULAS[formula], "O"
    else:
        query, cation, anion = REFERENCE_FORMULAS[formula]
    qs = urllib.parse.urlencode({"formula": query, "format": "json"})
    r = fetcher.get(COD_SEARCH + qs, cache_key(qs, "cod_search_"), "json")
    rows = r.json() if r.status == 200 else []
    entries, failures = [], []
    for row in sorted(rows, key=lambda x: int(x["file"])):
        cid = row["file"]
        c = fetcher.get(COD_CIF.format(id=cid), f"cod_{cid}", "cif")
        base = {"cod_id": cid, "sg_declared": row.get("sg"), "sg_number_declared": row.get("sgNumber"),
                "a": row.get("a"), "b": row.get("b"), "c": row.get("c"), "mineral": row.get("mineral"),
                "chemname": row.get("chemname"), "authors": row.get("authors"), "year": row.get("year"),
                "title": row.get("title"), "journal": row.get("journal"), "volume": row.get("volume"),
                "firstpage": row.get("firstpage"), "doi": row.get("doi"),
                "pressure_kPa": _pressure(row), "temperature_K": row.get("celltemp") or row.get("diffrtemp"),
                "cif_sha256": None, "cif_file": c.body_path.name}
        from .common import sha256_bytes
        base["cif_sha256"] = sha256_bytes(c.body)
        base.update(ambient_status(base["pressure_kPa"], base["title"]))
        if c.status != 200:
            failures.append({**base, "reason": f"CIF HTTP {c.status}"})
            continue
        try:
            base.update(analyse_cif(c.text(), cation, anion))
        except Exception as e:  # noqa: BLE001 -- every failure is counted on the face
            failures.append({**base, "reason": f"{type(e).__name__}: {e}"[:300]})
            continue
        entries.append(base)
    types = Counter(e["prototype"] for e in entries)
    return {"formula": formula, "cod_query": query, "n_returned": len(rows),
            "n_parsed": len(entries), "n_unparsed": len(failures), "entries": entries,
            "unparsed": failures, "prototype_counts": dict(sorted(types.items())),
            "search_cache_file": r.body_path.name}


def mp_key() -> str | None:
    k = os.environ.get("MP_API_KEY") or os.environ.get("PMG_MAPI_KEY")
    if k:
        return k
    try:
        from pymatgen.core import SETTINGS
        return SETTINGS.get("PMG_MAPI_KEY")
    except Exception:  # noqa: BLE001
        return None


MP_FIELDS = "material_id,formula_pretty,symmetry,energy_above_hull,is_stable,theoretical,database_IDs"


def mp_summary(fetcher: Fetcher, formula: str) -> dict:
    qs = urllib.parse.urlencode({"formula": formula, "_fields": MP_FIELDS, "_limit": 100})
    key = mp_key()
    r = fetcher.get(MP_SUMMARY + qs, cache_key(qs, "mp_summary_"), "json",
                    secret_headers={"X-API-KEY": key} if key else None)
    data = r.json().get("data", []) if r.status == 200 else []
    docs = []
    for d in data:
        sym = d.get("symmetry") or {}
        docs.append({"material_id": d.get("material_id"), "sg_symbol": sym.get("symbol"),
                     "sg_number": sym.get("number"), "e_above_hull_eV_atom": d.get("energy_above_hull"),
                     "is_stable": d.get("is_stable"), "theoretical": d.get("theoretical"),
                     "icsd_ids": sorted((d.get("database_IDs") or {}).get("icsd", []))})
    docs.sort(key=lambda x: (x["e_above_hull_eV_atom"] if x["e_above_hull_eV_atom"] is not None
                             else 9e9, x["material_id"]))
    return {"formula": formula, "status": r.status, "n": len(docs), "docs": docs,
            "cache_file": r.body_path.name}


def mp_by_ids(fetcher: Fetcher, legacy_id: str) -> dict:
    qs = urllib.parse.urlencode({"material_ids": legacy_id, "_fields": MP_FIELDS})
    key = mp_key()
    r = fetcher.get(MP_SUMMARY + qs, cache_key(qs, "mp_summary_id_"), "json",
                    secret_headers={"X-API-KEY": key} if key else None)
    s = fetcher.get(MP_ROBOCRYS + urllib.parse.urlencode(
        {"material_ids": legacy_id, "_fields": "material_id,description,condensed_structure"}),
        cache_key(legacy_id, "mp_robocrys_"), "json", secret_headers={"X-API-KEY": key} if key else None)
    summ = (r.json().get("data") or [{}])[0] if r.status == 200 else {}
    robo = (s.json().get("data") or [{}])[0] if s.status == 200 else {}
    sym = summ.get("symmetry") or {}
    cond = robo.get("condensed_structure") or {}
    return {"queried_id": legacy_id, "material_id": summ.get("material_id"),
            "sg_symbol": sym.get("symbol"), "sg_number": sym.get("number"),
            "e_above_hull_eV_atom": summ.get("energy_above_hull"),
            "robocrys_mineral_type": (cond.get("mineral") or {}).get("type"),
            "robocrys_description": robo.get("description"),
            "cache_files": [r.body_path.name, s.body_path.name]}


# ---------------------------------------------------------------------------
# claims

def locate(fragment: str, path: Path, line: int) -> dict:
    lines = read_lines(path)
    if 1 <= line <= len(lines) and fragment in lines[line - 1]:
        return {"found": True, "line": line, "drifted": False}
    hits = [i for i, t in enumerate(lines, 1) if fragment in t]
    return {"found": bool(hits), "line": hits[0] if hits else None, "drifted": bool(hits)}


def _params(chk: dict) -> dict:
    return {k: v for k, v in chk.items() if k != "kind"}


def formal_d_count(element: str, oxidation_state: int) -> dict:
    """d-electron count of a cation: remove electrons from the neutral configuration in
    order of decreasing n, then decreasing l (pymatgen's periodic-table data)."""
    from pymatgen.core import Element

    shells = [[n, l_, occ] for n, l_, occ in Element(element).full_electronic_structure]
    left = oxidation_state
    for shell in sorted(shells, key=lambda s: (-s[0], -"spdf".index(s[1]))):
        take = min(left, shell[2])
        shell[2] -= take
        left -= take
    d_shells = [(n, occ) for n, l_, occ in shells if l_ == "d" and occ]
    return {"element": element, "oxidation_state": oxidation_state,
            "d_count_outer": max(d_shells)[1] if d_shells else 0,
            "configuration": ".".join(f"{n}{l_}{occ}" for n, l_, occ in shells if occ)}


def _check(chk: dict, cod: dict, mp: dict, mp_ids: dict) -> dict:
    """One evidence test. result: PASS | FAIL | NO_ACCESSIBLE_EVIDENCE."""
    kind = chk["kind"]
    if kind == "not_checkable":
        return {"kind": kind, "result": "NO_ACCESSIBLE_EVIDENCE", "reason": chk["reason"]}
    if kind in ("cod_type_present", "cod_type_absent"):
        ents = cod[chk["formula"]]["entries"]
        sel = [e for e in ents if e["prototype"] == chk["type"]]
        if chk.get("ambient"):
            sel = [e for e in sel if e["ambient_pressure"]]
        if chk.get("mineral"):
            sel = [e for e in sel if (e.get("mineral") or "").lower() == chk["mineral"].lower()]
        if chk.get("name_regex"):
            rx = re.compile(chk["name_regex"], re.I)
            sel = [e for e in sel if rx.search(f"{e.get('chemname') or ''} {e.get('title') or ''}")]
        ev = [{"cod_id": e["cod_id"], "sg": e["sg_symbol_computed"], "mineral": e.get("mineral"),
               "chemname": e.get("chemname"), "authors": e.get("authors"), "year": e.get("year"),
               "journal": e.get("journal"), "doi": e.get("doi"), "pressure_kPa": e.get("pressure_kPa")}
              for e in sel]
        ok = bool(sel) if kind == "cod_type_present" else not sel
        return {"kind": kind, "params": _params(chk), "result": "PASS" if ok else "FAIL",
                "n_matching_entries": len(sel), "evidence": ev}
    if kind == "mp_lowest_ehull":
        docs = mp[chk["formula"]]["docs"]
        low = docs[0] if docs else None
        ok = False
        if low:
            if "sg_number" in chk:
                ok = low["sg_number"] == chk["sg_number"]
            if "not_sg_number" in chk:
                ok = low["sg_number"] != chk["not_sg_number"]
        same = [d for d in docs if d["sg_number"] == chk.get("sg_number", chk.get("not_sg_number"))]
        return {"kind": kind, "params": _params(chk), "result": "PASS" if ok else "FAIL",
                "lowest": low, "docs_with_named_sg": same}
    if kind == "mp_id_sg":
        d = mp_ids[chk["legacy_id"]]
        ok = d["sg_number"] == chk["sg_number"]
        if chk.get("robocrys_mineral"):
            ok = ok and (d["robocrys_mineral_type"] or "") == chk["robocrys_mineral"]
        for s in chk.get("description_contains", []):
            ok = ok and s in (d["robocrys_description"] or "")
        return {"kind": kind, "params": _params(chk), "result": "PASS" if ok else "FAIL", "record": d}
    if kind == "formal_d_count":
        r = formal_d_count(chk["element"], chk["oxidation_state"])
        return {"kind": kind, "params": _params(chk), "record": r,
                "result": "PASS" if r["d_count_outer"] == chk["expected"] else "FAIL"}
    raise ValueError(kind)


def subclaim_verdict(checks: list[dict]) -> tuple[str, str]:
    """Registered binary (docs/43 :1945): CLEARED only when every check passes."""
    if not checks:
        return EXCLUDED, "no evidence test defined"
    gaps = [k for k in checks if k["result"] == "NO_ACCESSIBLE_EVIDENCE"]
    if gaps:
        return EXCLUDED, "; ".join(k["reason"] for k in gaps)
    fails = [k for k in checks if k["result"] == "FAIL"]
    if fails:
        return EXCLUDED, "; ".join(
            f"{k['kind']} {json.dumps(k.get('params'), ensure_ascii=False, sort_keys=True)} failed"
            + (f" ({k['n_matching_entries']} matching records)" if "n_matching_entries" in k else "")
            for k in fails)
    return CLEARED, "every evidence test passed"


def evaluate_claims(claims: list[dict], cod: dict, mp: dict, mp_ids: dict) -> list[dict]:
    out = []
    for c in claims:
        loc = locate(c["fragment"], REPO / c["file"], c["line"])
        subs = []
        for s in c["subclaims"]:
            checks = [_check(k, cod, mp, mp_ids) for k in s["checks"]]
            if loc["found"]:
                verdict, reason = subclaim_verdict(checks)
            else:
                verdict, reason = EXCLUDED, "fragment not found in the file (the text changed)"
            row = {"id": s["id"], "text": s["text"], "verdict": verdict, "reason": reason,
                   "checks": checks,
                   "supporting_context": [_check(k, cod, mp, mp_ids) for k in s.get("supporting_context", [])]}
            if "narrowed" in s:
                n_checks = [_check(k, cod, mp, mp_ids) for k in s["narrowed"]["checks"]]
                n_verdict, n_reason = subclaim_verdict(n_checks) if loc["found"] else (EXCLUDED, reason)
                row["narrowed"] = {"text": s["narrowed"]["text"], "verdict": n_verdict, "reason": n_reason,
                                   "checks": n_checks}
            subs.append(row)
        out.append({"id": c["id"], "formula": c["formula"], "file": c["file"], "line": c["line"],
                    "located": loc, "fragment": c["fragment"], "assertion": c["assertion"],
                    "subclaims": subs,
                    "n_subclaims_cleared": sum(1 for s in subs if s["verdict"] == CLEARED),
                    "n_subclaims_excluded": sum(1 for s in subs if s["verdict"] == EXCLUDED),
                    "context_checks": [_check(k, cod, mp, mp_ids) for k in c.get("context_checks", [])],
                    "polymorphism_note": c.get("polymorphism_note", "")})
    return out


def scan_mentions(paths: list[Path], vocab_regex, formula_regex) -> list[dict]:
    hits = []
    for p in paths:
        for i, t in enumerate(read_lines(p), 1):
            if formula_regex.search(t) and vocab_regex.search(t):
                hits.append({"file": rel(p), "line": i, "text": t[:400]})
    return hits


def load_claims(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
