import logging
from os import makedirs
from os.path import isdir

from dynaconf import Validator, settings

LOGGER = logging.getLogger('standardlog')


class SettingValidationUtils:
    def check_create_folder(self, folder_path: str) -> bool:
        if not isdir(folder_path):
            makedirs(folder_path)
        return True


def initialise_settings() -> None:
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()
    settings.validators.register(
        Validator("OPENEO_FILES_DIR", must_exist=True, condition=utils.check_create_folder),
        Validator("UPLOAD_TMP_DIR", must_exist=True, condition=utils.check_create_folder),
    )
    settings.validators.validate()

    LOGGER.info("Settings validated")
