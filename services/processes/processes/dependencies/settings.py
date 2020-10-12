"""Provide functionality to handle package settings."""
import logging
from enum import Enum
from os import makedirs
from os.path import isdir
from urllib.parse import urlparse

from dynaconf import Validator, settings

LOGGER = logging.getLogger('standardlog')


class SettingKeys(Enum):
    """Holds all required setting keys with description."""

    PROCESSES_GITHUB_URL = "PROCESSES_GITHUB_URL"
    """The GitHub url to the the definition of predefined processes from.

    E.g.: the one for version 1.0.0: https://raw.githubusercontent.com/Open-EO/openeo-processes/1.0.0/
    """

    # Connection to RabbitMQ
    RABBIT_HOST = "RABBIT_HOST"
    """The host name of the RabbitMQ - e.g. `rabbitmq`.

    If you are running in docker this is the hostname of the container!
    """
    RABBIT_PORT = "RABBIT_PORT"
    """The port on which the RabbitMQ is running - e.g. `5672`.

    If you are running in docker and the capabilities container is in the same network as the RabbitMQ this is the port
    inside the docker network NOT the exposed one!
    """
    RABBIT_USER = "RABBIT_USER"
    """The username to authenticate on the RabbitMQ - e.g. `rabbitmq`."""
    RABBIT_PASSWORD = "RABBIT_PASSWORD"  # noqa S105
    """The password to authenticate with the given user on the RabbitMQ."""

    # Processes Database
    DB_USER = "DB_USER"
    """Database username for the processes database."""
    DB_PASSWORD = "DB_PASSWORD"  # noqa S105 - not a hardcoded password only the parameter name!
    """Database user password for the processes database matching the provided user name."""
    DB_HOST = "DB_HOST"
    """Host where the processes database is running."""
    DB_PORT = "DB_PORT"
    """Port where the processes database is running."""
    DB_NAME = "DB_NAME"
    """Database name of the processes database."""

    # Additional
    LOG_DIR = "LOG_DIR"
    """The path to the directory where log files should be saved.

    If you are running in docker this is the path inside the docker container! E.g. `/usr/src/logs`
    In case you want to persist the logs a volume or a local folder needs to be mounted into the specified location.
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

    def check_create_folder(self, folder_path: str) -> bool:
        """Create the given folder path if it does not exist, always returns True."""
        if not isdir(folder_path):
            makedirs(folder_path)
        return True


def initialise_settings() -> None:
    """Configure and validates settings.

    This method is called when starting the microservice to ensure all configuration settings are properly provided.

    Raises:
        :class:`~dynaconf.validator.ValidationError`: A setting is not valid.
    """
    not_doc = Validator("ENV_FOR_DYNACONF", is_not_in=["documentation"])
    not_doc_unittest = Validator("ENV_FOR_DYNACONF", is_not_in=["documentation", "unittest"])
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()

    settings.validators.register(
        Validator(SettingKeys.PROCESSES_GITHUB_URL.value, must_exist=True, condition=utils.check_processes_github_url,
                  when=not_doc),

        Validator(SettingKeys.RABBIT_HOST.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.RABBIT_PORT.value, must_exist=True, is_type_of=int, when=not_doc_unittest),
        Validator(SettingKeys.RABBIT_USER.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.RABBIT_PASSWORD.value, must_exist=True, when=not_doc_unittest),

        Validator(SettingKeys.DB_USER.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.DB_PASSWORD.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.DB_HOST.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.DB_PORT.value, must_exist=True, is_type_of=int, when=not_doc_unittest),
        Validator(SettingKeys.DB_NAME.value, must_exist=True, when=not_doc_unittest),

        Validator(SettingKeys.LOG_DIR.value, must_exist=True, condition=utils.check_create_folder,
                  when=not_doc_unittest),
    )
    settings.validators.validate()

    LOGGER.info("Settings validated")
