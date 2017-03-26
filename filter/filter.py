import os, sys
import pika
import json
import time
import traceback

from peewee import *
from datetime import datetime

MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')
RECORD_TIMEOUT = os.environ.get('RECORD_TIMEOUT')
"""In Seconds"""


"""
PSQL ORM courtesy of PeeWee

No need for schema.sql since PeeWee can take care of this for us!
"""

psql_db = PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)

class BaseModel(Model):
    class Meta:
        database = psql_db

class Record_LinkedIn(BaseModel):
    url = CharField(primary_key=True)
    last_accessed = DateTimeField(default=datetime.utcnow())

class Record_Fb(BaseModel):
    fb_id = CharField(primary_key=True)
    last_accessed = DateTimeField(default=datetime.utcnow())

class Record_Fsquare(BaseModel):
    fsquare_id = CharField(primary_key=True)
    last_accessed = DateTimeField(default=datetime.utcnow())    

while True:
    try:
        psql_db.connect()
        break
    except Exception:
        time.sleep(5)

if not Record_LinkedIn.table_exists():
    Record_LinkedIn.create_table()

if not Record_Fb.table_exists():
    Record_Fb.create_table()

if not Record_Fsquare.table_exists():
    Record_Fsquare.create_table()

"""
RabbitMQ support courtesy of Pika
"""

while True:
    try:
        _credentials = pika.PlainCredentials(MQTT_USER, MQTT_PASSWORD)
        mqtt_connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQTT_HOST, credentials=_credentials))
        break
    except Exception:
        print "connection failed"
        time.sleep(5)

pqdata = dict()
pqdata['x-max-priority'] = 5

ingress_channel = mqtt_connection.channel()
ingress_channel.queue_declare(queue='filter', durable=True, arguments=pqdata)
egress_channel = mqtt_connection.channel()
egress_channel.queue_declare(queue='fetch', durable=True, arguments=pqdata)

"""
Selectors
"""

def retrieve_Fb(facebook_id):
    return Record_Fb.select().where(Record_Fb.fb_id == facebook_id).get()

def seen_fb(facebook_id):
    try:
        retrieve_Fb(facebook_id)
        return True
    except Exception:
        return False

def retrieve_LinkedIn(website):
    return Record_LinkedIn.select().where(Record_LinkedIn.url == website).get()

def seen_website(website):
    """
    TODO: test this!
    """
    try:
        retrieve_LinkedIn(website)
        return True
    except Exception:
        return False

def retrieve_Fsquare(foursquare_id):
    return Record_Fsquare.select().where(Record_Fsquare.fsquare_id == foursquare_id).get()

def seen_fsquare(foursquare_id):
    try:
        retrieve_Fsquare(foursquare_id)
        return True
    except Exception:
        return False

"""
Message Handling
"""

def seen_fb_time_ago(lead):
    if (datetime.utcnow() - retrieve_Fb(lead).last_accessed).seconds > RECORD_TIMEOUT:
        return True
    return False

def seen_linkedin_time_ago(lead):
    if (datetime.utcnow() - retrieve_LinkedIn(lead).last_accessed).seconds > RECORD_TIMEOUT:
        return True
    return False

def seen_fsquare_time_ago(lead):
    if (datetime.utcnow() - retrieve_Fsquare(lead).last_accessed).seconds > RECORD_TIMEOUT:
        return True
    return False        

def callback(ch, method, properties, body):
    try:
        raw_data = json.loads(body)
        if (not raw_data.has_key("potential_leads") or not raw_data.has_key("protocol") or not raw_data.has_key("depth")):
            if raw_data.has_key("delete") and raw_data.has_key("resource_locator") and raw_data.has_key("protocol"):
                if raw_data["protocol"] == "fb":
                    """
                    sys.stderr.write("Deleted: " + str(raw_data["resource_locator"]) + "\n")
                    sys.stderr.flush()
                    """
                    if seen_fb(raw_data["resource_locator"]):
                        retrieve_Fb(raw_data["resource_locator"]).delete_instance()
                    return

                if raw_data["protocol"] == "linkedin":
                    if seen_website(raw_data["resource_locator"]):
                        retrieve_LinkedIn(raw_data["resource_locator"]).delete_instance()
                    return

                if raw_data["protocol"] == "fsquare":
                    if seen_fsquare(raw_data["resource_locator"]):
                        retrieve_Fsquare(raw_data["resource_locator"]).delete_instance()
                    return
                            
                raise Exception("Unknown protocol requested during deletion")
            else:
                raise Exception("Body malformed") 

        potential_leads = raw_data["potential_leads"]
        protocol = raw_data["protocol"]

        for lead in potential_leads:
            if protocol == "fb":
                if not seen_fb(lead):
                    newRecord = Record_Fb(fb_id=lead, last_accessed = datetime.utcnow())
                    newRecord.save(force_insert=True)
                    """
                    TODO: Handle elif difference
                    """
                elif seen_fb_time_ago(lead):
                    Record_Fb.update(last_accessed = datetime.utcnow()).where(fb_id == lead).execute()
                    sys.stderr.write("Updating: \n" + lead + "\n")
                    sys.stderr.flush()    
                else:
                    return
            if protocol == "linkedin":
                if not seen_website(lead):
                    newRecord = Record_LinkedIn(url=lead, last_accessed = datetime.utcnow())
                    newRecord.save(force_insert=True)
                    """
                    TODO: Handle elif difference
                    """
                elif seen_linkedin_time_ago(lead):
                    Record_LinkedIn.update(last_accessed = datetime.utcnow()).where(url == lead).execute()
                    sys.stderr.write("Updating: \n" + lead + "\n")
                    sys.stderr.flush()    
                else:
                    return
            if protocol == "fsquare":
                if not seen_fsquare(lead):
                    newRecord = Record_Fsquare(fsquare_id=lead, last_accessed= datetime.utcnow())
                    newRecord.save(force_insert=True)
                elif seen_fsquare_time_ago(lead):
                    Record_Fsquare.update(last_accessed = datetime.utcnow()).where(fsquare_id == lead).execute()
                    sys.stderr.write("Updating: \n" + lead + "\n")
                    sys.stderr.flush()
                else:
                    return  
            fetch_data = {"protocol": raw_data["protocol"], "resource_locator": lead, "depth": raw_data["depth"]}
            egress_channel.basic_publish(
                exchange='',
                routing_key='fetch',
                body=json.dumps(fetch_data),
                properties=pika.BasicProperties(
                    delivery_mode = 1,
                    priority=0 # default priority
                )
            )
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to filter: \n" + body + "\n")
        traceback.print_exc()
        sys.stderr.flush()
    finally:
        ingress_channel.basic_ack(delivery_tag = method.delivery_tag)


ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='filter')
ingress_channel.start_consuming()







