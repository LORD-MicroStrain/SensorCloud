import unittest
import mock
from mock import Mock

import sensorcloud

from helpers import authRequest

class TestUpload(unittest.TestCase):

    def test_timeseriesGatewayTimeout(self):
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

    def test_timeseriesConflict(self):
        uploadRequest = Mock()
        uploadRequest.doRequest = Mock()
        uploadRequest.status_code = 409
        uploadRequest.reason = ""
        uploadRequest.text = '{"errorcode": "409-001", "message": ""}'
        sensorcloud.webrequest.Requests.Request = Mock()
        sensorcloud.webrequest.Requests.Request.side_effect = [authRequest(), uploadRequest]

        with self.assertRaises(sensorcloud.UserError):
            device = sensorcloud.Device("FAKE", "fake")
            sensor = device.sensor("sensor")
            channel = sensor.channel("channel")
            channel.timeseries_append(sensorcloud.SampleRate.hertz(10), [sensorcloud.Point(12345, 10.5)])

    def test_histogramGatewayTimeout(self):
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
            data = [sensorcloud.Histogram(1234, 0, 1, [10.5])]
            channel.histogram_append(sensorcloud.SampleRate.hertz(10), data)

    def test_histogramConflict(self):
        uploadRequest = Mock()
        uploadRequest.doRequest = Mock()
        uploadRequest.status_code = 409
        uploadRequest.reason = ""
        uploadRequest.text = '{"errorcode": "409-001", "message": ""}'
        sensorcloud.webrequest.Requests.Request = Mock()
        sensorcloud.webrequest.Requests.Request.side_effect = [authRequest(), uploadRequest]

        with self.assertRaises(sensorcloud.UserError):
            device = sensorcloud.Device("FAKE", "fake")
            sensor = device.sensor("sensor")
            channel = sensor.channel("channel")
            data = [sensorcloud.Histogram(1234, 0, 1, [10.5])]
            channel.histogram_append(sensorcloud.SampleRate.hertz(10), data)

    def test_createAndRetryOn404(self):
        sensorNotFound = Mock()
        sensorNotFound.status_code = 404
        sensorNotFound.text = '{"errorcode": "404-001", "message": ""}'

        created = Mock()
        created.status_code = 201

        request = Mock()
        request.side_effect = [authRequest(), sensorNotFound, created, created, created]
        sensorcloud.webrequest.Requests.Request = request

        device = sensorcloud.Device("FAKE", "fake")
        sensor = device.sensor("sensor")
        channel = sensor.channel("channel")
        channel.timeseries_append(sensorcloud.SampleRate.hertz(10), [sensorcloud.Point(12345, 10.5)])

        calls = [
                mock.call('POST', 'https://dsx.sensorcloud.microstrain.com/SensorCloud/devices/FAKE/sensors/sensor/channels/channel/streams/timeseries/data/', mock.ANY),
                mock.call('PUT', 'https://dsx.sensorcloud.microstrain.com/SensorCloud/devices/FAKE/sensors/sensor/', mock.ANY),
                mock.call('PUT', 'https://dsx.sensorcloud.microstrain.com/SensorCloud/devices/FAKE/sensors/sensor/channels/channel/', mock.ANY),
                mock.call('POST', 'https://dsx.sensorcloud.microstrain.com/SensorCloud/devices/FAKE/sensors/sensor/channels/channel/streams/timeseries/data/', mock.ANY)
        ]
        request.assert_has_calls(calls)

    def test_createAndRetryChannel404(self):
        sensorNotFound = Mock()
        sensorNotFound.status_code = 404
        sensorNotFound.text = '{"errorcode": "404-002", "message": ""}'

        created = Mock()
        created.status_code = 201

        request = Mock()
        request.side_effect = [authRequest(), sensorNotFound, created, created]
        sensorcloud.webrequest.Requests.Request = request

        device = sensorcloud.Device("FAKE", "fake")
        sensor = device.sensor("sensor")
        channel = sensor.channel("channel")
        channel.timeseries_append(sensorcloud.SampleRate.hertz(10), [sensorcloud.Point(12345, 10.5)])

        calls = [
                mock.call('POST', 'https://dsx.sensorcloud.microstrain.com/SensorCloud/devices/FAKE/sensors/sensor/channels/channel/streams/timeseries/data/', mock.ANY),
                mock.call('PUT', 'https://dsx.sensorcloud.microstrain.com/SensorCloud/devices/FAKE/sensors/sensor/channels/channel/', mock.ANY),
                mock.call('POST', 'https://dsx.sensorcloud.microstrain.com/SensorCloud/devices/FAKE/sensors/sensor/channels/channel/streams/timeseries/data/', mock.ANY)
        ]
        request.assert_has_calls(calls)
