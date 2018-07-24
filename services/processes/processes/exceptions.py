class NotFound(Exception):
    ''' NotFound raises if teh user was not found. '''
    def __init__(self, msg=""):
         super(NotFound, self).__init__(msg)