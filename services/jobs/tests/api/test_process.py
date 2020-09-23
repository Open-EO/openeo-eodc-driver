"""Test process job."""
import pytest
from nameko_sqlalchemy.database_session import Session

from jobs.dependencies.dag_handler import DagHandler
from tests.utils import add_job, get_configured_job_service, get_random_user
from .base import BaseCase


@pytest.mark.usefixtures("set_job_data", "dag_folder")
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

        result = job_service.process(user=user, job_id=job_id)
        assert result == {'code': 202, 'status': 'success'}
        dag_id = DagHandler().get_preparation_dag_id(job_id=job_id)
        job_service.airflow.trigger_dag.assert_called_once_with(dag_id=dag_id)
