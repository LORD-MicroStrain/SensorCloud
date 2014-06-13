Device Methods
==============

Authenticate
------------
All access to a device is protected and can only be accessed by an authenticated request. To authenticate the user passes in the device’s auth key. If the auth key is valid for the device then an auth\_token (authentication token) will be returned that must used for all subsequent request for this device. Along with the auth\_token, the DNS server name for all other request is also returned.

The auth\_token will expire after 6 hours. Once a token expires, any attempt to use it will yield the error "401 Invalid Token". When you receive this error discard your current auth\_token and re-authenticate. Always make sure to keep the security key well protected. Anyone with this key will have full access to the device, including the ability to view and delete data.

####Alternate Authenication method

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
```
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
```
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









