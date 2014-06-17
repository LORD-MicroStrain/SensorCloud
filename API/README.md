API
===

* [Device Methods](DeviceMethods.md)
* [Sensor Methods](SensorMethods.md)
* [Channel Methods](ChannelMethods.md)
* [Data Stream Methods](DataStreamMethods.md)

Overview
--------
SensorCloud is a massively scalable data-store for sensor data.
SensorCloud provides a REST API to allow any device to upload data to SensorCloud.  The API is implemented as a web service using standard http request commands.  Using the web service model keeps the API Interface open and easily adapted to any platform.
HTTPS
All communication with SensorCloud is performed over https.  This ensures that all communication between SensorCloud and a device is over an encrypted communication channel.
Time Stamps
All timestamps used throughout the API are UNIX timestamps in nanosecond.  The timestamp values have nanosecond resolution but the accuracy of the timestamp is device dependent.  All timestamps are relative to UTC.
Data Format
All API requests use the XDR format for both request and response data.  We are also in the process of adding support for xml and json data formats for some of the requests.
Why XDR?
One of the primary goals of SensorCloud was to enable low powered devices to uploading large amounts of data.  The most efficient means to accomplish this is to use a binary data format.  XDR allows for a standardized mechanism for transmitting well-structured data in a machine independent manor, while minimizing the cost in time and space of encoding the data.
XML, CSV, JSON are all capable of communicating the same data as XDR, however they are all text based formats and therefore add computational overhead and require from 3 to 20 times as many bytes to transmit the same data.  Also because these formats are text based, this means that values must be converted from their native type to a text representation of the type.  For some data types there are potential ambiguities in the encodings.  This is particularly relevant with regard to the text encoding of floating point values.  While it is possible to reliably convert between a text and floating point value, there are many nuances that must be properly handled and there is no single definite standard convention that is used.  The actual precision and representations of special values such as +/- inf and NaNs vary between different implementations.

 


Concepts
--------
SensorCloud organizes data into a hierarchy of different components.  The Device is at the top level component.  A device contains Sensors.  Each Sensor may have one or more channels and each channel may have one or more datastreams.   A datastream is where the sensor data is actually stored.
Device   [1:N]    Sensor  [1:N]    Channel  [1:N]    Data-stream

### Device ###
A device represents a single point of aggregation.  A MicroStrain WSDA (Wireless Sensor Data Aggregator) is one example of a device.  A device may be a physical device that is collecting data from multiple sensors or a device could be a virtual device that is pulling data from multiple streams.  The device is a container for sensors.  

### Sensor ###
A Sensor represents a collection of related channels.  A sensor may be a physical sensor like a G-Link or 3DM-GX3-35, or it could be a virtual sensor like stock info.  Each sensor may contain one or more channels, and in turn each channel may contain one or more data-streams.  A Data-stream represents the data that the sensor sampled.  SensorCloud supports the concept of multiple stream types, but currently the only data-stream that is available is the time-series data-stream.  In the future additional data-stream types may be added to SensorCloud. 
