import pytest

from processes.models import Base


@pytest.fixture(scope='session')
def model_base():
    return Base

