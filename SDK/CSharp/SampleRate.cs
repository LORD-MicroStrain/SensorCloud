using System;
using System.Collections.Generic;
using System.Text;

using System.Diagnostics;

namespace SensorCloud
{

	public static class SampleRateExtensions
	{
		public static int ToXdr(this SampleRate.RateType type)
		{
			switch (type)
			{
				case SampleRate.RateType.Hertz: return 1;
				case SampleRate.RateType.Seconds: return 0;
			}
			throw new Exception("invalid enum type");
		}
	}

	/// <summary>
	/// Extend TimeSpan to allow Multipling and divinding TimeSpans with the Multiply and Divide methods.
	/// </summary>
	public static class TimeSpanExtensions
	{
		public static TimeSpan Multiply(this TimeSpan ts, int multiplier)
		{
			return new TimeSpan(ts.Ticks * multiplier);
		}

		public static TimeSpan Divide(this TimeSpan ts, int dividor)
		{
			return new TimeSpan(ts.Ticks / dividor);
		}
	}

	public class SampleRate : IComparable<SampleRate>
	{
		public enum RateType
		{
			Hertz,
			Seconds,
		}

		private readonly RateType _type;
		private readonly int _rate;

		public RateType Type{ get{return _type;} }
		public int Rate{ get{return _rate;}}
	
		

		// 
		/// <summary>
		/// Private class constructor.  Use the Factory functions, Hertz and Seconds, to create a samplerate. 
		/// </summary>
		/// <param name="type"></param>
		/// <param name="rate"></param>
		private SampleRate (RateType type, int rate)
		{
			if(rate == 1 && type == RateType.Seconds)
			{
				type = RateType.Hertz;
			}
		
			this._rate = rate;
			this._type = type;
		}
	
		/// <summary>
		/// Factory for creating a SampleRate in Hertz
		/// </summary>
		/// <param name="rate">rate in hertz</param>
		/// <returns>A new samplerate</returns>
		public static SampleRate Hertz(int rate)
		{
			return new SampleRate(RateType.Hertz, rate);		
		}
	
		/// <summary>
		/// Factory for creating a SampleRate in Seconds
		/// </summary>
		/// <param name="rate">rate in seconds</param>
		/// <returns>A new samplerate</returns>
		public static SampleRate Seconds(int rate)
		{
			return new SampleRate(RateType.Seconds, rate);		
		}

		/// <summary>
		/// Returns the sampling interval for the samplerate in nanoseconds
		/// </summary>
		/// <returns></returns>
		public long IntervalNanoseconds()
		{
			const long NANOSECONDS_PER_SECOND = 1000000000;

			if (Type == RateType.Hertz)
			{
				return NANOSECONDS_PER_SECOND/Rate;
			}
			else
			{
				Debug.Assert(Type == RateType.Seconds);
				return Rate * NANOSECONDS_PER_SECOND;
			}
		}

		/// <summary>
		/// Returns the sampling interval for the samplerate
		/// </summary>
		/// <returns></returns>
		public TimeSpan Interval()
		{
			return new TimeSpan(IntervalNanoseconds() / 100);
		}

		
		// Returns true if sample-rates represent the same sampling interval.
		// The sample rates '1 hertz' and '1 second' are considered equal
		public bool Equals(SampleRate smp)
		{
			if(object.Equals(smp, null)){ return false; }

			return this.CompareTo(smp) == 0;
		}

		public override bool Equals(object obj)
		{
			return Equals(obj as SampleRate);
		}

		//comparision operators
		public static bool operator < (SampleRate s1, SampleRate s2){ return s1.CompareTo(s2) <  0; }
		public static bool operator <=(SampleRate s1, SampleRate s2){ return s1.CompareTo(s2) <= 0; }
		public static bool operator ==(SampleRate s1, SampleRate s2){ return s1.CompareTo(s2) == 0; }
		public static bool operator !=(SampleRate s1, SampleRate s2){ return s1.CompareTo(s2) != 0; }
		public static bool operator >=(SampleRate s1, SampleRate s2){ return s1.CompareTo(s2) >= 0; }
		public static bool operator > (SampleRate s1, SampleRate s2){ return s1.CompareTo(s2) >  0; }
	
		public override int GetHashCode()
		{
			return 17 + this._rate.GetHashCode() + this._type.GetHashCode();
		}

		
				
		// Comparison of Samplerates.
		// A Faster rate is considered larger than a slower rate
		//
		// example:
		//    5Hz  >  1Hz
		//    1Hz  == 1Sec
		//    1Sec >  5Secs
		public int CompareTo(SampleRate other)
		{
			//an object is allways considered greater than a null
			if ((object)other == null) { return 1; }

			var delta = IntervalNanoseconds() - other.IntervalNanoseconds();

			//we need to ivert the result of delta, a smaller interval means a faster samplerate
			if (delta < 0) { return 1; }
			if (delta > 0) { return -1; }

			Debug.Assert(delta == 0);
			return 0;
		}
	
		public override String ToString()
		{
			return Rate + "-" + Type.ToString();
		}

	}
}
