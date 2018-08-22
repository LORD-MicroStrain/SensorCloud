"""
Copyright 2012 MicroStrain Inc. All Rights Reserved.

Distributed under the Simplified BSD License.
See file license.txt
"""

"""
Wrapper around HttpWebRequest to simplify the creation of http requests.
It was specifically designed for interacting with web services.

The intention is for this class to be a generic http request, but it was built
explicitly for sensorcloud, so only the options that are required for SensorCloud
have been implemented.
"""

import logging, ssl
log = logging.getLogger(__name__)

#from urllib import urlencode
#import httplib
import time
import zlib

class Requests(object):

    compression = "gzip"

    class RequestOptions(object):
        """
        RequestOptions stores all the possible variables required to make an http request
        """

        def __init__(self):
            self._queryParams = {}
            self._headers = {}
            self._requestBody = None
            self._cachedQueryString = None

        @property
        def headers(self):
            return self._headers

        @property
        def queryParams(self):
            return self._queryParams

        @property
        def requestBody(self):
            return self._requestBody

        @requestBody.setter
        def requestBody(self, body):
            if Requests.compression == "gzip":
                compressedBody = zlib.compress(body)
                if len(compressedBody) < len(body):
                    self.addHeader('content-encoding', "gzip")
                    self._requestBody = compressedBody
                else:
                    self._requestBody = body

        def addParam(self , name, value):
            """
            Add a query string param to the request options
            """
            self._queryParams[name] = value

        def addHeader(self, name, value):
            """
            Add an http header to the request options
            """

            self._headers[name] = value

        def setRequestBody(self, requestBody):
            """
            Adds data that is sent as the body of a request
            """
            self.requestBody = requestBody

    class RequestBuilder(object):
        """
        An http request has a wide range of possible options that can be specified.
        RequestBuilder parameterizes each possible options as a method returning a RequestBuilder option
        allowing the chaining of request options.  The chaining allows us to eliminate the need for having an overloaded
        method that can handle any combination of desired options, and also results in a very readable self documented
        request.
        """

        def __init__(self, url):
            self._url = url
            self._processors = []
            self._options =  Requests.RequestOptions()

        def header(self, name, value):
            """
            Add an http header to the request
            """
            self._options.addHeader(name, value)
            return self

        def content_type(self, contentType):
            """
            Set the content Type for the request's messageBody.
            This is a convenience method for setting the HTTP header "Content-Type".
            """
            return self.header("Content-Type", contentType)


        def accept(self, acceptType):
            """
            specifies the content-type or types that we can handle in the response.
            This is a convenience method for seeting the HTTP header "Accept".
            """
            return self.header("Accept", acceptType);

        def param(self, name, value):
            """
            Add a query parameter to the request
            """
            self._options.addParam(name, str(value))
            return self

        def data(self, requestBody):
            """
            Add a message body to the request.
            """
            self._options.setRequestBody(requestBody)
            return self

        def add_processor(self, processor):
            """
            Add a processor to be executed after the request is complete, but before it is returned to the caller.

            processor call args:
                response    - A Request object containing information about the request and response.
                handler        - A no arg callable to execute the next processor

            If the processor is successful it should return the result of calling handler
            If the processor needs to resend the request it should return True
            If the processor needs to stop executing processors it should return False
            """
            self._processors.append(processor)

        def get(self):
            """
            Invoke the request that has been built using the GET verb
            """
            return self.doRequest("GET", self._url, self._options)

        def put(self):
            """
            Invoke the request that has been built using the PUT verb
            """
            return self.doRequest("PUT", self._url, self._options)

        def post(self):
            """
            Invoke the request that has been built using the POST verb
            """
            return self.doRequest("POST", self._url, self._options)

        def delete(self):
            """
            Invoke the request that has been built using the DELETE verb
            """
            return self.doRequest("DELETE", self._url, self._options)

        def doRequest(self, method, url, options):
            assert method in ("GET", "PUT", "POST", "DELETE")
            assert url.startswith("http://") or url.startswith("https://")

            # retry the request until all of the processors succeed
            request = Requests.Request(method, url, options)
            if self._process(request, self._processors):
                # rerun the request
                request = Requests.Request(method, url, options)
            return request

        def _process(self, request, processors):
            if processors:
                p, rest = processors[0], processors[1:]
                return p(request, lambda: self._process(request, rest))
            else:
                return False

    class Request(object):

        @property
        def request_duration(self):
            return self._duration

        @property
        def status_code(self):
            """
            the status code of the response.
            rfc2612  "Hypertext Transfer Protocol -- HTTP/1.1" officially refrese to this as Status-Code
            """
            return self._status_code

        @property
        def reason(self):
            """
            the reason phrase the response.
            rfc2612 "Hypertext Transfer Protocol -- HTTP/1.1" officially refrese to this as Reason-Phrase
            """
            return self._reason

        @property
        def content_type(self):
            return self._response_headers.get("content-type")

        @property
        def response_headers(self):
            return self._response_headers

        @property
        def text(self):
            if self._response_data is None: return ""
            return unicode(self._response_data, "utf-8")

        @property
        def raw(self):
            return self._response_data

        def __init__(self, method, url, options):
            self._method = method;
            self._url = url;
            self._options = options;

            self._status_code = None;
            self._reason = None;
            self._response_data = None;
            self._response_headers = None;
            self._duration = None

            self.doRequest()
            log.debug("%s: %s %s s:%0.2f", self._method, self._url, self.status_code, self._duration)

        def doRequest(self):
            import httplib
            from urllib import urlencode

            # parse the url
            protocol, restofurl = self._url.split("://")
            parts = restofurl.split('/', 1) #max split 1, so we only pull off the server
            server = parts[0]
            if len(parts) == 2:
                url = "/" + parts[1]
            else:
                url = "/"

            if self._options.queryParams:
                url += "?" + urlencode(self._options.queryParams)

            protocol = protocol.lower()
            assert protocol in ("http", "https")
            if protocol == "https":
                conn = httplib.HTTPSConnection(server, context=ssl._create_unverified_context())
            else:
                conn = httplib.HTTPConnection(server)

            start = time.time()

            conn.request(self._method, url=url, headers=self._options.headers, body=self._options.requestBody)
            response = conn.getresponse()

            self._response_data = response.read()

            #once the response has been read, the request is complete
            self._duration = time.time() - start

            self._status_code = response.status
            self._reason = response.reason

            self._response_headers = dict(response.getheaders())

    def url(self, url):
        """
        Initiate the begining of a request using the url.  A request builder is returned allowing the request to be customized before
        it is executed.
        """
        return Requests.RequestBuilder(url)
