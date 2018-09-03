""" Process Discovery """

from nameko.rpc import rpc, RpcProxy
from nameko_sqlalchemy import DatabaseSession
from sqlalchemy import exc
from uuid import uuid4

from .models import Base, Process, Parameter, ProcessGraph, ProcessNode
from .schema import ProcessSchema
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
    db = DatabaseSession(Base)

    @rpc
    def create_process(self, user_id: str=None, **process_args):
        """The request will ask the back-end to create a new process using the description send in the request body.

        Keyword Arguments:
            user_id {str} -- The identifier of the user (default: {None})
        """

        try:
            parameters = process_args.pop("parameters", {})
            process = Process(**{"user_id": user_id, **process_args})

            for parameter_name, parameter_specs in parameters.items():
                parameter = Parameter(**{"name":parameter_name, "process_id": process.id, **parameter_specs})
                self.db.add(parameter)

            self.db.add(process)
            self.db.commit()

            return {
                "status": "success",
                "data": "The process {0} has been successfully created.".format(process_args["name"])
            }
        except exc.IntegrityError as exp:
            msg = "Process '{0}' does already exist.".format(
                process_args["name"])
            return ServiceException(ProcessesService.name, 400, user_id, msg, internal=False,
                                    links=["#tag/EO-Data-Discovery/paths/~1processes/post"]).to_dict()
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()

    @rpc
    def get_processes(self, user_id: str=None):
        """The request asks the back-end for available processes and returns detailed process descriptions.
        
        Keyword Arguments:
            user_id {str} -- The identifier of the user (default: {None})
        """

        try:
            processes = self.db.query(Process).order_by(Process.name).all()

            return {
                "status": "success",
                "data": ProcessSchema(many=True).dump(processes).data
            }
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()
    
    # @rpc
    # def get_processes(self, user_id):
    #     try:
    #         processes = self.db.query(Process).filter(Process.process_id.like("%{0}%".format(qname))).all() \
    #                     if qname else \
    #                     self.db.query(Process).order_by(Process.process_id).all()

    #         dumped_processes = []
    #         for process in processes:
    #             dumped_processes.append(ProcessSchemaShort().dump(process).data)

    #         return {
    #             "status": "success",
    #             "data": dumped_processes
    #         }
    #     except Exception as exp:
    #         return ServiceException(500, user_id, str(exp)).to_dict()

    # @rpc
    # def get_process(self, user_id, process_id):
    #     try:
    #         process = self.db.query(Process).filter_by(process_id=process_id).first()

    #         if not process:
    #             raise NotFound("Process '{0}' does not exist.".format(process_id))

    #         return {
    #             "status": "success",
    #             "data": ProcessSchema().dump(process)
    #         }
    #     except NotFound as exp:
    #         return ServiceException(400, user_id, str(exp), internal=False,
    #             links=["#tag/EO-Data-Discovery/paths/~1data~1{data_id}/get"]).to_dict() # TODO
    #     except Exception as exp:
    #         return ServiceException(500, user_id, str(exp)).to_dict()

    # @rpc
    # def get_all_processes_full(self, user_id):
    #     try:
    #         processes = self.db.query(Process).order_by(Process.process_id).all()

    #         dumped_processes = []
    #         for process in processes:
    #             dumped_processes.append(ProcessSchemaFull().dump(process).data)

    #         return {
    #             "status": "success",
    #             "data": dumped_processes
    #         }
    #     except Exception as exp:
    #         return ServiceException(500, user_id, str(exp)).to_dict()


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
    def create_process_graph(self, user_id: str=None, **process_graph_args):
        """The request will ask the back-end to create a new process using the description send in the request body.

        Keyword Arguments:
            user_id {str} -- The identifier of the user (default: {None})
        """
        # TODO: RESPONSE HEADERS -> OpenEO-Costs

        try:
            process_graph_json = process_graph_args.pop("process_graph", {})
            processes = self.process_service.get_processes()["data"]
            products = self.data_service.get_all_products()["data"]

            self.validator.update_datasets(processes, products)
            self.validator.validate_node(process_graph_json)
            
            process_graph = ProcessGraph(**{"user_id": user_id, **process_graph_args})

            nodes = self.node_parser.parse_process_graph(process_graph_json)
            imagery_id = None
            for idx, node in enumerate(nodes):
                process_node = ProcessNode(
                    user_id=user_id,
                    seq_num=len(nodes) - idx,
                    imagery_id=imagery_id,
                    process_graph_id=process_graph.id,
                    **node)
                self.db.add(process_node)
                imagery_id = process_node.id

            process_graph_id = process_graph.id
            self.db.add(process_graph)
            self.db.commit()

            # for node_name, node_specs in process_graph_nodes.items():
            #     parameter = Parameter(**{"id": uuid4(), "name":parameter_name, "process_id": process.id, **parameter_specs})
            #     self.db.add(parameter)

            # self.db.add(process)
            # self.db.commit()

            return {
                "status": "success",
                "data": process_graph_id
            }
        except ValidationError as exp:
            return ServiceException(ProcessesService.name, 400, user_id, exp.message, internal=False,
                                    links=["#tag/EO-Data-Discovery/paths/~1process_graph/post"]).to_dict()
        except Exception as exp:
            return ServiceException(ProcessesService.name, 500, user_id, str(exp)).to_dict()
