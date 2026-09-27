"""Public supporting-information retrieval (entrant's decision of 2026-09-27: "Download freely available
SI directly from official publisher pages, slowly ... No Purdue proxy ... Respect access blocks and
leave unsuccessful downloads unresolved").

  python retrieve_si_public.py [--limit N] [--ids S1,S2] [--no-browser]

Records: every record whose decision in reconcile/current_state.csv (v4_final) is NEEDS_SI or UNRESOLVED,
plus any --ids.  Routes, in order; a record stops at the first route that yields SI files:
  1. Europe PMC  /{pmcid}/supplementaryFiles for records with an open-access PMC copy (zip, unpacked).
  2. figshare    the figshare API (api.figshare.com), items whose resource_doi is the article DOI; this is
                 where ACS publishes its supporting information.
  3. publisher   the article page (https://doi.org/<doi>) in a normal browser window with its own profile,
                 no proxy.  Only a page served directly counts: if the first document response is not 200,
                 or the page is an interstitial check ("Just a moment", "Client Challenge", captcha ...),
                 the attempt is logged BLOCKED and that publisher is skipped for the rest of the run.  No
                 check is solved or clicked through.  Only SI links present on the loaded page are fetched.
                 When the page loads and shows no SI link, that is logged as NO_SI_LINK_ON_PAGE with the
                 page's visible text saved locally (evidence for the D10 no-SI check, reviewed before use).
Spacing: >= 30 s (+ jitter) between publisher page loads, >= 1 s between API calls.  Files go to
files_si/<sid>_SI<k>.<ext> (local only, never committed); every attempt goes to si_public_log.jsonl.
Nothing here reads the SI or decides eligibility.
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import pathlib
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

HERE = pathlib.Path(__file__).resolve().parent
SI = HERE / "files_si"
PAGES = HERE / "si_pages"
LOG = HERE / "si_public_log.jsonl"
KEEP = (".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".zip")
CHALLENGE = re.compile(r"just a moment|client challenge|attention required|verify you are human|are you a robot|"
                       r"captcha|unusual traffic|access denied|perfdrive|cf-chl", re.I)
SI_LINK = re.compile(r"/doi/suppl/|suppdata|downloadsupplement|moesm|/esm/|mmc\d|supplementary|supporting", re.I)
UA = "sts-plit-si/1.0 (literature census; public supporting information only)"


def log(entry):
    entry["at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    with open(LOG, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry) + "\n")


def api(url, data=None):
    time.sleep(1.0)
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **({"Content-Type": "application/json"} if data else {})})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def save(sid, k, name, body, route, url):
    ext = pathlib.Path(urllib.parse.urlparse(name).path).suffix.lower() or ".bin"
    if ext not in KEEP:
        log(dict(screen_id=sid, route=route, url=url, status="SKIPPED_TYPE", ext=ext))
        return False
    p = SI / ("%s_SI%d%s" % (sid, k, ext))
    p.write_bytes(body)
    log(dict(screen_id=sid, route=route, url=url, status="OK", file=p.name, bytes=len(body),
             sha256=hashlib.sha256(body).hexdigest()))
    return True


def via_epmc(sid, pmcid):
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/%s/supplementaryFiles" % pmcid
    try:
        body = api(url)
        z = zipfile.ZipFile(io.BytesIO(body))
    except Exception as e:
        log(dict(screen_id=sid, route="epmc_si", url=url, status="ERROR", error=str(e)[:160]))
        return 0
    k = 0
    for n in z.namelist():
        if n.endswith("/") or n.lower().endswith((".xml", ".jpg", ".gif", ".png", ".tif")):
            continue
        k += save(sid, k + 1, n, z.read(n), "epmc_si", url + "#" + n)
    if not k:
        log(dict(screen_id=sid, route="epmc_si", url=url, status="NO_FILES"))
    return k


def via_figshare(sid, doi):
    url = "https://api.figshare.com/v2/articles/search"
    try:
        hits = [h for h in json.loads(api(url, json.dumps({"resource_doi": doi, "page_size": 20}).encode()))
                if (h.get("resource_doi") or "").lower() == doi.lower()]
    except Exception as e:
        log(dict(screen_id=sid, route="figshare", url=doi, status="ERROR", error=str(e)[:160]))
        return 0
    k = 0
    for h in hits:
        try:
            item = json.loads(api("https://api.figshare.com/v2/articles/%s" % h["id"]))
        except Exception as e:
            log(dict(screen_id=sid, route="figshare", url=str(h.get("id")), status="ERROR", error=str(e)[:160]))
            continue
        for f in item.get("files") or []:
            if not f.get("name", "").lower().endswith(KEEP):
                continue
            try:
                k += save(sid, k + 1, f["name"], api(f["download_url"]), "figshare", f["download_url"])
            except Exception as e:
                log(dict(screen_id=sid, route="figshare", url=f.get("download_url"), status="ERROR", error=str(e)[:160]))
    if not k:
        log(dict(screen_id=sid, route="figshare", url=doi, status="NO_ITEM" if not hits else "NO_FILES"))
    return k


class Pub:
    def __init__(self):
        self.last, self.blocked = 0.0, set()

    def wait(self):
        time.sleep(max(0.0, self.last + 30 + random.uniform(0, 15) - time.time()))
        self.last = time.time()


def publisher(doi):
    return doi.split("/")[0]


def via_page(ctx, page, sid, doi, gate):
    pre = publisher(doi)
    if pre in gate.blocked:
        return 0
    gate.wait()
    try:
        resp = page.goto("https://doi.org/" + doi, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        status = resp.status if resp else None
        title = page.title() or ""
        text = page.inner_text("body")[:6000]
    except Exception as e:
        log(dict(screen_id=sid, route="publisher_page", url=doi, status="ERROR", error=str(e)[:160]))
        return 0
    host = urllib.parse.urlparse(page.url).netloc
    if status != 200 or CHALLENGE.search(title) or (len(text) < 1500 and CHALLENGE.search(text)):
        gate.blocked.add(pre)
        log(dict(screen_id=sid, route="publisher_page", url=page.url.split("?")[0], status="BLOCKED", http=status,
                 title=title[:80], note="access check; publisher %s skipped for this run" % pre))
        print("blocked at", host, "- skipping prefix", pre, flush=True)
        return 0
    links = page.evaluate("""() => Array.from(document.querySelectorAll('a[href]')).map(a => [a.href, (a.innerText || '').trim().slice(0, 80)])""")
    si = []
    for href, label in links:
        if (SI_LINK.search(href) or re.search(r"supporting|supplementar|electronic supplementary", label, re.I)) \
                and re.search(r"\.(pdf|docx?|xlsx?|zip)(\?|$)|downloadsupplement|/suppl/|suppdata|moesm|mmc", href, re.I):
            if href not in si:
                si.append(href)
    if not si:
        PAGES.mkdir(exist_ok=True)
        (PAGES / (sid + ".txt")).write_text(page.inner_text("body"), encoding="utf-8")
        log(dict(screen_id=sid, route="publisher_page", url=page.url.split("?")[0], status="NO_SI_LINK_ON_PAGE", http=status,
                 page_text=("si_pages/%s.txt" % sid)))
        return 0
    k = 0
    for href in si[:8]:
        gate.wait()
        try:
            r = ctx.request.get(href, timeout=90000)
            body = r.body()
        except Exception as e:
            log(dict(screen_id=sid, route="publisher_si", url=href, status="ERROR", error=str(e)[:160]))
            continue
        ctype = (r.headers.get("content-type") or "").lower()
        if r.status != 200 or "text/html" in ctype:
            log(dict(screen_id=sid, route="publisher_si", url=href, status="NOT_FILE", http=r.status, ctype=ctype[:40]))
            continue
        name = href.split("?")[0]
        if not pathlib.Path(urllib.parse.urlparse(name).path).suffix and "pdf" in ctype:
            name += ".pdf"
        k += save(sid, k + 1, name, body, "publisher_si", href)
    return k


def records(ids):
    pmc = {}
    for l in open(HERE / "retrieval_log.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if e.get("route") == "epmc" and e.get("accepted"):
            pmc[e["screen_id"]] = e["url"]
    out = []
    for r in csv.DictReader(open(HERE / "reconcile" / "current_state.csv", encoding="utf-8")):
        if r["v4_final"] in ("NEEDS_SI", "UNRESOLVED") or r["screen_id"] in ids:
            out.append(dict(screen_id=r["screen_id"], doi=r["doi"], pmcid=pmc.get(r["screen_id"])))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int)
    p.add_argument("--ids", default="")
    p.add_argument("--no-browser", action="store_true")
    a = p.parse_args()
    SI.mkdir(exist_ok=True)
    done = {f.name.split("_SI")[0] for f in SI.iterdir()}
    tried_pages = set()
    if LOG.exists():
        for l in open(LOG, encoding="utf-8"):
            e = json.loads(l)
            if e.get("route") == "publisher_page" and e.get("status") in ("NO_SI_LINK_ON_PAGE",):
                tried_pages.add(e["screen_id"])
    recs = [r for r in records(set(filter(None, a.ids.split(",")))) if r["screen_id"] not in done and r["doi"]]
    recs.sort(key=lambda r: (publisher(r["doi"]), r["screen_id"]))
    recs = recs[: a.limit]
    print(len(recs), "records without SI", flush=True)
    need_page = []
    got = 0
    for r in recs:
        k = (via_epmc(r["screen_id"], r["pmcid"]) if r["pmcid"] else 0) or via_figshare(r["screen_id"], r["doi"])
        got += bool(k)
        print(r["screen_id"], "api", k, flush=True)
        if not k and r["screen_id"] not in tried_pages:
            need_page.append(r)
    if not a.no_browser and need_page:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            ctx = pw.chromium.launch_persistent_context(str(HERE / ".browser_profile_public"), channel="chrome",
                                                        headless=False, accept_downloads=True)
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            gate = Pub()
            # interleave publishers so one slow or blocked publisher does not hold the others
            seen = {}
            for r in need_page:
                pre = publisher(r["doi"])
                r["_rank"] = seen[pre] = seen.get(pre, -1) + 1
            need_page.sort(key=lambda r: (r["_rank"], publisher(r["doi"])))
            for r in need_page:
                k = via_page(ctx, page, r["screen_id"], r["doi"], gate)
                got += bool(k)
                print(r["screen_id"], "page", k, flush=True)
            ctx.close()
    print(got, "of", len(recs), "records got SI files")


if __name__ == "__main__":
    main()
