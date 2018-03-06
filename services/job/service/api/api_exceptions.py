''' API Exceptions '''

class InvalidRequest(Exception):
    ''' InvalidRequest raises if the request is invalid. '''

    def __init__(self, msg=None):
        if not msg:
            msg = "The request is malformed or invalid."
        super(InvalidRequest, self).__init__(msg)
        self.code = 400

class AuthenticationError(Exception):
    ''' AuthenticationError if user could not be verified by token. '''

    def __init__(self, msg=None):
        if not msg:
            msg = "The back-end requires clients to authenticate in order to process this request."
        super(AuthenticationError, self).__init__(msg)
        self.code = 401

class AuthorizationError(Exception):
    ''' AuthorizationError raises if user is not allowed to access ressource. '''

    def __init__(self, msg=None):
        if not msg:
            msg = "Authorization failed, access to the requested resource has been denied."
        super(AuthorizationError, self).__init__(msg)
        self.code = 403