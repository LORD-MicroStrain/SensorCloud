import http.client
import xdrlib
import time
import math


class SensorCloudClient:
    """
    A client for interacting with the SensorCloud API.
    Handles authentication, sensor management, data upload, and data retrieval.
    """
    # Sample rate types
    HERTZ = 1
    SECONDS = 0

    def __init__(self, device_id, api_key, server="sensorcloud.microstrain.com"):
        """
        Initialize the SensorCloud client.

        Args:
            device_id (str): Your device ID
            api_key (str): Your API key for authentication
            server (str): Server address (default: SensorCloud server)
        """
        self.device_id = device_id
        self.api_key = api_key
        self.auth_server = server
        self.auth_token = None
        self.server = None
        self.is_authenticated = False

    def _get_connection(self, server=None):
        """
        Create and return an HTTPS connection to the specified server.

        Args:
            server (str): Server address (defaults to auth_server)

        Returns:
            http.client.HTTPSConnection: HTTPS connection object
        """
        target_server = server or self.auth_server
        return http.client.HTTPSConnection(target_server)

    def authenticate(self):
        """
        Authenticate with SensorCloud and obtain auth token and server address.
        Must be called before making other API requests.

        Returns:
            bool: True if authentication successful, False otherwise

        Raises:
            Exception: If authentication fails with details from server
        """
        conn = self._get_connection()
        headers = {"Accept": "application/xdr"}
        url = f"/SensorCloud/devices/{self.device_id}/authenticate/?version=1&key={self.api_key}"

        print("Authenticating with SensorCloud...")
        conn.request('GET', url=url, headers=headers)
        response = conn.getresponse()

        if response.status == http.client.OK:
            print("✓ Authentication successful")
            data = response.read()
            unpacker = xdrlib.Unpacker(data)
            self.auth_token = unpacker.unpack_string().decode('utf-8')
            self.server = unpacker.unpack_string().decode('utf-8')
            self.is_authenticated = True
            return True
        else:
            error_msg = response.read().decode('utf-8', errors='ignore')
            raise Exception(f"Authentication failed ({response.status}): {error_msg}")

    def _check_authenticated(self):
        """Verify that the client is authenticated before making requests."""
        if not self.is_authenticated:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

    def add_sensor(self, sensor_name, sensor_type="", sensor_label="", sensor_desc=""):
        """
        Add a sensor to your device.

        Args:
            sensor_name (str): Unique name for the sensor
            sensor_type (str): Type of sensor (optional)
            sensor_label (str): Display label for the sensor (optional)
            sensor_desc (str): Description of the sensor (optional)

        Returns:
            bool: True if sensor was created, False otherwise
        """
        self._check_authenticated()
        conn = self._get_connection(self.server)

        url = f"/SensorCloud/devices/{self.device_id}/sensors/{sensor_name}/?version=1&auth_token={self.auth_token}"
        headers = {"Content-type": "application/xdr"}

        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_string(sensor_type.encode('utf-8'))
        packer.pack_string(sensor_label.encode('utf-8'))
        packer.pack_string(sensor_desc.encode('utf-8'))
        data = packer.get_buffer()

        print(f"Adding sensor '{sensor_name}'...")
        conn.request('PUT', url=url, body=data, headers=headers)
        response = conn.getresponse()

        if response.status == http.client.CREATED:
            print(f"✓ Sensor '{sensor_name}' added successfully")
            return True
        else:
            error = response.read().decode('utf-8', errors='ignore')
            print(f"✗ Error adding sensor: {error}")
            return False

    def add_channel(self, sensor_name, channel_name, channel_label="", channel_desc=""):
        """
        Add a channel to a sensor.

        Args:
            sensor_name (str): Name of the sensor
            channel_name (str): Unique name for the channel
            channel_label (str): Display label for the channel (optional)
            channel_desc (str): Description of the channel (optional)

        Returns:
            bool: True if channel was created, False otherwise
        """
        self._check_authenticated()
        conn = self._get_connection(self.server)

        url = f"/SensorCloud/devices/{self.device_id}/sensors/{sensor_name}/channels/{channel_name}/?version=1&auth_token={self.auth_token}"
        headers = {"Content-type": "application/xdr"}

        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_string(channel_label.encode('utf-8'))
        packer.pack_string(channel_desc.encode('utf-8'))
        data = packer.get_buffer()

        print(f"Adding channel '{channel_name}' to sensor '{sensor_name}'...")
        conn.request('PUT', url=url, body=data, headers=headers)
        response = conn.getresponse()

        if response.status == http.client.CREATED:
            print(f"✓ Channel '{channel_name}' added successfully")
            return True
        else:
            error = response.read().decode('utf-8', errors='ignore')
            print(f"✗ Error adding channel: {error}")
            return False

    def upload_data(self, sensor_name, channel_name, data_points, sample_rate=10, sample_rate_type=None):
        """
        Upload time series data to a channel.

        Args:
            sensor_name (str): Name of the sensor
            channel_name (str): Name of the channel
            data_points (list): List of tuples (timestamp_ns, value) or list of values
                                If values only, timestamps are generated from current time
            sample_rate (int): Sample rate (default: 10)
            sample_rate_type (int): HERTZ or SECONDS (default: HERTZ)

        Returns:
            bool: True if data was uploaded successfully, False otherwise
        """
        self._check_authenticated()
        if sample_rate_type is None:
            sample_rate_type = self.HERTZ

        conn = self._get_connection(self.server)
        url = f"/SensorCloud/devices/{self.device_id}/sensors/{sensor_name}/channels/{channel_name}/streams/timeseries/data/?version=1&auth_token={self.auth_token}"

        packer = xdrlib.Packer()
        packer.pack_int(1)
        packer.pack_enum(sample_rate_type)
        packer.pack_int(sample_rate)
        packer.pack_int(len(data_points))

        # Handle different data point formats
        timestamp_ns = int(time.time() * 1000000000)
        sample_interval_ns = int(1e9 / sample_rate) if sample_rate_type == self.HERTZ else int(sample_rate * 1e9)

        print(f"Uploading {len(data_points)} data points...")
        for point in data_points:
            if isinstance(point, tuple) and len(point) == 2:
                ts, value = point
            else:
                ts, value = timestamp_ns, point
                timestamp_ns += sample_interval_ns

            packer.pack_hyper(ts)
            packer.pack_float(float(value))

        data = packer.get_buffer()
        headers = {"Content-type": "application/xdr"}

        conn.request('POST', url=url, body=data, headers=headers)
        response = conn.getresponse()

        if response.status == http.client.CREATED:
            print(f"✓ {len(data_points)} data points uploaded successfully")
            return True
        else:
            error = response.read().decode('utf-8', errors='ignore')
            print(f"✗ Error uploading data: {error}")
            return False

    def upload_sin_wave(self, sensor_name, channel_name, duration_minutes=10, frequency_hz=10, timestamp_ns=time.time_ns()):
        """
        Upload generated sine wave data (useful for testing).

        Args:
            sensor_name (str): Name of the sensor
            channel_name (str): Name of the channel
            duration_minutes (int): Duration of data to generate (default: 10)
            frequency_hz (int): Sample rate in Hz (default: 10)
            timestamp_ns (int): The NS timestamp of the first datapoint in the series (default: current timestamp)

        Returns:
            bool: True if data was uploaded successfully, False otherwise
        """
        total_points = duration_minutes * 60 * frequency_hz
        print(f"Generating {total_points} sine wave data points ({duration_minutes} minutes at {frequency_hz} Hz)...")

        sample_interval_ns = int(1e9 / frequency_hz)
        data_points = []

        for i in range(total_points):
            value = math.sin(timestamp_ns / 20000000000.0)
            data_points.append((timestamp_ns, value))
            timestamp_ns += sample_interval_ns

        return self.upload_data(sensor_name, channel_name, data_points, sample_rate=frequency_hz)

    def download_data_csv(self, sensor_name, channel_name, start_time, end_time):
        """
        Download time series data as CSV.

        Args:
            sensor_name (str): Name of the sensor
            channel_name (str): Name of the channel
            start_time (int): Start time (unix timestamp)
            end_time (int): End time (unix timestamp)

        Returns:
            str: CSV data as string, or None if download failed
        """
        self._check_authenticated()
        conn = self._get_connection(self.server)

        selector_ts = f"{sensor_name}({channel_name})"
        url = f"/SensorCloud/devices/{self.device_id}/download/timeseries/csv/?selector_ts={selector_ts}&startTime={start_time}&endTime={end_time}&nan=0&timeFmt=unix&version=1&auth_token={self.auth_token}"
        headers = {"Accept": "text/csv"}

        print(f"Downloading data from {start_time} to {end_time}...")
        begin = time.time()

        conn.request("GET", url=url, headers=headers)
        response = conn.getresponse()

        if response.status == http.client.OK:
            raw_data = response.read().decode('utf-8')
            elapsed = time.time() - begin
            print(f"✓ Download complete in {elapsed:.2f} seconds")
            return raw_data
        else:
            print(f"✗ Error downloading data: {response.status} {response.reason}")
            return None

    def download_data_xdr(self, sensor_name, channel_name, start_time, end_time):
        """
        Download time series data in XDR format.

        Args:
            sensor_name (str): Name of the sensor
            channel_name (str): Name of the channel
            start_time (int): Start time (unix timestamp)
            end_time (int): End time (unix timestamp)

        Returns:
            list: List of tuples (timestamp, value), or empty list if download failed
        """
        self._check_authenticated()
        conn = self._get_connection(self.server)

        url = f"/SensorCloud/devices/{self.device_id}/sensors/{sensor_name}/channels/{channel_name}/streams/timeseries/data/?version=1&auth_token={self.auth_token}&startTime={start_time}&endTime={end_time}"
        headers = {"Accept": "application/xdr"}

        print("Downloading data in XDR format...")
        conn.request("GET", url=url, headers=headers)
        response = conn.getresponse()

        data = []
        if response.status == http.client.OK:
            unpacker = xdrlib.Unpacker(response.read())
            while True:
                try:
                    timestamp = unpacker.unpack_uhyper()
                    value = unpacker.unpack_float()
                    data.append((timestamp, value))
                except Exception:
                    break
            print(f"✓ Downloaded {len(data)} data points")
            return data
        else:
            print(f"✗ Error downloading data: {response.status} {response.reason}")
            return data


