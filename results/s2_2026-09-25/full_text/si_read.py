"""SI read (FT4): the main text plus the downloaded supporting information of every live record whose SI is now
in hand, read under the current instructions by two independent passes, with a third read wherever the passes
do not settle the record.  Entrant, 2026-09-28: in-session agents, "preserving independent passes, source
locations, and third-read reconciliation"; no Batch API spending for now.

  python si_read.py extract                SI text with file and page markers -> text_si/<sid>.txt, si_texts.csv
  python si_read.py prepare [--ids S1,S2]  batch the selected records for pass 1 and pass 2 (different seeds)
  python si_read.py status                 batches without a valid output (both passes and the third read)
  python si_read.py collect                validate the passes -> si_read/pass_<n>.jsonl; lanes -> si_read/queue.csv
  python si_read.py third                  batch the THIRD_READ lane (records not yet batched)
  python si_read.py collect-third          validate -> si_read/third_read.jsonl

Selection: v5_final in reconcile/current_state.csv is NEEDS_SI or UNRESOLVED and the record's SI includes a
document (PDF or Word, also inside a zip), plus --ids (records whose open question needs their SI).  A record
whose SI is only source data or structure files waits for the SI document (SI checklist).  Records with a
reconciliation fact (reconcile/identity_check.csv, supplied_to_reads yes) are read in the same round whether or
not their SI is in hand (si_text null then), unless their decision is carried by a version primary.
SI text: SI documents in full, never cut: PDFs page by page ("[SI2.pdf p. 4]"), Word documents, plain-text files
(cut only past TEXT_CAP characters, marked "[truncated ...]").  Source data (spreadsheets, CSV) show every sheet
with its first DATA_ROWS rows and the row count; structure files (CIF, POSCAR/CONTCAR, xyz ...) their first
STRUCT_LINES lines, for the first STRUCT_FILES of a record; other zip members are listed by name.  Zip members are
treated like files.  The record's si_complete is false when an SI document could not be extracted, a text file
was cut, or an SI link on the article page did not yield a file (si_public_log.jsonl publisher_si entries other
than OK; in-page anchors "#...", videos and binary spreadsheets excepted).  Source data and structure files shown
in part do not make it false: they are the data behind figures and models, not text that reports results.  The batch line carries si_complete, the SI file list and any reconciliation facts
(reconcile/identity_check.csv, v5 D9) for the record.
Lanes (the excerpt check of reconcile.py, over main text + SI text):
  AGREED      both passes give the same disposition (and exclusion criterion) and every deciding excerpt is
              verified; an ELIGIBLE needs all six verified, an EXCLUDE its exclusion criterion
  NEEDS_SI    both passes NEEDS_SI (the SI in hand is not the whole SI) and neither excerpt fails
  THIRD_READ  anything else: disagreement, an unverified excerpt, UNRESOLVED, a pass that finds the file unreadable
Nothing here decides eligibility.
"""
import argparse
import csv
import datetime as dt
import io
import json
import pathlib
import random
import re
import urllib.parse
import zipfile

from ft_screen import BUDGET, MAX_PER_BATCH, check, sha
from reconcile import verified
from third_read import slim

HERE = pathlib.Path(__file__).resolve().parent
D = HERE / "si_read"
SI = HERE / "files_si"
TSI = HERE / "text_si"
SEEDS = {"1": 20260928, "2": 82906202}
TEXT_CAP = 120_000  # characters of a plain-text SI file (a caption list, notes); SI documents are never cut
DATA_ROWS = 15  # rows shown per spreadsheet sheet or CSV (source data behind figures)
STRUCT_LINES = 40  # lines shown per structure file, for the first STRUCT_FILES of a record
STRUCT_FILES = 5
LIST_CAP = 60  # member names listed per zip archive
DOCS = (".pdf", ".docx", ".doc")
STRUCT = re.compile(r"(\.cif|\.xyz|\.vasp|\.traj|\.cube|poscar|contcar|outcar)[^/]*$", re.I)


def pdf_text(body, tag):
    import fitz
    doc = fitz.open(stream=body, filetype="pdf")
    return "\n".join("[%s p. %d]\n%s" % (tag, i + 1, p.get_text()) for i, p in enumerate(doc)), doc.page_count


