from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from datetime import date, datetime , timezone
from dotenv import load_dotenv
import os, sys
import hashlib
from sqlmodel import create_engine, Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.pool import NullPool
from backend.config import settings


load_dotenv()
# Get the current script's directory 
current_dir = os.path.dirname(os.path.abspath(__file__))

# Move up two levels to reach the project root
project_root = os.path.abspath(os.path.join(current_dir, "../../"))

if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from backend.models.gym import GymMetaData , GymOccupancyData




DATABASE_URL = settings.SUPABASE_DATABASE_URL
# Need to manually change it to SUPABASE_DEV_DATABASE_URL if testing in local

#DATABASE_URL = os.getenv("SUPABASE_DEV_DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"connect_timeout": 30},
    pool_pre_ping=True
)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
]


def get_different_user_agent():
    today = date.today().isoformat()
    hash_val = int(hashlib.sha256(today.encode()).hexdigest(), 16)
    return USER_AGENTS[hash_val % len(USER_AGENTS)]


def scrape():
        
    with sync_playwright()as p:
        
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled",
         "--no-sandbox",
         "--disable-dev-shm-usage"])
        the_user_agent = get_different_user_agent()
        
        try:
            
            context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=the_user_agent,
            extra_http_headers={
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Referer": "https://www.google.com/"
                }
            )
            
            page = context.new_page()
            
            stealth_config = Stealth()
            stealth_config.apply_stealth_sync(page)
            # Apply stealth patches ( makes playwright even more human like to prevent bots)
            
            
            # maybe change it to page.wait_for_load_state
            # find out what is wait for load state and the difference between wait_until="load" and "networkidle"
            
    
            with page.expect_response(lambda response: "pass.getFacilityCapacities" in response.url, timeout=90000) as response_info:
                
                print("Navigating to website...")
                
                page.goto(settings.WEBSITE_URL, timeout=90000, wait_until="domcontentloaded")

                # 2. THE MISSING PIECE: Wait for a UI element to prove we are inside
                # Using 'text=Gym' or a specific CSS selector from the dashboard
                
                print("Waiting for dashboard UI to load...")
                try:
                    page.wait_for_selector("p.chakra-text", timeout=45000) 
                    print("Gym list detected. Bot check likely cleared.")
                except Exception as e:
                    print(f"UI element 'Gym' not found. We are likely stuck on the bot challenge: {e}")
                    # This screenshot will now show you EXACTLY where you are stuck
                    page.screenshot(path="stuck_on_challenge.png")
                    
                    raise Exception("Bot challenge not cleared.")
                
                response = response_info.value
                if response.status == 200:
                    
                    raw_data = response.json()
                    gyms = raw_data["result"]["data"]["json"]["gymFacilities"]
                    # ingest data function here
                    ingest_gym_data(gyms)
                    
                else:
                    raise Exception(f"Failed to fetch Data from ActiveSG: {response.status}")
            

        except Exception as e:
            page.screenshot(path="debug_timeout.png")
            
            print("--- PAGE SOURCE START ---")
            try:
                print(page.content())
                
            except Exception as e:
                print(f"Could not get page content: {e}")
            print("--- PAGE SOURCE END ---")
            
            print(f"Error occured in scrape(): {e}")
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
            print(f"Successfully recorded data for {len(gyms_list)} gyms")
            
            
        except Exception as e:
            session.rollback()
            print(f"Error occured in ingest_gym_data function: {e}")
            raise e



if __name__ == "__main__":
    scrape()


