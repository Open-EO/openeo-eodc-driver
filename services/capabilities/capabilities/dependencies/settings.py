"""Provides functionality to handle package settings."""

import logging
from enum import Enum

from dynaconf import settings

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


def initialise_settings() -> None:
    """Configures and validates settings.

    As this service needs no environment variables in the Python code this is an empty wrapper to be filled in the
    future.

    Raises:
        :py:class:`~dynaconf.validator.ValidationError`: A setting is not valid.
    """
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    settings.validators.register()
    settings.validators.validate()

    LOGGER.info("Settings validated")
