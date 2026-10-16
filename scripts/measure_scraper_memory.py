"""A/B peak-memory measurement of the scraper's Chromium. No DB writes.

Runs the real scrape flow (stealth, challenge wait, API response check) under
three configs, interleaved N times, and reports the median/min/max of the peak
memory summed across the whole browser process tree (RSS and PSS, from
/proc/<pid>/smaps_rollup). PSS splits shared pages between processes, so it's
the stricter number; RSS double-counts them.

Run on the Pi using the existing scraper image (no env file needed):

    docker run --rm -v "$PWD/scripts/measure_scraper_memory.py:/measure/m.py:ro" \
        activesg-scraper:latest python /measure/m.py 5

Stop activesg-scraper.timer first so a scheduled run doesn't overlap. Needs
WEBSITE_URL only if it differs from the default below.
"""
import json
import os
import statistics
import sys
import threading
import time

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

URL = os.environ.get("WEBSITE_URL", "https://activesg.gov.sg/gym-pool-crowd")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
COMMON = ["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]

VARIANTS = {
    "full_chromium_baseline": dict(channel="chromium", args=COMMON, block=False),
    "shell_only": dict(channel="chromium-headless-shell", args=COMMON, block=False),
    "optimised_prod": dict(
        channel="chromium-headless-shell",
        args=COMMON + ["--disable-gpu", "--js-flags=--max-old-space-size=256"],
        block=True,
    ),
}


def descendants(root):
    kids = {}
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                with open(f"/proc/{d}/stat") as f:
                    ppid = int(f.read().rsplit(")", 1)[1].split()[1])
                kids.setdefault(ppid, []).append(int(d))
            except Exception:
                pass
    out, stack = [], [root]
    while stack:
        p = stack.pop()
        out.append(p)
        stack.extend(kids.get(p, []))
    return out


def mem_kb(pid):
    pss = rss = 0
    try:
        with open(f"/proc/{pid}/smaps_rollup") as f:
            for line in f:
                if line.startswith("Pss:"):
                    pss = int(line.split()[1])
                elif line.startswith("Rss:"):
                    rss = int(line.split()[1])
    except Exception:
        pass
    return pss, rss


class Sampler(threading.Thread):
    def __init__(self, root):
        super().__init__(daemon=True)
        self.root, self.stop, self.peak_pss, self.peak_rss, self.nproc = root, False, 0, 0, 0

    def run(self):
        while not self.stop:
            pids = descendants(self.root)
            tot = [mem_kb(p) for p in pids]
            self.peak_pss = max(self.peak_pss, sum(t[0] for t in tot))
            self.peak_rss = max(self.peak_rss, sum(t[1] for t in tot))
            self.nproc = max(self.nproc, len(pids))
            time.sleep(0.1)


def run(name):
    v = VARIANTS[name]
    with sync_playwright() as p:
        kw = dict(headless=True, args=v["args"])
        if v["channel"]:
            kw["channel"] = v["channel"]
        browser = p.chromium.launch(**kw)
        # driver's browser pid: find chromium child of this process tree
        pids = [d for d in descendants(os.getpid()) if d != os.getpid()]
        root = None
        for pid in pids:
            try:
                cmd = open(f"/proc/{pid}/cmdline").read()
            except Exception:
                continue
            if "--remote-debugging-pipe" in cmd and "--type=" not in cmd:
                root = pid
                break
        s = Sampler(root)
        s.start()
        status = None
        ok = False
        try:
            ctx = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent=UA,
                extra_http_headers={"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", "Referer": "https://www.google.com/"},
            )
            page = ctx.new_page()
            if v["block"]:
                page.route(
                    "**/*",
                    lambda r: r.abort() if r.request.resource_type in ("image", "font", "media") else r.continue_(),
                )
            Stealth().apply_stealth_sync(page)
            with page.expect_response(lambda r: "pass.getFacilityCapacities" in r.url, timeout=90000) as ri:
                page.goto(URL, timeout=90000, wait_until="domcontentloaded")
                page.wait_for_selector("p.chakra-text", timeout=45000)
            resp = ri.value
            status = resp.status
            ok = status == 200 and len(resp.json()["result"]["data"]["json"]["gymFacilities"]) > 0
            time.sleep(0.5)
        except Exception as e:
            status = f"ERR {type(e).__name__}"
        finally:
            s.stop = True
            s.join()
            browser.close()
    return dict(variant=name, ok=ok, status=status, peak_pss_mb=s.peak_pss / 1024,
                peak_rss_mb=s.peak_rss / 1024, nproc=s.nproc)


if __name__ == "__main__":
    n = int(sys.argv[1])
    results = []
    for i in range(n):
        for name in VARIANTS:  # interleaved to spread out drift
            r = run(name)
            print(json.dumps(r), flush=True)
            results.append(r)
            time.sleep(3)
    print("\nSUMMARY (valid runs only)")
    for name in VARIANTS:
        rs = [r for r in results if r["variant"] == name and r["ok"]]
        if rs:
            for k in ("peak_pss_mb", "peak_rss_mb"):
                vals = [r[k] for r in rs]
                print(f"{name:22s} {k:12s} n={len(vals)} median={statistics.median(vals):7.1f} min={min(vals):7.1f} max={max(vals):7.1f}")
        else:
            print(f"{name:22s} no valid runs")
