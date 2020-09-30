"""Provides functionality to handle package settings."""
from enum import Enum
from os import makedirs
from os.path import isdir

from dynaconf import Validator, settings


class SettingKeys(Enum):
    """Holds all required setting keys."""

    OPENEO_VERSION = "OPENEO_VERSION"
    """The OpenEO version running - in the 'version url format'.

    This is used for version urls only! So depending how you setup version urls the format can change. E.g. v1.0
    """
    SECRETE_KEY = "SECRET_KEY"  # noqa S105 - not a hardcoded password only the parameter name!
    """Secret key for creating/validating basic auth tokens.

    This key is used when generating and validating a token for a user authenticating with basic auth.
    """
    UPLOAD_TMP_DIR = "UPLOAD_TMP_DIR"
    """The path to a directory where user upload data will be stored temporarily.

    To simplify file upload the file is first stored in a tmp folder and then copied to its final destination. The tmp
    folder needs to be mounted to both the gateway and the files service. That way a file is passed from the gateway
    to the files service via this folder but the user data folder does not need to be mounted to the gateway. If the
    provided Dockerfile is used do not change this variable from the one suggested in the sample_envs otherwise the
    setup may not work.
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

    # User DB
    DB_USER = "DB_USER"
    """Database user name for the users database."""
    DB_PASSWORD = "DB_PASSWORD"  # noqa S105 - not a hardcoded password only the parameter name!
    """Database user password for the users database matching the provided user name."""
    DB_HOST = "DB_HOST"
    """Host where the users database is running."""
    DB_PORT = "DB_PORT"
    """Port where the users database is running."""
    DB_NAME = "DB_NAME"
    """Database name of the users database."""


class SettingValidationUtils:
    """Provides a set of utility functions to validated settings."""

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
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()

    settings.validators.register(
        Validator(SettingKeys.OPENEO_VERSION.value, must_exist=True, when=not_doc),
        Validator(SettingKeys.SECRETE_KEY.value, must_exist=True, when=not_doc),
        Validator(SettingKeys.UPLOAD_TMP_DIR.value, must_exist=True, condition=utils.check_create_folder, when=not_doc),

        Validator(SettingKeys.RABBIT_HOST.value, must_exist=True, when=not_doc),
        Validator(SettingKeys.RABBIT_PORT.value, must_exist=True, is_type_of=int, when=not_doc),
        Validator(SettingKeys.RABBIT_USER.value, must_exist=True, when=not_doc),
        Validator(SettingKeys.RABBIT_PASSWORD.value, must_exist=True, when=not_doc),

        Validator(SettingKeys.DB_USER.value, must_exist=True, when=not_doc),
        Validator(SettingKeys.DB_PASSWORD.value, must_exist=True, when=not_doc),
        Validator(SettingKeys.DB_HOST.value, must_exist=True, when=not_doc),
        Validator(SettingKeys.DB_PORT.value, must_exist=True, is_type_of=int, when=not_doc),
        Validator(SettingKeys.DB_NAME.value, must_exist=True, when=not_doc),
    )
    settings.validators.validate()
