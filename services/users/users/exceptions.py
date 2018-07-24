class NotFound(Exception):
    ''' NotFound raises if the user was not found. '''
    def __init__(self, msg=""):
         super(NotFound, self).__init__(msg)

class LoginError(Exception):
    ''' LoginError raises if the user could not be logged in. '''
    def __init__(self, msg=""):
         super(LoginError, self).__init__(msg)