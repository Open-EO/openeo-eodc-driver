"""Prepare test environment and provide useful fixtures.

Set all environment variables needed and provide some fixture useful for different tests in this package.
"""
import os
import shutil

import pytest
from _pytest.fixtures import FixtureRequest
from dynaconf import settings

from jobs.models import Base


def get_test_data_folder() -> str:
    """Return absolute path to test data folder."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def get_dags_folder() -> str:
    """Return absolute path to test dags folder."""
    return os.path.join(get_test_data_folder(), 'dags')


def get_sync_results_folder() -> str:
    """Return absolute path to sync-results folder."""
    return os.path.join(get_test_data_folder(), 'sync-results')


def get_test_job_folder() -> str:
    """Return path to specific job folder."""
    return os.path.join(get_test_data_folder(), 'jb-12345')


os.environ["ENV_FOR_DYNACONF"] = "unittest"

os.environ["OEO_OPENEO_VERSION"] = "v1.0"
os.environ["OEO_AIRFLOW_HOST"] = "http://airflow-webserver:8080"
os.environ["OEO_AIRFLOW_OUTPUT"] = get_test_data_folder()
os.environ["OEO_AIRFLOW_DAGS"] = get_dags_folder()
os.environ["OEO_SYNC_DEL_DELAY"] = "5"
os.environ["OEO_SYNC_RESULTS_FOLDER"] = get_sync_results_folder()
os.environ["OEO_CSW_SERVER"] = "http://localhost:8000"
os.environ["OEO_JOB_FOLDER"] = get_test_job_folder()
os.environ["OEO_WEKEO_STORAGE"] = "/usr/local/airflow/wekeo_storage"

@pytest.fixture()
def dag_folder(request: FixtureRequest) -> None:
    """Create dag folder and add finalizer to remove it again after running the test."""
    folder = get_dags_folder()
    if not os.path.isdir(folder):
        os.mkdir(folder)

    def fin() -> None:
        shutil.rmtree(folder)
    request.addfinalizer(fin)


@pytest.fixture(scope='session')
def model_base() -> Base:
    """Return database model Base."""
    return Base


@pytest.fixture()
def set_job_data(request: FixtureRequest) -> None:
    """Create sync-results and airflow-output folder and add finalizer to remove the folders after running the test."""
    # For sync job test
    if not os.path.isdir(settings.SYNC_RESULTS_FOLDER):
        os.makedirs(settings.SYNC_RESULTS_FOLDER)
    # this env var is used in the mocked files service
    job_results = os.path.join(settings.JOB_FOLDER, "result")
    if not os.path.isdir(job_results):
        os.makedirs(job_results)
        # Create empty file (mock job output)
        open(os.path.join(job_results, "sample-output.tif"), 'w').close()
        shutil.copyfile(
            os.path.join(get_test_data_folder(), "results_metadata.json"),
            os.path.join(job_results, "results_metadata.json")
        )

    def fin() -> None:
        shutil.rmtree(settings.JOB_FOLDER)
        shutil.rmtree(settings.SYNC_RESULTS_FOLDER)
    request.addfinalizer(fin)
