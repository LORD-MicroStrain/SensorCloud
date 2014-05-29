
using System;
using System.IO;
using System.Diagnostics;
using System.Runtime.Serialization;

namespace SensorCloud
{
	public class VariableLengthDataExceedsLimitException : Exception, ISerializable
	{
		public VariableLengthDataExceedsLimitException(int limit, int count) :
			base("The read request specified a maximum length of " + limit + " bytes, but the length encoded in the data is " + count + ".") { }
		protected VariableLengthDataExceedsLimitException(SerializationInfo info, StreamingContext context):base(info, context){}
	}


	class XdrReader
	{
		private BinaryReader _binaryReader;
	
		public XdrReader(Stream input)
		{
			_binaryReader = new BinaryReader(input);
		}

		public XdrReader(byte[] bytes)
		{
			_binaryReader = new BinaryReader(new MemoryStream(bytes));
		}

		//Read an 4-byte signed integer from the xdr stream
		public int ReadInt()
		{
			return BitConverter.ToInt32(ReadBigEndianBytes(4), 0);
		}

		//Read an 4-byte unsigned integer from the xdr stream
		public uint ReadUnsignedInt()
		{
			return BitConverter.ToUInt32(ReadBigEndianBytes(4), 0);
		}


		//Read an 8-byte signed integer from the xdr stream
		public long ReadHyper()
		{
			return BitConverter.ToInt64(ReadBigEndianBytes(8), 0);
		}

		//Read an 8-byte unsigned integer from the xdr stream
		public ulong ReadUnsingedHyper()
		{
			return BitConverter.ToUInt64(ReadBigEndianBytes(8), 0);
		}


		// read a 4-byte single precision floating point value from the xdr stream
		public float ReadFloat()
		{
			return BitConverter.ToSingle(ReadBigEndianBytes(4), 0);
		}

		// read an 8-byte double precision floating point value from the xdr stream
		public double ReadDouble()
		{
			return BitConverter.ToDouble(ReadBigEndianBytes(8), 0);
		}

		/// <summary>
		/// read an opaque block of bytes from the xdr stream 
		/// </summary>
		/// <param name="limit">If specified an exception is throw if the value is longer than this limit.</param>
		/// <returns></returns>
		public byte[] ReadOpaque(int limit = int.MaxValue)
		{
			int count = ReadInt();
			if (count > limit)
			{
				throw new VariableLengthDataExceedsLimitException(limit, count);
			}
			return ReadBytes(count);
		}

		// Read a string from the xdr stream.  The encoding is assumed to be UTF8.
		public string ReadString(int maxLength = int.MaxValue)
		{
			var encoding = new System.Text.UTF8Encoding();
			return encoding.GetString(ReadOpaque(maxLength));
		}

		//Read a specified number of bytes from the xdr stream
		public byte[] ReadBytes(int count)
		{
			byte[] bytes = ReadBytesExactly(count);

			//XDR is always alligned on 4 byte bondaries, so when an entity that has a length that is not an exact multiple of
			// 4 it will be 0 padded to be alligned on a 4 byte boundary
			if (count % 4 != 0)
			{
				var padBytes = 4 - (count % 4);
				ReadBytesExactly(padBytes);
			}

			return bytes;
		}

		// Reads bytes from an underlying data stream that is assumed to be big endian, and if the current architectre 
		// doesn't match, will reverse the byte order to allow the bytes to be decoded into numeric values using
		// the system's native byte order 
		private byte[] ReadBigEndianBytes(int size)
		{
			Debug.Assert(size == 4 || size == 8); //all values that we currently read should be either 4 or 8 bytes

			byte[] buff = ReadBytesExactly(size);
			
			if (BitConverter.IsLittleEndian)
			{
				Array.Reverse(buff);
			}

			return buff;
		}

		//will read the exact number of bytes requested.  If there are not enough bytes in the stream, then an EndOfStreamException is throw
		private byte[] ReadBytesExactly(int size)
		{
			byte[] buff = _binaryReader.ReadBytes(size);

			//if readBytes gets back less than the required bytes
			if (buff.Length != size)
			{
				throw new EndOfStreamException();
			}

			return buff;
			
		}
	}
}
