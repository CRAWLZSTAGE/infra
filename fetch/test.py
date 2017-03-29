import os, sys
import pika
import json
import time
import traceback
"""
fetch specific dependencies
"""

import requests
from time import sleep
from lxml import html
import facebook

MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
FACEBOOK_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
MAX_DEPTH = int(os.environ.get('MAX_DEPTH'))

graph = facebook.GraphAPI(FACEBOOK_ACCESS_TOKEN)

import time
start_time = time.time()
facebook_company_info = graph.get_object(id="1443823632507167", fields='name, about, location, phone, category, description, fan_count, hours, link, call_to_actions')
facebook_company_info = graph.get_object(id="420608754800233", fields='name, about, location, phone, category, description, fan_count, hours, link, call_to_actions')
facebook_company_info = graph.get_object(id="10084673031", fields='name, about, location, phone, category, description, fan_count, hours, link, call_to_actions')
facebook_company_info = graph.get_object(id="113901278620393", fields='name, about, location, phone, category, description, fan_count, hours, link, call_to_actions')
elapsed = time.time() - start
print time_elasped