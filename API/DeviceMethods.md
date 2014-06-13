Device Methods
==============

* [Authenticate](#authenticate)
* [Get Sensors](#get-sensors)
* [Add Sensor](#add-sensor)
* [Update Sensor](#update-sensor)

Authenticate
------------

All access to a device is protected and can only be accessed by an authenticated request. To authenticate the user passes in the device’s auth key. If the auth key is valid for the device then an auth\_token (authentication token) will be returned that must used for all subsequent request for this device. Along with the auth\_token, the DNS server name for all other request is also returned.

The auth\_token will expire after 6 hours. Once a token expires, any attempt to use it will yield the error "401 Invalid Token". When you receive this error discard your current auth\_token and re-authenticate. Always make sure to keep the security key well protected. Anyone with this key will have full access to the device, including the ability to view and delete data.

#### Alternate Authenication method

It is also possible to us e a SensorCloud account’s username and password to authenticate for a device that is owned by the supplied account. Each device can enable or disable this authentication option. It can be configured on the Permission page for a device in SensorCloud. The setting is “Allow Open Data API access using device owner’s credentials.”

###Request
**Method**  | GET
------------|---------------------------
**Host**:   |sensorcloud.microstrain.com
**Url**     |```/SensorCloud/devices/<device_id>/authenticate/?version=1&key=<auth_key>```
**Url(alt)**| ```/SensorCloud/devices/<device_id>/authenticate/?version=1&username=<user>&password=<pwd>```
**Header**  | * ```Accept: <application/xdr>```

###Response
* **Success**: 200 OK
* **Errors**:
 * 401 Invalid Credentials: Username or password is not correct
* **Content**: XDR
```C
   string auth_token
   string server
   string reserved
```

===========
Get Sensors
-----------
GetSensors returns a list of all the sensors for the device with basic channel information for each sensor.
Note: Host and auth_token are returned from the call to authenticate.

###Request
Method    | GET
----------|-------------------
**Host**  | \*.sensorcloud.microstrain.com
**Url**   | ```/SensorCloud/devices/<device_id>/sensors/?version=1&auth_token=<auth_token>```
**Header**| * ```Accept: <application/xdr>```

###Response
* **Success**: 200 OK
* **Content**: XDR
```c
int x;
  struct	
  {
      string        	  storedUnit;
      string 		        preferredUnit;
      unsigned hyper  	timestamp;
      float  		slope;
      float  		offset;
  }unit;
  
  struct
  {
      inttotalBytes;           /* number of bytes contained within the structure.  Allows us to skip streams that we don't care about or understand */
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
  
  struct
  {
      string name<MAX_NAME_LEN>;
      string type<MAX_NAME_LEN>;
      string label<MAX_NAME_LEN>;
      string description<MAX_DESC_LEN>;
      channelInfo channels<>;
  } SensorInfo;
  
  int        version=1;       /* always 1, may change with future versions */
  SensorInfo sensors<>;       /* array of sensors */
```

=============
Add Sensor
-------------
Add a new sensor to a device.  A sensor groups related channels of data.  To create a sensor a unique name must be applied (unique relative to the device).  The name will be used to access the sensor after it is created.  A sensor’s name is immutable; once it is created it cannot be changed.  The sensor label is mutable, and can be updated at any time.  Generally the label is used at the presentation layer to indentify the sensor to the user, so the presentation of the sensor can be modified using the label.  The sensor name must be between 1 and 50 characters in the set [a-z,A-Z,0-9,-,_].

###Request
Method | PUT
-------|----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/?version=1&auth_token=<auth_token>```
Header | Content-Type: application/xdr
Content: XDR
```
int	   version=1;		    /* int, always 1, may change with future versions */
string	sensorType;        /* utf-8 string, sensor type name, 0-50 bytes */
string	sensorLabel;       /* utf-8 string, label for sensor, 0-50 bytes */
string	sensorDescription; /* utf-8 string, description for sensor, 0-1000 bytes */
```

###Response
* **Success**: 201 Created
* **Errors**:
   * 400 Invalid sensor name - Sensor name must be between 1 and 50 characters and only contain the following [a-z A-Z 0-9 _ -]
   * 400 Sensor exists - A Sensor with the same name already exists

=============
Update Sensor
-------------
Update an existing sensor.  This is similar to Add Sensor, except that the sensor referenced by ```<sensor_name>``` must already exist, and the http method POST is used instead of PUT.

###Request
Method | POST
-------|-----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/?version=1&auth_token=<auth_token>```
Header | Content-Type: application/xdr
Content: XDR
```
int	   version=1;		    /* int, always 1, may change with future versions */
string	sensorType;        /* utf-8 string, sensor type name, 0-50 bytes */
string	sensorLabel;       /* utf-8 string, label for sensor, 0-50 bytes */
string	sensorDescription; /* utf-8 string, description for sensor, 0-1000 bytes */
```

##Response
* **Success**: 201 Sensor Updated
* **Errors:
   * 404 Not Found - A sensor name was used that doesn't exist

===============
Get Sensor Info
---------------
Get sensor description, label, and type.

###Request
Method | GET
-------|----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/?version=1&auth_token=<auth_token>```
Header | Accept: application/xdr, text/xml

###Response
* ***Success***: 200 OK
* ***Errors***:
   * 404 Not Found - A sensor name was used that doesn't exist
* ***Content***:
   * XDR:         
                  
      ```c
      int           version=1;           /* always 1, may change with future versions */
      string        type;
      string        label;
      string        description;
      ```
   * XML
    
      ```xml
      <sensor version='1'>
         <type></type>
         <label></label>
         <description></description>
      </attribute>
      ```

=============
Delete Sensor
-------------
Delete a sensor and all information associated with the sensor.  All channels and all the data-streams and the underlying data must be deleted before this will succeed (refer to Delete Channel).  Use delete very carefully.  Once a sensor is deleted the action is immediate and permanent.  There is no way to recover a sensor or any of its data after it is deleted.

###Request
Method | DELETE
-------|-------
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/?version=1&auth_token=<auth_token>```

##Response
* ***Success***: 204 Deleted
* ***Errors***:
   * 404 Not Found - A sensor name was used that doesn't exist
   * 400 Bad Request – Cannot delete sensor, sensor currently has existing channels









