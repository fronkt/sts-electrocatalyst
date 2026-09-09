"""Emit the docs/95 readout (CENSUS-2 model ensemble, CENSUS-3 seeds 3-29, rank resolution) from files.

Every number in the emitted document is read from a file at run time: the census readout files
(readout/{per_site.csv, per_site.json, reproduction.json, ranking.json, distribution.json}), the
landed result files with their logs and manifests, MANIFESTS.sha256, o2_fragment/o2_records.json,
r4_gated.json, the rank_resolution*.json files, and the pre-stated documents (docs/91, the
rank-resolution spec, docs/93, docs/94) for lines quoted or checked by line number. Nothing is
typed in; prose carries the file:key or file:line anchor beside each value. status.json, STOP,
lock-file contents and torch-cache/ are never opened (directory names only). The sealed modules
are not imported; sha256_lf is re-implemented here (CRLF -> LF before hashing).

The document is a CALIBRATION readout: every [CENSUS-n ...] and [RANK-n ...] slot is reproduced
blank, no bar is widened, no docs/43 prediction is scored and no banked number moves; readings not
pre-stated in docs/91 section 2 or spec sections 3-4 are marked post-hoc where they appear.

Run from the repository root (defaults are resolved against the repository root regardless):

    python src/scripts/site_census_report.py --out docs/95-census-2-3-readout-<date>.md
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]

TAGS = ("mpa0", "omat0", "mp0", "matpes")
ENSEMBLE = ("omat0", "mp0", "matpes")
RULES = ("banked", "intact_only", "adsorbate_intact_only", "two_pathway")
RR_RULES = ("min", "median", "p10", "mean")
POLICIES = ("all", "no-desorbed", "intact", "adsorbate-intact", "two-pathway")
CATS = ("NORMAL", "DESORPTION", "DISSOCIATION", "MIGRATION", "RECONSTRUCTION")
STATES = ("OH", "O", "OOH")
CKPTS = ("mpa0", "mpa0_ext", "omat0", "mp0", "matpes", "endmember")
CKPT_LABEL = {"mpa0": "mpa0 (CENSUS-1)", "mpa0_ext": "mpa0_ext (CENSUS-3)", "omat0": "omat0", "mp0": "mp0",
              "matpes": "matpes", "endmember": "endmember_2x2__mpa0"}
ENDMEMBER = "endmember_2x2__mpa0"
_EXT = re.compile(r"^mpa0_ext__(?P<formula>[A-Za-z0-9]+)__s(?P<lo>\d{2})-(?P<hi>\d{2})$")
_STD = re.compile(r"^(?P<tag>mpa0|omat0|mp0|matpes)__(?P<formula>[A-Za-z0-9]+)$")
LAUNCH_RE = re.compile(r"=== (\S+) launch:")
EXIT_RE = re.compile(r"=== (\S+) exit (\d+)")
HEX64 = r"[0-9a-f]{64}"


# ----------------------------------------------------------------------------- helpers
def sha256_lf(path):
    """sha256 of the file bytes with CRLF normalised to LF (the repository's sha256_lf)."""
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def check(cond, msg):
    """Fail closed with one line on an inconsistent input; unlike assert it survives python -O."""
    if not cond:
        raise SystemExit("site_census_report: " + msg)


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def slot(C, k):
    """The blank docs/91 entrant slot [CENSUS-k 2026-09-__: ...] as the docs/91 line carries it."""
    return f"`{C.SLOT[k][0]}`"


def r(x):
    """A value copied from a file, printed as repr(float)."""
    return repr(float(x))


def rv(x):
    """A file value that may be null."""
    return "null" if x is None else r(x)


def has_eta(row):
    return row["eta_V"].strip() != ""


def re_(row):
    """The eta_V cell of a per_site.csv row, or "no eta" when the cell is empty."""
    return r(row["eta_V"]) if has_eta(row) else "no eta"


def e(x):
    """A difference, printed as %.3e."""
    return "%.3e" % x


def h2(x):
    return "%.2f" % x


def bl(x):
    return str(bool(x)).lower()


def iso_to_dt(s):
    d = dt.datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def zfmt(d):
    return d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_stem(stem):
    """Stem grammar of site_census_plan.py:73-91, re-implemented (no import of the sealed module)."""
    if stem == ENDMEMBER:
        return dict(arm="ENDMEMBER-2x2", tag="mpa0", formula=None, block=None)
    m = _EXT.match(stem)
    if m:
        return dict(arm="CENSUS-3", tag="mpa0", formula=m["formula"], block=(int(m["lo"]), int(m["hi"])))
    m = _STD.match(stem)
    if m:
        return dict(arm="CENSUS-1" if m["tag"] == "mpa0" else "CENSUS-2", tag=m["tag"], formula=m["formula"], block=None)
    raise ValueError("manifest name outside the census layout: " + stem)


def ckpt_of(stem):
    info = parse_stem(stem)
    if info["arm"] == "ENDMEMBER-2x2":
        return "endmember"
    if info["arm"] == "CENSUS-3":
        return "mpa0_ext"
    return info["tag"]


def kendall_tau_a(order, ref):
    """Kendall tau-a of a census order against the reference order (no ties)."""
    pos = {f: i for i, f in enumerate(ref)}
    n = len(order)
    conc = disc = 0
    for i in range(n):
        for j in range(i + 1, n):
            if pos[order[i]] < pos[order[j]]:
                conc += 1
            else:
                disc += 1
    return (conc - disc) / (n * (n - 1) / 2)


def cat5(rows, key):
    c = Counter(x[key] for x in rows)
    return "/".join(str(c.get(k, 0)) for k in CATS)


def cells(line):
    """Cells of a markdown table row."""
    return [c.strip() for c in line.strip().strip("|").split("|")]


class Doc:
    """A pre-stated document read for quoting by line number; anchors make a moved line fail loudly."""

    def __init__(self, path, name):
        self.path, self.name = path, name
        with open(path, encoding="utf-8") as fh:
            self.lines = fh.read().split("\n")

    def line(self, n, anchor=None):
        t = self.lines[n - 1]
        if anchor is not None:
            check(anchor in t, f"{self.name}:{n} does not contain {anchor!r}: the line moved")
        return t.strip()

    def hexes(self, n, anchor=None):
        return re.findall(HEX64, self.line(n, anchor))


# ----------------------------------------------------------------------------- inputs
class Ctx:
    pass


def build(args):
    C = Ctx()
    C.args = args
    C.census = Path(args.census_dir)
    C.readout = Path(args.readout_dir)
    C.rr_dir = Path(args.rr_dir)
    C.rr_names = OrderedDict()
    for item in args.rr_names.split(","):
        k, v = item.split("=", 1)
        C.rr_names[k.strip()] = v.strip()

    C.D91 = Doc(args.docs91, "docs/91")
    C.SPEC = Doc(args.spec, "spec")
    C.D93 = Doc(args.docs93, "docs/93")
    C.D94 = Doc(args.docs94, "docs/94")
    C.DESC = Doc(ROOT / "src" / "hea_oer" / "descriptors.py", "descriptors.py")
    C.P = planning(C)
    l14 = C.D91.line(14, "CENSUS BOUNDARY")
    m = re.search(r"commit ([0-9a-f]{7}) \([0-9a-f]{40}\), (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)", l14)
    check(m, "docs/91:14 carries no `commit <7> (<40>), <stamp>Z` boundary")
    C.BOUND = (m.group(1), m.group(2))
    m = re.search(r"commit ([0-9a-f]{7}) \([0-9a-f]{40}\), dated (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)", C.SPEC.line(5, "BLIND BOUNDARY"))
    check(m is not None and (m.group(1), m.group(2)) == C.BOUND, "spec:5 blind boundary differs from docs/91:14")
    C.N_MANIFESTS = int(re.search(r"the (\d+) manifests", l14).group(1))
    C.N_C1_SITES = int(re.search(r"the fraction of the (\d+) CENSUS-1 sites", C.D91.line(61, "Reported: per state")).group(1))
    C.N_FULL = int(re.search(r"(\d+) sites when complete", C.D91.line(69, "E[min_k]")).group(1))
    C.SLOT = {}
    for i, t in enumerate(C.D91.lines, start=1):
        for m in re.finditer(r"\[CENSUS-(\d) 2026-09-__: [^\]]*\]", t):
            C.SLOT.setdefault(int(m.group(1)), (m.group(0), i))
    check(sorted(C.SLOT) == list(range(1, 10)), f"docs/91 does not carry the nine blank CENSUS slots: {sorted(C.SLOT)}")
    l266 = C.D93.line(266, "MACE-OMAT-0")
    m = re.search(r"\((\d\.\d\d)x the CENSUS-1 mean", l266)
    check(m, "docs/93:266 carries no `(<x.xx>x the CENSUS-1 mean` figure")
    C.D93_OMAT_RATIO = m.group(1)
    m = re.search(r"the first figure reported before the other five — was (not met|met)", l266)
    check(m, "docs/93:266 carries no ordering verdict")
    C.D93_ORDER = m.group(1)

    C.R = load(C.readout / "reproduction.json")
    C.K = load(C.readout / "ranking.json")
    C.D = load(C.readout / "distribution.json")
    C.PSJ_hash = sha256_lf(C.readout / "per_site.json")
    with open(C.readout / "per_site.csv", newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        C.PS = list(rd)
        C.PS_COLS = list(rd.fieldnames)
    gens = {C.R["generated"], C.K["generated"], C.D["generated"], load(C.readout / "per_site.json")["generated"]}
    check(len(gens) == 1, f"readout files carry different `generated` stamps: {gens}")
    C.GEN = C.K["generated"]
    C.PARTIAL = bool(C.K["partial"])
    C.MISSING = C.K["missing"]
    C.MREAD = C.K["manifests_read"]
    C.STEMS = list(C.MREAD.keys())
    C.TH = C.R["thresholds"]
    C.kr = C.K["ranking"]
    C.ORDER = list(C.kr["banked_order"])
    C.GATED = C.ORDER
    C.BOX12 = list(C.kr["ensemble_spread"].keys())
    C.OTHER6 = [f for f in C.BOX12 if f not in C.GATED]
    check(len(C.GATED) == 6 and len(C.BOX12) == 12, 'input check failed: len(C.GATED) == 6 and len(C.BOX12) == 12')

    gated = load(args.gated)
    C.GROWS = {row["formula"]: row for row in gated["rows"]}
    check(C.ORDER == [row["formula"] for row in sorted(gated["rows"], key=lambda x: x["eta"])], "banked_order differs from r4_gated rows sorted by eta")

    # result files: only the small header fields are kept
    C.RES = OrderedDict()
    for stem in C.STEMS:
        p = C.census / "results" / f"{stem}_result.json"
        check(sha256_lf(p) == C.MREAD[stem]["result_sha256_lf"], f"result hash of {stem} differs from manifests_read")
        d = load(p)
        C.RES[stem] = dict(
            hash=C.MREAD[stem]["result_sha256_lf"], manifest_id=d["manifest_id"], status=d["status"],
            model=d["manifest"]["model"], impl=d["manifest"]["implementation_sha256_lf"],
            threads=d["environment"]["threads"],
            seconds=[x["seconds"] for x in d["results"]], n_sites=d["results"][0]["row"]["n_sites"],
            candidates=[(x["formula"], x["status"]) for x in d["results"]],
        )
        del d
    impls = {json.dumps(v["impl"], sort_keys=True) for v in C.RES.values()}
    check(len(impls) == 1, "implementation_sha256_lf differs across landed results")
    C.IMPL = next(iter(C.RES.values()))["impl"]
    check(len(C.IMPL) == 10, 'input check failed: len(C.IMPL) == 10')
    C.MAN = OrderedDict()
    for stem in C.STEMS:
        m = load(C.census / "manifests" / f"{stem}.json")
        C.MAN[stem] = dict(model=m["model"], work_estimate=m["work_estimate"], manifest_id=m["manifest_id"])
        check(m["manifest_id"] == C.RES[stem]["manifest_id"], f"manifest_id of {stem} differs between manifest and result")
        check(m["model"] == C.RES[stem]["model"], 'input check failed: m["model"] == C.RES[stem]["model"]')
    # model bytes hashes per tag against docs/91:34 and :38
    C.MODEL_PIN = {"mpa0": C.D91.hexes(34, "CENSUS-1")[0]}
    l38 = C.D91.line(38, "CENSUS-2")
    for tag in ENSEMBLE:
        m = re.search(r"`" + tag + r"__`[^`]*?sha256 (" + HEX64 + ")", l38)
        check(m, f"docs/91:38 carries no sha256 for {tag}")
        C.MODEL_PIN[tag] = m.group(1)
    check(len(set(C.MODEL_PIN.values())) == 4, 'input check failed: len(set(C.MODEL_PIN.values())) == 4')
    C.MODEL_FILE = {}
    for stem in C.STEMS:
        tag = parse_stem(stem)["tag"]
        check(C.MAN[stem]["model"]["sha256_bytes"] == C.MODEL_PIN[tag], f"{stem}: model bytes hash differs from docs/91")
        C.MODEL_FILE.setdefault(tag, C.MAN[stem]["model"]["filename"])

    # logs of the landed stems, and of the other gated stems of a landed tag (launch stamps only)
    C.LOG = {}
    C.RESULT_NAMES = sorted(os.listdir(C.census / "results"))
    C.LOG_NAMES = sorted(os.listdir(C.census / "logs"))
    C.LOCKS = [n[:-len("_result.json.lock")] for n in C.RESULT_NAMES if n.endswith("_result.json.lock")]
    for stem in C.STEMS:
        C.LOG[stem] = log_times(C.census / "logs" / f"{stem}.log")
    for tag in ENSEMBLE:
        if any(parse_stem(s)["tag"] == tag for s in C.STEMS):
            for f in C.GATED:
                stem = f"{tag}__{f}"
                if stem not in C.LOG and f"{stem}.log" in C.LOG_NAMES:
                    C.LOG[stem] = log_times(C.census / "logs" / f"{stem}.log")

    C.MANIFESTS_HASH = sha256_lf(C.census / "MANIFESTS.sha256")
    with open(C.census / "MANIFESTS.sha256", encoding="utf-8") as fh:
        C.MANIFEST_STEMS = [re.search(r"manifests/(\S+)\.json", ln).group(1) for ln in fh if ln.strip()]
    check(len(C.MANIFEST_STEMS) == C.N_MANIFESTS, f"MANIFESTS.sha256 lists {len(C.MANIFEST_STEMS)} stems, docs/91:14 says {C.N_MANIFESTS}")
    # arm sizes: counted from the MANIFESTS.sha256 stems, checked against docs/91:67 and the twelve-composition box
    C.PLANNED = OrderedDict((ck, sum(1 for s in C.MANIFEST_STEMS if ckpt_of(s) == ck)) for ck in CKPTS)
    check(sum(C.PLANNED.values()) == len(C.MANIFEST_STEMS), "a manifest stem falls outside the six checkpoint groups")
    check(C.PLANNED["mpa0"] == len(C.BOX12) and all(C.PLANNED[t] == len(C.BOX12) for t in ENSEMBLE), "per-checkpoint manifest count differs from the twelve-composition box of ranking.json")
    check(sum(C.PLANNED[t] for t in ENSEMBLE) == C.P["c2_manifests"] and C.PLANNED["mpa0_ext"] == C.P["c3_equiv"], "CENSUS-2 / CENSUS-3 arm sizes of MANIFESTS.sha256 differ from docs/91:67")
    per_f = {f: sum(1 for s in C.MANIFEST_STEMS if parse_stem(s)["tag"] == "mpa0" and parse_stem(s)["formula"] == f) for f in C.GATED}
    check(len(set(per_f.values())) == 1, f"mpa0 manifests per gated composition differ: {per_f}")
    C.MAN_PER_F = next(iter(per_f.values()))
    # result files on disk that the readout did not read (no lock): names, status and seconds only
    C.ONDISK = []
    for n in C.RESULT_NAMES:
        if not n.endswith("_result.json"):
            continue
        stem = n[:-len("_result.json")]
        if stem in C.MREAD or stem in C.LOCKS:
            continue
        try:
            d = load(C.census / "results" / n)
            C.ONDISK.append((stem, d["status"], [x["seconds"] for x in d["results"]]))
            del d
        except (ValueError, KeyError, TypeError, OSError):
            C.ONDISK.append((stem, "unreadable at emit time", None))
    pin92 = re.search(r"sha256_lf (" + HEX64 + ")", C.D91.line(92, "MANIFESTS.sha256")).group(1)
    check(C.MANIFESTS_HASH == pin92, "MANIFESTS.sha256 differs from the docs/91:92 pin")
    C.O2_PATH = C.census / "o2_fragment" / "o2_records.json"
    C.O2_HASH = sha256_lf(C.O2_PATH) if C.O2_PATH.is_file() else None
    if C.kr["o2_records_supplied"]:
        check(C.O2_HASH is not None, "ranking.json says o2 records were supplied but o2_fragment/o2_records.json is absent")
        pin94 = re.match(r"(" + HEX64 + r")  o2_fragment/o2_records\.json", C.D94.line(131, "o2_records.json")).group(1)
        check(C.O2_HASH == pin94, "o2_records.json differs from docs/94:131")

    # docs/93 pins: the twelve mpa0__ and the endmember result hashes
    pins93 = {}
    for n in range(228, 241):
        m = re.match(r"(" + HEX64 + r")  results/(\S+)_result\.json", C.D93.line(n))
        check(m, f"docs/93:{n} is not a result hash line")
        pins93[m.group(2)] = m.group(1)
    for stem, hsh in pins93.items():
        check(C.RES[stem]["hash"] == hsh, f"{stem}: hash differs from docs/93:228-240")
    C.PINS93 = pins93
    C.D93_STAMP = re.search(r"dated \*\*([0-9T:+\-]+)\*\*", C.D93.line(11, "readout files dated")).group(1)
    C.D93_C1_MEAN = float(re.search(r"mean (\d+\.\d) s", C.D93.line(166, "Totals")).group(1))

    # rank-resolution files
    C.RR = OrderedDict()
    C.RR_HASH = OrderedDict()
    for pol in list(POLICIES) + ["compare"]:
        name = C.rr_names.get(pol)
        p = C.rr_dir / name if name else None
        if p is not None and p.is_file():
            C.RR[pol] = load(p)
            C.RR_HASH[pol] = sha256_lf(p)
        else:
            C.RR[pol] = None
            C.RR_HASH[pol] = None

    # per-site views
    # a row with an empty eta_V stays in every integrity count and is left out of the eta arithmetic (named in (b))
    ev = [x for x in C.PS if x["candidate_status"] == "evaluated"]
    C.NOETA = [x for x in ev if not has_eta(x)]
    C.HEA = [x for x in ev if x["arm"] in ("CENSUS-1", "CENSUS-2")]
    C.MPA120 = [x for x in ev if x["arm"] in ("CENSUS-1", "CENSUS-3") and x["tag"] == "mpa0"]
    C.LANDED_TAGS = [t for t in TAGS if any(x["tag"] == t for x in C.HEA)]
    C.WIN = {}
    for tag in C.LANDED_TAGS:
        for f in C.BOX12:
            rows = [x for x in C.HEA if x["tag"] == tag and x["formula"] == f and has_eta(x)]
            if rows:
                C.WIN[(tag, f)] = min(rows, key=lambda x: float(x["eta_V"]))
    for (tag, f), wv in C.WIN.items():
        es = C.kr["ensemble_spread"][f]["min_site_eta_by_model_V"]
        check(tag in es and float(wv["eta_V"]) == es[tag], f"per_site min of {tag}/{f} differs from ranking.ensemble_spread")

    # arm counts
    C.COUNT = Counter()
    for stem in C.STEMS:
        info = parse_stem(stem)
        C.COUNT[(info["arm"], info["tag"])] += 1
    C.C2 = {t: C.COUNT[("CENSUS-2", t)] for t in ENSEMBLE}
    C.C2G = {t: sum(1 for s in C.STEMS if parse_stem(s)["arm"] == "CENSUS-2" and parse_stem(s)["tag"] == t and parse_stem(s)["formula"] in C.GATED) for t in ENSEMBLE}
    C.C3 = C.COUNT[("CENSUS-3", "mpa0")]
    C.C1 = C.COUNT[("CENSUS-1", "mpa0")]
    C.REASONS = Counter(m["reason"] for m in C.MISSING)
    return C


def log_times(path):
    launch = exit_ = code = None
    if not Path(path).is_file():
        return launch, exit_, code
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = LAUNCH_RE.match(line)
            if m:
                launch = m.group(1)
            m = EXIT_RE.match(line)
            if m:
                exit_, code = m.group(1), int(m.group(2))
    return launch, exit_, code


# ----------------------------------------------------------------------------- planning figures (docs/91:67)
def planning(C):
    t = C.D91.line(67, "511.016")
    P = {}
    m = re.search(r"(\d+\.\d+) s \(equiatomic\) and (\d+\.\d+) s \(leader\)", t)
    P["one_site"] = (float(m.group(1)), float(m.group(2)))
    m = re.search(r"gives (\d+\.\d+)-(\d+\.\d+) s per composition \((\d+\.\d+)-(\d+\.\d+) h\)", t)
    P["per12"] = (float(m.group(1)), float(m.group(2)))
    m = re.search(r"CENSUS-1: (\d+\.\d+)-(\d+\.\d+) s serial \((\d+\.\d+)-(\d+\.\d+) h\); with four concurrent 2-thread processes on 8 cores, (\d+\.\d+)-(\d+\.\d+) h wall", t)
    P["c1_serial_s"] = (float(m.group(1)), float(m.group(2)))
    P["c1_wall_h"] = (float(m.group(5)), float(m.group(6)))
    m = re.search(r"CENSUS-2 \(36 manifests, other checkpoints, MPA-0 figure used\): (\d+\.\d+)-(\d+\.\d+) h serial, (\d+\.\d+)-(\d+\.\d+) h wall", t)
    P["c2_serial_h"] = (float(m.group(1)), float(m.group(2)))
    P["c2_wall_h"] = (float(m.group(3)), float(m.group(4)))
    m = re.search(r"CENSUS-3 \(648 sites = 54 CENSUS-1-manifest equivalents\): (\d+\.\d+)-(\d+\.\d+) h serial, (\d+\.\d+)-(\d+\.\d+) h wall", t)
    P["c3_serial_h"] = (float(m.group(1)), float(m.group(2)))
    P["c3_wall_h"] = (float(m.group(3)), float(m.group(4)))
    m = re.search(r"`seconds` sum (\d+\.\d+) s", t)
    P["endmember_s"] = float(m.group(1))
    m = re.search(r"candidate `seconds` (\d+\.\d+) \(mpa0\), (\d+\.\d+) \(omat0\), (\d+\.\d+) \(mp0\), (\d+\.\d+) \(matpes\)", t)
    P["smoke"] = OrderedDict(zip(TAGS, (float(m.group(i)) for i in range(1, 5))))
    P["c2_manifests"] = int(re.search(r"CENSUS-2 \((\d+) manifests", t).group(1))
    P["c3_equiv"] = int(re.search(r"= (\d+) CENSUS-1-manifest equivalents", t).group(1))
    return P


# ----------------------------------------------------------------------------- section 1: banner
def banner(C):
    L = []
    w = L.append
    word = "PARTIAL" if C.PARTIAL else "complete"
    title_date = C.args.title_date or C.GEN[:10]
    w(f"# READOUT — CENSUS-2 (model ensemble) and CENSUS-3 (seeds 3-29) of the site-integrity census (docs/91) with the rank-resolution readout (docs/research/2026-09-06-rank-resolution-spec.md): the {word} readout of {C.GEN} ({title_date})")
    w("")
    w("> **CALIBRATION READOUT OF AN UNREGISTERED PROTOCOL. NOT A REGISTERED ARM.** docs/91 is not a docs/43 amendment and")
    w("> nothing in it is registered (`docs/91:3`); this readout is descriptive, labelled CALIBRATION under `docs/43:3447-3455`,")
    w("> and **scores no docs/43 prediction, registers no THRESHOLD, widens no pre-stated bar, fills no entrant slot, moves")
    w("> `results/r4_melt_list.json` nowhere and validates, ranks or certifies no electrode** (`docs/91:63`, `:90`). Every value")
    w("> docs/91 marks **Proposed** is reported below as Proposed beside its blank slot in the docs/92 form")
    w("> `[CENSUS-<n> 2026-09-__: ____]`, and every elective rank-resolution setting beside its blank `[RANK-<n> ...: ______]` slot; no slot is filled here.")
    w(f"> Blind boundary: commit `{C.BOUND[0]}`, {C.BOUND[1]} (`docs/91:14`; the rank-resolution readout carries the same pair, spec:5, asserted).")
    reasons = ", ".join(f"{n} `{k}`" for k, n in sorted(C.REASONS.items()))
    w(f"> Readout stamp: `generated` **{C.GEN}** (`readout/ranking.json`; the same stamp on `reproduction.json`, `distribution.json`, `per_site.json`), `partial: {bl(C.PARTIAL)}`:")
    w(f"> **{len(C.MREAD)} manifests read, {len(C.MISSING)} listed missing** ({reasons}; `ranking.json` `missing[].reason`);")
    o2s = f"with `o2_fragment/o2_records.json` sha256_lf `{C.O2_HASH}` (equal to `docs/94:131`, asserted)" if C.kr["o2_records_supplied"] else "(the CENSUS-1b records were not an input of this readout)"
    w(f"> `o2_records_supplied: {bl(C.kr['o2_records_supplied'])}` {o2s}; `scores_docs43_prediction: {bl(C.kr['scores_docs43_prediction'])}`.")
    per = ", ".join(f"{t} {C.C2[t]}/{C.PLANNED[t]}" for t in ENSEMBLE)
    locks = ", ".join(f"`{s}`" for s in C.LOCKS) or "none"
    PL = C.PLANNED
    w(f"> Landed by arm (stems of `manifests_read` under the stem grammar of `site_census_plan.py:73-91`; arm sizes are the stem counts of `MANIFESTS.sha256`, equal to `docs/91:67`, asserted): CENSUS-1 {C.C1}/{PL['mpa0']} (`mpa0__`), ENDMEMBER-2x2 {C.COUNT[('ENDMEMBER-2x2', 'mpa0')]}/{PL['endmember']},")
    w(f"> **CENSUS-2: {sum(C.C2.values())}/{sum(PL[t] for t in ENSEMBLE)} landed ({per})**, **CENSUS-3: {C.C3}/{PL['mpa0_ext']}** (`mpa0_ext__`); live `.lock` files in `results/` at emit time (names only, `docs/91:73`): {locks}.")
    od = []
    for stem, st, secs in C.ONDISK:
        od.append(f"`{stem}` `status: {st}`" + (f", `results[].seconds` {', '.join(f'{s:.3f}' for s in secs)}" if secs else ""))
    w(f"> \"Landed\" throughout this file means present in `manifests_read` at the readout stamp; the `results/` and `logs/` listings are read at emit time. Result files on disk at emit time that are neither in `manifests_read` nor beside a `.lock` (name, `status` and `results[].seconds` read from the file; they enter no count, sum or table of this file): {'; '.join(od) if od else 'none'}.")
    for t in ENSEMBLE:
        w(f"> {arm_pending(C, t)}")
    w(f"> {c3_pending(C)}")
    w(f"> docs/93 is the CENSUS-1 readout of record (its `readout/` stamp {C.D93_STAMP}, `docs/93:11`) and docs/94 the CENSUS-1b readout; this file re-reads the same twelve `mpa0__` results and the endmember (hashes equal `docs/93:228-240`, asserted) only for the per-model comparisons and the {C.N_FULL}-site set, and re-derives no (a)/(d) verdict of docs/93; where a docs/93 verdict is restated below it is cited to docs/93 and asserted equal.")
    w("> Where a reading below is not pre-stated in `docs/91:52-69` or spec:41-92 it is marked **post-hoc** and changes no verdict.")
    # rank-resolution status line
    parts = []
    bvals = []
    for pol in POLICIES:
        d = C.RR[pol]
        if d is None:
            parts.append(f"`--admit {pol}`: not run (no `{C.rr_names.get(pol, pol)}`)")
            continue
        s = d["settings"]
        cov = d["coverage"]
        defi = ", ".join(f"{x['formula']} ({x['n_decorations_usable']})" for x in d.get("deficient_compositions", [])) or "none"
        parts.append(f"`--admit {s['admit']}`: `status {d['status']}`, `B` {s['B']}, `seed` {s['seed']}, coverage expected {len(cov['expected'])} / present {len(cov['present'])} / missing {len(cov['missing'])}, deficient {defi}")
        bvals.append(str(s["B"]))
    w("> Rank resolution: " + "; ".join(parts) + ".")
    m = re.search(r"--B (\d+) --seed (\d+)", C.SPEC.line(45, "--B 10000"))
    w(f"> spec:45 fixes the command of record at `--B {m.group(1)} --seed {m.group(2)}`; these files carry `B` = {', '.join(bvals) if bvals else 'none'}; a file with `B` below {m.group(1)} is a dry run of the same code and not the readout of record.")
    w("")
    return L


def arm_pending(C, tag):
    n, g = C.C2[tag], C.C2G[tag]
    p = C.PLANNED[tag]
    if n == p:
        return f"{tag}: landed in full ({p}/{p})."
    if n == 0:
        return f"pending: {tag} not landed (0/{p})."
    not_landed = [f"`{tag}__{f}`" for f in C.BOX12 if f"{tag}__{f}" not in C.STEMS]
    return f"pending: {tag} {g}/{len(C.GATED)} gated ({n}/{p} overall); not landed: {', '.join(not_landed)}."


def c3_pending(C):
    p = C.PLANNED["mpa0_ext"]
    if C.C3 == p:
        return f"CENSUS-3: landed in full ({p}/{p})."
    if C.C3 == 0:
        return f"pending: CENSUS-3 not landed (0/{p}) — readout (f) holds the 12-site CENSUS-1 slice only."
    return f"pending: CENSUS-3 {C.C3}/{p} landed — readout (f) holds the CENSUS-1 slice plus the landed seed blocks."


# ----------------------------------------------------------------------------- section 2: verdict block
def verdict(C):
    L = []
    w = L.append
    w("## Verdict against what was pre-stated (`docs/91:52-69`; spec:41-92)")
    w("")
    # (b)
    parts = []
    for tag in ENSEMBLE:
        rows = [x for x in C.HEA if x["tag"] == tag and x["formula"] in C.GATED]
        if not rows:
            parts.append(f"{tag}: pending, no manifest landed")
            continue
        c = Counter(x["OOH_category"] for x in rows)
        n = len(rows)
        n_ht = sum(x["OOH_h_location"] == "H_TRANSFERRED" for x in rows)
        parts.append(f"{'O' if not parts else 'o'}ver the {n} {tag} sites of the gated six the OOH endpoint reads DESORPTION {c.get('DESORPTION', 0)}, NORMAL {c.get('NORMAL', 0)}, DISSOCIATION {c.get('DISSOCIATION', 0)}, MIGRATION {c.get('MIGRATION', 0)}, RECONSTRUCTION {c.get('RECONSTRUCTION', 0)}; OOH H_TRANSFERRED on {n_ht}/{n} = {n_ht / n:.4f}; INTACT {sum(x['all_states_intact'] == 'True' for x in rows)} sites, ADSORBATE-INTACT {sum(x['all_states_adsorbate_intact'] == 'True' for x in rows)}; unconverged sites {sum(int(x['unconverged_states']) > 0 for x in rows)}")
    m120 = [x for x in C.MPA120 if x["formula"] in C.GATED]
    c120 = Counter(x["OOH_category"] for x in m120)
    w("- **(b) INTEGRITY, per model** (`readout/per_site.csv`, rows `arm == CENSUS-2`, `tag == <tag>`, gated six; per-model fractions post-hoc). " + "; ".join(parts) + f". MPA-0 {C.N_FULL}-site set (`arm in (CENSUS-1, CENSUS-3)`, `tag mpa0`, gated six): {len(m120)} sites landed of {C.N_FULL * len(C.GATED)}; OOH DESORPTION {c120.get('DESORPTION', 0)}, NORMAL {c120.get('NORMAL', 0)}, DISSOCIATION {c120.get('DISSOCIATION', 0)}, MIGRATION {c120.get('MIGRATION', 0)}, RECONSTRUCTION {c120.get('RECONSTRUCTION', 0)}; INTACT {sum(x['all_states_intact'] == 'True' for x in m120)}, ADSORBATE-INTACT {sum(x['all_states_adsorbate_intact'] == 'True' for x in m120)}.")
    # (c)
    rp = []
    for rule in RULES:
        o = C.kr["orders"][rule]
        if o["complete"]:
            rp.append(f"{rule}: {'banked order' if o['order'] == C.ORDER else 'order differs from banked'}, tau-a {o['kendall_tau_vs_banked']}")
        else:
            rp.append(f"{rule}: EXCLUDED {', '.join(o['excluded'])}, tau not reported (`complete: false`)")
    sp = []
    for f in C.GATED:
        s = C.kr["ensemble_spread"][f]
        sp.append(f"{f} {r(s['spread_V'])} ({s['n_models']})")
    w(f"- **(c) RANKING.** {'; '.join(rp)} (`readout/ranking.json` `orders`). Ensemble spread (max − min of the models' min-site eta, `ranking.ensemble_spread.<f>.spread_V`, `n_models` in parentheses): {', '.join(sp)} for the gated six; the column is complete only at `n_models` 4. The per-model distributions behind these minima are in (c′) below (post-hoc).")
    # (d)
    dparts = []
    ds = C.R["decisive_site"]
    m0 = C.WIN[("mpa0", C.GATED[0])]
    check((m0["seed"], m0["site_index"]) == (str(ds["winner_seed"]), str(ds["winner_site_index"])), "per_site.csv min row of the leader under mpa0 differs from decisive_site")
    dparts.append(f"Under mpa0 the leader's winner is seed {ds['winner_seed']} / site {ds['winner_site_index']} / {ds['winner_site_metal']}, eta {r(ds['winner_eta_V'])} V, OOH {ds['ooh_readout']}, O-O {r(m0['OOH_o_o_A'])} A = {m0['OOH_o_o_class']}, hydrogen {m0['OOH_h_location']}, pathway {ds['winner_pathway']}, `unconverged_states` {m0['unconverged_states']} (`docs/93:24`, restated from `reproduction.json` `decisive_site` and the same site's `per_site.csv` row)")
    for tag in ENSEMBLE:
        wv = C.WIN.get((tag, C.GATED[0]))
        if wv is None:
            dparts.append(f"{tag} pending")
        else:
            dparts.append(f"under {tag} it is seed {wv['seed']} / site {wv['site_index']} / {wv['initial_metal']}, eta {r(wv['eta_V'])} V, OOH {wv['OOH_category']}, {'same' if (wv['seed'], wv['site_index']) == (str(ds['winner_seed']), str(ds['winner_site_index'])) else 'NOT the same'} (seed, site) as the mpa0 winner")
    w("- **(d) DECISIVE SITE per model (post-hoc extension of `docs/91:65`).** " + "; ".join(dparts) + " (section (d) below).")
    # (e)
    E = cost_numbers(C)
    cparts = []
    for ck in ("omat0", "mp0", "matpes"):
        g = E["groups"][ck]
        if g["n"] == 0:
            cparts.append(f"{ck} pending")
        else:
            cparts.append(f"{ck} {g['mean']:.1f} s ({g['mean'] / E['c1_mean']:.2f}x the CENSUS-1 mean)")
    cparts.append("CENSUS-3 pending" if E["groups"]["mpa0_ext"]["n"] == 0 else f"mpa0_ext {E['groups']['mpa0_ext']['mean']:.1f} s ({E['groups']['mpa0_ext']['mean'] / E['c1_mean']:.2f}x)")
    w(f"- **(e) COST.** {len(C.STEMS)} landed manifests: candidate seconds sum {E['total']:.3f} s = {E['total'] / 3600:.2f} h; per checkpoint mean: mpa0 (CENSUS-1) {E['c1_mean']:.1f} s, " + ", ".join(cparts) + f"; log-stamp wall, first launch → last exit line {zfmt(E['first'])} → {zfmt(E['last'])} = {E['wall'] / 3600:.2f} h and {E['total'] / E['wall']:.2f} candidate-seconds per wall-second (post-hoc arithmetic on `results/<stem>_result.json` `results[].seconds` and `logs/<stem>.log` stamps, in place of the pre-stated `status.json` runner wall, which this file does not open; section (e)).")
    # (f)
    pf = C.D["distribution"]["per_formula"]
    ns = {f: pf[f]["n_sites"] for f in C.GATED if f in pf}
    if all(n == C.N_FULL for n in ns.values()):
        sds = ", ".join(f"{f} {r(pf[f]['all_sites']['std'])}" for f in C.GATED)
        w(f"- **(f) DISTRIBUTION.** {C.N_FULL} sites per gated composition; sample sd (V): {sds}; the descriptive placement against the `docs/91:44` spreads is in section (f).")
    else:
        nn = ", ".join(f"{f} {n}" for f, n in ns.items())
        w(f"- **(f) DISTRIBUTION.** n sites per gated composition ({nn} of {C.N_FULL}, `distribution.json` `per_formula.<f>.n_sites`); E[min_k] for k <= n only; CENSUS-3 {'pending' if C.C3 == 0 else f'{C.C3}/{C.PLANNED['mpa0_ext']} landed'}.")
    # rank resolution
    w("- **Rank resolution.** " + rr_verdict_sentence(C))
    w("")
    return L


def rr_verdict_sentence(C):
    d = C.RR["all"]
    if d is None:
        return "`--admit all`: not run."
    parts = []
    st = d["status"]
    if d.get("resolved_boundaries"):
        rb = d["resolved_boundaries"]
        ib = d["inverted_boundaries"]
        parts.append(f"`--admit all`: status `{st}`, resolved boundaries min/median/p10/mean = {rb['min']}/{rb['median']}/{rb['p10']}/{rb['mean']} of {d['n_boundaries']} (`resolved_boundaries`); inverted = {ib['min']}/{ib['median']}/{ib['p10']}/{ib['mean']} (`inverted_boundaries`)")
    else:
        parts.append(f"`--admit all`: status `{st}`, no boundary verdict (`{d.get('message')}`)")
    sec = []
    for pol in POLICIES[1:]:
        x = C.RR[pol]
        if x is None:
            sec.append(f"{pol}: not run")
        else:
            defi = ", ".join(f"{y['formula']} ({y['n_decorations_usable']})" for y in x.get("deficient_compositions", [])) or "none"
            sec.append(f"{pol}: `{x['status']}`, deficient {defi}")
    parts.append("secondary policies: " + "; ".join(sec))
    cmp_ = C.RR["compare"]
    if cmp_ is None:
        parts.append("`--compare`: not run")
    else:
        parts.append(f"`--compare`: {cmp_['n_policy_dependent']} of {len(cmp_['boundaries'])} POLICY-DEPENDENT")
        if any(v == "ABSENT" for b in cmp_["boundaries"] for v in b["verdicts"].values()):
            parts.append("an `ABSENT` verdict marks a policy file that ended `insufficient_decorations`, so under partial data every boundary reads POLICY-DEPENDENT by construction and no R6 statement is made (T8 caveat, post-hoc reading of a pre-stated label)")
    return "; ".join(parts) + "."


# ----------------------------------------------------------------------------- section 3: (b) integrity per model
def section_b(C):
    L = []
    w = L.append
    TH = C.TH
    w("## (b) INTEGRITY per model — counts per category, per state, per composition (`readout/per_site.csv`; thresholds `reproduction.json thresholds`)")
    w("")
    w(f"Thresholds as applied (`readout/reproduction.json` `thresholds`): bound < {TH['bound_max_A']} A, desorbed >= {TH['desorbed_min_A']} A (INHERITED, `docs/33:317-322`, `src/hea_oer/data.py:20`); O-O bands O2_LIKE <= {TH['o2_like_max_A']}, SUPEROXO_LIKE <= {TH['superoxo_like_max_A']}, OOH_LIKE <= {TH['ooh_like_max_A']} A, OO_CLEAVED above — Proposed {slot(C, 2)}; hydrogen window {TH['h_bond_max_A']} A — Proposed {slot(C, 3)}; reconstruction per-atom {TH['reconstruction_max_A']} A — Proposed {slot(C, 4)}; label priority DESORPTION > DISSOCIATION > MIGRATION > RECONSTRUCTION > NORMAL — Proposed {slot(C, 5)} (`docs/91:55-58`, as `docs/93:73`).")
    w("")
    w(f"What is reported, `docs/91:61` verbatim: \"{C.D91.line(61, 'Reported: per state')}\"")
    w("")
    cols = C.PS_COLS
    state_cols = [c for c in cols if re.match(r"^(OH|O|OOH)_", c)]
    site_cols = [c for c in cols if c not in state_cols]
    check(not any("fixed" in c.lower() for c in cols), "per_site.csv carries a fixed-atom column this sentence does not name")
    w(f"The per-state level of `docs/91:61` is delegated to `readout/per_site.csv` (one row per site; the same rows as `per_site.json` `rows[]`): the per-state columns are {', '.join(f'`{c}`' for c in state_cols)} — `<S>_m_o_A` is the tiering distance of the nearest adsorbate oxygen to its metal, `OOH_slab_rms_A` the RMS displacement over the free slab atoms and `OOH_slab_max_A` the largest single free-atom displacement of `docs/91:58`; the site-level columns are {', '.join(f'`{c}`' for c in site_cols)}. The second O-metal distance of `docs/91:55` and the fixed-atom displacement of `docs/91:58` are not columns of the readout files (no column of `per_site.csv` names either) and are not reprinted here.")
    w("")
    noeta = "; ".join(f"`{x['manifest']}` seed {x['seed']} site {x['site_index']}" for x in C.NOETA) or "none"
    w(f"Rows with `candidate_status == evaluated` and an empty `eta_V` (kept in every integrity count, left out of every minimum and eta arithmetic, printed as \"no eta\"): {noeta}.")
    w("")
    w("**Table B1 — totals per model over the gated six** (rows `arm in (CENSUS-1, CENSUS-2)`, `tag == <model>`, `formula` in the gated six, `candidate_status == evaluated`; categories from `<S>_category`, tiers from `<S>_tier`):")
    w("")
    w("| model | n sites | state | NORMAL | DESORPTION | DISSOCIATION | MIGRATION | RECONSTRUCTION | tier bound / weak / desorbed |")
    w("|---|---|---|---|---|---|---|---|---|")
    for tag in TAGS:
        rows = [x for x in C.HEA if x["tag"] == tag and x["formula"] in C.GATED]
        if not rows:
            w(f"| {tag} | pending: {tag} not landed (0 of 6 gated manifests) | | | | | | | |")
            continue
        for st in STATES:
            c = Counter(x[f"{st}_category"] for x in rows)
            t = Counter(x[f"{st}_tier"] for x in rows)
            w(f"| {tag} | {len(rows)} | *{st} | {c.get('NORMAL', 0)} | {c.get('DESORPTION', 0)} | {c.get('DISSOCIATION', 0)} | {c.get('MIGRATION', 0)} | {c.get('RECONSTRUCTION', 0)} | {t.get('bound', 0)} / {t.get('weak', 0)} / {t.get('desorbed', 0)} |")
    w("")
    w("Per model over every landed site of that model (arms CENSUS-1 and CENSUS-2, all landed compositions; the mpa0 fraction over 144 is the `docs/91:61` statement, every other fraction is post-hoc):")
    w("")
    for tag in TAGS:
        rows = [x for x in C.HEA if x["tag"] == tag]
        if not rows:
            w(f"- {tag}: pending, no manifest landed.")
            continue
        n = len(rows)
        n_ht = sum(x["OOH_h_location"] == "H_TRANSFERRED" for x in rows)
        oo = Counter(x["OOH_o_o_class"] for x in rows)
        pw = Counter(x["pathway"] for x in rows)
        hl = Counter(x["OOH_h_location"] for x in rows)
        if tag == "mpa0":
            check(n == C.N_C1_SITES, f"mpa0 CENSUS-1 sites {n} differ from the {C.N_C1_SITES} of docs/91:61")
            frac = f"**{n_ht} of {n} sites = {n_ht / n:.4f}** (`docs/93:22`)"
        else:
            frac = f"{n_ht} of {n} sites = {n_ht / n:.4f} (post-hoc; {n} sites landed)"
        w(f"- **{tag}** ({n} sites, {sorted({x['manifest'] for x in rows}).__len__()} manifests): OOH hydrogen H_TRANSFERRED on {frac}; ON_ADSORBATE {hl.get('ON_ADSORBATE', 0)}, H_FREE {hl.get('H_FREE', 0)}. OOH O-O band: O2_LIKE {oo.get('O2_LIKE', 0)}, SUPEROXO_LIKE {oo.get('SUPEROXO_LIKE', 0)}, OOH_LIKE {oo.get('OOH_LIKE', 0)}, OO_CLEAVED {oo.get('OO_CLEAVED', 0)}. Pathway: cus {pw.get('cus', 0)}, bridge {pw.get('bridge', 0)}, undefined {pw.get('undefined', 0)}. Sites INTACT **{sum(x['all_states_intact'] == 'True' for x in rows)}**, ADSORBATE-INTACT **{sum(x['all_states_adsorbate_intact'] == 'True' for x in rows)}**; unconverged states {sum(int(x['unconverged_states']) for x in rows)} on {sum(int(x['unconverged_states']) > 0 for x in rows)} sites (`unconverged_states`); weak-tier states {sum(int(x['weak_states']) for x in rows)} on {sum(int(x['weak_states']) > 0 for x in rows)} sites (`weak_states`); reconstruction flags {sum(int(x['reconstructed_states']) for x in rows)} states on {sum(int(x['reconstructed_states']) > 0 for x in rows)} sites (`reconstructed_states`). OH hydrogen ON_ADSORBATE on {sum(x['OH_h_location'] == 'ON_ADSORBATE' for x in rows)} of {n} (`OH_h_location`).")
    w("")
    w("**Table B2 — per composition x model, gated six** (columns as `docs/93:88`; the winner is the min-`eta_V` site of `per_site.csv` for that (tag, formula) and its flags are `all_states_intact` / `all_states_adsorbate_intact` — for the mpa0 rows that is the banked winner of `docs/91:61`, for every other model it is the census min-site row, post-hoc; site counts cross-checked against `ranking.json` `convergence.per_formula.<f>.<tag>`, asserted):")
    w("")
    L += b2_table(C, C.GATED, TAGS)
    w("")
    # docs/93 Table B2 rows: 90-95 the gated six, 96-101 the other six (checked by first cell)
    check([cells(C.D93.line(n))[0] for n in range(90, 96)] == C.GATED, "docs/93:90-95 are not the gated six in banked order")
    check([cells(C.D93.line(n))[0] for n in range(96, 102)] == C.OTHER6, "docs/93:96-101 are not the other six")
    other_tags = [t for t in C.LANDED_TAGS if t != "mpa0" and any(x["tag"] == t and x["formula"] in C.OTHER6 for x in C.HEA)]
    if other_tags:
        w("**Table B2 (other six compositions)** — the tags that have landed them (CENSUS-2 covers twelve, `docs/91:38`); the mpa0 rows are `docs/93:96-101` and are not reprinted:")
        w("")
        L += b2_table(C, C.OTHER6, other_tags)
        w("")
    else:
        w(f"For the other six compositions ({', '.join(C.OTHER6)}) only mpa0 has landed (`docs/93:96-101`); every other tag is pending: " + ", ".join(f"`{t}__<f>` not landed" for t in ENSEMBLE if not any(x["tag"] == t and x["formula"] in C.OTHER6 for x in C.HEA)) + ".")
        w("")
    # B3
    w("**Table B3 — the MPA-0 120-site set (CENSUS-1 + CENSUS-3), gated six** (rows `tag == mpa0`, `arm in (CENSUS-1, CENSUS-3)`; manifests landed = distinct `manifest` values, asserted equal to `distribution.json` `per_formula.<f>.manifests`):")
    w("")
    w(f"| composition | manifests landed (of {C.MAN_PER_F}) | n sites (of {C.N_FULL}) | OOH N/D/X/M/R | O N/D/X/M/R | OH N/D/X/M/R | H_TRANSF (n, fraction) | INTACT | ADS-INTACT | cus/bridge/undef | unconv states / sites | weak states | recon states |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    any_c3 = False
    for f in C.GATED:
        rows = [x for x in C.MPA120 if x["formula"] == f]
        mans = sorted({x["manifest"] for x in rows})
        check(set(mans) == set(C.D["distribution"]["per_formula"][f]["manifests"]), f"manifest set of {f} differs from distribution.json")
        any_c3 = any_c3 or any(x["arm"] == "CENSUS-3" for x in rows)
        w("| " + " | ".join([f, str(len(mans)), str(len(rows))] + b_counts(rows)) + " |")
    w("")
    if any_c3:
        w("Post-hoc sub-table per seed block (`manifest` = `mpa0_ext__<f>__sNN-NN`), same counts:")
        w("")
        w("| composition | manifest | n sites | OOH N/D/X/M/R | O N/D/X/M/R | OH N/D/X/M/R | H_TRANSF (n, fraction) | INTACT | ADS-INTACT | cus/bridge/undef | unconv states / sites | weak states | recon states |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for f in C.GATED:
            for man in sorted({x["manifest"] for x in C.MPA120 if x["formula"] == f and x["arm"] == "CENSUS-3"}):
                rows = [x for x in C.MPA120 if x["manifest"] == man]
                w("| " + " | ".join([f, f"`{man}`", str(len(rows))] + b_counts(rows)) + " |")
        w("")
    else:
        w("pending: CENSUS-3 not landed; the table holds the 12 CENSUS-1 sites of `docs/93:90-95`.")
        w("")
    # banked winner status per model
    w(f"**Banked winner status per model** (`docs/91:61` last clause; banked `seed` / `site_metal` from `r4_gated.json` `rows[].bonds`). For mpa0 the winner row is `reproduction.json` `reproduction.<f>.winner` with `winner_site_intact` / `winner_site_adsorbate_intact` (docs/93 readout (a)); for the other models `reproduction.json` carries no entry (`site_census_readout.py:139` restricts (a) to CENSUS-1, and `docs/91:80`: \"{re.search(r'The three other checkpoints carry no historical claim at all', C.D91.line(80, 'Weight identity')).group(0)}\"), so their row is the census min-site row of that model beside whether its (seed, site_index) equals the mpa0 winner's — post-hoc:")
    w("")
    w("| composition | banked seed / metal | model | site(s) with that seed and `initial_metal` == banked metal: seed/site_index, eta_V, INTACT, ADS-INTACT | winner or min-site row: seed/site_index/metal, eta_V, INTACT / ADS-INTACT | same (seed, site) as mpa0 winner |")
    w("|---|---|---|---|---|---|")
    for f in C.GATED:
        g = C.GROWS[f]["bonds"]
        rep = C.R["reproduction"][f]
        mw = rep["winner"]
        for tag in TAGS:
            rows = [x for x in C.HEA if x["tag"] == tag and x["formula"] == f]
            if not rows:
                w(f"| {f} | {g['seed']} / {g['site_metal']} | {tag} | pending: `{tag}__{f}` not landed | | |")
                continue
            hits = [x for x in rows if x["seed"] == str(g["seed"]) and x["initial_metal"] == g["site_metal"]]
            hs = "; ".join(f"{x['seed']}/{x['site_index']}, {re_(x)}, {x['all_states_intact']}, {x['all_states_adsorbate_intact']}" for x in sorted(hits, key=lambda x: int(x["site_index"]))) or "none"
            if tag == "mpa0":
                ws = f"{mw['seed']}/{mw['site_index']}/{mw['site_metal']}, {r(rep['eta_min_V'])}, {'INTACT' if rep['winner_site_intact'] else 'no'} / {'yes' if rep['winner_site_adsorbate_intact'] else 'no'} (`reproduction.json`, {rep['verdict']})"
                same = "— (reference)"
            else:
                wv = C.WIN[(tag, f)]
                ws = f"{wv['seed']}/{wv['site_index']}/{wv['initial_metal']}, {r(wv['eta_V'])}, {'INTACT' if wv['all_states_intact'] == 'True' else 'no'} / {'yes' if wv['all_states_adsorbate_intact'] == 'True' else 'no'} (census min-site row, post-hoc)"
                same = "yes" if (wv["seed"], wv["site_index"]) == (str(mw["seed"]), str(mw["site_index"])) else "no"
            w(f"| {f} | {g['seed']} / {g['site_metal']} | {tag} | {hs} | {ws} | {same} |")
    w("")
    return L


def b_counts(rows):
    pc = Counter(x["pathway"] for x in rows)
    n = len(rows)
    n_ht = sum(x["OOH_h_location"] == "H_TRANSFERRED" for x in rows)
    return [cat5(rows, "OOH_category"), cat5(rows, "O_category"), cat5(rows, "OH_category"),
            f"{n_ht}, {n_ht / n:.4f}" if n else "—",
            str(sum(x["all_states_intact"] == "True" for x in rows)), str(sum(x["all_states_adsorbate_intact"] == "True" for x in rows)),
            f"{pc.get('cus', 0)}/{pc.get('bridge', 0)}/{pc.get('undefined', 0)}",
            f"{sum(int(x['unconverged_states']) for x in rows)} / {sum(int(x['unconverged_states']) > 0 for x in rows)}",
            str(sum(int(x["weak_states"]) for x in rows)), str(sum(int(x["reconstructed_states"]) for x in rows))]


def b2_table(C, formulas, tags):
    L = []
    w = L.append
    w("| composition | model | OOH N/D/X/M/R | O N/D/X/M/R | OH N/D/X/M/R | H_TRANSF | INTACT | ADS-INTACT | cus/bridge/undef | unconv states / sites | weak states | recon states | winner (seed/site/metal, eta V) | winner OOH (category, o_o_class, h_location) | winner INTACT / ADS-INTACT |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for f in formulas:
        for tag in tags:
            rows = [x for x in C.HEA if x["tag"] == tag and x["formula"] == f]
            if not rows:
                w(f"| {f} | {tag} | pending: `{tag}__{f}` not landed | | | | | | | | | | | | |")
                continue
            pc = Counter(x["pathway"] for x in rows)
            conv = C.kr["convergence"]["per_formula"][f][tag]
            n_unc_sites = sum(int(x["unconverged_states"]) > 0 for x in rows)
            n_int = sum(x["all_states_intact"] == "True" for x in rows)
            n_ads = sum(x["all_states_adsorbate_intact"] == "True" for x in rows)
            check(n_unc_sites == conv["n_unconverged_sites"] and n_int == conv["n_intact_sites"] and n_ads == conv["n_adsorbate_intact_sites"], f"{tag}/{f}: site counts differ from ranking.convergence")
            check(pc.get("bridge", 0) == conv["n_bridge_sites"] and pc.get("undefined", 0) == conv["n_undefined_pathway_sites"], f"{tag}/{f}: pathway counts differ from ranking.convergence")
            wv = C.WIN[(tag, f)]
            w(f"| {f} | {tag} | {cat5(rows, 'OOH_category')} | {cat5(rows, 'O_category')} | {cat5(rows, 'OH_category')} | {sum(x['OOH_h_location'] == 'H_TRANSFERRED' for x in rows)} | {n_int} | {n_ads} | {pc.get('cus', 0)}/{pc.get('bridge', 0)}/{pc.get('undefined', 0)} | {sum(int(x['unconverged_states']) for x in rows)} / {n_unc_sites} | {sum(int(x['weak_states']) for x in rows)} | {sum(int(x['reconstructed_states']) for x in rows)} | {wv['seed']}/{wv['site_index']}/{wv['initial_metal']}, {r(wv['eta_V'])} | {wv['OOH_category']} ({wv['OOH_o_o_class']}, {wv['OOH_h_location']}) | {'INTACT' if wv['all_states_intact'] == 'True' else 'no'} / {'yes' if wv['all_states_adsorbate_intact'] == 'True' else 'no'} |")
    return L


# ----------------------------------------------------------------------------- section 4: (c) ranking
def section_c(C):
    L = []
    w = L.append
    kr = C.kr
    w("## (c) DESCRIPTOR-DEFINED RANKING of the gated six under the four rules (`readout/ranking.json`)")
    w("")
    gaps = " / ".join(r(g["gap_V"]) for g in kr["banked_adjacent_gaps"])
    o2 = ("the CENSUS-1b diagnostic is supplied (`o2_records_supplied: true`); `per_formula.<f>.o2_fragment_diagnostics.<seed/site>` blocks carry `dG_ads_O2_eV`, `dG_O2_reference_cancelled_eV`, `hb_deprotonation_step_eV`, `o2_release_eV`, `zpe_ts_O2_eV`, `role`; the values equal `docs/94:82-86` (asserted) and change no value (`docs/91:63`)"
          if kr["o2_records_supplied"] else "the CENSUS-1b fragment diagnostic is not supplied (`o2_records_supplied: false`), so every `o2_fragment_diagnostics` block is empty")
    if kr["o2_records_supplied"]:
        check_o2_against_docs94(C)
    w(f"Site set: {kr['site_set']} (`ranking.site_set`). Banked order and gaps as pre-stated at `docs/91:63`: `banked_adjacent_gaps` {gaps} V. The pathway-undefined exclusion of the two-pathway rule is Proposed {slot(C, 6)}; {o2}.")
    w("")
    if kr["o2_records_supplied"]:
        # docs/91:63: the fragment diagnostic is printed beside the bridge sites
        br = []
        for f in C.GATED:
            blocks = kr["per_formula"][f]["o2_fragment_diagnostics"]
            bridge = sorted([x for x in C.HEA if x["tag"] == "mpa0" and x["formula"] == f and x["pathway"] == "bridge"], key=lambda x: (int(x["seed"]), int(x["site_index"])))
            keys = [f"{x['seed']}/{x['site_index']}" for x in bridge]
            check(sorted(keys) == sorted(blocks.keys()), f"{f}: o2_fragment_diagnostics keys {sorted(blocks.keys())} differ from the bridge sites {keys}")
            if not bridge:
                br.append(f"{f}: no bridge site")
                continue
            br.append(f"{f}: " + "; ".join(f"seed {x['seed']} site {x['site_index']} ({x['initial_metal']}, eta {re_(x)} V, OOH {x['OOH_category']}) `dG_ads_O2_eV` {r(blocks[k]['dG_ads_O2_eV'])}, `role` \"{blocks[k]['role']}\"" for x, k in zip(bridge, keys)))
        w("CENSUS-1b fragment diagnostic beside the bridge sites (`docs/91:63`; rows `tag == mpa0`, `pathway == bridge` of `per_site.csv` against `ranking.per_formula.<f>.o2_fragment_diagnostics.<seed/site>`, key sets asserted equal): " + " | ".join(br) + ".")
        w("")
    w("**Table C1 — per rule** (`ranking.orders.<rule>`; tau printed only when `complete`, `docs/91:63`: \"tau is reported only when all six have a value\"):")
    w("")
    w("| rule | order (ascending, V) | Kendall tau-a vs banked | adjacent gaps (V) | EXCLUDED (`n_intact_sites` / `n_adsorbate_intact_sites` / `n_pathway_defined_sites` of 12) |")
    w("|---|---|---|---|---|")
    d93 = {}
    for n in range(113, 117):
        cc = cells(C.D93.line(n))
        d93[cc[0]] = cc
    for rule in RULES:
        o = kr["orders"][rule]
        order_s = " < ".join(f"{f} {r(o['values_V'][f])}" for f in o["order"])
        gp = " / ".join(r(g["gap_V"]) for g in o["adjacent_gaps"])
        tau = str(o["kendall_tau_vs_banked"]) if o["complete"] else "not reported (`complete: false`)"
        exc = ", ".join(f"{f} ({kr['per_formula'][f]['n_intact_sites']} / {kr['per_formula'][f]['n_adsorbate_intact_sites']} / {kr['per_formula'][f]['n_pathway_defined_sites']})" for f in o["excluded"]) or "none"
        w(f"| {rule} | {order_s} | {tau} | {gp} | {exc} |")
        ref = d93[rule]
        check(ref[1] == order_s and ref[2] == tau, f"rule {rule}: order or tau differs from docs/93:113-116")
    w("")
    w("The four orders and tau values are unchanged from `docs/93:113-116` (asserted cell by cell; the rule site set is CENSUS-1 only and cannot change).")
    w("")
    w("**Table C2 — per composition, gated six** (`ranking.per_formula`, `ranking.ensemble_spread.<f>.{spread_V, n_models, min_site_eta_by_model_V}`; a spread cell at `n_models` < 4 names the pending tags):")
    w("")
    w("| composition | banked (V) | intact_only | adsorbate_intact_only | two_pathway | n_intact_sites | n_adsorbate_intact_sites | n_pathway_defined_sites | n_bridge_sites | n_undefined_pathway_sites | n_unconverged_sites | n_weak_sites | n_reconstructed_sites | ensemble spread (V) [n_models] | min-site eta by model (V) |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for f in C.GATED:
        w("| " + " | ".join(c2_row(C, f)) + " |")
    w("")
    others = [f for f in C.OTHER6 if kr["ensemble_spread"][f]["n_models"] > 1]
    if others:
        w("The same table for the other six compositions that carry a CENSUS-2 manifest (the `per_formula` rule values exist only for the gated six):")
        w("")
        w("| composition | ensemble spread (V) [n_models] | min-site eta by model (V) |")
        w("|---|---|---|")
        for f in C.OTHER6:
            s = kr["ensemble_spread"][f]
            w(f"| {f} | {spread_cell(s)} | {by_model_cell(s)} |")
        w("")
    else:
        w(f"For the other six compositions every `ensemble_spread` block reads `n_models` 1 and `spread_V` {r(kr['ensemble_spread'][C.OTHER6[0]]['spread_V'])} (mpa0 only); no CENSUS-2 manifest of them has landed.")
        w("")
    # C3
    w("**Table C3 — unconverged sites per composition and per model** (`docs/91:63`: \"the unconverged-site counts per composition and per model\"; risk 7 `docs/91:85`; `ranking.convergence.per_formula.<f>.<tag>.{n_unconverged_sites, n_sites}`, totals `convergence.per_model`):")
    w("")
    w("| composition | mpa0 n_unconverged / n_sites | omat0 | mp0 | matpes |")
    w("|---|---|---|---|---|")
    pfc = kr["convergence"]["per_formula"]
    for f in C.BOX12:
        cc = []
        for tag in TAGS:
            x = pfc.get(f, {}).get(tag)
            cc.append(f"{x['n_unconverged_sites']} / {x['n_sites']}" if x else "pending")
        w(f"| {f} | " + " | ".join(cc) + " |")
    pm = kr["convergence"]["per_model"]
    w("| **total** | " + " | ".join(f"{pm[t]['n_unconverged_sites']} / {pm[t]['n_sites']}" if t in pm else "pending" for t in TAGS) + " |")
    w("")
    unc = []
    for (tag, f), wv in sorted(C.WIN.items(), key=lambda kv: (TAGS.index(kv[0][0]), C.BOX12.index(kv[0][1]))):
        if int(wv["unconverged_states"]) > 0:
            unc.append(f"{tag} {f} (seed {wv['seed']} site {wv['site_index']}, `unconverged_states` {wv['unconverged_states']})")
    clause = re.search(r"a composition whose banked minimum sits on an unconverged site is reported with that fact beside the number", C.D91.line(85, "BFGS cap")).group(0)
    w(f"Whether a model's min-site eta sits on an unconverged site (winner row `unconverged_states > 0` in `per_site.csv`, every landed (tag, formula); the mpa0 entries are the pre-stated reading, the other models' are post-hoc): {('; '.join(unc)) if unc else 'none — no min-site row of any landed model carries an unconverged state'}. `docs/91:85`: \"{clause}\".")
    w("")
    # C4
    w("**Table C4 — post-hoc, per-model winner persistence** (min-`eta_V` row of `per_site.csv` per (tag, formula), gated six x landed tags; the last column compares (`seed`, `site_index`) with the mpa0 winner's):")
    w("")
    w("| composition | model | min-site eta (V) | winning seed / site_index | initial metal | OOH binding metal | OOH category | O-O class | H location | pathway | site INTACT / ADS-INTACT | same (seed, site) as mpa0 winner? |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    keep = Counter()
    for f in C.GATED:
        m0 = C.WIN[("mpa0", f)]
        for tag in C.LANDED_TAGS:
            wv = C.WIN.get((tag, f))
            if wv is None:
                w(f"| {f} | {tag} | pending: `{tag}__{f}` not landed | | | | | | | | | |")
                continue
            same = (wv["seed"], wv["site_index"]) == (m0["seed"], m0["site_index"])
            if tag != "mpa0" and same:
                keep[tag] += 1
            w(f"| {f} | {tag} | {r(wv['eta_V'])} | {wv['seed']} / {wv['site_index']} | {wv['initial_metal']} | {wv['OOH_binding_metal']} | {wv['OOH_category']} | {wv['OOH_o_o_class']} | {wv['OOH_h_location']} | {wv['pathway']} | {'INTACT' if wv['all_states_intact'] == 'True' else 'no'} / {'yes' if wv['all_states_adsorbate_intact'] == 'True' else 'no'} | {'—' if tag == 'mpa0' else ('yes' if same else 'no')} |")
    w("")
    sent = []
    for tag in [t for t in C.LANDED_TAGS if t != "mpa0"]:
        n_land = sum(1 for f in C.GATED if (tag, f) in C.WIN)
        sent.append(f"{tag} keeps the mpa0 winning site in {keep[tag]} of its {n_land} landed gated compositions")
    orders = []
    for tag in C.LANDED_TAGS:
        vals = {f: kr["ensemble_spread"][f]["min_site_eta_by_model_V"].get(tag) for f in C.GATED}
        if all(v is not None for v in vals.values()):
            order = sorted(C.GATED, key=lambda f: vals[f])
            tau = kendall_tau_a(order, C.ORDER)
            orders.append(f"{tag}: " + " < ".join(f"{f} {r(vals[f])}" for f in order) + f", tau-a {tau!r} against `banked_order` (computed here)")
        else:
            n_have = sum(v is not None for v in vals.values())
            orders.append(f"{tag}: pending ({n_have} of 6)")
    w("Post-hoc: " + ("; ".join(sent) + ". " if sent else "") + "Per-model orders of `min_site_eta_by_model_V` with Kendall tau-a against `banked_order`, computed by this script only when all six are present for that model (the pre-stated tau of `docs/91:63` is per rule, not per model): " + "; ".join(orders) + ".")
    w("")
    return L


def spread_cell(s):
    missing = [t for t in TAGS if t not in s["min_site_eta_by_model_V"]]
    if s["n_models"] < 4:
        return f"{r(s['spread_V'])} [n_models {s['n_models']}; pending: {', '.join(missing)}]"
    return f"{r(s['spread_V'])} [n_models {s['n_models']}]"


def by_model_cell(s):
    return ", ".join(f"{t} {r(s['min_site_eta_by_model_V'][t])}" if t in s["min_site_eta_by_model_V"] else f"{t} pending" for t in TAGS)


def c2_row(C, f):
    p = C.kr["per_formula"][f]
    s = C.kr["ensemble_spread"][f]
    io = "EXCLUDED" if p["intact_only"] is None else r(p["intact_only"])
    ai = "EXCLUDED" if p["adsorbate_intact_only"] is None else r(p["adsorbate_intact_only"])
    tp = "EXCLUDED" if p["two_pathway"] is None else r(p["two_pathway"])
    return [f, r(p["banked"]), io, ai, tp, str(p["n_intact_sites"]), str(p["n_adsorbate_intact_sites"]), str(p["n_pathway_defined_sites"]),
            str(p["n_bridge_sites"]), str(p["n_undefined_pathway_sites"]), str(p["n_unconverged_sites"]), str(p["n_weak_sites"]),
            str(p["n_reconstructed_sites"]), spread_cell(s), by_model_cell(s)]


def check_o2_against_docs94(C):
    seen = 0
    for n in range(82, 87):
        cc = cells(C.D94.line(n))
        f, key = cc[0], cc[1]
        blk = C.kr["per_formula"][f]["o2_fragment_diagnostics"][key]
        vals = [float(x.replace("−", "-")) for x in cc[2:6]]
        for got, want in zip((blk["dG_ads_O2_eV"], blk["dG_O2_reference_cancelled_eV"], blk["hb_deprotonation_step_eV"], blk["o2_release_eV"]), vals):
            check(abs(got - want) <= 1e-12, f"o2 diagnostic of {f} {key} differs from docs/94:{n}")
        seen += 1
    total = sum(len(C.kr["per_formula"][f]["o2_fragment_diagnostics"]) for f in C.GATED)
    check(seen == total, "o2_fragment_diagnostics block count differs from docs/94:82-86")


# ----------------------------------------------------------------------------- section 4b: (c') post-hoc per-model distributions
CP_ADDED = ("This subsection was added to the emitter on 2026-09-08 after the gated six had landed under all four checkpoints "
            "(readout stamp 2026-09-08T11:09:17+00:00); every threshold in it is a reading rule chosen after seeing those rows, "
            "not a pre-stated bar, and nothing in it enters any rule of readout (c) or fills any slot.")
CP_OO_CUT = 1.10   # A; post-hoc reading rule for a collapsed O-O endpoint
CP_ETA_HI = 2.0    # V; post-hoc reading rule for an extreme row
CP_OOH_LO = 2.0    # eV; post-hoc reading rule for an extreme row
CP_SEEDS = ("0", "1", "2")
CP_SITES = ("0", "1", "2", "3")
CP_PLS = ("1", "2", "3", "4")
CP_COLLAPSED_HEAD = "| model | composition | seed | site | initial metal | O-O (A) | M-O of the OOH (A) | OOH tier / category / H location | dG_OOH (eV) | eta (V) | pls | unconverged_states | OOH_slab_max_A |"
CP_COLLAPSED_SEP = "|---|---|---|---|---|---|---|---|---|---|---|---|---|"
CP_EXTREME_HEAD = "| model | composition | seed | site | initial metal | eta (V) | dG_OH | dG_O | dG_OOH | pls | OH tier | O tier / category | OOH tier / category / O-O (A) / O-O class / H location | OOH_slab_max_A | unconverged_states |"
CP_EXTREME_SEP = "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"


def f4(x):
    """A statistic computed here from file values, printed at four decimals."""
    return "%.4f" % x


def cp_where(row):
    return f"{row['tag']} {row['formula']} seed {row['seed']} site {row['site_index']}"


def fl(row, key):
    """A numeric csv cell as float; fails closed on a non-numeric cell."""
    try:
        return float(row[key])
    except ValueError:
        check(False, f"{cp_where(row)}: `{key}` is not numeric: {row[key]!r}")


def il(row, key):
    """An integer csv cell; fails closed on a non-integer cell."""
    try:
        return int(row[key])
    except ValueError:
        check(False, f"{cp_where(row)}: `{key}` is not an integer: {row[key]!r}")


def rcell(row, key):
    """A numeric csv cell printed as repr(float), or "no value" when the cell is empty."""
    return r(fl(row, key)) if row[key].strip() != "" else "no value"


def cp_box(C, box):
    """The composition box of a (c′)/(c′′) site set: the gated six unless a box is named; a tuple in its order."""
    return tuple(C.GATED if box is None else box)


def cp_rows(C, box=None):
    """Rows per model on a composition box (default the gated six): arm CENSUS-1 for mpa0, CENSUS-2 otherwise; seeds 0-2 x site_index 0-3; box order, then seed, site."""
    box = cp_box(C, box)
    if not hasattr(C, "_CP"):
        C._CP = {}
    if box in C._CP:
        return C._CP[box]
    out = OrderedDict()
    for tag in TAGS:
        arm = "CENSUS-1" if tag == "mpa0" else "CENSUS-2"
        rows = [x for x in C.HEA if x["tag"] == tag and x["arm"] == arm and x["formula"] in box and x["seed"] in CP_SEEDS and x["site_index"] in CP_SITES]
        rows.sort(key=lambda x: (box.index(x["formula"]), int(x["seed"]), int(x["site_index"])))
        keys = [cp_key(x) for x in rows]
        check(len(set(keys)) == len(keys), f"{tag}: duplicate (formula, seed, site_index) among the {len(box)}-composition rows of per_site.csv")
        out[tag] = rows
    C._CP[box] = out
    return out


def cp_key(x):
    return (x["formula"], x["seed"], x["site_index"])


def cp_full(C, box=None):
    return len(cp_box(C, box)) * len(CP_SEEDS) * len(CP_SITES)


def cp_complete(C, box=None):
    """Models whose row count on the box equals the full count; every other model prints pending."""
    return [t for t, rows in cp_rows(C, box).items() if len(rows) == cp_full(C, box)]


def cp_pending(C, tag, box=None):
    return f"pending ({len(cp_rows(C, box)[tag])} of {cp_full(C, box)})"


def cp_collapsed(C, tag, box=None):
    return [x for x in cp_rows(C, box)[tag] if x["OOH_o_o_A"].strip() != "" and fl(x, "OOH_o_o_A") < CP_OO_CUT]


def cp_collapsed_keys(C, tags, box=None):
    """(formula, seed, site_index) keys of the collapsed-O-O rows of the named models."""
    keys = set()
    for tag in tags:
        keys.update(cp_key(x) for x in cp_collapsed(C, tag, box))
    return keys


def cp_eta_stats(rows, tag, what):
    """The Table C′1 / C′′1 statistics of one model's rows (n; n with eta; mean; sd; median; p10; min; max; unconverged sites; pls counts)."""
    ev = [fl(x, "eta_V") for x in rows if has_eta(x)]
    check(len(ev) >= 2, f"{tag}: fewer than two {what} rows carry an eta")
    pls = Counter(x["pls"] for x in rows)
    check(set(pls) <= set(CP_PLS), f"{tag}: a {what} row carries `pls` outside 1-4: {sorted(set(pls) - set(CP_PLS))}")
    return dict(n=len(rows), n_eta=len(ev), mean=float(np.mean(ev)), sd=sd1(ev), median=float(np.median(ev)), p10=pct(ev, 10), min=min(ev), max=max(ev),
                unc=sum(1 for x in rows if il(x, "unconverged_states") > 0), pls=pls)


def cp_eta_cells(s):
    """The Table C′1 cells after the model name, from cp_eta_stats."""
    return f"{s['n']} ({s['n_eta']}) | {f4(s['mean'])} | {f4(s['sd'])} | {f4(s['median'])} | {f4(s['p10'])} | {f4(s['min'])} | {f4(s['max'])} | {s['unc']} | " + " / ".join(str(s["pls"].get(k, 0)) for k in CP_PLS)


def cp_oo_cells(rows, tag, what, n_coll):
    """The Table C′3 cells after the model name: n with an O-O value, min, p5, median, max, rows below the cut."""
    oo = [fl(x, "OOH_o_o_A") for x in rows if x["OOH_o_o_A"].strip() != ""]
    check(len(oo) >= 2, f"{tag}: fewer than two {what} rows carry an O-O value")
    return f"{len(oo)} | {f4(min(oo))} | {f4(pct(oo, 5))} | {f4(float(np.median(oo)))} | {f4(max(oo))} | {n_coll}"


def cp_collapsed_row(tag, x):
    """One row of the collapsed-O-O table (cells are the csv values)."""
    return f"| {tag} | {x['formula']} | {x['seed']} | {x['site_index']} | {x['initial_metal']} | {rcell(x, 'OOH_o_o_A')} | {rcell(x, 'OOH_m_o_A')} | {x['OOH_tier']} / {x['OOH_category']} / {x['OOH_h_location']} | {r(fl(x, 'dG_OOH'))} | {re_(x)} | {x['pls']} | {x['unconverged_states']} | {rcell(x, 'OOH_slab_max_A')} |"


def cp_extreme_rows(C, done, box=None):
    """Rows of the complete models with eta above CP_ETA_HI or dG_OOH below CP_OOH_LO, eta descending (rows without an eta last)."""
    box = cp_box(C, box)
    R = cp_rows(C, box)
    ext = []
    for tag in done:
        for x in R[tag]:
            if (has_eta(x) and fl(x, "eta_V") > CP_ETA_HI) or fl(x, "dG_OOH") < CP_OOH_LO:
                ext.append((tag, x))
    ext.sort(key=lambda tx: (0 if has_eta(tx[1]) else 1, -(fl(tx[1], "eta_V") if has_eta(tx[1]) else 0.0), TAGS.index(tx[0]), box.index(tx[1]["formula"]), int(tx[1]["seed"]), int(tx[1]["site_index"])))
    return ext


def cp_extreme_row(tag, x):
    """One row of the extreme-row table."""
    return f"| {tag} | {x['formula']} | {x['seed']} | {x['site_index']} | {x['initial_metal']} | {re_(x)} | {r(fl(x, 'dG_OH'))} | {r(fl(x, 'dG_O'))} | {r(fl(x, 'dG_OOH'))} | {x['pls']} | {x['OH_tier']} | {x['O_tier']} / {x['O_category']} | {x['OOH_tier']} / {x['OOH_category']} / {rcell(x, 'OOH_o_o_A')} / {x['OOH_o_o_class']} / {x['OOH_h_location']} | {rcell(x, 'OOH_slab_max_A')} | {x['unconverged_states']} |"


def sd1(v):
    """Sample sd (ddof = 1), or None below two values."""
    return float(np.std(np.asarray(v, dtype=float), ddof=1)) if len(v) >= 2 else None


def pct(v, q):
    """Percentile with linear interpolation (the `distribution.json` `statistics` convention)."""
    return float(np.percentile(np.asarray(v, dtype=float), q))


def avg_ranks(v):
    """Ranks 1..n with ties given their average rank."""
    v = np.asarray(v, dtype=float)
    order = np.argsort(v, kind="stable")
    ranks = np.empty(len(v), dtype=float)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def pearson(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < 2 or float(np.std(a)) == 0.0 or float(np.std(b)) == 0.0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def spearman(a, b):
    return pearson(avg_ranks(a), avg_ranks(b))


def opt3(x):
    return "—" if x is None else "%.3f" % x


def cp_pair_stats(C, a, b, keys_excluded, box=None):
    """Matched (formula, seed, site_index) rows of models a and b, both with eta, keys_excluded left out."""
    ra = {cp_key(x): x for x in cp_rows(C, box)[a] if has_eta(x)}
    rb = {cp_key(x): x for x in cp_rows(C, box)[b] if has_eta(x)}
    keys = [k for k in ra if k in rb and k not in keys_excluded]
    if not keys:
        return None
    ea = [fl(ra[k], "eta_V") for k in keys]
    eb = [fl(rb[k], "eta_V") for k in keys]
    d = np.asarray(eb, dtype=float) - np.asarray(ea, dtype=float)
    same = sum(1 for k in keys if ra[k]["OOH_category"] == rb[k]["OOH_category"])
    return dict(n=len(keys), r=pearson(ea, eb), rho=spearman(ea, eb), mean_shift=float(np.mean(d)), median_shift=float(np.median(d)), same_cat=same / len(keys))


def section_c_prime(C):
    L = []
    w = L.append
    R = cp_rows(C)
    full = cp_full(C)
    done = cp_complete(C)
    pending = [t for t in TAGS if t not in done]
    coll = {t: cp_collapsed(C, t) for t in done}
    coll_keys = cp_collapsed_keys(C, done)
    w("### (c′) post-hoc — the ensemble beyond the minimum: per-model site distributions on the gated six")
    w("")
    w(f"{CP_ADDED} Post-hoc throughout. The readout read here carries `generated` {C.GEN}. Rows: `per_site.csv` `candidate_status == evaluated`, `formula` in the gated six, arm CENSUS-1 for mpa0 and CENSUS-2 for omat0 / mp0 / matpes, seeds {', '.join(CP_SEEDS)} x site_index {'..'.join((CP_SITES[0], CP_SITES[-1]))} — {full} rows per model; a model with fewer rows prints pending and is left out of the pairwise tables. Every statistic below is arithmetic of this script on the named csv columns (`eta_V`, `pls`, `dG_OH`, `dG_O`, `dG_OOH`, `OOH_o_o_A`, `OOH_category`, `initial_metal`, `unconverged_states`); a row with an empty `eta_V` is counted in the n of Table C′1 and left out of every eta arithmetic (the n of Tables C′4 and C′5 count rows with an eta). Nothing here scores, ranks or changes a verdict.")
    w("")
    # ---- table 1
    w("**Table C′1 — site eta per model** (n; mean; sample sd, ddof = 1; median; p10, linear interpolation as `distribution.json` `statistics`; min; max; sites with `unconverged_states` > 0; `pls` counts 1 / 2 / 3 / 4):")
    w("")
    w("| model | n (with eta) | mean (V) | sd (V) | median (V) | p10 (V) | min (V) | max (V) | unconverged sites | pls 1 / 2 / 3 / 4 |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    S1 = {}
    for tag in TAGS:
        if tag not in done:
            w(f"| {tag} | {cp_pending(C, tag)} | | | | | | | | |")
            continue
        S1[tag] = cp_eta_stats(R[tag], tag, "gated-six")
        w(f"| {tag} | {cp_eta_cells(S1[tag])} |")
    w("")
    # ---- table 2
    w(f"**Table C′2 — descriptor means per model** (over the {full} rows: mean `dG_OH`, `dG_O`, `dG_OOH`; over the rows with `OOH_category` NORMAL: n, mean eta, mean `dG_OH`, mean `dG_OOH`, mean and sample sd of `dG_OOH` − `dG_OH`; eV except eta):")
    w("")
    w("| model | mean dG_OH | mean dG_O | mean dG_OOH | NORMAL n | NORMAL mean eta (V) | NORMAL mean dG_OH | NORMAL mean dG_OOH | NORMAL mean (dG_OOH − dG_OH) | NORMAL sd (dG_OOH − dG_OH) |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for tag in TAGS:
        if tag not in done:
            w(f"| {tag} | {cp_pending(C, tag)} | | | | | | | | |")
            continue
        rows = R[tag]
        check(all(x[k].strip() != "" for x in rows for k in ("dG_OH", "dG_O", "dG_OOH")), f"{tag}: a gated-six row carries an empty dG cell")
        m_oh, m_o, m_ooh = (float(np.mean([fl(x, k) for x in rows])) for k in ("dG_OH", "dG_O", "dG_OOH"))
        nm = [x for x in rows if x["OOH_category"] == "NORMAL"]
        nm_eta = [fl(x, "eta_V") for x in nm if has_eta(x)]
        if not nm:
            w(f"| {tag} | {f4(m_oh)} | {f4(m_o)} | {f4(m_ooh)} | 0 | — | — | — | — | — |")
            continue
        diff = [fl(x, "dG_OOH") - fl(x, "dG_OH") for x in nm]
        sdd = sd1(diff)
        w(f"| {tag} | {f4(m_oh)} | {f4(m_o)} | {f4(m_ooh)} | {len(nm)} | {f4(float(np.mean(nm_eta))) if nm_eta else '—'} | {f4(float(np.mean([fl(x, 'dG_OH') for x in nm])))} | {f4(float(np.mean([fl(x, 'dG_OOH') for x in nm])))} | {f4(float(np.mean(diff)))} | {'—' if sdd is None else f4(sdd)} |")
    w("")
    # ---- table 3
    w(f"**Table C′3 — O-O distance of the OOH endpoint per model** (`OOH_o_o_A` over the {full} rows: min, 5th percentile, median, max; rows below {CP_OO_CUT:.2f} A — a post-hoc reading rule, not a docs/91 band):")
    w("")
    w(f"| model | n with an O-O value | min (A) | p5 (A) | median (A) | max (A) | rows below {CP_OO_CUT:.2f} A |")
    w("|---|---|---|---|---|---|---|")
    for tag in TAGS:
        if tag not in done:
            w(f"| {tag} | {cp_pending(C, tag)} | | | | | |")
            continue
        w(f"| {tag} | {cp_oo_cells(R[tag], tag, 'gated-six', len(coll[tag]))} |")
    w("")
    n_coll = sum(len(v) for v in coll.values())
    if n_coll:
        w(f"**Collapsed O-O rows** (every row with `OOH_o_o_A` < {CP_OO_CUT:.2f} A; cells are the csv values):")
        w("")
        w(CP_COLLAPSED_HEAD)
        w(CP_COLLAPSED_SEP)
        for tag in done:
            for x in coll[tag]:
                w(cp_collapsed_row(tag, x))
        w("")
        L += cp_collapsed_reading(C, coll)
    else:
        w(f"No gated-six row of any complete model carries `OOH_o_o_A` below {CP_OO_CUT:.2f} A; the collapsed-row table is empty and the excluding versions of the tables below coincide with the full ones.")
        w("")
    # ---- table 4
    pairs = [(a, b) for i, a in enumerate(TAGS) for b in TAGS[i + 1:]]
    w("**Table C′4 — pairwise site-level agreement** (matched (`formula`, `seed`, `site_index`) rows of the two models; Pearson r and Spearman rho (average ranks) of `eta_V`; shift = eta(b) − eta(a) in V, mean and median; fraction of matched rows with the same `OOH_category`; each pair once over every matched row and once over the matched rows with no collapsed-O-O row under either model of the pair):")
    w("")
    w("| pair a, b | rows | n matched | Pearson r | Spearman rho | mean shift b − a (V) | median shift (V) | same OOH category |")
    w("|---|---|---|---|---|---|---|---|")
    S4 = {}
    for a, b in pairs:
        if a not in done or b not in done:
            miss = ", ".join(f"{t} {cp_pending(C, t)}" for t in (a, b) if t not in done)
            w(f"| {a}, {b} | — | {miss} | | | | | |")
            continue
        for label, excl in (("all", set()), ("excluding collapsed", cp_collapsed_keys(C, (a, b)))):
            st = cp_pair_stats(C, a, b, excl)
            if st is None:
                w(f"| {a}, {b} | {label} | 0 | — | — | — | — | — |")
                continue
            S4[(a, b, label)] = st
            w(f"| {a}, {b} | {label} | {st['n']} | {opt3(st['r'])} | {opt3(st['rho'])} | {f4(st['mean_shift'])} | {f4(st['median_shift'])} | {f4(st['same_cat'])} |")
    w("")
    # ---- table 5
    metals = sorted({x["initial_metal"] for t in done for x in R[t]})
    w("**Table C′5 — site eta per model x `initial_metal`** (n and mean `eta_V`; metals as present in the rows; the second block leaves out each model's own collapsed-O-O rows):")
    w("")
    if not metals:
        w("No model is complete, so no `initial_metal` column exists yet; pending: " + ", ".join(f"{t} {cp_pending(C, t)}" for t in pending) + ".")
        w("")
    for label, own in ((("all rows", False), ("excluding collapsed-O-O rows", True)) if metals else ()):
        w(f"*{label}*:")
        w("")
        w("| model | " + " | ".join(f"{m} n, mean (V)" for m in metals) + " |")
        w("|---|" + "---|" * len(metals))
        for tag in TAGS:
            if tag not in done:
                w(f"| {tag} | {cp_pending(C, tag)} |" + " |" * (len(metals) - 1))
                continue
            cc = []
            excl = cp_collapsed_keys(C, (tag,)) if own else set()
            for m in metals:
                ev = [fl(x, "eta_V") for x in R[tag] if x["initial_metal"] == m and has_eta(x) and cp_key(x) not in excl]
                cc.append(f"{len(ev)}, {f4(float(np.mean(ev)))}" if ev else "0, —")
            w(f"| {tag} | " + " | ".join(cc) + " |")
        w("")
    # ---- table 6
    ext = cp_extreme_rows(C, done)
    w(f"**Table C′6 — extreme rows** (post-hoc thresholds: `eta_V` > {CP_ETA_HI} V or `dG_OOH` < {CP_OOH_LO} eV; every gated-six row of a complete model, eta descending):")
    w("")
    if ext:
        w(CP_EXTREME_HEAD)
        w(CP_EXTREME_SEP)
        for tag, x in ext:
            w(cp_extreme_row(tag, x))
        w("")
    cnt = Counter(tag for tag, _ in ext)
    w(f"Rows in the extreme table per model (of {full}): " + "; ".join(f"{t} {cnt.get(t, 0)}" for t in done) + (f"; pending: {', '.join(f'{t} {cp_pending(C, t)}' for t in pending)}" if pending else "") + ".")
    w("")
    L += cp_closing(C, S1, S4, coll_keys, done, pending)
    return L


def cp_collapsed_reading(C, coll):
    L = []
    w = L.append
    rows = [(tag, x) for tag in coll for x in coll[tag]]
    l56 = C.D91.line(56, "Anchors:")
    check("The names assert" in l56, "docs/91:56 carries no \"The names assert\" clause after the anchors")
    anch = l56[l56.index("Anchors:"):l56.index("The names assert")]
    toks = re.findall(r"(\d\.\d+)(?= A\b| and \d| / \d| to \d| -> \d)", anch)
    check(len(toks) >= 5 and all(1.0 < float(t) < 2.0 for t in toks), "docs/91:56 anchor lengths could not be read")
    shortest = min(toks, key=float)
    m = re.search(r"O2_LIKE <= (\d\.\d+) A; SUPEROXO_LIKE \((\d\.\d+), (\d\.\d+)\]; OOH_LIKE \((\d\.\d+), (\d\.\d+)\]; OO_CLEAVED > (\d\.\d+) A", l56)
    check(m, "docs/91:56 carries no O-O band clause")
    o2_top = m.group(1)
    oo = [fl(x, "OOH_o_o_A") for _, x in rows]
    ooh = [fl(x, "dG_OOH") for _, x in rows]
    ncat = Counter(x["OOH_o_o_class"] for _, x in rows)
    rel = "shorter than" if max(oo) < float(shortest) else "not below"
    w(f"Reading of the collapsed rows (post-hoc, from the cells above): their O-O separations span {f4(min(oo))}-{f4(max(oo))} A, {rel} the shortest O-O length among the `docs/91:56` anchors, {shortest} A (the {len(toks)} anchor lengths of that line read here: {', '.join(toks)} A). The `docs/91:56` bands read \"{m.group(0)}\": the O2_LIKE band has no lower edge, so every O-O below {o2_top} A is O2_LIKE by construction and the classifier reads these rows as {', '.join(f'{k} ({n})' for k, n in sorted(ncat.items()))} (`OOH_o_o_class`).")
    check(all(x["OOH_o_o_class"] == "O2_LIKE" for _, x in rows), "a collapsed O-O row is not classed O2_LIKE by the csv")
    neg = sum(1 for v in ooh if v < 0.0)
    w(f"`dG_OOH` of these rows spans {f4(min(ooh))} to {f4(max(ooh))} eV; {neg} of {len(rows)} are negative.")
    pls4 = [(tag, x) for tag, x in rows if x["pls"] == "4"]
    if pls4:
        mg = re.match(r"G_TOTAL = (\d\.\d+)", C.DESC.line(34, "G_TOTAL"))
        mu = re.match(r"OER_EQUILIBRIUM_V = (\d\.\d+)", C.DESC.line(35, "OER_EQUILIBRIUM_V"))
        check(mg and mu, "descriptors.py:34-35 do not read as `G_TOTAL = <number>` / `OER_EQUILIBRIUM_V = <number>`")
        gt = float(mg.group(1))
        u0 = float(mu.group(1))
        for _, x in pls4:
            check(has_eta(x) and abs(fl(x, "eta_V") + u0 - (gt - fl(x, "dG_OOH"))) < 1e-9, f"{cp_where(x)}: a pls-4 collapsed row does not satisfy eta + U0 = G_TOTAL − dG_OOH")
        ev4 = [fl(x, "eta_V") for _, x in pls4]
        w(f"{len(pls4)} of {len(rows)} carry `pls` 4 and satisfy eta + {u0} = {gt} − `dG_OOH` to 1e-9 (`src/hea_oer/descriptors.py:10`, `:34-35`, read as text; asserted per row), so their eta of {f4(min(ev4))}-{f4(max(ev4))} V is the step-4 term {gt} − dG_OOH minus the equilibrium potential {u0} V.")
    else:
        w("None of these rows carries `pls` 4; the eta column is read as printed.")
    unc = sum(1 for _, x in rows if il(x, "unconverged_states") > 0)
    w(f"`unconverged_states` > 0 on {unc} of {len(rows)}.")
    verdicts = []
    for tag, x in rows:
        wv = C.WIN.get((tag, x["formula"]))
        check(wv is not None, f"no min-site row for {tag}/{x['formula']}")
        same = (wv["seed"], wv["site_index"]) == (x["seed"], x["site_index"])
        verdicts.append(f"{tag} {x['formula']} seed {x['seed']} site {x['site_index']}: {'IS the min-site row' if same else 'not the min-site row'} (min-site row seed {wv['seed']} site {wv['site_index']}, eta {r(wv['eta_V'])} V)")
    n_min = sum(1 for v in verdicts if "IS the" in v)
    n_min_mpa0 = sum(1 for (tag, _), v in zip(rows, verdicts) if "IS the" in v and tag == "mpa0")
    if n_min == 0:
        tail = "so the (c) rule values and the `ensemble_spread` minima are untouched by them"
    else:
        tail = f"so {n_min} of these rows {'is' if n_min == 1 else 'are'} the min-site row of {'its' if n_min == 1 else 'their'} composition under {'its' if n_min == 1 else 'their'} model and that composition's `ensemble_spread` entry under that model rests on a collapsed endpoint"
        tail += f"; {n_min_mpa0} of them under mpa0, whose minima are the (c) rule values" if n_min_mpa0 else "; none of them under mpa0, so no (c) rule value rests on one"
    w("Whether a collapsed row is the min-site row of its composition under its model (against `ranking.ensemble_spread.<f>.min_site_eta_by_model_V`, the (c) values): " + "; ".join(verdicts) + f" — {tail}.")
    w("")
    return L


def cp_lowest(C, box):
    """Per model with every min-site value of the box in `ranking.ensemble_spread` (the (c) values, i.e. C.WIN): the composition with the lowest value."""
    lowest = OrderedDict()
    for tag in TAGS:
        vals = {f: C.kr["ensemble_spread"][f]["min_site_eta_by_model_V"].get(tag) for f in box}
        if all(v is not None for v in vals.values()):
            low = min(box, key=lambda f: vals[f])
            lowest[tag] = (low, vals[low])
    return lowest


def cp_lead_sentence(lowest, word):
    """The lowest-composition sentence of a closing: per model, shared compositions, pending models; `word` names the box size."""
    parts = [f"under {t}: {f} ({r(v)} V)" for t, (f, v) in lowest.items()]
    groups = OrderedDict()
    for t, (f, _) in lowest.items():
        groups.setdefault(f, []).append(t)
    shared = [f"{f} holds the lowest value under {' and '.join(ts)}" for f, ts in groups.items() if len(ts) > 1]
    lead_s = "; ".join(parts) + (" — " + "; ".join(shared) if shared else " — no composition holds the lowest value under two models") if parts else f"no model has all {word} minima yet"
    miss_lead = [t for t in TAGS if t not in lowest]
    if miss_lead:
        lead_s += f" (pending: {', '.join(miss_lead)})"
    return lead_s


def cp_spread_sentence(C, box, table):
    """The largest `ensemble_spread.spread_V` over the box and the model pair that makes it."""
    sp = {f: C.kr["ensemble_spread"][f] for f in box}
    fmax = max(box, key=lambda f: sp[f]["spread_V"])
    bm = sp[fmax]["min_site_eta_by_model_V"]
    if len(bm) >= 2:
        lo_t = min(bm, key=lambda t: bm[t])
        hi_t = max(bm, key=lambda t: bm[t])
        return f"the largest `ensemble_spread.spread_V` of {table} is {fmax} at {r(sp[fmax]['spread_V'])} V (`n_models` {sp[fmax]['n_models']}), made by {lo_t} {r(bm[lo_t])} against {hi_t} {r(bm[hi_t])}"
    return f"the largest `ensemble_spread.spread_V` of {table} is {fmax} at {r(sp[fmax]['spread_V'])} V (`n_models` {sp[fmax]['n_models']}; no pair yet)"


def cp_shift_deltas(S4, excl_label, none_left):
    """Per model pair: the mean shift over every matched row against the mean shift with the `excl_label` rows left out."""
    deltas = []
    for (a, b, label), st in S4.items():
        if label != "all":
            continue
        ex = S4.get((a, b, excl_label))
        if ex is None:
            deltas.append(f"{a}, {b}: {f4(st['mean_shift'])} V over {st['n']}; {none_left}")
        elif ex["n"] == st["n"]:
            deltas.append(f"{a}, {b}: {f4(st['mean_shift'])} V over {st['n']}, no row excluded, the two figures coincide")
        else:
            deltas.append(f"{a}, {b}: {f4(st['mean_shift'])} V over {st['n']} against {f4(ex['mean_shift'])} V over {ex['n']} — a difference of {f4(st['mean_shift'] - ex['mean_shift'])} V carried by the {st['n'] - ex['n']} excluded rows")
    return "; ".join(deltas) if deltas else "no model pair is complete"


def cp_closing(C, S1, S4, coll_keys, done, pending):
    L = []
    w = L.append
    # the composition with the lowest min-site eta under each model (the (c) values, i.e. C.WIN)
    lead_s = cp_lead_sentence(cp_lowest(C, C.GATED), "six")
    # largest per-composition spread of (c)
    spread_s = cp_spread_sentence(C, C.GATED, "Table C2")
    # median beside minimum
    med_s = "; ".join(f"{t} min {f4(S1[t]['min'])}, median {f4(S1[t]['median'])} V" for t in done) or "no complete model"
    # mean-shift deltas with and without the collapsed rows
    delta_s = cp_shift_deltas(S4, "excluding collapsed", "no matched row remains without a collapsed endpoint")
    w(f"**Closing (post-hoc, every number from the tables above and Table C2).** Lowest min-site eta per model (`min_site_eta_by_model_V`, read, not ranked): {lead_s}. Spread: {spread_s}. Per-model median site eta beside the per-model minimum (Table C′1): {med_s}. Mean shift of Table C′4 with and without the collapsed-O-O rows ({len(coll_keys)} distinct (formula, seed, site) keys collapsed): {delta_s}." + (f" Pending in this subsection: {', '.join(f'{t} {cp_pending(C, t)}' for t in pending)}." if pending else "") + " The same readings over all twelve CENSUS-2 compositions are in (c′′) below (post-hoc).")
    w("")
    return L


# ----------------------------------------------------------------------------- section 4c: (c'') post-hoc, the same readings over the twelve
CPP_STAMP = "2026-09-09T01:20:23+00:00"  # `generated` of the first readout with every CENSUS-2 manifest landed
CPP_MANIFESTS = 36  # CENSUS-2 manifests: twelve compositions x three ensemble models
CPP_ADDED = (f"This block was added to the emitter on 2026-09-09 after all {CPP_MANIFESTS} CENSUS-2 manifests had landed (readout stamp "
             f"{CPP_STAMP}); every threshold in it is a reading rule chosen after seeing those rows, not a "
             "pre-stated bar, and nothing in it enters any rule of readout (c) or fills any slot.")
CPP_OOH_NEG = 0.0  # eV; post-hoc reading rule for a negative *OOH formation row
CPP_NEG_LABEL = "excluding negative-*OOH"


def cpp_box(C):
    """The twelve compositions of `ranking.ensemble_spread` in banked order: the keys sorted by `banked_eta_V` (never typed)."""
    es = C.kr["ensemble_spread"]
    check(all("banked_eta_V" in es[f] for f in es), "an `ensemble_spread` entry has no `banked_eta_V`")
    vals = {f: es[f]["banked_eta_V"] for f in es}
    check(len(set(vals.values())) == len(vals), "two `ensemble_spread` entries carry the same `banked_eta_V`; the banked twelve-order is not defined")
    box = tuple(sorted(es.keys(), key=lambda f: vals[f]))
    check(sorted(box) == sorted(C.BOX12), "the `ensemble_spread` keys differ from the twelve-composition box")
    check([f for f in box if f in C.GATED] == C.ORDER, "the banked twelve-order restricted to the gated six differs from `banked_order`")
    return box


def cpp_neg(C, tag, box):
    """Rows of one model with `dG_OOH` below CPP_OOH_NEG (a post-hoc reading rule); an empty or non-numeric cell fails closed."""
    return [x for x in cp_rows(C, box)[tag] if fl(x, "dG_OOH") < CPP_OOH_NEG]


def cpp_neg_keys(neg, tags):
    keys = set()
    for tag in tags:
        keys.update(cp_key(x) for x in neg.get(tag, ()))
    return keys


def cpp_win(C, tag, f):
    wv = C.WIN.get((tag, f))
    check(wv is not None, f"no min-site row for {tag}/{f}")
    return wv


def cpp_range(rows, key, n):
    """min-max of a numeric csv column over the rows with a value, in A at 4 dp; an empty cell is left out as in `rcell`, and a shortfall against n is named."""
    vals = [fl(x, key) for x in rows if x[key].strip() != ""]
    if not vals:
        return "no value"
    return f"{f4(min(vals))}-{f4(max(vals))} A" + (f" over {len(vals)} of {n} rows with a value" if len(vals) < n else "")


def section_c_double_prime(C):
    L = []
    w = L.append
    box = cpp_box(C)
    es = C.kr["ensemble_spread"]
    R = cp_rows(C, box)
    full = cp_full(C, box)
    done = cp_complete(C, box)
    pending = [t for t in TAGS if t not in done]
    coll = OrderedDict((t, cp_collapsed(C, t, box)) for t in done)
    neg = OrderedDict((t, cpp_neg(C, t, box)) for t in done)
    neg_keys = cpp_neg_keys(neg, done)
    pend_s = ", ".join(f"{t} {cp_pending(C, t, box)}" for t in pending)
    if not pending:
        # a complete readout must be consistent with the two typed facts of CPP_ADDED; a partial readout predates them
        check(C.GEN >= CPP_STAMP, f"a complete twelve-composition readout carries `generated` {C.GEN}, earlier than the stamp {CPP_STAMP} named in the post-hoc twelve-composition block")
        n_man = len({x["manifest"] for x in C.HEA if x["arm"] == "CENSUS-2"})
        check(n_man == CPP_MANIFESTS, f"{n_man} CENSUS-2 manifests in per_site.csv, not the {CPP_MANIFESTS} named in the post-hoc twelve-composition block")
    w(f"### (c′′) post-hoc — the same readings over all twelve CENSUS-2 compositions ({full} sites per model)")
    w("")
    w(f"{CPP_ADDED} Post-hoc throughout; it scores nothing, ranks nothing and changes no verdict. The readout read here carries `generated` {C.GEN}. Site set: `per_site.csv` `candidate_status == evaluated`, `formula` in the twelve keys of `ranking.ensemble_spread`, arm CENSUS-1 for mpa0 and CENSUS-2 for omat0 / mp0 / matpes, seeds {', '.join(CP_SEEDS)} x site_index {'..'.join((CP_SITES[0], CP_SITES[-1]))} — {full} rows per model; a model with fewer rows prints pending and is left out of the order and pairwise tables. The banked twelve-order is the twelve `ensemble_spread` keys sorted by their `banked_eta_V` (asserted equal to `banked_order` on the gated six): " + ", ".join(f"{f} {r(es[f]['banked_eta_V'])}" for f in box) + ". Every statistic below is arithmetic of this script on the named csv columns; the collapsed-O-O and extreme-row thresholds are the (c′) reading rules, the negative-*OOH threshold is a reading rule of this block alone, and none is a docs/91 band.")
    w("")
    # ---- table 1
    w("**Table C′′1 — site eta per model over the twelve** (columns as Table C′1, then `OOH_category` counts NORMAL / DESORPTION / DISSOCIATION / MIGRATION / RECONSTRUCTION, sites with `all_states_intact` True and with `all_states_adsorbate_intact` True):")
    w("")
    w("| model | n (with eta) | mean (V) | sd (V) | median (V) | p10 (V) | min (V) | max (V) | unconverged sites | pls 1 / 2 / 3 / 4 | OOH N/D/X/M/R | INTACT | ADS-INTACT |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    S1 = {}
    for tag in TAGS:
        if tag not in done:
            w(f"| {tag} | {cp_pending(C, tag, box)} | | | | | | | | | | | |")
            continue
        rows = R[tag]
        S1[tag] = cp_eta_stats(rows, tag, "twelve-composition")
        for k in ("all_states_intact", "all_states_adsorbate_intact"):
            check(all(x[k] in ("True", "False") for x in rows), f"{tag}: `{k}` carries a value other than True or False")
        w(f"| {tag} | {cp_eta_cells(S1[tag])} | {cat5(rows, 'OOH_category')} | {sum(x['all_states_intact'] == 'True' for x in rows)} | {sum(x['all_states_adsorbate_intact'] == 'True' for x in rows)} |")
    w("")
    # ---- table 2: per-model twelve-order and the lowest composition
    w("**Table C′′2 — the twelve-composition order of min-site eta per model** (`ranking.ensemble_spread.<f>.min_site_eta_by_model_V.<model>`, ascending; Kendall tau-a against the banked twelve-order, computed here; the lowest composition's min-site row from `per_site.csv`: seed / site_index / `initial_metal`, `OOH_category`, `OOH_o_o_class`, `O_tier`):")
    w("")
    w("| model | order of min-site eta (ascending, V) | Kendall tau-a vs banked twelve-order | lowest composition | its min-site row: seed / site / initial metal, OOH category, O-O class, O tier |")
    w("|---|---|---|---|---|")
    lowest = cp_lowest(C, box)
    low_win = OrderedDict()
    for tag in TAGS:
        if tag not in done:
            w(f"| {tag} | {cp_pending(C, tag, box)} | | | |")
            continue
        check(tag in lowest, f"{tag}: {full} rows landed but `ensemble_spread` lacks a min-site value of that model on some composition")
        vals = {f: es[f]["min_site_eta_by_model_V"][tag] for f in box}
        order = sorted(box, key=lambda f: vals[f])
        tau = kendall_tau_a(order, box)
        f_low = lowest[tag][0]
        check(order[0] == f_low, f"{tag}: the first of the order differs from the lowest composition")
        wv = cpp_win(C, tag, f_low)
        low_win[tag] = wv
        w(f"| {tag} | " + " < ".join(f"{f} {r(vals[f])}" for f in order) + f" | {tau!r} | {f_low} ({r(vals[f_low])} V) | {wv['seed']} / {wv['site_index']} / {wv['initial_metal']}, {wv['OOH_category']}, {wv['OOH_o_o_class']}, {wv['O_tier']} |")
    w("")
    if low_win:
        metals = Counter(wv["initial_metal"] for wv in low_win.values())
        n_cr = sum(1 for wv in low_win.values() if wv["initial_metal"] == "Cr")
        groups = OrderedDict()
        for tag, wv in low_win.items():
            groups.setdefault(lowest[tag][0], []).append(tag)
        shared = [f"{f} under {' and '.join(ts)}" for f, ts in groups.items() if len(ts) > 1]
        w(f"Of the {len(low_win)} complete model{'' if len(low_win) == 1 else 's'}, {n_cr} put a Cr site lowest (`initial_metal` of the lowest composition's min-site row: " + ", ".join(f"{t} {wv['initial_metal']}" for t, wv in low_win.items()) + f"; by metal {', '.join(f'{m} {n}' for m, n in sorted(metals.items()))}); " + (f"two or more models share a lowest composition: {'; '.join(shared)}" if shared else "no two models share the lowest composition") + (f". Pending: {pend_s}." if pending else "."))
        w("")
    else:
        w(f"No model is complete on the twelve; pending: {pend_s}.")
        w("")
    w("**Table C′′2b — per-composition ensemble spread over the twelve** (`ranking.ensemble_spread.<f>.{banked_eta_V, spread_V, n_models, min_site_eta_by_model_V}`, banked twelve-order; a spread cell at `n_models` < 4 names the pending tags; the values are those of `ranking.json`, anchored, not recomputed):")
    w("")
    w("| composition (banked twelve-order) | banked_eta_V | ensemble spread (V) [n_models] | min-site eta by model (V) |")
    w("|---|---|---|---|")
    for f in box:
        w(f"| {f} | {r(es[f]['banked_eta_V'])} | {spread_cell(es[f])} | {by_model_cell(es[f])} |")
    w("")
    # ---- table 3: O-O, collapsed rows, negative *OOH rows
    w(f"**Table C′′3 — O-O distance of the OOH endpoint per model over the twelve** (`OOH_o_o_A` over the {full} rows: min, 5th percentile, median, max; rows below {CP_OO_CUT:.2f} A — the (c′) reading rule):")
    w("")
    w(f"| model | n with an O-O value | min (A) | p5 (A) | median (A) | max (A) | rows below {CP_OO_CUT:.2f} A |")
    w("|---|---|---|---|---|---|---|")
    for tag in TAGS:
        if tag not in done:
            w(f"| {tag} | {cp_pending(C, tag, box)} | | | | | |")
            continue
        w(f"| {tag} | {cp_oo_cells(R[tag], tag, 'twelve-composition', len(coll[tag]))} |")
    w("")
    n_coll = sum(len(v) for v in coll.values())
    if n_coll:
        w(f"**Collapsed O-O rows over the twelve** (every row with `OOH_o_o_A` < {CP_OO_CUT:.2f} A; cells are the csv values):")
        w("")
        w(CP_COLLAPSED_HEAD)
        w(CP_COLLAPSED_SEP)
        for tag in done:
            for x in coll[tag]:
                w(cp_collapsed_row(tag, x))
        w("")
    else:
        w(f"No twelve-composition row of any complete model carries `OOH_o_o_A` below {CP_OO_CUT:.2f} A." + (f" Pending: {pend_s}." if pending else ""))
        w("")
    n_neg = sum(len(v) for v in neg.values())
    w(f"**Negative *OOH formation rows** (`dG_OOH` < {CPP_OOH_NEG} eV, a post-hoc reading rule of this block; every twelve-composition row of a complete model; cells are the csv values):")
    w("")
    if n_neg:
        w("| model | composition | seed | site | initial metal | dG_OOH (eV) | eta (V) | pls | OOH tier / M-O (A) / category / O-O (A) / O-O class / H location | unconverged_states | OOH_slab_max_A |")
        w("|---|---|---|---|---|---|---|---|---|---|---|")
        for tag in done:
            for x in neg[tag]:
                w(f"| {tag} | {x['formula']} | {x['seed']} | {x['site_index']} | {x['initial_metal']} | {r(fl(x, 'dG_OOH'))} | {re_(x)} | {x['pls']} | {x['OOH_tier']} / {rcell(x, 'OOH_m_o_A')} / {x['OOH_category']} / {rcell(x, 'OOH_o_o_A')} / {x['OOH_o_o_class']} / {x['OOH_h_location']} | {x['unconverged_states']} | {rcell(x, 'OOH_slab_max_A')} |")
        w("")
        L += cpp_negative_reading(C, neg, coll, done, full)
    else:
        w(f"No twelve-composition row of any complete model carries `dG_OOH` below {CPP_OOH_NEG} eV; the excluding versions of Table C′′5 coincide with the full ones." + (f" Pending: {pend_s}." if pending else ""))
        w("")
    # ---- table 4: extreme rows
    ext = cp_extreme_rows(C, done, box)
    w(f"**Table C′′4 — extreme rows over the twelve** (post-hoc thresholds as Table C′6: `eta_V` > {CP_ETA_HI} V or `dG_OOH` < {CP_OOH_LO} eV; every twelve-composition row of a complete model, eta descending):")
    w("")
    if ext:
        w(CP_EXTREME_HEAD)
        w(CP_EXTREME_SEP)
        for tag, x in ext:
            w(cp_extreme_row(tag, x))
        w("")
    cnt = Counter(tag for tag, _ in ext)
    w(f"Rows in the extreme table per model (of {full}): " + "; ".join(f"{t} {cnt.get(t, 0)}" for t in done) + (f"; pending: {pend_s}" if pending else "") + ".")
    w("")
    # ---- table 5: pairwise agreement
    pairs = [(a, b) for i, a in enumerate(TAGS) for b in TAGS[i + 1:]]
    w("**Table C′′5 — pairwise site-level agreement over the twelve** (matched (`formula`, `seed`, `site_index`) rows of the two models, columns as Table C′4; each pair once over every matched row and once over the matched rows whose key is in the negative-*OOH table under neither model of the pair; n is the matched count of each line):")
    w("")
    w("| pair a, b | rows | n matched | Pearson r | Spearman rho | mean shift b − a (V) | median shift (V) | same OOH category |")
    w("|---|---|---|---|---|---|---|---|")
    S4 = {}
    for a, b in pairs:
        if a not in done or b not in done:
            miss = ", ".join(f"{t} {cp_pending(C, t, box)}" for t in (a, b) if t not in done)
            w(f"| {a}, {b} | — | {miss} | | | | | |")
            continue
        for label, excl in (("all", set()), (CPP_NEG_LABEL, cpp_neg_keys(neg, (a, b)))):
            st = cp_pair_stats(C, a, b, excl, box)
            if st is None:
                w(f"| {a}, {b} | {label} | 0 | — | — | — | — | — |")
                continue
            S4[(a, b, label)] = st
            w(f"| {a}, {b} | {label} | {st['n']} | {opt3(st['r'])} | {opt3(st['rho'])} | {f4(st['mean_shift'])} | {f4(st['median_shift'])} | {f4(st['same_cat'])} |")
    w("")
    # ---- closing
    lead_s = cp_lead_sentence(lowest, "twelve")
    spread_s = cp_spread_sentence(C, box, "Table C′′2b")
    med_s = "; ".join(f"{t} min {f4(S1[t]['min'])}, median {f4(S1[t]['median'])} V" for t in done) or "no complete model"
    delta_s = cp_shift_deltas(S4, CPP_NEG_LABEL, "no matched row remains outside the negative-*OOH table")
    neg_models = [t for t in done if neg[t]]
    neg_where = (" (all under " + " and ".join(neg_models) + ")") if neg_models else ""
    w(f"**Closing (post-hoc, every number from the tables above).** Lowest min-site eta per model over the twelve (`min_site_eta_by_model_V`, read, not ranked): {lead_s}. Spread: {spread_s}. Per-model median site eta beside the per-model minimum (Table C′′1): {med_s}. Mean shift of Table C′′5 with and without the negative-*OOH rows ({len(neg_keys)} distinct (formula, seed, site) keys{neg_where}): {delta_s}." + (f" Pending in this block: {pend_s}." if pending else ""))
    w("")
    return L


def cpp_negative_reading(C, neg, coll, done, full):
    L = []
    w = L.append
    rows = [(tag, x) for tag in neg for x in neg[tag]]
    coll_keys = {(tag, cp_key(x)) for tag in coll for x in coll[tag]}
    w(f"Rows in the negative-*OOH table per model (of {full}): " + "; ".join(f"{t} {len(neg[t])}" for t in done) + ".")
    ooh = [fl(x, "dG_OOH") for _, x in rows]
    w("")
    w(f"A negative `dG_OOH` is a *OOH formation free energy below zero; these rows are read here, by a post-hoc rule of this block, as broken endpoints for the excluding lines of Table C′′5, not as site values. `dG_OOH` of the {len(rows)} rows spans {f4(min(ooh))} to {f4(max(ooh))} eV.")
    w("")
    in_coll = [(t, x) for t, x in rows if (t, cp_key(x)) in coll_keys]
    not_coll = [(t, x) for t, x in rows if (t, cp_key(x)) not in coll_keys]
    parts = [f"{len(in_coll)} of the {len(rows)} are rows of the collapsed-O-O table above"]
    if not_coll:
        n = len(not_coll)
        oo = cpp_range([x for _, x in not_coll], "OOH_o_o_A", n)
        mo = cpp_range([x for _, x in not_coll], "OOH_m_o_A", n)
        tiers = Counter(x["OOH_tier"] for _, x in not_coll)
        hl = Counter(x["OOH_h_location"] for _, x in not_coll)
        cls = Counter(x["OOH_o_o_class"] for _, x in not_coll)
        cols = f"`OOH_tier` {', '.join(f'{k} {v}' for k, v in sorted(tiers.items()))}; `OOH_m_o_A` {mo}; `OOH_o_o_A` {oo}, `OOH_o_o_class` {', '.join(f'{k} {v}' for k, v in sorted(cls.items()))}; `OOH_h_location` {', '.join(f'{k} {v}' for k, v in sorted(hl.items()))}"
        names = "; ".join(cp_where(x) for _, x in not_coll)
        if tiers.get("desorbed", 0) == n and hl.get("H_FREE", 0) == n and cls.get("O2_LIKE", 0) == n:
            parts.append(f"the other {n} ({names}) read, from the tier, H-location and O-O class columns, tier desorbed on {n} of {n}, hydrogen H_FREE on {n} of {n} and O-O class O2_LIKE on {n} of {n} ({cols}): a desorbed O2 fragment with a free hydrogen, an O-O separation inside the O2_LIKE band and no O-O collapse")
        else:
            parts.append(f"the other {n} ({names}) do not all read tier desorbed with hydrogen H_FREE and O-O class O2_LIKE ({cols}), so no single reading is given for them")
    else:
        parts.append("no negative row lies outside the collapsed-O-O table")
    w("; ".join(parts) + ".")
    w("")
    verdicts = []
    for tag, x in rows:
        wv = cpp_win(C, tag, x["formula"])
        same = (wv["seed"], wv["site_index"]) == (x["seed"], x["site_index"])
        verdicts.append(f"{tag} {x['formula']} seed {x['seed']} site {x['site_index']}: {'IS the min-site row' if same else 'not the min-site row'} (min-site row seed {wv['seed']} site {wv['site_index']}, eta {r(wv['eta_V'])} V)")
    n_min = sum(1 for v in verdicts if "IS the" in v)
    if n_min == 0:
        tail = f"so no `ensemble_spread` minimum of any composition under any complete model ({', '.join(done)}) rests on a negative-*OOH row"
    else:
        tail = f"so {n_min} of these rows {'is' if n_min == 1 else 'are'} the min-site row of {'its' if n_min == 1 else 'their'} composition under {'its' if n_min == 1 else 'their'} model and that composition's `ensemble_spread` entry under that model rests on a negative-*OOH endpoint"
    w("Whether a negative-*OOH row is the min-site row of its composition under its model (against `ranking.ensemble_spread.<f>.min_site_eta_by_model_V`; the (c) rule values concern the gated six and are read in (c′)): " + "; ".join(verdicts) + f" — {tail}.")
    w("")
    return L


# ----------------------------------------------------------------------------- section 5: (d)
def section_d(C):
    L = []
    w = L.append
    ds = C.R["decisive_site"]
    leader = C.GATED[0]
    w("## (d) DECISIVE SITE under each model — post-hoc extension of `docs/91:65` (the mpa0 line is the pre-stated reading)")
    w("")
    w(f"`docs/91:65` verbatim: \"{C.D91.line(65, 'DECISIVE SITE')}\"")
    w("")
    m0 = C.WIN[("mpa0", leader)]
    check((m0["seed"], m0["site_index"]) == (str(ds["winner_seed"]), str(ds["winner_site_index"])), "per_site.csv min row of the leader under mpa0 differs from decisive_site")
    w(f"mpa0 (`reproduction.json` `decisive_site`, `docs/93:133`, unchanged): winner seed {ds['winner_seed']}, site_index {ds['winner_site_index']}, {ds['winner_site_metal']}, eta {r(ds['winner_eta_V'])} V, `winner_seed_matches_banked: {bl(ds['winner_seed_matches_banked'])}`, OOH {ds['ooh_readout']}, `winner_site_intact: {bl(ds['winner_site_intact'])}`, `winner_pathway: {ds['winner_pathway']}`; from the same site's `per_site.csv` row (seed and site_index asserted equal): O-O {r(m0['OOH_o_o_A'])} A = {m0['OOH_o_o_class']}, hydrogen {m0['OOH_h_location']} on the {m0['OOH_h_carrier']}, `unconverged_states` {m0['unconverged_states']}, OOH tier {m0['OOH_tier']}.")
    w("")
    for tag in ENSEMBLE:
        wv = C.WIN.get((tag, leader))
        if wv is None:
            w(f"- {tag}: pending, `{tag}__{leader}` not landed.")
            continue
        ooh_intact = wv["OOH_category"] == "NORMAL" and int(wv["unconverged_states"]) == 0 and wv["OOH_tier"] != "desorbed"
        w(f"- **{tag}** (post-hoc; min-`eta_V` row of `per_site.csv` for `{tag}__{leader}`): seed {wv['seed']}, site_index {wv['site_index']}, initial metal {wv['initial_metal']}, eta {r(wv['eta_V'])} V; OOH {wv['OOH_category']}{' (INTACT by the csv columns: NORMAL, site `unconverged_states` 0, tier ' + wv['OOH_tier'] + ')' if ooh_intact else ''}, tier {wv['OOH_tier']}, O-O {r(wv['OOH_o_o_A'])} A = {wv['OOH_o_o_class']}, hydrogen {wv['OOH_h_location']} on the {wv['OOH_h_carrier']}, binding metal {wv['OOH_binding_metal']}, pathway {wv['pathway']}; `all_states_intact` {wv['all_states_intact']}, `all_states_adsorbate_intact` {wv['all_states_adsorbate_intact']}; seed equals 1 (banked): {'yes' if wv['seed'] == '1' else 'no'}.")
    w("")
    w(f"**Table D1 — the leader's four seed-1 sites under each model** (rows `formula == {leader}`, `seed == 1`; the mpa0 rows equal `decisive_site.seed1_sites[]`, asserted):")
    w("")
    w("| model | site_index | initial metal | eta (V) | OOH category | O-O class | H location | pathway | unconverged states | all states INTACT |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for tag in TAGS:
        rows = sorted([x for x in C.HEA if x["tag"] == tag and x["formula"] == leader and x["seed"] == "1"], key=lambda x: int(x["site_index"]))
        if not rows:
            w(f"| {tag} | pending: `{tag}__{leader}` not landed | | | | | | | | |")
            continue
        if tag == "mpa0":
            got = [(int(x["site_index"]), x["initial_metal"], float(x["eta_V"]) if has_eta(x) else None, x["OOH_category"], x["pathway"], int(x["unconverged_states"]), x["all_states_intact"] == "True") for x in rows]
            want = [(s["site_index"], s["initial_metal"], s["eta_V"], s["ooh_category"], s["pathway"], s["unconverged_states"], s["all_states_intact"]) for s in ds["seed1_sites"]]
            check(got == want, "mpa0 seed-1 rows differ from decisive_site.seed1_sites")
        for x in rows:
            w(f"| {tag} | {x['site_index']} | {x['initial_metal']} | {re_(x)} | {x['OOH_category']} | {x['OOH_o_o_class']} | {x['OOH_h_location']} | {x['pathway']} | {x['unconverged_states']} | {x['all_states_intact'].lower()} |")
    w("")
    return L


# ----------------------------------------------------------------------------- section 6: (e) cost
def cost_numbers(C):
    if hasattr(C, "_E"):
        return C._E
    E = {}
    secs = {stem: sum(C.RES[stem]["seconds"]) for stem in C.STEMS}
    E["secs"] = secs
    E["total"] = sum(secs.values())
    c1 = [secs[s] for s in C.STEMS if ckpt_of(s) == "mpa0"]
    E["c1_mean"] = sum(c1) / len(c1)
    check(abs(E["c1_mean"] - C.D93_C1_MEAN) < 0.05, "CENSUS-1 mean does not reproduce docs/93:166")
    groups = OrderedDict()
    for ck in CKPTS:
        stems = [s for s in C.STEMS if ckpt_of(s) == ck]
        g = dict(n=len(stems), stems=stems, sum=sum(secs[s] for s in stems))
        g["mean"] = g["sum"] / g["n"] if g["n"] else None
        if g["n"]:
            g["min"] = min(stems, key=lambda s: secs[s])
            g["max"] = max(stems, key=lambda s: secs[s])
        groups[ck] = g
    E["groups"] = groups
    # log stamps only: a landed stem without a log, or a log without an exit line, is named and left out of the wall
    launches, exits, nolog, noexit = {}, {}, [], []
    for stem in C.STEMS:
        la, ex, code = C.LOG[stem]
        if la is None:
            nolog.append(stem)
            continue
        launches[stem] = iso_to_dt(la)
        if ex is None:
            noexit.append(stem)
        else:
            exits[stem] = iso_to_dt(ex)
    E["launch"], E["exit"], E["nolog"], E["noexit"] = launches, exits, nolog, noexit
    check(launches and exits, "no landed stem carries both a launch and an exit stamp in its log; the wall cannot be read")
    E["first"] = min(launches.values())
    E["last"] = max(exits.values())
    E["wall"] = (E["last"] - E["first"]).total_seconds()
    C._E = E
    return E


def section_e(C):
    L = []
    w = L.append
    P = planning(C)
    E = cost_numbers(C)
    w("## (e) COST realised — every landed manifest beside the planning figure")
    w("")
    w(f"`docs/91:67` verbatim: \"{C.D91.line(67, '511.016')}\"")
    w("")
    w(f"`docs/91:86` (risk 8) verbatim: \"{C.D91.line(86, 'Ensemble checkpoint cost')}\"")
    w("")
    lo, hi = P["per12"]
    w(f"Realised: `results[0].seconds` of each result file (the endmember: the sum over `results[i].seconds`) and the `=== <iso> launch:` / `=== <iso> exit <code>` stamps of `logs/<stem>.log`, printed as UTC `Z`; a log without an exit line, or a landed stem without a log, is marked as such and no file time stands in for the stamp. CENSUS-1 mean = mean of the twelve `mpa0__` `seconds` = {E['c1_mean']:.1f} s (reproduces `docs/93:166`).")
    w("")
    w(f"**Table E1** (`manifests_read` order): | manifest | model (`manifest.model.filename`) | launch (UTC, log) | exit (UTC, log) | `seconds` | h | `seconds` / n sites | realised / planning {r(hi)}-{r(lo)} s | / CENSUS-1 mean |")
    w("")
    w("| manifest | model | launch (UTC, log) | exit (UTC, log) | seconds | h | seconds / n sites | realised / planning | / CENSUS-1 mean |")
    w("|---|---|---|---|---|---|---|---|---|")
    for stem in C.STEMS:
        la0, ex0, code = C.LOG[stem]
        s = E["secs"][stem]
        la = zfmt(E["launch"][stem]) if stem in E["launch"] else "no log"
        ex_s = f"{zfmt(E['exit'][stem])} (exit {code})" if stem in E["exit"] else ("no log" if stem in E["nolog"] else "no exit line")
        if ckpt_of(stem) == "endmember":
            n_cand = len(C.RES[stem]["seconds"])
            w(f"| {stem} ({n_cand} candidates) | {C.MAN[stem]['model']['filename']} | {la} | {ex_s} | {s:.3f} | {s / 3600:.2f} | — | vs {P['endmember_s']} s planned: {s / P['endmember_s']:.2f}x | — |")
        else:
            ns = C.RES[stem]["n_sites"]
            w(f"| {stem} | {C.MAN[stem]['model']['filename']} | {la} | {ex_s} | {s:.3f} | {s / 3600:.2f} | {s / ns:.1f} ({ns} sites) | {s / hi:.2f}x-{s / lo:.2f}x | {s / E['c1_mean']:.2f}x |")
    w("")
    tot = []
    PL = C.PLANNED
    for ck, g in E["groups"].items():
        if g["n"] == 0:
            if ck == "matpes":
                tot.append(f"**{CKPT_LABEL[ck]}**: 0 / {PL[ck]} landed — pending: matpes not landed — carries the MPA-0 figure (`docs/91:67`)")
            else:
                tot.append(f"**{CKPT_LABEL[ck]}**: 0 / {PL[ck]} landed — pending")
            continue
        if ck == "endmember":
            tot.append(f"**{CKPT_LABEL[ck]}**: {g['n']} / {PL[ck]}; {g['sum']:.3f} s = {g['sum'] / 3600:.2f} h against the {P['endmember_s']} s of `r4_validate.json` ({g['sum'] / P['endmember_s']:.2f}x)")
            continue
        tot.append(f"**{CKPT_LABEL[ck]}**: {g['n']} / {PL[ck]} landed; sum {g['sum']:.3f} s = {g['sum'] / 3600:.2f} h; mean {g['mean']:.1f} s = {g['mean'] / 3600:.2f} h per manifest, min {E['secs'][g['min']]:.1f} s (`{g['min']}`), max {E['secs'][g['max']]:.1f} s (`{g['max']}`); mean / CENSUS-1 mean {g['mean'] / E['c1_mean']:.2f}x; mean / planning band {g['mean'] / hi:.2f}x-{g['mean'] / lo:.2f}x")
    w("**Totals per checkpoint.** " + "; ".join(tot) + ".")
    w("")
    arms = ["CENSUS-1 %s-%s h" % P["c1_wall_h"]]
    if E["groups"]["omat0"]["n"] or E["groups"]["mp0"]["n"] or E["groups"]["matpes"]["n"]:
        arms.append("CENSUS-2 %s-%s h" % P["c2_wall_h"])
    if E["groups"]["mpa0_ext"]["n"]:
        arms.append("CENSUS-3 %s-%s h" % P["c3_wall_h"])
    left_out = (f"{len(E['noexit'])} landed logs carry no exit line ({', '.join(f'`{s}`' for s in E['noexit'])})" if E["noexit"] else "every landed log carries an exit line") + ("" if not E["nolog"] else f"; {len(E['nolog'])} landed stems have no log ({', '.join(f'`{s}`' for s in E['nolog'])})")
    w(f"**Wall (post-hoc arithmetic).** First launch over the {len(E['launch'])} landed logs {zfmt(E['first'])} → last exit line over the {len(E['exit'])} landed logs that carry one {zfmt(E['last'])} = **{E['wall'] / 3600:.2f} h** — a log-stamp wall in place of the pre-stated `status.json` runner wall of `docs/91:67`, which this file does not open; {left_out}, and those stems are outside the wall. Against the `docs/91:67` planning wall of the arms represented ({'; '.join(arms)}). Candidate-seconds per wall-second = {E['total']:.3f} / {E['wall']:.0f} = **{E['total'] / E['wall']:.2f}** (sum of every landed `seconds`, endmember included), with the `docs/93:166` caveat that seconds accrued by workers still running at the readout stamp are in neither figure. The result files carry no BFGS step counts (`docs/93:166`), so per-manifest seconds mix throughput with work content and are not separated here.")
    w("")
    ords = []
    for tag in ENSEMBLE:
        stems = [f"{tag}__{f}" for f in C.GATED]
        landed = [s for s in stems if s in C.STEMS and s in E["exit"]]
        if not landed:
            ords.append(f"{tag}: pending (no gated manifest landed with an exit line)")
            continue
        first_stem = min(landed, key=lambda s: E["exit"][s])
        first_exit = E["exit"][first_stem]
        others = [s for s in stems if s != first_stem]
        before, after, nolog = [], [], []
        for s in others:
            la = C.LOG.get(s, (None, None, None))[0]
            if la is None:
                nolog.append(s)
            elif iso_to_dt(la) < first_exit:
                before.append(f"{s} {zfmt(iso_to_dt(la))}")
            else:
                after.append(f"{s} {zfmt(iso_to_dt(la))}")
        status = "met by launch order" if not before else f"not met by launch order ({len(before)} of the other five launched before that exit)"
        if tag == "omat0":
            status += f"; `docs/93:266` reads that the ordering \"was {C.D93_ORDER}\" — a reporting-time reading of the same rule, cited beside this launch-order one and not compared with it"
        ords.append(f"{tag}: first exit `{first_stem}` {zfmt(first_exit)}; launches of the other five before it: {', '.join(before) or 'none'}; after it: {', '.join(after) or 'none'}; no log yet: {', '.join(nolog) or 'none'} — {status}")
    w("**The `docs/91:67` ordering** (\"that realised figure is reported before the other five of that checkpoint are treated as planned\"), read post-hoc from log stamps (the logs are read at emit time and may carry launches later than the readout stamp) as the first exit of each tag against the launch stamps of its other five gated manifests: " + "; ".join(ords) + ".")
    w("")
    w("**Contention (named risk 1, `docs/91:79`).** Only what the logs of the landed stems show is used above (launch and exit stamps); the runner restart, the power-throttling interval and the orphaned workers are the events of `docs/93:170-171`, cited and not re-derived (`status.json` `runner_started` is not read by this file).")
    w("")
    return L


# ----------------------------------------------------------------------------- section 7: (f) distribution
def section_f(C):
    L = []
    w = L.append
    D = C.D["distribution"]
    pf = D["per_formula"]
    w("## (f) SITE-ETA DISTRIBUTION per gated composition (`readout/distribution.json` `distribution.per_formula.<f>`)")
    w("")
    w(f"`docs/91:69` verbatim: \"{C.D91.line(69, 'E[min_k]')}\"")
    w("")
    w(f"`distribution.site_set`: {D['site_set']}. `distribution.statistics`: {D['statistics']}.")
    w("")
    w("**Table F1** (`manifests`, `n_sites`, `n_unconverged_sites`, `all_sites.{n, mean, std, median, p10, min, max}`, `intact_sites.{...}`, `twelve_site_min_V`):")
    w("")
    w(f"| composition | manifests landed (of {C.MAN_PER_F}) | n / unconverged | mean | std | median | p10 | min | max | INTACT n | INTACT mean | INTACT std | INTACT median | INTACT p10 | INTACT min | INTACT max | twelve_site_min_V |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for f in C.GATED:
        p = pf[f]
        a, i = p["all_sites"], p["intact_sites"]
        i_s = " | ".join(["—" if i[k] is None else r(i[k]) for k in ("mean", "std", "median", "p10", "min", "max")])
        std = "—" if a["std"] is None else r(a["std"])
        w(f"| {f} | {len(p['manifests'])} | {a['n']} / {p['n_unconverged_sites']} | {r(a['mean'])} | {std} | {r(a['median'])} | {r(a['p10'])} | {r(a['min'])} | {r(a['max'])} | {i['n']} | {i_s} | {r(p['twelve_site_min_V'])} |")
    w("")
    w("**Table F2** (`expected_min_vs_k[].{k, expected_min}`; `twelve_site_min_V` printed beside k = 12, `docs/91:69`: \"printed beside the k = 12 value as one draw from that curve\"; `o_o_A.{...}`, `o_o_class_counts`):")
    w("")
    w("| composition | E[min_1] | E[min_2] | E[min_3] | E[min_4] | E[min_6] | E[min_12] ‖ twelve-site min | E[min_24] | E[min_48] | E[min_96] | E[min_120] | OOH O-O (A): n, mean, std, median, p10, min, max | O-O class counts |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for f in C.GATED:
        p = pf[f]
        em = {x["k"]: x["expected_min"] for x in p["expected_min_vs_k"]}
        n = p["n_sites"]

        def cell(k):
            return r(em[k]) if k in em else f"pending: n = {n} < {k}"

        oo = p["o_o_A"]
        oos = ", ".join([str(oo["n"])] + [rv(oo[k]) for k in ("mean", "std", "median", "p10", "min", "max")])
        cc = ", ".join(f"{k} {v}" for k, v in sorted(p["o_o_class_counts"].items()))
        w(f"| {f} | {cell(1)} | {cell(2)} | {cell(3)} | {cell(4)} | {cell(6)} | {cell(12)} ‖ {r(p['twelve_site_min_V'])} | {cell(24)} | {cell(48)} | {cell(96)} | {cell(120)} | {oos} | {cc} |")
    w("")
    l44 = C.D91.line(44, "Baek")
    clause = re.search(r"120 permutations per active site with a ~0\.5 eV spread \(Baek et al\., Nat\. Commun\. 2023, 10\.1038/s41467-023-41359-7\); 768 sites per composition with site-energy sigma 0\.19-0\.27 eV \(Potter et al\., arXiv:2504\.11587\)", l44).group(0)
    m = re.search(r"sigma (\d\.\d+)-(\d\.\d+) eV", clause)
    plo, phi = float(m.group(1)), float(m.group(2))
    baek = float(re.search(r"~(\d\.\d) eV", clause).group(1))
    stds = {f: pf[f]["all_sites"]["std"] for f in C.GATED if pf[f]["all_sites"]["std"] is not None}
    ns = {f: pf[f]["n_sites"] for f in C.GATED}
    n_txt = f"n = {next(iter(ns.values()))} per composition" if len(set(ns.values())) == 1 else "n = " + ", ".join(f"{f} {n}" for f, n in ns.items())
    w(f"The site-to-site sample sd spans {min(stds.values()):.4f}-{max(stds.values()):.4f} V across the six ({n_txt}; `all_sites.std`, ddof = 1), beside the site-energy spreads `docs/91:44` names: \"{clause}\" (`docs/91:44`, `:69`). No bar is set on any of these (`docs/91:69`).")
    place = []
    for f in C.GATED:
        n = ns[f]
        if n < C.N_FULL:
            place.append(f"{f}: at n = {n} no comparison is drawn (`docs/93:197`)")
        else:
            sd = stds[f]
            rel = "below" if sd < plo else ("inside" if sd <= phi else "above")
            place.append(f"{f}: sd {r(sd)} V lies {rel} {plo}-{phi} and {'below' if sd < baek else 'above'} {baek} (descriptive placement, `docs/91:69`)")
    w("; ".join(place) + ".")
    w("")
    post = []
    for n in range(181, 187):
        cc = cells(C.D93.line(n))
        f = cc[0]
        if f in ns and ns[f] > 12:
            post.append(f"{f}: 12-site sd {cc[3]} (`docs/93:{n}`, cited) against {r(stds[f])} at n = {ns[f]}")
    if post:
        w("Post-hoc: sd of the 12-site slice against the landed n-site value — " + "; ".join(post) + ".")
    else:
        w("Post-hoc comparison of the 12-site sd with the 120-site sd: pending, no composition has more than its 12 CENSUS-1 sites (the 12-site values are `docs/93:181-186`).")
    w("")
    return L


# ----------------------------------------------------------------------------- section 8: rank resolution
def dn_cell(dn):
    """The decorations-needed cell of T4 / T7 from a decorations_needed block."""
    if dn is None:
        return "—"
    if dn.get("message") and dn.get("decorations_needed") is None and not dn.get("saturated"):
        return dn["message"]
    if dn.get("saturated"):
        return f"not resolvable by this statistic at <= {dn['max_decorations']} decorations; P({dn['max_decorations']}) = {r(dn['prob_at_max_decorations'])}, best {r(dn['best_prob_on_grid'])} at D = {dn['best_decorations_on_grid']}" + ("; `order_reverses_at_depth`" if dn.get("order_reverses_at_depth") else "")
    cnt = dn["decorations_needed"]
    br = dn.get("decorations_needed_bracket")
    # spec:37: a simulated count is read as its bracket, so the bracket is printed even when it equals the count
    s = f"{cnt}" if br is None else f"{cnt} [{br[0]}, {br[1]}]"
    if dn.get("achieved_prob") is not None:
        s += f" (P = {r(dn['achieved_prob'])})"
    return s


def dn_prob(dn):
    if dn is None or dn.get("decorations_needed") is None and not dn.get("saturated"):
        return "—"
    if dn.get("saturated"):
        return f"P({dn['max_decorations']}) = {r(dn['prob_at_max_decorations'])}"
    return rv(dn.get("achieved_prob"))


def interval(bi, rule, f, status):
    if not bi or rule not in bi or bi[rule].get(f) is None:
        return f"no interval: `status {status}`"
    lo, hi = bi[rule][f]
    return f"[{r(lo)}, {r(hi)}]"


def section_rr(C):
    L = []
    w = L.append
    w("## Rank resolution (spec:41-92) — one block per admission policy, then T7 and T8")
    w("")
    w(f"Command of record, spec:45 verbatim: `{C.SPEC.line(45, '--B 10000')}`")
    w("")
    w(f"spec:47 verbatim: \"{C.SPEC.line(47, 'admission policy')}\"")
    w("")
    w(f"Input guards, spec:51 verbatim: \"{C.SPEC.line(51, 'Exit 3')}\"")
    w("")
    w(f"R7, spec:74 verbatim: \"{C.SPEC.line(74, 'R7')}\"")
    w("")
    ref = C.RR["all"] or next((C.RR[p] for p in POLICIES if C.RR[p]), None)
    if ref is None:
        w("not run: no rank-resolution file was found; the tables T1-T8 are not printed.")
        w("")
        return L
    w("Elective settings (spec:78-89), every slot blank; the draft value is the spec's column 3 and the file value is `settings.<key>` of the policy files (identical across them, asserted where present):")
    w("")
    w("| slot | setting | draft value (spec) | flag | file value |")
    w("|---|---|---|---|---|")
    fmap = {1: ("target_prob",), 2: ("level",), 5: ("cutoff_A",), 6: ("ridge_alpha",), 7: ("min_decorations",), 8: ("B", "seed")}
    C.RANK_DRAFT = {}
    for n in range(80, 90):
        cc = cells(C.SPEC.line(n, "[RANK-"))
        k = int(re.match(r"\[RANK-(\d+)", cc[0]).group(1))
        C.RANK_DRAFT[k] = cc[2]
        check(cc[0].endswith(": ______]"), f"spec:{n} slot is not blank")
        if k in fmap:
            vals = []
            for key in fmap[k]:
                fv = {json.dumps(C.RR[p]["settings"][key]) for p in POLICIES if C.RR[p]}
                vals.append(f"`{key}` " + " / ".join(sorted(fv)))
            fvs = "; ".join(vals)
        else:
            fvs = "applied at reading (no `settings` key)"
        w(f"| {cc[0]} | {cc[1]} | {cc[2]} | {cc[3]} | {fvs} |")
    w("")
    for p in POLICIES:
        if C.RR[p]:
            check(C.RR[p]["model"]["sha256_bytes"] == C.MODEL_PIN["mpa0"], f"rr {p}: model hash differs from docs/91:34")
    w(f"Model line: `model.filename` {ref['model']['filename']}, `model.sha256_bytes` {ref['model']['sha256_bytes']} (equal to `docs/91:34`, asserted).")
    w("")
    cov = ref["coverage"]
    ext_set = {s for s in C.MANIFEST_STEMS if s.startswith("mpa0_ext__")}
    if set(cov["missing"]) == ext_set:
        miss = f"{len(ext_set)} `mpa0_ext__` stems (exactly the CENSUS-3 set of `MANIFESTS.sha256`, asserted)"
    else:
        miss = ", ".join(f"`{s}`" for s in cov["missing"]) or "none"
    w(f"Coverage (`--admit all`; identical across the policy files, asserted): expected {len(cov['expected'])}, present {len(cov['present'])}, missing {len(cov['missing'])}, refused {len(cov['refused'])}, `unverified` {bl(cov['unverified'])}, `partial` {bl(cov['partial'])}; missing: {miss}.")
    w("")
    for p in POLICIES:
        if C.RR[p]:
            check(C.RR[p]["coverage"]["missing"] == cov["missing"] and C.RR[p]["coverage"]["present"] == cov["present"], 'input check failed: C.RR[p]["coverage"]["missing"] == cov["missing"] and C.RR[p]["coverage"]["present"] == cov["present"]')
    second_wave = any(s.startswith("mpa0_ext__") for s in cov["present"])
    for pol in POLICIES:
        L += rr_policy_block(C, pol, second_wave)
    L += rr_t7(C)
    L += rr_t8(C)
    return L


def rr_policy_block(C, pol, second_wave):
    L = []
    w = L.append
    d = C.RR[pol]
    w(f"### `--admit {pol}`")
    w("")
    if d is None:
        w(f"not run: no `{C.rr_names.get(pol, pol)}` under the rank-resolution directory.")
        w("")
        return L
    S = d["settings"]
    st = d["status"]
    deficient = st == "insufficient_decorations"
    w(f"`status {st}`; `settings.admit_definition`: \"{S['admit_definition']}\"; `B` {S['B']}, `seed` {S['seed']}, `level` {S['level']}, `target_prob` {S['target_prob']}, `min_decorations` {S['min_decorations']}, `stems` `{S['stems']}`, `reproduction_tolerance_V` {S['reproduction_tolerance_V']}; `n_site_rows` {d['n_site_rows']}; sha256_lf `{C.RR_HASH[pol]}`."
      + (" The two-pathway site set is the rule whose pathway-undefined exclusion is Proposed `[CENSUS-6 2026-09-__: ____]` (`docs/91:63`)." if pol == "two-pathway" else ""))
    if st == "partial":
        w(f"`coverage.missing` names {len(d['coverage']['missing'])} stems (the CENSUS-3 second wave); T1-T7 are printed on the present stems.")
    if deficient:
        defi = ", ".join(f"{x['formula']} ({x['n_decorations_usable']} usable)" for x in d["deficient_compositions"])
        w(f"`message`: \"{d['message']}\". Deficient against `settings.min_decorations` {S['min_decorations']} (RANK-7): {defi}. T3 and T4 are replaced by that message; T1, T2 (no intervals), the census orders, T5, T6 and T7 are printed.")
    w("")
    # T1
    cen = d["census"]
    n_missing = len(d["coverage"]["missing"])
    ok = all(cen[f]["n_decorations"] == cen[f]["declared_n_decorations"] and cen[f]["n_sites"] == cen[f]["declared_n_sites"] for f in C.ORDER) and n_missing == 0
    why = "observed = declared for every composition and no stem missing" if ok else f"{n_missing} stems missing in `coverage.missing`"
    w(f"**T1 census** (spec:55): coverage is complete when observed = declared for every composition and `coverage.missing` is empty — {'yes' if ok else 'no'} ({why}).")
    w("")
    w("| composition | decorations (usable) | sites (admitted) | declared decorations x sites | bootstrap support C(2D-1, D) |")
    w("|---|---|---|---|---|")
    for f in C.ORDER:
        c = cen[f]
        w(f"| {f} | {c['n_decorations']} ({c['n_decorations_usable']}) | {c['n_sites']} ({c['n_admitted']}) | {c['declared_n_decorations']} x {c['declared_n_sites']} | {c['bootstrap_support']} |")
    w("")
    # T2
    bi = d.get("bootstrap_intervals")
    iv_note = f"intervals at `settings.level` {S['level']}" if bi else f"no intervals: `status {st}`, values only"
    w(f"**T2 statistics** (spec:56, R7; {iv_note}; the reproduction verdict at `tolerance_V` {S['reproduction_tolerance_V']} equals the docs/93 (a) verdict for the gated six, asserted):")
    w("")
    w("| composition | banked rank | banked eta (V) | abs(census min − banked eta) (V) | reproduction | min [interval] | median [interval] | p10 [interval] | mean [interval] |")
    w("|---|---|---|---|---|---|---|---|---|")
    d93v = {}
    for n in range(35, 41):
        cc = cells(C.D93.line(n))
        d93v[cc[0]] = cc[1].strip("*")
    for f in C.ORDER:
        rp = d["reproduction"][f]
        check(rp["verdict"] == d93v[f], f"{pol}: reproduction verdict of {f} differs from docs/93:35-40")
        cellsv = []
        for rule in RR_RULES:
            v = d["statistics"][rule].get(f)
            cellsv.append("EXCLUDED (no admitted site)" if v is None else (f"{r(v)} {interval(bi, rule, f, st)}" if bi else r(v)))
        w(f"| {f} | {C.ORDER.index(f) + 1} | {r(rp['banked_eta_V'])} | {e(rp['abs_difference_V'])} | {rp['verdict']} | " + " | ".join(cellsv) + " |")
    w("")
    ords = []
    for rule in RR_RULES:
        o = d["census_orders"][rule]
        # docs/91:63: tau is reported only when all six have a value (the file's partial tau is not printed)
        tau = f"tau-a {o['kendall_tau_a_vs_banked']}" if o["complete"] else f"tau not reported (`complete: false`; {len(o['order'])} present, EXCLUDED {', '.join(o['excluded'])})"
        ords.append(f"{rule}: " + " < ".join(o["order"]) + f" ({tau})")
    w("Census orders per rule (`census_orders.<rule>`; tau printed only when `complete`, `docs/91:63`): " + "; ".join(ords) + ".")
    if second_wave:
        w("R7 / spec:33: `mpa0_ext__` stems are present, so the `min` statistic above is the rank statistic of the second wave, not a re-screen value; the reproduction column uses the banked seeds only.")
    w("")
    if deficient:
        w(f"**T3 / T4**: not reported — `message`: \"{d['message']}\".")
        w("")
    else:
        L += rr_t3(C, d)
        L += rr_t4(C, d)
    L += rr_t5(C, d)
    L += rr_t6(C, d)
    return L


def rr_t3(C, d):
    L = []
    w = L.append
    rp = d.get("rank_probability")
    w(f"**T3 rank matrix** (spec:57; STABLE iff `stable.<f>.stable`, P(banked rank) >= `target_prob` {d['settings']['target_prob']}):")
    w("")
    for rule in RR_RULES:
        x = (rp or {}).get(rule)
        if not x:
            w(f"- {rule}: not reported: `{d.get('message')}`")
            continue
        K = len(x["formulas"])
        w(f"*{rule}* (`n_replicates` {x['n_replicates']}, `n_dropped` {x['n_dropped']}):")
        w("")
        w("| composition | " + " | ".join(f"r{k}" for k in range(1, K + 1)) + " | `expected_rank` (0-based in the file: rank 1 = 0) | banked rank (1-based) | P(banked rank) | label |")
        w("|---|" + "---|" * (K + 4))
        for f in C.ORDER:
            if f not in x["formulas"]:
                w(f"| {f} | EXCLUDED |" + " |" * (K + 3))
                continue
            i = x["formulas"].index(f)
            stb = x["stable"][f]
            w(f"| {f} | " + " | ".join(r(v) for v in x["rank_matrix"][i]) + f" | {r(x['expected_rank'][i])} | {stb['banked_rank']} | {r(stb['p_banked_rank'])} | {'STABLE' if stb['stable'] else 'not stable'} |")
        w("")
    return L


def rr_t4(C, d):
    L = []
    w = L.append
    ag = d.get("adjacent_gaps") or {}
    w("**T4 adjacent gaps** (spec:58, R1-R3):")
    w("")
    w("| pair | rule | observed gap (V) | P(order) | gap interval (V) | verdict | decorations needed [MC bracket] |")
    w("|---|---|---|---|---|---|---|")
    spread = []
    for rule in RR_RULES:
        for g in ag.get(rule, []):
            gi = g["gap_interval_V"]
            w(f"| {g['better']} < {g['worse']} | {rule} | {r(g['gap_point_V'])} | {r(g['p_order_preserved'])} | [{r(gi[0])}, {r(gi[1])}] | {g['verdict']} | {dn_cell(g.get('decorations_needed'))} |")
            if g.get("spread_decided"):
                spread.append(f"{g['better']} < {g['worse']} under {rule} (`near_extreme` {bl(g['decorations_needed'].get('near_extreme'))})")
    w("")
    rb, ib, nb = d["resolved_boundaries"], d["inverted_boundaries"], d["n_boundaries"]
    min_adm = min(d["census"][f]["n_admitted"] for f in C.ORDER)
    floor = C.RANK_DRAFT[10]
    p10_label = f", labelled near-extreme (`n_admitted` minimum {min_adm} < the RANK-10 floor {floor})" if min_adm < float(floor) else ""
    w(f"R1 (spec:68 verbatim: \"{C.SPEC.line(68, 'R1')}\"): resolving {rb['mean']} of {nb} boundaries under the mean rule, {rb['median']} under the median and {rb['min']} under the min rule; the min count is descriptive, the mean and median counts are the calibrated ones, and the p10 count is {rb['p10']}{p10_label}.")
    inv = []
    for rule in RR_RULES:
        pairs = [f"{g['better']} < {g['worse']}" for g in ag.get(rule, []) if g.get("inverted")]
        inv.append(f"{rule} {ib[rule]}" + (f" ({', '.join(pairs)})" if pairs else ""))
    w("R2 (spec:69): INVERTED boundaries — " + "; ".join(inv) + ".")
    tail = re.search(r"lower bounds on the depth under any heavier left tail", C.SPEC.line(70, "R3")).group(0)
    w(f"R3 (spec:70): SPREAD-DECIDED — {'; '.join(spread) if spread else 'none'}; every count above assumes normal i.i.d. sites and the figures are \"{tail}\" (spec:70).")
    w("")
    return L


def rr_t5(C, d):
    L = []
    w = L.append
    vc = d["variance_components"]
    band = float(C.RANK_DRAFT[3])
    w("**T5 variance components** (spec:59, R4):")
    w("")
    w("| composition | sites | decorations | site sd (population) | within sd | between sd | ICC | status |")
    w("|---|---|---|---|---|---|---|---|")
    hi = []
    for f in C.ORDER:
        x = vc[f]
        w(f"| {f} | {x['n_sites']} | {x['n_decorations']} | {rv(x['site_sd_population'])} | {rv(x['within_sd'])} | {rv(x['between_sd'])} | {rv(x['icc'])} | {x['status']} |")
        if x["icc"] is not None and x["icc"] > band:
            hi.append(f"{f} ({r(x['icc'])})")
    w("")
    w(f"R4 (spec:71; ICC band {band}, the RANK-3 draft): " + (f"{', '.join(hi)} — i.i.d. depth understated; decorations-needed figures for its pairs are lower bounds." if hi else "no composition exceeds the band."))
    w("")
    return L


def rr_t6(C, d):
    L = []
    w = L.append
    S = d["settings"]
    fits = d["ridge"]["fits"]
    w(f"**T6 ridge** (spec:60, R5; `cutoff_A` {S['cutoff_A']}, `ridge_alpha` {S['ridge_alpha']}; `n_sites_with_environment` {d['ridge']['n_sites_with_environment']}):")
    w("")
    w("| target | sites | status | R² in-sample | R² LOO | sigma in-sample | sigma LOO |")
    w("|---|---|---|---|---|---|---|")
    for t in ("eta", "dG_OH", "dG_O", "dG_OOH"):
        x = fits[t]
        if x["status"] != "ok":
            w(f"| {t} | {x['n_sites']} | not reported ({x['status']}: {x.get('message')}) | | | | |")
        else:
            w(f"| {t} | {x['n_sites']} | {x['status']} (`meaningful` {bl(x['meaningful'])}, `min_sites` {x['min_sites']}) | {r(x['r2_in_sample'])} | {r(x['r2_loo'])} | {r(x['sigma_in_sample'])} | {r(x['sigma_loo'])} |")
    w("")
    eta = fits["eta"]
    allv = np.array([x["eta"] for x in d["site_rows"]], dtype=float)
    adm = np.array([x["eta"] for x in d["site_rows"] if x["admitted"]], dtype=float)
    pooled = float(np.std(allv, ddof=0)) if allv.size else None
    pooled_adm = float(np.std(adm, ddof=0)) if adm.size else None
    if eta["status"] == "ok" and pooled is not None:
        # one comparison on one population: the ridge is fitted over every site row in every policy file
        check(allv.size == eta["n_sites"], f"site_rows ({allv.size}) differ from the ridge eta fit's n_sites ({eta['n_sites']})")
        verdict_ = "nearest-neighbour composition does not explain the site spread" if eta["sigma_loo"] >= pooled else "sigma_LOO lies below the pooled site sd"
        w(f"R5 (spec:72): `sigma_loo` (eta) {r(eta['sigma_loo'])} V against the pooled site sd {pooled!r} V (population sd over every `site_rows[].eta`, {allv.size} sites — the same {eta['n_sites']} sites the ridge is fitted on, so the comparison is on one population and identical in every policy block; computed by this script — post-hoc arithmetic on file values): {verdict_}; the fit is descriptive and no R² threshold is a success criterion. Beside it, post-hoc and not the R5 comparison: the population sd over the {adm.size} sites this policy admits is {pooled_adm!r} V.")
    else:
        w(f"R5: not reported (eta fit status `{eta['status']}`).")
    w("")
    return L


def rr_t7(C):
    L = []
    w = L.append
    ref = C.RR["all"] or next(C.RR[p] for p in POLICIES if C.RR[p])
    for p in POLICIES:
        if C.RR[p]:
            check(C.RR[p]["banked_reference"] == ref["banked_reference"], f"banked_reference differs in {p}")
    br = ref["banked_reference"]
    w(f"### T7 banked reference (spec:61) — from `banked_reference.pairs[]` (identical in every policy file, asserted; `target_prob` {br['target_prob']}, `n_sites_per_decoration` {br['n_sites_per_decoration']}; columns: `pairs[].{{better, worse, sigma_a, sigma_b}}`, \"own\" cells from `pairs[].own_gap.<rule>.{{gap_V, gap_source, decorations_needed, decorations_needed_bracket, achieved_prob}}`, \"at the banked min gap\" cells from `pairs[].hypothetical_min_gap.<rule>.{{...}}` with `log10_n_sites_asymptotic` where `equal_spreads`)")
    w("")
    w("| pair | sigma a / b | rule | own banked gap (V, source) | decorations on own gap [bracket] | P | decorations at the banked min gap [bracket] | P | log10 N Gumbel (sa = sb only) |")
    w("|---|---|---|---|---|---|---|---|---|")
    for pr in br["pairs"]:
        for rule in RR_RULES:
            og = pr["own_gap"][rule]
            hg = pr["hypothetical_min_gap"][rule]
            if og.get("gap_V") is None:
                own = f"— ({og.get('gap_source')})"
                own_cell = og.get("message", "—")
                own_p = "—"
            else:
                own = f"{r(og['gap_V'])} ({og.get('gap_source')})"
                own_cell = dn_cell(og)
                own_p = dn_prob(og)
            gum = r(hg["log10_n_sites_asymptotic"]) if hg.get("equal_spreads") else "—"
            w(f"| {pr['better']} < {pr['worse']} | {r(pr['sigma_a'])} / {r(pr['sigma_b'])} | {rule} | {own} | {own_cell} | {own_p} | {dn_cell(hg)} | {dn_prob(hg)} | {gum} |")
    w("")
    cmpx = []
    for n, pr in zip(range(103, 108), br["pairs"]):
        cc = cells(C.SPEC.line(n))
        check(cc[0] == f"{pr['better']} < {pr['worse']}", f"spec:{n} pair differs from banked_reference")
        spec_cell = cc[3]
        og = pr["own_gap"]["min"]
        m = re.match(r"^(\d+) \[(\d+), (\d+)\]", spec_cell)
        if m:
            sc, slo, shi = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if og.get("saturated") or og.get("decorations_needed") is None:
                res = "differs (file saturated)"
            elif og["decorations_needed"] == sc:
                res = "equal"
            elif slo <= og["decorations_needed"] <= shi or (og["decorations_needed_bracket"][0] <= sc <= og["decorations_needed_bracket"][1]):
                res = f"within bracket (file {og['decorations_needed']} [{og['decorations_needed_bracket'][0]}, {og['decorations_needed_bracket'][1]}])"
            else:
                res = f"differs (file {og['decorations_needed']} [{og['decorations_needed_bracket'][0]}, {og['decorations_needed_bracket'][1]}])"
        else:
            m = re.search(r"sat\., P\(10000\) = ([\d.]+), best ([\d.]+) at D = (\d+)", spec_cell)
            check(m, f"spec:{n} min cell has an unexpected form")
            if not og.get("saturated"):
                res = f"differs (file count {og.get('decorations_needed')})"
            else:
                same = ("%.3f" % og["prob_at_max_decorations"] == m.group(1)) and ("%.3f" % og["best_prob_on_grid"] == m.group(2)) and (str(og["best_decorations_on_grid"]) == m.group(3))
                res = f"equal at the spec's printed precision (file P({og['max_decorations']}) {r(og['prob_at_max_decorations'])}, best {r(og['best_prob_on_grid'])} at D = {og['best_decorations_on_grid']})" if same else f"differs (file P({og['max_decorations']}) {'%.3f' % og['prob_at_max_decorations']}, best {'%.3f' % og['best_prob_on_grid']} at D = {og['best_decorations_on_grid']})"
        cmpx.append(f"spec:{n} \"{spec_cell}\" — {res}")
    w(f"These rows reproduce spec Tables A / A' (spec:101-117) at `settings.seed` {ref['settings']['seed']}; spec:171 notes that simulated counts move within their brackets between random streams. The five min-rule cells against spec:103-107, cell by cell (\"equal\" for a count is equality of the integer count; for a saturated cell it is equality at the three decimals the spec prints): " + "; ".join(cmpx) + ".")
    w("")
    return L


def rr_t8(C):
    L = []
    w = L.append
    cmp_ = C.RR["compare"]
    w("### T8 comparison (spec:62, R6) — `--compare`")
    w("")
    if cmp_ is None:
        w(f"not run: no `{C.rr_names.get('compare', 'compare')}` under the rank-resolution directory.")
        w("")
        return L
    pols = cmp_["policies"]
    ins = []
    absent = []
    for x in cmp_["inputs"]:
        own = C.RR_HASH.get(x["policy"])
        if own is None:
            absent.append(x["policy"])
            ins.append(f"{x['policy']} `{x['status']}` `{x['sha256_lf'][:12]}…` — input `{C.rr_names.get(x['policy'], x['policy'])}` not present under the rank-resolution directory, hash not checked")
            continue
        check(own == x["sha256_lf"], f"compare input {x['policy']}: sha256_lf differs from the rr file read here")
        ins.append(f"{x['policy']} `{x['status']}` `{x['sha256_lf'][:12]}…`")
    w(f"`policies`: {', '.join(pols)}; `target_prob` {cmp_['target_prob']}; `inputs[]` (each `sha256_lf` equals this script's own hash of that file where the file is present, asserted{'; not present: ' + ', '.join(absent) if absent else ''}): " + "; ".join(ins) + ".")
    w("")
    w("| pair | rule | " + " | ".join(f"{p}: verdict (P)" for p in pols) + " | R6 |")
    w("|---|---|" + "---|" * (len(pols) + 1))
    any_absent = False
    for b in cmp_["boundaries"]:
        cc = []
        for p in pols:
            v = b["verdicts"][p]
            any_absent = any_absent or v == "ABSENT"
            cc.append(f"{v} ({rv(b['p_order'][p])})")
        w(f"| {b['better']} < {b['worse']} | {b['rule']} | " + " | ".join(cc) + f" | {'POLICY-DEPENDENT' if b['policy_dependent'] else '-'} |")
    w("")
    w(f"Policy-dependent boundaries: `n_policy_dependent` {cmp_['n_policy_dependent']} of {len(cmp_['boundaries'])}.")
    if any_absent:
        defi = "; ".join(f"{p}: " + (", ".join(f"{x['formula']} ({x['n_decorations_usable']})" for x in C.RR[p]["deficient_compositions"]) if C.RR.get(p) and C.RR[p].get("deficient_compositions") else "none") for p in pols)
        w(f"Caveat (post-hoc reading of a pre-stated label): `ABSENT` marks a policy whose readout ended `insufficient_decorations` (exit 3; `deficient_compositions` {defi}) and carries no `adjacent_gaps`; `compare_readouts` (`rank_resolution_readout.py:483-488`) sets `policy_dependent` from the set of verdict prefixes including ABSENT, so under partial data every boundary reads POLICY-DEPENDENT by construction; no R6 statement is made until every policy file is `complete`.")
    else:
        w(f"R6 (spec:73 verbatim: \"{C.SPEC.line(73, 'R6')}\"): stated as written from the table above.")
    w("")
    return L


# ----------------------------------------------------------------------------- section 9: what changed
def section_changed(C):
    L = []
    w = L.append
    E = cost_numbers(C)
    P = planning(C)
    w("## What changed and what did not; named risks (`docs/91:77-87`)")
    w("")
    w("- **Nothing registered moved.** No line of docs/43 is added or edited, no THRESHOLD is registered, no prediction is scored, no S8 or melt decision is taken, `results/r4_melt_list.json` is untouched, nothing enters the body-figure ledger (`docs/91:90`). `results/r4_validate.json`, `r4_screen_box.json` and `r4_gated.json` are read from their tracked LF copies and not rewritten (`docs/91:73`).")
    what = {1: "reproduction bars", 2: "O-O bands", 3: "hydrogen window", 4: "per-atom reconstruction bar", 5: "label priority", 6: "pathway-undefined exclusion", 7: "fragment (ZPE − TS)", 8: "the elective MH-1 leg", 9: "the elective UMA-S-1p2 leg"}
    w("- **Every entrant slot remains blank** (each slot string read from its docs/91 line): " + "; ".join(f"{slot(C, k)} {what[k]} (`:{C.SLOT[k][1]}`)" for k in range(1, 10)) + "; and the rank-resolution slots " + ", ".join(f"`[RANK-{k} " + cells(C.SPEC.line(79 + k))[0][len(f"[RANK-{k} "):] + "`" for k in range(1, 11)) + " (spec:80-89).")
    reasons = ", ".join(f"{n} `{k}`" for k, n in sorted(C.REASONS.items()))
    w(f"- **Pending.** {len(C.MISSING)} manifests listed missing ({reasons}). " + " ".join(arm_pending(C, t) for t in ENSEMBLE) + f" {c3_pending(C)} CENSUS-3 also gates the rank-resolution second wave (`coverage.missing`). MH-1 and UMA-S-1p2 are not run (`docs/91:40`, `:42`).")
    # risks
    threads_bad = [s for s in C.STEMS if C.RES[s]["threads"] != 2]
    label_bad = [s for s in C.STEMS if C.MAN[s]["model"]["historical_label"] != "medium-mpa-0"]
    check(not threads_bad, f"threads != 2 on {threads_bad}")
    check(not label_bad, f"historical_label differs on {label_bad}")
    with_log = {n[:-4] for n in C.LOG_NAMES if n.endswith(".log") and n != "runner.log"}
    with_result = {n[:-len("_result.json")] for n in C.RESULT_NAMES if n.endswith("_result.json")}
    lost = sorted(s for s in with_log if s not in with_result and s not in C.LOCKS)
    fnames = ", ".join(f"{t} `{C.MODEL_FILE[t]}`" for t in TAGS if t in C.MODEL_FILE) + "".join(f", {t} pending" for t in TAGS if t not in C.MODEL_FILE)
    unc_win = [f"{tag} {f}" for (tag, f), wv in C.WIN.items() if int(wv["unconverged_states"]) > 0]
    pm = C.kr["convergence"]["per_model"]
    r8 = []
    for ck in ("omat0", "mp0", "matpes"):
        g = E["groups"][ck]
        if g["n"] == 0:
            r8.append(f"{ck} pending")
            continue
        ratio = f"{g['mean'] / E['c1_mean']:.2f}"
        note = ""
        if ck == "omat0":
            note = f" (`docs/93:266` reads {C.D93_OMAT_RATIO}x on {'the same' if g['n'] == len(C.GATED) else 'its'} six: {'equal' if ratio == C.D93_OMAT_RATIO else 'DIFFERS'} at two decimals)"
        r8.append(f"{ck} {ratio}x{note}")
    w(f"- **Named risks, each decided from a file value.** Risk 1 (contention): wall {E['wall'] / 3600:.2f} h over the landed window against the planning walls of section (e); the events are `docs/93:170-171`. Risk 2 (weight identity): the CENSUS-1 verdicts are those of `docs/93:21` and are unchanged (T2 asserts them); `docs/91:80`: \"The three other checkpoints carry no historical claim at all\". Risk 3 (thread count): every landed result records `environment.threads` 2 (asserted over {len(C.STEMS)} results). Risk 4 (site enumeration): a standing caveat, not an event. Risk 5 (kill granularity): stems with a log and neither a result file nor a live lock — {', '.join(lost) if lost else 'none'} (from the `logs/` and `results/` directory listings). Risk 6: `manifest.model.historical_label` reads `medium-mpa-0` on every landed manifest (asserted) while `model.filename` differs per tag: {fnames}. Risk 7 (BFGS cap): unconverged sites per model " + ", ".join(f"{t} {pm[t]['n_unconverged_sites']} of {pm[t]['n_sites']}" for t in TAGS if t in pm) + f" (Table C3); a model's min-site eta on an unconverged site: {', '.join(unc_win) if unc_win else 'none'}. Risk 8 (ensemble cost): per-checkpoint realised mean against the CENSUS-1 mean {E['c1_mean']:.1f} s — " + ", ".join(r8) + f" (the MPA-0 planning band {r(P['per12'][0])}-{r(P['per12'][1])} s, `docs/91:67`).")
    w("- **Post-hoc readings in this file, each changing no verdict:** per-model H_TRANSFERRED fractions and per-model INTEGRITY on non-CENSUS-1 sites (b); the non-mpa0 winner columns of B2 and the non-mpa0 entries of the unconverged-min-site sentence of (c); per-model winner persistence (C4) and the per-model tau; section (d) under the other models; the log-stamp wall / throughput arithmetic and the launch-order reading of (e); the sd placement sentence of (f); the ABSENT / POLICY-DEPENDENT caveat of T8; the pooled-sd arithmetic of R5 and the admitted-subset sd beside it.")
    w("")
    return L


# ----------------------------------------------------------------------------- section 10: hashes
def section_hashes(C):
    L = []
    w = L.append
    w("## Hashes — sha256 of the LF-normalised bytes (CRLF → LF before hashing, the repository's `sha256_lf`)")
    w("")
    w(f"Readout files carry `generated: {C.GEN}`; every result hash equals `manifests_read[stem].result_sha256_lf` (asserted); the twelve `mpa0__` and the endmember hashes equal `docs/93:228-240` (asserted); `o2_records.json` equals `docs/94:131` (asserted when supplied); `MANIFESTS.sha256` equals the `docs/91:92` pin (asserted). Paths are relative to `results/site_census_2026-09-06/` for census files and to the rank-resolution directory for the `rank_resolution` files.")
    w("")
    w("```")
    for stem in C.STEMS:
        w(f"{C.RES[stem]['hash']}  results/{stem}_result.json")
    for n in ("per_site.csv", "per_site.json", "reproduction.json", "ranking.json", "distribution.json"):
        w(f"{sha256_lf(C.readout / n)}  readout/{n}")
    if C.O2_HASH:
        w(f"{C.O2_HASH}  o2_fragment/o2_records.json")
    w(f"{C.MANIFESTS_HASH}  MANIFESTS.sha256")
    for pol in list(POLICIES) + ["compare"]:
        if C.RR_HASH.get(pol):
            w(f"{C.RR_HASH[pol]}  {C.rr_names[pol]}")
    w("```")
    w("")
    impls = {json.dumps(C.RR[p]["implementation_sha256_lf"], sort_keys=True) for p in POLICIES if C.RR[p]}
    check(len(impls) <= 1, "implementation_sha256_lf differs across the rank-resolution files")
    if impls:
        imp = json.loads(next(iter(impls)))
        w("Implementation hashes the rank-resolution readouts record (`implementation_sha256_lf`, identical across the policy files, asserted): " + "; ".join(f"`{k}` {v}" for k, v in imp.items()) + ".")
    else:
        w("Implementation hashes of the rank-resolution readouts: not run.")
    w("")
    w("The ten `manifest.implementation_sha256_lf` keys (identical across every landed result, asserted): " + "; ".join(f"`{k}` {v}" for k, v in C.IMPL.items()) + ".")
    w("")
    pins = {}
    for n, rel in ((207, "src/hea_oer/site_integrity.py"), (212, "src/scripts/site_census_readout.py")):
        line = C.D91.line(n, rel)
        pins[rel] = re.match(HEX64, line).group(0)
    cmp_ = []
    for rel, pin in pins.items():
        on_disk = sha256_lf(ROOT / rel)
        cmp_.append(f"`{rel}` on disk {on_disk} against the `docs/91:{207 if 'integrity' in rel else 212}` pin {pin}: {'equal' if on_disk == pin else 'NOT EQUAL'}")
    w("On-disk scorer hashes against the docs/91 pins (the pin exists to make post-hoc change visible, `docs/91:204`; no edit is made): " + "; ".join(cmp_) + ".")
    w("")
    w("Paths are relative to `results/site_census_2026-09-06/`, which is gitignored (`.gitignore:14`); the manifests and `MANIFESTS.sha256` are in the boundary commit (`docs/91:5-14`), the results and readout are not (`docs/93:248`).")
    return L


# ----------------------------------------------------------------------------- main
def emit(C):
    L = []
    L += banner(C)
    L += verdict(C)
    L += section_b(C)
    L += section_c(C)
    L += section_c_prime(C)
    L += section_c_double_prime(C)
    L += section_d(C)
    L += section_e(C)
    L += section_f(C)
    L += section_rr(C)
    L += section_changed(C)
    L += section_hashes(C)
    text = "\n".join(ln.rstrip() for ln in L) + "\n"
    check(not re.search(r"\[CENSUS-\d 2026-09-\d\d", text), "a CENSUS slot reads filled")
    for m in re.finditer(r"\[RANK-\d+ [^\]]*\]", text):
        check(m.group(0).endswith(": ______]"), f"a RANK slot reads filled: {m.group(0)}")
    check("\r" not in text, 'input check failed: "\\r" not in text')
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--census-dir", default=str(ROOT / "results" / "site_census_2026-09-06"))
    ap.add_argument("--readout-dir", default=None, help="default <census-dir>/readout")
    ap.add_argument("--rr-dir", default=None, help="directory holding rank_resolution*.json; default <readout-dir>")
    ap.add_argument("--rr-names", default="all=rank_resolution.json,no-desorbed=rank_resolution_no-desorbed.json,intact=rank_resolution_intact.json,adsorbate-intact=rank_resolution_adsorbate-intact.json,two-pathway=rank_resolution_two-pathway.json,compare=rank_resolution_compare.json")
    ap.add_argument("--gated", default=str(ROOT / "results" / "ranking_adequacy_2026-09-06" / "inputs" / "r4_gated.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--title-date", default=None, help="YYYY-MM-DD in the heading; default the date of ranking.json generated")
    ap.add_argument("--docs91", default=str(ROOT / "docs" / "91-prereg-site-integrity-census-2026-09-06.md"))
    ap.add_argument("--spec", default=str(ROOT / "docs" / "research" / "2026-09-06-rank-resolution-spec.md"))
    ap.add_argument("--docs93", default=str(ROOT / "docs" / "93-census-1-readout-2026-09-07.md"))
    ap.add_argument("--docs94", default=str(ROOT / "docs" / "94-census-1b-readout-2026-09-07.md"))
    args = ap.parse_args(argv)
    if args.readout_dir is None:
        args.readout_dir = str(Path(args.census_dir) / "readout")
    if args.rr_dir is None:
        args.rr_dir = args.readout_dir
    C = build(args)
    text = emit(C)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(args.out, text.count("\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
