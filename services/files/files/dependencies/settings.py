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

    To simplify file upload the file is first stored in a tmp folder and then copied to its final destination. If the
    provided Dockerfile is used do not change this variable from the one suggested in the sample_envs otherwise the
    setup may not work.
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

    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()
    settings.validators.register(
        Validator(SettingKeys.OPENEO_FILES_DIR.value, must_exist=True, condition=utils.check_create_folder,
                  when=not_doc),
        Validator(SettingKeys.UPLOAD_TMP_DIR.value, must_exist=True, condition=utils.check_create_folder, when=not_doc),
    )
    settings.validators.validate()

    LOGGER.info("Settings validated")
