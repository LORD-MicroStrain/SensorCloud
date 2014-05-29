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
import java.net.HttpURLConnection;
import java.util.List;

import com.sensorcloud.Requests.Request;


public class Device
{
	private String authServer;
	private String deviceId;
	private String key;
	
	private String apiServer;
	private String authToken;
	
	/**
	 * @param deviceId  this is the unique ID for a particular device on SensorCloud
	 * @param key  the key generated for API access to this device.    
	 */
	public Device(String deviceId, String key)
	{
		final String DEFAULT_AUTH_SERVER = "https://sensorcloud.microstrain.com";
		
		this.authServer = DEFAULT_AUTH_SERVER;
		this.deviceId = deviceId;
		this.key = key;
	}
	
	/**
	 * @param deviceId  this is the unique ID for a particular device on SensorCloud
	 * @param key  the key generated for API access to this device.    
	 * @param authServer - custom auth-server to authenticate with.
	 */
	public Device(String deviceId, String key, String authServer)
	{
		this.authServer = authServer;
		this.deviceId = deviceId;
		this.key = key;
	}
		
	
	/**
	 * Authenticates using the key provided at construction.  authenticate must be called before
	 * any requests can be sent to SensorCloud.
	 * @throws Exception
	 */
	public void authenticate() throws Exception
	{
		try
		{
			//determine protocol from the auth server 
			final String PROTOCOL = authServer.startsWith("http://") ? "http://" : "https://";
			
			String url = authServer+"/SensorCloud/devices/"+deviceId+"/authenticate/";
			Request request = Requests.url(url)
		                              .param("version", "1")
		                              .param("key", this.key)
		                              .accept("application/xdr")
		                              .get();
			
			// check the response code for success
			if(request.getResponseCode() != HttpURLConnection.HTTP_OK)
			{		
				throw new SensorCloudException.AuthenticationError(request.getResponseData());
			}
			
			// Extract the authentication token and server from the response
			XDRInStream xdrStream = new XDRInStream(request.getResponseStream());
			authToken = xdrStream.readString();
			apiServer = PROTOCOL + xdrStream.readString();
		}
		//wrap exceptions in a SensorCloudException
		catch(IOException e)
		{
			throw new SensorCloudException("authenticate failed.", e);
		}
		
	}
	
	
	/**
	 * Determine if a sensor exists for this Device.
	 * @param sensorName
	 * @return true if the sensor exists.
	 * @throws SensorCloudException
	 */
	public boolean doesSensorExist(String sensorName) throws SensorCloudException
	{
		try
		{
			String url = apiServer + "/SensorCloud/devices/"+ deviceId + "/sensors/" + sensorName + "/";
			Request request = Requests.url(url)
	                .param("version", "1")
	                .param("auth_token", this.authToken)
	                .accept("application/xdr")
	                .get();
			
			// check the response code for success
			switch(request.getResponseCode())
			{
				case HttpURLConnection.HTTP_OK: return true;
				case HttpURLConnection.HTTP_NOT_FOUND: return false;
				default: throw new SensorCloudException("Unexpected response for get sensor. http status:" + request.getResponseCode() + " " + request.getResponseMessage() + "  info:" + request.getResponseData());
			}
		}
		//wrap exceptions in a SensorCloudException
		catch(IOException e)
		{
			throw new SensorCloudException("doesSensorExist failed.", e);
		}
	}

	
	/**
	 * Add a new sensor to the Device.
	 * 
	 * @param sensorName - Name that will be given to the sensor.  Once a sensor is created it's name cannot be changed.
	 *                     sensorName must be between 1 and 50 characters in length, and only contain characters in the set[A-Z,a-z,0-9,_]
	 * @throws SensorCloudException
	 */
	public void addSensor(String sensorName) throws SensorCloudException
	{
		addSensor(sensorName, "", "", "");
	}
	
	
	/**
	 * Add a new sensor to the Device.
	 * 
	 * @param sensorName - Name that will be given to the sensor.  Once a sensor is created it's name cannot be changed.
	 *                     sensorName must be between 1 and 50 characters in length, and only contain characters in the set[A-Z,a-z,0-9,_]
	 * @param label - User Friendly label for the sensor.  May be changed later.
	 *                label supports unicode, and must not be more than 50 bytes when encoded as UTF-8.
	 * @param type - Type of the sensor. May be changed later.
	 *               type supports unicode, and must not be more than 50 bytes when encoded as UTF-8.
	 * @param description - Description of the sensor.  May be changed later.
	 *                      description supports unicode, and must not be more than 1000 bytes when encoded as UTF-8.
	 * 
	 * @throws SensorCloudException
	 */
	public void addSensor(String sensorName, String label, String type, String description) throws SensorCloudException
	{
		try
		{
			ByteArrayOutputStream payload = new ByteArrayOutputStream();
			XDROutStream xdrStream = new XDROutStream(payload);
			
			final int VERSION = 1;
			xdrStream.writeInt(VERSION);
			xdrStream.writeString(type);
			xdrStream.writeString(label);
			xdrStream.writeString(description);
			
			String url = apiServer + "/SensorCloud/devices/"+ deviceId + "/sensors/" + sensorName + "/";
			Request request = Requests.url(url)
	                .param("version", "1")
	                .param("auth_token", this.authToken)
	                .contentType("application/xdr")
	                .data(payload)
	                .put();
			
			// check the response code for success
			if (request.getResponseCode() != HttpURLConnection.HTTP_CREATED)
			{
				throw new SensorCloudException("AddSensorFailed. http status:" + request.getResponseCode() + " " + request.getResponseMessage() + "  info:" + request.getResponseData());
			}
		}
		//wrap exceptions in a SensorCloudException
		catch(IOException e)
		{
			throw new SensorCloudException("AddSensor failed.", e);
		}
	}
	
	
	/**
	 * Determine if a channel for a specific sensor exits for the Device.
	 * 
	 * @param sensorName
	 * @param channelName
	 * 
	 * @return True if the channel exists
	 * 
	 * @throws SensorCloudException
	 */
	public boolean doesChannelExist(String sensorName, String channelName) throws SensorCloudException
	{
		try
		{
			//make a get request for channel attributes to determine if the channel exists
			String url = apiServer + "/SensorCloud/devices/"+ deviceId + "/sensors/" + sensorName + "/channels/" + channelName + "/attributes/";
			Request request = Requests.url(url)
	                .param("version", "1")
	                .param("auth_token", this.authToken)
	                .accept("application/xdr")
	                .get();
			
			// check the response code for success
			switch(request.getResponseCode())
			{
				case HttpURLConnection.HTTP_OK: return true;
				case HttpURLConnection.HTTP_NOT_FOUND: return false;
				default: throw new SensorCloudException("Unexpected response for get channel. http status:" + request.getResponseCode() + " " + request.getResponseMessage() + "  info:" + request.getResponseData());
			}
		}
		//wrap exceptions in a SensorCloudException
		catch(IOException e)
		{
			throw new SensorCloudException("doesChannelExist failed.", e);
		}
	}
	
