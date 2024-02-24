#script which reads data from a specified localwiki region
#initially just reading from the pages API endpoint, with files, pages_history et.al to follow
#determine which (all?) of these endpoints can be filtered by region for extraction?

import time
import requests
import json

# Define the URLs for the LocalWiki API and Wikimedia API
localwiki_api_url = "https://localwiki.org/api/v4/"

responses = []
initial_pages_url = f"{localwiki_api_url}pages/?region=23"
initial_files_url = f"{localwiki_api_url}files/?region=23"
pages_file_path = 'data/pages_responses.json'
files_file_path = 'data/files_responses.json'

def fetch_data_from_localwiki(url):
    """
    Fetches data from the LocalWiki API for a specific region.
    """
  
    # Send a GET request to the LocalWiki API for the specific region
    try:
            response = requests.get(url)
            response.raise_for_status()  # Raises stored HTTPError, if one occurred.
    except requests.exceptions.RequestException as err:
            print(f"Error fetching data from LocalWiki API for {url}: {err}")
            return None
        
    print(response.url)
    return response.json()  # Return JSON response

next_pages_url = initial_pages_url
while next_pages_url is not None:
    data = fetch_data_from_localwiki(next_pages_url)
    if data is not None:
        with open(pages_file_path, 'a') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')  # Newline separates each JSON object for readability
        next_pages_url = data['next']  # Update the next page URL for the next iteration
    else:
        time.wait(1)
        data = fetch_data_from_localwiki(next_files_url)


next_files_url = initial_files_url
while next_files_url is not None:
    data = fetch_data_from_localwiki(next_files_url)
    if data is not None:
        with open(files_file_path, 'a') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')  # Newline separates each JSON object for readability
        next_files_url = data['next']  # Update the next page URL for the next iteration
    else:
        time.wait(1)
        data = fetch_data_from_localwiki(next_files_url)
