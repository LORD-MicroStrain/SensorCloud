Channel Methods
===============

* [Add Channel Attribute](#add-channel-attribute)
* [Bulk Add Channel Attribute](#bulk-add-channel-attribute)
* [Get Channel Attributes](#get-channel-attributes)
* [Get Channel Attribute](#get-channel-attribute)
* [Delete Channel Attribute](#delete-channel-attribute)

Add Channel Attribute
---------------------
Add a custom attribute to the channel.  Each channel can have up to 25 custom attributes.  An attribute is of the type Text, Numeric, Boolean, or Custom.  A Text Attribute is a UTF-8 formatted string.  Numeric is a text representation of a number in either fixed point notation or scientific notation ^[-+]?[0-9]+((.[0-9]+)?([eE][0-9]+)?)?$ .  Boolean is a “false” or “true” string.  Custom is an arbitrary string of bytes.

### Request
Method | POST/PUT
-------|---------
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/attributes/<attribute_name>/?version=1&auth_token=<auth_token>``
Headers| Content-Type: application/xdr

Content: XDR
```D
enum		{TEXT=0, NUMBER=1, CUSTOM=2, BOOL=3 } attributeType

int    		version=1;	/* int, always 1, may change with future versions */
attributeType 	type;        	/* type of the attributes type */
opaque 		value<500>;  	/* byte array, attribute value, 0-500 bytes */
```

### Response
* ***Success***: 201 Attribute Set
* ***Errors***:
  * 404 Not Found - A channel name was used that doesn't exist
  * 400 Attribute Limit - Cannot create a new attribute because there are currently 25 existing attributes.  25 is the maximum allowed.

==========================
Bulk Add Channel Attribute
--------------------------
Add multiple custom attributes to the channel at one time.  Each channel can have up to 25 custom attributes.  An attribute is of the type Text, Numeric, Boolean, or Custom.  A Text Attribute is a UTF-8 formatted string.  Numeric is a text representation of a number in either fixed point notation or scientific notation ^[-+]?[0-9]+((.[0-9]+)?([eE][0-9]+)?)?$ .  Boolean is a “false” or “true” string.  Custom is an arbitrary string of bytes.

### Request
Method | POST/PUT
-------|---------
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/attributes/?version=1&auth_token=<auth_token>```
Headers| Content-Type: application/xdr

Content: XDR
```D
enum	{TEXT=0, NUMBER=1, CUSTOM=2, BOOL=3 } attributeType


MAX_ATTRIBUTES = 25;
MAX_NAME_LEN   = 50;
MAX_VALUE_LEN = 500;

struct
{
attributeType type;
string name<MAX_NAME_LEN>;
opaque value<MAX_VALUE_LEN>;
} attribute;

int	version=1;			/* always 1, may change with future versions */
attribute attributes<MAX_ATTRIBUTES>;	/* array of attributes to set */
```

### Response
* ***Success***: 201 Attribute Set
* ***Errors***:
  * 404 Not Found - A channel name was used that doesn't exist
  * 400 Attribute Limit - Cannot create a new attribute because there are currently 25 existing attributes.  25 is the maximum allowed.

======================
Get Channel Attributes
----------------------
Get all sensor attributes for a channel.  An attribute is of the type Text, Numeric, Boolean, or Custom.  A Text Attribute is a UTF-8 formatted string.  Numeric is a text representation of a number in either fixed point notation or scientific notation ^[-+]?[0-9]+((.[0-9]+)?([eE][0-9]+)?)?$ .  Boolean is a “false” or “true” string.  Custom is an arbitrary string of bytes.

### Request
Method | GET
-------|----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/attributes/?version=1&auth_token=<auth_token>```
Headers| Accept: application/xdr

### Response
* ***Success***: 200 OK
* ***Errors***:
  * 404 Not Found - A channel name was used that doesn't exist

Content: XDR

```D
enum	{ TEXT=0, NUMBER=1, CUSTOM=2, BOOL=3 } attributeType;

MAX_ATTRIBUTES = 25;
MAX_NAME_LEN   = 50;
MAX_VALUE_LEN = 500;

struct
{
attributeType type;
string        name<MAX_NAME_LEN>;
opaque        value<MAX_VALUE_LEN>;
} attribute;

int       version=1;                  /* always 1, may change with future versions */
attribute attributes<MAX_ATTRIBUTES>;
```

=====================
Get Channel Attribute
---------------------
Get a single attribute for a channel.  An attribute is of the type Text, Numeric, Boolean, or Custom.  A Text Attribute is a UTF-8 formatted string.  Numeric is a text representation of a number in either fixed point notation or scientific notation ^[-+]?[0-9]+((.[0-9]+)?([eE][0-9]+)?)?$ .  Boolean is a “false” or “true” string.  Custom is an arbitrary string of bytes.

### Request
Method | GET
-------|----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/attributes/<attribute_name>/?version=1&auth_token=<auth_token>```
Headers| Accept: application/xdr

### Response
* ***Success***: 200 OK
* ***Errors***:
  * 404 Not Found - A channel name was used that doesn't exist
  * 404 Not Found - A channel attribute name was used that doesn't exist

Content: XDR
```D
enum 	{ TEXT=0, NUMBER=1, CUSTOM=2, BOOL=3 } attributeType;

MAX_VALUE_LEN = 500;

int     	version=1;      	/* always 1, may change with future versions */
attributeType 	type;
opaque        	value<MAX_VALUE_LEN>;
```

========================
Delete Channel Attribute
------------------------
Delete a channel attribute.

### Request
Method | DELETE
-------|----
Url    | ```/SensorCloud/devices/<device_id>/sensors/<sensor_name>/channels/<channel_name>/attributes/<attribute_name>/?version=1&auth_token=<auth_token>```

### Response
* ***Success***: 204 Deleted
* ***Errors***:
  * 404 Not Found - A channel name was used that doesn't exist
  * 404 Not Found - A channel attribute name was used that doesn't exist






