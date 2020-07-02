from os.path import isfile

import pytest
from nameko_sqlalchemy.database_session import Session

from jobs.models import Job
from tests.utils import get_configured_job_service, get_dag_path, get_random_user, load_json


@pytest.mark.usefixtures("set_job_data", "dag_folder")
class TestCreateJob:

    def test_basic(self, db_session: Session) -> None:
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
        assert isfile(get_dag_path(result['headers']['OpenEO-Identifier']))

        job_service.processes_service.put_user_defined.assert_called_once_with(
            user=user, process_graph_id="pg_id", **job_data["process"]
        )
        job_service.files_service.setup_jobs_result_folder.assert_called_once_with(
            user_id=user["id"], job_id=results_job_id)
        job_service.processes_service.get_all_predefined.assert_called_once()

# TODO invalid PG
