"""The A9.3.5 atomate input-set verification gate (docs/43 :1902), checked against git history.

    python -m s2.p_builder.atomate_gate --out results/s2_2026-09-16/p_builder_prestate/atomate_gate.json

Statement under test (docs/43 :1902, from the round-2 synthesis): "atomate MPSurfaceSet sets
ISYM: 0 under the comment 'Should give better forces for optimization', introduced 25 May
2018, commit a7d5f316; the 2017-era workflow (commit d2742a3b) used pymatgen's MVLSlabSet,
which does not set ISYM (VASP default ISYM = 2)".

Every source is fetched from the GitHub REST API (and the VASP wiki for the ISYM default),
its git blob SHA-1 recomputed from the bytes and compared with the API's, and its sha256
recorded. Only extracted lines and hashes are written; source files are not redistributed.

Gating checks 1-5 test the statement at the two named commits. Two scope checks set the
wording of the dated statement (docs/43 :1910), which narrows when either fails:
 4b  every pymatgen release admitted by setup.py's install_requires at d2742a3b and first
     uploaded to PyPI before the ISYM commit: sdist sha256 against PyPI, then ISYM lines in
     MVLSlabSet's in-file inheritance chain and in the YAML configs that chain loads;
 7   every version of adsorption.py the commits API lists on the default branch from
     a7d5f316 to the head: ISYM 0 under the comment in MPSurfaceSet, MPSurfaceSet as the
     workflow default, a7d5f316 an ancestor of the head (compare API).
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import io
import json
import os
import re
import sys
import tarfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
ATOMATE = "hackingmaterials/atomate"
PYMATGEN = "materialsproject/pymatgen"
ADS_PATH = "atomate/vasp/workflows/base/adsorption.py"
COMMIT_ISYM = "a7d5f316"
COMMIT_2017 = "d2742a3b"
COMMENT = "# Should give better forces for optimization"
VASP_WIKI_ISYM = "https://www.vasp.at/wiki/index.php/ISYM"
PYPI_JSON = "https://pypi.org/pypi/pymatgen/json"
DEFAULT_SET_RE = r"vasp_input_set\s*=\s*vasp_input_set or MPSurfaceSet\("


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _get(url: str, accept: str = "application/vnd.github+json") -> bytes:
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "sts-electrocatalyst-p-builder-gate"})
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and url.startswith(API):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def get_json(url: str):
    return json.loads(_get(url))


def get_file(repo: str, path: str, ref: str) -> dict:
    d = get_json(f"{API}/repos/{repo}/contents/{path}?ref={ref}")
    data = base64.b64decode(d["content"])
    return dict(repo=repo, path=path, ref=ref, api_blob_sha=d["sha"], blob_sha_recomputed=git_blob_sha1(data),
                blob_sha_match=d["sha"] == git_blob_sha1(data), sha256=hashlib.sha256(data).hexdigest(),
                n_bytes=len(data), text=data.decode("utf-8"))


# ---------------------------------------------------------------- pure evaluation helpers

def find_lines(text: str, pattern: str) -> list[dict]:
    rx = re.compile(pattern)
    return [dict(line=i, text=l.rstrip()) for i, l in enumerate(text.splitlines(), start=1) if rx.search(l)]


def class_span(text: str, class_name: str) -> tuple[int, int] | None:
    """1-based [start, end] line span of a top-level class body."""
    lines = text.splitlines()
    start = None
    for i, l in enumerate(lines, start=1):
        if start is None and re.match(rf"class {re.escape(class_name)}\b", l):
            start = i
            continue
        if start is not None and re.match(r"(class |def |@|[A-Za-z_])", l) and not l.startswith(" "):
            return start, i - 1
    return (start, len(lines)) if start is not None else None


def commented_block(text: str, comment_line: int, max_lines: int = 20) -> tuple[int, int]:
    """Lines governed by a comment: from the next line through the first line closing a
    dict literal ('}'), stopping at a blank line or after max_lines."""
    lines = text.splitlines()
    end = comment_line
    for i in range(comment_line + 1, min(len(lines), comment_line + max_lines) + 1):
        if not lines[i - 1].strip():
            break
        end = i
        if "}" in lines[i - 1]:
            break
    return comment_line + 1, end


def isym_under_comment(text: str, class_name: str, comment: str = COMMENT) -> dict:
    """True when a `"ISYM": 0` entry sits inside the statement the comment governs, inside the class."""
    span = class_span(text, class_name)
    isym = find_lines(text, r"""["']ISYM["']\s*:\s*0\b""")
    com = find_lines(text, re.escape(comment))
    out = dict(class_name=class_name, class_span=span, isym_lines=isym, comment_lines=com, ok=False)
    if not span:
        return out
    for c in com:
        if not span[0] <= c["line"] <= span[1]:
            continue
        lo, hi = commented_block(text, c["line"])
        hits = [x for x in isym if lo <= x["line"] <= hi]
        if hits:
            out.update(ok=True, isym_line=hits[0], comment_line=c, governed_block=[lo, hi])
            break
    return out


def class_base(text: str, class_name: str) -> str | None:
    m = re.search(rf"^class {re.escape(class_name)}\((\w+)\)", text, flags=re.M)
    return m.group(1) if m else None


def count_isym(text: str) -> int:
    return len(find_lines(text, r"\bISYM\b"))


def class_chain(text: str, class_name: str, max_depth: int = 10) -> list[str]:
    """class_name and its single-base ancestors defined in the same file, nearest first."""
    chain = []
    name = class_name
    while name and name not in chain and len(chain) < max_depth and class_span(text, name):
        chain.append(name)
        name = class_base(text, name)
    return chain


def class_body(text: str, class_name: str) -> str:
    span = class_span(text, class_name)
    return "\n".join(text.splitlines()[span[0] - 1:span[1]]) if span else ""


def setup_py_pymatgen_spec(text: str) -> list[dict]:
    return [dict(line=x["line"], text=x["text"], spec=m.group(1))
            for x in find_lines(text, r"""['"]pymatgen[<>=!~][^'"]*['"]""")
            for m in [re.search(r"""['"]pymatgen([<>=!~][^'"]*)['"]""", x["text"])]]


def function_body(text: str, name: str) -> str:
    lines = text.splitlines()
    start = None
    for i, l in enumerate(lines, start=1):
        if start is None and re.match(rf"def {re.escape(name)}\(", l):
            start = i
            continue
        if start is not None and l and not l[0].isspace() and not l.startswith(("#", ")")):
            return "\n".join(lines[start - 1:i - 1])
    return "\n".join(lines[start - 1:]) if start is not None else ""


YAML_LITERAL_RE = r"""["'](\w+)\.yaml["']"""
YAML_HELPER_RE = r"""_load_yaml_config\(\s*["'](\w+)["']\s*\)"""


def chain_yaml_names(sets_text: str, class_name: str = "MVLSlabSet") -> list[str]:
    """YAML configs loaded by the class chain: literal 'X.yaml' references in the class bodies, and
    _load_yaml_config("X") calls plus every 'Y.yaml' literal inside that helper's body."""
    names = []
    helper = function_body(sets_text, "_load_yaml_config")
    for c in class_chain(sets_text, class_name):
        body = class_body(sets_text, c)
        names += re.findall(YAML_LITERAL_RE, body)
        called = re.findall(YAML_HELPER_RE, body)
        names += called
        if called:
            names += re.findall(YAML_LITERAL_RE, helper)
    return list(dict.fromkeys(names))


def mvlslabset_chain_isym(sets_text: str, yaml_texts: dict) -> dict:
    """ISYM lines in MVLSlabSet's in-file inheritance chain and in the YAML configs the chain loads
    (following PARENT keys). yaml_texts: {config name: text or None}."""
    chain = class_chain(sets_text, "MVLSlabSet")
    per_class = {c: count_isym(class_body(sets_text, c)) for c in chain}
    yaml_names = chain_yaml_names(sets_text)
    per_yaml, seen = {}, []
    queue = list(yaml_names)
    while queue:
        name = queue.pop(0)
        if name in seen:
            continue
        seen.append(name)
        t = yaml_texts.get(name)
        per_yaml[name] = None if t is None else count_isym(t)
        if t:
            queue += re.findall(r"^PARENT:\s*(\w+)", t, flags=re.M)
    ok = bool(chain and chain[0] == "MVLSlabSet" and yaml_names and all(v == 0 for v in per_class.values())
              and all(v == 0 for v in per_yaml.values()))
    return dict(chain=chain, isym_lines_per_class=per_class, yaml_configs=seen, isym_lines_per_yaml=per_yaml,
                class_line=find_lines(sets_text, r"^class MVLSlabSet\("), ok=ok)


def vasp_isym_default(page_html: str) -> dict:
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", page_html, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"\s+", " ", t)
    m = re.search(r"Default: (ISYM = .*?) Description:", t)
    rev = re.search(r'"wgCurRevisionId":(\d+)', page_html)
    default_text = m.group(1).strip() if m else None
    paw = None
    if default_text:
        mm = re.search(r"= (\d) else", default_text)
        paw = int(mm.group(1)) if mm else None
    return dict(default_text=default_text, revision_id=int(rev.group(1)) if rev else None, default_else=paw)


# ---------------------------------------------------------------- the gate

def _strip(f: dict) -> dict:
    return {k: v for k, v in f.items() if k != "text"}


def _sdist_members(data: bytes, filename: str, wanted_suffixes: dict) -> dict:
    """{key: text} for the first archive member whose path ends with each wanted suffix."""
    found = {}
    if filename.endswith((".tar.gz", ".tgz", ".tar.bz2")):
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
            for m in tf.getmembers():
                for key, suf in wanted_suffixes.items():
                    if key not in found and m.isfile() and m.name.endswith(suf) and m.name.count("/") == suf.count("/") + 1:
                        found[key] = tf.extractfile(m).read().decode("utf-8")
    elif filename.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                for key, suf in wanted_suffixes.items():
                    if key not in found and name.endswith(suf) and name.count("/") == suf.count("/") + 1:
                        found[key] = zf.read(name).decode("utf-8")
    return found


def pymatgen_releases_check(spec: str, before_utc: str) -> dict:
    """Every pymatgen release on PyPI admitted by `spec` whose first file was uploaded before
    `before_utc`: download its sdist, verify PyPI's sha256, and count ISYM in MVLSlabSet's chain."""
    from packaging.specifiers import SpecifierSet
    from packaging.version import InvalidVersion, Version
    meta = get_json(PYPI_JSON)
    spec_set = SpecifierSet(spec)
    before = before_utc.replace("Z", "")
    selected = []
    for v, files in meta["releases"].items():
        if not files:
            continue
        try:
            ver = Version(v)
        except InvalidVersion:
            continue
        first = min(f["upload_time_iso_8601"] for f in files)
        if ver in spec_set and first.replace("Z", "") < before:
            selected.append((ver, v, first, files))
    selected.sort()
    rows = []
    for _, v, first, files in selected:
        sd = [f for f in files if f["packagetype"] == "sdist"]
        row = dict(version=v, first_upload_utc=first)
        if not sd:
            rows.append(dict(row, ok=False, reason="no sdist on PyPI"))
            continue
        f = sd[0]
        data = _get(f["url"], accept="application/octet-stream")
        digest = hashlib.sha256(data).hexdigest()
        sets_suffix = "pymatgen/io/vasp/sets.py"
        texts = _sdist_members(data, f["filename"], {"sets": sets_suffix})
        sets_text = texts.get("sets")
        yaml_names = set(chain_yaml_names(sets_text)) if sets_text else set()
        yamls = _sdist_members(data, f["filename"], {n: f"pymatgen/io/vasp/{n}.yaml" for n in yaml_names})
        # follow PARENT keys once more (config inheritance)
        parents = {p for t in yamls.values() for p in re.findall(r"^PARENT:\s*(\w+)", t, flags=re.M)} - set(yamls)
        if parents:
            yamls.update(_sdist_members(data, f["filename"], {n: f"pymatgen/io/vasp/{n}.yaml" for n in parents}))
        res = mvlslabset_chain_isym(sets_text, yamls) if sets_text else dict(ok=False, reason="sets.py not found")
        rows.append(dict(row, sdist=f["filename"], sdist_sha256=digest, pypi_sha256=f["digests"]["sha256"],
                         sha256_match=digest == f["digests"]["sha256"],
                         sets_py_sha256=hashlib.sha256(sets_text.encode("utf-8")).hexdigest() if sets_text else None,
                         **res))
    return dict(source=PYPI_JSON, specifier=spec, uploaded_before_utc=before_utc, n_releases=len(rows),
                releases=rows)


def default_branch_history(head_sha: str, since_commit: dict) -> dict:
    """Every commit the GitHub API lists for ADS_PATH on the default branch from `since_commit`
    (inclusive) to the head, each version checked for ISYM 0 under the comment and for MPSurfaceSet
    as the workflow default."""
    rows, page = [], 1
    since = since_commit["commit"]["committer"]["date"][:10] + "T00:00:00Z"  # day start; truncated below
    while True:
        batch = get_json(f"{API}/repos/{ATOMATE}/commits?path={ADS_PATH}&sha={head_sha}&since={since}"
                         f"&per_page=100&page={page}")
        rows += batch
        if len(batch) < 100:
            break
        page += 1
    shas = [c["sha"] for c in rows]
    since_listed = since_commit["sha"] in shas
    n_before = len(rows) - shas.index(since_commit["sha"]) - 1 if since_listed else None
    if since_listed:
        rows = rows[:shas.index(since_commit["sha"]) + 1]
    versions = []
    for c in rows:
        f = get_file(ATOMATE, ADS_PATH, c["sha"])
        u = isym_under_comment(f["text"], "MPSurfaceSet")
        versions.append(dict(sha=c["sha"], committer_date=c["commit"]["committer"]["date"],
                             message=c["commit"]["message"].splitlines()[0], blob_sha=f["api_blob_sha"],
                             blob_sha_match=f["blob_sha_match"], isym_under_comment_ok=u["ok"],
                             isym_line=u.get("isym_line"), comment_line=u.get("comment_line"),
                             default_input_set_lines=find_lines(f["text"], DEFAULT_SET_RE)))
    cmp = get_json(f"{API}/repos/{ATOMATE}/compare/{since_commit['sha']}...{head_sha}")
    return dict(listed_newest_first=versions, since_commit_listed=since_listed,
                n_same_day_commits_before_since_commit_dropped=n_before, compare_status=cmp["status"],
                compare_ahead_by=cmp["ahead_by"], compare_behind_by=cmp["behind_by"])


def run_gate() -> dict:
    rec = dict(checked_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), sources={}, checks={})
    # 1-2: the ISYM commit
    c1 = get_json(f"{API}/repos/{ATOMATE}/commits/{COMMIT_ISYM}")
    patch_files = [dict(filename=f["filename"], additions=f["additions"], deletions=f["deletions"],
                        added_isym=[l for l in f.get("patch", "").splitlines() if l.startswith("+") and "ISYM" in l],
                        removed_isym=[l for l in f.get("patch", "").splitlines() if l.startswith("-") and "ISYM" in l])
                   for f in c1["files"]]
    rec["sources"]["commit_isym"] = dict(sha=c1["sha"], author=c1["commit"]["author"]["name"],
                                         author_date=c1["commit"]["author"]["date"],
                                         committer_date=c1["commit"]["committer"]["date"],
                                         message=c1["commit"]["message"], parents=[p["sha"] for p in c1["parents"]],
                                         files=patch_files, url=c1["html_url"])
    f_isym = get_file(ATOMATE, ADS_PATH, c1["sha"])
    under = isym_under_comment(f_isym["text"], "MPSurfaceSet")
    rec["sources"]["adsorption_py_at_isym_commit"] = dict(
        **_strip(f_isym), mpsurfaceset_base=class_base(f_isym["text"], "MPSurfaceSet"), isym_under_comment=under,
        mpsurfaceset_uses=find_lines(f_isym["text"], r"MPSurfaceSet\((?!MVLSlabSet)"),
        user_incar_settings_updates=find_lines(f_isym["text"], r"incar\.update\(self\.user_incar_settings\)"))
    f_parent = get_file(ATOMATE, ADS_PATH, c1["parents"][0]["sha"])
    rec["sources"]["adsorption_py_at_parent"] = dict(**_strip(f_parent), isym_count=count_isym(f_parent["text"]),
                                                     comment_lines=find_lines(f_parent["text"], re.escape(COMMENT)))
    # comment origin: walk the file history before the ISYM commit
    hist = get_json(f"{API}/repos/{ATOMATE}/commits?path={ADS_PATH}&until={c1['commit']['committer']['date']}"
                    f"&per_page=15")
    origin = None
    for h in hist:
        if h["sha"] == c1["sha"]:
            continue
        ch = get_json(f"{API}/repos/{ATOMATE}/commits/{h['sha']}")
        patch = "".join(f.get("patch", "") for f in ch["files"] if f["filename"] == ADS_PATH)
        added = any(l.startswith("+") and COMMENT in l for l in patch.splitlines())
        removed = any(l.startswith("-") and COMMENT in l for l in patch.splitlines())
        if added and not removed:
            parent_file = get_file(ATOMATE, ADS_PATH, ch["parents"][0]["sha"])
            if not find_lines(parent_file["text"], re.escape(COMMENT)):
                origin = dict(sha=ch["sha"], committer_date=ch["commit"]["committer"]["date"],
                              message=ch["commit"]["message"],
                              added_class_lines=[l for l in patch.splitlines() if l.startswith("+class ")],
                              parent_has_comment=False)
                break
    rec["sources"]["comment_origin"] = origin
    # 3-5: the 2017 commit, its pymatgen pin, MVLSlabSet and MPRelaxSet at that pin
    c2 = get_json(f"{API}/repos/{ATOMATE}/commits/{COMMIT_2017}")
    rec["sources"]["commit_2017"] = dict(sha=c2["sha"], author=c2["commit"]["author"]["name"],
                                         author_date=c2["commit"]["author"]["date"],
                                         committer_date=c2["commit"]["committer"]["date"],
                                         message=c2["commit"]["message"], url=c2["html_url"])
    f2017 = get_file(ATOMATE, ADS_PATH, c2["sha"])
    rec["sources"]["adsorption_py_at_2017_commit"] = dict(
        **_strip(f2017), mvlslabset_default_lines=find_lines(f2017["text"], r"vasp_input_set\s*=\s*vasp_input_set or MVLSlabSet"),
        mvlslabset_import=find_lines(f2017["text"], r"import .*MVLSlabSet"), isym_count=count_isym(f2017["text"]))
    req = get_file(ATOMATE, "requirements.txt", c2["sha"])
    pin = find_lines(req["text"], r"^pymatgen==")
    version = pin[0]["text"].split("==")[1].strip() if pin else None
    rec["sources"]["requirements_at_2017_commit"] = dict(**_strip(req), pymatgen_pin=pin, pymatgen_version=version)
    setup = get_file(ATOMATE, "setup.py", c2["sha"])
    spec_lines = setup_py_pymatgen_spec(setup["text"])
    rec["sources"]["setup_py_at_2017_commit"] = dict(**_strip(setup), pymatgen_install_requires=spec_lines)
    if len(spec_lines) == 1:
        rec["sources"]["pymatgen_releases_admitted_before_isym_commit"] = pymatgen_releases_check(
            spec_lines[0]["spec"], c1["commit"]["committer"]["date"])
    if version:
        tag = get_json(f"{API}/repos/{PYMATGEN}/git/ref/tags/v{version}")
        sets = get_file(PYMATGEN, "pymatgen/io/vasp/sets.py", f"v{version}")
        span = class_span(sets["text"], "MVLSlabSet")
        body = "\n".join(sets["text"].splitlines()[span[0] - 1:span[1]]) if span else ""
        yaml = get_file(PYMATGEN, "pymatgen/io/vasp/MPRelaxSet.yaml", f"v{version}")
        rec["sources"]["pymatgen_at_pin"] = dict(
            tag=f"v{version}", tag_object=tag["object"], sets_py=_strip(sets),
            mvlslabset_class_line=find_lines(sets["text"], r"^class MVLSlabSet\("),
            mvlslabset_base=class_base(sets["text"], "MVLSlabSet"), mvlslabset_span=span,
            isym_in_mvlslabset=count_isym(body),
            mprelaxset_yaml=_strip(yaml), isym_in_mprelaxset_yaml=count_isym(yaml["text"]),
            lhfcalc_in_mprelaxset_yaml=len(find_lines(yaml["text"], r"LHFCALC")))
    # 6: VASP default
    page = _get(VASP_WIKI_ISYM, accept="text/html").decode("utf-8", errors="replace")
    rec["sources"]["vasp_wiki_isym"] = dict(url=VASP_WIKI_ISYM, sha256=hashlib.sha256(page.encode("utf-8")).hexdigest(),
                                            **vasp_isym_default(page))
    # 7: current default branch
    repo = get_json(f"{API}/repos/{ATOMATE}")
    head = get_json(f"{API}/repos/{ATOMATE}/commits/{repo['default_branch']}")
    fmain = get_file(ATOMATE, ADS_PATH, head["sha"])
    rec["sources"]["adsorption_py_at_default_branch"] = dict(
        branch=repo["default_branch"], commit=head["sha"], committer_date=head["commit"]["committer"]["date"],
        **_strip(fmain), isym_under_comment=isym_under_comment(fmain["text"], "MPSurfaceSet"))
    rec["sources"]["default_branch_history_since_isym_commit"] = default_branch_history(head["sha"], c1)
    rec["checks"] = evaluate(rec["sources"], rec["checked_utc"])
    return rec


