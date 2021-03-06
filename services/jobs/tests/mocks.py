"""Mocks and auxiliary data used in the tests."""
import glob
import os
import shutil
from datetime import datetime
from os.path import dirname, join
from typing import Any, Dict, List, NamedTuple, Optional, Tuple
from unittest.mock import MagicMock

from dynaconf import settings

from jobs.dependencies.dag_handler import DagHandler
from jobs.models import JobStatus

PG_OLD_REF: dict = {
    "status": "success",
    "code": 200,
    "data": {
        "deprecated": False,
        "summary": "Enhanced Vegetation Index",
        "parameters": [
            {
                "deprecated": False,
                "description": "Value from the red band.",
                "schema": {
                    "type": "number",
                    "minItems": 0
                },
                "experimental": False,
                "name": "red",
                "optional": False
            },
            {
                "deprecated": False,
                "description": "Value from the blue band.",
                "schema": {
                    "type": "number",
                    "minItems": 0
                },
                "experimental": False,
                "name": "blue",
                "optional": False
            },
            {
                "deprecated": False,
                "description": "Value from the near infrared band.",
                "schema": {
                    "type": "number",
                    "minItems": 0
                },
                "experimental": False,
                "name": "nir",
                "optional": False
            }
        ],
        "returns": {
            "description": "Computed EVI.",
            "schema": {
                "type": "number",
                "minItems": 0
            }
        },
        "description": "Computes the Enhanced Vegetation Index (EVI). It is computed with the following formula:"
                       " `2.5 * (NIR - RED) / (1 + NIR + 6*RED + -7.5*BLUE)`.",
        "process_graph": {
            "sub": {
                "process_id": "subtract",
                "arguments": {
                    "data": [
                        {
                            "from_parameter": "nir"
                        },
                        {
                            "from_parameter": "red"
                        }
                    ]
                }
            },
            "p1": {
                "process_id": "product",
                "arguments": {
                    "data": [
                        6,
                        {
                            "from_parameter": "red"
                        }
                    ]
                }
            },
            "p2": {
                "process_id": "product",
                "arguments": {
                    "data": [
                        -7.5,
                        {
                            "from_parameter": "blue"
                        }
                    ]
                }
            },
            "sum": {
                "process_id": "sum",
                "arguments": {
                    "data": [
                        1,
                        {
                            "from_parameter": "nir"
                        },
                        {
                            "from_node": "p1"
                        },
                        {
                            "from_node": "p2"
                        }
                    ]
                }
            },
            "div": {
                "process_id": "divide",
                "arguments": {
                    "data": [
                        {
                            "from_node": "sub"
                        },
                        {
                            "from_node": "sum"
                        }
                    ]
                }
            },
            "p3": {
                "process_id": "product",
                "arguments": {
                    "data": [
                        2.5,
                        {
                            "from_node": "div"
                        }
                    ]
                },
                "result": True
            }
        },
        "id": "test-pg",
        "exceptions": {
            "401": {
                "description": "Some error description",
                "http": 401,
                "message": "Your code failed because ..."
            },
            "402": {
                "description": "Some error description2",
                "http": 402,
                "message": "Your code failed because ... 2"
            }
        },
        "experimental": False,
        "categories": [
            "catA",
            "catB",
            "catC"
        ],
        "links": [
            {
                "type": "the type of this link",
                "href": "https://open-eo.github.io/openeo-api/#operation/describe-custom-process",
                "rel": "latest-version",
                "title": "the title of this link"
            },
            {
                "type": "the type of this link2",
                "href": "https://open-eo.github.io/openeo-api/#tag/Capabilities",
                "rel": "latest-version2",
                "title": "the title of this link2"
            }
        ]
    }
}
"""Full Process Graph."""


class MockedAirflowConnection(MagicMock):
    """Simple Mocked AirflowRestConnection.

    Currently only implementing some methods.
    """

    def unpause_dag(self, dag_id: str, unpause: bool = True) -> bool:
        """Return True."""
        return True

    def check_dag_status(self, dag_id: str) -> Tuple[Optional[JobStatus], Optional[datetime]]:
        """Return JobStatus.create, None."""
        return JobStatus.created, None


class MockedDagDomain(NamedTuple):
    """Mocked DagDomain."""

    filepath: str


class MockedDagWriter(MagicMock):
    """Simple mocked DagWriter."""

    def write_and_move_job(self, job_id: str, **kwargs: Any) -> None:
        """Create an empty dag with the correct name."""
        dag_file = os.path.join(settings.AIRFLOW_DAGS, f'dag_{job_id}_prep.py')
        open(dag_file, 'a').close()


class MockedProcessesService(MagicMock):
    """Mocked ProcessesService."""

    def get_user_defined(self, user_id: str, process_graph_id: str) -> dict:
        """Return fixed process graph."""
        return PG_OLD_REF

    def put_user_defined_pg(self, user_id: str, process_graph_id: str, **process: Any) -> Dict[str, Any]:
        """Return success dictionary."""
        return {
            'status': 'success',
            "code": 200,
        }


class MockedFilesService(MagicMock):
    """Simple mocked FileService."""

    def get_job_output(self, user_id: str, job_id: str, internal: bool = False) -> Dict[str, Any]:
        """Return success with sample-output paths."""
        # TODO update structure to reflect latest version of method
        job_folder = settings.JOB_FOLDER
        return {
            "status": "success",
            "code": 200,
            "data": {
                "file_list": [
                    os.path.join(job_folder, "result", "sample-output.tif")
                ],
                "metadata_file": os.path.join(job_folder, "result", "results_metadata.json")
            }
        }

    def setup_jobs_result_folder(self, user_id: str, job_id: str, job_run: Optional[str] = None) -> str:
        """Set up a new job run with results folder and return the path."""
        folder_name = self.get_new_job_run_folder_name()
        to_create = join(settings.JOB_FOLDER, folder_name)
        if not os.path.exists(to_create):
            os.makedirs(to_create)
        return to_create

    def get_job_run_folder_from_results(self, job_result_folder: str) -> str:
        """Get the absolute path to the job run folder form its results folder."""
        return dirname(job_result_folder)

    def get_new_job_run_folder_name(self) -> str:
        """Return folder name of new job run folder."""
        return f"jr-{datetime.utcnow().strftime('%Y%m%dT%H%M%S%f')}"

    def get_latest_job_run_folder_name(self, user_id: str, job_id: str) -> str:
        """Return newest job_run folder name."""
        latest_job_run = sorted(glob.glob(settings.JOB_FOLDER + '/*'))[-1]
        return latest_job_run.split(os.sep)[-1]

    def delete_old_job_runs(self, user_id: str, job_id: str) -> None:
        """Delete all job runs of a job but the latest."""
        job_runs = sorted(glob.glob(settings.JOB_FOLDER + '/*'))[:-1]
        for job_run in job_runs:
            shutil.rmtree(job_run)


class MockedDagHandler(MagicMock):
    """Mocked DagHandler."""

    original_dag_handler = DagHandler()
    """Reference to original - not mocked - DagHandler."""

    def get_preparation_dag_id(self, job_id: str) -> str:
        """Return original get_preparation_dag_id."""
        return self.original_dag_handler.get_preparation_dag_id(job_id)

    def get_all_dag_ids(self, job_id: str) -> List[str]:
        """Return original get_all_dag_ids."""
        return self.original_dag_handler.get_all_dag_ids(job_id=job_id)

    def remove_all_dags(self, job_id: str) -> None:
        """Execute original remove_all_dags."""
        return self.original_dag_handler.remove_all_dags(job_id=job_id)
