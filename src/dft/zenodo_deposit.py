#!/usr/bin/env python3
"""Deposit docs/43 and its fileset to Zenodo as a new version of the concept record.

WHY THIS EXISTS

Three versions of the pre-registration have been published (21963144 A1-A7,
22072991 A1-A9, 22213117 A1-A11) and every one was a manual act; no script
existed, so the procedure lived only in prose. That is fine until a deposit is
overdue and the procedure has to be reconstructed under time pressure -- which
is exactly the situation A12-A13.DEP records. This is the procedure, executable
and checkable.

WHAT IT GUARANTEES

  * DRY RUN BY DEFAULT. It will not create, upload, or publish anything unless
    given --create / --upload / --publish explicitly, in that order.
  * It writes no manifest and creates, uploads or publishes nothing while a
    PENDING_ placeholder remains in the deposit's file names or metadata, or
    while the freeze text still carries a [CONFIRM] marker or its proposal
    status line (pending()).
  * It NEVER prints the token, and never puts it in a URL or an argv.
  * The manifest it writes lists the GIT-BLOB (LF) serialization, and says so.
    The 2026-08-31 manifest called its rows "the working-tree serialization"
    while its bytes/md5/sha256 were in fact the LF blobs (verified 9/9). The
    two differ by one CR per line on this machine, so the label matters.
  * Files are uploaded from the git blob at a NAMED COMMIT, not from the working
    tree, so a dirty tree cannot leak into a permanent record.
  * After upload it re-reads the deposition from the API and verifies every
    remote checksum against the local md5 before publish is even offered.
  * ACCESS IS RESTRICTED, matching the registered election for every prior
    version. Opening the deposits is a separate, unexercised entrant decision.

Usage (each step is a separate invocation, deliberately):

  PYTHONPATH=src python src/dft/zenodo_deposit.py --manifest            # write manifest, verify hashes
  PYTHONPATH=src python src/dft/zenodo_deposit.py --create              # open a new-version draft
  PYTHONPATH=src python src/dft/zenodo_deposit.py --upload              # upload + verify checksums
  PYTHONPATH=src python src/dft/zenodo_deposit.py --publish             # IRREVERSIBLE: mints the DOI
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

TOKEN_PATH = os.path.join(os.path.expanduser("~"), ".config", "zenodo", "token")
API = "https://zenodo.org/api"

# The concept record. Versions attach to THIS, not to any version DOI.
CONCEPT_RECID = "21963143"
# The most recently published version; the new version drafts off it.
LATEST_PUBLISHED_RECID = "23327000"

# The deposit this script is set up for: the S8 stage-1 melt freeze with arm C's and the arm C extension's final
# readouts (docs/research/s8-freeze-deposit-package-2026-10-11.md). Each PENDING_ value is filled when the entrant
# settles it; --manifest, --create, --upload and --publish refuse while any remains (pending()).
LABEL = "S8"
CONFIRMED = "2026-10-12"  # the entrant's dated confirmation of the freeze text ("keep everything as written")
# The deposit's timing against the melt (the entrant, 2026-10-12: "Yes. The first 3", "Friday and today",
# "Nothing measured yet"); the departure is recorded in freeze section 1b.
FIRST_INGOT = ("after three of its six buttons (Cu8Cr23Mn35Co34, Ni31Cr29Cu5Mn35, Fe25Co25Ni25Cr25) were melted "
               "on 2026-10-09 and 2026-10-12, with nothing yet measured on them")

# repo path -> name the file carries in the deposit. A new version replaces the whole fileset, so every earlier
# version's files are carried forward and the S8 files are added after them.
FILESET = [
    ("docs/43-prereg-week1-factorial.md", "43-prereg-week1-factorial-A1-A13-plus-A10-plus-S8.md"),
    ("docs/45-error-ledger.md", "45-error-ledger.md"),
    ("docs/74-amendment-10-DRAFT.md", "74-amendment-10-DRAFT-v2-as-adopted-2026-09-21.md"),
    ("docs/88-a10-signature-sheet-2026-09-05.md", "88-a10-signature-sheet-filled-2026-09-21.md"),
    ("docs/research/research-decisions-2026-09-16.md", "research-decisions-2026-09-16.md"),
    ("results/s5_beef_2026-09-17/readout.json", "s5_beef_readout_2026-09-17.json"),
    ("docs/77-amendment-12-pproj6-DRAFT.md", "77-amendment-12-pproj6-DRAFT.md"),
    ("docs/79-hp-cro2-ortho-readout-2026-09-04.md", "79-hp-cro2-ortho-readout-2026-09-04.md"),
    ("docs/80-own-u-arm-killtest-2026-09-04.md", "80-own-u-arm-killtest-2026-09-04.md"),
    ("docs/81-zpe-decomposition-of-a71-2026-09-04.md", "81-zpe-decomposition-of-a71-2026-09-04.md"),
    ("runs/a0/m_pproj6.txt", "m_pproj6.txt"),
    ("runs/a0/m_pproj_cell.txt", "m_pproj_cell.txt"),
    # S8: the freeze, the records arms B and C rest on, and the plan and weigh sheet its processing cites. Arm A is
    # dated by commit 96b1cb1 and its values are in the freeze; its record has changed since and is not deposited.
    ("docs/research/s8-stage1-freeze-proposal-2026-10-07.md", f"s8-stage1-freeze-as-confirmed-{CONFIRMED}.md"),
    ("docs/95-census-2-3-readout-2026-09-13.md", "95-census-2-3-readout-2026-09-13.md"),
    ("results/s8_ranking_statistic_2026-09-19/ranking_statistics.md", "s8-ranking-statistics-2026-09-19.md"),
    ("docs/research/s8-arm-c-dft-design-2026-10-07.md", "s8-arm-c-dft-design-2026-10-07.md"),
    ("results/arm_c_2026-10-07_rerun/readout.json", "s8-arm-c-final-readout-2026-10-07.json"),
    ("docs/research/s8-arm-c-extension-2026-10-08.md", "s8-arm-c-extension-2026-10-08.md"),
    ("results/arm_c_ext_r6_2026-10-11/readout.json", "s8-arm-c-extension-final-readout-2026-10-11.json"),
    ("docs/research/s8-melt-plan-2026-10-07.md", "s8-melt-plan-2026-10-07.md"),
    ("docs/research/s8-weigh-sheet-2026-10-08.md", "s8-weigh-sheet-2026-10-08.md"),
]

STATE_PATH = os.path.join(ROOT, "docs", "deposits", ".draft_state.json")


def token() -> str:
    if not os.path.exists(TOKEN_PATH):
        sys.exit(f"REFUSING: no token at {TOKEN_PATH}")
    with open(TOKEN_PATH) as fh:
        t = fh.read().strip()
    if not t:
        sys.exit("REFUSING: token file is empty")
    return t


def git(*args: str) -> bytes:
    return subprocess.run(["git", "-C", ROOT, *args], check=True,
                          stdout=subprocess.PIPE).stdout


def head() -> str:
    return git("rev-parse", "HEAD").decode().strip()


def blob(path: str, commit: str) -> bytes:
    """The file's bytes AS COMMITTED (LF), never the working tree."""
    return git("cat-file", "-p", f"{commit}:{path}")


