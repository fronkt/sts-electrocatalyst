"""Full-text eligibility screening: text extraction, batching, validation, collection.

  python ft_screen.py extract              extract text for every retrieved file -> text/<sid>.txt, texts.csv
  python ft_screen.py prepare --pass 1     batch the extracted texts (char budget per batch, seeded order per pass)
  python ft_screen.py status  --pass 1     list batches without a valid output
  python ft_screen.py collect --pass 1     validate all outputs -> pass_<n>.jsonl + collection.json

Texts: PyMuPDF for PDFs, tag-stripped <body> for Europe PMC XML.  The reference list is cut when a
References/Bibliography heading appears in the last 45% of the text (the cut position is recorded).
A text under 4,000 characters is flagged text_short (likely a landing/abstract page).  Batches carry
only record ids and text paths; screeners read the text files themselves.  Pass 1 and pass 2 use
different seeds, so batch membership and order differ.  Nothing here decides eligibility.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import pathlib
import random
import re

HERE = pathlib.Path(__file__).resolve().parent
SEEDS = {"1": 20260926, "2": 62906202}
BUDGET = 480_000  # characters of text per batch (about 120k tokens); batches before 2026-09-25 21:00Z used 320k
MAX_PER_BATCH = 10
DISP = {"ELIGIBLE", "EXCLUDE", "NEEDS_SI", "UNRESOLVED"}
RESUME = re.compile(r"^\s*(supporting information|supplementary (information|materials?|data|note|figures?|methods)|electronic supplementary|"
                    r"appendix\b|chapter\s+\d+|\d+\s+chapter)\b.*$", re.I | re.M)
REF = re.compile(r"^\s*(references|references and notes|bibliography|literature cited)\s*$", re.I | re.M)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def extract():
    import fitz
    (HERE / "text").mkdir(exist_ok=True)
    rows = []
    for f in sorted((HERE / "files").iterdir()):
        sid, out = f.stem, HERE / "text" / (f.stem + ".txt")
        try:
            if f.suffix == ".pdf":
                doc = fitz.open(f)
                t = "\n".join(p.get_text() for p in doc)
                pages = doc.page_count
            else:
                raw = f.read_text(encoding="utf-8", errors="replace")
                body = raw[raw.find("<body"):] if "<body" in raw else raw
                t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body.split("<ref-list")[0]))
                pages = None
        except Exception as e:
            rows.append(dict(screen_id=sid, file=f.name, status="EXTRACT_ERROR:" + type(e).__name__))
            continue
        cut = None
        m = [x for x in REF.finditer(t) if x.start() > 0.55 * len(t)]
        if m:
            cut = m[-1].start()
            # keep supporting information / later chapters that follow the reference list
            after = RESUME.search(t, cut + 20)
            kept = ("\n[text resumes: %s]\n" % after.group(0).strip() + t[after.start():]) if after else ""
            t = t[:cut] + "\n[reference list removed at character %d]\n" % cut + kept
        out.write_text(t, encoding="utf-8")
        rows.append(dict(screen_id=sid, file=f.name, file_sha256=sha(f), pages=pages, chars=len(t),
                         ref_cut_at=cut, status="text_short" if len(t) < 4000 else "ok"))
    with open(HERE / "texts.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["screen_id", "file", "file_sha256", "pages", "chars", "ref_cut_at", "status"])
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "texts;", sum(r["status"] == "ok" for r in rows), "ok")


def pdir(n):
    d = HERE / ("pass_%s" % n)
    (d / "batches").mkdir(parents=True, exist_ok=True)
    return d


def prepare(n):
    texts = [r for r in csv.DictReader(open(HERE / "texts.csv", encoding="utf-8")) if not r["status"].startswith("EXTRACT")]
    status = {r["screen_id"]: r for r in csv.DictReader(open(HERE / "status.csv", encoding="utf-8"))} \
        if (HERE / "status.csv").exists() else {}
    done = set()
    plan_path = pdir(n) / "plan.json"
    plan = json.load(open(plan_path)) if plan_path.exists() else {"batches": {}}
    for b in plan["batches"].values():
        done.update(b["records"])
    todo = [r for r in texts if r["screen_id"] not in done]
    random.Random(SEEDS[n] + len(plan["batches"])).shuffle(todo)
    batch, size, k = [], 0, len(plan["batches"])

    def flush():
        nonlocal batch, size, k
        if not batch:
            return
        k += 1
        name = "P%s_%04d" % (n, k)
        lines = [dict(screen_id=r["screen_id"], doi=(status.get(r["screen_id"]) or {}).get("doi", ""),
                      text="text/%s.txt" % r["screen_id"], chars=int(r["chars"]), text_status=r["status"]) for r in batch]
        p = pdir(n) / "batches" / (name + ".in.jsonl")
        p.write_text("".join(json.dumps(x) + "\n" for x in lines), encoding="utf-8", newline="\n")
        plan["batches"][name] = dict(records=[x["screen_id"] for x in lines], chars=size, sha256=sha(p))
        batch, size = [], 0

    for r in todo:
        c = int(r["chars"])
        if batch and (size + c > BUDGET or len(batch) >= MAX_PER_BATCH):
            flush()
        batch.append(r)
        size += c
    flush()
    plan.update(pass_=n, seed=SEEDS[n], budget_chars=BUDGET, max_per_batch=MAX_PER_BATCH,
                instructions_sha256=sha(HERE / "eligibility_instructions.md"),
                updated_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    json.dump(plan, open(plan_path, "w"), indent=1)
    print("pass", n, len(plan["batches"]), "batches;", len(todo), "records added")


def check(inp, out):
    if not out.exists():
        return ["missing"]
    want = [json.loads(l)["screen_id"] for l in open(inp, encoding="utf-8")]
    got, probs = [], []
    for i, l in enumerate(open(out, encoding="utf-8"), 1):
        if not l.strip():
            continue
        try:
            r = json.loads(l)
        except ValueError:
            probs.append("line %d not JSON" % i)
            continue
        got.append(r.get("screen_id"))
        if r.get("disposition") not in DISP:
            probs.append("line %d bad disposition" % i)
        if r.get("disposition") == "EXCLUDE" and r.get("exclude_criterion") not in {"E1", "E2", "E3", "E4", "E5", "E6"}:
            probs.append("line %d exclude without criterion" % i)
    if got != want:
        probs.append("order/coverage mismatch")
    return probs


def status(n, quiet=False):
    plan = json.load(open(pdir(n) / "plan.json"))["batches"]
    d = pdir(n) / "batches"
    bad = {b: check(d / (b + ".in.jsonl"), d / (b + ".out.jsonl")) for b in plan}
    bad = {b: p for b, p in bad.items() if p}
    if not quiet:
        print(json.dumps(dict(batches=len(plan), done=len(plan) - len(bad),
                              open=sorted(b for b, p in bad.items() if p == ["missing"]),
                              invalid={b: p for b, p in bad.items() if p != ["missing"]}), indent=1))
    return bad


def collect(n):
    plan = json.load(open(pdir(n) / "plan.json"))["batches"]
    d = pdir(n) / "batches"
    bad = status(n, quiet=True)
    rows = [json.loads(l) for b in plan if b not in bad for l in open(d / (b + ".out.jsonl"), encoding="utf-8") if l.strip()]
    out = pdir(n) / ("pass_%s.jsonl" % n)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8", newline="\n")
    disp = {}
    for r in rows:
        key = r["disposition"] + (":" + r["exclude_criterion"] if r["disposition"] == "EXCLUDE" else "")
        disp[key] = disp.get(key, 0) + 1
    json.dump(dict(recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(), records=len(rows),
                   open_or_invalid=sorted(bad), dispositions=disp, pass_file_sha256=sha(out)),
              open(pdir(n) / "collection.json", "w"), indent=1)
    print(len(rows), "records;", disp)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["extract", "prepare", "status", "collect"])
    p.add_argument("--pass", dest="n", choices=["1", "2"])
    a = p.parse_args()
    if a.cmd == "extract":
        extract()
    else:
        dict(prepare=prepare, status=status, collect=collect)[a.cmd](a.n)
