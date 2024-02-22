#script which reads data from a specified localwiki region
#initially just reading from the pages API endpoint, with files, pages_history et.al to follow
#determine which (all?) of these endpoints can be filtered by region for extraction?

import requests

# Define the URLs for the LocalWiki API and Wikimedia API
localwiki_api_url = "https://localwiki.org/api/v4/"
wikimedia_api_url = "https://wikimedia/api"
region_slug = "hsl"

def fetch_data_from_localwiki(region_slug):
    """
    Fetches data from the LocalWiki API for a specific region.
    """
    # Construct the URL for the specific region
    pages_url = f"{localwiki_api_url}pages/"
    
    # Parameters to be passed in the URL
    params = {'region': 23}
    
    # Send a GET request to the LocalWiki API for the specific region
    response = requests.get(pages_url, params=params)
    print(response.url)
    if response.status_code == 200:
        return response.json()  # Return JSON response
    else:
        # If request fails, print error message and return None
        print(f"Failed to fetch data from LocalWiki API for region {region_slug}. Status code: {response.status_code}")
        return None


# Fetch data from LocalWiki API

localwiki_data = fetch_data_from_localwiki(region_slug)
total_results = []
   
if localwiki_data:
    #Iterate through each page/object in the LocalWiki data and write to Wikimedia
    for key, value in localwiki_data.items():
        print(f"{key}: {value}")
        total_results.append(localwiki_data['results'])
    #print(total_results)