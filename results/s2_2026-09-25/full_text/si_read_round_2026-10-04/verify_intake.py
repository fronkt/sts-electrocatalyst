"""Offline checks of the 2026-10-04 SI-read intake (no network, no verdicts).  Exit code 1 and a list of problems on any failure.

  python verify_intake.py
Checks: package set; source pins against both recovery manifests and the intake manifest; reading copies (hash, SI-file headers,
page / paragraph / block markers); visual files exist; pass inputs (fields, paths, plan hashes, budget, identical content in the
two passes, S11392 absent); the instructions pin; no OpenAlex key text in any file of the three new directories; and that no
existing tracked file changed.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
FT = HERE.parent
REPO = FT.parents[2]
PRIOR, EXT = FT / "public_si_recovery_2026-10-04", FT / "public_si_recovery_2026-10-04_ext"
problems, notes = [], []


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def bad(msg):
    problems.append(msg)


man = json.loads((HERE / "intake_manifest.json").read_text(encoding="utf-8"))
pk = {p["screen_id"]: p for p in man["packages"]}
prior = {p["screen_id"]: p for p in json.loads((PRIOR / "recovered_manifest.json").read_text(encoding="utf-8"))["packages"]}
ext = {p["screen_id"]: p for p in json.loads((EXT / "recovered_manifest.json").read_text(encoding="utf-8"))["packages"]}
expected = (set(prior) - {"S11392"}) | set(ext)
if set(pk) != expected:
    bad("package set differs: extra %s missing %s" % (sorted(set(pk) - expected), sorted(expected - set(pk))))
if len(expected) != 22:
    bad("expected 22 packages, have %d" % len(expected))
if "S11392" in pk or "S22941" in pk:
    bad("S11392 / S22941 must not be in the intake")

# 1. sources and reading copies
for sid, p in sorted(pk.items()):
    src = (prior.get(sid) or ext.get(sid))
    for f, g in zip(p["source_files"], src["files"]):
        path = FT / g["local_path"]
        if not path.exists() or sha(path) != g["sha256"] or path.stat().st_size != g["bytes"] or f["sha256"] != g["sha256"]:
            bad("%s: source pin mismatch %s" % (sid, g["local_path"]))
    rc = FT / p["reading_copy"]["path"]
    if not rc.exists() or sha(rc) != p["reading_copy"]["sha256"]:
        bad("%s: reading copy missing or hash differs" % sid)
        continue
    t = rc.read_text(encoding="utf-8")
    heads = re.findall(r"^\[SI file ([^:\]]+): ", t, re.M)
    if len(heads) != len(p["source_files"]):
        bad("%s: %d SI-file headers for %d files" % (sid, len(heads), len(p["source_files"])))
    for f in p["source_files"]:
        tag = f["tag"]
        if tag not in heads:
            bad("%s: header for %s missing" % (sid, tag))
        if f["kind"] == "pdf":
            pages = [int(x) for x in re.findall(r"^\[%s p\. (\d+)\]" % re.escape(tag), t, re.M)]
            if pages != list(range(1, f["pages"] + 1)):
                bad("%s: page markers of %s are not 1..%d" % (sid, tag, f["pages"]))
        elif f["kind"] == "docx" and not f.get("duplicate_of"):
            if not re.search(r"^\[%s paragraph \d+\]" % re.escape(tag), t, re.M):
                bad("%s: no paragraph markers for %s" % (sid, tag))
            z = zipfile.ZipFile(FT / f["file"])
            n_media = len([n for n in z.namelist() if n.startswith("word/media/") and not n.endswith("/")])
            if n_media != f.get("media_items"):
                bad("%s: media count %s != %s in the zip" % (sid, f.get("media_items"), n_media))
        elif f["kind"] == "doc":
            if not re.search(r"^\[%s block \d+\]" % re.escape(tag), t, re.M):
                bad("%s: no block markers for %s" % (sid, tag))
    if re.search(r"\[sym [A-Za-z]+ [0-9A-F]+\]", t):
        notes.append("%s: reading copy keeps unmapped symbol placeholder(s) %s" % (sid, sorted(set(re.findall(r"\[sym [A-Za-z]+ [0-9A-F]+\]", t)))))
    for v in p["visual_review"]:
        for path in v.get("visual", []) if isinstance(v.get("visual"), list) else []:
            if not (FT / path).exists() or (FT / path).stat().st_size == 0:
                bad("%s: visual file missing %s" % (sid, path))
    mt = FT / p["main_text"]["path"]
    if sha(mt) != p["main_text"]["sha256"]:
        bad("%s: main text changed since intake" % sid)

# 2. pass inputs
if sha(FT / "eligibility_instructions.md") != man["instructions"]["sha256"]:
    bad("eligibility_instructions.md changed")
REQ = ("screen_id", "doi", "text", "si_text", "si_complete", "si_files", "facts")
seen = {"1": [], "2": []}
plans = {}
for n in ("1", "2"):
    plan = json.loads((HERE / ("pass_" + n) / "plan.json").read_text(encoding="utf-8"))
    plans[n] = plan
    for name, b in plan["batches"].items():
        path = HERE / ("pass_" + n) / "batches" / (name + ".in.jsonl")
        if sha(path) != b["sha256"]:
            bad("%s: plan hash differs" % name)
        rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        if [r["screen_id"] for r in rows] != b["records"]:
            bad("%s: records differ from plan" % name)
        if len(rows) > plan["max_per_batch"]:
            bad("%s: %d papers exceed the cap" % (name, len(rows)))
        size = sum(r["chars"] + r["si_chars"] for r in rows)
        if size != b["chars"] or (size > plan["budget_chars"] and len(rows) > 1):
            bad("%s: size %d vs plan %d / budget" % (name, size, b["chars"]))
        for r in rows:
            seen[n].append(r["screen_id"])
            for k in REQ:
                if k not in r:
                    bad("%s %s: field %s missing" % (name, r["screen_id"], k))
            if r["text"] != "text/%s.txt" % r["screen_id"] or not (FT / r["text"]).exists():
                bad("%s %s: main text path" % (name, r["screen_id"]))
            if not r["si_text"] or not (FT / r["si_text"]).exists():
                bad("%s %s: si_text path" % (name, r["screen_id"]))
            if r["screen_id"] == "S11392":
                bad("S11392 present in %s" % name)
            if len((FT / r["text"]).read_text(encoding="utf-8")) != r["chars"] or len((FT / r["si_text"]).read_text(encoding="utf-8")) != r["si_chars"]:
                bad("%s %s: chars/si_chars do not match the files" % (name, r["screen_id"]))
            if not isinstance(r["si_complete"], bool) or not isinstance(r["facts"], list):
                bad("%s %s: field types" % (name, r["screen_id"]))
            for fn in r["si_files"]:
                if not any(fn == f["file"].rsplit("/", 1)[-1] for f in pk[r["screen_id"]]["source_files"]):
                    bad("%s %s: si_files name %s not in the package" % (name, r["screen_id"], fn))
    if sorted(seen[n]) != sorted(pk) or len(set(seen[n])) != len(seen[n]):
        bad("pass %s does not cover every package exactly once" % n)
for key in plans["1"]["batches"]:
    k2 = key.replace("SI1_", "SI2_", 1)
    a = (HERE / "pass_1" / "batches" / (key + ".in.jsonl")).read_bytes()
    b = (HERE / "pass_2" / "batches" / (k2 + ".in.jsonl")).read_bytes()
    if a != b:
        bad("pass 1 and pass 2 differ for %s" % key)
if set(k.replace("SI1_", "SI2_", 1) for k in plans["1"]["batches"]) != set(plans["2"]["batches"]):
    bad("batch sets differ between passes")

# 3. secrets
key_path = pathlib.Path.home() / ".config" / "openalex" / "api_key"
if key_path.exists():
    key = key_path.read_text().strip()
    hit = []
    for base in (HERE, EXT, PRIOR):
        for f in base.rglob("*"):
            if f.is_file() and f.stat().st_size < 20_000_000 and f.suffix.lower() in (".json", ".jsonl", ".txt", ".md", ".py", ".out", ".log", ".csv", ".html", ".ps1"):
                try:
                    if key.encode() in f.read_bytes():
                        hit.append(str(f))
                except OSError:
                    pass
    if hit:
        bad("OpenAlex key text found in %d file(s) (paths only): %s" % (len(hit), hit[:5]))

# 4. no tracked file changed
st = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True, creationflags=0x08000000).stdout.splitlines()
changed = [l for l in st if not l.startswith("??")]
if changed:
    bad("tracked files changed: %s" % changed[:5])

print("packages", len(pk), "| pass 1 batches", len(plans["1"]["batches"]), "| pass 2 batches", len(plans["2"]["batches"]))
for n_ in notes:
    print("note:", n_)
if problems:
    print("PROBLEMS:")
    for p_ in problems:
        print(" -", p_)
    sys.exit(1)
print("all checks passed")
