from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession
from sqlalchemy import exc

from .models import Base, Process
from .schema import ProcessSchemaFull, ProcessSchema, ProcessSchemaShort
from .exceptions import NotFound

class ProcessesService:
    name = "processes"

    db = DatabaseSession(Base)

    @rpc
    def health(self, request):
        return { "status": "success"}

    @rpc
    def create_process(self, user_id, process_data):
        try:
            process = Process(
                process_data["process_id"], 
                user_id, 
                process_data["description"],
                process_data["process_type"],
                process_data["link"],
                process_data["args"],
                process_data["git_uri"],
                process_data["git_ref"],
                process_data["git_dir"])

            self.db.add(process)
            self.db.commit()

            return {
                "status": "success",
                "data": ProcessSchemaFull().dump(process).data
            }
        except exc.IntegrityError as exp:
            msg = "Process '{0}' does already exist.".format(process_data["process_id"])
            return {"status": "error", "service": self.name, "key": "BadRequest", "msg": msg}
        except Exception as exp:
            return {"status": "error", "service": self.name, "key": "InternalServerError", "msg": str(exp)}

    @rpc
    def get_all_processes(self, qname):
        try:
            processes = self.db.query(Process).filter(Process.process_id.like("%{0}%".format(qname))).all() \
                        if qname else \
                        self.db.query(Process).order_by(Process.process_id).all()

            dumped_processes = []
            for process in processes:
                dumped_processes.append(ProcessSchemaShort().dump(process).data)

            return {
                "status": "success",
                "data": dumped_processes
            }
        except Exception as exp:
            return {"status": "error", "service": self.name, "key": "InternalServerError", "msg": str(exp)}

    @rpc
    def get_process(self, process_id):
        try:
            process = self.db.query(Process).filter_by(process_id=process_id).first()

            if not process:
                raise NotFound("Process '{0}' does not exist.".format(process_id))

            return {
                "status": "success",
                "data": ProcessSchema().dump(process)
            }
        except NotFound as exp:
            return {"status": "error", "service": self.name, "key": "BadRequest", "msg": str(exp)}
        except Exception as exp:
            return {"status": "error", "service": self.name, "key": "InternalServerError", "msg": str(exp)}

    @rpc
    def get_all_processes_full(self):
        try:
            processes = self.db.query(Process).order_by(Process.process_id).all()

            dumped_processes = []
            for process in processes:
                dumped_processes.append(ProcessSchemaFull().dump(process).data)

            return {
                "status": "success",
                "data": dumped_processes
            }
        except Exception as exp:
            return {"status": "error", "service": self.name, "key": "InternalServerError", "msg": str(exp)}
