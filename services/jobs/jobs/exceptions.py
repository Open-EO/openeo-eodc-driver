"""Holds implementation of required exception classes."""
import logging

LOGGER = logging.getLogger('standardlog')


class ServiceException(Exception):
    """ServiceException is raised if an exception occurred while processing the request.

    The ServiceException is mapping any exception to a serializable format for the API gateway.
    Attributes:
        code: An integer holding the error code.
        user_id: The id of the user as string. (default: None)
        msg: A string with the error message.
        internal: A boolean indicating if this is an internal error. (default: True)
        links: A list of links which can be useful when getting this error. (default: None)
    """

    def __init__(self, code: int, user_id: str, msg: str, internal: bool = True, links: list = None) -> None:
        if not links:
            links = []

        self._service = "jobs"
        self._code = code
        self._user_id = user_id
        self._msg = msg
        self._internal = internal
        self._links = links
        LOGGER.exception(msg, exc_info=True)

    def to_dict(self) -> dict:
        """Serializes the object to a dict.

        Returns:
            The serialized exception.
        """

        return {
            "status": "error",
            "service": self._service,
            "code": self._code,
            "user_id": self._user_id,
            "msg": self._msg,
            "internal": self._internal,
            "links": self._links
        }


class JobLocked(ServiceException):
    """JobLocked raised if job is queued / running when trying to modify it."""
    def __init__(self, code: int, user_id: str, msg: str, internal: bool = False, links: list = None) -> None:
        super(JobLocked, self).__init__(code, user_id, msg, internal, links)


class JobNotFinished(ServiceException):
    """JobNotFinished raised if job is not finished but results are requested."""
    def __init__(self, code: int, user_id: str, job_id: str, msg: str = None, internal: bool = False,
                 links: list = None) -> None:
        if not msg:
            msg = f"Job {job_id} is not yet finished. Results cannot be accessed."
        super().__init__(code, user_id, msg, internal, links)


class BadRequest(Exception):
    """BadRequest raises if the job was not found."""
    def __init__(self, msg: str = None) -> None:
        msg = msg if msg else ""
        super(BadRequest, self).__init__(msg)


class Forbidden(Exception):
    """Forbidden raises if the user has not the permission to perform action."""
    def __init__(self, msg: str = None) -> None:
        msg = msg if msg else ""
        super(Forbidden, self).__init__(msg)


class APIConnectionError(Exception):
    """Template Exception raises if the template could not be parsed or executed."""
    def __init__(self, code: int, json: dict) -> None:
        super(APIConnectionError, self).__init__(json["message"])
        self.code = code
        self.json = json

    def __str__(self) -> str:
        return f"""
            APIConnectionError: {self.code}
            Response: {self.json}
        """
