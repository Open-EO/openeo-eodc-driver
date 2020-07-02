import logging
from urllib.parse import urlparse

from dynaconf import Validator, settings

LOGGER = logging.getLogger('standardlog')


class SettingValidationUtils:

    def check_parse_url(self, url: str) -> bool:
        result = urlparse(url)
        return all([result.scheme, result.netloc])


def initialise_settings() -> None:
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()
    settings.validators.register(
        Validator("GATEWAY_URL", must_exist=True, condition=utils.check_parse_url),
    )
    settings.validators.validate()

    LOGGER.info("Settings validated")
