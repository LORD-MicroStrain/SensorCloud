using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;
using System.IO;

namespace SensorCloud
{
	public class Sensor
	{
		private IRequests _requests;

		private readonly string _name;
		private string _label;
		private string _description;
		private string _sensorType;

		private bool _infoLoaded; 

		/// <summary>
		/// Name of the sensor
		/// </summary>
		public string Name { get { return _name; } }
		
		/// <summary>
		/// Get and set the label for the sensor
		/// </summary>
		public string Label
		{
			get
			{ 
				LoadFromSensorCloud();
				return _label;
			}
			set
			{
				SaveState(value, Description, SensorType);
				_label = value;
			}
		}

		/// <summary>
		/// Get and set the description for the sensor
		/// </summary>
		public string Description
		{
			get
			{
				LoadFromSensorCloud();
				return _description;
			}
			set
			{
				SaveState(Label, value, SensorType);
				_description = value;
			}
		}

		/// <summary>
		///  Get and set the type for the sensor
		/// </summary>
		public string SensorType
		{
			get
			{
				LoadFromSensorCloud();
				return _sensorType;
			}
			set
			{
				SaveState(Label, Description, value);
				_sensorType = value;
			}
		}

		// Save  type, label, and descritpion to SensorCloud
		private void  SaveState(string label, string description, string type)
		{
			var payload = new MemoryStream();
			var xdr = new XdrWriter(payload);

			const int VERSION = 1;
			xdr.WriteInt(VERSION);
			xdr.WriteString(type);
			xdr.WriteString(label);
			xdr.WriteString(description);
			

			var request = _requests.url("/sensors/" + this.Name + "/")
								  .Param("version", "1")
								  .Accept("application/xdr")
								  .ContentType("application/xdr")
								  .Data(payload.ToArray())
								  .Post();

			if (request.ResponseCode != HttpStatusCode.Created)
			{
				throw SensorCloudException.GenerateSensorCloudException(request, "Save Sensor state failed.");
			}
		}

		
		// Create's a sensor.  Olny a device should create a sensor.  That is why this is internal
		internal Sensor(string name, IRequests requests)
		{
			_name = name;
			_requests = requests;

			_infoLoaded = false;
		}


		/// <summary>
		/// Load info about this sensor from SensorCloud
		/// If this sensor doesn't exist then an exception will be thrown
		/// </summary>
		private void LoadFromSensorCloud()
		{
			if(_infoLoaded) { return; }

			//make a get request for channel attributes to determine if the channel exists
			var request = _requests.url("/sensors/" + this.Name + "/")
								  .Param("version", "1")
								  .Accept("application/xdr")
								  .Get();

			// check the response code for success
			if(request.ResponseCode == HttpStatusCode.OK)
			{
				
				var ms = new MemoryStream(request.Raw);
				var xdr = new XdrReader(ms);
				int version = xdr.ReadInt();
				if (version != 1)
				{
					throw new SensorCloudException("Unsupported xdr version");
				}

				string type = xdr.ReadString(1000);
				string label = xdr.ReadString(1000);  //a token is generally about 60 chars.  Limit the read to at most 1000 chars as a precation so in their is a protocol error we don't try to allocate lots of memory
				string descripiton = xdr.ReadString(1000);
				

				//Only if we get all the fields from xdr do we update this instance.  This prevents us from paritally updating the state of the instance.
				_label = label;
				_description = descripiton;
				_sensorType = type;
			}
			else
			{
				throw SensorCloudException.GenerateSensorCloudException(request, "Get Sensor Failed");
			}

			_infoLoaded = true;
		} 


		/// <summary>
		/// Determine if a channel for a specific sensor exits for the Device.
		/// </summary>
		/// <param name="sensorName"></param>
		/// <param name="channelName"></param>
		/// <returns>True if the channel exists</returns>
		/// <exception cref="SensorCloudException">Unexpected response from server.</exception>
		public bool HasChannel(string channelName)
		{
			//make a get request for channel attributes to determine if the channel exists
			String url = "/sensors/" + this.Name + "/channels/" + channelName + "/attributes/";
			var request = _requests.url(url)
								  .Param("version", "1")
								  .Accept("application/xdr")
								  .Get();

			// check the response code for success
			switch (request.ResponseCode)
			{
				case HttpStatusCode.OK: return true;
				case HttpStatusCode.NotFound: return false;
				default: throw SensorCloudException.GenerateSensorCloudException(request, "Unexpected response for HasChannel.");
			}
		}

		/// <summary>
		/// Get a channel from the Sensor.  If the channel doesn't exist this call will still succeed but when you try to access the CHannel you will get an error
		/// </summary>
		/// <param name="channelName"></param>
		/// <returns></returns>
		public Channel GetChannel(string channelName)
		{
			return new Channel(this.Name, channelName, _requests);
		}

		/// <summary>
		/// Add a new channel to the Sensor.
		/// </summary>
		/// <param name="channelName">Name of the channel to create. Once a channel is created it's name cannot be changed.
		/// <remarks>sensorName must be between 1 and 50 characters in length, and only contain characters in the set[A-Z,a-z,0-9,_]</remarks>
		/// </param>
		public Channel AddChannel(string channelName)
		{
			return AddChannel(channelName, "", "");
		}

		/// <summary>
		/// Add a new channel to the Device.
		/// </summary>
		/// <param name="channelName">Name of the channel to create. Once a channel is created it's name cannot be changed.
		/// <remarks>sensorName must be between 1 and 50 charcters in length, and only contain characters in the set[A-Z,a-z,0-9,_]</remarks>
		/// </param>
		/// <param name="label">User Friendly label for the channel.  May be changed later.
		/// <remarks>label supports unicode, and must not be more than 50 bytes when encoded as UTF-8.</remarks>
		/// </param>
		/// <param name="description">Description of the channel.  May be changed later.
		/// <remarks>description supports unicode, and must not be more than 1000 bytes when encoded as UTF-8.</remarks>
		/// </param>
		public Channel AddChannel(string channelName, string label, string description)
		{
			var payload = new MemoryStream();
			var xdr = new XdrWriter(payload);

			const int VERSION = 1;
			xdr.WriteInt(VERSION);
			xdr.WriteString(label);
			xdr.WriteString(description);

			string url = "/sensors/" + this.Name + "/channels/" + channelName + "/";
			var request = _requests.url(url)
								  .Param("version", "1")
								  .ContentType("application/xdr")
								  .Data(payload.ToArray())
								  .Put();

			// check the response code for success
			if (request.ResponseCode != HttpStatusCode.Created)
			{
				throw new SensorCloudException("AddChannel failed. http status:" + request.ResponseCode + " " + request.ResponseMessage + "  info:" + request.Text);
			}

			return new Channel(this.Name, channelName, _requests);
		}


		/// <summary>
		/// Delete a channel from the Sensor.  Deleteing a channel will delete all the data that is assosiated with the channel.
		/// </summary>
		/// <param name="channelName"></param>
		public void DeleteChannel(string channelName)
		{
			var request = _requests.url("/sensors/" + this.Name + "/channels/" + channelName + "/")
							       .Param("version", "1")
							       .Delete();

			if (request.ResponseCode != HttpStatusCode.NoContent)
			{
				throw SensorCloudException.GenerateSensorCloudException(request, "Delete channel Failed");
			}
		}
	}
}