	/**
	 * Add a new channel to the Device.
	 * 
	 * @param sensorname - Name of the sensor that the channel will be added to.
	 * @param channelName - Name of the channel to create. Once a channel is created it's name cannot be changed.
	 *                      The name must be between 1 and 50 characters in length, and only contain characters in the set[A-Z,a-z,0-9,_]
	 * @throws SensorCloudException
	 */
	public void addChannel(String sensorname, String channelName) throws SensorCloudException
	{
		addChannel(sensorname, channelName, "", "");
	}
	
	/**
	 * Add a new channel to the Device.
	 * 
	 * @param sensorname - Name of the sensor that the channel will be added to.
	 * @param channelName - Name of the channel to create. Once a channel is created it's name cannot be changed.
	 *                      The name must be between 1 and 50 characters in length, and only contain characters in the set[A-Z,a-z,0-9,_]
	 * @param label - User Friendly label for the channel.  May be changed later.
	 *                The label supports unicode and must not be more than 50 bytes when encoded as UTF-8.
	 * @param description - Description of the channel.  May be changed later.
	 *                      The description supports unicode, and must not be more than 1000 bytes when encoded as UTF-8.
	 * @throws SensorCloudException
	 */
	public void addChannel(String sensorname, String channelName, String label, String description) throws SensorCloudException
	{
		ByteArrayOutputStream payload = new ByteArrayOutputStream();
		XDROutStream xdrStream = new XDROutStream(payload);
		
		try
		{
			final int VERSION = 1;
			xdrStream.writeInt(VERSION);
			xdrStream.writeString(label);
			xdrStream.writeString(description);
			
			String url = apiServer + "/SensorCloud/devices/"+ deviceId + "/sensors/" + sensorname + "/channels/" + channelName + "/";
			Request request = Requests.url(url)
	                .param("version", "1")
	                .param("auth_token", this.authToken)
	                .contentType("application/xdr")
	                .data(payload)
	                .put();
			
			// check the response code for success
			if (request.getResponseCode() != HttpURLConnection.HTTP_CREATED)
			{
				throw new SensorCloudException("AddChannel failed. http status:" + request.getResponseCode() + " " + request.getResponseMessage() + "  info:" + request.getResponseData());
			}
		}
		//wrap exceptions in a SensorCloudException
		catch(IOException e)
		{
			throw new SensorCloudException("AddChannel failed.", e);
		}
	}
	
	/**
	 * Add time-series data to the channel.
	 * @param sensorname - sensor containing the channel to add data to.
	 * @param channelName - channel to add data to.
	 * @param sampleRate - sample-rate for points in data
	 * @param data - a list of points to add to the channel.  The points should be ordered and match the sample-rate provided.
	 * @throws SensorCloudException
	 */
	public void addTimeseriesData(String sensorname, String channelName, SampleRate sampleRate, List<Point> data) throws SensorCloudException
	{
		try
		{
			ByteArrayOutputStream payload = new ByteArrayOutputStream();
			XDROutStream xdrStream = new XDROutStream(payload);
			
			final int VERSION = 1;
			xdrStream.writeInt(VERSION);
			xdrStream.writeInt(sampleRate.getType().getXdr());
			xdrStream.writeInt(sampleRate.getRate());
			
			//Writing an array in XDR.  an array is always prefixed by the array length
			xdrStream.writeInt(data.size());
			for(Point p: data)
			{
				xdrStream.writeHyper(p.getUnixTimestamp());
				xdrStream.writeFloat(p.getValue());
			}
			
			String url = apiServer + "/SensorCloud/devices/"+ deviceId + "/sensors/" + sensorname + "/channels/" + channelName + "/streams/timeseries/data/";
			Request request = Requests.url(url)
	                .param("version", "1")
	                .param("auth_token", this.authToken)
	                .contentType("application/xdr")
	                .data(payload)
	                .put();
		
			// check the response code for success
			if (request.getResponseCode() != HttpURLConnection.HTTP_CREATED)
			{
				throw new SensorCloudException("AddChannel failed. http status:" + request.getResponseCode() + " " + request.getResponseMessage() + "  info:" + request.getResponseData());
			}
		}
		//wrap exceptions in a SensorCloudException
		catch(IOException e)
		{
			throw new SensorCloudException("AddData failed.", e);
		}
			 
	}
}
