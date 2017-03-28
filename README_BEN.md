## Retrieve Foursquare API Token

Access Tokens allow apps to make requests to Foursquare on the behalf of a user. However, for our project, we will be using Userless Access to obtain resources using Foursquare's API, as these resources do not require users to authenticate.

Since we only require Userless Access, we will need the Client ID and Client Secret to use the API. In order to obtain the Client ID and Client Secret, we will first to register as a Foursquare Developer and to also create a new app to obtain the Client ID and Client Secret, at here: 
https://developer.foursquare.com/

Here's an example of how we can use the Client ID and Client Secret to obtain:

requests.get("https://api.foursquare.com/v2/venues/foursquare_id?client_id=CLIENT_ID&client_secret=CLIENT_SECRET&v=20170101")

We use a HTTP GET method to the above URL to obtain the information about a venue


## Retrieve Google Places API key

First, you would need to register a Google account. Then navigate here:
https://developers.google.com/places/web-service/get-api-key

Click on the 'Get A Key' button and choose an existing project or create a new project.
Then it will present you a new API Key to use.

For this project, we will be using the Google Places API and we will need to use the API Key to call this service.

To do a broad search, we use 'Place Search' service. In order to do a search, we need to input location (latitude/longitude) into the URL we are calling. From here we will obtain a number of place_ids. 

Here's an example of a nearby search:
https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=latitude,longitude&radius=radius&rankby=prominence&key=GOOGLE_API_KEY

For more details, navigate here: https://developers.google.com/places/web-service/search

To get more details of a venue, we use 'Place Details' service. Using the place_ids of the various locations, we input them into the URL below and use a HTTP GET method and call the service:
https://maps.googleapis.com/maps/api/place/details/json?placeid=place_id&key=GOOGLE_API_KEY


## Things to do

Fix Google implementation
Doesn't seem to work after sending a second payload



