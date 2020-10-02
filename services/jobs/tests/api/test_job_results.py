"""Test get job results."""
from datetime import datetime
from typing import Any, Callable

import pytest
from nameko_sqlalchemy.database_session import Session

from jobs.models import JobStatus
from tests.utils import add_job, get_configured_job_service, get_random_user
from .base import BaseCase
from .exceptions import get_job_canceled_service_exception, get_job_error_service_exception, \
    get_job_not_finished_exception


@pytest.mark.usefixtures("set_job_data", "dag_folder")
class TestJobResults(BaseCase):
    """Test the get_results method."""

    api_spec = {
        "servers": [
            {
                "url": 'https://openeo.eodc.eu/',
                "description": 'The URL to the EODC API',
            },
            {
                "url": "https://openeo.eodc.eu/v1.0",
                "description": "API version 1.0.0-rc.2"
            },
        ],
        "info": {
            "stac_version": "0.9.0",
        },
    }
    """Basic, required, API_SPECS."""

    @pytest.fixture()
    def method(self) -> str:
        """Return get_results - Method to be used in base test case is get_results."""
        return "get_results"

    @pytest.mark.parametrize(("job_status", "exception_func"), (
        (JobStatus.error, get_job_error_service_exception),
        (JobStatus.canceled, get_job_canceled_service_exception),
        (JobStatus.created, get_job_not_finished_exception),
        (JobStatus.queued, get_job_not_finished_exception),
        (JobStatus.running, get_job_not_finished_exception),
    ))
    def test_result_exceptions(self, db_session: Session, job_status: JobStatus, exception_func: Callable) -> None:
        """Check the correct exceptions are returned depending on the current job status."""
        job_service = get_configured_job_service(db_session, airflow=False)
        user = get_random_user()
        job_id = add_job(job_service, user=user)
        job_service.airflow.check_dag_status.return_value = (job_status, datetime.now())

        result = job_service.get_results(user=user, job_id=job_id, api_spec=self.api_spec)
        assert result == exception_func(user_id=user["id"], job_id=job_id)

    def test_get_results(self, db_session: Session) -> None:
        """Check getting results for a basic job works as expected."""
        job_service = get_configured_job_service(db_session, airflow=False)
        job_service.airflow.check_dag_status.return_value = (JobStatus.finished, datetime.now())
        user = get_random_user()
        job_id = add_job(job_service, user=user)

        result = job_service.get_results(user=user, job_id=job_id, api_spec=self.api_spec)
        assert result["status"] == "success"
        assets = result["data"].pop("assets")
        assert assets["sample-output.tif"]["href"].endswith("result/sample-output.tif")
        assert result == {
            "status": "success",
            "code": 200,
            "headers": {"Expires": "not given", "OpenEO-Costs": 0},
            "data": {
                'bbox': [1, 2, 3, 4],
                'description': 'some description',
                'geometry': {
                    'coordinates': [[[12, 34], [24, 89]]],
                    'type': 'Polygon'
                },
                'id': job_id,
                'properties': {'datetime': '2020-02-20T16:05:21Z'},
                'stac_version': '0.9.0',
                'status': 'finished',
                'title': 'evi_job_old',
                'type': 'Feature',
                'links': [{'rel': 'self', 'href': 'https://openeo.eodc.eu/v1.0/collections'}]
            }
        }

    def test_not_existing_job(self, db_session: Session, method: str, **kwargs: Any) -> None:
        """Check the correct exception is returned if the job does not exist.

        The get_results method need an additional parameter api_spec therefore it cannot directly be executed form the
        parent class.
        """
        super(TestJobResults, self).test_not_existing_job(db_session, method, api_spec=self.api_spec)

    def test_not_authorized_for_job(self, db_session: Session, method: str, **kwargs: Any) -> None:
        """Check the correct exception is returned if the user is not authorized.

        The get_results method need an additional parameter api_spec therefore it cannot directly be executed form the
        parent class.
        """
        super(TestJobResults, self).test_not_authorized_for_job(db_session, method, api_spec=self.api_spec)
