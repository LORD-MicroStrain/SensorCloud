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
        if response.scerror:
            super(HTTPError, self).__init__("SensorCloud Error %s %s %s" % (message, response.scerror.code, response.scerror.message))
            self.error = response.scerror
        else:
            super(HTTPError, self).__init__("SensorCloud Error %s %s %s: %s" % (message, response.status_code, response.reason, response.text))
            self.error = None
        self.code = response.status_code
        self.reason = response.reason

class ServerError(HTTPError):
    def __init__(self, response, message):
        super(ServerError, self).__init__(response, message)

class UserError(HTTPError):
    def __init__(self, response, message):
        super(UserError, self).__init__(response, message)

class UnauthorizedError(UserError):
    def __init__(self, response, message):
        super(UnauthorizedError, self).__init__(response, message)

class QuotaExceededError(UnauthorizedError):
    def __init__(self, response, message):
        super(QuotaExceededError, self).__init__(response, message)

class TruncatedUploadError(UserError):
    def __init__(self, response, message):
        super(TruncatedUploadError, self).__init__(response, message)

def error(response, message):
    # setup specific errors
    if response.scerror:
        if response.status_code == 401:
            if response.scerror.code == "401-005":
                return QuotaExceededError(response, message)
        if response.status_code == 403:
            if response.scerror.code == "403-004":
                return QuotaExceededError(response, message)
        if response.status_code == 400:
            if response.scerror.code == "400-038":
                return TruncatedUploadError(response, message)

    if response.status_code == 401:
        return UnauthorizedError(response, message)

    # setup error groups
    if response.status_code >= 500:
        return ServerError(response, message)
    if response.status_code >= 400:
        return UserError(response, message)

    # generic error
    return HTTPError(response, message)
