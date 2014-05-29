using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

using SensorCloud;


namespace DemoSensorCloudApp
{
	class Program
	{
		static void Main(string[] args)
		{
			System.Console.WriteLine("Connecting to SensorCloud");
			var device = new SensorCloud.Device("YOUR_DEVICE_ID", "YOUR_DEVICE_OPEN_API_KEY_HERE");
				
			string sensorName = "sensor1";
			string channelName = "ch1";

			Sensor sensor = null;
			if (device.HasSensor(sensorName))
			{
				System.Console.WriteLine("getting sensor " + sensorName);
				sensor = device.GetSensor(sensorName);
			}
			else
			{
				System.Console.WriteLine("Adding sensor " + sensorName);
				sensor = device.AddSensor(sensorName);
			}


			Channel channel = null;
			if (sensor.HasChannel(channelName))
			{
				System.Console.WriteLine("getting channel " + channelName);
				channel = sensor.GetChannel(channelName);
			}
			else
			{
				System.Console.WriteLine("Adding channel " + channelName);
				channel = sensor.AddChannel(channelName);
			}
				
			//create a 5000 point sine wave with a samplerate of 1 Hz, using a now as the starttime
			var data = new List<Point>();
			var timestamp = DateTime.Now;
			var samplerate = SampleRate.Hertz(1);
			TimeSpan interval = samplerate.Interval();
			for (int i = 0; i < 5000; i++)
			{
				timestamp += interval;

				//Generate a sine wave
				float value = (float)Math.Sin((timestamp.Ticks / interval.Ticks) * 0.1);

				data.Add(new Point(timestamp, value));
			}

			System.Console.Write("uploading " + data.Count+ " datapoins...");
			channel.AddTimeSeriesData(samplerate, data);
			System.Console.WriteLine("complete");

			System.Console.WriteLine("\npress any key to exit");
			System.Console.ReadKey();
		}

	}
}
