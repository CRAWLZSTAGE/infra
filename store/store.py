import os
import pika
import json
import time

"""
store specific dependencies
"""

from storm.locals import *

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

database = create_database("postgres://" + 
    DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST 
    + ":5432/" + DB_NAME)

class Contact:
    __storm_table__ = "contacts"
    __storm_primary__ = "org_name"
    org_name = unicode()
    org_type = unicode()
    description = unicode()
    address = unicode()
    city = unicode()
    state = unicode()
    postal_code = Int()
    contact_no = unicode()
    fax_no = unicode()
    email_address = unicode()
    website = unicode()
    industry = unicode()
    follower_count = Int()

    def __init__(self, org_name=None, org_type=None, description=None, 
        address=None, city=None, state=None, postal_code=None, 
        contact_no=None, fax_no=None, email_address=None, 
        website=None, industry=None, follower_count=None):
        self.org_name = org_name
        self.org_type = org_type
        self.description = description
        self.address = address
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.contact_no = contact_no
        self.fax_no = fax_no
        self.email_address = email_address
        self.website = website
        self.industry = industry
        self.follower_count = follower_count
 
db = Store(database)

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
    if not data.has_key("org_name") or not data.has_key("contact_no"):
        return
    newContact = Contact(data["org_name"], data["contact_no"])
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
    if data.has_key("postal_code"):
        newContact.postal_code = data["postal_code"]
    if data.has_key("fax_no"):
        newContact.fax_no = data["fax_no"]
    if data.has_key("email_address"):
        newContact.email_address = data["email_address"]
    if data.has_key("website"):
        newContact.website = data["website"]
    if data.has_key("follower_count"):
        newContact.follower_count = data["follower_count"]
    """
    TODO
    Check for collision
    """
    db.add(newContact)
    db.commit()
    ch.basic_ack(delivery_tag = method.delivery_tag)

ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='store')
ingress_channel.start_consuming()

