from os.path import isfile

import pytest
from nameko_sqlalchemy.database_session import Session

from jobs.models import Job
from tests.utils import add_job, get_configured_job_service, get_random_user
from .base import BaseCase


@pytest.mark.usefixtures("set_job_data", "dag_folder")
class TestDeleteJob(BaseCase):

    @pytest.fixture()
    def method(self) -> str:
        return "delete"

    def test_delete_basic(self, db_session: Session) -> None:
        job_service = get_configured_job_service(db_session)
        user = get_random_user()
        job_id = add_job(job_service, user=user)
        assert db_session.query(Job).filter_by(user_id=user["id"]).filter_by(id=job_id).count() == 1

        result = job_service.delete(user=user, job_id=job_id)
        assert result == {"status": "success", "code": 204}

        # Check everything is deleted which should be deleted
        job_service.files_service.delete_complete_job.assert_called_once_with(user_id=user["id"], job_id=job_id)
        for dag_id in self.dag_handler.get_all_dag_ids(job_id=job_id):
            job_service.airflow.delete_dag.assert_any_call(dag_id=dag_id)
            assert not isfile(self.dag_handler.get_dag_path_from_id(dag_id=dag_id))
        assert db_session.query(Job).filter_by(user_id=user["id"]).filter_by(id=job_id).count() == 0

    def test_stop_running_job(self, db_session: Session) -> None:
        pass  # TODO implement
