"""Prepare test environment and provide useful fixtures."""
import os
from typing import Any

import pytest

from users.models import Base


os.environ["ENV_FOR_DYNACONF"] = "unittest"


@pytest.fixture(scope='session')
def model_base() -> Any:
    """Return database model Base."""
    return Base
