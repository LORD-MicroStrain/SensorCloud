#import sys
#import os
#sys.path.append(os.getcwd())

import unittest
import xdrlib
from mock import Mock

import sensorcloud

class TestAuthentication(unittest.TestCase):

    def test_quotaError(self):
        authRequestMock = Mock()
        authRequestMock.doRequest = Mock()
        authRequestMock.status_code = 401
        authRequestMock.text = '{"errorcode": "401-005", "message": ""}'
        sensorcloud.webrequest.Requests.Request = Mock(return_value=authRequestMock)

        with self.assertRaises(sensorcloud.QuotaExceededError):
            device = sensorcloud.Device("FAKE", "fake")
            device._requests.authenticate()

    def test_authError(self):
        authRequestMock = Mock()
        authRequestMock.doRequest = Mock()
        authRequestMock.status_code = 401
        authRequestMock.text = '{"errorcode": "401-001", "message": ""}'
        sensorcloud.webrequest.Requests.Request = Mock(return_value=authRequestMock)

        with self.assertRaises(sensorcloud.AuthenticationError):
            device = sensorcloud.Device("FAKE", "fake")
            device._requests.authenticate()

    def test_authValid(self):
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
        sensorcloud.webrequest.Requests.Request = Mock(return_value=authRequestMock)

        device = sensorcloud.Device("FAKE", "fake")
        device._requests.authenticate()
        self.assertEqual(device._requests._authToken, token)
        self.assertEqual(device._requests._apiServer, "https://" + server)

if __name__ == "__main__":
    unittest.main()
