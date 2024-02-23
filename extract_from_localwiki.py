#script which reads data from a specified localwiki region
#initially just reading from the pages API endpoint, with files, pages_history et.al to follow
#determine which (all?) of these endpoints can be filtered by region for extraction?

import requests
import json

# Define the URLs for the LocalWiki API and Wikimedia API
localwiki_api_url = "https://localwiki.org/api/v4/"

responses = []
initial_url = f"{localwiki_api_url}pages/?region=23"
file_path = 'data/responses1.json'

def fetch_data_from_localwiki(pages_url):
    """
    Fetches data from the LocalWiki API for a specific region.
    """
  
    # Send a GET request to the LocalWiki API for the specific region
    try:
            response = requests.get(pages_url)
            response.raise_for_status()  # Raises stored HTTPError, if one occurred.
    except requests.exceptions.RequestException as err:
            print(f"Error fetching data from LocalWiki API for {pages_url}: {err}")
            return None
        
    print(response.url)
    return response.json()  # Return JSON response

next_page_url = initial_url
while next_page_url is not None:
    data = fetch_data_from_localwiki(next_page_url)
    if data is not None:
        with open(file_path, 'a') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')  # Newline separates each JSON object for readability
        next_page_url = data['next']  # Update the next page URL for the next iteration
    else:
        break  # Exit the loop if fetching data fails