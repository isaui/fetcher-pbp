
"""
Fetch data buku dari GOOGLE BOOKS API terus simpan ke JSON
"""

import requests
import json
import time
import random

API_KEY = 'AIzaSyBeV9cHGXl6OQuEaLMGz-wflqXY-imRr38'

def fetch_books(query, lang="en", max_books=100):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "langRestrict": lang,
        "maxResults": 40,  # Maximum allowed by the API per request
        "startIndex": 0,
        "key": API_KEY
    }
    
    all_items = []
    retry_count = 0
    max_retries = 5
    
    while len(all_items) < max_books:
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                break
            
            all_items.extend(items[:max_books - len(all_items)])
            params["startIndex"] += len(items)
            
            print(f"Fetched {len(all_items)} of {max_books} items")
            
            if len(all_items) >= max_books:
                break
            
            # Reset retry count on successful request
            retry_count = 0
            
            # Add a small delay between requests
            time.sleep(random.uniform(0.5, 1.5))
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                retry_count += 1
                if retry_count > max_retries:
                    print("Max retries reached. Stopping.")
                    break
                
                wait_time = 2 ** retry_count + random.random()
                print(f"Rate limit reached. Waiting for {wait_time:.2f} seconds before retrying.")
                time.sleep(wait_time)
            else:
                print(f"HTTP Error occurred: {e}")
                break
        
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    
    return json.dumps(all_items, indent=2, ensure_ascii=False)

query = "Gate OR Reincarnation OR Tale OR War OR Palace OR Kingdom OR Mage OR Sword OR Prince OR Dungeon OR Fairy -Sex"
result = fetch_books(query, max_books=1000)

if result == "[]":
    print("No results were fetched. Check your query or try again later.")
else:
    fetched_items = json.loads(result)
    print(f"Successfully fetched {len(fetched_items)} items.")
    with open('google_books_results.json', 'w', encoding='utf-8') as f:
        f.write(result)
    print("Results saved to google_books_results.json")