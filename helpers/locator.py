from geopy.geocoders import Nominatim
import json
import os

def fill_location_item(location_item, location, add_hk=True):
    # 
    # Gathering geocodes from the location.json
    # 
    location = location.lower()
    file = open("location.json", "r")   #file location at jobs directory
    x = file.read()
    x = json.loads(x)
    lat = x[location]["latitude"]
    lon = x[location]["longitude"]
    file.close()

    location_item.add_value("raw_location", location)
    location_item.add_value("latitude", lat)
    location_item.add_value("longitude", lon)

    return location_item.load_item()

def loadJson(path):
    """Load a JSON file an return a dict object.

    :param path: relative path relative to the scrapy project root
    :returns: ajson
    :rtype: dict
    """
    ajson = {}
    with open(path, mode="r", encoding="utf8") as f:
        atext = f.read()
        try:
            ajson = json.loads(atext)
        except Exception as e:
            print(f"Error in loading JSON.", e)
    return ajson