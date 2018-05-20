class BadRequest(Exception):
    pass


class Forbidden(Exception):
    pass

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
