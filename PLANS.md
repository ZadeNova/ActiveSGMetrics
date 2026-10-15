# PLANS.md

Working plan for getting ActiveSGMetrics running again, redesigned instead of
band-aided. This is a living checklist, not a spec — update it as decisions
change. See `CLAUDE.md` for the principles/working style this plan should
follow (discuss trade-offs before implementing, keep it simple, no dead code,
review changes after writing them, sync docs after major work) and
`docs/OPERATIONAL.md` for the durable facts/decisions log.

Items marked **(DECISION NEEDED)** are blocking — don't implement that item
until it's resolved. Everything else reflects decisions already made in
discussion.

---

## Next steps — major milestones

**Milestone 1 — Scraper live on the Pi** _(done)_

- [x] Neon project created, region `ap-southeast-1`, direct connection
      string in `backend/.env`
- [x] `alembic upgrade head` run against it — `gym_metadata`/
      `gym_occupancy` + composite index confirmed present
- [x] Scraper tested locally (not containerized, not on the Pi) — cleared
      Cloudflare, ingested 30 real gym records, verified by direct query
      against Neon. See `docs/OPERATIONAL.md` for the exact invocation
      (local runs need `PYTHONPATH=..` from inside `backend/`)
- [x] Monitoring: failure-only email via Gmail SMTP, tested end-to-end
      (healthchecks.io dropped — see `docs/OPERATIONAL.md`)
- [x] Followed `services/scraper/DEPLOY.md` on the Pi: image built, manual
      test run confirmed a real row in Neon
- [x] Systemd timer installed and verified unattended, 2026-10-15: 5
      consecutive 8am-12pm SGT runs, all `challenge_cleared` →
      `ingest_success` (30 gyms each) in `journalctl`, cross-checked
      against Neon — 5 batches of exactly 30 rows at the matching
      timestamps, no manual intervention
- [ ] Decommission the old GitHub Actions scraper workflow
      (`.github/workflows/scraper.yml`) — Pi reliability now confirmed,
      safe to do. Note: the **GitHub repo secret** is still named
      `SUPABASE_DATABASE_URL`; rename it to `DATABASE_URL` on GitHub's
      side if this workflow needs to run again before decommissioning

**Milestone 2 — Backend cleanup** _(mostly done)_

- [x] Delete dead code: `backend/routers/ingest.py`, `backend/services/ingest_service.py`
      (done, along with unused `ACTIVE_SG_API`/`*_BACKEND_URL` settings,
      `.pre-commit-config.yaml`, and the backend Dockerfile/compose
      service — Lambda deploys a zip, not an image, per Milestone 3)
- [x] `pytest-cov` added (85% gate in CI)
- [x] Alembic migration-check job in `ci.yml` (`alembic upgrade head` +
      `alembic check`, runs before tests)
- [x] Lint scope widened to the whole repo (`ruff check .` in CI, not
      just `backend/`)
- [ ] Add `structlog` to the **backend** — scraper has it, backend still
      has zero structured logging
- [ ] Fix README: still has the removed "Wake Up mechanism" claim and
      the "soon to be full-stack" phrasing (it already is)
- [ ] Update CORS `ALLOWED_ORIGINS` — blocked until the Vercel origin
      exists (Milestone 4), correctly left for later

**Milestone 3 — Backend on Lambda** _(not started — needs an AWS account
ready)_

- Add Mangum, package as a zip (arm64, manylinux-targeted dependencies)
- Write the Terraform (Lambda, IAM role, concurrency cap, billing alarm, S3
  state backend) — you run `plan`/`apply` yourself
- Measure real cold start once deployed, don't assume

**Milestone 4 — Frontend migration** _(not started)_

- Scaffold Vite + React, port the existing components over
- Point the fetcher at the live Lambda Function URL
- Deploy to Vercel

**Milestone 5 — Polish** _(not started)_

- README architecture diagram
- Final end-to-end verification across all four pieces together

Detailed reasoning and specifics for each item are in the sections below.

---

## Frontend

- [ ] Migrate off Next.js to Vite + React — App Router features (SSR,
      file routing) were never actually used; this is a single
      client-side-fetched dashboard page, so Next.js was unused surface area
- [ ] Hosting: **Vercel** (primary) — reuses the existing account/workflow
      from the Next.js version, zero-config build detection for Vite
- [ ] Keep S3 + CloudFront as a documented backup option (provisioned in
      Terraform even though Vercel is primary — see Cloud section)
- [ ] No custom domain / DNS — use Vercel's default `*.vercel.app` URL
- [ ] Update `lib/fetcher.ts` / env config to point at the new Lambda
      Function URL once the backend is live
