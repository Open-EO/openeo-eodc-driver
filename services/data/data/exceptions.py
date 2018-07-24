class ValidationError(Exception):
    ''' ValidationError raises if a error occures while validating the arguments. '''
    def __init__(self, msg=""):
         super(ValidationError, self).__init__(msg)

class CWSError(Exception):
    ''' CWSError raises if a error occures while querying the CSW server. '''
    def __init__(self, msg=""):
         super(CWSError, self).__init__(msg)