"""Provide functionality to handle package settings."""
import logging
from enum import Enum
from os import makedirs
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
    # TODO to be removed once new bindings and api version is done
    CSW_SERVER = "CSW_SERVER"
    """The url to a running CSW server.

    E.g. eodc's CSW server is reachable under https://csw.eodc.eu
    If you are running in docker and also have a CSW server in the same docker network it could be http://pycsw:8000
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

    # Jobs Database
    DB_USER = "DB_USER"
    """Database username for the jobs database."""
    DB_PASSWORD = "DB_PASSWORD"  # noqa S105 - not a hardcoded password only the parameter name!
    """Database user password for the jobs database matching the provided user name."""
    DB_HOST = "DB_HOST"
    """Host where the jobs database is running."""
    DB_PORT = "DB_PORT"
    """Port where the jobs database is running."""
    DB_NAME = "DB_NAME"
    """Database name of the jobs database."""

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
    not_doc_unittest = Validator("ENV_FOR_DYNACONF", is_not_in=["documentation", "unittest"])

    settings.configure(ENVVAR_PREFIX_FOR_DYNACONF="OEO")
    utils = SettingValidationUtils()
    settings.validators.register(

        Validator(SettingKeys.OPENEO_VERSION.value, must_exist=True, when=not_doc),
        Validator(SettingKeys.AIRFLOW_HOST.value, must_exist=True, condition=utils.check_parse_url,
                  when=(not_doc_unittest and not_doc)),
        Validator(SettingKeys.AIRFLOW_OUTPUT.value, must_exist=True, when=not_doc),
        Validator(SettingKeys.AIRFLOW_DAGS.value, must_exist=True, condition=utils.check_create_folder, when=not_doc),
        Validator(SettingKeys.SYNC_DEL_DELAY.value, must_exist=True, is_type_of=int, condition=utils.check_positive_int,
                  when=not_doc),
        Validator(SettingKeys.SYNC_RESULTS_FOLDER.value, must_exist=True, condition=utils.check_create_folder,
                  when=not_doc),

        Validator(SettingKeys.RABBIT_HOST.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.RABBIT_PORT.value, must_exist=True, is_type_of=int, when=not_doc_unittest),
        Validator(SettingKeys.RABBIT_USER.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.RABBIT_PASSWORD.value, must_exist=True, when=not_doc_unittest),

        Validator(SettingKeys.DB_USER.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.DB_PASSWORD.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.DB_HOST.value, must_exist=True, when=not_doc_unittest),
        Validator(SettingKeys.DB_PORT.value, must_exist=True, is_type_of=int, when=not_doc_unittest),
        Validator(SettingKeys.DB_NAME.value, must_exist=True, when=not_doc_unittest),

        Validator(SettingKeys.LOG_DIR.value, must_exist=True, condition=utils.check_create_folder,
                  when=not_doc_unittest),
    )
    settings.validators.validate()
    LOGGER.info("Settings validated")
