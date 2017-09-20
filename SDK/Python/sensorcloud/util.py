"""
Copyright 2013 LORD MicroStrain All Rights Reserved.

Distributed under the Simplified BSD License.
See file license.txt
"""

from datetime import datetime

NANOSECONDS_PER_SECOND = 1000000000
UNIX_EPOCH = datetime(1970, 1, 1)

def nanosecond_to_timestamp(nanoseconds):
    return datetime.utcfromtimestamp(nanoseconds / float(NANOSECONDS_PER_SECOND))


def timestamp_to_nanosecond(dt):
    int((dt - UNIX_EPOCH).total_seconds() * NANOSECONDS_PER_SECOND)
