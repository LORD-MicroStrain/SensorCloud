"""
Copyright 2013 LORD MicroStrain All Rights Reserved.

Distributed under the Simplified BSD License.
See file license.txt
"""

from datetime import timedelta
import xdrlib

#samplerate types
HERTZ = 1
SECONDS = 0

SAMPLERATE_NAMES = {HERTZ:"hertz", SECONDS:"seconds"}

class SampleRate(object):


    def __init__(self, rate_type, rate):
        assert(rate_type in (HERTZ, SECONDS))
        assert(rate >= 0)

        self._rate_type = rate_type
        self._rate = rate


    def __str__(self):
        return "%d %s"%(self._rate, SAMPLERATE_NAMES[self._rate_type])

    def __eq__(self, other):
        if isinstance(other, SampleRate):
            return self._rate_type == other._rate_type and self._rate == other._rate
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    @property
    def interval(self):
        if self._rate_type == HERTZ:
            return timedelta(seconds=1.0/self._rate)
        else:
            return timedelta(seconds=self._rate)

    @classmethod
    def hertz(cls, rate):
        return SampleRate(HERTZ, rate)

    @classmethod
    def seconds(cls, rate):
        return SampleRate(SECONDS, rate)

    def to_xdr(self):
        packer = xdrlib.Packer()
        packer.pack_enum(self._rate_type)
        packer.pack_int(self._rate)
        return packer.get_buffer()
