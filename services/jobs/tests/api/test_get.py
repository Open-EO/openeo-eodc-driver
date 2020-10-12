"""Test get job."""
from datetime import datetime

import pytest
from nameko_sqlalchemy.database_session import Session

from tests.mocks import PG_OLD_REF
from tests.utils import add_job, get_configured_job_service, get_random_user
from .base import BaseCase


@pytest.mark.usefixtures("job_folder", "dag_folder")
class TestGetJob(BaseCase):
    """Test the get methods for a job / all jobs."""

    @pytest.fixture()
    def method(self) -> str:
        """Return get - Method to be used in base test case is get."""
        return "get"

    def test_add_and_get(self, db_session: Session) -> None:
        """Check getting details about a job works as expected."""
        job_service = get_configured_job_service(db_session)
        user = get_random_user()
        job_id = add_job(job_service, user=user)

        result = job_service.get(user=user, job_id=job_id)
        assert result['status'] == 'success'
        # Datetime changes for each test -> cannot be compared to fixed value
        assert datetime.strptime(result['data'].pop('created'), '%Y-%m-%dT%H:%M:%SZ')
        assert result['data'].pop('process') == PG_OLD_REF['data']
        assert result == {'code': 200,
                          'data': {
                              'id': job_id,
                              'budget': 1624.78,
                              'description': 'some description',
                              'plan': 'plan',
                              'status': 'created',
                              'title': 'evi_job_old'},
                          'status': 'success'}

    def test_get_all_jobs(self, db_session: Session) -> None:
        """Check getting all jobs works as expected."""
        job_service = get_configured_job_service(db_session)
        user = get_random_user()
        job_id = add_job(job_service, user=user)
        job_id_update = add_job(job_service, user=user, json_name='job_update_pg')

        # Get jobs
        result = job_service.get_all(user=user)
        assert result['status'] == 'success'
        # Datetime changes for each test -> cannot be compared to fixed value
        assert datetime.strptime(result['data']['jobs'][0].pop('created'), '%Y-%m-%dT%H:%M:%SZ')
        assert datetime.strptime(result['data']['jobs'][1].pop('created'), '%Y-%m-%dT%H:%M:%SZ')
        assert result == {'code': 200,
                          'data': {
                              'jobs': [{
                                  'id': job_id,
                                  'status': 'created',
                                  'budget': 1624.78,
                                  'description': 'some description',
                                  'plan': 'plan',
                                  'title': 'evi_job_old',
                              }, {
                                  'id': job_id_update,
                                  'status': 'created'
                              }],
                              'links': [],
                          },
                          'status': 'success',
                          }

    def test_get_all_empty(self, db_session: Session) -> None:
        """Check getting all jobs when no jobs exist."""
        job_service = get_configured_job_service(db_session)
        user = get_random_user()

        result = job_service.get_all(user=user)
        assert result == {
            "status": "success",
            "code": 200,
            "data": {
                "jobs": [],
                "links": [],
            }
        }
