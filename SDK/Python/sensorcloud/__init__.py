"""
Copyright 2013 LORD MicroStrain All Rights Reserved.

Distributed under the Simplified BSD License.
See file license.txt
"""

import sys
from samplerate import SampleRate
from device import Device
from point import Point

__version__ = '0.2.2'

# True to reauthenticate on token expiration, false otherwise
Reauthenticate = True
UserAgent = 'SC.py/%s (%s)' % (__version__, sys.platform)