"""
Rest API for searching results
"""

import os, sys
import pika
import json
import time
import traceback

"""from peewee import *"""
from playhouse.postgres_ext import Match
from playhouse.shortcuts import model_to_dict, dict_to_model
from extract_search import find_facebook_links, find_linkedin_links, find_google_links, find_fsquare_links


MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')

DB_HOST = os.environ.get('DB_HOST')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')

import sys
import signal

def handler(signum, frame):
    sys.exit(1)

signal.signal(signal.SIGTERM, handler)

from databaseModel import psql_db, BaseModel, FacebookContact, LinkedInContact, FourSquareContact, GoogleContact, _Match

while True:
    try:
        psql_db.connect()
        break
    except Exception as e:
        sys.stderr.write("Unable to connect to PSQL: \n" + str(e) + "\n")
        traceback.print_exc()
        sys.stderr.flush()
        time.sleep(5)

def openConnection():
    try:
        _credentials = pika.PlainCredentials(MQTT_USER, MQTT_PASSWORD)
        mqtt_connection = pika.BlockingConnection(
            parameters=pika.ConnectionParameters(host=MQTT_HOST, credentials=_credentials), 
        )
    except Exception as e:
        raise e
    return mqtt_connection

def setDepth(newDepth, channel):
    newbody = {"maxDepth": newDepth}
    channel.basic_publish(
        exchange='admin',
        routing_key='',
        body=json.dumps(newbody),
        properties=pika.BasicProperties(
            delivery_mode = 1,
            priority=1 # default priority
        )
    )

def _convertToList(contactsFromModel):
    _ = list()
    if len(contactsFromModel) == 0:
        return _
    for contact in contactsFromModel:
        _.append(model_to_dict(contact))
    return _

def send_facebook_contacts(channel, facebook_contacts, _routing_key):
    for contact in facebook_contacts:
        newbody = {
            "protocol": "fb", 
            "resource_locator": contact["id"], 
            "raw_response": contact, 
            "depth": 1
        }
        channel.basic_publish(
            exchange='',
            routing_key=_routing_key,
            body=json.dumps(newbody),
            properties=pika.BasicProperties(
                delivery_mode = 1,
                priority = 1 # default priority
            )
        )
    return

def send_ids(channel, linkedin_ids, _routing_key, protocol):
    newbody = {
        "protocol": protocol, 
        "potential_leads": linkedin_ids, 
        "depth": 1,
        "priority": 1
    }
    channel.basic_publish(
        exchange='',
        routing_key=_routing_key,
        body=json.dumps(newbody),
        properties=pika.BasicProperties(
            delivery_mode = 1,
            priority = 1 # default priority
        )
    )


import threading

# called by each thread
def injectNewSearchTerms(searchTerm, lat, lon):
    """SEARCH"""
    fb_contacts, fb_ids = find_facebook_links(searchTerm)
    """linkedin_ids = find_linkedin_links(searchTerm)"""
    google_ids = find_google_links(searchTerm)
    fsquare_ids = None
    if lat and lon:
        fsquare_ids = find_fsquare_links(searchTerm, lat, lon)

    mqtt_connection = openConnection()
    pqdata = dict()
    pqdata['x-max-priority'] = 5
    egress_channel_parse = mqtt_connection.channel()
    egress_channel_parse.queue_declare(queue='parse', durable=True, arguments=pqdata)
    egress_channel_filter = mqtt_connection.channel()
    egress_channel_filter.queue_declare(queue='filter', durable=True, arguments=pqdata)

    send_facebook_contacts(egress_channel_parse, fb_contacts, "parse")
    send_ids(egress_channel_filter, fb_ids, "filter", "fb")
    send_ids(egress_channel_filter, google_ids, "filter", "google")
    if fsquare_ids != None:
        send_ids(egress_channel_filter, fsquare_ids, "filter", "fsquare")
    
    """send_ids(egress_channel_filter, linkedin_ids, "filter", "linkedin")"""

    mqtt_connection.close()

"""
Flask

WARN
- Parallelize workflow on loaded search api
- reparsing data is not time efficient -> find a way to join 2 sets of data together?
"""

from flask import Flask, request, url_for
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": ['https://crawlz.me', 'https://localhost', 'https://localhost:8080', 'https://127.0.0.1', 'https://127.0.0.1:8080']}})

from extract_search import find_facebook_links, find_linkedin_links

@app.route('/api/fastSearch/<searchTerm>')
def fastSearch(searchTerm):
    if not isinstance(searchTerm, str) and not isinstance(searchTerm, unicode):
        raise Exception("Term is not a string<" + str(type(searchTerm)) + ">: " + str(searchTerm))
    """facebookContacts = FacebookContact.select().where(FacebookContact.org_name.contains(searchTerm)).order_by(FacebookContact.fan_count.desc()).limit(50)"""
    newSearchTerms = " & ".join(searchTerm.split())
    psql_db.close()
    psql_db.connect()
    try:
        facebookContacts = FacebookContact.select().where((_Match(FacebookContact.search_content, newSearchTerms)) | (FacebookContact.org_name.contains(searchTerm))).order_by(FacebookContact.fan_count.desc()).limit(50)
    except:
        psql_db.rollback()
        facebookContacts = list()
    try:
        googleMapsContacts = GoogleContact.select().where((_Match(GoogleContact.search_content, newSearchTerms)) | (GoogleContact.org_name.contains(searchTerm))).limit(50)
    except:
        psql_db.rollback()
        googleMapsContacts = list()
    try:
        foursquareContacts = FourSquareContact.select().where((_Match(FourSquareContact.search_content, newSearchTerms)) | (FourSquareContact.org_name.contains(searchTerm))).order_by(FourSquareContact.fan_count.desc()).limit(50)
    except:
        psql_db.rollback()
        foursquareContacts = list()

    returnValues = list()
    try:
        returnValues = {
            "facebookContacts": _convertToList(facebookContacts),
            "linkedinContacts": [],
            "googleContacts" : _convertToList(googleMapsContacts),
            "foursquareContacts" : _convertToList(foursquareContacts)
        }
    except:
        psql_db.rollback()
    return json.dumps(returnValues)

@app.route('/api/search/<searchTerm>')
def search(searchTerm):
    if not isinstance(searchTerm, str) and not isinstance(searchTerm, unicode):
        raise Exception("Term is not a string<" + str(type(searchTerm)) + ">: " + str(searchTerm))
    t = threading.Thread(target=injectNewSearchTerms, args=[searchTerm, request.args.get('lat'), request.args.get('lon')])
    t.daemon = True
    t.start()
    return fastSearch(searchTerm)

@app.route('/api/setDepth/<int:newDepth>')
def _setDepth(newDepth):
    newDepth = int(newDepth)

    mqtt_connection = openConnection()

    pqdata = dict()
    pqdata['x-max-priority'] = 5

    egress_channel = mqtt_connection.channel()

    setDepth(newDepth, egress_channel)
    mqtt_connection.close()
    return 'Depth set: ' + str(newDepth)

while True:
    try:
        app.run(host='0.0.0.0', port=80)
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to parse body: \n" + "\n")
        traceback.print_exc()
        sys.stderr.flush()




