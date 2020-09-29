"""Provide the implementation of the process discovery and management service and service exception."""
import json
import logging
from copy import deepcopy
from typing import Any, Dict, Optional

import requests
from dynaconf import settings
from jsonschema import ValidationError
from nameko.rpc import RpcProxy, rpc
from nameko_sqlalchemy import DatabaseSession
from openeo_pg_parser.validate import validate_process_graph

from .dependencies.settings import initialise_settings
from .models import Base, ProcessDefinitionEnum, ProcessGraph
from .schema import ProcessGraphFullSchema, ProcessGraphPredefinedSchema, ProcessGraphShortSchema

service_name = "processes"
LOGGER = logging.getLogger('standardlog')
initialise_settings()


class ServiceException(Exception):
    """The ServiceException is mapping any exception to a serializable format for the API gateway.

    Attributes:
        service: The name of the service as a string.
        code: An integer holding the error code.
        user_id: The id of the user as string. (default: None)
        msg: A string with the error message.
        internal: A boolean indicating if this is an internal error. (default: True)
        links: A list of links which can be useful when getting this error. (default: None)
    """

    def __init__(self, service: str, code: int, user_id: Optional[str], msg: str, internal: bool = True,
                 links: list = None) -> None:
        """Initialize service exception."""
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
        """Serialize the object to a dict.

        Returns:
            The serialized exception.
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
    """Process discovery and management of user-defined process graphs."""

    name = service_name
    db = DatabaseSession(Base)
    """Database connection to processes database."""
    data_service = RpcProxy("data")
    """Rpc connection to data service."""

    @rpc
    def get_user_defined(self, user: Dict[str, Any], process_graph_id: str) -> dict:
        """Get the process graph using the provided process_graph_id.

        Args:
            user: The user object to determine whether the user can access the given process graph.
            process_graph_id: The id of the process graph.

        Returns:
            A dictionary containing detailed information about the process graph and the request status or a serialized
            service exception.
        """
        try:
            process_graph_id = self._back_convert_old_process_graph_ids(process_graph_id)
            process_graph = self.db.query(ProcessGraph) \
                .filter_by(id_openeo=process_graph_id) \
                .filter_by(process_definition=ProcessDefinitionEnum.user_defined) \
                .first()
            response = self._exist_and_authorize(user["id"], process_graph_id, process_graph)
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
            return ServiceException(ProcessesService.name, 500, user["id"], str(exp)).to_dict()

    @rpc
    def delete(self, user: Dict[str, Any], process_graph_id: str) -> dict:
        """Delete the process graph with the given process_graph_id from the database.

        Args:
            user: The user object to determine whether the user can delete the given process graph.
            process_graph_id: The id of the process graph.

        Returns:
            A dictionary with the status of the request.
        """
        try:
            process_graph_id = self._back_convert_old_process_graph_ids(process_graph_id)
            # Check process graph exists and user is allowed to access / delete it
            process_graph = self.db.query(ProcessGraph).filter_by(id_openeo=process_graph_id).first()
            response = self._exist_and_authorize(user["id"], process_graph_id, process_graph)
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
            return ServiceException(ProcessesService.name, 500, user["id"], str(exp),
                                    links=[]).to_dict()

    @rpc
    def get_all_predefined(self, user: Dict[str, Any] = None) -> dict:
        """Return detailed process description of all available predefined processes.

        Args:
            user: The user object - not used, only given for consistency with all other methods.
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
            return ServiceException(ProcessesService.name, 500, self.get_user_id(user), str(exp)).to_dict()

    @rpc
    def get_all_user_defined(self, user: Dict[str, Any]) -> dict:
        """Return all available process graphs for the given user.

        Args:
            user: The user object.
        """
        try:
            process_graphs = self.db.query(ProcessGraph) \
                .filter_by(process_definition=ProcessDefinitionEnum.user_defined) \
                .filter_by(user_id=user["id"]) \
                .order_by(ProcessGraph.created_at).all()
            LOGGER.info(f"Found {len(process_graphs)} ProcessGraphs for User {user['id']}.")
            return {
                "status": "success",
                "code": 200,
                "data": {
                    "processes": ProcessGraphShortSchema(many=True).dump(process_graphs),
                    "links": [],
                }
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user["id"], str(exp),
                                    links=["#tag/Job-Management/paths/~1process_graphs/get"]).to_dict()

    @rpc
    def put_predefined(self, process_name: str, user: Dict[str, Any] = None) -> dict:
        """Add the process definition from GitHub using the process_name.

        Args:
            process_name: The name of the process to get from GitHub and create in the database.
            user: The user object - not used, only given for consistency with all other methods.
        """
        try:
            process_url = f"{settings.PROCESSES_GITHUB_URL}{process_name}.json"
            process_graph_response = requests.get(process_url)
            if process_graph_response.status_code != 200:
                return ServiceException(ProcessesService.name, process_graph_response.status_code,
                                        self.get_user_id(user), str(process_graph_response.text)).to_dict()
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
            return ServiceException(ProcessesService.name, 500, self.get_user_id(user), str(exp)).to_dict()

    @rpc
    def put_user_defined(self, user: Dict[str, Any], process_graph_id: str, **process_graph_args: Any) -> dict:
        """Create a new user-defined process graph using the description send in the request body.

        Args:
            user: The user object who creates the process graph.
            process_graph_id: The identifier of the process graph. This id overwrites the id in the process_graph_args
                if one is given.
            process_graph_args: The dictionary containing information needed to create a ProcessGraph.

        Returns:
            A dictionary with the status of the request.
        """
        try:
            response = self._check_not_in_predefined(user["id"], process_graph_id)
            if isinstance(response, ServiceException):
                return response.to_dict()

            process_graph_args['id'] = process_graph_id  # path parameter overwrites id in json
            validate_result = self.validate(user, **deepcopy(process_graph_args))
            if validate_result["status"] == "error":
                return validate_result

            process_graph = self.db.query(ProcessGraph).filter_by(id_openeo=process_graph_id).first()
            if process_graph:
                response = self._authorize(user["id"], process_graph)
                if isinstance(response, ServiceException):
                    return response.to_dict()
                process_graph_args['id_internal'] = process_graph.id

            process_graph_args['process_definition'] = ProcessDefinitionEnum.user_defined
            process_graph_args['user_id'] = user["id"]
            process_graph = ProcessGraphPredefinedSchema().load(process_graph_args)
            self.db.merge(process_graph)
            self.db.commit()
            LOGGER.info(f"User-defined ProcessGraph {process_graph_id} successfully created.")

            return {
                "status": "success",
                "code": 200,
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user["id"], str(exp)).to_dict()

    @rpc
    def validate(self, user: Dict[str, Any], **process: dict) -> dict:
        """Validate the provided process graph.

        Args:
            user: The user object.
            process: The process graph to validated.

        Returns:
            A dictionary including the status of the request and validation errors or a serialized service exception.
        """
        # TODO: RESPONSE HEADERS -> OpenEO-Costs
        try:
            # Get all processes
            process_response = self.get_all_predefined()
            if process_response["status"] == "error":
                return process_response
            processes = process_response["data"]["processes"]

            # Get all collections (full metadata)
            data_response = self.data_service.get_all_products()
            if data_response["status"] == "error":
                return data_response
            collections_full_md = []
            for col in data_response["data"]["collections"]:
                data_response = self.data_service.get_product_detail(collection_id=col['id'])
                if data_response["status"] == "error":
                    return data_response
                collections_full_md.append(data_response['data'])
            try:
                _ = validate_process_graph(process, processes_src=processes, collections_src=collections_full_md)
                output_errors: list = []
            except ValidationError as exp:
                output_errors = [
                    {
                        'code': 400,
                        'message': str(exp)
                    }
                ]

            return {
                "status": "success",
                "code": 200,
                "data": {
                    'errors': output_errors
                }
            }
        except ValidationError as exp:
            return ServiceException(ProcessesService.name, 400, user["id"], str(exp), internal=False,
                                    links=["#tag/EO-Data-Discovery/paths/~1process_graph/post"]).to_dict()
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user["id"], str(exp)).to_dict()

    def _exist_and_authorize(self, user_id: str, process_graph_id: str, process_graph: ProcessGraph) \
            -> Optional[ServiceException]:
        """Return Exception if given ProcessGraph does not exist or User is not allowed to access this ProcessGraph.

        Args:
            user_id: The identifier of the user.
            process_graph_id: The id of the process graph.
            process_graph: The ProcessGraph object for the given process_graph_id.
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

        Args:
            user_id The identifier of the user.
            process_graph_id: The id of the process graph.
            process_graph. The ProcessGraph object for the given process_graph_id.
        """
        if process_graph is None:
            return ServiceException(ProcessesService.name, 400, user_id,
                                    f"The process_graph with id '{process_graph_id}' does not exist.", internal=False,
                                    links=[])
        LOGGER.info(f"ProcessGraph {process_graph_id} exists.")
        return None

    def _authorize(self, user_id: str, process_graph: ProcessGraph) -> Optional[ServiceException]:
        """Return Exception if the User is not allowed to access this ProcessGraph.

        Args:
            user_id: The identifier of the user.
            process_graph: The ProcessGraph object for the given process_graph_id.
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
        """Return Exception if the process_graph_id is defined as predefined process.

        Args:
            user_id: The identifier of the user.
            process_graph_id: The id of the user-defined process graph.
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

    def _back_convert_old_process_graph_ids(self, process_graph_id: str) -> str:
        """Back-Translate reformated process_graph_ids.

        Due to backward compatibility some process_graph_ids (id_openeo) do not match the required regex (in the
        database) -> they are converted to match and need to be back converted when used internally.
        """
        if process_graph_id.startswith("regex_"):
            new = process_graph_id.replace("_", "-")
            return new[6:]
        return process_graph_id

    def get_user_id(self, user: Optional[Dict[str, Any]]) -> Optional[str]:
        """Return the user's id if a user object is given."""
        return user["id"] if user and "id" in user else None
