""" Process Discovery """

import os
import requests
import json

from nameko.rpc import rpc, RpcProxy
from nameko_sqlalchemy import DatabaseSession
from sqlalchemy import exc
from copy import deepcopy

from .models import Base, ProcessGraph, ProcessNode
from .schema import ProcessGraphShortSchema, ProcessGraphFullSchema, ProcessNodeSchema
from .dependencies import NodeParser, Validator
from jsonschema import ValidationError


class ServiceException(Exception):
    """ServiceException raises if an exception occured while processing the
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(self, service:str, code: int, user_id: str, msg: str,
                 internal: bool=True, links: list=[]):
        self._service = service
        self._code = code
        self._user_id = user_id
        self._msg = msg
        self._internal = internal
        self._links = links

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

    name = "processes"

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
                "data": "The processes {0} have been successfully created.".format(process_args_str)
            }
        except exc.IntegrityError as exp:
            msg = "Process '{0}' does already exist.".format(process_args_str)
            return ServiceException(ProcessesService.name, 400, user_id, msg, internal=False,
                                    links=["#tag/EO-Data-Discovery/paths/~1processes/post"]).to_dict()
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
        import pdb; pdb.set_trace()
        try:
            process_graph = self.db.query(ProcessGraph).filter_by(id=process_graph_id).first()

            if process_graph is None:
                return ServiceException(ProcessesService.name, 400, user_id,
                    "The process_graph with id '{0}' does not exist.".format(process_graph_id), internal=False,
                    links=["#tag/Job-Management/paths/~1process_graphs~1{process_graph_id}/get"]).to_dict()

            # TODO: Permission (e.g admin)
            if process_graph.user_id != user_id:
                return ServiceException(ProcessesService.name, 401, user_id,
                    "You are not allowed to access this resource.", internal=False,
                    links=["#tag/Job-Management/paths/~1process_graphs~1{process_graph_id}/get"]).to_dict()

            return {
                    "status": "success",
                    "code": 200,
                    "data": ProcessGraphFullSchema().dump(process_graph).data
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def delete(self, user_id: str, process_graph_id: str):
        try:
            raise Exception("Not implemented yet!")
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp),
                    links=["#tag/Job-Management/paths/~1process_graphs~1{process_graph_id}/delete"]).to_dict()

    @rpc
    def modify(self, user_id: str, process_graph_id: str, **process_graph_args):
        try:
            raise Exception("Not implemented yet!")
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp),
                    links=["#tag/Job-Management/paths/~1process_graphs~1{process_graph_id}/patch"]).to_dict()

    @rpc
    def get_all(self, user_id: str):
        try:
            process_graphs = self.db.query(ProcessGraph).order_by(ProcessGraph.created_at).all()

            return {
                "status": "success",
                "code": 200,
                "data": ProcessGraphShortSchema(many=True).dump(process_graphs).data
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp),
                    links=["#tag/Job-Management/paths/~1process_graphs/get"]).to_dict()

    @rpc
    def create(self, user_id: str, **process_graph_args):
        """The request will ask the back-end to create a new process using the description send in the request body.

        Keyword Arguments:
            user_id {str} -- The identifier of the user (default: {None})
        """

        try:
            process_graph_json = deepcopy(process_graph_args.get("process_graph", {}))

            validate = self.validate(user_id, process_graph_json)
            if validate["status"] == "error":
               return validate

            # Get all processes
            process_response = self.process_service.get_all()
            if process_response["status"] == "error":
               return process_response
            processes = process_response["data"]

            process_graph = ProcessGraph(**{"user_id": user_id, **process_graph_args})

            nodes = self.node_parser.parse_process_graph(process_graph_json, processes)
            imagery_id = None
            for idx, node in enumerate(nodes):
                process_node = ProcessNode(
                    user_id=user_id,
                    seq_num=len(nodes) - (idx + 1),
                    imagery_id=imagery_id,
                    process_graph_id=process_graph.id,
                    **node)
                self.db.add(process_node)
                imagery_id = process_node.id

            process_graph_id = str(process_graph.id)
            self.db.add(process_graph)
            self.db.commit()

            return {
                "status": "success",
                "code": 201,
                "headers": {"Location": "https://openeo.eodc.eu/api/v0/TBD"},
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
            processes = process_response["data"]

            # Get all products
            product_response = self.data_service.get_all_products()
            if product_response["status"] == "error":
               return product_response
            products = product_response["data"]

            self.validator.update_datasets(processes, products)
            self.validator.validate_node(process_graph)

            return {
                "status": "success",
                "code": 204
            }
        except ValidationError as exp:
            return ServiceException(ProcessesService.name, 400, user_id, exp.message, internal=False,
                                    links=["#tag/EO-Data-Discovery/paths/~1process_graph/post"]).to_dict()
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def get_nodes(self, user_id: str, process_graph_id: str):

        try:
            process_graph = self.db.query(ProcessGraph).filter_by(id=process_graph_id).first()
            nodes = sorted(process_graph.nodes, key=lambda n: n.seq_num)

            return {
                    "status": "success",
                    "data": ProcessNodeSchema(many=True).dump(nodes).data
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()
