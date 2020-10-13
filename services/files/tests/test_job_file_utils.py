"""Test utilities provided by files service but used by the jobs service."""
import shutil
from os import listdir, makedirs, sep
from os.path import isdir, isfile, join
from typing import Tuple

from nameko.testing.services import worker_factory

from files.service import FilesService
from .utils import create_user

file_service = worker_factory(FilesService)


def test_setup_job_result_folder(user_id_folder: Tuple[str, str]) -> None:
    """Check the job results folder is setup correctly."""
    user_folder, user_id = user_id_folder
    job_folder_ref = join(user_folder, 'jobs', 'test-job')

    file_service.setup_jobs_result_folder(user_id=user_id, job_id='test-job')

    assert isdir(job_folder_ref)
    job_runs = [d for d in listdir(job_folder_ref) if isdir(join(job_folder_ref, d))]
    assert len(job_runs) == 1
    assert isdir(join(job_folder_ref, job_runs[0], 'result'))


def test_download_result(user_id_folder: Tuple[str, str], upload_file: str) -> None:
    """Test the download result method returns a proper dictionary."""
    user_folder, user_id = user_id_folder
    user = create_user(user_id)
    file_service.setup_jobs_result_folder(user_id=user_id, job_id='test-job')
    folder_path = join(user_folder, 'jobs', 'test-job', 'jr-20201012T122939924612', 'result')
    makedirs(folder_path)
    filepath = join(folder_path, 'download.txt')
    shutil.copyfile(upload_file, filepath)
    assert isfile(filepath)

    result = file_service.download_result(user=user, job_id='test-job',
                                          path='jr-20201012T122939924612/result/download.txt')
    assert result == {
        'status': 'success',
        'code': 200,
        'headers': {'Content-Type': 'application/octet-stream'},
        'file': filepath
    }
    assert isfile(filepath)


def test_get_job_id_folder(user_id_folder: Tuple[str, str]) -> None:
    """Test the path to a specific job folder is properly build."""
    user_folder, user_id = user_id_folder
    assert file_service.get_job_id_folder(user_id=user_id, job_id='test-job') == \
           join(user_folder, 'jobs', 'test-job')


def test_upload_stop_file(user_id_folder: Tuple[str, str]) -> None:
    """Test the stop-file is properly created."""
    user_folder, user_id = user_id_folder
    file_service.setup_jobs_result_folder(user_id=user_id, job_id='test-job')
    file_service.upload_stop_job_file(user_id=user_id, job_id='test-job')
    job_run_folder = join(user_folder, 'jobs', 'test-job',
                          file_service.get_latest_job_run_folder_name(user_id, 'test-job'))
    assert isfile(join(user_folder, 'jobs', 'test-job', job_run_folder, 'STOP'))


def create_job(user_folder: str, user_id: str, upload_file: str) -> Tuple[str, str, str]:
    """Upload several files and check they are properly created - utils method."""
    file_service.setup_jobs_result_folder(user_id=user_id, job_id='test-job')
    job_run_folder = join(user_folder, 'jobs', 'test-job',
                          file_service.get_latest_job_run_folder_name(user_id, 'test-job'))

    results_folder = join(job_run_folder, 'result')
    assert isdir(results_folder)
    folder1 = join(job_run_folder, 'folder1')
    folder2 = join(job_run_folder, 'folder2')
    makedirs(folder1)
    makedirs(folder2)

    file1 = join(folder1, '1.txt')
    file2 = join(folder2, '2.txt')
    file_result = join(results_folder, 'result.txt')
    shutil.copyfile(upload_file, file1)
    shutil.copyfile(upload_file, file2)
    shutil.copyfile(upload_file, file_result)

    assert isfile(file1)
    assert isfile(file2)
    assert isfile(file_result)
    return file_result, file1, file2


def test_delete_complete_job(user_id_folder: Tuple[str, str], upload_file: str) -> None:
    """Test all files connected to a job are deleted."""
    user_folder, user_id = user_id_folder
    file_results, file1, file2 = create_job(user_folder, user_id, upload_file)
    file_service.delete_complete_job(user_id=user_id, job_id='test-job')
    assert not isfile(file1)
    assert not isfile(file2)
    assert not isfile(file_results)


def test_delete_job_without_results(user_id_folder: Tuple[str, str], upload_file: str) -> None:
    """Test everything besides the results folder is deleted."""
    user_folder, user_id = user_id_folder
    file_results, file1, file2 = create_job(user_folder, user_id, upload_file)
    file_service.delete_job_without_results(user_id=user_id, job_id='test-job')
    assert not isfile(file1)
    assert not isfile(file2)
    assert isfile(file_results)


def test_delete_old_job_runs(user_id_folder: Tuple[str, str]) -> None:
    """Check all old job runs are deleted correctly."""
    user_folder, user_id = user_id_folder
    job_id_folder = join(user_folder, 'jobs', 'test-job')

    def create_job_run_folder() -> str:
        file_service.setup_jobs_result_folder(user_id=user_id, job_id='test-job')
        result_folder = join(job_id_folder, file_service.get_latest_job_run_folder_name(user_id, 'test-job'), 'result')
        assert isdir(result_folder)
        return result_folder

    created_dirs = [create_job_run_folder() for _ in range(5)]
    latest = created_dirs[-1].split(sep)[-2]

    file_service.delete_old_job_runs(user_id, 'test-job')

    existing_dirs = [d for d in listdir(job_id_folder) if isdir(join(job_id_folder, d))]
    assert len(existing_dirs) == 1
    assert existing_dirs[0] == latest