def api(method: str, url: str, data=None, ctype="application/json"):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", "Bearer " + token())   # never in the URL
    body = None
    if data is not None:
        if isinstance(data, (bytes, bytearray)):
            body = data
            req.add_header("Content-Type", ctype)
        else:
            body = json.dumps(data).encode()
            req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, body, timeout=600) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:2000]
        sys.exit(f"ZENODO {method} {url.split('?')[0]} -> HTTP {e.code}\n{detail}")


def save_state(d):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as fh:
        json.dump(d, fh, indent=1)


def load_state():
    if not os.path.exists(STATE_PATH):
        sys.exit("REFUSING: no draft state. Run --create first.")
    with open(STATE_PATH) as fh:
        return json.load(fh)


def check_clean():
    # Only a modified deposited file (or the draft state) blocks: the deposit is read from blobs at the commit, and
    # other sessions share this worktree, so their unrelated edits are reported, not deposited.
    dirty = git("status", "--porcelain", "--untracked-files=no").decode().splitlines()
    ours = {p for p, _ in FILESET} | {os.path.relpath(STATE_PATH, ROOT).replace(os.sep, "/")}
    blocking = [line for line in dirty if line[3:].strip() in ours]
    if blocking:
        sys.exit("REFUSING: deposited files are modified. Commit first -- a deposit "
                 "must name a commit.\n" + "\n".join(blocking))
    if dirty:
        print("modified tracked files outside the deposit (not deposited):\n" + "\n".join(dirty))


