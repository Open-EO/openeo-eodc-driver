"""Provides functionality to handle package settings."""

import logging
from enum import Enum
from urllib.parse import urlparse

from dynaconf import Validator, settings

LOGGER = logging.getLogger('standardlog')


class SettingKeys(Enum):
    """Holds all required setting keys."""

    # Service internal
    GATEWAY_URL = "GATEWAY_URL"
    """The complete url to the gateway as string.

    This setting is only required in development environments to patch the url in the OpenAPI Specification. This
    should be improved in the future. E.g. `http://0.0.0.0:3000/v1.0`
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
    RABBIT_PASSWORD = "RABBIT_PASSWORD"
    """The password to authenticate with the given user on the RabbitMQ."""

    # Additional
    LOG_DIR = "LOG_DIR"
    """The path to the directory where log files should be saved.

    If you are running in docker this is the path inside the docker container! E.g. `/usr/src/logs`
    In case you want to persist the logs a volume or a local folder needs to be mounted into the specified location.
    """


class SettingValidationUtils:
    """Provides a set of functions to validated settings."""

    def check_parse_url(self, url: str) -> bool:
        """Checks if the provided url can be parsed."""
        result = urlparse(url)
        return all([result.scheme, result.netloc])


def initialise_settings() -> None:
    """Configures and validates settings.

    Raises:
        :py:class:`~dynaconf.validator.ValidationError`: A setting is not valid.
    """
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()
    settings.validators.register(
        Validator(SettingKeys.GATEWAY_URL, must_exist=True, condition=utils.check_parse_url,
                  when=Validator("ENV_FOR_DYNACONF", is_in=["development"])),
    )
    settings.validators.validate()

    LOGGER.info("Settings validated")
