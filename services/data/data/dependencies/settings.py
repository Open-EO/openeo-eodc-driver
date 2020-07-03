import logging
from os import makedirs
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

    def check_parse_url(self, url: str) -> bool:
        result = urlparse(url)
        return all([result.scheme, result.netloc])


def initialise_settings() -> None:
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()
    settings.validators.register(
        Validator("CACHE_PATH", must_exist=True, condition=utils.check_create_folder),
        Validator("DNS_URL", must_exist=True, condition=utils.check_parse_url),

        Validator("CSW_SERVER", must_exist=True, when=Validator("ENV_FOR_DYNACONF", is_not_in=["unittest"]),
                  condition=utils.check_url_is_reachable),
        Validator("DATA_ACCESS", must_exist=True),
        Validator("GROUP_PROPERTY", must_exist=True),
        Validator("WHITELIST", must_exist=True),

        Validator("CSW_SERVER_DC", must_exist=True, when=Validator("ENV_FOR_DYNACONF", is_not_in=["unittest"]),
                  condition=utils.check_url_is_reachable),
        Validator("DATA_ACCESS_DC", must_exist=True),
        Validator("GROUP_PROPERTY_DC", must_exist=True),
        Validator("WHITELIST_DC", must_exist=True),
    )
    settings.validators.validate()

    settings.WHITELIST = settings.WHITELIST.split(",")
    settings.WHITELIST_DC = settings.WHITELIST_DC.split(",")

    LOGGER.info("Settings validated")