def manifest_path(commit: str) -> str:
    """The manifest's repo path, dated by the commit the deposited blobs come from."""
    date = git("log", "-1", "--format=%cs", commit).decode().strip()
    return f"docs/deposits/{date}-{LABEL}.manifest.txt"


def metadata(commit: str) -> dict:
    # Metadata follows the convention of the published versions exactly:
    # same title stem, same upload_type/publication_type, same keywords, same
    # creators, restricted access, a "version" string naming the amendment span,
    # and a dated "New version" paragraph appended to the standing description.
    # Renaming a concept record between versions makes it read as a different
    # object, so the stem is not touched.
    return {
        "metadata": {
            "title": (
                "Pre-registration record, DFT error-budget campaign "
                "(sts-electrocatalyst): Week-1 factorial, Hessian test, U gate "
                "— Amendments 1-13 complete (A10 adopted 2026-09-21), the "
                "Hubbard-projector arms, and the S8 stage-1 melt freeze "
                f"(confirmed {CONFIRMED})"),
            "version": "A1-A13-plus-A10-plus-S8",
            "upload_type": "publication",
            "publication_type": "other",
            "access_right": "restricted",
            "keywords": ["pre-registration", "DFT", "DFT+U", "OER",
                         "electrocatalysis", "error budget", "Quantum ESPRESSO",
                         "reproducibility"],
            "creators": [{"name": "Cai, Frank",
                          "affiliation": "Purdue University",
                          "orcid": "0009-0003-0041-1459"}],
            "description": (
                "Dated pre-registration document for a computational catalysis "
                "error-budget campaign (Quantum ESPRESSO, rutile MO2(110) OER): "
                "registered predictions, thresholds, capability gates, and "
                "corrections of record. Files are closed until report submission "
                "(planned November 2026); the record exists to give the "
                "pre-registration chain an immutable third-party timestamp. "
                "Contact the author for access."
                "<p>New version, 2026-08-31: Amendment 11 (spin-treatment "
                "equalisation, adopted with all entrant elections), the "
                "P-DISPOSITION date amendment (Oct 15 → REPORT LOCK, backstop "
                "Nov 5 2026 8:00 pm ET), the countersigned docs/59 roster "
                "correction, the election record (docs/66), and the Mn AFM arm "
                "design of record (docs/67).</p>"
                "<p>New version, 2026-09-04: Amendment 12 (P-PROJ-6, the "
                "six-metal Hubbard-projector contrast at U = 7.50 eV; "
                "|Δη| primary, five blind metals, Cr excluded as "
                "calibration, four bands including a named middle band, and "
                "pseudopotential / spin confound clauses); Amendment 12b (CrO2 "
                "bulk one-shot linear-response U under both projectors, with the "
                "countersigned readout — 6.1635 eV atomic vs 7.2677 eV "
                "ortho-atomic) and its correction of record that these are "
                "one-shot, not self-consistent, U values; and Amendment 13 "
                "(the projector contrast repeated in the adopted 2×1v cell, "
                "registering no new threshold and disclosing its non-blind half "
                "in advance), together with a disclosure decomposing the flagship "
                "0.487 V projector effect into its electronic and ZPE/TS "
                "constants halves. RECORDED DEPARTURE: amendments 12 and 12b were "
                "adopted and committed before their jobs were submitted, but this "
                "deposit follows those submissions rather than preceding them; "
                "the departure and its consequences are stated in the document at "
                "section A12-A13.DEP. Amendment 10 remains undrafted as registered "
                "text. Files are the git-blob (LF) serialization of commit "
                "72aeee9 (branch r0-catalysis-revival); per-file md5 and sha256 "
                "manifest committed in-repo at "
                "docs/deposits/2026-09-04-A13.manifest.txt.</p>"
                "<p>New version, 2026-09-21: Amendment 10 (the S5 BEEF-vdW σ row: "
                "what σ_BEEF(η) is, Ladder B with the < 0.25 V / ≥ 0.30 V bands, the "
                "descriptive U-sensitivity comparison, scope label XC-only "
                "non-magnetic Ru/Ir/Ti, no Cr extension), adopted by the entrant on "
                "2026-09-21 by the same instrument as Amendment 8 (the fifteen "
                "operating decisions adopted as proposed; signature sheet docs/88 "
                "filled), together with the dated claim-sentence re-test line of "
                "2026-09-21 (the sentence of record and its constraint verdicts) and "
                "the error ledger. RECORDED DEPARTURE: the fourteen S5 decks ran on "
                "2026-09-17, before Amendment 10 was adopted and before this deposit, "
                "and their result (P-BEEF CONFIRMED 3/3) was known when the amendment "
                "was adopted; the thresholds stood in written draft before the run "
                "and were not changed after it; the departure is stated in the "
                "document at the dated addendum of 2026-09-21. Files are the "
                "git-blob (LF) serialization of commit cccdbc8 (branch "
                "r0-catalysis-revival); per-file md5 and sha256 manifest committed "
                "in-repo at docs/deposits/2026-09-21-A10.manifest.txt.</p>"
                f"<p>New version, {CONFIRMED}: the S8 stage-1 melt freeze, "
                f"confirmed by the entrant on {CONFIRMED} and deposited "
                f"{FIRST_INGOT}, and before any OER measurement of its six alloys. "
                "It freezes three predictions of their OER activity: (A) the "
                "August 5 MLIP screen, a dated historical prediction (commit "
                "96b1cb1); (B) the September MLIP site census, which is also the "
                "re-rank of record; (C) DFT+U values at fixed census geometries "
                "(arm C), whose registered readings (K1, K2, the Ni34 nomination) "
                "are not evaluable, entering as an exploratory partial order over "
                "four alloys, with the arm C extension's exploratory values for five "
                "alloys (Cu8Cr23Mn35Co34 has no DFT alloy value). Of the registered "
                "primary hypotheses, K1 decides between arms A and B and K2 is shared "
                "by them; a same-bench comparison with IrO2 is a registered secondary "
                "outcome. RECORDED DEPARTURES: the re-rank gate departs from the "
                "registered S8 rule in three places (freeze section 1a); every "
                "extension round after the first was chosen after the previous "
                "readout was known; the last round's selection threshold was set "
                "after its screen was run (freeze section 4b); and the deposit follows "
                "the first ingot, while the S8 rule requires it before (freeze section 1b): "
                "arms A, B and C were committed before the first melt, and the extension's "
                "Fe25 value after it. docs/43 also carries its four dated addenda "
                "of 2026-09-22 (three licensed compute additions under A11.R3 and "
                "the entrant's election \"Protocol research first, freeze later\"), "
                "deposited here for the first time. Files are the git-blob (LF) serialization of "
                f"commit {commit[:7]} (branch r0-catalysis-revival); per-file md5 "
                "and sha256 manifest committed in-repo at "
                f"{manifest_path(commit)}.</p>"),
        }
    }