if __name__ == "__main__":
    device_id = "" # REPLACE WITH YOUR DEVICE ID
    key = "" # REPLACE WITH YOUR API KEY

    # Initialize client
    client = SensorCloudClient(device_id=device_id, api_key=key)

    try:
        # Authenticate
        client.authenticate()

        # Add sensor S1 to your device
        client.add_sensor("S1")

        # Add channel C1 to sensor S1
        client.add_channel("S1", "C1")

        # Get start and end timestamps for the last 10 minutes
        end_time = int(time.time_ns())
        start_time = end_time - (10 * 60000000000)  # Last 10 minutes

        # Upload sine wave test data on channel C1 of sensor S1
        client.upload_sin_wave("S1", "C1", duration_minutes=10, frequency_hz=10, timestamp_ns=start_time)

        # Download data as a CSV (slower, but is pre-formatted)
        csv_data = client.download_data_csv(sensor_name="S1", channel_name="C1", start_time=start_time, end_time=end_time)

        # Download data in XDR format (faster, but requires more post-processing)
        xdr_data = client.download_data_xdr(sensor_name="S1", channel_name="C1", start_time=start_time, end_time=end_time)

        if csv_data:
            # CSV data comes out as a single string, so let's process it
            # Split csv into separate lines so it's one point per line
            csv_data = csv_data.split('\n')
            print("\n---Downloaded CSV data---")
            print("Points downloaded: " + str(len(csv_data) - 1)) # Subtract 1 to avoid counting the header

            # Note that csv data is already a string, if you want the timestamp or value separately,
            # you'll have to split the string based on the location of the comma
            print("First point: " + csv_data[1]) # Again, skip over index 0 which is the header line
            print("Last point: " + csv_data[-1])

        if xdr_data:
            # This is a list of tuples, so no header to discard, the length is the number of data points
            print("\n---Downloaded XDR data---")
            print("Points downloaded: " + str(len(xdr_data)))

            # Note that the tuples are in (timestamp, value) format, so if you want either one
            # separately you can pull it from the tuple
            print("First point: " + str(xdr_data[0])) # No header in xdr data
            print("Last point: " + str(xdr_data[-1]))

    except Exception as e:
        print(f"Error: {e}")
