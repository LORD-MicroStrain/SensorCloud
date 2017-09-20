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
from collections import namedtuple

from util import nanosecond_to_timestamp as to_ts
from timeseries import TimeSeriesStream
from point import Point
from histogram import Histogram

HistogramStreamInfo = namedtuple("HistogramStreamInfo", ["start_time", "end_time"])
TimeSeriesStreamInfo = namedtuple("TimeSeriesStreamInfo", ["start_time", "end_time", "units"])
Unit = namedtuple("Unit", ["stored_unit", "preferred_unit", "timestamp", "slope", "ofset"])



class DoRequest_createChannel:
    """
    Wrapper around a doRequest to catch a 404 Sensor Not found error.  If the Channel Doesn't exist, it will be created and then the original request will be
    resubmited.
    """

    def __init__(self, channel):
        self._channel = channel

    def  __call__(self, response, handler):
        """
        called for a request to doRequest
        """
        if response.status_code == httplib.NOT_FOUND:

            msg = {}
            try:
                msg = json.loads(response.text)
            except:
                #log the error, but if we couldn't parse the response, we will retry the original request and let it propogate through
                logger.exception("exception while trying to parse 404 response in the Channel's doRequest override")

            if msg.get("errorcode") == "404-001": #Sensor not found
                logger.info("intercepted '404-001 Sensor Not Found' error and adding the sensor %s", self._channel.sensor.name)
                self._channel.sensor.device.add_sensor(self._channel.sensor.name)
                self._channel.sensor.add_channel(self._channel.name)
                return True
            elif msg.get("errorcode") == "404-002": #Channel not found
                logger.info("intercepted '404-002 Channel Not Found' error. Creating channel:%s", self._channel.name)
                self._channel.sensor.add_channel(self._channel.name)

                # channel has now been created and we can resend the request
                return True

        return handler()

