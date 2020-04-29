import json
import os

import pytest
from nameko.testing.services import worker_factory

from processes.models import ProcessGraph
from processes.service import ProcessesService


def load_process_graph_json():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "process_graph.json")
    with open(json_path) as f:
        return json.load(f)


@pytest.mark.parametrize("process", ["absolute",
                                     "add",
                                     "add_dimension",
                                     "aggregate_spatial",
                                     "aggregate_spatial_binary",
                                     "aggregate_temporal",
                                     "all",
                                     "and",
                                     "any",
                                     "apply",
                                     "apply_dimension",
                                     "apply_kernel",
                                     "arccos",
                                     "arcosh",
                                     "arcsin",
                                     "arctan",
                                     "arctan2",
                                     "array_apply",
                                     "array_contains",
                                     "array_element",
                                     "array_filter",
                                     "array_find",
                                     "array_labels",
                                     "arsinh",
                                     "artanh",
                                     "between",
                                     "ceil",
                                     "clip",
                                     "cos",
                                     "cosh",
                                     "count",
                                     "create_raster_cube",
                                     "cummax",
                                     "cummin",
                                     "cumproduct",
                                     "cumsum",
                                     "debug",
                                     "dimension_labels",
                                     "divide",
                                     "drop_dimension",
                                     "e",
                                     "eq",
                                     "exp",
                                     "extrema",
                                     "filter_bands",
                                     "filter_bbox",
                                     "filter_labels",
                                     "filter_spatial",
                                     "filter_temporal",
                                     "first",
                                     "floor",
                                     "gt",
                                     "gte",
                                     "if",
                                     "int",
                                     "is_nan",
                                     "is_nodata",
                                     "is_valid",
                                     "last",
                                     "linear_scale_range",
                                     "ln",
                                     "load_collection",
                                     "load_result",
                                     "load_uploaded_files",
                                     "log",
                                     "lt",
                                     "lte",
                                     "mask",
                                     "mask_polygon",
                                     "max",
                                     "mean",
                                     "median",
                                     "merge_cubes",
                                     "min",
                                     "mod",
                                     "multiply",
                                     "ndvi",
                                     "neq",
                                     "normalized_difference",
                                     "not",
                                     "or",
                                     "order",
                                     "pi",
                                     "power",
                                     "product",
                                     "quantiles",
                                     "rearrange",
                                     "reduce_dimension",
                                     "reduce_dimension_binary",
                                     "rename_dimension",
                                     "rename_labels",
                                     "resample_cube_spatial",
                                     "resample_cube_temporal",
                                     "resample_spatial",
                                     "round",
                                     "run_udf",
                                     "run_udf_externally",
                                     "save_result",
                                     "sd",
                                     "sgn",
                                     "sin",
                                     "sinh",
                                     "sort",
                                     "sqrt",
                                     "subtract",
                                     "sum",
                                     "tan",
                                     "tanh",
                                     "text_begins",
                                     "text_contains",
                                     "text_ends",
                                     "text_merge",
                                     "trim_cube",
                                     "variance",
                                     "xor",
                                     ])
def test_put_pre_defined(db_session, process):
    processes_service = worker_factory(ProcessesService, db=db_session)
    os.environ["PROCESSES_GITHUB_URL"] = "https://raw.githubusercontent.com/Open-EO/openeo-processes/1.0.0-rc.1/"

    result = processes_service.put_predefined(process_name=process)
    assert result == {
        "status": "success",
        "code": 201,
        "headers": {"Location": "/processes"},
        "service_data": {"process_name": process}
    }
    assert db_session.query(ProcessGraph).filter(ProcessGraph.id_openeo == process).count() == 1


def test_put_user_defined(db_session):
    processes_service = worker_factory(ProcessesService, db=db_session)
    pg = load_process_graph_json()
    result = processes_service.put_user_defined(user_id="test-user", process_graph_id="test-pg", **pg)
    assert result == {"status": "success", "code": 200}
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user") \
               .filter(ProcessGraph.id_openeo == "test-pg").count() == 1


