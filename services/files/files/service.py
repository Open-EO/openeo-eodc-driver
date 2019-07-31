""" Files Management """

import os
import shutil
from nameko.rpc import rpc
from werkzeug.security import safe_join
from typing import List, Optional
import re

service_name = "files"


class ServiceException(Exception):
    """ServiceException raises if an exception occurs while processing the
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
            "links": self._links,
        }


class FileOperationUnsupported(ServiceException):
    """ FileOperationUnsupported raised if folder is passed when file is expected.
    """
    def __init__(self, code: int, user_id: str, msg: str, internal: bool=True, links: list=None):
        super(FileOperationUnsupported, self).__init__(code, user_id, msg, internal, links)


class FilesService:
    """Management of batch processing tasks (jobs) and their results.
    """

    name = service_name

    # each directory / file name is only allowed to use a max. of 200 Alpha-Numeric characters
    allowed_dirname = re.compile(r'[a-zA-Z0-9_]{1,200}')
    allowed_filename = re.compile(r'[a-zA-Z0-9_]{1,200}\.[a-zA-Z0-9]{1,10}')

    files_folder = "files"
    jobs_folder = "jobs"

    @rpc
    def download(self, user_id: str, path: str):
        """The request will ask the back-end to get the job using the job_id.

        Arguments:
            user_id {str} -- The identifier of the user
            path {str} -- The file path to the requested file
        """
        try:
            valid, err, complete_path = self.authorize_existing_file(user_id, path)
            if not valid:
                return err

            return {
                "status": "success",
                "code": 200,
                "headers": {"Content-Type": "application/octet-stream"},
                "file": complete_path,
            }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=["files/" + user_id]).to_dict()

    @rpc
    def delete(self, user_id: str, path: str):
        """The request will ask the back-end to delete the file at the given path.

        Arguments:
            user_id {str} -- The identifier of the user
            path {str} -- The location of the file
        """
        try:
            valid, err, complete_path = self.authorize_existing_file(user_id, path)
            if not valid:
                return err
            os.remove(complete_path)
            return {
                "status": "success",
                "code": 204
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=["/files/" + user_id]).to_dict()

    @rpc
    def get_all(self, user_id: str):
        """The request will ask the back-end to get all available files for the given user.

        Arguments:
            user_id {str} -- The identifier of the user
        """
        try:
            prefix, _ = self.setup_user_folder(user_id)
            file_list = []

            for root, dirs, files in os.walk(prefix):
                user_root = root[len(prefix) + 1:]
                for f in files:
                    file_list.append(
                        {
                            "path": os.path.join(user_root, f),
                            "size": self.sizeof_fmt(os.path.getsize(os.path.join(root, f)))
                        }
                    )

            return {
                "status": "success",
                "code": 200,
                "data": {
                    "files": file_list,
                    "links": ["/files/" + user_id]
                }
            }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=["/files/" + user_id]).to_dict()

    @rpc
    def upload(self, user_id: str, path: str, tmp_path: str):
        """The request will ask the back-end to create a new job using the description send in the request body.

        Arguments:
            user_id {str} -- The identifier of the user
            path {str} -- The file path to the requested file
            tmp_path {str} -- The path where the file was temporary stored
        """
        try:
            valid, err, complete_path = self.authorize_file(user_id, path)
            if not valid:
                os.remove(tmp_path)
                return err

            dirs, filename = os.path.split(complete_path)
            if not os.path.exists(dirs):
                os.makedirs(dirs, mode=664)

            os.rename(tmp_path, complete_path)

            return {
                "status": "success",
                "code": 200,
                "data": {
                    "path": complete_path[len(self.get_user_folder(user_id)) + 1:],
                    "size": self.sizeof_fmt(os.path.getsize(complete_path))
                }
            }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=["/files/" + user_id]).to_dict()

    @rpc
    def setup_user_folder(self, user_id: str) -> list:
        """
        Create user folder with files and jobs structure and return the paths.

        Arguments:
            user_id {str} -- The identifier of the user
        """
        user_dir = self.get_user_folder(user_id)
        dirs_to_create = [os.path.join(user_dir, dir_name) for dir_name in [self.files_folder, self.jobs_folder]]

        for d in dirs_to_create:
            if not os.path.exists(d):
                os.makedirs(d, mode=664)

        return dirs_to_create

    @staticmethod
    def get_user_folder(user_id: str) -> str:
        return os.path.join(os.environ.get("OPENEO_FILES_DIR"), user_id)

    @rpc
    def setup_jobs_folder(self, user_id: str, job_id: str) -> None:
        """
        Create user folder structure with folder for the given job_id.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The identifier for the job
        """
        _, jobs_dir = self.setup_user_folder(user_id)
        to_create = os.path.join(jobs_dir, job_id)

        if os.path.exists(to_create):
            shutil.rmtree(to_create)
        os.makedirs(to_create, mode=664)

    def authorize_file(self, user_id: str, path: str):
        """
        Returns Exception if path is invalid or points to a directory.

        Arguments:
            user_id {str} -- The identifier of the user
            path {str} -- The file path to the requested file
        """

        # check pattern
        complete_path = self.get_allowed_path(user_id, path.split('/'))
        if not complete_path:
            return False, FileOperationUnsupported(404, user_id, "{0}: This path is not valid.".format(path),
                                                   internal=False, links=["/files/" + user_id]).to_dict(), None

        if os.path.isdir(complete_path):
            return False, FileOperationUnsupported(400, user_id, "{0}: Must be a file, no directory.".format(path),
                                                   internal=False, links=["/files/" + user_id]).to_dict(), None
        return True, None, complete_path

    def authorize_existing_file(self, user_id: str, path: str):
        """
        Returns Exception if path is invalid, points to a directory or does not exist.

        Arguments:
            user_id {str} -- The identifier of the user
            path {str} -- The file path to the requested file
        """
        valid, err, complete_path = self.authorize_file(user_id, path)
        if valid:
            # check existence
            if not os.path.exists(complete_path):
                return False, FileOperationUnsupported(404, user_id, "{0}: No such file or directory.".format(path),
                                                       internal=False, links=["/files/" + user_id]).to_dict(), None
        return valid, err, complete_path

    def get_allowed_path(self, user_id: str, parts: List[str]) -> Optional[str]:
        """ Checks if file has an allowed extension

        Arguments:
            parts {List[str]} -- List of all directories and the filename
        """
        files_dir, _ = self.setup_user_folder(user_id)

        filename = parts.pop(-1)
        for part in parts:
            if re.fullmatch(self.allowed_dirname, part) is None:
                return
        if re.fullmatch(self.allowed_filename, filename) is None:
            return

        return safe_join(files_dir, *parts, filename)

    @staticmethod
    def sizeof_fmt(num: float) -> str:
        """Return human readable file size.

        Arguments:
            num {float} -- The number of bytes to convert.
        """
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%sB" % (num, unit)
            num /= 1024.0
        return "%.1f%sB" % (num, 'Yi')
