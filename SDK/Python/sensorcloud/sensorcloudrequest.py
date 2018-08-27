"""
Copyright 2013 LORD MicroStrain All Rights Reserved.

Distributed under the Simplified BSD License.
See file license.txt
"""

import logging
logger = logging.getLogger(__name__)

import webrequest
import httplib
import xdrlib

from error import *

class SensorCloudRequests:
    """
    SensorCloudRequest allows a user to make http request to a SensorCloud Server.
    SensorCLoudRequests handles the SensorCLoud authetication and reauthentication.
    """

    @property
    def authToken(self):
        return self._authToken

    @property
    def apiServer(self):
        return self._apiServer

    @property
    def deviceId(self):
        return self._deviceId

    def __init__(self, deviceId, deviceKey, authServer, requests = None, cache = None):

        assert authServer.startswith("http://") or authServer.startswith("https://")

        #if a request was passed in use it.  If one wasn't passed in then we create a default RequestsFatory
        if requests:
            self._requests = requests
        else:
            self._requests = webrequest.Requests()

        self._deviceId = deviceId
        self._deviceKey = deviceKey
        self._authServer = authServer.lower()

        self._authToken = None
        self._apiServer = None

        self._cache = cache

    def authenticate(self, os_version=None, local_ip=None):
        from sensorcloud import UserAgent

        #determine protocol from the auth server
        if self._authServer.startswith("http://"):
            PROTOCOL =  "http://"
        else:
            PROTOCOL =  "https://"

        url = self._authServer + "/SensorCloud/devices/" + self._deviceId + "/authenticate/"

        request = self._requests.url(url)
        if os_version: request.param("os_version", os_version)
        if local_ip: request.param("local_ip", local_ip)
        request = request.param("version", "1")\
                      .param("key", self._deviceKey)\
                      .accept("application/xdr")\
                      .header("User-Agent", UserAgent)\
                      .get()

        #check the response code for success
        if request.status_code != httplib.OK:
            response = SensorCloudRequests.Request(request)
            raise error(response, "authenticating")

        #Extract the authentication token and server from the response
        unpacker = xdrlib.Unpacker(request.raw)
        self._authToken = unpacker.unpack_string()
        self._apiServer = PROTOCOL + unpacker.unpack_string()
        if self._cache:
            self._cache.token = self._authToken
            self._cache.server = self._apiServer


    class AuthenticatedRequestBuilder(webrequest.Requests.RequestBuilder):

        def __init__(self, url, requests):
            webrequest.Requests.RequestBuilder.__init__(self, url)
            self._requests = requests
            self.scerror = None

        def doRequest(self, method, url, options):
            from sensorcloud import UserAgent
            from sensorcloud import Reauthenticate

            requests = self._requests

            #if this is the first request, we won't have an authtoken and will need to authenticate
            if not requests.authToken:
                requests.authenticate()

            full_url = requests.apiServer + "/SensorCloud/devices/" + requests.deviceId + url

            options.addParam("auth_token", requests.authToken)
            options.addHeader("User-Agent", UserAgent)

            response = webrequest.Requests.RequestBuilder.doRequest(self, method, full_url, options)
            response = SensorCloudRequests.Request(response)

            #if we get an authentication error, reatuheticate, update the authToken and try to make the request again
            if response.status_code == httplib.UNAUTHORIZED:
                if Reauthenticate:
                    logger.info("Authentication Error, reathenticating...")
                    requests.authenticate()

                    full_url = requests.apiServer + "/SensorCloud/devices/" + requests.deviceId + url

                    options.addParam("auth_token", requests.authToken)
                    options.addHeader("User-Agent", UserAgent)

                    response = webrequest.Requests.RequestBuilder.doRequest(self, method, full_url, options)
                    response = SensorCloudRequests.Request(response)

            return response

        def _process(self, request, processors):
            if not isinstance(request, SensorCloudRequests.Request):
                request = SensorCloudRequests.Request(request)
            return super(SensorCloudRequests.AuthenticatedRequestBuilder, self)._process(request, processors)

    class Request(object):
        def __init__(self, request):
            self._r = request

            if request.status_code >= 400:
                try:
                    self.scerror = ErrorMessage(request)
                except:
                    self.scerror = None

        def __getattr__(self, name):
            try:
                return self.__getattribute__(name)
            except:
                return getattr(self._r, name)

    def url(self, url):
        assert url.startswith("/"), "url is a subresorce for a device on sensorcloud and should start with a slash('/')"
        return SensorCloudRequests.AuthenticatedRequestBuilder(url, self)
