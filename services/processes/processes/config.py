# flake8: noqa
import os
import logging

LOGGER = logging.getLogger('standardlog')


class ProcessesConfiguration:
    def __init__(self, processes_github_url: str):
        self.processes_github_ul = processes_github_url

    def __repr__(self):
        return f"{self.__class__.__name__}(processes_github_url={self.processes_github_ul!r})"

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return False
        return self.processes_github_ul == other.processes_github_url

    def get_config_keys(self):
        return [
            # (name="githubUrl", env_var="PROCESS_GITHUB_URL", checker=HttpsUrlWithTrailingSlashChecker())
        ]

    @classmethod
    def load_from_environment(cls):
        processes_github_url = os.environ.get("PROCESSES_GITHUB_URL")

        if processes_github_url is None:
            raise OSError("Missing environment variable 'PROCESSES_GITHUB_URL'")
        if not processes_github_url.endswith("/"):
            raise ValueError("Environment variable 'PROCESSES_GITHUB_URL' has to end with a '/'."
                             "E.g.: https://raw.githubusercontent.com/Open-EO/openeo-processes/1.0.0-rc.1/")

        return cls(processes_github_url)


class RabbitConfiguration:

    def __init__(self, host: str, port: int, user: str = "rabbit_user", password: str = "rabbit_password") -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        logging.info(f"Rabbit config created: {self}")

    def __repr__(self):
        return (f"{self.__class__.__name__}"
                f"(host={self.host!r}, port={self.port!r}, user={self.user!r})")

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return False
        return (self.host, self.port, self.user, self.password) == (other.host, other.port, other.user, other.password)

    @classmethod
    def load_from_environment(cls):
        host = os.environ.get("RABBIT_HOST")
        port = os.environ.get("RABBIT_PORT")
        user = os.environ.get("RABBIT_USER")
        password = os.environ.get("RABBIT_PASSWORD")

        if host is None:
            raise OSError("Missing environment variable 'RABBIT_HOST'")
        if port is None:
            raise OSError("Missing environment variable 'RABBIT_PORT'")

        if user is None:
            logging.debug("Environment variable 'RABBIT_USER' not given - using default")
        if password is None:
            logging.debug("Environment variable 'RABBIT_PASSWORD' not given - using default")

        return cls(host=host, port=int(port), user=user, password=password)
