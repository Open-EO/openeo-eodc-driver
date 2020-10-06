"""Prepare test environment and provide useful fixtures."""
from typing import Any

import pytest

from users.models import Base


@pytest.fixture(scope='session')
def model_base() -> Any:
    """Return database model Base."""
    return Base
