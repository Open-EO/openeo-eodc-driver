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

        Validator("IS_CSW_SERVER", default=False),
        Validator("CSW_SERVER", "DATA_ACCESS", "GROUP_PROPERTY", "WHITELIST",
                  must_exist=True, when=Validator("IS_CSW_SERVER", eq="True")),

        Validator("IS_CSW_SERVER_DC", default=False),
        Validator("CSW_SERVER_DC", "DATA_ACCESS_DC", "GROUP_PROPERTY_DC", "WHITELIST_DC",
                  must_exist=True, when=Validator("IS_CSW_SERVER_DC", eq="True")),

        Validator("IS_HDA_WEKEO", default=False),
        Validator("WEKEO_API_URL", "WEKEO_USER", "WEKEO_PASSWORD", "WEKEO_DATA_FOLDER",
                  "DATA_ACCESS_WEKEO", "WHITELIST_WEKEO",
                  must_exist=True, when=Validator("IS_HDA_WEKEO", eq="True")),
    )
    settings.validators.validate()
    if not (settings.IS_CSW_SERVER or settings.IS_CSW_SERVER_DC or settings.IS_HDA_WEKEO):
        raise Exception("No (meta)data connector is specified. At least one of the"
                        "following env variables must be true: OEO_IS_CSW_SERVER,"
                        " OEO_IS_CSW_SERVER_DC, OEO_IS_HDA_WEKEO.")

    if settings.IS_CSW_SERVER:
        settings.WHITELIST = settings.WHITELIST.split(",")
    if settings.IS_CSW_SERVER_DC:
        settings.WHITELIST_DC = settings.WHITELIST_DC.split(",")
    if settings.IS_HDA_WEKEO:
        settings.WHITELIST_WEKEO = settings.WHITELIST_WEKEO.split(",")

    LOGGER.info("Settings validated")
