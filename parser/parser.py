import os
import pika
import json
import time

"""
parser specific dependencies
"""

from lxml import html

MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')

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
ingress_channel.queue_declare(queue='parse', durable=True)
store_egress_channel = mqtt_connection.channel()
store_egress_channel.queue_declare(queue='store', durable=True)
filter_egress_channel = mqtt_connection.channel()
filter_egress_channel.queue_declare(queue='filter', durable=True)

def linkedIn_parse(url, html_response):
    """
    TODO
    atomize this section
    """
    list_of_companies = []
    """
    remove comments
    """
    formatted_response = html_response.content.replace('<!--', '').replace('-->', '')
    doc = html.fromstring(formatted_response)
    datafrom_xpath = doc.xpath('//code[@id="stream-right-rail-embed-id-content"]//text()')
    if datafrom_xpath:
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
                'url': url,
            }

            for coy in alsoViewed:
                list_of_companies.append(coy["homeUrl"])
            return [ contact, list_of_companies ]
        except:
            print "cant parse page", url
            return None
    print "cannot find element", url
    return None


def callback(ch, method, properties, body):
    print("Method: {}".format(method))
    print("Properties: {}".format(properties))
    print("Message: {}".format(body))
    raw_data = json.loads(body)
    if not raw_data.has_key("url") or not raw_data.has_key("html_response"):
        return
    """
    TODO
    use appropriate parser according to URL
    """
    contact, list_of_companies = linkedIn_parse(raw_data["url"], raw_data["html_response"])
    if contact == None:
        return
    store_egress_channel.basic_publish(
        exchange='',
        routing_key='store',
        body=json.dumps(contact),
        properties=pika.BasicProperties(
            delivery_mode = 2, # make message persistent
        )
    )
    filter_egress_channel.basic_publish(
        exchange='',
        routing_key='filter',
        body=json.dumps(list_of_companies),
        properties=pika.BasicProperties(
            delivery_mode = 2, # make message persistent
        )
    )

ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='parse')
ingress_channel.start_consuming()













