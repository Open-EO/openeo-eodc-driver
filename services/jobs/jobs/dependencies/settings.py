"""Provide functionality to handle package settings."""
import logging
from enum import Enum
from os import environ, makedirs
from os.path import isdir
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from dynaconf import Validator, settings

LOGGER = logging.getLogger('standardlog')


class SettingKeys(Enum):
    """Holds all required setting keys with description."""

    OPENEO_VERSION = "OPENEO_VERSION"
    """The OpenEO version running - in the 'version url format'.

    This is used for version urls only! So depending how you setup version urls the format can change. E.g. v1.0
    """
    AIRFLOW_HOST = "AIRFLOW_HOST"
    """The complete url to the Apache Airflow webserver as a string.

    If you are running the provided docker setup use: http://airflow-webserver:8080.
    """
    AIRFLOW_OUTPUT = "AIRFLOW_OUTPUT"
    """The path on the Airflow worker where data output is written to.

    This path does not need to exist in the jobs service! It is only needed to write a correct dag for a job as the
    absolute paths of the output directories - on the airflow worker (!) - are also written in the dag.

    If you are running inside docker this path has to be inside the corresponding airflow worker container. E.g.
    /data_out
    """
    AIRFLOW_DAGS = "AIRFLOW_DAGS"
    """The path a folder where all dag files will be stored.

    If you are running in docker the path needs to be inside the container. E.g.: /usr/src/dags
    """
    SYNC_DEL_DELAY = "SYNC_DEL_DELAY"
    """Delay after which to delete sync-jobs output.

    It must be minimum above the timeout of gunicorn and nginx. E.g. 300
    """
    SYNC_RESULTS_FOLDER = "SYNC_RESULTS_FOLDER"
    """The path to the sync-results folder.

    The content of this folder is also mounted to the gateway to simplify data transfer.

    If you are running in docker the path needs to be inside the container. E.g.: /usr/src/sync-results
    """
    CSW_SERVER = "CSW_SERVER"
    """The url to a running CSW server.

    E.g. eodc's CSW server is reachable under https://csw.eodc.eu
    If you are running in docker and also have a CSW server in the same docker network it could be http://pycsw:8000
    """


class SettingValidationUtils:
    """Provides a set of utility functions to validated settings."""

    def check_create_folder(self, folder_path: str) -> bool:
        """Create the given folder path if it does not exist, always returns True."""
        if not isdir(folder_path):
            makedirs(folder_path)
        return True

    def check_positive_int(self, value: int) -> bool:
        """Return a boolean whether a given value is a positive integer."""
        return isinstance(value, int) and value > 0

    def check_parse_url(self, url: str) -> bool:
        """Return a boolean whether the url could be parsed.

        This is useful if a setting holding a url may not be reachable at the time of setting validation. Then this
        method at least validates that a valid url is provided. E.g. the gateway will most probably be not reachable
        when bringing up microservices.
        """
        result = urlparse(url)
        return all([result.scheme, result.netloc])

    def check_url_is_reachable(self, url: str) -> bool:
        """Return a boolean whether a connection to a given url could be created."""
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
    """Configure and validates settings.

    This method is called when starting the microservice to ensure all configuration settings are properly provided.

    Raises:
        :class:`~dynaconf.validator.ValidationError`: A setting is not valid.
    """
    not_doc = Validator("ENV_FOR_DYNACONF", is_not_in=["documentation"])
    not_unittest = Validator("ENV_FOR_DYNACONF", is_not_in=["unittest"])

    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()
    settings.validators.register(
        Validator(SettingKeys.OPENEO_VERSION.value, must_exist=True, when=not_doc),
        Validator(SettingKeys.AIRFLOW_HOST.value, must_exist=True, condition=utils.check_parse_url,
                  when=(not_unittest and not_doc)),
        Validator(SettingKeys.AIRFLOW_OUTPUT.value, must_exist=True, when=not_doc),
        Validator(SettingKeys.AIRFLOW_DAGS.value, must_exist=True, condition=utils.check_create_folder, when=not_doc),
        Validator(SettingKeys.SYNC_DEL_DELAY.value, must_exist=True, is_type_of=int, condition=utils.check_positive_int,
                  when=not_doc),
        Validator(SettingKeys.SYNC_RESULTS_FOLDER.value, must_exist=True, condition=utils.check_create_folder,
                  when=not_doc),
        # Validator(SettingKeys.CSW_SERVER.value, must_exist=True, condition=utils.check_url_is_reachable,
        #           when=(not_unittest and not_doc)),
        Validator(SettingKeys.CSW_SERVER.value, must_exist=True, when=not_doc),
    )
    settings.validators.validate()
    LOGGER.info("Settings validated")

    if settings.ENV_FOR_DYNACONF != "documentation":
        # needed for eodc-openeo-bindings - should be removed once this is handled in a better way
        environ["CSW_SERVER"] = settings.CSW_SERVER
        environ["AIRFLOW_DAGS"] = settings.AIRFLOW_DAGS
