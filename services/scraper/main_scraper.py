from playwright.sync_api import sync_playwright
import requests
from datetime import date
from dotenv import load_dotenv
import os
import random, time
import hashlib


load_dotenv()


def get_base_url():
    """Automatically toggles between local and production URLs."""
    if os.getenv("GITHUB_ACTIONS") == "true":
        return os.getenv("PROD_BACKEND_URL")
    return os.getenv("LOCAL_BACKEND_URL")

BASE_URL = get_base_url()
HEALTH_URL = f"{BASE_URL}/api/v1/health"
INGEST_URL = f"{BASE_URL}/api/v1/ingestdata"


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
    
    wake_up_backend()
    
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
                    send_data_to_backend(gyms)
                    
                else:
                    raise Exception(f"Failed to fetch Data from ActiveSG: {response.status}")
            

        except Exception as e:
            page.screenshot(path="error.png")
            print(f"Error occured in scrape(): {e}")
            raise

        finally:
            browser.close()
    


def wake_up_backend():
    """Ping the backend hosted on railway/render so that the backend will be awake."""
    try:
        requests.get(HEALTH_URL, timeout=5)
    except:
        pass        
    


# The Solution: If testing in Swagger, replace all single quotes with double quotes. When using your scraper, always use json=data in the requests.post() call, as it automatically converts Python's single quotes to valid JSON double quotes.
def send_data_to_backend(data_to_backend, retries=3, delay=30):
    
    
    for attempt in range(retries):
        
        try:
            print(f"Attempt {attempt + 1}: Sending data to backend...")
            response = requests.post(INGEST_URL, json=data_to_backend, timeout=60)
            
            if response.status_code == 201:
                print(f"Successfully sent data: {response.json()}")
                return True
            else:
                print(f"Server returned status {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            print(f"Could not detect to backend. Is the FastAPI server running? Waiting {delay}s...")
            time.sleep(delay)
        except Exception as e:
            print(f"Unexpected error occured: {e}")
            break
            
    print("Failed to send data after multiple retries")
    return False
    


scrape()
