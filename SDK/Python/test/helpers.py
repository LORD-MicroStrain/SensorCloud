from mock import Mock

def authRequest():
    import xdrlib
    token = "fake_token"
    server = "dsx.sensorcloud.microstrain.com"
    packer = xdrlib.Packer()
    packer.pack_string(token)
    packer.pack_string(server)
    packer.pack_string("")

    authRequestMock = Mock()
    authRequestMock.status_code = 200
    authRequestMock.raw = packer.get_buffer()
    return authRequestMock

def ok():
    response = Mock()
    response.status_code = 200
    return response

def created():
    response = Mock()
    response.status_code = 201
    return response

def mockCallArg(call, i, name):
    if len(call[1]) > i:
        return call[1][i]
    return call[2][name]
