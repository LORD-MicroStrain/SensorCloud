/*
 * Copyright 2012 MicroStrain Inc. All Rights Reserved.
 *
 * Distributed under the Simplified BSD License.
 * See file license.txt
 *
 */

package com.sensorcloud;

import java.io.ByteArrayInputStream;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;

/**
 * 
 * Provides a wrapper for java's DataInputStream so parse data using XDR specifications.
 * 
 *
 */
public class XDRInStream
{
	private DataInputStream dataStream;
	private int bytesRead;	
		
	/**
	 * @param in  input stream to read data from
	 */
	public XDRInStream(InputStream in)
	{
		dataStream = new DataInputStream(in);
		bytesRead = 0;
	}
	
	public XDRInStream(byte[] data)
	{
		dataStream = new DataInputStream(new ByteArrayInputStream(data));
		bytesRead = 0;
	}
	
	
	/**
	 * Reads a 4 byte integer from the underlying stream
	 * 
	 * @return Parsed integer
	 *  
	 * @throws IOException
	 */
	public int readInt() throws IOException
	{
		return dataStream.readInt();
	}
	

	
	/**
	 * Reads an 8 byte value from the underlying stream.
	 * The Java Long data type is equivalent to the XDR Hyper.
	 * 
	 * @return Hyper value as a Long
	 * @throws IOException
	 */
	public long readHyper() throws IOException
	{
		return dataStream.readLong();
	}
	
	
	/**
	 * Reads a single point precision value from the underlying stream
	 * 
	 * @return Float value 
	 * 
	 * @throws IOException
	 */
	public float readFloat() throws IOException
	{
		return dataStream.readFloat();
	}
	
	
	/**
	 * Reads an variable length array of bytes from the underlying stream.  The length is encoded in the stream.
	 * 
	 * @return Byte array
	 * 
	 * @throws IOException
	 */
	public byte [] readOpaque() throws IOException
	{
		int count = readInt();
		return readBytes(count);
	}
	
	/**
	 * Read a string from the stream.  The encoding is assumed to be UTF8.
	 * 
	 * @return String
	 * 
	 * @throws IOException
	 */
	public String readString() throws IOException
	{	
		return new String(readOpaque(), "UTF8" );
	}
	
	/**
	 * Reads a specified number of bytes from the underlying stream
	 * 
	 * @param i  number of bytes to be read
	 * @return  Byte array
	 * 
	 * @throws IOException
	 */
	public byte [] readBytes (int count) throws IOException
	{
		bytesRead += count;
		byte [] bytes = new byte[count];
		dataStream.readFully(bytes);
		pad();
		return bytes;
	}
	
	/**
	 * Skips a specified number of bytes from the underlying stream
	 * 
	 * @param i  number of bytes to be skipped
	 * 
	 * @throws IOException
	 */
	public void skip (int count) throws IOException
	{
		bytesRead += count;
		dataStream.skipBytes(count);
		pad();
	}
	
	
	/**
	 *  skip bytes to get to the next 4 byte boundary
	 *  All XDR values are encoded on 4 byte boundaries.  When reading arbitrary
	 *  length data(string, opaque) the underlying storage is padded.
	 */
	private void pad() throws IOException
	{
		int off =  4 - bytesRead % 4;
		if (off != 4) {
			dataStream.skipBytes( off );
			bytesRead += off;
		}
	}
	
}
