Data Stream Methods
===================

* [Get Data-Stream Info](#get-data-stream-info)
* [Get Sample Rate Info](#get-sample-rate-info)
* [Add Time-Series Data](#add-time-series-data)
* [Download Time-Series Data](#download-time-series-data)
* [Download CSV Data](#download-csv-data)
* [Download Latest Time-Series Data Point](#download-latest-time-series-data-point)
* [Get Unit Info](#get-unit-info)
* [Add or Update Unit](#add-or-update-unit)
* [Delete Unit](#delete-unit)

Get Data-Stream Info
--------------------
Get detailed info about a specific data-stream.  (Currently, time-series is the only stream type)

### Request ###
Method | GET
-------|----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/streams/ timeseries/?version=1&auth_token=<auth_token>```
Headers| Accept: application/xdr, text/xml

### Response ###
* ***Success***: 200 OK
* ***Errors***:
  * 404 Not Found - Channel does not have a time-series stream
* ***Content***:
  * XDR
    ```D
        struct
        {
          string			storedUnit<MAX_NAME_LEN>;
          string			preferredUnit<MAX_NAME_LEN>;
          unsigned hyper		timestamp;
          float			slope;
          float			offset;
        }unit;
        
        int		version=1;/* always 1, may change with future versions */
        unsigned hyper	startTime;
        unsigned hyper	endTime;
        unit		units<>;/* array of units for the stream */
    ```
        
  * XML
 
   ```XML
        <timeSeriesStream version=1>
           <startTime/>
           <endTime/>
           <units>
              <unit>
                 <storedUnit/>
                 <preferredUnit/>
                 <timestamp/>
                 <slope/>
                 <offset/>
              </unit>
           </units>
        </timeSeriesStream>
    ```

Get Sample Rate Info
--------------------
Get sample rate info for a time-series data stream.

### Request ###
Method | GET
-------|----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/streams/ timeseries/samplerates/?version=1&auth_token=<auth_token>```
Headers| Accept: application/xdr, text/xml

### Response ###
* ***Success***: 200 OK
* ***Errors*** :
  * 404 Not Found - A channel name was used that doesn't exist
  * 404 Not Found - A datastream was used that doesn't exist
* ***Content***:
  * XDR

    ```D
        enum{HERTZ=0, SECONDS=1} sampleRateType;
        
        struct 
        {
            sampleRateType type;
            int            rate;
        }sampleRate;
        
        struct
        {
            unsigned hyper	startTime;
            unsigned hyper 	endTime;       
            sampleRate 	partitionSampleRate;
        }partition;
        
        int        version=1;        /* always 1, may change with future versions */
        partition  partitions<>;     /* array of partitions */
    ```

  * XML

  ```XML
        <partitions version=1>
          <partition>
            <startTime/>
            <endTime/>
            <sampleRate>
              <type/>
              <rate/>
            </sampleRate>
          </partition>
        </partitions>
  ```

Add Time-Series Data
--------------------
Add time-series data for the specified channel.

Method | POST
-------|-----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/streams/ timeseries/data/?version=1&auth_token=<auth_token>```
Headers| Content-Type: application/xdr

Content: XDR
```D
    int MAX_DATAPOINTS = 100000;

    enum{HERTZ=1, SECONDS=0} sampleRateType;

    struct
    {
	sampleRateType type;
	int            rate;
    }sampleRate;

    struct
    {
	Unsigned hyper	timestamp;          	/* 8 byte unix time in nanoseconds (UTC) */
	float   	value;
    }datapoint;

    int         	version=1; 			/* always 1, may change with future versions */
    sampleRate	        dataSampleRate;
    datapoint	        datapoints<MAX_DATAPOINTS>;
```

### Response ###
* ***Success***: 201 Created
* ***Errors***:
  * 404 Not Found - A channel name was used that doesn't exist
  * 401 Quota - You have exceeded your upload quota

Download Time-Series Data
-------------------------
Download a single channel of time-series data in binary format.  This is the most efficient (both time and space) method to download data from SensorCloud.  This function will return a maximum of 100k data points.  Requests for a greater number of points should be split into multiple calls to this function.

By default all data-points from all sample rates will be included even if multiple sample rates exist in the time range. 

There are two optional parameters, showSampleRateBoundary and specificsamplerate, that can be used to customize the download behavior when the stream contains multiple sample-rates.

***showSampleRateBoundary***: (true|false default=false) - If set to true, each sample rate boundary will be delineated by a timestamp of zero, followed by sample-rate info, and then resume with time-stamped data-points.

***specificsamplerate***: (example hertz-23, seconds-100) -  When specified, only data points that where uploaded with the specified sample rate are returned.  This does not down-sample data.  It will only download data that had the exact sample-rate specified when uploaded. A listing of all the sample-rates for a channel can be obtained by calling “Get Sample Rate Info”.

***startTime, endTime***: (example 1388534400000000000) - A Unix timestamp in nanoseconds

### Request ###
Method | GET
-------|----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/streams/ timeseries/data/?version=1&auth_token=<auth_token>&starttime=<startTime>&endtime=<endtime>[&showSampleRateBoundary=<true false>][&specificsamplerate=<samplerate>]```
Headers| Accept: application/xdr

### Response ###
* ***Success***: 200 OK
* ***Errors***:
  * 404 Not Found - A channel name was used that doesn't exist
  * 404 Not Found - Channel does not have a time-series stream
* ***Content***:
  * XDR if showSampleRateBoundary is False

    ```D
        struct
        {
            unsigned hyper  	timestamp;
            float  		value;
        } point;
        
        /* returns a list of points */
        point  point-1;    
        point  point-2;
        point  point-3;
             .
             .
             .
        point  point-N;
    ```

  * XDR if showSampleRateBoundary is True

    ```D
        enum{HERTZ=0, SECONDS=1} sampleRateType;
        
        struct
        {
        	unsigned hyper	timestamp;
        	float  		value;
        }point;
        
        
        struct
        {
        	unsigned hyper timestamp;
        	sampleRateType	sampleRateType;
        	int		sampleRate;
        }sampleRate;
        
        
        /* list of data. including data points and sample rate boundary info each entry in data is either a point<> or a sampleRate<>
        The sampleRate type will have the first packed hyper value be 0.  */
        point||sampleRate data-1;
        point||sampleRate data-2;
        point||sampleRate data-3;
               .
               .
               .
        point||sampleRate data-N;
    ```

Download CSV Data
-----------------
Download sensor data in CSV format.  Downloading a CSV file allows for multiple sensors and channels in the same file.  The CSV format is supported by a wide range of applications and has become a de facto standard for the exchange of sensor data.  The CSV format does have some disadvantages.  It takes longer for SensorCloud to server CSV files than it does to serve the raw data-stream.  The resulting size of a CSV file is also larger than the same data in a binary format.

The first column of the CSV file is the timestamp which is used for all channels.  Not all channels will have data at all timestamps when multiple channels are selected.  An empty value is inserted for a channel that doesn&#39;t have a corresponding value for a specific timestamp.

* ***Parameters***:
  * selector_ts - list of sensor and channels to include in the download
```D
    <selector_ts>  ::= <sensor-list>
    <sensor-list>  ::= <sensor | ,<sensor-list>
    <sensor>       ::= sensor-name(<channel-list>)
    <channel-list> ::= <channel> | ,<channel-list>
    <channel>      ::= channel-name
```
    example = selector_ts=sensor_1(ch1,ch2),sensor_2(ch1,ch2,ch3),sensor_7(ch6)

  * startTime, endTime - A Unix timestamp in nanoseconds
```D
    example = 1388534400000000000
```
  
  * nan - Text to use to represent a NaN (Not a Number).  This parameter is optional.  Value specified as nanSymbol will be used to represent NaNs with the exception of "none", "excel", and "default" resulting in the mapping outlined below.  If nanSymbol is not provided then the default of "NaN" will be used.
```D
    "none" => ""
    "excel" -> "#N/A"
    "default" => "NaN"
```

  * timeFmt - Desired format of timestamps.  This parameter is optional.  Value must be "standard", "unix", or "relative".
```D
    "standard" - Standard readable format of month/day/year hour:minute:second.subseconds
      Example: 10/21/2015 15:30:30.000105800
    "unix" - Timestamp relative to Unix Epoc (Jan 1, 1970).  Timestamp value is nanoseconds since epoch.
    "relative" - All timestamps are relative to the first data point.  Timestamp value is in nanoseconds.
```

### Request ###
Method | GET
-------|----
Url    | ```/SensorCloud/devices/<device_id>/download/timeseries/csv/?selector_ts=<selector_ts>&startTime=<startTime>&endTime=<endTime>&nan=<nanSymbol>&timeFmt=<timeFmt>&version=1&auth_token=<auth_token>```
Headers| Accept: text/csv

### Response ###
* ***Success***: 200 OK
* ***Errors***:
  Note: no errors are raised for invalid sensors and/or channels.  The valid data will be sent and invalid channels will be ignored.
* ***Content***: CSV
```D
    Timestamp, <sn1>:<ch1>, <sn2>:<ch2>, ...
    Timestamp1, value_1, value_2, ...
    Timestamp2, value_1, value_2, ...
    ...
```

Download Latest Time-Series Data Point
--------------------------------------
Download a single channel’s latest time-series data point in binary format.  This is the most efficient (both time and space) method to retrieve the most recently uploaded point from SensorCloud.

### Request ###
Method | GET
-------|-----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/streams/ timeseries/data/latest/?version=1&auth_token=<auth_token>```
Headers| Accept: application/xdr

### Response ###
* ***Success***: 200 OK
* ***Errors***:
  * 404 Not Found - A channel name was used that doesn't exist
  * 404 Not Found - Channel does not have a time-series stream
* ***Content***: XDR

```D
    struct
    {
        unsigned hyper  	timestamp;
        float  		        value;
    } point;

    /* returns a single point */
    point  latest;
```

Get Unit Info
-------------
Get unit info for a time-series data stream.

### Request ###
Method | GET
-------|----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/streams/ timeseries/units/?version=1&auth_token=<auth_token>```
Headers| Accept: application/xdr, text/xml

### Response ###
* ***Success***: 200 OK
* ***Errors***:
  * 404 Not Found - A channel name was used that doesn't exist
  * 404 Not Found - A datastream was used that doesn't exist
* ***Content***:
  * XDR:

    ```D
        struct
        {
        	string		storedUnit<MAX_NAME_LEN>;
        	string		preferredUnit<MAX_NAME_LEN>;
        	unsigned hyper	timestamp;
        	float		slope;
        	float		offset;
        }unit;
        
        int	version=1;	/* always 1, may change with future versions */
        unit	units<>;	/* array of units for the stream */
    ```

  * XML:

    ```XML
        <units version=1>
           <unit>
              <storedUnit/>
              <preferredUnit/>
              <timestamp/>
              <slope/>
              <offset/>
           </unit>
        </units>
    ```

Add or Update Unit
---------------
Add a new unit to the time-series stream.  If an existing unit exists for the specified time then it will be updated.  Each time-series stream can have up to 10 distinct unit ranges set.  A unit range is identified by the time for which it is applicable.  A unit is in effect for all data until the start time for the next unit.  If there isn't a unit with a higher timestamp then the unit is applicable to the end of the data-stream.  It is recommended to use a timestamp of 0 for the first unit.  storedUnit should be set to the unit the data is stored with, and preferredUnit is the preferred display unit.  SensorCloud will automatically convert the data to the preferred unit in the viewer.

### Request ###
Method | POST/PUT
-------|---------
Url    | ```:/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/streams/ timeseries/units/<start_time>/?version=1&auth_token=<auth_token>```
Headers| Content-Type: application/xdr

Content: XDR
```D
    int	        version=1;	/* always 1, may change with future versions */
    string	storedUnit<MAX_NAME_LEN>;
    string	preferredUnit<MAX_NAME_LEN>;
    float	slope;
    float	offset;
```

### Response ###
* ***Success***: 201 Unit Set
* ***Errors***:
  * 404 Not Found - Channel does not have a time-series stream
  * 400 Unit Limit - Cannot create a new unit because there are currently 10 existing units.  10 is the maximum allowed. 

Delete Unit
-----------
Delete a unit for a specific time-series datastream.

### Request ###
Method | DELETE
-------|-------
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/streams/ timeseries/units/<start_time>/?version=1&auth_token=<auth_token>```

### Response ###
* ***Success***: 204 Deleted
* ***Errors***:
  * 404 Not Found - Channel does not have a time-series stream
  * 404 Not Found - A unit was specified that doesn’t exist
