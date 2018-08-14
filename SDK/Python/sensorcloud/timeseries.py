
import logging
logger = logging.getLogger(__name__)

from datetime import datetime
import httplib
import xdrlib
import warnings

from util import nanosecond_to_timestamp, timestamp_to_nanosecond
from point import Point
from error import *

def descriptor(sample_rate):
    return str(sample_rate)

class TimeSeriesStream(object):

    def __init__(self, channel, start=None, end=None, samplerate=None, convertToUnits=True):

        self._channel = channel
        self._sampleRate = samplerate
        self._convertToUnits = convertToUnits

        #convert start to nanoseconds, or use o for default
        if start is None:
            self._startTimestampNanoseconds = 0

        elif isinstance(start, datetime):
            self._startTimestampNanoseconds = timestamp_to_nanosecond(start)

        else:
            #it must be an int
            self._startTimestampNanoseconds = int(start)

        #convert end to nanoseconds or use MAX_TIMESTAMP for a defualt
        if end is None:
            MAX_TIMESTAMP = 0xFFFFFFFFFFFFFFFF #max timestamp is the largest possible 64 bit unit value
            self._endTimestampNanoseconds = MAX_TIMESTAMP

        elif isinstance(end, datetime):
            self._endTimestampNanoseconds = timestamp_to_nanosecond(end)

        else:
            #it must be an int
            self._endTimestampNanoseconds = int(end)

        assert(end >= start)

    @property
    def startTimestampNanoseconds(self):
        return self._startTimestampNanoseconds

    @property
    def endTimestampNanoseconds(self):
        return self._startTimestampNanoseconds

    @property
    def startTimestamp(self):
        return nanosecond_to_timestamp(self.startTimestampNanoseconds)
    
    @property
    def endTimestamp(self):
        return nanosecond_to_timestamp(self.endTimestampNanoseconds)

    @property
    def EndTimestamp(self):
        warnings.warn("deprecated", DeprecationWarning)
        return self.endTimestamp

    def  __iter__(self):

        currentTimestamp = self._startTimestampNanoseconds
        while currentTimestamp <= self._endTimestampNanoseconds:

            data = self._downloadData(currentTimestamp, self._endTimestampNanoseconds)
            for p in data:
                yield p

            #data is empty, then we,ve exaughstestd all the data in the range, if it's not
            # then update the current timestamp
            if len(data) > 0:
                currentTimestamp = data[-1].timestamp_nanoseconds + 1

            else:
                break

    def range(self, start, end):
        return TimeSeriesStream(self._channel, start, end, self._samplerate, self._convertToUnits)

    def _downloadData(self, start, end):
        start = int(start)
        end = int(end)

        #url: /sensors/<sensor_name>/channels/<channel_name>/streams/timeseries/data/
        #    params:
        #        start (required)
        #        end  (required)
        #        showSampleRateBoundary (oiptional)
        #        samplerate (oiptional)

        response = self._channel.url_without_create("/streams/timeseries/data/")\
                                  .param("version", "1")\
                                  .param("starttime", start)\
                                  .param("endtime", end)\
                                  .accept("application/xdr")\
                                  .get()

        # check the response code for success
        if response.status_code == httplib.NOT_FOUND:
            #404 is an empty list
            return []

        elif response.status_code != httplib.OK:
            #all other errors are exceptions
            raise error(response, "download timeseris data")


        #packer for the units xdr format
        xdrdata = xdrlib.Unpacker(response.raw)

        datapoints = []
        try:
            # timeseries/data always returns a relativly small chunk of data less than 50,000 points so we can proccess it all at once.  We won't be given an infinite stream
            # however a future enhancement could be to stat proccessing this stream as soon as we have any bytes avialable to the user, so they could be
            # iterating over the data while it is still being downloaded.
            while True:
                timestamp = xdrdata.unpack_uhyper()
                value = self._convert(xdrdata.unpack_float(), timestamp)
                datapoints.append(Point(timestamp, value))

        except EOFError:
            pass

        return datapoints



    def _convert(self, value, timestamp):
        return value
        if not self._convertToUnits:
            return value

        units = self._channel.GetTimeSeriresUnits()
        return units.Convert(timestamp, value)


