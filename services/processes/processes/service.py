""" Process Discovery """
import json
import logging
import os
from copy import deepcopy
from typing import Any, Optional

import requests
from jsonschema import ValidationError
from nameko.rpc import RpcProxy, rpc
from nameko_sqlalchemy import DatabaseSession
from openeo_pg_parser_python.validate import validate_process_graph

from .models import Base, ProcessDefinitionEnum, ProcessGraph
from .schema import ProcessGraphFullSchema, ProcessGraphPredefinedSchema, ProcessGraphShortSchema

service_name = "processes"
LOGGER = logging.getLogger('standardlog')


class ServiceException(Exception):
    """ServiceException raises if an exception occured while processing the
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(self, service: str, code: int, user_id: Optional[str], msg: str, internal: bool = True,
                 links: list = None) -> None:
        if not links:
            links = []
        self._service = service
        self._code = code
        self._user_id = user_id
        self._msg = msg
        self._internal = internal
        self._links = links
        LOGGER.exception(msg, exc_info=True)

    def to_dict(self) -> dict:
        """Serializes the object to a dict.

        Returns:
            dict -- The serialized exception
        """

        return {
            "status": "error",
            "service": self._service,
            "code": self._code,
            "user_id": self._user_id,
            "msg": self._msg,
            "internal": self._internal,
            "links": self._links
        }


class ProcessesService:
    """Management of stored process graphs.
    """

    name = service_name
    db = DatabaseSession(Base)
    data_service = RpcProxy("data")

    @rpc
    def get_user_defined(self, user_id: str, process_graph_id: str) -> dict:
        """The request will ask the back-end to get the process graph using the process_graph_id.

        Arguments:
            user_id {str} -- The identifier of the user
            process_graph_id {str} -- The id of the process graph
        """
        try:
            process_graph = self.db.query(ProcessGraph) \
                .filter_by(id_openeo=process_graph_id) \
                .filter_by(process_definition=ProcessDefinitionEnum.user_defined) \
                .first()
            response = self._exist_and_authorize(user_id, process_graph_id, process_graph)
            if isinstance(response, ServiceException):
                return response.to_dict()
            self.db.refresh(process_graph)  # To ensure the object is always taken from the db
            LOGGER.info(f"Return user-defined ProcessGraph {process_graph_id}.")
            return {
                "status": "success",
                "code": 200,
                "data": ProcessGraphFullSchema().dump(process_graph)
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def delete(self, user_id: str, process_graph_id: str) -> dict:
        """The request will ask the back-end to delete the process graph with the given process_graph_id.

        Arguments:
            user_id {str} -- The identifier of the user
            process_graph_id {str} -- The id of the process graph
        """
        try:
            # Check process graph exists and user is allowed to access / delete it
            process_graph = self.db.query(ProcessGraph).filter_by(id_openeo=process_graph_id).first()
            response = self._exist_and_authorize(user_id, process_graph_id, process_graph)
            if isinstance(response, ServiceException):
                return response.to_dict()

            self.db.delete(process_graph)
            self.db.commit()
            LOGGER.info(f"User-defined ProcessGraph {process_graph_id} successfully deleted.")
            return {
                "status": "success",
                "code": 204
            }

        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp),
                                    links=[]).to_dict()

    @rpc
    def get_all_predefined(self, user_id: str = None) -> dict:
        """The request asks the back-end for available predefined processes and returns detailed process descriptions.

        Arguments:
            user_id {str} -- The identifier of the user (default: {None})
        """

        try:
            process_graphs = self.db.query(ProcessGraph) \
                .filter_by(process_definition=ProcessDefinitionEnum.predefined) \
                .order_by(ProcessGraph.created_at).all()
            LOGGER.debug(f"Found {len(process_graphs)} pre-defined processes.")
            return {
                "status": "success",
                "code": 200,
                "data": {
                    "processes": ProcessGraphPredefinedSchema(many=True).dump(process_graphs),
                    "links": []
                }
            }

        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def get_all_user_defined(self, user_id: str) -> dict:
        """The request will ask the back-end to get all available process graphs for the given user.

        Arguments:
            user_id {str} -- The identifier of the user
        """
        try:
            process_graphs = self.db.query(ProcessGraph) \
                .filter_by(process_definition=ProcessDefinitionEnum.user_defined) \
                .filter_by(user_id=user_id) \
                .order_by(ProcessGraph.created_at).all()
            LOGGER.info(f"Found {len(process_graphs)} ProcessGraphs for User {user_id}.")
            return {
                "status": "success",
                "code": 200,
                "data": {
                    "processes": ProcessGraphShortSchema(many=True).dump(process_graphs),
                    "links": [],
                }
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1process_graphs/get"]).to_dict()

    @rpc
    def put_predefined(self, process_name: str, user_id: str = None, **process_args: Any) -> dict:
        """The request will ask the back-end to add the process from GitHub using the process_name.

        Arguments:
            process_name {str} -- The name of the process to create in the database

        Keyword Arguments:
            user_id {str} -- The identifier of the user (default: {None})
        """

        # TODO how to handle process extensions
        try:
            process_url = os.environ.get('PROCESSES_GITHUB_URL') + process_name + '.json'  # type: ignore
            process_graph_response = requests.get(process_url)
            if process_graph_response.status_code != 200:
                return ServiceException(ProcessesService.name, process_graph_response.status_code,
                                        user_id, str(process_graph_response.text)).to_dict()
            LOGGER.debug(f"Pre-defined Process {process_name} description is available on GitHub.")

            process_graph = self.db.query(ProcessGraph).filter_by(id_openeo=process_name).first()
            if process_graph:
                self.db.delete(process_graph)
                self.db.commit()
                LOGGER.debug(f"Pre-defined Process {process_name} delete to create new one with the same id.")

            process_graph_json = json.loads(process_graph_response.content)
            process_graph_json['process_definition'] = ProcessDefinitionEnum.predefined
            process_graph = ProcessGraphPredefinedSchema().load(process_graph_json)
            self.db.add(process_graph)
            self.db.commit()
            LOGGER.info(f"Pre-defined Process {process_name} successfully created.")

            return {
                "status": "success",
                "code": 201,
                "headers": {"Location": "/processes"},
                "service_data": {'process_name': process_name}
            }

        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def put_user_defined(self, user_id: str, process_graph_id: str, **process_graph_args: Any) -> dict:
        """
        The request will ask the back-end to create a new process graph using the description send in the request body.

        Arguments:
            user_id {str} -- The identifier of the user
            process_graph_id {str} -- The identifier of the process graph
            process_graph_args {Dict[str, Any]} -- The dictionary containing information needed to create a ProcessGraph
        """

        try:
            response = self._check_not_in_predefined(user_id, process_graph_id)
            if isinstance(response, ServiceException):
                return response.to_dict()

            process_graph_args['id'] = process_graph_id  # path parameter overwrites id in json
            validate_result = self.validate(user_id, **deepcopy(process_graph_args))
            if validate_result["status"] == "error":
                return validate_result

            process_graph = self.db.query(ProcessGraph).filter_by(id_openeo=process_graph_id).first()
            if process_graph:
                response = self._authorize(user_id, process_graph)
                if isinstance(response, ServiceException):
                    return response.to_dict()
                process_graph_args['id_internal'] = process_graph.id

            process_graph_args['process_definition'] = ProcessDefinitionEnum.user_defined
            process_graph_args['user_id'] = user_id
            process_graph = ProcessGraphPredefinedSchema().load(process_graph_args)
            self.db.merge(process_graph)
            self.db.commit()
            LOGGER.info(f"User-defined ProcessGraph {process_graph_id} successfully created.")

            return {
                "status": "success",
                "code": 200,
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def validate(self, user_id: str, **process: dict) -> dict:
        """The request will ask the back-end to create a new process using the description send in the request body.

        Arguments:
            user_id {str} -- The identifier of the user (default: {None})
            process {dict} -- The process (graph) to validated
        """
        # TODO: RESPONSE HEADERS -> OpenEO-Costs

        try:
            # Get all processes
            process_response = self.get_all_predefined()
            if process_response["status"] == "error":
                return process_response
            processes = process_response["data"]["processes"]

            # Get all products
            data_response = self.data_service.get_all_products()
            if data_response["status"] == "error":
                return data_response
            collections = data_response["data"]["collections"]

            valid = validate_process_graph(process, processes_src=processes,
                                           collections_src=collections)
            if valid:
                output_errors = []
            else:
                # TODO clarify errors -> use again json schemas for validation
                output_errors = [
                    {
                        "message": "error."
                    }
                ]

            return {
                "status": "success",
                "code": 200,
                "data": output_errors
            }
        except ValidationError as exp:
            return ServiceException(ProcessesService.name, 400, user_id, exp.message, internal=False,
                                    links=["#tag/EO-Data-Discovery/paths/~1process_graph/post"]).to_dict()
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()

    def _exist_and_authorize(self, user_id: str, process_graph_id: str, process_graph: ProcessGraph) \
            -> Optional[ServiceException]:
        """Return Exception if given ProcessGraph does not exist or User is not allowed to access this ProcessGraph.

        Arguments:
            user_id {str} -- The identifier of the user
            process_graph_id {str} -- The id of the process graph
            process_graph {ProcessGraph} -- The ProcessGraph object for the given process_graph_id
        """
        exists = self._check_exists(user_id, process_graph_id, process_graph)
        if isinstance(exists, ServiceException):
            return exists

        auth = self._authorize(user_id, process_graph)
        if not isinstance(auth, ServiceException):
            return auth

        return None

    def _check_exists(self, user_id: str, process_graph_id: str, process_graph: ProcessGraph) \
            -> Optional[ServiceException]:
        """Return Exception if given ProcessGraph does not exist.

        Arguments:
            user_id {str} -- The identifier of the user
            process_graph_id {str} -- The id of the process graph
            process_graph {ProcessGraph} -- The ProcessGraph object for the given process_graph_id
        """
        if process_graph is None:
            return ServiceException(ProcessesService.name, 400, user_id,
                                    f"The process_graph with id '{process_graph_id}' does not exist.", internal=False,
                                    links=[])
        LOGGER.info(f"ProcessGraph {process_graph_id} exists.")
        return None

    def _authorize(self, user_id: str, process_graph: ProcessGraph) -> Optional[ServiceException]:
        """Return Exception if the User is not allowed to access this ProcessGraph.

        Arguments:
            user_id {str} -- The identifier of the user
            process_graph {ProcessGraph} -- The ProcessGraph object for the given process_graph_id
        """
        if not process_graph:
            return None
        # TODO: Permission (e.g admin)
        if process_graph.user_id != user_id:
            return ServiceException(ProcessesService.name, 401, user_id,
                                    "You are not allowed to access this resource.", internal=False, links=[])
        LOGGER.info(f"User {user_id} is authorized to access ProcessGraph {process_graph.id}")
        return None

    def _check_not_in_predefined(self, user_id: str, process_graph_id: str) -> Optional[ServiceException]:
        """
        Return Exception if the process_graph_id is defined as pre-defined process.

        Arguments:
            user_id {str} -- The identifier of the user
            process_graph_id {str} -- The id of the user-defined process graph
        """
        predefined = list(map(lambda rec: rec[0],
                              self.db.query(ProcessGraph.id_openeo)
                              .filter_by(process_definition=ProcessDefinitionEnum.predefined).all()))
        if process_graph_id in predefined:
            return ServiceException(ProcessesService.name, 400, user_id,
                                    f"The process_graph_id {process_graph_id} is not allowed, as it corresponds"
                                    f" to a predefined process. Please use another process_graph_id. E.g. "
                                    f"user_{process_graph_id}", internal=False, links=[])
        LOGGER.debug(f"ProcessGraphId {process_graph_id} is not a predefined process")
        return None
