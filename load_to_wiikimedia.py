import requests

sample_localwiki_data = {
    'url': 'https://localwiki.org/api/v4/pages/232046/', 
    'name': 'Indian Carry Road', 
    'slug': 'indian carry road', 
    'content': '<p>\n\t<span class="image_frame image_frame_border image_left"><img src="_files/Swenson.jpg" style="width: 450px; height: 248px;"><span style="width: 450px;" class="image_caption">Originally a part of the Swenson Camp, this building was moved onto Indian Carry Road in the early 1980s.</span></span><span class="image_frame image_frame_border image_right"><img src="_files/Guide%20House.jpg" style="width: 450px; height: 280px;"><span style="width: 450px;" class="image_caption">The guide house, built in the late 1880s, is the last remaining building in its original location from the <a href="Rustic%20Lodge">Rustic Lodge</a> era. Photograph by Herbert MacArthur</span></span><a href="Indian%20Carry%20Road">Indian Carry Road</a> is a private road which runs north from <a href="New%20York%20Route%203">New York Route 3</a> , directly across from <a href="Corey\'s%20Road">Corey\'s Road</a> it leads past the <a href="Swenson%20Camp%20">Indian Carry Chapel</a> , the <a href="Rustic%20Lodge%20Guide%20House">Rustic Lodge guide house</a> , the <a href="Swenson%20Camp">Swenson Camp</a> and other homes which were built after the Swenson Camp era.<span class="image_frame image_frame_border"><img src="_files/Indian%20Carry%20Chapel.jpg" style="width: 450px; height: 338px;"><span style="width: 450px;" class="image_caption">Indian Carry Chapel</span></span></p>',
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