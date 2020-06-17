import os
import shutil

import pytest
from _pytest.fixtures import FixtureRequest
from dynaconf import settings

from jobs.models import Base


def get_test_data_folder() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def get_dags_folder() -> str:
    return os.path.join(get_test_data_folder(), 'dags')


def get_sync_results_folder() -> str:
    return os.path.join(get_test_data_folder(), 'sync-results')


def get_test_job_folder() -> str:
    return os.path.join(get_test_data_folder(), 'jb-12345')


os.environ["OEO_GATEWAY_URL"] = "http://0.0.0.0:3000/v1.0"
os.environ["OEO_AIRFLOW_HOST"] = "http://airflow-webserver:8080"
os.environ["OEO_JOB_DATA"] = get_test_data_folder()
os.environ["OEO_AIRFLOW_DAGS"] = get_dags_folder()
os.environ["OEO_SYNC_DEL_DELAY"] = "5"
os.environ["OEO_SYNC_RESULTS_FOLDER"] = get_sync_results_folder()

# os.environ["OEO_CSW_SERVER"] = "http://localhost:8000"
os.environ["OEO_JOB_FOLDER"] = get_test_job_folder()


@pytest.fixture()
def dag_folder(request: FixtureRequest) -> None:
    folder = get_dags_folder()
    if not os.path.isdir(folder):
        os.mkdir(folder)

    def fin() -> None:
        shutil.rmtree(folder)
    request.addfinalizer(fin)


@pytest.fixture(scope='session')
def model_base() -> Base:
    return Base


@pytest.fixture()
def set_job_data(request: FixtureRequest) -> None:
    # For sync job test
    if not os.path.isdir(settings.SYNC_RESULTS_FOLDER):
        os.makedirs(settings.SYNC_RESULTS_FOLDER)
    # this env var is used in the mocked files service
    if not os.path.isdir(settings.JOB_FOLDER):
        os.makedirs(settings.JOB_FOLDER)
        # Create empty file (mock job output)
        open(os.path.join(settings.JOB_FOLDER, "sample-output.tif"), 'w').close()

    def fin() -> None:
        shutil.rmtree(settings.JOB_FOLDER)
        shutil.rmtree(settings.SYNC_RESULTS_FOLDER)
    request.addfinalizer(fin)
