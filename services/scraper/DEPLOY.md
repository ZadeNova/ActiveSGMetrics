# Deploying the scraper to the Pi

Run everything below as `zade` on the Pi. Build context is the **repo
root**, not this directory — the Dockerfile copies files from both
`backend/` and `services/scraper/`.

## 1. One-time setup

```bash
mkdir -p /home/zade/activesg_metrics
mkdir -p /home/zade/activesg_metrics/scraper-debug
```

Create `/home/zade/activesg_metrics/scraper.env` with the real values (this file
is never committed — it's secrets). **No quotes around values** — unlike
`.env` files loaded by `python-dotenv`, Docker's `--env-file` takes the
value literally, quotes included, which breaks anything that parses the
value afterward (e.g. SQLAlchemy's URL parser):

```
DATABASE_URL=<Neon connection string>
WEBSITE_URL=https://activesg.gov.sg/gym-pool-crowd
ALERT_EMAIL_FROM=<sender gmail address>
ALERT_EMAIL_TO=<recipient email address>
ALERT_EMAIL_APP_PASSWORD=<gmail app password>
```

(The `ALERT_EMAIL_*` vars are optional — if any is missing, the scraper
just skips sending a failure email instead of erroring.)

## 2. Build the image

From the repo root:

```bash
docker build -f services/scraper/Dockerfile -t activesg-scraper:latest .
```

## 3. Test it manually before scheduling anything

```bash
docker run --rm \
  --env-file /home/zade/activesg_metrics/scraper.env \
  -v /home/zade/activesg_metrics/scraper-debug:/app/debug \
  activesg-scraper:latest
```

Confirm: it exits 0, and (once Neon is live) a new row actually lands in
`gym_occupancy`. If it fails, check `/home/zade/activesg_metrics/scraper-debug/`
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
docker image prune -f
```

No service restart needed — the timer's next scheduled run will use the
freshly tagged image. The `docker image prune -f` cleans up the old
dangling (`<none>`-tagged) layer left behind each time the `latest` tag
moves to a new build — skip it once and nothing breaks, but do it
regularly or these pile up and eat disk over many redeploys.

## Maintenance: log retention

journald (where the scraper's logs land, via `--log-driver journald`)
doesn't delete old entries on its own. A drop-in config caps retention at
14 days, applied Pi-wide (not just this service):

```bash
sudo mkdir -p /etc/systemd/journald.conf.d
sudo tee /etc/systemd/journald.conf.d/retention.conf <<'EOF'
[Journal]
MaxRetentionSec=14day
EOF
sudo systemctl restart systemd-journald
```

Debug screenshots don't need separate handling — `main_scraper.py`
already caps `scraper-debug/` at the 3 most recent PNGs on every run.
