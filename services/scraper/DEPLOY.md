# Deploying the scraper to the Pi

Run everything below as `zade` on the Pi. Build context is the **repo
root**, not this directory — the Dockerfile copies files from both
`backend/` and `services/scraper/`.

## 1. One-time setup

```bash
mkdir -p /home/zade/activesg
mkdir -p /home/zade/activesg/scraper-debug
```

Create `/home/zade/activesg/scraper.env` with the real values (this file
is never committed — it's secrets):

```
SUPABASE_DATABASE_URL=<Neon connection string>
ACTIVE_SG_API=<value from existing .env>
WEBSITE_URL=https://activesg.gov.sg/gym-pool-crowd
HEALTHCHECK_PING_URL=<your healthchecks.io ping URL, once you've created one>
```

(`HEALTHCHECK_PING_URL` can be left out entirely for now — the scraper
treats it as optional and just skips pinging if it's unset.)

## 2. Build the image

From the repo root:

```bash
docker build -f services/scraper/Dockerfile -t activesg-scraper:latest .
```

## 3. Test it manually before scheduling anything

```bash
docker run --rm \
  --env-file /home/zade/activesg/scraper.env \
  -v /home/zade/activesg/scraper-debug:/app/debug \
  activesg-scraper:latest
```

Confirm: it exits 0, and (once Neon is live) a new row actually lands in
`gym_occupancy`. If it fails, check `/home/zade/activesg/scraper-debug/`
for a screenshot.

## 4. Install the systemd units

```bash
sudo cp services/scraper/systemd/activesg-scraper.service /etc/systemd/system/
sudo cp services/scraper/systemd/activesg-scraper.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now activesg-scraper.timer
```

## 5. Verify

```bash
systemctl status activesg-scraper.timer     # confirm it's scheduled
systemctl list-timers activesg-scraper.timer # confirm next run time
journalctl -u activesg-scraper.service -f    # watch the next run live
```

## Redeploying after a code change

```bash
docker build -f services/scraper/Dockerfile -t activesg-scraper:latest .
```

No service restart needed — the timer's next scheduled run will use the
freshly tagged image.
