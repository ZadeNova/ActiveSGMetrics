# import requests
# from requests.exceptions import HTTPError
# from dotenv import load_dotenv
# import random
# from itertools import cycle
# import json
# import os


# load_dotenv()

# PUBLIC_API = os.getenv("ACTIVE_SG_API")


# user_agent_list = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    
    

# ]

# random.shuffle(user_agent_list)

# random_user_agent = cycle(user_agent_list)
# user_agent = next(random_user_agent)

# my_headers = {"User-Agent": user_agent,
#               "Referer": os.getenv("WEBSITE_URL"),
#               "Content-Type": "application/json",
#               }

# def fetch_data():
    
#     session = requests.Session()
#     session.headers.update(my_headers)
    
#     try:
        
#         response = requests.get(PUBLIC_API, timeout=10, headers=my_headers)
#         response.raise_for_status()
        
#     except HTTPError as http_err:
#         print(f"HTTP error occured: {http_err}")
#     except Exception as err:
#         print(f"Other error occurred: {err}")
#     else:
#         print("Fetch_Data function Success!")
#         print(json.dumps(response.json(), indent=4))
        
    
    
    
# def parse_data():
#     pass

# def post_data_to_backend():
#     pass



# fetch_data()
