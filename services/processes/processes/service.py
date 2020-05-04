""" Process Discovery """

import os
import requests
import json
import logging

from nameko.rpc import rpc, RpcProxy
from nameko_sqlalchemy import DatabaseSession
from sqlalchemy import exc
from copy import deepcopy

from .models import Base, ProcessGraph
from .schema import ProcessGraphShortSchema, ProcessGraphFullSchema
from .dependencies import NodeParser, Validator
from jsonschema import ValidationError
from openeo_pg_parser_python.validate import validate_process_graph

service_name = "processes"
LOGGER = logging.getLogger('standardlog')

class ServiceException(Exception):
    """ServiceException raises if an exception occured while processing the
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(self, service: str, code: int, user_id: str, msg: str, internal: bool=True, links: list=None):
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
    """Discovery of processes that are available at the back-end.
    """

    name = service_name

    @rpc
    def create(self, user_id: str=None, **process_args):
        """The request will ask the back-end to create get process from GitHub using the name send in the request body.

        Keyword Arguments:
            user_id {str} -- The identifier of the user (default: {None})

        Example:
            /processes POST is only reachable for admin users > authentication token needed in header!
            The POST body needs to be a dict: {'process-name': {'additional_key': 'value'}}
            Currently process-name has to be proccess defined within OpenEO
            > see: https://raw.githubusercontent.com/Open-EO/openeo-processes/
            The additional key-value pairs can also have complex structures. They will be added at the top-level of the
            json file.
        """
        process_args_str = ', '.join(process_args.keys())
        try:
            for process_name, process_extension in process_args.items():
                process_ext = process_name + '.json'
                response = requests.get(os.environ.get('PROCESSES_GITHUB_URL') + process_ext)
                with open(os.path.join(os.environ.get('PROCESS_API_DIR'), process_ext), 'w+') as f:
                    process_json = json.loads(response.content)
                    process_json.update(process_extension)
                    json.dump(process_json, f)

            return {
                "status": "success",
                "code": 201,
                "headers": {"Location": "/processes"},
                "service_data": ' ,'.join(process_args_str)
            }

        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def get_all(self, user_id: str=None):
        """The request asks the back-end for available processes and returns detailed process descriptions.

        Keyword Arguments:
            user_id {str} -- The identifier of the user (default: {None})
        """

        try:
            process_list = []
            for filename in os.listdir(os.environ.get('PROCESS_API_DIR')):
                if os.path.splitext(filename)[-1] == '.json':
                    process_path = os.path.join(os.environ.get('PROCESS_API_DIR'), filename)
                    with open(process_path, 'r') as f:
                        process_list.append(json.load(f))

            return_data = {
                "processes": process_list,
                "links": []  # TODO add links
            }
            return {
                "status": "success",
                "code": 200,
                "data": return_data
            }

        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()


class ProcessesGraphService:
    """Management of stored process graphs.
    """

    name = "process_graphs"
    db = DatabaseSession(Base)
    process_service = RpcProxy("processes")
    data_service = RpcProxy("data")
    validator = Validator()
    node_parser = NodeParser()

    @rpc
    def get(self, user_id: str, process_graph_id: str):
        """The request will ask the back-end to get the process graph using the process_graph_id.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            process_graph_id {str} -- The id of the process graph
        """
        try:
            process_graph = self.db.query(ProcessGraph).filter_by(id=process_graph_id).first()
            valid, response = self.authorize(user_id, process_graph_id, process_graph)
            if not valid:
                return response

            return {
                "status": "success",
                "code": 200,
                "data": ProcessGraphFullSchema().dump(process_graph).data
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def delete(self, user_id: str, process_graph_id: str):
        """The request will ask the back-end to delete the process graph with the given process_graph_id.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            process_graph_id {str} -- The id of the process graph
        """
        try:
            # Check process graph exists and user is allowed to access / delete it
            process_graph = self.db.query(ProcessGraph).filter_by(id=process_graph_id).first()
            valid, response = self.authorize(user_id, process_graph_id, process_graph)
            if not valid:
                return response

            self.db.delete(process_graph)
            self.db.commit()
            return {
                "status": "success",
                "code": 204
            }

        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1process_graphs~1{process_graph_id}/delete"]).to_dict()

    @rpc
    def modify(self, user_id: str, process_graph_id: str, **process_graph_args):
        """The request will ask the back-end to modify the process graph with the given process_graph_id.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            process_graph_id {str} -- The id of the process graph
        """
        try:
            process_graph = self.db.query(ProcessGraph).filter_by(id=process_graph_id).first()
            valid, response = self.authorize(user_id, process_graph_id, process_graph)
            if not valid:
                return response

            process_graph.update(**process_graph_args)
            self.db.merge(process_graph)
            self.db.commit()

            return {
                "status": "success",
                "code": 204
            }

        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1process_graphs~1{process_graph_id}/patch"]).to_dict()

    @rpc
    def get_all(self, user_id: str):
        """The request will ask the back-end to get all available process graphs for the given user.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
        """
        try:
            process_graphs = self.db.query(ProcessGraph).filter_by(user_id=user_id).order_by(ProcessGraph.created_at).all()
            return {
                "status": "success",
                "code": 200,
                "data": {
                    "process_graphs": ProcessGraphShortSchema(many=True).dump(process_graphs).data,
                    "links": []}
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1process_graphs/get"]).to_dict()

    @rpc
    def create(self, user_id: str, **process_graph_args):
        """The request will ask the back-end to create a new process graph using the description send in the request body.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            **process_graph_args {dict} -- The dictionary containing information needed to create a ProcessGraph
        """

        try:
            process_graph_json = deepcopy(process_graph_args.get("process_graph", {}))

            validate = self.validate(user_id, process_graph_json)
            if validate["status"] == "error":
                return validate

            process_graph = ProcessGraph(**{"user_id": user_id, **process_graph_args})
            process_graph_id = str(process_graph.id)
            self.db.add(process_graph)
            self.db.commit()

            return {
                "status": "success",
                "code": 201,
                "headers": {
                    "Location": "/process_graphs/" + process_graph_id,
                    "OpenEO-Identifier": process_graph_id
                },
                "service_data": process_graph_id
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def validate(self, user_id: str, process_graph: dict):
        """The request will ask the back-end to create a new process using the description send in the request body.

        Keyword Arguments:
            user_id {str} -- The identifier of the user (default: {None})
        """
        # TODO: RESPONSE HEADERS -> OpenEO-Costs

        try:
            # Get all processes
            process_response = self.process_service.get_all()
            if process_response["status"] == "error":
                return process_response
            processes = process_response["data"]["processes"]

            # # Get all products
            # product_response = self.data_service.get_all_products()
            # if product_response["status"] == "error":
            #     return product_response
            # products = product_response["data"]
            
            valid = validate_process_graph(process_graph, processes_list=processes)
            if valid:
                output_errors = []
            else:
                # TODO clarify errors -> use again json schemas for validation
                output_errors = [
                    {
                        "message": "error."
                    }
                ]

            # self.validator.update_datasets(processes, products)
            # self.validator.validate_node(process_graph)

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

    @staticmethod
    def authorize(user_id: str, process_graph_id: str, process_graph: ProcessGraph):
        """Return Exception if given ProcessGraph does not exist or User is not allowed to access this ProcessGraph.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            process_graph_id {str} -- The id of the process graph
            process_graph {ProcessGraph} -- The ProcessGraph object for the given process_graph_id
        """
        if process_graph is None:
            return False, ServiceException(ProcessesService.name, 400, user_id,
                                           "The process_graph with id '{0}' does not exist.".format(process_graph_id),
                                           internal=False,
                                           links=[
                                               "#tag/Job-Management/paths/~1process_graphs~1{process_graph_id}/get"]).to_dict()

        # TODO: Permission (e.g admin)
        if process_graph.user_id != user_id:
            return False, ServiceException(ProcessesService.name, 401, user_id,
                                           "You are not allowed to access this resource.", internal=False,
                                           links=[
                                               "#tag/Job-Management/paths/~1process_graphs~1{process_graph_id}/get"]).to_dict()
        return True, None
