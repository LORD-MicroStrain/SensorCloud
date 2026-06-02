import unittest
import tempfile
import os
import shutil

import sensorcloud

class CacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp_path = tempfile.mkdtemp()
        self.cache_path = os.path.join(self.tmp_path, "test_cache.json")
        cache = sensorcloud.cache.Cache(self.cache_path)
        cache.auth_server = sensorcloud.device.DEFAULT_AUTH_SERVER
        cache.device_id = "my_device"
        cache.server = "https://mdx.sensorcloud.microstrain.com"
        cache.token = "lasjdflajfdlasgjlasgf"
        cache.save()
    
    def tearDown(self):
        shutil.rmtree(self.tmp_path)

    def test_valid_cache(self):
        dev = sensorcloud.Device("my_device", "some_key", cache_file=self.cache_path)
        self.assertEqual(dev._requests._authToken, "lasjdflajfdlasgjlasgf")
        self.assertEqual(dev._requests._apiServer, "https://mdx.sensorcloud.microstrain.com")

    def test_invalid_cache_by_device_name(self):
        dev = sensorcloud.Device("my_device2", "some_key", cache_file=self.cache_path)
        self.assertEqual(dev._requests._authToken, None)
        self.assertEqual(dev._requests._apiServer, None)

    def test_invalid_cache_by_auth_server(self):
        dev = sensorcloud.Device("my_device2", "some_key", "https://my.new.server", cache_file=self.cache_path)
        self.assertEqual(dev._requests._authToken, None)
        self.assertEqual(dev._requests._apiServer, None)

    def test_cache_saved(self):
        dev = sensorcloud.Device("my_device2", "some_key", "https://my.new.server", cache_file=self.cache_path)
        dev.save_cache()

        cache = sensorcloud.cache.Cache(self.cache_path)
        self.assertEqual(cache.auth_server, "https://my.new.server")
        self.assertEqual(cache.device_id, "my_device2")