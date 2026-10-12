# PLANS.md

Working plan for getting ActiveSGMetrics running again, redesigned instead of
band-aided. This is a living checklist, not a spec — update it as decisions
change. See `CLAUDE.md` for the principles/working style this plan should
follow (discuss trade-offs before implementing, keep it simple, no dead code,
review changes after writing them) and `claude_info.md` for earlier advice
this plan supersedes in places.

Items marked **(DECISION NEEDED)** are blocking — don't implement that item
until it's resolved. Everything else reflects decisions already made in
discussion.

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
- [ ] Package as a container image for Lambda (simplest path to get
      `psycopg2`'s native binary right)
- [ ] Delete dead code: `backend/routers/ingest.py` and
      `backend/services/ingest_service.py` — both empty, not wired into
      `main.py` since commit `7507296`
- [ ] Add `structlog` — currently zero logging in the backend
- [ ] Add `pytest-cov` to `backend/requirements-test.txt` — right now
      `pytest --cov` fails outright because it isn't installed
- [ ] Update `ALLOWED_ORIGINS` (CORS) to include the new Vercel origin once
      it exists
- [ ] Neon connection string: plain Lambda env var vs SSM Parameter Store
      (SecureString, free tier) — **(DECISION NEEDED)**
- [ ] Extend `/api/v1/health` to report last scraper run time + record
      count, backed by a new `scraper_runs` table — **(DECISION NEEDED,
      see Scraper monitoring below — these are the same decision)**
- [ ] Add an Alembic migration-check job to `ci.yml` (doesn't exist yet)
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
- [ ] No lightweight-HTTP bypass of the browser — tested and ruled out.
      The target site fingerprints the TLS handshake itself (no
      `cf_clearance` cookie exists to reuse), so a real browser engine is
      mandatory for every single request, not just the first
- [ ] Use the headless-shell binary + block images/fonts/media + disable
      GPU — measured ~572MB peak vs. ~715MB baseline for plain headless
      Chromium; this is close to the realistic floor for a real-browser
      approach, further reduction isn't available without dropping the
      browser engine entirely
- [ ] Keep the existing jitter (`time.sleep(random.uniform(0,60))`) —
      avoids the "fires at exactly :00 every hour, forever" bot signature
- [ ] Fix `ruff` violations in `services/scraper/main_scraper.py` (E401
      multiple imports on one line, E402 import-order) — currently
      invisible to CI since the lint job only checks `backend/`
- [ ] Widen CI's lint scope to the whole repo, not just `backend/`
- [ ] Add structured logging (`structlog`) — currently bare `print()`
      calls, no logging framework
- [ ] Monitoring / dead-man's-switch so a silent failure is caught same-day
      instead of four months later like last time — **(DECISION NEEDED)**:
      a `scraper_runs` table + extended `/health` endpoint (reusable,
      gives a real signal: last run time, records written), a bare
      external heartbeat ping (e.g. healthchecks.io, free tier, not in the
      scraper's critical path so it doesn't recreate the cron-job.org
      single-point-of-failure problem), or both together
- [ ] Acknowledged, not solved by infrastructure: there's no guarantee
      against the target site eventually blocking this specific
      residential IP too. The goal is "common failure mode (datacenter
      ASN blocking) fixed, rare failure mode (this IP gets individually
      flagged) detected same-day" — not "unbannable"

---

## Open decisions blocking parts of this plan

1. **Neon secret in Lambda** — plain environment variable (simplest) vs.
   SSM Parameter Store SecureString (free, avoids the secret sitting in
   plaintext Terraform state). Leaning SSM as the low-cost-but-more-correct
   option — confirm?
2. **Scraper monitoring** — `scraper_runs` table + `/health` extension
   (more integrated, reuses infra you're building anyway) vs. a bare
   external heartbeat ping vs. both. Leaning "both" (the table gives you
   real operational data worth having regardless; a cheap external ping
   against `/health` is what actually alerts you without you remembering
   to check).
3. **Build order** — suggested sequence below, confirm or reorder:
   1. Scraper → Pi + systemd timer (this is "get it running again," the
      most time-sensitive item)
   2. Backend cleanup (dead code, structlog, pytest-cov, CORS) — needed
      before Lambda packaging anyway
   3. Lambda + Terraform (backend hosting)
   4. Frontend migration off Next.js + Vercel deploy
   5. Monitoring/heartbeat wiring, README, CI additions (Alembic check,
      widened lint scope)

Nothing above gets implemented until the three items in this section are
answered.
