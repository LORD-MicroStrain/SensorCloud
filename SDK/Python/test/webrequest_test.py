from sensorcloud.webrequest import url


req =  url("http://www.etecnologia.net/samples/webservices/mathservice.asmx").param('op','Add').get()

print req.raw[0:5]
print "================="
print req.responseCode, req.responseMessage
print "CT:",req.contentType
print req.responseHeaders