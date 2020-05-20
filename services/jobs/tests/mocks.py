import os
from datetime import datetime
from typing import Tuple, Optional
from unittest.mock import MagicMock

from jobs.models import JobStatus

PG_OLD_REF = {
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
        "description": "Computes the Enhanced Vegetation Index (EVI). It is computed with the following formula: `2.5 * (NIR - RED) / (1 + NIR + 6*RED + -7.5*BLUE)`.",
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


class MockedAirflowConnection:

    def __init__(self):
        pass

    def unpause_dag(self, job_id: str, unpause: bool = True) -> bool:
        return True

    def trigger_dag(self, job_id: str) -> bool:
        return True

    def check_dag_status(self, job_id: str) -> Tuple[Optional[JobStatus], Optional[datetime]]:
        return JobStatus.created, None

    def delete_dag(self, job_id: str) -> bool:
        return True


class MockedDagDomain:

    def __init__(self, filepath):
        self.filepath = filepath


class MockedDagWriter(MagicMock):

    def write_and_move_job(self, job_id, **kwargs):
        dag_file = os.path.join(os.environ['AIRFLOW_DAGS'], f'dag_{job_id}.py')
        open(dag_file, 'a').close()


class MockedProcessesService(MagicMock):

    def get_user_defined(self, user_id, process_graph_id):
        return PG_OLD_REF

    def put_user_defined_pg(self, user_id, process_graph_id, **process):
        return {
            'status': 'success',
            "code": 200,
        }
