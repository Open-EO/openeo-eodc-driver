""" Argument Parser """

import logging

from dynaconf import settings
from nameko.extensions import DependencyProvider

from .cache import get_cache_path, get_json_cache

LOGGER = logging.getLogger("standardlog")


class ValidationError(Exception):
    """ ValidationError raises if a error occures while validating the arguments. """

    def __init__(self, msg: str = "", code: int = 400) -> None:
        super(ValidationError, self).__init__(msg)
        self.code = code
