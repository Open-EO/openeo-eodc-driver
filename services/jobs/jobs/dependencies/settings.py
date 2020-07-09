import logging
from os import environ, makedirs
from os.path import isdir
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from dynaconf import Validator, settings

LOGGER = logging.getLogger('standardlog')


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

    def check_url_is_reachable(self, url: str) -> bool:
        try:
            if url.lower().startswith('http'):
                req = Request(url)
                with urlopen(req) as resp:  # noqa
                    return resp.status == 200
            else:
                return False
        except URLError:
            return False


def initialise_settings() -> None:
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()
    settings.validators.register(
        Validator("GATEWAY_URL", must_exist=True, condition=utils.check_is_url),
        Validator("AIRFLOW_HOST", must_exist=True, condition=utils.check_is_url,
                  when=Validator("ENV_FOR_DYNACONF", is_not_in=["unittest"])),
        Validator("JOB_DATA", must_exist=True),
        Validator("AIRFLOW_DAGS", must_exist=True, condition=utils.check_create_folder),
        Validator("SYNC_DEL_DELAY", must_exist=True, is_type_of=int, condition=utils.check_positive_int),
        Validator("SYNC_RESULTS_FOLDER", must_exist=True, condition=utils.check_create_folder),
        Validator("CSW_SERVER", must_exist=True, condition=utils.check_url_is_reachable,
                  when=Validator("ENV_FOR_DYNACONF", is_not_in=["unittest"])),
    )
    settings.validators.validate()
    LOGGER.info("Settings validated")

    # needed for eodc-openeo-bindings - should be removed once this is handled in a better way
    environ["CSW_SERVER"] = settings.CSW_SERVER
    environ["AIRFLOW_DAGS"] = settings.AIRFLOW_DAGS
