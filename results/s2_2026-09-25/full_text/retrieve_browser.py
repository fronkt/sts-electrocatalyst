"""Full-text retrieval, browser routes (see docs/research/full-text-access-amendment-2026-09-25.md).

Runs a dedicated, visible Chrome window (persistent profile in .browser_profile/, local only).
  1. Purdue University Libraries institutional access: open https://doi.org/<doi> through the
     library proxy, read the publisher's citation_pdf_url, fetch it inside the authenticated session.
  2. Sci-Hub (last fallback): open <mirror>/<doi> and fetch the embedded PDF if one is served.
The entrant logs in to Purdue once in the window (the script waits for it).  Records that already
have a file (from retrieve_http.py or an earlier browser run) are skipped.  Every attempt is logged
to browser_log.jsonl; files stay local.

  python retrieve_browser.py [--limit N] [--no-scihub] [--no-purdue]

Purdue rate limit (added 2026-09-26 after an EZproxy suspension caused by ~430 proxied page
loads per hour): at most PURDUE_PER_HOUR proxied landings, spaced with random jitter, and the
Purdue route shuts off for the rest of the run at the first sign of a block (see PurdueGate).
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import pathlib
import random
import time
import urllib.parse

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
FILES = HERE / "files"
PROXY = "https://login.ezproxy.lib.purdue.edu/login?url=https://doi.org/"
SCIHUB = ["https://sci-hub.ru/", "https://sci-hub.st/"]
PRIORITY = {"any_LIKELY": 0, "both_POSSIBLY": 1, "split": 2, "rescue": 3}
PURDUE_PER_HOUR = 40
BLOCK_WORDS = ("suspend", "exceeded", "too many requests", "blocked", "rate limit", "unusual activity")
# DOI prefixes the Purdue route cannot serve, from browser_log.jsonl up to 2026-09-26: Elsevier
# (Cloudflare check on /pdfft, 0/188), ECS (Radware "perfdrive" check, 0/185), MDPI (0/32 PDF
# fetches), ChemRxiv and SSRN (not proxied).  Skipping them keeps the hourly budget for publishers
# that deliver (Wiley 170/176, ACS 151/152, RSC 61/61, Springer 37/37).
PURDUE_SKIP = ("10.1016/", "10.1149/", "10.3390/", "10.26434/", "10.2139/")


class PurdueGate:
    """Spaces proxied page loads (>= 3600/PURDUE_PER_HOUR s apart, plus jitter) and closes for good
    once a response looks like a block, a suspension or a bounce back to the login page."""

    def __init__(self):
        self.last, self.closed = 0.0, False

    def wait(self):
        gap = 3600 / PURDUE_PER_HOUR + random.uniform(0, 30)
        time.sleep(max(0.0, self.last + gap - time.time()))
        self.last = time.time()

    def inspect(self, page, status=None):
        host = urllib.parse.urlparse(page.url).netloc
        try:
            text = page.inner_text("body")[:4000].lower()
        except Exception:
            text = ""
        # A DOI can resolve off-proxy (e.g. chemrxiv.org, open access); an error there is the
        # publisher's, not EZproxy's, and must not close the route.
        proxied = host.endswith("ezproxy.lib.purdue.edu")
        # Block words count only on EZproxy's own pages or a near-empty proxied page, never in a
        # publisher's article text (an APL abstract containing "exceeded" closed run 5).
        own = host in ("ezproxy.lib.purdue.edu", "login.ezproxy.lib.purdue.edu") or (proxied and len(text) < 1500)
        why = ("login page" if host.startswith("login.ezproxy") else
               "HTTP %s" % status if proxied and status in (403, 429, 503) else
               next((w for w in BLOCK_WORDS if w in text), None) if own else None)
        if why:
            self.closed = True
            log(dict(route="purdue_gate", url=page.url.split("?")[0], status="CLOSED", reason=why))
            print("Purdue route closed for this run:", why, flush=True)
        return not self.closed


def log(entry):
    entry["at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    with open(HERE / "browser_log.jsonl", "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry) + "\n")


def save_pdf(ctx, sid, route, url):
    try:
        resp = ctx.request.get(url, timeout=60000)
        body = resp.body()
    except Exception as e:
        log(dict(screen_id=sid, route=route, url=url, status="ERROR", accepted=False, error=str(e)[:160]))
        return False
    ok = body[:5] == b"%PDF-"
    entry = dict(screen_id=sid, route=route, url=url, status=resp.status, bytes=len(body), accepted=ok)
    if ok:
        entry["sha256"] = hashlib.sha256(body).hexdigest()
        (FILES / (sid + ".pdf")).write_bytes(body)
    log(entry)
    return ok


def wait_for_login(ctx, page):
    page.goto(PROXY + "10.1021/acscatal.5b01281", wait_until="domcontentloaded")
    print("Log in to Purdue in the browser window; waiting up to 15 minutes ...", flush=True)
    for i in range(180):
        urls = [p.url for p in ctx.pages]
        if i % 6 == 0:
            print("tabs:", [u.split("?")[0][:90] for u in urls], flush=True)
            try:
                ctx.pages[-1].screenshot(path=str(HERE / "login_state.png"))
            except Exception:
                pass
        for u in urls:
            host = urllib.parse.urlparse(u).netloc
            if host.endswith("ezproxy.lib.purdue.edu") and not host.startswith("login."):
                print("Logged in.", flush=True)
                return True
        time.sleep(5)
    return False


def via_purdue(ctx, page, sid, doi, gate):
    if gate.closed or doi.lower().startswith(PURDUE_SKIP):
        return False
    gate.wait()
    try:
        resp = page.goto(PROXY + doi, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2500)
        if not gate.inspect(page, resp.status if resp else None):
            return False
        pdf = page.evaluate("() => (document.querySelector('meta[name=\"citation_pdf_url\"]') || {}).content || null")
    except Exception as e:
        log(dict(screen_id=sid, route="purdue_landing", url=doi, status="ERROR", accepted=False, error=str(e)[:160]))
        return False
    log(dict(screen_id=sid, route="purdue_landing", url=page.url.split("?")[0], pdf_meta=bool(pdf)))
    if not pdf:
        return False
    url = urllib.parse.urljoin(page.url, pdf)
    if "wiley" in url:  # Wiley's /doi/pdf/ is an HTML viewer; /doi/pdfdirect/ serves the file
        url = url.replace("/doi/pdf/", "/doi/pdfdirect/").replace("/doi/epdf/", "/doi/pdfdirect/")
    return save_pdf(ctx, sid, "purdue_pdf", url)


SCIHUB_STATE = {"off": False, "last": 0.0}


def via_scihub(ctx, page, sid, doi):
    """Sci-Hub pages are spaced >= 20 s apart; the route turns off for the run at the first captcha
    (captchas are never solved or bypassed)."""
    for mirror in SCIHUB:
        if SCIHUB_STATE["off"]:
            return False
        time.sleep(max(0.0, SCIHUB_STATE["last"] + 20 + random.uniform(0, 10) - time.time()))
        SCIHUB_STATE["last"] = time.time()
        try:
            page.goto(mirror + doi, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(2000)
            src = page.evaluate("""() => { const e = document.querySelector('embed[src], iframe[src], object[data]');
                                        return e ? (e.getAttribute('src') || e.getAttribute('data')) : null; }""")
        except Exception as e:
            log(dict(screen_id=sid, route="scihub_page", url=mirror, status="ERROR", accepted=False, error=str(e)[:160]))
            continue
        captcha = "captcha" in page.content().lower()
        log(dict(screen_id=sid, route="scihub_page", url=mirror, pdf_found=bool(src), captcha=captcha))
        if captcha and not src:
            SCIHUB_STATE["off"] = True
            print("Sci-Hub route off for this run: captcha", flush=True)
            return False
        if src:
            url = urllib.parse.urljoin(page.url, src.split("#")[0])
            if save_pdf(ctx, sid, "scihub_pdf", url):
                return True
    return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--no-scihub", action="store_true")
    p.add_argument("--no-purdue", action="store_true")
    a = p.parse_args()
    FILES.mkdir(exist_ok=True)
    have = {f.stem for f in FILES.iterdir()}
    from retrieve_http import load_records
    recs = [r for r in load_records() if r["screen_id"] not in have and r["doi"]]
    recs.sort(key=lambda r: (PRIORITY[r["stratum"]], r["screen_id"]))
    recs = recs[: a.limit]
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(str(HERE / ".browser_profile"), channel="chrome",
                                                    headless=False, accept_downloads=True)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        gate = PurdueGate()
        gate.closed = a.no_purdue
        if not a.no_purdue and not wait_for_login(ctx, page):
            print("No login detected; stopping.")
            return
        # Purdue landings logged before the 2026-09-26 block that loaded normally are not repeated;
        # attempts after the block (or that errored) are retried.
        tried, sh_tried = set(), set()
        for line in open(HERE / "browser_log.jsonl", encoding="utf-8"):
            e = json.loads(line)
            # A landing that bounced to the login page never reached the article; retry it.
            if e.get("route") == "purdue_landing" and e.get("status") != "ERROR" and (
                    e["at"] < "2026-09-26T00:16:09" or e["at"] >= "2026-09-26T02:00") \
                    and "login.ezproxy" not in e.get("url", ""):
                tried.add(e.get("screen_id"))
            if e.get("route") == "scihub_page" and e.get("status") != "ERROR" and not e.get("captcha")                     and e["at"] >= "2026-09-26T00:40":
                sh_tried.add(e.get("screen_id"))
        print(len(tried), "records already tried through Purdue", flush=True)
        done = 0
        for r in recs:
            sid, doi = r["screen_id"], r["doi"]
            if (FILES / (sid + ".pdf")).exists():
                continue
            ok = (sid not in tried and via_purdue(ctx, page, sid, doi, gate)) or (not a.no_scihub and sid not in sh_tried and via_scihub(ctx, page, sid, doi))
            done += ok
            print(sid, r["stratum"], "OK" if ok else "--", flush=True)
            time.sleep(1.5)
        print(done, "of", len(recs), "retrieved")
        ctx.close()


if __name__ == "__main__":
    main()
