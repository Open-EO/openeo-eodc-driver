import os
import shutil

import pytest

from jobs.models import Base


def get_test_data_folder():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def get_dags_folder():
    return os.path.join(get_test_data_folder(), 'dags')


@pytest.fixture()
def dag_folder(request):
    folder = get_dags_folder()
    if not os.path.isdir(folder):
        os.mkdir(folder)

    def fin():
        shutil.rmtree(folder)
    request.addfinalizer(fin)
    os.environ['AIRFLOW_DAGS'] = folder


@pytest.fixture(scope='session')
def model_base():
    return Base


@pytest.fixture()
def set_job_data():
    os.environ['JOB_DATA'] = ''
    os.environ['SYNC_RESULTS_FOLDER'] = os.path.join(get_test_data_folder(), 'sync-results')
    
    # For sync job test
    if not os.path.isdir(os.environ['SYNC_RESULTS_FOLDER']):
        os.makedirs(os.environ['SYNC_RESULTS_FOLDER'])
    os.environ['SYNC_DEL_DELAY'] = '5' # seconds
    os.environ['JOB_FOLDER'] = os.path.join(get_test_data_folder(), 'jb-12345') # this env var is used in the mocked files service
    if not os.path.isdir(os.environ['JOB_FOLDER']):
        os.makedirs(os.environ['JOB_FOLDER'])
        # Create empty file (mock job output)
        open(os.path.join(os.environ['JOB_FOLDER'], "sample-output.tif"), 'w').close()


# should not be needed -> not a unittest!
@pytest.fixture()
def csw_server():
    os.environ['CSW_SERVER'] = 'http://localhost:8000'
