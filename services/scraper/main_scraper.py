import random
import smtplib
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import structlog
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.pool import NullPool
from sqlmodel import Session, create_engine

from backend.config import settings
from backend.models.gym import GymMetaData, GymOccupancyData

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()

DEBUG_DIR = Path("/app/debug")
MAX_DEBUG_SCREENSHOTS = 3

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"connect_timeout": 30},
    pool_pre_ping=True
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
]


def get_different_user_agent():
    return random.choice(USER_AGENTS)


def _block_unnecessary_resources(route):
    if route.request.resource_type in ("image", "font", "media"):
        route.abort()
    else:
        route.continue_()


def save_debug_screenshot(page) -> None:
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    screenshot_path = DEBUG_DIR / f"debug_{timestamp}.png"
    page.screenshot(path=str(screenshot_path))
    _prune_old_screenshots()


def _prune_old_screenshots() -> None:
    screenshots = sorted(
        DEBUG_DIR.glob("debug_*.png"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    for stale in screenshots[MAX_DEBUG_SCREENSHOTS:]:
        stale.unlink()


def send_failure_email(error: str) -> None:
    sender = settings.ALERT_EMAIL_FROM
    recipient = settings.ALERT_EMAIL_TO
    app_password = settings.ALERT_EMAIL_APP_PASSWORD
    if not (sender and recipient and app_password):
        return

    msg = EmailMessage()
    msg["Subject"] = "ActiveSGMetrics scraper failed"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(f"Scraper run failed:\n\n{error}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as smtp:
            smtp.login(sender, app_password)
            smtp.send_message(msg)
    except Exception as e:
        log.warning("failure_email_failed", error=str(e))


def scrape():
    time.sleep(random.uniform(0, 300))

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            channel="chromium-headless-shell",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--js-flags=--max-old-space-size=256",
            ],
        )
        the_user_agent = get_different_user_agent()
        page = None

        try:
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent=the_user_agent,
                extra_http_headers={
                    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                    "Referer": "https://www.google.com/"
                }
            )

            page = context.new_page()
            page.route("**/*", _block_unnecessary_resources)

            stealth_config = Stealth()
            stealth_config.apply_stealth_sync(page)
            # Apply stealth patches (makes playwright even more human-like to prevent bots)

            with page.expect_response(lambda response: "pass.getFacilityCapacities" in response.url, timeout=90000) as response_info:

                log.info("navigating_to_website", url=settings.WEBSITE_URL)

                page.goto(settings.WEBSITE_URL, timeout=90000, wait_until="domcontentloaded")

                try:
                    page.wait_for_selector("p.chakra-text", timeout=45000)
                    log.info("challenge_cleared")
                except Exception as e:
                    raise RuntimeError("Bot challenge not cleared") from e

                response = response_info.value
                if response.status == 200:
                    raw_data = response.json()
                    gyms = raw_data["result"]["data"]["json"]["gymFacilities"]
                    ingest_gym_data(gyms)
                else:
                    raise RuntimeError(f"Failed to fetch data from ActiveSG: {response.status}")

        except Exception as e:
            if page is not None:
                save_debug_screenshot(page)
            log.error("scrape_failed", error=str(e))
            raise

        finally:
            browser.close()


def ingest_gym_data(gyms_list):
    batch_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    with Session(engine) as session:
        try:
            for item in gyms_list:
                stmt = pg_insert(GymMetaData).values(
                    facility_id=item["id"],
                    name=item["name"],
                    facility_type=item["type"]
                ).on_conflict_do_nothing(index_elements=["facility_id"])
                session.exec(stmt)

                occupancy_record = GymOccupancyData(
                    facility_id=item["id"],
                    occupancy_percentage=item["capacityPercentage"],
                    is_closed=item["isClosed"],
                    timestamp=batch_time
                )

                session.add(occupancy_record)

            session.commit()
            log.info("ingest_success", gym_count=len(gyms_list))

        except Exception as e:
            session.rollback()
            log.error("ingest_failed", error=str(e))
            raise


if __name__ == "__main__":
    try:
        scrape()
    except Exception as e:
        send_failure_email(str(e))
        raise
