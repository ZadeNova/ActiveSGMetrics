# CLAUDE.md — ActiveSGMetrics

## Project
Gym occupancy analytics platform scraping 30+ ActiveSG facilities (Singapore).
Portfolio piece for backend/DevOps internship applications (May 2027–May 2028
internship window, single shot — no second internship). Every architectural
decision must be interview-defensible, not just functional.

## Stack
- Scraper: Playwright + playwright-stealth, triggered by a systemd timer on
  a residential-IP host (hosting TBD) — moved off GitHub Actions because
  Cloudflare fingerprints GitHub's datacenter IP ranges (see
  `docs/OPERATIONAL.md`)
- Backend: FastAPI, SQLModel, SQLAlchemy, Alembic, Pydantic Settings,
  psycopg2-binary — deployed as a container image on AWS Lambda (Function
  URL, no API Gateway) via Terraform, not Render
- DB: Neon (replacing Supabase — chosen for connect-triggered
  autosuspend/resume; see `docs/OPERATIONAL.md`)
- Frontend: React (Vite), Tailwind, SWR, Recharts — migrated off Next.js
  (App Router features were unused; single client-fetched dashboard page)
- Hosting: Vercel (frontend, primary) with S3 + CloudFront provisioned as
  a documented backup; AWS Lambda (backend); no custom domain/DNS

## Verify before acting
Do not assume project state from prior chat history or commit messages alone.
Before doing any work, check actual artifacts: `ruff check .`, `pytest --cov`,
`.github/workflows/`, `git log`, and live GitHub Actions run history via the
API if scheduling/CI behavior is in question. Report actual findings before
proposing next steps.

Also check `PLANS.md` for the current redesign plan (frontend/backend/
cloud/scraper) and any open decisions it flags as blocking — it's the
living roadmap this project is working from, and takes precedence over
assumptions carried from older chat history. Check `docs/OPERATIONAL.md`
for durable facts/decisions from past debugging — don't re-derive
something already answered there.

## Working style
- Discuss trade-offs and reasoning before implementing — especially for
  backend/infra decisions with cost, reversibility, or architectural
  implications. Only implement once the user has agreed on the plan *and*
  the underlying logic, not just the proposed outcome.
- Small, mechanical, low-risk fixes (lint errors, dead code removal, a stale
  README line) don't need a discussion round — just note them and do them.
- Frontend: full components/syntax can be provided directly.

## Change lifecycle

**Major implementation** — anything spanning multiple files, introducing
new infrastructure/dependencies, or completing/changing a PLANS.md item:

1. **Plan/discuss** — agree on approach and reasoning, not just outcome.
2. **Implement.**
3. **Review** — lint/compile/test, then actually read the diff for
   correctness, not just "did it run."
4. **Sync docs** — a separate, required pass, not something to hope
   falls out of step 3: update `PLANS.md` (tick what's actually done,
   correct anything that came out different from plan) and
   `docs/OPERATIONAL.md` if a durable fact or decision emerged that a
   future session would need.
5. **Findings** — if review or doc-sync turns up something that changes
   the plan or opens a new question, that goes back to step 1. If nothing
   material, done.

**Minor fix** (lint errors, dead code removal, a stale comment): skip
steps 1 and 4 — implement, run a lightweight version of step 3, tick a
`PLANS.md` line directly if one obviously applies. No full doc-sync sweep.

## Git commits
Commit author is always the user (local `git config user.name`/
`user.email` — `ZadeNova <muhderfannnn@gmail.com>`), never Claude. Commit
messages get a `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`
trailer line crediting the assist — that's metadata, not a change of
author. Commit messages: short and concise, describing what changed.

## Engineering principles (do not violate)
- Keep it simple: no duplicated code, no premature abstraction, smallest
  change that correctly solves the problem.
- No premature complexity: minimal viable fix before escalating (e.g.
  scraper bot-detection — see `docs/OPERATIONAL.md` for what was actually
  tried and what the real constraint turned out to be).
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
See `docs/OPERATIONAL.md` for the durable facts/decisions log (root causes
confirmed by testing, measurements taken, infra decisions made and why).
Append to it per step 4 of the Change lifecycle — don't let this kind of
history drift back into this file or get lost in chat history.
