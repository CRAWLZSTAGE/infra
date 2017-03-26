import os, sys
import pika
import json
import time
import traceback

import requests
from lxml import html
import facebook

MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
FACEBOOK_ACCESS_TOKEN = os.environ.get('FACEBOOK_ACCESS_TOKEN')
MAX_DEPTH = int(os.environ.get('MAX_DEPTH'))

"""
Note:

Should write classes and subclasses to deal with fetching from different sources.
"""

"""
RabbitMQ support courtesy of Pika
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
ingress_channel.queue_declare(queue='fetch', durable=True, arguments=pqdata)
egress_channel_parse = mqtt_connection.channel()
egress_channel_parse.queue_declare(queue='parse', durable=True, arguments=pqdata)
egress_channel_filter = mqtt_connection.channel()
egress_channel_filter.queue_declare(queue='filter', durable=True, arguments=pqdata)

"""
Fetchers
"""

def linkedIn_fetch(url):
    for _ in range(5):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        response = requests.get(url, headers=headers)
        formatted_response = response.content.replace('<!--', '').replace('-->', '')
        doc = html.fromstring(formatted_response)
        datafrom_xpath = doc.xpath('//code[@id="stream-right-rail-embed-id-content"]//text()')
        if datafrom_xpath:
            return datafrom_xpath
    return None

graph = facebook.GraphAPI(FACEBOOK_ACCESS_TOKEN)

def facebook_fetch(facebook_id):
    """
    https://developers.facebook.com/docs/graph-api/reference/page
    """
    facebook_company_info = graph.get_object(id=facebook_id, fields='name, about, location, phone, category, description, fan_count, hours, link, call_to_actions')
    if facebook_company_info.has_key("call_to_actions") and facebook_company_info["call_to_actions"].has_key("data"):
        for obj in facebook_company_info["call_to_actions"]["data"]:
            if obj.has_key("type") and obj["type"] == "CALL_NOW":
                facebook_call_now = graph.get_object(id=obj["id"], fields='from,id,intl_number_with_plus,status,type')
                if facebook_call_now.has_key("intl_number_with_plus"):
                    facebook_company_info["intl_number_with_plus"] = facebook_call_now["intl_number_with_plus"]
    facebook_company_info["connections"] = graph.get_connections(id=facebook_id, connection_name='likes')['data']
    return facebook_company_info

"""
Message Handling
"""

def deleteNode(data):
    new_body = {"delete": True, "resource_locator": data["resource_locator"], "protocol": data["protocol"]}
    egress_channel_filter.basic_publish(
        exchange='',
        routing_key='filter',
        body=json.dumps(new_body),
        properties=pika.BasicProperties(
            delivery_mode = 1,
            priority=0 # default priority
        )
    )


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        """
        Handle max depth
        """
        global MAX_DEPTH
        if data.has_key("maxDepth") and isinstance(data["maxDepth"], int):
            MAX_DEPTH = int(data["maxDepth"])
            return
        """
        Data bounds check
        """
        if not data.has_key("protocol") or not data.has_key("resource_locator") or not data.has_key("depth"):
            raise Exception("Body malformed")
        if data["resource_locator"] == None:
            raise Exception("Resource target unspecified")
        """
        Handle fetch drops gracefully
        """
        if data["depth"] >= MAX_DEPTH:
            deleteNode(data)
            return
        """
        Fetch Data
        """
        if data["protocol"] == "linkedin":
            try:
                html_response = linkedIn_fetch(data["resource_locator"])
                if html_response == None:
                    raise Exception("Unable to find LinkedIn data: " + str(data["resource_locator"]))
                new_body = {"protocol": data["protocol"], "resource_locator": data["resource_locator"], "raw_response": html_response, "depth": data["depth"]}
            except Exception as e:
                traceback.print_exc()
                deleteNode(data)
                raise e
        elif data["protocol"] == "fb":
            try:
                fb_response = facebook_fetch(data["resource_locator"])
                if fb_response == None:
                    raise Exception("Unable to find facebook id: " + str(data["resource_locator"]))
                new_body = {"protocol": data["protocol"], "resource_locator": data["resource_locator"], "raw_response": fb_response, "depth": data["depth"]}
            except Exception as e:
                traceback.print_exc()
                deleteNode(data)
                raise e
        else:
            deleteNode(data)
            raise Exception("Unable to categorize fetch instance: \n" + str(data["protocol"]) + ": " + str(data["resource_locator"]))
        """
        Hand data over to parser
        """
        egress_channel_parse.basic_publish(
            exchange='',
            routing_key='parse',
            body=json.dumps(new_body),
            properties=pika.BasicProperties(
                delivery_mode = 1,
                priority=0 # default priority
            )
        )
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to fetch: \n" + body + "\n")
        traceback.print_exc()
        sys.stderr.flush()
    finally:
        ingress_channel.basic_ack(delivery_tag = method.delivery_tag)

ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='fetch')
ingress_channel.start_consuming()
