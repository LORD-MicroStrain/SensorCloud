using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;
using System.IO;

namespace SensorCloud
{
	/// <summary>
	/// SensorCloudRequest allows a user to make http request to a SensorCloud Server.
	/// SensorCLoudRequests handles the SensorCLoud authetication and reauthentication.
	/// </summary>
	class SensorCloudRequests : IRequests
	{
		private IRequests _requests;

		private readonly string _deviceId;
		private readonly string _deviceKey;
		private readonly string _authServer;

		public string DeviceId { get{return _deviceId;}}
		public string DeviceKey{ get{return _deviceKey;}}
		public string AuthServer { get { return _authServer; } }
		
		public string AuthToken { get; private set; }
		public string ApiServer { get; private set; }
		
		/// <summary>
		/// 
		/// </summary>
		/// <param name="deviceId"></param>
		/// <param name="deviceKey"></param>
		/// <param name="authServer"></param>
		/// <param name="requests"></param>
		public SensorCloudRequests(string deviceId, string deviceKey, string authServer, IRequests requests = null)
		{
			//if a request was passed in use it.  If one wasn't passed in then we create a default RequestsFatory
			_requests = requests != null? requests : new Requests();

			_deviceId = deviceId;
			_deviceKey = deviceKey;
			_authServer = authServer;

			AuthToken = "";
			ApiServer = "";

			Authenticate();
		}

		public void Authenticate()
		{
			//determine protocol from the auth server 
			String PROTOCOL = AuthServer.StartsWith("http://") ? "http://" : "https://";
			
			String url = AuthServer+"/SensorCloud/devices/" + DeviceId + "/authenticate/";
			
			var request = _requests.url(url)
		                          .Param("version", "1")
		                          .Param("key", DeviceKey)
		                          .Accept("application/xdr")
		                          .Get();
			
			// check the response code for success
			if(request.ResponseCode != HttpStatusCode.OK)
			{
				throw new AuthenticationException(request.Text);
			}
			

			// Extract the authentication token and server from the response
			var ms = new MemoryStream(request.Raw);
			var xdr = new XdrReader(ms);
			AuthToken = xdr.ReadString(1000);  //a token is generally about 60 chars.  Limit the read to at most 1000 chars as a precation so in their is a protocol error we don't try to allocate lots of memory
			ApiServer = PROTOCOL + xdr.ReadString(255);  //max length for a FQDN is 255 chars
		}

		public class AuthneticatedRequestBuilder : Requests.RequestBuilder
		{
			private SensorCloudRequests _requests;
			public AuthneticatedRequestBuilder(string url, SensorCloudRequests requests) : base(url)
			{
				_requests = requests;
			}


			protected override IRequest DoRequest(string method, string url, Requests.RequestOptions options)
			{

				string full_url = _requests.ApiServer + "/SensorCloud/devices/" + _requests.DeviceId + url;
				options.AddParam("auth_token", _requests.AuthToken);
				var request = base.DoRequest(method, full_url, options);
				
				//if we get an authentication error, reatuheticate, update the authToken and try to make the request again
				if(request.ResponseCode == System.Net.HttpStatusCode.Forbidden)
				{
					_requests.Authenticate();

					full_url = _requests.ApiServer + "/SensorCloud/devices/" + _requests.DeviceId + url;
					options.AddParam("auth_token", _requests.AuthToken);
					request = base.DoRequest(method, full_url, options);
				}

				return request;
			}
		}

		public IRequestBuilder url(String url)
		{
			return new AuthneticatedRequestBuilder(url, this);
		}
	}
}
