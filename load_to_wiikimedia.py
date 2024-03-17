import requests

sample_localwiki_data = {
    'url': 'https://localwiki.org/api/v4/pages/232046/', 
    'name': 'Indian Carry Road', 
    'slug': 'indian carry road', 
    'content': "[[File:_files/Swenson.jpg|left|frame|450px|Originally a part of the Swenson Camp, this building was moved onto Indian Carry Road in the early 1980s.]][[File:_files/Guide%20House.jpg|right|frame|450px|The guide house, built in the late 1880s, is the last remaining building in its original location from the ]][[Rustic%20Lodge|Rustic Lodge]]| era. Photograph by Herbert MacArthur]][[Indian%20Carry%20Road|Indian Carry Road]] is a private road which runs north from [[New%20York%20Route%203|New York Route 3]] , directly across from [[Corey's%20Road|Corey's Road]] it leads past the [[Swenson%20Camp%20|Indian Carry Chapel]] , the [[Rustic%20Lodge%20Guide%20House|Rustic Lodge guide house]] , the [[Swenson%20Camp|Swenson Camp]] and other homes which were built after the Swenson Camp era.[[File:_files/Indian%20Carry%20Chapel.jpg|frame|450px|Indian Carry Chapel]]",
    'region': 'https://localwiki.org/api/v4/regions/23/', 
    'tags': []
    }

def write_to_wikimedia(data):

    # Define the base URL for the MediaWiki API
    mediawiki_api_url = "https://wiki.historicsaranaclake.org/api.php"

    # Define your wiki username and password
    username = "Migratebot@localwiki2mediawiki"
    password = "rr87nd3e95e8sb9huqdnnsgfs5tslp6d"

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
        
    def write_page(title, content, userid, token, login_cookie):
        """
        Get CSRF token and write a new page using MediaWiki API."""
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
            "userid": userid,
            "token": csrf_token
        }
        response = requests.post(mediawiki_api_url, data=payload, cookies=login_cookie)
        data = response.json()
        if "edit" in data and "result" in data["edit"] and data["edit"]["result"] == "Success":
            print("Page created successfully.")
        else:
            print("Failed to create page.")
            print(response.text)

    # Step 1: Get login token
    login_token, login_cookie = get_login_token()
    print(login_token)
    
    # Step 2: Log in
    userid, login_token, login_cookie = login(login_token, login_cookie)
    #print(login_token)
    #print(login_cookie)
    
    if userid and login_token:
        # Step 3: Write new page using data from LocalWiki API response
        # Assume localwiki_data contains response from previous LocalWiki API call
        title = sample_localwiki_data["name"]
        text = sample_localwiki_data["content"]
        write_page(title, text, userid, login_token, login_cookie)

write_to_wikimedia(sample_localwiki_data)