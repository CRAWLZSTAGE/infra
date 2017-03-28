import os, sys
import pika
import json
import time
import traceback
from bs4 import BeautifulSoup

"""
parser specific dependencies
"""

MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')
MAX_DEPTH = int(os.environ.get('MAX_DEPTH'))

while True:
    try:
        _credentials = pika.PlainCredentials(MQTT_USER, MQTT_PASSWORD)
        mqtt_connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQTT_HOST, credentials=_credentials))
        break
    except Exception:
        time.sleep(5)

pqdata = dict()
pqdata['x-max-priority'] = 5


ingress_channel_parse = mqtt_connection.channel()
ingress_channel_parse.queue_declare(queue='parse', durable=True, arguments=pqdata)
store_egress_channel = mqtt_connection.channel()
store_egress_channel.queue_declare(queue='store', durable=True, arguments=pqdata)
filter_egress_channel = mqtt_connection.channel()
filter_egress_channel.queue_declare(queue='filter', durable=True, arguments=pqdata)

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
            'linkedin_resource_locator': url,
            'year_founded': year_founded,
            'size': size
        }

        for coy in alsoViewed:
            list_of_companies.append(coy["homeUrl"])
        return [ contact, list_of_companies ]
    except:
        raise Exception("Unable to parse linkedIn body" + datafrom_xpath)

def facebook_parse(fb_id, facebook_company_info):
    """
    Parameters:
    facebook_company_info: dict, from fetcher, using get_object function

    Outputs:
    company_info: dict , information of the company
    other_companies_pages: array, each element containing an id and name
    , description, fan_count, hours, link

    TO-DO:
    company_postal and company_street should not both be under address
    """

    if facebook_company_info:
        company_name = facebook_company_info['name'] if ('name' in facebook_company_info) else None
        company_about = facebook_company_info['about'] if ('about' in facebook_company_info) else None
        company_phone = facebook_company_info['phone'] if ('phone' in facebook_company_info) else None
        company_category = facebook_company_info['category'] if ('category' in facebook_company_info) else None
        company_street = facebook_company_info["location"]['street'] if (facebook_company_info.has_key("location") and facebook_company_info["location"].has_key("street")) else None
        company_longitude = facebook_company_info["location"]['longitude'] if (facebook_company_info.has_key("location") and facebook_company_info["location"].has_key("longitude")) else None
        company_latitude = facebook_company_info["location"]['latitude'] if (facebook_company_info.has_key("location") and facebook_company_info["location"].has_key("latitude")) else None
        company_country = facebook_company_info["location"]['country'] if (facebook_company_info.has_key("location") and facebook_company_info["location"].has_key("country")) else None
        company_postal = facebook_company_info["location"]['zip'] if (facebook_company_info.has_key("location") and facebook_company_info["location"].has_key("zip")) else None
        company_fan_count = facebook_company_info['fan_count'] if ('fan_count' in facebook_company_info) else None
        company_hours = facebook_company_info['hours'] if ('hours' in facebook_company_info) else None
        company_link = facebook_company_info['link'] if ('link' in facebook_company_info) else None
        company_intl_number_with_plus = facebook_company_info['intl_number_with_plus'] if ('intl_number_with_plus' in facebook_company_info) else None

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
        'postal_code': company_postal,
        'contact_no': company_phone,
        'industry': company_category,
        'facebook_resource_locator': fb_id,
        'longitude': company_longitude,
        'latitude': company_latitude,
        'fan_count': company_fan_count,
        'hours': company_hours,
        'link': company_link,
        'intl_number_with_plus': company_intl_number_with_plus
    }

    return company_info, potential_leads


def foursquare_parse(foursquare_venue_info):
    """
    Parameters:
    foursquare_venue_info: dict, from fetcher, using requests.get function

    Outputs:
    company_info: dict , information of the company
    other_companies_pages: array, each element containing an id and name

    TO-DO:
    company_street and company_postal should not both be under address
    """

    if foursquare_venue_info:
        fsquare_id = foursquare_venue_info['id'] if ('id' in foursquare_venue_info) else None
        company_name = foursquare_venue_info['name'] if ('name' in foursquare_venue_info) else None
        company_about = foursquare_get_categories(foursquare_venue_info["categories"]) if (foursquare_venue_info.has_key("categories")) else None
        company_phone = foursquare_venue_info['contact']['phone'] if (foursquare_venue_info.has_key("contact") and foursquare_venue_info["contact"].has_key("phone")) else None
        company_street = foursquare_venue_info["location"]['address'] if (foursquare_venue_info.has_key("location") and foursquare_venue_info["location"].has_key("address")) else None
        company_country = foursquare_venue_info["location"]['country'] if (foursquare_venue_info.has_key("location") and foursquare_venue_info["location"].has_key("country")) else None
        company_postal = foursquare_venue_info["location"]['postalCode'] if (foursquare_venue_info.has_key("location") and foursquare_venue_info["location"].has_key("postalCode")) else None
        company_longitude = foursquare_venue_info["location"]["lng"] if (foursquare_venue_info.has_key("location") and foursquare_venue_info["location"].has_key("lng")) else None
        company_latitude = foursquare_venue_info["location"]["lat"] if (foursquare_venue_info.has_key("location") and foursquare_venue_info["location"].has_key("lat")) else None
        company_fan_count = foursquare_venue_info["likes"]["count"] if (foursquare_venue_info.has_key("likes") and foursquare_venue_info["likes"].has_key("count")) else None
        company_hours = foursquare_venue_info["hours"]["status"] if (foursquare_venue_info.has_key("hours") and foursquare_venue_info["hours"].has_key("status")) else None
        company_link = foursquare_venue_info["url"] if (foursquare_venue_info.has_key("url")) else None
    """
    TODO
    this section
    """

    company_info = {
        'foursquare_resource_locator': fsquare_id,
        'description': company_about,
        'org_name': company_name,
        'address': company_street,
        'country': company_country,
        'postal_code': int(company_postal),
        'contact_no': company_phone,
        'longitude': company_longitude,
        'latitude': company_latitude,
        'fan_count': company_fan_count,
        'hours': company_hours,
        'link': company_link
    }

    return company_info   