def _history_check(src: dict) -> dict:
    h = src.get("default_branch_history_since_isym_commit")
    head = src["adsorption_py_at_default_branch"]
    if not h:
        return dict(ok=False, detail=None)
    v = h["listed_newest_first"]
    ok = bool(v and h["since_commit_listed"] and v[-1]["sha"] == src["commit_isym"]["sha"]
              and h["compare_status"] in ("ahead", "identical")
              and all(x["blob_sha_match"] and x["isym_under_comment_ok"] and x["default_input_set_lines"] for x in v)
              and v[0]["blob_sha"] == head["api_blob_sha"])
    return dict(ok=ok, detail=dict(
        n_versions=len(v), oldest=v[-1]["sha"] if v else None, newest=v[0]["sha"] if v else None,
        newest_date=v[0]["committer_date"] if v else None, head=head["commit"], head_date=head["committer_date"],
        head_blob_equals_newest_listed=bool(v and v[0]["blob_sha"] == head["api_blob_sha"]),
        compare_status=h["compare_status"], compare_ahead_by=h["compare_ahead_by"],
        versions=[dict(sha=x["sha"][:12], date=x["committer_date"], isym_line=(x["isym_line"] or {}).get("line"),
                       comment_line=(x["comment_line"] or {}).get("line"),
                       default_lines=[y["line"] for y in x["default_input_set_lines"]],
                       ok=bool(x["blob_sha_match"] and x["isym_under_comment_ok"] and x["default_input_set_lines"]))
                  for x in v]))


