from playwright.sync_api import sync_playwright
import requests
from dotenv import load_dotenv
import os
import random, time


load_dotenv()

def scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        
        context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/114.0.0.0 Safari/537.36",
        )
        
        
        page = context.new_page()
        page.goto(os.getenv("WEBSITE_URL"))
        time.sleep(random.uniform(3,8))
        page.wait_for_selector("div.chakra-card div.chakra-stack", timeout=10000)
        
        cards = page.query_selector_all("div.chakra-card div.chakra-stack")
        print(len(cards))
        data = []
        
        for card in cards:
            facility = card.query_selector("p.chakra-text").inner_text().strip()
            status = card.query_selector("span.chakra-badge").inner_text().strip()
            data.append({
                "facility": facility,
                "status": status
            })
            
        print(data)
        browser.close()

scrape()