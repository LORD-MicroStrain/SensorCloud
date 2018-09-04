'''
Created on Nov 13, 2014

@author: jonathan_herbst
'''

import json

class Partition(object):
    @property
    def descriptor(self):
        return self._descriptor

    @property
    def last_timestamp(self):
        return self._attributes.get('last_timestamp')

    @last_timestamp.setter
    def last_timestamp(self, value):
        self._attributes['last_timestamp'] = long(value)

    def save(self):
        self._cache.save()

    def __init__(self, cache, descriptor, attributes):
        self._cache = cache
        self._descriptor = descriptor
        self._attributes = attributes

class ChannelCache(object):

    @property
    def name(self):
        return self._name

    @property
    def timeseries_partitions(self):
        return [Partition(self._cache, descriptor, attributes) for descriptor, attributes in self._timeseries_partitions.items()]

    @property
    def histogram_partitions(self):
        return [Partition(self._cache, descriptor, attributes) for descriptor, attributes in self._histogram_partitions.items()]

    def timeseries_partition(self, sample_rate):
        descriptor = str(sample_rate)
        if descriptor not in self._timeseries_partitions:
            self._timeseries_partitions[descriptor] = {}
        return Partition(self._cache, descriptor, self._timeseries_partitions[descriptor])

    def delete_timeseries_partition(self, sample_rate):
        descriptor = str(sample_rate)
        try:
            del self._timeseries_partitions[descriptor]
        except KeyError:
            pass

    def histogram_partition(self, sample_rate, bin_start, bin_size, num_bins):
        descriptor = "%s_%6e_%6e_%d" % (str(sample_rate), bin_start, bin_size, num_bins)
        if descriptor not in self._histogram_partitions:
            self._histogram_partitions[descriptor] = {}
        return Partition(self._cache, descriptor, self._histogram_partitions[descriptor])

    def delete_histogram_partition(self, sample_rate, bin_start, bin_size, num_bins):
        descriptor = "%s_%6e_%6e_%d" % (str(sample_rate), bin_start, bin_size, num_bins)
        try:
            del self._histogram_partitions[descriptor]
        except KeyError:
            pass

    def save(self):
        self._cache.save()

    def __init__(self, cache, name, attributes):
        self._cache = cache
        self._name = name
        if "timeseries_partitions" not in attributes:
            attributes["timeseries_partitions"] = {}
        self._timeseries_partitions = attributes["timeseries_partitions"]
        if "histogram_partitions" not in attributes:
            attributes["histogram_partitions"] = {}
        self._histogram_partitions = attributes["histogram_partitions"]

class SensorCache(object):

    @property
    def name(self):
        return self._name

    @property
    def channels(self):
        return [ChannelCache(self, channel[0], channel[1]) for channel in self._channels.items()]

    def channel(self, name):
        if name not in self._channels:
            self._channels[name] = {}
        return ChannelCache(self, name, self._channels[name])

    def save(self):
        self._cache.save()

    def __init__(self, cache, name, channels):
        self._cache = cache
        self._name = name
        self._channels = channels

class Cache(object):

    @property
    def server(self):
        if 'server' in self._data:
            return self._data["server"]
        return None

    @server.setter
    def server(self, value):
        self._data['server'] = value

    @property
    def token(self):
        if 'token' in self._data:
            return self._data['token']
        return None

    @token.setter
    def token(self, value):
        self._data['token'] = value

    @property
    def sensors(self):
        if 'sensors' not in self._data:
            self._data['sensors'] = {}
        return [SensorCache(self, sensor[0], sensor[1]) for sensor in self._data['sensors'].items()]

    def sensor(self, name):
        if 'sensors' not in self._data:
            self._data['sensors'] = {}
        if name not in self._data['sensors']:
            self._data['sensors'][name] = {}

        return SensorCache(self, name, self._data['sensors'][name])

    def save(self):
        with open(self._path, 'wb') as f:
            f.write(json.dumps(self._data, encoding='utf8'))

    def __init__(self, path):
        self._path = path
        self._data = {}
        try:
            self._data = json.loads(open(path, 'rb').read())
            self._data = json_decode(self._data)
        except: # the cache file doesn't exist yet
            pass

def json_decode(data):
    def json_decode_unicode(data):
        return data.encode('utf-8')

    def json_decode_list(data):
        return [json_decode(i) for i in data]

    def json_decode_dict(data):
        return dict([(json_decode_unicode(k), json_decode(v)) for k,v in data.items()])

    if isinstance(data, unicode):
        return json_decode_unicode(data)
    if isinstance(data, list):
        return json_decode_list(data)
    if isinstance(data, dict):
        return json_decode_dict(data)
    return data
