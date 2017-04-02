import os, sys
import pika
import json
import time
import traceback

from peewee import *
from playhouse.postgres_ext import *

# DEBUG = int(os.environ.get('DEBUG'))
MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')

DB_HOST = os.environ.get('DB_HOST')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')

psql_db = PostgresqlExtDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)

class BaseModel(Model):
    class Meta:
        database = psql_db

class FacebookContact(BaseModel):
    facebook_resource_locator = TextField(primary_key=True)
    org_name = CharField(null = True)
    description = TextField(null = True)
    address = TextField(null = True)
    country = CharField(null = True)
    state = CharField(null = True)
    postal_code = CharField(null = True)
    contact_no = CharField(null = True)
    industry = CharField(null = True)
    fan_count = IntegerField(null = True)
    hours = TextField(null = True)
    link = TextField(null = True)
    longitude = TextField(null = True)
    latitude = TextField(null = True)
    intl_number_with_plus = TextField(null = True)
    search_content = TSVectorField(null = True)

class LinkedInContact(BaseModel):
    linkedin_resource_locator = TextField(primary_key = True)
    org_name = CharField(null = True)
    org_type = CharField(null = True)
    description = TextField(null = True)
    address = TextField(null = True)
    city = CharField(null = True)
    state = CharField(null = True)
    postal_code = IntegerField(null = True)
    website = TextField(null = True)
    industry = CharField(null = True)
    specialities = TextField(null = True)
    follower_count = IntegerField(null = True)
    year_founded = TextField(null = True)
    size = TextField(null = True)
    search_content = TSVectorField(null = True)

class FourSquareContact(BaseModel):
    foursquare_resource_locator = TextField(primary_key=True)
    org_name = CharField(null = True)
    description = TextField(null = True)
    address = TextField(null = True)
    country = CharField(null = True)
    #state = CharField(null = True)
    postal_code = CharField(null = True)
    contact_no = CharField(null = True)
    #industry = CharField(null = True)
    fan_count = IntegerField(null = True)
    hours = TextField(null = True)
    link = TextField(null = True)
    longitude = TextField(null = True)
    latitude = TextField(null = True)  
    search_content = TSVectorField(null = True)

class GoogleContact(BaseModel):
    google_resource_locator = TextField(primary_key=True)
    org_name = CharField(null = True)
    address = TextField(null = True)
    country = CharField(null = True)
    postal_code = CharField(null = True)
    contact_no = CharField(null = True)
    industry = CharField(null = True)
    rating = FloatField(null = True)
    link = TextField(null = True)
    longitude = TextField(null = True)
    latitude = TextField(null = True)
    intl_number_with_plus = TextField(null = True)
    search_content = TSVectorField(null = True)

"""

class FTSFacebookContact(FTSBaseModel):
    org_name = CharField()
    description = TextField()
    address = TextField()
    country = CharField()
    postal_code = CharField()

class FTSLinkedInContact(FTSBaseModel):
    org_name = CharField()
    description = TextField()
    address = TextField()
    city = CharField()
    postal_code = CharField()

class FTSFourSquareContact(FTSBaseModel):
    org_name = CharField()
    description = TextField()
    address = TextField()
    country = CharField()
    postal_code = CharField()

class FTSGoogleContact(FTSBaseModel):
    org_name = CharField()
    address = TextField()
    country = CharField()
    postal_code = CharField()

"""

from peewee import Expression

def _Match(field, query, language=None):
    params = (language, query) if language is not None else (query,)
    return Expression(
        field,
        OP.TS_MATCH,
        fn.to_tsquery(*params))

import unicodedata

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


"""
Updating function

- Currently it just overwrites, also makes multiple requests per update, not cool
- follower count is different for different sites
"""

