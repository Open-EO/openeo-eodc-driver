"""Test modify job."""
from datetime import datetime

import pytest
from nameko_sqlalchemy.database_session import Session

from jobs.models import JobStatus
from tests.mocks import PG_OLD_REF
from tests.utils import add_job, get_configured_job_service, get_random_user
from .base import BaseCase
from .exceptions import get_job_locked_exception


@pytest.mark.usefixtures("job_folder", "dag_folder")
class TestModifyJob(BaseCase):
    """Test modify methode."""

    @pytest.fixture()
    def method(self) -> str:
        """Return modify - Method to be used in base test case is modify."""
        return "modify"

    def test_modify_job(self, db_session: Session) -> None:
        """Test modification of simple job attributes."""
        job_service = get_configured_job_service(db_session)
        user = get_random_user()
        job_id = add_job(job_service, user=user)

        job_args = {
            'title': 'New title',
            'description': 'New description',
            'plan': 'new plan',
            'budget': 1.28,
        }
        result = job_service.modify(user=user, job_id=job_id, **job_args)
        assert result == {'code': 204, 'status': 'success'}

        job_args.update({'status': 'created'})
        result = job_service.get(user=user, job_id=job_id)
        assert result['status'] == 'success'
        assert datetime.strptime(result['data'].pop('created'), '%Y-%m-%dT%H:%M:%SZ')
        assert result['data'].pop('id').startswith('jb-')
        assert result['data'].pop('process') == PG_OLD_REF['data']
        assert result == {'code': 200,
                          'data': job_args,
                          'status': 'success'}

    def test_modify_job_pg(self, db_session: Session) -> None:
        """Test modification of a job's process graph."""
        job_service = get_configured_job_service(db_session)
        user = get_random_user()
        job_id = add_job(job_service, user=user)

        job_args: dict = {'process': {'process_graph': {}}}
        result = job_service.modify(user=user, job_id=job_id, **job_args)
        assert result == {'code': 204, 'status': 'success'}

        result = job_service.get(user=user, job_id=job_id)
        assert result['status'] == 'success'
        assert datetime.strptime(result['data'].pop('created'), '%Y-%m-%dT%H:%M:%SZ')
        assert result['data'].pop('id').startswith('jb-')
        result['data'].pop('process')  # is returned from MockedProcessesService > always returns PG_OLD_REF
        assert result == {'code': 200,
                          'data': {'budget': 1624.78,
                                   'description': 'some description',
                                   'plan': 'plan',
                                   'status': 'created',
                                   'title': 'evi_job_old'},
                          'status': 'success'}

    @pytest.mark.parametrize("job_status", (JobStatus.running, JobStatus.queued))
    def test_job_active_error(self, db_session: Session, job_status: JobStatus) -> None:
        """Test the correct error is thrown if the user tries to modify an active job."""
        job_service = get_configured_job_service(db_session, airflow=False)
        job_service.airflow.check_dag_status.return_value = (job_status, datetime.now())
        user = get_random_user()
        job_id = add_job(job_service, user=user)

        job_args = {
            'title': 'New title',
        }
        result = job_service.modify(user=user, job_id=job_id, **job_args)
        assert result == get_job_locked_exception(user_id=user["id"], job_id=job_id, job_status=str(job_status))
