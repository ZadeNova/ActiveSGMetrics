# CLAUDE.md — ActiveSGMetrics

## Project
Gym occupancy analytics platform scraping 30+ ActiveSG facilities (Singapore).
Portfolio piece for backend/DevOps internship applications (May 2027–May 2028
internship window, single shot — no second internship). Every architectural
decision must be interview-defensible, not just functional.

## Stack
- Scraper: Playwright + playwright-stealth, triggered by a systemd timer on
  a residential-IP host (hosting TBD) — moved off GitHub Actions because
  Cloudflare fingerprints GitHub's datacenter IP ranges (see Operational
  history below)
- Backend: FastAPI, SQLModel, SQLAlchemy, Alembic, Pydantic Settings, psycopg2-binary
- DB: [Supabase or Neon — pending decision, see Operational history]
- Frontend: React (Vite), Tailwind, SWR, Recharts — migrated off Next.js
  (App Router features were unused; single client-fetched dashboard page)
- Hosting: Render (FastAPI, free tier), Vercel or static host (frontend)

## Verify before acting
Do not assume project state from prior chat history or commit messages alone.
Before doing any work, check actual artifacts: `ruff check .`, `pytest --cov`,
`.github/workflows/`, `git log`, and live GitHub Actions run history via the
API if scheduling/CI behavior is in question. Report actual findings before
proposing next steps.

Also check `PLANS.md` for the current redesign plan (frontend/backend/
cloud/scraper) and any open decisions it flags as blocking — it's the
living roadmap this project is working from, and takes precedence over
assumptions carried from older chat history.

## Working style
- Discuss trade-offs and reasoning before implementing — especially for
  backend/infra decisions with cost, reversibility, or architectural
  implications. Only implement once the user has agreed on the plan *and*
  the underlying logic, not just the proposed outcome.
- Small, mechanical, low-risk fixes (lint errors, dead code removal, a stale
  README line) don't need a discussion round — just note them and do them.
- Frontend: full components/syntax can be provided directly.

## Engineering principles (do not violate)
- Keep it simple: no duplicated code, no premature abstraction, smallest
  change that correctly solves the problem.
- No premature complexity: minimal viable fix before escalating (e.g.
  scraper bot-detection — see Operational history for what was actually
  tried and what the real constraint turned out to be).
- Review your own changes after writing them: read the diff, confirm it
  does what was intended, before calling anything done.
- No pre-commit hooks — CI is the enforcement layer for a solo dev.
- Rate limiting deferred until there's an external threat model; in-memory
  rate limiting is unreliable on Render free tier anyway (process
  restarts/multi-worker split state) — would need Redis.
- Resume/README claims must be literally accurate: no claiming anything
  that isn't true of the current code (e.g. don't describe a mechanism
  that was removed, don't call tiered background revalidation
  "real-time").
- NamedTuple is descriptive only — explicit int() casts on SQLAlchemy
  Decimal returns still required at call sites.

## Operational history
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
