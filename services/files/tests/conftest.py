# Triggered before every pytest run to add the directory so that the service can be found
# by pytest
import os
import shutil
import sys
from os.path import abspath
from os.path import dirname

import pytest
from nameko.testing.services import worker_factory

from files.service import FilesService

root_dir = dirname(dirname(abspath(__file__)))
sys.path.append(root_dir)

service = worker_factory(FilesService)


@pytest.fixture()
def file_service():
    return service


def get_data_folder():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def get_input_folder():
    return os.path.join(get_data_folder(), 'input')


def get_tmp_folder():
    return os.path.join(get_data_folder(), 'tmp')


def get_filesystem_folder():
    return os.path.join(get_data_folder(), 'file-system')


os.environ['OPENEO_FILES_DIR'] = get_filesystem_folder()


@pytest.fixture()
def filesystem_folder():
    return get_filesystem_folder()


@pytest.fixture()
def tmp_folder(request):
    folder = get_tmp_folder()
    if not os.path.isdir(folder):
        os.makedirs(folder)

    def fin():
        if os.path.isdir(folder):
            shutil.rmtree(folder)
    request.addfinalizer(fin)

    return folder


@pytest.fixture()
def input_folder():
    return get_input_folder()


@pytest.fixture()
def user_folder(request):
    folder = os.path.join(get_filesystem_folder(), 'test-user')
    service.setup_user_folder(user_id='test-user')

    def fin():
        shutil.rmtree(folder)
    request.addfinalizer(fin)
    return folder


@pytest.fixture()
def user_id():
    return 'test-user'
