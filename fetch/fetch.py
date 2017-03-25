import os, sys
import pika
import json
import time

"""
fetch specific dependencies
"""

import requests
from time import sleep
from exceptions import ValueError
from lxml import html
import facebook

MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
FACEBOOK_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')

while True:
    try:
        print "attempting connection"
        _credentials = pika.PlainCredentials(MQTT_USER, MQTT_PASSWORD)
        mqtt_connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQTT_HOST, credentials=_credentials))
        break
    except Exception:
        print "connection failed"
        time.sleep(5)

ingress_channel = mqtt_connection.channel()
ingress_channel.queue_declare(queue='fetch', durable=True)
egress_channel = mqtt_connection.channel()
egress_channel.queue_declare(queue='parse', durable=True)

def linkedIn_fetch(url):
    for i in range(5):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        response = requests.get(url, headers=headers)
        formatted_response = response.content.replace('<!--', '').replace('-->', '')
        doc = html.fromstring(formatted_response)
        datafrom_xpath = doc.xpath('//code[@id="stream-right-rail-embed-id-content"]//text()')
        if datafrom_xpath:
            return datafrom_xpath
    print "cant fetch page", url
    return None

graph = facebook.GraphAPI(FACEBOOK_ACCESS_TOKEN)

def facebook_fetch(facebook_id):
    sys.stderr.write("Received Message \n" + FACEBOOK_ACCESS_TOKEN + "\n")
    facebook_company_info = graph.get_object(id=facebook_id, fields='name, about, location, phone, category')
    facebook_company_info["connections"] = graph.get_connections(id=facebook_id, connection_name='likes')['data']
    return facebook_company_info

foursquare_version = '20170101'

def foursquare_fetch(foursquare_id):
    foursquare_url = "https://api.foursquare.com/v2/venues/" + foursquare_id + "?client_id=" + FOURSQUARE_CLIENT_ID + "&client_secret=" + FOURSQUARE_CLIENT_SECRET + "&v=" + foursquare_version
    foursquare_response = requests.get(foursquare_url)  
    foursquare_response_json = foursquare_response.json() 
    return foursquare_response_json["response"]["venue"]

def foursquare_fetch_nextvenues(foursquare_id):
    nextvenues_url = "https://api.foursquare.com/v2/venues/" + foursquare_id + "/nextvenues?client_id=" + FOURSQUARE_CLIENT_ID + "&client_secret=" + FOURSQUARE_CLIENT_SECRET + "&v=" + foursquare_version
    web_response = requests.get(nextvenues_url)
    resp = web_response.json()
    next_venue_ids = [venue["id"] for venue in resp["response"]["nextVenues"]["items"]]
    return next_venue_ids if next_venue_ids else []    

def callback(ch, method, properties, body):
    sys.stderr.write("Received Message \n" + body + "\n")
    # print("Method: {}".format(method))
    # print("Properties: {}".format(properties))
    # print("Message: {}".format(body))
    data = json.loads(body)
    ingress_channel.basic_ack(delivery_tag = method.delivery_tag)
    """
    Exception handling, failing silently now (TODO)
    """
    if not data.has_key("protocol") or not data.has_key("resource_locator"):
        return
    if data["resource_locator"] == None:
        return
    """
    TODO
    Pick appropriate fetcher from url
    """
    if data["protocol"] == "http":
        html_response = linkedIn_fetch(data["resource_locator"])
        new_body = {"protocol": data["protocol"], "resource_locator": data["resource_locator"], "raw_response": html_response}

    elif data["protocol"] == "fb":
        fb_response = facebook_fetch(data["resource_locator"])
        if fb_response == None:
            return
        new_body = {"protocol": data["protocol"], "resource_locator": data["resource_locator"], "raw_response": fb_response}

    elif data["protocol"] == "fsquare":
        fsquare_response = foursquare_fetch(data["resource_locator"])

        # here we fetch the other ids of venue's nextvenues attribute
        # TO-DO: find better way of traversing foursquare
        fsquare_next_venues = foursquare_fetch_nextvenues(data["resource_locator"])
        if fsquare_response == None:
            return    
        new_body = {"protocol": data["protocol"], "resource_locator": data["resource_locator"], "raw_response": fsquare_response, "potential_leads": fsquare_next_venues} 
           
    else:
        return
    
    """
    TODO
    Handle Null fetched url
    """
    egress_channel.basic_publish(
        exchange='',
        routing_key='parse',
        body=json.dumps(new_body),
        properties=pika.BasicProperties(
            delivery_mode = 1
        )
    )
    

ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='fetch')
ingress_channel.start_consuming()




