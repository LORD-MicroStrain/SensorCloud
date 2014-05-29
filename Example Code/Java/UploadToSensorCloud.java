
import java.util.ArrayList;

import com.sensorcloud.Device;
import com.sensorcloud.Point;
import com.sensorcloud.SampleRate;


public class UploadToSensorCloud
{
	public static void main(String[] args)
	{		
		Device device = new Device("DEVICE_ID_HERE", "OPEN_API_DEVICE_KEY_HERE______5ee724186461ae20");
		
		try
		{
			device.authenticate();
			
			String sensorName = "sensor1";
			String channelName = "ch1";
			
			if(!device.doesSensorExist(sensorName))
			{
				System.out.println("adding Sensor "+ sensorName);
				device.addSensor(sensorName);
			}
			
			
			if(!device.doesChannelExist(sensorName, channelName))
			{
				System.out.println("adding Channel "+ sensorName + ":" + channelName);
				device.addChannel(sensorName, channelName);
			}
			
			//get current time in nanoseconds
			long startTime = System.currentTimeMillis()*1000000;
			final long SECOND = 1000000000;
			
			ArrayList<Point> points = new ArrayList<Point>();
			for(int i = 0; i < 200; i++)
			{
				points.add(new Point(startTime+SECOND*i, 100+i));
			}
			
			System.out.println("adding "+ points.size() + " points...");
			device.addTimeseriesData(sensorName, channelName,  SampleRate.Hertz(1), points);
			
			System.out.println("done");
		}
		catch (Exception e)
		{
			e.printStackTrace();
		}
	}
	

	
}



