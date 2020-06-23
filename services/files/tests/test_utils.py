import os

from nameko.testing.services import worker_factory

from files.service import FilesService, ServiceException

file_service = worker_factory(FilesService)


def test_complete_to_public_path(user_folder: str, user_id: str) -> None:
    test_path = os.path.join(user_folder, 'files', 'some-file.txt')
    actual_public_path = file_service.complete_to_public_path(user_id=user_id, complete_path=test_path)
    assert actual_public_path == 'some-file.txt'


def test_authorize_file(user_folder: str, user_id: str) -> None:
    test_path = 'some-folder/some-file.txt'
    response = file_service.authorize_file(user_id=user_id, path=test_path)
    assert not isinstance(response, ServiceException)
    assert isinstance(response, str)
    assert response == os.path.join(user_folder, 'files', test_path)


def test_authorize_file_dir(user_folder: str, user_id: str) -> None:
    test_folder = 'somefolder.txt'
    ref_folder = os.path.join(user_folder, 'files', test_folder)
    if not os.path.isdir(ref_folder):
        os.mkdir(ref_folder)

    response = file_service.authorize_file(user_id=user_id, path=test_folder)
    assert isinstance(response, ServiceException)
    assert response.to_dict() == {
        'status': 'error',
        'service': 'files',
        'code': 400,
        'user_id': 'test-user',
        'msg': 'somefolder.txt: Must be a file, no directory.',
        'internal': False,
        'links': []}


def test_authorize_file_path(user_folder: str, user_id: str) -> None:
    test_file = 'somefile_without_extension'

    response = file_service.authorize_file(user_id=user_id, path=test_file)
    assert isinstance(response, ServiceException)
    assert response.to_dict() == {
        'status': 'error',
        'service': 'files',
        'code': 401,
        'user_id': 'test-user',
        'msg': 'somefile_without_extension: This path is not valid.',
        'internal': False,
        'links': []}


def test_authorize_existing_file_missing(user_folder: str, user_id: str) -> None:
    test_file = 'somefile.txt'
    response = file_service.authorize_existing_file(user_id=user_id, path=test_file)
    assert isinstance(response, ServiceException)
    assert response.to_dict() == {
        'status': 'error',
        'service': 'files',
        'code': 404,
        'user_id': 'test-user',
        'msg': 'somefile.txt: No such file or directory.',
        'internal': False,
        'links': []}


def test_authorize_exsiting_file(user_folder: str, user_id: str) -> None:
    test_file = 'somefile.txt'
    ref_path = os.path.join(user_folder, 'files', test_file)
    open(ref_path, 'a').close()
    response = file_service.authorize_existing_file(user_id=user_id, path=test_file)
    assert not isinstance(response, ServiceException)
    assert isinstance(response, str)
    assert response == ref_path
