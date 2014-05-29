/*
 * Copyright 2012 MicroStrain Inc. All Rights Reserved.
 *
 * Distributed under the Simplified BSD License.
 * See file license.txt
 *
 */


package com.sensorcloud;



/**
 * A sample rate on SensorCloud is measured in either hertz or seconds. Every point in a time series
 * has a corresponding <b>SampleRate</b>
 * 
 *
 */
public class SampleRate implements Comparable<SampleRate>
{
	/**
	 * enum for SampleRate types
	 *
	 */
	public enum RateType
	{
		HERTZ("hertz", 1),
		SECONDS("seconds", 0);
		
		private String str;
		private int xdr;
		
		private RateType(String str, int xdr)
		{
			this.str = str;
			this.xdr = xdr;
		}
		
		/**
		 * @return xdr representation of this RateType
		 */
		public int getXdr(){return xdr;}
		
		/**
		 * @return string name of this RateType
		 */
		public String toString(){return str;}
	}
	
	
	
	private final RateType type;
	private final int rate;
	
		
	/**
	 * Class constructor. The type should be supplied using the Factory methods.
	 * 
	 * @param rate  sample rate
	 * @param type  sample rate units
	 * 
	 */
	private SampleRate (RateType type, int rate)
	{
		if(rate == 1 && type == RateType.SECONDS)
		{
			type = RateType.HERTZ;
		}
		
		this.rate = rate;
		this.type = type;
	}
	
	
	/**
     * Factory for creating SampleRates in Hertz
     * @param rate in hertz
	 * @return SampleRate
	 */
	public static SampleRate Hertz(int rate)
	{
		return new SampleRate(RateType.HERTZ, rate);		
	}
	
	/**
	 * Factory for creating SampleRates in Seconds
	 * @param rate in seconds
	 * @return SampleRate
	 */
	public static SampleRate Seconds(int rate)
	{
		return new SampleRate(RateType.SECONDS, rate);		
	}
	
	
	/**
	 * @return sample-rate rate
	 */
	public int getRate()
	{
		return rate;
	}
	
	/**
	 * @return sample-rate type
	 */
	public RateType getType()
	{
		return type;
	}
	

	
	/**
	 * Returns true if sample-rates represent the same sampling interval.
	 * The sample rates '1 hertz' and '1 second' are considered equal
	 */
	@Override
	public boolean equals (Object obj)
	{
		if (!(obj instanceof SampleRate)) { return false; }
		
		return compareTo((SampleRate)obj) == 0;
	}
	
	
	@Override
	public int hashCode()
	{
		return 17 + this.rate + this.type.hashCode();
	}

	
	/**
	 * Comparison of Samplerates.
	 * A Faster rate is considered larger than a slower rate
	 * 
	 * example:
	 *    5Hz  >  1Hz
	 *    1Hz  == 1Sec
	 *    1Sec >  5Secs
	 *    
	 */
	
	@Override
	public int compareTo(SampleRate obj)
	{
		// 1Hz is the same as 1 second
		if(this.rate == 1 && obj.rate == 1){ return 0; }
		
		
		//Hertz is faster than seconds
		if(this.type == RateType.HERTZ && obj.type == RateType.SECONDS)
		{
			return 1;
		}
		
		//seconds is slower than Hertz
		if(this.type == RateType.SECONDS && obj.type == RateType.HERTZ)
		{
			return -1;
		}
		
		
		if(this.type == RateType.HERTZ)
		{
			assert(obj.type == RateType.HERTZ);
			
			return this.rate - obj.rate;
		}
		
		assert(this.type == RateType.SECONDS);
		assert(obj.type == RateType.SECONDS);
		
		return this.rate - obj.rate;
	}
	
	@Override
	public String toString()
	{
		return getRate() + "-" + getType().toString();
	}
}
