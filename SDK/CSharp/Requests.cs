/*
 * Copyright 2012 MicroStrain Inc. All Rights Reserved.
 *
 * Distributed under the Simplified BSD License.
 * See file license.txt
 *
 */

using System;
using System.Collections.Generic;
using System.Diagnostics;

using System.Web;
using System.Net;
using System.IO;


namespace SensorCloud
{
	/// <summary>
	/// Wrapper around HttpWebRequest to simplify the creation of http requests.
	/// It was specifically designed for interacting with web services.
	///
	/// The intention is for this class to be a generic http request, but it was built
	/// explicitly for sensorcloud, so only the options that are required for SensorCloud
	/// have been implemented. 
	/// </summary>
	public class Requests : IRequests
	{		
		/// <summary>
		///  Dictionary used exclusively for url parameters
		/// </summary>
		public class Params : Dictionary<String, String>
		{
			public String QueryString()
			{
				String s = "";
				foreach (var pair in this)
				{
					s += s.Length == 0 ? "?" : "&";
					s += HttpUtility.UrlEncode(pair.Key) + "=" + HttpUtility.UrlEncode(pair.Value);
				}
				return s;
			}
		}


		/// <summary>
		/// Dictionary used exclusively for http headers
		/// </summary>
		public class Headers : Dictionary<String, String> { }


		/// <summary>
		/// RequestOptions stores all the possible variables required to make an http request
		/// </summary>
		public class RequestOptions
		{
			private Params _queryParams;
			private Headers _headers;
			private byte[] _requestBody;

			public Headers Headers { get { return this._headers; } }
			public String QueryString { get { return this._queryParams.QueryString(); } }
			public byte[] RequestBody { get { return _requestBody; } }

			public RequestOptions()
			{
				this._queryParams = new Params();
				this._headers = new Headers();
				this._requestBody = null;
			}


			/// <summary>
			/// Add a query string param to the request options
			/// </summary>
			/// <param name="name"></param>
			/// <param name="value"></param>
			public void AddParam(String name, String value)
			{
				_queryParams.Add(name, value);
			}


			/// <summary>
			/// Add an http header to the request options
			/// </summary>
			/// <param name="name"></param>
			/// <param name="value"></param>
			public void AddHeader(String name, String value)
			{
				_headers.Add(name, value);
			}

			/*
			public void SetPayload(Stream requestBodyStream)
			{
				this._requestBody = requestBodyStream;
			}
		
			public void SetPayload(String requestBody)
			{
				this._requestBody = requestBody;		
			}
		*/

			/// <summary>
			/// Adds data that is sent as the body of a request
			/// </summary>
			/// <param name="requestBody"></param>
			public void SetRequestBody(byte[] requestBody)
			{
				this._requestBody = requestBody;
			}
		}



		/// <summary>
		/// An http request has a wide range of possible options that can be specified.
		/// RequestBuilder parameterizes each possible options as a method returning a RequestBuilder option
		/// allowing the chaining of request options.  The chaining allows us to eliminate the need for having an overloaded
		/// method that can handle any combination of desired options, and also results in a very readable self documented
		/// request.
		/// </summary>
		public class RequestBuilder : IRequestBuilder
		{
			private String _url;
			private RequestOptions _options;

			public RequestBuilder(String url)
			{
				this._url = url;
				this._options = new RequestOptions();
			}

			/// <summary>
			/// Add an http header to the request
			/// </summary>
			/// <param name="name"></param>
			/// <param name="value"></param>
			/// <returns></returns>
			public IRequestBuilder Header(String name, String value)
			{
				this._options.AddHeader(name, value);
				return this;
			}

			/// <summary>
			/// Set the content Type for the request's messageBody.
			/// This is a convenience method for setting the HTTP header "Content-Type".
			/// </summary>
			/// <param name="contentType"></param>
			/// <returns></returns>
			public IRequestBuilder ContentType(String contentType)
			{
				return Header("Content-Type", contentType);
			}

			/// <summary>
			/// specifies the content-type or types that we can handle in the response.
			/// This is a convenience method for seeting the HTTP header "Accept".
			/// </summary>
			/// <param name="acceptType"></param>
			/// <returns></returns>
			public IRequestBuilder Accept(String acceptType)
			{
				return Header("Accept", acceptType);
			}


			/// <summary>
			/// Add a query parameter to the request
			/// </summary>
			/// <param name="name"></param>
			/// <param name="value"></param>
			/// <returns></returns>
			public IRequestBuilder Param(String name, String value)
			{
				this._options.AddParam(name, value);
				return this;
			}

			/// <summary>
			/// Add a query parameter to the request for any object.  Uses the object's ToString to convert it to a string
			/// </summary>
			/// <param name="name"></param>
			/// <param name="value"></param>
			/// <returns></returns>
			public IRequestBuilder Param(String name, Object value)
			{
				return Param(name, value.ToString());
			}

