import unittest
import xdrlib
import tempfile
import os

import mock
from mock import Mock

import sensorcloud

from helpers import *

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

    def test_uploadTimeseries(self):
        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_int(0)
        noPartitions = Mock()
        noPartitions.status_code = 200
        noPartitions.raw = packer.get_buffer()

        request = Mock()
        request.side_effect = [authRequest(), created(), noPartitions]
        sensorcloud.webrequest.Requests.Request = request

        device = sensorcloud.Device("FAKE", "fake")
        sensor = device.sensor("sensor")
        channel = sensor.channel("channel")
        channel.timeseries_append(sensorcloud.SampleRate.hertz(10), [sensorcloud.Point(12345, 10.5)])
        self.assertEqual(channel.last_timestamp_nanoseconds, 12345)

    def test_uploadHistogram(self):
        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_int(0)
        noPartitions = Mock()
        noPartitions.status_code = 200
        noPartitions.raw = packer.get_buffer()

        request = Mock()
        request.side_effect = [authRequest(), created(), noPartitions]
        sensorcloud.webrequest.Requests.Request = request

        device = sensorcloud.Device("FAKE", "fake")
        sensor = device.sensor("sensor")
        channel = sensor.channel("channel")
        channel.histogram_append(sensorcloud.SampleRate.hertz(10), [sensorcloud.Histogram(12345, 0.0, 1.0, [10.5, 4328.3])])
        self.assertEqual(channel.last_timestamp_nanoseconds, 12345)

    def test_noData_lastTimestampZero(self):
        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_int(0)
        noPartitions = Mock()
        noPartitions.status_code = 200
        noPartitions.raw = packer.get_buffer()
        
        request = Mock()
        request.side_effect = [authRequest(), noPartitions, noPartitions]
        sensorcloud.webrequest.Requests.Request = request

        device = sensorcloud.Device("FAKE", "fake")
        sensor = device.sensor("sensor")
        channel = sensor.channel("channel")
        self.assertEqual(channel.last_timestamp_nanoseconds, 0)

    def test_lastTimestampUsesLatest(self):
        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_int(2)
        packer.pack_uhyper(0)
        packer.pack_uhyper(12345)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(1)
        packer.pack_int(10)
        packer.pack_int(1)
        packer.pack_int(1)
        packer.pack_uhyper(12345)
        packer.pack_float(10.5)
        packer.pack_uhyper(0)
        packer.pack_uhyper(123456)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(1)
        packer.pack_int(10)
        packer.pack_int(1)
        packer.pack_int(1)
        packer.pack_uhyper(12345)
        packer.pack_float(10.5)
        tsPartitions = Mock()
        tsPartitions.status_code = 200
        tsPartitions.raw = packer.get_buffer()
        
        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_int(2)
        packer.pack_uhyper(0)
        packer.pack_uhyper(12345)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(0)
        packer.pack_int(30)
        packer.pack_int(21)
        packer.pack_float(10.0)
        packer.pack_float(5.0)
        packer.pack_uhyper(0)
        packer.pack_uhyper(123455)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(0)
        packer.pack_int(60)
        packer.pack_int(10)
        packer.pack_float(11.0)
        packer.pack_float(8.0)
        histPartitions = Mock()
        histPartitions.status_code = 200
        histPartitions.raw = packer.get_buffer()

        request = Mock()
        request.side_effect = [authRequest(), tsPartitions, histPartitions]
        sensorcloud.webrequest.Requests.Request = request

        device = sensorcloud.Device("FAKE", "fake")
        sensor = device.sensor("sensor")
        channel = sensor.channel("channel")
        self.assertEqual(channel.last_timestamp_nanoseconds, 123456)

        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_int(2)
        packer.pack_uhyper(0)
        packer.pack_uhyper(12345)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(1)
        packer.pack_int(10)
        packer.pack_int(1)
        packer.pack_int(1)
        packer.pack_uhyper(12345)
        packer.pack_float(10.5)
        packer.pack_uhyper(0)
        packer.pack_uhyper(123455)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(1)
        packer.pack_int(10)
        packer.pack_int(1)
        packer.pack_int(1)
        packer.pack_uhyper(12345)
        packer.pack_float(10.5)
        tsPartitions = Mock()
        tsPartitions.status_code = 200
        tsPartitions.raw = packer.get_buffer()
        
        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_int(2)
        packer.pack_uhyper(0)
        packer.pack_uhyper(12345)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(0)
        packer.pack_int(30)
        packer.pack_int(21)
        packer.pack_float(10.0)
        packer.pack_float(5.0)
        packer.pack_uhyper(0)
        packer.pack_uhyper(123456)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(0)
        packer.pack_int(60)
        packer.pack_int(10)
        packer.pack_float(11.0)
        packer.pack_float(8.0)
        histPartitions = Mock()
        histPartitions.status_code = 200
        histPartitions.raw = packer.get_buffer()

        request = Mock()
        request.side_effect = [authRequest(), tsPartitions, histPartitions]
        sensorcloud.webrequest.Requests.Request = request

        device = sensorcloud.Device("FAKE", "fake")
        sensor = device.sensor("sensor")
        channel = sensor.channel("channel")
        self.assertEqual(channel.last_timestamp_nanoseconds, 123456)

    def test_cacheSetByGet(self):
        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_int(2)
        packer.pack_uhyper(0)
        packer.pack_uhyper(12345)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(1)
        packer.pack_int(10)
        packer.pack_int(1)
        packer.pack_int(1)
        packer.pack_uhyper(12345)
        packer.pack_float(10.5)
        packer.pack_uhyper(0)
        packer.pack_uhyper(123456)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(1)
        packer.pack_int(15)
        packer.pack_int(1)
        packer.pack_int(1)
        packer.pack_uhyper(12345)
        packer.pack_float(10.5)
        tsPartitions = Mock()
        tsPartitions.status_code = 200
        tsPartitions.raw = packer.get_buffer()
        
        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_int(2)
        packer.pack_uhyper(0)
        packer.pack_uhyper(12345)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(0)
        packer.pack_int(30)
        packer.pack_int(21)
        packer.pack_float(10.0)
        packer.pack_float(5.0)
        packer.pack_uhyper(0)
        packer.pack_uhyper(123455)
        packer.pack_int(15)
        packer.pack_int(5000)
        packer.pack_int(0)
        packer.pack_int(60)
        packer.pack_int(10)
        packer.pack_float(11.0)
        packer.pack_float(8.0)
        histPartitions = Mock()
        histPartitions.status_code = 200
        histPartitions.raw = packer.get_buffer()

        request = Mock()
        request.side_effect = [authRequest(), tsPartitions, histPartitions]
        sensorcloud.webrequest.Requests.Request = request

        fd, path = tempfile.mkstemp()
        os.close(fd)
        device = sensorcloud.Device("FAKE", "fake", cache_file=path)
        sensor = device.sensor("sensor")
        channel = sensor.channel("channel")
        channel.last_timestamp_nanoseconds

        self.assertEqual(channel._cache.timeseries_partition(sensorcloud.SampleRate.hertz(10)).last_timestamp, 12345)
        self.assertEqual(channel._cache.timeseries_partition(sensorcloud.SampleRate.hertz(15)).last_timestamp, 123456)
        self.assertEqual(channel._cache.histogram_partition(sensorcloud.SampleRate.seconds(30), 10.0, 5.0, 21).last_timestamp, 12345)
        self.assertEqual(channel._cache.histogram_partition(sensorcloud.SampleRate.seconds(60), 11.0, 8.0, 10).last_timestamp, 123455)
        os.unlink(path)

    def test_cacheSetOnUpload(self):
        request = Mock()
        request.side_effect = [authRequest(), created(), created()]
        sensorcloud.webrequest.Requests.Request = request

        fd, path = tempfile.mkstemp()
        os.close(fd)
        device = sensorcloud.Device("FAKE", "fake", cache_file=path)
        sensor = device.sensor("sensor")
        channel = sensor.channel("channel")
        channel.timeseries_append(sensorcloud.SampleRate.hertz(10), [sensorcloud.Point(12345, 10.5)])
        channel.histogram_append(sensorcloud.SampleRate.hertz(10), [sensorcloud.Histogram(123455, 0.0, 1.0, [10.5, 4328.3])])

        
        self.assertEqual(channel._cache.timeseries_partition(sensorcloud.SampleRate.hertz(10)).last_timestamp, 12345)
        self.assertEqual(channel._cache.histogram_partition(sensorcloud.SampleRate.hertz(10), 0.0, 1.0, 2).last_timestamp, 123455)
        os.unlink(path)
        
