using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.Serialization;

namespace SensorCloud
{
	public class SensorCloudException : Exception, ISerializable
	{
		public SensorCloudException() : base() { }
		public SensorCloudException(string message) : base(message) { }
		public SensorCloudException(string message, Exception innerException) : base(message, innerException) { }
		protected SensorCloudException(SerializationInfo info, StreamingContext context) : base(info, context) { }

		public static SensorCloudException GenerateSensorCloudException(IRequest request, string message)
		{
			return new SensorCloudException(message + " http status:" + request.ResponseCode + " " + request.ResponseMessage + "  info:" + request.Text);
		}
	}

	public class AuthenticationException : Exception, ISerializable
	{
		public AuthenticationException() : base("Authentication failed") { }
		public AuthenticationException(string message) : base(message) { }
		protected AuthenticationException(SerializationInfo info, StreamingContext context) : base(info, context) { }
	}

}