def foursquare_get_categories(categories_array):
    categories_string = None
    if categories_array:
        categories_string = ", ".join([category["name"] for category in categories_array])
    return categories_string 

def google_parse(google_venue_info):
    
    if google_venue_info:
        google_id = google_venue_info['place_id'] if ('place_id' in google_venue_info) else None
        company_name = google_venue_info['name'] if ('name' in google_venue_info) else None
        #company_about = foursquare_get_categories(foursquare_venue_info["categories"]) if (foursquare_venue_info.has_key("categories")) else None
        company_phone = google_venue_info['formatted_phone_number'] if ('formatted_phone_number' in google_venue_info) else None
        company_street, company_country, company_postal = google_get_address(google_venue_info['adr_address'])
        company_longitude = google_venue_info['geometry']['location']['lng'] if (google_venue_info.has_key("geometry") and google_venue_info["geometry"].has_key("location") and google_venue_info["geometry"]["location"].has_key("lng")) else None
        company_latitude = google_venue_info['geometry']['location']['lat'] if (google_venue_info.has_key("geometry") and google_venue_info["geometry"].has_key("location") and google_venue_info["geometry"]["location"].has_key("lat")) else None
        company_rating = google_venue_info['rating'] if ('rating' in google_venue_info) else None
        company_category = google_get_category(google_venue_info['types']) if ('types' in google_venue_info) else None
        company_link = google_venue_info['website'] if ('website' in google_venue_info) else None 
        company_intl_number_with_plus = google_venue_info['international_phone_number'] if ('international_phone_number' in google_venue_info) else None

    company_info = {
        'org_name': company_name,
        'address': company_street,
        'country': company_country,
        'postal_code': company_postal,
        'contact_no': company_phone,
        'industry': company_category,
        'google_resource_locator': google_id,
        'longitude': company_longitude,
        'latitude': company_latitude,
        'rating': company_rating,
        'link': company_link,
        'intl_number_with_plus': company_intl_number_with_plus
    }

    return company_info    
      

def google_get_address(google_address_info):
    company_street = company_country = company_postal = None

    if google_address_info:
        address_soup = BeautifulSoup(google_address_info, 'html.parser')
        street_array = address_soup.find_all('span', class_=lambda x: (x != 'country-name') and (x != 'postal_code'))
        country_array = address_soup.find_all('span', class_="country-name")
        postal_code_array = address_soup.find_all('span', class_="postal-code")

        company_street = ', '.join([tag.get_text() for tag in street_array]) if street_array else None
        company_country = country_array[0].get_text() if country_array else None
        company_postal = postal_code_array[0].get_text() if postal_code_array else None

    return company_street, company_country, company_postal    


def google_get_category(types_array):
    categories_string = None
    if types_array:
        categories_string = ', '.join(types_array)
    return categories_string    


def parseCallback(ch, method, properties, body):
    try:
        global MAX_DEPTH
        
        data = json.loads(body)
        if data.has_key("maxDepth") and isinstance(data["maxDepth"], int):
            MAX_DEPTH = int(data["maxDepth"])
 
            return
        if not data.has_key("protocol") or not data.has_key("resource_locator") or not data.has_key("raw_response") or not data.has_key("depth"):
            raise Exception("Body malformed")
        if data.has_key("raw_response") == None:
            raise Exception("None Message Recieved")
        """
        TODO
        use appropriate parser according to URL
        """
        if data["protocol"] == "linkedin":
            contact, potential_leads = linkedIn_parse(data["resource_locator"], data["raw_response"])
            if contact == None:
                return

        elif data["protocol"] == "fb":
            contact, potential_leads = facebook_parse(data["resource_locator"], data["raw_response"])

        elif data["protocol"] == "fsquare":
            potential_leads = data["potential_leads"]
            contact = foursquare_parse(data["raw_response"])
            if contact == None:
                return

        elif data["protocol"] == "google":
            potential_leads = data["potential_leads"]
            contact = google_parse(data["raw_response"])
            if contact == None:
                return        

        contact["protocol"] = data["protocol"]
        store_egress_channel.basic_publish(
            exchange='',
            routing_key='store',
            body=json.dumps(contact),
            properties=pika.BasicProperties(
                delivery_mode = 1,
                priority= 0 #default priority
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
                delivery_mode = 1,
                priority = 0 # default priority
            )
        )
    except Exception as e:
        sys.stderr.write(str(e) + "Unable to parse body: \n" + body + "\n")
        traceback.print_exc()
        sys.stderr.flush()
    finally:
        ingress_channel_parse.basic_ack(delivery_tag = method.delivery_tag)    

ingress_channel_parse.basic_qos(prefetch_count=1)
ingress_channel_parse.basic_consume(parseCallback, queue='parse')
ingress_channel_parse.start_consuming()


