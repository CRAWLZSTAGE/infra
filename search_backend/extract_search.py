import os
import google
import requests
import threading
from bs4 import BeautifulSoup
import json

SEARCH_LIMIT = 5
SEARCH_INTERVAL = 0.01
STANDARD = True
FACEBOOK_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')
FOURSQUARE_VERSION = os.environ.get('FOURSQUARE_VERSION')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')


def genericSearch(searchString):
    return google.search(searchString, stop=SEARCH_LIMIT, pause=SEARCH_INTERVAL, only_standard=STANDARD)

"""
WARN
- Using unscrubbed input here!
- repeated declaration of fields (Facebook)
"""

import facebook
graph = facebook.GraphAPI(FACEBOOK_ACCESS_TOKEN)

def extract_call_now(page):
    if page.has_key("call_to_actions") and page["call_to_actions"].has_key("data"):
        for obj in page["call_to_actions"]["data"]:
            if obj.has_key("type") and obj["type"] == "CALL_NOW":
                facebook_call_now = graph.get_object(id=obj["id"], fields='from,id,intl_number_with_plus,status,type')
                if facebook_call_now.has_key("intl_number_with_plus"):
                    page["intl_number_with_plus"] = facebook_call_now["intl_number_with_plus"]
    return page

fields = 'id, name, about, location, phone, category, description, fan_count, hours, link, call_to_actions'

def find_facebook_links(newTerm):
    raw_html = requests.get("https://graph.facebook.com/search?q=" + \
        newTerm.replace(" ", "+") + "&type=page&fields=" + fields.replace(" ", "") + \
        "&access_token=" + FACEBOOK_ACCESS_TOKEN)
    data = json.loads(raw_html.text)["data"]
    facebook_contacts = list()
    facebook_ids = list()
    for datum in data:
        datum["connections"]=list()
        facebook_contacts.append(extract_call_now(datum))
        facebook_ids.append(datum["id"])
    return facebook_contacts, facebook_ids

def find_linkedin_links(newTerm):
    urls = genericSearch(newTerm + " site:www.linkedin.com")
    linkedin_ids = list()
    for url in urls:
        linkedin_ids.append(url)
    return linkedin_ids

def find_google_links(newTerm):
    raw_html = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + \
        newTerm.replace(" ", "+") + "&key=" + GOOGLE_API_KEY)
    results = json.loads(raw_html.text)["results"]
    google_ids = list()
    for result in results:
        google_ids.append(result["place_id"])
    return google_ids

import sys

def find_fsquare_links(newTerm, lat, lon):
    foursquare_url = "https://api.foursquare.com/v2/venues/search?ll=" + lat + "," + lon + "&query=" + newTerm + "&client_id=" + FOURSQUARE_CLIENT_ID + "&client_secret=" + FOURSQUARE_CLIENT_SECRET + "&v=" + FOURSQUARE_VERSION
    raw_html = requests.get(foursquare_url)
    venues = json.loads(raw_html.text)["response"]["venues"]
    fsquare_ids = list()
    for venue in venues:
        fsquare_ids.append(venue["id"])
    return fsquare_ids

"""

1.3745612,103.8910849
FOURSQUARE_CLIENT_ID_2=S5Q1D0LSRPSAEIMPWGVRG2DFAJA043GVGPRQSSX01SHLBIZB
FOURSQUARE_CLIENT_SECRET_2=QFX2MMUHYAW335ZHJTPEA0M3XWPJ4CRYFFSQDZK14B0FQAL5

https://api.foursquare.com/v2/venues/search?query=singapore&client_id=S5Q1D0LSRPSAEIMPWGVRG2DFAJA043GVGPRQSSX01SHLBIZB&client_secret=QFX2MMUHYAW335ZHJTPEA0M3XWPJ4CRYFFSQDZK14B0FQAL5

"""








