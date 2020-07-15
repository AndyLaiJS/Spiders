from geopy.geocoders import Nominatim
import json
import os

def create_location(location):
    geolocator = Nominatim(user_agent="Spider Jobs")
    hk_location = geolocator.geocode(location)
    lat = hk_location.latitude
    lon = hk_location.longitude

    # Open json file
    file = open("location.json", "r")   #file location at jobs directory
    x = file.read()
    x = json.loads(x)
    file.close()

    # Update the json file with data
    file = open("location.json", "w")
    data = {
        location.lower(): {
            "latitude": lat,
            "longitude": lon
        }
    }
    # Update it to the read json file in x
    x.update(data)
    file.write(json.dumps(x, indent=4))
    file.close()