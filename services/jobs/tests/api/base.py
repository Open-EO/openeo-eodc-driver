from typing import Any, Callable

from nameko_sqlalchemy.database_session import Session

from jobs.service import JobService
from .exceptions import get_missing_resource_service_exception, get_not_authorized_service_exception
from ..utils import add_job, get_configured_job_service, get_random_job_id, get_random_user_id


class BaseCase:

    def get_method(self, service: JobService, method: str) -> Callable:
        mapper = {
            "get": service.get,
            "modify": service.modify,
            "delete": service.delete,
            "process": service.process,
            "get_results": service.get_results,
        }
        if method not in mapper:
            raise NotImplementedError(f"The method {method} is currently not supported")
        return mapper[method]

    def test_not_existing_job(self, db_session: Session, method: str, **kwargs: Any) -> None:
        job_service = get_configured_job_service(db_session)
        user_id = get_random_user_id()
        job_id = get_random_job_id()

        result = self.get_method(job_service, method)(user_id=user_id, job_id=job_id, **kwargs)
        assert result == get_missing_resource_service_exception(user_id=user_id, job_id=job_id)

    def test_not_authorized_for_job(self, db_session: Session, method: str, **kwargs: Any) -> None:
        job_service = get_configured_job_service(db_session)
        user_id = get_random_user_id()
        job_id = add_job(job_service, user_id=user_id)
        other_user_id = get_random_user_id()

        result = self.get_method(job_service, method)(user_id=other_user_id, job_id=job_id, **kwargs)
        assert result == get_not_authorized_service_exception(user_id=other_user_id, job_id=job_id)