def test_get_all_predefined(db_session):
    processes_service = worker_factory(ProcessesService, db=db_session)
    os.environ["PROCESSES_GITHUB_URL"] = "https://raw.githubusercontent.com/Open-EO/openeo-processes/1.0.0-rc.1/"

    processes = ["absolute", "add"]
    for proc in processes:
        processes_service.put_predefined(process_name=proc)
    assert db_session.query(ProcessGraph).count() == len(processes)

    result = processes_service.get_all_predefined()
    print(result)
    assert result == \
           {'status': 'success', 'code': 200, 'data': {'processes': [{'experimental': False, 'examples': [
               {'arguments': {'x': 0}, 'returns': 0}, {'arguments': {'x': 3.5}, 'returns': 3.5},
               {'arguments': {'x': -0.4}, 'returns': 0.4}, {'arguments': {'x': -3.5}, 'returns': 3.5}],
                                                                      'description': 'Computes the absolute value of a real number `x`, which is the "unsigned" portion of x and often denoted as *|x|*.\n\nThe no-data value `null` is passed through and therefore gets propagated.',
                                                                      'summary': 'Absolute value', 'links': [
                   {'href': 'http://mathworld.wolfram.com/AbsoluteValue.html',
                    'title': 'Absolute value explained by Wolfram MathWorld', 'rel': 'about'}], 'parameters': [
                   {'experimental': False, 'optional': False, 'schema': {'minItems': 0.0, 'type': ['number', 'null']},
                    'description': 'A number.', 'name': 'x', 'deprecated': False}], 'id': 'absolute', 'returns': {
                   'description': 'The computed absolute value.',
                   'schema': {'minItems': 0.0, 'type': ['number', 'null'], 'minimum': 0.0}}, 'process_graph': {
                   'lt': {'process_id': 'lt', 'arguments': {'x': {'from_parameter': 'x'}, 'y': 0}},
                   'multiply': {'process_id': 'multiply', 'arguments': {'x': {'from_parameter': 'x'}, 'y': -1}},
                   'if': {'process_id': 'if',
                          'arguments': {'value': {'from_node': 'lt'}, 'accept': {'from_node': 'multiply'},
                                        'reject': {'from_parameter': 'x'}}, 'result': True}}, 'deprecated': False,
                                                                      'exceptions': {}, 'categories': ['math']},
                                                                     {'experimental': False, 'examples': [
                                                                         {'arguments': {'x': 5, 'y': 2.5},
                                                                          'returns': 7.5},
                                                                         {'arguments': {'x': -2, 'y': -4},
                                                                          'returns': -6},
                                                                         {'arguments': {'x': 1, 'y': None},
                                                                          'returns': 'None'}],
                                                                      'description': 'Sums up the two numbers `x` and `y` (*x + y*) and returns the computed sum.\n\nNo-data values are taken into account so that `null` is returned if any element is such a value.\n\nThe computations follow [IEEE Standard 754](https://ieeexplore.ieee.org/document/8766229) whenever the processing environment supports it.',
                                                                      'summary': 'Addition of two numbers', 'links': [{
                                                                         'href': 'http://mathworld.wolfram.com/Sum.html',
                                                                         'title': 'Sum explained by Wolfram MathWorld',
                                                                         'rel': 'about'},
                                                                         {
                                                                             'href': 'https://ieeexplore.ieee.org/document/8766229',
                                                                             'title': 'IEEE Standard 754-2019 for Floating-Point Arithmetic',
                                                                             'rel': 'about'}],
                                                                      'parameters': [
                                                                          {'experimental': False, 'optional': False,
                                                                           'schema': {'minItems': 0.0,
                                                                                      'type': ['number', 'null']},
                                                                           'description': 'The first summand.',
                                                                           'name': 'x', 'deprecated': False},
                                                                          {'experimental': False, 'optional': False,
                                                                           'schema': {'minItems': 0.0,
                                                                                      'type': ['number', 'null']},
                                                                           'description': 'The second summand.',
                                                                           'name': 'y', 'deprecated': False}],
                                                                      'id': 'add', 'returns': {
                                                                         'description': 'The computed sum of the two numbers.',
                                                                         'schema': {'minItems': 0.0,
                                                                                    'type': ['number', 'null']}},
                                                                      'process_graph': {'sum': {'process_id': 'sum',
                                                                                                'arguments': {'data': [{
                                                                                                    'from_parameter': 'x'},
                                                                                                    {
                                                                                                        'from_parameter': 'y'}],
                                                                                                    'ignore_nodata': False},
                                                                                                'result': True}},
                                                                      'deprecated': False, 'exceptions': {},
                                                                      'categories': ['math']}], 'links': []}}


