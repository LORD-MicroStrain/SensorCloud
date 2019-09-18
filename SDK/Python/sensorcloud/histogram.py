"""
Copyright 2013 LORD MicroStrain All Rights Reserved.

Distributed under the Simplified BSD License.
See file license.txt
"""

from datetime import datetime

NANOSECONDS_PER_SECOND = 1000000000
UNIX_EPOCH = datetime(1970, 1, 1)

def descriptor(sample_rate, bin_start, bin_size, num_bins):
    return "%s_%6e_%6e_%d" % (str(sample_rate), bin_start, bin_size, num_bins)

def descriptor_match(descriptor, sample_rate = None, bin_start = None, bin_size = None, num_bins = None):
    
    def descriptor_float(value):
        return "%6e" % value

    def split_descriptor():
        sp = descriptor.split("_")
        if len(sp) != 4:
            return (None, None, None, None)
        return sp

    d_sample_rate, d_bin_start, d_bin_size, d_num_bins = split_descriptor()
    ret = str(sample_rate) == d_sample_rate if sample_rate is not None else True
    ret = ret and (descriptor_float(bin_start) == d_bin_start if bin_start is not None else True)
    ret = ret and (descriptor_float(bin_size) == d_bin_size if bin_size is not None else True)
    return ret and (str(num_bins) == d_num_bins if num_bins is not None else True)

class Histogram(object):
    """
    Point represents a datapoint as a timestamp and value in a timeseries dataset.
    """

    __slots__ = ["_nanosecond_timestamp", "_binStart", "_binSize", "_bins"]

    def __init__(self, timestamp, binStart, binSize, bins):
        self._binStart = binStart
        self._binSize = binSize
        self._bins = bins

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
    def bin_start(self):
        return self._binStart

    @property
    def bin_size(self):
        return self._binSize

    @property
    def bins(self):
        return self._bins

    def descriptor(self, sample_rate):
        return descriptor(sample_rate, self.bin_start, self.bin_size, len(self.bins))

    def __repr__(self):
        return "Histogram(Bin Start:%s,Bin Size:%s, %s, %s)"%(self.bin_start, self.bin_size, self.timestamp, self.bins)

    def __eq__(self, other):
        for i, binValue in enumerate(other.bins):
            if binvalue != self.bins[i]:
                return False

        return self.bin_start == other.bin_start and self.bin_size == other.bin_size and self.timestamp_nanoseconds == other.timestamp_nanoseconds

    def __ne__(self, other):
        return not self.__eq__(other)
