""" Process Discovery """

from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession
from sqlalchemy import exc

from .models import Base, Process
from .schema import ProcessSchema


service_name = "processes"


class ServiceException(Exception):
    """ServiceException raises if an exception occured while processing the 
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(self, code: int, user_id: str, msg: str,
                 internal: bool=True, links: list=[]):
        self._service = service_name
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

    name = service_name
    db = DatabaseSession(Base)

    @rpc
    def create_process(self, user_id: str=None, **process_args):
        """he request will ask the back-end to create a new process using the desciption send in the request body.

        Keyword Arguments:
            user_id {str} -- The identifier of the user (default: {None})
        """

        try:
            process = Process(**process_args)

            self.db.add(process)
            self.db.commit()

            return {
                "status": "success",
                "data": "The process {0} has been successfully created.".format(process_args["name"])
            }
        except exc.IntegrityError as exp:
            msg = "Process '{0}' does already exist.".format(
                process_args["name"])
            return ServiceException(400, user_id, msg, internal=False,
                                    links=["#tag/EO-Data-Discovery/paths/~1processes/post"]).to_dict()
        except Exception as exp:
            return ServiceException(500, user_id, str(exp)).to_dict()

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
            return ServiceException(500, user_id, str(exp)).to_dict()

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
