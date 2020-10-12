"""Prepare test environment and provide useful fixtures.

Set all environment variables needed and provide some fixture useful for different tests in this package.
"""
import os
import shutil
import sys
from os.path import abspath
from os.path import dirname
from typing import Any, Dict, Tuple
from uuid import uuid4

import pytest
from _pytest.fixtures import FixtureRequest


# Triggered before every pytest run to add the directory so that the service can be found by pytest
root_dir = dirname(dirname(abspath(__file__)))
sys.path.append(root_dir)

os.environ["ENV_FOR_DYNACONF"] = "unittest"


def get_data_folder() -> str:
    """Get path to data folder for tests."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def get_input_folder() -> str:
    """Get path to data input folder for tests."""
    return os.path.join(get_data_folder(), 'input')


def get_tmp_folder() -> str:
    """Get path to data tmp folder for tests."""
    return os.path.join(get_data_folder(), 'tmp')


def get_filesystem_folder() -> str:
    """Get data file system folder for tests."""
    return os.path.join(get_data_folder(), 'file-system')


os.environ['OEO_OPENEO_FILES_DIR'] = get_filesystem_folder()
os.environ['OEO_UPLOAD_TMP_DIR'] = get_tmp_folder()


@pytest.fixture()
def filesystem_folder() -> str:
    """Fixture to get data file system folder for tests."""
    return get_filesystem_folder()


@pytest.fixture()
def tmp_folder(request: FixtureRequest) -> str:
    """Fixture to get path to data tmp folder for tests."""
    folder = get_tmp_folder()
    if not os.path.isdir(folder):
        os.makedirs(folder)

    def fin() -> None:
        if os.path.isdir(folder):
            shutil.rmtree(folder)
    request.addfinalizer(fin)

    return folder


@pytest.fixture()
def input_folder() -> str:
    """Fixture to get path to data input folder for tests."""
    return get_input_folder()


def generate_random_id() -> str:
    """Return random id as string."""
    return str(uuid4())


def random_user_id() -> str:
    """Return random user id as string."""
    return generate_random_id()


@pytest.fixture()
def random_user() -> Dict[str, Any]:
    """Return random user object with id only."""
    return {
        "id": generate_random_id()
    }


def create_user_folder(user_id: str) -> str:
    """Create folder structure for given user."""
    folder = os.path.join(get_filesystem_folder(), user_id)
    dirs_to_create = [os.path.join(folder, dir_name) for dir_name in ["files", "jobs"]]

    for d in dirs_to_create:
        if not os.path.exists(d):
            os.makedirs(d)
    return folder


@pytest.fixture()
def user_id_folder(request: FixtureRequest) -> Tuple[str, str]:
    """Create return a test user folder and the fitting user_id as Tuple.

    A finalizer is added to remove the created user folder at the end of the test.
    """
    user_id = "test-user"
    folder = create_user_folder(user_id)

    def fin() -> None:
        shutil.rmtree(folder)
    request.addfinalizer(fin)

    return folder, user_id


@pytest.fixture()
def user_folder(request: FixtureRequest) -> str:
    """Create and return a test user folder.

    The user id is set to 'test-user'.
    A finalizer is added to remove the created user folder at the end of the test.
    """
    user_id = "test-user"
    folder = create_user_folder(user_id)

    def fin() -> None:
        shutil.rmtree(folder)
    request.addfinalizer(fin)

    return folder


@pytest.fixture()
def upload_file() -> str:
    """Return path to a local test file which can be uploaded."""
    return os.path.join(get_input_folder(), 'upload.txt')
