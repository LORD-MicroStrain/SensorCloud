"""
Copyright 2013 LORD MicroStrain All Rights Reserved.

Distributed under the Simplified BSD License.
See file license.txt
"""

import logging
logger = logging.getLogger(__name__)

import xdrlib
import httplib
import json

from channel import Channel
from error import *


class DoRequest_createSensor:
    """
    Wrapper around a doRequest to catch a 404 Sensor Not found error.  If the Senosr Doesn't exist, it will be created and then the original request will be
    resubmited.
    """

    def __init__(self, sensor):
        self._sensor = sensor

    def  __call__(self, response, handler):
        """
        called for a request to doRequest
        """
        if response.status_code == httplib.NOT_FOUND:

            if response.scerror and response.scerror.code == "404-001": #Sensor not found
                logger.info("intercepted '404-001 Sensor Not Found' error and adding the sensor %s", self._sensor.name)
                self._sensor.device.add_sensor(self._sensor.name)

                #sensor has now been created, resend the original request
                return True

        return handler()

class Sensor(object):

    def __init__(self, device, sensor_id, cache=None):
        self._device = device
        self._sensor_id = sensor_id
        self._channels = {}
        self._cache = cache

        if cache:
            for channelCache in cache.channels:
                self._channels[channelCache.name] = Channel(self, channelCache.name, channelCache)

    def url(self, url_path):
        """
        make a request from the sensor root
        """

        request_builder = self.url_without_create(url_path)

        # Add a processor so we can create a sensor if it doesn't exist
        request_builder.add_processor(DoRequest_createSensor(self))

        return request_builder

    def url_without_create(self, url_path):
        """
        create a request from the sensor without the create sensor processor
        """
        assert url_path.startswith("/"), "url_path is a subresource for a sensor and should start with a slash"

        return self._device.url("/sensors/%s%s"%(self._sensor_id, url_path))

    @property
    def device(self):
        return self._device

    @property
    def name(self):
        return self._sensor_id


    def channels(self):
        """
        return all channels
        """
        pass

    def __contains__(self, channel_name):
        """
        check if a channel exits for this device on SensorCloud
        """

        response = self.url("/channels/%s/attributes/"%channel_name)\
                                .param("version", "1")\
                                .accept("application/xdr").get()

        if response.status_code == httplib.OK: return True
        if response.status_code == httplib.NOT_FOUND: return False

        raise error(response, "channel contains")


    def channel(self, channel_name):
        cache = None
        if self._cache:
            cache = self._cache.channel(channel_name)
        return Channel(self, channel_name, cache)

    def __getitem__(self, channel_name):
        return self.channel(channel_name)

    def add_channel(self, channel_name, channel_label="", channel_desc=""):
        """
        Add a channel to the sensor.  label and description are optional.
        """

        packer = xdrlib.Packer()
        VERSION = 1
        packer.pack_int(VERSION)  #version 1
        packer.pack_string(channel_label)
        packer.pack_string(channel_desc)

        response = self.url("/channels/%s/"%channel_name)\
                       .param("version", "1")\
                       .data(packer.get_buffer())\
                       .content_type("application/xdr").put()

        #if response is 201 created then we know the sensor was added
        if response.status_code != httplib.CREATED:
            raise error(response, "add channel")

        return self.channel(channel_name)

    def delete(self):
        raise NotImplemented()

