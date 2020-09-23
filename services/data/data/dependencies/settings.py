"""Provide functionality to handle package settings."""

import logging
from enum import Enum
from os import makedirs
from os.path import isdir
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from dynaconf import Validator, settings

LOGGER = logging.getLogger('standardlog')


class SettingKeys(Enum):
    """Holds all required setting keys with description."""

    CACHE_PATH = "CACHE_PATH"
    """The path to a directory where collection metadata should be cached.

    If you are running in docker the path needs to be inside the container.
    """
    DNS_URL = "DNS_URL"
    """The URI visible from the outside.

    It is used to return proper links.
    In this setup it is the URI of the gateway. E.g. for eodc this is https://openeo.eodc.eu/v1.0, for a local
    deployment it could be http://0.0.0.0:3000/v1.0.
    """
    CSW_SERVER = "CSW_SERVER"
    """The url to a running CSW server.

    E.g. eodc's CSW server is reachable under https://csw.eodc.eu
    If you are running in docker and also have a CSW server in the same docker network it could be http://pycsw:8000
    """
    DATA_ACCESS = "DATA_ACCESS"
    """The required user permissions to access data from this CSW server.

    Each user has a profile and with this a 'data_access' associated to him-/herself e.g. 'public' or 'public,orga-a'.
    A CSW server with DATA_ACCESS 'orga-a' is only accessible for user with this 'data_access'.
    """
    GROUP_PROPERTY = "GROUP_PROPERTY"
    """The CSW property to query for when searching for a collection identifier.

    As different data sources may be structured differently in the metadata DB this parameter can be used to defined
    which field to query when searching for a given 'identifier'. E.g. the collection name can either be stored as
    identifier ('apiso:Parentidentifier') or as variable name ('eodc:variable_name').
    """
    WHITELIST = "WHITELIST"
    """A list collections on the CSW server which should be accessible via OpenEO.

    There are scenarios where not all collections available on a CSW server are meaningful in the context of OpenEO.
    """

    CSW_SERVER_DC = "CSW_SERVER_DC"
    """The url to a second running CSW server.

    This is basically the same as :attr:`~data.dependencies.settings.SettingKeys.CSW_SERVER`.
    To enable the use of two (exactly TWO) CSW servers this and all other parameters with the suffix `_DC` are used.
    Their meaning is completely equivalent to the parameters without the suffix just describing a different CSW server.
    """
    DATA_ACCESS_DC = "DATA_ACCESS_DC"
    """See :attr:`~data.dependencies.settings.SettingKeys.DATA_ACCESS` and description in
    :attr:`~data.dependencies.settings.SettingKeys.CSW_SERVER_DC`.
    """
    GROUP_PROPERTY_DC = "GROUP_PROPERTY_DC"
    """See :attr:`~data.dependencies.settings.SettingKeys.GROUP_PROPERTY` and description in
    :attr:`~data.dependencies.settings.SettingKeys.CSW_SERVER_DC`.
    """
    WHITELIST_DC = "WHITELIST_DC"
    """See :attr:`~data.dependencies.settings.SettingKeys.WHITELIST` and description in
    :attr:`~data.dependencies.settings.SettingKeys.CSW_SERVER_DC`.
    """


class SettingValidationUtils:
    """Provides a set of utility functions to validated settings."""

    def check_create_folder(self, folder_path: str) -> bool:
        """Create the given folder path if it does not exist, always returns True."""
        if not isdir(folder_path):
            makedirs(folder_path)
        return True

    def check_url_is_reachable(self, url: str) -> bool:
        """Return a boolean whether a connection to a given url could be created."""
        try:
            if url.lower().startswith('http'):
                req = Request(url)
                with urlopen(req) as resp:  # noqa
                    return resp.status == 200
            else:
                return False
        except URLError:
            return False

    def check_parse_url(self, url: str) -> bool:
        """Return a boolean whether the url could be parsed.

        This is useful if a setting holding a url may not be reachable at the time of setting validation. Then this
        method at least validates that a valid url is provided. E.g. the gateway will most probably be not reachable
        when bringing up microservices.
        """
        result = urlparse(url)
        return all([result.scheme, result.netloc])


def initialise_settings() -> None:
    """Configure and validates settings.

    This method is called when starting the microservice to ensure all configuration settings are properly provided.

    Raises:
        :class:`~dynaconf.validator.ValidationError`: A setting is not valid.
    """
    no_doc = Validator("ENV_FOR_DYNACONF", is_not_in=["documentation"])
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()

    settings.validators.register(
        Validator(SettingKeys.CACHE_PATH.value, must_exist=True, condition=utils.check_create_folder, when=no_doc),
        Validator(SettingKeys.DNS_URL.value, must_exist=True, condition=utils.check_parse_url, when=no_doc),

        # Validator("CSW_SERVER", must_exist=True, when=Validator("ENV_FOR_DYNACONF", is_not_in=["unittest"]),
        #           condition=utils.check_url_is_reachable),
        Validator(SettingKeys.CSW_SERVER.value, must_exist=True, when=no_doc),
        Validator(SettingKeys.DATA_ACCESS.value, must_exist=True, when=no_doc),
        Validator(SettingKeys.GROUP_PROPERTY.value, must_exist=True, when=no_doc),
        Validator(SettingKeys.WHITELIST.value, must_exist=True, when=no_doc),

        # Validator("CSW_SERVER_DC", must_exist=True, when=Validator("ENV_FOR_DYNACONF", is_not_in=["unittest"]),
        #           condition=utils.check_url_is_reachable),
        Validator(SettingKeys.CSW_SERVER_DC.value, must_exist=True, when=no_doc),
        Validator(SettingKeys.DATA_ACCESS_DC.value, must_exist=True, when=no_doc),
        Validator(SettingKeys.GROUP_PROPERTY_DC.value, must_exist=True, when=no_doc),
        Validator(SettingKeys.WHITELIST_DC.value, must_exist=True, when=no_doc),
    )
    settings.validators.validate()

    if settings.ENV_FOR_DYNACONF != "documentation":
        settings.WHITELIST = settings.WHITELIST.split(",")
        settings.WHITELIST_DC = settings.WHITELIST_DC.split(",")

    LOGGER.info("Settings validated")