def updateFacebookContact(data):
    """
    Data declarations for FTS Search
    """

    contact_attributes = ["org_name", "description", "address", "country", "state", "postal_code", "contact_no", "industry", "fan_count", "hours", "link", "longitude", "latitude", "intl_number_with_plus"]

    if data.has_key("org_name") and data["org_name"] != None:
        FacebookContact.update(org_name = data["org_name"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
        org_name = data["org_name"]
    if data.has_key("description") and data["description"] != None:
        FacebookContact.update(description = data["description"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
        description = data["description"]
    if data.has_key("address") and data["address"] != None:
        FacebookContact.update(address = data["address"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
        address = data["address"]
    if data.has_key("country") and data["country"] != None:
        FacebookContact.update(country = data["country"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
        country = data["country"]
    if data.has_key("state") and data["state"] != None:
        FacebookContact.update(state = data["state"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("postal_code") and data["postal_code"] != None:
        FacebookContact.update(postal_code = data["postal_code"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
        postal_code = data["postal_code"]
    if data.has_key("contact_no") and data["contact_no"] != None:
        FacebookContact.update(contact_no = data["contact_no"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("industry") and data["industry"] != None:
        FacebookContact.update(industry = data["industry"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("fan_count") and isinstance(data["fan_count"], int) and data["fan_count"] != None:
        FacebookContact.update(fan_count = data["fan_count"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("hours") and data["hours"] != None:
        FacebookContact.update(hours = data["hours"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("link") and data["link"] != None:
        FacebookContact.update(link = data["link"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("longitude") and data["longitude"] != None:
        FacebookContact.update(longitude = data["longitude"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("latitude") and data["latitude"] != None:
        FacebookContact.update(latitude = data["latitude"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    if data.has_key("intl_number_with_plus") and data["intl_number_with_plus"] != None:
        FacebookContact.update(intl_number_with_plus = data["intl_number_with_plus"]).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    """
    full_contact = FacebookContact.get(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"])
    ftsContact = FTSFacebookContact.select().where(FTSFacebookContact.docid == data["facebook_resource_locator"])
    if ftsContact.exists():
        ftsContact = ftsContact.get()
    else:
        ftsContact = FTSFacebookContact(facebook_resource_locator=data["facebook_resource_locator"])
    """
    search_attributes = ["org_name", "address", "state", "country", "postal_code"]
    search_attributes_filtered = filter(lambda key: data.has_key(key) and data[key] != None, search_attributes)
    data_to_add = " ".join(map(lambda key: data[key], search_attributes_filtered))
    FacebookContact.update(search_content = fn.to_tsvector(remove_accents(data_to_add))).where(FacebookContact.facebook_resource_locator == data["facebook_resource_locator"]).execute()
    return

def updateLinkedInContact(data):
    if data.has_key("org_name") and data["org_name"] != None:
        LinkedInContact.update(org_name = data["org_name"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("org_type") and data["org_type"] != None:
        LinkedInContact.update(org_type = data["org_type"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("description") and data["description"] != None:
        LinkedInContact.update(description = data["description"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("address") and data["address"] != None:
        LinkedInContact.update(address = data["address"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("city") and data["city"] != None:
        LinkedInContact.update(city = data["city"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("state") and data["state"] != None:
        LinkedInContact.update(state = data["state"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("postal_code") and isinstance(data["postal_code"], int) and data["postal_code"] != None:
        LinkedInContact.update(postal_code = data["postal_code"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("website") and data["website"] != None:
        LinkedInContact.update(website = data["website"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("industry") and data["industry"] != None:
        LinkedInContact.update(industry = data["industry"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("specialities") and data["specialities"] != None:
        LinkedInContact.update(specialities = data["specialities"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("follower_count") and isinstance(data["follower_count"], int) and data["follower_count"] != None:
        LinkedInContact.update(follower_count = data["follower_count"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("year_founded") and data["year_founded"] != None:
        LinkedInContact.update(year_founded = data["year_founded"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    if data.has_key("size") and data["size"] != None:
        LinkedInContact.update(size = data["size"]).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    search_attributes = ["org_name", "address", "city", "state", "postal_code"]
    search_attributes_filtered = filter(lambda key: data.has_key(key) and data[key] != None, search_attributes)
    data_to_add = " ".join(map(lambda key: data[key], search_attributes_filtered))
    LinkedInContact.update(search_content = fn.to_tsvector(remove_accents(data_to_add))).where(LinkedInContact.linkedin_resource_locator == data["linkedin_resource_locator"]).execute()
    return

def updateFourSquareContact(data):
    if data.has_key("org_name") and data["org_name"] != None:
        FourSquareContact.update(org_name = data["org_name"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("description") and data["description"] != None:
        FourSquareContact.update(description = data["description"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("address") and data["address"] != None:
        FourSquareContact.update(address = data["address"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("country") and data["country"] != None:
        FourSquareContact.update(country = data["country"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    # if data.has_key("state") and data["state"] != None:
    #     FourSquareContact.update(state = data["state"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("postal_code") and data["postal_code"] != None:
        FourSquareContact.update(postal_code = data["postal_code"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("contact_no") and data["contact_no"] != None:
        FourSquareContact.update(contact_no = data["contact_no"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    # if data.has_key("industry") and data["industry"] != None:
    #     FourSquareContact.update(industry = data["industry"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("fan_count") and isinstance(data["fan_count"], int) and data["fan_count"] != None:
        FourSquareContact.update(fan_count = data["fan_count"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("hours") and data["hours"] != None:
        FourSquareContact.update(hours = data["hours"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("link") and data["link"] != None:
        FourSquareContact.update(link = data["link"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("longitude") and data["longitude"] != None:
        FourSquareContact.update(longitude = data["longitude"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    if data.has_key("latitude") and data["latitude"] != None:
        FourSquareContact.update(latitude = data["latitude"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    # if data.has_key("intl_number_with_plus") and data["intl_number_with_plus"] != None:
    #     FourSquareContact.update(intl_number_with_plus = data["intl_number_with_plus"]).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    search_attributes = ["org_name", "address", "country", "postal_code"]
    search_attributes_filtered = filter(lambda key: data.has_key(key) and data[key] != None, search_attributes)
    data_to_add = " ".join(map(lambda key: data[key], search_attributes_filtered))
    FourSquareContact.update(search_content = fn.to_tsvector(remove_accents(data_to_add))).where(FourSquareContact.foursquare_resource_locator == data["foursquare_resource_locator"]).execute()
    return


def updateGoogleContact(data):
    if data.has_key("org_name") and data["org_name"] != None:
        GoogleContact.update(org_name = data["org_name"]).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    if data.has_key("address") and data["address"] != None:
        GoogleContact.update(address = data["address"]).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    if data.has_key("country") and data["country"] != None:
        GoogleContact.update(country = data["country"]).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    if data.has_key("postal_code") and data["postal_code"] != None:
        GoogleContact.update(postal_code = data["postal_code"]).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    if data.has_key("contact_no") and data["contact_no"] != None:
        GoogleContact.update(contact_no = data["contact_no"]).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    if data.has_key("industry") and data["industry"] != None:
        GoogleContact.update(industry = data["industry"]).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    if data.has_key("rating") and isinstance(data["rating"], float) and data["rating"] != None:
        GoogleContact.update(rating = data["rating"]).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    if data.has_key("link") and data["link"] != None:
        GoogleContact.update(link = data["link"]).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    if data.has_key("longitude") and data["longitude"] != None:
        GoogleContact.update(longitude = data["longitude"]).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    if data.has_key("latitude") and data["latitude"] != None:
        GoogleContact.update(latitude = data["latitude"]).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    if data.has_key("intl_number_with_plus") and data["intl_number_with_plus"] != None:
        GoogleContact.update(intl_number_with_plus = data["intl_number_with_plus"]).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    search_attributes = ["org_name", "address", "country", "postal_code"]
    search_attributes_filtered = filter(lambda key: data.has_key(key) and data[key] != None, search_attributes)
    data_to_add = " ".join(map(lambda key: data[key], search_attributes_filtered))
    GoogleContact.update(search_content = fn.to_tsvector(remove_accents(data_to_add))).where(GoogleContact.google_resource_locator == data["google_resource_locator"]).execute()
    return    
