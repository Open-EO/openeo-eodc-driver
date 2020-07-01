from typing import Any, Dict


def get_missing_resource_service_exception(user_id: str, job_id: str) -> Dict[str, Any]:
    return {
        "status": "error",
        "service": "jobs",
        "code": 400,
        "user_id": user_id,
        "msg": f"The job with id '{job_id}' does not exist.",
        "internal": False,
        "links": ["#tag/Job-Management/paths/~1data/get"],
    }


def get_not_authorized_service_exception(user_id: str, job_id: str) -> Dict[str, Any]:
    return {
        "status": "error",
        "service": "jobs",
        "code": 401,
        "user_id": user_id,
        "msg": f"You are not allowed to access the job {job_id}.",
        "internal": False,
        "links": ["#tag/Job-Management/paths/~1data/get"],
    }


def get_job_error_service_exception(user_id: str, job_id: str) -> Dict[str, Any]:
    return {
        "status": "error",
        "service": "jobs",
        "code": 424,
        "user_id": user_id,
        "msg": None,
        "internal": False,
        "links": [],
    }


def get_job_canceled_service_exception(user_id: str, job_id: str) -> Dict[str, Any]:
    return {
        "status": "error",
        "service": "jobs",
        "code": 400,
        "user_id": user_id,
        "msg": f"Job {job_id} was canceled.",
        "internal": False,
        "links": [],
    }


def get_job_not_finished_exception(user_id: str, job_id: str) -> Dict[str, Any]:
    return {
        "status": "error",
        "service": "jobs",
        "code": 400,
        "user_id": user_id,
        "msg": f"Job {job_id} is not yet finished. Results cannot be accessed.",
        "internal": False,
        "links": [],
    }


def get_job_locked_exception(user_id: str, job_id: str, job_status: str) -> Dict[str, Any]:
    return {
        "status": "error",
        "service": "jobs",
        "code": 400,
        "user_id": user_id,
        "msg": f"Job {job_id} is currently {job_status} and cannot be modified",
        "internal": False,
        "links": [],
    }
