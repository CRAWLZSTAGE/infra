"""
Rest API for searching results
"""

import os, sys
import pika
import json
import time
import traceback

from peewee import *
from extract_search import find_facebook_links, find_linkedin_links


MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')

DB_HOST = os.environ.get('DB_HOST')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')

psql_db = PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)

class BaseModel(Model):
    class Meta:
        database = psql_db


class FacebookContact(BaseModel):
    facebook_resource_locator = TextField(primary_key=True)
    org_name = CharField(null = True)
    description = TextField(null = True)
    address = TextField(null = True)
    country = CharField(null = True)
    state = CharField(null = True)
    postal_code = IntegerField(null = True)
    contact_no = CharField(null = True)
    industry = CharField(null = True)
    fan_count = IntegerField(null = True)
    hours = TextField(null = True)
    link = TextField(null = True)
    longitude = TextField(null = True)
    latitude = TextField(null = True)
    intl_number_with_plus = TextField(null = True)

class LinkedInContact(BaseModel):
    linkedin_resource_locator = TextField(primary_key = True)
    org_name = CharField(null = True)
    org_type = CharField(null = True)
    description = TextField(null = True)
    address = TextField(null = True)
    city = CharField(null = True)
    state = CharField(null = True)
    postal_code = IntegerField(null = True)
    website = TextField(null = True)
    industry = CharField(null = True)
    specialities = TextField(null = True)
    follower_count = IntegerField(null = True)
    year_founded = TextField(null = True)
    size = TextField(null = True)

while True:
    try:
        psql_db.connect()
        break
    except Exception:
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

def setDepth(newDepth, channel, _routing_key):
    newbody = {"maxDepth": newDepth}
    channel.basic_publish(
        exchange='',
        routing_key=_routing_key,
        body=json.dumps(newbody),
        properties=pika.BasicProperties(
            delivery_mode = 1,
            priority=1 # default priority
        )
    )

def _convertToList(contactsFromModel):
    _ = list()
    for contact in contactsFromModel:
        _.append(model_to_dict(contact))
    return _

def send_facebook_contacts(channel, facebook_contacts, _routing_key):
    for contact in facebook_contacts:
        newbody = {
            "protocol": "fb", 
            "resource_locator": contact["id"], 
            "raw_response": contact, 
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
    return

def send_facebook_ids(channel, facebook_ids, _routing_key):
    newbody = {
        "protocol": "fb", 
        "potential_leads": facebook_ids, 
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
    return

def send_linkedin_ids(channel, linkedin_ids, _routing_key):
    newbody = {
        "protocol": "linkedin", 
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


"""
Flask

WARN
Parallelize workflow on loaded search api
"""

from flask import Flask, url_for
from playhouse.shortcuts import model_to_dict, dict_to_model
app = Flask(__name__)

from extract_search import find_facebook_links, find_linkedin_links

@app.route('/api/search/<searchTerm>')
def search(searchTerm):
    """SEARCH"""
    facebook_contacts, facebook_ids = find_facebook_links(searchTerm)
    linkedin_ids = find_linkedin_links(searchTerm)

    mqtt_connection = openConnection()
    pqdata = dict()
    pqdata['x-max-priority'] = 5
    egress_channel_parse = mqtt_connection.channel()
    egress_channel_parse.queue_declare(queue='parse', durable=True, arguments=pqdata)
    egress_channel_filter = mqtt_connection.channel()
    egress_channel_filter.queue_declare(queue='filter', durable=True, arguments=pqdata)

    send_facebook_contacts(egress_channel_parse, facebook_contacts, "parse")
    send_facebook_ids(egress_channel_filter, facebook_ids, "filter")
    send_linkedin_ids(egress_channel_filter, linkedin_ids, "filter")

    mqtt_connection.close()

    facebookContacts = FacebookContact.select().where(FacebookContact.org_name.contains(searchTerm))
    linkedinContacts = LinkedInContact.select().where(LinkedInContact.org_name.contains(searchTerm))
    returnValues = {
        "facebookContacts": _convertToList(facebookContacts),
        "linkedinContacts": _convertToList(linkedinContacts)
    }
    return json.dumps(returnValues)


@app.route('/api/setDepth/<int:newDepth>')
def _setDepth(newDepth):
    newDepth = int(newDepth)

    mqtt_connection = openConnection()

    pqdata = dict()
    pqdata['x-max-priority'] = 5

    egress_channel_fetch = mqtt_connection.channel()
    egress_channel_fetch.queue_declare(queue='fetch', durable=True, arguments=pqdata)
    egress_channel_parse = mqtt_connection.channel()
    egress_channel_parse.queue_declare(queue='parse', durable=True, arguments=pqdata)

    setDepth(newDepth, egress_channel_fetch, "fetch")
    setDepth(newDepth, egress_channel_parse, "parse")
    mqtt_connection.close()
    return 'Depth set: ' + str(newDepth)

while True:
    try:
        app.run(host='0.0.0.0', port=80)
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to parse body: \n" + body + "\n")
        traceback.print_exc()
        sys.stderr.flush()




