# script to open JSON results files and download files from URLs

import time
import os
import json
import requests

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


# Define the path to the JSON file and the directory where files will be downloaded
json_path = "data/files_responses.json"
download_dir = "data/files/"

# Call the function to download files from the JSON
download_files_from_json(json_path, download_dir)