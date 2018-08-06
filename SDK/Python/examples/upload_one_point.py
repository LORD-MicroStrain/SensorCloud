import time
import sys
import os

sys.path.append(os.getcwd())

import sensorcloud

def timeNow():
    return int(time.time()) * 1000000000

def main():
    deviceName, key, sensorName, channelName = sys.argv[1:]

    device = sensorcloud.Device(deviceName, key)
    sensor = device.sensor(sensorName)
    channel = sensor.channel(channelName)

    channel.timeseries_append(sensorcloud.SampleRate.seconds(10), [sensorcloud.Point(timeNow(), 10.5)])

if __name__ == "__main__":
    main()
