/*
 * Copyright 2012 MicroStrain Inc. All Rights Reserved.
 *
 * Distributed under the Simplified BSD License.
 * See file license.txt
 *
 */

using System;
using System.IO;
using System.Diagnostics;

namespace SensorCloud
{
	public class XdrWriter
	{
		private BinaryWriter _binaryWriter;
	
		public XdrWriter(Stream output)
		{
			_binaryWriter = new BinaryWriter(output);
		}

		//Write a 4-byte signed integer to the xdr stream
		public void WriteInt(int value)
		{
			WriteBigEndianBytes(BitConverter.GetBytes(value));
		}

		//write a 4-byte unsigned integer to the xdr stream
		public void WriteUnsignedInt(uint value)
		{
			WriteBigEndianBytes(BitConverter.GetBytes(value));
		}


		//write an 8-byte signed integer to the xdr stream
		public void WriteHyper(long value)
		{
			WriteBigEndianBytes(BitConverter.GetBytes(value));
		}

		//write an 8-byte signed integer to the xdr stream
		public void WriteUnsingedHyper(ulong value)
		{
			WriteBigEndianBytes(BitConverter.GetBytes(value));
		}


		// write a 4-byte single precision floating point value to the xdr stream
		public void WriteFloat(float value)
		{
			WriteBigEndianBytes(BitConverter.GetBytes(value));
		}

		// write an 8-byte double precision floating point value to the xdr stream
		public void ReadDouble(double value)
		{
			WriteBigEndianBytes(BitConverter.GetBytes(value));
		}

		// write opaque data to the xdr stream
		public void WriteOpaque(byte[] buff)
		{
			WriteInt(buff.Length);
			WriteBytes(buff);
		}

		// Write a string to the xdr stream.  The encoding will be UTF8.
		public void WriteString(string str)
		{
			var encoding = new System.Text.UTF8Encoding();
			byte[] buff = encoding.GetBytes(str);
			WriteOpaque(buff);
		}

		//Write a specified number of bytes to the xdr stream
		public void WriteBytes(byte[] bytes)
		{
			_binaryWriter.Write(bytes);

			//XDR is always alligned on 4 byte bondaries, so when an entity that has a length that is not an exact multiple of
			// 4 it must be 0 padded to end on a 4 byte boundary
			if (bytes.Length % 4 != 0)
			{
				var padBytes = 4 - (bytes.Length % 4);
				byte b = 0;
				for (int i = 0; i < padBytes; i++)
				{
					_binaryWriter.Write(b);
				}
			}
		}

		// writes bytes to a data stream encoded as big endian. If the current architectre doesn't match,
		// then the bytes will be reversed, so the byte order that we actually write to the stream will
		// be big endian. The bytes represneting numeric values that are passed in have been encoded using
		// the system's native byte order. 
		private void WriteBigEndianBytes(byte[] bytes)
		{
			Debug.Assert(bytes.Length == 4 || bytes.Length == 8); //all values that we currently read should be either 4 or 8 bytes
			
			if (BitConverter.IsLittleEndian)
			{
				Array.Reverse(bytes);
			}

			_binaryWriter.Write(bytes);
		}
	}
}
