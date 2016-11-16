import os
import pika
import json

"""
fetch specific dependencies
"""

import requests
from time import sleep
from exceptions import ValueError
from lxml import html

MQTT_HOST = os.environ.get('MQTT_HOST')

mqtt_connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=MQTT_HOST))
ingress_channel = mqtt_connection.channel()
ingress_channel.queue_declare(queue='fetch', durable=True)
egress_channel = mqtt_connection.channel()
egress_channel.queue_declare(queue='parse', durable=True)

def linkedIn_fetch(url):
    for i in range(5):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        response = requests.get(url, headers=headers)
        formatted_response = response.content.replace('<!--', '').replace('-->', '')
        doc = html.fromstring(formatted_response)
        datafrom_xpath = doc.xpath('//code[@id="stream-right-rail-embed-id-content"]//text()')
        if datafrom_xpath
            return response
    print "cant fetch page", url
    return None

def callback(ch, method, properties, body):
    print("Method: {}".format(method))
    print("Properties: {}".format(properties))
    print("Message: {}".format(body))
    raw_data = json.loads(body)
    if not raw_data.has_key("url"):
        return
    """
    TODO
    Pick appropriate fetcher from url
    """
    html_response = linkedIn_fetch(url)
    new_body = {"url": url, "html_response": html_response}
    """
    TODO
    Handle Null fetched url
    """
    egress_channel.basic_publish(
        exchange='',
        routing_key='parse',
        body=json.dumps(new_body),
        properties=pika.BasicProperties(
            delivery_mode = 2, # make message persistent
        )
    )

ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='fetch')
ingress_channel.start_consuming()