FREEZE = "docs/research/s8-stage1-freeze-proposal-2026-10-07.md"
DOCS43 = "docs/43-prereg-week1-factorial.md"
UNCONFIRMED = "[CONFIRM"  # marks an item the entrant has not confirmed, in any deposited file
PROPOSED = "proposed, not frozen"  # the freeze's status line until the entrant confirms it


def pending(commit: str = "") -> list:
    """What still blocks the deposit; nothing is written while any remains.

    Placeholders in the deposit's names or metadata, a confirmation date that is not YYYY-MM-DD, a deposited file at
    the commit that still carries a [CONFIRM] marker, and a freeze that still carries its proposal status line.
    """
    commit = commit or head()
    text = json.dumps([FILESET, metadata(commit)], ensure_ascii=False)
    found = sorted(set(re.findall(r"PENDING_[A-Z_]+", text)))
    if "PENDING_CONFIRMATION_DATE" not in found and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", CONFIRMED):
        found.append(f"CONFIRMED is not a YYYY-MM-DD date: {CONFIRMED!r}")
    files = {path: blob(path, commit).decode("utf-8", errors="replace") for path, _ in FILESET}
    found += [f"{path} at {commit[:9]} still contains {UNCONFIRMED!r}"
              for path, t in files.items() if UNCONFIRMED in t]
    if PROPOSED in files[FREEZE]:
        found.append(f"the freeze at {commit[:9]} still contains {PROPOSED!r}")
    return found


