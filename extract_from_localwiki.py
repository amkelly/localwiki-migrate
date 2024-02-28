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
print("args:")
print(args)

# Define the URLs for the LocalWiki API and Wikimedia API
localwiki_api_url = "https://localwiki.org/api/v4/"

responses = []
initial_url = f"{localwiki_api_url}{args.endpoint}/?region=23"
print("initialurl:")
print(initial_url)
json_path = f"data/{args}_responses.json"
files_path = 'data/files'

def fetch_data_from_localwiki(url):
    """
    Fetches data from the LocalWiki API for a specific endpoint and region.
    """
    # Construct the URL based on the endpoint
    if args.endpoint not in ['files', 'redirects', 'files_history', 'tags_history', 'redirects_history', 'regions', 'maps', 'maps_history', 'pages_history', 'users', 'pages']:
        print(f"Invalid endpoint: {args.endpoint}. Please choose from: files, redirects, files_history, tags_history, redirects_history, regions, maps, maps_history, pages_history, users, pages.")
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

def download_files_from_json(file_path, download_dir, max_retries=3):
    """
    Opens a JSON file, reads each line, and downloads all files specified in the 'file' dict entry.
    Retries downloading the file up to max_retries times if the download fails.

    :param file_path: Path to the JSON file.
    :param download_dir: Directory where files will be downloaded.
    :param max_retries: Maximum number of retries for each download.
    """
    # Ensure the download directory exists
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    with open(file_path, 'r') as file:
        for line in file:
            try:
                data = json.loads(line)
                results = data.get('results', [])
                for result in results:
                    file_url = result.get('file')
                    if file_url:
                        # Extract the file name from the URL
                        file_name = file_url.split('/')[-1]
                        # Construct the full path where the file will be saved
                        download_path = os.path.join(download_dir, file_name)
                        # Attempt to download the file with retries
                        for attempt in range(max_retries):
                            try:
                                response = requests.get(file_url, stream=True)
                                if response.status_code ==  200:
                                    with open(download_path, 'wb') as f:
                                        f.write(response.content)
                                    print(f"Downloaded {file_name} to {download_path}")
                                    break  # Success, break out of the retry loop
                                else:
                                    print(f"Failed to download {file_name}. Status code: {response.status_code}")
                            except requests.exceptions.RequestException as err:
                                print(f"Error downloading file: {err}")
                                if attempt < max_retries -  1:  # Don't wait on the last attempt
                                    time.sleep(2)  # Wait for  2 seconds before retrying
                                else:
                                    print(f"Failed to download {file_name} after {max_retries} attempts.")
            except json.JSONDecodeError:
                print("Error parsing JSON. Skipping this line.")

next_pages_url = initial_url
while next_pages_url is not None:
    data = fetch_data_from_localwiki(next_pages_url)
    if data is not None:
        with open(json_path, 'a') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')  # Newline separates each JSON object for readability
        next_pages_url = data['next']  # Update the next page URL for the next iteration
    else:
        time.wait(1)
        data = fetch_data_from_localwiki(next_pages_url)


next_files_url = initial_url
while next_files_url is not None:
    data = fetch_data_from_localwiki(next_files_url)
    if data is not None:
        with open(files_path, 'a') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')  # Newline separates each JSON object for readability
        next_files_url = data['next']  # Update the next page URL for the next iteration
    else:
        time.wait(1)
        data = fetch_data_from_localwiki(next_files_url)

if args=="files":
    download_files_from_json(json_path, files_path)