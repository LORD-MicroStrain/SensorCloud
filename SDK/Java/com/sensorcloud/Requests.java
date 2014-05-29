/*
 * Copyright 2012 MicroStrain Inc. All Rights Reserved.
 *
 * Distributed under the Simplified BSD License.
 * See file license.txt
 *
 */

package com.sensorcloud;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.ProtocolException;
import java.net.URL;
import java.util.Hashtable;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

public class Requests
{
	public static class KeyValueStore 
	{
		private Hashtable<String, String> map;
		
		public KeyValueStore()
		{
			map = new Hashtable<String, String>();
		}
		
		@SuppressWarnings("unchecked")
		public KeyValueStore(Hashtable<String, String> hashtable)
		{
			map = (Hashtable<String, String>)hashtable.clone();
		}
		
		public void put(String key, String value)
		{
			map.put(key,  value);
		}
		
		public String get(String key)
		{
			return map.get(key);
		}
		
		public Hashtable<String, String> getMap()
		{
			return map;
		}
		
		public boolean isEmpty()
		{
			return map.isEmpty();
		}
		
		public int size()
		{
			return map.size();
		}
		
		public Set<Entry<String,String>> entrySet()
		{
			return map.entrySet();
		}
		
		
		@Override
		public boolean equals (Object obj)
		{
			if (!(obj instanceof KeyValueStore)) { return false; }
			return map.equals(((KeyValueStore)obj).map);
		}
		
		
		@Override
		public int hashCode()
		{
			return  map.hashCode();
		}	
	}
	
	public static class Params extends KeyValueStore
	{
		
		public String queryString()
		{
			StringBuilder s = new StringBuilder();
			for (Map.Entry<String, String> entry : entrySet())
			{
				s.append(s.length()==0?"?":"&");
				s.append(urlEncode(entry.getKey()));
				s.append("=");
				s.append(urlEncode(entry.getValue()));
			}
			
			return s.toString();
		}
		
		private String urlEncode(String s)
		{
			//TODO: need to escape the strings that we are placing on the url path
			//we should find an existing class that takes care of this instead of rolling our own
			return s;
		}
	}
	
	public static class Headers extends KeyValueStore{}
	
	public static class RequestOptions
	{
		private Params params;
		private Headers headers;
		private  byte[] payload;
	
		public RequestOptions()
		{
			this.params = new Params();
			this.headers = new Headers();
			this.payload = null;
		}
		
		public RequestOptions(Params params, Headers headers, byte[] data)
		{
			assert(params != null);
			assert(headers != null);
			
			this.params = params;
			this.headers = headers;
			this.payload = data;
		}
		
		public void addParam(String name, String value)
		{
			params.put(name, value);
		}
		
		public void addHeader(String name, String value)
		{
			headers.put(name, value);
		}
		
		public void setPayload(ByteArrayOutputStream payloadStream)
		{
			this.payload = payloadStream.toByteArray();
		}
		
		public void setPayload(String payload)
		{
			this.payload = payload.getBytes();		
		}
		
		public void setPayload(byte[] payload)
		{
			this.payload = payload;
		}
		
		public Params getParams(){return params;}
		public Headers getHeaders(){return headers;}
		
		public byte[] getData(){return payload;}
	}
	
	
	public static class RequestMaker
	{
		String url;
		RequestOptions options;
		
		public RequestMaker(String url)
		{
			this.url = url;
			this.options = new RequestOptions();
		}
		
		public RequestMaker header(String name, String value)
		{
			this.options.addHeader(name, value);
			return this;
		}
		
		public RequestMaker contentType(String contentType)
		{
			return header("Content-Type", contentType);
		}
		
		public RequestMaker accept(String acceptType)
		{
			return header("Accept", acceptType);
		}
		
		
		public RequestMaker param(String name, String value)
		{
			this.options.addParam(name, value);
			return this;
		}
		
		public RequestMaker data(ByteArrayOutputStream payload)
		{
			this.options.setPayload(payload);
			return this;
		}
		
		public Request get() throws IOException 
		{
			return new Request("GET", this.url, this.options);
		}
		
		public Request put() throws IOException 
		{
			return new Request("PUT", this.url, this.options);
		}
		
		public Request post() throws IOException 
		{
			return new Request("POST", this.url, this.options);
		}
		
		public Request delete() throws IOException 
		{
			return new Request("DELETE", this.url, this.options);
		}
	}
	
	
	public static class Request
	{
		private String method;
		private String url;
		private RequestOptions options;
		
		private int responseCode;
		private String responseMessage;
			
		private InputStream responseStream; 
		
		public Request(String method, String url, Params params, Headers headers, byte[] data) throws IOException
		{
			assert(params != null);
			assert(headers != null);
			
			this.method = method;
			this.url = url;
			this.options = new RequestOptions(params, headers, data);
			
			this.responseCode = 0;
			this.responseMessage = "";
			this.responseStream = null;
			
			doRequest();
		}
		
		public Request(String method,String url, RequestOptions options) throws IOException
		{
			this.method = method;
			this.url = url;
			this.options = options;
			
			this.responseCode = 0;
			this.responseMessage = "";
			this.responseStream = null;
			
			doRequest();
		}
		
		public int getResponseCode()
		{
			return this.responseCode;
		}
		
		public String getResponseMessage()
		{
			return this.responseMessage;
		}
		
		public InputStream getResponseStream()
		{
			return this.responseStream;
		}
		
		public String getResponseData() throws IOException
		{
			return new String(this.getRawResponseData());
		}
		
		public byte[] getRawResponseData() throws IOException
		{
			if(this.responseStream == null)
			{
				return null;
			}
			
			ByteArrayOutputStream os = new ByteArrayOutputStream();
				
			byte [] buf = new byte [1024];		
			int len;
			while((len = this.responseStream.read(buf)) > 0)
			{
				os.write(buf, 0, len);
			}		
			os.flush();
						
			return os.toByteArray();	
		}
		
		
		private void doRequest() throws IOException
		{
			//possible exception - UnknownHostException, MalformedURLException
			
			
			//build url
			String q = options.getParams().queryString();
			String strUrl = this.url + q;
			
			URL url = new URL(strUrl);
			
			HttpURLConnection connection = (HttpURLConnection) url.openConnection();
			
			try
			{
				connection.setRequestMethod(this.method);
			}
			catch (ProtocolException e)
			{
				//Should never happen. user never sets method directly.
				assert(false);
			}
			
			//add all the headers to the request
			for (Map.Entry<String, String> entry : options.getHeaders().entrySet())
			{
				connection.setRequestProperty(entry.getKey(), entry.getValue());
			}
			
			//send data to the server
			if(options.getData() != null)
			{
				connection.setDoOutput(true);
				OutputStream os = connection.getOutputStream();
				os.write(options.getData());
			}	
		
			this.responseCode = connection.getResponseCode();
			this.responseMessage = connection.getResponseMessage();
			
			// depending on the status code, the response will sometimes be in the error stream
			 this.responseStream = connection.getErrorStream();
			if(this.responseStream == null)
			{
				//call getInputStream will raise an exception with a 404,
				 this.responseStream = connection.getInputStream();
			}
		}
	}
	
	public static RequestMaker url(String url)
	{
		return new RequestMaker(url);
	}
}
