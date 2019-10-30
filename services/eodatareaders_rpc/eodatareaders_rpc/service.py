""" Exec sync jobs """

import os
import glob
from subprocess import Popen
from time import sleep
from uuid import uuid4
from nameko.rpc import rpc, RpcProxy

from eodc_openeo_bindings.write_basic_job import write_basic_job
from eodatareaders.eo_data_reader import eoDataReader


service_name = "eodatareaders_rpc"

class ServiceException(Exception):
    """ServiceException raises if an exception occured while processing the
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(self, code: int, user_id: str, msg: str, internal: bool=True, links: list=None):
        if not links:
            links = []

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

class EoDataReadersService:
    """Management of sync processing jobs and their results.
    """

    name = service_name

    @rpc
    def process_sync(self, user_id: str, process_graph: dict):
        """The request will ask the back-end to get the job using the job_id.

        Keyword Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The id of the job
        """
        try:
            
            # Create folder for tmp job
            job_tmp_id = str(uuid4())
            job_folder = os.path.join(os.environ['SYNC_RESULTS_FOLDER'], job_tmp_id)
            out_filepath = os.path.join(job_folder, 'jb-' + job_tmp_id + '.py')
            os.makedirs(job_folder)
            output_format, output_folder = write_basic_job(process_graph, job_folder, python_filepath=out_filepath)
            if output_format == 'Gtiff':
                output_format = '.tif'
            output_format = 'application/octet-stream'
            
            cmd = "python " + out_filepath
            out = Popen(cmd, shell=True).wait()
            results_path = glob.glob(output_folder + '*' + output_format)
            
            # results_path = filepath  # TODO needs to be set before
            # extension = results_path.split('.')[-1]  # maybe MIME type could be returned from process_graph
            return {
                "status": "success",
                "code": 200,
                "headers": {
                    "Content-Type": output_format,
                    "OpenEO-Costs": 0
                },
                "file": results_path,
                "delete_file": True,
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs~1{job_id}/get"]).to_dict()
