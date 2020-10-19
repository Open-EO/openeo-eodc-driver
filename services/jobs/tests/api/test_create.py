"""Test create jobs."""
from os.path import isfile

import pytest
from nameko_sqlalchemy.database_session import Session

from jobs.dependencies.dag_handler import DagHandler
from jobs.models import Job
from tests.utils import get_configured_job_service, get_random_user, load_json


@pytest.mark.usefixtures("job_folder", "dag_folder")
class TestCreateJob:
    """Tests the create job method."""

    def test_basic(self, db_session: Session) -> None:
        """Check creating a basic job works as expected."""
        job_service = get_configured_job_service(db_session, files=False)
        user = get_random_user()

        job_data = load_json('pg')
        # here: Job is added to database but dag file is not created (mocked away, as it happens in a separate pkg)
        result = job_service.create(user=user, **job_data)

        assert result['status'] == 'success'
        assert result['code'] == 201
        assert result['headers']['Location'].startswith('jobs/jb-')
        assert result['headers']['OpenEO-Identifier'].startswith('jb-')
        results_job_id = result['headers']['OpenEO-Identifier']
        assert results_job_id == result['headers']['Location'][5:]
        assert db_session.query(Job).filter(Job.user_id == user["id"]).filter(Job.id == results_job_id).count() == 1
        dag_handler = DagHandler()
        assert not isfile(dag_handler.get_dag_path_from_id(
            dag_handler.get_preparation_dag_id(job_id=result['headers']['OpenEO-Identifier'])))

        job_service.processes_service.put_user_defined.assert_called_once_with(
            user=user, process_graph_id="pg_id", **job_data["process"]
        )

# TODO invalid PG
