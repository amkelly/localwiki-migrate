#enter the name of your local wiki and this script returns the region's code for use in the following extract_from_localwik.py script
# could also just extract and post here all of the regions and codes? as of a certain date.

import requests

# Define the URLs for the LocalWiki API and Wikimedia API
localwiki_api_url = "https://localwiki.org/api/v4/regions/"

