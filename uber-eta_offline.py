#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 22:27:24 2017

@author: aguinaldo
"""



import os
import json
import numpy as np
import pandas as pd
import datetime as dt
import geohash
import time
from keys import UBER_API_KEY

from uber_rides.session import Session
from uber_rides.client import UberRidesClient

product = '65cb1829-9761-40f8-acc6-92d700fe2924'

#all_points_df = pd.read_csv('selected_points1.csv')
#all_points = all_points_df.values.tolist()

session = Session(server_token=UBER_API_KEY)
client = UberRidesClient(session)



# import geojson file about natal neighborhood
natal_neigh = os.path.join('geojson', 'natal.geojson')

# load the data and use 'UTF-8'encoding
geo_json_natal = json.load(open(natal_neigh,encoding='UTF-8'))


neighborhood = []
# list all neighborhoods
for neigh in geo_json_natal['features']:
        neighborhood.append(neigh['properties']['name'])


# import geojson file about potengi river bounds
potengi = os.path.join('geojson', 'potengi.geojson')

# load the data and use 'UTF-8'encoding
potengi_geojson = json.load(open(potengi,encoding='UTF-8'))

from shapely.geometry import shape, mapping

pontengi_multipoly = shape(potengi_geojson['features'][0]['geometry'])

def potengi(point):

    for poly in pontengi_multipoly:
        polygon = Polygon(poly)
        if polygon.contains(point):
            return True
        else:
            return False
     
        
def generate_random(number, polygon, neighborhood):
    list_of_points = []
    minx, miny, maxx, maxy = polygon.bounds
    counter = 0
    while counter < number:
        x = random.uniform(minx, maxx)
        y = random.uniform(miny, maxy)
        pnt = Point(x, y)
        if polygon.contains(pnt):
            if bm.is_land(x,y):
                if not potengi(pnt):
                #if not on_water(y,x):
                    #if uber_available(y,x):
                        list_of_points.append([x,y,neighborhood])
                        counter += 1
    return list_of_points


# Point generation
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
    #all_points.extend(points)

#all_points_df = pd.DataFrame(all_points)



uber_eta_df = pd.DataFrame(columns = ['datetime', 'log', 'lat', 'neigh', 'point_hash', 'eta'])

content_min_length = 50
max_rereq = 3
counter = 0
for i,value in enumerate(points):
    log, lat, name = value
        
    try:
        wait_time = client.get_pickup_time_estimates(lat,log,product)
        cont_len = wait_time.headers.get('Content-Length')
    except Exception as e:
         #print e.__doc__
         #print e.message
         cont_len = 0
    continue
    #print(wait_time.status_code)
    #print(wait_time.json)
    #print(cont_len)
    while int(cont_len) < content_min_length:
        time.sleep(5)
        print("Re-requesting...")
        wait_time = client.get_pickup_time_estimates(lat,log,product)
        print(wait_time.headers.get('Content-Length'))
        counter += 1
        if counter >= 3:
                    break
                    print("Giving up after 3 attempts...")

    eta = wait_time.json.get('times')[0]['estimate']
 
    uber_eta_df =  uber_eta_df.append({
                 "datetime": dt.datetime.now(),
                 "log": log,
                 "lat": lat,
                 "neigh": name,
                 "point_hash": geohash.encode(lat,log),
                #"eta": 0
                 "eta": wait_time.json.get('times')[0]['estimate']
                  }, ignore_index=True)
          
        
uber_eta_df.to_csv('uber-eta_offline.csv', mode='a', header=True, index=False)