- [ ] Confirm env var convention change (Next's `NEXT_PUBLIC_*` →
      Vite's `import.meta.env.VITE_*`)

## Backend

- [ ] Keep **FastAPI** — Go was evaluated and rejected; this isn't
      resource- or latency-constrained, and a rewrite isn't justified by
      project scope
- [ ] Add **Mangum** adapter so the existing ASGI app runs on Lambda
      unchanged
- [ ] Package as a **zip deployment, not a container image** — faster
      cold start (no image pull/mount step) and skips ECR entirely.
      Install dependencies with `pip install --platform manylinux2014_aarch64
    --only-binary=:all: --target ./package` (not a plain local
      `pip install`) so compiled packages like `psycopg2-binary` and
      `pydantic-core` match Lambda's actual runtime instead of the dev
      machine's
- [ ] Lambda architecture: **arm64/Graviton**, not x86_64 — slightly
      cheaper per GB-second and consistent with the Pi also being ARM;
      doesn't change the $0 bill either way, just a deliberate pick
- [x] Delete dead code: `backend/routers/ingest.py` and
      `backend/services/ingest_service.py` — both empty, not wired into
      `main.py` since commit `7507296`
- [ ] Add `structlog` — currently zero logging in the backend
- [x] Add `pytest-cov` to `backend/requirements-test.txt` — done, 85%
      gate in CI
- [ ] Update `ALLOWED_ORIGINS` (CORS) to include the new Vercel origin once
      it exists
- [ ] Neon connection string: **plain Lambda environment variable**
      (decided — SSM's real advantages, hiding it from console view and
      rotation without redeploy, mostly matter with multiple IAM
      principals, which this account doesn't have; SSM would also add a
      small cold-start cost for little benefit here)
- [x] Add an Alembic migration-check job to `ci.yml` — done
- [ ] Measure real Lambda + Mangum cold start once built — don't assume
      "fine for a dashboard," verify it
- [ ] Fix README: drop the "Wake Up mechanism" claim (removed from code)
      and the "soon to be full-stack" phrasing (it already is); add an
      architecture diagram

## Cloud / Infra

- [ ] AWS Lambda, Function URL (**not** API Gateway — keeps this on the
      permanent Always-Free compute tier instead of the 12-month-limited
      API Gateway free tier)
- [ ] IAM execution role for the Lambda (CloudWatch Logs + whatever else
      it needs — this is the one IAM artifact this plan needs)
- [ ] Lambda reserved concurrency cap (e.g. 5) + an AWS Budgets billing
      alarm (e.g. $1 threshold) — this is the cost ceiling, and
      deliberately **not** a rate limiter: single-user traffic has no
      fairness problem to solve, only a cost-blowup-from-abuse risk, which
      the concurrency cap already covers at zero extra code
- [ ] **No provisioned concurrency** — cold start is accepted as-is (to be
      measured once built, not assumed). Provisioned concurrency would
      eliminate it but costs real money for idle capacity, which breaks
      the $0/month goal for a problem that hasn't even been confirmed to
      exist yet
- [ ] S3 + CloudFront for the frontend backup path (see Frontend)
- [ ] **No VPC, subnets, or security groups** — nothing in this
      architecture needs them: Lambda runs in AWS's managed VPC by default,
      Neon is a public-internet endpoint, S3/CloudFront aren't VPC
      resources. (Trade-off, stated honestly: this means no "designed a
      VPC" resume line from this project, unless that's deliberately added
      later as its own exercise.)
- [ ] **No NAT Gateway, ALB, RDS, or EC2** — evaluated and rejected; the
      "textbook enterprise" version of this pattern runs ~$70–100+/month
      for traffic this project doesn't have
- [ ] **No Route53 / custom domain** — using AWS's and Vercel's default
      URLs
- [ ] Terraform remote state: S3 bucket + DynamoDB lock table (not local
      `.tfstate`)
- [ ] DB: **Neon**, replacing Supabase — chosen specifically for
      connect-triggered autosuspend/resume (Supabase's free-tier pause
      needing a manual dashboard click is what contributed to this
      project going dark). Historical data will **not** be migrated —
      starting fresh is an accepted trade-off
- [ ] Use Neon's **direct** connection string everywhere (not the pooled
      PgBouncer endpoint) — current connection concurrency doesn't justify
      pooling complexity

## Scraper

- [ ] Stop running on GitHub Actions entirely — confirmed by direct test
      that Cloudflare blocks GitHub's shared datacenter IP ranges;
      stealth/UA-rotation work was never the actual problem
- [ ] Run from a **residential-IP host** (Raspberry Pi) via a systemd
      timer, replacing the cron-job.org → GitHub `workflow_dispatch` chain
      — removes a third-party dependency with a silently-expiring PAT as a
      side effect
- [x] Pi confirmed running a 64-bit OS (`uname -m` → `aarch64`) — Playwright
      only ships ARM64 Chromium builds, not armhf/32-bit, so this was a
      real go/no-go check, not a formality. Cleared.
- [x] No lightweight-HTTP bypass of the browser — tested and ruled out.
      The target site fingerprints the TLS handshake itself (no
      `cf_clearance` cookie exists to reuse), so a real browser engine is
      mandatory for every single request, not just the first
