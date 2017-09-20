from sensorcloud.sensorcloudrequest import SensorCloudRequests

auth_server = "https://sensorcloud.microstrain.com"
device_id = "OAPI00DZ0BQ3X1BR"
key = "6b6a281effc9c5ab7753ec7ade215221794391d63cf533a37e59a180e2c4bb15"

requests = SensorCloudRequests(device_id, key, auth_server)

r =  requests.url("/sensors/")
r.accept("application/xdr")
r.param("version", "1")
req = r.get()

print req.raw[0:5]
print "================="
print req.status_code, req.reason
print "CT:",req.contentType
print req.responseHeaders