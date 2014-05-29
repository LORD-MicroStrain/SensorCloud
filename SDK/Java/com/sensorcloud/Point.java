/*
 * Copyright 2012 MicroStrain Inc. All Rights Reserved.
 *
 * Distributed under the Simplified BSD License.
 * See file license.txt
 *
 */

package com.sensorcloud;

import java.sql.Timestamp;


/**
 * A <b>Point</b> is a single point of data on SensorCloud. Each <b>Point</b> contains a UTC timestamp in nanoseconds
 * and a float value.
 * 
 *
 */
public class Point
{
	private long timestamp;
	private float value;
	
	/**
	 * Create a data point for a time-series consisting of a timestamp and a value where the timestamp is a unix timestamp in nanoseoncds.
	 * 
	 * @param timestamp - Timestamp for the data-point as the number of nanoseconds since Jan 1, 1970 UTC
	 * @param value - value of the data-point
	 * 
	 * @throws IllegalArgumentException 
	 */
	public Point (long timestamp, float value)
	{
		if (timestamp < 0)
		{
			throw new IllegalArgumentException( "Timestamp must be a positive value" );
		}
		
		this.timestamp = timestamp;
		this.value = value;
	}
	
	/**
	 * Create a data point for a time-series consisting of a timestamp and a value using an sql.Timestamp object for the timestamp. 
	 * 
	 * @param timestamp - Timestamp for the data-point as an sql.Timestamp object
	 * @param value - value of the data-point
	 * 
	 */
	public Point (Timestamp timestamp, float value)
	{
		this.timestamp = timestamp.getTime()*1000000+timestamp.getNanos();
		this.value = value;
	}
	
		
	/**
	 * @return Returns the value for this point object.
	 */
	public float getValue()
	{
		return value;
	}
	
	/**
	 * @return Returns the Timestamp for this Point object.
	 */
	public Timestamp getTimestamp()
	{
		Timestamp ts = new Timestamp(this.timestamp/1000000);  //our timestamp is in nanoseconds, need to convert to millisecs
		ts.setNanos((int)(this.timestamp%1000000000));
		
		return ts;
	}
	
	/**
	 * @return Returns the timestamp as the number of nanoseconds since January 1, 1970 UTC for this Point object.
	 */
	public long getUnixTimestamp()
	{
		return timestamp;
	}
}

