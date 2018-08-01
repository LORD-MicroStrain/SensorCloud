"""
Copyright 2013 LORD MicroStrain All Rights Reserved.

Distributed under the Simplified BSD License.
See file license.txt
"""

import xdrlib
import httplib

import logging
logger = logging.getLogger(__name__)

from sensorcloudrequest import SensorCloudRequests
from sensor import Sensor
from cache import Cache
from error import *

DEFAULT_AUTH_SERVER = "https://sensorcloud.microstrain.com"

class Device(object):


    def __init__(self, device_id, device_key, auth_server=DEFAULT_AUTH_SERVER, request_factory=None, cache_file=None):
        self._cache = Cache(cache_file) if cache_file else None
        self._requests = SensorCloudRequests(device_id, device_key, auth_server, requests = request_factory, cache = self._cache)
        self._sensors = {}
        if self._cache:

            self._requests._authToken = self._cache.token
            self._requests._apiServer = self._cache.server

            for sensorCache in self._cache.sensors:
                self._sensors[sensorCache.name] = Sensor(self, sensorCache.name, sensorCache)

    def __contains__(self, sensor_name):
        """
        check if a sensor exits for this device on SensorCloud
        """

        response = self.url("/sensors/%s/" % sensor_name)\
                       .param("version", "1")\
                       .accept("application/xdr").get()

        if response.status_code == httplib.OK: return True
        if response.status_code == httplib.NOT_FOUND: return False

        raise error(response, "has sensor")

    def url(self, url_path):
        return self._requests.url(url_path)

    def has_sensor(self, sensor_name):
        return self.__contains__(sensor_name)

    def __iter__(self):
        sensors = self.all_sensors()
        for sensor in sensors:
            yield sensor


    def __getitem__(self, sensor_name):
        return self.sensor(sensor_name)


    def add_sensor(self, sensor_name, sensor_type="", sensor_label="", sensor_desc=""):
        """
        Add a sensor to the device. type, label, and description are optional.
        """

        logger.debug("add_sensor(sensor_name='%s', sensor_type='%s', sensor_label='%s', sensor_desc='%s')", sensor_name, sensor_type, sensor_label, sensor_desc)

        #addSensor allows you to set the sensor type label and description.  All fileds are strings.
        #we need to pack these strings into an xdr structure
        packer = xdrlib.Packer()
        packer.pack_int(1)  #version 1
        packer.pack_string(sensor_type)
        packer.pack_string(sensor_label)
        packer.pack_string(sensor_desc)
        data = packer.get_buffer()

        response = self.url("/sensors/%s/"%sensor_name)\
                       .param("version", "1")\
                       .data(data)\
                       .content_type("application/xdr").put()

        #if response is 201 created then we know the sensor was added
        if response.status_code != httplib.CREATED:
            raise error(response, "add sensor")

        return self.sensor(sensor_name)

    def sensor(self, sensor_name):

        sensor = self._sensors.get(sensor_name)
        if not sensor:
            cache = None
            if self._cache:
                cache = self._cache.sensor(sensor_name)
            sensor = Sensor(self, sensor_name, cache)
            self._sensors[sensor_name] = sensor

        return sensor

    def save_cache(self):
        self._cache.save()

    def all_sensors(self):
        pass

