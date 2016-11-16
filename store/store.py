import os
import pika
import json
import time

"""
store specific dependencies
"""

from peewee import *

MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')


"""
This script uses the storm ORM module from canonical
https://storm.canonical.com/FrontPage#Documentation
"""

psql_db = PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)

class BaseModel(Model):
    class Meta:
        database = psql_db

class Contact(BaseModel):
    org_name = CharField(primary_key=True)
    org_type = CharField(null = True)
    description = TextField(null = True)
    address = TextField(null = True)
    city = CharField(null = True)
    state = CharField(null = True)
    postal_code = IntegerField(default=0, null = True)
    contact_no = CharField(null = True)
    fax_no = CharField(null = True)
    email_address = TextField(null = True)
    website = TextField(null = True)
    industry = CharField(null = True)
    follower_count = IntegerField(default=0, null = True)

while True:
    try:
        print "attemption DB connection at ", DB_HOST
        psql_db.connect()
        break
    except Exception:
        print "connection failed"
        time.sleep(5)

if not Contact.table_exists():
    Contact.create_table()

"""
MQTT tutorial from 
https://cuongba.com/install-rabbitmq-and-send-json-data-with-python-on-ubuntu/
"""

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
ingress_channel.queue_declare(queue='store', durable=True)

def callback(ch, method, properties, body):
    print("Method: {}".format(method))
    print("Properties: {}".format(properties))
    print("Message: {}".format(body))
    data = json.loads(body)
    if not data.has_key("org_name"):
        return
    newContact = Contact(org_name=data["org_name"])
    if data.has_key("contact_no"):
        newContact.contact_no = data["contact_no"]
    if data.has_key("org_type"):
        newContact.org_type = data["org_type"]
    if data.has_key("description"):
        newContact.description = data["description"]
    if data.has_key("address"):
        newContact.address = data["address"]
    if data.has_key("city"):
        newContact.city = data["city"]
    if data.has_key("state"):
        newContact.state = data["state"]
    if data.has_key("postal_code") and type(data["postal_code"]) == int:
        newContact.postal_code = data["postal_code"]
    if data.has_key("fax_no"):
        newContact.fax_no = data["fax_no"]
    if data.has_key("email_address"):
        newContact.email_address = data["email_address"]
    if data.has_key("website"):
        newContact.website = data["website"]
    if data.has_key("follower_count") and type(data["follower_count"]) == int:
        newContact.follower_count = data["follower_count"]
    """
    TODO
    Check for collision
    """
    newContact.save(force_insert=True)
    ingress_channel.basic_ack(delivery_tag = method.delivery_tag)

ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='store')
ingress_channel.start_consuming()

