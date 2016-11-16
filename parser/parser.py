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

FACEBOOK_ACCESS_TOKEN = 'access token here'

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
            'url': url,
        }

        for coy in alsoViewed:
            list_of_companies.append(coy["homeUrl"])
        return [ contact, list_of_companies ]
    except:
        print "cant parse page", url
        return [ None, None ]


def concatenate_facebook_location(company_location_dict):
    """
    Parameters:
    company_location_dict: dict, company's location dict from get_object

    Outputs:
    company_location: str, concatenated string 
    """
    company_street = company_location_dict['street'] if ('street' in company_location_dict) else ''
    company_country = company_location_dict['country'] if ('country' in company_location_dict)  else ''
    company_postal = company_location_dict['zip'] if ('zip' in company_location_dict) else ''
    company_location = company_street + ', ' + company_country + ' ' + company_postal
    company_location = company_location.strip()
    company_location = company_location.strip(',')

    return company_location


def facebook_parse(facebook_company_info):
    """
    Parameters:
    facebook_company_info: dict, from fetcher, using get_object function

    Outputs:
    company_info: dict , information of the company
    other_companies_pages: array, each element containing an id and name
    """

    if facebook_company_info:
        company_name = facebook_company_info['name'] if ('name' in facebook_company_info) else ''
        company_about = facebook_company_info['about'] if ('about' in facebook_company_info) else ''
        company_phone = facebook_company_info['phone'] if ('phone' in facebook_company_info) else ''
        company_category = facebook_company_info['category'] if ('category' in facebook_company_info) else ''
        if ('location' not in facebook_company_info):
            company_location = ''
        else:   
            company_location = concatenate_facebook_location(facebook_company_info['location'])

    company_info = {
        'name': company_name,
        'about': company_about,
        'location': company_location,
        'contact_number': company_phone,
        'category': company_category
    }

    other_companies_pages = graph.get_connections(id=timbreplus_profile['id'], connection_name='likes')['data'] 

    return company_info, other_companies_pages       

def callback(ch, method, properties, body):
    print("Method: {}".format(method))
    print("Properties: {}".format(properties))
    print("Message: {}".format(body))
    raw_data = json.loads(body)
    ingress_channel.basic_ack(delivery_tag = method.delivery_tag)
    if not raw_data.has_key("url") or not raw_data.has_key("html_response"):
        return
    if raw_data.has_key("html_response") == None:
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
            delivery_mode = 1
        )
    )
    filter_egress_channel.basic_publish(
        exchange='',
        routing_key='filter',
        body=json.dumps(list_of_companies),
        properties=pika.BasicProperties(
            delivery_mode = 1
        )
    )

ingress_channel.basic_qos(prefetch_count=1)
ingress_channel.basic_consume(callback, queue='parse')
ingress_channel.start_consuming()