def _releases_check(src: dict) -> dict:
    s = src.get("setup_py_at_2017_commit")
    r = src.get("pymatgen_releases_admitted_before_isym_commit")
    if not s or not r:
        return dict(ok=False, detail=dict(setup_py=s and s.get("pymatgen_install_requires")))
    rows = r["releases"]
    ok = bool(s["blob_sha_match"] and rows and all(x.get("ok") and x.get("sha256_match") for x in rows))
    failing = [x["version"] for x in rows if not (x.get("ok") and x.get("sha256_match"))]
    chains = sorted({" -> ".join(x.get("chain", [])) for x in rows})
    return dict(ok=ok, detail=dict(
        setup_py_line=s["pymatgen_install_requires"], specifier=r["specifier"], uploaded_before_utc=r["uploaded_before_utc"],
        n_releases=len(rows), first=rows[0]["version"] if rows else None, last=rows[-1]["version"] if rows else None,
        n_sdist_sha256_match=sum(1 for x in rows if x.get("sha256_match")),
        n_no_isym=sum(1 for x in rows if x.get("ok")), failing=failing, chains=chains,
        yaml_configs=sorted({y for x in rows for y in x.get("yaml_configs", [])})))


def dated_statement(checks: dict, src: dict, checked_utc: str | None) -> dict:
    """The docs/43 :1910 dated statement, worded from the checks (narrowed when a scope check fails)."""
    c1, c2 = src["commit_isym"], src["commit_2017"]
    h = checks["7_isym0_every_default_branch_version_since_a7d5f316"]
    r = checks["4b_MVLSlabSet_chain_no_ISYM_every_admitted_release_before_a7d5f316"]
    if h["ok"]:
        d = h["detail"]
        first = (f"MPSurfaceSet, the default input set of atomate's adsorption workflow, sets ISYM = 0 in every "
                 f"version of {ADS_PATH} on the default branch from {c1['sha'][:8]} ({c1['committer_date'][:10]}) "
                 f"through {d['newest'][:8]} ({d['newest_date'][:10]}), {d['n_versions']} versions, unless the caller "
                 f"overrides it through user_incar_settings; the default-branch head {d['head'][:8]} carries the last "
                 f"of them (checked {checked_utc}).")
    else:
        first = (f"MPSurfaceSet sets ISYM = 0 at {c1['sha'][:8]} ({c1['committer_date'][:10]}) and at the "
                 f"default-branch head {src['adsorption_py_at_default_branch']['commit'][:8]} as inspected on "
                 f"{checked_utc}; versions in between were not established.")
    pin = src["requirements_at_2017_commit"]["pymatgen_version"]
    if r["ok"]:
        d = r["detail"]
        second = (f"At {c2['sha'][:8]} ({c2['committer_date'][:10]}) the workflow default was MVLSlabSet; no class in "
                  f"its chain ({'; '.join(d['chains'])}) and no config it loads ({', '.join(d['yaml_configs'])}) sets "
                  f"ISYM in any of the {d['n_releases']} pymatgen releases admitted by setup.py's "
                  f"'pymatgen{d['specifier']}' and first uploaded to PyPI before {d['uploaded_before_utc']} "
                  f"({d['first']} to {d['last']}; requirements.txt pinned {pin}), so under that default VASP's own "
                  f"ISYM default applied unless the caller set ISYM.")
    else:
        second = (f"At {c2['sha'][:8]} ({c2['committer_date'][:10]}) the workflow default was MVLSlabSet, which sets "
                  f"no ISYM in the pinned pymatgen {pin}; other releases admitted by setup.py were not established.")
    return dict(text=[first, second], since_wording_supported=h["ok"], all_admitted_releases_checked=r["ok"])


