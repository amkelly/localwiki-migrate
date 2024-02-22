# localwiki-migrate

These scripts are designed to migrate a region's page from (localwiki)[localwiki.org] to a wikimedia instance.

The scripts are designed to be run in the following order:
    1. extract_from_localwiki.py
    2. transform.py (not implimented)
    3. load_to_wikimedia.py

### Miscellanious Notes:


https://localwiki.org/api/v4/regions/?slug__iexact=hsl&format=json

HSL region: https://localwiki.org/api/v4/regions/23/ 
(would be useful for others to write a secondary script that returns region numbers instead of digging through regions API.)

url to return all pages:
https://localwiki.org/api/v4/pages/?format=json&region=23 

url for all files:
https://localwiki.org/api/v4/files/?format=json&region=23

iterate through all the listed items in:

{
    "files": "https://localwiki.org/api/v4/files/", 
    "redirects": "https://localwiki.org/api/v4/redirects/", 
    "files_history": "https://localwiki.org/api/v4/files_history/", 
    "tags_history": "https://localwiki.org/api/v4/tags_history/", 
    "redirects_history": "https://localwiki.org/api/v4/redirects_history/", 
    "regions": "https://localwiki.org/api/v4/regions/", 
    "maps": "https://localwiki.org/api/v4/maps/", 
    "maps_history": "https://localwiki.org/api/v4/maps_history/", 
    "pages_history": "https://localwiki.org/api/v4/pages_history/", 
    "pages": "https://localwiki.org/api/v4/pages/", 
    "users": "https://localwiki.org/api/v4/users/"
}

can exclude "format=json" when using the script