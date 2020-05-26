""" Files Management """

import glob
import logging
import os
import re
import time
from datetime import datetime
from typing import List, Optional, Tuple
import shutil

from nameko.rpc import rpc
from werkzeug.security import safe_join

service_name = "files"
LOGGER = logging.getLogger('standardlog')


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
    allowed_dirname = re.compile(r'[a-zA-Z0-9_-]{1,200}')
    allowed_filename = re.compile(r'[a-zA-Z0-9_-]{1,200}\.[a-zA-Z0-9]{1,10}')

    files_folder = "files"
    jobs_folder = "jobs"
    result_folder = "results"

    @rpc
    def download(self, user_id: str, path: str, source_dir: str = 'files') -> dict:
        """
        The request will ask the back-end to get the get the file stored at the given path.

        Arguments:
            user_id {str} -- The identifier of the user
            path {str} -- The file path to the requested file
        """
        try:
            valid, err, complete_path = self.authorize_existing_file(user_id, path, source_dir=source_dir)
            if not valid:
                return err

            LOGGER.info(f"Download file {path}")
            return {
                "status": "success",
                "code": 200,
                "headers": {"Content-Type": "application/octet-stream"},
                "file": complete_path,
            }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=[]).to_dict()

    @rpc
    def delete(self, user_id: str, path: str) -> dict:
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
            LOGGER.info(f"File {path} successfully deleted.")
            return {
                "status": "success",
                "code": 204
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=[]).to_dict()

    @rpc
    def get_all(self, user_id: str) -> dict:
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
                    public_filepath = os.path.join(user_root, f)
                    internal_filepath = os.path.join(root, f)
                    file_list.append(
                        {
                            "path": public_filepath,
                            "size": int(os.path.getsize(internal_filepath)),
                            "modified": self.get_file_modification_time(internal_filepath)
                        }
                    )
            LOGGER.info(f"Found {len(file_list)} files in workspace of User {user_id}.")
            return {
                "status": "success",
                "code": 200,
                "data": {
                    "files": sorted(file_list, key=lambda file: file['path']),
                    "links": [],
                }
            }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=[]).to_dict()

    @rpc
    def upload(self, user_id: str, path: str, tmp_path: str) -> dict:
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
                os.makedirs(dirs, mode=0o700)

            os.rename(tmp_path, complete_path)
            LOGGER.info(f"File {path} successfully uploaded to User {user_id} workspace.")
            return {
                "status": "success",
                "code": 200,
                "data": {
                    "path": self.complete_to_public_path(user_id, complete_path),
                    "size": int(os.path.getsize(complete_path)),
                    "modified": self.get_file_modification_time(complete_path)
                }
            }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp), links=[]).to_dict()

    @rpc
    def setup_user_folder(self, user_id: str) -> List[str]:
        """
        Create user folder with files and jobs structure and return the paths.

        Arguments:
            user_id {str} -- The identifier of the user
        """
        user_dir = self.get_user_folder(user_id)
        dirs_to_create = [os.path.join(user_dir, dir_name) for dir_name in [self.files_folder, self.jobs_folder]]

        for d in dirs_to_create:
            if not os.path.exists(d):
                LOGGER.info(f"Folder {d} successfully created")
                os.makedirs(d)

        LOGGER.info(f"User folder successfully setup for User {user_id}.")
        return dirs_to_create

    @staticmethod
    def get_user_folder(user_id: str) -> str:
        return os.path.join(os.environ.get("OPENEO_FILES_DIR"), user_id)

    def authorize_file(self, user_id: str, path: str, source_dir: str = 'files') -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        Returns Exception if path is invalid or points to a directory.

        Arguments:
            user_id {str} -- The identifier of the user
            path {str} -- The file path to the requested file

        Returns
            Tuple[bool, Optional[dict], Optional[str]] -- if authorized, error, complete path
        """

        # check pattern
        complete_path = self.get_allowed_path(user_id, path.split('/'), source_dir=source_dir)
        if not complete_path:
            return False, FileOperationUnsupported(401, user_id, f"{path}: This path is not valid.",
                                                   internal=False, links=[]).to_dict(), None

        if os.path.isdir(complete_path):
            return False, FileOperationUnsupported(400, user_id, f"{path}: Must be a file, no directory.",
                                                   internal=False, links=[]).to_dict(), None
        LOGGER.info(f'User {user_id} is granted access to {path}')
        return True, None, complete_path

    def authorize_existing_file(self, user_id: str, path: str, source_dir: str = 'files') -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        Returns Exception if path is invalid, points to a directory or does not exist.

        Arguments:
            user_id {str} -- The identifier of the user
            path {str} -- The file path to the requested file

        Returns:
            Tuple[bool, Optional[dict], Optional[str]] -- if authorized, error, complete path
        """
        valid, err, complete_path = self.authorize_file(user_id, path, source_dir=source_dir)
        if valid:
            # check existence
            if not os.path.exists(complete_path):
                return False, FileOperationUnsupported(404, user_id, f"{path}: No such file or directory.",
                                                       internal=False, links=[]).to_dict(), None
        LOGGER.info(f"File {path} exists.")
        return valid, err, complete_path

    def get_allowed_path(self, user_id: str, parts: List[str], source_dir: str = 'files') -> Optional[str]:
        """ Checks if file matches allowed pattern.

        Arguments:
            parts {List[str]} -- List of all directories and the filename

        Returns:
            Optional[str] -- The path, if it is allowed otherwise None
        """
        files_dir, jobs_dir = self.setup_user_folder(user_id)
        if source_dir == 'files':
            out_dir = files_dir
        else:
            out_dir = jobs_dir

        filename = parts.pop(-1)
        for part in parts:
            if re.fullmatch(self.allowed_dirname, part) is None:
                return
        if re.fullmatch(self.allowed_filename, filename) is None:
            return

        return safe_join(out_dir, *parts, filename)

    def complete_to_public_path(self, user_id: str, complete_path: str) -> str:
        """
        Creates the public path seen by the user from a path on the file system.

        Arguments:
            user_id {str} -- The identifier of the user
            complete_path {str} -- A complete file path on the file system

        Returns:
            {str} -- The corresponding public path to the file visible to the user
        """

        return complete_path.replace(f'{self.get_user_folder(user_id)}/files/', '')

    def get_file_modification_time(self, filepath: str) -> datetime.timestamp:
        """
        Returns timestamp of last modification in format: '2019-05-21T16:11:37Z'.
        
        Returns:
            {str} -- The timestamp when the file was last modified.
        """

        numeric_tstamp = os.path.getmtime(filepath)
        timestamp = datetime.fromtimestamp(numeric_tstamp).isoformat("T", "seconds") + "Z"

        return timestamp

    # needed for job management
    @rpc
    def setup_jobs_result_folder(self, user_id: str, job_id: str) -> None:
        """
        Create user folder structure with folder for the given job_id.

        Arguments:
            user_id {str} -- The identifier of the user
            job_id {str} -- The identifier for the job
        """
        self.setup_user_folder(user_id)
        to_create = self.get_job_results_folder(user_id, job_id)
        if not os.path.exists(to_create):
            LOGGER.debug(f"Creating Job results folder {to_create}.")
            os.makedirs(to_create)
        LOGGER.info(f"Job results folder {to_create} exists.")

    @rpc
    def get_job_output(self, user_id: str, job_id: str):
        """
        Returns a list of output files produced by a job.
        """
        try:
            file_list = glob.glob(os.path.join(self.get_job_results_folder(user_id, job_id), '*'))
            if not file_list:
                return ServiceException(400, user_id, f"Job output folder is empty. No files generated.")

            LOGGER.info(f"Found {len(file_list)} output files for job {job_id}.")
            return {
                "status": "success",
                "code": 200,
                "data": {"file_list": [self.complete_to_public_path(user_id, f) for f in file_list]}
            }

        except Exception as exp:
            return ServiceException(500, user_id, str(exp)).to_dict()

    @rpc
    def download_result(self, user_id: str, path: str) -> dict:
        """
        The request will ask the back-end to get the get the job result stored at the given path.

        Arguments:
            user_id {str} -- The identifier of the user
            path {str} -- The file path to the requested file
        """
        return self.download(user_id, path, source_dir='jobs')

    @rpc
    def upload_stop_job_file(self, user_id: str, job_id: str) -> None:
        """
        Creates an empty file called STOP in a job directory.

        This is used in the current Airflow setup to stop a dag.

        Arguments:
            user_id {str} - The identifier of the user
            job_id {str} -- The  identifier of the job
        """
        job_folder = self.get_job_id_folder(user_id, job_id)
        open(os.path.join(job_folder, 'STOP'), 'a').close()
        LOGGER.info(f"STOP file added to job folder {job_folder}.")

    @rpc
    def delete_complete_job(self, user_id: str, job_id: str) -> None:
        """
        Deletes the complete job folder of the given job.

        Arguments:
            user_id {str} - The identifier of the user
            job_id {str} -- The  identifier of the job
        """
        job_folder = self.get_job_id_folder(user_id, job_id)
        shutil.rmtree(job_folder)
        LOGGER.info(f"Complete job folder for job {job_id} deleted.")

    @rpc
    def delete_job_without_results(self, user_id: str, job_id: str) -> bool:
        """
        Deletes everything in the job folder but the results folder of the given job.

        Arguments:
            user_id {str} - The identifier of the user
            job_id {str} -- The  identifier of the job

        Returns:
            {bool} -- Whether there are results available or not
        """
        job_result_folder = self.get_job_results_folder(user_id, job_id)
        if os.listdir(job_result_folder) == 0:
            LOGGER.info(f"No results exist for job {job_id}.")
            self.delete_complete_job(user_id, job_id)
            self.setup_jobs_result_folder(user_id, job_id)
        else:
            LOGGER.info(f"Job {job_id} has results.")
            bak_result_folder = os.path.join(self.get_user_folder(user_id=user_id), f"{job_id}_backup")
            os.makedirs(bak_result_folder)
            LOGGER.debug(f"Results backup folder created for job {job_id}.")

            os.rename(job_result_folder, bak_result_folder)
            self.delete_complete_job(user_id, job_id)
            self.setup_jobs_result_folder(user_id, job_id)
            os.rename(bak_result_folder, job_result_folder)

            if os.path.isdir(bak_result_folder):
                shutil.rmtree(bak_result_folder)
            LOGGER.debug(f"Results backup folder delete for job {job_id}.")

        return os.listdir(job_result_folder) != 0

    def get_job_id_folder(self, user_id: str, job_id: str) -> str:
        """
        Creates the complete path to a specific job folder.

        Arguments:
            user_id {str} - The identifier of the user
            job_id {str} -- The  identifier of the job
        """
        return os.path.join(self.get_user_folder(user_id), self.jobs_folder, job_id)

    def get_job_results_folder(self, user_id: str, job_id: str) -> str:
        """
        Create the path to a result folder in a specific job folder.

        Arguments:
            user_id {str} - The identifier of the user
            job_id {str} -- The  identifier of the job
        """
        return os.path.join(self.get_job_id_folder(user_id, job_id), self.result_folder)
