## Getting Started ##

### Accessing a SensorCloud time-series###

The time-series repository class is used to access, as well as create, any SensorCloud time-series. Each instance of the SensorCloud repository class is able to search for the time-series on a specific device,

```repo = TimeSeriesRepo("FFFF35A5623")   % can access all time-series on the device with the serial FFFF35A5623```

This creates a new instance of the time-series repository class named repo. With this time series repository, it is possible to retrieve every time series associated with the device using the getAllTimeSeries method. This will return a list of time-series that match the specified criteria, or all time series if no criteria is specified. If it cannot find any matching time series, it will return an empty list. 

To create a new time series use the  createTimeSeries function, where SampleRateType is 'hertz' or 'seconds'.
```newSeries = repo.createTimeSeries( SensorName, ChannelName, SampleRate, SampleRateType )```

The function getAllTimeSeries also accepts the same arguments, though all of them are optional.
```TimeSeriesRepo.getAllTimeSeries( SensorName, ChannelName, SampleRate, SampleRateType )```

To access all the time-series on a device, call the method without any input arguments.
```allseries = repo.getAllTimeSeries()```

To find all the time-series on the Counter sensor.
```allseries = repo.getAllTimeSeries("Counter")```

To to get a list of all time-series on the Pitch channel of the Counter sensor.
```allseries = repo.getAllTimeSeries("Counter", "Pitch")```

The sample rate must either be "hertz" or "seconds," and the method will return an error if the sample rate doesn't match either type. To get only the 10 Hz time-series on a device named FlightTest, sensor named Counter, on a channel named Pitch,
Accessing time-series properties
```allSeries = repo.getAllTimeSeries("Counter", "Pitch", 10, "hertz")```

You can access the sensorName, channelName, sampleRate, and sampleRateType of an existing time-series by using the getSensorName, getChannelName, getSampleRate, and getSampleRateType methods,
```python
>>> series = allSeries[0]
>>> series.getSensorName()
Counter
>>> series.getChannelName()
Pitch
>>> series.getSampleRate()
10
>>> series.getSampleRateType()
hertz
```

### Indexing into a Time-Series ###

All time-series data is stored as a list of tuples, where each tuple represents a single data point of the time-series. Each tuple has two element, where the first element is a time-stamp and the second element is a value. All data points are sorted in order of increasing time-stamp. The time-series class supports both indexing and slicing,
>>> firstPoint = series[0];   % return the first point in the time-series
>>> firstTimeStamp = firstPoint[0]  % return the time-stamp of the first point in the time-series
>>> firstTimeStamp
1298040900212767000L
>>> firstPoint[1]   % return the value of the first point in the time-series
8.59136962890625
>>> firstTenPoints = series[: 10]   % return a slice containing the first ten points in the time-series

All time-stamps are recorded as the number of nanoseconds since 1970.  Helper functions for converting to/from SensorCloud nanosecond time-stamps are available in the Helpers module. To convert a time-stamp from nanoseconds to a human-readable date,
>>> import Helpers
>>> date = Helpers.getDateFromTimeStamp(firstTimeStamp)
>>> date
datetime.datetime(2011, 2, 18, 9, 55, 0, 212767)% returns a time datetime object

You can also convert a date into a nanosecond time-stamp,
>>> Helpers.getTimeStampFromDate(date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond)
1298040900212767000L

To access the first 100 points in the time-series,
>>> data = series[: 100]

When indexing into a time-series, it will check if the corresponding data has already been pulled from SensorCloud. If it has, it is returned immediately, and if it hasn't then it is pulled and stored in a cache, therefore improving subsequent indexing performance. All SensorCloud time-series data is read-only, therefore you cannot make changes to the time-stamp or values of any points in the time-series.

The len method isn't supported for the SensorCloud time-series. Since new data can be uploaded at any moment, the time-series doesn't have a fixed size.  Attempting to invoke this method results in an error message
>>> len(series)
Traceback (most recent call last):
File "<console>", line 1, in <module>
TypeError: object of type 'TimeSeriesData' has no len()

