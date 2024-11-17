import requests
import json
import logging
import re
from load_to_wiikimedia import get_login_token 
from load_to_wiikimedia import login

 
def edit_page_image(page_id, page_text, userid, token, login_cookie):
    """ Get CSRF token and edit existing pages using MediaWiki API."""

    params = {
        "action": "query",
        "format": "json",
        "meta": "tokens",
        "formatversion": "2"
    }
    response = requests.get(mediawiki_api_url, params=params, cookies=login_cookie)
    print(response.url)
    data = response.json()
    csrf_token = data["query"]["tokens"]["csrftoken"]
    print(f'csrf_token: {csrf_token}')

    payload = {
        "action": "edit",
        "pageid": page_id,
        "text": page_text,
        "format": "json",
        "bot": True,
        "userid": userid,
        "token": csrf_token
    }
    response = requests.post(mediawiki_api_url, data=payload, cookies=login_cookie)
    data = response.json()
    print(data)
    if "edit" in data and "result" in data["edit"] and data["edit"]["result"] == "Success":
        print("Page created successfully.")
    else:
        print("Failed to create page.")
        #logger.error(f"Failed to create page: ['{title}','{content}'] Response: {response.text}")

def get_page_contents(page_id):
    """Query wiki page based on page_id integer & return page contents"""

    params = {
        "action": "query",
        "format": "json",
        "meta": "tokens",
        "formatversion": "2"
    }
    response = requests.get(mediawiki_api_url, params=params, cookies=login_cookie)
    data = response.json()
    csrf_token = data["query"]["tokens"]["csrftoken"]
    print(f'csrf_token: {csrf_token}')

    payload = {
        "action": "parse",
        "format": "json",
        "prop": "wikitext",
        "pageid": page_id,
    }
    response = requests.post(mediawiki_api_url, data=payload, cookies=login_cookie)

    #decompose respons.json into plaintext page contents
    data = response.json()
   
    return data['parse']['wikitext']['*']

def remove_photo_dupe(wikitext):
    # Regex pattern to find adjacent [[File:...]] tags
    pattern = r'(\[\[File:[^\]]+\]\])(\[\[File:[^\]]+\]\])'
    #print(f'pattern: {pattern}')
    if wikitext.count("[[File:") == 0:
        return None
    else:
        # Replace duplicates with second instance of tag, keeping the |thumb| version
        deduplicated_text = re.sub(pattern, r'\2', wikitext)
        
        print(f'Deduplicated text: {deduplicated_text[:200]}...')  # Print first 200 chars of deduplicated text
        print(f'Number of replacements: {wikitext.count("[[File:") - deduplicated_text.count("[[File:")}')
        # Return the deduplicated text
        return deduplicated_text


# Define the base URL for the MediaWiki API
mediawiki_api_url = "https://wiki.historicsaranaclake.org/api.php"

# Define your wiki username and password
username = "Migratebot@localwiki2mediawiki"
password = "rr87nd3e95e8sb9huqdnnsgfs5tslp6d"

# Step 1: Get login token
login_token, login_cookie = get_login_token()

# Step 2: Log in
userid, login_token, login_cookie = login(login_token, login_cookie)

page_id = 9981

# main loop
while page_id < 17394:
    #print("Oringial content:")
    contents = get_page_contents(page_id)
    deduplicated_content = remove_photo_dupe(contents)
    if deduplicated_content == None:
        page_id += 1
        continue
    else:
        edit_page_image(page_id, deduplicated_content, username, login_token, login_cookie)
        page_id += 1
