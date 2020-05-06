import os
import shutil
import pytest


@pytest.mark.parametrize(
    'ref_path',
    ['final.txt', 'folder1/folder2/final.txt']
)
def test_upload_path(file_service, user_folder, user_id, tmp_folder, upload_file, ref_path):
    tmp_path = os.path.join(tmp_folder, 'upload.txt')
    shutil.copyfile(upload_file, tmp_path)
    assert os.path.isfile(tmp_path)

    result = file_service.upload(user_id=user_id, tmp_path=tmp_path, path=ref_path)
    assert result == {
        'code': 200,
        'data': {
            'path': f'files/{ref_path}',
            'size': '15.0B'
        },
        'status': 'success'}
    assert os.path.isfile(os.path.join(user_folder, 'files', ref_path))


@pytest.mark.parametrize(
    'folders_only',
    ['', 'folder1/folder2'])
def test_delete(file_service, user_folder, user_id, upload_file, folders_only):
    folders_path = os.path.join(user_folder, 'files', folders_only)
    filepath = os.path.join(folders_path, 'delete.txt')
    if folders_only:
        os.makedirs(folders_path)
    shutil.copyfile(upload_file, filepath)
    assert os.path.isfile(filepath)

    result = file_service.delete(user_id=user_id, path=os.path.join(folders_only, 'delete.txt'))
    assert result == {'status': 'success', 'code': 204}
    assert not os.path.isfile(filepath)


def test_get_all(file_service, user_folder, user_id, upload_file):
    shutil.copyfile(upload_file, os.path.join(user_folder, 'files', '1.txt'))
    folders2 = os.path.join(user_folder, 'files', 'folder1', 'folder2')
    os.makedirs(folders2)
    shutil.copyfile(upload_file, os.path.join(folders2, '2.txt'))
    folders3 = os.path.join(user_folder, 'files', 'folder3')
    os.makedirs(folders3)
    shutil.copyfile(upload_file, os.path.join(folders3, '3.txt'))
    shutil.copyfile(upload_file, os.path.join(folders3, '4.txt'))

    result = file_service.get_all(user_id=user_id)
    assert result == {
        'status': 'success',
        'code': 200,
        'data': {
            'files': [
                {'path': '1.txt', 'size': '15.0B'},
                {'path': 'folder1/folder2/2.txt', 'size': '15.0B'},
                {'path': 'folder3/3.txt', 'size': '15.0B'},
                {'path': 'folder3/4.txt', 'size': '15.0B'},
            ],
            'links': []}}


def test_download(file_service, user_folder, user_id, upload_file):
    filepath = os.path.join(user_folder, 'files', 'download.txt')
    shutil.copyfile(upload_file, filepath)
    assert os.path.isfile(filepath)

    result = file_service.download(user_id=user_id, path='download.txt')
    assert result == {
        'status': 'success',
        'code': 200,
        'headers': {'Content-Type': 'application/octet-stream'},
        'file': filepath
    }
    assert os.path.isfile(filepath)
