import os, sys
import pika
import json
import time
import traceback

from peewee import *

# DEBUG = int(os.environ.get('DEBUG'))
MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD')

DB_HOST = os.environ.get('DB_HOST')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')

from peewee import *

psql_db = PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)

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

class GoogleContact(BaseModel):
    google_resource_locator = TextField(primary_key=True)
    org_name = CharField(null = True)
    address = CharField(null = True)
    country = CharField(null = True)
    postal_code = CharField(null = True)
    contact_no = CharField(null = True)
    industry = CharField(null = True)
    rating = FloatField(null = True)
    link = TextField(null = True)
    longitude = TextField(null = True)
    latitude = TextField(null = True)
    intl_number_with_plus = TextField(null = True)