def docx_text(body):
    x = zipfile.ZipFile(io.BytesIO(body)).read("word/document.xml").decode("utf-8", "replace")
    x = re.sub(r"</w:p>", "\n", x)
    x = re.sub(r"<w:tab/>", "\t", x)
    return re.sub(r"<[^>]+>", "", x)


def rows_text(rows, where, total=None):
    """The first DATA_ROWS non-empty rows; total is the sheet's row count where the file states it."""
    lines, more = [], False
    for row in rows:
        line = "\t".join("" if v is None else str(v) for v in row).rstrip()
        if not line:
            continue
        if len(lines) == DATA_ROWS:
            more = True
            break
        lines.append(line[:300])
    note = "\n[source data: %s has more rows (%s in all); the first %d are shown]" % (
        where, total or "count not stated", len(lines)) if more else ""
    return "\n".join(lines) + note


def xlsx_text(body, tag):
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(body), read_only=True, data_only=True)
    out = ["[%s sheet '%s']\n%s" % (tag, ws.title, rows_text(ws.iter_rows(values_only=True), "sheet '%s'" % ws.title, ws.max_row))
           for ws in wb.worksheets]
    wb.close()
    return "\n".join(out)


class Record:
    """Text of one record's SI: documents in full, data and structure files abbreviated, the rest listed."""

    def __init__(self):
        self.chunks, self.pages, self.incomplete, self.structs = [], 0, [], 0

    def part(self, name, body, tag, member=False):
        low = name.lower()
        try:
            if low.endswith(".pdf"):
                t, n = pdf_text(body, tag)
                self.pages += n
                return t
            if low.endswith(".docx"):
                return docx_text(body)
            if low.endswith(".doc"):
                self.incomplete.append("%s: old Word format, not extracted" % tag)
                return "[%s: old Word document, not extracted; its content is not in this file]" % tag
            if low.endswith((".xlsx", ".xlsm")):
                return xlsx_text(body, tag)
            if low.endswith(".csv"):
                return rows_text(csv.reader(io.StringIO(body.decode("utf-8", "replace"))), tag)
            head = body[:400].decode("utf-8", "replace")
            if STRUCT.search(low) or (low.endswith(".txt") and re.search(r"coordinates|lattice|poscar|contcar|atoms", head, re.I)) \
                    or ((member or not re.search(r"\.[a-z0-9]{1,5}$", low)) and re.match(r"\s*\S.*\n\s*[\d.]+\s*\n\s*-?[\d.]+\s+-?[\d.]+\s+-?[\d.]+", head)) \
                    or (member and re.search(r"^data_|^_cell_length_a", head, re.M)):  # CIF saved under another extension
                self.structs += 1
                if self.structs > STRUCT_FILES:
                    return "[structure file, not shown]"
                lines = body.decode("utf-8", "replace").splitlines()
                return "\n".join(lines[:STRUCT_LINES]) + (
                    "\n[structure file: %d more lines not shown]" % (len(lines) - STRUCT_LINES) if len(lines) > STRUCT_LINES else "")
            if low.endswith(".txt"):
                t = body.decode("utf-8", "replace")
                if len(t) > TEXT_CAP:
                    self.incomplete.append("%s: text cut at %d characters" % (tag, TEXT_CAP))
                    return t[:TEXT_CAP] + "\n[truncated: %s continues for %d characters that are not in this file]" % (tag, len(t) - TEXT_CAP)
                return t
        except Exception as e:
            if low.endswith(DOCS):
                self.incomplete.append("%s: unreadable (%s)" % (tag, type(e).__name__))
            return "[%s: unreadable (%s)]" % (tag, type(e).__name__)
        return None

    def add(self, f, published):
        tag = f.name.split("_", 1)[1]  # "SI1.pdf": unique even when two files share a number
        head = "[SI file %s: %s (published as %s)]" % (tag, f.name, published)
        body = f.read_bytes()
        if f.suffix.lower() != ".zip":
            t = self.part(f.name, body, tag)
            self.chunks.append(head + ("\n" + t if t is not None else " (not text)"))
            return
        try:
            z = zipfile.ZipFile(io.BytesIO(body))
        except zipfile.BadZipFile:
            self.chunks.append(head + " (unreadable zip)")
            return
        members = [m for m in z.infolist() if not m.is_dir()]
        self.chunks.append(head + " zip archive, %d files" % len(members))
        unlisted = 0
        for i, m in enumerate(members):
            t = self.part(m.filename, z.read(m), "%s/%d" % (tag, i + 1), member=True)
            if t is None or t == "[structure file, not shown]":
                if i < LIST_CAP:
                    self.chunks.append("[%s member %d: %s, %d bytes%s]" % (
                        tag, i + 1, m.filename, m.file_size, ", structure file" if t else ", not text"))
                else:
                    unlisted += 1
            else:
                self.chunks.append("[%s member %d: %s]\n%s" % (tag, i + 1, m.filename, t))
        if unlisted:
            self.chunks.append("[%s: %d further members not listed]" % (tag, unlisted))


