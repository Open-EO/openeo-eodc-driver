from nameko_sqlalchemy.database_session import Session

from tests.utils import get_configured_job_service, get_random_user


class TestEstimateJob:

    def test_default_estimates(self, db_session: Session) -> None:
        job_service = get_configured_job_service(db_session)
        user = get_random_user()
        result = job_service.estimate(user=user, job_id='test_job')
        assert result == {
            "status": "success",
            "code": 200,
            "data": {
                "costs": 0,
            },
        }
