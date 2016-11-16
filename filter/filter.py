import os
import pika
import json

"""
filter specific dependencies
"""

from storm.locals import *
from datetime import datetime

MQTT_HOST = os.environ.get('MQTT_HOST')
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

class Record:
    __store_table__ = "records"
    __storm_primary__ = "url"
    url = Unicode()
    last_accessed = DateTime()

    def __init__(self, url=None, last_accessed=None):
        self.url = url
        self.last_accessed = datetime.utcnow() if last_accessed == None else last_accessed
 
db = Store(database)

mqtt_connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=MQTT_HOST))
ingress_channel = mqtt_connection.channel()
ingress_channel.queue_declare(queue='filter', durable=True)
egress_channel = mqtt_connection.channel()
egress_channel.queue_declare(queue='fetch', durable=True)

def seen(website):
    """
    TODO: test this!
    """
    if db.find(Record, Record.url == website).one()
        return True
    return False

def callback(ch, method, properties, body):
    print("Method: {}".format(method))
    print("Properties: {}".format(properties))
    print("Message: {}".format(body))
    raw_data = json.loads(body)
    for website in raw_data
        if not seen(website):
            egress_channel.basic_publish(
                exchange='',
                routing_key='fetch',
                body=json.dumps(website),
                properties=pika.BasicProperties(
                    delivery_mode = 2, # make message persistent
                )
            )


ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='filter')
ingress_channel.start_consuming()







