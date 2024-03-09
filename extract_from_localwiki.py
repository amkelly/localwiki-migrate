#script which reads data from a specified localwiki region
#initially just reading from the pages API endpoint, with files, pages_history et.al to follow
#determine which (all?) of these endpoints can be filtered by region for extraction?

import time
import os
import requests
import json
import argparse

# Define the command-line arguments
parser = argparse.ArgumentParser(description='Download data from a specified LocalWiki API endpoint.')
parser.add_argument('endpoint', type=str, help='The local wiki API endpoint to download data from. Options: files, redirects, files_history, tags_history, redirects_history, regions, maps, maps_history, pages_history, users, pages.')

# Parse the arguments
args = parser.parse_args()


# Define the URLs for the LocalWiki API and Wikimedia API
localwiki_api_url = "https://localwiki.org/api/v4/"
responses = []
initial_url = f"{localwiki_api_url}{args.endpoint}/?region=23"
json_path = f"data/{args.endpoint}_responses.json"

def fetch_data_from_localwiki(url):
    """
    Fetches data from the LocalWiki API for a specific endpoint and region.
    """
    # Construct the URL based on the endpoint
    if args.endpoint not in ['files', 'redirects', 'files_history', 'tags_history', 'redirects_history', 'regions', 'maps', 'maps_history', 'pages_history', 'pages']:
        print(f"Invalid endpoint: {args.endpoint}. Please choose from: files, redirects, files_history, tags_history, redirects_history, regions, maps, maps_history, pages_history, pages.")
        return None

    # Send a GET request to the LocalWiki API for the specific endpoint and region
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises stored HTTPError, if one occurred.
    except requests.exceptions.RequestException as err:
        print(f"Error fetching data from LocalWiki API for {url}: {err}")
        return None

    print(response.url)
    return response.json()  # Return JSON response


'''
# add some checks to see if the data files exist, and to resume from the last page if they do
if os.path.exists(json_path):
    print(f"Data file {json_path} already exists. Resuming from last page...")
    with open(json_path, 'r') as infile:
        for line in infile:
            responses.append(json.loads(line))
    next_url = responses[-1]['next']
else:
    '''

# main script logic
next_url = initial_url

while next_url is not None:
    data = fetch_data_from_localwiki(next_url)
    if data is not None:
        with open(json_path, 'a') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')  # Newline separates each JSON object for readability
        next_url = data['next']  # Update the next page URL for the next iteration
    else:
        time.sleep(1)
        data = fetch_data_from_localwiki(next_url)


else: 
    exit()