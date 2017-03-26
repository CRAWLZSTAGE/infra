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

class FourSquareContact(BaseModel):
    foursquare_resource_locator = TextField(primary_key=True)
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

while True:
    try:
        psql_db.connect()
        break
    except Exception:
        time.sleep(5)

if not FacebookContact.table_exists():
    FacebookContact.create_table()

if not LinkedInContact.table_exists():
    LinkedInContact.create_table()

if not FourSquareContact.table_exists():
    FourSquareContact.create_table()    

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
ingress_channel.queue_declare(queue='store', durable=True, arguments=pqdata)


"""
Updating function

- Currently it just overwrites, also makes multiple requests per update, not cool
- follower count is different for different sites
"""

def updateFacebookContact(data):
    if data.has_key("org_name") and data["org_name"] != None:
        FacebookContact.update(org_name = data["org_name"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("description") and data["description"] != None:
        FacebookContact.update(description = data["description"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("address") and data["address"] != None:
        FacebookContact.update(address = data["address"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("country") and data["country"] != None:
        FacebookContact.update(country = data["country"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("state") and data["state"] != None:
        FacebookContact.update(state = data["state"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("postal_code") and isinstance(data["postal_code"], int) and data["postal_code"] != None:
        FacebookContact.update(postal_code = data["postal_code"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("contact_no") and data["contact_no"] != None:
        FacebookContact.update(contact_no = data["contact_no"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("industry") and data["industry"] != None:
        FacebookContact.update(industry = data["industry"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("fan_count") and isinstance(data["fan_count"], int) and data["fan_count"] != None:
        FacebookContact.update(fan_count = data["fan_count"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("hours") and data["hours"] != None:
        FacebookContact.update(hours = data["hours"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("link") and data["link"] != None:
        FacebookContact.update(link = data["link"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("longitude") and data["longitude"] != None:
        FacebookContact.update(longitude = data["longitude"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("latitude") and data["latitude"] != None:
        FacebookContact.update(latitude = data["latitude"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("intl_number_with_plus") and data["intl_number_with_plus"] != None:
        FacebookContact.update(intl_number_with_plus = data["intl_number_with_plus"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    return

def updateLinkedInContact(data):
    if data.has_key("org_name") and data["org_name"] != None:
        LinkedInContact.update(org_name = data["org_name"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("org_type") and data["org_type"] != None:
        LinkedInContact.update(org_type = data["org_type"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("description") and data["description"] != None:
        LinkedInContact.update(description = data["description"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("address") and data["address"] != None:
        LinkedInContact.update(address = data["address"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("city") and data["city"] != None:
        LinkedInContact.update(city = data["city"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("state") and data["state"] != None:
        LinkedInContact.update(state = data["state"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("postal_code") and isinstance(data["postal_code"], int) and data["postal_code"] != None:
        LinkedInContact.update(postal_code = data["postal_code"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("website") and data["website"] != None:
        LinkedInContact.update(website = data["website"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("industry") and data["industry"] != None:
        LinkedInContact.update(industry = data["industry"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("specialities") and data["specialities"] != None:
        LinkedInContact.update(specialities = data["specialities"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("follower_count") and isinstance(data["follower_count"], int) and data["follower_count"] != None:
        LinkedInContact.update(follower_count = data["follower_count"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("year_founded") and data["year_founded"] != None:
        LinkedInContact.update(year_founded = data["year_founded"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("size") and data["size"] != None:
        LinkedInContact.update(size = data["size"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    return

def updateFourSquareContact(data):
    if data.has_key("org_name") and data["org_name"] != None:
        FourSquareContact.update(org_name = data["org_name"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("description") and data["description"] != None:
        FourSquareContact.update(description = data["description"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("address") and data["address"] != None:
        FourSquareContact.update(address = data["address"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("country") and data["country"] != None:
        FourSquareContact.update(country = data["country"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("state") and data["state"] != None:
        FourSquareContact.update(state = data["state"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("postal_code") and isinstance(data["postal_code"], int) and data["postal_code"] != None:
        FourSquareContact.update(postal_code = data["postal_code"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("contact_no") and data["contact_no"] != None:
        FourSquareContact.update(contact_no = data["contact_no"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("industry") and data["industry"] != None:
        FourSquareContact.update(industry = data["industry"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("fan_count") and isinstance(data["fan_count"], int) and data["fan_count"] != None:
        FourSquareContact.update(fan_count = data["fan_count"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("hours") and data["hours"] != None:
        FourSquareContact.update(hours = data["hours"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("link") and data["link"] != None:
        FourSquareContact.update(link = data["link"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("longitude") and data["longitude"] != None:
        FourSquareContact.update(longitude = data["longitude"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("latitude") and data["latitude"] != None:
        FourSquareContact.update(latitude = data["latitude"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("intl_number_with_plus") and data["intl_number_with_plus"] != None:
        FourSquareContact.update(intl_number_with_plus = data["intl_number_with_plus"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    return
"""
Message Handling
This is real ugly, should introduce classes
"""

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        if not data.has_key("org_name") or not data.has_key("protocol"):
            return
        if not data.has_key("facebook_resource_locator") and not data.has_key("linkedin_resource_locator") and not data.has_key("foursquare_resource_locator"):
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
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to parse body: \n" + body + "\n")
        traceback.print_exc()
        sys.stderr.flush()
    finally:
        ingress_channel.basic_ack(delivery_tag = method.delivery_tag)

ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='store')
ingress_channel.start_consuming()

