import requests
import json
import re
from load_to_wiikimedia import get_login_token 
from load_to_wiikimedia import login

def delete_page(page_id, token, login_cookie):
    """ Get CSRF token and edit existing pages using MediaWiki API."""

    params = {
        "action": "query",
        "format": "json",
        "meta": "tokens",
        "formatversion": "2"
    }
    response = requests.get(mediawiki_api_url, params=params, cookies=login_cookie)
    #print(response.url)
    data = response.json()
    csrf_token = data["query"]["tokens"]["csrftoken"]
    #print(f'csrf_token: {csrf_token}')

    payload = {
        "action": "delete",
        "pageid": page_id,
        "reason": "spam removal",
        "token": csrf_token
    }
    response = requests.post(mediawiki_api_url, data=payload, cookies=login_cookie)
    #print(response)
    #data = response.json()
    #print(data)
    if response.status_code == 200:
        return 1
    else:
        if "error" in data and data["error"].get("code") == "nosuchpageid":
            print("No such page with the given ID.")
            return 0
        else:
            print("Failed to delete page.")


# Define the base URL for the MediaWiki API
mediawiki_api_url = "https://wiki.historicsaranaclake.org/api.php"

# Define your wiki username and password
username = "Migratebot@localwiki2mediawiki"
password = "rr87nd3e95e8sb9huqdnnsgfs5tslp6d"

# Step 1: Get login token
login_token, login_cookie = get_login_token()

# Step 2: Log in
userid, login_token, login_cookie = login(login_token, login_cookie)

page_id = 17430
#debug with one page
#print(delete_page(page_id, login_token, login_cookie))

while page_id <= 93122:
    result = delete_page(page_id, login_token, login_cookie)
    if result == 0:
        print(f"Page {page_id} does not exist or could not be deleted.")
    else:
        print(f"Page {page_id} deleted successfully.")
    page_id += 1