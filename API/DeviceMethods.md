Device Methods
==============

Authenticate
------------
All access to a device is protected and can only be accessed by an authenticated request. To authenticate the user passes in the device’s auth key. If the auth key is valid for the device then an auth\_token (authentication token) will be returned that must used for all subsequent request for this device. Along with the auth\_token, the DNS server name for all other request is also returned.

The auth\_token will expire after 6 hours. Once a token expires, any attempt to use it will yield the error "401 Invalid Token". When you receive this error discard your current auth\_token and re-authenticate. Always make sure to keep the security key well protected. Anyone with this key will have full access to the device, including the ability to view and delete data.

####Alternate Authenication method

It is also possible to us e a SensorCloud account’s username and password to authenticate for a device that is owned by the supplied account. Each device can enable or disable this authentication option. It can be configured on the Permission page for a device in SensorCloud. The setting is “Allow Open Data API access using device owner’s credentials.”

###Request
* **Host**: sensorcloud.microstrain.com
* **Url**: ```/SensorCloud/devices/<device_id>/authenticate/?version=1&key=<auth_key>```
* **Url(alt)**: ```/SensorCloud/devices/<device_id>/authenticate/?version=1&username=<user>&password=<pwd>```
* **Method**: GET
* **Header**:
  * ```Accept: <application/xdr>```

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

Get Sensors
-----------
GetSensors returns a list of all the sensors for the device with basic channel information for each sensor.
Note: Host and auth_token are returned from the call to authenticate.

###Request
* **Host**: \*.sensorcloud.microstrain.com
* **Url**: ```/SensorCloud/devices/<device_id>/sensors/?version=1&auth_token=<auth_token>```
* **Method**: GET
* **Header**:
  * ```Accept: <application/xdr>```

###Response
* **Success**: 200 OK
* **Content**: XDR
```
```









