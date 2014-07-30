using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;
using System.IO;

namespace SensorCloud
{
	public class Device
	{
		private readonly string _deviceId;
		private IRequests _requests;

		/// <summary>
		/// Initializes a new instance of a SensorCloud Device for a specific account.
		/// </summary>
		/// <param name="deviceId">id for the Device's SensorCloud account</param>
		/// <param name="key">key required to access the Device</param>
		/// <param name="authServer">The authentication server to use.
		/// <remarks>default: https://sensorcloud.microstrain.com</remarks>
		/// </param>
		public Device(String deviceId, String key, String authServer = "https://sensorcloud.microstrain.com", IRequests requests = null)
		{
			//if a request was passed in use it.  If one wasn't passed in then we create a default RequestsFatory
			_requests = requests != null? requests : new SensorCloudRequests(deviceId, key, authServer);
			
			this._deviceId = deviceId;
		}

		/// <summary>
		/// Determine if a sensor exists for this Device.
		/// </summary>
		/// <param name="sensorName"></param>
		/// <returns>True if the sensor exists.</returns>
		public bool HasSensor(String sensorName)
		{
			var request = _requests.url("/sensors/" + sensorName + "/")
					.Param("version", "1")
					.Accept("application/xdr")
					.Get();
			
			// check the response code for success
			switch(request.ResponseCode)
			{
				case HttpStatusCode.OK: return true;
				case HttpStatusCode.NotFound: return false;
				default: throw SensorCloudException.GenerateSensorCloudException(request, "HasSensor failed");
			}
		}

	
		/// <summary>
		/// Add a new sensor to the Device.
		/// </summary>
		/// <param name="sensorName">Name that will be given to the sensor.  Once a sensor is created it's name cannot be changed.
		/// <remarks>sensorName must be between 1 and 50 characters in length, and only contain characters in the set[A-Z,a-z,0-9,_]</remarks>
		/// </param>
		public Sensor AddSensor(String sensorName)
		{
			return AddSensor(sensorName, "", "", "");
		}

		/// <summary>
		/// Add a new sensor to the Device.
		/// </summary>
		/// <param name="sensorName">Name that will be given to the sensor.  Once a sensor is created it's name cannot be changed.
		/// <remarks>sensorName must be between 1 and 50 characters in length, and only contain characters in the set[A-Z,a-z,0-9,_]</remarks>
		/// </param>
		/// <param name="label">User Friendly label for the sensor.  May be changed later.
		/// <remarks>label supports unicode, and must not be more than 50 bytes when encoded as UTF-8.</remarks>
		/// </param>
		/// <param name="type">Type of the sensor. May be changed later.
		/// <remarks>type supports unicode, and must not be more than 50 bytes when encoded as UTF-8.</remarks>
		/// </param>
		/// <param name="description">Description of the sensor.  May be changed later.
		/// <remarks>description supports unicode, and must not be more than 1000 bytes when encoded as UTF-8.</remarks>
		/// </param>
		public Sensor AddSensor(String sensorName, String label, String type, String description)
		{
			var payload = new MemoryStream();
			var xdr = new XdrWriter(payload);
			
			int VERSION = 1;
			xdr.WriteInt(VERSION);
			xdr.WriteString(type);
			xdr.WriteString(label);
			xdr.WriteString(description);
			
			var request = _requests.url("/sensors/" + sensorName + "/")
								   .Param("version", "1")
								   .ContentType("application/xdr")
								   .Data(payload.ToArray())
								   .Put();
			
			// check the response code for success
			if (request.ResponseCode != HttpStatusCode.Created)
			{
				throw SensorCloudException.GenerateSensorCloudException(request, "AddSensor Failed");
			}

			return new Sensor(sensorName, _requests);
		}

