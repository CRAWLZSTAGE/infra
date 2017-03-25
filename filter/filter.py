import os, sys
import pika
import json
import time

"""
filter specific dependencies
"""

from peewee import *
from datetime import datetime

"""
Environment Variables
"""

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

class Record(BaseModel):
    url = CharField(primary_key=True)
    last_accessed = DateTimeField(default=datetime.utcnow())

class Record_fb(BaseModel):
    fb_id = CharField(primary_key=True)
    last_accessed = DateTimeField(default=datetime.utcnow())

while True:
    try:
        psql_db.connect()
        break
    except Exception:
        time.sleep(5)

if not Record.table_exists():
    Record.create_table()

if not Record_fb.table_exists():
    Record_fb.create_table()


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

ingress_channel = mqtt_connection.channel()
ingress_channel.queue_declare(queue='filter', durable=True)
egress_channel = mqtt_connection.channel()
egress_channel.queue_declare(queue='fetch', durable=True)


"""
Selectors
"""


def seen_fb(facebook_id):
    try:
        Record_fb.select().where(Record_fb.fb_id == facebook_id).get()
        return True
    except Exception:
        return False

def seen_website(website):
    """
    TODO: test this!
    """
    try:
        Record.select().where(Record.url == website).get()
        return True
    except Exception:
        return False

"""
Message Handling
"""

def callback(ch, method, properties, body):
    try:
        raw_data = json.loads(body)
        if not raw_data.has_key("potential_leads") or not raw_data.has_key("protocol") or not raw_data.has_key("depth"):
            raise Exception("Body malformed")
        potential_leads = raw_data["potential_leads"]
        protocol = raw_data["protocol"]
        for lead in potential_leads:
            if protocol == "fb":
                if not seen_fb(lead):
                    newRecord = Record_fb(fb_id=lead)
                    newRecord.save(force_insert=True)
                else:
                    return
            if protocol == "html":
                if not seen_website(lead):
                    newRecord = Record(url=lead)
                    newRecord.save(force_insert=True)
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
        sys.stderr.write(str(e) + "Unable to parse body: \n" + body + "\n")
        sys.stderr.flush()
    finally:
        ingress_channel.basic_ack(delivery_tag = method.delivery_tag)


ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='filter')
ingress_channel.start_consuming()







