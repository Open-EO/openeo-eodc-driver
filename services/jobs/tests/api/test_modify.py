from datetime import datetime
from os.path import getmtime, isfile

import pytest
from nameko_sqlalchemy.database_session import Session

from tests.mocks import PG_OLD_REF
from tests.utils import add_job, get_configured_job_service, get_dag_path, get_random_user_id
from .base import BaseCase


@pytest.mark.usefixtures("set_job_data", "dag_folder")
class TestModifyJob(BaseCase):

    @pytest.fixture()
    def method(self) -> str:
        return "get"

    def test_modify_job(self, db_session: Session) -> None:
        """Test modification of simple Job Attributes"""
        job_service = get_configured_job_service(db_session)
        user_id = get_random_user_id()
        job_id = add_job(job_service, user_id=user_id)
        initial_dag_file_time = getmtime(get_dag_path(job_id))

        job_args = {
            'title': 'New title',
            'description': 'New description',
            'plan': 'new plan',
            'budget': 1.28,
        }
        result = job_service.modify(user_id=user_id, job_id=job_id, **job_args)
        assert result == {'code': 204, 'status': 'success'}
        # Check dag file was not modified
        assert isfile(get_dag_path(job_id))
        assert initial_dag_file_time == getmtime(get_dag_path(job_id))

        job_args.update({'status': 'created'})
        result = job_service.get(user_id=user_id, job_id=job_id)
        assert result['status'] == 'success'
        assert datetime.strptime(result['data'].pop('created'), '%Y-%m-%dT%H:%M:%S.%f')
        assert result['data'].pop('id').startswith('jb-')
        assert result['data'].pop('process') == PG_OLD_REF['data']
        assert result == {'code': 200,
                          'data': job_args,
                          'status': 'success'}

    def test_modify_job_pg(self, db_session: Session) -> None:
        """Test modification of a job's process graph"""
        job_service = get_configured_job_service(db_session)
        user_id = get_random_user_id()
        job_id = add_job(job_service, user_id=user_id)
        initial_dag_file_time = getmtime(get_dag_path(job_id))

        job_args: dict = {'process': {'process_graph': {}}}
        result = job_service.modify(user_id=user_id, job_id=job_id, **job_args)
        assert result == {'code': 204, 'status': 'success'}
        # Check dag file was updated
        assert isfile(get_dag_path(job_id))
        assert initial_dag_file_time < getmtime(get_dag_path(job_id))

        result = job_service.get(user_id=user_id, job_id=job_id)
        assert result['status'] == 'success'
        assert datetime.strptime(result['data'].pop('created'), '%Y-%m-%dT%H:%M:%S.%f')
        assert result['data'].pop('id').startswith('jb-')
        result['data'].pop('process')  # is returned from MockedProcessesService > always returns PG_OLD_REF
        assert result == {'code': 200,
                          'data': {'budget': 1624.78,
                                   'description': 'some description',
                                   'plan': 'plan',
                                   'status': 'created',
                                   'title': 'evi_job_old'},
                          'status': 'success'}
