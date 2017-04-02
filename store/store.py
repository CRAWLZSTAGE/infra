import os, sys
import pika
import json
import time
import traceback

from peewee import *

# DEBUG = int(os.environ.get('DEBUG'))
MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')

import sys
import signal

def handler(signum, frame):
    sys.exit(1)

signal.signal(signal.SIGTERM, handler)

"""
PSQL ORM courtesy of PeeWee

No need for schema.sql since PeeWee can take care of this for us!
"""

from databaseModel import psql_db, BaseModel, FacebookContact, LinkedInContact, FourSquareContact, GoogleContact, updateFacebookContact, updateLinkedInContact, updateFourSquareContact, updateGoogleContact

while True:
    try:
        psql_db.connect()
        break
    except Exception as e:
        sys.stderr.write("Unable to connect to PSQL: \n" + str(e) + "\n")
        traceback.print_exc()
        sys.stderr.flush()
        time.sleep(5)

if not FacebookContact.table_exists():
    FacebookContact.create_table()

if not LinkedInContact.table_exists():
    LinkedInContact.create_table()

if not FourSquareContact.table_exists():
    FourSquareContact.create_table()    

if not GoogleContact.table_exists():
    GoogleContact.create_table()

"""
if not FTSFacebookContact.table_exists():
    FTSFacebookContact.create_table()

if not FTSLinkedInContact.table_exists():
    FTSLinkedInContact.create_table()

if not FTSFourSquareContact.table_exists():
    FTSFourSquareContact.create_table()

if not FTSGoogleContact.table_exists():
    FTSGoogleContact.create_table()
"""

"""
RabbitMQ support courtesy of Pika

MQTT tutorial from 
https://cuongba.com/install-rabbitmq-and-send-json-data-with-python-on-ubuntu/
"""

while True:
    try:
        _credentials = pika.PlainCredentials(MQTT_USER, MQTT_PASSWORD)
        mqtt_connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQTT_HOST, credentials=_credentials))
        break
    except Exception:
        time.sleep(5)

pqdata = dict()
pqdata['x-max-priority'] = 5

ingress_channel = mqtt_connection.channel()
ingress_channel.exchange_declare(exchange='admin', type='fanout')

ingress_channel.queue_declare(queue='store', durable=True, arguments=pqdata)
admin_queue = ingress_channel.queue_declare(arguments=pqdata)
ingress_channel.queue_bind(exchange="admin", queue=admin_queue.method.queue)
 
"""
Message Handling
This is real ugly, should introduce classes
"""

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        if not data.has_key("org_name") or not data.has_key("protocol"):
            return
        if not data.has_key("facebook_resource_locator") and not data.has_key("linkedin_resource_locator") and not data.has_key("foursquare_resource_locator") and not data.has_key("google_resource_locator"):
            raise Exception("Unable to identify resource")
        if data["protocol"] == "fb":
            newContact = FacebookContact.select().where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"])
            if newContact.exists():
                newContact = newContact.get()
            else:
                newContact = FacebookContact(facebook_resource_locator=data["facebook_resource_locator"])
                try:
                    newContact.save(force_insert=True)
                except Exception, e:
                    """
                    Collide, should not happen!
                    """
                    sys.stderr.write("Collision occured: " + str(e))
                    psql_db.rollback()
            updateFacebookContact(data)
        elif data["protocol"] == "linkedin":
            newContact = LinkedInContact.select().where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"])
            if newContact.exists():
                newContact = newContact.get()
            else:
                newContact = LinkedInContact(linkedin_resource_locator=data["linkedin_resource_locator"])
                try:
                    newContact.save(force_insert=True)
                except Exception, e:
                    sys.stderr.write("Collision occured: " + str(e)) 
                    psql_db.rollback()
            updateLinkedInContact(data)
        elif data["protocol"] == "fsquare":
            newContact = FourSquareContact.select().where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"])
            if newContact.exists():
                newContact = newContact.get()
            else:
                newContact = FourSquareContact(foursquare_resource_locator=data["foursquare_resource_locator"])
                try:
                    newContact.save(force_insert=True)
                except Exception, e:
                    """
                    Collide, should not happen!
                    """
                    sys.stderr.write("Collision occured: " + str(e))
                    psql_db.rollback()
            updateFourSquareContact(data)   
        elif data["protocol"] == "google":
            newContact = GoogleContact.select().where(GoogleContact.google_resource_locator == data["google_resource_locator"])
            if newContact.exists():
                newContact = newContact.get()
            else:
                newContact = GoogleContact(google_resource_locator=data["google_resource_locator"])
                try:
                    newContact.save(force_insert=True)
                except Exception, e:
                    """
                    Collide, should not happen!
                    """
                    sys.stderr.write("Collision occured: " + str(e))
                    psql_db.rollback()
            updateGoogleContact(data)     
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to parse body: \n" + body + "\n")
        traceback.print_exc()
        sys.stderr.flush()
    finally:
        ingress_channel.basic_ack(delivery_tag = method.delivery_tag)

def admin_callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        return
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to fetch: \n" + body + "\n")
        traceback.print_exc()
        sys.stderr.flush()
    finally:
        ingress_channel.basic_ack(delivery_tag = method.delivery_tag)

ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='store')
ingress_channel.basic_consume(admin_callback, queue=admin_queue.method.queue)
ingress_channel.start_consuming()

