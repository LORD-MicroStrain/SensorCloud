import json

class ErrorMessage:
    def __init__(self, response):
        self._data = json.loads(response.text)

    @property
    def code(self):
        return self._data.get("errorcode")

    @property
    def message(self):
        return self._data.get("message")

class Error(Exception):
    def __init__(self, message):
        super(Error, self).__init__(message)

class HTTPError(Error):
    def __init__(self, response, message):
        super(HTTPError, self).__init__("HTTP Error %s %s %s: %s" % (message, response.status_code, response.reason, response.text))
        self.code = response.status_code
        self.reason = response.reason

class ServerError(HTTPError):
    def __init__(self, response, message):
        super(ServerError, self).__init__(response, message)

class BodyError(Error):
    def __init__(self, error, message):
        super(BodyError, self).__init__("SensorCloud Error %s %s %s" % (message, error.code, error.message))
        self.error = error

class UnauthorizedError(BodyError):
    def __init__(self, error, message):
        super(UnauthorizedError, self).__init__(error, message)

class AuthenticationError(BodyError):
    def __init__(self, error):
        super(AuthenticationError, self).__init__(error, "authenticating")

class QuotaExceededError(AuthenticationError):
    def __init__(self, error):
        super(QuotaExceededError, self).__init__(error)

def error(makeBodyError, response, message):
    if BodyErrorClass and response.scerror:
        return makeBodyError()
    else:
        return HTTPError(response, message)
