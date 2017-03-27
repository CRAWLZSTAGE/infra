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
    if not isinstance(newTerm, str) and not isinstance(newTerm, unicode):
        raise Exception("Term is not a string<" + str(type(newTerm)) + ">: " + str(newTerm))
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
    if not isinstance(newTerm, str) and not isinstance(newTerm, unicode):
        raise Exception("Term is not a string<" + str(type(newTerm)) + ">: " + str(newTerm))
    urls = genericSearch(newTerm + " site:www.linkedin.com")
    linkedin_ids = list()
    for url in urls:
        linkedin_ids.append(url)
    return linkedin_ids
