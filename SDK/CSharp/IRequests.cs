using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;

namespace SensorCloud
{
	public interface IRequests
	{
		IRequestBuilder url(String url);
	}

	public interface IRequestBuilder
	{
		IRequestBuilder Header(String name, String value);
		IRequestBuilder ContentType(String contentType);
		IRequestBuilder Accept(String acceptType);
		IRequestBuilder Param(String name, String value);
		IRequestBuilder Param(String name, Object value);
		IRequestBuilder Data(byte[] requestBody);

		IRequest Get();
		IRequest Put();
		IRequest Post();
		IRequest Delete();
	}

	public interface IRequest
	{
		HttpStatusCode ResponseCode{ get;}
		String ResponseMessage { get; }
		String ContentType { get; }

		String Text { get; }
		byte[] Raw { get; }
	}
	
}

