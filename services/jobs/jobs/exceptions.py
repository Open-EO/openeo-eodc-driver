class BadRequest(Exception):
    """ BadRequest raises if the job was not found. """
    def __init__(self, msg: str = None) -> None:
        msg = msg if msg else ""
        super(BadRequest, self).__init__(msg)


class Forbidden(Exception):
    """ Forbidden raises if the user has not the permission to perform action. """
    def __init__(self, msg: str = None) -> None:
        msg = msg if msg else ""
        super(Forbidden, self).__init__(msg)


class APIConnectionError(Exception):
    """ Template Exception raises if the template could not be parsed or executed. """
    def __init__(self, code: int, json: dict) -> None:
        super(APIConnectionError, self).__init__(json["message"])
        self.code = code
        self.json = json

    def __str__(self) -> str:
        return f"""
            APIConnectionError: {self.code}
            Response: {self.json}
        """
