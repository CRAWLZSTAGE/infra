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
FOURSQUARE_VERSION = os.environ.get('FOURSQUARE_VERSION')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
MAX_DEPTH = int(os.environ.get('MAX_DEPTH'))

import sys
import signal

def handler(signum, frame):
    sys.exit(1)

signal.signal(signal.SIGTERM, handler)

"""
import logging
logging.basicConfig(level=logging.DEBUG)
"""

"""
Note:

Should write classes and subclasses to deal with fetching from different sources.
"""

while True:
    try:
        _credentials = pika.PlainCredentials(MQTT_USER, MQTT_PASSWORD)
        mqtt_connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQTT_HOST, port=5672, credentials=_credentials))
        break
    except Exception:
        time.sleep(5)

pqdata = dict()
pqdata['x-max-priority'] = 5

ingress_channel = mqtt_connection.channel()
ingress_channel.exchange_declare(exchange='admin', type='fanout')

ingress_channel.queue_declare(queue='fetch', durable=True, arguments=pqdata)
admin_queue = ingress_channel.queue_declare(arguments=pqdata)
ingress_channel.queue_bind(exchange="admin", queue=admin_queue.method.queue)

egress_channel_parse = mqtt_connection.channel()
egress_channel_parse.queue_declare(queue='parse', durable=True, arguments=pqdata)
egress_channel_filter = mqtt_connection.channel()
egress_channel_filter.queue_declare(queue='filter', durable=True, arguments=pqdata)

"""
Fetchers
"""

def linkedIn_fetch(url):
    for _ in range(5):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        response = requests.get(url, headers=headers)
        formatted_response = response.content.replace('<!--', '').replace('-->', '')
        doc = html.fromstring(formatted_response)
        datafrom_xpath = doc.xpath('//code[@id="stream-right-rail-embed-id-content"]//text()')
        if datafrom_xpath:
            return datafrom_xpath
    return None

graph = facebook.GraphAPI(FACEBOOK_ACCESS_TOKEN)

def facebook_fetch(facebook_id):
    """
    https://developers.facebook.com/docs/graph-api/reference/page
    """
    facebook_company_info = graph.get_object(id=facebook_id, fields='name, about, location, phone, category, description, fan_count, hours, link, call_to_actions')
    if facebook_company_info.has_key("call_to_actions") and facebook_company_info["call_to_actions"].has_key("data"):
        for obj in facebook_company_info["call_to_actions"]["data"]:
            if obj.has_key("type") and obj["type"] == "CALL_NOW":
                facebook_call_now = graph.get_object(id=obj["id"], fields='from,id,intl_number_with_plus,status,type')
                if facebook_call_now.has_key("intl_number_with_plus"):
                    facebook_company_info["intl_number_with_plus"] = facebook_call_now["intl_number_with_plus"]
    facebook_company_info["connections"] = graph.get_connections(id=facebook_id, connection_name='likes')['data']
    return facebook_company_info    

def foursquare_fetch(foursquare_id):
    """
    https://developer.foursquare.com/docs/
    """
    foursquare_url = "https://api.foursquare.com/v2/venues/" + foursquare_id + "?client_id=" + FOURSQUARE_CLIENT_ID + "&client_secret=" + FOURSQUARE_CLIENT_SECRET + "&v=" + FOURSQUARE_VERSION
    foursquare_response = requests.get(foursquare_url)  
    foursquare_response_json = foursquare_response.json() 
    return foursquare_response_json["response"]["venue"]

def foursquare_fetch_nextvenues(foursquare_id):
    """
    https://developer.foursquare.com/docs/
    """
    nextvenues_url = "https://api.foursquare.com/v2/venues/" + foursquare_id + "/nextvenues?client_id=" + FOURSQUARE_CLIENT_ID + "&client_secret=" + FOURSQUARE_CLIENT_SECRET + "&v=" + FOURSQUARE_VERSION
    web_response = requests.get(nextvenues_url)
    resp = web_response.json()
    next_venue_ids = [venue["id"] for venue in resp["response"]["nextVenues"]["items"]]
    return next_venue_ids if next_venue_ids else []    

def google_fetch(google_id):
    """
    https://developers.google.com/places/web-service/
    """
    google_details_url = "https://maps.googleapis.com/maps/api/place/details/json?placeid=" + google_id + "&key=" + GOOGLE_API_KEY
    google_response = requests.get(google_details_url)
    google_response_json = google_response.json()
    return google_response_json["result"]

