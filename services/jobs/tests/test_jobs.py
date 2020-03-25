# import os
# import pytest
from nameko.testing.services import worker_factory
from jobs.service import JobService, JobLocked, ServiceException
from jobs.models import Job
from unittest import mock


@mock.patch('jobs.service.Airflow.check_dag_status')
@mock.patch('jobs.service.Job')
@mock.patch('jobs.service.DatabaseSession')  # .query.filter_by.order_by.all')
def test_get_all(mock_db, mock_job, mock_check_dag_status):

    class MockJob(object):
        def __init__(self, identifier):
            self.id = identifier

    mock_job.return_value = MockJob('1234')

    class MockQuery():
        def filter_by(self, user_id):
            return self

        def order_by(self, created_at):
            return self

        def all(self):
            return [mock_job]

    class MockDatabaseSession(object):
        def query(self):
            return MockQuery

    mock_check_dag_status.return_value = 'test_status'

    service = worker_factory(JobService)
    result = service.get_all('user_id')

    assert result == \
        {
            "status": "success",
            "code": 200,
            "data": {
                "jobs": [
                    {
                        "id": "1234",
                        "status": "test_status",
                        "submitted": "2020-01-01"
                    },
                ],
                "links": []
            }
        }
