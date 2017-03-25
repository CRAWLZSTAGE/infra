import os, sys, socket
import pika
import json
import time

"""
store specific dependencies
"""

from peewee import *

# DEBUG = int(os.environ.get('DEBUG'))
MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')

DB_HOST = os.environ.get('DB_HOST')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')


"""
PSQL ORM courtesy of PeeWee

No need for schema.sql since PeeWee can take care of this for us!
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
        psql_db.connect()
        break
    except Exception:
        time.sleep(5)

if not Contact.table_exists():
    Contact.create_table()

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

ingress_channel = mqtt_connection.channel()
ingress_channel.queue_declare(queue='store', durable=True)


"""
Updating function

- Currently it just overwrites, also makes multiple requests per update, not cool
- follower count is different for different sites
"""

def updateContact(data):
    if data.has_key("contact_no") and data["contact_no"] != None:
        Contact.update(contact_no = data["contact_no"]).where(Contact.org_name == data["org_name"]).execute()
    if data.has_key("org_type") and data["org_type"] != None:
        Contact.update(org_type = data["org_type"]).where(Contact.org_name == data["org_name"]).execute()
    if data.has_key("description") and data["description"] != None:
        Contact.update(description = data["description"]).where(Contact.org_name == data["org_name"]).execute()
    if data.has_key("address") and data["address"] != None:
        Contact.update(address = data["address"]).where(Contact.org_name == data["org_name"]).execute()
    if data.has_key("city") and data["city"] != None:
        Contact.update(city = data["city"]).where(Contact.org_name == data["org_name"]).execute()
    if data.has_key("state") and data["state"] != None:
        Contact.update(state = data["state"]).where(Contact.org_name == data["org_name"]).execute()
    if data.has_key("postal_code") and type(data["postal_code"]) == int and data["postal_code"] != None:
        Contact.update(postal_code = data["postal_code"]).where(Contact.org_name == data["org_name"]).execute()
    if data.has_key("fax_no") and data["fax_no"] != None:
        Contact.update(fax_no = data["fax_no"]).where(Contact.org_name == data["org_name"]).execute()
    if data.has_key("email_address") and data["email_address"] != None:
        Contact.update(email_address = data["email_address"]).where(Contact.org_name == data["org_name"]).execute()
    if data.has_key("website") and data["website"] != None:
        Contact.update(website = data["website"]).where(Contact.org_name == data["org_name"]).execute()
    if data.has_key("follower_count") and type(data["follower_count"]) == int and data["follower_count"] != None:
        Contact.update(follower_count = data["follower_count"]).where(Contact.org_name == data["org_name"]).execute()
    return


"""
Message Handling
"""

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        if not data.has_key("org_name"):
            return
        newContact = Contact.select().where(Contact.org_name == data["org_name"])
        if newContact.exists():
            newContact = newContact.get()
        else:
            newContact = Contact(org_name=data["org_name"])
            try:
                newContact.save(force_insert=True)
            except Exception, e:
                """
                Collide, should not happen!
                """
                sys.stderr.write("Collision occured: " + str(e)) 
                psql_db.rollback()
        updateContact(data)
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to parse body: \n" + body + "\n")
        sys.stderr.flush()
    finally:
        ingress_channel.basic_ack(delivery_tag = method.delivery_tag)
    

ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='store')
ingress_channel.start_consuming()

