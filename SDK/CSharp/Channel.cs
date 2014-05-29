using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Net;

namespace SensorCloud
{
	public class Channel
	{
		private IRequests _requests;
		private readonly string _sensorName;
		private readonly string _name;

		/// <summary>
		/// Name of the Sensor
		/// </summary>
		public string Name { get { return _name; } }


		// channel constructor.  This is internal because only a sensor should create a channel.
		internal Channel(string SensorName, string name, IRequests requests)
		{
			_sensorName = SensorName;
			_name = name;
			_requests = requests;
		}

		/// <summary>
		/// Add time-series data to the channel.
		/// </summary>
		/// <param name="sensorName">sensor containing the channel to add data to.</param>
		/// <param name="channelName">channel to add data to.</param>
		/// <param name="sampleRate">sample-rate for points in data</param>
		/// <param name="data">a list of points to add to the channel.
		/// <remarks>The points should be ordered and match the sample-rate provided.</remarks>
		/// </param>
		public void AddTimeSeriesData(SampleRate sampleRate, IEnumerable<Point> data)
		{
			var payload = new MemoryStream();
			var xdr = new XdrWriter(payload);

			const int VERSION = 1;
			xdr.WriteInt(VERSION);
			xdr.WriteInt(sampleRate.Type.ToXdr());
			xdr.WriteInt(sampleRate.Rate);

			//Writing an array in XDR.  an array is always prefixed by the array length
			xdr.WriteInt(data.Count());
			foreach (Point p in data)
			{
				xdr.WriteUnsingedHyper(p.UnixTimestamp);
				xdr.WriteFloat(p.Value);
			}

			string url = "/sensors/" + _sensorName + "/channels/" + this.Name + "/streams/timeseries/data/";
			var request = _requests.url(url)
								   .Param("version", "1")
								   .ContentType("application/xdr")
								   .Data(payload.ToArray())
								   .Put();

			// check the response code for success
			if (request.ResponseCode != HttpStatusCode.Created)
			{
				throw SensorCloudException.GenerateSensorCloudException(request, "AddTimeSeriesData failed.");
			}
		}

		/// <summary>
		/// Get's a TimeSeriesStream that can be used to read data from the channel
		/// </summary>
		/// <returns></returns>
		public TimeSeriesStream GetTimeSeriesStream()
		{
			return new TimeSeriesStream(_sensorName, this.Name, _requests);
		}
	}
}
