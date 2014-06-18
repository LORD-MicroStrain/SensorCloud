Sensor Methods
==============

* [Get Channels](#get-channels)
* [Add Channel](#add-channel)
* [Update Channel](#update-channel)
* [Delete Channel](#delete-channel)

Get Channels
------------
Get a list of all the channels for a sensor.

###Request
Method | GET
-------|-----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/?version=1&auth_token=<auth_token>```
Headers| <ul><li>Accept: application/xdr, txt/xml</li><li>Accept-Encoding: compress, gzip, identity</li></ul>

###Response
* ***Success***: 200 OK
* ***Content***:
  * XDR
        
        ```D
        struct
        {
            string 		      storedUnit;
            string 		      preferredUnit;
            unsigned hyper  timestamp;
            float  		      slope;
            float  		      offset;
        }unit;
        
        struct
        {
            inttotalBytes;  /* number of bytes contained within the structure.  Allows us to skip streams that we don't care about or understand */
            unit units<>;
        }timeSeriesInfo;
        
        union streamInfo switch(string type)
        {
            case “TS_V1”:  timeSeriesInfo data;    /* time series specific info */
            case “FFT_V1”: void;                   /* not implemented yet*/
        };
        
        struct
        {
            string name<MAX_NAME_LEN>;
            string label<MAX_NAME_LEN>;
            string description<MAX_DESC_LEN>;
            streamInfodataStreams<>;
        } channelInfo;
        
        
        int         version=1;       /* always 1, may change with future versions */
        channelInfo channels<>;     /* array of channels */
        ````
  * XML
        
        ```XML
        <channels version='1'>
          <channel>
            <name></name>
            <label></label>
            <description></description>
            <datastreams>
              <stream type=timeseries>
                <units>
                  <unit>
                    <storedUnit/>
                    <preferredUnit/>
                    <timestamp/>
                    <slope/>
                    <offset/>
                  </unit>
                </units>
              </stream>
            </datastreams>
          </channel>
        </channels>
        ```

===========
Add Channel
-----------
Add a channel to the current sensor.  The channel name must be between 1 and 50 characters in the set [-_a-z, A-Z, 0-9].

###Request
Method | PUT
-------|----
Url    | ```:SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/?version=1&auth_token=<auth_token>```
Headers| Content-Type: application/xdr
Content: XDR
```D
int    	version=1;          	/* int, always 1, may change with future versions */
string	channelLabel;        	/* utf-8 string, label for channel, 0-50 bytes */
string	channelDescription;  	/* utf-8 string, description for channel, 0-1000 bytes */
```

###Response
* ***Success***: 201 Channel Created
* Errors:
  * 400 Invalid Channel Name - Channel name must be between 1 and 50 characters and only contain the following [-_a-zA-Z0-9]
  * 400 Channel Exists - A channel with the same name already exists

==============
Update Channel
--------------
Updates an existing channel.  This is similar to Add Channel except that the channel referenced by <channel_name> must already exist, and the http method POST is used instead of PUT.

###Request
Method | POST
-------|-----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/?version=1&auth_token=<auth_token>```
Headers| Content-Type: application/xdr
Content: XDR
```D
int    	version=1;          	/* int, always 1, may change with future versions */
string	channelLabel;        	/* utf-8 string, label for channel, 0-50 bytes */
string	channelDescription;  	/* utf-8 string, description for channel, 0-1000 bytes */
```

###Response
* ***Success***: 201 Channel Updated
* Errors:
  * 400 Invalid Channel Name - Channel name must be between 1 and 50 characters and only contain the following [-_a-zA-Z0-9]
  * 400 Channel Exists - A channel with the same name already exists
  * 404 Not Found - A channel name was used that doesn't exist

==============
Delete Channel
--------------
Delete a Channel and all information associated with the channel.  All the data-streams and the underlying data will be deleted.  Use delete very carefully.  Once a channel is deleted the action is immediate and permanent.  There is no way to recover a channel or any of its data after it is deleted.

###Request
Method | DELETE
-------|-------
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/?version=1&auth_token=<auth_token>```

###Response
* ***Success***: 204 Deleted
* ***Errors***:
  * 404 Not Found - A channel name was used that doesn't exist











