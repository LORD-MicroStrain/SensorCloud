import unittest
import mock
from mock import Mock

import sensorcloud

from helpers import authRequest

class TestAutoCreate(unittest.TestCase):

    def test_autoCreateSensor(self):
        sensorNotFound = Mock()
        sensorNotFound.status_code = 404
        sensorNotFound.text = '{"errorcode": "404-001", "message": ""}'

        created = Mock()
        created.status_code = 201

        ok = Mock()
        ok.status_code = 200

        request = Mock()
        request.side_effect = [authRequest(), sensorNotFound, created, ok]
        sensorcloud.webrequest.Requests.Request = request

        device = sensorcloud.Device("FAKE", "fake")
        sensor = device.sensor("sensor")
        self.assertTrue("channel" in sensor)

        calls = [
                mock.call('GET', 'https://dsx.sensorcloud.microstrain.com/SensorCloud/devices/FAKE/sensors/sensor/channels/channel/attributes/', mock.ANY),
                mock.call('PUT', 'https://dsx.sensorcloud.microstrain.com/SensorCloud/devices/FAKE/sensors/sensor/', mock.ANY),
                mock.call('GET', 'https://dsx.sensorcloud.microstrain.com/SensorCloud/devices/FAKE/sensors/sensor/channels/channel/attributes/', mock.ANY)
        ]
        request.assert_has_calls(calls)

    def test_autoCreateSensorFails(self):
        sensorNotFound = Mock()
        sensorNotFound.status_code = 404
        sensorNotFound.text = '{"errorcode": "404-001", "message": ""}'

        serverError = Mock()
        serverError.status_code = 500

        request = Mock()
        request.side_effect = [authRequest(), sensorNotFound, serverError]
        sensorcloud.webrequest.Requests.Request = request

        with self.assertRaises(sensorcloud.ServerError):
            device = sensorcloud.Device("FAKE", "fake")
            sensor = device.sensor("sensor")
            "channel" in sensor
