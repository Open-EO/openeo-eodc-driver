"""Unittests for processes service api functions."""
import json
import os
from typing import Any, Dict

import pytest
from nameko.testing.services import worker_factory
from sqlalchemy.orm import Session

from processes.models import ProcessGraph
from processes.service import ProcessesService


def load_json(filename: str) -> dict:
    """Load JSON files in from the tests data folder."""
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", filename)
    with open(json_path) as f:
        return json.load(f)


def mock_processes_service(db_session: Session, add_processes: bool = False) -> ProcessesService:
    """Return a mocked processes service.

    If requested a set of predefined processes is added.
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
    """Test a predefined process can be added."""
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
    """Test predefined processes are returned properly."""
    processes_service = mock_processes_service(db_session, add_processes=True)

    result = processes_service.get_all_predefined()
    ref_output = load_json("r_get_all_predefined.json")
    assert result == ref_output


def test_get_all_user_defined(db_session: Session, user: Dict[str, Any]) -> None:
    """Add and return a user_defined processes and check they are formatted correctly."""
    processes_service = mock_processes_service(db_session, add_processes=True)
    processes_service.data_service.get_all_products.return_value = load_json("collections.json")

    pg = load_json("process_graph.json")
    processes_service.put_user_defined(user=user, process_graph_id="test_pg_1", **pg)
    processes_service.put_user_defined(user=user, process_graph_id="test_pg_2", **pg)
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == user["id"]).count() == 2

    result = processes_service.get_all_user_defined(user=user)
    ref_output = load_json("r_get_all_user_defined.json")
    assert result == ref_output


def test_put_get_user_defined(db_session: Session, user: Dict[str, Any]) -> None:
    """More extensive test for putting and getting a user_defined process.

    Check reinstering the same process graph twice has no effect.
    Check the modify process graph method.
    """
    processes_service = mock_processes_service(db_session, add_processes=True)

    processes_service.data_service.get_all_products.return_value = load_json("collections.json")
    pg = load_json("process_graph.json")
    result = processes_service.put_user_defined(user=user, process_graph_id="test_pg", **pg)
    assert result["status"] == "success"
    query = db_session.query(ProcessGraph).filter(ProcessGraph.user_id == user["id"]) \
        .filter(ProcessGraph.id_openeo == "test_pg")
    id_orig = query.first().id
    assert query.count() == 1

    result = processes_service.get_user_defined(user=user, process_graph_id="test_pg")
    ref_output = load_json("r_put_get_user_defined.json")
    assert result == ref_output

    # Insert same pg again - nothing should change
    processes_service.put_user_defined(user=user, process_graph_id="test_pg", **pg)
    assert query.count() == 1
    assert query.first().id == id_orig
    result = processes_service.get_user_defined(user=user, process_graph_id="test_pg")
    assert result == ref_output

    # Make a small change (update summary) - only the summary should change
    pg['summary'] = 'A new summary'
    ref_output['data']['summary'] = 'A new summary'
    processes_service.put_user_defined(user=user, process_graph_id="test_pg", **pg)
    assert query.count() == 1
    assert query.first().id == id_orig
    result = processes_service.get_user_defined(user=user, process_graph_id="test_pg")
    assert result == ref_output


def test_put_user_defined_predefined(db_session: Session, user: Dict[str, Any]) -> None:
    """Test a user can not create a process graph with the same name as a predefined process."""
    processes_service = mock_processes_service(db_session, add_processes=True)

    pg = load_json("process_graph.json")
    result = processes_service.put_user_defined(user=user, process_graph_id="absolute", **pg)

    ref_output = load_json("r_put_user_defined_predefined.json")
    ref_output["user_id"] = user["id"]
    assert result == ref_output
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user") \
        .filter(ProcessGraph.id_openeo == "absolute").count() == 0


def test_get_user_defined_non_existing(db_session: Session, user: Dict[str, Any]) -> None:
    """Test the error msg when the user tries to access a none-existing process graph."""
    processes_service = mock_processes_service(db_session)
    assert db_session.query(ProcessGraph).filter(ProcessGraph.id_openeo == "test_pg").count() == 0

    result = processes_service.get_user_defined(user=user, process_graph_id="test_pg")
    ref_output = load_json("r_get_user_defined_non_existing.json")
    ref_output["user_id"] = user["id"]
    assert result == ref_output


def test_delete(db_session: Session, user: Dict[str, Any]) -> None:
    """Test the delete process graph method."""
    processes_service = mock_processes_service(db_session, add_processes=True)

    processes_service.data_service.get_all_products.return_value = load_json("collections.json")

    pg = load_json("process_graph.json")
    processes_service.put_user_defined(user=user, process_graph_id="test_pg", **pg)
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == user["id"]) \
        .filter(ProcessGraph.id_openeo == "test_pg").count() == 1

    result = processes_service.delete(user=user, process_graph_id="test_pg")
    assert result == {"status": "success", "code": 204}
    assert db_session.query(ProcessGraph).filter(ProcessGraph.user_id == "test-user") \
        .filter(ProcessGraph.id_openeo == "test_pg").count() == 0


def test_delete_non_existing(db_session: Session, user: Dict[str, Any]) -> None:
    """Test the error msg when the user tries to delete a none-existing process graph."""
    processes_service = mock_processes_service(db_session)
    assert db_session.query(ProcessGraph).filter(ProcessGraph.id_openeo == "test_pg").count() == 0

    result = processes_service.delete(user=user, process_graph_id="test_pg")
    ref_output = load_json("r_delete_non_existing.json")
    ref_output["user_id"] = user["id"]
    assert result == ref_output
