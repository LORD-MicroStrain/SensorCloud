using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Collections;
using System.Diagnostics;
using System.Net;
using System.IO;

namespace SensorCloud
{
	public class TimeSeriesStream : System.Collections.Generic.IEnumerable<Point>
	{
		private readonly string _sensorName;
		private readonly string _channelName;
		private readonly ulong _startTimestampNanoseconds;
		private readonly ulong _endTimestampNanoseconds;

		private readonly SampleRate _sampleRate;
		
		public ulong StartTimestampNanoseconds{get{return _startTimestampNanoseconds;}}
		public ulong EndTimestampNanoseconds{get{return _startTimestampNanoseconds;}}

		public DateTime StartTimestamp{get{return new DateTime((long)_startTimestampNanoseconds/100);}}
		public DateTime EndTimestamp{get{return new DateTime((long)_endTimestampNanoseconds/100);}}

		IRequests _requests;

		// In the implementing class
		IEnumerator IEnumerable.GetEnumerator()
		{
			return GetEnumerator();
		}

		public IEnumerator<Point> GetEnumerator()
		{
			//var _buffer = LoadBUffer
			ulong _currentTimestamp = _startTimestampNanoseconds;
			while (_currentTimestamp <= _endTimestampNanoseconds)
			{
				var data = this.DownloadData(_currentTimestamp, _endTimestampNanoseconds);
				foreach(Point p in data)
				{
					yield return p;
				}

				// if data is empty, then we,ve exaughstestd all the data in the range, if it's not 
				// then update the current timestamp
				if (data.Count > 0)
				{
					_currentTimestamp = data.Last().UnixTimestamp + 1;
				}
				else
				{
					break;
				}
			}
		}

        private static ulong convertToEpoch(DateTime value)
        {
            DateTime epochDT = new DateTime(1970, 1, 1, 0, 0, 0, System.DateTimeKind.Utc);
            ulong unixTimestamp = (ulong)(value - epochDT).TotalSeconds;
            ulong nanoTimestamp = unixTimestamp * 1000000000;
            return nanoTimestamp;
        }

		internal TimeSeriesStream(string sensorName, string channelName, IRequests requests)
			: this(sensorName, channelName, requests, null)
		{}

		internal TimeSeriesStream(string sensorName, string channelName, IRequests requests, DateTime start, DateTime end)
            : this(sensorName, channelName, requests, convertToEpoch(start), convertToEpoch(end))
		{}

		internal TimeSeriesStream(string sensorName, string channelName, IRequests requests, ulong start, ulong end)
			: this(sensorName, channelName, requests, start, end, null)
		{}

		internal TimeSeriesStream(string sensorName, string channelName, IRequests requests, DateTime start, DateTime end, SampleRate samplerate)
            : this(sensorName, channelName, requests, convertToEpoch(start), convertToEpoch(end))
		{}

		internal TimeSeriesStream(string sensorName, string channelName, IRequests requests, SampleRate sampleRate)
			: this(sensorName, channelName, requests, 0, ulong.MaxValue, sampleRate)
		{}


		internal TimeSeriesStream(string sensorName, string channelName, IRequests requests, ulong start, ulong end, SampleRate samplerate)
		{
			Debug.Assert(end >= start);

			_sensorName = sensorName;
			_channelName = channelName;
			_requests = requests;
			_sampleRate = samplerate;

			_startTimestampNanoseconds = start;
			_endTimestampNanoseconds = end;
		}


		public TimeSeriesStream Range(DateTime start, DateTime end)
		{
            return Range(convertToEpoch(start), convertToEpoch(end));
		}

		public TimeSeriesStream Range(ulong startTimestampNanoseconds, ulong endTimestampNanoseconds)
		{
			return new TimeSeriesStream(_sensorName, _channelName, _requests, startTimestampNanoseconds, endTimestampNanoseconds, _sampleRate);
		}


		private IList<Point> DownloadData(ulong startTime, ulong endTime)
		{
			//url: /sensors/<sensor_name>/channels/<channel_name>/streams/timeseries/data/
			// params:
			//    starttime (required)
			//    endtime  (required)
			//    showSampleRateBoundary (oiptional)
			//    samplerate (oiptional)

			string url = "/sensors/" + _sensorName + "/channels/" + this._channelName + "/streams/timeseries/data/";
			var request = _requests.url(url)
								   .Param("version", "1")
								   .Param("starttime", startTime)
								   .Param("endtime", endTime)
								   .Accept("application/xdr")
								   .Get();

			// check the response code for success
			if (request.ResponseCode == HttpStatusCode.NotFound)
			{
				//404 is an empty list
				return new List<Point>();
			}
			else if (request.ResponseCode != HttpStatusCode.OK)
			{
				//all other errors are exceptions
				throw SensorCloudException.GenerateSensorCloudException(request, "AddTimeSeriesData failed.");
			}

			var xdrReader = new XdrReader(request.Raw);
			
			var datapoints = new List<Point>();

			ulong timestamp;
			float value;

			try
			{
				// timeseries/data always returns a relativly small chunk of data less than 50,000 points so we can proccess it all at once.  We won't be given an infinite stream
				//however a futre enhancemnts could be to stat proccessing this stream as soon as we have any bytes avialable to the user, so they could be 
				//iterating over the data while it is still being downloaded.
				while (true)
				{
					timestamp = xdrReader.ReadUnsingedHyper();
					value = xdrReader.ReadFloat();

					datapoints.Add(new Point(timestamp, value));
				}
			}
			catch (EndOfStreamException)
			{}

			return datapoints;
		}
	}
}
