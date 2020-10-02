"""Prepare test environment and provide useful fixtures.

Set all environment variables needed and provide some fixture useful for different tests in this package.
"""
from os import environ
from typing import Any, Dict
from uuid import uuid4

import pytest

from processes.models import Base

environ["OEO_PROCESSES_GITHUB_URL"] = "https://raw.githubusercontent.com/Open-EO/openeo-processes/1.0.0/"


@pytest.fixture(scope='session')
def model_base() -> Any:
    """Return database model Base."""
    return Base


@pytest.fixture()
def user() -> Dict[str, Any]:
    """Return a basic user with a random id."""
    return {
        "id": str(uuid4())
    }
