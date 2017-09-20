from datetime import datetime

import sensorcloud
from sensorcloud import SampleRate, Device, Point

print SampleRate.hertz(10)


device_id = "OAPI00DZ0BQ3X1BR"
key = "6b6a281effc9c5ab7753ec7ade215221794391d63cf533a37e59a180e2c4bb15"

d = Device(device_id, key)

print "test" in d

print d.has_sensor("test")

import logging
logging.basicConfig(level=logging.DEBUG)


Device_ID = "OAPI0079MY1R194D"
DEVICE_KEY = "5c2a834e6b276b7e9cdd0fabd07463197b0147d2146e2ea85aee9acc96a9434c"
AUTH_SERVER = "https://test.sensorcloud.microstrain.com"

device = sensorcloud.Device(device_id=Device_ID, device_key=DEVICE_KEY, auth_server=AUTH_SERVER)

s = device.sensor("test")

c = s["ch1"]
print c.name



#c.timeseries_append(SampleRate.hertz(1), [Point(datetime.now(),99)])

for p in c.timeseries_data():
	print p

print c.last_timestamp
print c.last_point
