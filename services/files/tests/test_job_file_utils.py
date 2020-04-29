import os
import shutil


def test_setup_job_result_folder(file_service, user_folder, user_id):
    file_service.setup_jobs_result_folder(user_id=user_id, job_id='test-job')
    assert os.path.isdir(os.path.join(user_folder, 'jobs', 'test-job', 'results'))


def test_download_result(file_service, user_folder, user_id, upload_file):
    file_service.setup_jobs_result_folder(user_id=user_id, job_id='test-job')
    filepath = os.path.join(user_folder, 'jobs', 'test-job', 'download.txt')
    shutil.copyfile(upload_file, filepath)
    assert os.path.isfile(filepath)

    result = file_service.download_result(user_id=user_id, path='test-job/download.txt')
    assert result == {
        'status': 'success',
        'code': 200,
        'headers': {'Content-Type': 'application/octet-stream'},
        'file': filepath
    }
    assert os.path.isfile(filepath)


def test_get_job_id_folder(file_service, user_folder, user_id):
    assert file_service.get_job_id_folder(user_id=user_id, job_id='test-job') == \
           os.path.join(user_folder, 'jobs', 'test-job')


def test_get_job_result_folder(file_service, user_folder, user_id):
    assert file_service.get_job_results_folder(user_id=user_id, job_id='test-job') == \
           os.path.join(user_folder, 'jobs', 'test-job', 'results')


def test_upload_stop_file(file_service, user_folder, user_id):
    file_service.setup_jobs_result_folder(user_id=user_id, job_id='test-job')
    file_service.upload_stop_job_file(user_id=user_id, job_id='test-job')
    assert os.path.isfile(os.path.join(user_folder, 'jobs', 'test-job', 'STOP'))


def create_job(file_service, user_folder, user_id, upload_file):
    file_service.setup_jobs_result_folder(user_id=user_id, job_id='test-job')
    results_folder = os.path.join(user_folder, 'jobs', 'test-job', 'results')
    assert os.path.isdir(results_folder)
    job_id_folder = os.path.join(user_folder, 'jobs', 'test-job')
    folder1 = os.path.join(job_id_folder, 'folder1')
    folder2 = os.path.join(job_id_folder, 'folder2')
    os.makedirs(folder1)
    os.makedirs(folder2)
    file1 = os.path.join(folder1, '1.txt')
    file2 = os.path.join(folder2, '2.txt')
    file_result = os.path.join(results_folder, 'result.txt')
    shutil.copyfile(upload_file, file1)
    shutil.copyfile(upload_file, file2)
    shutil.copyfile(upload_file, file_result)
    assert os.path.isfile(file1)
    assert os.path.isfile(file2)
    return file_result, file1, file2


def test_delete_complete_job(file_service, user_folder, user_id, upload_file):
    file_results, file1, file2 = create_job(file_service, user_folder, user_id, upload_file)
    file_service.delete_complete_job(user_id=user_id, job_id='test-job')
    assert not os.path.isfile(file1)
    assert not os.path.isfile(file2)
    assert not os.path.isfile(file_results)


def test_delete_job_without_results(file_service, user_folder, user_id, upload_file):
    file_results, file1, file2 = create_job(file_service, user_folder, user_id, upload_file)
    file_service.delete_job_without_results(user_id=user_id, job_id='test-job')
    assert not os.path.isfile(file1)
    assert not os.path.isfile(file2)
    assert os.path.isfile(file_results)
