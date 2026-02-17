from playwright.sync_api import sync_playwright
import requests
from datetime import date, datetime , timezone
from dotenv import load_dotenv
import os, sys
import random, time
import hashlib
from sqlmodel import create_engine, Session, select
from sqlalchemy.pool import NullPool

load_dotenv()
# Get the current script's directory 
current_dir = os.path.dirname(os.path.abspath(__file__))

# Move up two levels to reach the project root
project_root = os.path.abspath(os.path.join(current_dir, "../../"))

if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from backend.models.gym import GymMetaData , GymOccupancyData


def get_base_url():
    """Automatically toggles between local and production URLs."""
    if os.getenv("GITHUB_ACTIONS") == "true":
        return os.getenv("PROD_BACKEND_URL")
    return os.getenv("LOCAL_BACKEND_URL")

BASE_URL = get_base_url()
#BASE_URL = os.getenv("LOCAL_BACKEND_URL")
HEALTH_URL = f"{BASE_URL}/api/v1/health"
INGEST_URL = f"{BASE_URL}/api/v1/ingestdata"


DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")
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
    
    """
    Commented out
    """
    # if not wake_up_backend():
    #     print("Backend failed to wake up. Aborting scrape to save github action minutes.")
    #     return
    
    with sync_playwright() as p:
        
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        the_user_agent = get_different_user_agent()
        
        try:
            
            context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=the_user_agent
            )
            
            page = context.new_page()
            
            with page.expect_response(lambda response: "pass.getFacilityCapacities" in response.url) as response_info:
                page.goto(os.getenv("WEBSITE_URL"))
                
                response = response_info.value
                if response.status == 200:
                    
                    raw_data = response.json()
                    gyms = raw_data["result"]["data"]["json"]["gymFacilities"]
                    # ingest data function here
                    ingest_gym_data(gyms)
                    
                else:
                    raise Exception(f"Failed to fetch Data from ActiveSG: {response.status}")
            

        except Exception as e:
            page.screenshot(path="error.png")
            print(f"Error occured in scrape(): {e}")
            raise

        finally:
            browser.close()
    
    
    
def ingest_gym_data(gyms_list):
    
    batch_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    with Session(engine) as session:
        try:
           
            existing_ids = session.exec(select(GymMetaData.facility_id)).all()
            existing_ids_set = set(existing_ids)
            
            for item in gyms_list:
                
                if item["id"] not in existing_ids_set:
                    new_metadata = GymMetaData(
                        facility_id=item["id"],
                        name=item["name"],
                        facility_type=item["type"]
                    )                
                    session.add(new_metadata)
                    existing_ids_set.add(item["id"])
                    
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




scrape()


"""
Commented out as I will be shifting the database ingestion to the scraper.
Will just leave this here in case I need it again.
"""
# def wake_up_backend(retries=35, delay=5):
#     """Ping the backend hosted on railway/render so that the backend will be awake."""
#     for attempt in range(1, retries+1):
#         try:
#             print(f"Wake-up attempt {attempt}/{retries}...")
#             response = requests.get(HEALTH_URL, timeout=10)
#             if response.status_code == 200:
#                 print("Backend is awake")
#                 return True
#             else:
#                 print(f"Backend returned status {response.status_code}, retrying...")
#         except requests.exceptions.RequestException:
#             print(f"Backend not awake yet, retrying in {delay}s...")
#         time.sleep(delay)
#     print("Backend failed to wake up after multiple attempts")
#     return False    

"""
Commented out as I will be shifting the database ingestion to the scraper.
Will just leave this here in case I need it again.
"""
# The Solution: If testing in Swagger, replace all single quotes with double quotes. When using your scraper, always use json=data in the requests.post() call, as it automatically converts Python's single quotes to valid JSON double quotes.
# def send_data_to_backend(data_to_backend, retries=3, delay=30):
    
    
#     for attempt in range(retries):
        
#         try:
#             print(f"Attempt {attempt + 1}: Sending data to backend...")
#             response = requests.post(INGEST_URL, json=data_to_backend, timeout=120)
            
#             if response.status_code in [201, 202]:
#                 print(f"Successfully sent data: {response.json()}")
#                 return True
#             else:
#                 print(f"Server returned status {response.status_code}")
        
#         except requests.exceptions.ConnectionError:
#             print(f"Could not detect to backend. Is the FastAPI server running? Waiting {delay}s...")
#             time.sleep(delay)
        
#         except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout):
#             print(f"Request timed out on attempt {attempt + 1}. Retrying in {delay}s...")
#             time.sleep(delay)
            
#         except Exception as e:
#             print(f"Unexpected error occured: {e}")
#             break
            
#     print("Failed to send data after multiple retries")
#     return False
    
    
# Nullpull forces a fresh new connection to supabase for every new request.