For these same reasons, the end operator isn't support either.
Adding new data

Data can appended data to any new or existing time-series using the push method. All new data must be added as a list of tuples, where the first element is a time-stamp and the second element is a value,
>>> newSeries = repo.createTimeSeries("Counter", "Pitch", 10, "hertz")
>>> time = [.01 * i for i in range(0, 300)] % create a vector of time values, from 0 to 3, sampled at 100 Hz
>>> signal = [sin(2 * pi * t * 1.1) for t in time] % create a 1.1 Hz sine wave
>>> startTime += getTimeStampFromDate(2010, 10, 7, 6, 14, 22, 7524); % make all time-stamps relative to 10/7/2010 6:14:22.007524  
>>> time = [startTime + t * 1000000000 for t in time]  % convert seconds to nanoseconds
>>> newSeries.push([(time[i], signal[i]) for i in range(0, 300)])   % push 300 new data points to the time-series, as a list of tuples

Data that's been pushed to the time-series isn't immediately saved to SensorCloud, instead it's stored in a "new data buffer" as a stack (last-in-first-out). Data that's been pushed onto a time-series can be removed using the pop method,
>>> newSeries.pop(20)   % remove the last 20 points added to the time-series

All the new, unsaved data, can accessed using the peek function
>>> lastTenPoints = newSeries.peek(10)   % return a list containing the last 10 points added

If the second value is omitted, then peek will return all new data that's been added.
Saving a time-series to SensorCloud

The data that has been appended to any new or existing time-series can be saved using the save method
>>> newSeries.save()

When saving new data to an existing time-series, Math Engine will ensure that the first time-stamp of the new data is greater than the last time-stamp of the old data, and that the time-stamps of the new data increase monotonically. These measures ensure the integrity of the any time-series isn't inadvertently compromised when pushing new data to SensorCloud.

The save method will save all the new data to SensorCloud, and reset the "new data buffer" of the time-series,
>>> len(newSeries.peek()) % peek will return a list of all unsaved data points, but since the time-series has been saved, it will return an empty list
0
Example

The following example demonstrates all the key features of the SensorCloud time-series class. This script accesses temperature data available in SensorCloud, finds all the min and max temperatures each day, then uploads the results to SensorCloud
ProcessTemperature(uploadSensor):
    repo = TimeSeriesRepo("temperature")
    temperature = repo.getAllTimeSeries('SV1', 'temp')[0]
    minTemps = []
    maxTemps = []
    dailyTemps = []
    currentDate = helpers.getDateFromTimeStamp(temperature[0][0])
    for t in temperature:
        newDate = helpers.getDateFromTimeStamp(t[0])
        if newDate.day != currentDate.day:
            currentTimeStamp = helpers.getTimeStampFromDate(currentDate.year, currentDate.month, currentDate.day, 12, 0, 0, 0)
            minTemps.append((currentTimeStamp, min(dailyTemps, key = lambda x: x[1])[1]))
            maxTemps.append((currentTimeStamp, max(dailyTemps, key = lambda x: x[1])[1]))
            dailyTemps = []
            currentDate = newDate
        else:
            dailyTemps.append(t)
     
    delta = [(minTemps[i][0], maxTemps[i][1] - minTemps[i][1]) for i in range(0, len(minTemps))]    
    minSeries = repo.createTimeSeries(uploadSensor, 'minTemp', 86400, 'seconds')[0]
    maxSeries = repo.createTimeSeries(uploadSensor, 'maxTemp', 86400, 'seconds')[0]
    deltaSeries = repo.createTimeSeries(uploadSensor, 'deltaTemp', 86400, 'seconds')[0]
     
    minSeries.push(minTemps)
    maxSeries.push(maxTemps)
    deltaSeries.push(delta)
     
    minSeries.save()
    maxSeries.save()
    deltaSeries.save()
