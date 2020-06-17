from os import makedirs
from os.path import isdir
from urllib.parse import urlparse

from dynaconf import Validator, settings


class SettingValidationUtils:

    def check_create_folder(self, folder_path: str) -> bool:
        if not isdir(folder_path):
            makedirs(folder_path)
        return True

    def check_positive_int(self, value: int) -> bool:
        return value > 0

    def check_is_url(self, url: str) -> bool:
        result = urlparse(url)
        return all([result.scheme, result.netloc])


def initialise_settings() -> None:
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()
    settings.validators.register(
        Validator("GATEWAY_URL", must_exist=True, condition=utils.check_is_url),
        Validator("AIRFLOW_HOST", must_exist=True, condition=utils.check_is_url),
        Validator("JOB_DATA", must_exist=True),
        Validator("AIRFLOW_DAGS", must_exist=True, condition=utils.check_create_folder),
        Validator("SYNC_DEL_DELAY", must_exist=True, is_type_of=int, condition=utils.check_positive_int),
        Validator("SYNC_RESULTS_FOLDER", must_exist=True, condition=utils.check_create_folder),
    )
    settings.validators.validate()
