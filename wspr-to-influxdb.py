#!/usr/bin/python
import re
from time import gmtime, strftime, strptime
from influxdb import InfluxDBClient
import datetime
from pyhamtools.locator import locator_to_latlong, calculate_distance, calculate_heading
import geohash

import sys
import time, calendar
import subprocess
import argparse
import mlocs
import Geohash