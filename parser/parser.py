import os, sys
import pika
import json
import time
import threading
from Queue import Queue

"""
parser specific dependencies
"""

from lxml import html

MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
MAX_DEPTH = int(os.environ.get('MAX_DEPTH'))

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

ingress_channel_parse = mqtt_connection.channel()
ingress_channel_parse.queue_declare(queue='parse', durable=True)
ingress_channel_depth = mqtt_connection.channel()
ingress_channel_depth.queue_declare(queue='depth', durable=True)
store_egress_channel = mqtt_connection.channel()
store_egress_channel.queue_declare(queue='store', durable=True)
filter_egress_channel = mqtt_connection.channel()
filter_egress_channel.queue_declare(queue='filter', durable=True)


"""
Parsers
"""

def linkedIn_parse(url, datafrom_xpath):
    """
    TODO
    atomize this section
    """
    list_of_companies = []
    """
    remove comments
    """
    try:
        json_formatted_data = json.loads(datafrom_xpath[0])
        company_name = json_formatted_data['companyName'] if 'companyName' in json_formatted_data.keys() else None
        size = json_formatted_data['size'] if 'size' in json_formatted_data.keys() else None
        industry = json_formatted_data['industry'] if 'industry' in json_formatted_data.keys() else None
        description = json_formatted_data['description'] if 'description' in json_formatted_data.keys() else None
        follower_count = json_formatted_data['followerCount'] if 'followerCount' in json_formatted_data.keys() else None
        year_founded = json_formatted_data['yearFounded'] if 'yearFounded' in json_formatted_data.keys() else None
        website = json_formatted_data['website'] if 'website' in json_formatted_data.keys() else None
        org_type = json_formatted_data['companyType'] if 'companyType' in json_formatted_data.keys() else None
        specialities = json_formatted_data['specialties'] if 'specialties' in json_formatted_data.keys() else None
        alsoViewed = json_formatted_data['alsoViewed'] if 'alsoViewed' in json_formatted_data.keys() else None

        if "headquarters" in json_formatted_data.keys():
            city = json_formatted_data["headquarters"]['city'] if 'city' in json_formatted_data["headquarters"].keys() else None
            country = json_formatted_data["headquarters"]['country'] if 'country' in json_formatted_data['headquarters'].keys() else None
            state = json_formatted_data["headquarters"]['state'] if 'state' in json_formatted_data['headquarters'].keys() else None
            street1 = json_formatted_data["headquarters"]['street1'] if 'street1' in json_formatted_data['headquarters'].keys() else None
            street2 = json_formatted_data["headquarters"]['street2'] if 'street2' in json_formatted_data['headquarters'].keys() else None
            postal_code = json_formatted_data["headquarters"]['zip'] if 'zip' in json_formatted_data['headquarters'].keys() else None
            street = street1 + ', ' + street2
        else:
            city = None
            country = None
            state = None
            street1 = None
            street2 = None
            street = None
            postal_code = None

        contact = {
            'org_name': company_name,
            'org_type': org_type,
            'description': description,
            'address': street,
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'website': website,
            'industry': industry,
            'follower_count': follower_count,
            'specialities': specialities,
            'country': country,
            'url': url
        }

        for coy in alsoViewed:
            list_of_companies.append(coy["homeUrl"])
        return [ contact, list_of_companies ]
    except:
        raise Exception("Unable to parse linkedIn body" + datafrom_xpath)

def facebook_parse(facebook_company_info):
    """
    Parameters:
    facebook_company_info: dict, from fetcher, using get_object function

    Outputs:
    company_info: dict , information of the company
    other_companies_pages: array, each element containing an id and name
    """

    if facebook_company_info:
        company_name = facebook_company_info['name'] if ('name' in facebook_company_info) else None
        company_about = facebook_company_info['about'] if ('about' in facebook_company_info) else None
        company_phone = facebook_company_info['phone'] if ('phone' in facebook_company_info) else None
        company_category = facebook_company_info['category'] if ('category' in facebook_company_info) else None
        company_street = facebook_company_info["location"]['street'] if (facebook_company_info.has_key("location") and facebook_company_info["location"].has_key("street")) else None
        company_country = facebook_company_info["location"]['country'] if (facebook_company_info.has_key("location") and facebook_company_info["location"].has_key("country")) else None
        company_postal = facebook_company_info["location"]['zip'] if (facebook_company_info.has_key("location") and facebook_company_info["location"].has_key("zip")) else None

    potential_leads = []

    """
    TODO
    this section
    """
    for companies in facebook_company_info["connections"]:
        potential_leads.append(companies["id"])

    company_info = {
        'org_name': company_name,
        'description': company_about,
        'address': company_street,
        'country': company_country,
        'address': company_postal,
        'contact_no': company_phone,
        'industry': company_category
    }

    return company_info, potential_leads       


"""
Message Handling
"""


def parseCallback(ch, method, properties, body):
    try:
        global MAX_DEPTH
        data = json.loads(body)
        if not data.has_key("protocol") or not data.has_key("resource_locator") or not data.has_key("raw_response") or not data.has_key("depth"):
            raise Exception("Body malformed")
        if data.has_key("raw_response") == None:
            raise Exception("None Message Recieved")
        """
        TODO
        use appropriate parser according to URL
        """
        if data["protocol"] == "http":
            contact, potential_leads = linkedIn_parse(data["resource_locator"], data["raw_response"])
            if contact == None:
                return
        elif data["protocol"] == "fb":
            contact, potential_leads = facebook_parse(data["raw_response"])
        store_egress_channel.basic_publish(
            exchange='',
            routing_key='store',
            body=json.dumps(contact),
            properties=pika.BasicProperties(
                delivery_mode = 1
            )
        )
        """
        Recurse further if depth is not reached yet
        """
        if data["depth"] >= MAX_DEPTH:
            return
        leads_data = {"potential_leads": potential_leads, "protocol": data["protocol"], "depth": data["depth"] + 1}
        filter_egress_channel.basic_publish(
            exchange='',
            routing_key='filter',
            body=json.dumps(leads_data),
            properties=pika.BasicProperties(
                delivery_mode = 1
            )
        )
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to parse body: \n" + body + "\n")
        sys.stderr.flush()
    finally:
        ingress_channel_parse.basic_ack(delivery_tag = method.delivery_tag)


def maxDepth(ch, method, properties, body):
    try:
        global MAX_DEPTH
        data = json.loads(body)
        if not data.has_key("maxDepth") or type(data["maxDepth"]) != int:
            raise Exception("Body malformed")
        MAX_DEPTH = data["maxDepth"]
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to parse body: \n" + body + "\n")
        sys.stderr.flush()
    finally:
        ingress_channel_depth.basic_ack(delivery_tag = method.delivery_tag)

def consume_messages(channel, callback, queueName):
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=queueName)
    channel.start_consuming()

"""
Handle multiple blocking pika threads

Issue with globals
https://github.com/pika/pika/issues/158
"""

THREADS = list()

# Create the two listening threads.
THREADS.append(threading.Thread(target=consume_messages,
                                args=(ingress_channel_parse, parseCallback,
                                      'parse')))
THREADS.append(threading.Thread(target=consume_messages,
                                args=(ingress_channel_depth, maxDepth,
                                      'depth')))

# Start the threads that handle incoming messages.
for thread in THREADS:
    thread.daemon = True
    thread.start()

# Wait until the threads are dead.
while sum([thread.isAlive() for thread in THREADS]):
    time.sleep(1)