			/// <summary>
			/// Add a message body to the request.
			/// </summary>
			/// <param name="requestBody"></param>
			/// <returns></returns>
			public IRequestBuilder Data(byte[] requestBody)
			{
				this._options.SetRequestBody(requestBody);
				return this;
			}

			/// <summary>
			/// Invoke the request that has been built using the GET verb
			/// </summary>
			/// <returns></returns>
			public IRequest Get()
			{
				return DoRequest("GET", this._url, this._options);
			}

			/// <summary>
			/// Invoke the request that has been built using the PUT verb
			/// </summary>
			/// <returns></returns>
			public IRequest Put()
			{
				return DoRequest("PUT", this._url, this._options);
			}

			/// <summary>
			/// Invoke the request that has been built using the POST verb
			/// </summary>
			/// <returns></returns>
			public IRequest Post()
			{
				return DoRequest("POST", this._url, this._options);
			}

			/// <summary>
			/// Invoke the request that has been built using the DELETE verb
			/// </summary>
			/// <returns></returns>
			public IRequest Delete()
			{
				//return new Request("DELETE", this._url, this._options);
				return DoRequest("DELETE", this._url, this._options);
			}

			protected virtual IRequest DoRequest(string method, string url, RequestOptions options)
			{
				return new Request(method, url, options);
			}
		}

		public class Request : IRequest
		{
			protected String _method;
			protected String _url;
			protected RequestOptions _options;


			private byte[] responseData;

			public HttpStatusCode ResponseCode { get; private set; }
			public String ResponseMessage { get; private set; }
			public String ContentType { get; private set; }

			public String Text
			{
				get
				{
					if (responseData == null) { return ""; }
					var encoding = new System.Text.UTF8Encoding();
					return encoding.GetString(responseData);
				}
			}


			public byte[] Raw { get { return responseData; } }


			public Request(String method, String url, RequestOptions options)
			{
				this._method = method;
				this._url = url;
				this._options = options;

				this.ResponseCode = 0;
				this.ResponseMessage = "";
				this.ContentType = "";
				this.responseData = null;

				DoRequest();
			}


			private void DoRequest()
			{
				//build url
				String q = _options.QueryString;
				String strUrl = this._url + q;

				var request = (HttpWebRequest)WebRequest.Create(strUrl);
				request.Method = this._method;

				//add all the headers to the request
				foreach (KeyValuePair<String, String> pair in _options.Headers)
				{
					var key = pair.Key.ToLowerInvariant();
					switch (key)
					{
						case "accept": request.Accept = pair.Value; break;
						case "content-type": request.ContentType = pair.Value; break;
						case "expect": request.Expect = pair.Value; break;
						case "host": request.Host = pair.Value; break;
						case "referer": request.Referer = pair.Value; break;
						case "transfer-encoding": request.TransferEncoding = pair.Value; break;
						case "user-agent": request.UserAgent = pair.Value; break;

						//TODO: These require actual date objects to be set, but we don't currently use these headers
						//case "if-modified-since": request.IfModifiedSince = pair.Value; break;
						//case "date": request.Date:

						default: request.Headers.Add(pair.Key, pair.Value); break;
					}
				}

				//send data to the server
				if (_options.RequestBody != null)
				{
					using (var stream = request.GetRequestStream())
					{
						stream.Write(_options.RequestBody, 0, _options.RequestBody.Length);
						stream.Close();
					}
				}

				try
				{
					using (var response = (HttpWebResponse)request.GetResponse())
					{
						this.ResponseCode = response.StatusCode;
						this.ResponseMessage = response.StatusDescription;
						this.ContentType = response.ContentType;

						using (var responseStream = response.GetResponseStream())
						using (var ms = new MemoryStream())
						{
							responseStream.CopyTo(ms);
							this.responseData = ms.ToArray();
						}
					}
				}
				catch (WebException e)
				{
					if (e.Response is HttpWebResponse)
					{
						var response = (HttpWebResponse)e.Response;
						this.ResponseCode = response.StatusCode;
						this.ResponseMessage = response.StatusDescription;
						this.ContentType = response.ContentType;

						using (var responseStream = response.GetResponseStream())
						{
							using (var ms = new MemoryStream())
							{
								responseStream.CopyTo(ms);
								this.responseData = ms.ToArray();
							}
						}
					}
					else
					{
						throw;
					}
				}
			}
		}

	
		/// <summary>
		/// Initiate the begining of a request using the url.  A request builder is returned allowing the request to be customized before 
		/// it is executed.
		/// </summary>
		/// <param name="url"></param>
		/// <returns></returns>
		public IRequestBuilder url(String url)
		{
			return new RequestBuilder(url);
		}
	}
}