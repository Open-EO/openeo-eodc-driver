""" Exec sync jobs """

import os
import glob
from subprocess import Popen
from uuid import uuid4
from nameko.rpc import rpc
from collections import namedtuple

from eodc_openeo_bindings.write_basic_job import write_basic_job


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
        TypeMap = namedtuple('TypeMap', 'file_extension content_type')
        type_map = {
            'Gtiff': TypeMap('tif', 'image/tiff'),
            'png': TypeMap('png', 'image/png'),
            'jpeg': TypeMap('jpeg', 'image/jpeg'),
        }

        try:
            # Create folder for tmp job
            job_tmp_id = str(uuid4())
            job_folder = os.path.join(os.environ['SYNC_RESULTS_FOLDER'], job_tmp_id)
            os.makedirs(job_folder)
            py_filepath = os.path.join(job_folder, 'jb-' + job_tmp_id + '.py')

            output_format, output_folder = write_basic_job(process_graph, job_folder, python_filepath=py_filepath)
            fmt = self.map_output_format(output_format)

            cmd = "python " + py_filepath
            Popen(cmd, shell=True).wait()
            # TODO catch errors happening while processing

            results_path = glob.glob(output_folder + '*.' + type_map[fmt].file_extension)
            if len(results_path) == 1:
                result_path = results_path[0]
            else:
                raise RuntimeError('Processing failed. Result paths: {}'.format(results_path))

            return {
                "status": "success",
                "code": 200,
                "headers": {
                    "Content-Type": type_map[fmt].content_type,
                    "OpenEO-Costs": 0,
                },
                "file": result_path
                #"delete_folder": job_folder,
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                                    links=["#tag/Job-Management/paths/~1jobs~1{job_id}/get"]).to_dict()

    @staticmethod
    def map_output_format(output_format):
        out_map = [(['Gtiff', 'GTiff', 'tif', 'tiff'], 'Gtiff'),
                   (['jpg', 'jpeg'], 'jpeg'),
                   (['png'], 'png')
                   ]
        for l, out in out_map:
            if output_format in l:
                return out
        raise ValueError('{} is not a supported output format'.format(output_format))