def evaluate(src: dict, checked_utc: str | None = None) -> dict:
    c1 = src["commit_isym"]
    f1 = src["adsorption_py_at_isym_commit"]
    par = src["adsorption_py_at_parent"]
    origin = src.get("comment_origin")
    c2 = src["commit_2017"]
    f2 = src["adsorption_py_at_2017_commit"]
    pm = src.get("pymatgen_at_pin", {})
    vw = src["vasp_wiki_isym"]
    ads_file_added_isym = [f for f in c1["files"] if f["filename"] == ADS_PATH and f["added_isym"]]
    checks = {
        "1_isym0_in_MPSurfaceSet_under_comment_at_a7d5f316": dict(
            ok=bool(f1["isym_under_comment"]["ok"] and f1["blob_sha_match"] and c1["sha"].startswith(COMMIT_ISYM)),
            detail=dict(isym_line=f1["isym_under_comment"].get("isym_line"),
                        comment_line=f1["isym_under_comment"].get("comment_line"),
                        class_span=f1["isym_under_comment"]["class_span"], base_class=f1["mpsurfaceset_base"],
                        mpsurfaceset_uses=f1.get("mpsurfaceset_uses"),
                        user_incar_settings_updates=f1.get("user_incar_settings_updates"))),
        "2_introduced_2018_05_25_by_a7d5f316": dict(
            ok=bool(c1["committer_date"].startswith("2018-05-25") and ads_file_added_isym and par["isym_count"] == 0),
            detail=dict(committer_date=c1["committer_date"], message=c1["message"], parent=c1["parents"][0],
                        parent_isym_count=par["isym_count"], added_lines=[f["added_isym"] for f in ads_file_added_isym])),
        "2q_comment_predates_isym": dict(
            ok=bool(origin and origin["sha"] != c1["sha"]),
            detail=origin,
            note="qualifier: the comment was added with the class, before ISYM was added under it"),
        "3_d2742a3b_uses_MVLSlabSet_no_ISYM": dict(
            ok=bool(c2["sha"].startswith(COMMIT_2017) and c2["committer_date"].startswith("2017")
                    and f2["mvlslabset_default_lines"] and f2["isym_count"] == 0 and f2["blob_sha_match"]),
            detail=dict(committer_date=c2["committer_date"], default_lines=f2["mvlslabset_default_lines"],
                        import_lines=f2["mvlslabset_import"], isym_count=f2["isym_count"])),
        "4_MVLSlabSet_at_pinned_pymatgen_sets_no_ISYM": dict(
            ok=bool(pm and pm["isym_in_mvlslabset"] == 0 and pm["isym_in_mprelaxset_yaml"] == 0
                    and pm["sets_py"]["blob_sha_match"] and pm["mprelaxset_yaml"]["blob_sha_match"]),
            detail=dict(pin=src["requirements_at_2017_commit"]["pymatgen_pin"], tag=pm.get("tag"),
                        class_line=pm.get("mvlslabset_class_line"), base=pm.get("mvlslabset_base"),
                        isym_in_class=pm.get("isym_in_mvlslabset"), isym_in_yaml=pm.get("isym_in_mprelaxset_yaml"),
                        lhfcalc_in_yaml=pm.get("lhfcalc_in_mprelaxset_yaml"))),
        "5_vasp_default_isym_2": dict(
            ok=bool(vw["default_else"] == 2),
            detail=dict(default_text=vw["default_text"], revision_id=vw["revision_id"]),
            note="qualifier: 2 for PAW without LHFCALC; 1 with USPPs; 3 if LHFCALC=.TRUE."),
        "6_default_branch_still_isym0": dict(
            ok=bool(src["adsorption_py_at_default_branch"]["isym_under_comment"]["ok"]),
            detail=dict(commit=src["adsorption_py_at_default_branch"]["commit"],
                        isym_line=src["adsorption_py_at_default_branch"]["isym_under_comment"].get("isym_line"))),
    }
    checks["4b_MVLSlabSet_chain_no_ISYM_every_admitted_release_before_a7d5f316"] = dict(
        **_releases_check(src),
        note="scope: setup.py admits pymatgen>=4.7.1 while requirements.txt pins 4.7.7; every admitted release "
             "uploaded before the ISYM commit is checked from its PyPI sdist")
    checks["7_isym0_every_default_branch_version_since_a7d5f316"] = dict(
        **_history_check(src),
        note="scope: every commit the GitHub commits API lists for the file on the default branch since a7d5f316")
    gating = ["1_isym0_in_MPSurfaceSet_under_comment_at_a7d5f316", "2_introduced_2018_05_25_by_a7d5f316",
              "3_d2742a3b_uses_MVLSlabSet_no_ISYM", "4_MVLSlabSet_at_pinned_pymatgen_sets_no_ISYM",
              "5_vasp_default_isym_2"]
    checks["GATE"] = dict(passed=all(checks[k]["ok"] for k in gating), gating_checks=gating,
                          scope_checks=["4b_MVLSlabSet_chain_no_ISYM_every_admitted_release_before_a7d5f316",
                                        "7_isym0_every_default_branch_version_since_a7d5f316"],
                          qualifiers=[checks["2q_comment_predates_isym"]["note"], checks["5_vasp_default_isym_2"]["note"]])
    checks["DATED_STATEMENT"] = dated_statement(checks, src, checked_utc)
    return checks


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--reevaluate", action="store_true",
                    help="recompute checks offline from the sources already recorded in --out (no network)")
    args = ap.parse_args(argv)
    if args.reevaluate:
        rec = json.loads(args.out.read_text(encoding="utf-8"))
        rec["checks"] = evaluate(rec["sources"], rec["checked_utc"])
    else:
        rec = run_gate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.write("\n")
    for k, v in rec["checks"].items():
        print(k, v.get("ok", v.get("passed", v.get("since_wording_supported"))))
    return 0 if rec["checks"]["GATE"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
