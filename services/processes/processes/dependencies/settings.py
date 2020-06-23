from urllib.parse import urlparse

from dynaconf import Validator, settings


class SettingValidationUtils:

    def check_is_url(self, url: str) -> bool:
        result = urlparse(url)
        return all([result.scheme, result.netloc])

    def check_endswith(self, value: str, suffix: str = "/") -> bool:
        return value.endswith(suffix)

    def check_processes_github_url(self, url: str) -> bool:
        return self.check_is_url(url) and self.check_endswith(url, "/")


def initialise_settings() -> None:
    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()
    settings.validators.register(
        Validator("PROCESSES_GITHUB_URL", must_exist=True, condition=utils.check_processes_github_url),
    )
    settings.validators.validate()
