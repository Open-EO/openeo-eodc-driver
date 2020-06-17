import json
import os

import pytest
from nameko.testing.services import worker_factory
from sqlalchemy.orm import Session

from processes.models import ProcessGraph
from processes.service import ProcessesService


def load_json(filename: str) -> dict:
    """
    Helper function to load JSON files in the ./data folder.
    """

    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", filename)
    with open(json_path) as f:
        return json.load(f)


def mock_processes_service(db_session: Session, add_processes: bool = False) -> ProcessesService:
    """
    Mock processes service.
    """

    processes_service = worker_factory(ProcessesService, db=db_session)

    if add_processes:
        # Add processes to mocked process service.
        processes = [
            "absolute",
            "add",
            "divide",
            "product",
            "subtract",
            "sum"
        ]
        for proc in processes:
            processes_service.put_predefined(process_name=proc)

        assert db_session.query(ProcessGraph).count() == len(processes)

    return processes_service


@pytest.mark.parametrize("process", load_json("process_list.json"))
def test_put_pre_defined(db_session: Session, process: str) -> None:
    processes_service = mock_processes_service(db_session)
    result = processes_service.put_predefined(process_name=process)

    assert result == {
        "status": "success",
        "code": 201,
        "headers": {"Location": "/processes"},
        "service_data": {"process_name": process}
    }

    assert db_session.query(ProcessGraph).filter(ProcessGraph.id_openeo == process).count() == 1


def test_get_all_predefined(db_session: Session) -> None:
    processes_service = mock_processes_service(db_session, add_processes=True)

    result = processes_service.get_all_predefined()
    ref_output = load_json("r_get_all_predefined.json")
    assert result == ref_output


def test_get_all_user_defined(db_session: Session) -> None:
    processes_service = mock_processes_service(db_session, add_processes=True)
    processes_service.data_service.get_all_products.return_value = load_json("collections.json")

    pg = load_json("process_graph.json")
    processes_service.put_user_defined(user_id="test-user", process_graph_id="test-pg-1", **pg)
    processes_service.put_user_defined(user_id="test-user", process_graph_id="test-pg-2", **pg)
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user").count() == 2

    result = processes_service.get_all_user_defined(user_id="test-user")
    ref_output = load_json("r_get_all_user_defined.json")
    assert result == ref_output


def test_put_get_user_defined(db_session: Session) -> None:
    processes_service = mock_processes_service(db_session, add_processes=True)

    processes_service.data_service.get_all_products.return_value = load_json("collections.json")
    pg = load_json("process_graph.json")
    processes_service.put_user_defined(user_id="test-user", process_graph_id="test-pg", **pg)
    query = db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user") \
        .filter(ProcessGraph.id_openeo == "test-pg")
    id_orig = query.first().id
    assert query.count() == 1

    result = processes_service.get_user_defined(user_id="test-user", process_graph_id="test-pg")
    ref_output = load_json("r_put_get_user_defined.json")
    assert result == ref_output

    # Insert same pg again - nothing should change
    processes_service.put_user_defined(user_id="test-user", process_graph_id="test-pg", **pg)
    assert query.count() == 1
    assert query.first().id == id_orig
    result = processes_service.get_user_defined(user_id="test-user", process_graph_id="test-pg")
    assert result == ref_output

    # Make a small change (update summary) - only the summary should change
    pg['summary'] = 'A new summary'
    ref_output['data']['summary'] = 'A new summary'
    processes_service.put_user_defined(user_id="test-user", process_graph_id="test-pg", **pg)
    assert query.count() == 1
    assert query.first().id == id_orig
    result = processes_service.get_user_defined(user_id="test-user", process_graph_id="test-pg")
    assert result == ref_output


def test_put_user_defined_predefined(db_session: Session) -> None:
    processes_service = mock_processes_service(db_session, add_processes=True)

    pg = load_json("process_graph.json")
    result = processes_service.put_user_defined(user_id="test-user", process_graph_id="absolute", **pg)

    ref_output = load_json("r_put_user_defined_predefined.json")
    assert result == ref_output
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user") \
        .filter(ProcessGraph.id_openeo == "absolute").count() == 0


def test_get_user_defined_non_existing(db_session: Session) -> None:
    processes_service = mock_processes_service(db_session)
    assert db_session.query(ProcessGraph).filter(ProcessGraph.id_openeo == "test-pg").count() == 0

    result = processes_service.get_user_defined(user_id="test-user", process_graph_id="test-pg")
    ref_output = load_json("r_get_user_defined_non_existing.json")
    assert result == ref_output


def test_delete(db_session: Session) -> None:
    processes_service = mock_processes_service(db_session, add_processes=True)

    processes_service.data_service.get_all_products.return_value = load_json("collections.json")

    pg = load_json("process_graph.json")
    processes_service.put_user_defined(user_id="test-user", process_graph_id="test-pg", **pg)
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user") \
        .filter(ProcessGraph.id_openeo == "test-pg").count() == 1

    result = processes_service.delete(user_id="test-user", process_graph_id="test-pg")
    assert result == {"status": "success", "code": 204}
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user") \
        .filter(ProcessGraph.id_openeo == "test-pg").count() == 0


def test_delete_non_existing(db_session: Session) -> None:
    processes_service = mock_processes_service(db_session)
    assert db_session.query(ProcessGraph).filter(ProcessGraph.id_openeo == "test-pg").count() == 0

    result = processes_service.delete(user_id="test-user", process_graph_id="test-pg")
    ref_output = load_json("r_delete_non_existing.json")
    assert result == ref_output
