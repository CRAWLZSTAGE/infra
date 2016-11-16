import os
import pika
import json
import time
"""
filter specific dependencies
"""

from peewee import *
from datetime import datetime

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

class Record(BaseModel):
    url = CharField(primary_key=True)
    last_accessed = DateTimeField(default=datetime.utcnow())

while True:
    try:
        print "attemption DB connection at ", DB_HOST
        psql_db.connect()
        break
    except Exception:
        print "connection failed"
        time.sleep(5)

if not Record.table_exists():
    Record.create_table()

while True:
    try:
        print "attempting pika connection at ", MQTT_HOST
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

def seen(website):
    """
    TODO: test this!
    """
    try:
        Record.select().where(Record.url == website).get()
        return True
    except Exception:
        return False

def callback(ch, method, properties, body):
    print("Method: {}".format(method))
    print("Properties: {}".format(properties))
    print("Message: {}".format(body))
    raw_data = json.loads(body)
    for website in raw_data:
        if not seen(website):
            egress_channel.basic_publish(
                exchange='',
                routing_key='fetch',
                body=json.dumps(website),
                properties=pika.BasicProperties(
                    delivery_mode = 1
                )
            )
            newRecord = Record(url=website)
            newRecord.save(force_insert=True)
    ingress_channel.basic_ack(delivery_tag = method.delivery_tag)


ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='filter')
ingress_channel.start_consuming()






