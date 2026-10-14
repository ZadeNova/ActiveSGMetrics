# Operational history — ActiveSGMetrics

Durable facts and decisions from debugging/redesign work. Referenced from
`CLAUDE.md`. Add to this whenever step 4 of the Change lifecycle (see
`CLAUDE.md`) turns up something a future session would need to know —
don't re-derive what's already answered here.

- Scraper was offline 2026-06-01 through [date resumed] — stopped
  deliberately, not an accidental outage. Root cause, confirmed by direct
  test: Cloudflare's managed challenge consistently blocked GitHub Actions'
  shared datacenter IP ranges; identical code cleared the challenge
  immediately when run from a residential IP. Stealth/UA-rotation work was
  never the problem.
- Direct-API extraction (bypassing the browser) was tested and ruled out:
  the target site has no cf_clearance cookie to reuse — Cloudflare is
  scoring the TLS handshake fingerprint itself, which a plain HTTP client
  (httpx/requests) cannot replicate regardless of headers/cookies copied
  from a real browser session. A real browser engine is required for every
  request, not just the first.
- Headless-shell + blocking images/fonts/media + disabled GPU cuts the
  scraper's peak memory from ~715MB to ~572MB. That's close to the floor
  for this approach — further reduction would require dropping the real
  browser engine, which isn't viable given the TLS-fingerprinting finding
  above.
- cron-job.org → GitHub `workflow_dispatch` was the old trigger chain;
  being replaced with a systemd timer on a self-controlled, residential-IP
  host to fix the IP-reputation problem at its source and remove a
  third-party dependency with a silently-expiring PAT.
- Pi confirmed running `aarch64` (64-bit) — required, since Playwright only
  ships ARM64 Chromium builds, not armhf/32-bit.
- Pi memory: `free -h` showed 2.9GB available (not the "free" column —
  buff/cache is reclaimable) with one Go project running, comfortably
  covering the scraper's ~572-715MB peak. Re-check once the second Go
  project (LGTM stack) deploys — that's a meaningfully heavier footprint
  than a typical small Go binary.
- `playwright install --with-deps chromium` also installs the
  `chromium-headless-shell` binary alongside regular Chromium (same
  release, bundled together) — no separate install target needed for the
  headless-shell channel used in `main_scraper.py`.
- The local `.venv`'s console-script shebangs (not just the pre-commit
  hook) are stale — they hardcode the pre-move path
  `/home/nova/Personal/side_projects/ActiveSGMetrics/.venv/bin/python`.
  This breaks any pip-installed Python entry-point script run directly
  (`.venv/bin/alembic`, `.venv/bin/pip`, `.venv/bin/pytest`) with
  `cannot execute: required file not found`. `ruff` is unaffected — it's a
  native binary with no shebang. Workaround: always invoke via
  `.venv/bin/python -m <module>` instead of the direct executable. A full
  fix would mean recreating the venv; not done yet, not blocking.
- Monitoring approach reversed: healthchecks.io was planned, then dropped
  in favor of failure-only email (Gmail SMTP, stdlib only) to avoid adding
  a new external dependency. Important correction made at this point: the
  original justification for monitoring at all had drifted into claiming
  cron-job.org "failed silently" — it didn't. The user deliberately and
  visibly stopped the trigger chain themselves after diagnosing the
  Cloudflare block; there is no precedent in this project of an external
  dependency silently failing unnoticed. The real, narrower justification
  for any monitoring is purely forward-looking (future IP block, Pi
  hardware/power failure, Neon outage, a bug), not re-catching something
  that already happened. Accepted gap: email-on-failure only covers "ran
  and threw an exception" — it cannot catch total Pi silence, since
  nothing can send an alert if nothing can run.
- Local (non-Docker) scraper runs need two things pydantic-settings and
  the `backend.*` imports want differently: `config.py`'s
  `env_file=".env"` resolves relative to **CWD** (needs `backend/` as
  CWD to find `backend/.env`), while `main_scraper.py`'s
  `from backend.config import ...` needs the **repo root** importable.
  Resolved by running with CWD=`backend/` and `PYTHONPATH=..`:
  `cd backend && PYTHONPATH=.. ../.venv/bin/python ../services/scraper/main_scraper.py`.
  Verified end-to-end against live Neon: cleared Cloudflare, ingested 30
  gym records, confirmed via direct query.
- Scraper deployed to the Pi 2026-10-15: image built, manual run verified
  a fresh row in Neon, systemd timer installed and enabled, confirmed
  scheduled for the next 8am-9pm SGT slot. `docker run --env-file` does
  **not** strip quotes from values the way `python-dotenv` does — quoted
  values in `scraper.env` broke SQLAlchemy's URL parser; `scraper.env`
  must use bare `KEY=value`, no quotes. Jitter widened from 0-60s to
  0-5min (`time.sleep(random.uniform(0, 300))`) for a less bot-like
  pattern, since the only cost is a few minutes' delay on hourly data
  that doesn't need minute-level precision.
- Pi log/disk hygiene: journald retention capped at 14 days Pi-wide via
  `/etc/systemd/journald.conf.d/retention.conf` (`MaxRetentionSec=14day`)
  — journald doesn't self-prune by time otherwise. Debug screenshots are
  already bounded by count (3 newest) in `main_scraper.py`, not a
  separate concern. `docker image prune -f` after each rebuild clears the
  dangling layer left behind when the `latest` tag moves — not automated,
  a manual habit documented in `services/scraper/DEPLOY.md`.
