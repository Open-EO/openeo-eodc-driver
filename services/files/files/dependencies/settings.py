"""Provide functionality to handle package settings."""

import logging
from enum import Enum
from os import makedirs
from os.path import isdir

from dynaconf import Validator, settings

LOGGER = logging.getLogger('standardlog')


class SettingKeys(Enum):
    """Holds all required setting keys with description."""

    OPENEO_FILES_DIR = "OPENEO_FILES_DIR"
    """The path to a directory where all user file spaces are created in.

    Inside this folder one folder per user will be created. All data uploaded or computed by this user will be stored
    there. If you are running in docker the path needs to be inside the container.
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
        Validator(SettingKeys.OPENEO_FILES_DIR.value, must_exist=True, condition=utils.check_create_folder,
                  when=not_doc),
        Validator(SettingKeys.UPLOAD_TMP_DIR.value, must_exist=True, condition=utils.check_create_folder, when=not_doc),

        Validator(SettingKeys.RABBIT_HOST.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.RABBIT_PORT.value, must_exist=True, is_type_of=int, when=not_doc_unittest),
        Validator(SettingKeys.RABBIT_USER.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.RABBIT_PASSWORD.value, must_exist=True, when=not_doc_unittest),

        Validator(SettingKeys.LOG_DIR.value, must_exist=True, condition=utils.check_create_folder,
                  when=not_doc_unittest),
    )
    settings.validators.validate()

    LOGGER.info("Settings validated")
