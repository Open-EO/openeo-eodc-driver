from typing import Any

import pytest

from processes.models import Base


@pytest.fixture(scope='session')
def model_base() -> Any:
    return Base