def names():
    """Published name of each SI file (from the retrieval log URL)."""
    out = {}
    for l in open(HERE / "si_public_log.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if e.get("status") == "OK":
            out[e["file"]] = urllib.parse.unquote(e["url"].split("?")[0].rstrip("/").split("/")[-1])
    return out


def incomplete_links():
    bad = {}
    for l in open(HERE / "si_public_log.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if e.get("route") == "publisher_si" and e.get("status") != "OK" and "#" not in e["url"] \
                and not re.search(r"\.(mp4|avi|mov|gif|xlsb)$", e["url"], re.I):
            bad.setdefault(e["screen_id"], []).append(e["url"])
    return bad


def has_document(sid):
    for f in SI.glob(sid + "_SI*"):
        if f.suffix.lower() in DOCS:
            return True
        if f.suffix.lower() == ".zip":
            try:
                if any(n.lower().endswith(DOCS) for n in zipfile.ZipFile(f).namelist()):
                    return True
            except zipfile.BadZipFile:
                pass
    return False


def extract():
    TSI.mkdir(exist_ok=True)
    nm, bad = names(), incomplete_links()
    files = {}
    for f in sorted(SI.iterdir(), key=lambda p: (p.name.split("_SI")[0], int(re.search(r"_SI(\d+)", p.name).group(1)), p.suffix)):
        files.setdefault(f.name.split("_SI")[0], []).append(f)
    rows = []
    for sid, fs in files.items():
        rec = Record()
        for f in fs:
            rec.add(f, nm.get(f.name, "?"))
        text = "\n\n".join(rec.chunks) + "\n"
        p = TSI / (sid + ".txt")
        if not p.exists() or p.read_text(encoding="utf-8") != text:  # never rewrite a text a reader may be reading
            p.write_text(text, encoding="utf-8")
        why = rec.incomplete + ["SI link on the article page gave no file: %s" % u for u in bad.get(sid, [])]
        rows.append(dict(screen_id=sid, files=";".join(f.name for f in fs), document=has_document(sid), pages=rec.pages,
                         chars=len(text), si_complete=not why, incomplete="; ".join(why),
                         text_sha256=sha(TSI / (sid + ".txt"))))
    with open(HERE / "si_texts.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "records;", sum(r["document"] for r in rows), "with an SI document;",
          sum(not r["si_complete"] for r in rows), "incomplete;", sum(r["chars"] for r in rows), "characters")


def facts():
    p = HERE / "reconcile" / "identity_check.csv"
    out = {}
    if p.exists():
        for r in csv.DictReader(open(p, encoding="utf-8")):
            if r["supplied_to_reads"] != "yes":  # items that wait for an entrant ruling (see the csv)
                continue
            for sid in r["records"].split(";"):
                out.setdefault(sid, []).append(
                    "Identity check at reconciliation (v5 D9): %s = %s; rutile-type (P4_2/mnm): %s. Source: %s" % (
                        r["item"], r["identity"], r["rutile_type"], r["source"]))
    return out


def pdir(n):
    d = D / ("pass_%s" % n)
    (d / "batches").mkdir(parents=True, exist_ok=True)
    return d


def selected(ids):
    """Records with an SI document that are NEEDS_SI, UNRESOLVED or named in ids, and records with a reconciliation
    fact (reconcile/identity_check.csv) whose own decision stands (not collapsed, readable), with or without SI."""
    si = {r["screen_id"]: r for r in csv.DictReader(open(HERE / "si_texts.csv", encoding="utf-8"))}
    st = list(csv.DictReader(open(HERE / "reconcile" / "current_state.csv", encoding="utf-8")))
    fx = facts()
    doc = lambda s: s in si and si[s]["document"] == "True"
    return [r for r in st if (doc(r["screen_id"]) and (r["v5_final"] in ("NEEDS_SI", "UNRESOLVED") or r["screen_id"] in ids))
            or (r["screen_id"] in fx and not r["v5_final"].startswith(("collapsed", "no readable")))], si


def text_chars():
    return {x["screen_id"]: int(x["chars"]) for x in csv.DictReader(open(HERE / "texts.csv", encoding="utf-8"))
            if x.get("chars")}


def line(r, si, fx, tc):
    sid = r["screen_id"]
    has = sid in si and si[sid]["document"] == "True"
    return dict(screen_id=sid, doi=r["doi"], text="text/%s.txt" % sid, si_text=("text_si/%s.txt" % sid) if has else None,
                chars=tc.get(sid, 0), si_chars=int(si[sid]["chars"]) if has else 0,
                si_complete=has and si[sid]["si_complete"] == "True",
                si_files=si[sid]["files"].split(";") if has else [], facts=fx.get(sid, []))


def prepare(ids):
    recs, si = selected(ids)
    fx, tc = facts(), text_chars()
    for n in ("1", "2"):
        plan_p = pdir(n) / "plan.json"
        plan = json.load(open(plan_p)) if plan_p.exists() else {"batches": {}}
        done = {s for b in plan["batches"].values() for s in b["records"]}
        todo = [line(r, si, fx, tc) for r in recs if r["screen_id"] not in done]
        random.Random(SEEDS[n] + len(plan["batches"])).shuffle(todo)
        batch, size, k = [], 0, len(plan["batches"])

        def flush():
            nonlocal batch, size, k
            if not batch:
                return
            k += 1
            name = "SI%s_%04d" % (n, k)
            p = pdir(n) / "batches" / (name + ".in.jsonl")
            p.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in batch), encoding="utf-8", newline="\n")
            plan["batches"][name] = dict(records=[x["screen_id"] for x in batch], chars=size, sha256=sha(p))
            batch, size = [], 0

        for x in todo:
            c = x["chars"] + x["si_chars"]
            if batch and (size + c > BUDGET or len(batch) >= MAX_PER_BATCH):
                flush()
            batch.append(x)
            size += c
        flush()
        plan.update(pass_=n, seed=SEEDS[n], budget_chars=BUDGET, instructions_version="v5",
                    instructions_sha256=sha(HERE / "eligibility_instructions.md"),
                    updated_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        json.dump(plan, open(plan_p, "w"), indent=1)
        print("pass", n, len(plan["batches"]), "batches;", len(todo), "records added")


def statuses(d):
    plan = json.load(open(d / "plan.json"))["batches"] if (d / "plan.json").exists() else {}
    bad = {b: check(d / "batches" / (b + ".in.jsonl"), d / "batches" / (b + ".out.jsonl")) for b in plan}
    return plan, {b: p for b, p in bad.items() if p}


def status():
    for d in (pdir("1"), pdir("2"), D / "third"):
        plan, bad = statuses(d)
        print(d.name, json.dumps(dict(batches=len(plan), done=len(plan) - len(bad),
                                      open=sorted(b for b, p in bad.items() if p == ["missing"]),
                                      invalid={b: p for b, p in bad.items() if p != ["missing"]})))


def rows_of(d):
    plan, bad = statuses(d)
    return {r["screen_id"]: r for b in plan if b not in bad
            for r in (json.loads(l) for l in open(d / "batches" / (b + ".out.jsonl"), encoding="utf-8") if l.strip())}


def both_texts(sid):
    t = (HERE / "text" / (sid + ".txt")).read_text(encoding="utf-8")
    p = TSI / (sid + ".txt")
    return t + "\n" + (p.read_text(encoding="utf-8") if p.exists() and has_document(sid) else "")


def lane(a, b, text):
    if not (a and b):
        return "ONE_PASS"
    if any(x.get("text_ok") is False for x in (a, b)):
        return "THIRD_READ"
    da = a["disposition"] + ":" + str(a.get("exclude_criterion"))
    db = b["disposition"] + ":" + str(b.get("exclude_criterion"))
    ok = verified(a, text) and verified(b, text)
    if da == db and a["disposition"] in ("ELIGIBLE", "EXCLUDE") and ok:
        return "AGREED"
    if da == db == "NEEDS_SI:None":
        return "NEEDS_SI"
    return "THIRD_READ"


def collect():
    out, counts = [], {}
    p = {n: rows_of(pdir(n)) for n in ("1", "2")}
    for n, rs in p.items():
        f = D / ("pass_%s.jsonl" % n)
        f.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs.values()), encoding="utf-8", newline="\n")
    for sid in sorted(set(p["1"]) | set(p["2"])):
        a, b = p["1"].get(sid), p["2"].get(sid)
        text = both_texts(sid)
        ln = lane(a, b, text)
        counts[ln] = counts.get(ln, 0) + 1
        lab = lambda x: x and (x["disposition"] + (":" + x["exclude_criterion"] if x.get("exclude_criterion") else ""))
        out.append(dict(screen_id=sid, lane=ln, p1=lab(a), p2=lab(b),
                        p1_verified=a and verified(a, text), p2_verified=b and verified(b, text)))
    with open(D / "queue.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    json.dump(dict(recorded_utc=dt.datetime.now(dt.timezone.utc).isoformat(), records=len(out), lanes=counts),
              open(D / "collection.json", "w"), indent=1)
    print(len(out), "records;", counts)


