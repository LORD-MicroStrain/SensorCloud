Data Stream Methods
===================

* [Get Data-Stream Info](#get-data-stream-info)
* [Get Sample Rate Info](#get-sample-rate-info)
* [Add Time-Series Data](#add-time-series-data)
* [Download Time-Series Data](#download-time-series-data)
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

====================
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

====================
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
sampleRate	dataSampleRate;
datapoint	datapoints<MAX_DATAPOINTS>;
```

### Response ###
* ***Success***: 201 Created
* ***Errors***:
  * 404 Not Found - A channel name was used that doesn't exist
  * 401 Quota - You have exceeded your upload quota

=========================
Download Time-Series Data
-------------------------
Download a single channel of time-series data in binary format.  This is the most efficient (both time and space) method to download data from SensorCloud.

By default all data-points from all sample rates will be included even if multiple sample rates exist in the time range. 

There are two optional parameters, showSampleRateBoundary and sampleRate, that can be used to customize the download behavior when the stream contains multiple sample-rates.

***showSampleRateBoundary***: (true|false default=false) - If set to true, each sample rate boundary will be delineated by a timestamp of zero, followed by sample-rate info, and then resume with time-stamped data-points.

***sampleRate***: (example hertz-23, seconds-100) -  When specified, only data points that where uploaded with the specified timestamp are returned.  This does not down-sample data.  It will only download data that had the exact sample-rate specified when uploaded. A listing of all the sample-rates for a channel can be obtained by calling “Get Sample Rate Info”.

### Request ###
Method | GET
-------|----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/streams/ timeseries/data/?version=1&auth_token=<auth_token>&starttime=<startTime>&endtime=<endtime>[&showSampleRateBoundary=<true|false>[&samplerate=<samplerate>]```
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

======================================
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
    float  		value;
} point;

/* returns a single point */
point  latest;
```

=============
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

===============
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
int	version=1;			/* always 1, may change with future versions */
string	storedUnit<MAX_NAME_LEN>;
string	preferredUnit<MAX_NAME_LEN>;
float	slope;
float	offset;
```

### Response ###
* ***Success***: 201 Unite Set
* ***Errors***:
  * 404 Not Found - Channel does not have a time-series stream
  * 400 Unit Limit - Cannot create a new unit because there are currently 10 existing units.  10 is the maximum allowed. 

===========
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
