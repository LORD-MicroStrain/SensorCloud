/*
 * Copyright 2012 MicroStrain Inc. All Rights Reserved.
 *
 * Distributed under the Simplified BSD License.
 * See file license.txt
 *
 */

using System;
using System.Collections.Generic;
using System.Text;

namespace SensorCloud
{
	/// <summary>
	/// Represents a single datapoint in a time-series. A point consists of a timestamp and a value.
	/// </summary>
	public class Point : IEquatable<Point>
	{
		private readonly ulong _timestamp;
		private readonly float _value;

		private const long WIN_FILE_TIME_TO_UNIX_EPOCH_OFFSET = 116444736000000000;


		///<summary>
		/// Represents the point's Value. This field is read-only.
		/// </summary>
		public float Value { get { return _value; } }
  
		/// <summary>
		/// Represents the point's timestamp as a DateTime. This field is read-only.
		/// <para></para>
		///  A Point's timestamp has a resolution of 1 nanosecond, however the DateTime object
		///  only has a resolution of 100 nanoseconds.  If you need nanosecond resolution you should
		///  use the UnixTimestamp field.
		/// </summary>
		public DateTime Timestamp
		{
			get
			{
				return new DateTime((long)(UnixTimestamp / 100) + 116444736000000000);
			}
		}

		/// <summary>
		/// Represents the point's timestamp as a Unix timestamp in nanosecond (number of nanoseconds since Jan 1, 1970 UTC).
		/// </summary>
		/// <remarks>
		/// This field is read-only.
		/// </remarks>
		public ulong UnixTimestamp { get { return _timestamp; } }


		/// <summary>
		///     Initializes a new instance of a Point specified by a unix timestamp and a value.
		/// </summary>
		/// <param name="timestamp">
		///     A timestamp expressed as a UTC Unix Timestamp(duration since Jan 1, 1970) in nanoseconds.
		/// </param>
		/// <param name="value">
		///     The floating point value that coresponds to the timestamp.
		/// </param>
		public Point(ulong timestamp, float value)
		{
			this._timestamp = timestamp;
			this._value = value;
		}

		/// <summary>
		/// Initializes a new instance of a Point specified by a DateTime timestamp and a value.
		/// </summary>
		/// <param name="timestamp">
		/// A DateTime timestamp.
		/// <para>
		/// Point can contain a timestamp with a resolution of 1 nanosecond, however the DateTime object
		/// only has a resolution of 100 nanoseconds.  If you need to create a Point with nanosecond resolution
		/// pass in the timestamp as a unixtimestamp in nanoseconds.
		/// </para>
		/// </param>
		/// <param name="value">The floating point value that coresponds to the timestamp.</param>
		public Point(DateTime timestamp, float value)
		{
			this._timestamp = ((ulong)(timestamp.ToFileTimeUtc() - WIN_FILE_TIME_TO_UNIX_EPOCH_OFFSET)) * 100; //*100 to convert from 100 nanoseconds to nanoseconds
			this._value = value;
		}

		public bool Equals(Point pt)
		{
			if (Object.ReferenceEquals(pt, null)){return false;}

			return (this.UnixTimestamp == pt.UnixTimestamp) &&
				   (this.Value == pt.Value);
		}
	}
}
