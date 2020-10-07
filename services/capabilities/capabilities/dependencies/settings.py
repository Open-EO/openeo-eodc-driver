"""Provides functionality to handle package settings."""

import logging
from enum import Enum
from os import makedirs
from os.path import isdir

from dynaconf import Validator, settings

LOGGER = logging.getLogger('standardlog')


class SettingKeys(Enum):
    """Holds all required setting keys."""

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

    # Additional
    LOG_DIR = "LOG_DIR"
    """The path to the directory where log files should be saved.

    If you are running in docker this is the path inside the docker container! E.g. `/usr/src/logs`
    In case you want to persist the logs a volume or a local folder needs to be mounted into the specified location.
    """


class SettingValidationUtils:
    """Provides a set of utility functions to validated settings."""

    def check_create_folder(self, folder_path: str) -> bool:
        """Create the given folder path if it does not exist, always returns True."""
        if not isdir(folder_path):
            makedirs(folder_path)
        return True


def initialise_settings() -> None:
    """Configures and validates settings.

    As this service needs no environment variables in the Python code this is an empty wrapper to be filled in the
    future.

    Raises:
        :py:class:`~dynaconf.validator.ValidationError`: A setting is not valid.
    """
    not_doc = Validator("ENV_FOR_DYNACONF", is_not_in=["documentation"])
    not_unittest = Validator("ENV_FOR_DYNACONF", is_not_in=["unittest"])
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()

    settings.validators.register(
        Validator(SettingKeys.RABBIT_HOST.value, must_exist=True, when=not_doc and not_unittest),
        Validator(SettingKeys.RABBIT_PORT.value, must_exist=True, is_type_of=int, when=not_doc and not_unittest),
        Validator(SettingKeys.RABBIT_USER.value, must_exist=True, when=not_doc and not_unittest),
        Validator(SettingKeys.RABBIT_PASSWORD.value, must_exist=True, when=not_doc and not_unittest),

        Validator(SettingKeys.LOG_DIR.value, must_exist=True, condition=utils.check_create_folder,
                  when=not_doc and not_unittest),
    )
    settings.validators.validate()

    LOGGER.info("Settings validated")
