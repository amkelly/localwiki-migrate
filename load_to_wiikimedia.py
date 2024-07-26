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
sample_pagewithtable = {"url": "https://localwiki.org/api/v4/pages/238037/", 
                        "name": "Vic Macy", 
                        "slug": "vic macy", 
                        "content": "<p>\n\t<strong>Born: </strong>August 13, 1913</p>\n<p>\n\t<strong>Died:</strong> April 29, 1970</p>\n<p>\n\t<strong>Married: </strong>Stella Paquin</p>\n<p>\n\t<strong>Children:</strong> Donald Macy</p>\n<p>\n\t<strong>Victor Macy</strong> operated the <a href=\"Cedar%20Post%20restaurant\">Cedar Post restaurant</a> on <a href=\"Lake%20Flower%20Avenue\">Lake Flower Avenue</a>.\u00a0 From 1945 to 1950 he lived at <a href=\"23%20McIntyre%20Street\">23 McIntyre Street</a>.\u00a0 He later moved to <a href=\"175%20Lake%20Flower%20Avenue\">175 Lake Flower Avenue</a>, site of the restaurant, where he lived from 1962 to 1967.</p>\n<hr>\n<p class=\"MsoNormal\">\n\t<em>Adirondack Daily Enterprise</em>, April 30, 1970</p>\n<p class=\"MsoNormal\">\n\tVictor Macy, owner and operator of the Cedar Post Restaurant, died suddenly Wednesday morning at his home at Edward St. Extension. He was 56 years of age.</p>\n<p class=\"MsoNormal\">\n\tMr. Macy was born Aug. 13, 1913 in <a href=\"Goldsmith\">Goldsmith</a>, a son of Frank and Rose Amell Macy. He was a member of BPOE Lodge 1508, the Saranac Lake Moose Lodge and was a third and fourth degree-Knight-of Columbus.</p>\n<p class=\"MsoNormal\">\n\tSurvivors include his wile, Stella Paquin Macy whom he married in 1935, a son, Donald of Peekskill; three grandchildren; three brothers, Edward of Upton, Wyo., Philip and John of Saranac Lake; four sisters, Mrs. Helen Mose of Saranac Lake, Mrs. Philomene Gardner of Saranac Lake, Mrs. Alfina Murray of Saranac Lake and Mrs. Alma Monaghan of Owls Head; and several nieces and nephews.</p>\n<p class=\"MsoNormal\">\n\tFriends may call at the <a href=\"Fortune%20Funeral%20Home\">Fortune Funeral Home</a>. An Elks service will be held there 7:30 this evening and a Knights of Columbus Rosary service will be held at 8:15. A Funeral Mass will be offered at 11:15 a.m. Friday at <a href=\"St.%20Bernard's%20Church\">St. Bernard's Church</a>. Burial will be in <a href=\"St.%20Bernard's%20Cemetery\">St. Bernard's Cemetery</a>.</p>\n<h2>\n\tComments</h2>\n<p>\n\t\u00a0</p>\n", 
                        "region": "https://localwiki.org/api/v4/regions/23/", }


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
mode_flag = 'p'
page_count = 0
file_count = 0
file_resume_count = 50

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
                    title = r['name']
                    content = parse_and_convert(r['content'])
                    page_count += 1
                    percent_complete = page_count / 8104
                    logging.info(f"{percent_complete}% Wrote page {page_count}: {title}")
                    write_page(title, content, userid, login_token, login_cookie, page_count)

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
                    if file_resume_count > file_count:
                        file_count += 1
                        continue
                    else:
                        file_count = upload_file(name, file_url, userid, login_token, login_cookie, file_count)
    else:
        print("no flag provided.")