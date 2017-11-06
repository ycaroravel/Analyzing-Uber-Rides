# Script for interest points colect
import os
#import folium
import json
import pandas as pd
#from branca.colormap import linear
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import Point
from numpy import random
from mpl_toolkits.basemap import Basemap
bm = Basemap(resolution='c')
import requests
import time
import datetime as dt
from keys import UBER_API_KEY, ON_WATER_KEY

# import geojson file about natal neighborhood
natal_neigh = os.path.join('geojson', 'natal.geojson')

# load the data and use 'UTF-8'encoding
geo_json_natal = json.load(open(natal_neigh,encoding='UTF-8'))


neighborhood = []
# list all neighborhoods
for neigh in geo_json_natal['features']:
        neighborhood.append(neigh['properties']['name'])
#neighborhood


from uber_rides.session import Session
from uber_rides.client import UberRidesClient

session = Session(server_token=UBER_API_KEY)
uber_client = UberRidesClient(session)


def on_water(lat,log):
    lat = str(lat)
    log = str(log)
    api_url="https://api.onwater.io/api/v1/results/"+lat+","+log+"?access_token="+ON_WATER_KEY
    try:
        onwater = requests.get(api_url,timeout=10).json()  
    except requests.exceptions.HTTPError as err:
        print(err)
        return False
        continue
    print("On Water")
    print(onwater['water'])
    time.sleep(5)
    return onwater['water']


def uber_available(lat,log):
    content_min_length = 50
    product = '65cb1829-9761-40f8-acc6-92d700fe2924'
    wait_time = uber_client.get_pickup_time_estimates(lat,log,product)
    #print(wait_time.headers.get('Content-Length'))
    #print(wait_time.json.get('times')[0]['estimate'])
    if int(wait_time.headers.get('Content-Length')) < content_min_length:
        print("Empty Uber Response")
        return False
    print("Uber Available")
    return True

# return a number of points inside the polygon
# test if there's an Uber API response for them and if they are in land or water
def generate_random(number, polygon, neighborhood):
    list_of_points = []
    minx, miny, maxx, maxy = polygon.bounds
    counter = 0
    while counter < number:
        x = random.uniform(minx, maxx)
        y = random.uniform(miny, maxy)
        pnt = Point(x, y)
        if polygon.contains(pnt):
            #if bm.is_land(x,y):
                if not on_water(y,x):
                    if uber_available(y,x):
                        list_of_points.append([x,y,neighborhood])
                        counter += 1
    return list_of_points


number_of_points = 3
all_points = []
# search all features
for feature in geo_json_natal['features']:
    # get the name of neighborhood
    neighborhood = feature['properties']['name']
    # take the coordinates (lat,log) of neighborhood
    geom = feature['geometry']['coordinates']
    # create a polygon using all coordinates
    polygon = Polygon(geom[0])
    # return number_of_points by neighborhood as a list [[log,lat],....]
    points = generate_random(number_of_points,polygon, neighborhood)
    all_points.extend(points)
    # iterate over all points and print in the map


all_points_df = pd.DataFrame(all_points)


# Get the current date and time
now = dt.datetime.now()
now_str = now.strftime("%Y%m%d_%H%M")
# Write out to a file for today
filename = 'selected_points.csv.'+now_str
all_points_df.to_csv(filename, mode='w', header=True, index=False)