def why(q):
    out = []
    if q["p1"] != q["p2"]:
        out.append("passes disagree (%s vs %s)" % (q["p1"], q["p2"]))
    if q["p1_verified"] == "False" or q["p2_verified"] == "False":
        out.append("a deciding excerpt was not found verbatim in the main text or SI")
    if "UNRESOLVED" in (q["p1"], q["p2"]):
        out.append("a pass left it UNRESOLVED")
    return "; ".join(out) or "lane rule"


def third():
    d = D / "third"
    (d / "batches").mkdir(parents=True, exist_ok=True)
    plan_p = d / "plan.json"
    plan = json.load(open(plan_p)) if plan_p.exists() else {"batches": {}}
    done = {s for b in plan["batches"].values() for s in b["records"]}
    p1, p2 = rows_of(pdir("1")), rows_of(pdir("2"))
    _, si = selected(set())
    fx, tc = facts(), text_chars()
    st = {r["screen_id"]: r for r in csv.DictReader(open(HERE / "reconcile" / "current_state.csv", encoding="utf-8"))}
    todo = []
    for q in csv.DictReader(open(D / "queue.csv", encoding="utf-8")):
        if q["lane"] != "THIRD_READ" or q["screen_id"] in done:
            continue
        x = line(st[q["screen_id"]], si, fx, tc)
        x.update(why=why(q), pass1=slim(p1.get(q["screen_id"])), pass2=slim(p2.get(q["screen_id"])))
        todo.append(x)
    batch, size, k = [], 0, len(plan["batches"])

    def flush():
        nonlocal batch, size, k
        if not batch:
            return
        k += 1
        name = "SI3_%04d" % k
        p = d / "batches" / (name + ".in.jsonl")
        p.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in batch), encoding="utf-8", newline="\n")
        plan["batches"][name] = dict(records=[x["screen_id"] for x in batch], chars=size, sha256=sha(p))
        batch, size = [], 0

    for x in todo:
        c = x["chars"] + x["si_chars"]
        if batch and (size + c > BUDGET or len(batch) >= MAX_PER_BATCH):
            flush()
        batch.append(x)
        size += c
    flush()
    plan.update(instructions_version="v5", instructions_sha256=sha(HERE / "eligibility_instructions.md"),
                updated_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    json.dump(plan, open(plan_p, "w"), indent=1)
    print(len(plan["batches"]), "third-read batches;", len(todo), "records added")


def collect_third():
    rs = rows_of(D / "third")
    out = D / "third_read.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rs.values()), encoding="utf-8", newline="\n")
    disp = {}
    for r in rs.values():
        key = r["disposition"] + (":" + r["exclude_criterion"] if r["disposition"] == "EXCLUDE" else "")
        disp[key] = disp.get(key, 0) + 1
    print(len(rs), "records;", disp, "; entrant questions", sum(bool(r.get("entrant_question")) for r in rs.values()))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["extract", "prepare", "status", "collect", "third", "collect-third"])
    ap.add_argument("--ids", default="")
    a = ap.parse_args()
    if a.cmd == "prepare":
        prepare(set(filter(None, a.ids.split(","))))
    else:
        dict(extract=extract, status=status, collect=collect, third=third, collect_third=collect_third)[a.cmd.replace("-", "_")]()
