from os import environ
from typing import Any

import pytest

from processes.models import Base

environ["OEO_PROCESSES_GITHUB_URL"] = "https://raw.githubusercontent.com/Open-EO/openeo-processes/1.0.0-rc.1/"


@pytest.fixture(scope='session')
def model_base() -> Any:
    return Base
