"""Test process job."""
from datetime import datetime
from os import listdir
from os.path import isdir, isfile, join

import pytest
from dynaconf import settings
from nameko_sqlalchemy.database_session import Session

from jobs.dependencies.dag_handler import DagHandler
from jobs.models import JobStatus
from tests.utils import add_job, get_configured_job_service, get_random_user
from .base import BaseCase
from .exceptions import get_cannot_start_processing


@pytest.mark.usefixtures("dag_folder", "job_folder")
class TestProcessJob(BaseCase):
    """Test the process job method."""

    @pytest.fixture()
    def method(self) -> str:
        """Return process - Method to be used in base test case is process."""
        return "process"

    def test_start_processing_job(self, db_session: Session) -> None:
        """Test start processing a created job."""
        job_service = get_configured_job_service(db_session)
        user = get_random_user()
        job_id = add_job(job_service, user=user)
        dag_handler = DagHandler()

        result = job_service.process(user=user, job_id=job_id)

        assert result == {'code': 202, 'status': 'success'}
        assert isfile(dag_handler.get_dag_path_from_id(dag_handler.get_preparation_dag_id(job_id=job_id)))
        # one job run should be present
        assert len([d for d in listdir(settings.JOB_FOLDER) if isdir(join(settings.JOB_FOLDER, d))]) == 1
        job_service.processes_service.get_all_predefined.assert_called_once()
        dag_id = dag_handler.get_preparation_dag_id(job_id=job_id)
        job_service.airflow.trigger_dag.assert_called_once_with(dag_id=dag_id)

    @pytest.mark.parametrize("job_status", (JobStatus.created, JobStatus.canceled, JobStatus.error))
    def test_multiple_job_runs(self, db_session: Session, job_status: JobStatus) -> None:
        """Try to run the same job multiple times."""
        job_service = get_configured_job_service(db_session, airflow=False)
        user = get_random_user()
        job_id = add_job(job_service, user=user)
        dag_handler = DagHandler()
        job_service.airflow.check_dag_status.return_value = (job_status, datetime.now())
        num_runs = 5

        results = [job_service.process(user=user, job_id=job_id) for _ in range(num_runs)]

        assert all([res == {'code': 202, 'status': 'success'} for res in results])
        assert isfile(dag_handler.get_dag_path_from_id(dag_handler.get_preparation_dag_id(job_id=job_id)))
        # there should be a job run folder for each job run
        assert len([d for d in listdir(settings.JOB_FOLDER) if isdir(join(settings.JOB_FOLDER, d))]) == num_runs

    @pytest.mark.parametrize("job_status", (JobStatus.queued, JobStatus.running))
    def test_multiple_job_runs_exception(self, db_session: Session, job_status: JobStatus) -> None:
        """Test exception if running/queued job is triggered again."""
        job_service = get_configured_job_service(db_session, airflow=False)
        user = get_random_user()
        job_id = add_job(job_service, user=user)
        dag_handler = DagHandler()

        job_service.airflow.check_dag_status.return_value = (JobStatus.created, datetime.now())
        result1 = job_service.process(user=user, job_id=job_id)

        job_service.airflow.check_dag_status.return_value = (job_status, datetime.now())
        result2 = job_service.process(user=user, job_id=job_id)

        assert result1 == {'code': 202, 'status': 'success'}
        assert result2 == get_cannot_start_processing(user["id"], job_id, str(job_status))
        assert isfile(dag_handler.get_dag_path_from_id(dag_handler.get_preparation_dag_id(job_id=job_id)))
        # one job run should be present
        assert len([d for d in listdir(settings.JOB_FOLDER) if isdir(join(settings.JOB_FOLDER, d))]) == 1
