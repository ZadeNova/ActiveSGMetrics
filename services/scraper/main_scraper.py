from playwright.sync_api import sync_playwright
import requests
from datetime import date
from dotenv import load_dotenv
import os
import random, time
import hashlib


load_dotenv()

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
                    print("\n \n \n \n")
                    gyms = raw_data["result"]["data"]["json"]["gymFacilities"]
                    print(gyms)
                else:
                    raise Exception("something went wrong")
            

        
        except Exception as e:
            page.screenshot(path="error.png")
            raise
        
        finally:
            browser.close()



# The Solution: If testing in Swagger, replace all single quotes with double quotes. When using your scraper, always use json=data in the requests.post() call, as it automatically converts Python's single quotes to valid JSON double quotes.
def send_data_to_backend():
    pass

scrape()