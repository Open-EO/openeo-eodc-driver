class BadRequest(Exception):
    ''' BadRequest raises if the job was not found. '''
    def __init__(self, msg=""):
         super(BadRequest, self).__init__(msg)

class Forbidden(Exception):
    ''' Forbidden raises if the user ha snot the permission tt perform action. '''
    def __init__(self, msg=""):
         super(Forbidden, self).__init__(msg)

class APIConnectionError(Exception):
    ''' Template Exception raises if the template could not be parsed or excecuted. '''
    def __init__(self, code, json):
        super(APIConnectionError, self).__init__(json["message"])
        self.code = code
        self.json = json

    def __str__(self):
        return """
            APIConnectionError: {0}
            Response: {1}
        """.format(self.code, self.json)
