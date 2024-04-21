import requests
import json
import logging
from html_convert import parse_and_convert

def get_login_token():
    """
    Get login token from MediaWiki API.
    """
    params = {
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    }
    response = requests.get(mediawiki_api_url, params=params)
    data = response.json()
    login_token = data["query"]["tokens"]["logintoken"]
    login_cookie = response.cookies
    return login_token, login_cookie

def login(login_token, login_cookie):
    """
    Log in to MediaWiki API.
    """
    payload = {
        "action": "login",
        "lgname": username,
        "lgpassword": password,
        "lgtoken": login_token,
        "format": "json"
    }

    response = requests.post(mediawiki_api_url, data=payload, cookies=login_cookie)
    data = response.json()
    if data["login"]["result"] == "Success":
        #print("Login successful.")
        #print(f'login_cookie: {login_cookie}')
        return data["login"]["lguserid"], login_token, response.cookies
    elif data["login"]["result"] == "NeedToken":
        # If session timed out, try obtaining a new token and login again
        print("Possible session timed out. Refreshing token and trying again.")
        login_token = get_login_token()
        return login(login_token, login_cookie)
    else:
        print("Login failed.")
        return None, None
    
def write_page(title, content, userid, token, login_cookie, page_count):
    """ Get CSRF token and write a new page using MediaWiki API."""

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
        "title": title,
        "text": content,
        "format": "json",
        "bot": True,
        "createonly": True,
        "userid": userid,
        "token": csrf_token
    }
    response = requests.post(mediawiki_api_url, data=payload, cookies=login_cookie)
    data = response.json()
    if "edit" in data and "result" in data["edit"] and data["edit"]["result"] == "Success":
        print("Page created successfully.")
    else:
        print("Failed to create page.")
        logger.error(f"Failed to create page: ['{title}','{content}'] Response: {response.text}")

def upload_file(name, file_url, userid, token, login_cookie, file_count):
    """
    using Localwiki API's files data to upload files, 
    Get CSRF token and write a file using MediaWiki API.
    As localwiki provides URL of the files, use Example 2: Upload file from URL from 
    https://www.mediawiki.org/wiki/API:Upload
    """
    
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

    '''file_path = './data/' + '/'.join(file.split('/')[5:])
    print(file_path)
    file = {'file':(name, open(file_path, 'rb'), 'multipart/form-data')}'''

    payload = {
        "action": "upload",
        "filename": name,
        "url": file_url,
        "format": "json",
        "token": csrf_token,
        "ignorewarnings": 1
    }

    upload_finished = False
    file_count += 1
    file_percent_complete = file_count / 13316

    while upload_finished == False:
        response = requests.post(mediawiki_api_url, data=payload, cookies=login_cookie)
        data = response.json()
        print(data)
        if "upload" in data and "result" in data["upload"] and data["upload"]["result"] == "Success":
            print("File created successfully.")
            logger.info(f"{file_count} - {file_percent_complete}% {name} from {file_url} uploaded.")
            upload_finished = True
        elif data["error"]["code"] == "http-bad-status":
            #retry upload with same parameters
            continue
        elif data["error"]["code"] == "fileexists-no-change":
            logger.info(f"{file_count} - {file_percent_complete}% {name} from {file_url} already exists.")
            upload_finished = True
        else:
            print("Failed to upload file.")
            logger.error(f"Failed to create page: ['{name}','{file_url}'] Response: {response.text}")
            break
    else:
         return(file_count)

# Create a logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG) # Set the logger's level to DEBUG so it captures all messages

# Create handlers
error_handler = logging.FileHandler('error_log.txt')
error_handler.setLevel(logging.ERROR) # Only handle ERROR and above

info_handler = logging.FileHandler('info_log.txt')
info_handler.setLevel(logging.INFO) # Only handle INFO and above

# Create formatters and add it to handlers
error_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
info_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_format)
info_handler.setFormatter(info_format)

# Add handlers to the logger
logger.addHandler(error_handler)
logger.addHandler(info_handler)

#sample data
sample_localwiki_data = {
    'url': 'https://localwiki.org/api/v4/pages/232046/', 
    'name': 'Indian Carry Road', 
    'slug': 'indian carry road', 
    'content': "[[File:_files/Swenson.jpg|left|frame|450px|Originally a part of the Swenson Camp, this building was moved onto Indian Carry Road in the early 1980s.]][[File:_files/Guide%20House.jpg|right|frame|450px|The guide house, built in the late 1880s, is the last remaining building in its original location from the ]][[Rustic%20Lodge|Rustic Lodge]]| era. Photograph by Herbert MacArthur]][[Indian%20Carry%20Road|Indian Carry Road]] is a private road which runs north from [[New%20York%20Route%203|New York Route 3]] , directly across from [[Corey's%20Road|Corey's Road]] it leads past the [[Swenson%20Camp%20|Indian Carry Chapel]] , the [[Rustic%20Lodge%20Guide%20House|Rustic Lodge guide house]] , the [[Swenson%20Camp|Swenson Camp]] and other homes which were built after the Swenson Camp era.[[File:_files/Indian%20Carry%20Chapel.jpg|frame|450px|Indian Carry Chapel]]",
    'region': 'https://localwiki.org/api/v4/regions/23/', 
    'tags': []
    }
sample_files_data = {
    "url": "https://localwiki.org/api/v4/files/159559/", 
    "name": "Swenson.jpg", 
    "file": "https://localwiki.org/media/pages/files/kgtnl2j0fkmd6jcb.jpg", 
    "slug": "indian carry road", 
    "region": "https://localwiki.org/api/v4/regions/23/"
    }

# Define the base URL for the MediaWiki API
mediawiki_api_url = "https://wiki.historicsaranaclake.org/api.php"

# Define your wiki username and password
username = "Migratebot@localwiki2mediawiki"
password = "rr87nd3e95e8sb9huqdnnsgfs5tslp6d"

# Step 1: Get login token
login_token, login_cookie = get_login_token()

# Step 2: Log in
userid, login_token, login_cookie = login(login_token, login_cookie)

#Step 3: if Steps 1 & 2 complete determine which 
mode_flag = 'f'
page_count = 0
file_count = 0

if userid and login_token:
    # Step 3: Write new page using data from LocalWiki API response
    # Assume localwiki_data contains response from previous LocalWiki API call
    print("login successful...")
    if mode_flag == 'p':
        # Open a JSON file
        with open('./data/pages_responses.json', 'r') as file:
        # Loop through each line of responses in the file
        # each line is effectivly a json file.
            for line in file:
                json_obj = json.loads(line)
                for r in json_obj["results"]:
                    name = r['name']
                    text = parse_and_convert(r['content'])
                    pagecount += 1
                    percent_complete = pagecount / 8104
                    logging.info(f"{percent_complete}% Wrote page {pagecount}: {name}")
                    #write_page(title, content, userid, login_token, login_cookie)

    if mode_flag == 'f':
        #name = sample_files_data["name"]
        #file_url = sample_files_data["file"]
                # Open a JSON file
        with open('./data/files_responses.json', 'r') as file:
        # Loop through each line of responses in the file
        # each line is effectivly a json file.
            for line in file:
                json_obj = json.loads(line)
                for r in json_obj["results"]:
                    name = r['name']
                    file_url = r['file']
                    file_count = upload_file(name, file_url, userid, login_token, login_cookie, file_count)
    else:
        print("no flag provided.")