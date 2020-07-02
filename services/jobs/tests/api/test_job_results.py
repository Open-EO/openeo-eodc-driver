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

    api_spec = {
        "info": {
            "stac_version": "0.9.0",
        },
    }

    @pytest.fixture()
    def method(self) -> str:
        return "get_results"

    @pytest.mark.parametrize(("job_status", "exception_func"), (
        (JobStatus.error, get_job_error_service_exception),
        (JobStatus.canceled, get_job_canceled_service_exception),
        (JobStatus.created, get_job_not_finished_exception),
        (JobStatus.queued, get_job_not_finished_exception),
        (JobStatus.running, get_job_not_finished_exception),
    ))
    def test_result_excpetions(self, db_session: Session, job_status: JobStatus, exception_func: Callable) -> None:
        job_service = get_configured_job_service(db_session, airflow=False)
        user = get_random_user()
        job_id = add_job(job_service, user=user)
        job_service.airflow.check_dag_status.return_value = (job_status, datetime.now())

        result = job_service.get_results(user=user, job_id=job_id, api_spec=self.api_spec)
        assert result == exception_func(user_id=user["id"], job_id=job_id)

    def test_get_results(self, db_session: Session) -> None:
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
            }
        }

    def test_not_existing_job(self, db_session: Session, method: str, **kwargs: Any) -> None:
        super(TestJobResults, self).test_not_existing_job(db_session, method, api_spec=self.api_spec)

    def test_not_authorized_for_job(self, db_session: Session, method: str, **kwargs: Any) -> None:
        super(TestJobResults, self).test_not_authorized_for_job(db_session, method, api_spec=self.api_spec)
