import unittest
import xdrlib
from mock import Mock

import sensorcloud

def authRequest():
    import xdrlib
    token = "fake_token"
    server = "dsx.sensorcloud.microstrain.com"
    packer = xdrlib.Packer()
    packer.pack_string(token)
    packer.pack_string(server)
    packer.pack_string("")

    authRequestMock = Mock()
    authRequestMock.doRequest = Mock()
    authRequestMock.status_code = 200
    authRequestMock.raw = packer.get_buffer()
    return authRequestMock

class TestUpload(unittest.TestCase):

    def test_gatewayTimeout(self):
        uploadRequest = Mock()
        uploadRequest.doRequest = Mock()
        uploadRequest.status_code = 504
        uploadRequest.reason = ""
        uploadRequest.text = "text"
        sensorcloud.webrequest.Requests.Request = Mock()
        sensorcloud.webrequest.Requests.Request.side_effect = [authRequest(), uploadRequest]

        with self.assertRaises(sensorcloud.ServerError):
            device = sensorcloud.Device("FAKE", "fake")
            sensor = device.sensor("sensor")
            channel = sensor.channel("channel")
            channel.timeseries_append(sensorcloud.SampleRate.hertz(10), [sensorcloud.Point(12345, 10.5)])
            
