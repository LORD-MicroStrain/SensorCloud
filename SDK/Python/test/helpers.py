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
