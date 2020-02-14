""" Exec sync jobs """

import os
import glob
import logging
from subprocess import Popen
from uuid import uuid4
from nameko.rpc import rpc
from collections import namedtuple

from eodc_openeo_bindings.job_writer.basic_writer import BasicJobWriter


service_name = "eodatareaders_rpc"
LOGGER = logging.getLogger('standardlog')

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

            output_format, output_folder = BasicJobWriter(process_graph, job_folder, output_filepath=py_filepath).write_job()
            fmt = self.map_output_format(output_format)

            cmd = "python " + py_filepath
            Popen(cmd, shell=True).wait()
            # TODO catch errors happening while processing

            search_str = os.path.join(output_folder, '*.' + type_map[fmt].file_extension)
            results_path = sorted(glob.glob(search_str))
            if not results_path:
                raise RuntimeError('Processing failed. Result paths: {} - Search string: {}'.format(results_path, search_str))
            else:
                # TODO this only returns one file (the first) -> API endpoint does not allow to return more currently
                result_path = results_path[0]

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