def google_fetch_nextvenues(google_response):
    """
    https://developers.google.com/places/web-service/

    Parameters:
    google_response: json output from google_fetch()

    Outputs:
    google_nextvenues_ids: array of google place_ids for next venues to explore
    """

    """
    First we find the latitude and longitude of the current venue
    """
    venue_latitude = google_response["geometry"]["location"]["lat"] if (google_response.has_key('geometry') and google_response['geometry'].has_key('location') and google_response['geometry']['location'].has_key('lat')) else None
    venue_longitude = google_response["geometry"]["location"]["lng"] if (google_response.has_key('geometry') and google_response['geometry'].has_key('location') and google_response['geometry']['location'].has_key('lng')) else None

    google_nextvenues_ids = [] 

    if (venue_latitude != None) and (venue_longitude != None):
        """
        We calculate new latitude and longitude to find new place_ids of locations aorund that coordinate

        Here we divide by 222.0 because 1 degree = 111.0km approximately and we want to move
        our search coordinate by 500m approximately

        Positive latitude is above the equator
        Positive longitude is east of the meridian

        We set our search radius as 500m
        """
        new_latitude = float(venue_latitude) + (1.0 / 222.0)
        new_longitude = float(venue_longitude) + (1.0 / 222.0)
        radius = 500
        next_venues_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(new_latitude) + "," + str(new_longitude) + "&radius=" + str(radius) + "&rankby=prominence&key=" + GOOGLE_API_KEY
        response = requests.get(next_venues_url)
        response_json = response.json()
        venues_results = response_json["results"]
        for venue_result in venues_results:
            google_nextvenues_ids.append(venue_result["place_id"])

    return google_nextvenues_ids     

"""
Message handling
"""

def deleteNode(data):
    new_body = {"delete": True, "resource_locator": data["resource_locator"], "protocol": data["protocol"]}
    egress_channel_filter.basic_publish(
        exchange='',
        routing_key='filter',
        body=json.dumps(new_body),
        properties=pika.BasicProperties(
            delivery_mode = 1,
            priority=0 # default priority
        )
    )

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        """
        Data bounds check
        """
        if not data.has_key("protocol") or not data.has_key("resource_locator") or not data.has_key("depth"):
            raise Exception("Body malformed")
        if data["resource_locator"] == None:
            raise Exception("Resource target unspecified")

        """
        Handle fetch drops gracefully
        """
        if data["depth"] >= MAX_DEPTH:
            deleteNode(data)
            return
        """
        Fetch Data
        """
        if data["protocol"] == "linkedin":
            try:
                html_response = linkedIn_fetch(data["resource_locator"])
                if html_response == None:
                    raise Exception("Unable to find LinkedIn data: " + str(data["resource_locator"]))
                new_body = {"protocol": data["protocol"], "resource_locator": data["resource_locator"], "raw_response": html_response, "depth": data["depth"]}
            except Exception as e:
                traceback.print_exc()
                deleteNode(data)
                raise e
        elif data["protocol"] == "fb":
            try:
                fb_response = facebook_fetch(data["resource_locator"])
                if fb_response == None:
                    raise Exception("Unable to find facebook id: " + str(data["resource_locator"]))
                new_body = {"protocol": data["protocol"], "resource_locator": data["resource_locator"], "raw_response": fb_response, "depth": data["depth"]}
            except Exception as e:
                traceback.print_exc()
                deleteNode(data)
                raise e
        elif data["protocol"] == "fsquare":
            try:
                fsquare_response = foursquare_fetch(data["resource_locator"])
                if fsquare_response == None:
                    raise Exception("Unable to find foursquare id: " + str(data["resource_locator"]))
                fsquare_next_venues = foursquare_fetch_nextvenues(data["resource_locator"])
                if fsquare_next_venues == None:
                    raise Exception("Unable to find next venues of foursquare id: " + str(data["resource_locator"]))
                new_body = {"protocol": data["protocol"], "resource_locator": data["resource_locator"], "raw_response": fsquare_response, "depth": data["depth"], "potential_leads": fsquare_next_venues} 
            except Exception as e:
                traceback.print_exc()
                deleteNode(data)
                raise e    
        elif data["protocol"] == "google":
            try:
                google_response = google_fetch(data["resource_locator"])
                if google_response == None:
                    raise Exception("Unable to find google id: " + str(data["resource_locator"]))  
                google_next_venues = google_fetch_nextvenues(google_response)
                if google_next_venues == None:
                    raise Exception("Unable to find next venues of google id: " + str(data["resource_locator"]))
                new_body = {"protocol": data["protocol"], "resource_locator": data["resource_locator"], "raw_response": google_response, "depth": data["depth"], "potential_leads": google_next_venues}  
            except Exception as e:
                traceback.print_exc()
                deleteNode(data)
                raise e               
        else:
            deleteNode(data)
            raise Exception("Unable to categorize fetch instance: \n" + str(data["protocol"]) + ": " + str(data["resource_locator"]))
        """
        Hand data over to parser
        """
        egress_channel_parse.basic_publish(
            exchange='',
            routing_key='parse',
            body=json.dumps(new_body),
            properties=pika.BasicProperties(
                delivery_mode = 1,
                priority=0 # default priority
            )
        )
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to fetch: \n" + body + "\n")
        traceback.print_exc()
        sys.stderr.flush()
    finally:
        ingress_channel.basic_ack(delivery_tag = method.delivery_tag)

def admin_callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        """
        Handle max depth
        """
        global MAX_DEPTH
        if data.has_key("maxDepth") and isinstance(data["maxDepth"], int):
            MAX_DEPTH = int(data["maxDepth"])
            return
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to fetch: \n" + body + "\n")
        traceback.print_exc()
        sys.stderr.flush()
    finally:
        ingress_channel.basic_ack(delivery_tag = method.delivery_tag)

ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='fetch')
ingress_channel.basic_consume(admin_callback, queue=admin_queue.method.queue)
ingress_channel.start_consuming()

