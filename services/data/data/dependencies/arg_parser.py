""" Argument Parser """


class ValidationError(Exception):
    """ ValidationError raises if a error occures while validating the arguments. """

    def __init__(self, msg: str = "", code: int = 400) -> None:
        super(ValidationError, self).__init__(msg)
        self.code = code