def names_manifest(commit) -> bool:
    """docs/43's addendum names the manifest this deposit writes, so the deposited record points at it."""
    return manifest_path(commit) in blob(DOCS43, commit).decode("utf-8", errors="replace")


def cmd_manifest(commit):
    if not names_manifest(commit):
        sys.exit(f"REFUSING: docs/43 at {commit[:9]} does not name the manifest {manifest_path(commit)}. "
                 "Its addendum must name the manifest of the commit being deposited.")
    rows = []
    print(f"fileset at {commit[:9]} (git-blob / LF bytes):\n")
    for path, name in FILESET:
        b = blob(path, commit)
        rows.append((len(b), hashlib.md5(b).hexdigest(),
                     hashlib.sha256(b).hexdigest(), path, name))
        print(f"  {len(b):>9,}  {hashlib.md5(b).hexdigest()}  {path}")
        if name != os.path.basename(path):
            print(f"  {'':>9}  {'':32}  -> deposited as {name}")

    out = os.path.join(ROOT, manifest_path(commit))
    date = os.path.basename(out)[:10]
    names = dict(FILESET)
    lines = [
        f"# Zenodo deposit fileset manifest -- {date} {LABEL} deposit (the S8 stage-1 melt freeze, confirmed by the"
        f" entrant on {CONFIRMED}, with arm C's final readout and the arm C extension's final readout)",
        f"# All files: the GIT-BLOB (LF) serialization at commit {commit}. Not the CRLF"
        f" working tree; the two differ by one CR per line on the authoring machine."
        f" Deposit name for docs/43: {names['docs/43-prereg-week1-factorial.md']}; for the freeze:"
        f" {names['docs/research/s8-stage1-freeze-proposal-2026-10-07.md']}",
        "# columns: bytes  md5  sha256  repo-path",
    ]
    for n, m, s, path, _name in rows:
        lines.append(f"{n}  {m}  {s}  {path}")
    with open(out, "w", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\nmanifest -> {os.path.relpath(out, ROOT)}")
    return rows


def cmd_create(commit):
    prev = api("GET", f"{API}/deposit/depositions/{LATEST_PUBLISHED_RECID}")
    print(f"latest published: {prev.get('id')}  "
          f"doi={prev.get('doi')}  title={prev.get('title','')[:60]!r}")
    conceptrec = str(prev.get("conceptrecid", ""))
    if conceptrec != CONCEPT_RECID:
        sys.exit(f"REFUSING: conceptrecid is {conceptrec}, expected {CONCEPT_RECID}. "
                 "The lineage is not what the registration says.")
    print(f"conceptrecid {conceptrec} matches the registered concept record.")

    nv = api("POST", f"{API}/deposit/depositions/{LATEST_PUBLISHED_RECID}"
                     f"/actions/newversion")
    draft_url = nv["links"]["latest_draft"]
    draft = api("GET", draft_url)
    did = draft["id"]
    print(f"new-version DRAFT created: id={did}  (nothing published)")
    save_state({"draft_id": did, "commit": commit,
                "bucket": draft["links"].get("bucket"),
                "prev_doi": prev.get("doi")})
    print(f"state -> {os.path.relpath(STATE_PATH, ROOT)}")


def cmd_upload(commit):
    st = load_state()
    did = st["draft_id"]
    # Upload from the commit the draft (and the manifest) NAME, not from HEAD.
    # HEAD legitimately moves on -- the manifest commit itself moves it, exactly
    # as the 2026-08-31 manifest named 6fe167b and was committed later at
    # 80260bb. What must not drift is the FILESET: every deposited blob at the
    # named commit has to be byte-identical to HEAD's, or the deposit would
    # freeze bytes the repo has since changed without saying so.
    named = st["commit"]
    if named != commit:
        drift = [p for p, _ in FILESET if blob(p, named) != blob(p, commit)]
        if drift:
            msg = ["REFUSING: the fileset changed between the commit the draft "
                   "names (%s) and HEAD (%s):" % (named[:9], commit[:9])]
            msg += ["  " + p for p in drift]
            msg.append("Re-run --manifest and --create at HEAD.")
            sys.exit(os.linesep.join(msg))
        print(f"draft names {named[:9]}; HEAD is {commit[:9]}; all "
              f"{len(FILESET)} deposited blobs identical across the two.")
    commit = named
    draft = api("GET", f"{API}/deposit/depositions/{did}")
    bucket = draft["links"]["bucket"]

    # A new version inherits the previous version's files. Remove them all, so
    # the deposit is exactly this fileset and nothing carried over silently.
    existing = draft.get("files", [])
    if existing:
        print(f"removing {len(existing)} inherited file(s) from the draft:")
        for f in existing:
            print(f"   - {f['filename']}")
            api("DELETE", f"{API}/deposit/depositions/{did}/files/{f['id']}")

    want = {}
    for path, name in FILESET:
        b = blob(path, commit)
        want[name] = hashlib.md5(b).hexdigest()
        print(f"uploading {name} ({len(b):,} bytes) ...", end=" ", flush=True)
        api("PUT", f"{bucket}/{name}", data=b, ctype="application/octet-stream")
        print("ok")

    meta = metadata(commit)
    api("PUT", f"{API}/deposit/depositions/{did}", data=meta)

    after = api("GET", f"{API}/deposit/depositions/{did}")
    remote = {f["filename"]: f["checksum"].replace("md5:", "") for f in after["files"]}
    bad = []
    print("\nchecksum verification (remote vs local git blob):")
    for name, m in want.items():
        r = remote.get(name)
        ok = (r == m)
        print(f"  {'OK  ' if ok else 'FAIL'} {name}  {m}  remote={r}")
        if not ok:
            bad.append(name)
    extra = set(remote) - set(want)
    for e in extra:
        print(f"  FAIL unexpected file still on the draft: {e}")
        bad.append(e)
    if bad:
        sys.exit(f"REFUSING: {len(bad)} checksum/fileset problem(s). Not publishable.")
    print(f"\nall {len(want)} files verified. Draft id {did} is ready.")
    print("Nothing is published. To mint the DOI (IRREVERSIBLE): --publish")


def cmd_publish(commit):
    st = load_state()
    did = st["draft_id"]
    d = api("GET", f"{API}/deposit/depositions/{did}")
    if d.get("submitted"):
        print(f"already published: doi={d.get('doi')}")
        return
    print(f"publishing draft {did} ({len(d.get('files', []))} files) -- IRREVERSIBLE")
    r = api("POST", f"{API}/deposit/depositions/{did}/actions/publish")
    print(f"\nPUBLISHED\n  DOI      {r.get('doi')}\n  record   {r.get('id')}"
          f"\n  concept  {r.get('conceptdoi')}\n  url      {r.get('links', {}).get('record_html')}")
    st["published_doi"] = r.get("doi")
    st["published_recid"] = r.get("id")
    save_state(st)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--create", action="store_true")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--publish", action="store_true")
    a = ap.parse_args(argv)
    left = pending()
    if left and any([a.manifest, a.create, a.upload, a.publish]):
        sys.exit("REFUSING: the deposit is not ready: " + "; ".join(left)
                 + ". Settle these (see LABEL above FILESET) and commit first.")
    sys.stdout.reconfigure(encoding="utf-8")

    check_clean()
    commit = head()

    if not any([a.manifest, a.create, a.upload, a.publish]):
        print("DRY RUN. Nothing contacted, nothing written.\n")
        print(f"HEAD {commit}")
        cmd_manifest_dry(commit)
        return
    if a.manifest:
        cmd_manifest(commit)
    if a.create:
        cmd_create(commit)
    if a.upload:
        cmd_upload(commit)
    if a.publish:
        cmd_publish(commit)


def cmd_manifest_dry(commit):
    print("fileset that WOULD be deposited (git-blob / LF bytes):\n")
    total = 0
    for path, name in FILESET:
        b = blob(path, commit)
        total += len(b)
        print(f"  {len(b):>9,}  {hashlib.md5(b).hexdigest()}  {path}"
              + (f"  -> {name}" if name != os.path.basename(path) else ""))
    print(f"\n  {total:>9,}  bytes total, {len(FILESET)} files")
    print(f"\nconcept record {CONCEPT_RECID}; new version drafts off "
          f"{LATEST_PUBLISHED_RECID}; access_right=restricted")
    left = pending(commit)
    print(f"{LABEL} deposit; still to settle: " + ("; ".join(left) if left else "nothing"))
    print(f"docs/43 names the manifest {manifest_path(commit)}: {'yes' if names_manifest(commit) else 'NO'}")


if __name__ == "__main__":
    main()
