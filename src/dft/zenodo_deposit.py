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
LATEST_PUBLISHED_RECID = "22213117"

# repo path -> name the file carries in the deposit
FILESET = [
    ("docs/43-prereg-week1-factorial.md", "43-prereg-week1-factorial-A1-A13.md"),
    ("docs/77-amendment-12-pproj6-DRAFT.md", "77-amendment-12-pproj6-DRAFT.md"),
    ("docs/79-hp-cro2-ortho-readout-2026-09-04.md", "79-hp-cro2-ortho-readout-2026-09-04.md"),
    ("docs/80-own-u-arm-killtest-2026-09-04.md", "80-own-u-arm-killtest-2026-09-04.md"),
    ("docs/81-zpe-decomposition-of-a71-2026-09-04.md", "81-zpe-decomposition-of-a71-2026-09-04.md"),
    ("runs/a0/m_pproj6.txt", "m_pproj6.txt"),
    ("runs/a0/m_pproj_cell.txt", "m_pproj_cell.txt"),
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
    dirty = git("status", "--porcelain", "--untracked-files=no").decode().strip()
    if dirty:
        sys.exit("REFUSING: tracked files are modified. Commit first -- a deposit "
                 "must name a commit.\n" + dirty)


def cmd_manifest(commit):
    rows = []
    print(f"fileset at {commit[:9]} (git-blob / LF bytes):\n")
    for path, name in FILESET:
        b = blob(path, commit)
        rows.append((len(b), hashlib.md5(b).hexdigest(),
                     hashlib.sha256(b).hexdigest(), path, name))
        print(f"  {len(b):>9,}  {hashlib.md5(b).hexdigest()}  {path}")
        if name != os.path.basename(path):
            print(f"  {'':>9}  {'':32}  -> deposited as {name}")

    date = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%cs", commit],
                          check=True, stdout=subprocess.PIPE).stdout.decode().strip()
    out = os.path.join(ROOT, "docs", "deposits", f"{date}-A13.manifest.txt")
    lines = [
        f"# Zenodo deposit fileset manifest -- {date} A12+A12b+A13 deposit (A12-A13.DEP)",
        f"# All files: the GIT-BLOB (LF) serialization at commit {commit}. Not the CRLF"
        f" working tree; the two differ by one CR per line on the authoring machine."
        f" Deposit name for docs/43: 43-prereg-week1-factorial-A1-A13.md",
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

    # Metadata follows the convention of the three published versions exactly:
    # same title stem, same upload_type/publication_type, same keywords, same
    # creators, restricted access, a "version" string naming the amendment span,
    # and a dated "New version" paragraph appended to the standing description.
    # Renaming a concept record between versions makes it read as a different
    # object, so the stem is not touched.
    meta = {
        "metadata": {
            "title": (
                "Pre-registration record, DFT error-budget campaign "
                "(sts-electrocatalyst): Week-1 factorial, Hessian test, U gate "
                "— Amendments 1-13 (A10 pending) + the Hubbard-projector arms, "
                "frozen 2026-09-04"),
            "version": "A1-A13",
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
                "docs/deposits/2026-09-04-A13.manifest.txt.</p>"),
        }
    }
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--create", action="store_true")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--publish", action="store_true")
    a = ap.parse_args()
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


if __name__ == "__main__":
    main()
