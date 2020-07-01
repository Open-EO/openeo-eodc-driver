# Triggered before every pytest run to add the directory so that the service can be found
# by pytest

import sys
from os import environ
from os.path import abspath
from os.path import dirname

import pytest

root_dir = dirname(dirname(abspath(__file__)))
sys.path.append(root_dir)


@pytest.fixture()
def get_envs() -> None:
    environ['DEVELOPMENT'] = 'False'
