"""
Copyright 2013 LORD MicroStrain All Rights Reserved.

Distributed under the Simplified BSD License.
See file license.txt
"""

from datetime import datetime

NANOSECONDS_PER_SECOND = 1000000000
UNIX_EPOCH = datetime(1970, 1, 1)

class Point(object):
    """
    Point represents a datapoint as a timestamp and value in a timeseries dataset.
    """

    __slots__ = ["_nanosecond_timestamp", "_value"]

    def __init__(self, timestamp, value):
        self._value = float(value)

        if isinstance(timestamp, datetime):
            self._nanosecond_timestamp = int((timestamp-UNIX_EPOCH).total_seconds()*NANOSECONDS_PER_SECOND)
        else:
            self._nanosecond_timestamp = int(timestamp)

        assert self._nanosecond_timestamp >= 0, "timestamp must be greater than 0, or later than Jan 1, 1970"

    @property
    def timestamp(self):
        """ utc timestamp for the point. result is a datetime object.  point stores the timestamp with more resolution
           than a datetime object has.  To get the extra precision use either nanoseconds or timestamp_nanoseconds"""
        return datetime.utcfromtimestamp(self._nanosecond_timestamp / float(NANOSECONDS_PER_SECOND))

    @property
    def nanseconds(self):
        """ nanosecond portion of the timestamp.  will return a value between 0 and 999999999 """
        return self._nanosecond_timestamp%NANOSECONDS_PER_SECOND

    @property
    def timestamp_nanoseconds(self):
        """ get the utc timestamp as numer of nanoseconds since the unix epoch, Jan 1, 1970."""
        return self._nanosecond_timestamp

    @property
    def value(self):
        return self._value

    def __repr__(self):
        return "Point(%s,%s)"%(self.timestamp, self.value)

    def __eq__(self, other):
        return self.value == other.value and self.timestamp_nanoseconds == other.timestamp_nanoseconds

    def __ne__(self, other):
        return not self.__eq__(other)