- [x] Use the headless-shell binary + block images/fonts/media + disable
      GPU — measured ~572MB peak vs. ~715MB baseline for plain headless
      Chromium; this is close to the realistic floor for a real-browser
      approach, further reduction isn't available without dropping the
      browser engine entirely. Implemented in `main_scraper.py`
      (`channel="chromium-headless-shell"`, `page.route` blocking
      image/font/media, `--disable-gpu`)
- [x] Jitter at the start of each run (`time.sleep(random.uniform(0,300))`,
      widened from an initial 0-60s) — avoids the "fires at exactly :00
      every hour, forever" bot signature.
      Note: reducing run frequency (below) helps volume a little but does
      **not** meaningfully reduce ban risk on its own — jitter is what
      actually breaks the pattern; frequency is a separate, legitimate
      decision (see schedule below)
- [x] **Scheduler: systemd timer** (confirmed) — `OnCalendar=*-*-* 08..21:00:00`,
      Pi timezone confirmed as `Asia/Singapore` so this can be written in
      local time directly, no UTC conversion needed. Matches the
      project's own original cron window (`30 0-13 * * *` UTC ≈
      8:30am-9:30pm SGT) — restoring prior intent, not a new constraint.
      14 runs/day instead of 24
- [x] Pi memory headroom checked: `free -h` shows 2.9GB **available**
      (not the misleading "free" column — buff/cache is reclaimable) with
      one Go project currently running. Comfortably covers the ~572-715MB
      measured scraper peak. **Re-check this once the second Go project
      (LGTM stack — Loki/Grafana/Tempo/Mimir) actually deploys** — that's
      a meaningfully heavier footprint than a typical small Go binary and
      could change this picture; don't assume it still holds later
- [x] Containerize with Docker: `python:3.12-slim` base +
      `playwright install --with-deps chromium` (not Microsoft's prebuilt
      image — arm64 availability for this exact Playwright version isn't
      confirmed). `services/scraper/Dockerfile` written; not yet built or
      run on the Pi itself — see `services/scraper/DEPLOY.md`
- [x] Fix `ruff` violations in `services/scraper/main_scraper.py` (E401
      multiple imports on one line, E402 import-order) — fixed by removing
      the `sys.path` hack entirely (see Dockerfile's `PYTHONPATH=/app`
      instead), not just reordering imports
- [x] Widen CI's lint scope to the whole repo, not just `backend/`
- [x] Add structured logging (`structlog`) — bare `print()` calls replaced
      throughout `main_scraper.py`
- [x] Monitoring: **failure-only email via Gmail SMTP** (revised away
      from healthchecks.io to avoid a new external dependency).
      `send_failure_email()` implemented in `main_scraper.py`, stdlib
      `smtplib`/`email` only, no new pip dependency. `ALERT_EMAIL_FROM`/
      `ALERT_EMAIL_TO`/`ALERT_EMAIL_APP_PASSWORD` set in `config.py` and
      `backend/.env`. **Tested end-to-end**: App Password generated for
      the dedicated alert account, forced `send_failure_email()` call,
      email confirmed received. Known gap, accepted: only catches "ran
      and threw," not total Pi silence. See `docs/OPERATIONAL.md`
- [ ] Acknowledged, not solved by infrastructure: there's no guarantee
      against the target site eventually blocking this specific
      residential IP too. The goal is "common failure mode (datacenter
      ASN blocking) fixed, rare failure mode (this IP gets individually
      flagged) detected same-day" — not "unbannable"

---

## Decisions log (all settled — nothing left blocking)

- Neon secret in Lambda → plain environment variable.
- Scraper monitoring → **revised**: healthchecks.io dropped (reduce
  external dependencies); failure-only email via Gmail SMTP instead,
  using a dedicated Gmail account created just for this (not a personal
  address — actual value lives in `backend/.env`/`scraper.env`, never
  committed), no new third-party
  signup. No `scraper_runs` table. Known gap, accepted: this only catches
  "ran and threw an exception" — total silence (Pi offline/dead) isn't
  covered, since nothing can alert if nothing can run. See
  `docs/OPERATIONAL.md`.
- Pi execution → user runs commands themselves; Claude prepares scripts/
  files, user copies them over and reports back errors (no SSH access
  granted).
- AWS/Terraform execution → Claude writes all `.tf` files; user runs
  `terraform plan`/`apply` themselves and reports back results.

## Build order

1. Scraper → Pi + systemd timer + heartbeat ping (this is "get it running
   again," the most time-sensitive item, and monitoring is cheap enough to
   fold in here rather than treat as a separate later step)
2. Backend cleanup (dead code, structlog, pytest-cov, CORS) — needed
   before Lambda packaging anyway
3. Lambda + Terraform (backend hosting), zip deployment, arm64
4. Frontend migration off Next.js + Vercel deploy
5. Polish: README, CI additions (Alembic check, widened lint scope)