		/// <summary>
		/// Get an existing Sensor.  GetSensor will succeed even if the sensor doesn't exit.
		/// However,  you will get a SensorDoesntExist exception when you call a function on the returned
		/// Sensor object that communicates  with SensorCloud.
		/// </summary>
		/// <param name="sensorName"></param>
		/// <returns></returns>
		public Sensor GetSensor(string sensorName)
		{
			return new Sensor(sensorName, _requests);
		}

		/// <summary>
		/// Get a list of existing Sensors for this device.
		/// </summary>
		public List<Sensor> GetSensors()
		{
			List<Sensor> outputList = new List<Sensor>();
			//make a get request for channel attributes to determine if the channel exists
			var request = _requests.url("/sensors/")
														.Param("version", "1")
														.Accept("application/xdr")
														.Get();

			// check the response code for success
			if (request.ResponseCode == HttpStatusCode.OK)
			{
				var ms = new MemoryStream(request.Raw);
				var xdr = new XdrReader(ms);
				//The first value is the version.  We expect this to be 1
				int version = xdr.ReadInt();
				if (version != 1)
				{
					throw new SensorCloudException("Unsupported xdr version");
				}

				//The next value is an integer telling us how many sensors to unpack
				//Each sensor has its info packed a certain way, so this allows us to know how many sensors we must unpack
				int sensorCount = xdr.ReadInt();
				//loop through sensors
				for(var i=0; i < sensorCount; i++)
				{
					string sensorName = xdr.ReadString(1000);
					//for example's sake, I'm going to push a Sensor Object onto our output array
					//This object only needs the Sensor name, and will fetch the Sensor info on it's own
					//However, to get all sensor names we must still parse all of the stream.  You can modify 
					//this function to meet your own needs, and return a different set of information 
					//tailored to what you need.
					outputList.Add(new Sensor(sensorName, _requests));

					string sensortype = xdr.ReadString(1000);
					string sensorlabel = xdr.ReadString(1000);  //a token is generally about 60 chars.  Limit the read to at most 1000 chars as a precation so in their is a protocol error we don't try to allocate lots of memory
					string sensordescripiton = xdr.ReadString(1000);

					//the next value is the number of channels this sensor has
					int channelCount = xdr.ReadInt();
					//loop all channels
					for (var j=0; j < channelCount; j++)
					{
						string channelName = xdr.ReadString(1000);
						string channelLabel = xdr.ReadString(1000);
						string channelDescription = xdr.ReadString(1000);

						//This tells us how many datastreams the channel has
						//This should be one, as we only currently support TimeSeries, but could grow as more stream types are added
						int streamCount = xdr.ReadInt();
						//loop through streams
						for (var k=0; k < streamCount; k++)
						{
							//the first value in the stream is the type of stream.  We expect this to be TS_V1, meaning timeseries version 1
							string streamType = xdr.ReadString(1000);
							//the second value of a stream is the number of bytes that describes the stream.  
							//This is convenient as it allows us to just skip the stream if we are not interested in it.  
							//For this example's purpose, we are uninterested and will simply skip ahead in the xdr.  We do this by reading the number bytes, but doing anything
							//with the data
							int totalBytes = xdr.ReadInt();
							//just reading the bytes by previously parsed length advances the xdr reader forward in the data
							xdr.ReadBytes(totalBytes);
						}
					}
				}
				return outputList;
			}
			else
			{
				throw SensorCloudException.GenerateSensorCloudException(request, "Get Sensors Failed");
			}
		}


		/// <summary>
		/// Delete's a Sensor from the device.  All channels must be deleted before you can delete the Sensor.
		/// </summary>
		/// <param name="sensorName"></param>
		public void DeleteSensor(string sensorName)
		{
			var request = _requests.url("/sensors/" + sensorName + "/")
								   .Param("version", "1")
								   .Delete();

			if(request.ResponseCode != HttpStatusCode.NoContent)
			{
				throw SensorCloudException.GenerateSensorCloudException(request, "Delete Sensor Failed");
			}
		}
	}
}
