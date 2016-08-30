#!/usr/bin/python
'''
This module does prepare and upload the ALL_WSPR.TXT-format to the influxdb-server

Author : PA7T Clemens Heese
         DK5HH Michael Hartje DK5HH at darc.de

Installation: 
Prepare the python installation depending on what python version you are 
using (2/3)
we need to add the modules in addition to a standeard python installation
influxdb
pyhamtools
geohash
You can install these modules with for pythoon 2 with
pip2 install modulename
or for python 3 with
pip3 install modulename

check the installtion in python console
import modulename
(no answer is good news.)

'''

import re
from time import gmtime, strftime, strptime
from influxdb import InfluxDBClient
import datetime
from pyhamtools.locator import locator_to_latlong, calculate_distance, calculate_heading
import geohash


client = InfluxDBClient('thehost.home.net', 8087, 'user_name', 'secret_password', 'wspr')

wspr_reporter = 'mycall'
wspr_loc_reporter = 'maidenhead_locater_6_letter'

with open('wspr_spots.txt') as f:
	for in_str in f:
		try:
			wspr_date = in_str[0:6].strip()
			wspr_time = in_str[7:11].strip()
			wspr_other = in_str[12:15].strip()
			wspr_snr = in_str[16:19].strip()
			wspr_a = in_str[20:24].strip()
			wspr_freq = in_str[24:35].strip()
			wspr_msg = in_str[37:60]
			wspr_drift = in_str[60:62]
			wspr_rest = in_str[61:-1]
		
			wspr_msg_split = re.split('[ ]',wspr_msg,maxsplit=3)
			wspr_call = re.sub('[<>]','',wspr_msg_split[0])
			wspr_loc = wspr_msg_split[1]
			wspr_pwr = wspr_msg_split[2]
			if (len(wspr_msg_split) != 4):
				print 'No correct wspr message.'

			band_vec = ('LF', 'MW', '160m', '80m', '60m', '40m', '30m', '20m', '17m', '15m', '12m', '10m')
			freq_vec = (0.1, 0.4, 1.8, 3.5, 5.2, 7.0, 10.1, 14.0, 18.1, 21.0, 24.9, 28.1)
			wspr_band = band_vec[freq_vec.index(round(float(wspr_freq) - 0.05, 1))]

			wspr_dist = str(int(calculate_distance(wspr_loc_reporter, wspr_loc)))
			wspr_az = str(int(calculate_heading(wspr_loc_reporter, wspr_loc)))
			
			latitude, longitude = locator_to_latlong(wspr_loc)
			wspr_loc_geohash = geohash.encode(latitude, longitude, precision=5)
			
			print wspr_date + '' + wspr_time
			wspr_tuple_time = strptime(wspr_date+wspr_time, "%y%m%d%H%M")
			wspr_time = strftime("%Y-%m-%dT%H:%M:%SZ", wspr_tuple_time)
			print wspr_time

			json_body = [
			{
				"measurement": "wspr_redpitaya_test",
				"tags": {
					"band": wspr_band,
					"reporter": wspr_reporter,
					"loc_reporter": wspr_loc_reporter,
					"geohash": wspr_loc_geohash,
					"call": wspr_call
				},
				"time": wspr_time,
				"fields": {
					"call": wspr_call,
					"freq": float(wspr_freq),
					"loc": wspr_loc,
					"snr": int(float(wspr_snr)),
					"pwr": int(float(wspr_pwr)),
					"drift": int(float(wspr_drift)),
					"az": wspr_az,
					"dist": wspr_dist
				}
			}
			]
			print json_body
			ret = client.write_points(json_body)
			print ret
		except Exception,e:
			print '<<< could not parse spot >>>'
			print str(e)
			pass
