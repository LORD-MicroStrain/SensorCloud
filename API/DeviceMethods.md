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
