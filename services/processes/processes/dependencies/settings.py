"""Provide functionality to handle package settings."""

import logging
from enum import Enum
from urllib.parse import urlparse

from dynaconf import Validator, settings

LOGGER = logging.getLogger('standardlog')


class SettingKeys(Enum):
    """Holds all required setting keys with description."""

    PROCESSES_GITHUB_URL = "PROCESSES_GITHUB_URL"
    """The GitHub url to the the definition of predefined processes from.

    E.g.: the one for version 1.0.0: https://raw.githubusercontent.com/Open-EO/openeo-processes/1.0.0/
    """


class SettingValidationUtils:
    """Provides a set of utility functions to validated settings."""

    def parse_url(self, url: str) -> bool:
        """Return a boolean whether the url could be parsed.

        This is useful if a setting holding a url may not be reachable at the time of setting validation. Then this
        method at least validates that a valid url is provided. E.g. the gateway will most probably be not reachable
        when bringing up microservices.
        """
        result = urlparse(url)
        return all([result.scheme, result.netloc])

    def check_endswith(self, value: str, suffix: str = "/") -> bool:
        """Return a boolean whether the string ends with a specific suffix."""
        return value.endswith(suffix)

    def check_processes_github_url(self, url: str) -> bool:
        """Check the processes_github_url can be parsed and ends with a /."""
        return self.parse_url(url) and self.check_endswith(url, "/")


def initialise_settings() -> None:
    """Configure and validates settings.

    This method is called when starting the microservice to ensure all configuration settings are properly provided.

    Raises:
        :class:`~dynaconf.validator.ValidationError`: A setting is not valid.
    """
    not_doc = Validator("ENV_FOR_DYNACONF", is_not_in=["documentation"])
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()

    settings.validators.register(
        Validator(SettingKeys.PROCESSES_GITHUB_URL.value, must_exist=True, condition=utils.check_processes_github_url,
                  when=not_doc),
    )
    settings.validators.validate()

    LOGGER.info("Settings validated")
