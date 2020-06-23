import os
import shutil
from datetime import datetime

import pytest
from nameko.testing.services import worker_factory

from files.service import FilesService

file_service = worker_factory(FilesService)


@pytest.mark.parametrize(
    'ref_path',
    ['final.txt', 'folder1/folder2/final.txt']
)
def test_upload_path(user_folder: str, user_id: str, tmp_folder: str, upload_file: str,
                     ref_path: str) -> None:
    tmp_path = os.path.join(tmp_folder, 'upload.txt')
    shutil.copyfile(upload_file, tmp_path)
    assert os.path.isfile(tmp_path)

    result = file_service.upload(user_id=user_id, tmp_path=tmp_path, path=ref_path)
    assert datetime.strptime(result['data'].pop('modified'), '%Y-%m-%dT%H:%M:%SZ')
    assert result == {
        'code': 200,
        'data': {
            'path': f'{ref_path}',
            'size': 15
        },
        'status': 'success'}
    assert os.path.isfile(os.path.join(user_folder, 'files', ref_path))


@pytest.mark.parametrize(
    'folders_only',
    ['', 'folder1/folder2'])
def test_delete(user_folder: str, user_id: str, upload_file: str, folders_only: str) \
        -> None:
    folders_path = os.path.join(user_folder, 'files', folders_only)
    filepath = os.path.join(folders_path, 'delete.txt')
    if folders_only:
        os.makedirs(folders_path)
    shutil.copyfile(upload_file, filepath)
    assert os.path.isfile(filepath)

    result = file_service.delete(user_id=user_id, path=os.path.join(folders_only, 'delete.txt'))
    assert result == {'status': 'success', 'code': 204}
    assert not os.path.isfile(filepath)


def test_get_all(user_folder: str, user_id: str, upload_file: str) -> None:
    shutil.copyfile(upload_file, os.path.join(user_folder, 'files', '1.txt'))
    folders2 = os.path.join(user_folder, 'files', 'folder1', 'folder2')
    os.makedirs(folders2)
    shutil.copyfile(upload_file, os.path.join(folders2, '2.txt'))
    folders3 = os.path.join(user_folder, 'files', 'folder3')
    os.makedirs(folders3)
    shutil.copyfile(upload_file, os.path.join(folders3, '3.txt'))
    shutil.copyfile(upload_file, os.path.join(folders3, '4.txt'))

    result = file_service.get_all(user_id=user_id)
    for i in range(len(result['data']['files'])):
        datetime.strptime(result['data']['files'][i].pop('modified'), '%Y-%m-%dT%H:%M:%SZ')
    assert result == {
        'status': 'success',
        'code': 200,
        'data': {
            'files': [
                {'path': '1.txt', 'size': 15},
                {'path': 'folder1/folder2/2.txt', 'size': 15},
                {'path': 'folder3/3.txt', 'size': 15},
                {'path': 'folder3/4.txt', 'size': 15},
            ],
            'links': []}}


def test_download(user_folder: str, user_id: str, upload_file: str) -> None:
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