class Channel(object):

    def __init__(self, sensor, channel_name, cache=None):
        self._sensor = sensor
        self._channel_name = channel_name

        self._last_point = None
        self._last_histogram = None

        self._timeseriesInfo = None
        self._histogramInfo = None

        self._last_timestamp_nanoseconds = None
        self._last_timestamp_timeseries = None
        self._last_timestamp_histogram = None

        self._cache = cache
        if self._cache:
            self._last_timestamp_nanoseconds = self._cache.last_timestamp
            self._last_timestamp_timeseries = self._cache.last_timestamp_timeseries
            self._last_timestamp_histogram = self._cache.last_timestamp_histogram

    @property
    def sensor(self):
        return self._sensor

    @property
    def name(self):
        return self._channel_name


    @property
    def last_point(self):
        if not self._last_point:
            self._update_last_point()
        return self._last_point

    @property
    def last_histogram(self):
        if not self._last_histogram:
            self._update_last_histogram()
        return self._last_histogram

    @property
    def last_timestamp(self):
        """
        get the timestamp for the last point stored for this channel as a DateTime
        """
        if self.last_timestamp_nanoseconds is None:
            return None
        else:
            return to_ts(self.last_timestamp_nanoseconds)

    @property
    def last_timestamp_nanoseconds(self):
        """
        get the timestamp for the last point stored for this channel as the number of nanoseconds since 1970
        """
        if not self._last_timestamp_nanoseconds:
            self._update_timeseries_info()
            self._update_histogram_info()

            if self._last_timestamp_timeseries > self._last_timestamp_histogram:
                self._last_timestamp_nanoseconds = self._last_timestamp_timeseries
            else:
                self._last_timestamp_nanoseconds = self._last_timestamp_histogram

        return self._last_timestamp_nanoseconds

    def url(self, url_path):
        """
        make a request from the channel root
        """

        request_builder = self.url_without_create(url_path)

        #we need to hijack doRequest so we can create the channel if needed
        request_builder.add_processor(DoRequest_createChannel(self))

        return request_builder

    def url_without_create(self, url_path):
        """
        make a request from the channel root, but don't create the channel if it doesn't exist
        """
        assert url_path.startswith("/"), "url_path is a subresource for a channel and should start with a slash"

        return self._sensor.url_without_create("/channels/%s%s"%(self._channel_name, url_path))

    def delete(self):
        raise NotImplemented()


    def _update_last_point(self):
        """
        called internally to get an updated copy of the last datapoint from the server.
        """

        if self._last_timestamp_nanoseconds is None:
            self._last_point = None
        else:
            points = list(self.timeseries_data(start=self._last_timestamp_nanoseconds, end=self._last_timestamp_nanoseconds))
            if points:
                self._last_point = points[-1]
            else:
                self._last_point = None

    def _update_last_histogram(self):
        """
        called internally to get an updated copy of the last histogram from the server.
        """
        response = self.url("/streams/histogram/data/latest/")\
                       .param("version", "1")\
                       .accept("application/xdr")\
                       .get()

        #if the channel doesn't have histogram data then we'll get a 404-010 error
        if response.status_code == httplib.NOT_FOUND:
            error = json.loads(response.text)
            if error.get("errorcode") == "404-010":
                self._last_histogram = None
        #if we don't get a 200 ok then we had an error
        if response.status_code != httplib.OK:
            raise Exception("get histogram info failed. status: %s %s  message:%s"%(response.status_code , response.reason, response.text))

        #packer for the units xdr format
        unpacker = xdrlib.Unpacker(response.raw)

        datastructure_version = unpacker.unpack_int()
        assert datastructure_version == 1, "structure version should always be 1"

        timestamp = unpacker.unpack_uhyper()

        bin_start = unpacker.unpack_float()
        bin_size = unpacker.unpack_float()

        numBins = unpacker.unpack_uint()

        binData = []
        for i in xrange(numBins):
            binData.append(unpacker.unpack_uint())

        self._last_histogram = Histogram(timestamp, bin_start, bin_size, binData)

        #check if we need to update last histogram time
        if self._last_histogram.timestamp_nanoseconds > self._last_timestamp_histogram:
            self._last_timestamp_histogram = self._last_histogram.timestamp_nanoseconds
            if self._cache:
                self._cache.last_timestamp_histogram = self._last_histogram.timestamp_nanoseconds
        if self._last_histogram.timestamp_nanoseconds > self._last_timestamp_nanoseconds:
            self._last_timestamp_nanoseconds = self._last_histogram.timestamp_nanoseconds

    def _update_histogram_info(self):
        """
        called internally to update info about the stream from the server
        """
        self._histogramInfo = self._get_histogram_info()


        if self._histogramInfo:
            self._last_timestamp_histogram = self._histogramInfo.end_time
        else:
            self._last_timestamp_histogram = None

        if self._cache:
            if self._last_timestamp_histogram is not None:
                self._cache.last_timestamp_histogram = self._last_timestamp_histogram

        #When we update timeseries info, verify our last point cache is valid, if it's not invalidate it
        if self._last_histogram:
            if self._last_histogram.timestamp != self._last_timestamp_histogram:
                self._last_histogram = None

    def _get_histogram_info(self):
        """ get a histogram start and end from SensorCloud"""

        response = self.url("/streams/histogram/")\
                       .param("version", "1")\
                       .accept("application/xdr")\
                       .get()

        #if the channel doesn't have timeseries data then we'll get a 404-003 error
        if response.status_code == httplib.NOT_FOUND:
            error = json.loads(response.text)
            if error.get("errorcode") == "404-010":
                return None
        #if we don't get a 200 ok then we had an error
        if response.status_code != httplib.OK:
            raise Exception("get histogram info failed. status: %s %s  message:%s"%(response.status_code , response.reason, response.text))


        #packer for the units xdr format
        unpacker = xdrlib.Unpacker( response.raw)

        datastructure_version = unpacker.unpack_int()
        assert datastructure_version == 1, "structure version should always be 1"

        start_nano = unpacker.unpack_uhyper()
        end_nano = unpacker.unpack_uhyper()

        s = HistogramStreamInfo(start_time=start_nano, end_time=end_nano)
        return s

    def _update_timeseries_info(self):
        """
        called internally to update info about the stream from the server
        """
        self._timeseriesInfo = self._get_timeseries_info()


        if self._timeseriesInfo:
            self._last_timestamp_timeseries = self._timeseriesInfo.end_time
        else:
            self._last_timestamp_timeseries = None

        if self._cache:
            if self._last_timestamp_timeseries is not None:
                self._cache.last_timestamp_timeseries = self._last_timestamp_timeseries

        #When we update timeseries info, verify our last point cache is valid, if it's not invalidate it
        if self._last_point:
            if self._last_point.timestamp != self._last_timestamp_timeseries:
                self._last_point = None

    def _get_timeseries_info(self):
        """ get a timeseries start, end and unit info from SensorCloud"""

        response = self.url("/streams/timeseries/")\
                       .param("version", "1")\
                       .accept("application/xdr")\
                       .get()

        #if the channel doesn't have timeseries data then we'll get a 404-003 error
        if response.status_code == httplib.NOT_FOUND:
            error = json.loads(response.text)
            if error.get("errorcode") == "404-003":
                return None
        #if we don't get a 200 ok then we had an error
        if response.status_code != httplib.OK:
            raise Exception("get timeseries info failed. status: %s %s  message:%s"%(response.status_code , response.reason, response.text))


        #packer for the units xdr format
        unpacker = xdrlib.Unpacker( response.raw)

        datastructure_version = unpacker.unpack_int()
        assert datastructure_version == 1, "structure version should always be 1"

        start_nano = unpacker.unpack_uhyper()
        end_nano = unpacker.unpack_uhyper()

        unit_count = unpacker.unpack_uint()
        if not 0<= unit_count <= 100:
            raise Exception("Invalid timeseres stream info structure. unit count not in the range [0,100]. value:%s"%unit_count)

        units = []
        for i in range(0,unit_count):
            stored_unit = unpacker.unpack_string()
            preferred_unit = unpacker.unpack_string()
            timestamp = unpacker.unpack_uhyper()
            slope = unpacker.unpack_float()
            offset = unpacker.unpack_float()
            units.append(Unit(stored_unit, preferred_unit, timestamp, slope, offset))

        s = TimeSeriesStreamInfo(start_time=start_nano, end_time=end_nano, units=units)
        return s


    def timeseries_data(self, start=None, end=None, limit=None, samplerate=None, convertToUnits=True):
        """
        get a range of timeseries data for this channel
        """
        return TimeSeriesStream(self, start, end, samplerate, convertToUnits)

    def timeseries_append(self, samplerate, data):
        """
        append time-series data to this channel
        """

        logger.debug("calling  timeseries_append. points:%s", len(data))


        #server allows a maximum upload size of 100,000 (as of 3-12-2013) we're limitting upload size to 20,000 points
        MAX_UPLOAD_SIZE = 20000

        #split the data into MAX_UPLOAD_SIZE chunchs to upload to sensorcloud
        s = 0
        e = MAX_UPLOAD_SIZE
        while s < len(data):
            self._timeseries_append_chunk(samplerate, data[s:e])
            s = e
            e = e + MAX_UPLOAD_SIZE

    def _timeseries_append_chunk(self, samplerate, data):

        logger.debug("calling  _timeseries_append_chunk. points:%s", len(data))

        #if we get an empty container then there's nothing to do

        if len(data) == 0:
            return

        packer = xdrlib.Packer()
        for point in data:
            packer.pack_uhyper(point.timestamp_nanoseconds)
            packer.pack_float(point.value)

        #we are about to update the timeseries stream, if the request fails, we won't    so we don't know if it is going to be updated
        self._last_point = None
        self._last_timestamp_nanoseconds = None

        self._timeseries_submit_blob(samplerate, packer.get_buffer())

        #at this point we know that the upload was successful so we can update the last point
        self._last_point = data[-1]
        self._last_timestamp_nanoseconds = self._last_point.timestamp_nanoseconds
        if self._cache:
            self._cache.last_timestamp_timeseries = self._last_timestamp_nanoseconds

    def timeseries_append_blob(self, sampleRate, blob):
        assert(len(blob) % 12 == 0)

        if len(blob) == 0:
            return

        self._last_point = None
        self._last_timestamp_nanoseconds = None

        self._timeseries_submit_blob(sampleRate, blob)

        unpacker = xdrlib.Unpacker(blob[-12:])
        self._last_point = Point(unpacker.unpack_uhyper(), unpacker.unpack_float())
        self._last_timestamp_nanoseconds = self._last_point.timestamp_nanoseconds
        if self._cache:
            self._cache.last_timestamp_timeseries = self._last_timestamp_nanoseconds

    def _timeseries_submit_blob(self, sampleRate, blob):
        pointCount = len(blob) / 12

        packer = xdrlib.Packer()
        VERSION = 1
        packer.pack_int(VERSION)
        packer.pack_fopaque(8, sampleRate.to_xdr())

        #Writing an array in XDR.  an array is always prefixed by the array length
        packer.pack_int(pointCount)
        data = packer.get_buffer() + blob

        response = self.url("/streams/timeseries/data/")\
                                 .param("version", "1")\
                                 .content_type("application/xdr")\
                                 .data(data)\
                                 .post()

        # if response is 201 created then we know the data was successfully added
        if response.status_code != httplib.CREATED:
            raise Exception("add timeseries data failed. status: %s %s  message:%s"%(response.status_code , response.reason, response.text))

    def histogram_append(self, samplerate, data):
        """
        append histogram data to this channel
        """

        logger.debug("calling  histogram_append. points:%s", len(data))


        #server allows a maximum upload size of 100,000 (as of 3-12-2013) we're limitting upload size to 20,000 points
        MAX_UPLOAD_SIZE = 20000

        #split the data into MAX_UPLOAD_SIZE chunchs to upload to sensorcloud
        s = 0
        e = MAX_UPLOAD_SIZE
        while s < len(data):
            self._histogram_append_chunk(samplerate, data[s:e])
            s = e
            e = e + MAX_UPLOAD_SIZE

    def _histogram_append_chunk(self, samplerate, data):

        logger.debug("calling  _histogram_append_chunk. points:%s", len(data))

        #if we get an empty container then there's nothing to do

        if len(data) == 0:
            return

        first_histogram = data[0]
        bin_start = first_histogram.bin_start
        bin_size = first_histogram.bin_size
        num_bins = len(first_histogram.bins)

        packer = xdrlib.Packer()
        for histogram in data:
            #check that all of the histograms have the same meta-info
            if histogram.bin_start != bin_start or\
                    histogram.bin_size != bin_size or\
                    len(histogram.bins) != num_bins:
                raise Exception("All histograms must have same bin start, bin size, and number of bins")
            packer.pack_uhyper(histogram.timestamp_nanoseconds)
            for bin_value in histogram.bins:
                packer.pack_uint(bin_value)

        #we are about to update the timeseries stream, if the request fails, we won't    so we don't know if it is going to be updated
        self._last_histogram = None
        self._last_timestamp_histogram = None
        self._last_timestamp_nanoseconds = None

        self._histogram_submit_blob(samplerate, bin_start, bin_size, num_bins, packer.get_buffer())

        #at this point we know that the upload was successful so we can update the last point
        self._last_histogram = data[-1]
        self._last_timestamp_histogram = self._last_histogram.timestamp_nanoseconds
        self._last_timestamp_nanoseconds = self._last_histogram.timestamp_nanoseconds
        if self._cache:
            self._cache.last_timestamp_histogram = self._last_histogram.timestamp_nanoseconds

    def histogram_append_blob(self, sampleRate, bin_start, bin_size, num_bins, blob):
        hist_size = 8 + (4 * num_bins)
        assert(len(blob) % hist_size == 0)

        if len(blob) == 0:
            return

        self._last_histogram = None
        self._last_timestamp_histogram = None
        self._last_timestamp_nanoseconds = None

        self._histogram_submit_blob(sampleRate, bin_start, bin_size, num_bins, blob)

        unpacker = xdrlib.Unpacker(blob[-hist_size:])
        timestamp = unpacker.unpack_uhyper()
        bins = []
        for i in xrange(num_bins):
            bins.append(unpacker.unpack_uint())
        self._last_histogram = Histogram(timestamp, bin_start, bin_size, bins)
        self._last_timestamp_histogram = self._last_histogram.timestamp_nanoseconds
        self._last_timestamp_nanoseconds = self._last_histogram.timestamp_nanoseconds
        if self._cache:
            self._cache.last_timestamp_histogram = self._last_histogram.timestamp_nanoseconds

    def _histogram_submit_blob(self, sampleRate, bin_start, bin_size, num_bins, blob):
        hist_size = 8 + (4 * num_bins)
        hist_count = len(blob) / hist_size

        packer = xdrlib.Packer()
        VERSION = 1
        packer.pack_int(VERSION)
        packer.pack_fopaque(8, sampleRate.to_xdr())

        #pack histogram info
        packer.pack_float(bin_start)
        packer.pack_float(bin_size)
        packer.pack_uint(num_bins)

        #Writing an array in XDR.  an array is always prefixed by the array length
        packer.pack_int(hist_count)
        data = packer.get_buffer() + blob

        response = self.url("/streams/histogram/data/")\
                                 .param("version", "1")\
                                 .content_type("application/xdr")\
                                 .data(data)\
                                 .post()

        # if response is 201 created then we know the data was successfully added
        if response.status_code != httplib.CREATED:
            raise Exception("add histogram data failed. status: %s %s  message:%s"%(response.status_code , response.reason, response.text))