def test_get_all_user_defined(db_session):
    processes_service = worker_factory(ProcessesService, db=db_session)
    pg = load_process_graph_json()
    processes_service.put_user_defined(user_id="test-user", process_graph_id="test-pg-1", **pg)
    processes_service.put_user_defined(user_id="test-user", process_graph_id="test-pg-2", **pg)
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user").count() == 2

    result = processes_service.get_all_user_defined(user_id="test-user")
    assert result == {
        "status": "success",
        "code": 200,
        "data": {
            "processes": [
                {
                    "categories": [
                        "catA",
                        "catB",
                        "catC"
                    ],
                    "experimental": False,
                    "deprecated": False,
                    "id": "test-pg-1",
                    "returns": {
                        "description": "Computed EVI.",
                        "schema": {
                            "minItems": 0,
                            "type": "number"
                        }
                    },
                    "description": "Computes the Enhanced Vegetation Index (EVI). It is computed with the following formula: `2.5 * (NIR - RED) / (1 + NIR + 6*RED + -7.5*BLUE)`.",
                    "summary": "Enhanced Vegetation Index",
                    "parameters": [
                        {
                            "experimental": False,
                            "deprecated": False,
                            "optional": False,
                            "schema": {
                                "minItems": 0,
                                "type": "number"
                            },
                            "description": "Value from the red band.",
                            "name": "red"
                        },
                        {
                            "experimental": False,
                            "deprecated": False,
                            "optional": False,
                            "schema": {
                                "minItems": 0,
                                "type": "number"
                            },
                            "description": "Value from the blue band.",
                            "name": "blue"
                        },
                        {
                            "experimental": False,
                            "deprecated": False,
                            "optional": False,
                            "schema": {
                                "minItems": 0,
                                "type": "number"
                            },
                            "description": "Value from the near infrared band.",
                            "name": "nir"
                        }
                    ]
                },
                {
                    "categories": [
                        "catA",
                        "catB",
                        "catC"
                    ],
                    "experimental": False,
                    "deprecated": False,
                    "id": "test-pg-2",
                    "returns": {
                        "description": "Computed EVI.",
                        "schema": {
                            "minItems": 0,
                            "type": "number",
                            "additional": {}
                        }
                    },
                    "description": "Computes the Enhanced Vegetation Index (EVI). It is computed with the following formula: `2.5 * (NIR - RED) / (1 + NIR + 6*RED + -7.5*BLUE)`.",
                    "summary": "Enhanced Vegetation Index",
                    "parameters": [
                        {
                            "experimental": False,
                            "deprecated": False,
                            "optional": False,
                            "schema": {
                                "minItems": 0,
                                "type": "number",
                                "additional": {}
                            },
                            "description": "Value from the red band.",
                            "name": "red"
                        },
                        {
                            "experimental": False,
                            "deprecated": False,
                            "optional": False,
                            "schema": {
                                "minItems": 0,
                                "type": "number",
                                "additional": {}
                            },
                            "description": "Value from the blue band.",
                            "name": "blue"
                        },
                        {
                            "experimental": False,
                            "deprecated": False,
                            "optional": False,
                            "schema": {
                                "minItems": 0,
                                "type": "number",
                                "additional": {}
                            },
                            "description": "Value from the near infrared band.",
                            "name": "nir"
                        }
                    ]
                }
            ],
            "links": []
        }
    }


def test_get_user_defined(db_session):
    processes_service = worker_factory(ProcessesService, db=db_session)
    pg = load_process_graph_json()
    processes_service.put_user_defined(user_id="test-user", process_graph_id="test-pg", **pg)
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user") \
               .filter(ProcessGraph.id_openeo == "test-pg").count() == 1

    result = processes_service.get_user_defined(user_id="test-user", process_graph_id="test-pg")
    assert result == {
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


def test_delete(db_session):
    processes_service = worker_factory(ProcessesService, db=db_session)
    pg = load_process_graph_json()
    processes_service.put_user_defined(user_id="test-user", process_graph_id="test-pg", **pg)
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user") \
               .filter(ProcessGraph.id_openeo == "test-pg").count() == 1

    result = processes_service.delete(user_id="test-user", process_graph_id="test-pg")
    assert result == {"status": "success", "code": 204}
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user") \
               .filter(ProcessGraph.id_openeo == "test-pg").count() == 0
