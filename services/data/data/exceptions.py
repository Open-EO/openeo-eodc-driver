class NotFound(Exception):
    pass

class CWSError(Exception):
    ''' CWSError raises if a error occures while querying the CSW server. '''
    def __init__(self, msg=""):
         super(CWSError, self).__init__(msg)