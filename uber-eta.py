#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 16:25:38 2017

@author: aguinaldo
"""
import os
import json
import numpy as np
import pandas as pd
import datetime as dt
import geohash
import time


from uber_rides.session import Session
from uber_rides.client import UberRidesClient

product = '65cb1829-9761-40f8-acc6-92d700fe2924'

all_points_df = pd.read_csv('selected_points1.csv')
all_points = all_points_df.values.tolist()

session = Session(server_token=UBER_API_KEY)
client = UberRidesClient(session)

uber_eta_df = pd.DataFrame(columns = ['datetime', 'log', 'lat', 'neigh', 'point_hash', 'eta'])


content_min_length = 50
max_rereq = 3
counter = 0
for i,value in enumerate(all_points):
        log, lat, name = value
        
        try:
            wait_time = client.get_pickup_time_estimates(lat,log,product)
            cont_len = wait_time.headers.get('Content-Length')
        except Exception as e:
             print e.__doc__
             print e.message
             cont_len = 0
	     continue
	#print(wait_time.status_code)
	#print(wait_time.json)
	print(cont_len)
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
          
        
uber_eta_df.to_csv('uber-eta.csv', mode='a', header=True, index=False)

