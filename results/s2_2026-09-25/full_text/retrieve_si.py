"""Supporting-information retrieval for records a full-text pass marked NEEDS_SI.

Uses the same dedicated browser profile as retrieve_browser.py, so run it only after that
script has finished.  For each record: open the article through the Purdue proxy, collect
links that look like supplementary files, and fetch the PDF ones inside the session.
  - ACS: /doi/suppl/...
  - RSC: suppdata
  - Elsevier: mmc
  - Wiley: downloadSupplement
  - Springer/Nature: MOESM
  - IOP, AIP, MDPI: "supplementary" / "supporting" in the link text or URL
Files land in files_si/<sid>_SI<k>.pdf; every attempt goes to si_log.jsonl.  Files stay
local.  Nothing here reads the SI or decides eligibility.

  python retrieve_si.py [--limit N]

Rate-limited through retrieve_browser.PurdueGate (40 proxied landings per hour, stops at the
first sign of an EZproxy block).
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import time
import urllib.parse

from playwright.sync_api import sync_playwright

from retrieve_browser import PurdueGate

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "files_si"
PROXY = "https://login.ezproxy.lib.purdue.edu/login?url=https://doi.org/"
PATTERNS = ("/doi/suppl/", "suppdata", "mmc", "downloadsupplement", "moesm", "supplementary", "supporting",
            "/suppl/", "esi")


def log(entry):
    entry["at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    with open(HERE / "si_log.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry) + "\n")


def needs_si():
    """Records with NEEDS_SI in either pass, with their DOI."""
    out = {}
    for n in ("1", "2"):
        for p in sorted((HERE / ("pass_%s" % n) / "batches").glob("*.out.jsonl")):
            for line in open(p, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    if r.get("disposition") == "NEEDS_SI" and r.get("doi"):
                        out.setdefault(r["screen_id"], r["doi"])
    return out


def si_links(page):
    links = page.evaluate("""() => Array.from(document.querySelectorAll('a[href]')).map(a =>
                               [a.href, (a.textContent || '').trim().slice(0, 80)])""")
    keep = []
    for href, text in links:
        h, t = href.lower(), text.lower()
        if any(k in h for k in PATTERNS) or "supplement" in t or "supporting" in t or "electronic supplementary" in t:
            if href not in [k[0] for k in keep]:
                keep.append((href, text))
    return keep


def fetch(ctx, sid, k, url):
    try:
        resp = ctx.request.get(url, timeout=90000)
        body = resp.body()
    except Exception as e:
        log(dict(screen_id=sid, url=url, status="ERROR", accepted=False, error=str(e)[:160]))
        return False
    ok = body[:5] == b"%PDF-"
    entry = dict(screen_id=sid, url=url, status=resp.status, bytes=len(body), accepted=ok)
    if ok:
        entry["sha256"] = hashlib.sha256(body).hexdigest()
        (OUT / ("%s_SI%d.pdf" % (sid, k))).write_bytes(body)
    log(entry)
    return ok


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None)
    a = p.parse_args()
    OUT.mkdir(exist_ok=True)
    have = {f.name.split("_SI")[0] for f in OUT.iterdir()}
    todo = sorted((s, d) for s, d in needs_si().items() if s not in have)[: a.limit]
    print(len(todo), "records need SI", flush=True)
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(str(HERE / ".browser_profile"), channel="chrome",
                                                    headless=False, accept_downloads=True)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        got, gate = 0, PurdueGate()
        for sid, doi in todo:
            gate.wait()
            try:
                resp = page.goto(PROXY + doi, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(3000)
                if not gate.inspect(page, resp.status if resp else None):
                    break
                links = si_links(page)
            except Exception as e:
                log(dict(screen_id=sid, url=doi, status="ERROR", accepted=False, error=str(e)[:160]))
                continue
            log(dict(screen_id=sid, route="landing", url=page.url.split("?")[0], si_links=len(links)))
            k, ok_any = 0, False
            for href, _ in links[:8]:
                url = urllib.parse.urljoin(page.url, href)
                time.sleep(20)  # SI files also pass through the proxy
                if fetch(ctx, sid, k + 1, url):
                    k += 1
                    ok_any = True
            got += ok_any
            print(sid, "SI x%d" % k if ok_any else "--", flush=True)
            time.sleep(1.5)
        print(got, "of", len(todo), "with SI")
        ctx.close()


if __name__ == "__main__":
    main()
